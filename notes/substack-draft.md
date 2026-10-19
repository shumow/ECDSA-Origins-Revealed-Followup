# I spent the weekend on the NIST curves. Here's what's left.

*Anthropic solved the seeds. I went looking for what they skipped, and found something in a generator nobody was looking at.*

---

On Thursday Anthropic published a result I'd half given up on seeing in my lifetime. The seed values behind the NIST elliptic curves — the twenty-byte constants that were handed to NIST in 1997 with no explanation and have been a low-grade source of paranoia in my field ever since — are not hashes of anything. They're the output of `lrand48()`, the C library's not-very-good random number generator, seeded from the Unix clock. P-256 is the 1,842nd candidate drawn from a run that started at 01:52:34 UTC on August 16, 1997. Filippo Valsorda reproduced it the same day and paid out the bounty.

If you've followed my career you know why I care about this. A long time ago I stood up at a conference and said the NSA's Dual_EC_DRBG looked backdoored, which it was. Since then I've considered it part of the job to keep an eye on government-selected cryptographic parameters. The NIST curves were always the big one: used everywhere, origins unknown, and the man who generated them — Jerry Solinas, who by all accounts was a lovely person — died in 2023 saying the records were "sitting on a hard drive near the Ark of the Covenant." The best story anyone had was that the seeds were hashes of a joke about Jerry and his colleague Bob getting a raise.

They weren't. It was a clock. I'll admit the first thing I felt was mild irritation at being handed a weekend's worth of homework on a Friday night. The second was that the post left a loose end, and loose ends are the whole point.

## The loose end

Here's how the generation worked. The program drew twenty bytes from `lrand48`, treated them as a seed, ran the X9.62 procedure to turn the seed into a curve coefficient *b*, and checked whether the resulting curve had prime order and the right size. If not, it drew the next twenty bytes and tried again. The published curve is wherever the run stopped.

Except that isn't quite what happened. In the P-256 run, candidate number 876 — long before 1,842 — also gives a prime-order curve of the right size, passing every criterion in the standard. The P-224 run passed over three such curves. The two ANSI X9.62 runs that produced P-192 and the prime192/prime239 example curves passed over seven more. Eleven perfectly good curves, skipped, with eight others published later in the same runs. Filippo's write-up put it plainly: roughly twice as many valid seeds as were published, rejected by a second undocumented criterion that "still escapes us."

So what was the criterion?

## What I checked

I had a hypothesis. My master's thesis was on isogenies, and the thing a number theorist worries about with a random curve is the class number of its CM field — the discriminant *t*² − 4*p*, how much of it is a square, and whether the resulting endomorphism ring is "special" in a way that would make someone cautious. Nobody had checked. And there's a nice statistical argument that a class-number floor is exactly the kind of criterion that would reject half the candidates: the relevant statistic is the largest square divisor of the discriminant, whose distribution is heavy-tailed, not the near-squareness, which never happens.

So I regenerated all four runs, verified every group order two independent ways, and computed the class numbers.

It isn't the class number. The published P-224 curve has the *smallest* class number among the four viable candidates in its run. The published P-256 has the *largest* of its two. A floor is ruled out by one run and a ceiling by the other.

Fine. It was a good hypothesis. I kept going. Over the weekend, with Claude doing the computation and me telling it what to compute, we checked roughly fifty properties of those nineteen curves — everything a cryptographer in 1997 could have cheaply asked:

- The arithmetic of the order: twist order, complete factorizations of *n* ± 1, congruences.
- The CM structure: discriminant, conductor, class number with the *L*-value included.
- Isogeny structure over the base field — End(*E*), volcano position, which small primes split — and over extension fields up to degree 12.
- Group orders over extension fields up to degree 12, and their smoothness.
- Embedding degree. GCDs of *p* ± 1 with *n* ± 1, which is the kind of thing a careful programmer might have looped over. Nine Legendre symbols. Residue classes.
- The small-*x* points on each curve, the full 256-entry on-curve bitmap for *x* < 256, and whether any of them are small multiples of each other or of the published generator.

Nothing. Not one of these separates the eleven skipped curves from the eight published ones. The most decisive evidence comes from the two runs that published three curves each: there, the published curves disagree *with each other* on nearly every binary property. If the criterion were "*n* must be 1 mod 8," two of the three published prime192 curves would have failed it.

Then we stopped asking about the curves and asked about the program. We simulated eleven ways a 1997 point-counting routine could have been buggy — trace sign flipped, wrong square root, off-by-one in the order test, testing the trace instead of the order — and checked which of the nineteen each bug would have wrongly rejected. None matches the actual pattern. We checked whether the skipped curves would have been slow to count (they'd have been *faster*). We checked whether the skipped candidate *indices* share any arithmetic property, whether the skipped *seeds* have byte patterns a C program would choke on, whether the base-point generator Anthropic recovered would have failed on them, whether a human sorting a printout by any column would have picked the published ones. No, no, no, and no.

Finally — this was my idea, and I think it's the right way to close the question — we asked whether the eleven could be the *union* of several small bugs rather than one criterion. Set cover: from 135 "bug-shaped" predicates, find the smallest union that covers all eleven skipped curves and none of the eight published. The answer is four predicates. Then we ran the identical search on 300 random relabellings of published-versus-skipped. A third of them also need four or fewer. The real labelling is unremarkable. Whatever the covers find is noise fitted to noise.

**The eleven skipped curves are indistinguishable from the eight published ones.** On everything in the parameters, they are the same kind of object. My best guess is the boring one: a point counter that sometimes gave up, or Jerry taking the last curve off a printout. Nothing in the numbers can tell those apart, and nothing in the numbers ever will.

I want to say clearly what that means. It *strengthens* Anthropic's conclusion. If the skips were a selection — if someone were searching for a curve with a hidden property — the chosen curves would differ from the rejected ones in some way. They don't. A designer looking for weak curves would have had to find them among candidates that are statistically identical to the ones taken.

## What I found instead

There's a second provenance question Anthropic's post left open, and it's the one I'd actually been arguing about with Nadia Heninger over the summer: the base points. Every curve comes with a generator *G*, and the seed doesn't determine it. Anthropic explained the generators for P-192 and the ANSI curves — they came from Arjen Lenstra's FreeLIP package with small integer seeds — but P-224, P-256, P-384 and P-521 remain unexplained, and the post says nothing about the binary curves at all.

Nadia's idea, which I'd been carrying around: if someone picked a generator by hashing a phrase to an *x*-coordinate and then doubling the point, you'd see it by computing *G*/2 and finding a short coordinate. So we computed *G*/2, and *G*/*k* and *k*·*G* for *k* up to 65,536, for all ten prime-field generators.

Nothing. Every coordinate is within a couple of bits of what a random field element would give.

Then we did the same for the ten binary curves. Nine of them: nothing. The tenth is K-163.

```
K-163, G/2:   x = 0x3a5da90060df8af5be2121e601ae11f1
```

That's 126 bits. On a 163-bit curve. A 128-bit number with two leading zeros, with a full-size *y* — exactly what you'd see if someone chose a 128-bit *x*, solved for *y*, and multiplied by the cofactor 2 to land in the prime-order subgroup. A coordinate 37 bits short of the field is a one-in-2³⁷ event. Across the seventy thousand points we looked at, the chance of seeing one by accident is about one in a million.

K-163 is a Koblitz curve: *y*² + *xy* = *x*³ + *x*² + 1, with *b* fixed at 1. It has no seed. The generator is the *only* randomly chosen parameter on that curve. Which makes it the one place the old lore — a hash of a phrase — could still live. We've since tried about thirty million hashes of the obvious phrases, names, dates and curve identifiers under MD5, MD4, SHA-0, SHA-1 and RIPEMD, and found nothing. So it isn't the obvious thing. But it is *something*, and it's the first structural fingerprint anyone has found on a NIST base point.

## What this means

Nothing changes for anyone using these curves. The skips are noise. The K-163 observation is a lead, not a finding — until that 128-bit value is identified, it's a very surprising number and nothing more.

But it says the story isn't over. Anthropic closed the seed question; the base-point question is a separate one, and it's open, and it has at least one concrete handle on it. If anyone recognizes `3a5da90060df8af5be2121e601ae11f1`, or has an old copy of the WTLS or X9.62 drafts with a different generator for sect163k1, I want to hear from you.

Everything — the data, the scripts, every verified group order, the full record of every dead end — is at [github.com/shumow/ECDSA-Origins-Revealed-Followup](https://github.com/shumow/ECDSA-Origins-Revealed-Followup). The negative result is the kind that saves the next person a week. The K-163 number is the kind that might cost someone one.

*Thanks to Nadia Heninger for the half-point idea, to the Anthropic Frontier Red Team and Filippo Valsorda for a trail so well marked I could follow it on a Friday night, and to Claude for doing the arithmetic while I did the swearing.*
