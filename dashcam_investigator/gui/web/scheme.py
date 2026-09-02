"""
Custom URL scheme `dci://` that serves files from gui/assets/.

Registering a scheme with predictable security/CORS rules avoids the
`file://` quirks that bite QWebEngineView when templates load relative
assets. All in-app pages use `dci://app/<path under gui/assets>`.

Two-step usage:

    # Before QApplication:
    from dashcam_investigator.gui.web.scheme import register_scheme
    register_scheme()

    # After QApplication is running, install the handler on a profile:
    from dashcam_investigator.gui.web.scheme import install_handler
    install_handler(QWebEngineProfile.defaultProfile())
"""

from __future__ import annotations

import logging
import mimetypes
from pathlib import Path

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QMimeDatabase, QUrl
from PySide6.QtWebEngineCore import (
    QWebEngineProfile,
    QWebEngineUrlRequestJob,
    QWebEngineUrlScheme,
    QWebEngineUrlSchemeHandler,
)

from .renderer import assets_path

logger = logging.getLogger(__name__)

SCHEME_NAME = b"dci"
HOST = "app"

_registered = False
_handler: "DciSchemeHandler | None" = None


def register_scheme() -> None:
    """Register the dci:// scheme. MUST be called before QApplication is created."""
    global _registered
    if _registered:
        return

    scheme = QWebEngineUrlScheme(SCHEME_NAME)
    scheme.setSyntax(QWebEngineUrlScheme.Syntax.Host)
    scheme.setDefaultPort(QWebEngineUrlScheme.SpecialPort.PortUnspecified.value)
    scheme.setFlags(
        QWebEngineUrlScheme.Flag.SecureScheme
        | QWebEngineUrlScheme.Flag.LocalAccessAllowed
        | QWebEngineUrlScheme.Flag.CorsEnabled
    )
    # Deliberately NOT QWebEngineUrlScheme.Flag.LocalScheme: that flag
    # mirrors file://'s cross-origin restrictions, which blocks the
    # embedded folium/Altair output (loaded via <iframe srcdoc> on a
    # dci:// page) from fetching its CDN-hosted JS (Leaflet, jQuery,
    # Vega) -- the map/speed-graph panels render blank with
    # "X is not defined" console errors otherwise.
    QWebEngineUrlScheme.registerScheme(scheme)
    _registered = True
    logger.debug("Registered dci:// URL scheme")


def install_handler(profile: QWebEngineProfile) -> "DciSchemeHandler":
    """Install (or reuse) the scheme handler on the given QWebEngineProfile."""
    global _handler
    if _handler is None:
        _handler = DciSchemeHandler()
    profile.installUrlSchemeHandler(SCHEME_NAME, _handler)
    return _handler


class DciSchemeHandler(QWebEngineUrlSchemeHandler):
    """Resolves dci://app/<rel> to gui/assets/<rel>."""

    def requestStarted(
        self, job: QWebEngineUrlRequestJob
    ) -> None:  # noqa: N802 (Qt API)
        url: QUrl = job.requestUrl()
        if url.host() != HOST:
            logger.warning("dci:// request rejected: bad host %r", url.host())
            job.fail(QWebEngineUrlRequestJob.Error.UrlNotFound)
            return

        rel = url.path().lstrip("/")
        if not rel:
            job.fail(QWebEngineUrlRequestJob.Error.UrlNotFound)
            return

        target = (assets_path() / rel).resolve()
        try:
            target.relative_to(assets_path().resolve())
        except ValueError:
            logger.warning("dci:// request rejected: path escape %r", rel)
            job.fail(QWebEngineUrlRequestJob.Error.UrlInvalid)
            return

        if not target.is_file():
            logger.debug("dci:// 404 for %s -> %s", rel, target)
            job.fail(QWebEngineUrlRequestJob.Error.UrlNotFound)
            return

        data = target.read_bytes()
        mime = _guess_mime(target)

        buf = QBuffer(parent=job)
        buf.setData(QByteArray(data))
        buf.open(QIODevice.OpenModeFlag.ReadOnly)
        job.reply(mime.encode("ascii"), buf)


def _guess_mime(path: Path) -> str:
    suffix = path.suffix.lower()
    overrides = {
        ".js": "application/javascript",
        ".mjs": "application/javascript",
        ".css": "text/css",
        ".html": "text/html",
        ".svg": "image/svg+xml",
        ".json": "application/json",
        ".woff2": "font/woff2",
        ".woff": "font/woff",
    }
    if suffix in overrides:
        return overrides[suffix]

    guess, _ = mimetypes.guess_type(str(path))
    if guess:
        return guess

    db_guess = QMimeDatabase().mimeTypeForFile(str(path)).name()
    return db_guess or "application/octet-stream"
