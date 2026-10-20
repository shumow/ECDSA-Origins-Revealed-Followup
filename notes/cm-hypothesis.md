# The skipped NIST/ANSI curve candidates: what does and does not explain them

*Dan Shumow, with Claude. 2026-10-17. Part A is the results map; Part B is the detailed record, with section numbers kept stable for cross-reference; Part C covers the base points; Part D reproducibility and sources.*

## Summary

**This is an exploratory negative result.** Anthropic's lrand48 discovery explains every NIST/ANSI prime-curve seed but leaves eleven viable unpublished candidates in the four runs studied here. Roughly fifty properties and a dozen program models give **no tested rule separating the eleven skipped curves from the eight published ones**. This is not an exclusion of every numerical criterion, consistent implementation bug, or run-specific process. Seven published coefficients match the textbook square root; the recovered RNG offsets constrain cumulative alignment, not each individual call. Separately, K-163's subgroup half-point has a verified 126-bit x-coordinate. Its original printed value was coefficient-bit-reversed; the corrected target and the limitations of earlier hash searches are in §7.1.

Reproducing the four prime-field runs (P-256, P-224, prime192, prime239) with that square-root convention and Filippo Valsorda's size rule gives **8 published curves and 11 skipped-but-viable ones** — the same lists both Anthropic and Valsorda report.

**Curve invariants — fifteen families tested, no separator found.** These include the arithmetic of n and t, CM discriminant and estimated class number, isogeny and extension-field structure, embedding degree, gcds, symbols, residues, and small-x points. This is a finite collection, not everything a 1997 program could compute. The class numbers use truncated Euler products without certified errors; several features are algebraically dependent.

**Generation process — observations, not a recovered program.** Published coefficients match b = (−27/c)^((p+1)/4) for p ≡ 3 (mod 4), seven for seven. Each recorded window ends at a published candidate. Recovered offsets constrain cumulative RNG alignment at published checkpoints, not the granularity of every extra draw; no tested fixed-block skip rule fits.

**Program models — six families tested (Part A.3), plus set cover (§6.21).** The tested rules do not explain all labels. Unweighted Elkies counts are only a timing proxy. Intermediate-arithmetic bugs, other deterministic rules, variable RNG consumption, and differences between runs remain open.

---

## Part A. Results map

### A.1 Curve invariants (all null)

| Family | What was tested | Where | Result |
|---|---|---|---|
| Arithmetic of n and t | twist order n' = 2p + 2 − n (smoothness, cofactor primality); n ± 1 full factorizations and largest prime factors; congruences on t, n, b mod 2, 3, 4, 5, 8; b < p/2; (n−1)/2 prime | §6.1–6.3, §6.6, §6.9 | interleave |
| Arithmetic of b | complete factorization of b as an integer: Ω, ω, largest and second-largest prime factors, smooth part, square-freeness; b mod 3, 4, 5, 7, 8 | §6.23 | interleave |
| CM structure | D = t² − 4p; conductor s; fundamental discriminant f; class number via √|f|·L(1,χ)/π with L(1,χ) from the Euler product to 10⁶; complete factorization of every |D| (ω, Ω, largest primes, smooth part); q ± 1 structure and cross-divisibility of the discriminant primes | §2–3 (theory), §6.1–6.2, §6.5, §6.9, §6.22 | floor refuted by P-224 (published has smallest h); ceiling refuted by P-256 (published has larger h); interleave on 19 |
| Isogeny structure over F_p | End(E) vs Z[π]; P-224 at the crater of a height-1 3-volcano; prime239 2320 and 2682 at floors of height-1 5-volcanoes; rational ℓ-isogeny counts | §6.7, §6.12, `battery*.txt` | no tested separator; the two nonmaximal endomorphism rings include one published and one skipped curve |
| Isogeny structure over F_{p^k} | conductor s·U_k and ℓ-volcano depths for ℓ ≤ 47, k ∈ {2,3,4,6,12} | §6.12 | interleave |
| Extension-field group orders | #E(F_{p^k})/n for k ≤ 12: 10⁶-smooth part, cofactor size and primality | §6.17 | random-integer behaviour, interleave |
| Extension-order cofactors, deep | C₃ = #E(F_{p³})/n, C₄ = (p−1)²+t², C₆ (sextic piece): ECM to t25 + ½t30, smooth parts, largest factors, remainder primality | §6.24 | interleave |
| Embedding degree | ord_n(p) (exact for some, otherwise > 20000) | §6.1–6.2, §6.9 | > 20000 for every viable candidate |
| gcds | gcd(p±1, n±1), gcd(p²−1, n²−1), odd parts, largest prime factors; per-run ranking | §6.16 | no consistent direction across runs |
| Symbols and residues | (n/p), (p/n), (t/p), (t/n), (b/p), (−3/n), (f/n), (−1/n), (2/n); n, p, t mod 4 and 8 | §6.18 | published curves disagree among themselves in the 3-curve runs |
| Point structure | smallest on-curve x and its y; x = 0…255 on-curve bitmaps; small-scalar relations | §6.13–6.15 | no tested separator; the textbook-root convention forces x = 0 on the p ≡ 3 (mod 4) curves |

### A.2 Generation process

| Property | Where | Result |
|---|---|---|
| Square-root convention for b | §6.10 | b = (−27/c)^((p+1)/4) for all seven published curves over p ≡ 3 (mod 4); accepting either root adds 4 + 10 + 9 viable candidates, without establishing which roots the original code tried |
| Size rule | §1.2, §6.9 | Valsorda's bitlen(n) ≤ bitlen(p) rejects 8 prime-order P-224 and 7 prime192 candidates; reproduced |
| Published = last viable of the run | §6.3, §6.9 | holds in all four runs (1842, 7026, 6013, 3048) but earlier published curves (139, 5228; 2185, 2320) have later skipped ones, so it is not a rule |
| RNG alignment | §6.11 | cumulative extra draws must restore 20-draw alignment at published checkpoints; individual extras need not be multiples of 20 |
| Event-triggered skip rules | §6.11 | none of the "after property X, skip k blocks" rules (X from 6 candidate properties, k ≤ 7) fits; best 13/19 vs. random ≈ 9.5 |
| Candidate-index patterns | §6.11 | skips not periodic, not parity-based |

### A.3 Program models

- **Sequential multi-check model (checks in order, class number as a later stage) — tested, §6.22: no disjunction of ≤ 4 thresholded invariants covers the skipped set; 32 % of random relabellings admit one.**
- **Union of small bugs — tested, §6.21: no signal.** Smallest cover size is 4. Under the exact endpoint-conditioned null, 88/126 labellings (69.8%) do as well or better; the original count-only Monte Carlo comparison gave 35%.
- **Early-abort false negatives — tested, §6.19: no listed buggy rule fits.** Eleven simple abort models and their tested bounded-ℓ and residue variants fail to separate. This does not exhaust consistent bugs involving intermediate arithmetic or particular implementations.
- **Per-candidate time limit — tested, §6.19: not supported.** Published curves are slightly *more* Atkin-heavy (mean 9.9 Elkies of 24 vs 12.5 for skipped); the two most Elkies-rich curves are skipped.
- **Position-dependent bugs — tested, §6.20: nothing.** Residues, bit positions, popcount, and byte-offset-mod-buffer tests on the 11 skipped indices find no property disjoint from the published 8.
- **Different candidate stream — partially tested, §6.11, §6.20.** Cumulative alignment is constrained at published seeds, not at every candidate; tested seed-byte mangling does not explain the whole label set.
- **Two-pass selection — sorting rules tested, §6.20: none.** The three published curves in prime192/prime239 are not the top-3 or bottom-3 under index, seed, b, n, t, or n − p. A non-numerical human choice remains possible and untestable.
- **A test on the base point — tested, §6.20: no.** The published FreeLIP recipe, run on every viable prime192/prime239 curve with the published seeds and 600 nearby seeds, behaves identically on skipped and published curves (≈ 2 tries to an on-curve x; no failure mode fires selectively).

---

## Part B. Detailed record

## 1. Background

### 1.1 The seed result

Anthropic's Frontier Red Team post "Claude reveals ECDSA curve origins" (2026-10-16) showed that the `SEED` values in FIPS 186-2 / ANSI X9.62 are not hashes of anything. Each prime-field seed is 20 consecutive bytes of `lrand48() >> 23` after `srand48(t)`, where `t` is a Unix timestamp between May 1997 and April 1998. A "run" draws 20-byte candidates one after another; the published seed is candidate number *n* of its run. The runs relevant here:

| Curve | `srand48` time (UTC) | Published candidate |
|---|---|---|
| P-256 | 1997-08-16 01:52:34 | 1842 |
| P-224 | 1998-04-03 12:52:07 | 7026 |
| P-192, prime192v2/v3 | 1997-05-18 14:45:34 | 139 / 6013 / 5228 |
| prime239v1/v2/v3 | 1997-05-15 15:49:03 | 2185 / 2320 / 3048 |

Each seed determines the coefficient *b* through the X9.62 / FIPS 186-2 procedure: SHA-1 expansion of the seed gives *c*, and *b* is a square root of −27/*c* mod *p* (with *a* = −3). About half of all candidates have no such root and are discarded by the standard itself.

### 1.2 The skipped candidates

Anthropic observed that the runs passed over candidates that look viable:

- **P-256:** candidate 876 of the same run also gives a prime-order curve of the right size, "with parameters chosen the same way," yet candidate 1842 was published.
- **P-224:** the run passed over three such curves.
- **ANSI runs (192/239):** seven more.

Filippo Valsorda's follow-up ("The NIST Elliptic Curves Seeds Bounty Has Been Claimed", 2026-10-16) adds two things. First, there is one *understood* undocumented criterion beyond X9.62: a seed is rejected if the bit length of the order *n* exceeds the bit length of *p* (not the stricter *n* < *p*, because prime239v2 has *p* < *n* < 2²³⁹). Second, after applying that, "roughly twice as many valid seeds as were published" remain — i.e. a second criterion, or an artifact, rejects on the order of half of the otherwise-valid candidates. Neither post mentions class numbers, CM discriminants, embedding degree, or twist order.

That "half" calibrates every hypothesis below: the unknown criterion did not reject one candidate in several hundred of *all* candidates; it rejected roughly one in two of the candidates that already had prime order and the right size.

## 2. The first hypothesis: CM discriminant and class number

*This section and the next record the initial hypothesis. The tested class-number thresholds do not explain the labels. Section 3 is a random-discriminant heuristic, not a validated distribution for the root-conditioned, prime-order candidates.*

For an ordinary curve *E*/F_p with trace *t* = *p* + 1 − #*E*, the Frobenius endomorphism satisfies π² − *t*π + *p* = 0, so Z[π] sits inside an imaginary quadratic order of discriminant

D = t² − 4p < 0.

Write D = f · s² with *f* a fundamental discriminant (so *f* is square-free apart from a possible factor of 4). The endomorphism ring End(*E*) lies between Z[π] and the maximal order O_K of K = Q(√D); its discriminant is *f* · s'² for some s' | s. The class number of the maximal order is, by the class number formula,

h(f) = (√|f| / π) · L(1, χ_f)   (for |f| > 4),

and L(1, χ_f) is a slowly varying factor,[^siegel] so to first approximation

h ≈ √|f|.

[^siegel]: L(1, χ_f) is bounded above by O(log |f|). The matching lower bound ≫ 1/log |f| holds only in the absence of an exceptional (Siegel) zero; unconditionally one has Siegel's ineffective |f|^{−ε}. For comparing nineteen discriminants of similar size, §6.5 keeps L(1, χ) explicit rather than dropping it, so none of this affects the comparison.

For a random curve of a 256-bit *p*, |D| ≈ 4*p* ≈ 2²⁵⁸, and if D were square-free then h ≈ 2¹²⁹. A small class number is what makes CM constructions possible and is the property SafeCurves checks under "CM field discriminant"; a curve with tiny *f* (such as −3 or −4) has an endomorphism ring that is "special" in a way a cautious designer in 1997 might have wanted to avoid. The hypothesis was that such a floor, set near the generic size, was the undocumented criterion.

## 3. The statistical point: largest square divisor, not near-squareness

A first instinct is that a random D is essentially never a small multiple of a square: the probability that t² − 4p is within a constant factor of a perfect square is on the order of 1/√p, which at 224–256 bits is zero for all practical purposes. If that were the relevant statistic, a class number floor could never explain any skips.

But that is the wrong statistic. What determines how much the class number drops below its generic size is the **largest square divisor** s² of D, and its distribution is heavy-tailed:

- For a fixed *s*, the probability that s² | D for a random D is about 1/s².
- So the probability that D is divisible by some square s² with s ≥ X is roughly Σ_{s ≥ X} 1/s² ≈ 1/X (up to a constant; multiplicity and the restriction to D ≡ 0,1 mod 4 change the constant but not the shape).
- If s ≥ X then |f| = |D|/s² is reduced by a factor of at least X², and h ≈ √|f| is reduced by a factor of at least X.

So: **P( h ≤ h_generic / R ) ≈ 1/R**, polynomially — not exponentially — small in the reduction factor. A floor of the form "h must exceed √p / 2^k" is failed by roughly one candidate in 2^k. This is a completely different regime from the 1/√p near-squareness estimate, and it is why a class number floor is a *statistically admissible* candidate for an undocumented criterion.

Two further consequences of the heavy tail:

1. The size of the reduction is set by small primes most of the time: s is usually a product of small primes (D divisible by 4, 9, 25, …), so the square part of D can be found by trial division to a modest bound plus a cheap perfect-square test on the cofactor. We never need to factor a 256-bit number.
2. The same heavy tail means that among a few thousand candidates one *expects* a handful with h down by a factor of 2¹⁰ or so, and essentially none with h down by 2⁶⁰. Any criterion that rejected ~50% of prime-order candidates (Filippo's observation) would have to be set at the *median* of the distribution, which for the largest-square-divisor statistic means a floor like "D must not be divisible by 4" or "by 4 and 9" — i.e. a *very* weak class number condition, or equivalently a congruence condition on *t* mod small primes. The prediction was therefore sharp: if the hypothesis were right, the published and skipped curves would differ systematically in the square part of D at small primes. They do not (§6.1–6.5).

## 4. Alternatives considered at the outset

**Stricter embedding degree bound.** X9.62 requires the MOV condition with B = 20. The computations show k = ord_n(p) > 20,000 for every viable candidate. That excludes rejection by small fixed MOV limits, not every possible bound: for example, a requirement k = n − 1 can reject a substantial fraction of inputs. A universal statement that no embedding-degree threshold could reject half the candidates does not follow.

**Twist order.** The quadratic twist has order n' = 2p + 2 − n = p + 1 + t. A requirement that n' be prime would reject ~99% of candidates; a requirement that n' have no small prime factors below some bound, or a large prime factor above some bound, rejects a tunable fraction and *could* sit near 50%. This was the strongest conventional competitor, since twist security was understood in the 1990s and is cheap to check. Result in §6.3: no clean separation.

**Square-root choice (an artifact hypothesis).** Both roots satisfy b²c ≡ −27 (mod p); for p ≡ 3 (mod 4) they give quadratic twists. Using the textbook root reproduces the source posts' candidate lists, whereas accepting either root adds candidates. Seven published-root matches are evidence for that convention, not proof that the historical code tested only one root. This does not explain the residual skips, since the source lists already use the matching convention. For P-224 the two roots give isomorphic curves.

**Buggy order computation.** Filippo mentions the possibility of a point-counting bug that returned the wrong answer half the time. Testable only in its consistent forms — §6.19 simulates eleven of them and none fits — and otherwise only negatively: no clean property separating accepted from rejected was found, so a bug is not displaced by anything more parsimonious.

## 5. Method

For each run (P-256, 1842 candidates; P-224, 7026; prime192, 6013; prime239, 3048):

1. Regenerate the 20-byte candidates from the published `srand48` timestamp with the CC0 reproducer.
2. For each candidate, derive c by the X9.62 / FIPS 186-2 SHA-1 expansion, test whether −27/c is a quadratic residue, and if so compute both square roots b₁, b₂.
3. Discard candidates with 2-torsion (the cubic has a root mod p). Count points with full SEA (PARI/GP built from source) for the curve y² = x³ − 3x + b₁, and verify the order by n·P = O on random points; the twist order follows. (A first pass used SEA's early-abort mode and produced trace-sign errors in this PARI build; it was discarded.)
4. A candidate is *viable* if the curve at the published root has prime order and passes the size check (bitlen n ≤ bitlen p). Both roots were counted for the p ≡ 3 (mod 4) runs to settle the root convention (§6.10).
5. For each viable candidate and the published curve compute: t; D = t² − 4p; the square part s² of D (trial division to 10⁶ plus a perfect-square test on the cofactor); the fundamental discriminant f = D/s² (with the factor-of-4 adjustment); log₂ of the class number proxy √|f|; the embedding degree (order of p in (Z/nZ)*, computed from the factorization of n − 1 as far as it is feasible, otherwise bounded below); and the twist order n' with its small-factor structure.

Later sections add n ± 1 factorizations, isogeny and extension-field structure, gcds, symbols, point structure, simulated abort rules, and the set-cover search; each names its script. Full inventory in §8.

## 6. Results

Point counting: PARI/GP 2.10-dev (built from a GitHub mirror; no `seadata`, so modular polynomials were computed on the fly and cached). Every reported order was independently verified by checking n·P = O for random points P, which for a prime n in the Hasse interval determines #E exactly. A first pass using SEA's early-abort mode produced several trace-sign errors (twist order returned instead of the curve's); those results were discarded and everything below comes from the full, verified recount. Candidates whose cubic x³ − 3x + b has a root mod p (even order) were excluded without counting.

The reproduction agrees exactly with the accepted lists in Filippo's transcript — P-256 run {876, 1842}, P-224 run {777, 1485, 5736, 7026} — once (a) for P-256 only the same square root of −27/c as the published b is considered, and (b) Filippo's size criterion (bitlen n ≤ bitlen p) is applied. The P-224 size criterion is doing real work: eight of the twelve prime-order P-224 candidates have negative trace and a 225-bit order, and are rejected by it.

*Note on class-number columns:* the tables in §6.1–6.2 and §6.9 report `log2 h~` = log₂√|f|, the leading-order class-number proxy with no L(1, χ) factor; §6.5 onward reports the corrected estimate log₂(√|f|·L(1,χ)/π), which differs by 2–3 bits. Comparisons within a table are consistent; compare across tables only via §6.5 and §6.9.

Notation: `s` is the largest square divisor extracted from D = t² − 4p (trial division to 10⁶ plus a perfect-square test); `log2 h~` is log₂√|f| for the fundamental discriminant f = D/s² (generic value log₂√(4p): 129.0 for P-256, 113.0 for P-224); `emb deg` is the embedding degree ord_n(p) where n − 1 could be factored, else a lower bound; twist columns give the small prime factors of n' = 2p + 2 − n and the size of the remaining cofactor.

### 6.1 P-256 run (1842 candidates; 960 with a valid b; 348 without 2-torsion)

Prime-order curves, counting both square roots of −27/c (for p ≡ 3 mod 4 the two roots are quadratic twists of each other; `b_pub` = same root as the published b, `-b` = the other root):

```
 cand  curve pub size   t      s   log2h~  D%4  D%9 D%25    emb deg          twist small factors cofbit  cofpr
   81     -b       ok   -      1    129.0    1    6   21    > 20000             [3, 11, 17, 197]    240  False
  276     -b       ok   +      1    129.0    1    3    5    > 20000                  [3, 5, 127]    246  False
  876  b_pub       ok   +      1    129.0    1    3    2    2^254.4            [3, 11, 37, 8081]    233  False
 1049     -b       ok   +      1    128.9    1    6   10    > 20000                   [3, 5, 41]    247  False
 1383     -b       ok   +      1    128.7    1    2   21    > 20000                 [13, 17, 71]    243  False
 1842  b_pub   *   ok   +      1    129.0    1    6   10    > 20000              [3, 5, 13, 179]    241   True
```

Both `b_pub` curves — the skipped 876 and the published 1842 — have square-free discriminants and class-number proxy at the generic maximum; the discriminant does not separate them. The four `-b` curves are not counted by Anthropic or Filippo: "parameters chosen the same way" means "same square root," and a reproduction that accepts either root roughly triples the apparent number of valid seeds in this run.

Across all 348 counted candidates, 39.7% have s ≥ 3, consistent with the heavy-tail estimate in §3 (D ≡ 0 mod ℓ² with probability ≈ 2/ℓ², summed over odd primes ≈ 0.4).

### 6.2 P-224 run (7026 candidates; 3545 with a valid b; 1161 without 2-torsion)

For p ≡ 1 (mod 4) the two roots give isomorphic curves, so there is one curve per candidate:

```
 cand  curve pub size   t      s   log2h~  D%4  D%9 D%25    emb deg          twist small factors cofbit  cofpr
   77      b      BIG   -      1    111.3    1    6   12    2^224.0                     [3, 233]    215  False
  777      b       ok   +      1    112.9    1    3    5    > 20000                  [3, 5, 683]    211  False
 1485      b       ok   +      1    113.0    1    6   22    > 20000                      [3, 31]    218  False
 2232      b      BIG   -      1    112.8    1    3    1    > 20000                  [3, 11, 31]    215  False
 2328      b      BIG   -      1    112.8    1    6   12    > 20000                          [3]    223  False
 2938      b      BIG   -      1    113.0    1    2    1    > 20000 [7, 1697, 2417, 509939, 887449]    161  False
 2954      b      BIG   -      3    111.4    1    0    5    > 20000             [3, 3, 5, 7, 11]    213  False
 3191      b      BIG   -      1    112.5    1    2    7    > 20000                           []    224  False
 3199      b      BIG   -     21    108.6    1    0   17    > 20000              [3, 3, 53, 173]    208  False
 5736      b       ok   +      1    112.9    1    3   17    2^222.4 [3, 1607, 3371, 17539, 20347]    172  False
 5861      b      BIG   -      1    112.2    1    2    7    > 20000                           []    224  False
 7026      b   *   ok   +      3    111.2    1    0   17    2^222.4               [3, 3, 11, 47]    212  False
```

This run refuted the class-number hypothesis. The published P-224 curve has D divisible by 9 (s = 3), so its fundamental discriminant and class number are *smaller* than generic by a factor ≈ 3 (log₂√|f| ≈ 111.4 versus 113.0), while all three skipped-but-valid candidates (777, 1485, 5736) have square-free D and the generic class number. A class-number floor set anywhere would have rejected the published curve before any of the skipped ones.

Among all 1161 counted candidates, 43.3% have s ≥ 3.

### 6.3 Assessment of the initial hypotheses

- **CM discriminant / class number floor: refuted.** P-256 gives no separation (all s = 1); P-224 gives separation in the wrong direction. The statistical argument of §3 stands — a floor near generic size *would* have failed at a sensible rate — but no such floor was applied. (A "ceiling," i.e. preferring small class number, is not a security criterion anyone would impose, and P-256 rules it out anyway: the published curve has the larger class number there, §6.5.)
- **Stricter embedding degree: refuted**, as expected: every viable candidate has embedding degree > 20000 (exact values where n − 1 was factored; a bound of 2²²² is impossible for the 192-bit runs since k | n − 1). This excludes small fixed MOV limits, not every conceivable embedding-degree rule; see §4.
- **Twist order: no clean separation.** The published P-256 twist has cofactor 3·5·13·179 times a 241-bit prime, while 876's twist cofactor is composite — suggestive in isolation — but the published P-224 twist (3²·11·47 × 212-bit composite) is no better than 1485's (3·31 × 218-bit composite) or 777's. No threshold on twist smoothness or twist-cofactor primality accepts all four published/accepted curves while rejecting all four skipped ones.
- **Class number with L(1,χ), n ± 1 smoothness, isogeny structure (over F_p and extensions), short-x points, low-byte x bitmaps, gcd(p ± 1, n ± 1):** see §6.5–6.16; none separates the groups.
- **Simple congruences** on t, n, and b (mod 2, 3, 4, 5, 8; b < p/2; (n−1)/2 prime) do not separate accepted from skipped either.
- **Square-root convention** is confirmed to matter for p ≡ 3 (mod 4) runs: four extra prime-order curves in the P-256 run live on the other root. It does not, however, explain Filippo's residual factor of two, since his accepted lists already use the published root and still contain unpublished seeds (1 of 2 for P-256, 3 of 4 for P-224).

What the skipped candidates look like, concretely: prime-order, generic-discriminant, large-embedding-degree curves that pass every documented criterion and every undocumented one tested here. The sections that follow extend the sweep to the ANSI runs and to every further family of invariants, then to models of the program itself.

### 6.5 Class-number estimates with L(1, χ), and the flipped hypothesis

The square-free parts in §6.1–6.2 ignore L(1, χ). Estimating L(1, χ_f) by the Euler product over primes to 10⁶ (stable to the second decimal between 10⁵ and 10⁶; exact `quadclassunit` on these 68–78-digit discriminants did not finish in this environment):

| Run | cand | L(1,χ) | log₂ h (est.) | log₂√\|f\| |
|---|---|---|---|---|
| P-256 | 876 (skipped) | 0.530 | 126.4 | 129.0 |
| P-256 | 1842 (published) | 0.723 | 126.9 | 129.0 |
| P-224 | 777 (skipped) | 0.607 | 110.5 | 112.9 |
| P-224 | 1485 (skipped) | 0.495 | 110.3 | 113.0 |
| P-224 | 5736 (skipped) | 0.540 | 110.4 | 112.9 |
| P-224 | 7026 (published) | 0.359 | 108.1 | 111.3 |

The published P-224 curve has the smallest class number of its run by a factor ≈ 4.5–5 (from both the 3² in D and an unusually small L(1,χ)); the published P-256 curve has a class number ≈ 1.4× *larger* than its skipped competitor. Neither a floor ("reject small h") nor the flipped rule ("prefer small h") is consistent with both runs, and §6.9 extends this to all nineteen curves. Two runs splitting one each way is what an irrelevant statistic looks like.

### 6.6 Smoothness of n ± 1

All twelve numbers were factored completely (trial division, then PARI's ECM/MPQS; every cofactor fell within seconds). Largest prime factors:

| Run | cand | n − 1 | LPF(n−1) | LPF(n+1) |
|---|---|---|---|---|
| P-256 | 876 (skipped) | 2·3·7·11·43·P242 | 242 bits | 232 bits |
| P-256 | 1842 (published) | 2⁴·3·71·131·373·3407·17449·38189·P28·P30·P40·P92 | **92 bits** | 215 bits |
| P-224 | 777 (skipped) | 2·3·743·54277·P53·P145 | 145 bits | 182 bits |
| P-224 | 1485 (skipped) | 2³·3·5·31·131·211·6421·7591·P39·P60·P74 | 74 bits | 102 bits |
| P-224 | 5736 (skipped) | 2³·3·19·2791·P204 | 204 bits | 142 bits |
| P-224 | 7026 (published) | 2²·3⁶·5·17·2153·P196 | 196 bits | 177 bits |

A "large prime factor of n − 1" (strong-prime style) criterion is excluded: the published P-256 has the smoothest n − 1 of all six (every factor ≤ 92 bits), while the candidate it displaced has n − 1 = 2·3·7·11·43 × a 242-bit prime. n + 1 and n² − 1 do not separate the groups either; the published values sit inside the range of the skipped ones.

### 6.7 Isogeny structure

For an ordinary curve with trace t, End(E) is an order between Z[π] (discriminant D = t² − 4p) and the maximal order O_K (discriminant f). The index [O_K : Z[π]] is the conductor s from §6.1–6.2.

- Five of the six curves have s = 1: Z[π] is already maximal, so End(E) = O_K is forced, every ℓ-isogeny volcano is a bare crater, and the number of rational ℓ-isogenies from E is exactly 1 + (f/ℓ): two if ℓ splits in K, one if ramified, none if inert. For a prime-order curve these isogenies have Galois-stable kernels with no rational points; they are the only isogeny structure the curve has.
- The published P-224 curve (7026) has s = 3: Z[π] has index 3 in O_K, so it sits on a 3-volcano of height one. Counting roots of Φ₃(j(E), X) over F_p gives 4 (crater: one horizontal edge since 3 is ramified in K, plus three descending edges) rather than 1 (floor). So End(E) = O_K: the published curve is on the crater, and its three descending 3-isogenies lead to curves with End = Z[π]. It is the only one of the six with any non-trivial volcano structure.

Rational ℓ-isogeny counts (roots of the classical modular polynomial Φ_ℓ(j(E), X) mod p, verified against the Kronecker symbols (f/ℓ)):

```
          ℓ=   2 3 5 7 11 13 17 19 23 29 31 37 41 43
P-256  876     0 1 0 0  2  0  2  2  0  2  2  2  0  2
P-256 1842 *   0 1 1 0  2  2  2  0  2  2  0  2  2  2
P-224  777     0 1 1 0  2  0  2  0  2  1  0  0  2  0
P-224 1485     0 1 0 0  2  0  0  0  2  2  2  0  1  2
P-224 5736     0 1 0 0  2  1  2  2  2  2  0  0  0  2
P-224 7026 *   0 4 0 0  2  0  0  0  0  1  0  0  0  0
```

Observations: ℓ = 2 is inert for every prime-order candidate (forced: n odd ⇒ t odd ⇒ D ≡ 5 mod 8), so none has a rational 2-isogeny. ℓ = 3 divides D for all six (so each has exactly one rational 3-isogeny, and in fact every one of these curves has a quadratic twist with a 3-torsion point) — but this is not forced; several of the other prime-order candidates in the runs have 3 inert. ℓ = 11 splits in all six, a ≈1.5 % coincidence that also fails on the broader candidate set. Beyond that the splitting patterns look random: the published P-256 has many split primes and the published P-224 has almost none (which is just the L(1,χ) difference in §6.5 seen prime by prime). Nothing in the isogeny structure — conductor, position on the volcano, or the pattern of rational small-degree isogenies — separates published from skipped. The one curve with any volcano structure at all is a published one, which is the opposite of what a "reject curves with non-maximal Frobenius order" rule would produce.

### 6.9 The ANSI X9.62 runs (prime192 and prime239)

Same pipeline (published root, 2-torsion filter, verified SEA count; no sign errors in either run).

**prime192 run** (srand48 1997-05-18 14:45:34; 6013 candidates, 3061 with valid b, 1057 counted). Viable: **139\***, 2198, **5228\***, 5405, **6013\*** — two skipped. Seven prime-order candidates were rejected by the size rule and ten are prime only on the twist root.

**prime239 run** (srand48 1997-05-15 15:49:03; 3048 candidates, 1555 with valid b, 506 counted). Viable: 36, 1562, **2185\***, **2320\***, 2491, 2682, 2863, **3048\*** — five skipped. None rejected by the size rule; nine prime only on the twist root.

Two plus five is exactly the "seven more" Anthropic reported for the ANSI runs, so the reproduction agrees with theirs here too. Across all four runs: 8 published, 11 skipped-but-viable.

| Run | cand | s | L(1,χ) | log₂ h | LPF(n−1) bits | LPF(n+1) bits |
|---|---|---|---|---|---|---|
| 192 | 139 \* | 1 | 0.411 | 94.0 | 92 | 108 |
| 192 | 2198 | 1 | 0.498 | 93.6 | 176 | 149 |
| 192 | 5228 \* | 1 | 0.352 | 93.8 | 157 | 161 |
| 192 | 5405 | 1 | 0.434 | 94.0 | 132 | 177 |
| 192 | 6013 \* | 1 | 0.529 | 93.6 | 64 | 145 |
| 239 | 36 | 1 | 0.436 | 117.1 | 105 | 153 |
| 239 | 1562 | 1 | 0.590 | 118.1 | 219 | 136 |
| 239 | 2185 \* | 1 | 0.246 | 116.8 | 69 | 136 |
| 239 | 2320 \* | 5 | 0.476 | 115.2 | 128 | 123 |
| 239 | 2491 | 1 | 0.415 | 117.6 | 76 | 131 |
| 239 | 2682 | 5 | 0.558 | 115.7 | 170 | 227 |
| 239 | 2863 | 1 | 0.505 | 117.7 | 183 | 72 |
| 239 | 3048 \* | 1 | 0.410 | 117.5 | 110 | 151 |

(generic log₂ h: 97.0 for 192, 120.5 for 239)

Class number, in either direction, is now dead on 19 curves: published and skipped values interleave in both ANSI runs, and the prime239 run has one published (2320) and one skipped (2682) curve with conductor s = 5. n ± 1 smoothness interleaves likewise. The embedding degrees are all astronomically large; the isogeny patterns (rational ℓ-isogeny counts, full tables in `battery192.txt` / `battery239.txt`) are random-looking, and 3 is inert for every curve in both runs because p ≡ 2 (mod 3) for both ANSI primes.

"Published = last viable candidate of the run" holds in all four runs (1842, 7026, 6013, 3048), but as a selection rule it is empty: 139 and 5228 were published with later viable candidates (2198, 5405) skipped in between, and likewise 2185 and 2320 before 2491/2682/2863. It only says the runs stopped when a curve was taken.

### 6.10 Positive finding: the square-root convention

For every published curve over a field with p ≡ 3 (mod 4), the published b equals the textbook root (−27/c)^((p+1)/4) mod p, seven of seven. This suggests that routine, but does not prove the original code never tested the other root. Reproducing with that convention gives the source posts' lists; accepting either root adds 4 + 10 + 9 candidates across the three runs. For P-224 the roots give isomorphic curves. This root choice also forces b to be a square, hence a point at x = 0.

### 6.11 The RNG-consumption hypothesis

A different kind of explanation for the skips: perhaps the program did not consume exactly 20 bytes of `lrand48` output per candidate. If it drew extra output after certain events (random bases for a primality test of the order, a random point, a second seed), then the 20-byte windows it actually tested would not be the 20-byte-aligned "candidates" of the reproduction, and a "skipped viable candidate" could simply be a window the program never looked at.

Two constraints from the data:

1. **Cumulative alignment is constrained, not every RNG call.** Published seeds occur at offsets 20·138, 20·5227, 20·6012 and 20·2184, 20·2319, 20·3047. From the recovered initialization, these exclude a larger constant stride for nonoverlapping 20-draw candidates. Variable consumption need only restore alignment cumulatively at the observed checkpoints: extras of 1 and later 19 draws suffice. Intervening tested windows need not be 20-draw-aligned.
2. **No simple event-triggered rule fits.** Simulating rules of the form "after a candidate with property X, skip the next k blocks" for X ∈ {valid b; even order; odd order; odd order with no factor < 2¹⁶ on the curve (or on it or its twist); prime but too large; prime on the twist root}, singly and in pairs, with k = 1…7, and asking whether any rule visits all 8 published seeds while missing all 11 skipped viable ones. None does; the best rules get 13 of 19 right, barely above what a random half-density subset would score (9.5).

These tests exclude the listed fixed-block models, not general variable-consumption state machines. Both auxiliary seed-sized blocks and smaller draws that cumulatively restore alignment remain possible.

### 6.12 Isogeny volcanoes over extension fields

Over F_{p^k}, t_k = t·t_{k−1} − p·t_{k−2}, with t_0 = 2 and t_1 = t. The discriminant is D·U_k², where U_0 = 0, U_1 = 1 and U_k = t·U_{k−1} − p·U_{k−2}. The CM field and geometric endomorphism ring do not change; the Frobenius-order conductor becomes s·|U_k|. A prime inert in K stays inert in K, but can acquire descending rational isogenies when it divides U_k. Volcano height is v_ℓ(sU_k), while the vertex's distance from the crater is the valuation of the conductor of End(E).

**Endomorphism-ring correction.** F_p-rationality of the endomorphisms does not imply maximality. Besides P-224 (s = 3, crater), prime239 candidates 2320 and 2682 have s = 5 and one rational 5-isogeny each, placing them on the floors with End(E) = Z[π]. A maximal-order vertex at the crater of a height-1 5-volcano would have all six roots of Φ₅ (two horizontal plus four descending for 2320, where 5 splits in K; one plus five for 2682, where 5 ramifies), since Φ₅(j, X) has degree 6. PARI/GP 2.19.0 reproduces the single-root counts. Their endomorphism conductor stays 5 over extensions, so these two vertices are not on the crater.

Depths v_ℓ(s·U_k) for ℓ ≤ 47, k ∈ {2, 3, 4, 6, 12} (full table in the transcript; summary): ℓ = 2 appears at k = 3 for every curve (forced: 2 is inert for all, so its rank of apparition is 3) with depth varying from 1 to 7; ℓ = 3 at k = 4 (or k = 3 where 3 | D); and otherwise a scattering of small primes whose rank of apparition divides k. Published and skipped curves are indistinguishable: e.g. in the prime239 run the published 2185 has a 5-volcano of depth 5 over F_{p³} while the skipped 36 has depth 2 and the published 3048 depth 0; in P-224 the skipped 777 has a 2-volcano of depth 7 over F_{p³} against depth 3 for the published 7026. No level k ≤ 12 and no ℓ ≤ 47 separates the groups.

### 6.13 Short x-coordinates

For each viable curve, the smallest x ≥ 0 with a point (x³ − 3x + b a square mod p), the first eight such x, and the y at the smallest one:

```
run      cand      first x with a point           y at smallest x        b
P-256     876      0 4 7 8 10 12 13 14            256 bits, odd          256 bits, odd
P-256    1842 *    0 5 6 8 9 12 13 17             255 bits, even         255 bits, odd
P-224     777      0 3 8 10 11 12 17 18           222 bits, even         223 bits, even
P-224    1485      1 2 3 5 10 12 15 16            224 bits, odd          224 bits, even
P-224    5736      1 2 9 14 15 17 18 23           224 bits, even         223 bits, even
P-224    7026 *    3 4 5 6 7 8 10 13              224 bits, odd          223 bits, odd
192       139 *    0 2 3 5 6 8 12 13              192 bits, odd          191 bits, odd
192      2198      0 2 3 6 9 15 16 18             192 bits, odd          192 bits, even
192      5228 *    0 1 4 5 6 7 8 9                192 bits, odd          190 bits, even
192      5405      0 1 6 10 11 12 13 16           190 bits, even         192 bits, odd
192      6013 *    0 2 3 5 14 15 18 19            187 bits, even         192 bits, odd
239        36      0 1 3 6 7 9 11 13              237 bits, odd          236 bits, even
239      1562      0 1 3 6 10 11 12 14            239 bits, even         239 bits, even
239      2185 *    0 1 6 7 8 9 10 11              238 bits, odd          239 bits, even
239      2320 *    0 2 3 4 6 8 10 11              238 bits, even         239 bits, even
239      2491      0 1 3 4 5 8 9 10               239 bits, even         236 bits, even
239      2682      0 1 3 4 7 9 12 14              239 bits, odd          235 bits, odd
239      2863      0 1 5 8 12 13 17 19            237 bits, odd          239 bits, odd
239      3048 *    0 2 5 8 13 14 16 19            234 bits, odd          238 bits, odd
```

x = 0 carries a point iff b is a square. This is **forced**, not a coin flip, on all fifteen viable curves over p ≡ 3 (mod 4): b is an integer power of the quadratic residue −27/c, hence is itself a residue. One P-224 candidate also has square b, giving 16 of 19 in total. The three exceptions include the published P-224. Thus the root convention explains this aggregate pattern; bitmap null models must condition on it. No tested small-x rule separates the labels.

### 6.14 Low-byte x patterns

For each viable curve, the on-curve indicator for every x in 0…255 (1 if x³ − 3x + b is a square mod p), packed as 32 hex bytes with x = 0 the most significant bit of the first byte; count of on-curve x, first on-curve x, longest run of consecutive off-curve x, longest run of on-curve x, on-curve count among x < 16 and x < 64:

```
run      cand pub  #on  1st off-run on-run on<16 on<64  pattern
P-256     876      118    0       6      6     9    31  89af5b19263109e7b0471a887c88d02593858ea4ec44903f6be97b761e21c116
P-256    1842   *  125    0       5      6     7    31  86cc41e5350cbeda17221e7374d72913d2526b4f42a6a86723591cc9b184fd75
P-224     777      130    0       9      7     6    32  90b86bbd33bd6d008befe637767664c01b7194143afb50c27509e2ee2be8ccb4
P-224    1485      139    1       7     11     7    35  7429b07c7ff299d10fb4067d8d38e0ab227b687b46b81f6df4d37d34b3e59caf
P-224    5736      133    1       6      6     5    29  604361259c8b2e6f8e8b761357122ac6fbf7ddb8489486f7c37da5d929a617ba
P-224    7026   *  120    3       9      8    10    32  1fa79a680bebca30191b09fbbef70b005db0d0613c902310d4d93793fd4431c0
192       139   *  121    0       6      7     9    28  b68d6232a14bd841c5384d9aa050d20e87d4543dacb8d6de4bf8766a14adaea0
192      2198      126    0      10      7     6    25  b241ac51a21c640795bf8785002abccf2dc36fc8d15aaabdd45efced8d80a837
192      5228   *  131    0       6      6    11    38  cfceb9c66ed913d62e5a8a9b850cc2b3689d75af5931e2a454aa05676be7c921
192      5405      138    0       5      7     7    29  c23ca1eb85a12335f57482b5dda09b6462f47f24f4cf6be48f1bbdef5d22bd2e
192      6013   *  133    0       8      6     6    28  b4033685879a8f416cf0535a74991db6bdb7b2c54f88c1db6fa351c1a5fb953d
239        36      127    0       9     10     9    31  d3557d132c2b3d011c8cda52b690f88b5fc5068ef93006f261e93c25affdf032
239      1562      131    0       6      7     9    32  d23be7905ac8c99c6390773e19fcf27839d27758e19e7902dd6266a6ab6418ce
239      2185   *  148    0       4      9    11    41  c3f74b7e565e57f3777cfb73cff968c64b52527861778e9e85531eb956b27696
239      2320   *  124    0       5      5    10    33  baba458d687b6117a0b5f19b043e6597ba499bb2392f4b046318b32e30c3890f
239      2491      131    0       5      4    10    31  dce32d0d64a6454ea8db520baaf28c220a6c9c96f32e4cb672adc35d8e777b6b
239      2682      129    0       7     10     8    34  d94a43c8379acedddb69e691a8ec358b3ff40b34db154044b19781b10d1a7c5f
239      2863      124    0       7      5     6    32  c48c5ae7a5e65e28a9da53e2c040d8f7ae5c713911180b7a2e295155add961f2
239      3048   *  124    0       7      8     6    29  a486903951688bfd7358f24dea24d5d5360296dea17e9734f1810d1176cc45dc
```

The on-curve counts range from 118 to 148 (published mean 128.2, skipped 129.6), with longest off-curve runs 4–10 and on-curve runs 4–11. Binomial(256, ½) is only a rough scale comparison, not an exact null: the root convention forces the x = 0 bit in fifteen curves, and the entries have algebraic dependencies. No tested low-byte pattern separates the labels.

### 6.15 Small-x points, with the right square root, and small-scalar relations

Recomputed the small-x points taking y = (x³ − 3x + b)^((p+1)/4) as the primary root for the p ≡ 3 (mod 4) fields (the convention pinned down for b in §6.10) and Tonelli–Shanks with both roots for P-224. Full x, y, p − y for the first eight on-curve x of every viable curve are in `pts.out`. On a prime-order curve every non-identity point has order n, so there is no "special-order" small-x point to look for; the only possible structure is relational. Checked, for each curve: whether any of the first eight small-x points is a scalar multiple k·P₀ (k ≤ 2²⁰, up to sign) of the point at the smallest x, and for the eight published curves whether the published generator G is such a multiple, or P₀ a multiple of G. Result: no relation anywhere beyond k = 1; no published generator sits at a small x, and none is within 2²⁰ of the smallest-x point in either direction.

### 6.16 gcd(p ± 1, n ± 1)

Distinct from the MOV condition (which asks whether n | p^k − 1): here the question is whether p ± 1 and n ± 1 share any unusually large common factor, which a 1997 program might have looped over as a cheap "independence" check.

```
run    cand pub  (p-1,n-1)  (p+1,n+1)  (p-1,n+1)  (p+1,n-1)  (p^2-1,n^2-1)  (p-1,n)  (n-1,t)  (n+1,t)
P-256   876              6         16          2         14            672        1        1        1
P-256  1842   *          6          2         10         16            480        1        1        1
P-224   777              6          2         20          2            120        1        1        1
P-224  1485            120          2          2          2            240        1        1        1
P-224  5736             24          2          2          2             48        1        1        1
P-224  7026   *       1020          2          2          2           2040        1        1        1
192     139   *          2          6          2         80            480        1        1        1
192    2198              2          2          2         24             48        1        1        7
192    5228   *          2         20          2          6            120        1        1        1
192    5405              2          2          2         96            192        1        1        1
192    6013   *          2         10          2         48            480        1        1        1
239      36              2          4          2         42            168        1        1        1
239    1562              2        160          2        126          20160        1        1        1
239    2185   *          2          4          2         18             72        1        1        1
239    2320   *          2         68          2        630          42840        1        1        1
239    2491              2          2          2         36             72        1        1        1
239    2682              2       5784          2         70         404880        1        1        1
239    2863              2      13192          2         30         395760        1        1        1
239    3048   *          2         42          2         80           3360        1        1        1
```

All gcds are tiny (products of small primes, as expected for two random numbers that are both ≡ 1 or ≡ 3 mod small moduli for structural reasons — e.g. 2 always divides every entry since p and n are both odd). The largest, gcd(p² − 1, n² − 1) = 404880 and 395760, belong to two *skipped* prime239 curves, but the published prime239v2 is next at 42840 and the published P-224 has the largest gcd(p − 1, n − 1) of its run (1020). gcd(p − 1, n) = 1 everywhere (trivially, n prime and n ≠ p), and t is coprime to n ± 1 everywhere except one skipped curve (2198, gcd 7). No threshold or specific factor separates published from skipped.

**Per-run ranking.** For each gcd, and for its odd part and its largest prime factor, whether every published curve in the run is above every skipped one, below every skipped one, or neither. A threshold criterion needs the same direction in all four runs:

```
gcd             stat             P-256       P-224         192         239   consistent?
(p-1,n-1)       value            mixed   pub ABOVE       mixed       mixed   no
(p-1,n-1)       odd part         mixed   pub ABOVE       mixed       mixed   no
(p-1,n-1)       LPF              mixed   pub ABOVE       mixed       mixed   no
(p+1,n+1)       value        pub BELOW       mixed   pub ABOVE       mixed   no
(p+1,n+1)       odd part         mixed       mixed   pub ABOVE       mixed   no
(p+1,n+1)       LPF              mixed       mixed   pub ABOVE       mixed   no
(p-1,n+1)       value        pub ABOVE       mixed       mixed       mixed   no
(p-1,n+1)       odd part     pub ABOVE       mixed       mixed       mixed   no
(p-1,n+1)       LPF          pub ABOVE       mixed       mixed       mixed   no
(p+1,n-1)       value        pub ABOVE       mixed       mixed       mixed   no
(p+1,n-1)       odd part     pub BELOW       mixed       mixed       mixed   no
(p+1,n-1)       LPF          pub BELOW       mixed       mixed       mixed   no
(p^2-1,n^2-1)   value        pub BELOW   pub ABOVE       mixed       mixed   no
(p^2-1,n^2-1)   odd part     pub BELOW   pub ABOVE   pub ABOVE       mixed   no
(p^2-1,n^2-1)   LPF          pub BELOW   pub ABOVE   pub ABOVE       mixed   no
```

No gcd statistic has a consistent direction. gcd(p − 1, n − 1) puts the published curve on top in P-224 only; the odd part of gcd(p² − 1, n² − 1) has the published curves above the skipped in P-224 and prime192 but *below* in P-256 and mixed in prime239. A threshold on any of these is excluded.

### 6.17 Smoothness of #E(F_{p^k}) / n for k ≤ 12

Group orders over the extension fields from the trace recurrence (t_k = t·t_{k−1} − p·t_{k−2}), divided by n, cofactor trial-divided to 10⁶. Each cell is (bits of the 10⁶-smooth part) / (bits of the remaining cofactor) followed by P if that cofactor is a probable prime, C if composite, 1 if fully factored. k = 1 is trivial (n prime) and omitted.

```
run    cand pub   k=2        k=3        k=4        k=5        k=6        k=7        k=8        k=9        k=10       k=11       k=12
P-256   876      24/233 C  24/489 C  34/735 C   5/1020C  52/1229C   1/1536C  72/1721C  28/2021C  49/2256C   1/2560C  65/2752C
P-256  1842   *  16/241 P   3/510 C  51/718 C  16/1009C  46/1235C  21/1516C  69/1724C   8/2041C  82/2223C  10/2551C  92/2725C
P-224   777      14/211 C  19/430 C  31/642 C  25/872 C  38/1083C  27/1318C  47/1522C  51/1742C  47/1970C  26/2215C  77/2388C
P-224  1485       7/218 C  26/423 C  32/641 C  23/874 C  48/1073C  16/1329C  51/1518C  39/1754C  39/1978C   5/2236C  75/2390C
P-224  5736      53/172 C  17/432 C  66/607 C  12/885 C  90/1031C  55/1290C  74/1495C  47/1746C  68/1949C  13/2228C 147/2318C
P-224  7026   *  13/212 C   3/447 C  13/660 C  40/857 P  44/1077C   5/1340C  27/1542C  20/1773C  87/1930C   1/2241C  46/2419C
192     139   *   5/188 C  16/369 C  11/566 C  12/757 C  38/923 C  22/1131C  22/1323C  32/1505C  51/1678C  41/1880C  49/2064C
192    2198      23/170 P   5/380 P  49/528 C   5/764 C  36/925 C   1/1153C  52/1293C   5/1532C  44/1685C  17/1904C  94/2019C
192    5228   *   8/185 C  10/375 C  31/546 C  20/749 C  60/901 C   1/1153C  68/1277C  35/1502C  34/1695C  52/1869C 141/1972C
192    5405      12/181 P  15/370 C  16/561 C  40/729 C  48/913 C  21/1132C  49/1296C  34/1503C  59/1670C   7/1914C  85/2028C
192    6013   *  24/169 C  16/369 C  26/551 C  15/754 C  60/901 C   6/1147C  43/1302C  24/1513C  58/1671C  20/1901C  88/2025C
239      36      23/217 C  22/457 C  36/682 C  35/922 C  51/1145C  37/1398C  66/1608C  37/1876C  58/2094C  36/2355C  89/2541C
239    1562      26/214 C  15/464 C  28/690 C   1/956 C  42/1154C   5/1430C  41/1633C  45/1868C  35/2117C  23/2368C  67/2563C
239    2185   *  49/191 C  46/433 C  66/652 C   1/956 C 104/1092C   1/1434C  86/1588C  80/1833C  78/2074C  17/2374C 153/2477C
239    2320   *  11/229 C   3/476 C  31/687 C  15/942 C  67/1129C   1/1434C  50/1624C   3/1910C  45/2107C  26/2365C 100/2530C
239    2491      32/208 C   7/472 C  42/676 C  17/940 P  45/1151C   7/1428C  52/1622C  24/1889C  55/2097C  19/2372C  78/2552C
239    2682       5/235 C  49/430 C  36/682 C  11/946 C  80/1116C  17/1418C  42/1632C  56/1857C  38/2114C  18/2373C 113/2517C
239    2863       1/239 C  14/465 C  16/702 C  26/931 C  16/1180C   1/1434C  33/1641C  19/1894C  37/2115C   1/2390C  41/2589C
239    3048   *  14/226 C  49/430 C  27/691 C   1/956 C 111/1085C   1/1434P  68/1606C  68/1845C  14/2138C  17/2374C 132/2498C
```

The smooth parts are what random integers of these sizes give — typically 1–100 bits of small factors, occasionally more (e.g. 147 bits at k = 12 for the skipped 5736, 153 for the published 2185). Published and skipped values interleave at every k; no level shows the published curves systematically smoother or rougher than the skipped ones. The k = 2 cofactor (the twist order, up to the factor already covered in §6.2) is prime for one published (P-256) and three skipped curves (2198, 5405 at 192; none at 239) — no pattern. Nothing in the extension-field group structure separates the groups.

### 6.18 Legendre symbols and residue classes

For each viable curve: (n/p), (p/n), (t/p), (t/n), (b/p), (−3/n), (f/n) with f the fundamental CM discriminant, (−1/n), (2/n), and n, p, t mod 4 / 8. ((f/n) = 1 always, since n = p + 1 − t and 4p = t² − D makes D a square mod n; (b/p) is just whether x = 0 carries a point.)

```
run    cand pub   (n/p)  (p/n)  (t/p)  (t/n)  (b/p) (-3/n)  (f/n) (-1/n)  (2/n)    n%4    n%8    p%4    p%8    t%4
P-256   876           1     -1      1     -1      1      1      1     -1      1      3      7      3      7      1
P-256  1842   *      -1     -1      1     -1      1      1      1      1      1      1      1      3      7      3
P-224   777           1      1     -1      1      1      1      1     -1     -1      3      3      1      1      3
P-224  1485          -1     -1      1     -1     -1      1      1      1      1      1      1      1      1      1
P-224  5736          -1     -1      1     -1     -1      1      1      1      1      1      1      1      1      1
P-224  7026   *      -1     -1      1     -1     -1      1      1      1     -1      1      5      1      1      1
192     139   *       1      1      1      1      1     -1      1      1      1      1      1      3      7      3
192    2198           1      1      1      1      1      1      1      1      1      1      1      3      7      3
192    5228   *      -1      1      1     -1      1      1      1     -1     -1      3      3      3      7      1
192    5405           1      1     -1      1      1      1      1      1      1      1      1      3      7      3
192    6013   *       1      1      1      1      1      1      1      1      1      1      1      3      7      3
239      36           1     -1      1     -1      1      1      1     -1     -1      3      3      3      7      1
239    1562          -1      1     -1      1      1      1      1     -1      1      3      7      3      7      1
239    2185   *      -1      1     -1      1      1      1      1     -1     -1      3      3      3      7      1
239    2320   *      -1      1      1      1      1      1      1     -1     -1      3      3      3      7      1
239    2491           1      1     -1      1      1      1      1      1     -1      1      5      3      7      3
239    2682           1     -1      1     -1      1     -1      1     -1      1      3      7      3      7      1
239    2863           1     -1      1     -1      1     -1      1     -1      1      3      7      3      7      1
239    3048   *       1      1      1      1      1     -1      1      1      1      1      1      3      7      3
```

Quadratic reciprocity ties (n/p) and (p/n) together through n mod 4 and p mod 4 (equal unless both ≡ 3 mod 4), so there are fewer independent bits here than columns. Within a single run several columns happen to be constant on the published curves and differ on a skipped one — in P-256 (two curves) that is almost inevitable, and in P-224 the published curve is the only one with n ≡ 5 (mod 8). But no column takes the same published-constant value in all four runs: e.g. n mod 4 is 1 for the published P-256 and P-224 curves but the three published prime239 curves have n ≡ 3, 3, 1; (n/p) is −1 for published P-256/P-224 but +1 for published P-192, prime192v2, prime239v3. In the prime192 and prime239 runs, where three curves are published each, the published curves themselves disagree on nearly every symbol. No Legendre symbol or small residue class is a selection criterion.

### 6.19 Simulated early-abort rules and Elkies/Atkin balance

Hypothesis A.3(1): the 1997 point counter rejected good curves through a buggy early abort. For each of the 19 curves the true t and n are known, so any abort rule of the form "reject if some statistic ≡ 0 (mod ℓ) for some prime ℓ ≤ 100" can be simulated exactly. Rules tried, with what they reject:

```
rule                                                           skipped rejected   published rejected
(a) n ≡ 0 mod ℓ            correct abort (control)                 0/11               0/8
(b) p+1+t ≡ 0 mod ℓ        trace sign flipped (= twist order)      9/11               7/8
(c) order of the OTHER root of b (twist for p≡3 mod 4)             6/11               6/8
(d) sign and root both flipped                                     3/11               1/8
(e) t ≡ 0 mod ℓ            tests the trace, not the order          5/11               4/8
(f) t ≡ ±1, ±2 mod ℓ       sloppy trace tests                     11/11               8/8
(g1) n ≡ 1 mod ℓ           off-by-one (tests n−1)                 11/11               8/8
(g2) n ≡ −1 mod ℓ          off-by-one (tests n+1)                 10/11               7/8
(g3) |t| ≡ 0 mod ℓ         signed/unsigned confusion               5/11               4/8
(g4) gcd(partial CRT order, modulus) > 1   = (a)                   0/11               0/8
(h) twist order ≡ 0 mod ℓ  twist-security abort                    9/11               7/8
```

None separates. Rules (f), (g1) fire on essentially everything, (b), (h) on most of both groups, (d) on the P-224 run only (because P-224 has p ≡ 1 mod 4 and the "other root" is the same curve). Bounded versions — "reject at the first ℓ ≤ B where the statistic vanishes" for any B ≤ 1000 — were tested for all these statistics (and for t ± 1, t ± 2, n ± 1): for no statistic do the skipped curves' first-ℓ values all lie below the published curves' (or all above). Single-residue rules "X ≡ r (mod ℓ)" for X ∈ {n, t, n', n ± 1, t ± 1}, ℓ ≤ 100, r arbitrary: none is satisfied by six or more skipped curves and zero published ones.

None of these simulated abort rules explains the labels. That does not exclude consistent bugs involving untested intermediate values, arithmetic representations, or particular modular polynomials.

**Elkies vs Atkin primes (hypothesis A.3(2), time limit).** ℓ is Elkies iff (D/ℓ) ≥ 0. Counts for 3 ≤ ℓ ≤ 97 (24 primes):

```
run     cand pub  Elkies Atkin
P-256    876       10    14
P-256   1842  *    13    11
P-224    777       14    10
P-224   1485       13    11
P-224   5736       11    13
P-224   7026  *     8    16
192      139  *     9    15
192     2198       11    13
192     5228  *     6    18
192     5405       10    14
192     6013  *    13    11
239       36       12    12
239     1562       17     7
239     2185  *     8    16
239     2320  *    10    14
239     2491       11    13
239     2682       17     7
239     2863       13    11
239     3048  *    12    12
```

Published mean 9.9 Elkies, skipped mean 12.5: the opposite direction from a simple unweighted-Elkies-count timeout proxy. The two most Elkies-rich curves are skipped. These counts are not timings of a historical SEA implementation and do not exclude a real time limit, whose cost depends on degrees, arithmetic paths, and implementation details.

### 6.20 Remaining process hypotheses: indices, seed bytes, base-point step, human choice

**Position-dependent bug (A.3(3)).** The eleven skipped indices are 36, 777, 876, 1485, 1562, 2198, 2491, 2682, 2863, 5405, 5736; the published eight are 139, 1842, 2185, 2320, 3048, 5228, 6013, 7026. Tested: popcount; residues mod 2…256; the byte offset 20(i − 1) of the candidate in the lrand48 stream mod 64…65536 (buffer-boundary bugs); every modulus m ≤ 4096 for which the skipped indices (or offsets) fall into ≤ 3 residue classes disjoint from the published; each bit position of i. Nothing separates. Parity, for instance, is 5 odd / 6 even among skipped and 4 / 4 among published.

**Seed byte patterns (A.3(4), different candidate stream).** If the program mangled some seeds before hashing (C-string truncation at 0x00, text-mode newline translation of 0x0A/0x0D, a bignum conversion dropping leading zeros), the affected "candidates" were never tested as such. Checked for every viable seed: top bit, first byte, count of 0x00 bytes, presence of 0x0A/0x0D/0x1A/0x20/0xFF, number of bytes ≥ 0x80, bit length, parity, popcount, and byte-value sets. Two skipped seeds contain a 0x00 byte (5736, 36) and no published seed does — suggestive for those two but it leaves nine unexplained, and 0x0A appears in skipped and published seeds alike (1485, 5736, 3048). Top bit is 0 for 8 of 11 skipped and 3 of 8 published, so a "bitlen(seed) = 160" check is excluded too (published P-192's seed has a 158-bit value). No byte position has disjoint value ranges between the groups.

**Failed base-point step (A.3(6)).** For the May 1997 runs Anthropic published the base-point recipe (FreeLIP `zrandom`, seed s, discard 7, 26-bit limbs, first x on curve). Control: the six published seeds reproduce the six published Gx here. Running the recipe on every viable prime192/prime239 curve — with each of the six published seeds and with every seed 20000…20600 — the number of tries to the first on-curve x behaves identically for published and skipped curves (mean ≈ 2.0, max 8–15, ≈ 12–16 % needing more than 3 tries in every case), and the assembled x exceeds p before reduction in every run (so a "reject if x ≥ p" bug would have killed everything). The recipe has no failure branch that fires on the skipped curves and not the published ones.

**Two-pass human choice (A.3(5)).** If all valid curves were printed and a person picked, the picks might be extremal in some printed column. For each run, whether the k published curves are exactly the k smallest or k largest under index, seed (as integer or hex string), b, n, t, n − p: in the single-published runs the published curve is the largest index (the "last viable" fact) and also has the smallest b (P-256: 1 of 2; P-224: 1 of 4), but in prime192 and prime239 the three published curves are not the top-3 or bottom-3 under any of these keys. No sorting rule fits.

**Union-of-bugs hypothesis:** tested by set cover in §6.21; the true labelling needs four predicates. The exact endpoint-conditioned comparison admits covers at least that small in 88/126 labellings (69.8%) — no evidence for an exceptional fit under that null.

**Status of Part A.3.** The tested abort, index, seed-byte, base-point, and sorting models do not fit the full labelling; Elkies counts do not support one simple timing proxy. The skips remain unexplained. The tests do not establish that the reason was unrelated to the parameters or unrecoverable from them.

### 6.21 Set cover: could the skips be a union of several small bugs?

The union-of-defects hypothesis was tested as set cover: from 135 predicates on seed bytes, n, t, b, index, residues and symbols, use only predicates false on all published curves, and find the smallest union covering all skipped ones, through size 5. The original exploratory null used 300 random within-run, count-preserving relabellings. Review adds conditioning on each recorded window ending at a published candidate, and enumerates all 126 possible labellings exactly.

Result (`cover.py`, `cover.md`, `cover.json`):

- True labelling: **minimal cover size 4**, ten distinct minimal covers, all made of residue-class predicates (e.g. `20(i−1) mod 4096 < 1024 ∪ b ≡ 1 mod 7 ∪ n ≡ 7 mod 8 ∪ t ≡ 0 mod 7`). Nothing bug-shaped appears in any minimal cover; the best single usable predicate covers 6 of 11 (`t ≡ 1 mod 8`).
- Exact endpoint-conditioned relabellings: cover size 2 in 1 case, 3 in 35, 4 in 52, 5 in 23, and none ≤ 5 in 15. A cover of size ≤ 4 exists in **88/126 = 69.8%**. The original count-only Monte Carlo comparison gave 35%; these are different null models, not interchangeable estimates.
- The genuinely bug-shaped predicates individually: seed contains 0x00 — 2/11 skipped, 0/8 published; seed contains 0x0A — 2/11, 1/8; 0x0D — 1/11, 1/8; 0xFF — 0/11, 1/8; 0x20 — 1/11, 1/8; n > p (negative trace, allowed by the size rule when bitlen(n) = bitlen(p)) — 3/11 skipped, 1/8 published (prime239v2, the case Filippo notes); b shorter than p by a bit — 5/11 vs 5/8. None covers more than two skipped curves while excluding the published ones.

Conclusion: no union of at most three predicates in this library explains the labels, and the observed minimum of four is not unusual under the endpoint-conditioned null. The library was selected during exploration; the comparison neither establishes randomness nor excludes other unions, intersections, thresholds, or stateful checks.

### 6.22 Complete discriminant factorizations, second-order structure, and the multi-check model

**Full factorizations.** Every |D| = 4p − t² is now completely factored (PARI ECM/MPQS; the 255-bit P-256 cofactor took 18 s, the longest 133 s; `results/Dfac.out`). With them, every first-order statistic of the discriminant primes: number of distinct primes ω, with multiplicity Ω, largest and second-largest prime factor, 10⁶-smooth part. Per-run ranking of published against skipped is "mixed" for every statistic in the two three-curve runs; P-224's published curve is the most-factored of its four (Ω = 9) while P-256's published curve is the less-factored of its two. A weak population lean (published discriminants have fewer small factors: smooth part median 7 bits vs 28; one-sided permutation p ≈ 0.05) is a trend, not a trait.

| run | cand | pub | ω | Ω | prime sizes of |D| (bits) |
|---|---|---|---|---|---|
| P-256 | 876 | | 6 | 6 | 2, 9, 11, 12, 92, 134 |
| P-256 | 1842 | ★ | 5 | 5 | 2, 3, 39, 81, 136 |
| P-224 | 777 | | 8 | 8 | 2, 3, 5, 10, 13, 39, 61, 97 |
| P-224 | 1485 | | 4 | 4 | 2, 6, 9, 211 |
| P-224 | 5736 | | 6 | 6 | 2, 4, 11, 15, 86, 112 |
| P-224 | 7026 | ★ | 7 | 9 | 2, 2, 2, 5, 7, 13, 16, 34, 149 |
| 192 | 2198 | | 3 | 3 | 12, 25, 157 |
| 192 | 5405 | | 4 | 4 | 13, 16, 49, 119 |
| 192 | 139 | ★ | 4 | 4 | 3, 4, 5, 184 |
| 192 | 5228 | ★ | 4 | 4 | 3, 51, 58, 84 |
| 192 | 6013 | ★ | 3 | 3 | 3, 12, 179 |
| 239 | 36 | | 4 | 4 | 9, 9, 19, 205 |
| 239 | 1562 | | 5 | 5 | 3, 4, 5, 72, 160 |
| 239 | 2491 | | 4 | 4 | 4, 7, 55, 177 |
| 239 | 2682 | | 10 | 12 | 3, 3, 3, 4, 4, 8, 19, 23, 26, 35, 37, 81 |
| 239 | 2863 | | 3 | 3 | 3, 90, 149 |
| 239 | 2185 | ★ | 3 | 3 | 5, 21, 217 |
| 239 | 2320 | ★ | 5 | 6 | 3, 3, 4, 23, 79, 132 |
| 239 | 3048 | ★ | 2 | 2 | 3, 239 |

**Second-order structure (q ± 1 for q | D).** For all 40 primes q > 10⁶ dividing a discriminant, q − 1 and q + 1 were fully factored (`results/qpm1.out`). Per candidate: max and sum of v₂(q − 1); counts of q ≡ 1, 3 (mod 4) and q ≡ 1 (mod 3); largest prime factor of q ± 1 relative to q for the large q. Nothing separates in any run. Cross-divisibility q_i | q_j ± 1 within a discriminant: all hits are q_i = 3 (always true), q_i = 5 (coin flips), or seven q_i ∈ {11, 13, 41, 71} hits that all land on skipped curves — but the expected number of such hits is ≈ 1.6 for the published set (whose discriminants simply carry fewer medium primes) and ≈ 6 for the skipped, so 0 vs 7 is p ≈ 0.2. Across candidates in a run, shared primes (29 in P-224; 11, 13 in prime239) and cross-divisibilities mix published and skipped.

**Exact class numbers.** `quadclassunit` on the 58–78-digit fundamental discriminants did not finish in this PARI build (> 1 h on the smallest); the write-up rests on Euler-product estimates, stable to 0.01 between bounds 10⁵ and 10⁶. The 19 fundamental discriminants are reproducible from `data/` for anyone with Sage or Magma.

**Sequential multi-check model (exploratory record).** Candidate-local, side-effect-free checks in sequence reject exactly the union of their failure predicates. The original experiment on thresholds of about 22 invariants found no disjunction of at most four that covered all eleven skips; its count-only random-label comparison gave 32%. This threshold experiment has not been regenerated with the endpoint-conditioned null, and its generating script is not included, so that percentage is not a reproduced review result. The observed relative class-number estimates do not support a universal separating floor or ceiling. This does not exclude a check passing all nineteen candidates, run-dependent thresholds, or checks whose side effects change the candidate stream.

### 6.23 Factorization of b as an integer

b is the one seed-derived integer in each candidate (a = −3 is fixed), so a program that looked at b itself — its factorization, its residues — would have a hook here that the point-count tests cannot see. All nineteen b values were factored completely (msieve 1.54 QS/ECM; every cofactor passed a primality test and the products were checked; `results/bfac-msieve.out`, `results/bfac.txt`, `scripts/bfac/`). Field size, bit length, Ω, ω, largest-prime-factor bits, second-largest, smooth part, square-freeness and b mod 3, 4, 5, 7, 8:

```
run    cand  pub  p   |b|  Ω  ω  LPF  2nd  smooth  sqfree  b mod 3 4 5 7 8   factor bit lengths
P-256    876      256  256  5  5  216   27     40   y      0 1 0 1 5   [2, 3, 9, 27, 216]
P-256   1842  *   256  255  5  4  201   29     54   n      2 3 1 0 3   [3, 3, 20, 29, 201]
P-224    777      224  223  8  7  134   34     89   n      2 0 1 3 4   [2, 2, 10, 11, 12, 22, 34, 134]
P-224   1485      224  224  5  4  107   82    117   n      1 0 1 2 4   [2, 2, 34, 82, 107]
P-224   5736      224  223  7  5  127   55     97   n      2 0 4 4 0   [2, 2, 2, 16, 24, 55, 127]
P-224   7026  *   224  223  7  6  149   28     75   n      0 1 2 4 5   [2, 2, 7, 16, 21, 28, 149]
192      139  *   192  191  7  7   96   66     96   y      0 1 0 4 1   [2, 3, 7, 7, 13, 66, 96]
192     2198      192  192  5  5   95   71     98   y      1 2 1 2 2   [2, 13, 14, 71, 95]
192     5228  *   192  190  8  8   50   46    140   y      1 2 2 5 6   [2, 10, 11, 13, 21, 41, 46, 50]
192     5405      192  192  6  6   77   46    116   y      1 3 2 1 7   [9, 16, 20, 26, 46, 77]
192     6013  *   192  192  6  6   76   58    117   y      0 3 2 4 3   [2, 4, 21, 33, 58, 76]
239       36      239  236  7  7   89   57    147   y      0 2 1 2 2   [2, 2, 4, 30, 56, 57, 89]
239     1562      239  239 13  9  112   61    127   n      0 0 4 6 4   [2, 2, 2, 2, 2, 2, 6, 7, 11, 14, 22, 61, 112]
239     2185  *   239  239  5  5  119   79    120   y      2 2 1 3 2   [2, 9, 32, 79, 119]
239     2320  *   239  239  8  7  195   25     44   n      2 0 0 5 4   [2, 2, 3, 4, 5, 7, 25, 195]
239     2491      239  236  6  5  103   73    133   n      2 0 0 3 4   [2, 2, 3, 56, 73, 103]
239     2682      239  235  2  2  219   16     16   y      2 3 1 5 3   [16, 219]
239     2863      239  239 10  7  180   27     59   n      0 1 0 0 5   [2, 2, 3, 3, 3, 3, 4, 15, 27, 180]
239     3048  *   239  238  9  7  139   72     99   n      0 2 1 3 6   [2, 2, 2, 2, 6, 7, 10, 72, 139]
```

Every statistic interleaves. Largest-prime-factor bits, ranked within each run: P-256 published 201 < skipped 216; P-224 published 149 is the largest of four; prime192 published 50, 76, 96 bracket the skipped 77, 95; prime239 published 119, 139, 195 sit among skipped 89, 103, 112, 180, 219. Ω runs 5–9 on the published side and 2–13 on the skipped side (the skipped 2682 is 51239 × a 219-bit prime; the skipped 1562 has 2⁶·3⁴ in it). Four of eight published and five of eleven skipped b are square-free. No residue class mod 3, 4, 5, 8 is constant on either side; mod 7 the published values avoid {1, 2, 6}, which with eight draws from seven classes is a ~1% coincidence before the look-elsewhere correction over the moduli tried, and the b ≡ r (mod 7) predicates were already in the §6.21 library (b ≡ 1 mod 7 appears in minimal covers there). Crossed with the quadratic character (`results/legendre-b.txt`): (b/p) = +1 is forced on the fifteen p ≡ 3 (mod 4) curves (§6.10, §6.13), and on the four P-224 candidates it is a fair coin — +1 for the skipped 777, −1 for the skipped 1485 and 5736 and for the **published** 7026, which therefore has no point at x = 0. The three non-squares have Ω = 5, 7, 7 and largest prime factors of 107, 127, 149 bits, inside the range of the sixteen squares; the symbol depends on p and carries no information about b's factorization as an integer. Nothing about b as an integer separates the labels. The multiplicative structure of b is also what the §6.19 abort models did not touch, so this closes the one remaining candidate-local input the program had in hand before point counting.

### 6.24 Deeper factorization of the extension-field order cofactors (k = 3, 4, 6)

§6.17 trial-divided #E(F_{p^k})/n to 10⁶. Here the genuinely new pieces are isolated by dividing out the subfield orders — C₃ = #E(F_{p³})/n (so n is removed), C₄ = #E(F_{p⁴})/#E(F_{p²}) = (p−1)² + t² (n and the twist order removed), and C₆ = #E(F_{p⁶})·n/(#E(F_{p³})·#E(F_{p²})) — and each is run through GMP-ECM at a full t25 level plus half of t30 (trial division to 10⁶, 280 curves at B1 = 50 000, 215 at 250 000; `scripts/extfac/`, `results/extfac.json`, `results/extfac.txt`). That reliably finds every prime factor below ~2⁸⁰ and most below ~2¹⁰⁰; the remainders of 180–490 bits are unfactored and marked P or C.

```
--- k=3
run    cand pub  bits  smooth(<2^40) bits  found factor bits                       rem   LPF-found bits
P-256    876      512     28                [2, 2, 3, 3, 5, 13]                      489C  13
P-256   1842  *   512      4                [2, 2, 59, 59]                           394C  59
P-224    777      449     31                [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 7, 44, 90] 297P  90
P-224   1485      449     54                [2, 2, 6, 19, 25, 55]                    344P  55
P-224   5736      449     21                [2, 2, 3, 3, 4, 7, 82]                   351P  82
P-224   7026  *   449     44                [2, 2, 40, 68, 68, 79]                   194P  79
192      139  *   385     58                [2, 2, 14, 40]                           330C  40
192     2198      385      7                [2, 2, 3]                                380P  3
192     5228  *   385     13                [2, 2, 4, 5, 43, 72, 81]                 180C  81
192     5405      385     53                [2, 2, 3, 5, 6, 35]                      336C  35
192     6013  *   385     18                [2, 2, 3, 11]                            369C  11
239       36      478     49                [2, 2, 4, 16, 25, 97]                    336C  97
239     1562      478     17                [2, 2, 5, 8]                             464C  8
239     2185  *   478     49                [2, 2, 12, 15, 18, 86, 94]               254P  94
239     2320  *   478      4                [2, 2, 109]                              368C  109
239     2491      478      9                [2, 2, 5]                                472C  5
239     2682      478     79                [2, 2, 6, 12, 14, 18, 25]                406C  25
239     2863      478     54                [2, 2, 12, 38, 82]                       346C  82
239     3048  *   478     52                [2, 2, 8, 20, 20, 89, 99]                243P  99

  published smooth-part bits [4, 4, 13, 18, 44, 49, 52, 58]; largest found factor bits [11, 40, 59, 79, 81, 94, 99, 109]; prime remainder in 3/8
  skipped   smooth-part bits [7, 9, 17, 21, 28, 31, 49, 53, 54, 54, 79]; largest found factor bits [3, 5, 8, 13, 25, 35, 55, 82, 82, 90, 97]; prime remainder in 4/11

--- k=4
run    cand pub  bits  smooth(<2^40) bits  found factor bits                       rem   LPF-found bits
P-256    876      512     11                [11, 58]                                 444C  58
P-256   1842  *   512     67                [4, 14, 19, 30]                          447C  30
P-224    777      448     17                [17]                                     432P  17
P-224   1485      448     26                [6, 20, 60]                              364P  60
P-224   5736      448     14                [14, 53, 56]                             327C  56
P-224   7026  *   448      0                [85]                                     364C  85
192      139  *   384      7                [3, 4]                                   378P  4
192     2198      384     27                [6, 9, 12, 52, 61]                       247P  61
192     5228  *   384     24                [3, 7, 14, 56, 75]                       232C  75
192     5405      384     33                [4, 29]                                  352P  29
192     6013  *   384      3                [3, 77]                                  306P  77
239       36      478     13                [13, 41, 53]                             373C  53
239     1562      478      3                [3, 58]                                  419P  58
239     2185  *   478     41                [8, 10, 23, 51]                          389C  51
239     2320  *   478     87                [3, 3, 6, 10, 28, 37]                    395P  37
239     2491      478     84                [4, 7, 36, 37, 55, 69]                   273C  69
239     2682      478     34                [3, 3, 4, 8, 16, 88]                     361C  88
239     2863      478     45                [3, 14, 28]                              435P  28
239     3048  *   478     45                [3, 11, 31, 59]                          377P  59

  published smooth-part bits [0, 3, 7, 24, 41, 45, 67, 87]; largest found factor bits [4, 30, 37, 51, 59, 75, 77, 85]; prime remainder in 4/8
  skipped   smooth-part bits [3, 11, 13, 14, 17, 26, 27, 33, 34, 45, 84]; largest found factor bits [17, 28, 29, 53, 56, 58, 58, 60, 61, 69, 88]; prime remainder in 6/11

--- k=6
run    cand pub  bits  smooth(<2^40) bits  found factor bits                       rem   LPF-found bits
P-256    876      512      8                [2, 2, 2, 2, 65]                         443C  65
P-256   1842  *   512     65                [2, 2, 2, 2, 2, 6, 17, 32]               452P  32
P-224    777      448     31                [2, 2, 2, 2, 23]                         421C  23
P-224   1485      448     52                [2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 28, 97] 309C  97
P-224   5736      448     28                [2, 2, 2, 2, 2, 2, 2, 2, 12, 52, 74]     303C  74
P-224   7026  *   448     38                [2, 2, 2, 2, 2, 2, 3, 3, 5, 5, 10, 62, 89] 269C  89
192      139  *   384     20                [2, 2, 8, 8]                             367C  8
192     2198      384     44                [2, 2, 3, 3, 34, 42]                     301P  42
192     5228  *   384     47                [2, 2, 4, 5, 9, 11, 14]                  342P  14
192     5405      384     24                [2, 2, 5, 15]                            363P  15
192     6013  *   384     23                [2, 2, 19]                               364C  19
239       36      478      8                [2, 2, 4]                                473P  4
239     1562      478     28                [2, 2, 24]                               453C  24
239     2185  *   478     71                [2, 2, 8, 29, 30]                        411P  30
239     2320  *   478     84                [2, 2, 9, 12, 17, 17, 25, 56]            345C  56
239     2491      478      9                [2, 2, 5]                                472C  5
239     2682      478     30                [2, 2, 7, 8, 11]                         453C  11
239     2863      478      4                [2, 2]                                   476P  2
239     3048  *   478     78                [2, 2, 5, 6, 19, 20, 24, 68]             339C  68

  published smooth-part bits [20, 23, 38, 47, 65, 71, 78, 84]; largest found factor bits [8, 14, 19, 30, 32, 56, 68, 89]; prime remainder in 3/8
  skipped   smooth-part bits [4, 8, 8, 9, 24, 28, 28, 30, 31, 44, 52]; largest found factor bits [2, 4, 5, 11, 15, 23, 24, 42, 65, 74, 97]; prime remainder in 4/11
```

Everything interleaves: smooth parts, largest found prime factor, whether the remainder is prime. The one 2σ-ish contrast is the 2⁴⁰-smooth part of C₆, published [20–84 bits, median 56] against skipped [4–52, median 28]; a rank-sum z ≈ 2.2, which across three k, three statistics each and the ~50 invariants already tried is the expected size of the largest coincidence, and C₆ is not a quantity a 1997 program would have computed (n ∤ C₆ for any of these curves, the embedding degree being > 20 000). Published and skipped curves are not separated by the cubic, quartic or sextic extension orders at this depth.

## Part C. Base-point structure (separate from the skips)

## 7. Base-point structure

For all ten published prime-field generators (P-192, P-224, P-256, P-384, P-521, prime192v2/v3, prime239v1/v2/v3; parameters verified by n·G = O), computed k·G and (k⁻¹ mod n)·G for 2 ≤ k ≤ 2¹⁶ and recorded the bit length of x and of min(y, p − y) (so negations are covered). Looking for a hash-sized coordinate — 128 bits (MD5) or 160 bits (SHA-1) — or anything else far below the field size:

| Curve | G/2 x-coordinate | shortest x found, k ≤ 2¹⁶ either way | rough expected min of 2¹⁷ random |
|---|---|---|---|
| P-192 | full size | 174 bits (61807·G) | ~175 |
| prime192v2 | full size | 175 bits (G/7467) | ~175 |
| prime192v3 | full size | 176 bits (9061·G) | ~175 |
| P-224 | full size | 208 bits (G/42457) | ~207 |
| prime239v1 | full size | 222 bits (41569·G) | ~222 |
| prime239v2 | full size | 220 bits (G/40829) | ~222 |
| prime239v3 | full size | 221 bits (4319·G) | ~222 |
| P-256 | full size | 237 bits (G/53620) | ~239 |
| P-384 | full size | 367 bits (14971·G) | ~367 |
| P-521 | full size | 502 bits (10735·G) | ~504 |

Every reported minimum x is within two bits of the rough minimum expected from 2¹⁷ uniform field elements. The prime-field scan finds no bare 128/160-bit coordinate within its radius. For these cofactor-1 curves, subgroup division is unique. Expanded hashes, RNG seeds, scalar mappings, and larger multipliers remain possible; see `base-point-brief.md`.

### 7.1 Binary curves: the K-163 half-point

The same scan over GF(2^m) (PARI/GP with `ffgen`; parameters from the std-curves database, each verified by G ∈ E and n·G = O) for the ten NIST binary curves — k·G for 2 ≤ k ≤ 2¹⁶ and G/k for 2 ≤ k ≤ 2¹², negations covered via y ↦ x + y. Results (`binpts.gp`, `binpts.out`):

| Curve | h | G/2 x bits | shortest x found | random expectation |
|---|---|---|---|---|
| B-163 | 2 | 163 | 147 (37609·G) | ~147 |
| **K-163** | **2** | **126** | **126 (G/2)** | ~147 |
| B-233 | 2 | 232 | 215 (G/1579) | ~217 |
| K-233 | 4 | 232 | 219 | ~217 |
| B-283 | 2 | 283 | 267 | ~267 |
| K-283 | 4 | 281 | 267 | ~267 |
| B-409 | 2 | 408 | 391 | ~393 |
| K-409 | 4 | 409 | 393 | ~393 |
| B-571 | 2 | 571 | 554 | ~555 |
| K-571 | 4 | 555 | 555 | ~555 |

Nine of ten are random-looking. **K-163 is not.** Its half-point G/2 = ((n+1)/2)·G is

x = 0x23e21d6019e1211f6bd47ec180256e97 (126 bits), y = 161 bits,

a 128-bit-sized x-coordinate on a 163-bit curve. Under a uniform-coordinate heuristic, a specified x meets this threshold with probability 2⁻³⁷. There were 69,630 point evaluations per binary curve, 696,300 total, giving about 5.1 × 10⁻⁶ expected x-hits. Across both prime and binary scans, allowing x and both y signs gives a rough trial-count heuristic of 4.4 × 10⁻⁵, before other exploratory pattern choices. These are not calibrated discovery probabilities, and novelty has not been established.

A plausible reading is that a 128-bit x was chosen, y solved, and the cofactor applied. This is not a recovered recipe. Cofactor clearing has multiple rational preimages: if Q = [h⁻¹ mod n]G, they are Q + T for T in E(F_{2^m})[h], not just Q. Review checked all 28 such preimages across the ten binary curves. No additional 128-bit-x hit appears; K-163's other half has a 162-bit x. The larger k scans remain subgroup-only, so they do not exclude every cofactor-clearing construction.

**Coordinate and search correction (19 October).** `fromdigits(Vecrev(Vec(f.pol)),2)` reversed the 126 coefficient bits when printing the coordinate. The old value `3a5da90060df8af5be2121e601ae11f1` is that reversal, not the standard polynomial-basis integer. Removing `Vecrev` gives the coordinate above; the degree-based bit count was unaffected. All ten decimal exports and the hash-search target are corrected, and Python/PARI regression checks agree. The previous negative hash searches used the wrong target and do not apply to the corrected one; the full sweep was rerun against the corrected target on 19 October with the same string set and hash readings: 29,577,717 evaluations, no hits (`results/k163-search-rerun.txt`). The corrected 32-bit words have top bits 0,0,0,1, excluding four consecutive 31-bit `lrand48` words in that reading only.

### 7.2 The SEC 2 curves: a half-generator constant shared across four Koblitz curves

The same scan (k·G, k ≤ 2¹⁶; G/k, k ≤ 2¹²; all cofactor preimages where h > 1) run on the ten SEC 2 prime-field curves not already covered — secp112r1/r2, secp128r1/r2, secp160k1/r1/r2, secp192k1, secp224k1, secp256k1; parameters from SEC 2 v1.0 and v2.0, n·G = O verified for each (`scripts/secg_scan.py`, `results/secg-halfpoints.txt`). This reproduces, and extends to the full SEC 2 list, the observation in the Heninger–Scholl–Shumow Crypto 2019 rump-session talk, whose title *is* x(G/2) on secp160k1 (`48ce563f89a0ed9414f5aa28ad0d96d6795f9c62`).

Six of the ten look random: shortest coordinates within a few bits of the 2¹⁶ + 2¹² uniform expectation, and the cofactor preimages on the two h = 4 curves full-size. The four Koblitz curves do not:

```
secp160k1  x(G/2) =        48ce563f89a0ed9414f5aa28ad0d96d6795f9c62   (159 bits on 160)
secp192k1  x(G/2) = 554123b78ce563f89a0ed9414f5aa28ad0d96d6795f9c66   (187 on 192)
secp224k1  x(G/2) =      3b78ce563f89a0ed9414f5aa28ad0d96d6795f9c63   (166 on 224)
secp256k1  x(G/2) =      3b78ce563f89a0ed9414f5aa28ad0d96d6795f9c63   (166 on 256)
```

secp224k1 and secp256k1 have the *identical* 166-bit x at G/2. All four share the 148-bit core `ce563f89a0ed9414f5aa28ad0d96d6795f9c6`; three share `3b78` above it (192k1 has a further `55412` above that); the last nibbles are 2, 6, 3, 3. So the generators of Certicom's secp*k1 curves were built from one constant, by the recipe this record has been hypothesising for K-163 — choose x, solve y, double — and the constant was reused across fields. What produced the constant, why its high part differs between fields, and what set the last nibble are not resolved: a simple "smallest increment of …9c60 that lands on the curve" fails (…9c60 is already on secp160k1, …9c61 on secp256k1).

A second echo: x(G/2) on secp160r2 begins `4a96b5688ef573284664698`, the first 92 bits of x(G) on secp160r1 (`4a96b5688ef573284664698968c38bb913cbfc82`). The remaining 68 bits differ wholesale, which is not an increment either.

Against the rest: no shared substring of ≥ 32 bits between any SEC 2 half-generator and any NIST/ANSI prime or binary one, nor between any two NIST/ANSI ones; the K-163 value `23e21d6019e1211f6bd47ec180256e97` is not a substring or truncation of the secp constant. K-163 (sect163k1) is likewise a Certicom curve, so the secp*k1 pattern is the strongest external support so far for reading its short half as a chosen x. The things to try next on the constant itself are the same as for K-163 — fixed-width encodings and 1990s hashes of Certicom-era strings — but with a 148-bit core whose top and bottom are uncertain, so matching on the core rather than the full value.

## Part D. Reproducibility and sources

### 8. Reproducibility

The imported working files now live under `scripts/`, `data/`, and `results/`; not every exploratory script mentioned in the historical record was imported (in particular `fac*.gp` and the threshold-cover experiment). From the repository root, `python -X utf8 -m unittest discover -s scripts -p test_research.py -v` runs the review checks, and `python -X utf8 scripts/cover.py` regenerates the exact endpoint-conditioned cover outputs. Set `GP` to the PARI executable or put it on PATH for the arithmetic checks. The tests certify all nineteen viable prime orders, all ten binary exports and all 28 cofactor preimages; they do not rerun the 3,072 SEA counts or the full corrected-target phrase search. The retained long-scan minima were not affected by the coefficient-export error.

## 9. Sources

- Anthropic, "Claude reveals ECDSA curve origins", 2026-10-16. https://www.anthropic.com/research/ecdsa-curve-origins
- Filippo Valsorda, "The NIST Elliptic Curves Seeds Bounty Has Been Claimed", 2026-10-16. https://words.filippo.io/seeds-solved/
- Anthropic Frontier Red Team, "Discovering cryptographic weaknesses with Claude", 2026-07-28 (the programme the seed result came out of; no curve content). https://www.anthropic.com/research/discovering-cryptographic-weaknesses
- Koblitz & Menezes, "A Riddle Wrapped in an Enigma", IACR ePrint 2015/1018.
- ANSI X9.62-1998 / FIPS 186-2, Appendix A (curve generation and verification from a seed).
