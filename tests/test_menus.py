"""DocumentationMenu turns the navigation file into the app sidebar's menu."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from flex_menu import MenuItem
from mvp.menus import MenuGroup

from mvp_sphinx.docs_build import DocsBuild
from mvp_sphinx.menus import ContentsEntry


def label(item) -> str:
    return item.extra_context["label"]


def below(item) -> list:
    """Return the processed items drawn under ``item``."""
    return item.pages if isinstance(item, ContentsEntry) else item.visible_children


def outline(items) -> list:
    """Reduce processed items to their address, or label, and what is drawn below."""
    found = []
    for item in items:
        name = item.url or label(item)
        found.append([name, outline(below(item))] if below(item) else name)
    return found


def leaves(items) -> list[str]:
    """Return every address the processed items draw a link to, in order."""
    found = []
    for item in items:
        found += [item.url] if item.url else []
        found += leaves(below(item))
    return found


def every_entry(items) -> list:
    """Return every unprocessed entry of the contents, the pages under each too."""
    found = []
    for item in items:
        under = item.pages if isinstance(item, ContentsEntry) else item.children
        found += [item, *every_entry(under)]
    return found


def child(item, text):
    return next(each for each in below(item) if label(each) == text)


def raw_child(item, text):
    return next(each for each in item.children if label(each) == text)


def marked(items) -> list[str]:
    """Return the names of the links marked as the page being read."""
    found = []
    for item in items:
        current = item.extra_context.get("current", item.selected and not below(item))
        if item.url and current:
            found.append(item.name)
        found += marked(below(item))
    return found


def opened(items) -> set[str]:
    """Return the names of the items on the way to the page, the page itself not."""
    found = set()
    for item in items:
        if item.selected and below(item):
            found.add(item.name)
        found |= opened(below(item))
    return found


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

    def test_the_front_page_entry_is_labelled_with_the_root_documents_title(
        self, processed, contents_build
    ) -> None:
        first = processed().visible_children[0]

        assert label(first) == DocsBuild(contents_build).front_page_title()

    def test_groups_and_uncaptioned_entries_follow_in_the_files_order(
        self, processed
    ) -> None:
        top = processed().visible_children[1:]

        assert [each.url or label(each) for each in top] == [
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

    def test_every_page_is_an_entry_linking_to_it_with_its_pages_under_it(
        self, contents_app, processed
    ) -> None:
        processed()
        one = raw_child(raw_child(contents_app.menu, "Getting started"), "Chain one")

        assert type(one) is ContentsEntry
        assert [
            (each.extra_context["page_url"], len(each.pages))
            for each in every_entry([one])
        ] == [("/docs/chain/one/", 1), ("/docs/chain/two/", 1), ("/docs/chain/three/", 0)]

    def test_an_entry_fetches_its_pages_from_the_apps_contents_address(
        self, contents_app, processed
    ) -> None:
        processed()
        one = raw_child(raw_child(contents_app.menu, "Getting started"), "Chain one")

        assert one.extra_context["branch_url"] == "/docs/contents/?entry=chain%2Fone%2F"

    def test_every_page_is_the_mount_prefix_plus_the_entrys_address(
        self, processed, contents_app, contents_build
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
        processed()

        assert {
            each.extra_context["page_url"]
            for each in every_entry(contents_app.menu.contents)
            if isinstance(each, ContentsEntry)
        } == {f"/docs/{url}" for url in listed}

    def test_every_link_sits_under_the_prefix_a_second_app_is_mounted_at(
        self, handbook_app, contents_build, monkeypatch, rf
    ) -> None:
        monkeypatch.setattr(handbook_app, "build_dir", contents_build)

        menu = handbook_app.menu.process(rf.get("/manuals/admin/chain/three/"))

        assert all(
            url.startswith("/manuals/admin/") for url in leaves(menu.visible_children)
        )

    def test_the_top_entries_are_the_same_on_every_page(self, processed) -> None:
        def top(tree):
            return [
                [each.url or label(each), [e.url for e in each.visible_children]]
                for each in tree.visible_children
            ]

        assert top(processed("/docs/")) == top(processed("/docs/chain/three/"))

    def test_a_page_at_the_top_draws_no_page_below_the_top_entries(
        self, processed
    ) -> None:
        assert "/docs/chain/two/" not in leaves(processed("/docs/").visible_children)

    def test_a_deep_page_draws_every_entry_on_its_way(self, processed) -> None:
        one = child(child(processed("/docs/chain/three/"), "Getting started"), "Chain one")

        assert outline([one]) == [
            ["/docs/chain/one/", [["/docs/chain/two/", ["/docs/chain/three/"]]]]
        ]

    def test_a_page_outside_the_documentation_draws_the_top_entries_alone(
        self, processed
    ) -> None:
        assert set(leaves(processed("/").visible_children)) == set(
            leaves(processed("/docs/").visible_children)
        )

    def test_a_label_with_markup_characters_is_a_plain_string(self, processed) -> None:
        item = child(child(processed(), "Getting started"), "Fish <b>& chips</b>")

        assert type(label(item)) is str


class TestBranch:
    def test_an_entry_gives_its_pages_each_closed(self, contents_app, rf) -> None:
        pages = contents_app.menu.branch(rf.get("/docs/contents/"), "chain/one/")

        assert [(each.url, each.pages) for each in pages] == [("/docs/chain/two/", [])]
        assert pages[0].extra_context["branch"]
        assert not pages[0].extra_context["open"]

    def test_an_entry_listed_below_the_top_is_found(self, contents_app, rf) -> None:
        pages = contents_app.menu.branch(rf.get("/docs/contents/"), "chain/two/")

        assert [each.url for each in pages] == ["/docs/chain/three/"]

    @pytest.mark.parametrize("address", ["", "install/", "chain/three/", "nowhere/"])
    def test_an_address_with_no_pages_under_it_gives_none(
        self, contents_app, rf, address
    ) -> None:
        assert contents_app.menu.branch(rf.get("/docs/contents/"), address) is None


class TestMenuSettings:
    @pytest.fixture
    def menu(self, menu_settings_app, rf):
        def process(address="/docs/"):
            return menu_settings_app.menu.process(rf.get(address))

        return process

    def test_a_group_page_is_an_entry_in_the_group_style(
        self, menu, menu_settings_app
    ) -> None:
        heading = child(menu("/docs/heading/one/"), "Heading")

        assert heading.extra_context["style"] == "group"
        assert outline([heading]) == [["/docs/heading/", ["/docs/heading/one/"]]]

    def test_a_hidden_page_with_pages_of_its_own_keeps_its_section_without_a_link(
        self, menu
    ) -> None:
        quiet = child(menu("/docs/quiet/one/"), "Quiet")

        assert outline([quiet]) == [
            ["Quiet", ["/docs/quiet/one/", "/docs/quiet/two/"]]
        ]
        assert quiet.extra_context["branch"]

    def test_a_hidden_group_page_is_a_section_without_a_link_in_the_group_style(
        self, menu
    ) -> None:
        quiet = child(menu("/docs/quiet-heading/one/"), "Quiet heading")

        assert quiet.extra_context["style"] == "group"
        assert outline([quiet]) == [["Quiet heading", ["/docs/quiet-heading/one/"]]]

    def test_a_hidden_page_is_left_out_of_its_section(self, menu) -> None:
        ordinary = child(menu("/docs/ordinary/"), "Ordinary")

        assert outline([ordinary]) == [["/docs/ordinary/", ["/docs/ordinary/kept/"]]]

    def test_a_page_whose_pages_are_all_hidden_is_a_link(self, menu) -> None:
        emptied = child(menu("/docs/emptied/"), "Emptied")

        assert outline([emptied]) == ["/docs/emptied/"]
        assert not emptied.extra_context["branch"]

    def test_the_settings_on_a_page_without_pages_of_its_own(self, menu) -> None:
        items = outline(menu().visible_children)

        assert "/docs/shown/" in items
        assert "/docs/hidden/" not in items

    def test_reading_a_hidden_page_opens_its_section_and_marks_no_entry(
        self, menu
    ) -> None:
        tree = menu("/docs/quiet/")

        assert child(tree, "Quiet").extra_context["open"]
        assert marked(tree.visible_children) == []

    def test_a_file_written_before_the_settings_draws_as_it_did(
        self, menu_settings_app, tmp_path, monkeypatch, rf
    ) -> None:
        contents = {
            "title": "Old",
            "groups": [
                {
                    "caption": "",
                    "entries": [
                        {
                            "title": "Section",
                            "url": "section/",
                            "children": [
                                {"title": "Page", "url": "page/", "children": []}
                            ],
                        }
                    ],
                }
            ],
        }
        (tmp_path / DocsBuild.NAVIGATION_FILE).write_text(json.dumps(contents))
        monkeypatch.setattr(menu_settings_app, "build_dir", tmp_path)

        tree = menu_settings_app.menu.process(rf.get("/docs/page/"))

        assert outline([child(tree, "Section")]) == [
            ["/docs/section/", ["/docs/page/"]]
        ]
        assert child(tree, "Section").extra_context["style"] == "collapse"


class TestCurrentPage:
    def test_a_page_nested_in_two_entries_is_the_only_marked_link(
        self, processed
    ) -> None:
        tree = processed("/docs/chain/three/").visible_children

        assert marked(tree) == ["g0-2-0-0"]

    def test_every_item_holding_the_page_is_open_and_no_other(
        self, processed
    ) -> None:
        tree = processed("/docs/chain/three/").visible_children

        assert opened(tree) == {"g0", "g0-2", "g0-2-0"}

    def test_a_page_with_pages_of_its_own_is_marked_and_open(
        self, processed
    ) -> None:
        tree = processed("/docs/chain/one/").visible_children
        one = child(child(processed("/docs/chain/one/"), "Getting started"), "Chain one")

        assert marked(tree) == ["g0-2"]
        assert opened(tree) == {"g0", "g0-2"}
        assert one.extra_context["open"]

    def test_the_front_page_entry_is_the_only_marked_item_on_the_front_page(
        self, processed
    ) -> None:
        tree = processed("/docs/").visible_children

        assert marked(tree) == ["front-page"]
        assert opened(tree) == set()

    def test_a_page_listed_twice_is_marked_at_both_places(self, processed) -> None:
        tree = processed("/docs/shared/").visible_children

        assert sorted(marked(tree)) == ["g0-4", "g2-1"]
        assert opened(tree) == {"g0", "g2"}

    def test_a_page_at_the_top_level_is_marked_without_any_group(
        self, processed
    ) -> None:
        tree = processed("/docs/standalone/").visible_children

        assert marked(tree) == ["g1-0"]
        assert opened(tree) == set()

    def test_a_page_no_toctree_lists_marks_nothing_and_draws_the_top_entries(
        self, processed
    ) -> None:
        tree = processed("/docs/orphan/").visible_children

        assert marked(tree) == []
        assert opened(tree) == set()
        assert outline(tree) == outline(processed("/").visible_children)

    def test_a_request_with_a_query_marks_the_same_link(self, processed) -> None:
        tree = processed("/docs/chain/three/?q=a#top").visible_children

        assert marked(tree) == ["g0-2-0-0"]


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
        second = processed("/docs/install/")

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


@pytest.fixture
def project_entry(contents_app):
    """Add an entry of the project's own to the menu, and take it out afterwards."""
    added = []

    def add(name, position=None, **kwargs):
        item = MenuItem(
            name=name, url=f"/{name}/", extra_context={"label": name}, **kwargs
        )
        if position is None:
            contents_app.menu.append(item)
        else:
            contents_app.menu.insert(item, position=position)
        added.append(item)
        return item

    yield add
    for item in added:
        item.parent = None


class TestProjectEntries:
    def test_an_appended_entry_follows_the_contents(
        self, processed, project_entry
    ) -> None:
        contents = leaves(processed().visible_children)

        project_entry("studio")

        assert leaves(processed().visible_children) == [*contents, "/studio/"]

    def test_an_entry_inserted_first_comes_before_the_front_page(
        self, processed, project_entry
    ) -> None:
        contents = leaves(processed().visible_children)

        project_entry("home", position=0)

        assert leaves(processed().visible_children) == ["/home/", *contents]

    def test_entries_added_before_the_first_processing_keep_their_places(
        self, processed, project_entry, replaceable
    ) -> None:
        project_entry("home", position=0)
        project_entry("studio")

        drawn = leaves(processed().visible_children)

        assert (drawn[0], drawn[1], drawn[-1]) == ("/home/", "/docs/", "/studio/")

    def test_entries_keep_their_places_across_a_rebuild(
        self, processed, project_entry, replaceable
    ) -> None:
        contents = leaves(processed().visible_children)
        project_entry("home", position=0)
        project_entry("studio")

        rewrite_contents(
            replaceable,
            lambda groups: groups[1]["entries"].append(
                {"title": "Added", "url": "added/", "children": []}
            ),
        )
        drawn = leaves(processed().visible_children)

        assert (drawn[0], drawn[-1]) == ("/home/", "/studio/")
        assert set(drawn[1:-1]) == {*contents, "/docs/added/"}

    def test_the_contents_are_still_drawn_without_the_front_page_entry(
        self, processed, contents_app, replaceable
    ) -> None:
        contents = leaves(processed().visible_children)
        front_page = contents_app.menu.pop("front-page")

        rewrite_contents(replaceable, lambda groups: None)
        try:
            drawn = leaves(processed().visible_children)
        finally:
            contents_app.menu.insert(front_page, position=0)

        assert drawn == contents[1:]

    def test_an_entry_whose_check_refuses_the_request_is_not_drawn(
        self, processed, project_entry
    ) -> None:
        contents = leaves(processed().visible_children)

        project_entry("studio", check=lambda request, **kwargs: False)

        assert leaves(processed().visible_children) == contents


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


class TestASubclassThatRefreshes:
    def test_a_subclass_overriding_refresh_without_arguments_still_draws(
        self, contents_app, rf, monkeypatch
    ) -> None:
        from mvp_sphinx.menus import DocumentationMenu

        class Relabelled(DocumentationMenu):
            def refresh(self) -> None:
                super().refresh()
                self.front_page.extra_context["label"] = "Start here"

        menu = Relabelled("relabelled-menu", app=contents_app)

        processed = menu.process(rf.get("/docs/"))

        assert label(processed.visible_children[0]) == "Start here"
        assert len(leaves(processed.visible_children)) > 1
