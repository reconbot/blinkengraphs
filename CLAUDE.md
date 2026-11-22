# blinkengraphs spec

Vocabulary `CONTEXT.md`, rules `rules/`, conformance data `vectors/`, defaults `defaults.json`, design tokens `tokens/`, app icon `brand/icon.svg` (hand-edited; platforms render their formats from it), preview data `fixtures/`, decisions `docs/`. No app code lives here.

Every file here is authored here; no platform repo owns or generates any of it. A rule change lands here first, prose in `rules/` and its vectors together; each platform then implements it and passes the vectors.

`defaults.json` is hand-edited here and is the source every platform embeds; each platform deep-merges its own `defaults.override.json` over it (`rules/defaults.md`).

Any change that touches more than one repo follows `docs/sync.md`; finish every step it lists before calling the change done.

Platform repos pin a release tag. release-please cuts releases from Conventional Commits: a rule change that alters any vector's `expected` is breaking (`feat!:`).

Skills come from `.claude/settings.json` (`mattpocock-skills`):
- `domain-modeling` when a term or decision changes
- `writing-for-agents` for any doc or CLAUDE.md edit
- `research` for primary-source findings, saved under `docs/`
- `grilling` to stress-test a proposed rule before it lands

Prose earns each sentence.

Commits, PRs and comments stay free of session links and personal or employer details; the repo is public.

Never force-push `main` once the repo has a release.

Release PRs (release-please) merge only after the owner has reviewed them and said so. Feature PRs merge when tests pass.
