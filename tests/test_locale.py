"""The package's own strings, in the catalogues it ships."""

from pathlib import Path

import pytest
from babel.messages.mofile import read_mo, write_mo
from babel.messages.pofile import read_po
from django.utils import translation
from django.utils.translation import trans_real

import mvp_sphinx

LOCALE = Path(mvp_sphinx.__file__).parent / "locale"


def read(language: str):
    with (LOCALE / language / "LC_MESSAGES" / "django.po").open("rb") as source:
        return read_po(source)


def translated(catalogue) -> dict[object, object]:
    """Each message's id and translation, a plural's as a tuple."""
    return {
        tuple(message.id) if isinstance(message.id, list | tuple) else message.id: (
            tuple(message.string)
            if isinstance(message.string, list | tuple)
            else message.string
        )
        for message in catalogue
        if message.id
    }


class TestGermanCatalogue:
    def test_it_holds_every_message_the_package_shows(self) -> None:
        assert set(translated(read("de"))) == set(translated(read("en")))

    def test_every_message_has_a_translation(self) -> None:
        missing = [
            message_id
            for message_id, string in translated(read("de")).items()
            if not all(string if isinstance(string, tuple) else (string,))
        ]

        assert missing == []

    def test_the_compiled_catalogue_holds_what_the_source_does(self) -> None:
        compiled = LOCALE / "de" / "LC_MESSAGES" / "django.mo"
        with compiled.open("rb") as source:
            built = read_mo(source)

        assert translated(built) == translated(read("de"))

    def test_django_finds_it(self) -> None:
        with translation.override("de"):
            assert translation.gettext("On this page") != "On this page"


class TestProjectCatalogue:
    @pytest.fixture
    def project_locale(self, tmp_path, settings, monkeypatch):
        catalogue = read("de")
        catalogue.locale = "de"
        for message in catalogue:
            if message.id == "On this page":
                message.string = "Ein eigener Text"
        folder = tmp_path / "locale" / "de" / "LC_MESSAGES"
        folder.mkdir(parents=True)
        with (folder / "django.mo").open("wb") as target:
            write_mo(target, catalogue)
        settings.LOCALE_PATHS = [tmp_path / "locale"]
        # Django keeps each language's catalogue for the life of the process.
        monkeypatch.setattr(trans_real, "_translations", {})

    @pytest.mark.usefixtures("project_locale")
    def test_a_project_translation_wins_over_the_packages(self) -> None:
        with translation.override("de"):
            assert translation.gettext("On this page") == "Ein eigener Text"
