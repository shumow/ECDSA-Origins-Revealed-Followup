"""Set-cover search: is the skipped set a union of a few 'bug-shaped' predicates that exclude all published curves?
Then a permutation test: same search on random relabellings (per-run counts preserved)."""
import json, random, itertools, sys
from analyze2 import load

RUNS = {"P-256": (2**256-2**224+2**192+2**96-1, "P-256", [876, 1842], [1842]),
        "P-224": (2**224-2**96+1, "P-224", [777, 1485, 5736, 7026], [7026]),
        "192": (2**192-2**64-1, "ANSI192", [139, 2198, 5228, 5405, 6013], [139, 5228, 6013]),
        "239": (2**239-2**143-2**95+2**47-1, "ANSI239", [36, 1562, 2185, 2320, 2491, 2682, 2863, 3048], [2185, 2320, 3048])}

def leg(a, q):
    a %= q
    if a == 0: return 0
    return 1 if pow(a, (q-1)//2, q) == 1 else -1

curves = []
for run, (p, f, ids, pub) in RUNS.items():
    d = load(f); cands = {int(l.split()[0]): (bytes.fromhex(l.split()[1]), int(l.split()[2])) for l in open(f + ".cands")}
    for i in ids:
        seed, b = cands[i]; n, m = d[i]; t = p + 1 - n
        curves.append(dict(run=run, i=i, pub=i in pub, p=p, n=n, t=t, b=b, seed=seed, m=m))

# ---- predicate library (each a function curve -> bool) ----
P = {}
for byte, name in ((0x00, "00"), (0xFF, "FF"), (0x0A, "0A"), (0x0D, "0D"), (0x20, "20"), (0x09, "09"), (0x1A, "1A"), (0x7F, "7F")):
    P[f"seed has byte 0x{name}"] = (lambda bb: lambda c: bb in c['seed'])(byte)
P["seed first byte >= 0x80"] = lambda c: c['seed'][0] >= 0x80
P["seed first byte < 0x80"] = lambda c: c['seed'][0] < 0x80
P["seed first byte == 0"] = lambda c: c['seed'][0] == 0
P["seed last byte even"] = lambda c: c['seed'][-1] % 2 == 0
P["seed last byte odd"] = lambda c: c['seed'][-1] % 2 == 1
P["seed last byte >= 0x80"] = lambda c: c['seed'][-1] >= 0x80
P["seed has >= 12 bytes >= 0x80"] = lambda c: sum(1 for x in c['seed'] if x >= 0x80) >= 12
P["seed has <= 7 bytes >= 0x80"] = lambda c: sum(1 for x in c['seed'] if x >= 0x80) <= 7
P["seed has a byte < 0x10"] = lambda c: any(x < 0x10 for x in c['seed'])
P["seed has two equal adjacent bytes"] = lambda c: any(c['seed'][k] == c['seed'][k+1] for k in range(19))
P["seed bitlength < 160"] = lambda c: int.from_bytes(c['seed'], 'big').bit_length() < 160
P["seed bitlength < 158"] = lambda c: int.from_bytes(c['seed'], 'big').bit_length() < 158
P["n > p"] = lambda c: c['n'] > c['p']
P["n < p"] = lambda c: c['n'] < c['p']
P["t < 0"] = lambda c: c['t'] < 0
P["bitlen(n) < bitlen(p)"] = lambda c: c['n'].bit_length() < c['p'].bit_length()
P["bitlen(b) < bitlen(p)"] = lambda c: c['b'].bit_length() < c['p'].bit_length()
P["bitlen(b) < bitlen(p)-1"] = lambda c: c['b'].bit_length() < c['p'].bit_length() - 1
P["b > p/2"] = lambda c: c['b'] > c['p'] // 2
P["b < p/2"] = lambda c: c['b'] < c['p'] // 2
P["b even"] = lambda c: c['b'] % 2 == 0
P["b odd"] = lambda c: c['b'] % 2 == 1
P["b top byte == 0"] = lambda c: (c['b'] >> (c['p'].bit_length() - 8)) == 0
P["b has a 0x00 byte"] = lambda c: 0 in c['b'].to_bytes((c['p'].bit_length() + 7)//8, 'big')
P["(b/p) = -1 (no point at x=0)"] = lambda c: leg(c['b'], c['p']) == -1
P["(b/p) = +1"] = lambda c: leg(c['b'], c['p']) == 1
P["bitlen(t) < bitlen(p)/2"] = lambda c: c['t'].bit_length() < c['p'].bit_length() // 2
P["bitlen(t) < bitlen(p)/2 - 1"] = lambda c: c['t'].bit_length() < c['p'].bit_length() // 2 - 1
for mod in (3, 4, 5, 7, 8, 16):
    for r in range(mod):
        for nm, key in (("n", 'n'), ("t", 't'), ("b", 'b')):
            P[f"{nm} ≡ {r} mod {mod}"] = (lambda kk, mm, rr: lambda c: c[kk] % mm == rr)(key, mod, r)
P["n-1 has factor 3"] = lambda c: (c['n'] - 1) % 3 == 0
P["n+1 has factor 3"] = lambda c: (c['n'] + 1) % 3 == 0
P["twist order even (always) and ≡ 0 mod 3"] = lambda c: (2*c['p'] + 2 - c['n']) % 3 == 0
P["twist order ≡ 0 mod 5"] = lambda c: (2*c['p'] + 2 - c['n']) % 5 == 0
P["D ≡ 0 mod 9 (s>1)"] = lambda c: (c['t']**2 - 4*c['p']) % 9 == 0
P["D ≡ 0 mod 25"] = lambda c: (c['t']**2 - 4*c['p']) % 25 == 0
P["(-3/n) = -1"] = lambda c: leg(-3, c['n']) == -1
P["(n/p) = -1"] = lambda c: leg(c['n'], c['p']) == -1
P["(p/n) = -1"] = lambda c: leg(c['p'], c['n']) == -1
P["(t/p) = -1"] = lambda c: leg(c['t'], c['p']) == -1
P["(2/n) = -1"] = lambda c: leg(2, c['n']) == -1
P["index even"] = lambda c: c['i'] % 2 == 0
P["index odd"] = lambda c: c['i'] % 2 == 1
P["index ≡ 0 mod 3"] = lambda c: c['i'] % 3 == 0
P["index < 1000"] = lambda c: c['i'] < 1000
P["20(i-1) mod 4096 < 1024"] = lambda c: (20*(c['i']-1)) % 4096 < 1024

M = {name: [bool(f(c)) for c in curves] for name, f in P.items()}
# drop constant predicates
M = {k: v for k, v in M.items() if any(v) and not all(v)}
names = sorted(M)

def min_cover(labels, maxk=4):
    """labels: list of bool (True = skipped). Return (size, covers) minimal unions of predicates
    that are false on every published curve and together true on every skipped curve."""
    skipped = [j for j, s in enumerate(labels) if s]; published = [j for j, s in enumerate(labels) if not s]
    usable = [nm for nm in names if not any(M[nm][j] for j in published)]
    for k in range(1, maxk + 1):
        covers = []
        for combo in itertools.combinations(usable, k):
            if all(any(M[nm][j] for nm in combo) for j in skipped): covers.append(combo)
        if covers: return k, covers, usable
    return None, [], usable

true_labels = [not c['pub'] for c in curves]
k, covers, usable = min_cover(true_labels, maxk=5)
out = {"n_predicates_total": len(names), "n_usable_true_labels": len(usable), "usable": usable,
       "true_min_cover_size": k, "true_covers": [list(c) for c in covers[:50]], "n_true_covers_at_min": len(covers)}
# near misses: best coverage with 1 and 2 predicates
sk = [j for j, s in enumerate(true_labels) if s]
best1 = sorted(((sum(M[nm][j] for j in sk), nm) for nm in usable), reverse=True)[:8]
out["best_single_usable_predicates(cover count of 11)"] = best1
# per-predicate stats on true labels for the record
out["predicate_table"] = {nm: {"skipped_true": sum(M[nm][j] for j in sk), "published_true": sum(M[nm][j] for j in range(len(curves)) if not true_labels[j])} for nm in names}

# ---- permutation test ----
random.seed(1)
runs_idx = {}
for j, c in enumerate(curves): runs_idx.setdefault(c['run'], []).append(j)
NPERM = int(sys.argv[1]) if len(sys.argv) > 1 else 300
dist = {}
for _ in range(NPERM):
    lab = [None]*len(curves)
    for run, js in runs_idx.items():
        npub = sum(1 for j in js if curves[j]['pub']); pubs = set(random.sample(js, npub))
        for j in js: lab[j] = j not in pubs
    kk, cv, us = min_cover(lab, maxk=5)
    dist[str(kk)] = dist.get(str(kk), 0) + 1
out["permutation_test"] = {"n_perm": NPERM, "min_cover_size_distribution": dist}
json.dump(out, open("cover.json", "w"), indent=1, default=str)

with open("cover.md", "w") as f:
    f.write(f"# Set-cover search for the skipped-seed criterion\n\n{len(names)} non-constant predicates; {len(usable)} are false on all 8 published curves and so usable in a cover.\n\n")
    f.write(f"**True labelling:** minimal cover size = {k}; {len(covers)} distinct minimal covers. Examples:\n\n")
    for c in covers[:12]: f.write(f"- {' ∪ '.join(c)}\n")
    f.write("\nBest single usable predicates (how many of the 11 skipped each covers):\n\n")
    for cnt, nm in best1: f.write(f"- {cnt}/11  {nm}\n")
    f.write(f"\n**Permutation test** ({NPERM} random relabellings preserving per-run published counts): distribution of minimal cover size\n\n")
    for kk in sorted(dist, key=lambda x: (x == 'None', x)): f.write(f"- size {kk}: {dist[kk]} ({100*dist[kk]/NPERM:.1f}%)\n")
print(open("cover.md").read())
