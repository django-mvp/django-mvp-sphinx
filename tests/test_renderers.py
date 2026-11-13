"""SidebarRenderer draws the pages of the contents with the package's entry."""

import pytest
from bs4 import BeautifulSoup
from django.test import override_settings
from flex_menu import MenuItem
from mvp.renderers import SidebarRenderer as MvpSidebarRenderer

from mvp_sphinx.renderers import SidebarRenderer

ENTRY_OVERRIDE = """{% extends "mvp_sphinx/contents/entry.html" %}
{% block mvp_sphinx.entry_end %}<b data-pages="{{ entry.children|length }}"></b>{% endblock %}
"""


def drawn(app, rf, address):
    request = rf.get(address)
    return BeautifulSoup(
        SidebarRenderer().render(app.menu.process(request)), "html.parser"
    )


class TestSidebarRenderer:
    def test_it_is_django_mvps_sidebar_renderer(self) -> None:
        assert issubclass(SidebarRenderer, MvpSidebarRenderer)

    def test_any_other_item_is_drawn_by_django_mvps_templates(self) -> None:
        item = MenuItem(name="home", url="/", parent=None)

        assert SidebarRenderer().get_template(item) == MvpSidebarRenderer().get_template(
            item
        )

    def test_it_brings_the_contents_script_and_styles(self) -> None:
        media = str(SidebarRenderer().media)

        assert "mvp_sphinx/contents.js" in media
        assert "mvp_sphinx/contents.css" in media

    def test_an_entry_is_a_list_item_with_a_link_to_its_page(
        self, contents_app, rf
    ) -> None:
        soup = drawn(contents_app, rf, "/docs/")

        entry = soup.select_one("li.mvp-sphinx-entry > a[href='/docs/install/']")
        assert entry.select_one(".mvp-sphinx-entry-title").get_text() == "Install"

    def test_a_hidden_page_with_pages_of_its_own_has_a_heading_and_no_link(
        self, menu_settings_app, rf
    ) -> None:
        soup = drawn(menu_settings_app, rf, "/docs/quiet/one/")

        heading = next(
            each
            for each in soup.select("li.mvp-sphinx-entry > .mvp-sphinx-entry-heading")
            if each.get_text(strip=True) == "Quiet"
        )
        assert heading.name == "span"
        assert not soup.find("a", href="/docs/quiet/")

    def test_a_project_adds_to_every_entry_through_the_entry_end_block(
        self, contents_app, rf, tmp_path
    ) -> None:
        override = tmp_path / "mvp_sphinx" / "contents"
        override.mkdir(parents=True)
        (override / "entry.html").write_text(ENTRY_OVERRIDE)
        from django.conf import settings

        templates = [{**settings.TEMPLATES[0], "DIRS": [tmp_path]}]

        with override_settings(TEMPLATES=templates):
            soup = drawn(contents_app, rf, "/docs/chain/two/")

        assert {
            link["href"]: link.b["data-pages"]
            for link in soup.select("li.mvp-sphinx-entry > a")
        } == {
            "/docs/install/": "0",
            "/docs/explicit/": "0",
            "/docs/chain/one/": "1",
            "/docs/chain/two/": "1",
            "/docs/chain/three/": "0",
            "/docs/markup/": "0",
            "/docs/shared/": "0",
            "/docs/standalone/": "0",
            "/docs/reference/api/": "0",
            "/docs/hidden-page/": "0",
        }

    @pytest.mark.parametrize("address", ["/docs/", "/docs/chain/three/"])
    def test_the_request_is_in_the_entrys_context(self, contents_app, rf, address) -> None:
        request = rf.get(address)
        item = contents_app.menu.process(request).visible_children[1].visible_children[0]

        assert SidebarRenderer().get_context_data(item)["request"] is request
