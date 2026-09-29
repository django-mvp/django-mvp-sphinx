"""PageView renders a page of the docs build inside the application shell."""

import json
import re
import shutil
import sys
from urllib.parse import urljoin

import pytest

pytestmark = pytest.mark.usefixtures("docs_app")

FRONT_PAGE_TEXT = "Welcome to the guide"
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
