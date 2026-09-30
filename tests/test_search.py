"""DocsSearch lists the pages of a docs build that hold the words searched for."""

import json
import shutil

import pytest

from mvp_sphinx.docs_build import DocsBuild
from mvp_sphinx.search import DocsSearch, PageText

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


def set_body(root, name, body) -> None:
    page = root / f"{name}.fjson"
    data = json.loads(page.read_text())
    data["body"] = body
    page.write_text(json.dumps(data))


def write_index(
    root, titles, terms, titleterms=None, alltitles=None, docnames=None
) -> DocsSearch:
    docnames = docnames or [title.lower().replace(" ", "-") for title in titles]
    (root / DocsSearch.SEARCH_DATA_FILE).write_text(
        json.dumps(
            {
                "docnames": docnames,
                "titles": titles,
                "terms": terms,
                "titleterms": titleterms or {},
                "alltitles": alltitles or {},
            }
        )
    )
    return DocsSearch(DocsBuild(root))


class TestResultOrder:
    def test_the_page_titled_with_the_word_comes_before_pages_that_mention_it(
        self, search
    ) -> None:
        results = search.results("lantern")

        assert results[0]["path"] == "lanterns/"
        assert len(results) == len(LANTERN_PAGES)

    def test_a_page_matching_in_its_title_and_body_is_listed_once(self, search) -> None:
        listed = [result["path"] for result in search.results("lantern")]

        assert listed.count("lanterns/") == 1

    def test_pages_that_only_mention_the_word_follow_in_title_order(
        self, search
    ) -> None:
        titles = [result["title"] for result in search.results("lantern")[1:]]

        assert len(titles) == len(LANTERN_PAGES) - 1
        assert titles == sorted(titles, key=str.lower)

    def test_a_title_match_comes_before_a_section_match_before_the_rest(
        self, tmp_path
    ) -> None:
        search = write_index(
            tmp_path,
            ["Alpha", "Beta", "Gasket housing"],
            {"gasket": [0, 1, 2]},
            alltitles={"Gasket": [[1, "gasket"]]},
        )

        assert [result["title"] for result in search.results("gasket")] == [
            "Gasket housing",
            "Beta",
            "Alpha",
        ]

    def test_pages_of_one_tier_are_ordered_by_title_then_document_name(
        self, tmp_path
    ) -> None:
        search = write_index(
            tmp_path,
            ["beta", "Alpha", "Alpha"],
            {"gasket": [0, 1, 2]},
            docnames=["z", "y", "x"],
        )

        assert [result["path"] for result in search.results("gasket")] == [
            "x/",
            "y/",
            "z/",
        ]

    def test_a_page_needs_every_word_in_its_title_to_be_a_title_match(
        self, tmp_path
    ) -> None:
        search = write_index(
            tmp_path,
            ["Alpha", "Gasket only"],
            {"gasket": [0, 1], "ring": [0, 1]},
        )

        assert [result["title"] for result in search.results("gasket ring")] == [
            "Alpha",
            "Gasket only",
        ]

    def test_a_title_word_matches_in_another_form(self, tmp_path) -> None:
        search = write_index(
            tmp_path,
            ["Alpha", "Gaskets"],
            {"gasket": [0, 1]},
        )

        assert search.results("gasket")[0]["title"] == "Gaskets"


class TestSectionLink:
    def test_a_word_in_a_section_heading_names_that_sections_anchor(
        self, search
    ) -> None:
        results = search.results("gasket")

        assert [(result["path"], result["anchor"]) for result in results] == [
            ("sections/", "gasket")
        ]

    def test_a_word_in_the_page_title_names_no_section(self, search) -> None:
        assert search.results("marsupials")[0]["anchor"] == ""

    def test_a_word_only_in_the_body_names_no_section(self, search) -> None:
        assert search.results("yodel")[0]["anchor"] == ""

    def test_a_heading_without_an_anchor_is_not_a_section(self, tmp_path) -> None:
        search = write_index(
            tmp_path,
            ["Alpha"],
            {"gasket": 0},
            alltitles={"Gasket": [[0, None]]},
        )

        assert search.results("gasket")[0]["anchor"] == ""

    @pytest.mark.parametrize(
        "entries",
        [
            "oops",
            [],
            [[0]],
            [["x", "a"]],
            [[7, "a"]],
            [[True, "a"]],
            [[0, 5]],
            [[0, ""]],
        ],
    )
    def test_an_entry_of_the_wrong_shape_is_not_a_section(
        self, tmp_path, entries
    ) -> None:
        search = write_index(
            tmp_path, ["Alpha"], {"gasket": 0}, alltitles={"Gasket": entries}
        )

        assert search.results("gasket") == [
            {"title": "Alpha", "path": "alpha/", "anchor": "", "passage": ""}
        ]

    def test_every_section_named_exists_in_its_page(self, search, search_build) -> None:
        results = [
            result
            for word in ("gasket", "sections", "folder")
            for result in search.results(word)
            if result["anchor"]
        ]

        assert results
        for result in results:
            page = json.loads(
                (search_build / f"{result['path'].rstrip('/')}.fjson").read_text()
            )
            assert f'id="{result["anchor"]}"' in page["body"]


class TestPassage:
    def test_a_passage_holds_the_searched_word_as_plain_text(self, search) -> None:
        passage = search.results("quetzal")[0]["passage"]

        assert "quetzal" in passage
        assert "<" not in passage
        assert "¶" not in passage

    def test_a_short_page_gives_its_whole_text_without_ellipses(self, search) -> None:
        passage = search.results("quetzal")[0]["passage"]

        assert not passage.startswith("…")
        assert not passage.endswith("…")

    def test_a_stemmed_match_still_finds_the_word_in_the_passage(self, search) -> None:
        results = {result["path"]: result for result in search.results("lantern")}

        assert "lanterns" in results["metals/"]["passage"]

    def test_markup_characters_of_the_page_are_plain_characters(self, search) -> None:
        passage = search.results("escapist")[0]["passage"]

        assert "<em>" in passage
        assert "&" in passage
        assert "&amp;" not in passage

    def test_a_long_page_gives_a_window_about_the_word_cut_at_word_boundaries(
        self, copied_build
    ) -> None:
        set_body(
            copied_build,
            "lanterns",
            f"<p>{'filler ' * 200}quetzal {'other ' * 200}</p>",
        )
        passage = DocsSearch(DocsBuild(copied_build)).results("quetzal")[0]["passage"]

        assert "quetzal" in passage
        assert passage.startswith("…")
        assert passage.endswith("…")
        assert len(passage) <= DocsSearch.PASSAGE_LENGTH + 2
        assert len(passage) > DocsSearch.PASSAGE_LENGTH // 2
        assert set(passage.strip("…").split()) <= {"filler", "quetzal", "other"}

    def test_a_word_at_the_start_of_a_long_page_has_no_leading_ellipsis(
        self, copied_build
    ) -> None:
        set_body(copied_build, "lanterns", f"<p>quetzal {'other ' * 200}</p>")
        passage = DocsSearch(DocsBuild(copied_build)).results("quetzal")[0]["passage"]

        assert passage.startswith("quetzal")
        assert passage.endswith("…")

    def test_a_word_at_the_end_of_a_long_page_has_no_trailing_ellipsis(
        self, copied_build
    ) -> None:
        set_body(copied_build, "lanterns", f"<p>{'other ' * 200}quetzal</p>")
        passage = DocsSearch(DocsBuild(copied_build)).results("quetzal")[0]["passage"]

        assert passage.startswith("…")
        assert passage.endswith("quetzal")

    def test_a_title_only_match_has_an_empty_passage(self, copied_build) -> None:
        set_body(copied_build, "wombat", "<p>Nothing to see.</p>")
        results = DocsSearch(DocsBuild(copied_build)).results("marsupials")

        assert [(result["path"], result["passage"]) for result in results] == [
            ("wombat/", "")
        ]

    def test_a_missing_page_file_gives_an_empty_passage(self, copied_build) -> None:
        (copied_build / "wombat.fjson").unlink()
        results = DocsSearch(DocsBuild(copied_build)).results("koala")

        assert [(result["path"], result["passage"]) for result in results] == [
            ("wombat/", "")
        ]

    @pytest.mark.parametrize(
        "content", [b"{not json", b"\xff\xfe", b"", b"[]", b'{"body": 5}']
    )
    def test_an_unreadable_page_file_gives_an_empty_passage(
        self, copied_build, content
    ) -> None:
        (copied_build / "wombat.fjson").write_bytes(content)
        results = DocsSearch(DocsBuild(copied_build)).results("koala")

        assert [(result["path"], result["passage"]) for result in results] == [
            ("wombat/", "")
        ]

    def test_a_page_file_that_is_a_directory_gives_an_empty_passage(
        self, copied_build
    ) -> None:
        (copied_build / "wombat.fjson").unlink()
        (copied_build / "wombat.fjson").mkdir()
        results = DocsSearch(DocsBuild(copied_build)).results("koala")

        assert [(result["path"], result["passage"]) for result in results] == [
            ("wombat/", "")
        ]


class TestPageText:
    def test_a_permalink_is_not_text(self) -> None:
        markup = '<h1>Title<a class="headerlink" href="#t" title="Link">¶</a></h1>'

        assert PageText.text(markup) == "Title"

    def test_a_link_with_other_classes_beside_headerlink_is_skipped(self) -> None:
        assert PageText.text('<a class="x headerlink">¶</a>after') == "after"

    def test_an_ordinary_link_is_text(self) -> None:
        assert PageText.text('<a href="x" class="reference">link</a>') == "link"

    def test_scripts_and_styles_are_not_text(self) -> None:
        markup = '<p>a</p>\n<script>var x = "hidden";</script>\n<style>.h{}</style>\n<p>b</p>'

        assert PageText.text(markup) == "a b"

    def test_an_element_inside_a_skipped_one_is_skipped_with_it(self) -> None:
        markup = '<a class="headerlink"><span>¶<br></span>x</a>after'

        assert PageText.text(markup) == "after"

    def test_entities_are_converted_to_characters(self) -> None:
        markup = "<p>Fish &amp; &lt;chips&gt; &#8220;q&#8221; &nbsp;x</p>"

        assert PageText.text(markup) == "Fish & <chips> “q” x"

    def test_whitespace_between_elements_is_one_space(self) -> None:
        assert PageText.text("<p>a\n\n  b</p>\n<p>\tc</p>") == "a b c"

    def test_no_markup_gives_empty_text(self) -> None:
        assert PageText.text("") == ""
