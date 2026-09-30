"""DocsSearch lists the pages of a docs build that hold the words searched for."""

import json
import shutil

import pytest

from mvp_sphinx.docs_build import DocsBuild
from mvp_sphinx.search import DocsSearch

UNIQUE_WORDS = {
    "": "aardvark",
    "lanterns/": "quetzal",
    "products/": "zeppelin",
    "sections/": "yodel",
    "metals/": "molybdenum",
    "coins/": "denarius",
    "spoons/": "ladle",
    "markup/": "escapist",
    "wombat/": "koala",
    "folder/": "folderfront",
    "folder/inner/": "innerword",
}
LANTERN_PAGES = ["", "coins/", "lanterns/", "metals/", "products/"]


def address(docname: str) -> str:
    if docname == "index":
        return ""
    if docname.endswith("/index"):
        return docname[: -len("index")]
    return f"{docname}/"


def paths(results) -> list[str]:
    return sorted(result["path"] for result in results)


@pytest.fixture
def search(search_build) -> DocsSearch:
    return DocsSearch(DocsBuild(search_build))


@pytest.fixture
def copied_build(search_build, tmp_path):
    root = tmp_path / "copy"
    shutil.copytree(search_build, root)
    return root


class TestDocsSearch:
    @pytest.mark.parametrize(("path", "word"), UNIQUE_WORDS.items())
    def test_a_words_only_page_is_the_only_result(self, search, path, word) -> None:
        assert paths(search.results(word)) == [path]

    def test_a_word_on_several_pages_lists_each_once_at_its_path(self, search) -> None:
        assert paths(search.results("lantern")) == LANTERN_PAGES

    def test_several_words_list_only_pages_holding_all_of_them(self, search) -> None:
        assert paths(search.results("copper silver")) == ["metals/"]

    @pytest.mark.parametrize("query", ["Lanterns", "LANTERN", "lanterns"])
    def test_case_and_word_form_find_the_page(self, search, query) -> None:
        assert paths(search.results(query)) == LANTERN_PAGES

    def test_a_word_stored_capitalised_is_found_by_its_lower_case_form(
        self, search
    ) -> None:
        assert paths(search.results("others")) == ["metals/"]

    def test_words_in_no_page_give_no_results(self, search) -> None:
        assert search.results("nothingmatchesthis") == []

    def test_one_word_missing_from_the_page_gives_no_results(self, search) -> None:
        assert search.results("aardvark quetzal") == []

    @pytest.mark.parametrize("query", ["", "   ", "?! -- ...", "\n\t"])
    def test_a_query_without_words_gives_no_results(self, search, query) -> None:
        assert search.results(query) == []

    def test_stopwords_do_not_stop_the_other_words_matching(self, search) -> None:
        assert paths(search.results("the product list")) == ["products/"]

    def test_a_word_only_in_a_pages_file_name_gives_no_results(self, search) -> None:
        assert search.results("wombat") == []

    def test_a_fragment_of_a_word_gives_no_results(self, search) -> None:
        assert search.results("lante") == []

    def test_digits_alone_are_ignored(self, search) -> None:
        assert search.results("2024") == []
        assert paths(search.results("aardvark 2024")) == [""]

    def test_no_result_is_a_page_sphinx_builds_for_itself(
        self, search, search_build
    ) -> None:
        data = json.loads((search_build / DocsSearch.SEARCH_DATA_FILE).read_text())
        found = {
            result["path"]
            for key in [*data["terms"], *data["titleterms"]]
            for result in search.results(key) or []
        }

        assert found
        assert found.isdisjoint({"genindex/", "search/"})

    def test_every_word_the_search_data_holds_lists_the_pages_it_names(
        self, search, search_build
    ) -> None:
        data = json.loads((search_build / DocsSearch.SEARCH_DATA_FILE).read_text())
        addresses = [address(name) for name in data["docnames"]]
        checked = 0

        for key in {*data["terms"], *data["titleterms"]}:
            if key != key.lower() or search.words(key) != [key]:
                continue
            listed = set()
            for mapping in (data["terms"], data["titleterms"]):
                value = mapping.get(key, [])
                numbers = value if isinstance(value, list) else [value]
                listed.update(addresses[number] for number in numbers)
            assert listed <= {result["path"] for result in search.results(key)}, key
            checked += 1

        assert checked > 20

    def test_a_query_of_many_words_is_cut_to_the_word_limit(self, search) -> None:
        query = " ".join(f"word{number}" for number in range(DocsSearch.WORD_LIMIT * 5))

        assert len(search.words(query)) == DocsSearch.WORD_LIMIT
        assert search.results(query) == []

    def test_a_result_has_the_page_title_and_path_and_no_section_or_passage(
        self, search
    ) -> None:
        result = search.results("quetzal")[0]

        assert result == {
            "title": "Lanterns and lamps",
            "path": "lanterns/",
            "anchor": "",
            "passage": "",
        }

    def test_results_are_ordered_by_title_then_document_name(self, search) -> None:
        results = search.results("lantern")
        titles = [result["title"] for result in results]

        assert titles == sorted(titles, key=str.lower)

    def test_the_front_page_is_the_empty_path_and_a_folder_page_its_folder(
        self, search
    ) -> None:
        assert search.results("aardvark")[0]["path"] == ""
        assert search.results("folderfront")[0]["path"] == "folder/"


class TestUnavailableSearchData:
    @pytest.mark.parametrize(
        "content",
        [
            b"",
            b"not json",
            b"\xff\xfe",
            b"[]",
            b"{}",
            json.dumps(
                {"docnames": ["a"], "titles": [], "terms": {}, "titleterms": {}}
            ).encode(),
            json.dumps(
                {"docnames": ["a"], "titles": ["A"], "terms": [], "titleterms": {}}
            ).encode(),
            json.dumps(
                {
                    "docnames": ["a"],
                    "titles": ["A"],
                    "terms": {"x": 5},
                    "titleterms": {},
                }
            ).encode(),
            json.dumps(
                {"docnames": [1], "titles": ["A"], "terms": {}, "titleterms": {}}
            ).encode(),
        ],
    )
    def test_search_data_of_the_wrong_shape_gives_none(
        self, copied_build, content
    ) -> None:
        (copied_build / DocsSearch.SEARCH_DATA_FILE).write_bytes(content)

        assert DocsSearch(DocsBuild(copied_build)).results("lantern") is None

    def test_missing_search_data_gives_none(self, copied_build) -> None:
        (copied_build / DocsSearch.SEARCH_DATA_FILE).unlink()

        assert DocsSearch(DocsBuild(copied_build)).results("lantern") is None

    def test_a_build_that_does_not_exist_gives_none(self, tmp_path) -> None:
        assert DocsSearch(DocsBuild(tmp_path / "nothing")).results("lantern") is None

    def test_an_empty_query_on_missing_search_data_still_gives_none(
        self, copied_build
    ) -> None:
        (copied_build / DocsSearch.SEARCH_DATA_FILE).unlink()

        assert DocsSearch(DocsBuild(copied_build)).results("") is None


class TestStopwordsFromTheBuild:
    def test_a_stopword_is_dropped_from_the_query(self, search) -> None:
        assert paths(search.results("and product list")) == ["products/"]

    def test_without_the_language_data_no_word_is_a_stopword(
        self, copied_build
    ) -> None:
        (copied_build / DocsSearch.LANGUAGE_DATA_FILE).unlink()
        search = DocsSearch(DocsBuild(copied_build))

        assert search.results("and product list") == []
        assert paths(search.results("product list")) == ["products/"]

    def test_language_data_in_the_older_array_form_is_read(self, copied_build) -> None:
        (copied_build / DocsSearch.LANGUAGE_DATA_FILE).write_text(
            'var stopwords = ["and"];\n'
        )
        search = DocsSearch(DocsBuild(copied_build))

        assert paths(search.results("and product list")) == ["products/"]

    def test_unparsable_language_data_leaves_no_stopwords(self, copied_build) -> None:
        (copied_build / DocsSearch.LANGUAGE_DATA_FILE).write_text(
            "stopwords = new Set([not json]);"
        )
        search = DocsSearch(DocsBuild(copied_build))

        assert search.results("and product list") == []


class TestLanguageFromTheBuild:
    def test_a_missing_global_context_is_read_as_english(self, copied_build) -> None:
        (copied_build / "globalcontext.json").unlink()
        search = DocsSearch(DocsBuild(copied_build))

        assert paths(search.results("Lanterns")) == LANTERN_PAGES

    @pytest.mark.parametrize("content", ['{"language": null}', "not json", "[]"])
    def test_a_language_that_is_not_named_is_read_as_english(
        self, copied_build, content
    ) -> None:
        (copied_build / "globalcontext.json").write_text(content)
        search = DocsSearch(DocsBuild(copied_build))

        assert paths(search.results("Lanterns")) == LANTERN_PAGES

    def test_a_language_without_a_stemmer_matches_the_word_as_written(
        self, copied_build
    ) -> None:
        (copied_build / "globalcontext.json").write_text('{"language": "xx"}')
        search = DocsSearch(DocsBuild(copied_build))

        assert search.results("Lanterns") == []
        assert paths(search.results("Lantern")) == LANTERN_PAGES


class TestWords:
    def test_a_query_is_split_on_anything_but_letters_digits_and_underscore(
        self, search
    ) -> None:
        assert search.words("Copper,silver;COPPER_x 12 a-b copper") == [
            "copper",
            "silver",
            "copper_x",
            "b",
        ]
