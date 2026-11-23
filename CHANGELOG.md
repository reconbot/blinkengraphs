# Changelog

## [5.3.0](https://github.com/reconbot/blinkengraphs/compare/v5.2.0...v5.3.0) (2026-11-22)


### Features

* the Verdict judges the Followed Adapter's Link, so a pinned adapter is the one it speaks for ([8407df8](https://github.com/reconbot/blinkengraphs/commit/8407df8dace551a50bd95aac04dcb8257faa19db))

## [5.2.0](https://github.com/reconbot/blinkengraphs/compare/v5.1.0...v5.2.0) (2026-11-22)


### Features

* a platform may depart from the spec for its normal use (ADR 0002) ([#48](https://github.com/reconbot/blinkengraphs/issues/48)) ([aca3c9f](https://github.com/reconbot/blinkengraphs/commit/aca3c9f5fcfbbd9c93a2bcc95afa1d1228085ab9))

## [5.1.0](https://github.com/reconbot/blinkengraphs/compare/v5.0.0...v5.1.0) (2026-11-22)


### Features

* name a Link by its IPv4 Gateway, else its IPv6 one, else its interface alone ([e5b8cec](https://github.com/reconbot/blinkengraphs/commit/e5b8cecd86c9a501125d1b675b1f6e0f56f0af71))

## [5.0.0](https://github.com/reconbot/blinkengraphs/compare/v4.0.0...v5.0.0) (2026-11-22)


### ⚠ BREAKING CHANGES

* every History vector is replaced, probe-stats vectors take now and raw_s, empty.json now expects no stats, and defaults.json history keys change.

### Features

* History is Raw plus fixed-step Archives; Pauses; stats from now; several Links ([14ba222](https://github.com/reconbot/blinkengraphs/commit/14ba22287e35c695a3b7821aa4fbba5725a6a158))

## [4.0.0](https://github.com/reconbot/blinkengraphs/compare/v3.0.0...v4.0.0) (2026-11-22)


### ⚠ BREAKING CHANGES

* isp-loss and vpn-isp-loss now expect 1.1.1.1 instead of 8.8.8.8. New vector isp-loss-tie covers the rounding.

### Features

* a tie for worst Internet Probe goes to the first in Probe Group order ([7b7fcfb](https://github.com/reconbot/blinkengraphs/commit/7b7fcfbda45cda58217637ed0f5f48e88704a570))


### Bug Fixes

* RAM serves every whole minute it holds; storage hands over where RAM ends ([872ba15](https://github.com/reconbot/blinkengraphs/commit/872ba15093b51ac051a752f29a06b89151779315))

## [3.0.0](https://github.com/reconbot/blinkengraphs/compare/v2.0.0...v3.0.0) (2026-11-22)


### ⚠ BREAKING CHANGES

* defaults.json public_address.https_url is replaced by https_url_ipv4 and https_url_ipv6. Platforms that read or override https_url must switch to the new keys.
* RTTs are recorded in whole milliseconds

### Features

* Public Address HTTPS lookup uses one icanhazip URL per IP version ([0809e05](https://github.com/reconbot/blinkengraphs/commit/0809e05ff13ca403376faaa939fe8d5fa83c268d)), closes [#34](https://github.com/reconbot/blinkengraphs/issues/34)
* RTTs are recorded in whole milliseconds ([cc20632](https://github.com/reconbot/blinkengraphs/commit/cc2063255cc5e0564a46dc1790faccb9190368df))

## [2.0.0](https://github.com/reconbot/blinkengraphs/compare/v1.7.0...v2.0.0) (2026-11-22)


### ⚠ BREAKING CHANGES

* history rules shared by every platform; one percentile rank; readouts default to p95

### Features

* history rules shared by every platform; one percentile rank; readouts default to p95 ([44758ff](https://github.com/reconbot/blinkengraphs/commit/44758ff5767d36a65ec32bcd21a00590c6823172))


### Bug Fixes

* a graph's seam is where written Minutes end, not the oldest RAM result ([6f7958e](https://github.com/reconbot/blinkengraphs/commit/6f7958e9f45d0b20be4bb0b33a3456ac23f8d8d9))

## [1.7.0](https://github.com/reconbot/blinkengraphs/compare/v1.6.0...v1.7.0) (2026-11-22)


### Features

* Appearance (System, Light or Dark) chosen in Settings; defaults.json appearance ([6636510](https://github.com/reconbot/blinkengraphs/commit/66365108a222282b46d8f925fac0d0b226ec053a))
* Captive Portal Finding and Public Address reading, with vectors; their hosts in defaults.json ([783e3be](https://github.com/reconbot/blinkengraphs/commit/783e3be399514e968bc2e95b800bbcd8b0c3e29a))
* graph aggregate defaults to p95 and is chosen in Settings ([d90e03d](https://github.com/reconbot/blinkengraphs/commit/d90e03d50f7443d07d4b8f49d48df502699663a7))
* Probe readouts show a chosen aggregate of their window, default p50; the Verdict keeps rtt_ms ([53b59f0](https://github.com/reconbot/blinkengraphs/commit/53b59f00178757520e63df15a73c7a6c4b77039c))

## [1.6.0](https://github.com/reconbot/blinkengraphs/compare/v1.5.0...v1.6.0) (2026-11-22)


### Features

* light palette in tokens; the spec authors all its files, no platform generates them ([8900e73](https://github.com/reconbot/blinkengraphs/commit/8900e735841db92cf8880f563eb0eefb71f80924))

## [1.5.0](https://github.com/reconbot/blinkengraphs/compare/v1.4.0...v1.5.0) (2026-11-22)


### Features

* run a Hop Trace only over an IP version the path carries natively ([509884e](https://github.com/reconbot/blinkengraphs/commit/509884e4ef9a67293a569f1587cd60e4ebac0a69))
* VPN Fault Domain; through a VPN the Verdict names the tunnel instead of the ISP or a ping filter ([74d1622](https://github.com/reconbot/blinkengraphs/commit/74d16226958ae99921a1d87c2dff115c4bdefd8e))

## [1.4.0](https://github.com/reconbot/blinkengraphs/compare/v1.3.0...v1.4.0) (2026-11-22)


### Features

* Hop names by reverse DNS, like mtr; hop_trace.reverse_dns default ([82291ff](https://github.com/reconbot/blinkengraphs/commit/82291ff99b443c5466b75c9e82375e6d0bd699ad))
* IPv6 Targets in the shared defaults; per-family Verdict rule; skip a family the path can't reach ([f886dfb](https://github.com/reconbot/blinkengraphs/commit/f886dfb72f621a110ea750ea3793af744e760bad))
* Offline Fault Domain; the Verdict reports it when no network path exists, and Probes pause ([d43be7e](https://github.com/reconbot/blinkengraphs/commit/d43be7e9f719968bc35aaa17a2e9dc4e11dfffd6))

## [1.3.0](https://github.com/reconbot/blinkengraphs/compare/v1.2.0...v1.3.0) (2026-11-22)


### Features

* shared app icon in brand/icon.svg that every platform renders from ([4fd7a02](https://github.com/reconbot/blinkengraphs/commit/4fd7a02513f2806bb1ea3f6286d1f2dba43c3c78))

## [1.2.0](https://github.com/reconbot/blinkengraphs/compare/v1.1.0...v1.2.0) (2026-11-22)


### Features

* defaults merge vector, generated by blinkengraphs-win ([8cb26c1](https://github.com/reconbot/blinkengraphs/commit/8cb26c1281a7157f3544e21035dfa3b8fbf3418b))
* shared defaults.json is hand-edited here and platforms merge their overrides over it; Quad9 replaces Google DNS ([90b0434](https://github.com/reconbot/blinkengraphs/commit/90b0434045b3c84c9f6616d9f6cc5420f64aa01b))

## [1.1.0](https://github.com/reconbot/blinkengraphs/compare/v1.0.0...v1.1.0) (2026-11-21)


### Features

* graph aggregate rule with a deterministic per-minute histogram and vectors ([81bb89c](https://github.com/reconbot/blinkengraphs/commit/81bb89c9e9105162910f097582b8375486dc7463))

## 1.0.0 (2026-11-21)


### Features

* probe-stats and hop-trace rules with vectors, denied Probes, defaults ([beb1966](https://github.com/reconbot/blinkengraphs/commit/beb1966f68c3c45e143d21fce33235fc929b9abf))
* shared spec — vocabulary, Verdict rules, test vectors, design tokens, landing README ([866a425](https://github.com/reconbot/blinkengraphs/commit/866a425beb46692b6f3a0b6a0c4938a0eaf05e2a))


### Continuous Integration

* release-please cuts tagged spec versions ([0362f13](https://github.com/reconbot/blinkengraphs/commit/0362f13c43d78f6f2972e404a97d4fa39b2c6cf5))
