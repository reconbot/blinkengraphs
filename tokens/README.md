# Tokens

Colors and thresholds in [W3C design-token](https://www.designtokens.org/) format.

| File | Holds |
|---|---|
| `blinkengraphs.tokens.json` | Every token. Its colors are the dark appearance |
| `blinkengraphs.light.tokens.json` | The light appearance: colors only, at the same paths |

A platform that follows the system appearance reads the base file, then, in light appearance, replaces each color whose path the light file has. A path the light file lacks keeps its base value. Thresholds have no light variant.

The light palette keeps each hue and darkens it to stay legible on a light card; severity, loss and Section colors must stay distinguishable from each other in both appearances.
