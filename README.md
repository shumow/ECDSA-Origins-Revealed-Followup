# The seeds are solved. The curves aren't done.

*A follow-up to Anthropic's [Claude reveals ECDSA curve origins](https://www.anthropic.com/research/ecdsa-curve-origins) and Filippo Valsorda's [reproduction](https://words.filippo.io/seeds-solved/).*

*Readers should take this as the next chapter, not the closing one. There is still no action to take on the NIST curves. There is, however, more to find.*

---

On 16 October 2026 a 25-year-old question closed: the `SEED` values behind the NIST and ANSI X9.62 elliptic curves are not hashes of a joke about Jerry Solinas's salary. They are raw `lrand48()` output, seeded from the Unix clock, drawn 20 bytes at a time until a candidate produced a usable curve. P-256 is candidate 1842 of a run started at 01:52:34 UTC on 16 August 1997.

Both write-ups left a residue. Each run produced *earlier* candidates that also give prime-order curves of the right size and pass every documented check — and the program passed them over. Candidate 876 of the P-256 run is such a curve; so are three in the P-224 run and seven across the two ANSI X9.62 runs. Valsorda: "roughly twice as many valid seeds as were published," rejected by a second undocumented criterion that "still escapes us."

This repository is what happened when we went looking for that criterion — and what we found instead.

## What we did

We regenerated all four prime-field runs, verified every group order independently (full SEA, then $n \cdot P = O$ on random points), and confirmed the published-vs-skipped lists match Anthropic's and Valsorda's exactly: **8 published curves, 11 skipped but viable.**

Then we asked every question a cryptographer in 1997 could cheaply have asked of those 19 curves, and some they could not:

| Family | What we checked | Separates published from skipped? |
|---|---|---|
| Arithmetic of *n*, *t* | twist order, complete factorizations of *n* ± 1, congruences | No |
| CM structure | discriminant *t*² − 4*p*, conductor, class number with *L*(1, χ) | No — the published P-224 has the *smallest* class number in its run; the published P-256 the *largest* |
| Isogenies over 𝔽<sub>*p*</sub> | End(*E*), volcano position, rational ℓ-isogenies for ℓ ≤ 43 | No — the one curve with any volcano structure is published |
| Isogenies over 𝔽<sub>*p*<sup>*k*</sup></sub> | volcano depths for ℓ ≤ 47, *k* ≤ 12 | No |
| Extension-field orders | #*E*(𝔽<sub>*p*<sup>*k*</sup></sub>)/*n* smoothness, *k* ≤ 12 | No |
| Embedding degree | ord<sub>*n*</sub>(*p*) | No — ≥ 2²²² everywhere |
| gcd(*p* ± 1, *n* ± 1) | values, odd parts, largest prime factors, per-run ranking | No — flips direction between runs |
| Symbols and residues | nine Legendre symbols; *n*, *p*, *t* mod 4, 8 | No — the published curves disagree *with each other* |
| Point structure | smallest on-curve *x*, 256-bit on-curve bitmaps, small-scalar relations | No — coin flips |

Then we modelled the program instead of the curve: eleven simulated early-abort bugs (sign flips, wrong root, off-by-one, trace-instead-of-order), a per-candidate time limit (Elkies/Atkin balance), index-dependent bugs, mangled seed bytes, a failing base-point step, and sorted human choice. **None fits.** Finally we asked whether the eleven could be a *union* of several small defects, via exhaustive set cover over 135 bug-shaped predicates: the real labelling needs a four-predicate cover, and so do 35% of random relabellings.

**The eleven skipped curves are indistinguishable from the eight published ones.** Whatever rejected them left no trace in the parameters. Our best guess is the boring one — a point counter that sometimes gave up, or a person taking the last curve off a printout — and the parameters cannot tell those apart.

Two things about the program *did* come out of the sweep:

- For every published curve over *p* ≡ 3 (mod 4), *b* = (−27/*c*)<sup>(*p*+1)/4</sup> mod *p*. Seven for seven. The program used the textbook square root and tested only that curve; a reproduction that accepts either root triples the apparent number of valid seeds.
- The published seeds within a run sit at coprime indices, so the program drew exactly 20 bytes per candidate. Any extra RNG consumption came in whole blocks.

## What we found instead

The seeds are explained. The **base points** mostly are not: Anthropic recovered P-192 and the ANSI example generators from FreeLIP's `zrandom`, and found nothing for P-224, P-256, P-384, P-521 or any binary curve.

We computed small multiples and small divisors of every published generator — *k*·*G* and *G*/*k* for *k* up to 2¹⁶ — looking for a hash-sized coordinate. On the ten prime-field curves: nothing. Every coordinate is within two bits of random.

On the binary curves, nine of ten are likewise random. **K-163 is not.** Halving its generator gives

```
G/2 :  x = 0x3a5da90060df8af5be2121e601ae11f1     (126 bits on a 163-bit curve)
       y = full size (161 bits)
```

A coordinate 37 bits short of the field is a 2<sup>−37</sup> event. Across the ~70,000 points we scanned, the expected number of such hits is about 10<sup>−6</sup>.

The reading that writes itself: K-163 is a Koblitz curve, *y*² + *xy* = *x*³ + *x*² + 1, with no seed at all — the generator is the *only* randomly chosen parameter. Someone picked a 128-bit *x*, solved for *y*, and multiplied by the cofactor 2 to land in the prime-order subgroup. That is a different procedure from the FreeLIP recipe on the prime curves. We have not identified the 128-bit value. It is not the MD5 or SHA-1 of the obvious strings, and it is not four `lrand48` words.

We report it for what it shows: at least one published NIST generator carries a fingerprint of its construction that nobody has decoded. The seeds were one provenance problem. The base points are a second.

## What this means

Nothing changes for users of these curves. The skipped-candidate result *strengthens* the case Anthropic made: with ~50 invariants showing no pattern, the eleven skips look like noise, not selection, and a designer searching for weak curves would have had to find them among candidates that are statistically identical to the ones chosen.

The K-163 observation is a lead, not a finding. If the 128-bit value turns out to be a hash of something, it dates and explains the binary-curve generators the way `lrand48` explained the seeds — and the lore about a sentence may yet have somewhere to live.

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

## Open questions

1. **The 128-bit value behind K-163's *G*/2.** Hash preimage over 1997-era phrases, encodings and hash functions, or an RNG stream. This is the one with a concrete target.
2. **The other base points.** P-224/256/384/521, the five B curves, the four other K curves. If the K-163 method was general, *x* was full-size on the rest — a hash expanded to field size, or RNG output, possibly from the same 17 April 1998 session as the B seeds.
3. **The B-163 seed**, which fits no generator Anthropic tried.
4. **The eleven skips.** Only archival evidence — the program, or a printout — will settle it now.

## Who

Dan Shumow. Computation and drafting with Claude (Anthropic). Thanks to Nadia Heninger for the half-point idea, and to the Anthropic Frontier Red Team and Filippo Valsorda for leaving such a well-marked trail.

Code CC0 1.0; text CC BY 4.0.
