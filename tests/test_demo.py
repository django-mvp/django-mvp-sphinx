"""The demo project's pages, asserted as rendered."""

# Everything in the demo fails quietly: an unresolvable component renders empty
# and a menu entry whose URL will not resolve is dropped from the tree.

from bs4 import BeautifulSoup
from django.urls import reverse

from demo.mounted import docs
from demo.settings import BASE_DIR
from mvp_sphinx.docs_build import DocsBuild
from tests.factories import UserFactory


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


class TestDocumentationSearch:
    def test_the_front_page_offers_the_search(
        self, client, db, sphinx_build, monkeypatch
    ) -> None:
        monkeypatch.setattr(docs, "build_dir", sphinx_build(BASE_DIR / "demo" / "docs"))

        form = BeautifulSoup(client.get("/docs/").content, "html.parser").find(
            "form", role="search"
        )

        assert form["action"] == reverse("docs:search")


class TestStaffGuideEntry:
    def test_the_entry_is_absent_for_an_anonymous_reader(
        self, sidebar, overview_page: str
    ) -> None:
        assert 'href="/staff-guide/"' not in sidebar(overview_page)

    def test_the_entry_is_absent_for_a_regular_user(
        self, sidebar, client, user
    ) -> None:
        client.force_login(user)
        page = client.get(reverse("overview")).content.decode()

        assert 'href="/staff-guide/"' not in sidebar(page)

    def test_the_entry_is_present_for_a_staff_user(self, sidebar, client, db) -> None:
        client.force_login(UserFactory(is_staff=True))
        page = client.get(reverse("overview")).content.decode()

        assert 'href="/staff-guide/"' in sidebar(page)

    def test_a_staff_user_gets_the_front_page(
        self, client, db, staff_guide_app
    ) -> None:
        client.force_login(UserFactory(is_staff=True))

        assert client.get("/staff-guide/").status_code == 200


class TestDemoGuide:
    def test_building_the_guide_writes_the_navigation_file(self, sphinx_build) -> None:
        out = sphinx_build(BASE_DIR / "demo" / "docs")

        assert (out / DocsBuild.NAVIGATION_FILE).is_file()

    def test_building_the_staff_guide_writes_the_navigation_file(
        self, sphinx_build
    ) -> None:
        out = sphinx_build(BASE_DIR / "demo" / "staff_guide")

        assert (out / DocsBuild.NAVIGATION_FILE).is_file()
