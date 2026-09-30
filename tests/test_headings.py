"""PageHeadings reads the heading tree out of a page's toc fragment."""

import json

import pytest
from bs4 import BeautifulSoup
from django.utils.safestring import SafeString

from mvp_sphinx.headings import PageHeadings

TWO_OUTER_ENTRIES = (
    '<ul><li><a href="#">Title</a><ul>'
    '<li><a href="#first">First</a><ul><li><a href="#inner">Inner</a></li></ul></li>'
    "</ul></li>"
    '<li><a href="#second">Second</a></li></ul>'
)


def page(build, name: str) -> dict:
    return json.loads((build / f"{name}.fjson").read_text())


def headings_of(build, name: str) -> list[dict]:
    return PageHeadings.from_toc(page(build, name)["toc"])


def outline(headings: list[dict]) -> list:
    return [(heading["anchor"], outline(heading["children"])) for heading in headings]


def flatten(headings: list[dict]) -> list[dict]:
    return [
        found
        for heading in headings
        for found in (heading, *flatten(heading["children"]))
    ]


class TestPageHeadings:
    def test_the_front_page_lists_its_two_sections_with_the_sub_section_nested(
        self, reading_build
    ) -> None:
        headings = headings_of(reading_build, "index")

        assert outline(headings) == [
            ("#first-part", []),
            ("#second-part", [("#a-sub-section", [])]),
        ]

    def test_a_page_nests_its_headings_as_deep_as_it_does(self, reading_build) -> None:
        headings = headings_of(reading_build, "long")

        assert outline(headings) == [
            ("#level-one", [("#level-two", [("#level-three", [])])]),
            ("#the-code-heading", []),
        ]

    @pytest.mark.parametrize("name", ["index", "long", "single"])
    def test_every_anchor_is_the_id_of_a_heading_in_the_pages_body(
        self, reading_build, name
    ) -> None:
        body = BeautifulSoup(page(reading_build, name)["body"], "html.parser")

        anchors = [
            heading["anchor"] for heading in flatten(headings_of(reading_build, name))
        ]

        assert anchors
        for anchor in anchors:
            assert anchor.startswith("#")
            assert body.find(id=anchor[1:]) is not None

    def test_a_heading_with_inline_code_keeps_its_markup(self, reading_build) -> None:
        headings = flatten(headings_of(reading_build, "long"))

        heading = next(
            item for item in headings if item["anchor"] == "#the-code-heading"
        )

        assert BeautifulSoup(heading["title"], "html.parser").find("code") is not None

    def test_a_page_with_one_section_lists_one_heading(self, reading_build) -> None:
        assert outline(headings_of(reading_build, "single")) == [
            ("#the-only-section", [])
        ]

    def test_a_page_with_no_section_lists_nothing(self, reading_build) -> None:
        assert headings_of(reading_build, "plain") == []

    @pytest.mark.parametrize("name", ["index", "long", "single", "plain"])
    def test_no_entry_is_the_pages_own_title(self, reading_build, name) -> None:
        anchors = [item["anchor"] for item in flatten(headings_of(reading_build, name))]

        assert "#" not in anchors

    def test_an_empty_fragment_gives_no_headings(self) -> None:
        assert PageHeadings.from_toc("") == []

    def test_a_title_with_an_empty_list_gives_no_headings(self) -> None:
        assert (
            PageHeadings.from_toc('<ul><li><a href="#">Title</a><ul>\n</ul></li></ul>')
            == []
        )

    def test_a_second_outer_entry_follows_the_first_ones_children(self) -> None:
        headings = PageHeadings.from_toc(TWO_OUTER_ENTRIES)

        assert outline(headings) == [("#first", [("#inner", [])]), ("#second", [])]

    def test_a_title_is_the_markup_between_its_link_tags_as_written(self) -> None:
        markup = "A &amp; B <code>c</code> &copy; &"
        fragment = (
            '<ul><li><a href="#">Title</a><ul><li>'
            f'<a class="reference internal" href="#a">{markup}</a>'
            "</li></ul></li></ul>"
        )

        (heading,) = PageHeadings.from_toc(fragment)

        assert heading["title"] == markup
        assert isinstance(heading["title"], SafeString)
