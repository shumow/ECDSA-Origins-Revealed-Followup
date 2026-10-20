"""Validate coefficient-factor witnesses and regenerate the two-root analysis."""
import argparse
from collections import Counter
import io
import json
import math
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analyze2 import DATA_DIR
from cover import leg, load_curves
from factorization import check_prime_factors, pari_factors, square_divisor_root

RESULTS = DATA_DIR.parent / "results"


def coefficient_cases():
    for c in load_curves(p224_root=2):
        yield c, c["coefficient_root"], c["b"]
        if c["run"] == "P-224":
            yield c, 1, c["p"] - c["b"]


def stats(c, root, b, factors, source):
    factors = sorted(factors)
    check_prime_factors(b, factors)
    counts = Counter(factors)
    lpf = factors[-1]
    return dict(run=c["run"], i=c["i"], pub=c["pub"], coefficient_root=root,
                matches_published=(b == c["published_b"]) if c["pub"] else None,
                pbits=c["p"].bit_length(), b=b, bbits=b.bit_length(), factors=factors,
                omega=len(counts), Omega=len(factors), lpf_bits=lpf.bit_length(),
                second_bits=factors[-2].bit_length() if len(factors) > 1 else 0,
                smooth_bits=(b // lpf).bit_length(),
                max_small=max((f for f in factors if f != lpf), default=1),
                mod={q: b % q for q in (2, 3, 4, 5, 7, 8, 16)},
                square_part=square_divisor_root(factors),
                squarefree=all(e == 1 for e in counts.values()), factor_source=source)


def occupancy_probability(draws, classes, max_occupied):
    if draws < 0 or classes < 1 or not 0 <= max_occupied <= classes:
        raise ValueError("Invalid occupancy-model parameters")
    stirling = [1] + [0] * classes
    for _ in range(draws):
        stirling = [0] + [k * stirling[k] + stirling[k - 1] for k in range(1, classes + 1)]
    return sum(math.comb(classes, k) * math.factorial(k) * stirling[k]
               for k in range(max_occupied + 1)) / classes**draws


def report(rows):
    out = io.StringIO()
    print("Primary model: generator root 1 except P-224 root 2, matching published P-224.", file=out)
    print("The skipped P-224 sign convention is unknown; both roots are retained below and in JSON.", file=out)
    print("square_part is the root s of the largest square divisor s^2; smooth is bit_length(b/LPF).", file=out)
    print("\nrun    cand pub root |b| Omega omega LPF 2nd smooth squarefree factor bits", file=out)
    for r in rows:
        print(f"{r['run']:6s} {r['i']:5d} {'*' if r['pub'] else ' '}    {r['coefficient_root']} "
              f"{r['bbits']:3d} {r['Omega']:5d} {r['omega']:5d} {r['lpf_bits']:3d} "
              f"{r['second_bits']:3d} {r['smooth_bits']:6d} {str(r['squarefree']):10s} "
              f"{[f.bit_length() for f in r['factors']]}", file=out)
    print("\nP-224 alternate root-1 witnesses (not the published coefficient at 7026):", file=out)
    for r in rows:
        if "other_root" in r:
            a = r["other_root"]
            print(f"{a['i']}: b={a['b']}; Omega={a['Omega']}; LPF={a['lpf_bits']} bits; "
                  f"factors={a['factors']}", file=out)
    for key in ("Omega", "omega", "lpf_bits", "smooth_bits", "second_bits"):
        print(f"\n{key}: published {sorted(r[key] for r in rows if r['pub'])}; "
              f"skipped {sorted(r[key] for r in rows if not r['pub'])}", file=out)
    for run in ("P-256", "P-224", "192", "239"):
        rr = sorted((r for r in rows if r["run"] == run), key=lambda r: r["lpf_bits"])
        print(run, "by LPF bits:", [(r["i"], r["lpf_bits"], r["pub"]) for r in rr], file=out)
    published = [r for r in rows if r["pub"]]
    occupied = len({r["b"] % 7 for r in published})
    print(f"\nPublished b occupy {occupied} residue classes modulo 7.", file=out)
    print(f"IID-uniform illustration: a fixed allowed set has probability {(occupied / 7)**len(published):.8f}; "
          f"any at-most-{occupied} classes have probability "
          f"{occupancy_probability(len(published), 7, occupied):.8f}.", file=out)
    print("The allowed classes were chosen after inspection. Neither value is a calibrated study-wide p-value.", file=out)
    return out.getvalue()


def legendre_report(rows):
    out = io.StringIO()
    print("Quadratic character of the primary coefficient model; P-224 root 2 matches publication.", file=out)
    print("For p=3 mod4 the textbook coefficient root is a square. P-224 signs have the same character.", file=out)
    print("The character equals the product of the prime-factor characters, with multiplicity;", file=out)
    print("it is not independent of a complete integer factorization once p is fixed.\n", file=out)
    print("run    cand pub root (b/p) |b| Omega LPF squarefree", file=out)
    by_key = {(c["run"], c["i"]): c for c in load_curves(p224_root=2)}
    for r in rows:
        p = by_key[r["run"], r["i"]]["p"]
        print(f"{r['run']:6s} {r['i']:5d} {'*' if r['pub'] else ' '}   {r['coefficient_root']} "
              f"{leg(r['b'], p):+3d} {r['bbits']:3d} {r['Omega']:5d} {r['lpf_bits']:3d} "
              f"{r['squarefree']}", file=out)
    return out.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--factor", action="store_true", help="Refactor every coefficient with PARI/GP")
    parser.add_argument("--factor-missing", action="store_true", help="Use PARI/GP for missing sign witnesses")
    parser.add_argument("--from-msieve", type=Path, help="Read work_RUN_INDEX_rROOT/out.txt under this directory")
    parser.add_argument("--write-inputs", type=Path, help="Write the 23 msieve inputs and exit")
    args = parser.parse_args()
    if args.write_inputs:
        args.write_inputs.parent.mkdir(parents=True, exist_ok=True)
        with args.write_inputs.open("w", encoding="utf-8") as f:
            for c, root, b in coefficient_cases():
                label = "pub" if c["pub"] and b == c["published_b"] else "pub-alt" if c["pub"] else "skip"
                f.write(f"{c['run']} {c['i']} {root} {label} {c['p'].bit_length()} {b}\n")
        print(f"Wrote coefficient inputs to {args.write_inputs}")
        return
    cache = {}
    if args.factor or args.from_msieve:
        old = []
    else:
        with (RESULTS / "bfac.json").open(encoding="utf-8") as f:
            old = json.load(f)
    for r in old:
        for witness in (r, r.get("other_root")):
            if witness is not None:
                cache[r["run"], r["i"], witness["b"]] = (
                    witness["factors"], witness.get("factor_source", "archived msieve root-1 run"))
    cases = {}
    for c, root, b in coefficient_cases():
        if args.from_msieve:
            path = args.from_msieve / f"work_{c['run']}_{c['i']}_r{root}" / "out.txt"
            factors = [int(n) for n in re.findall(r"^\s*p\d+:\s*(\d+)\s*$",
                                                  path.read_text(), re.M)]
            source = "msieve per-root transcript"
        elif args.factor or (args.factor_missing and (c["run"], c["i"], b) not in cache):
            factors = pari_factors(b)
            source = "PARI/GP factor, with isprime certificates"
        else:
            key = c["run"], c["i"], b
            if key not in cache:
                raise ValueError(f"Missing coefficient witness for {key}; use --factor-missing or --factor")
            factors, source = cache[key]
        cases[c["run"], c["i"], root] = stats(c, root, b, factors, source)
    rows = []
    for c in load_curves(p224_root=2):
        row = cases[c["run"], c["i"], c["coefficient_root"]]
        if c["pub"] and not row["matches_published"]:
            raise ValueError(f"Primary coefficient does not match publication: {c['run']}/{c['i']}")
        if c["run"] == "P-224":
            row["other_root"] = cases[c["run"], c["i"], 1]
        rows.append(row)
    with (RESULTS / "bfac.json").open("w", encoding="utf-8") as f:
        json.dump(rows, f, indent=1)
        f.write("\n")
    text = report(rows)
    (RESULTS / "bfac.txt").write_text(text, encoding="utf-8")
    (RESULTS / "legendre-b.txt").write_text(legendre_report(rows), encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
