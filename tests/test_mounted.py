"""DocumentationApp is a mounted app that serves one docs build."""

import re
import shutil
from pathlib import Path
from urllib.parse import quote, urljoin

import pytest
from bs4 import BeautifulSoup
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
from mvp.menus import AppMenu
from sphinx.cmd.build import build_main

from mvp_sphinx.mounted import DocumentationApp
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
        attrs={"role": "navigation", "aria-label": str(app.name)}
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
