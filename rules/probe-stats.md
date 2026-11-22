# Probe stats

How each platform turns a Probe's results into the stats the Verdict and the Panel read. `vectors/probe-stats/*.json` is the authority: for each vector's `results` and `now`, an implementation conforms when it produces `expected` to within 0.01.

## Results

A Probe result is `(at, rtt_ms)`, where `at` is its Round's whole Unix second ([`history.md`](history.md), "Rounds") and `rtt_ms` is absent when the Probe got no reply before its timeout. The timeout is `min(interval, max_timeout_ms)` from `defaults.json`.

`rtt_ms` is a whole number of milliseconds: the measured round trip `d`, in milliseconds, recorded as `⌊d + 0.5⌋`. A reply faster than 0.5 ms records 0 and displays as "< 1 ms". Finer resolution tells a user nothing, and whole numbers keep every platform's stored values, ranks and Minutes identical. Stats and aggregates computed from them, such as `jitter_ms` or avg, can still have fractions; displays show whole milliseconds. `vectors/rtt/whole-ms.json` covers the rounding.

A `denied` result, where the OS refused to send the Probe (for example iOS Local Network Privacy blocking the Gateway), is not a loss. It is not recorded, so a denied Probe has no stats and is absent from the Verdict input. The platform says so outside the Verdict.

A Probe whose Target's IP version the path can't reach is not sent and records nothing, like a denied one. IPv6 Targets need IPv6 on the path. IPv4 Targets need IPv4, native or translated (464XLAT, NAT64): on an IPv6-only path, an IPv4 send that fails at once for lack of a route marks IPv4 unreachable.

While the OS reports no network path, platforms send no Probes and record nothing; the Verdict reports Offline instead ([`verdict.md`](verdict.md)).

A Probe is sent on a Link only if that Link routes its Target. A Target the Link doesn't route, such as 1.1.1.1 on a split-tunnel VPN that carries only 10.0.0.0/8, is not sent on it and records nothing.

A Round cut by a Pause records nothing ([`history.md`](history.md), "Pauses").

Stats are per Link: a Probe on each active Link has its own. Raw keeps results for `raw_s` (2 h) ([`history.md`](history.md), "Raw").

## Stats

Let *window* be the results with `at > now − window_s`, where `window_s` is `defaults.json` `history.recent_window_s` (30). The window is measured back from now, not from the newest result, so results from before a Pause age out of it. *Replies* are the window's results that have an RTT, in arrival order.

| Stat | Definition |
|---|---|
| `loss` | `1 − replies / window` |
| `rtt_ms` | Median of replies: sorted ascending, the element at index `⌊(n − 1) / 2⌋`. Absent when there are no replies |
| `baseline_ms` | 10th percentile of every RTT in Raw (`at > now − raw_s`), not only the window: sorted ascending, the element at index `⌊(n − 1) × 10 / 100⌋`. Absent when there are none |
| `jitter_ms` | Mean absolute difference between consecutive replies. Absent with fewer than two |

A Probe whose window is empty has no stats: it is absent from the Verdict input, and its readout shows "–".

The baseline spans all of Raw so that congestion lasting most of the window still reads as a rise above normal.

Every percentile here and in [`graph-aggregate.md`](graph-aggregate.md) uses one rank: pX of *n* sorted values is the element at index `⌊(n − 1) × X / 100⌋`, in integer arithmetic. `rtt_ms` is p50 and `baseline_ms` is p10.

## Readouts

A Probe's latency readout shows one number for its window: p50, p95, p99, avg or max, picked by the user in Settings and starting at `defaults.json` `readout_aggregate` (`p95`: it shows the slow tail a median hides). With `p50` it is `rtt_ms`. Otherwise it is that aggregate of the window's replies, ranked as above. The readout names its aggregate unless it is `p50`.

The Verdict always uses `rtt_ms`, whatever the readout shows.
