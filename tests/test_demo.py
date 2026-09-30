"""The demo project's pages, asserted as rendered."""

# Everything in the demo fails quietly: an unresolvable component renders empty
# and a menu entry whose URL will not resolve is dropped from the tree.

from urllib.parse import urldefrag, urljoin

import pytest
from bs4 import BeautifulSoup
from django.urls import reverse
from mvp.menus import MenuCollapse, MenuGroup

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


def leaves(items) -> list[str]:
    found = []
    for item in items:
        found += leaves(item.visible_children) if item.is_parent else [item.url]
    return found


def branches(items) -> list:
    found = []
    for item in items:
        if item.is_parent:
            found += [item, *branches(item.visible_children)]
    return found


def admonition_classes(pages) -> set[str]:
    return {
        name
        for soup in pages.values()
        for each in soup.select("div.admonition")
        for name in each["class"]
    }


@pytest.fixture
def guide_menu(demo_guide_app, rf):
    return demo_guide_app.menu.process(rf.get("/docs/"))


@pytest.fixture
def guide_responses(guide_menu, client, db):
    return {
        address: client.get(address) for address in leaves(guide_menu.visible_children)
    }


@pytest.fixture
def guide_pages(guide_responses):
    return {
        address: BeautifulSoup(response.content, "html.parser")
        for address, response in guide_responses.items()
    }


class TestDemoGuideStates:
    ADMONITION_KINDS = {
        "note",
        "tip",
        "hint",
        "important",
        "warning",
        "caution",
        "attention",
        "danger",
        "error",
        "seealso",
    }

    def test_every_page_in_the_contents_answers(self, guide_responses) -> None:
        assert {each.status_code for each in guide_responses.values()} == {200}

    def test_the_contents_holds_two_or_more_captioned_groups(self, guide_menu) -> None:
        groups = [
            each
            for each in branches(guide_menu.visible_children)
            if isinstance(each, MenuGroup)
        ]

        assert len(groups) >= 2

    def test_the_contents_holds_a_collapsible_branch(self, guide_menu) -> None:
        nested = [
            each
            for each in branches(guide_menu.visible_children)
            if isinstance(each, MenuCollapse)
        ]

        assert nested

    def test_a_page_lists_three_headings_with_a_nested_list(self, guide_pages) -> None:
        landmarks = [
            soup.find("nav", attrs={"aria-labelledby": "mvp-sphinx-on-this-page"})
            for soup in guide_pages.values()
        ]

        assert any(
            landmark and len(landmark.find_all("a")) >= 3 and landmark.select("ul ul")
            for landmark in landmarks
        )

    def test_a_page_links_both_its_previous_and_its_next_page(
        self, guide_pages
    ) -> None:
        assert any(
            soup.find("a", rel="prev") and soup.find("a", rel="next")
            for soup in guide_pages.values()
        )

    def test_each_admonition_kind_is_drawn(self, guide_pages) -> None:
        classes = admonition_classes(guide_pages)

        assert classes >= self.ADMONITION_KINDS

    def test_a_generic_admonition_is_drawn(self, guide_pages) -> None:
        classes = admonition_classes(guide_pages)

        assert any(name.startswith("admonition-") for name in classes)

    def test_code_is_highlighted(self, guide_pages) -> None:
        assert any(soup.select("div.highlight") for soup in guide_pages.values())

    def test_a_table_sits_in_the_scroll_region(self, guide_pages) -> None:
        assert any(
            soup.select("div.mvp-sphinx-scroll table") for soup in guide_pages.values()
        )

    def test_an_image_is_served_as_an_image(self, guide_pages, client) -> None:
        found = []
        for address, soup in guide_pages.items():
            for image in soup.select("img[src]"):
                response = client.get(urljoin(address, image["src"]))
                found.append((response.status_code, response.headers["Content-Type"]))
                response.close()

        assert any(
            status == 200 and kind.startswith("image/") for status, kind in found
        )

    def test_a_download_is_served(self, guide_pages, client) -> None:
        statuses = []
        for address, soup in guide_pages.items():
            for link in soup.select("a.download[href]"):
                response = client.get(urljoin(address, link["href"]))
                statuses.append(response.status_code)
                response.close()

        assert 200 in statuses

    def test_a_glossary_is_drawn(self, guide_pages) -> None:
        assert any(soup.select("dl.glossary") for soup in guide_pages.values())

    def test_a_reference_links_another_page_of_the_guide(self, guide_pages) -> None:
        targets = {
            (address, urldefrag(urljoin(address, link["href"]))[0])
            for address, soup in guide_pages.items()
            for link in soup.select("a.reference.internal[href]")
        }

        assert any(
            target in guide_pages and target != address for address, target in targets
        )

    def test_an_address_with_no_page_answers_not_found(
        self, demo_guide_app, client, db
    ) -> None:
        assert client.get("/docs/no-such-page/").status_code == 404

    def test_the_demo_menu_entry_leads_to_the_front_page(
        self, demo_guide_app, sidebar, client, db
    ) -> None:
        page = client.get(reverse("overview")).content.decode()
        entry = BeautifulSoup(sidebar(page), "html.parser").find(
            "a", href=lambda href: href and href.startswith("/docs/")
        )

        response = client.get(entry["href"])

        assert response.resolver_match.view_name == "docs:front_page"
