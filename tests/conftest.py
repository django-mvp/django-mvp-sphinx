"""Fixtures shared across the test suite."""

from pathlib import Path

import pytest
from django import template as dj_template
from django.template import Context
from django.urls import reverse
from django_cotton.compiler_regex import CottonCompiler
from sphinx.cmd.build import build_main

SPHINX_SOURCES = Path(__file__).parent / "sphinx"


@pytest.fixture(scope="session")
def render():
    # No request is involved, which holds components to rendering anywhere a
    # template does, including outside the request cycle.
    compiler = CottonCompiler()

    def render_source(source, **context):
        return dj_template.Template(compiler.process(source)).render(Context(context))

    return render_source


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


@pytest.fixture(scope="session")
def guide_build(sphinx_json_build):
    return sphinx_json_build("guide")


@pytest.fixture(scope="session")
def handbook_build(sphinx_json_build):
    return sphinx_json_build("handbook")


@pytest.fixture
def docs_app(guide_build, monkeypatch):
    from demo.mounted import docs

    monkeypatch.setattr(docs, "build_dir", guide_build)
    return docs
