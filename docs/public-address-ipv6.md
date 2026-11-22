# Research: an HTTPS Public Address lookup that works over IPv6

Issue #34. Checked 2026-11-22. Not normative until it lands in `rules/public-address.md`.

## Question

`rules/public-address.md` runs the HTTPS lookup once per IP version against `defaults.json` `public_address.https_url`, `https://checkip.amazonaws.com`. That host has no AAAA record, so the IPv6 lookup connects only where DNS64/NAT64 synthesizes one, and then answers with an IPv4 address. Either switch to an endpoint with native IPv6 (option 1), or state that IPv6 HTTPS works only under NAT64 (option 2).

## Method

- A and AAAA queried at two resolvers, which agreed on every name: `https://cloudflare-dns.com/dns-query?name=<host>&type=<A|AAAA>` with `accept: application/dns-json`, and `https://dns.google/resolve?name=<host>&type=<A|AAAA>`.
- Bodies fetched with curl over IPv4, through an HTTPS proxy. The test container has no IPv6 route (`curl -6` exits 7), so **no IPv6 body was observed**; IPv6 formats below are assumed equal to IPv4.

## Findings

| Endpoint | A | AAAA | Body (IPv4) | Operator | Usage terms |
|---|---|---|---|---|---|
| `checkip.amazonaws.com` | yes, via CNAME `checkip.check-ip.aws.a2z.com` | **none** (CNAME target has no AAAA) | address, `\n`; `text/plain` | AWS (Amazon addresses) | None found on docs.aws.amazon.com (low confidence that none exists) |
| `icanhazip.com` | yes | yes, `2606:4700::/32` (Cloudflare) | address, `\n`; `text/plain`, `server: cloudflare` | Cloudflare since June 2021 ([Major Hayden, "A new future for icanhazip", 2021-06-06](https://major.io/p/a-new-future-for-icanhazip/): "the new owners and operators of icanhazip.com") | None published that I found; no Cloudflare page names the service (low confidence) |
| `ipv4.icanhazip.com` | yes | **none** | as above | Cloudflare | as above |
| `ipv6.icanhazip.com` | **none** | yes | untested | Cloudflare | as above |
| `api.ipify.org` | yes | none | address, no newline | Not stated; site credits Heroku and links [rdegges/ipify-api](https://github.com/rdegges/ipify-api) ([ipify.org](https://www.ipify.org/)) | "use it without limit"; footer © 2014–2019 ([ipify.org](https://www.ipify.org/)) |
| `api6.ipify.org` / `api64.ipify.org` | none / yes | yes / yes | api64: address, no newline | as above | as above; api6 "is used for IPv6 request only" |
| `ifconfig.co` | yes | yes | address, `\n` | Not stated; source [mpolden/echoip](https://github.com/mpolden/echoip) | Automated use "1 request per minute", may 429 or drop; v4/v6 subdomains no longer force a protocol ([ifconfig.co FAQ](https://ifconfig.co/)) |
| `ident.me`, `4.`/`v4.`, `6.`/`v6.ident.me` | yes, v4 names only | yes, v6 names only | address, no newline | One person, a VPS in Helsinki, "bus factor (one)" ([api.ident.me](https://api.ident.me/)) | "use this service for anything"; email first above 500 req/s ([api.ident.me](https://api.ident.me/)) |
| `ipv6.whatismyip.akamai.com` | none | yes | address, no newline, but `text/html` | Akamai (CNAME to `akamai.net`) | No documentation found (low confidence) |
| `domains.google.com/checkip` | | | 301 to `domains.google` | Google | Gone with Google Domains |
| `1.1.1.1/cdn-cgi/trace` | | | `key=value` lines incl. `ip=` (via `one.one.one.one`; the IP literal was refused by the test proxy) | Cloudflare | Docs say only "Note the `colo` field" ([troubleshooting](https://developers.cloudflare.com/support/troubleshooting/general-troubleshooting/gathering-information-for-troubleshooting-sites/#identify-the-cloudflare-data-center-serving-your-request), [cdn-cgi endpoint](https://developers.cloudflare.com/fundamentals/reference/cdn-cgi-endpoint/)). The rule's reason to drop it holds |

No Azure or Google first-party "what is my IP" HTTPS endpoint was found (low confidence: searched, not exhaustive).

The DNS half already has native IPv6: `ns3.cloudflare.com` has AAAA `2400:cb00:2049:1::a29f:21` and `…::a29f:7e2`, and Cloudflare documents the query (`nslookup -type=txt whoami.cloudflare.com ns3.cloudflare.com`, [1.1.1.1 troubleshooting](https://developers.cloudflare.com/1.1.1.1/troubleshooting/)). Whether it answers `remote_ip` with an IPv6 address over IPv6 is untested here.

## Pinning the address family

Not needed if each version gets its own single-stack hostname; recorded for completeness.

- **Windows:** `WINHTTP_OPTION_RESOLUTION_HOSTNAME`: "WinHttp will use the caller-provided string as the hostname for DNS resolution" ([option flags](https://learn.microsoft.com/en-us/windows/win32/winhttp/option-flags)). The page states no minimum Windows version, no address-family behaviour, and nothing about SNI or certificate names. The issue's "21H1+" and "keeps the hostname for SNI" are **unverified**.
- **Apple:** `NWProtocolIP.Options.version` is "a required IP version that disables all other versions for a connection", with cases `v4`, `v6`, `any` ([version](https://developer.apple.com/documentation/network/nwprotocolip/options/version-swift.property), [Version](https://developer.apple.com/documentation/network/nwprotocolip/options/version-swift.enum)). It applies to `NWConnection`, not `URLSession`; no `URLSession` equivalent found (low confidence). `requiredInterfaceType` picks an interface type, not a family ([requiredInterfaceType](https://developer.apple.com/documentation/network/nwparameters/requiredinterfacetype)).

## Recommendation

**Option 1, with one URL per version:** `https://ipv4.icanhazip.com` and `https://ipv6.icanhazip.com`.

- **Why icanhazip:** the only candidate with both families, a body identical to `checkip.amazonaws.com` (address then newline, so parsing is unchanged), and a large operator. It is as informal as checkip: no published terms or rate limit. ipify's operator and currency are unclear; ident.me is one person; ifconfig.co limits automated use to one request a minute.
- **Why split hostnames:** a single-stack name selects the family through DNS, so no platform needs WinHTTP or Network.framework pinning, and `URLSession` works as is. Under NAT64, `ipv4.icanhazip.com` gets a synthesized AAAA and still reports the public IPv4.
- **Operator diversity:** the DNS and HTTPS lookups would both be Cloudflare. The rule calls them "independent"; they stay independent in path (UDP to an authoritative server vs. TCP/TLS to an edge) but not in operator. Say so in the Risk section.

Changes:

- `rules/public-address.md`: the HTTPS row becomes "GET `https_url_ipv4` or `https_url_ipv6`"; replace "by sending to that version's address of the host" with: the DNS lookup sends to that version's address of `dns_server`, the HTTPS lookup uses that version's URL. Update Risk: icanhazip is Cloudflare-operated without a stated contract (cite the 2021 post).
- `defaults.json`: replace `public_address.https_url` with `https_url_ipv4: "https://ipv4.icanhazip.com"` and `https_url_ipv6: "https://ipv6.icanhazip.com"`.
- `vectors/public-address/`: no `expected` changes; the vectors take bodies, not URLs. Consider a vector for a body with no trailing newline, since fallbacks (ipify, ident.me) omit it; trimming already covers it.
- **Commit type:** by the CLAUDE.md test (a vector's `expected` changes) this is `feat:`, not `feat!:`. But renaming a `defaults.json` key breaks any platform that reads `https_url` or overrides it, so mark it `feat!:` anyway. Keeping `https_url` and adding only `https_url_ipv6` avoids the break but leaves one key family-ambiguous.

Option 2 would leave IPv6 single-source (DNS only) on every network with native IPv6, which is most dual-stack networks.

## Open questions

- **IPv6 bodies are untested** for icanhazip, ipify, ident.me. Confirm from a host with native IPv6 (a platform CI run) before landing.
- **The `nat64` state may become rare.** With AAAA on both hosts, an IPv6-only network with NAT64 reaches both natively and answers with its IPv6 address, so `nat64` fires only when a lookup is itself routed through NAT64. The Evidence section's runner got an IPv4 answer from DNS forced to IPv6, though `ns3.cloudflare.com` has AAAA; how that run "forced" IPv6 (synthesized `64:ff9b::/96` address, or something else) is unknown and should be checked before trusting the NAT64 reading of it.
- **No published terms** for icanhazip. Ask Cloudflare, or accept the same informal status checkip has today.
