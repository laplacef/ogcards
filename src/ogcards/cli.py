"""Command-line interface: ``ogcards build | preview | init``."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from ogcards import cache as cache_mod
from ogcards.config import Theme, load_theme
from ogcards.errors import OgcardsError
from ogcards.manifest import Card, load_manifest
from ogcards.render import render_card

_SAMPLE_TOML = """\
[canvas]
width = 1200
height = 630
background = "#ffffff"

[templates.post]
title_size = 64
title_color = "#1a1a1a"
meta_size = 28
meta_color = "#535358"
accent = "#0645ad"
padding = 80
max_title_lines = 3
"""

_SAMPLE_MANIFEST = {
    "cards": [
        {
            "title": "Your Post Title Goes Here",
            "subtitle": "June 13, 2026",
            "template": "post",
            "out": "assets/og/posts/your-post.png",
        }
    ]
}


def _build(args: argparse.Namespace) -> int:
    theme = load_theme(Path(args.config))
    manifest = load_manifest(Path(args.manifest))
    out_dir = Path(args.out_dir)
    cache_path = out_dir / ".ogcards-cache.json"
    cache = {} if args.force else cache_mod.load_cache(cache_path)
    token = _theme_token(theme)

    rendered = skipped = 0
    for card in manifest.cards:
        template = theme.template(card.template)
        fp = cache_mod.fingerprint(card, template, token)
        dest = out_dir / card.out
        if not args.force and dest.is_file() and cache.get(card.out) == fp:
            skipped += 1
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        render_card(card, template, theme).save(dest, "PNG", optimize=True)
        cache[card.out] = fp
        rendered += 1
        if args.verbose:
            print(f"rendered {dest}")

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_mod.save_cache(cache_path, cache)
    print(f"ogcards: {rendered} rendered, {skipped} unchanged")
    return 0


def _preview(args: argparse.Namespace) -> int:
    theme = load_theme(Path(args.config)) if args.config else Theme()
    card = Card(
        title=args.title,
        out=args.out,
        subtitle=args.subtitle,
        kicker=args.kicker,
        footer=args.footer,
        label=args.label,
        template=args.template,
    )
    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    render_card(card, theme.template(card.template), theme).save(dest, "PNG", optimize=True)
    print(f"ogcards: wrote {dest}")
    return 0


def _init(args: argparse.Namespace) -> int:
    target = Path(args.dir)
    target.mkdir(parents=True, exist_ok=True)
    config = target / "ogcards.toml"
    manifest = target / "og-manifest.json"
    for path, contents in (
        (config, _SAMPLE_TOML),
        (manifest, json.dumps(_SAMPLE_MANIFEST, indent=2) + "\n"),
    ):
        if path.exists():
            print(f"ogcards: {path} exists, leaving it alone")
        else:
            path.write_text(contents, encoding="utf-8")
            print(f"ogcards: wrote {path}")
    return 0


def _theme_token(theme: Theme) -> str:
    return json.dumps(
        {"canvas": asdict(theme.canvas), "fonts": asdict(theme.fonts)},
        sort_keys=True,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ogcards",
        description="Build-time Open Graph card generator for any static site.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build", help="render every card in a manifest")
    build.add_argument("--config", required=True, help="path to ogcards.toml")
    build.add_argument("--manifest", required=True, help="path to og-manifest.json")
    build.add_argument("--out-dir", required=True, help="base directory for outputs")
    build.add_argument("--force", action="store_true", help="ignore the incremental cache")
    build.add_argument("-v", "--verbose", action="store_true", help="print each rendered path")
    build.set_defaults(func=_build)

    preview = sub.add_parser("preview", help="render a single card for design iteration")
    preview.add_argument("--title", required=True)
    preview.add_argument("--subtitle")
    preview.add_argument("--kicker", help="small tracked label above the title")
    preview.add_argument("--footer", help="footer text, bottom-left (e.g. name/domain)")
    preview.add_argument("--label", help="footer text, bottom-right (e.g. date)")
    preview.add_argument("--template", default="post")
    preview.add_argument("--config", help="optional ogcards.toml; omit for defaults")
    preview.add_argument("--out", default="card.png")
    preview.set_defaults(func=_preview)

    init = sub.add_parser("init", help="write a sample config and manifest")
    init.add_argument("--dir", default=".")
    init.set_defaults(func=_init)

    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except OgcardsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
