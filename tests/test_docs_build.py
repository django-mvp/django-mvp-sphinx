"""DocsBuild finds pages in a docs build and refuses addresses outside it."""

import json
import shutil

import pytest

from mvp_sphinx.docs_build import DocsBuild


@pytest.fixture
def build(guide_build) -> DocsBuild:
    return DocsBuild(guide_build)


class TestPage:
    def test_the_empty_address_is_the_front_page(self, build) -> None:
        assert build.page("")["current_page_name"] == "index"

    def test_a_folder_address_is_the_folders_index_page(self, build) -> None:
        assert build.page("section/")["current_page_name"] == "section/index"

    def test_a_nested_address_is_the_nested_page(self, build) -> None:
        page = build.page("section/nested/page/")
        assert page["current_page_name"] == "section/nested/page"

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
