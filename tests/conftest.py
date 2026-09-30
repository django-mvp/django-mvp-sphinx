"""Fixtures shared across the test suite."""

from pathlib import Path

import pytest
from django.urls import reverse
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
        status = build_main(["-b", builder, "-q", str(source), str(out)])
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
def search_build(sphinx_json_build):
    return sphinx_json_build("search")


@pytest.fixture(scope="session")
def reading_build(sphinx_json_build):
    return sphinx_json_build("reading")


@pytest.fixture(scope="module")
def demo_guide_build(tmp_path_factory):
    out = tmp_path_factory.mktemp("demo-guide-build")
    status = build_main(["-b", "json", "-q", "-W", str(DEMO_GUIDE), str(out)])
    assert status == 0
    return out


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
