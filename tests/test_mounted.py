"""DocumentationApp is a mounted app that serves one docs build."""

import re
from urllib.parse import urljoin

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse

from mvp_sphinx.mounted import DocumentationApp


class TestDocumentationApp:
    def test_it_needs_a_build_dir(self) -> None:
        with pytest.raises(ImproperlyConfigured):
            DocumentationApp()

    def test_a_build_dir_that_does_not_exist_does_not_stop_construction(
        self, tmp_path
    ) -> None:
        DocumentationApp(build_dir=tmp_path / "not-built-yet")

    def test_its_landing_is_the_mount_prefix(self, docs_app) -> None:
        assert reverse(docs_app.landing) == "/docs/"


class TestMenuEntry:
    def test_the_entry_leads_to_the_apps_front_page(self, docs_app) -> None:
        assert reverse(docs_app.menu_item().view_name) == "/docs/"

    def test_following_the_entry_answers_the_front_page(
        self, client, db, docs_app
    ) -> None:
        response = client.get(reverse(docs_app.menu_item().view_name))

        assert response.status_code == 200
        assert response.context["page_data"]["current_page_name"] == "index"

    def test_a_second_apps_entry_leads_to_its_own_front_page(
        self, client, db, handbook_app
    ) -> None:
        url = reverse(handbook_app.menu_item().view_name)

        assert url == "/manuals/admin/"
        assert client.get(url).status_code == 200


FRONT_PAGE_TEXT = "Welcome to the guide"


def sidebar(page: str) -> str:
    return page.split('aria-label="Main navigation"', 1)[1].split("</ul>", 1)[0]


def asset_addresses(client, guide_build) -> list[str]:
    linked_page = client.get("/docs/page/").content.decode()
    image = next((guide_build / "_images").iterdir()).name
    href = re.search(r'href="([^"]*_downloads/[^"]+)"', linked_page).group(1)
    return [f"/docs/_images/{image}", urljoin("/docs/page/", href)]


class TestEveryoneByDefault:
    @pytest.mark.parametrize("address", ["/docs/", "/docs/page/"])
    def test_an_anonymous_reader_gets_a_page(self, client, db, docs_app, address):
        assert client.get(address).status_code == 200

    def test_an_anonymous_reader_gets_the_front_page_content(
        self, client, db, docs_app
    ):
        assert FRONT_PAGE_TEXT in client.get("/docs/").content.decode()

    def test_an_anonymous_reader_gets_the_image_and_the_download(
        self, client, db, docs_app, guide_build
    ):
        for address in asset_addresses(client, guide_build):
            assert client.get(address).status_code == 200

    def test_the_overview_page_offers_the_entry(self, overview_page, docs_app):
        assert f'href="{reverse(docs_app.landing)}"' in sidebar(overview_page)
