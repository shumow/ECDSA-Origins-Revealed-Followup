# The seeds are solved. The curves aren't done.

*A follow-up to Anthropic's [Claude reveals ECDSA curve origins](https://www.anthropic.com/research/ecdsa-curve-origins) and Filippo Valsorda's [reproduction](https://words.filippo.io/seeds-solved/). The Anthropic result is one product of the Frontier Red Team's [model-assisted cryptanalysis programme](https://www.anthropic.com/research/discovering-cryptographic-weaknesses), whose authors name independent human validation as their bottleneck. Consider this some of that.*

*Readers should take this as the next chapter, not the closing one. There is still no action to take on the NIST curves. There is, however, more to find.*

---

On 16 October 2026 a 25-year-old question closed: the `SEED` values behind the NIST and ANSI X9.62 elliptic curves are not hashes of a joke about Jerry Solinas's salary. They are raw `lrand48()` output, seeded from the Unix clock, drawn 20 bytes at a time until a candidate produced a usable curve. P-256 is candidate 1842 of a run started at 01:52:34 UTC on 16 August 1997.

Both write-ups left a residue. Each run produced *earlier* candidates that also give prime-order curves of the right size and pass every documented check — and the program passed them over. Candidate 876 of the P-256 run is such a curve; so are three in the P-224 run and seven across the two ANSI X9.62 runs. Valsorda: "roughly twice as many valid seeds as were published," rejected by a second undocumented criterion that "still escapes us."

This repository is what happened when we went looking for that criterion — and what we found instead.

## What we did

We regenerated all four prime-field runs, computed the retained orders with SEA and checked $n \cdot P = O$ on random points. The nineteen viable prime orders also have independent primality/Hasse/scalar-multiplication certificates. The published-vs-skipped lists match Anthropic's and Valsorda's exactly: **8 published curves, 11 skipped but viable.**

Then we tested a broad collection of properties of those 19 curves, including checks available in 1997 and some more expensive ones:

| Family | What we checked | Separates published from skipped? |
|---|---|---|
| Arithmetic of *n*, *t* | twist order, complete factorizations of *n* ± 1, congruences | No |
| Arithmetic of *b* | complete factorizations, square-freeness, residues; both P-224 signs retained | No tested separator; the skipped P-224 sign convention is unknown |
| CM structure | discriminant *t*² − 4*p*, conductor, class number with *L*(1, χ) | No — the published P-224 has the *smallest* class number in its run; the published P-256 the *largest* |
| Isogenies over 𝔽<sub>*p*</sub> | End(*E*), volcano position, rational ℓ-isogenies for ℓ ≤ 43 | No — P-224 is on a 3-volcano crater; prime239 candidates 2320 and 2682 are on 5-volcano floors |
| Isogenies over 𝔽<sub>*p*<sup>*k*</sup></sub> | volcano heights for ℓ ≤ 47, *k* ∈ {2, 3, 4, 6, 12} | No |
| Extension-field orders | trial division through *k* = 12; validated partial factors for cubic, quartic and sextic pieces | No established separator; legacy ECM coverage is unverified |
| Embedding degree | ord<sub>*n*</sub>(*p*) | No — > 20,000 for every candidate; exact values available for some |
| gcd(*p* ± 1, *n* ± 1) | values, odd parts, largest prime factors, per-run ranking | No — flips direction between runs |
| Symbols and residues | nine Legendre symbols; *n*, *p*, *t* mod 4, 8 | No — the published curves disagree *with each other* |
| Point structure | smallest on-curve *x*, 256-bit on-curve bitmaps, small-scalar relations | No separator found; the square-root convention forces a point at *x* = 0 in the *p* ≡ 3 (mod 4) runs |

Then we modelled the program instead of the curve: simulated aborts, an Elkies/Atkin timing proxy, index and byte patterns, base-point failures, and sorting rules. **None of the tested rules fits.** Set cover over 135 predicates in the original coefficient model needs four predicates; **88/126 (69.8%)** endpoint-conditioned relabellings do at least as well. Using the other P-224 root throughout that run, matching its published coefficient, gives four predicates and **98/126 (77.8%)**. The historical skipped-candidate root convention remains unknown. The earlier exploratory count-only comparison gave 35%.

**No tested rule separates the eleven skipped curves from the eight published ones.** This is an exploratory negative result on nineteen curves, not a proof that no numerical criterion exists. A point counter that sometimes gave up or a human choice remains plausible, as do untested numerical rules, different code between runs, and more general RNG-consumption models.

Two constraints on the program *did* come out of the sweep:

- For every published curve over *p* ≡ 3 (mod 4), *b* = (−27/*c*)<sup>(*p*+1)/4</sup> mod *p*. Seven for seven. Using this textbook root reproduces the source posts' candidate lists; accepting either root adds 23 candidates across the three runs. The matches do not prove that the original program never tested the other root.
- The published seeds align with the 20-draw candidate stream. This constrains *cumulative* extra RNG consumption at published checkpoints, not each individual event: an extra draw followed later by nineteen extra draws could restore alignment.

**P-224 correction (20 October).** The original root-1 representative is the negative of the published coefficient. That does not change the curve's order or intrinsic CM invariants, but it changes integer and coordinate-level properties. The coefficient tables now use the publication-aligned root-2 model, retain all four alternate-root factorizations, and identify the sign assumption explicitly. The published coefficient's largest prime factor is 123 bits, not 149. The point scan now requires the exact published coefficient and both generator coordinates; its minimum x is 205 bits at 4819·G, with no coordinate at least 32 bits short.

Coordinate comparisons for the unpublished P-224 candidates retain the original root-1 scenario and label their coefficients in the regenerated records. They do not establish the historical sign choice; the complete integer-factor witnesses separately retain both signs.

The extension-factor records have also been repaired: four composite atoms were split into primes, and smoothness is now log₂ of the known smooth product, not a sum of individual bit lengths. The old ECM driver could discard later factors and hide process failures. Its 57 historical searches have **not** been rerun, so their coverage remains marked `legacy-unverified`. The known sextic smoothness contrast has medians 51.2 versus 21.7 bits and an exploratory within-run, endpoint-conditioned rank tail of 11/126 (8.7%), before multiple-comparison adjustment—not a recovered selection rule.

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
| [`scripts/`](scripts/) | cached checks use Python 3.8+; point scans/certificates use PARI/GP; fresh ECM uses GMP-ECM; optional msieve replay requires msieve and Bash |
| [`results/`](results/) | raw outputs behind every number above |

**One warning for reproducers.** We built PARI/GP 2.10 from source without `seadata`. Its `ellsea(E,1)` early-abort mode returned the *twist's* order for several curves in that build. Use `ellcard` and check `ellmul(E,P,n)==[0]`.

### Review regression checks

From the repository root, run:

```text
python -X utf8 -m unittest discover -s scripts -p "test*.py" -v
python -X utf8 scripts\cover.py
python -X utf8 scripts\bfac\summarize.py
python -X utf8 scripts\extfac\summarize_ext.py
```

These are PowerShell examples from the repository root. Put PARI/GP on `PATH`, or set `GP` to its executable path, to include the cross-language, exact-generator, cofactor-preimage, and prime-order checks. Without GP those tests are explicitly skipped. The tests do not repeat SEA for all 3,072 counted candidates. `cover.py` preserves the original root-1 comparison and records root-2 sensitivity; the two factor summarizers validate the cached witnesses and regenerate the reports without repeating ECM.

To repeat the corrected P-224 coordinate and small-scalar scans:

```text
python -X utf8 scripts\run_points.py
```

The runner uses a fresh temporary directory and replaces only the selected blocks. `--curve P-521` repeats the P-521 multiple/inverse-multiple scan; `--all` repeats every scan. The corrected P-224 scan and the P-521 scan have both been repeated. The latter fixes a stale, out-of-Hasse subgroup-order literal in the script and reproduces its cached 502-bit minimum; the other eight prime-generator outputs remain from the original run. Every declared generator order must now be prime and inside the Hasse interval, as well as killing the point.

To refactor all 23 coefficient cases with PARI/GP, use `python -X utf8 scripts\bfac\summarize.py --factor`. Alternatively, `scripts/bfac/run_all.sh` generates its inputs and runs msieve in separate per-root work directories; existing work directories are not overwritten.

For a **new, potentially expensive** ECM study, put GMP-ECM on `PATH` or set `ECM` to its executable:

```text
python -X utf8 scripts\extfac\cofactors.py results\ecm-work\cof.txt
python -X utf8 scripts\extfac\ecm_driver.py results\ecm-work\cof.txt results\ecm-work\ext-new.json
python -X utf8 scripts\extfac\summarize_ext.py results\ecm-work\ext-new.json
```

The driver uses `-one`, shares each level's curve budget across composite subproblems, checks GMP-ECM's documented exit statuses, and retains stdout/stderr (including bounds, curve parameters and engine version) beside the output. Existing outputs/transcript directories are not overwritten. Explicit shard files can be passed together to the summarizer; missing or duplicate curve/degree records are rejected. Bounded ECM never certifies a universal factor-size cutoff.

The raw binary scan's coordinate exports have been recomputed; its long-scan minima are retained from the original run because the conversion error did not affect polynomial degrees. The full phrase/hash search (`scripts/k163/search.py`, 29,577,717 evaluations) was rerun against the corrected target on 19 October: no hits (`results/k163-search-rerun.txt`).

## Open questions

1. **The 128-bit value behind K-163's *G*/2.** Hash preimage over 1997-era phrases, encodings and hash functions, or an RNG stream. This is the one with a concrete target.
2. **The other base points.** P-224/256/384/521, the five B curves, the four other K curves. Compare complete cofactor-preimage sets, field encodings, hash expansions, and RNG layouts; a negative subgroup-only scan is not a general exclusion of cofactor clearing.
3. **The B-163 seed**, which fits no generator Anthropic tried.
4. **The eleven skips.** Seek archival code and printouts, but also test explicit variable-consumption state machines and historically plausible, run-specific point-counter behaviour. The present tests do not exhaust those possibilities.

## Who

Dan Shumow. Computation and drafting with Claude (Anthropic). Thanks to Nadia Heninger for the half-point idea, and to the Anthropic Frontier Red Team and Filippo Valsorda for leaving such a well-marked trail.

Code CC0 1.0; text CC BY 4.0.
