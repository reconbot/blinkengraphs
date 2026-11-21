# Probe stats

How each platform turns a Probe's results into the stats the Verdict and the Panel read. `vectors/probe-stats/*.json` is the authority: for each vector's `results`, an implementation conforms when it produces `expected` to within 0.01.

## Results

A Probe result is `(at, rtt_ms)`, where `at` is Unix seconds and `rtt_ms` is absent when the Probe got no reply before its timeout. The timeout is `min(interval, max_timeout_ms)` from `defaults.json`.

A `denied` result, where the OS refused to send the Probe (for example iOS Local Network Privacy blocking the Gateway), is not a loss. It is not recorded, so a denied Probe has no stats and is absent from the Verdict input. The platform says so outside the Verdict.

History keeps results for `ram_s` (15 min) behind the newest result of any kind; older ones are dropped.

## Stats

Let *window* be the results with `at + window_s > newest.at`, where `window_s` is 30 and *newest* is this Probe's newest result. *Replies* are the window's results that have an RTT, in arrival order.

| Stat | Definition |
|---|---|
| `loss` | `1 − replies / window`, or 0 when the window is empty |
| `rtt_ms` | Median of replies: sorted ascending, the element at index `⌊n / 2⌋`. Absent when there are no replies |
| `baseline_ms` | 10th percentile of every RTT in history, not only the window: sorted ascending, the element at index `⌊(n − 1) × 0.1⌋`. Absent when there are none |
| `jitter_ms` | Mean absolute difference between consecutive replies. Absent with fewer than two |

The baseline spans the whole history so that congestion lasting most of the window still reads as a rise above normal.
