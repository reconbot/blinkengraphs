# Public Address

Every platform shows the Public Address for IPv4 and IPv6, found two independent ways. The hosts and refresh interval are `defaults.json` `public_address`. `vectors/public-address/*.json` is the authority for reading the answers: for each vector's `input`, an implementation produces the `expected` reading.

## Two lookups

| Lookup | How | Answer |
|---|---|---|
| DNS | TXT query for `whoami.cloudflare.com` sent straight to `ns3.cloudflare.com` over UDP | TXT records `remote_ip: <address>`, `asn: <number>`, `country_code: <code>` ([1.1.1.1 troubleshooting](https://developers.cloudflare.com/1.1.1.1/troubleshooting/)) |
| HTTPS | GET `https://checkip.amazonaws.com` | The address alone, then a newline |

Each runs twice, once per IP version, by sending to that version's address of the host.

## Parsing

- **DNS:** the TXT strings of the answer. `remote_ip: <address>` gives the address, `asn: <number>` the ASN; other strings are ignored.
- **HTTPS:** the body, trimmed of whitespace.

An answer that isn't a valid IPv4 or IPv6 address counts as no answer. Addresses compare as addresses, not text: `2001:db8::1` equals `2001:0db8:0:0:0:0:0:1`.

## Reading the answers

Per IP version, with the inputs `family` (`ipv4` or `ipv6`), `dns_txt` (the TXT strings, or null when the lookup failed) and `https_body` (or null), the reading is one `state`:

| State | When | Fields |
|---|---|---|
| `none` | Neither lookup answered | |
| `nat64` | `family` is `ipv6` and an answer is an IPv4 address | `address`: that IPv4 address |
| `agree` | Both answered with the same address | `address`, `asn` when DNS gave one |
| `differ` | Both answered, with different addresses | `dns`, `https`, `asn` when DNS gave one |
| `single` | Only one answered | `address`, `source` (`dns` or `https`), `asn` when DNS gave one |

States are checked in this order. Addresses in the output are written in their canonical text form ([RFC 5952](https://www.rfc-editor.org/rfc/rfc5952) for IPv6).

| State | Shown as |
|---|---|
| `agree` | The Public Address, with the ASN |
| `differ` | Both addresses, flagged: DNS and HTTPS leave by different paths. Causes: the network intercepts DNS, a split-tunnel VPN or proxy, or a carrier NAT pool that maps UDP and TCP to different addresses (harmless) |
| `nat64` | "IPv6-only network with NAT64" |
| `none` | "No IPv6 internet" or "No IPv4 internet" |
| `single` | The address, marked single-source |

None of these feed the Verdict: a DNS/HTTPS mismatch has a harmless carrier cause, so it is shown, not judged.

Refresh on start, when the Link changes, and every `refresh_s`.

## Evidence

A hosted macOS runner (`reconbot/blinkengraphs-ios`, Network diagnostics run 44975922516, 2026-11-22):

- Over IPv4, both lookups answered, in the formats above.
- Forced to IPv6, both answered with an IPv4 address. An earlier run could not reach Cloudflare's native IPv6 resolver, so the runner is likely an IPv6-only network with NAT64 (moderate confidence). Native IPv6 is untested.

`https://1.1.1.1/cdn-cgi/trace` also returns an `ip` line, but Cloudflare documents only its `colo` key, so it was dropped.

## Risk

Cloudflare documents `whoami.cloudflare.com` as a troubleshooting command, and AWS publishes `checkip.amazonaws.com` without a stated contract (unconfirmed). Either can change, which the second lookup covers: a response that doesn't parse is "unknown", never a Verdict input.
