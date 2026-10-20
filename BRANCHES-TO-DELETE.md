# Branches to delete manually

Remote branches that have been fully merged into `main` but could not be deleted
from the automated session (the git proxy permits pushes, not ref deletion).
Delete from the GitHub Branches page or with `git push origin --delete <branch>`,
then remove the line here.

| Branch | Merged into `main` at | Notes |
|---|---|---|
| `review/fable-review` | `cb9416d` (2026-10-19) | Claude's review of the Copilot review branch; folded into `review/verified-corrections`, then fast-forwarded into `main` |
| `review/verified-corrections` | `cb9416d` (2026-10-19) | Copilot review (`73690a7`) plus the fable-review commits; identical to `main` |
| `base-points` | `b95c1b4` (2026-10-20) | Base-point work; merged into `main`, then spun out to the base-point-origins repository |
| `review/base-points-corrections` | not merged (`7c114fb`, 2026-10-20) | Copilot review of the base-point scripts; forked from `b95c1b4`, conflicts with `main`, and the work it reviews now lives in base-point-origins — its improvements (kernel validation, strict hash init, tests) were ported there instead |
