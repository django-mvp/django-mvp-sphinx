"""The languages a docs source is translated into, and the build that serves a reader."""

import sys
from pathlib import Path

import pytest

from mvp_sphinx.docs_build import DocsBuild
from mvp_sphinx.languages import (
    build_for,
    conf_assignments,
    conf_value,
    language_builds,
    site_languages,
    source_language,
    translations,
)


def make_source(root, conf="", catalogues=()):
    root.mkdir(exist_ok=True)
    (root / "conf.py").write_text(conf)
    for catalogue in catalogues:
        path = root / catalogue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("")
    return root


class TestConf:
    def test_a_literal_assignment_is_read(self, tmp_path) -> None:
        source = make_source(tmp_path / "docs", 'language = "de"\n')

        assert conf_value(source, "language", None) == "de"

    def test_a_name_conf_never_assigns_gets_the_default(self, tmp_path) -> None:
        source = make_source(tmp_path / "docs", 'project = "Docs"\n')

        assert conf_value(source, "language", "en") == "en"

    def test_a_value_that_is_not_a_literal_gets_the_default(self, tmp_path) -> None:
        source = make_source(
            tmp_path / "docs", 'import os\nlanguage = os.environ["DOCS_LANGUAGE"]\n'
        )

        assert conf_value(source, "language", "en") == "en"

    def test_the_names_conf_assigns_are_listed(self, tmp_path) -> None:
        source = make_source(tmp_path / "docs", 'project = "Docs"\nhtml_theme = "x"\n')

        assert set(conf_assignments(source)) == {"project", "html_theme"}

    @pytest.mark.parametrize("conf", [None, "language = (\n"])
    def test_a_conf_that_cannot_be_read_assigns_nothing(self, tmp_path, conf) -> None:
        source = tmp_path / "docs"
        source.mkdir()
        if conf is not None:
            (source / "conf.py").write_text(conf)

        assert conf_assignments(source) == {}
        assert conf_value(source, "language", "en") == "en"


class TestSourceLanguage:
    def test_it_is_english_when_conf_sets_none(self, tmp_path) -> None:
        source = make_source(tmp_path / "docs")

        assert source_language(source) == "en"

    def test_it_is_the_language_conf_sets(self, tmp_path) -> None:
        source = make_source(tmp_path / "docs", 'language = "de"\n')

        assert source_language(source) == "de"

    def test_it_is_english_without_a_source_dir(self) -> None:
        assert source_language(None) == "en"


class TestTranslations:
    def test_the_default_locale_dir_is_locales(self, tmp_path) -> None:
        source = make_source(
            tmp_path / "docs",
            catalogues=[
                "locales/de/LC_MESSAGES/index.po",
                "locales/pt_BR/LC_MESSAGES/index.po",
            ],
        )

        assert translations(source) == ["de", "pt_BR"]

    def test_every_locale_dir_conf_names_is_searched(self, tmp_path) -> None:
        source = make_source(
            tmp_path / "docs",
            'locale_dirs = ["locales/", "more"]\n',
            ["locales/de/LC_MESSAGES/index.po", "more/fr/LC_MESSAGES/index.po"],
        )

        assert translations(source) == ["de", "fr"]

    def test_the_default_is_not_searched_once_conf_names_locale_dirs(
        self, tmp_path
    ) -> None:
        source = make_source(
            tmp_path / "docs",
            'locale_dirs = ["more"]\n',
            ["locales/de/LC_MESSAGES/index.po"],
        )

        assert translations(source) == []

    def test_a_locale_dir_that_does_not_exist_is_passed_over(self, tmp_path) -> None:
        source = make_source(
            tmp_path / "docs",
            'locale_dirs = ["gone", "locales"]\n',
            ["locales/de/LC_MESSAGES/index.po"],
        )

        assert translations(source) == ["de"]

    def test_a_language_with_no_catalogue_is_not_a_translation(self, tmp_path) -> None:
        source = make_source(
            tmp_path / "docs", catalogues=["locales/de/LC_MESSAGES/x.mo"]
        )
        (source / "locales" / "fr" / "LC_MESSAGES").mkdir(parents=True)

        assert translations(source) == []

    def test_a_catalogue_in_a_folder_below_counts(self, tmp_path) -> None:
        source = make_source(
            tmp_path / "docs", catalogues=["locales/de/LC_MESSAGES/guide/index.po"]
        )

        assert translations(source) == ["de"]

    def test_a_source_with_no_locale_dir_has_no_translations(self, tmp_path) -> None:
        assert translations(make_source(tmp_path / "docs")) == []


class TestSiteLanguages:
    def test_each_language_is_in_djangos_form(self, settings) -> None:
        settings.LANGUAGES = [("en", "English"), ("pt-br", "Portuguese")]

        assert site_languages() == {"en", "pt-br"}


def make_builds(build_dir, *codes):
    for code in codes:
        (build_dir / code).mkdir(parents=True)
        (build_dir / code / DocsBuild.CONTEXT_FILE).write_text("{}")
    return build_dir


class TestLanguageBuilds:
    def test_each_folder_holding_a_build_is_a_language_build(self, tmp_path) -> None:
        make_builds(tmp_path, "de", "en")

        assert language_builds(tmp_path) == {
            "de": tmp_path / "de",
            "en": tmp_path / "en",
        }

    def test_a_language_is_keyed_in_djangos_form(self, tmp_path) -> None:
        make_builds(tmp_path, "pt_BR")

        assert language_builds(tmp_path) == {"pt-br": tmp_path / "pt_BR"}

    def test_a_folder_holding_no_build_is_not_a_language_build(self, tmp_path) -> None:
        make_builds(tmp_path, "de")
        (tmp_path / "other").mkdir()

        assert list(language_builds(tmp_path)) == ["de"]

    def test_a_build_dir_holding_a_build_of_its_own_has_no_language_builds(
        self, tmp_path
    ) -> None:
        make_builds(tmp_path / "de")
        (tmp_path / DocsBuild.CONTEXT_FILE).write_text("{}")

        assert language_builds(tmp_path) == {}

    def test_a_build_dir_that_does_not_exist_has_none(self, tmp_path) -> None:
        assert language_builds(tmp_path / "missing") == {}

    def test_a_language_built_later_is_seen_at_once(self, tmp_path) -> None:
        make_builds(tmp_path, "de")
        assert list(language_builds(tmp_path)) == ["de"]

        make_builds(tmp_path, "en")

        assert list(language_builds(tmp_path)) == ["de", "en"]


class TestBuildFor:
    @pytest.fixture
    def build_dir(self, tmp_path):
        return make_builds(tmp_path / "build", "de", "en", "pt_BR")

    @pytest.fixture(autouse=True)
    def site(self, settings):
        settings.LANGUAGE_CODE = "en-us"

    def test_the_language_itself_is_served(self, build_dir) -> None:
        assert build_for(build_dir, "de", None) == build_dir / "de"

    def test_a_regional_language_is_served_by_its_sphinx_folder(
        self, build_dir
    ) -> None:
        assert build_for(build_dir, "pt-br", None) == build_dir / "pt_BR"

    def test_a_variant_is_served_by_its_base_language(self, build_dir) -> None:
        assert build_for(build_dir, "de-at", None) == build_dir / "de"

    def test_a_language_with_no_build_is_served_the_language_code_build(
        self, build_dir, settings
    ) -> None:
        settings.LANGUAGE_CODE = "de"

        assert build_for(build_dir, "it", None) == build_dir / "de"

    def test_a_language_code_variant_is_served_by_its_base_language(
        self, build_dir, settings
    ) -> None:
        settings.LANGUAGE_CODE = "de-at"

        assert build_for(build_dir, "it", None) == build_dir / "de"

    def test_the_active_language_comes_before_the_language_code(
        self, build_dir, settings
    ) -> None:
        settings.LANGUAGE_CODE = "en"

        assert build_for(build_dir, "de", None) == build_dir / "de"

    def test_with_nothing_else_the_source_language_is_served(
        self, tmp_path, settings
    ) -> None:
        build_dir = make_builds(tmp_path / "build", "de", "fr")
        source = make_source(tmp_path / "docs", 'language = "fr"\n')
        settings.LANGUAGE_CODE = "en"

        assert build_for(build_dir, "it", source) == build_dir / "fr"

    def test_with_translation_turned_off_the_language_code_is_used(
        self, build_dir, settings
    ) -> None:
        settings.LANGUAGE_CODE = "de"

        assert build_for(build_dir, None, None) == build_dir / "de"

    def test_a_reader_is_still_served_when_the_source_language_has_no_build(
        self, tmp_path, settings
    ) -> None:
        build_dir = make_builds(tmp_path / "build", "de")
        settings.LANGUAGE_CODE = "en"

        assert build_for(build_dir, "it", None) == build_dir / "de"

    def test_a_build_dir_with_a_build_of_its_own_is_served_as_it_is(
        self, tmp_path
    ) -> None:
        make_builds(tmp_path, "de")
        (tmp_path / DocsBuild.CONTEXT_FILE).write_text("{}")

        assert build_for(tmp_path, "de", None) == tmp_path

    def test_a_build_dir_with_no_language_builds_is_served_as_it_is(
        self, tmp_path
    ) -> None:
        assert build_for(tmp_path / "missing", "de", None) == tmp_path / "missing"

    def test_the_choice_is_made_without_importing_sphinx(
        self, build_dir, monkeypatch
    ) -> None:
        for name in [
            name
            for name in sys.modules
            if name == "sphinx" or name.startswith("sphinx.")
        ]:
            monkeypatch.setitem(sys.modules, name, None)

        assert build_for(build_dir, "de", None) == build_dir / "de"

    def test_a_build_dir_is_returned_as_a_path(self, build_dir) -> None:
        assert isinstance(build_for(str(build_dir), "de", None), Path)
