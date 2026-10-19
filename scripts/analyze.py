import sys, math, random
from math import isqrt, gcd

def is_probable_prime(n, k=20):
    if n < 2: return False
    for q in (2,3,5,7,11,13,17,19,23,29,31,37):
        if n % q == 0: return n == q
    d, s = n-1, 0
    while d % 2 == 0: d //= 2; s += 1
    for _ in range(k):
        a = random.randrange(2, n-1); x = pow(a, d, n)
        if x in (1, n-1): continue
        for _ in range(s-1):
            x = x*x % n
            if x == n-1: break
        else: return False
    return True

SMALL = []
def sieve(B):
    s = bytearray([1])*(B+1); s[0]=s[1]=0
    for i in range(2, isqrt(B)+1):
        if s[i]: s[i*i::i] = bytearray(len(s[i*i::i]))
    return [i for i in range(B+1) if s[i]]
SMALL = sieve(10**6)

def square_part(D):
    """Return (s, f) with D = f*s^2, s built from primes < 1e6 plus perfect-square cofactor.
    f has the discriminant congruence, but is only a candidate fundamental discriminant:
    an unfactored cofactor can still hide a square prime factor."""
    n = abs(D); s = 1; m = n
    for q in SMALL:
        if q*q > m: break
        e = 0
        while m % q == 0: m //= q; e += 1
        s *= q ** (e//2)
    r = isqrt(m)
    if r*r == m and m > 1: s *= r; m = 1
    f = -(n // (s*s))
    # make fundamental: if f ≡ 2,3 mod 4 then true fundamental disc is 4f
    if f % 4 in (2, 3): f *= 4; s //= 2
    return s, f

def small_factors(n, B=10**6):
    fs = []; m = n
    for q in SMALL:
        if q*q > m: break
        while m % q == 0: fs.append(q); m //= q
    return fs, m

def embedding_degree_info(n, p):
    """Embedding degree k = ord_n(p). k | n-1. Return k if n-1 factors fully with small primes
    + probable prime cofactor, else a lower bound from the small part."""
    fs, m = small_factors(n-1)
    cof_prime = m == 1 or is_probable_prime(m)
    primes = sorted(set(fs)) + ([m] if m > 1 else [])
    if not cof_prime:
        # k | n-1 and k is a multiple of every prime q with p^((n-1)/q) != 1; give a lower bound instead
        x = 1
        for i in range(1, 20001):
            x = x * p % n
            if x == 1: return i, "exact"
        return None, "> 20000"
    k = n-1
    for q in primes:
        while k % q == 0 and pow(p, k//q, n) == 1: k //= q
    return k, "exact"

def main(name, p, published_idx):
    orders = {}
    for line in open(f"{name}.orders"):
        if line.startswith("DONE"): continue
        i, n1, n2 = map(int, line.split()); orders[i] = (n1, n2)
    bits = p.bit_length()
    rows = []
    for i, (n1, n2) in sorted(orders.items()):
        for root, n in ((1, n1), (2, n2)):
            if n and is_probable_prime(n):
                size_ok = n.bit_length() <= bits
                t = p + 1 - n; D = t*t - 4*p; s, f = square_part(D)
                ntw = 2*p + 2 - n
                twf, twcof = small_factors(ntw)
                k, note = embedding_degree_info(n, p)
                rows.append(dict(idx=i, root=root, n=n, size_ok=size_ok, t=t, D=D, s=s, f=f,
                                 logh=math.log2(math.sqrt(abs(f))), k=k, knote=note,
                                 tw_small=twf, tw_cof_bits=twcof.bit_length(),
                                 tw_cof_prime=is_probable_prime(twcof) if twcof > 1 else True))
    print(f"\n=== {name}: p is {bits} bits, {len(orders)} candidates with valid b, "
          f"{len(rows)} prime-order curves found (counting both roots) ===")
    print(f"generic log2 h ~ log2 sqrt(4p) = {math.log2(math.sqrt(4*p)):.1f}\n")
    hdr = f"{'cand':>5} {'root':>4} {'pub':>3} {'size':>4} {'t sign':>6} {'s':>8} {'log2 h~':>8} {'D mod 4':>7} {'D mod 9':>7} {'emb deg':>10} {'twist small factors':>22} {'tw cof bits':>11} {'tw cof prime':>12}"
    print(hdr)
    for r in rows:
        k = r['k']; kstr = ("2^%.1f" % math.log2(k)) if k else ">2e4"
        print(f"{r['idx']:>5} {r['root']:>4} {'*' if r['idx']==published_idx else '':>3} "
              f"{'ok' if r['size_ok'] else 'BIG':>4} {'+' if r['t']>0 else '-':>6} {r['s']:>8} {r['logh']:>8.1f} "
              f"{r['D']%4:>7} {r['D']%9:>7} {kstr:>10} {str(r['tw_small'][:6]):>22} {r['tw_cof_bits']:>11} {str(r['tw_cof_prime']):>12}")
    return rows

if __name__ == "__main__":
    name = sys.argv[1]
    P = {"P-256": (2**256-2**224+2**192+2**96-1, 1842), "P-224": (2**224-2**96+1, 7026)}[name]
    main(name, *P)
