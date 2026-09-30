"""The demo project's pages, asserted as rendered."""

# Everything in the demo fails quietly: an unresolvable component renders empty
# and a menu entry whose URL will not resolve is dropped from the tree.

from django.urls import reverse

from demo.settings import BASE_DIR
from mvp_sphinx.docs_build import DocsBuild


class TestOverviewPage:
    def test_it_responds(self, client, db) -> None:
        assert client.get(reverse("overview")).status_code == 200

    def test_the_shell_wraps_it(self, overview_page: str) -> None:
        # A template that fails to extend the shell still returns 200.
        assert 'aria-label="Main navigation"' in overview_page

    def test_the_sidebar_links_the_pages_that_exist(self, overview_page: str) -> None:
        sidebar = overview_page.split('aria-label="Main navigation"', 1)[1]
        sidebar = sidebar.split("</ul>", 1)[0]
        assert f'href="{reverse("overview")}"' in sidebar


class TestDocumentationEntry:
    def test_the_sidebar_links_the_documentation(self, overview_page: str) -> None:
        sidebar = overview_page.split('aria-label="Main navigation"', 1)[1]
        sidebar = sidebar.split("</ul>", 1)[0]
        assert 'href="/docs/"' in sidebar


class TestDemoGuide:
    def test_building_the_guide_writes_the_navigation_file(self, sphinx_build) -> None:
        out = sphinx_build(BASE_DIR / "demo" / "docs")

        assert (out / DocsBuild.NAVIGATION_FILE).is_file()
