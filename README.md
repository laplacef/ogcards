# ogcards

Generate Open Graph cards for a static site at build time. Give it a JSON
manifest and a TOML theme, and it writes one PNG per card with Pillow. No
headless browser, no Node, no system libraries, just Pillow.

It's framework-agnostic, so any generator that can write a JSON file can drive it.

## Install

```sh
uv tool install ogcards
```

## Usage

```sh
ogcards init                # writes a sample ogcards.toml and og-manifest.json
ogcards build --config ogcards.toml --manifest og-manifest.json --out-dir _site
ogcards preview --title "Hello" --subtitle "June 2026" --out card.png
```

`build` is incremental, so a card re-renders only when its title, subtitle,
template, or theme changes. Pass `--force` to rebuild everything.

## Inputs

Two files. The theme (`ogcards.toml`) is your branding. The manifest
(`og-manifest.json`) is the per-build content your generator emits.

```toml
[canvas]
width = 1200
height = 630
background = "#ffffff"

[templates.post]
title_size = 64       # shrinks automatically past max_title_lines
title_color = "#1a1a1a"
meta_color = "#535358"
accent = "#0645ad"
padding = 80
max_title_lines = 3
```

```json
{
  "cards": [
    {
      "kicker": "Blog",
      "title": "Your Post Title",
      "subtitle": "An optional one-line description",
      "footer": "example.com",
      "label": "June 11, 2026",
      "out": "assets/og/posts/your-post.png"
    }
  ]
}
```

Only `title` and `out` are required. `kicker` is a small tracked label above the title; `footer` and `label` sit bottom-left and bottom-right under a rule. `out` is relative to `--out-dir`; `template` defaults to `post`. The theme also supports an inset panel (`[canvas]` `panel_background`/`panel_border`) and a serif title via the bundled `[fonts] title = "SourceSerif4Display-Bold.ttf"`.

## Static sites

Have your generator write `og-manifest.json` at build time, run `ogcards build`, 
then point each `og:image` at the `out` path. See [`examples/jekyll/`](examples/jekyll/) 
for a Jekyll manifest; the pattern is the same for Hugo or Eleventy.

## License

MIT. See [`LICENSE`](LICENSE).
