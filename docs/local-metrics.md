# Research: platform-neutral Local Metrics

Checked 2026-11-22. Decided in [ADR 0003](adr/0003-local-metrics-are-platform-neutral.md); the rules are in [`rules/verdict.md`](../rules/verdict.md#local-rules). Closes the research half of [`cross-platform.md`](cross-platform.md#spec-changes-needed-before-a-second-platform) item 1.

## Question

The Local rules (`rules/verdict.md`, "Local rules") name Windows counters: CPU total, commit charge, hard faults, disk active time and disk response time. For each one: what does Windows actually measure? What is the closest value an unsandboxed, unprivileged macOS 26 menu-bar app can read, and through which API? Does the threshold still mean the same thing? Where it doesn't, what should a neutral rule test instead?

## Method

- macOS: source at the macOS 26 tags. [xnu-12377.121.6](https://github.com/apple-oss-distributions/xnu/tree/xnu-12377.121.6), [IOStorageFamily-337.100.1](https://github.com/apple-oss-distributions/IOStorageFamily/tree/IOStorageFamily-337.100.1) and [system_cmds-1042.120.1](https://github.com/apple-oss-distributions/system_cmds/tree/system_cmds-1042.120.1) (`iostat`), plus Apple developer docs. Apple's own docs leave out Mach and BSD calls; Apple DTS names the Darwin source as the reference for them ([forum 723334](https://developer.apple.com/forums/thread/723334)). Nothing was run on a Mac. Every macOS behaviour below is read from source, not observed.
- Windows: Microsoft Learn, and how the reference implementation reads the counters. That is [`crates/collect/src/win/pdh.rs`](https://github.com/reconbot/blinkengraphs-win/blob/main/crates/collect/src/win/pdh.rs) L14–37, the conversions in [`calc.rs`](https://github.com/reconbot/blinkengraphs-win/blob/main/crates/collect/src/calc.rs) L23–30, and the rules in [`crates/verdict/src/lib.rs`](https://github.com/reconbot/blinkengraphs-win/blob/main/crates/verdict/src/lib.rs) `fn local`.
- Shorthand: `xnu:` means `https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.121.6/`, and `iosf:` means `https://github.com/apple-oss-distributions/IOStorageFamily/blob/IOStorageFamily-337.100.1/`.

## Summary

| Neutral name (proposal) | Windows source | macOS source (API) | Units | Threshold transfers? | Notes |
|---|---|---|---|---|---|
| `CpuBusy`, "CPU busy" (today `CpuTotal`) | PDH `\Processor(_Total)\% Processor Time` | `host_statistics(mach_host_self(), HOST_CPU_LOAD_INFO)`: `(user+system+nice) / all four` tick deltas | % of all logical CPUs | **Yes**, ≥ 90% | Same definition on both: 100 − idle share |
| `MemPressure`, "Memory pressure" (replaces `MemCommit`) | PDH `\Memory\% Committed Bytes In Use` = Committed Bytes ÷ Commit Limit | `sysctl kern.memorystatus_vm_pressure_level` (1/2/4), or `DISPATCH_SOURCE_TYPE_MEMORYPRESSURE` events | level: `normal` / `warn` / `critical` | **No.** macOS has no commit limit | Rule becomes "pressure is critical". Windows maps commit ≥ 90% to critical |
| `MemPageIns`, "Paging in" (replaces `MemHardFaults`) | PDH `\Memory\Pages Input/sec` | `host_statistics64(HOST_VM_INFO64)`: Δ(`pageins` + `swapins`) per second | pages/s today; **bytes/s proposed** | **Not as pages.** Apple silicon pages are 16 KiB, x64 pages are 4 KiB | 1000 pages/s on x64 ≈ 4 MB/s. Calibration on a Mac is unverified (low confidence) |
| `DiskBusy`, "Disk busy" (today `DiskActive`) | PDH `\PhysicalDisk(_Total)\% Idle Time`, reported as 100 − idle | IOKit `IOBlockStorageDriver` property `"Statistics"`: Δ(`Total Time (Read)` + `Total Time (Write)`) ÷ Δwall, capped at 100% | % | **Approximately.** macOS's figure is the mean number of requests in flight, which is ≥ busy share | On macOS the rule fires at least as often as on Windows (inferred) |
| `DiskResponse`, "Disk response" (unchanged) | PDH `\PhysicalDisk(_Total)\Avg. Disk sec/Transfer` × 1000 | Same dictionary: Δ`Total Time` ÷ Δ(`Operations (Read)` + `Operations (Write)`) | ms per request | **Yes**, ≥ 50 ms | Do **not** use the `Latency Time` keys. The base driver records 0 for them (see Disk) |

## CPU

**Windows.** `\Processor(_Total)\% Processor Time` "monitors the amount of time the CPU spends executing a thread that is not idle" ([Learn: Monitor CPU Usage](https://learn.microsoft.com/en-us/sql/relational-databases/performance-monitor/monitor-cpu-usage?view=sql-server-ver17)). The collector clamps it to 0–100 (`calc.rs` L30).

**macOS.**
- `host_statistics(mach_host_self(), HOST_CPU_LOAD_INFO, …)` returns `cpu_ticks[CPU_STATE_MAX]`, indexed USER, SYSTEM, IDLE and NICE ([`xnu:osfmk/mach/host_info.h` L193, L283–285](https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.121.6/osfmk/mach/host_info.h#L283-L285); [`xnu:osfmk/mach/machine.h` L74–79](https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.121.6/osfmk/mach/machine.h#L74-L79)).
- The kernel sums ticks over every processor ([`xnu:osfmk/kern/host.c` L516–541](https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.121.6/osfmk/kern/host.c#L516-L541)).
- Per core: `host_processor_info(…, PROCESSOR_CPU_LOAD_INFO, …)` ([`xnu:osfmk/mach/mach_host.defs` L137](https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.121.6/osfmk/mach/mach_host.defs#L137); [`processor_info.h` L114–116](https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.121.6/osfmk/mach/processor_info.h#L114-L116)).
- Busy % = (Δuser + Δsystem + Δnice) ÷ Δ(all four).

**Gotchas.**
- Ticks are 32-bit `natural_t`, so take deltas with wrapping subtraction.
- Third-party processes are rate-limited to between 2 and 10 calls per flavor per second. Past that limit they get cached data ([`host.c` L586–588, L778–781](https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.121.6/osfmk/kern/host.c#L586-L588)). Sampling at 1 Hz stays inside it.
- Both calls take the unprivileged `host_t`, not `host_priv_t`.

**Threshold.** It transfers. Both platforms measure the non-idle share averaged over all logical CPUs, so 90% means the same thing. Performance and efficiency cores count equally on macOS (inferred from the per-processor sum).

## Memory: commit charge becomes memory pressure

**Windows.**
- "The \Memory\% Committed Bytes In Use counter is a ratio of \Memory\Committed Bytes to \Memory\Commit Limit." The commit limit "is the sum of physical memory and all page files combined". When the charge reaches the limit, processes "might not get committed memory", which causes "freezing, crashing, and other malfunctions" ([Learn: Introduction to the page file](https://learn.microsoft.com/en-us/troubleshoot/windows-client/performance/introduction-to-the-page-file)).
- The same page says system-managed page files grow "when the system commit charge reaches 90 percent of the system commit limit". So on default settings, commit ≥ 90% can be brief: the limit rises a moment later. This does not change the rule, but explains flicker.

**macOS has no commit limit.**
- Anonymous memory is compressed, then swapped to files created on demand: up to 100 files of up to 1 GiB on macOS ([`xnu:osfmk/vm/vm_compressor_backing_store.c` L173–175](https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.121.6/osfmk/vm/vm_compressor_backing_store.c#L173-L175); [`vm_compressor_backing_store_internal.h` L52–56](https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.121.6/osfmk/vm/vm_compressor_backing_store_internal.h#L52-L56)). Free disk space also bounds this (inferred, low confidence).
- `vm.swapusage` (`struct xsw_usage`) reports current swap total and used, readable without privilege ([`xnu:bsd/kern/kern_sysctl.c` L4233–4235](https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.121.6/bsd/kern/kern_sysctl.c#L4233-L4235)). Its total grows as files are added, so a "used ÷ total" ratio is not a ceiling. No macOS value is a counterpart of commit %.

**What macOS offers instead: the kernel's memory-pressure level.**
- `sysctl kern.memorystatus_vm_pressure_level`:
  - It is readable without privilege on macOS. The `priv_check_cred` call is compiled only for `!XNU_TARGET_OS_OSX`.
  - It is `CTLFLAG_MASKED`, so it is hidden from listings but readable by name ([`xnu:bsd/kern/kern_memorystatus_notify.c` L1885–1910](https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.121.6/bsd/kern/kern_memorystatus_notify.c#L1885-L1910)).
  - It returns 1 (normal), 2 (warn: the internal Warning and Urgent states) or 4 (critical) ([L1776–1805](https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.121.6/bsd/kern/kern_memorystatus_notify.c#L1776-L1805); [`event_private.h` L301–303](https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.121.6/bsd/sys/event_private.h#L301-L303)).
  - The sysctl is undocumented and its constants are in a private header, so its stability is not guaranteed (low confidence that it lasts).
- The public, documented route gives the same three states:
  - `DispatchSource.makeMemoryPressureSource` / `DISPATCH_SOURCE_TYPE_MEMORYPRESSURE`, with `DISPATCH_MEMORYPRESSURE_NORMAL`, `_WARN` and `_CRITICAL` ([Apple: DISPATCH_SOURCE_TYPE_MEMORYPRESSURE](https://developer.apple.com/documentation/dispatch/dispatch_source_type_memorypressure); [DISPATCH_MEMORYPRESSURE_CRITICAL](https://developer.apple.com/documentation/dispatch/dispatch_memorypressure_critical): "The system memory pressure condition is at the critical stage").
  - It delivers events rather than a value to poll. Read the sysctl once at launch, then track events (proposal).
- How the kernel decides the level, with the compressor active (the macOS default):
  - Warn when `active + inactive + free + speculative` pages drop below the compressor's compaction threshold.
  - Critical when the compressor is nearly out of segments or compressed pages, or when those pages drop below 1.2 × the swap-unthrottle threshold.
  - Hysteresis is 1.2× going back to normal and 1.4× going back to warn.
  - Sources: [`xnu:osfmk/vm/vm_pageout.c` L10750–10817](https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.121.6/osfmk/vm/vm_pageout.c#L10750-L10817); [`vm_page.h` L1705–1706](https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.121.6/osfmk/vm/vm_page.h#L1705-L1706); [`vm_compressor_xnu.h` L418–421](https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.121.6/osfmk/vm/vm_compressor_xnu.h#L418-L421); [`vm_compressor.c` L573–577](https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.121.6/osfmk/vm/vm_compressor.c#L573-L577).
  - Each threshold depends on kernel tunables whose release values were not traced (low confidence on exact percentages).
- `kern.memorystatus_level` gives available memory as a whole-number percentage of RAM ([`vm_pageout.c` L5283](https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.121.6/osfmk/vm/vm_pageout.c#L5283); [`kern_memorystatus.c` L891](https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.121.6/bsd/kern/kern_memorystatus.c#L891)). It could feed a Meter, but it is not the Verdict's test.

**Threshold.** It does not transfer. A neutral rule should test a level, not a percentage:

| Condition | Finding |
|---|---|
| Memory pressure is critical | Crit `LocalLoad` "Memory nearly exhausted" (+ platform detail, e.g. "commit 93%") |

Windows sets `MemPressure` = critical when commit ≥ 90%, which keeps today's behaviour. macOS sets it from the kernel level. Whether Windows reports `warn` (for example at commit ≥ 80%, the "critical" band in [Learn: Troubleshoot performance problems](https://learn.microsoft.com/en-us/troubleshoot/windows-server/performance/troubleshoot-performance-problems-in-windows)) only matters if a rule ever uses `warn`.

## Paging: hard faults become pages read in

**Windows.**
- The collector's "hard faults" are `\Memory\Pages Input/sec` (`pdh.rs` L19), not `\Memory\Page Faults/sec`.
- Pages Input/sec "is the rate at which pages are read from disk to resolve hard page faults". It counts pages, while Page Reads/sec counts read operations ([Microsoft Q&A 273520](https://learn.microsoft.com/en-gb/answers/questions/273520/page-reads-sec-vs-pages-input-sec); moderate confidence, since it is a forum answer quoting the counter's explain text).
- Pages/sec is the sum of Pages Input/sec and Pages Output/sec ([Learn: BizTalk system-level bottlenecks](https://learn.microsoft.com/en-us/biztalk/technical-guides/system-level-bottlenecks)).
- So the UI label "hard faults/s" is really pages read in per second.

**macOS.**
- `host_statistics64(mach_host_self(), HOST_VM_INFO64, …)` returns `vm_statistics64` ([`xnu:osfmk/mach/vm_statistics.h` L142–176](https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.121.6/osfmk/mach/vm_statistics.h#L142-L176)).
- Two lifetime counters together cover what Windows counts:
  - `pageins` counts pages brought in from a pager, file-backed or mapped, to satisfy a fault. It skips plain file I/O (`!(cntrl_flags & UPL_FILE_IO)`) ([`vm_pageout.c` L7138–7141](https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.121.6/osfmk/vm/vm_pageout.c#L7138-L7141)).
  - `swapins` counts pages read back from swap files into the compressor ([`vm_compressor_backing_store.c` L1739, L2327](https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.121.6/osfmk/vm/vm_compressor_backing_store.c#L1739)).
- `decompressions` are faults served from RAM with no disk read, so they are soft and excluded (inferred: the counter increments in `vm_fault.c` with no I/O, [L244](https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.121.6/osfmk/vm/vm_fault.c#L244)).
- Rate = Δ(`pageins` + `swapins`) ÷ Δt, in pages per second. Multiply by `vm_page_size` for bytes.
- `swapins` adds a whole compressor segment's pages at once, so it arrives in bursts. Average it over the window, not per tick (inferred).

**Units differ.**
- Apple says page sizes differ on Apple silicon and code should read `vm_page_size` ([Apple: Addressing architectural differences](https://developer.apple.com/documentation/apple-silicon/addressing-architectural-differences-in-your-macos-code)).
- XNU's arm64 maximum is 16 KiB ([`xnu:osfmk/mach/arm/vm_param.h` L100–101](https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.121.6/osfmk/mach/arm/vm_param.h#L100-L101)).
- Windows x64 uses 4 KiB pages. That value is reported by `SYSTEM_INFO.dwPageSize` ([Learn: SYSTEM_INFO](https://learn.microsoft.com/en-us/windows/win32/api/sysinfoapi/ns-sysinfoapi-system_info)); the 4 KiB figure is not stated on that page (low confidence on the cited value, high on the fact).
- So 1000 pages/s is about 4 MB/s on Windows x64 and about 16 MB/s on Apple silicon.

**Threshold.** It transfers only once units match. Proposal: name it `MemPageIns` in **bytes/s** and set the threshold to 4 096 000 B/s (≈ 1000 x64 pages/s). The Windows result is unchanged, and the "Otherwise" clause keys off `MemPressure` ≠ critical. Whether 4 MB/s of page-ins means trouble on an SSD Mac is unverified. macOS reads executables in through `pageins` at app launch, so launch bursts may trip it (low confidence; needs a trace on hardware).

## Disk

**Windows.**
- `DiskActive` = 100 − `\PhysicalDisk(_Total)\% Idle Time` (`pdh.rs` L20, `calc.rs` L28). % Idle Time is the "percentage of time during the sample interval that the disk was idle".
- `DiskResponse` = `Avg. Disk sec/Transfer` × 1000. That counter is the "time, in seconds, of the average disk transfer".
- Both definitions: [Learn: Win32_PerfFormattedData_PerfDisk_PhysicalDisk](https://learn.microsoft.com/en-us/previous-versions/aa394262(v=vs.85)).
- How `_Total` combines several disks for a % counter (average or sum) was not confirmed (low confidence).
- `diskperf -n` can switch disk counters off, and they then read 0 (`pdh.rs` L68).

**macOS.**
- Each `IOBlockStorageDriver` publishes a `"Statistics"` dictionary (`kIOBlockStorageDriverStatisticsKey`) with these lifetime counters:
  - `Operations (Read|Write)`
  - `Bytes (Read|Write)`
  - `Total Time (Read|Write)`: "nanoseconds spent performing reads/writes"
  - `Latency Time (Read|Write)`
  - `Errors` and `Retries`
  - Source: [`iosf:IOBlockStorageDriver.h` L54–222](https://github.com/apple-oss-distributions/IOStorageFamily/blob/IOStorageFamily-337.100.1/IOBlockStorageDriver.h#L54-L222).
- These are SDK constants, which is what Apple DTS advises relying on ([forum 770333](https://developer.apple.com/forums/thread/770333)).
- Read them with `IOServiceGetMatchingServices(kIOMainPortDefault, IOServiceMatching("IOBlockStorageDriver"), …)` and `IORegistryEntryCreateCFProperties` ([Apple: IOKitLib](https://developer.apple.com/documentation/iokit/iokitlib_h)). This reads registry properties only and opens no user client, so it needs no entitlement when unsandboxed (inferred, not tested). Apple's `iostat` reads the same keys this way ([`system_cmds iostat.c` L605–658](https://github.com/apple-oss-distributions/system_cmds/blob/system_cmds-1042.120.1/iostat/iostat.c#L605-L658)).

**What `Total Time` measures.**
- Per request, the clock starts in `prepareRequest`, before deblocking and splitting ([`iosf:IOBlockStorageDriver.cpp` L3558](https://github.com/apple-oss-distributions/IOStorageFamily/blob/IOStorageFamily-337.100.1/IOBlockStorageDriver.cpp#L3558)).
- It stops at completion and is added to the counters ([L744–752, L552–576](https://github.com/apple-oss-distributions/IOStorageFamily/blob/IOStorageFamily-337.100.1/IOBlockStorageDriver.cpp#L744-L752)).
- Consequences (inferred from the code):
  - **Response:** Δ`Total Time` ÷ Δ`Operations` is the mean time per request, the same thing as `Avg. Disk sec/Transfer`. 50 ms transfers.
  - **Busy:** overlapping requests are summed, so Δ`Total Time` ÷ Δwall is the mean number of requests in flight (Little's law). That is closer to `Avg. Disk Queue Length` than to busy time, and it can exceed 1 on NVMe. Busy share ≤ mean in flight, so a capped value of 100% or more means "never idle or queued", and ≥ 90% fires at least whenever Windows' busy ≥ 90% would. No macOS counter gives true idle time.
- **`Latency Time` is 0.** The base class passes `latentTime = 0` ([L752](https://github.com/apple-oss-distributions/IOStorageFamily/blob/IOStorageFamily-337.100.1/IOBlockStorageDriver.cpp#L752)). Yet `iostat` builds its `msps` from those keys ([`iostat.c` L648–658, L688–691](https://github.com/apple-oss-distributions/system_cmds/blob/system_cmds-1042.120.1/iostat/iostat.c#L648-L691)). `addToBytesTransferred` is virtual, so a subclass might report real latency. That was not checked (low confidence). Use `Total Time`.

**Threshold.** Response transfers. Busy transfers as a gate, and macOS fires more readily. A neutral alternative that avoids "busy" altogether is "response ≥ 50 ms while requests are in flight ≥ 0.9". Windows could compute it from `Avg. Disk Queue Length`, but that changes the Windows rule.

## Vectors that carry these fields

- `sample` keys in `vectors/verdict`: `CpuTotal`, `CpuKernel`, `CpuQueue`, `MemCommit`, `MemPhysical`, `MemHardFaults`, `DiskActive`, `DiskRead`, `DiskWrite`, `DiskResponse`, `DiskQueue`, `NetDown`, `NetUp`, `NetErrors`. The Local rules read only `CpuTotal`, `MemCommit`, `MemHardFaults`, `DiskActive` and `DiskResponse`.
- Vectors with a `sample`: `cpu-pinned`, `resuming-local-load`, `idle`, `isp-loss`, `resumed-with-stats`, `upload-saturation`. Only the first two expect `LocalLoad` Findings: "CPU pinned at 96%" and "Paging heavily: 1400 hard faults/s". Renaming `MemHardFaults` to bytes/s changes that headline and its `expected`, which makes it `feat!:`.
- **No vector exercises** the commit rule, the disk rule, or the "Otherwise" suppression of paging under commit ≥ 90%.
- `vectors/meters` and `vectors/history` carry none of these fields. `fixtures/scenarios` use Section series (`cpu`, `memory`, `disk`) and need no rename.

## Decisions

The owner answered the open questions on 2026-11-22; [ADR 0003](adr/0003-local-metrics-are-platform-neutral.md) records them.

1. Vectors carry `MemPressure` only.
2. The memory headline is fixed: "Memory nearly exhausted".
3. Paging is in bytes/s; the threshold is 4 096 000 B/s.
4. Disk busy keeps its definition; a platform without an idle counter uses mean requests in flight, capped at 100%.
5. The disk rule tests each disk; the busiest qualifying one is named.
6. `MemPressure` `warn` raises no Finding.

Still unverified: whether 4 MB/s of page-ins means trouble on an SSD Mac. Trace it on hardware before trusting the paging Finding there.
