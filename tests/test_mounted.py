"""DocumentationApp is a mounted app that serves one docs build."""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote, urljoin

import pytest
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, Permission
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.core.management.base import CommandError
from django.shortcuts import resolve_url
from django.urls import reverse
from django.utils import translation
from flex_menu.checks import (
    user_has_any_permission,
    user_in_any_group,
    user_is_authenticated,
)
from mvp.menus import AppMenu
from mvp.search import Result, registered
from mvp.search.registry import default_registry
from sphinx.cmd.build import build_main

from mvp_sphinx.docs_build import DocsBuild
from mvp_sphinx.mounted import DocumentationApp
from mvp_sphinx.search import DocsSearch
from tests.factories import UserFactory
from tests.urls_quickstart import docs as quickstart_docs


class TestDocumentationApp:
    def test_it_needs_a_build_dir(self) -> None:
        with pytest.raises(ImproperlyConfigured):
            DocumentationApp()

    def test_a_build_dir_that_does_not_exist_does_not_stop_construction(
        self, tmp_path
    ) -> None:
        DocumentationApp(build_dir=tmp_path / "not-built-yet")

    def test_it_needs_no_source_dir(self, tmp_path) -> None:
        assert DocumentationApp(build_dir=tmp_path).source_dir is None

    def test_its_landing_is_the_mount_prefix(self, docs_app) -> None:
        assert reverse(docs_app.landing) == "/docs/"


class TestEditAddress:
    def test_the_source_is_put_in_for_path(self, tmp_path) -> None:
        app = DocumentationApp(
            build_dir=tmp_path, edit_url="https://example.com/{path}?plain=1"
        )

        assert app.edit_address("guide/install.rst") == (
            "https://example.com/guide/install.rst?plain=1"
        )

    def test_a_source_name_is_quoted_for_an_address(self, tmp_path) -> None:
        app = DocumentationApp(
            build_dir=tmp_path, edit_url="https://example.com/{path}"
        )

        assert app.edit_address("guide/first steps.md") == (
            "https://example.com/guide/first%20steps.md"
        )

    def test_there_is_no_address_without_an_edit_url(self, tmp_path) -> None:
        assert DocumentationApp(build_dir=tmp_path).edit_address("index.rst") == ""

    def test_there_is_no_address_without_a_source(self, tmp_path) -> None:
        app = DocumentationApp(
            build_dir=tmp_path, edit_url="https://example.com/{path}"
        )

        assert app.edit_address("") == ""


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


def sign_in_address(address: str) -> str:
    return f"{resolve_url(settings.LOGIN_URL)}?next={quote(address, safe='/')}"


def body(response) -> bytes:
    if response.streaming:
        return b"".join(response.streaming_content)
    # The language switcher's form holds a token that is masked anew each time.
    return re.sub(rb'name="csrfmiddlewaretoken" value="[^"]*"', b"", response.content)


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

    def test_the_overview_page_offers_the_entry(self, sidebar, overview_page, docs_app):
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
        response = client.get(location)

        assert response.status_code == 200
        assert response.context["next"] == "/docs/page/"

    def test_signing_in_lands_on_the_requested_address_with_its_query(
        self, client, user, docs_app, monkeypatch
    ):
        monkeypatch.setattr(docs_app, "check", user_is_authenticated)
        location = client.get("/docs/page/?x=1").url
        sign_in_page = client.get(location)

        response = client.post(
            reverse("account_login"),
            {
                "username": user.username,
                "password": "password",
                "next": sign_in_page.context["next"],
            },
        )

        assert location == sign_in_address("/docs/page/?x=1")
        assert response.status_code == 302
        assert response["Location"] == "/docs/page/?x=1"
        assert client.get(response["Location"]).status_code == 200

    def test_the_entry_is_absent_for_an_anonymous_reader(
        self, sidebar, client, db, docs_app, monkeypatch
    ):
        monkeypatch.setattr(docs_app, "check", user_is_authenticated)
        page = client.get(reverse("overview")).content.decode()

        assert f'href="{reverse(docs_app.landing)}"' not in sidebar(page)

    def test_the_entry_leads_a_signed_in_reader_to_the_front_page(
        self, sidebar, client, user, docs_app, monkeypatch
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

    def test_the_entry_is_absent_for_a_non_member(
        self, sidebar, client, user, docs_app
    ):
        client.force_login(user)
        page = client.get(reverse("overview")).content.decode()

        assert f'href="{reverse(docs_app.landing)}"' not in sidebar(page)

    def test_the_entry_is_present_for_a_member(self, sidebar, client, member, docs_app):
        client.force_login(member)
        page = client.get(reverse("overview")).content.decode()

        assert f'href="{reverse(docs_app.landing)}"' in sidebar(page)

    def test_the_forbidden_page_does_not_name_the_app(
        self, client, user, member, group, handbook_app, monkeypatch
    ):
        monkeypatch.setattr(handbook_app, "check", user_in_any_group(group.name))
        client.force_login(member)
        admitted = client.get("/manuals/admin/backups/")
        client.force_login(user)

        refused = client.get("/manuals/admin/backups/")

        assert admitted.context["mounted_app"] == handbook_app
        assert admitted.context["mounted_menu"] == handbook_app.menu
        assert is_forbidden(refused)
        assert not refused.context["mounted_app"]
        assert not refused.context["mounted_menu"]


class TestPermissionRule:
    @pytest.fixture(autouse=True)
    def permission_rule(self, docs_app, monkeypatch):
        monkeypatch.setattr(
            docs_app, "check", user_has_any_permission("auth.view_group")
        )

    def test_a_user_granted_the_permission_gets_a_page(self, client, user):
        user.user_permissions.add(Permission.objects.get(codename="view_group"))
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

    def test_a_superuser_is_offered_no_entry(
        self, sidebar, client, superuser, docs_app
    ):
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


class TestSeveralApps:
    @pytest.fixture(autouse=True)
    def two_apps(self, docs_app, staff_guide_app, sidebar):
        self.sidebar = sidebar
        return docs_app, staff_guide_app

    @pytest.fixture
    def staff(self, db):
        return UserFactory(is_staff=True)

    def entries(self, client) -> str:
        return self.sidebar(client.get(reverse("overview")).content.decode())

    def test_an_anonymous_reader_is_offered_only_the_open_app(self, client, db):
        entries = self.entries(client)

        assert 'href="/docs/"' in entries
        assert 'href="/staff-guide/"' not in entries

    def test_a_regular_user_is_offered_only_the_open_app(self, client, user):
        client.force_login(user)
        entries = self.entries(client)

        assert 'href="/docs/"' in entries
        assert 'href="/staff-guide/"' not in entries

    def test_a_staff_user_is_offered_both_apps(self, client, staff):
        client.force_login(staff)
        entries = self.entries(client)

        assert 'href="/docs/"' in entries
        assert 'href="/staff-guide/"' in entries

    def test_an_anonymous_reader_gets_the_open_app_and_is_sent_to_sign_in(
        self, client, db
    ):
        assert client.get("/docs/").status_code == 200

        response = client.get("/staff-guide/")

        assert response.status_code == 302
        assert response["Location"] == sign_in_address("/staff-guide/")

    def test_a_regular_user_gets_the_open_app_and_is_forbidden_the_other(
        self, client, user
    ):
        client.force_login(user)

        assert client.get("/docs/").status_code == 200
        assert is_forbidden(client.get("/staff-guide/"))

    def test_a_staff_user_gets_both_apps(self, client, staff):
        client.force_login(staff)

        assert client.get("/docs/").status_code == 200
        assert client.get("/staff-guide/").status_code == 200

    def test_signing_in_changes_the_next_response(
        self, client, user, staff_guide_app, monkeypatch
    ):
        monkeypatch.setattr(staff_guide_app, "check", user_is_authenticated)
        assert client.get("/staff-guide/").status_code == 302

        client.force_login(user)

        assert client.get("/staff-guide/").status_code == 200

    def test_signing_in_adds_the_entry_to_the_next_overview_page(
        self, client, user, staff_guide_app, monkeypatch
    ):
        monkeypatch.setattr(staff_guide_app, "check", user_is_authenticated)
        assert 'href="/staff-guide/"' not in self.entries(client)

        client.force_login(user)

        assert 'href="/staff-guide/"' in self.entries(client)

    def test_joining_the_group_changes_the_next_response(
        self, client, user, group, staff_guide_app, monkeypatch
    ):
        monkeypatch.setattr(staff_guide_app, "check", user_in_any_group(group.name))
        client.force_login(user)
        assert is_forbidden(client.get("/staff-guide/"))

        user.groups.add(group)

        assert client.get("/staff-guide/").status_code == 200

    def test_joining_the_group_adds_the_entry_to_the_next_overview_page(
        self, client, user, group, staff_guide_app, monkeypatch
    ):
        monkeypatch.setattr(staff_guide_app, "check", user_in_any_group(group.name))
        client.force_login(user)
        assert 'href="/staff-guide/"' not in self.entries(client)

        user.groups.add(group)

        assert 'href="/staff-guide/"' in self.entries(client)


class TestSearchUnderTheReaderRule:
    SEARCH_ADDRESSES = ["/docs/search/", "/docs/search/?q=lantern"]

    @pytest.fixture
    def member(self, group):
        member = UserFactory()
        member.groups.add(group)
        return member

    @pytest.mark.parametrize("address", SEARCH_ADDRESSES)
    def test_an_anonymous_reader_is_turned_away_as_from_a_page(
        self, client, db, search_app, monkeypatch, address
    ):
        monkeypatch.setattr(search_app, "check", user_is_authenticated)

        response = client.get(address)

        assert response.status_code == 302
        assert response["Location"] == sign_in_address(address)
        assert response.content == b""

    @pytest.mark.parametrize("address", SEARCH_ADDRESSES)
    def test_a_signed_in_reader_gets_the_results_page(
        self, client, user, search_app, monkeypatch, address
    ):
        monkeypatch.setattr(search_app, "check", user_is_authenticated)
        client.force_login(user)

        response = client.get(address)

        assert response.status_code == 200

    @pytest.mark.parametrize("address", SEARCH_ADDRESSES)
    def test_an_anonymous_reader_is_turned_away_by_a_group_rule_too(
        self, client, db, search_app, group, monkeypatch, address
    ):
        monkeypatch.setattr(search_app, "check", user_in_any_group(group.name))

        response = client.get(address)

        assert response.status_code == 302
        assert response["Location"] == sign_in_address(address)

    def test_a_member_gets_the_results(
        self, client, search_app, group, member, monkeypatch
    ):
        monkeypatch.setattr(search_app, "check", user_in_any_group(group.name))
        client.force_login(member)

        response = client.get("/docs/search/", {"q": "quetzal"})

        assert response.status_code == 200
        assert "Lanterns and lamps" in response.content.decode()

    @pytest.mark.parametrize("address", SEARCH_ADDRESSES)
    def test_a_signed_in_non_member_is_forbidden_with_no_result_text(
        self, client, user, search_app, group, monkeypatch, address
    ):
        monkeypatch.setattr(search_app, "check", user_in_any_group(group.name))
        client.force_login(user)

        response = client.get(address)

        assert is_forbidden(response)
        assert "Lanterns and lamps" not in response.content.decode()


# The README's quickstart, followed step by step against a source of its own.
QUICKSTART_SOURCE = Path(__file__).parent / "sphinx" / "quickstart"
QUICKSTART_FRONT_PAGE = "/help/guide/"


def run_build(source: Path, out: Path, *options: str) -> None:
    # Step 3's command, with -W so the test's own source must build clean.
    arguments = ["-b", "json", "-W", *options, str(source), str(out)]
    assert build_main(arguments) == 0


def page_address(name: str) -> str:
    return reverse("quickstart:page", kwargs={"path": f"{name}/"})


def sidebar_of(app, response):
    # The app's own menu, a navigation landmark named after the app.
    return BeautifulSoup(response.content, "html.parser").find(
        "nav", attrs={"aria-label": str(app.name)}
    )


def leaves(item) -> list[str]:
    return [each.url for each in item.visible_children if not each.is_parent]


@pytest.fixture
def quickstart_source(tmp_path) -> Path:
    shutil.copytree(QUICKSTART_SOURCE, tmp_path / "docs")
    return tmp_path / "docs"


@pytest.fixture
def quickstart_build_dir(quickstart_source) -> Path:
    return quickstart_source / "_build" / "json"


@pytest.fixture
def quickstart(db, settings, monkeypatch, quickstart_source, quickstart_build_dir):
    run_build(quickstart_source, quickstart_build_dir)
    monkeypatch.setattr(quickstart_docs, "build_dir", quickstart_build_dir)
    settings.ROOT_URLCONF = "tests.urls_quickstart"
    # Step 5. AppMenu is process-wide, so the entry comes out again afterwards.
    entry = quickstart_docs.menu_item()
    AppMenu.append(entry)
    yield quickstart_docs
    AppMenu.pop(entry.name)


class TestQuickstart:
    def test_the_front_page_answers_in_the_shell_at_the_chosen_prefix(
        self, client, quickstart
    ) -> None:
        response = client.get(reverse("quickstart:front_page"))

        assert reverse("quickstart:front_page") == QUICKSTART_FRONT_PAGE
        assert response.status_code == 200
        assert sidebar_of(quickstart, response).find("a", href=QUICKSTART_FRONT_PAGE)

    def test_the_contents_group_holds_both_pages_and_each_answers(
        self, client, quickstart, rf
    ) -> None:
        tree = quickstart.menu.process(rf.get(QUICKSTART_FRONT_PAGE))
        groups = [each for each in tree.visible_children if each.is_parent]

        assert len(groups) == 1
        assert leaves(groups[0]) == [page_address("first"), page_address("second")]
        assert [client.get(url).status_code for url in leaves(groups[0])] == [200, 200]

    def test_the_host_menu_entry_leads_to_the_front_page(
        self, client, quickstart, sidebar
    ) -> None:
        host_page = client.get(reverse("overview")).content.decode()
        entry = BeautifulSoup(sidebar(host_page), "html.parser").find(
            "a", href=QUICKSTART_FRONT_PAGE
        )

        response = client.get(entry["href"])

        assert response.status_code == 200
        assert response.context["page_data"]["current_page_name"] == "index"

    def test_a_rebuild_into_the_same_folder_adds_a_page_to_the_next_request(
        self, client, quickstart, quickstart_source, quickstart_build_dir
    ) -> None:
        before = client.get(page_address("third"))
        (quickstart_source / "third.rst").write_text("The third page\n==============\n")
        index = quickstart_source / "index.rst"
        index.write_text(index.read_text() + "   third\n")

        # Sphinx 9.1 warns that it will not overwrite the copies it keeps of
        # changed sources, which -W would turn into a failed rebuild.
        run_build(
            quickstart_source,
            quickstart_build_dir,
            "-D",
            "suppress_warnings=misc.copy_overwrite",
        )
        after = client.get(page_address("third"))
        sidebar = sidebar_of(quickstart, client.get(QUICKSTART_FRONT_PAGE))

        assert before.status_code == 404
        assert after.status_code == 200
        assert sidebar.find("a", href=page_address("third"))


GUIDE_HOST = "guide.example.test"
SEARCH_HOST = "search.example.test"


@pytest.fixture
def chosen_app(guide_build, search_build, monkeypatch, settings):
    # The demo's docs app, serving the guide on one host and the search
    # fixture on any other, as a project serving one build per site would.
    from demo.mounted import docs

    settings.ALLOWED_HOSTS = [GUIDE_HOST, SEARCH_HOST, "testserver"]

    def build_for(request):
        return guide_build if request.get_host() == GUIDE_HOST else search_build

    monkeypatch.setattr(docs, "build_dir", build_for)
    return docs


def page(client, host, path="/docs/", **query):
    return client.get(path, query, HTTP_HOST=host)


class TestPagesFollowTheChosenBuild:
    def test_each_host_gets_its_own_front_page(self, client, db, chosen_app) -> None:
        assert "The guide front page" in page(client, GUIDE_HOST).content.decode()
        assert "The search fixture" in page(client, SEARCH_HOST).content.decode()

    def test_a_page_only_one_build_has_is_not_found_on_the_other(
        self, client, db, chosen_app
    ) -> None:
        assert page(client, SEARCH_HOST, "/docs/lanterns/").status_code == 200
        assert page(client, GUIDE_HOST, "/docs/lanterns/").status_code == 404

    def test_a_file_is_served_from_the_chosen_build_only(
        self, client, db, chosen_app, guide_build
    ) -> None:
        image = next((guide_build / "_images").iterdir()).name

        assert page(client, GUIDE_HOST, f"/docs/_images/{image}").status_code == 200
        assert page(client, SEARCH_HOST, f"/docs/_images/{image}").status_code == 404

    def test_a_chosen_build_that_does_not_exist_answers_not_found(
        self, client, db, chosen_app, monkeypatch, tmp_path
    ) -> None:
        monkeypatch.setattr(chosen_app, "build_dir", lambda request: tmp_path / "none")

        assert page(client, GUIDE_HOST).status_code == 404


class TestTheSidebarFollowsTheChosenBuild:
    def test_the_sidebar_is_rebuilt_for_each_hosts_build_in_turn(
        self, rf, chosen_app
    ) -> None:
        def addresses(host):
            def leaves(items):
                found = []
                for item in items:
                    if item.is_parent:
                        found += leaves(item.visible_children)
                    else:
                        found.append(item.url)
                return found

            request = rf.get("/docs/", HTTP_HOST=host)
            return leaves(chosen_app.menu.process(request).visible_children)

        for _ in range(2):
            guide = addresses(GUIDE_HOST)
            search = addresses(SEARCH_HOST)

            assert "/docs/page/" in guide
            assert "/docs/lanterns/" not in guide
            assert "/docs/lanterns/" in search
            assert "/docs/page/" not in search


class TestSearchFollowsTheChosenBuild:
    def test_search_reads_the_chosen_build(self, client, db, chosen_app) -> None:
        path = reverse("docs:search")

        assert "Lanterns and lamps" in (
            page(client, SEARCH_HOST, path, q="quetzal").content.decode()
        )
        assert "Lanterns and lamps" not in (
            page(client, GUIDE_HOST, path, q="quetzal").content.decode()
        )


class TestPageExtractsFollowTheChosenBuild:
    def test_an_extract_is_read_from_the_requests_build(
        self, rf, db, chosen_app
    ) -> None:
        def request_for(host):
            request = rf.get("/", HTTP_HOST=host)
            request.user = AnonymousUser()
            return request

        assert chosen_app.page_extract("lanterns/", request_for(SEARCH_HOST))
        assert chosen_app.page_extract("lanterns/", request_for(GUIDE_HOST)) is None


class TestTheBuildCommandWithABuildChosenPerRequest:
    @pytest.fixture
    def chosen_source(self, chosen_app, monkeypatch, tmp_path):
        monkeypatch.setattr(chosen_app, "source_dir", tmp_path)
        return chosen_app

    def test_naming_an_app_whose_build_is_chosen_per_request_is_an_error(
        self, chosen_source
    ) -> None:
        with pytest.raises(CommandError, match="each request"):
            call_command("build_docs", chosen_source.namespace, verbosity=0)

    def test_an_app_whose_build_is_chosen_per_request_is_left_out(
        self, chosen_source, monkeypatch
    ) -> None:
        from demo.mounted import staff_guide

        monkeypatch.setattr(staff_guide, "source_dir", None)

        with pytest.raises(CommandError, match="source_dir"):
            call_command("build_docs", verbosity=0)


class TestABuildChosenPerRequestIsAccepted:
    def test_an_app_takes_a_function_as_its_build_dir(self, tmp_path) -> None:
        DocumentationApp(build_dir=lambda request: tmp_path, namespace="chosen")


def site_search(app, query, request) -> list[Result]:
    """What the site's search finds in ``app`` for ``query``."""
    return list(default_registry.kinds[app.search_kind].find(query, request))


class TestSiteSearchKind:
    def test_each_documentation_app_is_a_kind_of_the_site_search(
        self, docs_app, staff_guide_app, handbook_app
    ) -> None:
        kinds = {kind.name: kind for kind in registered()}

        for app in (docs_app, staff_guide_app, handbook_app):
            kind = kinds[f"mvp_sphinx-{app.namespace}"]
            assert app.search_kind == kind.name
            assert str(kind.label) == str(app.name)
            assert kind.icon == app.icon

    def test_a_second_app_under_a_namespace_already_searched_is_accepted(
        self, tmp_path
    ) -> None:
        count = len(registered())

        DocumentationApp(build_dir=tmp_path)

        assert len(registered()) == count

    def test_a_word_finds_the_page_holding_it(self, rf, search_app, search_build):
        found = DocsSearch(DocsBuild(search_build)).results("quetzal")

        [result] = site_search(search_app, "quetzal", rf.get("/"))

        assert result.title == found[0]["title"]
        assert result.url == "/docs/lanterns/"
        assert result.passage == found[0]["passage"]

    def test_a_word_in_a_section_heading_leads_to_the_section(
        self, rf, search_app
    ) -> None:
        [result] = site_search(search_app, "gasket", rf.get("/"))

        assert result.url == "/docs/sections/#gasket"

    def test_a_result_leads_to_its_page_under_its_own_app(
        self, rf, handbook_app
    ) -> None:
        results = site_search(handbook_app, "backups", rf.get("/"))

        assert results
        assert all(result.url.startswith("/manuals/admin/") for result in results)

    @pytest.mark.parametrize(
        ("query", "where"),
        [
            # A page in a captioned part of the contents.
            ("install", "Getting started"),
            # Two titles at most, the outermost first.
            ("last", "Getting started · Chain one"),
        ],
    )
    def test_where_names_the_titles_above_the_page_in_the_contents(
        self, rf, contents_app, query, where
    ) -> None:
        # The page titled with the word comes first.
        result = site_search(contents_app, query, rf.get("/"))[0]

        assert result.where == where

    @pytest.mark.parametrize("query", ["standalone", "front"])
    def test_where_names_the_app_for_a_page_with_nothing_above_it(
        self, rf, contents_app, query
    ) -> None:
        result = site_search(contents_app, query, rf.get("/"))[0]

        assert result.where == str(contents_app.name)

    def test_a_reader_the_app_refuses_finds_nothing(self, rf, staff_guide_app) -> None:
        request = rf.get("/")
        request.user = AnonymousUser()

        assert site_search(staff_guide_app, "backups", request) == []

    def test_a_reader_the_app_admits_finds_its_pages(
        self, rf, db, staff_guide_app
    ) -> None:
        request = rf.get("/")
        request.user = UserFactory(is_staff=True)

        assert site_search(staff_guide_app, "backups", request)

    def test_a_build_that_does_not_exist_finds_nothing(
        self, rf, docs_app, monkeypatch, tmp_path
    ) -> None:
        monkeypatch.setattr(docs_app, "build_dir", tmp_path / "not-built-yet")

        assert site_search(docs_app, "quetzal", rf.get("/")) == []

    def test_an_app_the_request_has_not_mounted_finds_nothing(self, rf) -> None:
        assert site_search(quickstart_docs, "install", rf.get("/")) == []


def served_title(client, language, address="/docs/"):
    response = client.get(address, headers={"Accept-Language": language})
    assert response.status_code == 200
    return response.context["page_data"]["title"]


def built_title(translated_build, folder, path=""):
    return DocsBuild(translated_build / folder).page(path)["title"]


class TestPagesFollowTheLanguage:
    def test_a_german_reader_is_served_the_german_build(
        self, client, db, translated_app, translated_build
    ) -> None:
        assert served_title(client, "de") == built_title(translated_build, "de")

    def test_an_english_reader_is_served_the_english_build(
        self, client, db, translated_app, translated_build
    ) -> None:
        assert served_title(client, "en") == built_title(translated_build, "en")

    def test_a_regional_reader_is_served_the_build_of_that_region(
        self, client, db, translated_app, translated_build
    ) -> None:
        assert served_title(client, "pt-br") == built_title(translated_build, "pt_BR")

    def test_a_page_the_translation_left_alone_is_served_in_the_german_build(
        self, client, db, translated_app, translated_build
    ) -> None:
        title = served_title(client, "de", "/docs/untranslated/")

        assert title == built_title(translated_build, "de", "untranslated/")

    def test_the_layout_is_read_on_every_request(
        self, client, db, translated_app, translated_build, tmp_path, monkeypatch
    ) -> None:
        shutil.copytree(translated_build / "en", tmp_path / "build" / "en")
        monkeypatch.setattr(translated_app, "build_dir", tmp_path / "build")
        assert served_title(client, "de") == built_title(translated_build, "en")

        shutil.copytree(translated_build / "de", tmp_path / "build" / "de")

        assert served_title(client, "de") == built_title(translated_build, "de")

    def test_a_build_dir_holding_a_build_of_its_own_serves_it_in_every_language(
        self, client, db, translated_app, translated_build, monkeypatch
    ) -> None:
        monkeypatch.setattr(translated_app, "build_dir", translated_build / "de")

        assert served_title(client, "en") == built_title(translated_build, "de")

    def test_a_function_build_dir_is_not_given_a_language_choice(
        self, client, db, translated_app, translated_build, monkeypatch
    ) -> None:
        monkeypatch.setattr(
            translated_app, "build_dir", lambda request: translated_build / "pt_BR"
        )

        assert served_title(client, "de") == built_title(translated_build, "pt_BR")

    def test_a_reader_is_served_when_sphinx_cannot_be_imported(
        self, translated_app, translated_build
    ) -> None:
        code = (
            "import sys; sys.modules['sphinx'] = None; "
            "import django; django.setup(); "
            "from django.test import RequestFactory; "
            "from django.utils import translation; "
            "from demo.mounted import docs; "
            f"docs.build_dir = r'{translated_build}'; "
            "translation.activate('de'); "
            "print(docs.build_dir_for(RequestFactory().get('/docs/')).name)"
        )

        result = subprocess.run(  # noqa: S603 - fixed arguments
            [sys.executable, "-c", code],
            cwd=Path(__file__).parent.parent,
            env={**os.environ, "DJANGO_SETTINGS_MODULE": "tests.settings"},
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.stdout.strip() == "de", result.stderr


@pytest.fixture
def nested_app(tmp_path, monkeypatch, settings):
    """A guide whose front page lists a page that lists a page, in two languages."""
    from demo.mounted import docs

    source = tmp_path / "source"
    (source / "locales" / "de" / "LC_MESSAGES").mkdir(parents=True)
    (source / "conf.py").write_text(
        'extensions = ["mvp_sphinx.navigation"]\nlocale_dirs = ["locales"]\n'
        "gettext_compact = False\n"
    )
    (source / "index.rst").write_text("Home\n====\n\n.. toctree::\n\n   parent\n")
    (source / "parent.rst").write_text("Parent\n======\n\n.. toctree::\n\n   child\n")
    (source / "child.rst").write_text("Child\n=====\n\nText.\n")
    (source / "locales" / "de" / "LC_MESSAGES" / "child.po").write_text(
        'msgid ""\nmsgstr ""\n"Content-Type: text/plain; charset=UTF-8\\n"\n'
        '"Language: de\\n"\n\nmsgid "Child"\nmsgstr "Kind"\n'
    )
    for language in ("en", "de"):
        subprocess.run(  # noqa: S603 - fixed arguments
            [
                *(sys.executable, "-m", "sphinx", "-b", "json", "-q"),
                *("-D", f"language={language}"),
                str(source),
                str(tmp_path / "build" / language),
            ],
            check=True,
        )
    monkeypatch.setattr(docs, "build_dir", tmp_path / "build")
    monkeypatch.setattr(docs, "source_dir", source)
    settings.LANGUAGES = [("en", "English"), ("de", "German")]
    settings.LANGUAGE_CODE = "en"
    return docs


def hrefs_under(response, prefix: str) -> list[str]:
    main = BeautifulSoup(response.content, "html.parser").find("main")
    return [
        a["href"] for a in main.find_all("a", href=True) if a["href"].startswith(prefix)
    ]


def get_as(client, language: str, address: str, **query):
    return client.get(address, query, headers={"Accept-Language": language})


class TestEveryPartFollowsTheLanguage:
    def test_the_page_of_each_language_holds_its_own_text(
        self, client, db, translated_app, translated_build
    ) -> None:
        for language, folder in (("de", "de"), ("en", "en")):
            built = DocsBuild(translated_build / folder).page("page/")["body"]
            served = get_as(client, language, "/docs/page/").context["page_data"]

            assert served["body"] == built

    def test_the_two_languages_hold_different_text(
        self, client, db, translated_app
    ) -> None:
        german = get_as(client, "de", "/docs/page/").context["page_data"]["body"]
        english = get_as(client, "en", "/docs/page/").context["page_data"]["body"]

        assert german != english

    def test_an_image_and_a_download_are_served_in_each_language(
        self, client, db, translated_app, translated_build
    ) -> None:
        for language in ("de", "en"):
            html = get_as(client, language, "/docs/page/").content.decode()
            files = [
                urljoin("/docs/page/", re.search(pattern, html).group(1))
                for pattern in (
                    r'src="([^"]*_images/[^"]+)"',
                    r'href="([^"]*_downloads/[^"]+)"',
                )
            ]

            statuses = [
                get_as(client, language, address).status_code for address in files
            ]

            assert statuses == [200, 200]

    def test_a_german_search_stems_the_german_words(
        self, client, db, translated_app
    ) -> None:
        # "Katze" is the singular of the "Katzen" the German page holds.
        response = get_as(client, "de", "/docs/search/", q="Katze")

        assert hrefs_under(response, "/docs/page/") != []

    def test_an_english_reader_does_not_find_the_german_words(
        self, client, db, translated_app
    ) -> None:
        response = get_as(client, "en", "/docs/search/", q="Katzen")

        assert hrefs_under(response, "/docs/page/") == []

    def test_an_english_search_finds_the_english_page(
        self, client, db, translated_app
    ) -> None:
        response = get_as(client, "en", "/docs/search/", q="cats")

        assert hrefs_under(response, "/docs/page/") != []

    def test_the_sites_search_follows_the_language(
        self, client, db, translated_app
    ) -> None:
        kind = translated_app.search_kind
        german = get_as(client, "de", "/search/", q="Katze", kind=kind)
        english = get_as(client, "en", "/search/", q="Katze", kind=kind)

        assert hrefs_under(german, "/docs/page/") != []
        assert hrefs_under(english, "/docs/page/") == []

    def test_an_extract_is_read_from_the_readers_build(
        self, rf, translated_app, translated_build
    ) -> None:
        def extract(language):
            request = rf.get("/", headers={"Accept-Language": language})
            request.user = AnonymousUser()
            with translation.override(language):
                return translated_app.page_extract("page/", request)

        assert extract("de").content != extract("en").content

    def test_the_branch_view_lists_the_pages_of_the_readers_build(
        self, client, db, nested_app
    ) -> None:
        german = get_as(client, "de", "/docs/contents/", entry="parent/")
        english = get_as(client, "en", "/docs/contents/", entry="parent/")

        assert ("Kind" in german.content.decode()) is True
        assert "Kind" not in english.content.decode()
        assert "Child" in english.content.decode()

    def test_an_anchor_reaches_the_same_section_in_each_language(
        self, client, db, translated_app
    ) -> None:
        def anchors(language):
            body = get_as(client, language, "/docs/page/").context["page_data"]["body"]
            return re.findall(r'id="([^"]+)"', body)

        assert anchors("de") == anchors("en")

    def test_a_paragraph_the_catalogue_leaves_out_stays_in_english(
        self, client, db, translated_app
    ) -> None:
        body = get_as(client, "de", "/docs/page/").context["page_data"]["body"]

        assert "This paragraph is not translated yet." in body

    def test_the_language_can_change_between_two_requests(
        self, client, db, translated_app
    ) -> None:
        titles = [
            get_as(client, language, "/docs/").context["page_data"]["title"]
            for language in ("de", "en", "de")
        ]

        assert titles[0] == titles[2] != titles[1]


class TestFallbackThroughTheClient:
    def test_a_regional_reader_gets_the_language_without_the_region(
        self, client, db, translated_app, translated_build
    ) -> None:
        title = get_as(client, "de-at", "/docs/").context["page_data"]["title"]

        assert title == built_title(translated_build, "de")

    def test_a_reader_with_no_build_gets_the_projects_language_code(
        self, client, db, translated_app, translated_build, settings
    ) -> None:
        settings.LANGUAGE_CODE = "de"

        title = get_as(client, "it", "/docs/").context["page_data"]["title"]

        assert title == built_title(translated_build, "de")

    def test_a_reader_with_no_build_and_no_matching_code_gets_the_source_language(
        self, client, db, translated_app, translated_build, settings
    ) -> None:
        settings.LANGUAGE_CODE = "it"

        title = get_as(client, "it", "/docs/").context["page_data"]["title"]

        assert title == built_title(translated_build, "en")
