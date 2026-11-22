# A platform may depart from the spec where its normal use calls for it

The platforms are used differently. Windows and macOS run all day in the tray or menu bar and measure almost continuously. iOS measures only while the app is open: it is a check-up opened when something is wrong, and most of every hour and day is a Pause. A rule that fits one platform's normal use can misfit another's. For example, a graph bucket more than half Paused draws as Paused, which on iOS erases most of the 7d and All ranges.

So a platform may depart from any rule here, presentation and History included, where its normal use calls for it.

- **The departure is recorded in the departing platform's repo,** in an ADR that names the rule it replaces and the use that calls for it. The spec does not list platform departures.
- **Vectors:** the platform skips a vector that no longer applies by name, pointing to that ADR. Every other vector still passes.
- **What platforms compare stays common:** Probe stats, the Verdict, and Row fields and their merge. The same measurements give the same Verdict and numbers on every platform.
- **A departure that would serve every platform** comes back here as a spec PR.

## Considered options

- **Every platform follows every rule.** Rejected: it forces desktop assumptions onto a foreground-only app, and the iOS graphs then show mostly Paused.
- **Platform variants written into the rules.** Rejected: every rule would grow per-platform branches the other platforms must read and never use.

## Consequences

- A platform's conformance is every vector except those its ADRs skip by name.
- Where a platform departs, `docs/sync.md` points to that platform's ADRs, not to a spec PR.
