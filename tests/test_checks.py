"""The package's startup checks."""

import pytest
from django.test import override_settings

from mvp_sphinx.checks import check_sidebar_renderer
from mvp_sphinx.renderers import SidebarRenderer


class OwnRenderer(SidebarRenderer):
    """A project's own renderer built on the package's."""


def renderers(sidebar):
    return {"FLEX_MENUS": {"renderers": {"sidebar": sidebar}} if sidebar else {}}


class TestSidebarRendererCheck:
    @pytest.mark.parametrize(
        "sidebar",
        ["mvp_sphinx.renderers.SidebarRenderer", "tests.test_checks.OwnRenderer"],
    )
    def test_the_packages_renderer_or_a_subclass_passes(self, sidebar) -> None:
        with override_settings(**renderers(sidebar)):
            assert check_sidebar_renderer(None) == []

    @pytest.mark.parametrize(
        "sidebar", ["mvp.renderers.SidebarRenderer", "no.such.Renderer", None]
    )
    def test_any_other_renderer_is_an_error(self, sidebar) -> None:
        with override_settings(**renderers(sidebar)):
            errors = check_sidebar_renderer(None)

        assert [error.id for error in errors] == ["mvp_sphinx.E001"]
