"""
Tests for the dci:// URL scheme.

QtWebEngineCore requires a working OpenGL/EGL stack to import. On
headless CI/dev containers without libEGL the import itself fails, so
these tests skip cleanly rather than fail.
"""

from __future__ import annotations

import pytest

QtWebEngineCore = pytest.importorskip(
    "PySide6.QtWebEngineCore",
    reason="QtWebEngineCore not loadable (likely missing libEGL on this host)",
    exc_type=ImportError,
)

from dashcam_investigator.gui.web import scheme  # noqa: E402


def test_register_scheme_is_idempotent() -> None:
    scheme.register_scheme()
    scheme.register_scheme()  # second call must not raise
    assert scheme._registered is True


def test_guess_mime_uses_overrides(tmp_path) -> None:
    js_file = tmp_path / "x.js"
    js_file.write_text("// js")
    assert scheme._guess_mime(js_file) == "application/javascript"

    css_file = tmp_path / "x.css"
    css_file.write_text("/* css */")
    assert scheme._guess_mime(css_file) == "text/css"

    svg_file = tmp_path / "x.svg"
    svg_file.write_text("<svg/>")
    assert scheme._guess_mime(svg_file) == "image/svg+xml"


def test_scheme_constants_match_renderer_url_base() -> None:
    from dashcam_investigator.gui.web.renderer import static_url

    url = static_url("css/tokens.css")
    assert url.startswith(f"dci://{scheme.HOST}/")
    assert scheme.SCHEME_NAME == b"dci"
