"""DocumentationApp is a mounted app that serves one docs build."""

import html
import re
from urllib.parse import quote, urljoin

import pytest
from django.conf import settings
from django.contrib.auth.models import Permission
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import resolve_url
from django.urls import reverse
from flex_menu.checks import (
    user_has_any_permission,
    user_in_any_group,
    user_is_authenticated,
)

from mvp_sphinx.mounted import DocumentationApp
from tests.factories import UserFactory


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
        self, client, user, docs_app, guide_build, monkeypatch
    ):
        client.force_login(user)
        addresses = ["/docs/", "/docs/page/", *asset_addresses(client, guide_build)]
        without_rule = [client.get(address) for address in addresses]

        monkeypatch.setattr(docs_app, "check", user_is_authenticated)
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


PAGE_TEXTS = [
    FRONT_PAGE_TEXT,
    "This page sits beside the front page.",
    "The pages inside this folder.",
    "Two folders down.",
]


def is_forbidden(response) -> bool:
    return response.status_code == 403 and "403.html" in [
        template.name for template in response.templates
    ]


def boom(request):
    raise RuntimeError("boom")


class TestOwnRule:
    @pytest.fixture(autouse=True)
    def group_rule(self, docs_app, group, monkeypatch):
        monkeypatch.setattr(docs_app, "check", user_in_any_group(group.name))

    @pytest.fixture
    def member(self, group):
        member = UserFactory()
        member.groups.add(group)
        return member

    @pytest.fixture
    def files(self, client, db, docs_app, guide_build, monkeypatch):
        with monkeypatch.context() as admitted:
            admitted.setattr(docs_app, "check", True)
            return asset_addresses(client, guide_build)

    @pytest.mark.parametrize("address", ["/docs/", "/docs/page/"])
    def test_a_member_gets_a_page(self, client, member, address):
        client.force_login(member)

        assert client.get(address).status_code == 200

    def test_a_member_gets_the_front_page_content(self, client, member):
        client.force_login(member)

        assert FRONT_PAGE_TEXT in client.get("/docs/").content.decode()

    @pytest.mark.parametrize("index", [0, 1])
    def test_a_member_gets_the_image_and_the_download(
        self, client, member, files, index
    ):
        client.force_login(member)

        assert client.get(files[index]).status_code == 200

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
    def test_a_signed_in_non_member_is_forbidden_with_no_page_text(
        self, client, user, address
    ):
        client.force_login(user)

        response = client.get(address)

        assert is_forbidden(response)
        assert not any(text in response.content.decode() for text in PAGE_TEXTS)

    @pytest.mark.parametrize("index", [0, 1])
    def test_a_signed_in_non_member_is_forbidden_with_no_file(
        self, client, user, member, files, index
    ):
        client.force_login(member)
        content = body(client.get(files[index]))
        client.force_login(user)

        response = client.get(files[index])

        assert is_forbidden(response)
        assert content not in body(response)

    def test_a_signed_in_non_member_is_forbidden_when_the_build_is_missing(
        self, client, user, docs_app, monkeypatch, tmp_path
    ):
        monkeypatch.setattr(docs_app, "build_dir", tmp_path / "missing")
        client.force_login(user)

        assert is_forbidden(client.get("/docs/page/"))

    def test_an_anonymous_reader_is_sent_to_sign_in(self, client, db):
        response = client.get("/docs/page/")

        assert response.status_code == 302
        assert response["Location"] == sign_in_address("/docs/page/")

    def test_the_entry_is_absent_for_a_non_member(self, client, user, docs_app):
        client.force_login(user)
        page = client.get(reverse("overview")).content.decode()

        assert f'href="{reverse(docs_app.landing)}"' not in sidebar(page)

    def test_the_entry_is_present_for_a_member(self, client, member, docs_app):
        client.force_login(member)
        page = client.get(reverse("overview")).content.decode()

        assert f'href="{reverse(docs_app.landing)}"' in sidebar(page)

    def test_the_forbidden_page_does_not_name_the_app(
        self, client, user, member, group, handbook_app, monkeypatch
    ):
        monkeypatch.setattr(handbook_app, "check", user_in_any_group(group.name))
        name = html.escape(str(handbook_app.name))
        client.force_login(member)
        admitted = client.get("/manuals/admin/backups/")
        client.force_login(user)

        refused = client.get("/manuals/admin/backups/")

        assert name in admitted.content.decode()
        assert is_forbidden(refused)
        assert name not in refused.content.decode()


class TestPermissionRule:
    @pytest.fixture(autouse=True)
    def permission_rule(self, docs_app, monkeypatch):
        monkeypatch.setattr(
            docs_app, "check", user_has_any_permission("auth.view_user")
        )

    def test_a_user_granted_the_permission_gets_a_page(self, client, user):
        user.user_permissions.add(Permission.objects.get(codename="view_user"))
        client.force_login(user)

        assert client.get("/docs/page/").status_code == 200

    def test_a_user_without_the_permission_is_forbidden(self, client, user):
        client.force_login(user)

        assert is_forbidden(client.get("/docs/page/"))


class TestRuleAdmittingNoOne:
    @pytest.fixture(autouse=True)
    def nobody(self, docs_app, monkeypatch):
        monkeypatch.setattr(docs_app, "check", False)

    @pytest.fixture
    def superuser(self, db):
        return UserFactory(is_staff=True, is_superuser=True)

    def test_a_superuser_is_forbidden(self, client, superuser):
        client.force_login(superuser)

        assert is_forbidden(client.get("/docs/page/"))

    def test_a_superuser_is_offered_no_entry(self, client, superuser, docs_app):
        client.force_login(superuser)
        page = client.get(reverse("overview")).content.decode()

        assert f'href="{reverse(docs_app.landing)}"' not in sidebar(page)


class TestRuleThatRaises:
    def test_a_page_request_raises_the_error(self, client, db, docs_app, monkeypatch):
        monkeypatch.setattr(docs_app, "check", boom)

        with pytest.raises(RuntimeError):
            client.get("/docs/page/")

    def test_the_overview_page_raises_the_error(
        self, client, db, docs_app, monkeypatch
    ):
        monkeypatch.setattr(docs_app, "check", boom)

        with pytest.raises(RuntimeError):
            client.get(reverse("overview"))
