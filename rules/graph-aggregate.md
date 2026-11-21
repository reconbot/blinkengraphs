# Graph aggregate

What each point of a history graph shows when it covers several samples: p50, p95, p99, avg or max, chosen once for all graphs. `vectors/sketch/*.json` is the authority, and f64 results must match their `bits` exactly.

## Per-minute storage

For each key and minute, keep:

| Field | Definition |
|---|---|
| `n` | Values recorded |
| `lost` | Probes lost (Probes only) |
| `sum` | f64 sum of the values in arrival order |
| `min`, `max` | Exact |
| `sk` | Log-linear histogram, below |

### Histogram ("BG-LL5")

- **Input:** each value as recorded, widened to f64.
- **Zero bucket:** values below 2⁻¹⁰, including 0 and negatives.
- **Bucket index:** for every other value, with `b` its IEEE-754 bits:
  - `e = ((b >> 52) & 0x7FF) − 1023`
  - `m = (b >> 47) & 31`
  - `index = clamp((e + 10) · 32 + m, 0, 1599)`
- **Representative value:** with `lo = (32 + m) · 2^(e − 5)` and `hi = (33 + m) · 2^(e − 5)`, it is `2 · lo · hi / (lo + hi)`. Relative error is at most 1/65 (1.54%).
- **Exact arithmetic only:** bit extraction and `+ − × ÷`, no logarithms. `ln` precision is unspecified and differs between platforms.
- **Encoding:** `uleb128(zero_count)`, then for each non-empty bucket in ascending order `uleb128(index − previous − 1)`, `uleb128(count)`, with `previous` starting at −1.

## A graph bucket

A bucket spans whole minutes from storage, or raw samples from the recent RAM history.

- **Merge:** add `n`, `lost` and the histogram counts as integers; any order gives the same result. Add `sum` in ascending minute order. Take the min of `min` and the max of `max`.
- **Loss:** `lost / (n + lost)`.
- **avg:** `sum / n`.
- **max:** `max`.
- **pX:** with per-mille X ∈ {500, 950, 990}:
  1. `r = ⌊X · (n − 1) / 1000⌋` in integer arithmetic.
  2. If `r` is below the zero count, the value is 0.
  3. Otherwise walk the buckets upward. At the first bucket whose cumulative count exceeds `r`, the value is its representative, clamped to `[min, max]`.
- **Raw samples:** use the same rank on the sorted values, with no histogram.

The Verdict and the per-Probe readouts do not use this. They follow `probe-stats.md` and each Probe's own window.
