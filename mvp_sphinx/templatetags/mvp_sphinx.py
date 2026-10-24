"""Template tags for placing the documentation on a host project's own pages."""

from django import template
from django.core.exceptions import ImproperlyConfigured
from django.template import Context
from mvp.mounted import MountedApp

from mvp_sphinx.extracts import PageExtract
from mvp_sphinx.mounted import DocumentationApp

register = template.Library()


@register.simple_tag(takes_context=True)
def page_extract(context: Context, namespace: str, address: str) -> PageExtract | str:
    """Place a page of a documentation app, or one section of it, in a template.

    The extract is the one ``DocumentationApp.page_extract`` returns, asked for
    the template's ``request``.

    Args:
        context: The template's context. It must hold ``request``.
        namespace: The URL namespace of the documentation app, ``"docs"`` unless
            the project mounts several.
        address: The page's address below the app's prefix, with a section's
            anchor or not. The empty address is the front page.

    Returns:
        The extract, which renders as its content, or an empty string when there
        is none to show. Used with ``as``, the extract binds the name, so its
        ``title`` and ``url`` can be read.

    Raises:
        ImproperlyConfigured: The context holds no ``request``, or no
            documentation app is mounted under ``namespace``.

    Example::

        {% load mvp_sphinx %}
        {% page_extract "docs" "reference/accounts#sharing" %}
    """
    request = context.get("request")
    if request is None:
        raise ImproperlyConfigured(
            "page_extract needs the request in the template's context. Add "
            "django.template.context_processors.request to the template settings."
        )
    for mounted in MountedApp.mounts(request):
        app = mounted.app
        if isinstance(app, DocumentationApp) and app.namespace == namespace:
            return app.page_extract(address, request) or ""
    raise ImproperlyConfigured(
        f'page_extract: no documentation app is mounted under the namespace "{namespace}".'
    )
