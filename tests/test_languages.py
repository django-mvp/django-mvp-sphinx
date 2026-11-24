"""The languages a docs source is translated into, and the build that serves a reader."""

import pytest

from mvp_sphinx.languages import (
    conf_assignments,
    conf_value,
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
