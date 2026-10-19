# Brief: the unexplained NIST base points (P-224, P-256, P-384, P-521)

*Hand-off document for a fresh session. Written 2026-10-17 after a night of work on the skipped-seed question, which is closed as a negative result (see `cm-hypothesis.md`). Everything below funnels into one target: where the four unexplained generators came from.*

## 1. What is settled

- **Curve coefficients (b) for all fourteen NIST/ANSI prime and binary curves**: the FIPS 186-2 / X9.62 `SEED` values are raw `lrand48()` output after `srand48(unix_timestamp)`, 1997–98 (Anthropic, "Claude reveals ECDSA curve origins", 2026-10-16; independently reproduced here and by Filippo Valsorda). The "hash of a Solinas sentence" story is false *as told about the seeds*.
- **Square-root convention**: for every published curve over p ≡ 3 (mod 4), b = (−27/c)^((p+1)/4) mod p, never the other root (seven of seven). The 1997 code used the textbook root. Likely the same code path produced y-coordinates from x-coordinates, if it did that at all.
- **Base points for P-192 and the five ANSI X9.62 example curves** (prime192v2/v3, prime239v1/v2/v3): x-coordinates come from FreeLIP's `zrandom` (state × 3¹²¹ mod 2¹⁰⁷ − 1), seeded with small integers (20000, 20420, 20507, 20509, 20512, 20517), seven outputs discarded, 26-bit limbs assembled into x, first x on the curve taken. Reproducer on the Anthropic page. These were generated in May 1997.
- **Skipped viable seeds** (11 across the four prime runs, against 8 published): no algebraic invariant separates them from the published curves — class number (either direction), embedding degree, twist order, n ± 1 smoothness, isogeny structure over F_p and extensions, short-x points, low-byte x bitmaps, congruences on t/n/b. No simple event-triggered RNG-consumption rule fits either. Treat as closed; most likely a lost early-abort or a program artifact. Full write-up: `cm-hypothesis.md`.

## 2. What is open

- **Base points for P-224, P-256, P-384, P-521.** No derivation known to anyone. Anthropic tested the FreeLIP recipe and it does not fit. These curves were generated Aug 1997 (P-521, P-256, P-384) and Apr 1998 (P-224) — after the May 1997 FreeLIP-era runs, so the base-point code may have changed between runs.
- **Base points for the binary curves** (B-163 … B-571; also K-curves). Unexplained.
- **B-163 seed.** Unexplained.

## 2a. New lead: K-163 (found 2026-10-17, after this brief was first written)

On K-163 (Koblitz, b = 1, cofactor 2), the half-point G/2 = ((n+1)/2)·G has x = **0x3a5da90060df8af5be2121e601ae11f1** — 126 bits, a 128-bit-sized value — with full-size y. Parameters verified (G ∈ E, n·G = O, 2·(G/2) = G). None of the other nine binary curves, and none of the ten prime-field curves, has anything like it. Reading: x(P) was a 128-bit chosen value (MD5? a 128-bit RNG?), y solved from it, G = 2·P. **This is now the primary target:** find a string s and hash H with H(s) = 3a5da900 60df8af5 be2121e6 01ae11f1 (try both byte orders, and the possibility that x was reduced or that the value is a truncated SHA-1). Already tried and negative (`scripts/k163/`): ≈ 29.6 million evaluations — the Solinas phrases, people/org/curve-name strings with case, punctuation, newline/NUL and UTF-16 variants, every date 1997–98 in 13 formats, the run timestamps as decimal/hex/ctime, under MD5, MD4, SHA-0, SHA-1, RIPEMD-128/160 and doubled variants, with X9.62-style appended counters, read as-is / byte-reversed / word-swapped / high or low 128 of a 160-bit digest / top-two-bits-masked. It is not four lrand48 words. See cm-hypothesis.md §7.1 and binpts.out.

## 2b. The binary-curve side (B and K curves)

Anthropic's post covers the binary curves only for seeds: B-233/283/409/571 are five full 31-bit `lrand48` words per candidate from one sitting on 1998-04-17 (clock apparently halved); B-163's seed fits nothing they tried. Binary base points get one sentence ("the same goes for the NIST binary curves" — unexplained). K curves are not mentioned: they have no seed (a ∈ {0,1}, b = 1), so for a Koblitz curve the generator is the *entire* provenance question. Three work items, in priority order:

**(i) K-163's half-point value.** Covered in §2a. Note the implication for method: if G = 2·P with x(P) a 128-bit value, the binary base-point procedure was "choose x, solve y, multiply by h" — different in kind from the FreeLIP procedure on the prime curves (random x, first on-curve x, no cofactor step).

**(ii) The other nine binary generators under the same method.** `binpts.out` shows G/h (h = 2 for B curves, 4 for K-233…571) has a full-size x on every one of them, and nothing short appears for k ≤ 2¹⁶ or G/k, k ≤ 2¹². So on those curves, if the method was choose-x-then-×h, x was full-size — a hash *expanded* to field size, or an RNG output, not a bare digest. Test with the same lookup table as the prime curves, built on the binary field: for each curve store x(G/h), x(G/(2h)), x(G/(4h)) and the small multiples, then compare against (a) X9.62-style SHA-1 expansion of candidate strings to m bits, (b) `lrand48`-word concatenations in the 31-bit and 32-bit layouts and both clock conventions that Anthropic found for the B seeds — the base points may have come from the same 1998-04-17 session, so sweep `srand48(t)` and `srand48(t/2)` for t within ±1 day of the four seed timestamps and compare every 20-byte / 5-word window against x(G/h). (c) For the five B curves, also test whether x(G/h) or x(G) equals the curve's own seed-derived value under any X9.62 expansion (seed → SHA-1 chain → m bits), since a lazy program might have reused the seed machinery for G.

**(iii) B-163's seed.** `85E25BFE5C86226CDB12016F7553F9D0E693A268`. Nothing in the two posts explains it. Checklist: every 1990s C-library PRNG (`lrand48`/`mrand48`/`drand48` bit layouts, `rand()` from BSD and System V, `random()`, Park–Miller, Knuth's subtractive generator, Numerical Recipes `ran0/1/2`), each at every byte offset and word size, with and without the halved clock; a FreeLIP `zrandom` stream (it was on the same machine in 1997); seed = hash (MD5, SHA-0, SHA-1) of a short string, including the other 13 seeds, curve names, dates; seed derived from another seed (XOR/addition of two published seeds, byte permutation of one); hand-typed or hex-edited (look at the ASCII of the bytes, repeated nibbles, keyboard-adjacent hex). The negative space is informative too: if B-163's seed is unlike every other one, B-163 may have been generated at a different time by a different process — B-163/K-163 are the WTLS/ANSI "sect163" curves and may predate the April 1998 session.

Deliverable for (ii) and (iii): a table of what was tried, in the same style as cm-hypothesis.md Part A, so the next person does not repeat it.

## 3. The displaced hypothesis

The Solinas lore ("the seed was a hash of a joke about Bob and Jerry getting a raise") cannot be about the curve seeds. If it is true at all, the only place it can live is the base points. Nobody has tested it there.

Concrete form: **G, or a small multiple of G, has an x-coordinate (or y) derived from a 1997-era hash of a human-readable string.**

What the data already say (this session, `mult.out`):

- For all ten published prime-field generators, the half-point G/2 (= (2⁻¹ mod n)·G) has a full-size x-coordinate.
- Over k = 2 … 2¹⁶ in both directions (k·G and G/k, 2¹⁷ points per curve, negations covered since ±P share x and y is reported as min(y, p−y)), no point has a coordinate shorter than the field size minus ~20 bits — exactly the minimum expected from 2¹⁷ random values. No 128- or 160-bit coordinate anywhere.
- So "hash output is x, then double/small-multiply" with a *bare* hash as x is excluded at this radius. Surviving forms: the hash is padded/expanded to field size (as the X9.62 seed-to-c procedure does), or the hash chooses x in some other way (e.g., hash gives a FreeLIP-style seed integer, or a counter is hashed), or the multiplier is outside the radius.

## 4. Plan for the new session

**Step 0 — fix the target set.** Four points: P-224, P-256, P-384, P-521 generators. Optionally also run every test on the six FreeLIP-explained points as a control: anything that "finds" a derivation for those is a false positive.

**Step 1 — precompute a lookup table per curve** (cheap, do once): x-coordinates of k·G and G/k for k up to some radius R (R = 2¹⁶ is minutes; 2²⁰ is an hour per curve in PARI, far less in C). Store as a hash set of x values. Also store the *low* and *high* 128/160-bit windows of each x, so a hash can be matched against a truncated or padded coordinate, and store min(y, p−y) likewise.

**Step 2 — candidate strings.** Solinas-flavoured sentences and their variants ("Jerry Solinas should make a million dollars a year" and the versions Solinas himself gave in 2015 — "Give Bob and Jerry a raise", "Bob and Jerry rule" — plus raises, salaries, Bob Reiter, Jerry Solinas, "rule", years, "NSA", curve names "P-256"/"P256"/"nistp256", dates in several formats, the srand48 timestamps themselves as decimal/hex/ctime strings, "Give Bob and Jerry a raise", "Bob and Jerry rule", punctuation and case variants, with and without trailing newline/NUL). Build it with an LLM; this is the part a model is good at. Keep the list in a file with provenance.

**Step 3 — hash and map.** For each string, each of MD5, SHA-1, SHA-0 (and RIPEMD-160, SHA-1 of SHA-1, counter-appended variants), produce candidate x values in each mapping:
  - bare digest as x (big- and little-endian);
  - digest expanded to field size by the X9.62 Appendix A seed-to-integer procedure (SHA-1 chain with counter) — this is the most "1997-NSA" mapping;
  - digest repeated/zero-padded to field size;
  - digest as a FreeLIP `zrstarts` seed, then the published FreeLIP recipe;
  - digest as an `srand48` seed, then lrand48 bytes as x.
  For each candidate x: test x on curve; if on curve, compute the point and look up both its x and the x of its small multiples in the Step 1 table. Also test "x = candidate, take first on-curve x ≥ candidate" (the FreeLIP/X9.62 style of incrementing).

**Step 4 — the "which coordinate" question** (undecided in the voice conversation): is the hash the x-coordinate, the y-coordinate, or a scalar that multiplies some canonical point (e.g. the point at the smallest x, which is x = 0 for P-256 and x = 3 for P-224)? The scalar form is cheap: hash → k, check k·P₀ = ±G for P₀ the smallest-x point. Include it.

**Step 5 — older standards.** X9.62-1998, SEC 1/SEC 2 v1 (2000), IEEE P1363 drafts, early FIPS 186-2 drafts, and the 1997–98 ANSI X9F1 working drafts may carry different or additional base points for the same curves, or the same points with provenance text. Check whether any draft ever printed a different G for P-224/256/384/521; a change in G between drafts would date the generation and might expose the method.

**Step 6 — controls and stopping rule.** Run everything on the six explained generators; expect zero hits. Count the total number of (string, hash, mapping, multiplier) trials and compute the expected number of chance hits (≈ trials × on-curve probability × |table| / p); stop when the search is clearly in the regime where a hit would be meaningful.

## 5. Files and tools

In `/home/claude/cm` (this sandbox; copy out before it expires):
- `cm-hypothesis.md` — the full skipped-seed investigation (negative result).
- `gen.py` — regenerates lrand48 candidates and both roots of b per X9.62 for any run.
- `*.cands`, `*.orders2` — every candidate's b and every verified order for P-256, P-224, prime192, prime239.
- `battery.py`, `analyze*.py`, `isog.gp`, `pts.gp` — the test battery.
- `binpts.gp`, `binpts.out`, `bincurves.json` — GF(2^m) scan of all ten binary generators; K-163 hit; verified parameters.
- `pts.out` — small-x points with y (root convention as in §1) for all 19 viable curves; no small-scalar relations among them or with G.
- `mult.out` — half-points and shortest coordinates among k·G, G/k, k ≤ 2¹⁶, all ten published generators.
- PARI/GP 2.10-dev built from a GitHub mirror at `/home/claude/src/pari` (no seadata; SEA early-abort mode has a trace-sign bug in this build — use full `ellcard` and verify with n·P = O).

Sources: Anthropic post https://www.anthropic.com/research/ecdsa-curve-origins ; Filippo Valsorda https://words.filippo.io/seeds-solved/ ; Koblitz & Menezes, ePrint 2015/1018; Bernstein, Lange et al., "How to manipulate curve standards" (2014/2015) for the sentence-lore background.
