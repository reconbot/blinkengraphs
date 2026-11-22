# blinkengraphs

System monitors for Windows, macOS and iOS that answer at a glance: "why is my computer slow?" and "why isn't my network responding?" This glossary is shared by every platform.

## Language

### Measuring the machine

**Section**:
One of the five things blinkengraphs watches: CPU, Memory, Network, Disk, Latency. Each Section has one Meter and one area in the Panel.
_Avoid_: category, widget, module

**Metric**:
One named series of numbers within a Section, such as CPU total, commit charge, or download throughput.
_Avoid_: counter, stat, sensor

**Readout**:
Something a Section can show: one of its Metrics, or for Latency the Probe's latency or loss. The user picks the Readouts each Surface and the Panel show, per Section. A Section with none is hidden there.
_Avoid_: field, item

**Sample**:
The values of every enabled Metric at one instant.
_Avoid_: reading, tick, datapoint

**Memory Pressure**:
How close the machine is to running out of committable memory, together with how hard it is paging. It is not "% of RAM used."
_Avoid_: memory usage, RAM %

**Followed Adapter**:
The network adapter whose traffic the Network Section shows and whose Link the Verdict judges: either the one that currently carries the default route, or one the user pinned.
_Avoid_: interface (overloaded), NIC

### Measuring the network

**Target**:
A host that blinkengraphs measures reachability to, such as the Gateway, 1.1.1.1, 2606:4700:4700::1111 or example.com. Each IP address Target has one IP version. A Target given as a name is resolved, and resolved again at most every 30 seconds; it takes the IP version of the address it resolves to, and its Probes are skipped while it doesn't resolve. Which address a platform picks when a name has both versions is the platform's choice.
_Avoid_: host, endpoint, server

**Gateway**:
The first-hop router on the Followed Adapter's default route.
_Avoid_: router, default gateway IP

**Link**:
One adapter's current attachment to a network: its interface, its Gateway, and its Access Point when known. Several Links can be active at once, such as Ethernet, Wi-Fi and a VPN; each is measured on its own, and its Probe results and Hop statistics belong to it. The Followed Adapter's Link is the one the Network Section shows.
_Avoid_: connection (overloaded), network

**Public Address**:
The address the internet sees this machine as, one per IP version. Behind NAT it belongs to the router or the carrier, not the Followed Adapter.
_Avoid_: external IP, WAN IP, my IP

**Wi-Fi Network**:
Every Access Point that shares one network name and its credentials. A station's Wi-Fi is one Wi-Fi Network of many Access Points.
_Avoid_: SSID (that is its name), hotspot

**Access Point**:
One radio of a Wi-Fi Network, identified by its BSSID. The Followed Adapter is joined to one Access Point at a time; several can sit behind one Gateway.
_Avoid_: AP, BSSID (that is its identifier), router, base station

**Avoided Access Point**:
An Access Point the user chose to skip. Where the OS allows choosing, blinkengraphs joins another Access Point of the same Wi-Fi Network instead. It stays avoided until the user undoes it.
_Avoid_: blocklist, banned AP

**Probe**:
One kind of reachability measurement against one Target, over one protocol: ICMP echo, TCP handshake to a port, UDP datagram to a port (a reply or port-unreachable counts as alive), or DNS query. A Probe yields a round-trip time, a loss, or `denied` when the OS refuses to send it (iOS and macOS Local Network Privacy). Denied is not a loss.
_Avoid_: ping (only ICMP is a ping), check, test

**Probe Group**:
A named table of Targets and what to measure on each: ICMP, a TCP port, a UDP port, DNS, Hop Trace. Latency, DNS and Hop Traces each run on their own interval. Every config starts with one group, "Default".
_Avoid_: schedule, batch

**Round**:
One firing of a Probe Group's Probes, all stamped with the instant it started. A Round cut short by a Pause records nothing: only a Round that ran its full timeout while measuring can record a loss.
_Avoid_: tick, cycle, poll

**Hop Trace**:
A continuous traceroute towards a Target that keeps latency and loss for every Hop, in the style of mtr.
_Avoid_: traceroute (implies one-shot), mtr (name of a tool)

**Hop**:
One router on the path to a Target, identified by its TTL distance and the address that answered.
_Avoid_: node, router

### Explaining

**Finding**:
One rule-based conclusion: a Fault Domain, a severity, and a one-line headline.
_Avoid_: alert, issue, problem

**Verdict**:
The current Findings, most severe first; the top one is the headline, such as "Gateway OK, 1.1.1.1 losing 12% → ISP problem".
_Avoid_: diagnosis, alert, insight

**Fault Domain**:
Where the trouble is: Local Load, LAN, Captive Portal (a sign-in page holding back the internet), ISP, DNS, Remote, ICMP Filtering, Self-Saturation (your own traffic filling the link), VPN (the tunnel or its exit), Offline (no network path at all), or Paused (measurements resuming after a Pause, never a fault).
_Avoid_: root cause, failure type

**Process Snapshot**:
A list of the top processes per Section, taken only while the Panel is open.
_Avoid_: blame log, process history

### Showing

**Meter**:
The always-visible small graph of one Section's enabled Metrics.
_Avoid_: icon (that's one Surface), sparkline, gauge

**Surface**:
Where Meters appear: Tray Icons or the Taskbar Strip. Labeled "Taskbar display" in Settings. The Taskbar Strip is the default.
_Avoid_: view

**Tray Icons**:
The Surface where each Meter is its own notification-area icon.
_Avoid_: systray, menu-bar item

**Taskbar Strip**:
The Surface where all Meters sit side by side, docked inside the taskbar. When it is active, a single Menu Icon stays in the tray.
_Avoid_: deskband, toolbar, overlay

**Menu Icon**:
The single Tray Icon kept while the Taskbar Strip is attached. It carries the right-click menu and opens the Panel. It shows the app icon (default), the app icon colored by the Verdict, or one Section's Meter.
_Avoid_: tray button

**Panel**:
The detail window that opens from any Meter or the hotkey. It shows the Verdict, history graphs, Hop Traces, and the Process Snapshot.
_Avoid_: popup, dashboard, flyout

**Appearance**:
The light or dark color set every Surface and the Panel draw with. The user picks System (the default: follow the OS), Light or Dark in Settings. Labeled "Theme" in Settings.
_Avoid_: theme (except as the Settings label), mode, skin

**Pause**:
A stretch of time when blinkengraphs was not measuring: the app suspended or choosing to rest while the machine is idle, the machine asleep, the process killed or not yet started. It lasts until a settle time after measuring resumes, so Probes sent before the network is usable again are not counted. A Pause is not loss and not Offline (Offline is measured: no network path); History shows it as its own state.
_Avoid_: gap, sleep, downtime, outage

**History**:
Every Sample, Probe result and Hop statistic kept for later viewing: Raw for the recent past, Archives beyond it.
_Avoid_: log, timeline

**Raw**:
The results and Samples exactly as measured, kept for the last two hours. Short graph ranges draw from Raw.
_Avoid_: RAM, recent buffer, live data

**Archive**:
History at one fixed step: one Row per step for each Metric and Probe, and how much of each step was Paused, for a fixed span. Each long graph range draws from exactly one Archive.
_Avoid_: rollup, RRA, tier

**Row**:
The summary of one step of one Metric or Probe in an Archive: its count, losses, sum, min, max and a histogram for percentiles. Written once, when its step ends, and never changed.
_Avoid_: rollup, bucket, minute, consolidated data point

**Elevated Extras**:
Measurements that need privileges the app itself never has: bytes per process on the network, and UDP Hop Traces. Both come from an optional LocalSystem companion service.
_Avoid_: admin mode, pro features
