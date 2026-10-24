"""The page_extract template tag, asserted as a template would use it."""

import pytest
from bs4 import BeautifulSoup
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured
from django.template import Context, Template
from django.urls import reverse

from tests.factories import UserFactory


@pytest.fixture
def page_request(rf):
    request = rf.get("/")
    request.user = AnonymousUser()
    return request


def render(source, request=None, **context):
    template = Template("{% load mvp_sphinx %}" + source)
    if request is not None:
        context["request"] = request
    return template.render(Context(context))


def soup(markup):
    return BeautifulSoup(markup, "html.parser")


class TestPageExtractTag:
    def test_it_places_the_pages_content(self, extracts_app, page_request) -> None:
        page = soup(render('{% page_extract "docs" "screens/" %}', page_request))

        assert page.find(id="first-section")
        assert page.find(id="third-section")
        assert not page.find("h1")

    def test_it_places_one_section(self, extracts_app, page_request) -> None:
        page = soup(
            render('{% page_extract "docs" "screens/#search-filters" %}', page_request)
        )

        assert page.find(id="details")
        assert not page.find(id="first-section")
        assert not page.find(id="third-section")

    def test_the_address_can_come_from_the_context(
        self, extracts_app, page_request
    ) -> None:
        page = soup(
            render(
                '{% page_extract "docs" address %}',
                page_request,
                address="screens/#search-filters",
            )
        )

        assert page.find(id="details")

    def test_as_binds_the_extract_for_its_title_and_address(
        self, extracts_app, page_request
    ) -> None:
        rendered = render(
            '{% page_extract "docs" "screens/" as extract %}'
            "{{ extract.title }}|{{ extract.url }}",
            page_request,
        )

        url = reverse("docs:page", kwargs={"path": "screens/"})
        assert rendered == f"Screens|{url}"

    def test_it_reads_from_the_app_mounted_under_that_namespace(
        self, handbook_app, extracts_build, page_request, monkeypatch
    ) -> None:
        monkeypatch.setattr(handbook_app, "build_dir", extracts_build)

        rendered = render(
            '{% page_extract "handbook" "screens/" as extract %}{{ extract.url }}',
            page_request,
        )

        assert rendered == reverse("handbook:page", kwargs={"path": "screens/"})


class TestNothingToPlace:
    def test_a_page_the_guide_lacks_places_nothing(
        self, extracts_app, page_request
    ) -> None:
        assert render('{% page_extract "docs" "moved/" %}', page_request) == ""

    def test_a_page_the_guide_lacks_binds_nothing(
        self, extracts_app, page_request
    ) -> None:
        rendered = render(
            '{% page_extract "docs" "moved/" as extract %}'
            "{% if extract %}shown{% else %}none{% endif %}",
            page_request,
        )

        assert rendered == "none"

    def test_a_reader_the_rule_excludes_gets_nothing(
        self, staff_guide_app, page_request
    ) -> None:
        assert render('{% page_extract "staff_guide" "backups/" %}', page_request) == ""

    def test_a_reader_the_rule_admits_gets_the_page(
        self, staff_guide_app, rf, db
    ) -> None:
        request = rf.get("/")
        request.user = UserFactory(is_staff=True)

        rendered = render(
            '{% page_extract "staff_guide" "backups/" as extract %}{{ extract.title }}',
            request,
        )

        assert rendered == "Backups"


class TestMisuse:
    def test_a_namespace_no_documentation_app_is_mounted_under_raises(
        self, extracts_app, page_request
    ) -> None:
        with pytest.raises(ImproperlyConfigured, match="manual"):
            render('{% page_extract "manual" "screens/" %}', page_request)

    def test_a_template_rendered_without_its_request_raises(self, extracts_app) -> None:
        with pytest.raises(ImproperlyConfigured, match="request"):
            render('{% page_extract "docs" "screens/" %}')
