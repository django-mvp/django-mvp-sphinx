"""DocumentationApp is a mounted app that serves one docs build."""

import re
from urllib.parse import quote, urljoin

import pytest
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import resolve_url
from django.urls import reverse
from flex_menu.checks import user_is_authenticated

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


def sign_in_address(address: str) -> str:
    return f"{resolve_url(settings.LOGIN_URL)}?next={quote(address, safe='/')}"


def body(response) -> bytes:
    if response.streaming:
        return b"".join(response.streaming_content)
    return response.content


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


class TestSignedInOnly:
    def test_a_signed_in_reader_gets_what_they_got_without_a_rule(
        self, client, user, docs_app, guide_build
    ):
        client.force_login(user)
        addresses = ["/docs/", "/docs/page/", *asset_addresses(client, guide_build)]
        without_rule = [client.get(address) for address in addresses]

        docs_app.check = user_is_authenticated
        with_rule = [client.get(address) for address in addresses]

        assert [r.status_code for r in with_rule] == [200] * len(addresses)
        assert [body(r) for r in with_rule] == [body(r) for r in without_rule]

    @pytest.mark.parametrize("address", ["/docs/", "/docs/page/", "/docs/page/?x=1"])
    def test_an_anonymous_reader_is_sent_to_sign_in_and_back(
        self, client, db, docs_app, monkeypatch, address
    ):
        monkeypatch.setattr(docs_app, "check", user_is_authenticated)

        response = client.get(address)

        assert response.status_code == 302
        assert response["Location"] == sign_in_address(address)
        assert response.content == b""

    def test_the_sign_in_address_answers_a_page(
        self, client, db, docs_app, monkeypatch
    ):
        monkeypatch.setattr(docs_app, "check", user_is_authenticated)
        location = client.get("/docs/page/").url

        assert client.get(location).status_code == 200

    def test_signing_in_lands_on_the_requested_address_with_its_query(
        self, client, user, docs_app, monkeypatch
    ):
        monkeypatch.setattr(docs_app, "check", user_is_authenticated)
        location = client.get("/docs/page/?x=1").url

        response = client.post(
            reverse("account_login"),
            {
                "username": user.username,
                "password": "password",
                "next": "/docs/page/?x=1",
            },
        )

        assert location == sign_in_address("/docs/page/?x=1")
        assert response.status_code == 302
        assert response["Location"] == "/docs/page/?x=1"
        assert client.get(response["Location"]).status_code == 200

    def test_the_entry_is_absent_for_an_anonymous_reader(
        self, client, db, docs_app, monkeypatch
    ):
        monkeypatch.setattr(docs_app, "check", user_is_authenticated)
        page = client.get(reverse("overview")).content.decode()

        assert f'href="{reverse(docs_app.landing)}"' not in sidebar(page)

    def test_the_entry_leads_a_signed_in_reader_to_the_front_page(
        self, client, user, docs_app, monkeypatch
    ):
        monkeypatch.setattr(docs_app, "check", user_is_authenticated)
        client.force_login(user)
        page = client.get(reverse("overview")).content.decode()

        assert f'href="{reverse(docs_app.landing)}"' in sidebar(page)
        assert reverse(docs_app.landing) == "/docs/"


class TestRefusal:
    @pytest.fixture(autouse=True)
    def signed_in_only(self, docs_app, monkeypatch):
        monkeypatch.setattr(docs_app, "check", user_is_authenticated)

    @pytest.fixture
    def addresses(self, client, db, docs_app, guide_build, monkeypatch):
        # The files' addresses come from a page an admitted reader can open.
        with monkeypatch.context() as admitted:
            admitted.setattr(docs_app, "check", True)
            return asset_addresses(client, guide_build)

    @pytest.mark.parametrize(
        "address",
        [
            "/docs/",
            "/docs/page/",
            "/docs/section/",
            "/docs/section/nested/page/",
            "/docs/nope/",
            "/docs/page",
            "/docs/nope",
        ],
    )
    def test_an_anonymous_reader_is_turned_away_the_same_way(self, client, db, address):
        response = client.get(address)

        assert response.status_code == 302
        assert response["Location"] == sign_in_address(address)
        assert response.content == b""

    @pytest.mark.parametrize("index", [0, 1])
    def test_an_anonymous_reader_gets_no_file(self, client, addresses, index):
        address = addresses[index]

        response = client.get(address)

        assert response.status_code == 302
        assert response["Location"] == sign_in_address(address)
        assert body(response) == b""

    def test_a_missing_build_is_refused_like_any_other_address(
        self, client, db, docs_app, monkeypatch, tmp_path
    ):
        monkeypatch.setattr(docs_app, "build_dir", tmp_path / "missing")

        response = client.get("/docs/page/")

        assert response.status_code == 302
        assert response["Location"] == sign_in_address("/docs/page/")
        assert response.content == b""
