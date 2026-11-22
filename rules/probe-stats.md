# Probe stats

How each platform turns a Probe's results into the stats the Verdict and the Panel read. `vectors/probe-stats/*.json` is the authority: for each vector's `results`, an implementation conforms when it produces `expected` to within 0.01.

## Results

A Probe result is `(at, rtt_ms)`, where `at` is its round's whole Unix second ([`history.md`](history.md), "Timing") and `rtt_ms` is absent when the Probe got no reply before its timeout. The timeout is `min(interval, max_timeout_ms)` from `defaults.json`.

A `denied` result, where the OS refused to send the Probe (for example iOS Local Network Privacy blocking the Gateway), is not a loss. It is not recorded, so a denied Probe has no stats and is absent from the Verdict input. The platform says so outside the Verdict.

A Probe whose Target's IP version the path can't reach is not sent and records nothing, like a denied one. IPv6 Targets need IPv6 on the path. IPv4 Targets need IPv4, native or translated (464XLAT, NAT64): on an IPv6-only path, an IPv4 send that fails at once for lack of a route marks IPv4 unreachable.

While the OS reports no network path, platforms send no Probes and record nothing; the Verdict reports Offline instead ([`verdict.md`](verdict.md)).

History keeps results for `ram_s` (15 min) behind the newest result of any kind ([`history.md`](history.md), "RAM").

## Stats

Let *window* be the results with `at + window_s > newest.at`, where `window_s` is 30 and *newest* is this Probe's newest result. *Replies* are the window's results that have an RTT, in arrival order.

| Stat | Definition |
|---|---|
| `loss` | `1 − replies / window`, or 0 when the window is empty |
| `rtt_ms` | Median of replies: sorted ascending, the element at index `⌊(n − 1) / 2⌋`. Absent when there are no replies |
| `baseline_ms` | 10th percentile of every RTT in history, not only the window: sorted ascending, the element at index `⌊(n − 1) × 10 / 100⌋`. Absent when there are none |
| `jitter_ms` | Mean absolute difference between consecutive replies. Absent with fewer than two |

The baseline spans the whole history so that congestion lasting most of the window still reads as a rise above normal.

Every percentile here and in [`graph-aggregate.md`](graph-aggregate.md) uses one rank: pX of *n* sorted values is the element at index `⌊(n − 1) × X / 100⌋`, in integer arithmetic. `rtt_ms` is p50 and `baseline_ms` is p10.

## Readouts

A Probe's latency readout shows one number for its window: p50, p95, p99, avg or max, picked by the user in Settings and starting at `defaults.json` `readout_aggregate` (`p95`: it shows the slow tail a median hides). With `p50` it is `rtt_ms`. Otherwise it is that aggregate of the window's replies, ranked as above. The readout names its aggregate unless it is `p50`.

The Verdict always uses `rtt_ms`, whatever the readout shows.
