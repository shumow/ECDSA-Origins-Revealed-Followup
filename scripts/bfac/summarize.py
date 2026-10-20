import re, sys, json
sys.path.insert(0, "..")
from analyze import is_probable_prime

rows = []
for line in open("./b_list.txt"):
    run, idx, lab, pbits, b = line.split()
    b = int(b); idx = int(idx)
    out = open(f"./work_{run}_{idx}/out.txt").read()
    facs = [int(m) for m in re.findall(r"^p\d+: (\d+)$", out, re.M)]
    prod = 1
    for f in facs:
        assert is_probable_prime(f), (run, idx, f)
        prod *= f
    assert prod == b, (run, idx)
    lpf = max(facs)
    smooth = b // lpf
    rows.append(dict(run=run, i=idx, pub=lab == "pub", pbits=int(pbits), b=b, bbits=b.bit_length(),
                     factors=facs, omega=len(set(facs)), Omega=len(facs), lpf_bits=lpf.bit_length(),
                     second_bits=sorted(facs)[-2].bit_length() if len(facs) > 1 else 0,
                     smooth_bits=smooth.bit_length(), max_small=max(f for f in facs if f != lpf) if len(facs) > 1 else 1,
                     mod={q: b % q for q in (2, 3, 4, 5, 7, 8, 16)},
                     square_part=max((f for f in set(facs) if facs.count(f) > 1), default=1),
                     squarefree=len(set(facs)) == len(facs)))

json.dump(rows, open("./bfac.json", "w"), indent=1, default=str)

hdr = "run    cand  pub  p   |b|  Ω  ω  LPF  2nd  smooth  sqfree  b mod 3 4 5 7 8   factor bit lengths"
print(hdr)
for r in rows:
    m = r["mod"]
    print(f"{r['run']:6s} {r['i']:5d}  {'*' if r['pub'] else ' '}   {r['pbits']:3d} {r['bbits']:4d} {r['Omega']:2d} {r['omega']:2d} {r['lpf_bits']:4d} {r['second_bits']:4d} {r['smooth_bits']:6d}   {'y' if r['squarefree'] else 'n'}      {m[3]} {m[4]} {m[5]} {m[7]} {m[8]}   {[f.bit_length() for f in r['factors']]}")

def summ(key, label):
    pub = [r[key] for r in rows if r["pub"]]; sk = [r[key] for r in rows if not r["pub"]]
    print(f"{label:28s} published {sorted(pub)}  mean {sum(pub)/len(pub):.1f} | skipped {sorted(sk)}  mean {sum(sk)/len(sk):.1f}")
print()
summ("Omega", "Ω (with multiplicity)")
summ("omega", "ω (distinct)")
summ("lpf_bits", "LPF bits")
summ("smooth_bits", "smooth-part bits (b/LPF)")
summ("second_bits", "2nd-largest factor bits")
# per-run rank of LPF-bits (relative to field size)
print()
for run in ("P-256", "P-224", "192", "239"):
    rr = sorted((r for r in rows if r["run"] == run), key=lambda r: r["lpf_bits"])
    print(run, "by LPF bits:", [(r["i"], r["lpf_bits"], "*" if r["pub"] else "") for r in rr])
print()
print("square-free:", {"pub": sum(r["squarefree"] for r in rows if r["pub"]), "skip": sum(r["squarefree"] for r in rows if not r["pub"])})
for q in (3, 4, 5, 7, 8):
    print(f"b mod {q}: pub {[r['mod'][q] for r in rows if r['pub']]}  skip {[r['mod'][q] for r in rows if not r['pub']]}")
