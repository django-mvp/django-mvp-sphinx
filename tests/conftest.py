"""Fixtures shared across the test suite."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from django.urls import reverse
from mvp.config import MVP_CONFIG
from sphinx.cmd.build import build_main

from tests.factories import GroupFactory, UserFactory

SPHINX_SOURCES = Path(__file__).parent / "sphinx"
DEMO_GUIDE = Path(__file__).parent.parent / "demo" / "docs"


@pytest.fixture(scope="session")
def sidebar():
    # The shell's main navigation, where the host's menu entries are drawn.
    def region(page):
        return page.split('aria-label="Main navigation"', 1)[1].split("</ul>", 1)[0]

    return region


@pytest.fixture
def overview_page(client, db):
    return client.get(reverse("overview")).content.decode()


@pytest.fixture(scope="session")
def sphinx_json_build(tmp_path_factory):
    def build(name):
        out = tmp_path_factory.mktemp(f"{name}-build")
        warnings = tmp_path_factory.mktemp(f"{name}-warnings") / "warnings.txt"
        status = build_main(
            [
                "-b",
                "json",
                "-D",
                "html_theme=daisyui",
                "-q",
                "-w",
                str(warnings),
                str(SPHINX_SOURCES / name),
                str(out),
            ]
        )
        assert status == 0
        assert not warnings.exists() or warnings.read_text() == ""
        return out

    return build


@pytest.fixture
def sphinx_build(tmp_path):
    def build(source, builder="json"):
        out = tmp_path / f"{builder}-build"
        status = build_main(
            ["-b", builder, "-D", "html_theme=daisyui", "-q", str(source), str(out)]
        )
        assert status == 0
        return out

    return build


@pytest.fixture(scope="session")
def guide_build(sphinx_json_build):
    return sphinx_json_build("guide")


@pytest.fixture(scope="session")
def handbook_build(sphinx_json_build):
    return sphinx_json_build("handbook")


@pytest.fixture(scope="session")
def contents_build(sphinx_json_build):
    return sphinx_json_build("contents")


@pytest.fixture(scope="session")
def menu_settings_build(sphinx_json_build):
    return sphinx_json_build("menu-settings")


@pytest.fixture(scope="session")
def search_build(sphinx_json_build):
    return sphinx_json_build("search")


@pytest.fixture(scope="session")
def reading_build(sphinx_json_build):
    return sphinx_json_build("reading")


@pytest.fixture(scope="session")
def reference_build(sphinx_json_build):
    return sphinx_json_build("reference")


@pytest.fixture(scope="session")
def metadata_build(sphinx_json_build):
    return sphinx_json_build("metadata")


@pytest.fixture(scope="session")
def examples_build(sphinx_json_build):
    return sphinx_json_build("examples")


@pytest.fixture(scope="session")
def extracts_build(sphinx_json_build):
    return sphinx_json_build("extracts")


@pytest.fixture(scope="module")
def demo_guide_build(tmp_path_factory):
    out = tmp_path_factory.mktemp("demo-guide-build")
    status = build_main(["-b", "json", "-q", "-W", str(DEMO_GUIDE), str(out)])
    assert status == 0
    return out


@pytest.fixture(scope="session")
def translated_build(tmp_path_factory):
    # The layout build_docs writes: one build in a folder named for each language.
    root = tmp_path_factory.mktemp("translated-build")
    # A copy, because Sphinx compiles each catalogue next to its .po file.
    source = shutil.copytree(SPHINX_SOURCES / "translated", root / "source")
    for language in ["en", "de", "pt_BR"]:
        # One process for each language, as build_docs runs them: Sphinx keeps
        # the first language's catalogues for the life of a process.
        subprocess.run(  # noqa: S603 - fixed arguments
            [
                sys.executable,
                "-m",
                "sphinx",
                "-b",
                "json",
                "-D",
                "html_theme=daisyui",
                "-D",
                f"language={language}",
                "-q",
                str(source),
                str(root / "build" / language),
            ],
            check=True,
        )
    return root / "build"


@pytest.fixture
def translated_app(translated_build, monkeypatch, settings):
    from demo.mounted import docs

    monkeypatch.setattr(docs, "build_dir", translated_build)
    monkeypatch.setattr(docs, "source_dir", SPHINX_SOURCES / "translated")
    settings.LANGUAGES = [
        ("en", "English"),
        ("de", "German"),
        ("pt-br", "Brazilian Portuguese"),
        ("it", "Italian"),
    ]
    settings.LANGUAGE_CODE = "en"
    return docs


@pytest.fixture
def docs_app(guide_build, monkeypatch):
    from demo.mounted import docs

    monkeypatch.setattr(docs, "build_dir", guide_build)
    return docs


@pytest.fixture
def search_app(search_build, monkeypatch):
    from demo.mounted import docs

    monkeypatch.setattr(docs, "build_dir", search_build)
    return docs


@pytest.fixture
def contents_app(contents_build, monkeypatch):
    from demo.mounted import docs

    monkeypatch.setattr(docs, "build_dir", contents_build)
    return docs


@pytest.fixture
def menu_settings_app(menu_settings_build, monkeypatch):
    from demo.mounted import docs

    monkeypatch.setattr(docs, "build_dir", menu_settings_build)
    return docs


@pytest.fixture
def handbook_app(handbook_build, monkeypatch):
    from tests.urls import handbook

    monkeypatch.setattr(handbook, "build_dir", handbook_build)
    return handbook


@pytest.fixture
def staff_guide_app(handbook_build, monkeypatch):
    from demo.mounted import staff_guide

    monkeypatch.setattr(staff_guide, "build_dir", handbook_build)
    return staff_guide


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def group(db):
    return GroupFactory()


@pytest.fixture
def reading_app(reading_build, monkeypatch):
    from demo.mounted import docs

    monkeypatch.setattr(docs, "build_dir", reading_build)
    return docs


@pytest.fixture
def demo_guide_app(demo_guide_build, monkeypatch):
    from demo.mounted import docs

    monkeypatch.setattr(docs, "build_dir", demo_guide_build)
    return docs


@pytest.fixture
def reference_app(reference_build, monkeypatch):
    from demo.mounted import docs

    monkeypatch.setattr(docs, "build_dir", reference_build)
    return docs


@pytest.fixture
def examples_app(examples_build, monkeypatch):
    from demo.mounted import docs

    monkeypatch.setattr(docs, "build_dir", examples_build)
    return docs


@pytest.fixture
def extracts_app(extracts_build, monkeypatch):
    from demo.mounted import docs

    monkeypatch.setattr(docs, "build_dir", extracts_build)
    return docs


@pytest.fixture
def metadata_app(metadata_build, monkeypatch):
    from demo.mounted import docs

    monkeypatch.setattr(docs, "build_dir", metadata_build)
    return docs


@pytest.fixture
def without_site_search(monkeypatch):
    # A site that has not put django-mvp's site search in its navbar.
    navbar = MVP_CONFIG["layout"]["navbar"]
    monkeypatch.setitem(
        navbar, "end", [name for name in navbar["end"] if name != "mvp.actions.search"]
    )
