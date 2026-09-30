"""DocumentationMenu turns the navigation file into the app sidebar's menu."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from mvp.menus import MenuCollapse, MenuGroup

from mvp_sphinx.docs_build import DocsBuild


def label(item) -> str:
    return item.extra_context["label"]


def outline(items) -> list:
    """Reduce processed items to their address, or their label and outline."""
    return [
        [label(item), outline(item.visible_children)] if item.is_parent else item.url
        for item in items
    ]


def leaves(items) -> list[str]:
    found = []
    for item in items:
        found += leaves(item.visible_children) if item.is_parent else [item.url]
    return found


def child(item, text):
    return next(each for each in item.visible_children if label(each) == text)


def raw_child(item, text):
    return next(each for each in item.children if label(each) == text)


@pytest.fixture
def processed(contents_app, rf):
    def process(address="/docs/"):
        return contents_app.menu.process(rf.get(address))

    return process


class TestDocumentationMenu:
    def test_the_menu_carries_the_apps_name(self, processed, contents_app) -> None:
        assert label(processed()) == contents_app.name

    def test_the_front_page_entry_comes_first_at_the_apps_address(
        self, processed
    ) -> None:
        first = processed().visible_children[0]

        assert first.url == "/docs/"

    def test_groups_and_uncaptioned_entries_follow_in_the_files_order(
        self, processed
    ) -> None:
        top = processed().visible_children[1:]

        assert [each.url if not each.is_parent else label(each) for each in top] == [
            "Getting started",
            "/docs/standalone/",
            "Reference",
            "/docs/hidden-page/",
        ]

    def test_a_captioned_group_is_a_menu_group_holding_its_entries_in_order(
        self, processed, contents_app
    ) -> None:
        group = child(processed(), "Getting started")

        assert type(raw_child(contents_app.menu, "Getting started")) is MenuGroup
        assert [label(each) for each in group.visible_children] == [
            "Install",
            "Chosen title",
            "Chain one",
            "Fish <b>& chips</b>",
            "Shared page",
        ]

    def test_a_page_with_children_is_a_collapsible_group_opening_on_its_own_page(
        self, processed, contents_app
    ) -> None:
        one = child(child(processed(), "Getting started"), "Chain one")
        raw = raw_child(contents_app.menu, "Getting started")

        assert type(raw_child(raw, "Chain one")) is MenuCollapse
        assert outline(one.visible_children) == [
            "/docs/chain/one/",
            [
                label(one.visible_children[1]),
                ["/docs/chain/two/", "/docs/chain/three/"],
            ],
        ]

    def test_every_leaf_is_the_mount_prefix_plus_the_entrys_address(
        self, processed, contents_build
    ) -> None:
        def addresses(entries):
            for entry in entries:
                yield entry["url"]
                yield from addresses(entry["children"])

        listed = {
            url
            for group in DocsBuild(contents_build).navigation()
            for url in addresses(group["entries"])
        }

        assert set(leaves(processed().visible_children)) == {
            "/docs/",
            *(f"/docs/{url}" for url in listed),
        }

    def test_every_leaf_sits_under_the_prefix_a_second_app_is_mounted_at(
        self, handbook_app, contents_build, monkeypatch, rf
    ) -> None:
        monkeypatch.setattr(handbook_app, "build_dir", contents_build)

        menu = handbook_app.menu.process(rf.get("/manuals/admin/"))

        assert all(
            url.startswith("/manuals/admin/") for url in leaves(menu.visible_children)
        )

    def test_the_tree_is_the_same_for_different_page_requests(self, processed) -> None:
        on_front_page = outline(processed("/docs/").visible_children)
        on_a_deep_page = outline(processed("/docs/chain/two/").visible_children)

        assert on_front_page == on_a_deep_page

    def test_a_label_with_markup_characters_is_a_plain_string(self, processed) -> None:
        item = child(child(processed(), "Getting started"), "Fish <b>& chips</b>")

        assert type(label(item)) is str


def selected_leaves(items) -> list[str]:
    """Return the names of the selected links in the processed tree."""
    found = []
    for item in items:
        if item.is_parent:
            found += selected_leaves(item.visible_children)
        elif item.selected:
            found.append(item.name)
    return found


def selected_groups(items) -> set[str]:
    """Return the names of the selected groups in the processed tree."""
    found = set()
    for item in items:
        if item.is_parent:
            if item.selected:
                found.add(item.name)
            found |= selected_groups(item.visible_children)
    return found


class TestCurrentPage:
    def test_a_page_nested_in_two_groups_is_the_only_selected_link(
        self, processed
    ) -> None:
        tree = processed("/docs/chain/three/").visible_children

        assert selected_leaves(tree) == ["g0-2-0-0"]

    def test_every_group_holding_the_page_is_selected_and_no_other(
        self, processed
    ) -> None:
        tree = processed("/docs/chain/three/").visible_children

        assert selected_groups(tree) == {"g0", "g0-2", "g0-2-0"}

    def test_the_link_to_a_page_with_pages_of_its_own_is_the_selected_link(
        self, processed
    ) -> None:
        tree = processed("/docs/chain/one/").visible_children

        assert selected_leaves(tree) == ["g0-2-page"]
        assert selected_groups(tree) == {"g0", "g0-2"}

    def test_the_front_page_entry_is_the_only_selected_item_on_the_front_page(
        self, processed
    ) -> None:
        tree = processed("/docs/").visible_children

        assert selected_leaves(tree) == ["front-page"]
        assert selected_groups(tree) == set()

    def test_a_page_listed_twice_is_selected_at_both_places(self, processed) -> None:
        tree = processed("/docs/shared/").visible_children

        assert sorted(selected_leaves(tree)) == ["g0-4", "g2-1"]
        assert selected_groups(tree) == {"g0", "g2"}

    def test_a_page_at_the_top_level_is_selected_without_any_group(
        self, processed
    ) -> None:
        tree = processed("/docs/standalone/").visible_children

        assert selected_leaves(tree) == ["g1-0"]
        assert selected_groups(tree) == set()

    def test_a_page_no_toctree_lists_selects_nothing_and_draws_the_full_contents(
        self, processed
    ) -> None:
        tree = processed("/docs/orphan/").visible_children

        assert selected_leaves(tree) == []
        assert selected_groups(tree) == set()
        assert outline(tree) == outline(processed("/docs/").visible_children)

    def test_a_request_with_a_query_selects_the_same_link(self, processed) -> None:
        tree = processed("/docs/chain/three/?q=a#top").visible_children

        assert selected_leaves(tree) == ["g0-2-0-0"]


@pytest.fixture
def replaceable(contents_app, contents_build, tmp_path, monkeypatch):
    """Point the app at a copy of the contents build the test may rewrite."""
    build = tmp_path / "rebuilt"
    shutil.copytree(contents_build, build)
    monkeypatch.setattr(contents_app, "build_dir", build)
    return build


def rewrite_contents(build, edit) -> None:
    """Change the build's contents as a new docs build would."""
    target = build / DocsBuild.NAVIGATION_FILE
    data = json.loads(target.read_text())
    edit(data["groups"])
    target.write_text(json.dumps(data))


class TestRefresh:
    @pytest.fixture
    def reads(self, monkeypatch) -> list:
        """Record every read of a navigation file."""
        found = []
        read = DocsBuild.navigation

        def counting(self):
            found.append(self.root)
            return read(self)

        monkeypatch.setattr(DocsBuild, "navigation", counting)
        return found

    def test_a_page_added_by_a_rebuild_is_in_the_next_processing(
        self, processed, replaceable
    ) -> None:
        before = leaves(processed().visible_children)

        rewrite_contents(
            replaceable,
            lambda groups: groups[1]["entries"].append(
                {"title": "Added", "url": "added/", "children": []}
            ),
        )

        assert set(leaves(processed().visible_children)) == {*before, "/docs/added/"}

    def test_a_page_removed_by_a_rebuild_is_gone_from_the_next_processing(
        self, processed, replaceable
    ) -> None:
        before = leaves(processed().visible_children)

        rewrite_contents(replaceable, lambda groups: groups[1]["entries"].clear())

        assert leaves(processed().visible_children) == [
            url for url in before if url != "/docs/standalone/"
        ]

    def test_the_file_is_not_read_again_while_it_is_unchanged(
        self, processed, replaceable, reads
    ) -> None:

        first = processed()
        second = processed("/docs/chain/two/")

        assert len(reads) == 1
        assert outline(first.visible_children) == outline(second.visible_children)

    def test_a_replaced_file_is_read_again(self, processed, replaceable, reads) -> None:
        processed()

        rewrite_contents(replaceable, lambda groups: groups.pop())
        processed()

        assert len(reads) == 2

    def test_pointing_the_app_at_another_build_rebuilds_the_menu(
        self, processed, contents_app, handbook_build, monkeypatch
    ) -> None:
        processed()

        monkeypatch.setattr(contents_app, "build_dir", handbook_build)

        assert set(leaves(processed().visible_children)) == {
            "/docs/",
            "/docs/backups/",
        }

    def test_pointing_the_app_at_the_same_build_by_another_path_reads_it_again(
        self, processed, contents_app, replaceable, reads, monkeypatch, tmp_path
    ) -> None:
        processed()
        link = tmp_path / "linked"
        link.symlink_to(replaceable)

        monkeypatch.setattr(contents_app, "build_dir", link)
        processed()

        assert len(reads) == 2

    def test_processing_under_another_mount_prefix_rebuilds_the_menu(
        self, processed, contents_app, handbook_app, monkeypatch
    ) -> None:
        processed()

        monkeypatch.setattr(contents_app, "landing", handbook_app.landing)

        assert all(
            url.startswith("/manuals/admin/")
            for url in leaves(processed("/manuals/admin/").visible_children)
        )


class TestServingSideImports:
    def test_the_documentation_app_imports_when_sphinx_cannot_be_imported(
        self,
    ) -> None:
        code = (
            "import sys; sys.modules['sphinx'] = None; "
            "import django; django.setup(); import mvp_sphinx.mounted"
        )

        result = subprocess.run(  # noqa: S603 - fixed arguments
            [sys.executable, "-c", code],
            cwd=Path(__file__).parent.parent,
            env={**os.environ, "DJANGO_SETTINGS_MODULE": "tests.settings"},
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0, result.stderr
