# Hop Trace

A Hop Trace sends one Probe per TTL towards its Target every trace interval, in the style of mtr. `vectors/hop-trace/*.json` is the authority: feeding each vector's `ticks` in order must produce the `expected` hop table, to within 0.01.

## Sweeping

- A sweep sends TTL 1 up to `max_ttl` (30) in parallel and waits up to the Probe timeout.
- A reply from the Target itself marks that TTL `reached`. The path length is the lowest reached TTL.
- Once the path length is known, later sweeps stop at it. Every `full_sweep_every_s` (30) one sweep goes back to `max_ttl` in case the path grew.
- ICMP needs no privilege on any platform. TCP uses a TTL-limited connect and reads the ICMP error the OS reports. UDP needs raw sockets and is an Elevated Extra.

A Hop Trace runs only over an IP version the path carries natively. Through translation (464XLAT, NAT64) the routers before the translator can't answer: on an IPv6-only path the IPv4 trace shows nothing but its Target, so it is not run, and the IPv6 trace shows that path instead.

## Recording

Each result is `(ttl, addr, rtt_ms, reached)`, where `addr` is the router that answered and both it and `rtt_ms` are absent on a timeout.

- A hop keeps its last non-absent `addr`.
- A hop keeps its last `hop_window` (60) results.
- When a result is `reached`, rows with a higher TTL are deleted.

## Hop table

Per TTL, over that hop's kept results:

| Column | Definition |
|---|---|
| `sent` | Results kept |
| `loss` | `1 − replies / sent` |
| `last_ms` | The newest result's RTT, absent if it timed out |
| `best_ms`, `avg_ms`, `worst_ms` | Minimum, mean and maximum of the replies |

## Names

When `hop_trace.reverse_dns` is true (`defaults.json`), each Hop's address is looked up by reverse DNS (a PTR query) through the system resolver, as mtr does.

- Once per address, cached for the session, including addresses that have no name.
- Off the probing path: a lookup never delays a sweep or changes a hop's stats.
- The hop table shows the name, or the address while there is none; the address stays available beside it. Names are for display only and never feed the Verdict.
