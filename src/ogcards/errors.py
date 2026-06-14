"""Typed error hierarchy. Every failure surfaces as an OgcardsError subclass."""

from __future__ import annotations


class OgcardsError(Exception):
    """Base class for all ogcards errors."""


class ConfigError(OgcardsError):
    """The theme config is missing or invalid."""


class ManifestError(OgcardsError):
    """The card manifest is missing or invalid."""


class RenderError(OgcardsError):
    """A card could not be rendered (bad font, unknown layout, bad color)."""
