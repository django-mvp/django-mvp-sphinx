"""The demo project's pages, asserted as rendered."""

# Everything in the demo fails quietly: an unresolvable component renders empty
# and a menu entry whose URL will not resolve is dropped from the tree.

import re
from pathlib import Path
from textwrap import dedent
from urllib.parse import urldefrag, urljoin

import pytest
from bs4 import BeautifulSoup
from django.templatetags.static import static
from django.urls import reverse
from mvp.menus import MenuCollapse, MenuGroup

from demo.mounted import docs
from demo.settings import BASE_DIR
from mvp_sphinx.docs_build import DocsBuild
from tests.factories import UserFactory
from tests.test_static.test_content_css import STYLESHEET, Stylesheet


class TestOverviewPage:
    def test_it_responds(self, client, db) -> None:
        assert client.get(reverse("overview")).status_code == 200

    def test_the_shell_wraps_it(self, overview_page: str) -> None:
        # A template that fails to extend the shell still returns 200.
        assert 'aria-label="Main navigation"' in overview_page

    def test_the_sidebar_links_the_pages_that_exist(self, overview_page: str) -> None:
        sidebar = overview_page.split('aria-label="Main navigation"', 1)[1]
        sidebar = sidebar.split("</ul>", 1)[0]
        assert f'href="{reverse("overview")}"' in sidebar


class TestDocumentationEntry:
    def test_the_sidebar_links_the_documentation(self, overview_page: str) -> None:
        sidebar = overview_page.split('aria-label="Main navigation"', 1)[1]
        sidebar = sidebar.split("</ul>", 1)[0]
        assert 'href="/docs/"' in sidebar


class TestDocumentationSearch:
    def test_the_front_page_offers_the_search(
        self, client, db, sphinx_build, monkeypatch
    ) -> None:
        monkeypatch.setattr(docs, "build_dir", sphinx_build(BASE_DIR / "demo" / "docs"))

        form = BeautifulSoup(client.get("/docs/").content, "html.parser").find(
            "form", role="search"
        )

        assert form["action"] == reverse("docs:search")


class TestStaffGuideEntry:
    def test_the_entry_is_absent_for_an_anonymous_reader(
        self, sidebar, overview_page: str
    ) -> None:
        assert 'href="/staff-guide/"' not in sidebar(overview_page)

    def test_the_entry_is_absent_for_a_regular_user(
        self, sidebar, client, user
    ) -> None:
        client.force_login(user)
        page = client.get(reverse("overview")).content.decode()

        assert 'href="/staff-guide/"' not in sidebar(page)

    def test_the_entry_is_present_for_a_staff_user(self, sidebar, client, db) -> None:
        client.force_login(UserFactory(is_staff=True))
        page = client.get(reverse("overview")).content.decode()

        assert 'href="/staff-guide/"' in sidebar(page)

    def test_a_staff_user_gets_the_front_page(
        self, client, db, staff_guide_app
    ) -> None:
        client.force_login(UserFactory(is_staff=True))

        assert client.get("/staff-guide/").status_code == 200


class TestDemoGuide:
    def test_building_the_guide_writes_the_navigation_file(self, sphinx_build) -> None:
        out = sphinx_build(BASE_DIR / "demo" / "docs")

        assert (out / DocsBuild.NAVIGATION_FILE).is_file()

    def test_building_the_staff_guide_writes_the_navigation_file(
        self, sphinx_build
    ) -> None:
        out = sphinx_build(BASE_DIR / "demo" / "staff_guide")

        assert (out / DocsBuild.NAVIGATION_FILE).is_file()


def leaves(items) -> list[str]:
    found = []
    for item in items:
        found += leaves(item.visible_children) if item.is_parent else [item.url]
    return found


def branches(items) -> list:
    found = []
    for item in items:
        if item.is_parent:
            found += [item, *branches(item.visible_children)]
    return found


def admonition_classes(pages) -> set[str]:
    return {
        name
        for soup in pages.values()
        for each in soup.select("div.admonition")
        for name in each["class"]
    }


WORKING_FORM = "/docs/examples/a-working-form/"
CANNOT_RUN = "/docs/examples/when-an-example-cannot-run/"
SOURCE_LINE = re.compile(r"^(?P<path>.+?)(?:\s+(?P<first>\d+)(?:-(?P<last>\d+))?)?$")


def written_sources(address: str) -> list[list[tuple[Path, int | None, int | None]]]:
    page = (
        BASE_DIR / "demo" / "docs" / f"{address.removeprefix('/docs/').rstrip('/')}.rst"
    )
    examples: list[list[tuple[Path, int | None, int | None]]] = []
    inside = False
    for line in page.read_text(encoding="utf-8").splitlines():
        if line.startswith(".. live-example::"):
            examples.append([])
            inside = True
        elif inside and line and not line.startswith(" "):
            inside = False
        elif inside and line.strip() and not line.strip().startswith(":"):
            found = SOURCE_LINE.match(line.strip())
            first, last = found["first"], found["last"]
            examples[-1].append(
                (
                    (page.parent / found["path"]).resolve(),
                    int(first) if first else None,
                    int(last or first) if first else None,
                )
            )
    return examples


def shown_examples(soup: BeautifulSoup) -> list:
    return soup.select("section.mvp-sphinx-example")


@pytest.fixture
def guide_menu(demo_guide_app, rf):
    return demo_guide_app.menu.process(rf.get("/docs/"))


@pytest.fixture
def guide_responses(guide_menu, client, db):
    return {
        address: client.get(address) for address in leaves(guide_menu.visible_children)
    }


@pytest.fixture
def guide_pages(guide_responses):
    return {
        address: BeautifulSoup(response.content, "html.parser")
        for address, response in guide_responses.items()
    }


@pytest.fixture
def link_helpers(guide_pages):
    return guide_pages["/docs/reference/link-helpers/"]


@pytest.fixture
def maths_page(guide_pages):
    return guide_pages["/docs/reference/reading-time/"]


def description(page, entry_id):
    return page.select_one(f'dt.sig-object[id="{entry_id}"]').find_next_sibling("dd")


class TestDemoGuideStates:
    ADMONITION_KINDS = {
        "note",
        "tip",
        "hint",
        "important",
        "warning",
        "caution",
        "attention",
        "danger",
        "error",
        "seealso",
    }

    def test_every_page_in_the_contents_answers(self, guide_responses) -> None:
        assert {each.status_code for each in guide_responses.values()} == {200}

    def test_the_contents_holds_two_or_more_captioned_groups(self, guide_menu) -> None:
        groups = [
            each
            for each in branches(guide_menu.visible_children)
            if isinstance(each, MenuGroup)
        ]

        assert len(groups) >= 2

    def test_the_contents_holds_a_collapsible_branch(self, guide_menu) -> None:
        nested = [
            each
            for each in branches(guide_menu.visible_children)
            if isinstance(each, MenuCollapse)
        ]

        assert nested

    def test_a_page_lists_three_headings_with_a_nested_list(self, guide_pages) -> None:
        landmarks = [
            soup.find("nav", attrs={"aria-labelledby": "mvp-sphinx-on-this-page"})
            for soup in guide_pages.values()
        ]

        assert any(
            landmark and len(landmark.find_all("a")) >= 3 and landmark.select("ul ul")
            for landmark in landmarks
        )

    def test_a_page_links_both_its_previous_and_its_next_page(
        self, guide_pages
    ) -> None:
        assert any(
            soup.find("a", rel="prev") and soup.find("a", rel="next")
            for soup in guide_pages.values()
        )

    def test_each_admonition_kind_is_drawn(self, guide_pages) -> None:
        classes = admonition_classes(guide_pages)

        assert classes >= self.ADMONITION_KINDS

    def test_a_generic_admonition_is_drawn(self, guide_pages) -> None:
        classes = admonition_classes(guide_pages)

        assert any(name.startswith("admonition-") for name in classes)

    def test_code_is_highlighted(self, guide_pages) -> None:
        assert any(soup.select("div.highlight") for soup in guide_pages.values())

    def test_a_table_sits_in_the_scroll_region(self, guide_pages) -> None:
        assert any(
            soup.select("div.mvp-sphinx-scroll table") for soup in guide_pages.values()
        )

    def test_an_image_is_served_as_an_image(self, guide_pages, client) -> None:
        found = []
        for address, soup in guide_pages.items():
            for image in soup.select("img[src]"):
                response = client.get(urljoin(address, image["src"]))
                found.append((response.status_code, response.headers["Content-Type"]))
                response.close()

        assert any(
            status == 200 and kind.startswith("image/") for status, kind in found
        )

    def test_a_download_is_served(self, guide_pages, client) -> None:
        statuses = []
        for address, soup in guide_pages.items():
            for link in soup.select("a.download[href]"):
                response = client.get(urljoin(address, link["href"]))
                statuses.append(response.status_code)
                response.close()

        assert 200 in statuses

    def test_a_glossary_is_drawn(self, guide_pages) -> None:
        assert any(soup.select("dl.glossary") for soup in guide_pages.values())

    def test_a_reference_links_another_page_of_the_guide(self, guide_pages) -> None:
        targets = {
            (address, urldefrag(urljoin(address, link["href"]))[0])
            for address, soup in guide_pages.items()
            for link in soup.select("a.reference.internal[href]")
        }

        assert any(
            target in guide_pages and target != address for address, target in targets
        )

    def test_an_address_with_no_page_answers_not_found(
        self, demo_guide_app, client, db
    ) -> None:
        assert client.get("/docs/no-such-page/").status_code == 404

    def test_the_demo_menu_entry_leads_to_the_front_page(
        self, demo_guide_app, sidebar, client, db
    ) -> None:
        page = client.get(reverse("overview")).content.decode()
        entry = BeautifulSoup(sidebar(page), "html.parser").find(
            "a", href=lambda href: href and href.startswith("/docs/")
        )

        response = client.get(entry["href"])

        assert response.resolver_match.view_name == "docs:front_page"

    def test_a_function_entry_holds_a_field_list(self, link_helpers) -> None:
        entry = description(link_helpers, "demo.links.page_address")

        assert entry.select_one("dl.field-list > dt")

    def test_a_class_entry_holds_entries_of_its_own(self, link_helpers) -> None:
        entry = description(link_helpers, "demo.links.SharedLink")

        assert entry.select("dl > dt.sig-object[id]")

    def test_a_class_nested_in_a_class_holds_an_entry(self, link_helpers) -> None:
        outer = description(link_helpers, "demo.links.SharedLink")
        inner = description(link_helpers, "demo.links.SharedLink.Reader")

        assert inner in outer.descendants
        assert inner.select_one("dl > dt.sig-object[id]")

    def test_an_entry_can_have_an_empty_description(self, link_helpers) -> None:
        entry = description(link_helpers, "demo.links.strip_heading")

        assert not entry.get_text(strip=True)

    def test_an_entry_holds_a_deprecation(self, link_helpers) -> None:
        entry = description(link_helpers, "demo.links.old_address")

        assert entry.select_one("div.deprecated")

    def test_the_page_links_the_packages_stylesheet_and_none_from_the_build(
        self, link_helpers
    ) -> None:
        sheets = [
            link["href"] for link in link_helpers.select('link[rel="stylesheet"]')
        ]

        assert static("mvp_sphinx/content.css") in sheets
        assert not [each for each in sheets if "_static" in each]

    def test_a_source_link_leads_to_a_page_of_the_app(
        self, link_helpers, client
    ) -> None:
        address = "/docs/reference/link-helpers/"
        links = link_helpers.select("dt.sig-object a:has(> span.viewcode-link)")

        assert links
        for link in links:
            response = client.get(urldefrag(urljoin(address, link["href"]))[0])
            assert response.status_code == 200
            response.close()

    def test_every_name_in_the_summary_table_links_to_an_entry_of_the_page(
        self, link_helpers
    ) -> None:
        links = link_helpers.select("table.autosummary td:first-child a[href]")

        assert len(links) >= 4
        for link in links:
            assert urldefrag(link["href"])[0] == ""
            assert link_helpers.find(id=urldefrag(link["href"])[1])

    def test_the_summary_table_sits_in_a_scroll_region(self, link_helpers) -> None:
        table = link_helpers.select_one("table.autosummary")

        region = table.find_parent("div", class_="mvp-sphinx-scroll")
        assert region["role"] == "region"
        assert region["tabindex"] == "0"

    def test_a_deprecation_in_an_entry_is_one_the_stylesheet_draws(
        self, link_helpers
    ) -> None:
        entry = description(link_helpers, "demo.links.old_address")
        selectors = " ".join(
            selector for selector, declared in Stylesheet(STYLESHEET.read_text()).rules
        )

        notice = entry.select_one("div.deprecated")
        assert notice.select_one(".versionmodified")
        for hook in ("div.deprecated", r"\.versionmodified"):
            assert re.search(rf"{hook}(?![\w-])", selectors)

    def test_the_maths_page_loads_the_settings_then_the_library(
        self, maths_page
    ) -> None:
        sources = [script["src"] for script in maths_page.select("script[src]")]

        library = [source for source in sources if "cdn.jsdelivr.net" in source]
        assert len(library) == 1
        assert sources.index(static("mvp_sphinx/maths.js")) < sources.index(library[0])

    def test_each_numbered_equation_of_the_maths_page_holds_a_region(
        self, maths_page
    ) -> None:
        equations = maths_page.select("article div.math[id]")

        assert len(equations) >= 2
        for equation in equations:
            regions = equation.select('[role="region"]')
            assert len(regions) == 1
            assert regions[0]["tabindex"] == "0"
            assert regions[0]["aria-label"]

    @pytest.mark.parametrize("address", [WORKING_FORM, CANNOT_RUN])
    def test_each_source_shown_is_the_named_file_or_the_named_lines_of_it(
        self, guide_pages, address
    ) -> None:
        written = written_sources(address)
        shown = shown_examples(guide_pages[address])

        assert len(shown) == len(written)
        for example, sources in zip(shown, written, strict=True):
            panes = example.select(".mvp-sphinx-example-code pre")
            assert len(panes) == len(sources)
            for pane, (file, first, last) in zip(panes, sources, strict=True):
                text = file.read_text(encoding="utf-8")
                if first:
                    text = dedent("\n".join(text.splitlines()[first - 1 : last]))
                assert pane.get_text().splitlines() == text.splitlines()

    def test_the_working_form_page_holds_an_example_of_three_sources_and_one_of_part_of_a_file(
        self, guide_pages
    ) -> None:
        form, status = shown_examples(guide_pages[WORKING_FORM])

        file, first, last = written_sources(WORKING_FORM)[1][0]
        assert len(form.select("input[type=radio]")) == 3
        assert len(form.select(".mvp-sphinx-example-code")) == 3
        assert status.select("input[type=radio]") == []
        assert len(status.select(".mvp-sphinx-example-code")) == 1
        assert first is not None
        assert last - first + 1 < len(file.read_text(encoding="utf-8").splitlines())

    def test_the_cannot_run_page_holds_three_frames_and_one_notice(
        self, guide_pages
    ) -> None:
        examples = shown_examples(guide_pages[CANNOT_RUN])

        framed = [example for example in examples if example.select("iframe")]
        gone = [example for example in examples if not example.select("iframe")]
        assert [example.select_one("iframe")["src"] for example in framed] == [
            "/examples/slow/",
            "/examples/staff/",
            "/examples/broken/",
        ]
        assert len(gone) == 1
        assert len(gone[0].select("[role=alert]")) == 1
        assert all(example.select("[role=alert]") == [] for example in framed)

    @pytest.mark.parametrize("address", [WORKING_FORM, CANNOT_RUN])
    def test_both_example_pages_answer_200_to_an_anonymous_reader(
        self, guide_responses, address
    ) -> None:
        assert guide_responses[address].status_code == 200


class TestExamplePage:
    ADDRESS = "/examples/contact/"
    VALID = {
        "name": "Ada",
        "email": "ada@example.com",
        "message": "A message of some length.",
    }

    @staticmethod
    def has_shell(response) -> bool:
        return 'aria-label="Main navigation"' in response.content.decode()

    def test_the_example_answers_with_its_form_and_without_the_shell(
        self, client, db, overview_page
    ) -> None:
        response = client.get(self.ADDRESS)

        soup = BeautifulSoup(response.content, "html.parser")
        assert response.status_code == 200
        assert soup.select_one("form:has(input[name=email])") is not None
        assert not self.has_shell(response)
        assert 'aria-label="Main navigation"' in overview_page

    def test_a_form_sent_invalid_answers_with_its_errors_and_without_the_shell(
        self, client, db
    ) -> None:
        response = client.post(self.ADDRESS, {})

        assert response.status_code == 200
        assert response.context["form"].has_error("name", code="required")
        assert not self.has_shell(response)

    def test_a_form_sent_valid_redirects_to_its_own_address(self, client, db) -> None:
        response = client.post(self.ADDRESS, self.VALID)

        assert response.status_code == 302
        assert response.url == self.ADDRESS

    def test_the_page_it_redirects_to_carries_the_message(self, client, db) -> None:
        response = client.post(self.ADDRESS, self.VALID, follow=True)

        soup = BeautifulSoup(response.content, "html.parser")
        assert [message.level_tag for message in response.context["messages"]] == [
            "success"
        ]
        assert soup.select("[role=alert]")
        assert not self.has_shell(response)
