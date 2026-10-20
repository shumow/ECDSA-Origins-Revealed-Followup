import json, glob, sys
rows = []
for f in sorted(glob.glob("./ext[0-9].json")):
    rows += json.load(open(f))
assert len(rows) == 57, len(rows)
rows.sort(key=lambda r: (["P-256", "P-224", "192", "239"].index(r["run"]), r["k"], r["i"]))
json.dump(rows, open("./extfac.json", "w"), indent=1)

print("Cofactors of extension orders after dividing out subfield orders:")
print("  k=3: #E(F_p^3)/n   k=4: #E(F_p^4)/#E(F_p^2) = (p-1)^2 + t^2   k=6: #E(F_p^6) n / (#E(F_p^3) #E(F_p^2))")
print("ECM effort per number: trial division to 10^6, 280 curves at B1=50000 (t25), 215 curves at B1=250000 (half t30).")
print("'found' = bits of prime factors found, 'rem' = bits of the unfactored remainder, P/C = prime/composite, 1 = fully factored.\n")
for k in (3, 4, 6):
    print(f"--- k={k}")
    print("run    cand pub  bits  smooth(<2^40) bits  found factor bits                       rem   LPF-found bits")
    for r in rows:
        if r["k"] != k: continue
        fb = r["factor_bits"]
        sm = sum(b for b in fb if b <= 40)
        rem = f"{r['cofactor_bits']}{'P' if r['cofactor_prime'] else 'C'}" if r["cofactor_bits"] else "1"
        print(f"{r['run']:6s} {r['i']:5d}  {'*' if r['pub'] else ' '}   {r['bits']:3d}   {sm:4d}                {str(fb):40s} {rem:5s} {max(fb) if fb else 0}")
    print()
    for lab, sel in (("published", True), ("skipped", False)):
        rs = [r for r in rows if r["k"] == k and r["pub"] == sel]
        sm = sorted(sum(b for b in r["factor_bits"] if b <= 40) for r in rs)
        big = sorted(max(r["factor_bits"] + [0]) for r in rs)
        pr = sum(1 for r in rs if r["cofactor_prime"])
        print(f"  {lab:9s} smooth-part bits {sm}; largest found factor bits {big}; prime remainder in {pr}/{len(rs)}")
    print()
