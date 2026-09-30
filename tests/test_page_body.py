"""BodyRewriter adds names and focus to a page's body and touches nothing else."""

import re
from html.parser import HTMLParser

import pytest

from mvp_sphinx.page_body import BodyRewriter

TABLE = "<table><tbody><tr><td>cell</td></tr></tbody></table>"
CAPTIONED = (
    '<table class="docutils" id="id1"><caption>'
    '<span class="caption-text">{text}</span>'
    '<a class="headerlink" href="#id1" title="Link to this table">¶</a>'
    "</caption><tbody><tr><td>cell</td></tr></tbody></table>"
)


class Regions(HTMLParser):
    """Collect the attributes of each region and the tables it holds."""

    def __init__(self, markup: str) -> None:
        super().__init__()
        self.regions: list[dict[str, str | None]] = []
        self.tables_in_region: list[int] = []
        self.open_regions = 0
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if attributes.get("role") == "region":
            self.regions.append(attributes)
            self.tables_in_region.append(0)
            self.open_regions += 1
        elif tag == "table" and self.open_regions:
            self.tables_in_region[-1] += 1


class HeadingLinks(HTMLParser):
    """Collect the attributes of each heading link, in document order."""

    def __init__(self, markup: str) -> None:
        super().__init__()
        self.links: list[dict[str, str | None]] = []
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "a" and "headerlink" in (attributes.get("class") or "").split():
            self.links.append(attributes)


def heading_links(markup: str) -> list[dict[str, str | None]]:
    return HeadingLinks(markup).links


def heading(text: str, title: str | None = "Link to this heading", tag="h2") -> str:
    attribute = "" if title is None else f' title="{title}"'
    return (
        f'<{tag} id="anchor">{text}'
        f'<a class="headerlink" href="#anchor"{attribute}>\u00b6</a></{tag}>'
    )


def regions(markup: str) -> list[dict[str, str | None]]:
    return Regions(markup).regions


class TestBodyRewriter:
    def test_a_table_is_wrapped_in_a_focusable_named_region(self) -> None:
        result = BodyRewriter.rewrite(TABLE)

        found = Regions(result)
        assert len(found.regions) == 1
        assert found.regions[0]["tabindex"] == "0"
        assert found.regions[0]["aria-label"]
        assert found.tables_in_region == [1]
        assert re.fullmatch(r"<div [^>]*>" + re.escape(TABLE) + "</div>", result)

    def test_a_captioned_tables_label_is_its_caption_without_the_heading_link(
        self,
    ) -> None:
        result = BodyRewriter.rewrite(CAPTIONED.format(text="Release schedule"))

        assert regions(result)[0]["aria-label"] == "Release schedule"

    def test_a_caption_holding_inline_markup_and_entities_labels_as_its_text(
        self,
    ) -> None:
        text = "The <code>setup</code> &amp; the &#8217;s"

        result = BodyRewriter.rewrite(CAPTIONED.format(text=text))

        assert (
            regions(result)[0]["aria-label"]
            == "The setup & the \N{RIGHT SINGLE QUOTATION MARK}s"
        )

    def test_an_uncaptioned_tables_label_is_not_empty(self) -> None:
        result = BodyRewriter.rewrite(TABLE)

        assert regions(result)[0]["aria-label"].strip()

    def test_a_caption_with_no_text_falls_back_to_the_uncaptioned_label(self) -> None:
        plain = regions(BodyRewriter.rewrite(TABLE))[0]["aria-label"]
        empty = CAPTIONED.format(text="  ")

        result = BodyRewriter.rewrite(empty)

        assert regions(result)[0]["aria-label"] == plain

    def test_a_label_with_an_ampersand_and_a_quote_is_escaped_once(self) -> None:
        result = BodyRewriter.rewrite(CAPTIONED.format(text='Q&amp;A "quoted"'))

        assert 'aria-label="Q&amp;A &quot;quoted&quot;"' in result
        assert regions(result)[0]["aria-label"] == 'Q&A "quoted"'

    def test_a_table_nested_in_a_table_is_wrapped_once(self) -> None:
        nested = f"<table><tbody><tr><td>{TABLE}</td></tr></tbody></table>"

        result = BodyRewriter.rewrite(nested)

        found = Regions(result)
        assert len(found.regions) == 1
        assert found.tables_in_region == [2]

    def test_each_of_two_adjacent_tables_is_wrapped_on_its_own(self) -> None:
        result = BodyRewriter.rewrite(TABLE + TABLE)

        found = Regions(result)
        assert len(found.regions) == 2
        assert found.tables_in_region == [1, 1]

    @pytest.mark.parametrize(
        "template",
        [
            '<div class="admonition note"><p>Note</p>{table}</div>',
            "<ul><li><p>Item</p>{table}</li></ul>",
        ],
        ids=["admonition", "list item"],
    )
    def test_a_table_inside_other_content_is_wrapped(self, template) -> None:
        result = BodyRewriter.rewrite(template.format(table=TABLE))

        assert Regions(result).tables_in_region == [1]

    def test_a_table_written_in_capitals_is_wrapped(self) -> None:
        result = BodyRewriter.rewrite("<TABLE><TR><TD>x</TD></TR></TABLE >")

        assert Regions(result).tables_in_region == [1]

    def test_everything_but_the_wrapper_comes_back_as_it_arrived(self) -> None:
        original = (
            "<p>R&D &amp; &#8217; &copy caf&eacute;</p><!-- <table> -->\n"
            "<TABLE class=x>\r\n<tr><td>a &lt; b &copy</td></tr></TABLE >\n<p>end</p>"
        )

        result = BodyRewriter.rewrite(original)

        opening = re.search(r'<div [^>]*role="region"[^>]*>', result)
        assert opening
        assert re.search(r"<div [^>]*><TABLE.*</TABLE ></div>\n<p>end", result, re.S)
        unwrapped = result.replace(opening.group(), "", 1).replace("</div>", "", 1)
        assert unwrapped == original

    @pytest.mark.parametrize(
        "markup",
        [
            "",
            "<p>Plain</p>",
            "<p>&amp; and &#8217; and &lt;</p>",
            "<p>R&D and AT&T</p>",
            "<p>&copy and &nbsp text</p>",
            "<div>a</div></TABLE >",
            "<!-- <table><tr><td>hidden</td></tr></table> -->",
            "<p CLASS='x' data-a = 1>Odd   spacing\n\n and case</P>",
        ],
        ids=[
            "empty",
            "plain",
            "entities",
            "bare ampersand",
            "semicolon-less entities",
            "stray capital end tag",
            "comment",
            "odd tags",
        ],
    )
    def test_markup_without_a_table_comes_back_byte_for_byte(self, markup) -> None:
        assert BodyRewriter.rewrite(markup) == markup


class TestBodyRewriterHeadingLinks:
    def test_a_heading_link_is_named_by_its_title_and_the_headings_text(self) -> None:
        result = BodyRewriter.rewrite(heading("Installing"))

        assert heading_links(result)[0]["aria-label"] == (
            "Link to this heading: Installing"
        )

    def test_a_heading_link_keeps_its_address_and_the_rest_of_the_heading(self) -> None:
        original = heading("Installing")

        result = BodyRewriter.rewrite(original)

        link = heading_links(result)[0]
        assert re.search(r'\s+aria-label="[^"]*"\s+\S', result)
        assert link["href"] == "#anchor"
        assert link["title"] == "Link to this heading"
        assert result.replace(' aria-label="Link to this heading: Installing"', "") == (
            original
        )

    @pytest.mark.parametrize("tag", ["h1", "h2", "h3", "h4", "h5", "h6"])
    def test_a_link_in_a_heading_of_any_level_is_named(self, tag) -> None:
        result = BodyRewriter.rewrite(heading("Installing", tag=tag))

        assert heading_links(result)[0]["aria-label"].endswith("Installing")

    def test_a_heading_holding_inline_code_is_named_with_the_codes_text(self) -> None:
        text = (
            'Using <code class="docutils literal"><span class="pre">run()</span></code>'
        )

        result = BodyRewriter.rewrite(heading(text))

        assert heading_links(result)[0]["aria-label"].endswith("Using run()")

    def test_a_heading_holding_a_link_is_named_with_the_links_text(self) -> None:
        text = '<a class="reference external" href="https://x.test">The site</a> setup'

        result = BodyRewriter.rewrite(heading(text))

        assert heading_links(result)[0]["aria-label"].endswith("The site setup")

    def test_a_link_with_no_title_is_named_by_the_text_alone(self) -> None:
        result = BodyRewriter.rewrite(heading("Installing", title=None))

        assert heading_links(result)[0]["aria-label"] == "Installing"

    def test_heading_text_with_an_ampersand_is_unescaped_then_escaped_once(
        self,
    ) -> None:
        result = BodyRewriter.rewrite(heading("Q&amp;A <em>&quot;now&quot;</em>"))

        assert 'aria-label="Link to this heading: Q&amp;A &quot;now&quot;"' in result
        assert heading_links(result)[0]["aria-label"].endswith('Q&A "now"')

    def test_whitespace_in_the_heading_is_collapsed(self) -> None:
        result = BodyRewriter.rewrite(heading("  Two\n   lines  "))

        assert heading_links(result)[0]["aria-label"].endswith(": Two lines")

    def test_a_glossary_terms_link_is_named_by_its_title_and_the_term(self) -> None:
        markup = (
            '<dl class="glossary simple"><dt id="term-widget">widget'
            '<a class="headerlink" href="#term-widget" title="Link to this term">'
            "\u00b6</a></dt><dd><p>A thing.</p></dd></dl>"
        )

        result = BodyRewriter.rewrite(markup)

        assert heading_links(result)[0]["aria-label"] == "Link to this term: widget"

    def test_a_tables_caption_link_is_named_by_its_title_and_the_caption(self) -> None:
        result = BodyRewriter.rewrite(CAPTIONED.format(text="Release schedule"))

        assert heading_links(result)[0]["aria-label"] == (
            "Link to this table: Release schedule"
        )

    def test_each_of_two_headings_is_named_by_its_own_text(self) -> None:
        result = BodyRewriter.rewrite(heading("First") + heading("Second"))

        labels = [link["aria-label"] for link in heading_links(result)]
        assert [label.split(": ")[1] for label in labels] == ["First", "Second"]

    def test_a_heading_after_unclosed_and_void_elements_is_named_by_its_own_text(
        self,
    ) -> None:
        markup = "<ul><li>item<br><p>para<img src=x></ul>" + heading("Installing")

        result = BodyRewriter.rewrite(markup)

        assert heading_links(result)[0]["aria-label"].endswith(": Installing")

    def test_a_link_that_is_not_a_heading_link_is_left_alone(self) -> None:
        markup = '<h2>Title <a href="#x" title="Elsewhere">here</a></h2>'

        assert BodyRewriter.rewrite(markup) == markup
