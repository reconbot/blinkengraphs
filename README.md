# blinkengraphs

Live CPU, memory, disk, network and latency graphs where you can always see them, and a plain-language answer to two questions: **why is my computer slow?** and **why isn't my network responding?** Inspired by iStat Menus, MenuMeters, gping and mtr.

<p>
  <img src="https://raw.githubusercontent.com/reconbot/blinkengraphs-win/ci-screenshots/main/panel-isp-loss-overview.png" height="420" alt="Windows Panel during ISP packet loss">
  <img src="https://raw.githubusercontent.com/reconbot/blinkengraphs-ios/ci-screenshots/main/isp-loss-dark-top.png" height="420" alt="iOS during the same ISP packet loss">
</p>

## Download

| Platform | Status | Get it |
|---|---|---|
| **Windows 11** (x64, ARM64) | v1.0 | [Latest release](https://github.com/reconbot/blinkengraphs-win/releases/latest) · [source](https://github.com/reconbot/blinkengraphs-win) |
| **macOS** (menu bar) | planned | [blinkengraphs-mac](https://github.com/reconbot/blinkengraphs-mac) |
| **iOS** (network diagnosis) | v1.0, build from source and sideload | [Latest release](https://github.com/reconbot/blinkengraphs-ios/releases/latest) · [source](https://github.com/reconbot/blinkengraphs-ios) |

## The apps

Each platform is native and implements this spec ([`docs/cross-platform.md`](docs/cross-platform.md)). The iOS and macOS apps share their Swift rules code through [blinkengraphs-kit](https://github.com/reconbot/blinkengraphs-kit).

| Windows 11 | iOS |
|---|---|
| Meters in the taskbar or tray, and a Panel with the Verdict, history graphs, Hop Traces and the processes behind CPU, memory, disk and network load. | Network diagnosis while the app is open: the Verdict, latency and loss over 1m to 7d, Target cards, a Hop Trace and the Public Address. No CPU or memory: iOS doesn't expose them. |
| <img src="https://raw.githubusercontent.com/reconbot/blinkengraphs-win/ci-screenshots/main/panel-isp-loss-network.png" width="380" alt="Windows Panel, network view"> | <img src="https://raw.githubusercontent.com/reconbot/blinkengraphs-ios/ci-screenshots/main/range-24h-isp-loss-dark.png" width="220" alt="iOS, 24 hours of latency"> <img src="https://raw.githubusercontent.com/reconbot/blinkengraphs-ios/ci-screenshots/main/wifi-light-bottom.png" width="220" alt="iOS Hop Trace, light"> |

Screenshots are rendered by each app's CI from demo data.

## What it shows

- **Meters:** small always-visible graphs, as tray icons or a strip in the taskbar.
  ![Taskbar Strip](https://raw.githubusercontent.com/reconbot/blinkengraphs-win/ci-screenshots/main/strip-upload-saturation.png)
- **Verdict:** names the fault: your LAN or Wi-Fi, your ISP, IPv4 or IPv6 broken, DNS, ping filtering, a remote host, a VPN, a captive portal, your own upload filling the link, or local CPU, memory or disk load.
- **Probes:** ICMP, TCP and DNS latency to the gateway, Cloudflare and Quad9 over IPv4 and IPv6, graphed like gping, plus an mtr-style hop trace.
- **Public Address:** your IPv4 and IPv6 as the internet sees them, from two independent lookups.
- **Footprint:** a feature in its own right. The Windows version uses under 1% of one core, about 16 MB of RAM and a 6.5 MB exe.

## This repository

The shared spec that keeps every platform consistent. It contains no app code.

| Path | Contents |
|---|---|
| [`CONTEXT.md`](CONTEXT.md) | Vocabulary: Section, Metric, Probe, Verdict, Finding, Fault Domain… |
| [`rules/verdict.md`](rules/verdict.md) | The Verdict rules |
| [`rules/probe-stats.md`](rules/probe-stats.md) | Loss, RTT, baseline and jitter from raw Probe results |
| [`rules/hop-trace.md`](rules/hop-trace.md) | Hop Trace sweeping and the hop table |
| [`rules/probe-group.md`](rules/probe-group.md) | One row per Target, `system-dns` measuring DNS only, and what its lookup asks |
| [`rules/defaults.md`](rules/defaults.md) | How a platform's overrides merge over `defaults.json` |
| [`rules/history.md`](rules/history.md) | Probe timing, RAM retention, minute Rollups, graph ranges and buckets |
| [`rules/graph-aggregate.md`](rules/graph-aggregate.md) | What a Row holds, and p50/p95/p99/avg/max per graph bucket |
| [`rules/public-address.md`](rules/public-address.md) | The Public Address per IP version, from a DNS and an HTTPS lookup |
| [`defaults.json`](defaults.json) | Shared defaults: Probe Group, intervals, timeouts and history lengths. Platforms override it per [`rules/defaults.md`](rules/defaults.md) |
| [`vectors/verdict/`](vectors/verdict/) | Test vectors: inputs and the Findings each platform must produce |
| [`vectors/probe-stats/`](vectors/probe-stats/) | Raw results → Probe stats |
| [`vectors/hop-trace/`](vectors/hop-trace/) | Hop results → hop table |
| [`vectors/defaults/`](vectors/defaults/) | Defaults and overrides → merged defaults |
| [`vectors/sketch/`](vectors/sketch/) | Histogram index, encoding and merged aggregates |
| [`vectors/meters/`](vectors/meters/) | Meter normalization vectors (network cube root, latency scale) |
| [`vectors/public-address/`](vectors/public-address/) | Lookup answers → Public Address reading |
| [`brand/`](brand/) | The app icon (`icon.svg`) every platform renders its formats from |
| [`tokens/`](tokens/) | Colors and thresholds in [W3C design-token](https://www.designtokens.org/) format, with a light palette |
| [`fixtures/scenarios/`](fixtures/scenarios/) | Synthetic histories for screenshots and previews |
| [`docs/sync.md`](docs/sync.md) | How a change flows through every repo |
| [`docs/access-points.md`](docs/access-points.md) | Proposal: diagnosing and avoiding failing Access Points |
| [`docs/cross-platform.md`](docs/cross-platform.md) | Why each platform is native and they share a spec instead of code |

Platform repos pin a tagged version of this spec and run its vectors in CI. Versions are cut by release-please from Conventional Commits: a breaking rule change is a major version. A rule change is a PR here plus one PR per platform.

Everything here, vectors, fixtures and tokens included, is authored in this repo. Platforms implement it; none generates it.

## License

MIT OR Apache-2.0
