"""
Self-serve documentation portal for this generated API.

Serves a landing page (``/portal``) with sidebar navigation that links every live endpoint —
Swagger (/docs), ReDoc (/redoc), GraphQL (/graphql), health (/health) — renders the data model
and per-model API guide, and exposes the raw README / API reference. Mounted by ``main.py`` via
``mount(app)``; opens in your browser on startup in development (set ``OPEN_BROWSER=0`` to skip).
"""

from __future__ import annotations

import logging
import os
import threading
import webbrowser
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, PlainTextResponse

logger = logging.getLogger(__name__)
router = APIRouter()

_BASE = Path(__file__).resolve().parent
_PORTAL_HTML = _BASE / "docs" / "portal.html"
_README = _BASE / "README.md"
_API_MD = _BASE / "docs" / "API.md"


@router.get("/portal", include_in_schema=False, response_class=HTMLResponse)
def docs_portal() -> HTMLResponse:
    """The documentation landing page."""
    if _PORTAL_HTML.is_file():
        return HTMLResponse(_PORTAL_HTML.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Docs portal</h1><p>docs/portal.html was not generated.</p>")


@router.get("/portal/readme", include_in_schema=False, response_class=PlainTextResponse)
def portal_readme() -> PlainTextResponse:
    """Raw project README (markdown)."""
    return PlainTextResponse(_README.read_text(encoding="utf-8") if _README.is_file() else "")


@router.get("/portal/api", include_in_schema=False, response_class=PlainTextResponse)
def portal_api() -> PlainTextResponse:
    """Raw full API reference (markdown)."""
    return PlainTextResponse(_API_MD.read_text(encoding="utf-8") if _API_MD.is_file() else "")


def _portal_url() -> str:
    host = os.getenv("HOST", "127.0.0.1")
    if host in ("0.0.0.0", "", "::"):
        host = "127.0.0.1"
    return f"http://{host}:{os.getenv('PORT', '8000')}/portal"


def _open_browser() -> None:
    """Open the portal in a browser shortly after startup (dev convenience)."""
    if os.getenv("OPEN_BROWSER", "1").lower() not in ("1", "true", "yes", "on"):
        return
    if os.getenv("ENVIRONMENT", "development").lower() == "production":
        return
    url = _portal_url()
    try:
        threading.Timer(1.2, lambda: webbrowser.open(url)).start()
        logger.info("Opening docs portal at %s", url)
    except Exception as exc:  # headless / no display
        logger.debug("Could not open browser: %s", exc)


def mount(app, *, open_browser: bool = True) -> None:
    """Attach portal routes to ``app`` and (optionally) auto-open the browser on startup."""
    app.include_router(router)
    if open_browser:
        app.add_event_handler("startup", _open_browser)
