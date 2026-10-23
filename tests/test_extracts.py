"""Page extracts, asserted as a developer would ask for them."""

import json
import shutil
import sys

import pytest
from bs4 import BeautifulSoup
from django.contrib.auth.models import AnonymousUser
from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import conditional_escape

from mvp_sphinx.examples import LiveExamples


@pytest.fixture
def page_request(rf):
    request = rf.get("/")
    request.user = AnonymousUser()
    return request


def soup(extract):
    return BeautifulSoup(str(extract), "html.parser")


class TestPageExtract:
    def test_the_content_holds_the_opening_paragraph_and_every_section(
        self, extracts_app, page_request
    ) -> None:
        extract = extracts_app.page_extract("screens/", page_request)

        page = soup(extract)
        assert page.find("img", alt="A single pixel")
        for anchor in ["first-section", "search-filters", "details", "third-section"]:
            assert page.find(id=anchor)

    def test_the_content_leaves_out_the_pages_own_heading(
        self, extracts_app, page_request
    ) -> None:
        extract = extracts_app.page_extract("screens/", page_request)

        assert not soup(extract).find("h1")
        assert not soup(extract).find(id="screens")

    def test_the_title_is_the_pages_title_as_plain_text(
        self, extracts_app, page_request
    ) -> None:
        extract = extracts_app.page_extract("screens/", page_request)

        assert extract.title == "Screens"

    def test_the_address_is_the_page_in_the_documentation_app(
        self, extracts_app, page_request
    ) -> None:
        extract = extracts_app.page_extract("screens/", page_request)

        assert extract.url == reverse("docs:page", kwargs={"path": "screens/"})

    def test_the_empty_address_is_the_front_page(
        self, extracts_app, page_request
    ) -> None:
        extract = extracts_app.page_extract("", page_request)

        assert extract.url == reverse("docs:front_page")
        assert extract.title == "Extracts"
        assert soup(extract).find("p")

    def test_it_renders_as_markup_not_as_escaped_text(
        self, extracts_app, page_request
    ) -> None:
        extract = extracts_app.page_extract("screens/", page_request)

        assert conditional_escape(extract) == extract.content
        assert extract.__html__() == extract.content
        assert str(extract) == extract.content

    def test_a_rebuilt_page_shows_on_the_next_call(
        self, extracts_app, extracts_build, page_request, tmp_path, monkeypatch
    ) -> None:
        build = tmp_path / "build"
        shutil.copytree(extracts_build, build)
        monkeypatch.setattr(extracts_app, "build_dir", build)
        assert "A short page" in str(extracts_app.page_extract("other/", page_request))

        page_file = build / "other.fjson"
        page = json.loads(page_file.read_text())
        page["body"] = page["body"].replace("A short page", "A rebuilt page")
        page_file.write_text(json.dumps(page))

        content = str(extracts_app.page_extract("other/", page_request))
        assert "A rebuilt page" in content
        assert "A short page" not in content


class TestExtractContent:
    def test_the_content_is_wrapped_in_the_documentation_apps_styles(
        self, extracts_app, page_request
    ) -> None:
        extract = extracts_app.page_extract("screens/", page_request)

        page = soup(extract)
        assert page.select_one("div.mvp-sphinx-content")
        stylesheet = page.find("link", rel="stylesheet")
        assert stylesheet["href"] == static("mvp_sphinx/content.css")

    def test_maths_is_left_as_written(self, extracts_app, page_request) -> None:
        extract = extracts_app.page_extract("screens/", page_request)

        content = str(extract)
        assert r"\(a^2 + b^2 = c^2\)" in content
        assert r"\[e^{i\pi} + 1 = 0\]" in content

    def test_a_table_is_wrapped_to_scroll_as_on_the_page_itself(
        self, extracts_app, page_request
    ) -> None:
        extract = extracts_app.page_extract("screens/", page_request)

        region = soup(extract).find("table").find_parent(attrs={"role": "region"})
        assert region["tabindex"] == "0"

    def test_live_examples_are_left_out(self, examples_app, page_request) -> None:
        extract = examples_app.page_extract("single/", page_request)

        assert LiveExamples.EXAMPLE_CLASS not in str(extract)
        assert "Written before the example." in str(extract)
        assert "Written after the example." in str(extract)


class TestNothingToShow:
    def test_a_page_holding_only_a_contents_is_a_false_extract(
        self, extracts_app, page_request
    ) -> None:
        extract = extracts_app.page_extract("toc-only/", page_request)

        assert extract is not None
        assert not extract
        assert (extract or "") == ""

    def test_a_page_with_text_is_a_true_extract(
        self, extracts_app, page_request
    ) -> None:
        assert extracts_app.page_extract("other/", page_request)

    def test_a_page_holding_only_an_image_is_a_true_extract(
        self, extracts_app, extracts_build, page_request, tmp_path, monkeypatch
    ) -> None:
        build = tmp_path / "build"
        shutil.copytree(extracts_build, build)
        monkeypatch.setattr(extracts_app, "build_dir", build)
        page_file = build / "toc-only.fjson"
        page = json.loads(page_file.read_text())
        page["body"] = (
            '<section id="x"><h1>X</h1><img alt="" src="../_images/pixel.png" />'
            "</section>"
        )
        page_file.write_text(json.dumps(page))

        assert extracts_app.page_extract("toc-only/", page_request)


class TestWithoutSphinx:
    def test_an_extract_is_had_when_sphinx_cannot_be_imported(
        self, extracts_app, page_request, monkeypatch
    ) -> None:
        for name in [
            name
            for name in sys.modules
            if name == "sphinx" or name.startswith("sphinx.")
        ]:
            monkeypatch.setitem(sys.modules, name, None)

        extract = extracts_app.page_extract("screens/", page_request)

        assert extract.title == "Screens"
