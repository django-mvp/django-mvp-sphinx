"""Page extracts, asserted as a developer would ask for them."""

import json
import logging
import shutil
import sys
from urllib.parse import urldefrag, urlsplit

import pytest
from bs4 import BeautifulSoup
from django.contrib.auth.models import AnonymousUser
from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import conditional_escape

from mvp_sphinx.docs_build import DocsBuild
from mvp_sphinx.examples import LiveExamples
from mvp_sphinx.extracts import LinkRewriter, SectionFinder
from tests.factories import UserFactory


@pytest.fixture
def page_request(rf):
    request = rf.get("/")
    request.user = AnonymousUser()
    return request


def soup(extract):
    return BeautifulSoup(str(extract), "html.parser")


class TestPageExtract:
    def test_the_content_holds_the_opening_paragraph_and_every_section(
        self, extracts_app, page_request
    ) -> None:
        extract = extracts_app.page_extract("screens/", page_request)

        page = soup(extract)
        assert page.find("img", alt="A single pixel")
        for anchor in ["first-section", "search-filters", "details", "third-section"]:
            assert page.find(id=anchor)

    def test_the_content_leaves_out_the_pages_own_heading(
        self, extracts_app, page_request
    ) -> None:
        extract = extracts_app.page_extract("screens/", page_request)

        assert not soup(extract).find("h1")
        assert not soup(extract).find("a", href="/docs/screens/#screens")

    def test_a_second_top_level_section_is_kept(
        self, extracts_app, page_request
    ) -> None:
        extract = extracts_app.page_extract("two-parts/", page_request)

        page = soup(extract)
        assert page.find(id="second-part")
        assert not page.find(id="first-part").find("h1")

    def test_the_title_is_the_pages_title_as_plain_text(
        self, extracts_app, page_request
    ) -> None:
        extract = extracts_app.page_extract("screens/", page_request)

        assert extract.title == "Screens"

    def test_the_address_is_the_page_in_the_documentation_app(
        self, extracts_app, page_request
    ) -> None:
        extract = extracts_app.page_extract("screens/", page_request)

        assert extract.url == reverse("docs:page", kwargs={"path": "screens/"})

    def test_the_empty_address_is_the_front_page(
        self, extracts_app, page_request
    ) -> None:
        extract = extracts_app.page_extract("", page_request)

        assert extract.url == reverse("docs:front_page")
        assert extract.title == "Extracts"
        assert soup(extract).find("p")

    def test_it_renders_as_markup_not_as_escaped_text(
        self, extracts_app, page_request
    ) -> None:
        extract = extracts_app.page_extract("screens/", page_request)

        assert conditional_escape(extract) == extract.content
        assert extract.__html__() == extract.content
        assert str(extract) == extract.content

    def test_a_rebuilt_page_shows_on_the_next_call(
        self, extracts_app, extracts_build, page_request, tmp_path, monkeypatch
    ) -> None:
        build = tmp_path / "build"
        shutil.copytree(extracts_build, build)
        monkeypatch.setattr(extracts_app, "build_dir", build)
        assert "A short page" in str(extracts_app.page_extract("other/", page_request))

        page_file = build / "other.fjson"
        page = json.loads(page_file.read_text())
        page["body"] = page["body"].replace("A short page", "A rebuilt page")
        page_file.write_text(json.dumps(page))

        content = str(extracts_app.page_extract("other/", page_request))
        assert "A rebuilt page" in content
        assert "A short page" not in content


class TestExtractContent:
    def test_the_content_is_wrapped_in_the_documentation_apps_styles(
        self, extracts_app, page_request
    ) -> None:
        extract = extracts_app.page_extract("screens/", page_request)

        page = soup(extract)
        assert page.select_one("div.mvp-sphinx-content")
        stylesheet = page.find("link", rel="stylesheet")
        assert stylesheet["href"] == static("mvp_sphinx/content.css")

    def test_maths_is_left_as_written(self, extracts_app, page_request) -> None:
        extract = extracts_app.page_extract("screens/", page_request)

        content = str(extract)
        assert r"\(a^2 + b^2 = c^2\)" in content
        assert r"\[e^{i\pi} + 1 = 0\]" in content

    def test_a_table_is_wrapped_to_scroll_as_on_the_page_itself(
        self, extracts_app, page_request
    ) -> None:
        extract = extracts_app.page_extract("screens/", page_request)

        region = soup(extract).find("table").find_parent(attrs={"role": "region"})
        assert region["tabindex"] == "0"

    def test_live_examples_are_left_out(self, examples_app, page_request) -> None:
        extract = examples_app.page_extract("single/", page_request)

        assert LiveExamples.EXAMPLE_CLASS not in str(extract)
        assert "Written before the example." in str(extract)
        assert "Written after the example." in str(extract)


class TestSectionExtract:
    @pytest.fixture
    def extract(self, extracts_app, page_request):
        return extracts_app.page_extract("screens/#search-filters", page_request)

    def test_it_holds_the_section_and_its_subsection(self, extract) -> None:
        page = soup(extract)

        assert page.find(id="details")
        assert page.find("table")
        assert "Written for the second screen" in str(extract)

    def test_it_holds_nothing_from_the_sections_around_it(self, extract) -> None:
        page = soup(extract)

        assert not page.find(id="first-section")
        assert not page.find(id="third-section")
        assert "Written for the first screen" not in str(extract)
        assert "Written for the third screen" not in str(extract)
        assert not page.find(attrs={"alt": "A single pixel"})

    def test_it_leaves_out_the_sections_own_heading(self, extract) -> None:
        page = soup(extract)

        assert not page.find("h2")
        assert not page.find(id="search-filters")

    def test_the_title_is_the_headings_text_with_its_ampersand_intact(
        self, extract
    ) -> None:
        assert extract.title == "Search & filters"

    def test_the_address_leads_to_the_section_in_the_documentation_app(
        self, extract
    ) -> None:
        assert extract.url == "/docs/screens/#search-filters"

    def test_a_link_to_another_section_leads_to_it_in_the_documentation_app(
        self, extract
    ) -> None:
        link = soup(extract).find("a", href=lambda href: href.endswith("#third"))

        assert link["href"] == "/docs/screens/#third"

    def test_a_subsection_ends_at_its_own_end_not_its_parents(
        self, extracts_app, page_request
    ) -> None:
        extract = extracts_app.page_extract("screens/#details", page_request)

        assert extract.title == "Details"
        assert soup(extract).find("table")
        assert "Written for the second screen" not in str(extract)
        assert "Written for the third screen" not in str(extract)

    def test_the_last_section_of_a_page_is_had(
        self, extracts_app, page_request
    ) -> None:
        extract = extracts_app.page_extract("screens/#third-section", page_request)

        assert "Written for the third screen" in str(extract)
        assert extract.title == "Third section"

    @pytest.mark.parametrize("anchor", ["no-such-section", "search-and-filters", "id1"])
    def test_an_anchor_that_names_no_section_gives_no_extract_and_a_warning(
        self, extracts_app, page_request, caplog, anchor
    ) -> None:
        address = f"screens/#{anchor}"

        assert extracts_app.page_extract(address, page_request) is None
        assert [
            record
            for record in caplog.records
            if record.levelno == logging.WARNING
            and address in record.getMessage()
            and "docs" in record.getMessage()
        ]


class TestSectionFinder:
    BODY = (
        '<section id="page">\n<h1>Page<a class="headerlink" href="#page">¶</a></h1>\n'
        '<section id="one">\n<h2><code class="literal"><span>a</span></code> &amp; '
        '<em>b</em><a class="headerlink" href="#one" title="Link">¶</a></h2>\n'
        "<p>One.</p>\n</section>\n</section>\n"
    )

    def test_the_title_is_the_headings_text_up_to_its_link(self) -> None:
        found = SectionFinder(self.BODY, "one")

        assert found.title == "a & b"

    def test_the_content_runs_from_after_the_heading_to_the_end_of_the_section(
        self,
    ) -> None:
        found = SectionFinder(self.BODY, "one")

        assert self.BODY[found.start : found.end] == "\n<p>One.</p>\n"

    def test_a_body_with_no_such_section_has_no_offsets(self) -> None:
        found = SectionFinder(self.BODY, "two")

        assert found.start is None
        assert found.end is None


class TestExtractAddress:
    @pytest.fixture
    def handbook(self, handbook_app, extracts_build, monkeypatch):
        monkeypatch.setattr(handbook_app, "build_dir", extracts_build)
        return handbook_app

    def test_a_page_address_begins_with_the_prefix_the_app_is_mounted_at(
        self, handbook, page_request
    ) -> None:
        extract = handbook.page_extract("screens/", page_request)

        assert extract.url == "/manuals/admin/screens/"

    def test_a_section_address_begins_with_the_prefix_the_app_is_mounted_at(
        self, handbook, page_request
    ) -> None:
        extract = handbook.page_extract("screens/#third-section", page_request)

        assert extract.url == "/manuals/admin/screens/#third-section"

    def test_links_in_the_content_lead_under_the_prefix_the_app_is_mounted_at(
        self, handbook, page_request
    ) -> None:
        extract = handbook.page_extract("screens/", page_request)

        link = soup(extract).find("a", href=lambda href: "other" in href)
        assert link["href"] == "/manuals/admin/other/"
        assert soup(extract).find("img")["src"] == "/manuals/admin/_images/pixel.png"

    def test_two_apps_give_addresses_under_their_own_prefixes(
        self, extracts_app, handbook, page_request
    ) -> None:
        first = extracts_app.page_extract("screens/", page_request)
        second = handbook.page_extract("screens/", page_request)

        assert first.url == "/docs/screens/"
        assert second.url == "/manuals/admin/screens/"

    def test_each_app_gives_extracts_of_its_own_pages_only(
        self, extracts_app, handbook_build, handbook, page_request, monkeypatch
    ) -> None:
        monkeypatch.setattr(handbook, "build_dir", handbook_build)

        assert handbook.page_extract("backups/", page_request).title == "Backups"
        assert extracts_app.page_extract("backups/", page_request) is None


class TestReaderRule:
    @pytest.fixture
    def reader(self, rf):
        def request_for(user):
            request = rf.get("/")
            request.user = user
            return request

        return request_for

    def test_an_anonymous_reader_gets_no_extract(
        self, staff_guide_app, reader, caplog
    ) -> None:
        assert staff_guide_app.page_extract("backups/", reader(AnonymousUser())) is None
        assert not caplog.records

    def test_a_regular_user_gets_no_extract(
        self, staff_guide_app, reader, user, caplog
    ) -> None:
        assert staff_guide_app.page_extract("backups/", reader(user)) is None
        assert not caplog.records

    def test_a_staff_user_gets_the_extract(self, staff_guide_app, reader, db) -> None:
        extract = staff_guide_app.page_extract(
            "backups/", reader(UserFactory(is_staff=True))
        )

        assert extract.title == "Backups"
        assert extract.url == reverse("staff_guide:page", kwargs={"path": "backups/"})


class TestNothingToShow:
    def warnings_for(self, caplog, address):
        return [
            record
            for record in caplog.records
            if record.levelno == logging.WARNING
            and address in record.getMessage()
            and "docs" in record.getMessage()
        ]

    def test_a_missing_build_gives_no_extract(
        self, extracts_app, page_request, tmp_path, monkeypatch
    ) -> None:
        monkeypatch.setattr(extracts_app, "build_dir", tmp_path / "not-built")

        assert extracts_app.page_extract("screens/", page_request) is None

    def test_a_missing_page_gives_no_extract_and_a_warning(
        self, extracts_app, page_request, caplog
    ) -> None:
        assert extracts_app.page_extract("no-such-page/", page_request) is None
        assert self.warnings_for(caplog, "no-such-page/")

    def test_an_address_without_its_trailing_slash_names_no_page(
        self, extracts_app, page_request
    ) -> None:
        assert extracts_app.page_extract("screens", page_request) is None

    def test_an_address_leaving_the_build_gives_no_extract(
        self, extracts_app, extracts_build, page_request, tmp_path, monkeypatch
    ) -> None:
        build = tmp_path / "build"
        shutil.copytree(extracts_build, build)
        (tmp_path / "secret.fjson").write_text('{"title": "S", "body": "<p>x</p>"}')
        monkeypatch.setattr(extracts_app, "build_dir", build)

        assert extracts_app.page_extract("../secret/", page_request) is None
        assert extracts_app.page_extract("../secret", page_request) is None

    def test_a_page_file_that_is_not_json_gives_no_extract_and_a_warning(
        self, extracts_app, extracts_build, page_request, tmp_path, monkeypatch, caplog
    ) -> None:
        build = tmp_path / "build"
        shutil.copytree(extracts_build, build)
        (build / "other.fjson").write_text("{not json")
        monkeypatch.setattr(extracts_app, "build_dir", build)

        assert extracts_app.page_extract("other/", page_request) is None
        assert self.warnings_for(caplog, "other/")

    def test_a_page_file_that_cannot_be_read_gives_no_extract_and_a_warning(
        self, extracts_app, page_request, monkeypatch, caplog
    ) -> None:
        def refuse(self, path):
            raise PermissionError(path)

        monkeypatch.setattr(DocsBuild, "page", refuse)

        assert extracts_app.page_extract("other/", page_request) is None
        assert self.warnings_for(caplog, "other/")

    def test_a_page_holding_only_a_contents_is_a_false_extract(
        self, extracts_app, page_request
    ) -> None:
        extract = extracts_app.page_extract("toc-only/", page_request)

        assert extract is not None
        assert not extract
        assert (extract or "") == ""

    def test_a_page_with_text_is_a_true_extract(
        self, extracts_app, page_request
    ) -> None:
        assert extracts_app.page_extract("other/", page_request)

    def test_a_page_holding_only_an_image_is_a_true_extract(
        self, extracts_app, extracts_build, page_request, tmp_path, monkeypatch
    ) -> None:
        build = tmp_path / "build"
        shutil.copytree(extracts_build, build)
        monkeypatch.setattr(extracts_app, "build_dir", build)
        page_file = build / "toc-only.fjson"
        page = json.loads(page_file.read_text())
        page["body"] = (
            '<section id="x"><h1>X</h1><img alt="" src="../_images/pixel.png" />'
            "</section>"
        )
        page_file.write_text(json.dumps(page))

        assert extracts_app.page_extract("toc-only/", page_request)


class TestWithoutSphinx:
    def test_an_extract_is_had_when_sphinx_cannot_be_imported(
        self, extracts_app, page_request, monkeypatch
    ) -> None:
        for name in [
            name
            for name in sys.modules
            if name == "sphinx" or name.startswith("sphinx.")
        ]:
            monkeypatch.setitem(sys.modules, name, None)

        extract = extracts_app.page_extract("screens/", page_request)

        assert extract.title == "Screens"


class TestExtractLinks:
    @pytest.fixture
    def extract(self, extracts_app, page_request):
        return extracts_app.page_extract("screens/", page_request)

    def test_every_internal_link_and_image_is_answered_by_the_documentation_app(
        self, client, db, extract
    ) -> None:
        page = soup(extract)
        targets = [
            urldefrag(tag[attribute])[0] or extract.url
            for tag, attribute in [
                *((tag, "href") for tag in page.find_all("a", href=True)),
                *((tag, "src") for tag in page.find_all("img", src=True)),
            ]
            if not urlsplit(tag[attribute]).scheme
        ]

        assert targets
        for target in targets:
            response = client.get(target)
            assert response.status_code == 200, target

    def test_a_link_to_another_page_leads_to_that_page(self, extract) -> None:
        link = soup(extract).find("a", href=lambda href: "other" in href)

        assert link["href"] == reverse("docs:page", kwargs={"path": "other/"})

    def test_an_image_leads_to_the_file_the_documentation_app_serves(
        self, client, extract
    ) -> None:
        image = soup(extract).find("img")

        assert image["src"] == "/docs/_images/pixel.png"

    def test_a_link_to_a_section_of_the_page_leads_to_it_in_the_documentation_app(
        self, extract
    ) -> None:
        link = soup(extract).find("a", href=lambda href: href.endswith("#details"))

        assert link["href"] == f"{extract.url}#details"

    def test_an_external_link_is_left_as_written(self, extract) -> None:
        assert 'href="https://example.com/a?b=1&amp;c=2"' in str(extract)

    def test_an_ampersand_in_a_rewritten_address_stays_as_written(self) -> None:
        markup = '<a href="../other/?a=1&amp;b=2">x</a>'

        assert LinkRewriter.rewrite(markup, "/docs/screens/") == (
            '<a href="/docs/other/?a=1&amp;b=2">x</a>'
        )


class TestLinkRewriter:
    @pytest.mark.parametrize(
        "markup",
        [
            '<a href="/elsewhere/">x</a>',
            '<a href="https://example.com/">x</a>',
            '<a href="mailto:someone@example.com">x</a>',
            '<a href="//example.com/path">x</a>',
            "<p>an href=&quot;../other/&quot; inside text</p>",
            '<p>say href="../other/" in prose</p>',
        ],
    )
    def test_an_address_that_is_not_relative_is_left_alone(self, markup) -> None:
        assert LinkRewriter.rewrite(markup, "/docs/screens/") == markup

    def test_a_self_closing_image_is_rewritten(self) -> None:
        markup = '<img alt="" src="../_images/pixel.png" />'

        assert LinkRewriter.rewrite(markup, "/docs/screens/") == (
            '<img alt="" src="/docs/_images/pixel.png" />'
        )

    def test_an_embedded_objects_data_address_is_rewritten(self) -> None:
        markup = '<object data="../_images/graph.svg" type="image/svg+xml"></object>'

        assert LinkRewriter.rewrite(markup, "/docs/screens/") == (
            '<object data="/docs/_images/graph.svg" type="image/svg+xml"></object>'
        )

    def test_a_fragment_only_address_leads_to_the_page(self) -> None:
        assert LinkRewriter.rewrite('<a href="#x">x</a>', "/docs/screens/") == (
            '<a href="/docs/screens/#x">x</a>'
        )

    def test_every_byte_but_the_address_is_kept(self) -> None:
        markup = '<P  CLASS="a"\n   HREF = \'../b/\' >&nbsp;&amp;\n<A href="../c/">'

        assert LinkRewriter.rewrite(markup, "/docs/screens/") == (
            '<P  CLASS="a"\n   HREF = \'/docs/b/\' >&nbsp;&amp;\n<A href="/docs/c/">'
        )
