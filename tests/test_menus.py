"""DocumentationMenu turns the navigation file into the app sidebar's menu."""

import os
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
