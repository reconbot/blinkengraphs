# Keeping the four repositories in sync

| Repo | Role |
|---|---|
| reconbot/blinkengraphs | The spec and the landing page. Source of truth for terms, rules, vectors, fixtures, tokens, defaults and brand; all authored here |
| reconbot/blinkengraphs-win, reconbot/blinkengraphs-mac, reconbot/blinkengraphs-ios | Implement the spec natively, pinned to a spec release |

## When a change touches several repos

| Change | Do, in order |
|---|---|
| Rule, threshold or token | 1. Spec PR with the prose in `rules/` and its vectors, or the token edit.<br>2. Merge it. release-please cuts a spec release; a vector whose `expected` changed is a breaking release (`feat!:`).<br>3. In every platform repo, a PR that implements the change, bumps the pinned spec tag and passes the vectors. |
| Shared default | 1. Spec PR that edits `defaults.json`. A default a vector depends on is a rule change instead.<br>2. Merge it; release-please cuts a spec release.<br>3. In every platform repo, a PR that bumps the pinned spec. |
| Platform default | A PR in that platform repo that edits its `defaults.override.json`, with the reason in its ADRs. |
| Icon or brand (`brand/`) | Spec PR. Each platform's next spec bump re-renders its icon formats from `brand/icon.svg`; none commits its own icon art. |
| Term in `CONTEXT.md` | Spec PR first, using the `domain-modeling` skill. Then rename the term in code, UI and docs in each platform repo. |
| Something one platform needs that the spec lacks | Spec PR first, unless it is a departure for that platform's normal use. |
| A platform departs from a rule for its normal use ([ADR 0002](adr/0002-platforms-may-depart-for-their-normal-use.md)) | An ADR in that platform's repo naming the rule it replaces; its tests skip any vector that no longer applies, by name. A spec PR follows if every platform would benefit. |
| A repo is added or renamed | Update the Repositories table in every README, the Download table in the spec README, and the roles table above. |
| Shared conventions (`CLAUDE.md` rules, `.claude/settings.json`) | Apply the same edit to all four repos. The four `.claude/settings.json` files are identical. |

## Done means

- Every platform repo pins the latest spec release, or has an open PR moving to it.
- Every platform's CI runs that release's vectors and passes.
- The spec README's Download table shows each platform's status and latest release.
