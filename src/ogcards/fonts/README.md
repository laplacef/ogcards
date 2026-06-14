# Bundled fonts

These ship with the package so cards render identically on every machine,
independent of system fonts.

- `Inter-Regular.ttf`, `Inter-Bold.ttf` — [Inter](https://github.com/rsms/inter)
  by Rasmus Andersson (SIL OFL 1.1); the default sans, used for meta text.
- `SourceSerif4Display-Bold.ttf` — [Source Serif 4](https://github.com/adobe-fonts/source-serif)
  by Adobe (SIL OFL 1.1); an optional serif for titles.
- `OFL.txt`, `SourceSerif4-OFL.txt` — the license texts, both listed in
  `pyproject.toml` `license-files` so they ship in the wheel.

The renderer prefers these over any system font (see `render.py: _resolve_font`).
A theme selects a bundled font by **bare filename** under `[fonts]` (e.g.
`title = "SourceSerif4Display-Bold.ttf"`), or overrides with an explicit path
(any value containing `/`). Default sans falls back to system DejaVu in dev.
