# Proposal: Public Address

Show the Public Address for IPv4 and IPv6 on every platform. This is a proposal: the lookup host and refresh interval land in `defaults.json` through blinkengraphs-win (`docs/sync.md`).

## Lookup

One HTTPS GET per IP version, each pinned to that version by its literal address:

| Version | URL |
|---|---|
| IPv4 | `https://1.1.1.1/cdn-cgi/trace` |
| IPv6 | `https://[2606:4700:4700::1111]/cdn-cgi/trace` |

The response is `key=value` lines; the Public Address is the `ip` value. 1.1.1.1 is already a Target, so the lookup adds no new party.

- No answer over IPv6 means "no IPv6 internet", worth showing beside the IPv4 address.
- Refresh on start, when the Followed Adapter or Access Point changes, and every `refresh_s` (proposed 300).
- Shown in plain text. It feeds no Verdict rule.

## Evidence

A hosted macOS runner (`reconbot/blinkengraphs-ios`, Network diagnostics run 44975291720, 2026-11-22) got HTTP 200 with a valid certificate from the IPv4 URL, with keys `fl h ip ts visit_scheme uag colo sliver http loc tls sni warp gateway rbi kex`. The runner has no IPv6, so the IPv6 URL is untested.

## Risk

Cloudflare documents `/cdn-cgi/trace` only for finding the serving data center, and names only its `colo` key ([cdn-cgi endpoint](https://developers.cloudflare.com/fundamentals/reference/cdn-cgi-endpoint/)). The `ip` key and the endpoint on 1.1.1.1 are undocumented and could change. Platforms treat a response without `ip` as "unknown" and never as an error in the Verdict.

## Open

- Defaults keys and names, decided in blinkengraphs-win.
- Whether to also offer a documented fallback; the closest is a TXT query for `whoami.cloudflare.com` to `ns3.cloudflare.com`, itself documented as a diagnostic only ([1.1.1.1 troubleshooting](https://developers.cloudflare.com/1.1.1.1/troubleshooting/)).
