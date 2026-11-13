"""The checks Django runs on the project when it starts."""

from typing import Any

from django.conf import settings
from django.core.checks import CheckMessage, Error
from django.utils.module_loading import import_string

from mvp_sphinx.renderers import SidebarRenderer

RENDERER_HINT = (
    'Set FLEX_MENUS["renderers"]["sidebar"] to '
    '"mvp_sphinx.renderers.SidebarRenderer", or to a subclass of it.'
)


def check_sidebar_renderer(app_configs: Any, **kwargs: Any) -> list[CheckMessage]:
    """Refuse a sidebar renderer that can't draw the contents.

    The contents' entries need the package's renderer, which draws their
    toggles and brings the script that opens them.

    Args:
        app_configs: The app configs Django asks the check about. Unused.
        **kwargs: Anything else Django passes a check. Unused.

    Returns:
        An error when the sidebar renderer is missing, can't be imported, or
        is not the package's.
    """
    path = getattr(settings, "FLEX_MENUS", {}).get("renderers", {}).get("sidebar")
    try:
        renderer = import_string(path) if path else None
    except ImportError:
        renderer = None
    if isinstance(renderer, type) and issubclass(renderer, SidebarRenderer):
        return []
    return [
        Error(
            f"The sidebar renderer {path!r} can't draw the documentation's contents.",
            hint=RENDERER_HINT,
            id="mvp_sphinx.E001",
        )
    ]
