# Branches to delete manually

Remote branches that have been fully merged into `main` but could not be deleted
from the automated session (the git proxy permits pushes, not ref deletion).
Delete from the GitHub Branches page or with `git push origin --delete <branch>`,
then remove the line here.

| Branch | Merged into `main` at | Notes |
|---|---|---|
| `review/fable-review` | `cb9416d` (2026-10-19) | Claude's review of the Copilot review branch; folded into `review/verified-corrections`, then fast-forwarded into `main` |
| `review/verified-corrections` | `cb9416d` (2026-10-19) | Copilot review (`73690a7`) plus the fable-review commits; identical to `main` |
