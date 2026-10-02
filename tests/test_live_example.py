"""The ``live-example`` directive, read from the pages it writes into a docs build."""

import json
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from tests.conftest import SPHINX_SOURCES

EXAMPLES_SOURCE = SPHINX_SOURCES / "examples"


def body(build: Path, page: str) -> BeautifulSoup:
    page_data = json.loads((build / f"{page}.fjson").read_text(encoding="utf-8"))
    return BeautifulSoup(page_data["body"], "html.parser")


def source_text(element) -> str:
    return element.select_one("pre").get_text()


class TestLiveExampleElement:
    def test_the_example_carries_the_address_and_title_written(
        self, examples_build
    ) -> None:
        examples = body(examples_build, "single").select(".mvp-sphinx-example")

        assert len(examples) == 1
        assert examples[0]["data-address"] == "/examples/contact/"
        assert examples[0]["data-title"] == "The contact form"

    def test_a_title_with_quotes_and_an_ampersand_reads_back_as_written(
        self, examples_build
    ) -> None:
        titled = body(examples_build, "two").select(".mvp-sphinx-example")[0]

        assert titled["data-title"] == 'Status of "an order" & its items'

    def test_an_example_with_no_title_writes_an_empty_one(self, examples_build) -> None:
        untitled = body(examples_build, "two").select(".mvp-sphinx-example")[1]

        assert untitled["data-title"] == ""

    def test_the_example_sits_between_the_paragraphs_it_was_written_between(
        self, examples_build
    ) -> None:
        example = body(examples_build, "single").select_one(".mvp-sphinx-example")

        before, after = example.find_previous_sibling(), example.find_next_sibling()
        assert before.name == "p"
        assert after.name == "p"

    def test_a_page_with_two_examples_holds_two_elements(self, examples_build) -> None:
        examples = body(examples_build, "two").select(".mvp-sphinx-example")

        assert [e["data-address"] for e in examples] == [
            "/examples/status/",
            "/examples/contact/",
        ]

    def test_a_plain_page_holds_none(self, examples_build) -> None:
        assert body(examples_build, "plain").select(".mvp-sphinx-example") == []

    def test_an_address_the_site_lacks_is_still_written(self, examples_build) -> None:
        example = body(examples_build, "missing").select_one(".mvp-sphinx-example")

        assert example["data-address"] == "/examples/retired/"

    def test_the_host_names_one_extension_and_nothing_else_about_examples(
        self,
    ) -> None:
        settings: dict = {}
        exec((EXAMPLES_SOURCE / "conf.py").read_text(), settings)  # noqa: S102

        assert settings["extensions"] == ["mvp_sphinx.navigation"]
        assert [name for name in settings if "example" in name.lower()] == []


class TestLiveExampleSources:
    def test_each_source_is_named_by_its_file_and_holds_its_text(
        self, examples_build
    ) -> None:
        example = body(examples_build, "single").select_one(".mvp-sphinx-example")

        sources = example.select(".mvp-sphinx-example-source")
        assert [s["data-name"] for s in sources] == ["contact.py"]
        assert source_text(sources[0]) == (
            EXAMPLES_SOURCE / "sources" / "contact.py"
        ).read_text(encoding="utf-8")

    def test_sources_come_in_the_order_written(self, examples_build) -> None:
        example = body(examples_build, "several").select_one(".mvp-sphinx-example")

        names = [s["data-name"] for s in example.select(".mvp-sphinx-example-source")]

        assert names == ["contact.py", "long.py", "markup.html"]

    def test_a_line_range_shows_only_those_lines(self, examples_build) -> None:
        example = body(examples_build, "several").select_one(".mvp-sphinx-example")

        long = example.select(".mvp-sphinx-example-source")[1]

        assert source_text(long).splitlines() == [
            "third = 3",
            "fourth = 4",
            "fifth = 5",
        ]

    def test_markup_in_a_source_reaches_the_body_escaped_and_reads_back_as_written(
        self, examples_build
    ) -> None:
        page = json.loads((examples_build / "several.fjson").read_text())["body"]
        example = BeautifulSoup(page, "html.parser").select_one(".mvp-sphinx-example")
        markup = example.select(".mvp-sphinx-example-source")[2]

        assert "<p class" not in page
        assert source_text(markup) == (
            EXAMPLES_SOURCE / "sources" / "markup.html"
        ).read_text(encoding="utf-8")

    def test_a_source_is_highlighted_as_a_code_block_of_its_language_is(
        self, examples_build
    ) -> None:
        page = body(examples_build, "single")
        example = page.select_one(".mvp-sphinx-example")

        shown = example.select_one(".mvp-sphinx-example-source > div")
        written = [
            d for d in page.select("div.highlight-python") if d.parent is not example
        ][-1]

        assert shown["class"] == written["class"]
        assert shown.select_one("div")["class"] == written.select_one("div")["class"]
        assert shown.select("span[class]")

    @pytest.mark.parametrize(
        ("page", "example", "position", "language"),
        [
            ("several", 0, 0, "python"),
            ("several", 0, 2, "html+django"),
            ("two", 1, 0, "text"),
        ],
    )
    def test_the_language_follows_the_files_name(
        self, examples_build, page, example, position, language
    ) -> None:
        written = body(examples_build, page).select(".mvp-sphinx-example")[example]

        source = written.select(".mvp-sphinx-example-source")[position]

        assert f"highlight-{language}" in source.select_one("div")["class"]
