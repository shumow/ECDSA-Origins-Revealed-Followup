import sys, math
from pathlib import Path
from analyze import is_probable_prime, square_part, small_factors, embedding_degree_info

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

def load(name):
    path = DATA_DIR / f"{name}.orders2"
    out = {}; seen = set(); done = False
    with open(path) as source:
        for lineno, line in enumerate(source, 1):
            f = line.split()
            if not f: continue
            if done: raise ValueError(f"{path}:{lineno}: record after DONE")
            if f == ["DONE"]:
                done = True; continue
            if len(f) < 2 or f[1] == "FAIL":
                raise ValueError(f"{path}:{lineno}: invalid or failed point count: {line.strip()}")
            i = int(f[0])
            if i in seen: raise ValueError(f"{path}:{lineno}: duplicate candidate {i}")
            seen.add(i)
            if f[1:] == ["even"]: continue
            if len(f) != 4 or f[3] not in ("ok", "signfix"):
                raise ValueError(f"{path}:{lineno}: unverified point count: {line.strip()}")
            out[i] = (int(f[1]), int(f[2]))
    if not done: raise ValueError(f"{path}: incomplete point-count log (missing DONE)")
    return out

def describe(p, i, n, published, label):
    bits = p.bit_length()
    t = p + 1 - n; D = t*t - 4*p; s, f = square_part(D)
    ntw = 2*p + 2 - n; twf, twcof = small_factors(ntw)
    k, note = embedding_degree_info(n, p)
    kstr = ("2^%.1f" % math.log2(k)) if k else note
    return (f"{i:>5} {label:>6} {'*' if i == published else '':>3} "
            f"{'ok' if n.bit_length() <= bits else 'BIG':>4} {'+' if t > 0 else '-':>3} "
            f"{s:>6} {math.log2(math.sqrt(abs(f))):>8.1f} {D % 4:>4} {D % 9:>4} {D % 25:>4} "
            f"{kstr:>10} {str(twf[:5]):>28} {twcof.bit_length():>6} {str(is_probable_prime(twcof) if twcof > 1 else True):>6}")

HDR = (f"{'cand':>5} {'curve':>6} {'pub':>3} {'size':>4} {'t':>3} {'s':>6} {'log2h~':>8} {'D%4':>4} {'D%9':>4} {'D%25':>4} "
       f"{'emb deg':>10} {'twist small factors':>28} {'cofbit':>6} {'cofpr':>6}")

def run(name, p, published, twist_is_candidate):
    data = load(name)
    print(f"\n=== {name} ({p.bit_length()}-bit p): {len(data)} candidates without 2-torsion counted; "
          f"generic log2 h ~ {math.log2(math.sqrt(4*p)):.1f} ===")
    print(HDR)
    rows = []
    for i, (n, m) in sorted(data.items()):
        if is_probable_prime(n): rows.append((i, n, "b_pub" if twist_is_candidate else "b"))
        if twist_is_candidate and is_probable_prime(m): rows.append((i, m, "-b"))
    for i, n, lab in rows: print(describe(p, i, n, published, lab))
    # summary stats over all counted candidates: how common is s>1?
    svals = [square_part((p+1-n)**2 - 4*p)[0] for n, _ in data.values()]
    print(f"\nAmong all {len(svals)} counted candidates: fraction with square divisor s>1 of D: "
          f"{sum(1 for s in svals if s > 1)/len(svals):.3f}; s>=3: {sum(1 for s in svals if s >= 3)/len(svals):.3f}")

if __name__ == "__main__":
    run("P-256", 2**256-2**224+2**192+2**96-1, 1842, True)    # p ≡ 3 mod 4: -b is the quadratic twist
    run("P-224", 2**224-2**96+1, 7026, False)                  # p ≡ 1 mod 4: -b is isomorphic to b
