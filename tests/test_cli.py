from __future__ import annotations

from pathlib import Path

from ogcards.cli import main


def _write_inputs(tmp_path: Path) -> tuple[Path, Path, Path]:
    config = tmp_path / "ogcards.toml"
    config.write_text('[templates.post]\naccent = "#0645ad"\n')
    manifest = tmp_path / "og-manifest.json"
    manifest.write_text('{"cards":[{"title":"Hello","out":"og/a.png","subtitle":"June 2026"}]}')
    return config, manifest, tmp_path / "site"


def test_build_creates_output(tmp_path: Path) -> None:
    config, manifest, out = _write_inputs(tmp_path)
    rc = main(
        ["build", "--config", str(config), "--manifest", str(manifest), "--out-dir", str(out)]
    )
    assert rc == 0
    assert (out / "og/a.png").is_file()


def test_build_is_incremental(tmp_path: Path) -> None:
    config, manifest, out = _write_inputs(tmp_path)
    argv = ["build", "--config", str(config), "--manifest", str(manifest), "--out-dir", str(out)]
    main(argv)
    first = (out / "og/a.png").stat().st_mtime_ns
    main(argv)  # second run should skip the unchanged card
    assert (out / "og/a.png").stat().st_mtime_ns == first


def test_init_writes_samples(tmp_path: Path) -> None:
    rc = main(["init", "--dir", str(tmp_path)])
    assert rc == 0
    assert (tmp_path / "ogcards.toml").is_file()
    assert (tmp_path / "og-manifest.json").is_file()
