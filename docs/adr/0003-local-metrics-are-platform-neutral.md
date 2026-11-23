# Local Metrics are platform-neutral

The Local rules named Windows counters: CPU total, commit charge, hard faults, disk active time and response time. macOS has no commit limit and pages are 16 KiB on Apple silicon against 4 KiB on x64, so a second platform could not implement the same rules with the same meaning ([research](../local-metrics.md)).

The Verdict now reads Metrics defined by meaning, and each platform maps its counters to them:

- `CpuBusy` in %.
- `MemPressure` as a level, `normal`, `warn` or `critical`, because "out of memory" is a judgment each OS already makes. Windows derives `critical` from commit ≥ 90%.
- `MemPageIns` in bytes/s, so the threshold survives a different page size. 4 096 000 B/s keeps Windows' 1000 pages/s.
- `Disks`, each with `DiskBusy` and `DiskResponse`. The rule fires on the worst disk, not the total, so a saturated external disk can't hide behind an idle internal one.

## Considered options

- **Keep Windows names; each platform maps to its nearest counter.** Rejected: the same input would mean different things, and the Verdict would disagree across platforms on the same machine state.
- **Pages/s, scaled per platform.** Rejected: a platform-scaled threshold is not one rule.
- **Disk rule on queue depth instead of busy %.** Rejected for now: it changes Windows' behaviour to suit one platform's missing counter. macOS uses mean requests in flight capped at 100%, which fires at least as readily.
- **A Warn Finding for `MemPressure` `warn`.** Rejected: Windows has no matching signal.

## Consequences

- Breaking: the Sample's keys and the paging headline change. Windows renames its Metrics and collects per-disk counters.
- A vector's Sample holds only what the Verdict reads; Windows-only Metrics left the vectors.
