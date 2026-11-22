# Verdict rules

The Verdict is an ordered list of Findings, most severe first, and is never empty. Every platform implements these rules natively. `vectors/verdict/*.json` is the authority: an implementation conforms when, for each vector's `input`, it produces the `expected` Findings with the same `domain`, `severity` and `headline`.

## Input

- **Probe stats**, per Probe, as defined in [`probe-stats.md`](probe-stats.md): `loss` (0–1), `rtt_ms`, `baseline_ms`, `jitter_ms`. Denied Probes are absent.
- **The last Sample**, optional, holding the Metric values.
- **`upload_peak_bps`**: the highest upload rate seen recently. It stands in for the link capacity, which is unknown.
- **`path_up`**, optional, default `true`: whether the OS reports any usable network path. It is `false` in airplane mode, with every radio off, or with the cable out.

## Probe classes

- **Gateway:** Probes whose target is `gateway`.
- **Internet:** Probes to any other target except `system-dns`, excluding DNS Probes.
- **DNS:** Probes with protocol `dns`.

A Gateway or Internet Probe only counts once it has a baseline or has recorded loss.

## Offline

When `path_up` is `false`, the only network Finding is Crit `Offline` "No network connection". No network rule and no DNS rule runs; the Local rules still do.

## Network rules, in order

| # | Condition | Finding |
|---|---|---|
| 1 | Gateway loss ≥ 50% and every Internet Probe loss ≥ 50% | Crit `Lan` "Gateway unreachable: Wi-Fi or LAN problem". Stop evaluating network rules. |
| 2 | Gateway loss ≥ 5% | Warn `Lan` "Local network unstable: gateway losing {loss}" |
| 3 | Best Internet loss ≥ 50% | Crit `Isp` "Gateway OK, internet unreachable: ISP or WAN problem". With no Gateway Probe: "Internet unreachable, gateway not measured: ISP or WAN problem" |
| 4 | Every ICMP Internet Probe loss ≥ 50% and some TCP Internet Probe loss < 5% | Warn `IcmpFiltering` "ICMP blocked; TCP gets through: something filters ping" |
| 5 | The worst Internet Probe has loss ≥ 5%, and every Internet Probe has loss ≥ 5% | `Isp` "Gateway OK, {target} losing {loss}: ISP problem", without "Gateway OK, " when there is no Gateway Probe. Crit when loss ≥ 20%, otherwise Warn. |
| 6 | The worst Internet Probe has loss ≥ 5%, and another one has loss < 5% | Warn `Remote` "{bad} losing {loss}, {good} fine: problem is on their side" |
| 7 | Otherwise: some Internet RTT > 3 × its baseline and more than 30 ms above it, while upload > 1 MB/s and ≥ 80% of `upload_peak_bps` | Warn `SelfSaturation` "Upload saturated ({upload}/s): {rtt} ms vs {baseline} ms normal" |

Rules 3–7 are exclusive: the first that matches wins.

**DNS rule.** A DNS Probe is bad when its loss ≥ 30% or its RTT > 250 ms. If the `system-dns` Probe is bad, the Finding is Warn `Dns` "Your DNS server is {slow ({rtt} ms) | losing {loss}}". When another DNS Probe is fine, the headline ends with "; 1.1.1.1 answers fine".

## Local rules

| Condition | Finding |
|---|---|
| CPU total ≥ 90% | Crit `LocalLoad` "CPU pinned at {cpu}%" |
| Commit ≥ 90% | Crit `LocalLoad` "Memory nearly exhausted: commit {commit}%" |
| Otherwise, hard faults ≥ 1000/s | Warn `LocalLoad` "Paging heavily: {faults} hard faults/s" |
| Disk active ≥ 90% and response ≥ 50 ms | Warn `LocalLoad` "Disk saturated: {active}% busy, {ms} ms response" |

Local Metric names follow Windows (commit charge, hard faults). Other platforms map them to their nearest equivalent. Pending: platform-neutral Metric names ([cross-platform proposal](../docs/cross-platform.md#spec-changes-needed-before-a-second-platform)).

## Formatting

- Percentages are rounded to whole numbers.
- Milliseconds are rounded to whole numbers.
- Byte rates use 1000-based units with one decimal above 1 MB (`10.7 MB`).

If no rule fires, the Verdict is a single Ok `Clear` "All clear". Findings are sorted Crit, then Warn, then Ok; ties keep rule order.
