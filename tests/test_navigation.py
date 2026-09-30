"""The Sphinx extension writes the whole contents into the docs build."""

import json
from types import SimpleNamespace

import pytest
from docutils import nodes
from sphinx import addnodes

from mvp_sphinx.docs_build import DocsBuild
from mvp_sphinx.navigation import NavigationWriter, write_navigation
from tests.conftest import SPHINX_SOURCES


@pytest.fixture
def navigation(contents_build) -> dict:
    return json.loads((contents_build / DocsBuild.NAVIGATION_FILE).read_text())


def entry(entries: list[dict], title: str) -> dict:
    return next(each for each in entries if each["title"] == title)


class TestNavigationFile:
    def test_there_is_one_group_per_root_toctree_in_document_order(
        self, navigation
    ) -> None:
        captions = [group["caption"] for group in navigation["groups"]]

        assert captions == ["Getting started", "", "Reference", ""]

    def test_a_group_lists_its_toctrees_pages_in_order(self, navigation) -> None:
        started, uncaptioned, reference = navigation["groups"][:3]

        assert [each["title"] for each in started["entries"]] == [
            "Install",
            "Chosen title",
            "Chain one",
            "Fish <b>& chips</b>",
            "Shared page",
        ]
        assert [each["url"] for each in uncaptioned["entries"]] == ["standalone/"]
        assert [each["url"] for each in reference["entries"]] == [
            "reference/api/",
            "shared/",
        ]

    def test_the_pages_of_a_hidden_toctree_are_present(self, navigation) -> None:
        hidden = navigation["groups"][3]

        assert [each["url"] for each in hidden["entries"]] == ["hidden-page/"]

    def test_a_page_chain_nests_three_levels_at_the_builders_addresses(
        self, navigation
    ) -> None:
        one = entry(navigation["groups"][0]["entries"], "Chain one")
        two = entry(one["children"], "Chain two")
        three = entry(two["children"], "Chain three")

        assert [one["url"], two["url"], three["url"]] == [
            "chain/one/",
            "chain/two/",
            "chain/three/",
        ]

    def test_an_entrys_own_title_wins_over_the_pages_title(self, navigation) -> None:
        titles = [each["title"] for each in navigation["groups"][0]["entries"]]

        assert "Chosen title" in titles
        assert "Page title of the explicit page" not in titles

    def test_an_external_link_and_a_self_entry_are_absent(self, navigation) -> None:
        hidden = navigation["groups"][3]

        assert len(hidden["entries"]) == 1

    def test_a_page_listed_twice_appears_at_both_places(self, navigation) -> None:
        started, reference = navigation["groups"][0], navigation["groups"][2]

        assert entry(started["entries"], "Shared page")["url"] == "shared/"
        assert entry(reference["entries"], "Shared page")["url"] == "shared/"

    def test_a_page_at_the_end_of_a_chain_has_no_children(self, navigation) -> None:
        one = entry(navigation["groups"][0]["entries"], "Chain one")
        three = entry(entry(one["children"], "Chain two")["children"], "Chain three")

        assert three["children"] == []

    def test_a_page_no_toctree_lists_is_absent(self, navigation) -> None:
        def urls(entries):
            for each in entries:
                yield each["url"]
                yield from urls(each["children"])

        listed = [
            url for group in navigation["groups"] for url in urls(group["entries"])
        ]

        assert "orphan/" not in listed

    def test_a_title_with_markup_characters_is_stored_as_literal_text(
        self, navigation
    ) -> None:
        titles = [each["title"] for each in navigation["groups"][0]["entries"]]

        assert "Fish <b>& chips</b>" in titles

    def test_a_root_document_without_a_toctree_has_no_groups(
        self, tmp_path, sphinx_build
    ) -> None:
        source = tmp_path / "source"
        source.mkdir()
        (source / "conf.py").write_text('extensions = ["mvp_sphinx.navigation"]\n')
        (source / "index.rst").write_text("Alone\n=====\n")

        out = sphinx_build(source)

        assert json.loads((out / DocsBuild.NAVIGATION_FILE).read_text()) == {
            "groups": []
        }

    def test_a_build_with_another_builder_writes_no_navigation_file(
        self, sphinx_build
    ) -> None:
        out = sphinx_build(SPHINX_SOURCES / "contents", builder="html")

        assert not (out / DocsBuild.NAVIGATION_FILE).exists()


class TestNavigationWriter:
    # Sphinx 9 stops with a recursion error on a toctree cycle, so no real build
    # reaches the writer with one; a stand-in environment stands for it.
    def test_a_toctree_pointing_back_up_the_tree_stops_at_the_repeat(
        self, tmp_path
    ) -> None:
        def toctree(*refs):
            return addnodes.toctree(entries=[(None, ref) for ref in refs])

        doctrees = {
            "index": nodes.container("", toctree("a")),
            "a": nodes.container("", toctree("b")),
            "b": nodes.container("", toctree("a", "index")),
        }
        app = SimpleNamespace(
            env=SimpleNamespace(
                titles={name: nodes.title(text=name) for name in doctrees},
                get_doctree=doctrees.get,
            ),
            builder=SimpleNamespace(get_target_uri=lambda name: f"{name}/"),
            config=SimpleNamespace(root_doc="index"),
            outdir=tmp_path,
        )

        (group,) = NavigationWriter(app).groups()

        (a,) = group["entries"]
        (b,) = a["children"]
        assert b["children"] == []

    def test_a_build_that_failed_writes_no_navigation_file(self, tmp_path) -> None:
        app = SimpleNamespace(builder=SimpleNamespace(name="json"), outdir=tmp_path)

        write_navigation(app, RuntimeError("the build failed"))

        assert not (tmp_path / DocsBuild.NAVIGATION_FILE).exists()
