"""Full battery on one run: viable candidates (published-root prime & size ok), twist-root primes,
discriminant square part, L(1,chi) estimate, n±1 factorization, isogeny root counts, last-viable test."""
import sys, math, subprocess, os
from analyze2 import load
from analyze import is_probable_prime, square_part, SMALL

GP = "/home/claude/src/pari/gp"; ENV = dict(os.environ, LD_LIBRARY_PATH="/home/claude/src/pari/Olinux-x86_64")

def kron(D, q):
    if q == 2: return 0 if D % 2 == 0 else (1 if D % 8 in (1, 7) else -1)
    l = pow(D % q, (q-1)//2, q); return 0 if l == 0 else (1 if l == 1 else -1)

def L1(f, B=10**6):
    L = 1.0
    for q in SMALL:
        if q > B: break
        L *= 1/(1 - kron(f, q)/q)
    return L

def gp(script):
    r = subprocess.run([GP, "-q", "-s", "1000000000"], input=script + "\nquit\n", capture_output=True, text=True, env=ENV, timeout=3600)
    return [l for l in r.stdout.splitlines() if not l.startswith("  ***")]

def run(name, p, published):
    data = load(name); cands = {int(l.split()[0]): int(l.split()[2]) for l in open(f"{name}.cands")}
    bits = p.bit_length()
    viable = [(i, n) for i, (n, m) in sorted(data.items()) if is_probable_prime(n) and n.bit_length() <= bits]
    bigs = [i for i, (n, m) in sorted(data.items()) if is_probable_prime(n) and n.bit_length() > bits]
    twist_primes = [i for i, (n, m) in sorted(data.items()) if is_probable_prime(m) and m.bit_length() <= bits]
    print(f"\n=== {name}: {bits}-bit p, {len(data)} candidates counted (no 2-torsion) ===")
    print(f"viable (published root, prime, size ok): {[i for i,_ in viable]}   published: {published}")
    print(f"skipped viable: {[i for i,_ in viable if i not in published]}")
    print(f"prime-order but too big (rejected by size rule): {bigs}")
    print(f"other-root (twist) prime & size ok, not counted by anyone: {twist_primes}")
    # last-viable test
    print(f"last viable candidate of run = {viable[-1][0]} -> published? {viable[-1][0] in published}")
    rows = []
    for i, n in viable:
        t = p + 1 - n; D = t*t - 4*p; s, f = square_part(D); L = L1(f)
        rows.append((i, n, t, s, f, L))
    print(f"\n{'cand':>5} {'pub':>3} {'s':>4} {'log2sqrt|f|':>11} {'L(1,chi)':>8} {'log2 h':>7}   (generic log2 h ~ {math.log2(math.sqrt(4*p)):.1f})")
    for i, n, t, s, f, L in rows:
        print(f"{i:>5} {'*' if i in published else '':>3} {s:>4} {math.log2(math.sqrt(abs(f))):>11.1f} {L:>8.3f} {math.log2(math.sqrt(abs(f))*L/math.pi):>7.1f}")
    # n±1 factorization and isogeny counts via PARI
    sc = ['rep(lab,x)={my(F=factor(x),k=#F[,1]); print(lab," LPF bits ",#binary(F[k,1]),"  factors bits ",vector(k,j,#binary(F[j,1])))};',
          'rc(l,j,p)={my(Ph=polmodular(l,0), f=subst(Ph,y,Mod(j,p))); #polrootsmod(lift(f),p)};']
    for i, n, t, s, f, L in rows:
        b = cands[i]
        sc.append(f'print("## {i}"); n={n}; rep("n-1",n-1); rep("n+1",n+1); p={p}; b={b}; j=lift(Mod(-6912,p)/Mod(b^2-4,p)); st=""; forprime(l=2,43, st=Str(st," ",l,":",rc(l,j,p))); print("isog",st); print("twist small factors ", factor(2*p+2-n, 10^6)[,1]~);')
    for line in gp("\n".join(sc)): print(line)

if __name__ == "__main__":
    name = sys.argv[1]
    cfg = {"ANSI192": (2**192-2**64-1, [139, 5228, 6013]), "ANSI239": (2**239-2**143-2**95+2**47-1, [2185, 2320, 3048])}
    run(name, *cfg[name])
