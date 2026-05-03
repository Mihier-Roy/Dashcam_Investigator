"""
WebPanel: a thin wrapper around QWebEngineView that renders a Jinja
template, attaches a shared QWebChannel, and serves assets via dci://.

The dci:// scheme handler is installed once on the default profile.
Each WebPanel reuses that handler. A single Bridge instance is shared
across all panels so JS sees one consistent `window.api`.
"""

from __future__ import annotations

import logging
from typing import Any

from PySide6.QtCore import QUrl
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEngineProfile
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget

from .bridge import Bridge
from .renderer import render
from .scheme import HOST, install_handler

logger = logging.getLogger(__name__)

_BASE_URL = QUrl(f"dci://{HOST}/")


class WebPanel(QWebEngineView):
    """A QWebEngineView that knows how to render Jinja templates."""

    def __init__(
        self,
        template_name: str,
        bridge: Bridge,
        *,
        parent: QWidget | None = None,
        context: dict[str, Any] | None = None,
        profile: QWebEngineProfile | None = None,
    ) -> None:
        super().__init__(parent)

        self._template_name = template_name
        self._bridge = bridge

        used_profile = profile or QWebEngineProfile.defaultProfile()
        install_handler(used_profile)

        channel = QWebChannel(self.page())
        channel.registerObject("bridge", bridge)
        self.page().setWebChannel(channel)

        self.set_context(context or {})

    def set_context(self, context: dict[str, Any]) -> None:
        """Re-render the template with a new context."""
        html = render(self._template_name, **context)
        self.setHtml(html, _BASE_URL)
