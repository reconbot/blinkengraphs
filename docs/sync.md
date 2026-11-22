# Keeping the four repositories in sync

| Repo | Role |
|---|---|
| reconbot/blinkengraphs | The spec and the landing page. Source of truth for terms, rules and vectors |
| reconbot/blinkengraphs-win | Reference implementation. Generates `vectors/`, `fixtures/` and `tokens/` |
| reconbot/blinkengraphs-mac, reconbot/blinkengraphs-ios | Implement the spec natively, pinned to a spec release |

## When a change touches several repos

| Change | Do, in order |
|---|---|
| Rule, threshold or token | 1. PR to -win that changes code and tests, then regenerates into a spec checkout.<br>2. Spec PR with the prose in `rules/` and the regenerated files.<br>3. Merge both. release-please cuts a spec release; a vector whose `expected` changed is a breaking release (`feat!:`).<br>4. In every platform repo, a PR that bumps the pinned spec tag and passes the vectors. |
| Shared default | 1. Spec PR that edits `defaults.json`. A default a vector depends on is a rule change instead.<br>2. Merge it; release-please cuts a spec release.<br>3. In every platform repo, a PR that bumps the pinned spec. |
| Platform default | A PR in that platform repo that edits its `defaults.override.json`, with the reason in its ADRs. |
| Term in `CONTEXT.md` | Spec PR first, using the `domain-modeling` skill. Then rename the term in code, UI and docs in each platform repo. |
| Something one platform needs that the spec lacks | Spec PR first. The platform does not ship a private rule. |
| A repo is added or renamed | Update the Repositories table in every README, the Download table in the spec README, and the roles table above. |
| Shared conventions (`CLAUDE.md` rules, `.claude/settings.json`) | Apply the same edit to all four repos. The four `.claude/settings.json` files are identical. |

## Done means

- Every platform repo pins the latest spec release, or has an open PR moving to it.
- Every platform's CI runs that release's vectors and passes.
- The spec README's Download table shows each platform's status and latest release.
