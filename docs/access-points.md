# Proposal: Access Point diagnosis

A station's Wi-Fi Network can have many Access Points, some of them dead. blinkengraphs should say which Access Point is failing and, where the OS allows, let the user skip it. This is a proposal: no rule here is normative until it lands in `rules/` with vectors from blinkengraphs-win.

## Agreed behaviour

- **Attribution.** On Wi-Fi, every Probe result belongs to the Access Point that was joined when it was sent. The Panel shows Probe stats per Access Point of the current Wi-Fi Network.
- **Suggest, the user confirms.** When the joined Access Point is failing, the Verdict names it and offers "Avoid this Access Point". Nothing switches without the user.
- **Memory.** Avoided Access Points stay avoided until the user undoes it. Per-Access Point measurements age out with the rest of History.
- **Captive Portal** is a Fault Domain, so a sign-in page reads as itself and not as an ISP problem.

## Rules to write

Each goes to blinkengraphs-win first, then `rules/verdict.md` with vectors (`docs/sync.md`).

1. **Window.** The Verdict reads only results since the current Access Point was joined, so roaming doesn't blend a dead Access Point into a good one. Open: the minimum results before a Finding.
2. **Failing Access Point.** On Wi-Fi, when rule 1 or rule 3 of the Verdict would fire and another Access Point of the same Wi-Fi Network is in range or was measured fine: Crit `Lan` "Access Point {bssid} passes no traffic; {n} others on {network} in range". Open: whether this replaces rule 1/3 or precedes them.
3. **No address.** Joined to an Access Point but no Gateway, or a self-assigned address: Crit `Lan` "Joined {network} but got no address: DHCP problem".
4. **Captive Portal.** A plain-HTTP GET to `http://cp.cloudflare.com/generate_204` returns anything but 204 with an empty body, or the OS reports a captive network: Warn `CaptivePortal` "Sign-in page is blocking the internet". Evaluated before the ISP rules. It must be plain HTTP: a portal can intercept HTTP but cannot answer HTTPS without a certificate error. Verified: a hosted macOS runner got 204 with 0 bytes (`reconbot/blinkengraphs-ios` Network diagnostics run 44975922516). Open: which OS signal each platform reads; iOS needs an App Transport Security exception for that one host.

## What each platform can do

| | Identify the Access Point | Choose or avoid one |
|---|---|---|
| Windows | Native Wifi API reports the BSSID (unconfirmed) | `WlanConnect` takes a desired-BSSID list (unconfirmed) |
| macOS | CoreWLAN scan results carry `bssid` ([CWNetwork](https://developer.apple.com/documentation/corewlan/cwnetwork)) | `CWInterface.associate(to:password:)` joins a scanned network; whether it holds to that BSSID is unconfirmed ([CWInterface](https://developer.apple.com/documentation/corewlan/cwinterface)) |
| iOS | `NEHotspotNetwork.fetchCurrent` returns the BSSID with the paid-only Access Wi-Fi Information entitlement and precise Location ([fetchCurrent](https://developer.apple.com/documentation/networkextension/nehotspotnetwork/fetchcurrent(completionhandler:))) | No: configurations match by SSID or prefix only ([NEHotspotConfiguration](https://developer.apple.com/documentation/networkextension/nehotspotconfiguration)). iOS shows the Finding without the action |

## Privacy

A BSSID locates the user as precisely as GPS: iOS gates it behind precise Location for that reason. Access Point identifiers and their measurements stay on the device and never leave it in exports, logs or screenshots by default.
