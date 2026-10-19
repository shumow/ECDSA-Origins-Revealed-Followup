# I spent the weekend on the NIST curves. Here's what's left.

*Anthropic solved the seeds. I went looking for what they skipped, and found something in a generator nobody was looking at.*

---

On Friday, October 16, Anthropic published a result I'd half given up on seeing in my lifetime. The ten NIST/ANSI prime-curve seeds match `lrand48()`, the C library's not-very-good random number generator, seeded from the Unix clock. Four binary-curve seeds match too; B-163's does not. P-256 is the 1,842nd candidate drawn from a run that started at 01:52:34 UTC on August 16, 1997. Filippo Valsorda independently reproduced the result; the Anthropic team directed its bounty to ISRG.

If you've followed my career you know why I care about this. A long time ago I stood up at a conference and said the NSA's Dual_EC_DRBG looked backdoored, which it was. Since then I've considered it part of the job to keep an eye on government-selected cryptographic parameters. The NIST curves were always the big one: used everywhere, origins unknown, and the man who generated them — Jerry Solinas, who by all accounts was a lovely person — died in 2023 saying the records were "sitting on a hard drive near the Ark of the Covenant." The best story anyone had was that the seeds were hashes of a joke about Jerry and his colleague Bob getting a raise.

They weren't. It was a clock. I'll admit the first thing I felt was mild irritation at being handed a weekend's worth of homework on a Friday night. The second was that the post left a loose end, and loose ends are the whole point.

## The loose end

Here's how the generation worked. The program drew twenty bytes from `lrand48`, treated them as a seed, ran the X9.62 procedure to turn the seed into a curve coefficient *b*, and checked whether the resulting curve had prime order and the right size. If not, it drew the next twenty bytes and tried again. The published curve is wherever the run stopped.

Except that isn't quite what happened. In the P-256 run, candidate number 876 — long before 1,842 — also gives a prime-order curve of the right size, passing every criterion in the standard. The P-224 run passed over three such curves. The two ANSI X9.62 runs that produced P-192 and the prime192/prime239 example curves passed over seven more. Eleven perfectly good curves, skipped, with eight others published later in the same runs. Filippo's write-up put it plainly: roughly twice as many valid seeds as were published, rejected by a second undocumented criterion that "still escapes us."

So what was the criterion?

## What I checked

I had a hypothesis. My master's thesis was on isogenies, and the thing a number theorist worries about with a random curve is the class number of its CM field — the discriminant *t*² − 4*p*, how much of it is a square, and whether the resulting endomorphism ring is "special" in a way that would make someone cautious. Nobody had checked. And there's a nice statistical argument that a class-number floor is exactly the kind of criterion that would reject half the candidates: the relevant statistic is the largest square divisor of the discriminant, whose distribution is heavy-tailed, not the near-squareness, which never happens.

So I regenerated all four runs, checked the group orders, and estimated the class numbers using Euler products. Those are estimates, not exact class-number computations or certified error bounds.

It isn't the class number. The published P-224 curve has the *smallest* class number among the four viable candidates in its run. The published P-256 has the *largest* of its two. A floor is ruled out by one run and a ceiling by the other.

Fine. It was a good hypothesis. I kept going. Over the weekend, with Claude doing the computation and me telling it what to compute, we checked roughly fifty properties of those nineteen curves — everything a cryptographer in 1997 could have cheaply asked:

- The arithmetic of the order: twist order, complete factorizations of *n* ± 1, congruences.
- The CM structure: discriminant, conductor, class number with the *L*-value included.
- Isogeny structure over the base field — End(*E*), volcano position, which small primes split — and over extension fields up to degree 12.
- Group orders over extension fields up to degree 12, and their smoothness.
- Embedding degree. GCDs of *p* ± 1 with *n* ± 1, which is the kind of thing a careful programmer might have looped over. Nine Legendre symbols. Residue classes.
- The small-*x* points on each curve, the full 256-entry on-curve bitmap for *x* < 256, and whether any of them are small multiples of each other or of the published generator.

Nothing tested separates all eleven skipped curves from the eight published ones. In the runs that published three curves each, the published curves disagree *with each other* on many binary properties. For example, a global "*n* must be 1 mod 8" requirement fails on published prime192v3 and two published prime239 curves.

Then we asked about the program. Eleven simple abort-bug models did not match the pattern. Elkies/Atkin counts point against one simple proxy for a timeout, but they are not actual historical timing measurements. The tested index patterns, seed-byte patterns, base-point failure models, and sorting rules did not explain the full labelling either. This rules out those models, not every implementation bug.

Finally we asked whether the eleven could be the *union* of several small bugs. From 135 predicates, the smallest union covering all eleven skipped curves and none of the eight published needs four predicates. The original 300-sample comparison gave 35% with covers that small. A better matched, exact comparison keeps each run's final candidate published as well as preserving its published count: 88 of the 126 possible labellings, or 69.8%, admit covers of four or fewer. That is not evidence for a special pattern in the real labels. Since the predicates were chosen during exploration, it is not a confirmatory test of every possible selection rule.

**No tested rule separates the eleven skipped curves from the eight published ones.** A point-counter artifact or a human choice remains plausible. But nineteen curves and a finite collection of tests cannot show that the reason left no numerical trace, or that archival evidence is the only way forward.

Nothing here demonstrates a curve weakness or calls for an operational change. The investigation finds no evidence of selection by the properties tested. It does not establish statistical identity or rule out arbitrary untested hidden properties.

## What I found instead

There's a second provenance question Anthropic's post left open, and it's the one I'd actually been arguing about with Nadia Heninger over the summer: the base points. Every curve comes with a generator *G*, and the seed doesn't determine it. Anthropic explained the generators for P-192 and the ANSI curves — they came from Arjen Lenstra's FreeLIP package with small integer seeds — but P-224, P-256, P-384 and P-521 remain unexplained. The post explicitly leaves the binary generators unexplained too.

Nadia's idea, which I'd been carrying around: if someone picked a generator by hashing a phrase to an *x*-coordinate and then doubling the point, you'd see it by computing *G*/2 and finding a short coordinate. So we computed *G*/2, and *G*/*k* and *k*·*G* for *k* up to 65,536, for all ten prime-field generators.

Nothing. Every coordinate is within a couple of bits of what a random field element would give.

Then we did the same for the ten binary curves. Nine of them: nothing. The tenth is K-163.

```
K-163, G/2:   x = 0x23e21d6019e1211f6bd47ec180256e97
```

That's 126 bits on a 163-bit curve, with a full-size *y*. Choosing a 128-bit *x*, solving for *y*, and multiplying by the cofactor is a plausible explanation, not a recovered recipe. The binary scan covered 69,630 points per curve, 696,300 total. A uniform-coordinate heuristic gives roughly five-in-a-million expected *x*-hits at that threshold, before accounting for the prime-field scans, other coordinates, and exploratory pattern choices. That is not a calibrated probability for the whole investigation.

K-163 is a Koblitz curve: *y*² + *xy* = *x*³ + *x*² + 1, with *b* fixed at 1 and no seed. Its generator is a natural place to test the old phrase-hash lore. But a review found that the original PARI coordinate export reversed coefficient bits: the 126-bit length was right and the hexadecimal target was wrong. The roughly thirty million earlier negative hash evaluations do not apply to the corrected value above. We reran the same thirty million against the corrected value: still nothing. So it isn't the obvious thing under the obvious hashes. We have not established that this observation is new.

There is also a cofactor subtlety: the subgroup half is only one of two rational points that double to G. We checked both, and all cofactor preimages on the other nine binary curves. K-163 remains the only 128-bit-*x* hit; its other half has a 162-bit *x*.

## What this means

Nothing here demonstrates a weakness in these curves. The skips remain unexplained. The K-163 observation is a concrete provenance lead, not an identified construction.

The story isn't over: B-163's seed and most base points remain unexplained. The corrected K-163 coordinate `23e21d6019e1211f6bd47ec180256e97` is one concrete handle. Old WTLS, SEC, and X9.62 drafts and generation code would be especially valuable evidence.

Everything — the data, the scripts, every verified group order, the full record of every dead end — is at [github.com/shumow/ECDSA-Origins-Revealed-Followup](https://github.com/shumow/ECDSA-Origins-Revealed-Followup). The negative result is the kind that saves the next person a week. The K-163 number is the kind that might cost someone one.

*Thanks to Nadia Heninger for the half-point idea, to the Anthropic Frontier Red Team and Filippo Valsorda for a trail so well marked I could follow it on a Friday night, and to Claude for doing the arithmetic while I did the swearing.*
