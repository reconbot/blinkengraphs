# History

How results are timed, kept, rolled up and drawn, so the same measurements give the same graphs and numbers on every platform. `vectors/history/*.json` is the authority. Probe stats over a window are in [`probe-stats.md`](probe-stats.md), and what a graph point holds is in [`graph-aggregate.md`](graph-aggregate.md).

## Timing

A Probe Group runs in rounds at a fixed rate: round *k* starts at `start + k × interval`, however long earlier rounds took. A round that comes due while the previous one is still running starts when that one ends. Rounds it missed are skipped, not queued.

Every result of a round carries the round's `at`: whole Unix seconds, rounded down, when the round started. A Sample's `at` is whole Unix seconds when it was taken. So a 30 s window at a 1 s interval holds 30 rounds.

## RAM

Per key (each Metric, each Probe), keep the results with `at + ram_s > newest.at`, where *newest* is the newest result of any kind and `ram_s` is `defaults.json` `history.ram_minutes × 60`. A result exactly `ram_s` older than the newest is dropped.

## Minutes

A minute is `m = ⌊at / 60⌋ × 60`. For each key and minute with at least one result, storage keeps one Minute ([`graph-aggregate.md`](graph-aggregate.md), "Per-minute storage") built from that minute's results.

- **When a Minute is written:** once a result arrives with `at ≥ m + 60 + g`, where `g = ⌈max_timeout_ms / 1000⌉ + 1` seconds. Results stamped in the minute arrive at most a timeout after their `at`, so none is left out. Shutting down writes every minute not yet written.
- **Retention:** delete Minutes with `m < newest.at − rollup_days × 86400` (`defaults.json` `history.rollup_days`, or the user's choice).
- A Minute is written once and never merged with a later write of the same key and minute.

## Graph ranges

| Range | Span |
|---|---|
| 1m | 60 s |
| 15m | 900 s |
| 1h | 3600 s |
| 24h | 86 400 s |
| 7d | 604 800 s |
| All | From the oldest Minute or RAM result to now, at least 60 s |

A graph shows `[now − span, now]` in up to 240 points.

## Graph buckets

Let `w = max(⌊span / 240⌋, 1)` seconds, and `c = ⌈first / 60⌉ × 60`, where *first* is the oldest RAM result of the key; with no RAM results, `c` is `now + 1`.

- **From storage:** Minutes with `now − span ≤ m + 59` and `m < c`, grouped into buckets of `W = ⌈w / 60⌉ × 60` seconds starting at `⌊m / W⌋ × W`, merged as in `graph-aggregate.md`.
- **From RAM:** results with `max(now − span, c) ≤ at ≤ now`, grouped into buckets of `w` seconds starting at `⌊at / w⌋ × w`, ranked as raw samples.

Buckets align to the Unix epoch, not to `now`. RAM results before `c` are left out: their minute comes from storage, so nothing is counted twice. A point's time is its bucket's start.

## Drawing

- A bucket with no results has no point, and the line breaks there rather than joining its neighbours.
- A bucket whose results are all lost has no value: it draws as a loss mark, not as a line point.
- A bucket with some losses draws its value, plus its loss (`graph-aggregate.md`, "Loss").
- The part of the span before the first point is shaded as having no data.
