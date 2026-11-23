# History

How results are timed, kept, summarised and drawn, so the same measurements give the same graphs and numbers on every platform. History is Raw plus three Archives ([ADR 0001](../docs/adr/0001-rrd-style-history.md)). `vectors/history/*.json` is the authority. Probe stats over a window are in [`probe-stats.md`](probe-stats.md), and what a Row holds is in [`graph-aggregate.md`](graph-aggregate.md).

A *key* is one Metric or one Probe on one Link. Times are Unix seconds. `g = ⌈max_timeout_ms / 1000⌉ + 1` seconds is how long after its `at` a result can still arrive.

## Rounds

A Probe Group runs in Rounds at a fixed rate: Round *k* starts at `start + k × interval`, however long earlier Rounds took. A Round that comes due while the previous one is still running starts when that one ends. Rounds it missed are skipped, not queued.

Every result of a Round carries the Round's `at`: whole Unix seconds, rounded down, when the Round started. A Sample's `at` is whole Unix seconds when it was taken.

## Pauses

A Pause is a stretch `[begin, end)` when blinkengraphs was not measuring, for any reason: the app suspended, the machine asleep, the process killed, or resting while idle.

- **Begin:** when the platform stops measuring. After a kill, it is one second after the newest record of any kind in Raw (a result, a Sample, a mark or a Link change), found on the next launch. A launch with nothing in Raw begins with a Pause from the launch, so the Verdict says measurements are resuming rather than all clear before any Probe has stats.
- **End:** when measuring resumes, plus the platform's settle time. The settle time covers the network becoming usable again; each platform sets it from its own device tests and records it in an ADR.
- **Cut Rounds:** a Round records nothing if any part of it, from its start to the end of its last Probe, falls in a Pause. Only a Round that ran its full timeout while measuring records a loss.

Each platform offers a Setting for resting while idle on desktops (display off, locked, screen saver); its default is the platform's, in an ADR.

## Link settle

A Link that appears, or whose Gateway or IP versions change, waits the settle time before it is measured: its Rounds that touch `[change, change + settle)` record nothing, as a Pause cuts Rounds. It is not a Pause, which is machine-wide: every other Link goes on measuring, and nothing is Paused in History. `vectors/history/link-settle.json` covers it.

## Raw

Raw holds every result and Sample, Pause and Link change, each with its Link. It keeps those with `at > now − raw_s`, where `raw_s` is `defaults.json` `history.raw_minutes × 60`. Raw reaches disk at most 10 seconds after each result, and when a Pause begins; on the next launch, anything newer than the last write is part of the Pause.

A write with nothing else in it, such as while Offline, records a *mark*: measuring went on. Without one, a kill after a long Offline stretch would turn that stretch into a Pause.

`vectors/history/launch.json` covers the Pause a launch finds.

## Archives

An Archive holds one Row per key and step, for steps that had at least one result, and the Paused seconds of every step. Steps are `[m, m + step)` with `m` a multiple of `step`, so days start at UTC midnight.

| Archive | Step | Rows kept | Built from |
|---|---|---|---|
| A1 | 300 s | 288 (24 h) | Raw results in the step |
| A2 | 3600 s | 168 (7 d) | the 12 A1 Rows of the step |
| A3 | 86 400 s | 365 (1 year), or fewer if the user chooses | the 24 A2 Rows of the step |

`defaults.json` `history.archives` holds the steps and Rows kept.

- **Written:** a step's Row is written once `now ≥ m + step + g`, and never changed. A2 and A3 merge the Rows of the Archive above, in ascending order ([`graph-aggregate.md`](graph-aggregate.md), "Merge").
- **Paused seconds:** the length of the step that falls in Pauses. A2 and A3 add their Rows' Paused seconds.
- **Retention:** an Archive drops Rows and Paused seconds older than its Rows kept: `m + step ≤ now − rows × step`.
- **Links:** Archive keys name a Link by its interface and Gateway, so the Access Points behind one Gateway share them. The interface is the OS's identity for the adapter that survives a restart. The Gateway is the Link's IPv4 Gateway, or its IPv6 Gateway when it has no IPv4 one, together with that Gateway's link-layer (MAC) address when the platform can read it without extra privileges or entitlements. Two networks behind the same Gateway address, such as two homes on `192.168.1.1`, then keep separate History. A platform that can't read the address names the Gateway by its IP address alone, so those networks share History there. A Link with no Gateway, such as a VPN whose default route is on-link, is named by its interface alone.

## Graph ranges

| Range | Span | Source | Point width |
|---|---|---|---|
| 1m | 60 s | Raw | 1 s |
| 15m | 900 s | Raw | 3 s |
| 1h | 3600 s | Raw | 15 s |
| 24h | 86 400 s | A1 | 300 s |
| 7d | 604 800 s | A2 | 3600 s |
| All | from the oldest A3 Row to now | A3 | 86 400 s × `k` |

A graph draws exactly one source. Its points are buckets `[b, b + w)` with `b` a multiple of the point width `w`, for every bucket with `b + w > now − span` and `b ≤ now`. For All, `k = ⌈rows / 240⌉`, where *rows* is the number of steps from the oldest A3 Row to now, so All draws at most 240 points.

- **From Raw:** a bucket holds the key's results with `b ≤ at < b + w`, ranked as raw values ([`graph-aggregate.md`](graph-aggregate.md), "Raw values").
- **From an Archive:** a bucket is the merge of the key's Rows in it.
- **Paused:** a bucket whose Paused seconds exceed `w / 2` is Paused, whatever results it holds. From Raw, its Paused seconds are its overlap with Pauses; from an Archive, the sum over its steps.
- **Provisional:** a bucket that isn't finished yet, `now < b + w + g`, is provisional. From an Archive, its unwritten steps are built the same way their Rows will be, from the Rows and Raw that exist now. Only provisional points can change.

A graph draws one line per Link of the key ("1.1.1.1 · Wi-Fi"); the user can pick one Link. On ranges drawn from Raw, a marker shows where the default-route Link changed.

## Drawing

- A bucket with no results and not Paused has no point, and the line breaks there rather than joining its neighbours.
- A Paused bucket draws as Paused: shaded "not measuring", never as loss.
- A bucket whose results are all lost has no value: it draws as a loss mark, not as a line point.
- A bucket with some losses draws its value, plus its loss (`graph-aggregate.md`, "Loss").
- A provisional point is marked as such.
- The part of the span before the first point is shaded as having no data.
