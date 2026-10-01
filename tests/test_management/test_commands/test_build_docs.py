"""build_docs runs the Sphinx build for the project's documentation apps."""

import sys

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

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
