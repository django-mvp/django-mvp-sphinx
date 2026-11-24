"""build_docs runs the Sphinx build for the project's documentation apps."""

import re
import shutil
import sys
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings

from demo.mounted import docs, staff_guide
from mvp_sphinx.docs_build import DocsBuild
from tests.conftest import SPHINX_SOURCES
from tests.urls import handbook


@pytest.fixture
def apps(monkeypatch, tmp_path):
    # The suite's three mounted apps, each building into the test's own
    # directory. Only the first two say where their source is.
    monkeypatch.setattr(docs, "source_dir", SPHINX_SOURCES / "guide")
    monkeypatch.setattr(staff_guide, "source_dir", SPHINX_SOURCES / "handbook")
    monkeypatch.setattr(handbook, "source_dir", None)
    for app in (docs, staff_guide, handbook):
        monkeypatch.setattr(app, "build_dir", tmp_path / app.namespace)
    return {app.namespace: app for app in (docs, staff_guide, handbook)}


def front_page(app):
    return DocsBuild(app.build_dir).page("")


class TestBuildDocs:
    def test_it_builds_every_app_that_has_a_source_dir(self, apps) -> None:
        call_command("build_docs", verbosity=0)

        assert front_page(apps["docs"]) is not None
        assert front_page(apps["staff_guide"]) is not None

    def test_the_build_holds_the_navigation_file(self, apps) -> None:
        call_command("build_docs", "staff_guide", verbosity=0)

        assert DocsBuild(apps["staff_guide"].build_dir).navigation() is not None

    def test_a_build_uses_the_daisyui_theme_by_default(self, apps) -> None:
        call_command("build_docs", "staff_guide", verbosity=0)

        written = apps["staff_guide"].build_dir / DocsBuild.THEME_STYLESHEET
        assert written.is_file()

    def test_a_conf_that_names_a_theme_keeps_it(
        self, apps, monkeypatch, tmp_path
    ) -> None:
        source = tmp_path / "own-theme"
        source.mkdir()
        (source / "conf.py").write_text('project = "Own"\nhtml_theme = "basic"\n')
        (source / "index.rst").write_text("Own\n===\n")
        monkeypatch.setattr(docs, "source_dir", source)

        call_command("build_docs", "docs", verbosity=0)

        assert front_page(apps["docs"]) is not None
        assert not (apps["docs"].build_dir / DocsBuild.THEME_STYLESHEET).exists()

    def test_an_app_without_a_source_dir_is_left_alone(self, apps) -> None:
        call_command("build_docs", verbosity=0)

        assert not apps["handbook"].build_dir.exists()

    def test_naming_an_app_builds_that_one_only(self, apps) -> None:
        call_command("build_docs", "staff_guide", verbosity=0)

        assert front_page(apps["staff_guide"]) is not None
        assert not apps["docs"].build_dir.exists()

    def test_a_namespace_no_app_has_is_an_error(self, apps) -> None:
        with pytest.raises(CommandError):
            call_command("build_docs", "nothing-mounted-here", verbosity=0)

    def test_a_wrong_namespace_builds_nothing(self, apps) -> None:
        with pytest.raises(CommandError):
            call_command("build_docs", "docs", "nothing-mounted-here", verbosity=0)

        assert not apps["docs"].build_dir.exists()

    def test_naming_an_app_without_a_source_dir_is_an_error(self, apps) -> None:
        with pytest.raises(CommandError):
            call_command("build_docs", "handbook", verbosity=0)

    def test_no_app_with_a_source_dir_is_an_error(self, apps, monkeypatch) -> None:
        monkeypatch.setattr(docs, "source_dir", None)
        monkeypatch.setattr(staff_guide, "source_dir", None)

        with pytest.raises(CommandError):
            call_command("build_docs", verbosity=0)

    def test_a_build_sphinx_fails_is_an_error(
        self, apps, monkeypatch, tmp_path
    ) -> None:
        # A source directory with no conf.py is one Sphinx refuses.
        monkeypatch.setattr(docs, "source_dir", tmp_path / "no-sphinx-project")

        with pytest.raises(CommandError):
            call_command("build_docs", "docs", verbosity=0)

    def test_a_failed_build_stops_the_ones_after_it(
        self, apps, monkeypatch, tmp_path
    ) -> None:
        monkeypatch.setattr(docs, "source_dir", tmp_path / "no-sphinx-project")

        with pytest.raises(CommandError):
            call_command("build_docs", verbosity=0)

        assert not apps["staff_guide"].build_dir.exists()

    def test_sphinx_not_installed_is_an_error(self, apps, monkeypatch) -> None:
        # None in sys.modules is how Python records a module that cannot be found.
        monkeypatch.setitem(sys.modules, "sphinx", None)

        with pytest.raises(CommandError):
            call_command("build_docs", verbosity=0)

        assert not apps["docs"].build_dir.exists()


LANGUAGES = [
    ("en", "English"),
    ("de", "German"),
    ("pt-br", "Brazilian Portuguese"),
    ("it", "Italian"),
]


def make_source(root, catalogues, conf="", language=None):
    root.mkdir()
    (root / "conf.py").write_text(f'project = "Tiny"\n{conf}')
    (root / "index.rst").write_text("Tiny\n====\n")
    for code in catalogues:
        catalogue = root / "locales" / code / "LC_MESSAGES" / "index.po"
        catalogue.parent.mkdir(parents=True)
        catalogue.write_text(
            f'msgid ""\nmsgstr ""\n"Content-Type: text/plain; charset=UTF-8\\n"\n'
            f'"Language: {code}\\n"\n\nmsgid "Tiny"\nmsgstr "Winzig"\n'
        )
    return root


def folders(build_dir):
    return sorted(
        folder.name
        for folder in build_dir.iterdir()
        if (folder / DocsBuild.CONTEXT_FILE).exists()
    )


@pytest.fixture
def tiny(monkeypatch, tmp_path):
    def mount(catalogues, conf=""):
        source = make_source(tmp_path / "tiny", catalogues, conf)
        monkeypatch.setattr(docs, "source_dir", source)
        monkeypatch.setattr(docs, "build_dir", tmp_path / "build")
        return docs

    return mount


@pytest.fixture(scope="module")
def translated(tmp_path_factory):
    root = tmp_path_factory.mktemp("translated-builds")
    source = shutil.copytree(SPHINX_SOURCES / "translated", root / "source")
    with pytest.MonkeyPatch.context() as patch, override_settings(LANGUAGES=LANGUAGES):
        patch.setattr(docs, "source_dir", source)
        patch.setattr(docs, "build_dir", root / "build")
        out = StringIO()
        call_command("build_docs", "docs", stdout=out)
        return docs.build_dir, out.getvalue()


class TestTranslatedBuilds:
    def test_the_source_language_and_each_offered_translation_get_a_folder(
        self, translated
    ) -> None:
        build_dir, _ = translated

        assert folders(build_dir) == ["de", "en", "pt_BR"]

    def test_nothing_is_built_straight_into_the_build_dir(self, translated) -> None:
        build_dir, _ = translated

        assert not (build_dir / DocsBuild.CONTEXT_FILE).exists()

    def test_each_build_is_made_in_its_language(self, translated) -> None:
        build_dir, _ = translated

        titles = {
            code: DocsBuild(build_dir / code).page("")["title"]
            for code in ["en", "de", "pt_BR"]
        }
        assert titles == {"en": "Welcome", "de": "Willkommen", "pt_BR": "Bem-vindo"}

    def test_a_translation_the_site_does_not_offer_is_not_built(
        self, translated
    ) -> None:
        build_dir, _ = translated

        assert not (build_dir / "fr").exists()

    def test_the_skipped_translations_are_reported_in_one_line(
        self, translated
    ) -> None:
        _, output = translated

        reports = [line for line in output.splitlines() if re.search(r"\bfr\b", line)]
        assert len(reports) == 1
        assert "docs" in reports[0]

    def test_a_quiet_run_reports_nothing(self, tiny) -> None:
        tiny(["fr"])
        out = StringIO()

        with override_settings(LANGUAGES=LANGUAGES):
            call_command("build_docs", "docs", verbosity=0, stdout=out)

        assert out.getvalue() == ""

    def test_the_source_language_conf_sets_is_built_once_beside_a_translation(
        self, tiny
    ) -> None:
        app = tiny(["en"], conf='language = "de"\n')

        with override_settings(LANGUAGES=LANGUAGES):
            call_command("build_docs", "docs", verbosity=0)

        assert folders(app.build_dir) == ["de", "en"]
        assert DocsBuild(app.build_dir / "de").page("")["title"] == "Tiny"

    def test_catalogues_for_the_source_language_are_not_a_translation(
        self, tiny
    ) -> None:
        app = tiny(["en"])

        with override_settings(LANGUAGES=LANGUAGES):
            call_command("build_docs", "docs", verbosity=0)

        assert (app.build_dir / DocsBuild.CONTEXT_FILE).exists()
        assert folders(app.build_dir) == []

    def test_catalogues_for_the_source_language_leave_it_built_once(self, tiny) -> None:
        app = tiny(["en", "de"])

        with override_settings(LANGUAGES=LANGUAGES):
            call_command("build_docs", "docs", verbosity=0)

        assert folders(app.build_dir) == ["de", "en"]

    def test_a_translated_app_and_an_untranslated_one_each_get_their_layout(
        self, tiny, monkeypatch, tmp_path
    ) -> None:
        app = tiny(["de"])
        monkeypatch.setattr(staff_guide, "source_dir", SPHINX_SOURCES / "handbook")
        monkeypatch.setattr(staff_guide, "build_dir", tmp_path / "staff-build")

        with override_settings(LANGUAGES=LANGUAGES):
            call_command("build_docs", "docs", "staff_guide", verbosity=0)

        assert folders(app.build_dir) == ["de", "en"]
        assert (staff_guide.build_dir / DocsBuild.CONTEXT_FILE).exists()


def old_build(directory, *extra):
    for name in [DocsBuild.CONTEXT_FILE, "index.fjson", "_static/old.css", *extra]:
        path = directory / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("old")


def build(languages=None):
    with override_settings(LANGUAGES=languages or LANGUAGES):
        call_command("build_docs", "docs", verbosity=0)


class TestClearingTheOtherLayout:
    def test_a_single_build_gives_way_to_language_folders(self, tiny) -> None:
        app = tiny(["de"])
        old_build(app.build_dir, ".doctrees/environment.pickle")

        build()

        assert sorted(child.name for child in app.build_dir.iterdir()) == ["de", "en"]

    def test_language_folders_give_way_to_a_single_build(self, tiny) -> None:
        app = tiny([])
        old_build(app.build_dir / "de")
        old_build(app.build_dir / "en")

        build()

        assert folders(app.build_dir) == []
        assert not (app.build_dir / "de").exists()
        assert (app.build_dir / DocsBuild.CONTEXT_FILE).exists()

    def test_a_language_the_site_stopped_offering_is_removed(self, tiny) -> None:
        app = tiny(["de"])
        old_build(app.build_dir / "fr")

        build()

        assert folders(app.build_dir) == ["de", "en"]

    def test_the_folders_it_rebuilds_are_kept_for_an_incremental_build(
        self, tiny
    ) -> None:
        app = tiny(["de"])
        old_build(app.build_dir / "de", ".doctrees/environment.pickle")

        build()

        assert (app.build_dir / "de" / ".doctrees" / "environment.pickle").exists()

    def test_a_build_dir_holding_no_build_loses_nothing(self, tiny) -> None:
        app = tiny(["de"])
        (app.build_dir / "other").mkdir(parents=True)
        (app.build_dir / "notes.txt").write_text("keep")

        build()

        assert (app.build_dir / "other").is_dir()
        assert (app.build_dir / "notes.txt").read_text() == "keep"

    def test_a_folder_that_is_not_a_build_survives_a_single_build(self, tiny) -> None:
        app = tiny([])
        (app.build_dir / "other").mkdir(parents=True)

        build()

        assert (app.build_dir / "other").is_dir()
