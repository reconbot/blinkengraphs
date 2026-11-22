# History is Raw plus fixed-step Archives, and unmeasured time is a Pause

History used to keep 15 minutes of results in memory and write one-minute summaries to disk, and each graph mixed the two at a moving seam. A drawn point changed width, source and percentile method as it aged. A suspended or sleeping app left no trace, and a Round cut by suspension recorded loss. History now follows RRDtool:

- **Raw:** every result kept on disk for two hours.
- **Archives:** fixed steps, each Row written once when its step ends and never changed.
- **One source per range:** each graph range draws from exactly one source, Raw or one Archive.
- **Pause:** time not measured is its own state, like RRD's UNKNOWN, never loss.

## Considered options

- **Keep the minute summaries and fix the seam.** Rejected: any graph that joins two sources at a moving boundary redraws points as they age, and iOS ends a suspended app without warning, so "write on shutdown" can't be relied on.
- **One-minute Archive only, merged at draw time.** Rejected: the 24h and 7d graphs would still re-merge minutes on every draw, and the 1h graph would get 60 points instead of 240.
- **A Round cut by a Pause counts as loss.** Rejected: on iOS this is most resumes, so the Verdict would blame the network for the app being backgrounded.

## Consequences

- Every History vector changes, and the spec release is breaking.
- `defaults.json` `history.ram_minutes` and `history.rollup_days` are replaced.
- Stats windows are measured back from now, not from the newest result. Right after a Pause a Probe has no stats and the Verdict says measurements are resuming.
- History is kept per Link, and several Links can be active and measured at once. Graphs show them together by default, and the user can pick one.

Proposal and per-platform plan: [`docs/history-redesign.md`](../history-redesign.md).
