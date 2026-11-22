# Proposal: Raw, Archives and Pauses

Graphs show gaps, false loss after a resume, and points that change value as they age. The cause is in the spec, not in one app. This proposal replaces the History model with an RRDtool-style one ([ADR 0001](adr/0001-rrd-style-history.md)) and plans each platform's move to it. No rule here is normative until it lands in `rules/` with vectors (`docs/sync.md`). Terms are in `CONTEXT.md`: Round, Pause, Raw, Archive, Row.

## What goes wrong today

Reviewed at iOS `066eb9c`, Windows `2bbb58a` and macOS `2ed53ba`. iOS and Windows both pin spec v3.0.0. The macOS repo has no code yet.

| Symptom | Spec cause | iOS | Windows |
|---|---|---|---|
| Gaps | A Minute is written only once a later result arrives, or on shutdown (`history.md`, Minutes). Suspended apps are killed without a shutdown. RAM is never saved. | The open minute is lost on kill (`Rollups.swift:65-70`, ADR 0007, 0012). The write in `stop()` is unprotected (`Monitor.swift:92-101`). Graphs show only the current Link (`Graphs.swift:78`). | Hibernate never calls `close()` (`app/src/win.rs:494,703`). |
| False loss on resume | Nothing says what a Round in flight across a suspension records. A Probe sent before the network is usable again counts as loss. | Late arrivals are dropped (#28). The first Probes after the path "settles" for 1 s still time out (`PathSettle.swift:21-33`, ADR 0013). | No sleep or resume handling. An in-flight Round keeps its pre-sleep `at` and times out (`probe/src/lib.rs:259`). A stale route passes `family_up` after wake (`probe/src/win.rs:416`). |
| Points change value | One graph joins RAM (raw ranks, `w`-second buckets) and storage (sketch merges, `⌈w/60⌉×60`-second buckets) at a seam `c` that moves (`history.md`, Graph buckets). | v3 seam, about 1-2 min behind now (`HistoryLine.swift:17`). Two points share one start on 24h and 7d (`Graphs.swift:210-224`). A per-minute line cache freezes, then jumps (`Graphs.swift:85-88`). | v3 seam (`history/src/lib.rs:720-773`). Percentiles switch from exact to sketch (`lib.rs:109-140`). |
| Stale Verdict after a pause | Stats and RAM are measured back from the newest result, not from now (`probe-stats.md`, Stats; `history.md`, RAM). | Pre-pause stats show as current (`ProbeStats.swift:59-62`). | Same (`history/src/lib.rs:330-333`). |

## Agreed behaviour

- **Pause.** Time not measured is a Pause, whatever the reason: suspended, asleep, killed, not yet started, or resting while idle. A Pause lasts until `settle_s` after measuring resumes. It is not loss and not Offline. Whether to rest while idle stays each platform's choice.
- **Cut Rounds.** A Round whose timeout ends after a Pause began records nothing. Only a Round that ran its full timeout while measuring records a loss.
- **Now, not newest.** Stats windows and Raw retention are measured back from now. Right after a Pause a Probe has no stats; readouts show "–" and the Verdict says measurements are resuming.
- **Raw.** Every result and Sample, with its Link, kept on disk for 2 hours. Pauses and Link changes are kept beside them. How often Raw reaches disk is each platform's choice, within a bound the spec sets; on the next launch the unwritten stretch is a Pause.
- **Archives.** Each Row is one step of one key, aligned to the Unix epoch, so days start at UTC midnight: `n`, `lost`, `sum`, `min`, `max`, the BG-LL5 histogram (`graph-aggregate.md`) and `paused_s`. It is written once its step has ended and every result for it has arrived, and never changes.

  | Source | Step | Kept | Built from | Serves |
  |---|---|---|---|---|
  | Raw | the Round | 2 h | measurement | 1m, 15m, 1h |
  | A1 | 5 min | 24 h (288 Rows) | Raw | 24h |
  | A2 | 1 h | 7 d (168 Rows) | A1 (12 Rows) | 7d |
  | A3 | 1 day | 365 d by default; the user can shorten it | A2 (24 Rows) | All |

  Each Archive merges Rows of the one before it, which is exact for every field (`graph-aggregate.md`, Merge), so a Row needs no Raw older than 5 minutes plus the arrival allowance. Every step divides the next, so Rows nest.
- **Paused Rows.** A Row or graph bucket more than half Paused draws as Paused. Otherwise it draws its data, and its Paused share is still recorded.
- **One source per range.** A graph draws closed buckets or Rows from its one source, one point per Row: 288 on 24h and 168 on 7d. Ranges drawn from Raw keep today's bucket widths: 1 s, 3 s and 15 s. The stretch after the last closed Row is built the same way from what exists so far, and marked provisional. Closed points never change; only the provisional edge moves.
- **All.** Draws A3, at most 240 points; when more Rows exist, adjacent Rows merge in fixed, epoch-aligned groups.
- **Links.** Several Links can be active at once (Ethernet, Wi-Fi, a VPN; on iOS, Wi-Fi and cellular), on every platform. Each active Link runs the Probe Group on its own interface, and its Raw, Archives (through All), stats and baselines are kept per Link. Graphs show one line per Link by default ("1.1.1.1 · Wi-Fi"), with Link changes marked, and the user can pick one Link. The Verdict speaks for the Link carrying the default route; other Links show their state in the Panel only. A Probe is sent on a Link only if that Link routes its Target, so a split-tunnel VPN measures only Targets inside it; the rest record nothing, as for an unreachable IP version.

## Rules and data to write

One breaking spec release (`feat!:`), in a single PR:

1. **`rules/history.md`, rewritten:** Round timing kept; Pause, settle and cut Rounds; Raw; Archives and when a Row is written; range to source; Paused buckets; provisional edge; Link markers.
2. **`rules/probe-stats.md`:** windows from now; a Probe is sent on a Link only if that Link routes its Target; a Probe with an empty window has no stats; Raw replaces "RAM".
3. **`rules/graph-aggregate.md`:** "Per-minute storage" becomes the Row; add `paused_s` and its merge.
4. **`rules/verdict.md`:** the Verdict's input is the default-route Link's Probes. While the window is empty after a Pause: Ok `Paused` "Resuming measurements", so a resume never turns the Menu Icon amber or red.
5. **`defaults.json`:** replace `history.ram_minutes` and `history.rollup_days` with `raw_minutes` (120), `settle_s` (2), and the Archive table with its retention.
6. **Vectors:** new `vectors/history/` (Pause and cut Rounds, settle, Row writing and merging, paused share, range to source, provisional edge, Link markers); `probe-stats` vectors gain `now`; `sketch` vectors gain `paused_s`. The vectors replaced are `history/{timing, minutes, ranges, buckets, steady}`.

Hop statistics, Process Snapshots and the Verdict's other rules don't change.

## Plan per platform

Each platform implements the release above and passes its vectors. Each plan is written for that repo's own agent. Order: iOS first, where the pain is, then Windows, then macOS.

### iOS

- **History core (`BlinkengraphsCore`):** replace `Rollups`, `RollupFiles`, `HistoryBuckets`, `GraphBuckets`, `HistoryLine` and `LinkHistories` with:
  - **Raw:** an append-only file of results, Pauses and Link changes.
  - **An Archive writer:** A1 from Raw; A2 and A3 from A1.
  - **A range reader:** picks the one source for a range and returns closed points plus the provisional edge.
  - Keep it Foundation-only (ADR 0001) so the vectors run on Linux, and so macOS can use it.
- **Lifecycle (`Monitor`, `BlinkengraphsApp`):**
  - `.background` begins a Pause and `.active` ends it after `settle_s`. This replaces `PathSettle`'s 1 s guess.
  - Rounds whose timeout ends after the Pause began record nothing.
  - On launch, a Pause covers the time from the last Raw record to now.
  - Wrap the stop path in `beginBackgroundTask`, so the Pause record reaches disk.
- **Stats:** windows from now; "–" and the resuming Finding after a Pause.
- **Links:** run the Probe Group on each active Link, Wi-Fi and cellular included, by pinning each Probe's interface (`NWParameters.requiredInterface`). History, stats and baselines per Link.
- **Graphs:** Links together by default with a Link picker; Link changes marked; Paused buckets and the provisional edge drawn; drop the per-minute line cache.
- **ADRs:** supersede 0005 (graphs per Link), 0007 (daily JSON-lines Rollups), 0012 (backgrounding) and 0013 (path settle), each pointing to this proposal.

### Windows

- **`history` crate:** split the 1111-line `lib.rs` into Raw (SQLite tables for results, Pauses and Link changes), the Archive writer and the range reader. Keep the `History::series` and `record_*` surface, which `panel`, `meters`, `config` and the app use.
- **Lifecycle:**
  - `RegisterSuspendResumeNotification` (or `WM_POWERBROADCAST`) begins and ends a Pause.
  - The existing display-off, lock and screen-saver rest (`win.rs:657-680`) also records a Pause.
  - In-flight Rounds that a Pause cut record nothing.
  - Hibernate and abrupt exits need nothing more, because Raw is already on disk.
- **Stats:** windows from now (`history/src/lib.rs:330-333`).
- **Links:** enumerate active adapters and run the Probe Group on each, sending from that interface (`IP_UNICAST_IF` for TCP/UDP/DNS, a source address with `IcmpSendEcho2Ex`/`Icmp6SendEcho2`). History, stats and baselines per Link; Panel graphs get a Link picker.
- **Meters:** the tray meter draws by time, so a Pause shows as a Pause, not as old and new results side by side (`meters/src/lib.rs:27`).
- **Conformance:** replace the `buckets` and `minutes` vectors in `tools/conformance` with the new set.
- **ADR:** supersede the Minute and seam parts of ADR 0017.

### macOS

- **No code yet.** Build to this model from the start.
- **Decide first, in an ADR:** use iOS's `BlinkengraphsCore`, which already declares macOS 15 (`BlinkengraphsKit/Package.swift:6`), as a SwiftPM dependency, or move it to its own repo.
- **Lifecycle:**
  - NSWorkspace `willSleep`/`didWake` begin and end a Pause.
  - A dark wake (Power Nap) stays Paused.
  - `ProcessInfo.beginActivity` keeps App Nap from throttling Rounds while measuring.
- **Links:** run the Probe Group on each active Link, as on iOS (`NWParameters.requiredInterface`).
- **Spec pin:** pin the release that carries this proposal, and run its vectors in CI.

## Open questions

- `settle_s` ships as 2 s. A device test of first-reply time after resume on Wi-Fi, cellular and VPN should confirm or change it.
- Raw on disk at 1 s Rounds is about 100k results per 2 hours per Link. Each platform measures its write cost, especially iOS flash wear and battery.
