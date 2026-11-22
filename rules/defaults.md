# Defaults

`defaults.json` holds the defaults every platform shares. Each platform embeds the pinned spec's copy at build time and merges its own `defaults.override.json` over it. `vectors/defaults/merge.json` is the authority: for each case, merging `override` over `base` must produce `expected` exactly.

## Merge

Merging an override value over a base value:

| Override | Result |
|---|---|
| An object, over an object | Each key merged recursively; keys absent from the override keep the base value |
| `null`, as an object member | That key is removed |
| Anything else | The override value, replacing the base whole. Arrays are replaced, not concatenated |

The override file's top level is an object; `{}` overrides nothing.

## Overrides

A platform may override any key. Each override carries its reason in that platform's ADRs, so a reader can tell a platform constraint from drift.
