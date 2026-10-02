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


def write_source(directory: Path, page: str, files: dict[str, str]) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "conf.py").write_text(
        'extensions = ["mvp_sphinx.navigation"]\n', encoding="utf-8"
    )
    (directory / "index.rst").write_text(page, encoding="utf-8")
    for name, text in files.items():
        file = directory / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(text, encoding="utf-8")
    return directory


def example_page(*content: str, address: str = "/examples/contact/") -> str:
    lines = "\n".join(f"   {line}" for line in content)
    return f"A page\n======\n\n.. live-example:: {address}\n\n{lines}\n"


@pytest.fixture
def example_build(tmp_path, sphinx_build):
    def build(content: list[str], files: dict[str, str]) -> BeautifulSoup:
        source = write_source(tmp_path / "source", example_page(*content), files)
        return body(sphinx_build(source), "index")

    return build


def source_names(page: BeautifulSoup) -> list[str]:
    return [s["data-name"] for s in page.select(".mvp-sphinx-example-source")]


NESTED = (
    "class Order:\n"
    "    def one(self):\n"
    "        return 1\n"
    "\n"
    "    def two(self):\n"
    "        return 2\n"
)


class TestLiveExampleRanges:
    def test_a_range_shows_its_lines_with_their_common_indentation_removed(
        self, example_build
    ) -> None:
        page = example_build(["order.py 2-3"], {"order.py": NESTED})

        assert source_text(
            page.select_one(".mvp-sphinx-example-source")
        ).splitlines() == [
            "def one(self):",
            "    return 1",
        ]

    def test_a_single_line_number_shows_that_line(self, example_build) -> None:
        page = example_build(["order.py 5"], {"order.py": NESTED})

        shown = source_text(page.select_one(".mvp-sphinx-example-source"))

        assert shown.splitlines() == ["def two(self):"]

    def test_a_file_with_no_range_is_shown_whole(self, example_build) -> None:
        page = example_build(["order.py"], {"order.py": NESTED})

        assert source_text(page.select_one(".mvp-sphinx-example-source")) == NESTED

    def test_a_path_with_a_space_and_no_range_is_read_as_a_path(
        self, example_build
    ) -> None:
        page = example_build(["my notes.py"], {"my notes.py": "x = 1\n"})

        assert source_names(page) == ["my notes.py"]
        assert source_text(page.select_one(".mvp-sphinx-example-source")) == "x = 1\n"

    def test_a_path_with_a_space_takes_a_range_from_its_last_word(
        self, example_build
    ) -> None:
        page = example_build(["my notes.py 2"], {"my notes.py": "x = 1\ny = 2\n"})

        assert source_names(page) == ["my notes.py"]
        assert source_text(page.select_one(".mvp-sphinx-example-source")) == "y = 2\n"


class TestLiveExampleNames:
    def test_a_file_named_once_keeps_its_bare_name(self, example_build) -> None:
        page = example_build(
            ["app/forms.py 1-2", "views.py"],
            {"app/forms.py": "a = 1\nb = 2\n", "views.py": "c = 3\n"},
        )

        assert source_names(page) == ["forms.py", "views.py"]

    def test_two_files_of_one_name_take_the_folder_that_tells_them_apart(
        self, example_build
    ) -> None:
        page = example_build(
            ["a/forms.py", "b/forms.py"],
            {"a/forms.py": "a = 1\n", "b/forms.py": "b = 2\n"},
        )

        assert source_names(page) == ["a/forms.py", "b/forms.py"]

    def test_each_file_takes_only_as_many_folders_as_it_needs(
        self, example_build
    ) -> None:
        page = example_build(
            ["a/x/forms.py", "b/x/forms.py", "c/forms.py"],
            {
                "a/x/forms.py": "a = 1\n",
                "b/x/forms.py": "b = 2\n",
                "c/forms.py": "c = 3\n",
            },
        )

        assert source_names(page) == ["a/x/forms.py", "b/x/forms.py", "c/forms.py"]

    def test_one_file_named_twice_with_different_lines_adds_the_lines(
        self, example_build
    ) -> None:
        page = example_build(
            ["views.py 1-2", "views.py 4-5"],
            {"views.py": "a = 1\nb = 2\nc = 3\nd = 4\ne = 5\n"},
        )

        assert source_names(page) == ["views.py 1-2", "views.py 4-5"]

    def test_the_same_name_in_two_folders_and_one_file_twice_all_differ(
        self, example_build
    ) -> None:
        page = example_build(
            ["a/forms.py 1", "a/forms.py 2", "b/forms.py"],
            {"a/forms.py": "a = 1\nb = 2\n", "b/forms.py": "c = 3\n"},
        )

        assert source_names(page) == ["a/forms.py 1", "a/forms.py 2", "b/forms.py"]
