# Brand

`icon.svg` is the app icon for every platform: a background-colored tile with three bars in the CPU, memory and network colors from `tokens/`. It is hand-edited here. Each platform renders its own formats from it at build time and does not commit renders or hand-draw its own:

| Platform | Renders |
|---|---|
| Windows | `.ico` (exe, shortcut, Apps & features), installer banner and dialog bitmaps |
| macOS | `.icns` / asset catalog |
| iOS | asset catalog app icon |

Changing the icon or a color it uses is a spec release; platforms pick it up when they bump their spec pin (`docs/sync.md`).
