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
