import contextlib
import ast
import copy
import io
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import cover
from analyze2 import DATA_DIR
from bfac import summarize as bfac
from extfac import cofactors, ecm_driver, summarize_ext
from factorization import check_prime_factors, check_product, smooth_log2, smooth_part, square_divisor_root
from run_points import merge_blocks

ROOT = DATA_DIR.parent
GP = os.environ.get("GP") or shutil.which("gp")
P224_B = 0xb4050a850c04b3abf54132565044b0b7d7bfd8ba270b39432355ffb4


class CoefficientTests(unittest.TestCase):
    def test_root_models_preserve_intrinsic_orders_but_match_publication_explicitly(self):
        first, second = cover.load_curves(1), cover.load_curves(2)
        for a, b in zip(first, second):
            self.assertEqual((a["run"], a["i"], a["p"], a["n"], a["t"]),
                             (b["run"], b["i"], b["p"], b["n"], b["t"]))
            if a["run"] == "P-224":
                self.assertEqual(a["b"] + b["b"], a["p"])
            else:
                self.assertEqual(a["b"], b["b"])
            if b["pub"]:
                self.assertEqual(b["b"], b["published_b"])
        published = next(c for c in second if c["run"] == "P-224" and c["pub"])
        self.assertEqual(published["b"], P224_B)
        with self.assertRaises(ValueError):
            cover.load_curves(0)

    def test_complete_coefficient_witnesses_include_both_p224_roots(self):
        with (ROOT / "results" / "bfac.json").open(encoding="utf-8") as f:
            rows = json.load(f)
        self.assertEqual(len(rows), 19)
        curves = {(c["run"], c["i"]): c for c in cover.load_curves(2)}
        for row in rows:
            c = curves[row["run"], row["i"]]
            self.assertEqual(row["b"], c["b"])
            check_prime_factors(row["b"], row["factors"])
            self.assertEqual(row["square_part"], square_divisor_root(row["factors"]))
            if row["pub"]:
                self.assertTrue(row["matches_published"])
            if row["run"] == "P-224":
                other = row["other_root"]
                check_prime_factors(other["b"], other["factors"])
                self.assertEqual(row["b"] + other["b"], c["p"])
                self.assertEqual((row["coefficient_root"], other["coefficient_root"]), (2, 1))
        published = next(r for r in rows if r["run"] == "P-224" and r["pub"])
        self.assertEqual((published["b"], published["lpf_bits"]), (P224_B, 123))

    def test_missing_msieve_inputs_can_be_generated_from_a_clean_checkout(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "b_list.txt"
            with patch.object(bfac.sys, "argv", ["summarize.py", "--write-inputs", str(path)]):
                with contextlib.redirect_stdout(io.StringIO()):
                    bfac.main()
            rows = [line.split() for line in path.read_text().splitlines()]
        self.assertEqual(len(rows), 23)
        self.assertEqual(len({tuple(r[:3]) for r in rows}), 23)
        published = next(r for r in rows if r[:3] == ["P-224", "7026", "2"])
        self.assertEqual((published[3], int(published[5])), ("pub", P224_B))

    def test_square_part_uses_all_repeated_primes(self):
        factors = [2, 2, 3, 3, 3, 3, 101]
        self.assertEqual(square_divisor_root(factors), 18)
        self.assertEqual(math.prod(factors) % 18**2, 0)

    def test_refactor_mode_does_not_require_an_existing_results_cache(self):
        with (ROOT / "results" / "bfac.json").open(encoding="utf-8") as f:
            source = json.load(f)
        witnesses = {r["b"]: r["factors"] for r in source}
        witnesses.update({r["other_root"]["b"]: r["other_root"]["factors"]
                          for r in source if "other_root" in r})
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(bfac, "RESULTS", Path(directory)):
                with patch.object(bfac, "pari_factors", side_effect=lambda b: witnesses[b]):
                    with patch.object(bfac.sys, "argv", ["summarize.py", "--factor"]):
                        with contextlib.redirect_stdout(io.StringIO()):
                            bfac.main()
            self.assertTrue(Path(directory, "bfac.json").exists())

    def test_msieve_transcripts_can_rebuild_results_without_a_cache(self):
        with (ROOT / "results" / "bfac.json").open(encoding="utf-8") as f:
            source = json.load(f)
        witnesses = {r["b"]: r["factors"] for r in source}
        witnesses.update({r["other_root"]["b"]: r["other_root"]["factors"]
                          for r in source if "other_root" in r})
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            work, results = root / "work", root / "results"
            results.mkdir()
            for c, coefficient_root, b in bfac.coefficient_cases():
                path = work / f"work_{c['run']}_{c['i']}_r{coefficient_root}" / "out.txt"
                path.parent.mkdir(parents=True)
                path.write_text("".join(f"p{len(str(q))}: {q}\n" for q in witnesses[b]))
            with patch.object(bfac, "RESULTS", results):
                with patch.object(bfac.sys, "argv", ["summarize.py", "--from-msieve", str(work)]):
                    with contextlib.redirect_stdout(io.StringIO()):
                        bfac.main()
            with (results / "bfac.json").open() as f:
                rebuilt = json.load(f)
            self.assertEqual(len(rebuilt), 19)
            self.assertTrue(all(r["matches_published"] for r in rebuilt if r["pub"]))

    def test_root2_set_cover_sensitivity_is_not_the_root1_result(self):
        matrix = cover.predicate_matrix(cover.load_curves(2))
        labels = [not c["pub"] for c in cover.curves]
        size, covers, _ = cover.min_cover(labels, maxk=5, matrix=matrix)
        self.assertEqual((size, len(covers)), (4, 22))
        result = cover.permutation_result(matrix, size)
        self.assertEqual(result["n_perm"], 126)
        self.assertAlmostEqual(result["fraction_at_most_observed"], 98 / 126)

    def test_adaptively_chosen_residue_classes_are_not_a_fixed_set_test(self):
        self.assertAlmostEqual(bfac.occupancy_probability(8, 7, 4), 1637041 / 5764801)
        self.assertGreater(bfac.occupancy_probability(8, 7, 4), (4 / 7)**8)
        self.assertEqual(bfac.occupancy_probability(0, 7, 0), 1)


class ECMProtocolTests(unittest.TestCase):
    @staticmethod
    def output(curves, used, factors=()):
        text = "GMP-ECM 7.0.6\n"
        for i in range(1, used + 1):
            if i > 1:
                text += f"Run {i} out of {curves}:\n"
            text += "Using B1=50000\nStep 1 took 1ms\nStep 2 took 1ms\n"
        text += "".join(f"Found prime factor of {len(str(f))} digits: {f}\n" for f in factors)
        return text

    def test_stop_at_first_factor_and_accept_factor_found_exit_status(self):
        value = 1000003 * 1000033 * 1000037
        completed = subprocess.CompletedProcess(["ecm"], 6,
                                               self.output(5, 2, [1000003]), "")
        with patch.object(ecm_driver.subprocess, "run", return_value=completed) as run:
            self.assertEqual(ecm_driver.ecm_once(value, 50000, 5), (1000003, 2))
        self.assertIn("-one", run.call_args.args[0])

    def test_first_curve_factor_has_no_run_heading_in_real_ecm_output(self):
        value = 1000003 * 1000033 * 1000037
        completed = subprocess.CompletedProcess(["ecm"], 6, self.output(3, 1, [1000033]), "")
        with patch.object(ecm_driver.subprocess, "run", return_value=completed):
            self.assertEqual(ecm_driver.ecm_once(value, 50000, 3), (1000033, 1))

    def test_multiple_factors_are_rejected_not_silently_discarded(self):
        value = 1000003 * 1000033 * 1000037
        completed = subprocess.CompletedProcess(["ecm"], 6,
                                               self.output(5, 5, [1000003, 1000033]), "")
        with patch.object(ecm_driver.subprocess, "run", return_value=completed):
            with self.assertRaisesRegex(RuntimeError, "multiple factors"):
                ecm_driver.ecm_once(value, 50000, 5)

    def test_errors_are_not_recorded_as_a_no_factor_search(self):
        for code, error in [(1, ""), (-9, ""), (0, "invalid B1")]:
            with self.subTest(exit=code, stderr=error):
                completed = subprocess.CompletedProcess(["ecm"], code, "", error)
                with patch.object(ecm_driver.subprocess, "run", return_value=completed):
                    with self.assertRaises(RuntimeError):
                        ecm_driver.ecm_once(1000003 * 1000033, 50000, 5)

    def test_transcripts_are_preserved_even_on_failure(self):
        completed = subprocess.CompletedProcess(["ecm"], 1, "partial output", "failure")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "attempt.txt"
            with patch.object(ecm_driver.subprocess, "run", return_value=completed):
                with self.assertRaises(RuntimeError):
                    ecm_driver.ecm_once(1000003 * 1000033, 50000, 5, path)
            text = path.read_text()
            self.assertIn("exit: 1", text)
            self.assertIn("partial output", text)
            self.assertIn("failure", text)

    def test_timeout_keeps_partial_output_without_claiming_a_completed_budget(self):
        error = subprocess.TimeoutExpired(["ecm"], 3600, output=b"partial curve", stderr=b"interrupted")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "timeout.txt"
            with patch.object(ecm_driver.subprocess, "run", side_effect=error):
                with self.assertRaisesRegex(RuntimeError, "timed out"):
                    ecm_driver.ecm_once(1000003 * 1000033, 50000, 5, path)
            text = path.read_text()
            self.assertIn("exit: timeout", text)
            self.assertIn("partial curve", text)

    def test_no_factor_requires_a_complete_run_count(self):
        for text in ("", "GMP-ECM 7.0.6\n", self.output(5, 2), "Run 1 out of 6:\n"):
            with self.subTest(transcript=text):
                completed = subprocess.CompletedProcess(["ecm"], 0, text, "")
                with patch.object(ecm_driver.subprocess, "run", return_value=completed):
                    with self.assertRaises(RuntimeError):
                        ecm_driver.ecm_once(1000003 * 1000033, 50000, 5)

    def test_single_curve_banner_is_not_a_completed_search(self):
        completed = subprocess.CompletedProcess(["ecm"], 0, "GMP-ECM 7.0.6\n", "")
        with patch.object(ecm_driver.subprocess, "run", return_value=completed):
            with self.assertRaises(RuntimeError):
                ecm_driver.ecm_once(1000003 * 1000033, 50000, 1)

    def test_completed_single_curve_without_loop_headers_is_supported(self):
        text = "GMP-ECM 7.0.6\nUsing B1=50000\nStep 1 took 1ms\nStep 2 took 1ms\n"
        completed = subprocess.CompletedProcess(["ecm"], 0, text, "")
        with patch.object(ecm_driver.subprocess, "run", return_value=completed):
            self.assertEqual(ecm_driver.ecm_once(1000003 * 1000033, 50000, 1), (None, 1))

    def test_nondivisor_is_rejected(self):
        completed = subprocess.CompletedProcess(["ecm"], 6, self.output(2, 1, [101]), "")
        with patch.object(ecm_driver.subprocess, "run", return_value=completed):
            with self.assertRaisesRegex(RuntimeError, "non-proper factor"):
                ecm_driver.ecm_once(1000003 * 1000033, 50000, 2)

    def test_no_factor_and_degenerate_curves_are_accounted_separately(self):
        for code, used in [(0, 5), (8, 1)]:
            completed = subprocess.CompletedProcess(["ecm"], code, self.output(5, used), "")
            with self.subTest(exit=code):
                with patch.object(ecm_driver.subprocess, "run", return_value=completed):
                    self.assertEqual(ecm_driver.ecm_once(1000003 * 1000033, 50000, 5), (None, used))


class ECMSearchTests(unittest.TestCase):
    def test_composite_factors_are_split_without_losing_their_product(self):
        a, b, c = 1000003, 1000033, 1000037
        with patch.object(ecm_driver, "LEVELS", [(50000, 3)]):
            with patch.object(ecm_driver, "ecm_once", side_effect=[(a*b, 1), (a, 1)]):
                factors, remainder, log = ecm_driver.factor(a*b*c)
        self.assertEqual(factors, [a, b, c])
        self.assertEqual(remainder, 1)
        self.assertEqual(log, [[50000, 2]])

    def test_each_level_has_one_shared_budget(self):
        value = 1000003 * 1000033

        def no_factor(n, bound, count, path):
            return None, count

        with patch.object(ecm_driver, "LEVELS", [(50000, 3), (250000, 2)]):
            with patch.object(ecm_driver, "ecm_once", side_effect=no_factor):
                factors, remainder, log = ecm_driver.factor(value)
        self.assertEqual((factors, remainder, log), ([], value, [[50000, 3], [250000, 2]]))

    def test_degenerate_attempt_does_not_discard_remaining_budget(self):
        value = 1000003 * 1000033
        with patch.object(ecm_driver, "LEVELS", [(50000, 3)]):
            with patch.object(ecm_driver, "ecm_once", side_effect=[(None, 1), (None, 2)]) as run:
                factors, remainder, log = ecm_driver.factor(value)
        self.assertEqual(run.call_args.args[2], 2)
        self.assertEqual((factors, remainder, log), ([], value, [[50000, 3]]))

    def test_invalid_curve_accounting_fails(self):
        with patch.object(ecm_driver, "LEVELS", [(50000, 1)]):
            with patch.object(ecm_driver, "ecm_once", return_value=(None, 0)):
                with self.assertRaises(RuntimeError):
                    ecm_driver.factor(1000003 * 1000033)

    def test_input_generator_and_driver_agree_without_working_directory_assumptions(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cof.txt"
            with patch.object(cofactors.sys, "argv", ["cofactors.py", str(path)]):
                with contextlib.redirect_stdout(io.StringIO()):
                    cofactors.main()
            rows = ecm_driver.read_inputs(path)
            self.assertEqual(len(rows), 57)
            with path.open("a") as f:
                f.write(path.read_text().splitlines()[0] + "\n")
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                ecm_driver.read_inputs(path)

    def test_empty_shard_has_an_explicit_result_without_running_ecm(self):
        with tempfile.TemporaryDirectory() as directory:
            inputs, output = Path(directory) / "cof.txt", Path(directory) / "empty.json"
            with patch.object(cofactors.sys, "argv", ["cofactors.py", str(inputs)]):
                with contextlib.redirect_stdout(io.StringIO()):
                    cofactors.main()
            with patch.object(ecm_driver.sys, "argv",
                              ["ecm_driver.py", str(inputs), str(output), "57", "58"]):
                with patch.object(ecm_driver, "factor") as factor:
                    with contextlib.redirect_stdout(io.StringIO()) as text:
                        ecm_driver.main()
                    factor.assert_not_called()
            self.assertEqual(json.loads(output.read_text()), [])
            self.assertIn("no assigned inputs", text.getvalue())


class FactorDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = summarize_ext.load_rows([ROOT / "results" / "extfac.json"])

    def test_all_57_records_have_prime_atoms_and_valid_products(self):
        self.assertEqual(len(self.rows), 57)
        self.assertEqual(len({(r["run"], r["i"], r["k"]) for r in self.rows}), 57)
        for r in self.rows:
            c = summarize_ext.CANDIDATES[r["run"], r["i"]]
            value = cofactors.extension_components(c["p"], c["t"])[r["k"]]
            check_prime_factors(value, list(map(int, r["factors"])), int(r["cofactor"]))
            self.assertFalse(r["coverage"]["exhaustive"])
            self.assertEqual(r["known_smooth_log2"], smooth_log2(map(int, r["factors"])))

    @unittest.skipUnless(GP, "Set GP or put PARI/GP on PATH to certify every cached prime atom")
    def test_pari_certifies_every_cached_coefficient_and_extension_prime(self):
        primes = {int(f) for r in self.rows for f in r["factors"]}
        with (ROOT / "results" / "bfac.json").open(encoding="utf-8") as f:
            coefficients = json.load(f)
        for r in coefficients:
            primes.update(r["factors"])
            if "other_root" in r:
                primes.update(r["other_root"]["factors"])
        script = ("v=[" + ",".join(map(str, sorted(primes))) + "];"
                  'for(j=1,#v,if(!isprime(v[j]),error("composite cached atom")));'
                  'print("ALL_PRIMES_OK");quit\n')
        r = subprocess.run([GP, "-fq", "-s", "512000000"], input=script,
                           capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stderr.strip(), "")
        self.assertEqual(r.stdout.strip(), "ALL_PRIMES_OK")

    def test_legacy_coverage_is_not_relabelled_as_a_fresh_search(self):
        self.assertTrue(all(r["coverage"]["status"] == "legacy-unverified" for r in self.rows))
        self.assertEqual(sum(len(r.get("factor_refinements", [])) for r in self.rows), 4)

    def test_smoothness_uses_log_of_product_not_sum_of_bit_lengths(self):
        self.assertEqual(smooth_log2([2, 2, 2, 2]), 4)
        self.assertEqual(smooth_log2([]), 0)
        self.assertEqual(smooth_part([2, 3, 11], 11), 6)
        r = next(r for r in self.rows if (r["run"], r["i"], r["k"]) == ("P-256", 1842, 3))
        self.assertAlmostEqual(r["known_smooth_log2"], 60.418, places=3)

    def test_duplicate_or_missing_shards_are_not_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            for rows in (self.rows[:-1], self.rows[:-1] + [self.rows[0]]):
                path.write_text(json.dumps(rows))
                with self.assertRaises(ValueError):
                    summarize_ext.load_rows([path])

    def test_corrupt_products_and_composite_prime_atoms_fail(self):
        with self.assertRaises(ValueError):
            check_product(101, [2, 3])
        with self.assertRaisesRegex(ValueError, "Composite"):
            check_prime_factors(101 * 103, [101 * 103])
        r = copy.deepcopy(self.rows[0])
        r["factors"][0] = str(int(r["factors"][0]) + 1)
        with self.assertRaises(ValueError):
            summarize_ext.normalize_row(r)

    def test_sextic_rank_null_conditions_on_runs_and_endpoints(self):
        result = summarize_ext.sextic_rank_test(self.rows)
        self.assertEqual((result["tail_count"], result["n_perm"]), (11, 126))
        self.assertAlmostEqual(result["one_sided_fraction"], 11 / 126)
        self.assertTrue(result["exploratory"])
        self.assertFalse(result["multiple_comparisons_adjusted"])

    def test_fresh_coverage_is_preserved_but_inconsistent_budgets_are_rejected(self):
        row = copy.deepcopy(self.rows[0])
        row["log"] = [[50000, 3]]
        row["coverage"] = {"status": "bounded-recorded", "exhaustive": False, "protocol": "-one",
                           "levels_requested": [[50000, 5]], "levels_completed": [[50000, 3]]}
        self.assertEqual(summarize_ext.normalize_row(row)["coverage"]["status"], "bounded-recorded")
        row["coverage"]["levels_completed"][0][1] = 6
        with self.assertRaises(ValueError):
            summarize_ext.normalize_row(row)


class PublishedPointTests(unittest.TestCase):
    def test_all_declared_prime_generator_orders_are_in_hasse_interval(self):
        for line in (ROOT / "scripts" / "pts.gp").read_text().splitlines():
            if line.startswith('mult("'):
                args = ast.literal_eval(line[len("mult"):-1])
                name, p, _, _, n = args[:5]
                with self.subTest(curve=name):
                    self.assertLessEqual((p + 1 - n)**2, 4*p)
                    if name == "P-521":
                        self.assertEqual(n, 0x01fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffa51868783bf2f966b7fcc0148f709a5d03bb5c9b8899c47aebb6fb71e91386409)

    def test_point_result_merge_preserves_other_curves_and_rejects_duplicates(self):
        header = r"^\S+: G on curve"
        old = "P-256: G on curve 1\nold256\nP-224: G on curve 1\nold224\n"
        new = "P-224: G on curve 1\ncorrect224\n"
        self.assertEqual(merge_blocks(old, new, header),
                         "P-256: G on curve 1\nold256\nP-224: G on curve 1\ncorrect224\n")
        with self.assertRaises(ValueError):
            merge_blocks(old, new + new, header)

    @unittest.skipUnless(GP, "Set GP or put PARI/GP on PATH for exact published-point checks")
    def test_p224_source_call_uses_actual_standard_generator(self):
        source = (ROOT / "scripts" / "pts.gp").read_text()
        helpers = source.split('scan("P-256"', 1)[0]
        call = re.search(r'^mult\("P-224".*;$', source, re.M).group(0)
        script = helpers + '\nKM=8;ONLY="P-224";\n' + call + '\nprint("POINT_OK");quit\n'
        with tempfile.TemporaryDirectory() as directory:
            r = subprocess.run([GP, "-fq", "-s", "1000000000"], input=script, cwd=directory,
                               capture_output=True, text=True, timeout=60)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(r.stderr.strip(), "")
            self.assertIn("POINT_OK", r.stdout)
            text = Path(directory, "mult.out").read_text()
            self.assertIn("24426795498533690031342169898947419208493664027087368092401043037658", text)

    @unittest.skipUnless(GP, "Set GP or put PARI/GP on PATH for exact published-point checks")
    def test_p224_wrong_curve_cannot_manufacture_a_passing_generator(self):
        source = (ROOT / "scripts" / "pts.gp").read_text()
        helpers = source.split('scan("P-256"', 1)[0]
        script = helpers + """
p=2^224-2^96+1;b=0xb4050a850c04b3abf54132565044b0b7d7bfd8ba270b39432355ffb4;
E=ellinit([-3,p-b],p);
iferr(published_point("P-224",E,p,p-b,0xb70e0cbd6bb4bf7f321390b94a03c1d356c21122343280d6115c1d21,0xbd376388b5f723fb4c22dfe6cd4375a05a07476444d5819985007e34),e,print("REJECTED"));
quit
"""
        r = subprocess.run([GP, "-fq", "-s", "1000000000"], input=script,
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stderr.strip(), "")
        self.assertEqual(r.stdout.strip(), "REJECTED")

    @unittest.skipUnless(GP, "Set GP or put PARI/GP on PATH for prime-generator source checks")
    def test_all_ten_source_generator_calls_pass_exact_order_checks(self):
        source = (ROOT / "scripts" / "pts.gp").read_text()
        helpers = source.split('scan("P-256"', 1)[0]
        calls = re.findall(r'^mult\(".*;$', source, re.M)
        self.assertEqual(len(calls), 10)
        script = helpers + '\nKM=2;ONLY="";\n' + "\n".join(calls) + '\nprint("TEN_POINTS_OK");quit\n'
        with tempfile.TemporaryDirectory() as directory:
            r = subprocess.run([GP, "-fq", "-s", "1000000000"], input=script, cwd=directory,
                               capture_output=True, text=True, timeout=120)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(r.stderr.strip(), "")
            self.assertIn("TEN_POINTS_OK", r.stdout)
            self.assertEqual(Path(directory, "mult.out").read_text().count("n*G=O: 1"), 10)


if __name__ == "__main__":
    unittest.main()
