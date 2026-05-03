"""
Jinja2 environment + asset path resolution.

Used both by the in-app WebPanel and by core.generate_report so the live
UI and the exported HTML report share one set of templates.

`assets_path()` resolves to the source tree in dev and to the bundle in
PyInstaller-frozen builds. All other helpers go through it.
"""

from __future__ import annotations

import logging
import sys
from functools import lru_cache
from pathlib import Path

from jinja2 import ChoiceLoader, Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

logger = logging.getLogger(__name__)

ASSETS_DIRNAME = "gui/assets"


@lru_cache(maxsize=1)
def assets_path() -> Path:
    """Return the absolute path to gui/assets in dev or frozen builds."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        bundle_root = Path(sys._MEIPASS)  # type: ignore[attr-defined]
        candidate = bundle_root / "dashcam_investigator" / ASSETS_DIRNAME
        if candidate.is_dir():
            return candidate
        # Fall back to flat layout (some PyInstaller specs strip the package prefix).
        flat = bundle_root / ASSETS_DIRNAME
        if flat.is_dir():
            return flat

    # Dev: this file lives at gui/web/renderer.py, assets at gui/assets.
    return (Path(__file__).resolve().parent.parent / "assets").resolve()


def templates_path() -> Path:
    return assets_path() / "templates"


def static_path() -> Path:
    return assets_path() / "static"


def qss_path() -> Path:
    return assets_path() / "qss"


def static_url(rel: str, base: str = "dci://app/static/") -> str:
    """Build a URL pointing at a static asset. Default base uses the dci:// scheme."""
    rel = lstrip_url(rel)
    return f"{base.rstrip('/')}/{rel}"


def lstrip_url(rel: str) -> str:
    return rel.lstrip("/")


@lru_cache(maxsize=128)
def _read_icon(name: str) -> str:
    """Read an SVG file from static/icons/. Cached because icons are small and reused."""
    path = static_path() / "icons" / f"{name}.svg"
    if not path.is_file():
        logger.warning("Icon not found: %s", path)
        return ""
    return path.read_text()


def inline_svg(name: str, cls: str = "icon") -> Markup:
    """Return an inline <svg> for the named icon, ready to drop into HTML.

    The class attribute on the SVG is replaced with `cls` so callers can
    size or recolor without overriding the file. Markup() prevents
    autoescaping.
    """
    svg = _read_icon(name)
    if not svg:
        return Markup("")
    if 'class="icon"' in svg:
        svg = svg.replace('class="icon"', f'class="{cls}"', 1)
    return Markup(svg)


@lru_cache(maxsize=16)
def _read_static(rel: str) -> str:
    """Read a file from gui/assets/static/. Cached: assets are small + reused."""
    path = static_path() / rel
    if not path.is_file():
        logger.warning("Static asset missing: %s", path)
        return ""
    return path.read_text()


def inline_css(rel: str) -> Markup:
    """Return the contents of a CSS file from static/, ready for a <style> tag."""
    return Markup(_read_static(rel))


@lru_cache(maxsize=1)
def _build_env() -> Environment:
    loader = ChoiceLoader([FileSystemLoader(str(templates_path()))])
    env = Environment(
        loader=loader,
        autoescape=select_autoescape(("html", "xml")),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    env.globals["static"] = static_url
    env.globals["inline_svg"] = inline_svg
    env.globals["inline_css"] = inline_css
    env.globals["app"] = True  # overridden to False when rendering the report
    return env


def get_env() -> Environment:
    return _build_env()


def render(template_name: str, **context: object) -> str:
    """Render a template by name. Context overrides any global of the same key."""
    env = get_env()
    template = env.get_template(template_name)
    return template.render(**context)
