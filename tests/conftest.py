"""Fixtures shared across the test suite."""

import pytest
from django import template as dj_template
from django.template import Context
from django.urls import reverse
from django_cotton.compiler_regex import CottonCompiler


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
