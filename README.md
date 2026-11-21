# blinkengraphs

Live CPU, memory, disk, network and latency graphs where you can always see them, and a plain-language answer to two questions: **why is my computer slow?** and **why isn't my network responding?** Inspired by iStat Menus, MenuMeters, gping and mtr.

![Panel during ISP packet loss](https://raw.githubusercontent.com/reconbot/blinkengraphs-win/ci-screenshots/main/panel-isp-loss-overview.png)

## Download

| Platform | Status | Get it |
|---|---|---|
| **Windows 11** (x64, ARM64) | v1.0 | [Latest release](https://github.com/reconbot/blinkengraphs-win/releases/latest) · [source](https://github.com/reconbot/blinkengraphs-win) |
| **macOS** (menu bar) | planned | [blinkengraphs-mac](https://github.com/reconbot/blinkengraphs-mac) |
| **iOS** (network diagnosis) | planned | [blinkengraphs-ios](https://github.com/reconbot/blinkengraphs-ios) |

## What it shows

- **Meters:** small always-visible graphs, as tray icons or a strip in the taskbar.
  ![Taskbar Strip](https://raw.githubusercontent.com/reconbot/blinkengraphs-win/ci-screenshots/main/strip-upload-saturation.png)
- **Verdict:** names the fault: your LAN or Wi-Fi, your ISP, DNS, ping filtering, a remote host, your own upload filling the link, or local CPU, memory or disk load.
- **Probes:** ICMP, TCP and DNS latency to the gateway, 1.1.1.1 and 8.8.8.8, graphed like gping, plus an mtr-style hop trace.
- **Footprint:** a feature in its own right. The Windows version uses under 1% of one core, about 16 MB of RAM and a 6.5 MB exe.

## This repository

The shared spec that keeps every platform consistent. It contains no app code.

| Path | Contents |
|---|---|
| [`CONTEXT.md`](CONTEXT.md) | Vocabulary: Section, Metric, Probe, Verdict, Finding, Fault Domain… |
| [`rules/verdict.md`](rules/verdict.md) | The Verdict rules |
| [`rules/probe-stats.md`](rules/probe-stats.md) | Loss, RTT, baseline and jitter from raw Probe results |
| [`rules/hop-trace.md`](rules/hop-trace.md) | Hop Trace sweeping and the hop table |
| [`defaults.json`](defaults.json) | Default Probe Group, intervals, timeouts and history lengths |
| [`vectors/verdict/`](vectors/verdict/) | Test vectors: inputs and the Findings each platform must produce |
| [`vectors/probe-stats/`](vectors/probe-stats/) | Raw results → Probe stats |
| [`vectors/hop-trace/`](vectors/hop-trace/) | Hop results → hop table |
| [`vectors/meters/`](vectors/meters/) | Meter normalization vectors (network cube root, latency scale) |
| [`tokens/`](tokens/) | Colors and thresholds in [W3C design-token](https://www.designtokens.org/) format |
| [`fixtures/scenarios/`](fixtures/scenarios/) | Synthetic histories for screenshots and previews |
| [`docs/cross-platform.md`](docs/cross-platform.md) | Why each platform is native and they share a spec instead of code |

Platform repos pin a tagged version of this spec and run its vectors in CI. Versions are cut by release-please from Conventional Commits: a breaking rule change is a major version. A rule change is a PR here plus one PR per platform.

The vectors are generated from the Windows reference implementation: `cargo run -p vectors -- <path to this repo>` in blinkengraphs-win.

## License

MIT OR Apache-2.0
