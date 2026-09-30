"""DocsBuild finds pages in a docs build and refuses addresses outside it."""

import json
import os
import shutil

import pytest

from mvp_sphinx.docs_build import DocsBuild


@pytest.fixture
def build(guide_build) -> DocsBuild:
    return DocsBuild(guide_build)


def entry(**overrides) -> dict:
    return {"title": "Page", "url": "page/", "children": []} | overrides


class TestPage:
    def test_the_empty_address_is_the_front_page(self, build) -> None:
        assert build.page("")["current_page_name"] == "index"

    def test_a_folder_address_is_the_folders_index_page(self, build) -> None:
        assert build.page("section/")["current_page_name"] == "section/index"

    def test_a_nested_address_is_the_nested_page(self, build) -> None:
        page = build.page("section/nested/page/")
        assert page["current_page_name"] == "section/nested/page"

    @pytest.mark.parametrize(
        "address",
        ["index/", "section/index/", "section//", "page/../section/", "./section/"],
    )
    def test_a_page_has_only_its_own_address(self, build, address) -> None:
        assert build.page(address) is None

    def test_an_absolute_address_is_not_a_page_even_inside_the_build(
        self, build, guide_build
    ) -> None:
        address = f"{guide_build.resolve().as_posix()}/section/"

        assert build.page(address) is None

    def test_a_top_level_page_is_found_by_its_name(self, build) -> None:
        assert build.page("page/")["current_page_name"] == "page"

    @pytest.mark.parametrize("address", ["page", "section", "section/nested/page"])
    def test_an_address_without_a_trailing_slash_is_not_a_page(
        self, build, address
    ) -> None:
        assert build.page(address) is None

    def test_an_unknown_address_is_not_a_page(self, build) -> None:
        assert build.page("nowhere/") is None

    @pytest.mark.parametrize(
        "address",
        ["../../outside/", "section/../../../outside/", "{outside}/"],
        ids=["parent", "parent-after-a-segment", "absolute"],
    )
    def test_an_address_leading_outside_the_build_is_not_a_page(
        self, tmp_path, address
    ) -> None:
        root = tmp_path / "build" / "json"
        root.mkdir(parents=True)
        outside = tmp_path / "outside"
        outside.mkdir()
        (outside / "index.fjson").write_text(json.dumps({"title": "Outside"}))
        (tmp_path / "outside.fjson").write_text(json.dumps({"title": "Outside"}))

        assert DocsBuild(root).page(address.format(outside=outside)) is None

    def test_an_address_holding_a_nul_byte_is_not_a_page(self, build) -> None:
        assert build.page("section/\x00/") is None

    def test_a_missing_build_root_has_no_pages(self, tmp_path) -> None:
        assert DocsBuild(tmp_path / "absent").page("") is None

    def test_a_build_reached_through_a_symlink_still_serves_pages(
        self, guide_build, tmp_path
    ) -> None:
        link = tmp_path / "linked"
        link.symlink_to(guide_build, target_is_directory=True)

        assert DocsBuild(link).page("section/")["current_page_name"] == "section/index"

    def test_a_page_file_that_is_not_valid_json_raises(
        self, guide_build, tmp_path
    ) -> None:
        broken = tmp_path / "broken"
        shutil.copytree(guide_build, broken)
        (broken / "page.fjson").write_text("{not json")

        with pytest.raises(json.JSONDecodeError):
            DocsBuild(broken).page("page/")


class TestFile:
    def test_an_image_is_found_by_its_name(self, build, guide_build) -> None:
        assert (
            build.file("_images/pixel.png")
            == (guide_build / "_images" / "pixel.png").resolve()
        )

    def test_a_download_is_found_below_its_hash_folder(
        self, build, guide_build
    ) -> None:
        target = next((guide_build / "_downloads").glob("*/sample.txt"))
        relative = target.relative_to(guide_build).as_posix()

        assert build.file(relative) == target.resolve()

    @pytest.mark.parametrize(
        "address",
        [
            "_images/../environment.pickle",
            "_images/../../outside.txt",
            "_downloads/../index.fjson",
            "_images/../_downloads/x/../../index.fjson",
        ],
    )
    def test_an_address_climbing_out_of_its_folder_is_not_a_file(
        self, build, address
    ) -> None:
        assert build.file(address) is None

    def test_a_symlink_pointing_outside_its_folder_is_not_a_file(
        self, guide_build, tmp_path
    ) -> None:
        copy = tmp_path / "build"
        shutil.copytree(guide_build, copy)
        secret = tmp_path / "secret.txt"
        secret.write_text("secret")
        (copy / "_images" / "leak.png").symlink_to(secret)

        assert DocsBuild(copy).file("_images/leak.png") is None

    def test_a_file_folder_linked_outside_the_build_is_not_served(
        self, guide_build, tmp_path
    ) -> None:
        copy = tmp_path / "build"
        shutil.copytree(guide_build, copy)
        outside = tmp_path / "outside"
        outside.mkdir()
        (outside / "secret.txt").write_text("secret")
        shutil.rmtree(copy / "_images")
        (copy / "_images").symlink_to(outside, target_is_directory=True)

        assert DocsBuild(copy).file("_images/secret.txt") is None

    def test_a_missing_name_is_not_a_file(self, build) -> None:
        assert build.file("_images/missing.png") is None

    def test_a_folder_is_not_a_file(self, build) -> None:
        assert build.file("_images/") is None
        assert build.file("_downloads/") is None

    def test_an_address_holding_a_nul_byte_is_not_a_file(self, build) -> None:
        assert build.file("_images/\x00.png") is None

    @pytest.mark.parametrize(
        "address",
        [
            "globalcontext.json",
            "searchindex.json",
            "environment.pickle",
            "_sources/index.rst.txt",
            "index.fjson",
            "page.fjson",
            "_static/basic.css",
            ".doctrees/environment.pickle",
        ],
    )
    def test_anything_outside_the_image_and_download_folders_is_not_a_file(
        self, build, address
    ) -> None:
        assert build.file(address) is None


class TestNavigation:
    @pytest.fixture
    def written(self, tmp_path):
        def write(content: str | bytes):
            data = content.encode() if isinstance(content, str) else content
            (tmp_path / DocsBuild.NAVIGATION_FILE).write_bytes(data)
            return DocsBuild(tmp_path)

        return write

    def test_the_contents_builds_file_gives_its_groups(self, contents_build) -> None:
        groups = DocsBuild(contents_build).navigation()

        assert [group["caption"] for group in groups] == [
            "Getting started",
            "",
            "Reference",
            "",
        ]

    def test_no_file_gives_none(self, tmp_path) -> None:
        assert DocsBuild(tmp_path).navigation() is None

    def test_a_file_that_is_not_json_gives_none(self, written) -> None:
        assert written("{not json").navigation() is None

    def test_a_file_of_invalid_utf8_gives_none(self, written) -> None:
        assert written(b"\xff\xfe\x00").navigation() is None

    @pytest.mark.parametrize(
        "content",
        [
            [],
            {"groups": {}},
            {"groups": [{"caption": "", "entries": [{"title": "T", "url": ""}]}]},
            {"groups": [{"caption": "Only"}]},
            {"groups": [{"entries": []}]},
            {"groups": [{"caption": "", "entries": [entry(children="none")]}]},
            {"groups": [{"caption": "", "entries": [entry(title=3)]}]},
            {"groups": [{"caption": "", "entries": [entry(url=None)]}]},
            {
                "groups": [
                    {"caption": "", "entries": [entry(children=[entry(title=3)])]}
                ]
            },
        ],
        ids=[
            "top-level-list",
            "groups-not-a-list",
            "entry-without-children",
            "group-without-entries",
            "group-without-caption",
            "children-not-a-list",
            "non-string-title",
            "non-string-url",
            "bad-grandchild",
        ],
    )
    def test_valid_json_of_the_wrong_shape_gives_none(self, written, content) -> None:
        assert written(json.dumps(content)).navigation() is None

    def test_a_file_that_is_a_symlink_out_of_the_build_gives_none(
        self, tmp_path
    ) -> None:
        build = tmp_path / "build"
        build.mkdir()
        outside = tmp_path / "outside.json"
        outside.write_text('{"groups": []}')
        (build / DocsBuild.NAVIGATION_FILE).symlink_to(outside)

        assert DocsBuild(build).navigation() is None


class TestNavigationStamp:
    def test_a_present_file_has_a_stamp(self, contents_build) -> None:
        assert DocsBuild(contents_build).navigation_stamp() is not None

    def test_no_file_has_no_stamp(self, tmp_path) -> None:
        assert DocsBuild(tmp_path).navigation_stamp() is None

    def test_replacing_the_file_changes_the_stamp(self, tmp_path) -> None:
        build = DocsBuild(tmp_path)
        target = tmp_path / DocsBuild.NAVIGATION_FILE
        target.write_text('{"groups": []}')
        staging = tmp_path / "staging"
        staging.write_text('{"groups": []}')
        # Same size and time, so only the file's identity can tell them apart.
        os.utime(target, ns=(10**18, 10**18))
        os.utime(staging, ns=(10**18, 10**18))
        before = build.navigation_stamp()

        staging.replace(target)

        assert build.navigation_stamp() != before
