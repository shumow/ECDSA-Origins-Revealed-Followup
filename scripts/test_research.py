import contextlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from analyze2 import DATA_DIR, load
import battery
from binpts import Curve, poly_from
import cover

sys.path.insert(0, str(Path(__file__).resolve().parent / "k163"))
import search as k163_search
from hashes import md4, sha0, ripemd128
from strings import TIMES

ROOT = DATA_DIR.parent
GP = os.environ.get("GP") or shutil.which("gp")
K163_X = 0x23e21d6019e1211f6bd47ec180256e97


class BinaryCoordinateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(DATA_DIR / "bincurves.json") as f:
            d = json.load(f)["K-163"]
        cls.curve = Curve(d["m"], poly_from(d["m"], d["taps"]),
                          int(d["a"], 16), int(d["b"], 16), int(d["n"], 16), d["h"])
        cls.generator = (int(d["Gx"], 16), int(d["Gy"], 16))
        cls.half = cls.curve.mul((cls.curve.n + 1) // 2, cls.generator)

    def test_k163_half_coordinate_and_group_relations(self):
        self.assertTrue(self.curve.on(self.generator))
        self.assertTrue(self.curve.on(self.half))
        self.assertEqual(self.half[0], K163_X)
        self.assertEqual(self.half[0].bit_length(), 126)
        self.assertEqual(self.half[1], 0x1055096ab2f2c1e9da15bbaedbbfaea60a07b80c9)
        self.assertEqual(self.curve.add(self.half, self.half), self.generator)
        self.assertIsNone(self.curve.mul(self.curve.n, self.half))

    def test_full_group_has_another_half(self):
        torsion = (0, 1)
        other = self.curve.add(self.half, torsion)
        self.assertTrue(self.curve.on(other))
        self.assertIsNone(self.curve.add(torsion, torsion))
        self.assertEqual(self.curve.add(other, other), self.generator)
        self.assertEqual(other[0], 0x389ff55b1717d231e466c6a90bef265d7ad1ca9a4)

    @unittest.skipUnless(GP, "Set GP or put PARI/GP on PATH for the cross-language check")
    def test_pari_conversion_round_trip_and_half(self):
        helpers = (ROOT / "scripts" / "binpts.gp").read_text().split("mult(name,", 1)[0]
        script = helpers + """
T=ffgen(Mod(1,2)*(x^163+x^7+x^6+x^3+1),'t);
for(i=0,255, if(intof(toff(i,T))!=i, error("coordinate round trip failed")));
G=[toff(0x02fe13c0537bbc11acaa07d793de4e6d5e5c94eee8,T),toff(0x0289070fb05d38ff58321f2e800536d538ccdaa3d9,T)];
E=ellinit([toff(1,T),toff(1,T),toff(0,T),toff(0,T),toff(1,T)]);
n=0x04000000000000000000020108a2e0cc0d99f8a5ef;
Q=ellmul(E,G,(n+1)/2);
if(intof(Q[1])!=0x23e21d6019e1211f6bd47ec180256e97,error("wrong half-point coordinate"));
if(bits(Q[1])!=126 || ellmul(E,Q,2)!=G || ellmul(E,Q,n)!=[0],error("wrong half-point relations"));
print("GP_CHECKS_OK");
quit
"""
        result = subprocess.run([GP, "-fq", "-s", "512000000"], input=script, capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr.strip(), "")
        self.assertEqual(result.stdout.strip(), "GP_CHECKS_OK")

    @unittest.skipUnless(GP, "Set GP or put PARI/GP on PATH for the cross-language check")
    def test_all_binary_coordinate_exports_and_cofactor_preimages(self):
        with open(DATA_DIR / "bincurves.json") as f:
            params = json.load(f)
        script = (ROOT / "scripts" / "binpts.gp").read_text().split("mult(name,", 1)[0]
        for name, d in params.items():
            polynomial = "+".join([f"x^{d['m']}"] + [f"x^{k}" for k in d["taps"]])
            script += f"""
T=ffgen(Mod(1,2)*({polynomial}),'t);
E=ellinit([toff(1,T),toff(0x{d['a']},T),toff(0,T),toff(0,T),toff(0x{d['b']},T)]);
G=[toff(0x{d['Gx']},T),toff(0x{d['Gy']},T)]; n=0x{d['n']}; h={d['h']};
Q=ellmul(E,G,(n+1)/2);
if(!ellisoncurve(E,G)||ellmul(E,G,n)!=[0]||ellmul(E,Q,2)!=G,error("invalid generator or half"));
print("{name} ",intof(Q[1]));
Q=ellmul(E,G,lift(Mod(h,n)^-1));
S=if(h==2,[toff(0,T),sqrt(toff(0x{d['b']},T))],[toff(1,T),toff(0,T)]);
if(!ellisoncurve(E,S)||ellmul(E,S,h)!=[0]||ellmul(E,S,h/2)==[0],error("wrong torsion generator"));
for(j=0,h-1,R=elladd(E,Q,ellmul(E,S,j));if(ellmul(E,R,h)!=G,error("wrong cofactor preimage")));
for(j=0,h-1,R=elladd(E,Q,ellmul(E,S,j));if((bits(R[1])<=128)!=("{name}"=="K-163"&&j==0),error("unexpected short cofactor preimage")));
"""
        result = subprocess.run([GP, "-fq", "-s", "512000000"], input=script + "quit\n",
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr.strip(), "")
        exported = dict(line.split() for line in result.stdout.splitlines())
        recorded = {}
        for block in (ROOT / "results" / "binpts.out").read_text().split("== ")[1:]:
            name = block.split(":", 1)[0]
            recorded[name] = re.search(r"x = (\d+) \(decimal\)", block).group(1)
        self.assertEqual(exported, recorded)


class HashSearchTests(unittest.TestCase):
    def test_target_is_standard_polynomial_basis_coordinate(self):
        self.assertEqual(k163_search.T_INT, K163_X)
        self.assertEqual(k163_search.match(K163_X.to_bytes(16, "big")), "d")
        self.assertIsNone(k163_search.match(bytes.fromhex("3a5da90060df8af5be2121e601ae11f1")))

    def test_search_readings(self):
        target = K163_X.to_bytes(16, "big")
        self.assertEqual(k163_search.match(target[::-1]), "rev")
        self.assertEqual(k163_search.match(b"\xff" * 4 + target), "d[-16:]")
        self.assertEqual(k163_search.match(target + b"\xff" * 4), "d[:16]")
        masked = (K163_X | (3 << 126)).to_bytes(16, "big")
        self.assertEqual(k163_search.match(masked), "d (top 2 bits masked)")

    def test_small_search_runs_without_import_side_effects(self):
        output = io.StringIO()
        with patch.object(k163_search, "all_strings", return_value=[("control", b"abc")]):
            with patch.object(k163_search, "HASHES", {"md4": md4}):
                with contextlib.redirect_stdout(output):
                    k163_search.main()
        self.assertEqual(output.getvalue().strip(), "done: 13 hash evaluations, 0 hits")

    def test_hash_vectors(self):
        vectors = [
            (md4, b"", "31d6cfe0d16ae931b73c59d7e0c089c0"),
            (md4, b"abc", "a448017aaf21d8525fc10ae87aa6729d"),
            (sha0, b"", "f96cea198ad1dd5617ac084a3d92c6107708c0ef"),
            (sha0, b"abc", "0164b8a914cd2a5e74c4f7ff082c4d97f1edf880"),
            (ripemd128, b"", "cdf26213a150dc3ecb610f18f6b38b46"),
            (ripemd128, b"abc", "c14a12199c66e4ba84636b0f69144c77"),
        ]
        for function, message, expected in vectors:
            with self.subTest(hash=function.__name__, message=message):
                self.assertEqual(function(message).hex(), expected)

    def test_prime_run_timestamp_inputs(self):
        self.assertTrue({863711343, 863966734, 871002724, 871696354, 872952608, 891607927}.issubset(TIMES))


class EvidenceTests(unittest.TestCase):
    def test_embedding_degrees_exceed_twenty_thousand(self):
        for c in cover.curves:
            x = 1
            for degree in range(1, 20001):
                x = x * c["p"] % c["n"]
                self.assertNotEqual(x, 1, (c["run"], c["i"], degree))

    def test_textbook_root_forces_square_b(self):
        for c in cover.curves:
            if c["p"] % 4 == 3:
                self.assertEqual(pow(c["b"], (c["p"] - 1) // 2, c["p"]), 1)

    @unittest.skipUnless(GP, "Set GP or put PARI/GP on PATH to certify the 19 viable orders")
    def test_viable_prime_orders_and_nonmaximal_orders(self):
        script = ""
        for c in cover.curves:
            script += f"""
p={c['p']}; n={c['n']}; b={c['b']}; E=ellinit([-3,b],p);
if(!isprime(n)||(p+1-n)^2>4*p||n^2<=16*p,error("order not certified"));
u=0;while(!issquare(Mod(u^3-3*u+b,p)),u++);
Q=[Mod(u,p),sqrt(Mod(u^3-3*u+b,p))];
if(ellmul(E,Q,n)!=[0],error("wrong prime order"));
"""
            if c["run"] == "239" and c["i"] in (2320, 2682):
                script += """
j=lift(Mod(-6912,p)/Mod(b^2-4,p));
if(#polrootsmod(lift(subst(polmodular(5,0),y,Mod(j,p))),p)!=1,error("wrong 5-isogeny count"));
"""
        result = subprocess.run([GP, "-fq", "-s", "512000000"],
                                input=script + 'print("19_ORDERS_OK");quit\n',
                                capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr.strip(), "")
        self.assertEqual(result.stdout.strip(), "19_ORDERS_OK")

    def test_all_point_count_logs_are_complete(self):
        for name, expected in [("P-256", 348), ("P-224", 1161), ("ANSI192", 1057), ("ANSI239", 506)]:
            with self.subTest(run=name):
                self.assertEqual(len(load(name)), expected)

    def test_bad_point_count_logs_fail_explicitly(self):
        bad_logs = ["1 FAIL\nDONE\n", "1 101 103 ok\n", "1 101 103\nDONE\n",
                    "1 101 103 ok\n1 even\nDONE\n", "DONE\n1 even\n"]
        with tempfile.TemporaryDirectory() as directory:
            name = Path(directory) / "sample"
            for text in bad_logs:
                with self.subTest(log=text):
                    name.with_suffix(".orders2").write_text(text)
                    with self.assertRaises(ValueError):
                        load(name)

    def test_gp_errors_are_not_hidden(self):
        for code, error in [(0, "  *** simulated GP error"), (1, "")]:
            result = subprocess.CompletedProcess(["gp"], code, stdout="", stderr=error)
            with self.subTest(returncode=code, stderr=error):
                with patch.object(battery.subprocess, "run", return_value=result):
                    with self.assertRaises(RuntimeError):
                        battery.gp("1+1")

    def test_exact_endpoint_conditioned_null(self):
        labels = list(cover.relabellings())
        self.assertEqual(len(labels), 126)
        self.assertEqual(len({tuple(lab) for lab in labels}), 126)
        for lab in labels:
            for run in cover.RUNS:
                js = [j for j, c in enumerate(cover.curves) if c["run"] == run]
                endpoint = max(js, key=lambda j: cover.curves[j]["i"])
                self.assertFalse(lab[endpoint])
                self.assertEqual(sum(not lab[j] for j in js), sum(cover.curves[j]["pub"] for j in js))
        distribution = {}
        for lab in labels:
            size, _, _ = cover.min_cover(lab, maxk=5)
            distribution[size] = distribution.get(size, 0) + 1
        self.assertEqual(distribution, {None: 15, 2: 1, 3: 35, 4: 52, 5: 23})
        size, covers, _ = cover.min_cover([not c["pub"] for c in cover.curves], maxk=5)
        self.assertEqual((size, len(covers)), (4, 10))


if __name__ == "__main__":
    unittest.main()
