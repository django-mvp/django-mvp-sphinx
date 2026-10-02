"""PageView renders a page of the docs build inside the application shell."""

import json
import os
import re
import shutil
import sys
from html import unescape
from urllib.parse import urldefrag, urljoin

import pytest
from bs4 import BeautifulSoup
from django.templatetags.static import static
from django.urls import reverse

from mvp_sphinx.page_body import BodyRewriter
from tests.conftest import SPHINX_SOURCES
from tests.test_live_example import write_source

pytestmark = pytest.mark.usefixtures("docs_app")

DEFAULT_NAME = "Documentation"
FRONT_PAGE_TEXT = "Welcome to the guide"
CONTENTS_PAGES = {
    f"/docs/{address}"
    for address in (
        "",
        "install/",
        "explicit/",
        "chain/one/",
        "chain/two/",
        "chain/three/",
        "markup/",
        "shared/",
        "standalone/",
        "reference/api/",
        "hidden-page/",
    )
}
TITLE_TEXT = {
    "": "front page",
    "page/": "Top-level page",
    "section/": "section",
    "section/nested/page/": "Nested page",
}


def headings(response) -> list[str]:
    body = response.content.decode()
    return [
        re.sub(r"<[^>]+>", "", h)
        for h in re.findall(r"<h1[^>]*>(.*?)</h1>", body, re.S)
    ]


def linked_stylesheets(response) -> list[str]:
    body = response.content.decode()
    return [
        href
        for tag in re.findall(r"<link\b[^>]*>", body)
        if 'rel="stylesheet"' in tag
        for href in re.findall(r'href="([^"]+)"', tag)
    ]


def contents_links(response, app) -> list[str]:
    """Return the addresses the app's contents links to, as the page draws it."""
    soup = BeautifulSoup(response.content, "html.parser")
    contents = soup.find("ul", attrs={"aria-label": str(app.name)})
    return [link["href"] for link in contents.find_all("a")]


class TestPageView:
    def test_the_front_page_is_served_inside_the_shell(self, client, db) -> None:
        response = client.get("/docs/")

        assert response.status_code == 200
        content = response.content.decode()
        assert FRONT_PAGE_TEXT in content
        assert "<aside" in content
        assert "<main" in content

    def test_a_folders_index_page_is_served(self, client, db) -> None:
        response = client.get("/docs/section/")

        assert response.status_code == 200
        assert "The pages inside this folder" in response.content.decode()

    def test_a_nested_page_is_served(self, client, db) -> None:
        response = client.get("/docs/section/nested/page/")

        assert response.status_code == 200
        assert "Two folders down" in response.content.decode()

    @pytest.mark.parametrize("address", TITLE_TEXT)
    def test_every_page_has_one_h1_holding_its_title(self, client, db, address) -> None:
        response = client.get(f"/docs/{address}")

        found = headings(response)
        assert len(found) == 1
        assert TITLE_TEXT[address] in found[0]

    def test_every_link_in_the_front_page_body_leads_to_a_page(
        self, client, db
    ) -> None:
        response = client.get("/docs/")
        body = response.context["page_data"]["body"]
        links = [
            href
            for href in re.findall(r'href="([^"]+)"', body)
            if not href.startswith("#")
        ]

        assert len(links) >= 3
        for href in links:
            assert client.get(urljoin("/docs/", href)).status_code == 200


class TestSphinxsOwnPages:
    @pytest.mark.parametrize("address", ["/docs/genindex/"])
    def test_the_general_index_and_search_pages_are_served(
        self, client, db, docs_app, address
    ) -> None:
        assert client.get(address).status_code == 200


class TestPageTitle:
    def test_the_tab_title_is_the_pages_title_as_plain_text(self, client, db) -> None:
        response = client.get("/docs/")

        tab = re.search(r"<title>(.*?)</title>", response.content.decode(), re.S).group(
            1
        )
        assert "guide front page" in tab
        assert "<code" not in tab
        assert "&lt;" not in tab

    def test_the_tab_title_names_the_documentation(self, client, db, docs_app) -> None:
        response = client.get("/docs/")

        tab = re.search(r"<title>(.*?)</title>", response.content.decode(), re.S).group(
            1
        )
        assert str(docs_app.name) in tab


class TestBreadcrumbs:
    def test_the_front_page_shows_only_the_apps_name(
        self, client, db, docs_app
    ) -> None:
        crumbs = client.get("/docs/").context["page"]["breadcrumbs"]

        assert [(str(c["text"]), c.get("href")) for c in crumbs] == [
            (str(docs_app.name), None)
        ]

    def test_a_nested_page_links_back_through_its_parents(
        self, client, db, docs_app
    ) -> None:
        crumbs = client.get("/docs/section/nested/page/").context["page"]["breadcrumbs"]

        assert [(str(c["text"]), c.get("href")) for c in crumbs] == [
            (str(docs_app.name), "/docs/"),
            ("The section folder", "/docs/section/"),
            ("Nested page", None),
        ]


class TestServingWithoutSphinx:
    def test_a_changed_page_file_shows_on_the_next_request(
        self, client, db, docs_app, guide_build, tmp_path, monkeypatch
    ) -> None:
        build = tmp_path / "build"
        shutil.copytree(guide_build, build)
        monkeypatch.setattr(docs_app, "build_dir", build)
        assert "Welcome to the guide" in client.get("/docs/").content.decode()

        page_file = build / "index.fjson"
        page = json.loads(page_file.read_text())
        page["body"] = page["body"].replace("Welcome to the guide", "Rebuilt guide")
        page_file.write_text(json.dumps(page))

        content = client.get("/docs/").content.decode()
        assert "Rebuilt guide" in content
        assert "Welcome to the guide" not in content

    @pytest.mark.parametrize("address", ["", "section/nested/page/"])
    def test_pages_are_served_when_sphinx_cannot_be_imported(
        self, client, db, monkeypatch, address
    ) -> None:
        for name in [
            name
            for name in sys.modules
            if name == "sphinx" or name.startswith("sphinx.")
        ]:
            monkeypatch.setitem(sys.modules, name, None)

        response = client.get(f"/docs/{address}")

        assert response.status_code == 200
        assert TITLE_TEXT[address] in response.content.decode()


class TestFiles:
    @pytest.fixture
    def linked_page(self, client, db):
        return client.get("/docs/page/").context["page_data"]["body"]

    def test_the_image_a_page_links_is_served(
        self, client, db, guide_build, linked_page
    ) -> None:
        src = re.search(r'src="([^"]+)"', linked_page).group(1)

        response = client.get(urljoin("/docs/page/", src))

        assert response.status_code == 200
        assert response["Content-Type"] == "image/png"
        assert (
            b"".join(response.streaming_content)
            == (guide_build / "_images" / "pixel.png").read_bytes()
        )

    def test_the_download_a_page_links_is_served(
        self, client, db, guide_build, linked_page
    ) -> None:
        href = re.search(r'href="([^"]*_downloads/[^"]+)"', linked_page).group(1)

        response = client.get(urljoin("/docs/page/", href))

        assert response.status_code == 200
        assert (
            b"".join(response.streaming_content)
            == next((guide_build / "_downloads").glob("*/sample.txt")).read_bytes()
        )

    def test_a_missing_image_is_not_found(self, client, db) -> None:
        assert client.get("/docs/_images/missing.png").status_code == 404

    @pytest.mark.parametrize(
        "address",
        [
            "_images/../environment.pickle",
            "_images/../../outside.txt",
            "_downloads/../index.fjson",
            "_images/%2e%2e/environment.pickle",
            "_images/..%2Fenvironment.pickle",
        ],
    )
    def test_an_address_climbing_out_of_the_image_folder_is_not_found(
        self, client, db, address
    ) -> None:
        assert client.get(f"/docs/{address}").status_code == 404

    @pytest.mark.parametrize(
        "address",
        [
            "globalcontext.json",
            "searchindex.json",
            "environment.pickle",
            "index.fjson",
            "page.fjson",
            "_sources/index.rst.txt",
            "_sources/index.rst.txt/",
            "_static/basic.css",
            ".doctrees/environment.pickle",
        ],
    )
    def test_nothing_but_images_and_downloads_is_served_as_a_file(
        self, client, db, guide_build, address
    ) -> None:
        response = client.get(f"/docs/{address}")

        served = (
            b"".join(response.streaming_content)
            if response.streaming
            else response.content
        )
        assert response.status_code == 404
        assert served != (guide_build / address.rstrip("/")).read_bytes()

    def test_images_and_downloads_are_served_when_sphinx_cannot_be_imported(
        self, client, db, monkeypatch
    ) -> None:
        for name in [
            name
            for name in sys.modules
            if name == "sphinx" or name.startswith("sphinx.")
        ]:
            monkeypatch.setitem(sys.modules, name, None)

        image = client.get("/docs/_images/pixel.png")
        assert image.status_code == 200
        assert image["Content-Type"] == "image/png"
        assert client.get("/docs/page/").status_code == 200


class TestAddresses:
    def test_a_page_address_without_its_slash_redirects_permanently(
        self, client, db
    ) -> None:
        response = client.get("/docs/section/nested/page?x=1")

        assert response.status_code == 301
        assert response["Location"] == "/docs/section/nested/page/?x=1"

    def test_the_prefix_without_its_slash_redirects_with_its_query(
        self, client, db
    ) -> None:
        response = client.get("/docs?x=1")

        assert response.status_code == 301
        assert response["Location"] == "/docs/?x=1"

    def test_a_slashless_address_with_no_page_is_not_found(self, client, db) -> None:
        assert client.get("/docs/nowhere").status_code == 404

    def test_an_image_address_is_never_redirected(self, client, db) -> None:
        assert client.get("/docs/_images/pixel.png").status_code == 200

    def test_an_unknown_address_gets_the_hosts_not_found_page(self, client, db) -> None:
        inside = client.get("/docs/nowhere/")
        outside = client.get("/nowhere-at-all/")

        assert inside.status_code == outside.status_code == 404
        assert [t.name for t in inside.templates] == [t.name for t in outside.templates]
        assert "404.html" in [t.name for t in inside.templates]


class TestAddressesNamingTheDisk:
    def test_an_absolute_path_under_the_prefix_is_not_found(
        self, client, db, docs_app, guide_build
    ) -> None:
        response = client.get(
            f"/docs/{guide_build.resolve().as_posix().lstrip('/')}//section/"
        )

        assert response.status_code == 404

    def test_an_absolute_path_without_its_slash_is_not_redirected(
        self, client, db, docs_app, guide_build
    ) -> None:
        absolute = guide_build.resolve().as_posix().replace("/", "%2F")

        response = client.get(f"/docs/{absolute}%2Fsection")

        assert response.status_code == 404


class TestMissingBuild:
    @pytest.fixture
    def missing(self, docs_app, tmp_path, monkeypatch):
        build = tmp_path / "not-built-yet"
        monkeypatch.setattr(docs_app, "build_dir", build)
        return build

    def test_the_rest_of_the_site_still_answers(self, client, db, missing) -> None:
        assert client.get(reverse("overview")).status_code == 200

    @pytest.mark.parametrize(
        "address", ["/docs/", "/docs/page/", "/docs/_images/pixel.png"]
    )
    def test_documentation_addresses_are_not_found(
        self, client, db, missing, address
    ) -> None:
        assert client.get(address).status_code == 404

    def test_a_build_created_afterwards_is_served_by_the_next_request(
        self, client, db, missing, guide_build
    ) -> None:
        assert client.get("/docs/").status_code == 404

        shutil.copytree(guide_build, missing)

        assert client.get("/docs/").status_code == 200


class TestBrokenPage:
    @pytest.fixture
    def broken(self, docs_app, guide_build, tmp_path, monkeypatch):
        build = tmp_path / "broken"
        shutil.copytree(guide_build, build)
        (build / "page.fjson").write_text("{not json")
        monkeypatch.setattr(docs_app, "build_dir", build)
        return build

    def test_a_page_file_that_is_not_json_raises(self, client, db, broken) -> None:
        with pytest.raises(json.JSONDecodeError):
            client.get("/docs/page/")

    def test_a_page_file_that_is_not_json_is_a_server_error(
        self, client, db, broken
    ) -> None:
        client.raise_request_exception = False

        assert client.get("/docs/page/").status_code == 500


class TestNamingAnApp:
    def test_the_tab_carries_the_name_the_host_gave(
        self, client, db, handbook_app
    ) -> None:
        response = client.get("/manuals/admin/")

        tab = re.search(r"<title>(.*?)</title>", response.content.decode(), re.S).group(
            1
        )
        assert str(handbook_app.name) in unescape(tab)
        assert str(DEFAULT_NAME) not in unescape(tab)

    def test_the_first_breadcrumb_carries_the_name_the_host_gave(
        self, client, db, handbook_app
    ) -> None:
        crumbs = client.get("/manuals/admin/backups/").context["page"]["breadcrumbs"]

        assert str(crumbs[0]["text"]) == str(handbook_app.name)
        assert str(DEFAULT_NAME) not in [str(c["text"]) for c in crumbs]

    def test_the_front_page_breadcrumb_is_the_name_the_host_gave(
        self, client, db, handbook_app
    ) -> None:
        crumbs = client.get("/manuals/admin/").context["page"]["breadcrumbs"]

        assert [str(c["text"]) for c in crumbs] == [str(handbook_app.name)]


class TestTwoAppsSideBySide:
    def test_each_app_serves_pages_from_its_own_build(
        self, client, db, handbook_app
    ) -> None:
        assert "Start with" in client.get("/manuals/admin/").content.decode()
        assert "Welcome to the guide" in client.get("/docs/").content.decode()
        assert (
            "Welcome to the guide" not in client.get("/manuals/admin/").content.decode()
        )
        assert client.get("/manuals/admin/page/").status_code == 404
        assert client.get("/docs/backups/").status_code == 404

    def test_a_nested_page_keeps_its_breadcrumbs_within_its_own_prefix(
        self, client, db, handbook_app, docs_app
    ) -> None:
        guide = client.get("/docs/section/nested/page/").context["page"]["breadcrumbs"]
        handbook = client.get("/manuals/admin/backups/").context["page"]["breadcrumbs"]

        assert [c["href"] for c in guide if "href" in c] == ["/docs/", "/docs/section/"]
        assert [c["href"] for c in handbook if "href" in c] == ["/manuals/admin/"]

    def test_each_apps_tab_names_its_own_app(
        self, client, db, handbook_app, docs_app
    ) -> None:
        tabs = {}
        for address in ("/docs/", "/manuals/admin/"):
            body = client.get(address).content.decode()
            tabs[address] = unescape(
                re.search(r"<title>(.*?)</title>", body, re.S).group(1)
            )

        assert str(docs_app.name) in tabs["/docs/"]
        assert str(handbook_app.name) not in tabs["/docs/"]
        assert str(handbook_app.name) in tabs["/manuals/admin/"]
        assert str(docs_app.name) not in tabs["/manuals/admin/"]


class TestContentStyling:
    STYLESHEET = "mvp_sphinx/content.css"
    PAGE_STYLESHEET = "mvp_sphinx/page.css"

    def test_a_docs_page_links_the_packages_stylesheet(self, client, db) -> None:
        response = client.get("/docs/content/")

        assert static(self.STYLESHEET) in linked_stylesheets(response)

    def test_the_hosts_own_pages_do_not_link_the_stylesheet(self, client, db) -> None:
        response = client.get(reverse("overview"))

        assert static(self.STYLESHEET) not in linked_stylesheets(response)

    def test_no_stylesheet_from_the_docs_build_is_linked(self, client, db) -> None:
        response = client.get("/docs/content/")

        assert not [s for s in linked_stylesheets(response) if "_static" in s]

    @pytest.mark.parametrize("address", ["/docs/content/", "/docs/search/?q=a"])
    def test_docs_pages_link_the_page_stylesheet(self, client, db, address) -> None:
        response = client.get(address)

        assert static(self.PAGE_STYLESHEET) in linked_stylesheets(response)

    def test_the_hosts_own_pages_do_not_link_the_page_stylesheet(
        self, client, db
    ) -> None:
        response = client.get(reverse("overview"))

        assert static(self.PAGE_STYLESHEET) not in linked_stylesheets(response)


class TestWideContent:
    def test_every_table_of_a_page_is_in_a_focusable_named_region(
        self, client, db
    ) -> None:
        response = client.get("/docs/content/")

        body = response.content.decode()
        regions = re.findall(r'<div [^>]*role="region"[^>]*>', body)
        assert len(regions) == body.count("<table") == 3
        assert all('tabindex="0"' in tag and "aria-label=" in tag for tag in regions)

    def test_a_captioned_table_is_named_by_its_caption(self, client, db) -> None:
        response = client.get("/docs/content/")

        assert 'aria-label="Release schedule"' in response.content.decode()

    def test_every_equation_of_a_page_holds_one_focusable_named_region(
        self, client, db, reference_app
    ) -> None:
        response = client.get("/docs/maths/")

        soup = BeautifulSoup(response.content.decode(), "html.parser")
        equations = soup.select("div.math")
        assert len(equations) == 3
        for equation in equations:
            regions = equation.select('[role="region"]')
            assert len(regions) == 1
            assert regions[0]["tabindex"] == "0"
            assert regions[0]["aria-label"]
            assert regions[0].find_parent("div", class_="math") is equation


class TestHeadingLinks:
    HEADING_LINK = re.compile(
        r"<(?:h[1-6]|dt)\b[^>]*>"
        r"(?P<held>(?:(?!<h[1-6]\b|<dt\b|<a\b[^>]*headerlink).)*?)"
        r"<a\b(?P<attributes>[^>]*\bheaderlink\b[^>]*)>",
        re.S,
    )

    def page(self, client) -> str:
        return client.get("/docs/content/").content.decode()

    def links(self, body: str) -> list[tuple[str, dict[str, str]]]:
        return [
            (
                re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", "", match["held"]))),
                dict(re.findall(r'([\w-]+)="([^"]*)"', match["attributes"])),
            )
            for match in self.HEADING_LINK.finditer(body)
        ]

    def test_every_heading_link_of_a_page_is_named_by_its_headings_text(
        self, client, db
    ) -> None:
        links = self.links(self.page(client))

        assert len(links) >= 5
        for text, attributes in links:
            assert unescape(attributes["aria-label"]).endswith(text.strip())

    def test_a_heading_link_leads_to_an_anchor_on_the_page(self, client, db) -> None:
        body = self.page(client)

        for link in self.links(body):
            attributes = link[1]
            assert attributes["href"].startswith("#")
            assert f'id="{attributes["href"][1:]}"' in body

    def test_no_two_heading_links_of_a_page_share_a_name(self, client, db) -> None:
        names = [
            attributes["aria-label"]
            for text, attributes in self.links(self.page(client))
        ]

        assert len(names) == len(set(names))

    def test_the_link_of_a_heading_with_code_and_an_ampersand_is_named_by_them(
        self, client, db
    ) -> None:
        names = [unescape(a["aria-label"]) for _, a in self.links(self.page(client))]

        assert any(name.endswith("Using run() & friends") for name in names)

    def test_a_glossary_terms_link_is_named_by_the_term(self, client, db) -> None:
        links = {a["href"]: a for _, a in self.links(self.page(client))}

        assert links["#term-widget"]["aria-label"].endswith("widget")


class TestContentsInTheSidebar:
    def test_every_link_answers_and_together_they_reach_every_listed_page(
        self, client, db, contents_app
    ) -> None:
        links = contents_links(client.get("/docs/"), contents_app)

        assert {*links} == CONTENTS_PAGES
        for link in links:
            assert client.get(link).status_code == 200

    @pytest.mark.parametrize("address", ["", "chain/three/", "reference/api/"])
    def test_any_page_draws_the_whole_contents(
        self, client, db, contents_app, address
    ) -> None:
        links = contents_links(client.get(f"/docs/{address}"), contents_app)

        assert {*links} == CONTENTS_PAGES

    def test_a_title_with_markup_characters_is_escaped(
        self, client, db, contents_app
    ) -> None:
        soup = BeautifulSoup(client.get("/docs/").content, "html.parser")
        contents = soup.find("ul", attrs={"aria-label": str(contents_app.name)})

        link = contents.find("a", href="/docs/markup/")

        assert link.get_text(strip=True) == "Fish <b>& chips</b>"
        assert link.find("b") is None

    def test_a_second_app_draws_its_own_contents_under_its_own_prefix(
        self, client, db, handbook_app, docs_app
    ) -> None:
        links = contents_links(client.get("/manuals/admin/backups/"), handbook_app)

        assert {*links} == {"/manuals/admin/", "/manuals/admin/backups/"}

    def test_a_page_of_one_app_draws_none_of_the_others_entries(
        self, client, db, handbook_app, docs_app
    ) -> None:
        sidebar = BeautifulSoup(client.get("/docs/page/").content, "html.parser").find(
            "aside"
        )

        hrefs = [link["href"] for link in sidebar.find_all("a", href=True)]

        assert "/docs/page/" in hrefs
        assert not [href for href in hrefs if href.startswith("/manuals/admin/")]

    def test_the_contents_is_drawn_when_sphinx_cannot_be_imported(
        self, client, db, contents_app, monkeypatch
    ) -> None:
        for name in [
            name
            for name in sys.modules
            if name == "sphinx" or name.startswith("sphinx.")
        ]:
            monkeypatch.setitem(sys.modules, name, None)

        links = contents_links(client.get("/docs/chain/two/"), contents_app)

        assert {*links} == CONTENTS_PAGES


class TestRebuiltContents:
    @pytest.fixture
    def rebuilt(self, contents_app, contents_build, tmp_path, monkeypatch):
        build = tmp_path / "rebuilt"
        shutil.copytree(contents_build, build)
        monkeypatch.setattr(contents_app, "build_dir", build)
        return build

    @staticmethod
    def rewrite(build, edit) -> None:
        target = build / "navigation.json"
        data = json.loads(target.read_text())
        edit(data["groups"])
        target.write_text(json.dumps(data))

    def test_a_page_added_by_a_rebuild_is_in_the_sidebar_on_the_next_request(
        self, client, db, contents_app, rebuilt
    ) -> None:
        assert "/docs/added/" not in contents_links(client.get("/docs/"), contents_app)

        self.rewrite(
            rebuilt,
            lambda groups: groups[1]["entries"].append(
                {"title": "Added", "url": "added/", "children": []}
            ),
        )

        assert "/docs/added/" in contents_links(client.get("/docs/"), contents_app)

    def test_a_page_removed_by_a_rebuild_is_gone_on_the_next_request(
        self, client, db, contents_app, rebuilt
    ) -> None:
        assert "/docs/standalone/" in contents_links(client.get("/docs/"), contents_app)

        self.rewrite(rebuilt, lambda groups: groups[1]["entries"].clear())

        assert "/docs/standalone/" not in contents_links(
            client.get("/docs/"), contents_app
        )


class TestContentsUnavailable:
    @pytest.fixture
    def rebuilt(self, contents_app, contents_build, tmp_path, monkeypatch):
        build = tmp_path / "rebuilt"
        shutil.copytree(contents_build, build)
        monkeypatch.setattr(contents_app, "build_dir", build)
        return build

    def test_a_build_without_a_navigation_file_serves_its_pages_with_the_front_page_only(
        self, client, db, contents_app, rebuilt
    ) -> None:
        (rebuilt / "navigation.json").unlink()

        response = client.get("/docs/chain/two/")

        assert response.status_code == 200
        assert contents_links(response, contents_app) == ["/docs/"]

    @pytest.mark.parametrize(
        "content",
        [
            "{not json",
            "[]",
            '{"groups": "x"}',
            '{"groups": [{"caption": 1, "entries": []}]}',
            '{"groups": [{"caption": "", "entries": [{"title": "T"}]}]}',
        ],
    )
    def test_a_navigation_file_that_cannot_be_used_gives_the_front_page_only(
        self, client, db, contents_app, rebuilt, content
    ) -> None:
        (rebuilt / "navigation.json").write_text(content)

        response = client.get("/docs/chain/two/")

        assert response.status_code == 200
        assert contents_links(response, contents_app) == ["/docs/"]

    @pytest.mark.skipif(os.geteuid() == 0, reason="root reads any file")
    def test_an_unreadable_navigation_file_gives_the_front_page_only(
        self, client, db, contents_app, rebuilt
    ) -> None:
        (rebuilt / "navigation.json").chmod(0o000)

        response = client.get("/docs/chain/two/")

        assert response.status_code == 200
        assert contents_links(response, contents_app) == ["/docs/"]

    def test_a_missing_build_leaves_the_hosts_own_pages_and_menu_drawn(
        self, client, db, contents_app, tmp_path, monkeypatch
    ) -> None:
        monkeypatch.setattr(contents_app, "build_dir", tmp_path / "not-built-yet")

        response = client.get(reverse("overview"))

        sidebar = BeautifulSoup(response.content, "html.parser").find("aside")
        assert response.status_code == 200
        assert {link["href"] for link in sidebar.find_all("a", href=True)} >= {
            reverse("overview"),
            "/docs/",
        }

    @pytest.mark.skipif(os.geteuid() == 0, reason="root reads any file")
    def test_an_unreadable_navigation_file_leaves_the_hosts_own_pages_and_menu_drawn(
        self, client, db, rebuilt
    ) -> None:
        (rebuilt / "navigation.json").chmod(0o000)

        response = client.get(reverse("overview"))

        sidebar = BeautifulSoup(response.content, "html.parser").find("aside")
        assert response.status_code == 200
        assert reverse("overview") in {
            link["href"] for link in sidebar.find_all("a", href=True)
        }

    def test_a_file_broken_mid_run_gives_the_front_page_only_until_it_is_fixed(
        self, client, db, contents_app, rebuilt
    ) -> None:
        target = rebuilt / "navigation.json"
        good = target.read_text()
        full = contents_links(client.get("/docs/"), contents_app)

        target.write_text("garbage that is not json")
        broken = contents_links(client.get("/docs/"), contents_app)

        target.write_text(good)
        fixed = contents_links(client.get("/docs/"), contents_app)

        assert (broken, fixed) == (["/docs/"], full)
        assert {*full} == CONTENTS_PAGES


SEARCH_PAGES = [
    "",
    "lanterns/",
    "products/",
    "sections/",
    "metals/",
    "coins/",
    "spoons/",
    "markup/",
    "wombat/",
    "folder/",
    "folder/inner/",
]
LANTERN_HREFS = [
    "/docs/",
    "/docs/coins/",
    "/docs/lanterns/",
    "/docs/metals/",
    "/docs/products/",
]


def search_form(response):
    return BeautifulSoup(response.content, "html.parser").find("form", role="search")


def query_field(response):
    return search_form(response).find("input", attrs={"name": "q"})


def result_hrefs(response) -> list[str]:
    soup = BeautifulSoup(response.content, "html.parser")
    section = soup.find("main").find("section", attrs={"aria-labelledby": True})
    if section is None:
        return []
    assert soup.find(id=section["aria-labelledby"]) is not None
    return [link["href"] for link in section.select("ol a[href]")]


def submit_search(client, response, query):
    form = search_form(response)
    return client.get(form["action"], {form.find("input")["name"]: query})


class TestSearchForm:
    @pytest.mark.parametrize("path", SEARCH_PAGES)
    def test_every_page_of_the_app_offers_a_search_of_the_app(
        self, client, db, search_app, path
    ) -> None:
        form = search_form(client.get(f"/docs/{path}"))

        assert form is not None
        assert form["method"].lower() == "get"
        assert form["action"] == reverse(f"{search_app.namespace}:search")
        assert form.find("input", attrs={"name": "q"}) is not None

    def test_the_results_page_offers_the_search_again(
        self, client, db, search_app
    ) -> None:
        form = search_form(client.get("/docs/search/"))

        assert form["action"] == "/docs/search/"

    def test_the_search_input_has_a_label(self, client, db, search_app) -> None:
        form = search_form(client.get("/docs/"))
        field = form.find("input", attrs={"name": "q"})

        assert form.find("label", attrs={"for": field["id"]}) is not None

    def test_a_page_of_the_host_offers_no_search(self, client, db, search_app) -> None:
        assert search_form(client.get(reverse("overview"))) is None

    def test_a_second_app_offers_a_search_of_its_own(
        self, client, db, handbook_app
    ) -> None:
        form = search_form(client.get("/manuals/admin/"))

        assert form["action"] == "/manuals/admin/search/"


class TestSearchResults:
    def test_a_word_lists_the_pages_holding_it_inside_the_shell(
        self, client, db, search_app
    ) -> None:
        response = submit_search(client, client.get("/docs/"), "quetzal")

        assert response.status_code == 200
        content = response.content.decode()
        assert "<aside" in content
        assert "<main" in content
        assert result_hrefs(response) == ["/docs/lanterns/"]

    def test_a_word_on_several_pages_lists_each_once(
        self, client, db, search_app
    ) -> None:
        response = submit_search(client, client.get("/docs/coins/"), "lantern")

        assert sorted(result_hrefs(response)) == LANTERN_HREFS

    def test_every_result_leads_to_a_page_of_the_app(
        self, client, db, search_app
    ) -> None:
        response = submit_search(client, client.get("/docs/"), "lantern")

        for href in result_hrefs(response):
            assert href.startswith("/docs/")
            assert client.get(href).status_code == 200

    def test_several_words_list_only_pages_holding_all_of_them(
        self, client, db, search_app
    ) -> None:
        response = submit_search(client, client.get("/docs/"), "copper silver")

        assert result_hrefs(response) == ["/docs/metals/"]

    def test_the_same_address_gives_the_same_search_and_results(
        self, client, db, search_app
    ) -> None:
        first = client.get("/docs/search/", {"q": "lantern"})
        second = client.get("/docs/search/", {"q": "lantern"})

        assert result_hrefs(first) == result_hrefs(second) != []
        assert query_field(first)["value"] == query_field(second)["value"] == "lantern"

    @pytest.mark.parametrize("query", ["nothingmatchesthis", "", "   ", "?!"])
    def test_a_search_finding_nothing_says_so_and_offers_the_search(
        self, client, db, search_app, query
    ) -> None:
        response = client.get("/docs/search/", {"q": query})
        soup = BeautifulSoup(response.content, "html.parser")

        assert response.status_code == 200
        assert result_hrefs(response) == []
        assert soup.find("main").find(attrs={"role": "status"}) is not None
        assert query_field(response)["value"] == query

    def test_a_page_with_no_query_at_all_lists_nothing(
        self, client, db, search_app
    ) -> None:
        response = client.get("/docs/search/")

        assert response.status_code == 200
        assert result_hrefs(response) == []

    def test_the_readers_text_comes_back_escaped(self, client, db, search_app) -> None:
        query = '<script>alert("x")</script> & "quoted"'

        response = client.get("/docs/search/", {"q": query})
        content = response.content.decode()

        assert '<script>alert("x")' not in content
        assert "&lt;script&gt;" in content
        assert query_field(response)["value"] == query

    def test_a_titles_markup_characters_come_back_escaped(
        self, client, db, search_app
    ) -> None:
        response = client.get("/docs/search/", {"q": "escapist"})

        assert "<chips>" not in response.content.decode()
        assert result_hrefs(response) == ["/docs/markup/"]

    def test_the_fronts_link_to_sphinxs_search_page_leads_to_the_apps_search(
        self, client, db, search_app
    ) -> None:
        front = BeautifulSoup(client.get("/docs/").content, "html.parser")
        links = {
            urljoin("/docs/", link["href"])
            for link in front.find("article").find_all("a", href=True)
        }

        assert reverse(f"{search_app.namespace}:search") in links
        assert client.get(reverse(f"{search_app.namespace}:search")).status_code == 200

    def test_a_word_only_in_the_hosts_pages_lists_nothing(
        self, client, db, search_app
    ) -> None:
        word = "demonstration"
        assert word in client.get(reverse("overview")).content.decode()

        response = client.get("/docs/search/", {"q": word})

        assert result_hrefs(response) == []


def result_items(response):
    soup = BeautifulSoup(response.content, "html.parser")
    section = soup.find("main").find("section", attrs={"aria-labelledby": True})
    return section.select("ol > li") if section else []


class TestSearchResultDetails:
    def test_the_page_titled_with_the_word_is_listed_before_pages_that_mention_it(
        self, client, db, search_app
    ) -> None:
        response = client.get("/docs/search/", {"q": "lantern"})

        assert result_hrefs(response)[0] == "/docs/lanterns/"
        assert sorted(result_hrefs(response)) == LANTERN_HREFS

    def test_a_result_shows_the_pages_title_as_plain_text(
        self, client, db, search_app
    ) -> None:
        (item,) = result_items(client.get("/docs/search/", {"q": "escapist"}))

        assert item.find("a").get_text() == "Fish & <chips>"
        assert item.find("chips") is None

    def test_a_result_shows_a_passage_holding_the_word_without_markup_or_permalink(
        self, client, db, search_app
    ) -> None:
        (item,) = result_items(client.get("/docs/search/", {"q": "quetzal"}))
        passage = item.find("p")

        assert "quetzal" in passage.get_text()
        assert "¶" not in item.get_text()
        assert passage.find(True) is None

    def test_markup_characters_in_a_passage_come_back_escaped(
        self, client, db, search_app
    ) -> None:
        response = client.get("/docs/search/", {"q": "escapist"})
        (item,) = result_items(response)

        assert "<em>" in item.find("p").get_text()
        assert item.find("em") is None
        assert "&lt;em&gt;" in response.content.decode()

    def test_a_word_in_a_section_heading_leads_to_that_section(
        self, client, db, search_app
    ) -> None:
        (href,) = result_hrefs(client.get("/docs/search/", {"q": "gasket"}))
        page, _, anchor = href.partition("#")

        assert page == "/docs/sections/"
        assert anchor
        target = BeautifulSoup(client.get(page).content, "html.parser")
        assert target.find(id=anchor) is not None

    def test_a_word_in_the_title_leads_to_the_page_itself(
        self, client, db, search_app
    ) -> None:
        assert result_hrefs(client.get("/docs/search/", {"q": "marsupials"})) == [
            "/docs/wombat/"
        ]

    def test_a_title_only_match_lists_the_page_without_a_passage(
        self, client, db, search_app
    ) -> None:
        (item,) = result_items(client.get("/docs/search/", {"q": "marsupials"}))

        assert item.find("a")["href"] == "/docs/wombat/"
        assert item.find("p") is None

    def test_a_page_whose_file_is_missing_is_listed_without_a_passage(
        self, client, db, search_app, tmp_path, monkeypatch
    ) -> None:
        build = tmp_path / "missing-page"
        shutil.copytree(search_app.build_dir, build)
        (build / "wombat.fjson").unlink()
        monkeypatch.setattr(search_app, "build_dir", build)

        response = client.get("/docs/search/", {"q": "koala"})

        assert response.status_code == 200
        (item,) = result_items(response)
        assert item.find("a")["href"] == "/docs/wombat/"
        assert item.find("p") is None


def status_text(response) -> str:
    soup = BeautifulSoup(response.content, "html.parser")
    return soup.find("main").find(attrs={"role": "status"}).get_text(strip=True)


class TestSearchAfterARebuild:
    def test_a_word_added_by_a_rebuild_is_searchable_on_the_next_request(
        self, client, db, search_app, sphinx_build, tmp_path, monkeypatch
    ) -> None:
        source = tmp_path / "source"
        shutil.copytree(SPHINX_SOURCES / "search", source)
        monkeypatch.setattr(search_app, "build_dir", sphinx_build(source))
        assert result_hrefs(client.get("/docs/search/", {"q": "mongoose"})) == []

        (source / "mongooses.rst").write_text("Newcomers\n=========\n\nA mongoose.\n")
        index = source / "index.rst"
        index.write_text(
            index.read_text().replace("   lanterns\n", "   lanterns\n   mongooses\n")
        )
        assert sphinx_build(source) == search_app.build_dir

        assert result_hrefs(client.get("/docs/search/", {"q": "mongoose"})) == [
            "/docs/mongooses/"
        ]


class TestTwoApps:
    @pytest.fixture
    def shared_word(self, handbook_app, sphinx_build, tmp_path, monkeypatch):
        source = tmp_path / "handbook"
        shutil.copytree(SPHINX_SOURCES / "handbook", source)
        page = source / "backups.rst"
        page.write_text(page.read_text() + "\nA lantern hangs above the shelf.\n")
        monkeypatch.setattr(handbook_app, "build_dir", sphinx_build(source))
        return "lantern"

    def test_a_word_common_to_both_lists_only_the_searched_apps_pages(
        self, client, db, search_app, handbook_app, shared_word
    ) -> None:
        guide = result_hrefs(client.get("/docs/search/", {"q": shared_word}))
        handbook = result_hrefs(
            client.get("/manuals/admin/search/", {"q": shared_word})
        )

        assert sorted(guide) == LANTERN_HREFS
        assert handbook == ["/manuals/admin/backups/"]

    def test_each_apps_form_submits_to_its_own_search(
        self, client, db, search_app, handbook_app, shared_word
    ) -> None:
        response = client.get("/manuals/admin/search/", {"q": shared_word})

        assert search_form(response)["action"] == "/manuals/admin/search/"
        assert query_field(response)["value"] == shared_word


class TestUnavailableSearch:
    @pytest.fixture
    def rebuilt(self, search_app, search_build, tmp_path, monkeypatch):
        build = tmp_path / "rebuilt"
        shutil.copytree(search_build, build)
        monkeypatch.setattr(search_app, "build_dir", build)
        return build

    @pytest.fixture
    def nothing_matched(self, client, db, search_app):
        return status_text(client.get("/docs/search/", {"q": "nothingmatchesthis"}))

    @pytest.mark.parametrize("query", ["lantern", ""])
    def test_a_build_without_search_data_says_search_is_unavailable(
        self, client, db, rebuilt, nothing_matched, query
    ) -> None:
        (rebuilt / "searchindex.json").unlink()

        response = client.get("/docs/search/", {"q": query})

        assert response.status_code == 200
        assert result_hrefs(response) == []
        assert status_text(response) != nothing_matched

    @pytest.mark.parametrize("content", ["{not json", "[]", "{}", '{"docnames": 5}'])
    def test_search_data_that_is_not_valid_says_search_is_unavailable(
        self, client, db, rebuilt, nothing_matched, content
    ) -> None:
        (rebuilt / "searchindex.json").write_text(content)

        response = client.get("/docs/search/", {"q": "lantern"})

        assert response.status_code == 200
        assert status_text(response) != nothing_matched

    @pytest.mark.parametrize("path", SEARCH_PAGES)
    def test_the_pages_are_still_served(self, client, db, rebuilt, path) -> None:
        (rebuilt / "searchindex.json").unlink()

        assert client.get(f"/docs/{path}").status_code == 200

    def test_the_search_form_is_still_offered(self, client, db, rebuilt) -> None:
        (rebuilt / "searchindex.json").unlink()

        response = client.get("/docs/search/", {"q": "lantern"})

        assert query_field(response)["value"] == "lantern"


class TestSearchOfAMissingBuild:
    @pytest.fixture
    def missing(self, handbook_app, tmp_path, monkeypatch):
        monkeypatch.setattr(handbook_app, "build_dir", tmp_path / "not-built-yet")

    def test_the_search_address_answers_as_a_page_address_does(
        self, client, db, missing
    ) -> None:
        page = client.get("/manuals/admin/backups/")
        search = client.get("/manuals/admin/search/", {"q": "lantern"})

        assert page.status_code == search.status_code == 404

    def test_the_rest_of_the_site_still_answers(self, client, db, missing) -> None:
        assert client.get(reverse("overview")).status_code == 200


class TestSearchWithoutSphinx:
    def test_a_search_gives_the_same_results_when_sphinx_cannot_be_imported(
        self, client, db, search_app, monkeypatch
    ) -> None:
        expected = result_hrefs(client.get("/docs/search/", {"q": "lantern"}))
        assert expected

        for name in [
            name
            for name in sys.modules
            if name == "sphinx" or name.startswith("sphinx.")
        ]:
            monkeypatch.setitem(sys.modules, name, None)

        response = client.get("/docs/search/", {"q": "lantern"})

        assert response.status_code == 200
        assert result_hrefs(response) == expected


class TestSearchOfAVeryLongQuery:
    @pytest.mark.parametrize(
        "query",
        ["a" * 5000, "word " * 1000, "lantern " * 625],
        ids=["one-word", "many-words", "repeated-word"],
    )
    def test_a_query_of_five_thousand_characters_is_answered(
        self, client, db, search_app, query
    ) -> None:
        response = client.get("/docs/search/", {"q": query})

        assert response.status_code == 200
        assert query_field(response)["value"] == query


class TestOnThisPage:
    @staticmethod
    def soup(client, address: str) -> BeautifulSoup:
        return BeautifulSoup(client.get(f"/docs/{address}").content, "html.parser")

    @staticmethod
    def on_this_page(soup: BeautifulSoup):
        return soup.find("nav", attrs={"aria-labelledby": True})

    def test_a_page_with_sections_lists_them_in_a_named_navigation_region(
        self, client, db, reading_app
    ) -> None:
        soup = self.soup(client, "")

        nav = self.on_this_page(soup)

        assert soup.find(id=nav["aria-labelledby"]).get_text(strip=True)
        assert [link["href"] for link in nav.find_all("a")] == [
            "#first-part",
            "#second-part",
            "#a-sub-section",
        ]

    def test_a_sub_section_is_listed_inside_its_parents_entry(
        self, client, db, reading_app
    ) -> None:
        nav = self.on_this_page(self.soup(client, ""))

        entry = nav.find("a", href="#a-sub-section").find_parent("li")
        parent = entry.find_parent("li")

        assert entry.find_parent("ul").parent is parent
        assert parent.find("a")["href"] == "#second-part"

    @pytest.mark.parametrize("address", ["", "long/", "single/"])
    def test_every_link_leads_to_a_heading_in_the_pages_article(
        self, client, db, reading_app, address
    ) -> None:
        soup = self.soup(client, address)
        article = soup.find("article")

        links = self.on_this_page(soup).find_all("a")

        assert links
        for link in links:
            assert link["href"].startswith("#")
            assert article.find(id=link["href"][1:]) is not None

    @pytest.mark.parametrize("address", ["", "long/", "single/"])
    def test_no_link_leads_to_the_pages_own_title(
        self, client, db, reading_app, address
    ) -> None:
        links = self.on_this_page(self.soup(client, address)).find_all("a")

        assert "#" not in [link["href"] for link in links]

    def test_a_page_with_no_section_has_no_such_region(
        self, client, db, reading_app
    ) -> None:
        assert self.on_this_page(self.soup(client, "plain/")) is None

    def test_the_front_page_lists_none_of_the_headings_of_the_pages_it_lists(
        self, client, db, reading_app
    ) -> None:
        nav = self.on_this_page(self.soup(client, ""))

        hrefs = {link["href"] for link in nav.find_all("a")}

        assert hrefs.isdisjoint(
            {"#level-one", "#the-code-heading", "#the-only-section"}
        )

    def test_the_regions_name_differs_from_the_contents_name(
        self, client, db, reading_app
    ) -> None:
        soup = self.soup(client, "")
        nav = self.on_this_page(soup)

        name = soup.find(id=nav["aria-labelledby"]).get_text(strip=True)

        assert name != str(reading_app.name)
        assert soup.find("ul", attrs={"aria-label": str(reading_app.name)})

    def test_a_page_with_one_section_lists_one_link(
        self, client, db, reading_app
    ) -> None:
        nav = self.on_this_page(self.soup(client, "single/"))

        assert [link["href"] for link in nav.find_all("a")] == ["#the-only-section"]

    def test_a_heading_with_inline_code_keeps_its_markup(
        self, client, db, reading_app
    ) -> None:
        nav = self.on_this_page(self.soup(client, "long/"))

        link = nav.find("a", href="#the-code-heading")

        assert link.find("code") is not None

    def test_the_list_is_drawn_when_sphinx_cannot_be_imported(
        self, client, db, reading_app, monkeypatch
    ) -> None:
        for name in [
            name
            for name in sys.modules
            if name == "sphinx" or name.startswith("sphinx.")
        ]:
            monkeypatch.setitem(sys.modules, name, None)

        nav = self.on_this_page(self.soup(client, "long/"))

        assert nav.find("a", href="#level-three") is not None


class TestPreviousAndNextPage:
    @staticmethod
    def soup(client, address: str) -> BeautifulSoup:
        return BeautifulSoup(client.get(f"/docs/{address}").content, "html.parser")

    @staticmethod
    def at(client, href: str) -> BeautifulSoup:
        return BeautifulSoup(client.get(href).content, "html.parser")

    @staticmethod
    def link(soup: BeautifulSoup, rel: str):
        return soup.find("a", rel=rel)

    @staticmethod
    def title_of(client, href: str) -> str:
        return client.get(href).context["page_data"]["title"]

    def test_a_middle_page_links_to_both_neighbours_in_a_named_region(
        self, client, db, reading_app
    ) -> None:
        soup = self.soup(client, "long/")

        previous = self.link(soup, "prev")
        following = self.link(soup, "next")

        assert previous["href"] == "/docs/"
        assert following["href"] == "/docs/single/"
        assert previous.find_parent("nav")["aria-label"]
        assert previous.find_parent("nav") is following.find_parent("nav")

    def test_each_link_holds_the_title_of_the_page_it_leads_to(
        self, client, db, reading_app
    ) -> None:
        soup = self.soup(client, "long/")

        for rel in ("prev", "next"):
            link = self.link(soup, rel)
            assert self.title_of(client, link["href"]) in link.get_text()

    def test_the_front_page_has_a_next_link_and_no_previous_link(
        self, client, db, reading_app
    ) -> None:
        soup = self.soup(client, "")

        assert self.link(soup, "next")["href"] == "/docs/long/"
        assert self.link(soup, "prev") is None

    def test_the_last_page_has_a_previous_link_and_no_next_link(
        self, client, db, reading_app
    ) -> None:
        soup = self.soup(client, "plain/")

        assert self.link(soup, "prev")["href"] == "/docs/single/"
        assert self.link(soup, "next") is None

    def test_the_page_after_the_front_page_links_back_to_the_apps_own_address(
        self, client, db, reading_app
    ) -> None:
        assert self.link(self.soup(client, "long/"), "prev")["href"] == "/docs/"

    def test_a_build_of_one_page_has_neither_link(
        self, client, db, docs_app, sphinx_build, tmp_path, monkeypatch
    ) -> None:
        source = tmp_path / "source"
        source.mkdir()
        (source / "conf.py").write_text('project = "One"\n')
        (source / "index.rst").write_text("Only page\n=========\n\nAlone.\n")
        monkeypatch.setattr(docs_app, "build_dir", sphinx_build(source))

        soup = self.soup(client, "")

        assert self.link(soup, "prev") is None
        assert self.link(soup, "next") is None

    def test_following_next_links_from_the_front_page_visits_every_listed_page(
        self, client, db, reading_app
    ) -> None:
        listed = contents_links(client.get("/docs/"), reading_app)
        visited = ["/docs/"]
        while following := self.link(self.at(client, visited[-1]), "next"):
            visited.append(following["href"])

        assert sorted(visited) == sorted(listed)

        back = [visited[-1]]
        while previous := self.link(self.at(client, back[-1]), "prev"):
            back.append(previous["href"])

        assert back == visited[::-1]

    def test_a_page_of_a_hidden_toctree_is_linked_from_its_neighbour(
        self, client, db, contents_app
    ) -> None:
        previous = self.link(self.soup(client, "hidden-page/"), "prev")["href"]

        assert previous == "/docs/reference/api/"
        assert self.link(self.at(client, previous), "next")["href"] == (
            "/docs/hidden-page/"
        )

    def test_an_orphan_page_has_neither_link(self, client, db, contents_app) -> None:
        response = client.get("/docs/orphan/")
        soup = BeautifulSoup(response.content, "html.parser")

        assert response.status_code == 200
        assert self.link(soup, "prev") is None
        assert self.link(soup, "next") is None

    def test_a_second_app_links_under_its_own_prefix(
        self, client, db, handbook_app
    ) -> None:
        front = BeautifulSoup(client.get("/manuals/admin/").content, "html.parser")
        backups = BeautifulSoup(
            client.get("/manuals/admin/backups/").content, "html.parser"
        )

        assert self.link(front, "next")["href"] == "/manuals/admin/backups/"
        assert self.link(backups, "prev")["href"] == "/manuals/admin/"

    def test_sphinxs_general_index_has_neither_link(
        self, client, db, reading_app
    ) -> None:
        response = client.get("/docs/genindex/")
        soup = BeautifulSoup(response.content, "html.parser")

        assert response.status_code == 200
        assert self.link(soup, "prev") is None
        assert self.link(soup, "next") is None

    def test_the_links_are_drawn_when_sphinx_cannot_be_imported(
        self, client, db, reading_app, monkeypatch
    ) -> None:
        for name in [
            name
            for name in sys.modules
            if name == "sphinx" or name.startswith("sphinx.")
        ]:
            monkeypatch.setitem(sys.modules, name, None)

        soup = self.soup(client, "long/")

        assert self.link(soup, "prev") is not None
        assert self.link(soup, "next") is not None


class TestReadingAfterARebuild:
    @pytest.fixture
    def rebuilt(self, docs_app, tmp_path, sphinx_build, monkeypatch):
        source = tmp_path / "source"
        shutil.copytree(SPHINX_SOURCES / "reading", source)
        monkeypatch.setattr(docs_app, "build_dir", sphinx_build(source))

        def rebuild() -> None:
            index = source / "index.rst"
            index.write_text(
                index.read_text().replace("   long\n", "   inserted\n   long\n")
                + "\nAdded part\n----------\n\nText of the added part.\n"
            )
            (source / "inserted.rst").write_text("Inserted page\n=============\n")
            sphinx_build(source)

        return rebuild

    @staticmethod
    def front_page(client) -> BeautifulSoup:
        return BeautifulSoup(client.get("/docs/").content, "html.parser")

    def test_a_section_added_by_a_rebuild_is_listed_on_the_next_request(
        self, client, db, rebuilt
    ) -> None:
        assert self.front_page(client).find("a", href="#added-part") is None

        rebuilt()

        assert self.front_page(client).find("a", href="#added-part") is not None

    def test_a_page_inserted_by_a_rebuild_is_the_next_link_on_the_next_request(
        self, client, db, rebuilt
    ) -> None:
        assert self.front_page(client).find("a", rel="next")["href"] == "/docs/long/"

        rebuilt()

        assert self.front_page(client).find("a", rel="next")["href"] == (
            "/docs/inserted/"
        )


class TestEntryLinks:
    @pytest.fixture
    def page(self, client, db, reference_app) -> BeautifulSoup:
        response = client.get("/docs/api/")
        return BeautifulSoup(response.content, "html.parser")

    def test_every_entry_holds_a_heading_link_to_itself(self, page) -> None:
        entries = page.select("dt.sig-object[id]")

        assert entries
        for each in entries:
            link = each.select_one("a.headerlink")
            assert link["href"] == f"#{each['id']}"

    def test_every_entry_link_has_a_name(self, page) -> None:
        links = [each.select_one("a.headerlink") for each in page.select("dt[id]")]

        assert links
        assert all(link["aria-label"] for link in links)

    def test_no_two_heading_links_of_the_page_share_a_name(self, page) -> None:
        names = [link["aria-label"] for link in page.select("a.headerlink")]

        assert len(names) > len(page.select("dt.sig-object[id]"))
        assert len(names) == len(set(names))

    def test_a_reference_in_a_description_leads_to_an_entry_on_the_page(
        self, page
    ) -> None:
        description = page.select_one(
            'dt[id="demo.links.page_address"]'
        ).find_next_sibling("dd")

        link = description.select_one("a.reference.internal[href]")
        assert page.find("dt", id=urldefrag(link["href"])[1])


class TestMaths:
    SETTINGS_FILE = "mvp_sphinx/maths.js"
    NOTATIONS = [
        r"\(a^2 + b^2 = c^2\)",
        r"\[e^{i\pi} + 1 = 0\]",
        r"\[x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}\]",
        r"\[\sum_{k=1}^{n} k = \frac{n(n+1)}{2}\]",
    ]
    PLACES = {
        "note": ".admonition.note",
        "table cell": "table td",
        "list item": "ul li",
        "heading": "h2",
    }

    @staticmethod
    def scripts(response) -> list[dict[str, str]]:
        soup = BeautifulSoup(response.content.decode(), "html.parser")
        return [
            {**tag.attrs, "src": tag["src"]}
            for tag in soup.find_all("script", src=True)
        ]

    def settings_scripts(self, response) -> list[dict[str, str]]:
        return [
            tag
            for tag in self.scripts(response)
            if tag["src"] == static(self.SETTINGS_FILE)
        ]

    def library_scripts(self, response) -> list[dict[str, str]]:
        return [
            tag for tag in self.scripts(response) if "cdn.jsdelivr.net" in tag["src"]
        ]

    def test_a_page_with_maths_loads_the_settings_then_the_library(
        self, client, db, reference_app
    ) -> None:
        response = client.get("/docs/maths/")

        settings, library = (
            self.settings_scripts(response),
            self.library_scripts(response),
        )
        assert len(settings) == len(library) == 1
        assert "defer" in library[0]
        assert "defer" not in settings[0]
        order = [tag["src"] for tag in self.scripts(response)]
        assert order.index(settings[0]["src"]) < order.index(library[0]["src"])

    @pytest.mark.parametrize("address", ["/docs/plain/", "/docs/api/"])
    def test_a_page_without_maths_loads_neither_script(
        self, client, db, reference_app, address
    ) -> None:
        response = client.get(address)

        assert response.status_code == 200
        assert self.settings_scripts(response) == []
        assert self.library_scripts(response) == []

    def test_a_page_of_the_host_loads_neither_script(
        self, client, db, reference_app
    ) -> None:
        response = client.get(reverse("overview"))

        assert response.status_code == 200
        assert self.settings_scripts(response) == []
        assert self.library_scripts(response) == []

    @pytest.mark.parametrize("notation", NOTATIONS)
    def test_each_notation_reaches_the_response_as_written_in_a_math_element(
        self, client, db, reference_app, notation
    ) -> None:
        response = client.get("/docs/maths/")

        soup = BeautifulSoup(response.content.decode(), "html.parser")
        holders = [m for m in soup.select(".math") if notation in m.get_text()]
        assert len(holders) == 1

    @pytest.mark.parametrize("place", PLACES)
    def test_maths_in_a_place_inside_the_page_is_in_a_math_element(
        self, client, db, reference_app, place
    ) -> None:
        response = client.get("/docs/maths/")

        soup = BeautifulSoup(response.content.decode(), "html.parser")
        article = soup.select_one("article")
        assert article.select(f"{self.PLACES[place]} .math")

    def test_the_maths_page_is_served_when_sphinx_cannot_be_imported(
        self, client, db, reference_app, monkeypatch
    ) -> None:
        for name in [
            name
            for name in sys.modules
            if name == "sphinx" or name.startswith("sphinx.")
        ]:
            monkeypatch.setitem(sys.modules, name, None)

        response = client.get("/docs/maths/")

        assert response.status_code == 200
        assert len(self.library_scripts(response)) == 1


class TestNumberedEquations:
    @staticmethod
    def soup(client) -> BeautifulSoup:
        response = client.get("/docs/maths/")
        return BeautifulSoup(response.content.decode(), "html.parser")

    @staticmethod
    def numbered(soup) -> list:
        return soup.select("article div.math[id]")

    def test_each_labelled_equation_has_an_id_and_its_number_links_to_it(
        self, client, db, reference_app
    ) -> None:
        soup = self.soup(client)

        equations = self.numbered(soup)
        assert len(equations) == 2
        for equation in equations:
            link = equation.select_one("span.eqno > a.headerlink[href]")
            assert urldefrag(link["href"])[1] == equation["id"]

    def test_the_link_in_a_number_is_named_with_the_number(
        self, client, db, reference_app
    ) -> None:
        soup = self.soup(client)

        for equation in self.numbered(soup):
            eqno = equation.select_one("span.eqno")
            number = str(eqno.contents[0]).strip()
            name = unescape(eqno.select_one("a.headerlink")["aria-label"])
            assert number
            assert number in name

    def test_two_equations_links_have_different_names(
        self, client, db, reference_app
    ) -> None:
        soup = self.soup(client)

        names = [
            equation.select_one("span.eqno a.headerlink")["aria-label"]
            for equation in self.numbered(soup)
        ]
        assert len(names) == 2
        assert len(set(names)) == 2

    def test_each_reference_to_an_equation_leads_to_an_equation_of_the_page(
        self, client, db, reference_app
    ) -> None:
        soup = self.soup(client)

        references = soup.select("article a.reference.internal[href^='#']")
        equations = {equation["id"] for equation in self.numbered(soup)}
        assert len(references) == 2
        assert {urldefrag(link["href"])[1] for link in references} == equations


class TestLiveExamples:
    @staticmethod
    def soup(client, address: str) -> BeautifulSoup:
        return BeautifulSoup(client.get(f"/docs/{address}").content, "html.parser")

    def test_the_page_holds_a_frame_on_a_path_of_the_same_site(
        self, client, db, examples_app
    ) -> None:
        response = client.get("/docs/single/")

        frames = BeautifulSoup(response.content, "html.parser").select("iframe")
        assert response.status_code == 200
        assert [frame["src"] for frame in frames] == ["/examples/contact/"]
        assert frames[0]["title"]

    def test_the_example_shows_the_sources_text(self, client, db, examples_app) -> None:
        code = self.soup(client, "single/").select_one(".mvp-sphinx-example-code pre")

        assert code.get_text() == (
            SPHINX_SOURCES / "examples" / "sources" / "contact.py"
        ).read_text(encoding="utf-8")

    def test_the_example_sits_between_the_paragraphs_it_was_written_between(
        self, client, db, examples_app
    ) -> None:
        article = self.soup(client, "single/").select_one("article")

        example = article.select_one(".mvp-sphinx-example")

        assert example.find_previous_sibling().name == "p"
        assert example.find_next_sibling().name == "p"

    def test_the_sidebar_contents_are_those_of_a_page_with_no_example(
        self, client, db, examples_app
    ) -> None:
        with_example = contents_links(client.get("/docs/single/"), examples_app)
        without = contents_links(client.get("/docs/plain/"), examples_app)

        assert with_example == without

    def test_on_this_page_lists_the_pages_own_headings_and_none_from_the_example(
        self, client, db, examples_app
    ) -> None:
        soup = self.soup(client, "single/")
        article = soup.select_one("article")

        listed = [
            link["href"]
            for link in soup.find("nav", attrs={"aria-labelledby": True}).find_all("a")
        ]

        written = [
            heading.select_one(".headerlink")["href"]
            for heading in article.select("h2")
            if heading.find_parent(class_="mvp-sphinx-example") is None
        ]
        assert listed == written
        assert len(listed) == 2

    def test_a_page_with_two_examples_holds_two_frames_with_different_names(
        self, client, db, examples_app
    ) -> None:
        frames = self.soup(client, "two/").select("iframe")

        names = [frame["name"] for frame in frames]

        assert len(names) == 2
        assert names[0] != names[1]

    def test_a_page_with_an_example_links_the_examples_stylesheet(
        self, client, db, examples_app
    ) -> None:
        stylesheet = static("mvp_sphinx/example.css")

        assert stylesheet in linked_stylesheets(client.get("/docs/single/"))
        assert stylesheet not in linked_stylesheets(client.get("/docs/plain/"))

    def test_a_page_with_no_example_has_the_rewritten_body_as_its_article(
        self, client, db, examples_app, examples_build
    ) -> None:
        page = json.loads((examples_build / "plain.fjson").read_text())
        rewritten = BodyRewriter.parse(page["body"]).splice()

        content = client.get("/docs/plain/").content.decode()

        article = re.search(r"<article[^>]*>(.*)</article>", content, re.S)
        assert article.group(1).strip() == rewritten.strip()

    def test_the_page_is_served_when_sphinx_cannot_be_imported(
        self, client, db, examples_app, monkeypatch
    ) -> None:
        for name in [
            name
            for name in sys.modules
            if name == "sphinx" or name.startswith("sphinx.")
        ]:
            monkeypatch.setitem(sys.modules, name, None)

        response = client.get("/docs/single/")

        assert response.status_code == 200
        assert len(BeautifulSoup(response.content, "html.parser").select("iframe")) == 1

    def test_several_sources_are_a_group_of_radio_inputs_the_first_checked(
        self, client, db, examples_app
    ) -> None:
        radios = self.soup(client, "several/").select("input[type=radio]")

        assert [radio["aria-label"] for radio in radios] == [
            "contact.py",
            "long.py",
            "markup.html",
        ]
        assert len({radio["name"] for radio in radios}) == 1
        assert [radio.has_attr("checked") for radio in radios] == [True, False, False]

    def test_a_single_source_shows_no_radio_input(
        self, client, db, examples_app
    ) -> None:
        assert self.soup(client, "single/").select("input[type=radio]") == []

    def test_two_examples_with_several_sources_use_different_group_names(
        self, client, db, tmp_path, sphinx_build, monkeypatch
    ) -> None:
        from demo.mounted import docs

        example = ".. live-example:: /examples/contact/\n\n   a.py\n   b.py\n"
        page = f"A page\n======\n\n{example}\nBetween.\n\n{example}"
        source = write_source(
            tmp_path / "source", page, {"a.py": "a = 1\n", "b.py": "b = 2\n"}
        )
        monkeypatch.setattr(docs, "build_dir", sphinx_build(source))

        radios = self.soup(client, "").select("input[type=radio]")

        assert len(radios) == 4
        assert len({radio["name"] for radio in radios}) == 2

    def test_start_again_is_a_link_aimed_at_the_examples_own_frame(
        self, client, db, examples_app
    ) -> None:
        example = self.soup(client, "single/").select_one("section.mvp-sphinx-example")

        links = example.select("a[target]")

        assert len(links) == 1
        assert links[0]["target"] == example.select_one("iframe")["name"]
        assert links[0]["href"] == "/examples/contact/"

    def test_open_on_its_own_is_a_link_to_the_address_with_no_target(
        self, client, db, examples_app
    ) -> None:
        example = self.soup(client, "single/").select_one("section.mvp-sphinx-example")

        links = [
            link
            for link in example.select("a[href]")
            if link["href"] == "/examples/contact/" and not link.has_attr("target")
        ]

        assert len(links) == 1

    def test_each_start_again_on_a_page_names_its_own_frame(
        self, client, db, examples_app
    ) -> None:
        examples = self.soup(client, "two/").select("section.mvp-sphinx-example")

        targets = [example.select_one("a[target]")["target"] for example in examples]

        assert targets == [example.select_one("iframe")["name"] for example in examples]
        assert len(set(targets)) == 2

    @pytest.mark.parametrize("page", ["single/", "two/", "several/", "missing/"])
    def test_the_component_holds_no_script_and_no_inline_handler(
        self, client, db, examples_app, page
    ) -> None:
        examples = self.soup(client, page).select("section.mvp-sphinx-example")

        assert examples
        for example in examples:
            assert example.select("script") == []
            handlers = [
                attribute
                for element in example.find_all(True)
                for attribute in element.attrs
                if attribute.startswith("on")
            ]
            assert handlers == []
