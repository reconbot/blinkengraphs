# Probe Group

A Probe Group is a table of Targets, one row each, with what to measure on it (`defaults.json` `probe_group.targets`). `vectors/probe-group/normalize.json` is the authority: normalizing each case's `targets` must produce `expected` exactly.

## Normalizing

Every platform normalizes a group when it loads one and before it saves one, so a hand-edited or older config can't measure a Target twice or send a Probe that can't work.

1. **Target text.** Trimmed and lowercased. An IP literal is written in its canonical form ([RFC 5952](https://www.rfc-editor.org/rfc/rfc5952) for IPv6), so `2606:4700:4700:0:0:0:0:1111` becomes `2606:4700:4700::1111`.
2. **One row per Target.** Rows with the same Target text merge into the first one, in its place: `icmp`, `dns` and `trace` are true when any row's is; `tcp` and `udp` take the first non-null port.
3. **`system-dns` measures DNS only.** It has no address, so `icmp` and `trace` become false and `tcp` and `udp` null.

A Target editor refuses a Target already in the group, naming the row that has it.

## The `system-dns` Probe

The `system-dns` DNS Probe measures the lookup an app's first visit to a site waits for: the configured resolver going upstream ([ADR 0004](../docs/adr/0004-system-dns-asks-a-random-name-under-microsoft-com.md)).

- Each Probe resolves `<label>.<system_dns_domain>` through the OS resolver, where `<label>` is 12 fresh random characters from `a`–`z` and `0`–`9`. A name never asked before misses every cache, so the resolver must ask the domain's name servers.
- Any answer is a reply, NXDOMAIN included. No answer before the Probe's timeout is a loss.

`system_dns_domain` must be a registered domain whose own name servers answer for it. A name under a domain that doesn't exist can be answered from cache once the parent is known missing ([RFC 8020](https://www.rfc-editor.org/rfc/rfc8020)). It also has:

- Name servers run by no operator of a default Probe Group resolver, so no resolver answers from its own zone.
- No DNSSEC, or compact denial, so a resolver can't synthesize NXDOMAIN from cached proofs ([RFC 8198](https://www.rfc-editor.org/rfc/rfc8198)).
- No wildcard record, so every random name gets NXDOMAIN.

Other DNS Probes send `dns_query_name` straight to their Target over UDP port 53, where a cached answer measures the path to that resolver.
