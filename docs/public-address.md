# Proposal: Public Address

Show the Public Address for IPv4 and IPv6 on every platform, found two independent ways. This is a proposal: the lookup hosts and refresh interval land in `defaults.json` (`docs/sync.md`).

## Two lookups

| Lookup | How | Answer |
|---|---|---|
| DNS | TXT query for `whoami.cloudflare.com` sent straight to `ns3.cloudflare.com` over UDP | TXT records `remote_ip: <address>`, `asn: <number>`, `country_code: <code>` ([1.1.1.1 troubleshooting](https://developers.cloudflare.com/1.1.1.1/troubleshooting/)) |
| HTTPS | GET `https://checkip.amazonaws.com` | The address alone, then a newline |

Each runs twice, once per IP version, by sending to that version's address of the host.

## Reading the answers

| Observation | Shown as |
|---|---|
| Both lookups agree | The Public Address, with the DNS lookup's ASN |
| They differ | Both addresses, flagged: DNS and HTTPS leave by different paths. Causes: the network intercepts DNS, a split-tunnel VPN or proxy, or a carrier NAT pool that maps UDP and TCP to different addresses (harmless) |
| The IPv6 lookup answers with an IPv4 address | "IPv6-only network with NAT64" |
| No answer over IPv6 | "No IPv6 internet" |
| One lookup fails | The other's address, marked single-source |

None of these feed the Verdict. Open: whether a DNS/HTTPS mismatch earns a Finding, given the harmless carrier case.

Refresh on start, when the Followed Adapter or Access Point changes, and every `refresh_s` (proposed 300). Shown in plain text.

## Evidence

A hosted macOS runner (`reconbot/blinkengraphs-ios`, Network diagnostics run 44975922516, 2026-11-22):

- Over IPv4, both lookups answered, in the formats above.
- Forced to IPv6, both answered with an IPv4 address. An earlier run could not reach Cloudflare's native IPv6 resolver, so the runner is likely an IPv6-only network with NAT64 (moderate confidence). Native IPv6 is untested.

`https://1.1.1.1/cdn-cgi/trace` also returns an `ip` line, but Cloudflare documents only its `colo` key, so it was dropped.

## Risk

Cloudflare documents `whoami.cloudflare.com` as a troubleshooting command, and AWS publishes `checkip.amazonaws.com` without a stated contract (unconfirmed). Either can change, which the second lookup covers: a response that doesn't parse is "unknown", never a Verdict input.
