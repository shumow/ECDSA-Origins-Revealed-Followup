# ECDSA Origins Revealed — follow-up

Analysis following Anthropic's Frontier Red Team post on the origins of the NIST/ANSI elliptic-curve seeds: the skipped candidates, and the K-163 generator.

Follow-up to Anthropic's ["Claude reveals ECDSA curve origins"](https://www.anthropic.com/research/ecdsa-curve-origins) (2026-10-16) and Filippo Valsorda's [reproduction](https://words.filippo.io/seeds-solved/).

**Result 1 (negative).** In the four prime-field seed runs, eleven earlier candidates give prime-order curves of the right size, yet eight later ones were published. Roughly fifty invariants of the nineteen curves and a dozen models of the generating program fail to separate the eleven from the eight. The skips are unexplained by any property of the curves.

**Result 2 (positive).** On K-163, half of the published generator has a 126-bit x-coordinate on a 163-bit curve (`0x3a5da90060df8af5be2121e601ae11f1`): a 2^-37 coincidence, or a 128-bit chosen value doubled into the prime-order subgroup.

**Also settled.** The 1997 program used b = (-27/c)^((p+1)/4) for p ≡ 3 mod 4 (7/7 published curves), and drew exactly 20 bytes of lrand48 output per candidate.

## Layout

| path | contents |
|---|---|
| `paper/` | LaTeX draft (`main.tex`, `tables.tex`); `latexmk -pdf main.tex` |
| `notes/cm-hypothesis.md` | full working record: results map, every test, every table |
| `notes/base-point-brief.md` | plan for the base-point provenance search (K-163 first) |
| `notes/cover.md` | set-cover search summary |
| `data/*.cands` | per run: candidate index, 20-byte seed, both roots of b (X9.62) |
| `data/*.orders2` | per run: verified group order of the published-root curve and its twist |
| `data/bincurves.json` | binary-curve parameters (from std-curves), verified by nG = O |
| `scripts/` | `gen.py` (regenerate candidates), `count2.gp` (verified SEA), `analyze*.py`, `battery.py`, `isog.gp`, `pts.gp`, `smooth.gp`, `cover.py`, `binpts.gp`/`.py` |
| `results/` | raw outputs behind every table |

## Reproducing

PARI/GP 2.10 built from source (github.com/jpflori/pari mirror) with no `seadata`; modular polynomials are computed on the fly. **Do not use `ellsea(E,1)` early-abort mode in that build** — it returned the twist's order for several curves; use `ellcard` and verify with `ellmul(E,P,n)==[0]`. Python 3 for everything else; no third-party packages.

```
python3 scripts/gen.py P-256          # candidates and b for a run
gp -q scripts/count2.gp               # orders (edit NAME / P at top)
python3 scripts/battery.py ANSI239    # invariant tables
python3 scripts/cover.py 300          # set-cover + permutation test
gp -q scripts/binpts.gp               # binary-curve generator scan
```

## License

Code: CC0 1.0. Text: CC BY 4.0.
