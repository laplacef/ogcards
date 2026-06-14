# Changelog

This project adheres to [Common Changelog](https://common-changelog.org) and
[Semantic Versioning](https://semver.org).

## [0.2.0] - 2026-06-14

### Changed

- Redesign the `stack` layout: a tracked kicker, a vertically-centered title, and a footer rule with brand (left) and label (right)

### Added

- Add card `kicker`, `footer`, and `label` fields for a consistent header/footer across every card
- Add an optional inset panel (`[canvas]`: `panel_background`, `panel_border`, `panel_inset`, `panel_radius`)
- Bundle Source Serif 4 Display, and select a bundled font by bare filename in `[fonts]`

## [0.1.0] - 2026-06-14

_Initial release._

### Added

- Add `build`, `preview`, and `init` CLI commands
- Add a TOML theme with named templates and a JSON card manifest
- Add a Pillow `stack` layout with title auto-fit, wrapping, and ellipsis
- Add incremental rendering via a content-fingerprint cache
- Add custom layout registration through `ogcards.templates.register`
- Bundle the Inter typeface (SIL OFL 1.1) with a system-font fallback

[0.2.0]: https://github.com/laplacef/ogcards/releases/tag/v0.2.0
[0.1.0]: https://github.com/laplacef/ogcards/releases/tag/v0.1.0
