# The Missing Recipe: five levels of explanation

An illustrated, progressively deeper explanation of **both** investigations in
this repository: skipped curve candidates and base-point provenance.

- **[Open the offline website](index.html)** in a modern browser.
- **[Read the illustrated PDF](five-levels.pdf)** for a shareable print edition.
- The editable sources are [index.html](index.html) and [styles.css](styles.css).

## The five treatments

| Level | Audience | Format and purpose |
|---|---|---|
| 1 | Child / newcomer | Six-panel original vector comic: public ingredients, a replayable recipe, unexplained choices and clues. |
| 2 | Teenager / curious beginner | Six-panel comic: the seed pipeline, a rule that must fit all candidates, group halving and its limits. |
| 3 | College undergraduate | Three-page illustrated textbook chapter: a verified finite-field toy curve, candidate pipeline, coordinate bit-length graphic and shared-core comparison. |
| 4 | Graduate student | Two-page research walkthrough: dataset conventions, order certification, the conditional null, cofactor cosets and reproduction. |
| 5 | Fellow expert | Two-page evidence brief: exact contribution, adaptive-search limits, representation dependence and what would establish a historical explanation. |

The 11-page PDF also includes a cover and a source appendix. Audience levels model prior
familiarity, not age or intelligence. Both comics use the same original characters,
Kit and Ada; numbered panels are read left to right, then down.

## Framework and editorial choices

This follows the
[Five-Level Explanation Guide](https://github.com/danshumow-msft/five-level-explanations/blob/main/five-level-explanation-guide.md),
read on 22 October 2026, rather than copying its text. Every level follows the same
chain: **reconstruct the recipe -> compare its outputs -> distinguish a clue from
a historical explanation**. Each includes a boundary and a reader check.

The research snapshot is
[`cede36edf99b41b0a252352f8ee82760936e03af`](https://github.com/shumow/ECDSA-Origins-Revealed-Followup/tree/cede36edf99b41b0a252352f8ee82760936e03af).
The appendix pins sources to that commit. In particular:

- The nineteen-candidate dataset is conditional on the reconstructed root and
  size conventions.
- The 88/126 comparison is an exact *conditional* enumeration, not a probability
  that the historical selection was benign.
- Shared coordinates are verified mathematical structure, not proof of the
  designers' construction direction or intent.
- This snapshot retains legacy SEC scripts. Review fixes were ported to
  [base-point-origins](https://github.com/shumow/base-point-origins), not merged
  here; this companion does not imply that main contains those fixes or that
  the separate repository was newly reviewed.
- There is no demonstrated attack or deployment-change recommendation.

## Offline use and accessibility

No server, build system, JavaScript, external font, remote image or package
installation is required to read the website. The SVG artwork is embedded in the
HTML and remains sharp in the PDF. Internet access is only needed to follow the
source links.

The website includes keyboard navigation, a skip link, real HTML comic dialogue,
descriptive SVG titles/labels, a single-column mobile layout, reduced-motion
support, and support for the browser's high-contrast display. Color is never the
only carrier of an evidence distinction. The HTML is the preferred accessible
reading version; a fully tagged/accessible PDF has not been independently certified.

## Rebuilding the PDF

1. Open [index.html](index.html) in Edge or Chrome.
2. Print to PDF using **A4**, **100% scale**, **background graphics on**, and
   **browser headers/footers off**. The stylesheet provides page margins and
   deliberate page breaks.
3. Save as `five-levels.pdf` in this directory.

The checked-in edition was exported with installed Microsoft Edge's headless
`--print-to-pdf` facility using the same HTML and print stylesheet. No screenshots
are substituted for text or diagrams. Platform fonts can change pagination;
inspect a regenerated PDF rather than assuming that a successful export implies
correct layout.

For a headless export on Windows with system high-contrast mode enabled, this
edition also used `--disable-blink-features=ForcedColors` and
`--force-color-profile=srgb`, with `--no-pdf-header-footer` and an isolated
temporary browser profile. The website itself still respects high-contrast mode;
print styling preserves illustration colors and a white page background.

## Validation performed for this edition

- Ran the existing `test_research.py` suite with PARI/GP available:
  **16 tests passed, none skipped**. This includes the nineteen viable prime
  orders, the exact 126-bit K-163 half-coordinate, Python/PARI encoding checks,
  rational binary cofactor preimages, and the conditional cover distribution.
- Checked the toy curve over F17 has exactly the 18 plotted affine points,
  plus the identity, and that doubling `(5, 1)` gives `(6, 3)`.
- Checked the four shared 148-bit cores, identical 166-bit half x-coordinates,
  and the 92-bit prefix against the recorded SEC data and parameter table.
- Checked SVG well-formedness, local fragment references, mobile/desktop
  layout, and the PDF's page structure and representative rendered pages.
  The final PDF has exactly 11 pages, no orphan pages, and no out-of-bounds text
  blocks. Browser checks found no document overflow at 390px or 1440px.

From the repository root:

```text
python -B -X utf8 -m unittest discover -s scripts -p test_research.py -v
```

Set `GP` to a PARI/GP executable, or put `gp` on `PATH`, to include the independent
PARI checks. Without it, those tests are explicitly skipped.

This preparation **did not** rerun full historical point counting, full
scalar/hash searches or every factorization. It is an explanation with focused
checks, not a new cryptographic audit or a comprehensive literature review.

Original text and vector illustrations follow the repository's text license,
CC BY 4.0. The explanation framework is credited above; its guide is MIT-licensed.
