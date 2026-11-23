# The `system-dns` Probe asks the OS resolver for a random name under microsoft.com

iOS has no public API for the configured resolver's address, so its `system-dns` Probe asked the OS resolver for a fresh random name under `dns_query_name` (iOS ADR 0008), while Windows sent `dns_query_name` straight to the adapter's resolver. On one network, iOS read 110 ms where a direct query to the same resolver read 13 ms, so iOS alone crossed the Verdict's 250 ms "slow" line on busy networks. Every platform now does what iOS did, under a domain chosen for it: `system_dns_domain`, `microsoft.com`.

- **Random names, for `system-dns` only.** It is the one Probe whose resolver the user may not choose, and the lookup an app's first visit waits for is what "Your DNS server is slow" means. Other DNS Probes keep a cached query, which isolates the path to their resolver.
- **A domain that exists.** Under a missing parent, resolvers answer every later name from cache (RFC 8020), measuring the cache.
- **Not `cloudflare.com`.** 1.1.1.1 is a default resolver and answers names in Cloudflare's zone in-house, which would favour it. `microsoft.com` is on Azure DNS, unsigned, with no wildcard (checked 2026-11-23).

## Considered options

- **Random names on every DNS Probe.** Rejected: each reading would include the test domain's name servers, so a slow one would blame every resolver.
- **A direct cached query to the configured resolver everywhere.** Rejected: iOS can't find the address, and the cached answer hides the upstream lookup users wait for.
- **`msftncsi.com`.** Rejected: networks that intercept Windows' connectivity check may answer it locally.
- **A project-owned zone.** Not chosen: none exists; `microsoft.com` absorbs the queries without notice. Revisit if Microsoft's DNS starts rate-limiting them.
