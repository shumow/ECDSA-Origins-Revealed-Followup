# The seeds are solved. The curves aren't done.

*A follow-up to Anthropic's [Claude reveals ECDSA curve origins](https://www.anthropic.com/research/ecdsa-curve-origins) and Filippo Valsorda's [reproduction](https://words.filippo.io/seeds-solved/). The Anthropic result is one product of the Frontier Red Team's [model-assisted cryptanalysis programme](https://www.anthropic.com/research/discovering-cryptographic-weaknesses), whose authors name independent human validation as their bottleneck. Consider this some of that.*

*Readers should take this as the next chapter, not the closing one. There is still no action to take on the NIST curves. There is, however, more to find.*

---

On 16 October 2026 a 25-year-old question closed: the `SEED` values behind the NIST and ANSI X9.62 elliptic curves are not hashes of a joke about Jerry Solinas's salary. They are raw `lrand48()` output, seeded from the Unix clock, drawn 20 bytes at a time until a candidate produced a usable curve. P-256 is candidate 1842 of a run started at 01:52:34 UTC on 16 August 1997.

Both write-ups left a residue. Each run produced *earlier* candidates that also give prime-order curves of the right size and pass every documented check — and the program passed them over. Candidate 876 of the P-256 run is such a curve; so are three in the P-224 run and seven across the two ANSI X9.62 runs. Valsorda: "roughly twice as many valid seeds as were published," rejected by a second undocumented criterion that "still escapes us."

This repository is what happened when we went looking for that criterion — and what we found instead.

## What we did

We regenerated all four prime-field runs, verified every group order independently (full SEA, then $n \cdot P = O$ on random points), and confirmed the published-vs-skipped lists match Anthropic's and Valsorda's exactly: **8 published curves, 11 skipped but viable.**

Then we tested a broad collection of properties of those 19 curves, including checks available in 1997 and some more expensive ones:

| Family | What we checked | Separates published from skipped? |
|---|---|---|
| Arithmetic of *n*, *t* | twist order, complete factorizations of *n* ± 1, congruences | No |
| CM structure | discriminant *t*² − 4*p*, conductor, class number with *L*(1, χ) | No — the published P-224 has the *smallest* class number in its run; the published P-256 the *largest* |
| Isogenies over 𝔽<sub>*p*</sub> | End(*E*), volcano position, rational ℓ-isogenies for ℓ ≤ 43 | No — P-224 is on a 3-volcano crater; prime239 candidates 2320 and 2682 are on 5-volcano floors |
| Isogenies over 𝔽<sub>*p*<sup>*k*</sup></sub> | volcano heights for ℓ ≤ 47, *k* ∈ {2, 3, 4, 6, 12} | No |
| Extension-field orders | #*E*(𝔽<sub>*p*<sup>*k*</sup></sub>)/*n* smoothness, *k* ≤ 12 | No |
| Embedding degree | ord<sub>*n*</sub>(*p*) | No — > 20,000 for every candidate; exact values available for some |
| gcd(*p* ± 1, *n* ± 1) | values, odd parts, largest prime factors, per-run ranking | No — flips direction between runs |
| Symbols and residues | nine Legendre symbols; *n*, *p*, *t* mod 4, 8 | No — the published curves disagree *with each other* |
| Point structure | smallest on-curve *x*, 256-bit on-curve bitmaps, small-scalar relations | No separator found; the square-root convention forces a point at *x* = 0 in the *p* ≡ 3 (mod 4) runs |

Then we modelled the program instead of the curve: eleven simulated early-abort bugs (sign flips, wrong root, off-by-one, trace-instead-of-order), an Elkies/Atkin proxy for counting cost, index-dependent bugs, mangled seed bytes, a failing base-point step, and sorted human choice. **None of the tested rules fits.** Finally we asked whether the eleven could be a *union* of several small defects, via exhaustive set cover over 135 predicates: the real labelling needs a four-predicate cover. An exact comparison preserving each run's published count and keeping its final candidate published admits covers of size at most four in **88 of 126 relabellings (69.8%)**. The earlier exploratory count-only, 300-sample comparison gave 35%.

**No tested rule separates the eleven skipped curves from the eight published ones.** This is an exploratory negative result on nineteen curves, not a proof that no numerical criterion exists. A point counter that sometimes gave up or a human choice remains plausible, as do untested numerical rules, different code between runs, and more general RNG-consumption models.

Two constraints on the program *did* come out of the sweep:

- For every published curve over *p* ≡ 3 (mod 4), *b* = (−27/*c*)<sup>(*p*+1)/4</sup> mod *p*. Seven for seven. Using this textbook root reproduces the source posts' candidate lists; accepting either root adds 23 candidates across the three runs. The matches do not prove that the original program never tested the other root.
- The published seeds align with the 20-draw candidate stream. This constrains *cumulative* extra RNG consumption at published checkpoints, not each individual event: an extra draw followed later by nineteen extra draws could restore alignment.

## What we found instead

The seeds are explained. The **base points** mostly are not: Anthropic recovered P-192 and the ANSI example generators from FreeLIP's `zrandom`, and found nothing for P-224, P-256, P-384, P-521 or any binary curve.

We computed small multiples and subgroup inverse-multiples of every published generator — *k*·*G* up to 2¹⁶, and *G*/*k* up to 2¹⁶ on prime-field curves or 2¹² on binary curves — looking for a hash-sized coordinate. On the ten prime-field curves: no such hit. The reported minimum *x*-coordinates are within two bits of the rough random-minimum expectation.

On the binary curves, nine of ten are likewise random. **K-163 is not.** Halving its generator gives

```
G/2 :  x = 0x23e21d6019e1211f6bd47ec180256e97     (126 bits on a 163-bit curve)
       y = full size (161 bits)
```

Under a uniform-coordinate heuristic, a specified *x*-coordinate being at most 126 bits has probability 2<sup>−37</sup>. The binary scan evaluated **69,630 points per curve, 696,300 across ten curves**, giving about 5.1 × 10<sup>−6</sup> expected *x*-hits. Including the prime-field scans, both signs of *y*, and the exploratory choice of which pattern to report requires a broader look-elsewhere assessment; this is not a calibrated discovery probability.

A plausible reading: K-163 is a Koblitz curve, *y*² + *xy* = *x*³ + *x*² + 1, with no seed at all — the generator is its only randomly chosen parameter. Someone may have picked a 128-bit *x*, solved for *y*, and multiplied by the cofactor 2. We have not identified the value or established that procedure. It is not four consecutive 31-bit `lrand48` words.

**Coordinate correction (19 October).** The original PARI export reversed the polynomial coefficients before interpreting them as a binary integer. The shortness calculation was correct, but the printed value and hash-search target were not. The earlier negative hash searches therefore do not apply to the corrected target above. The conversion, all ten exported half-point coordinates, and the search target are corrected here; regression tests compare Python and PARI arithmetic.

The short coordinate is a concrete provenance lead, not an identified construction or an established novelty claim. Also, *G*/*h* denotes only the inverse inside the prime-order subgroup. Cofactor clearing can start from any *P* with [*h*]*P* = *G*; these form a torsion coset. Checking all rational cofactor preimages on all ten binary curves leaves K-163 as the only 128-bit-*x* hit. Its other half has a 162-bit *x*.

## What this means

Nothing here demonstrates a weakness in these curves. The skipped-candidate investigation finds no evidence of selection by the tested properties. Failure to distinguish nineteen curves is not proof of statistical identity or evidence against an arbitrary untested hidden property.

If the corrected K-163 value turns out to come from a reproducible recipe, it could explain that generator. It would not by itself explain or date all the other binary-curve generators.

## In this repository

| | |
|---|---|
| [`paper/`](paper/) | LaTeX draft of the write-up (`latexmk -pdf main.tex`) |
| [`notes/cm-hypothesis.md`](notes/cm-hypothesis.md) | the full working record — every test, every table, every dead end |
| [`notes/base-point-brief.md`](notes/base-point-brief.md) | the plan for the base-point search, K-163 first |
| [`data/`](data/) | every candidate's seed and *b*; every verified group order; verified binary-curve parameters |
| [`scripts/`](scripts/) | regenerate, count, analyze — Python 3 and PARI/GP, no other dependencies |
| [`results/`](results/) | raw outputs behind every number above |

**One warning for reproducers.** We built PARI/GP 2.10 from source without `seadata`. Its `ellsea(E,1)` early-abort mode returned the *twist's* order for several curves in that build. Use `ellcard` and check `ellmul(E,P,n)==[0]`.

### Review regression checks

From the repository root, run:

```text
python -X utf8 -m unittest discover -s scripts -p test_research.py -v
python -X utf8 scripts/cover.py
```

Put PARI/GP on `PATH`, or set `GP` to its executable path, to include the cross-language coordinate, cofactor-preimage, and prime-order checks. Without GP those tests are explicitly skipped. The test suite checks all nineteen viable prime orders using primality, the Hasse bound, and a nonzero point killed by the claimed order; it does not repeat SEA for all 3,072 counted candidates. `cover.py` regenerates `results/cover.json` and `notes/cover.md` with the exact, endpoint-conditioned null.

The raw binary scan's coordinate exports have been recomputed; its long-scan minima are retained from the original run because the conversion error did not affect polynomial degrees. The full phrase/hash search has not yet been rerun against the corrected target.

## Open questions

1. **The 128-bit value behind K-163's *G*/2.** Hash preimage over 1997-era phrases, encodings and hash functions, or an RNG stream. This is the one with a concrete target.
2. **The other base points.** P-224/256/384/521, the five B curves, the four other K curves. Compare complete cofactor-preimage sets, field encodings, hash expansions, and RNG layouts; a negative subgroup-only scan is not a general exclusion of cofactor clearing.
3. **The B-163 seed**, which fits no generator Anthropic tried.
4. **The eleven skips.** Seek archival code and printouts, but also test explicit variable-consumption state machines and historically plausible, run-specific point-counter behaviour. The present tests do not exhaust those possibilities.

## Who

Dan Shumow. Computation and drafting with Claude (Anthropic). Thanks to Nadia Heninger for the half-point idea, and to the Anthropic Frontier Red Team and Filippo Valsorda for leaving such a well-marked trail.

Code CC0 1.0; text CC BY 4.0.
