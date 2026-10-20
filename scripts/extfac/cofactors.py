"""Write the cubic, quartic and sextic cofactors of the extension-field orders for the 19 viable candidates."""
import sys; sys.path.insert(0, "..")
import cover
def ords(p, t, K):
    tk = {0: 2, 1: t}
    for k in range(2, K + 1): tk[k] = t * tk[k - 1] - p * tk[k - 2]
    return {k: p**k + 1 - tk[k] for k in range(1, K + 1)}
with open("cof.txt", "w") as f:
    for c in cover.curves:
        p, n, t = c["p"], c["n"], c["t"]; o = ords(p, t, 6)
        C3 = o[3] // n; C4 = o[4] // o[2]; C6 = o[6] * n // (o[3] * o[2])
        assert C3 * n == o[3] and C4 * o[2] == o[4] and C4 == (p - 1)**2 + t * t and C6 * o[3] * o[2] == o[6] * n
        for k, C in ((3, C3), (4, C4), (6, C6)):
            f.write(f"{c['run']} {c['i']} {'pub' if c['pub'] else 'skip'} {k} {C}\n")
