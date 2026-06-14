# Bundled fonts

These ship with the package so cards render identically on every machine,
independent of system fonts.

- `Inter-Regular.ttf`, `Inter-Bold.ttf` — [Inter](https://github.com/rsms/inter)
  by Rasmus Andersson, under the SIL Open Font License 1.1.
- `OFL.txt` — the license text, also listed in `pyproject.toml` `license-files`
  so it ships in the wheel.

The renderer prefers these over any system font (see `render.py: _resolve_font`).
A theme can still override them with explicit paths under `[fonts]`. To swap the
default family, drop replacement `Inter-Regular.ttf` / `Inter-Bold.ttf` files
here and update this note and the license.
