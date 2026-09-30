"""Following the README's quickstart gets a project to a working documentation page."""

import shutil
from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from django.urls import reverse
from mvp.menus import AppMenu
from sphinx.cmd.build import build_main

from tests.urls_quickstart import docs

SOURCE = Path(__file__).parent / "sphinx" / "quickstart"
FRONT_PAGE = "/help/guide/"


def run_build(source: Path, out: Path, *options: str) -> None:
    # Step 3's command, with -W so the test's own source must build clean.
    arguments = ["-b", "json", "-W", *options, str(source), str(out)]
    assert build_main(arguments) == 0


def page_address(name: str) -> str:
    return reverse("quickstart:page", kwargs={"path": f"{name}/"})


def sidebar_of(app, response):
    # The app's own menu, a navigation landmark named after the app.
    return BeautifulSoup(response.content, "html.parser").find(
        attrs={"role": "navigation", "aria-label": str(app.name)}
    )


def leaves(item) -> list[str]:
    return [each.url for each in item.visible_children if not each.is_parent]


@pytest.fixture
def source(tmp_path) -> Path:
    shutil.copytree(SOURCE, tmp_path / "docs")
    return tmp_path / "docs"


@pytest.fixture
def build_dir(source) -> Path:
    return source / "_build" / "json"


@pytest.fixture
def quickstart(db, settings, monkeypatch, source, build_dir):
    run_build(source, build_dir)
    monkeypatch.setattr(docs, "build_dir", build_dir)
    settings.ROOT_URLCONF = "tests.urls_quickstart"
    # Step 5. AppMenu is process-wide, so the entry comes out again afterwards.
    entry = docs.menu_item()
    AppMenu.append(entry)
    yield docs
    AppMenu.pop(entry.name)


class TestQuickstart:
    def test_the_front_page_answers_in_the_shell_at_the_chosen_prefix(
        self, client, quickstart
    ) -> None:
        response = client.get(reverse("quickstart:front_page"))

        assert reverse("quickstart:front_page") == FRONT_PAGE
        assert response.status_code == 200
        assert sidebar_of(quickstart, response).find("a", href=FRONT_PAGE)

    def test_the_contents_group_holds_both_pages_and_each_answers(
        self, client, quickstart, rf
    ) -> None:
        tree = quickstart.menu.process(rf.get(FRONT_PAGE))
        groups = [each for each in tree.visible_children if each.is_parent]

        assert len(groups) == 1
        assert leaves(groups[0]) == [page_address("first"), page_address("second")]
        assert [client.get(url).status_code for url in leaves(groups[0])] == [200, 200]

    def test_the_host_menu_entry_leads_to_the_front_page(
        self, client, quickstart, sidebar
    ) -> None:
        host_page = client.get(reverse("overview")).content.decode()
        entry = BeautifulSoup(sidebar(host_page), "html.parser").find(
            "a", href=FRONT_PAGE
        )

        response = client.get(entry["href"])

        assert response.status_code == 200
        assert response.context["page_data"]["current_page_name"] == "index"

    def test_a_rebuild_into_the_same_folder_adds_a_page_to_the_next_request(
        self, client, quickstart, source, build_dir
    ) -> None:
        before = client.get(page_address("third"))
        (source / "third.rst").write_text("The third page\n==============\n")
        index = source / "index.rst"
        index.write_text(index.read_text() + "   third\n")

        # Sphinx 9.1 warns that it will not overwrite the copies it keeps of
        # changed sources, which -W would turn into a failed rebuild.
        run_build(source, build_dir, "-D", "suppress_warnings=misc.copy_overwrite")
        after = client.get(page_address("third"))
        sidebar = sidebar_of(quickstart, client.get(FRONT_PAGE))

        assert before.status_code == 404
        assert after.status_code == 200
        assert sidebar.find("a", href=page_address("third"))
