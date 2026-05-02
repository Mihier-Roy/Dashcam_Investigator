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
    rel = rel.lstrip("/")
    return f"{base.rstrip('/')}/{rel}"


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
    env.globals["app"] = True  # overridden to False when rendering the report
    return env


def get_env() -> Environment:
    return _build_env()


def render(template_name: str, **context: object) -> str:
    """Render a template by name. Context overrides any global of the same key."""
    env = get_env()
    template = env.get_template(template_name)
    return template.render(**context)
