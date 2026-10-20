"""Validate partial-factor witnesses and report known, not guaranteed, smooth parts."""
import argparse
from collections import Counter
import io
import json
from pathlib import Path
import statistics
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analyze import is_probable_prime
from analyze2 import DATA_DIR
from cover import curves, relabellings
from extfac.cofactors import extension_components
from factorization import check_product, check_prime_factors, pari_factors, smooth_log2, smooth_part

RESULTS = DATA_DIR.parent / "results"
CANDIDATES = {(c["run"], c["i"]): c for c in curves}


def normalize_row(row, refine=False):
    row = dict(row)
    key = row["run"], row["i"]
    if key not in CANDIDATES or row["k"] not in (3, 4, 6):
        raise ValueError(f"Unknown curve/degree record: {key}")
    c = CANDIDATES[key]
    value = extension_components(c["p"], c["t"])[row["k"]]
    factors = [int(f) for f in row["factors"]]
    cofactor = int(row["cofactor"])
    check_product(value, factors, cofactor)
    if row["pub"] != c["pub"] or row["bits"] != value.bit_length():
        raise ValueError(f"Curve metadata mismatch: {key}")
    if row["factor_bits"] != [f.bit_length() for f in factors]:
        raise ValueError(f"Factor bit lengths do not match values: {key}")
    expected_bits = cofactor.bit_length() if cofactor > 1 else 0
    prime_remainder = is_probable_prime(cofactor) if cofactor > 1 else None
    if row["cofactor_bits"] != expected_bits or row["cofactor_prime"] != prime_remainder:
        raise ValueError(f"Remainder metadata mismatch: {key}")
    primes, refinements = [], list(row.get("factor_refinements", []))
    for factor in factors:
        if is_probable_prime(factor):
            primes.append(factor)
        elif refine:
            parts = pari_factors(factor)
            primes.extend(parts)
            refinements.append({"composite": str(factor), "prime_factors": [str(p) for p in parts],
                                "method": "PARI/GP factor and isprime"})
        else:
            raise ValueError(f"Composite atom {factor} in {key}; use --refine to split legacy extracted atoms")
    if prime_remainder:
        primes.append(cofactor)
        cofactor = 1
    primes.sort()
    check_prime_factors(value, primes, cofactor)
    row.update(factors=[str(f) for f in primes], factor_bits=[f.bit_length() for f in primes],
               cofactor=str(cofactor), cofactor_bits=cofactor.bit_length() if cofactor > 1 else 0,
               cofactor_prime=is_probable_prime(cofactor) if cofactor > 1 else None,
               complete=cofactor == 1, known_smooth_log2=smooth_log2(primes),
               largest_known_prime_bits=max((f.bit_length() for f in primes), default=0))
    if refinements:
        row["factor_refinements"] = refinements
    if "coverage" not in row:
        row["coverage"] = {
            "status": "legacy-unverified", "exhaustive": False,
            "note": "Pre-fix ECM loop outputs were not retained. Original curve-count logs are not "
                    "validated coverage. Prime atoms/products were repaired; the 57 searches were not rerun."}
    if row["coverage"].get("exhaustive") is not False:
        raise ValueError("A bounded ECM record must not claim exhaustive coverage")
    if row["coverage"]["status"] == "bounded-recorded":
        requested = row["coverage"].get("levels_requested", [])
        completed = row["coverage"].get("levels_completed", [])
        if (row["coverage"].get("protocol") != "-one" or not requested
                or len(requested) != len(completed) or completed != row["log"]
                or any(len(a) != 2 or len(b) != 2 or a[0] != b[0]
                       or not 0 <= b[1] <= a[1] for a, b in zip(requested, completed))):
            raise ValueError("Recorded ECM bounds, protocol, or completed budgets are inconsistent")
    elif row["coverage"]["status"] != "legacy-unverified":
        raise ValueError("Unknown ECM coverage status")
    return row


def load_rows(paths, refine=False):
    rows, seen = [], set()
    for path in paths:
        with Path(path).open(encoding="utf-8") as f:
            records = json.load(f)
        for original in records:
            key = original["run"], original["i"], original["k"]
            if key in seen:
                raise ValueError(f"Duplicate factor record: {key}")
            seen.add(key)
            rows.append(normalize_row(original, refine))
    expected = {(c["run"], c["i"], k) for c in curves for k in (3, 4, 6)}
    if seen != expected:
        raise ValueError(f"Expected all 57 unique factor records; missing {sorted(expected - seen)}")
    return sorted(rows, key=lambda r: (list(("P-256", "P-224", "192", "239")).index(r["run"]),
                                       r["k"], r["i"]))


def sextic_rank_test(rows):
    six = {(r["run"], r["i"]): r for r in rows if r["k"] == 6}
    ranks = {}
    for run in ("P-256", "P-224", "192", "239"):
        group = sorted((r for r in six.values() if r["run"] == run),
                       key=lambda r: smooth_part(map(int, r["factors"])))
        j = 0
        while j < len(group):
            score = smooth_part(map(int, group[j]["factors"]))
            end = j + 1
            while end < len(group) and smooth_part(map(int, group[end]["factors"])) == score:
                end += 1
            for r in group[j:end]:
                ranks[r["run"], r["i"]] = j + 1 + end
            j = end
    observed = sum(ranks[c["run"], c["i"]] for c in curves if c["pub"])
    null = [sum(ranks[c["run"], c["i"]] for j, c in enumerate(curves) if not labels[j])
            for labels in relabellings()]
    tail = sum(value >= observed for value in null)
    return {"statistic": "within-run midrank sum of known 2^40-smooth products",
            "condition": "per-run published counts and final candidate published",
            "observed_twice_rank_sum": observed, "tail_count": tail, "n_perm": len(null),
            "one_sided_fraction": tail / len(null), "exploratory": True,
            "multiple_comparisons_adjusted": False}


def summary_stats(rows):
    result = {"coverage_status_counts": dict(Counter(r["coverage"]["status"] for r in rows)),
              "known_smoothness_bound": 2**40, "components": {}}
    for k in (3, 4, 6):
        result["components"][k] = {}
        for label, selected in (("published", True), ("skipped", False)):
            group = [r for r in rows if r["k"] == k and r["pub"] == selected]
            scores = sorted(r["known_smooth_log2"] for r in group)
            result["components"][k][label] = {
                "known_smooth_log2": scores, "median_known_smooth_log2": statistics.median(scores),
                "largest_known_prime_bits": sorted(r["largest_known_prime_bits"] for r in group),
                "complete": sum(r["complete"] for r in group), "count": len(group)}
    result["sextic_rank_test"] = sextic_rank_test(rows)
    return result


def report(rows, stats):
    out = io.StringIO()
    print("Extension-order components: C3=#E3/n; C4=#E4/#E2; C6=#E6*n/(#E3*#E2).", file=out)
    print("Only validated prime atoms contribute to known smoothness: log2(product(q<2^40)).", file=out)
    print("A composite remainder may hide additional small factors. Neither ECM bounds nor a no-hit run prove absence.", file=out)
    print("Prime residuals are included among known prime factors; remainder 1 means fully factored.", file=out)
    print("Coverage:", stats["coverage_status_counts"], file=out)
    if any(r["coverage"]["status"] == "legacy-unverified" for r in rows):
        print("LEGACY: products/prime atoms repaired, but the pre-fix ECM budgets are unverified and the searches were not rerun.", file=out)
    for k in (3, 4, 6):
        print(f"\n--- k={k}\nrun    cand pub bits known-smooth-log2 known-prime-bits remainder", file=out)
        for r in rows:
            if r["k"] == k:
                remaining = f"{r['cofactor_bits']}C" if r["cofactor_bits"] else "1"
                print(f"{r['run']:6s} {r['i']:5d} {'*' if r['pub'] else ' '}  {r['bits']:3d} "
                      f"{r['known_smooth_log2']:8.3f} {str(r['factor_bits']):55s} {remaining}", file=out)
        for label, s in stats["components"][k].items():
            print(f"  {label}: median known-smooth log2 {s['median_known_smooth_log2']:.3f}; "
                  f"complete {s['complete']}/{s['count']}", file=out)
    test = stats["sextic_rank_test"]
    print(f"\nExploratory endpoint-conditioned C6 rank tail: {test['tail_count']}/{test['n_perm']} "
          f"= {test['one_sided_fraction']:.6f}, one-sided, before multiple-comparison adjustment.", file=out)
    print("This compares the known factors, not unknown complete smooth parts or historical selection mechanisms.", file=out)
    return out.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="*", type=Path, help="Complete JSON or explicit shard files")
    parser.add_argument("--refine", action="store_true", help="Split legacy extracted composite atoms with PARI/GP")
    parser.add_argument("--output-dir", type=Path, default=RESULTS)
    args = parser.parse_args()
    rows = load_rows(args.inputs or [RESULTS / "extfac.json"], args.refine)
    stats = summary_stats(rows)
    text = report(rows, stats)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, data in (("extfac.json", rows), ("extfac-stats.json", stats)):
        with (args.output_dir / name).open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=1)
            f.write("\n")
    (args.output_dir / "extfac.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
