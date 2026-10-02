"""BodyRewriter adds names and focus to a page's body and touches nothing else."""

import json
import re
from html import unescape
from html.parser import HTMLParser

import pytest
from bs4 import BeautifulSoup

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


def entry(entry_id: str, signature: str, classes: str = "sig sig-object py") -> str:
    return (
        f'<dt class="{classes}" id="{entry_id}">{signature}'
        f'<a class="headerlink" href="#{entry_id}" title="Link to this definition">'
        "\u00b6</a></dt>"
    )


def sig_name(text: str) -> str:
    return (
        '<span class="sig-name descname"><span class="n">'
        f'<span class="pre">{text}</span></span></span>'
    )


def sig_prename(text: str) -> str:
    return f'<span class="sig-prename descclassname">{text}</span>'


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


class TestEntryLinks:
    @pytest.fixture
    def api_body(self, reference_build) -> str:
        return json.loads((reference_build / "api.fjson").read_text())["body"]

    @pytest.fixture
    def api_links(self, api_body) -> dict[str, dict[str, str | None]]:
        links = heading_links(BodyRewriter.rewrite(api_body))
        return {link["href"]: link for link in links}

    @staticmethod
    def name(link: dict[str, str | None]) -> str:
        return unescape(link["aria-label"]).split(": ", 1)[1]

    def test_a_top_level_function_is_named_by_its_dotted_name(self, api_links) -> None:
        link = api_links["#demo.links.page_address"]

        assert self.name(link) == "demo.links.page_address"

    def test_the_names_of_same_named_methods_of_two_classes_differ(
        self, api_links
    ) -> None:
        names = [
            self.name(api_links[f"#demo.links.{each}.render"])
            for each in ("Link", "Shortcut")
        ]

        assert names == ["demo.links.Link.render", "demo.links.Shortcut.render"]

    def test_a_method_in_a_nested_class_is_named_by_its_whole_path(
        self, api_links
    ) -> None:
        link = api_links["#demo.links.Link.Reader.can_open"]

        assert self.name(link) == "demo.links.Link.Reader.can_open"

    def test_another_languages_function_is_named_by_its_name(self, api_links) -> None:
        assert self.name(api_links["#buildAddress"]) == "buildAddress"

    def test_a_link_beside_a_source_link_is_named_without_its_text(self) -> None:
        source = (
            '<a class="reference internal" href="_modules/demo/#f">'
            '<span class="viewcode-link"><span class="pre">[source]</span></span></a>'
        )
        signature = (
            f"{sig_prename('demo.')}{sig_name('f')}(<em>a</em>) &#8594; str{source}"
        )

        result = BodyRewriter.rewrite(entry("demo.f", signature))

        assert self.name(heading_links(result)[0]) == "demo.f"

    def test_the_title_still_leads_the_name(self, api_links) -> None:
        link = api_links["#demo.links.page_address"]

        assert link["aria-label"] == f"{link['title']}: demo.links.page_address"

    @pytest.mark.parametrize(
        ("entry_id", "prename", "name", "expected"),
        [
            ("demo.links.f", "demo.links.", "f", "demo.links.f"),
            ("Foo", "", "Foo", "Foo"),
            ("_CPPv43Foo", "", "Foo", "Foo"),
            ("_CPPv4N2ns3FooE", "ns::", "Foo", "ns::Foo"),
            ("barFoo", "ns.", "Foo", "ns.Foo"),
            ("envvar-MY_VAR", "", "MY_VAR", "MY_VAR"),
        ],
    )
    def test_an_ids_text_names_the_link_only_when_it_ends_in_the_name(
        self, entry_id, prename, name, expected
    ) -> None:
        signature = f"{sig_prename(prename)}{sig_name(name)}(<em>a</em>)"

        result = BodyRewriter.rewrite(entry(entry_id, signature))

        assert self.name(heading_links(result)[0]) == expected

    def test_a_signature_with_two_names_is_named_by_its_text_as_written(self) -> None:
        signature = f"{sig_name('-v')}{sig_prename('')}{sig_prename(', ')}{sig_name('--verbose')}"

        result = BodyRewriter.rewrite(entry("cmdoption-v", signature))

        assert self.name(heading_links(result)[0]) == "-v, --verbose"

    def test_two_names_are_not_replaced_by_an_id_ending_in_the_first(self) -> None:
        signature = f"{sig_name('-v')}{sig_prename(', ')}{sig_name('--verbose')}"

        result = BodyRewriter.rewrite(entry("program.-v", signature))

        assert self.name(heading_links(result)[0]) == "-v, --verbose"

    def test_an_entry_with_no_name_is_named_by_its_text_as_before(self) -> None:
        markup = entry("thing", '<span class="n">thing</span> (<em>a</em>)')

        result = BodyRewriter.rewrite(markup)

        assert self.name(heading_links(result)[0]) == "thing (a)"

    def test_a_names_class_outside_a_signature_does_not_name_a_link(self) -> None:
        markup = entry("term", f"widget {sig_name('other')}", classes="glossary")

        result = BodyRewriter.rewrite(markup)

        assert self.name(heading_links(result)[0]) == "widget other"

    def test_a_heading_and_a_glossary_term_are_named_as_before(self) -> None:
        markup = (
            heading("Installing")
            + '<dl class="glossary"><dt id="term-widget">widget'
            + '<a class="headerlink" href="#term-widget" title="Link to this term">'
            + "\u00b6</a></dt><dd></dd></dl>"
        )

        result = BodyRewriter.rewrite(markup)

        assert [link["aria-label"] for link in heading_links(result)] == [
            "Link to this heading: Installing",
            "Link to this term: widget",
        ]

    def test_nothing_but_the_inserted_attributes_changes(self, api_body) -> None:
        result = BodyRewriter.rewrite(api_body)

        assert re.sub(r' aria-label="[^"]*"', "", result) == api_body

    def test_a_heading_after_an_entry_is_not_named_by_that_entry(self) -> None:
        markup = (
            '<dl><dt class="sig sig-object py" id="m.f">'
            '<span class="sig-name descname">f</span>'
            '<a class="headerlink" href="#m.f" title="Definition">¶</a></dt></dl>'
            '<h2 class="sig-object">Other thing'
            '<a class="headerlink" href="#o" title="Heading">¶</a></h2>'
        )

        rewritten = BeautifulSoup(BodyRewriter.rewrite(markup), "html.parser")

        link = rewritten.find("a", href="#o")
        assert link["aria-label"] == "Heading: Other thing"


class TestMathsDetection:
    @pytest.mark.parametrize(
        "markup",
        [
            '<p>So <span class="math notranslate nohighlight">\\(x\\)</span>.</p>',
            '<div class="math notranslate nohighlight">\n\\[x\\]</div>',
            '<span class="eqno math">(1)</span>',
        ],
        ids=["inline", "display", "among other classes"],
    )
    def test_a_body_with_a_math_element_has_maths(self, markup) -> None:
        assert BodyRewriter.parse(markup).has_maths is True

    @pytest.mark.parametrize(
        "markup",
        [
            "",
            "<p>Plain prose and $5 and $6.</p>",
            '<pre><span class="n">&lt;span class="math"&gt;\\(x\\)&lt;/span&gt;'
            "</span></pre>",
            '<span class="mathematics">x</span>',
            '<span class="mathjax_process">x</span>',
            '<span class="prefix-math">x</span>',
        ],
        ids=[
            "empty",
            "prose",
            "a code sample showing the element",
            "class starting with math",
            "class starting with math and an underscore",
            "class ending in math",
        ],
    )
    def test_a_body_without_a_math_element_has_none(self, markup) -> None:
        assert BodyRewriter.parse(markup).has_maths is False


class Balance(HTMLParser):
    """Check that every element opened is closed in the order it was opened."""

    VOID = BodyRewriter.VOID_TAGS

    def __init__(self, markup: str) -> None:
        super().__init__()
        self.stack: list[str] = []
        self.mismatches: list[str] = []
        self.feed(markup)
        self.close()

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack.pop() != tag:
            self.mismatches.append(tag)

    @property
    def balanced(self) -> bool:
        return not self.stack and not self.mismatches


def soup(markup: str) -> BeautifulSoup:
    return BeautifulSoup(markup, "html.parser")


NOTATION = "\n\\[e^{i\\pi} + 1 = 0\\]"
NUMBER = (
    '\n<span class="eqno">{number}'
    '<a class="headerlink" href="#equation-first" title="Link to this equation">'
    "¶</a></span>"
)
UNNUMBERED = f'<div class="math notranslate nohighlight">{NOTATION}</div>'
NUMBERED = (
    '<div class="math notranslate nohighlight" id="equation-first">'
    f"{NUMBER.format(number='(1)')}\\[x = y\\]</div>"
)
IN_A_PARAGRAPH = (
    '<div class="math"><p><span class="eqno">(1)</span> \\[x = y\\]</p></div>'
)
REGION_OPENING = re.compile(r'<div class="mvp-sphinx-scroll"[^>]*>')


class TestEquationRegion:
    def test_an_unnumbered_equation_is_in_a_focusable_named_region(self) -> None:
        result = BodyRewriter.rewrite(UNNUMBERED)

        found = regions(result)
        assert len(found) == 1
        assert found[0]["tabindex"] == "0"
        assert found[0]["aria-label"]
        region = soup(result).select_one("div.math > .mvp-sphinx-scroll")
        assert region["role"] == "region"
        assert "e^{i" in region.get_text()

    def test_the_region_of_a_numbered_equation_follows_the_number(self) -> None:
        result = BodyRewriter.rewrite(NUMBERED)

        equation = soup(result).select_one("div.math")
        children = [child.name for child in equation.children if child.name]
        assert children == ["span", "div"]
        number, region = (
            equation.find(name, recursive=False) for name in ("span", "div")
        )
        assert "eqno" in number["class"]
        assert region["role"] == "region"
        assert not number.find_parent(attrs={"role": "region"})
        assert "x = y" in region.get_text()
        assert "x = y" not in number.get_text()

    def test_the_name_of_a_numbered_equation_holds_its_number(self) -> None:
        result = BodyRewriter.rewrite(NUMBERED)

        label = regions(result)[0]["aria-label"]
        assert "(1)" in label
        assert "\u00b6" not in label
        assert label != regions(BodyRewriter.rewrite(UNNUMBERED))[0]["aria-label"]

    def test_two_numbered_equations_are_named_by_their_own_numbers(self) -> None:
        second = NUMBERED.replace("(1)", "(2)")

        found = regions(BodyRewriter.rewrite(NUMBERED + second))

        assert ["(1)" in f["aria-label"] for f in found] == [True, False]
        assert ["(2)" in f["aria-label"] for f in found] == [False, True]

    @pytest.mark.parametrize(
        "markup", [UNNUMBERED, NUMBERED], ids=["unnumbered", "numbered"]
    )
    def test_the_notation_between_the_regions_tags_is_as_sphinx_wrote_it(
        self, markup
    ) -> None:
        result = BodyRewriter.rewrite(markup)

        inside = re.search(REGION_OPENING.pattern + r"(.*)</div></div>$", result, re.S)
        assert inside
        start = markup.index("</span>") + len("</span>") if "eqno" in markup else None
        notation = markup[start or markup.index(">") + 1 : -len("</div>")]
        assert inside[1] == notation

    def test_inline_maths_is_not_wrapped(self) -> None:
        markup = '<p>So <span class="math notranslate">\\(a^2\\)</span> holds.</p>'

        assert BodyRewriter.rewrite(markup) == markup

    def test_a_span_with_a_math_class_inside_an_equation_is_not_wrapped_on_its_own(
        self,
    ) -> None:
        markup = '<div class="math">\\[x\\] <span class="math">\\(y\\)</span></div>'

        assert len(regions(BodyRewriter.rewrite(markup))) == 1

    def test_an_equation_in_a_table_has_its_own_region_inside_the_tables(
        self,
    ) -> None:
        markup = f"<table><tbody><tr><td>{UNNUMBERED}</td></tr></tbody></table>"

        result = BodyRewriter.rewrite(markup)

        assert Balance(result).balanced
        outer, inner = soup(result).select('[role="region"]')
        assert outer.find("table")
        assert inner.find_parent(attrs={"role": "region"}) is outer
        assert inner.find_parent("div", class_="math")
        assert not inner.find("table")

    def test_a_number_holding_markup_characters_is_escaped_in_the_name(self) -> None:
        markup = NUMBERED.replace("(1)", "(1&amp;&lt;b&gt;&quot;)")

        result = BodyRewriter.rewrite(markup)

        assert Balance(result).balanced
        found = regions(result)
        assert len(found) == 1
        assert '(1&<b>")' in found[0]["aria-label"]
        assert "<b>" not in REGION_OPENING.search(result).group()

    def test_an_equation_whose_number_is_in_a_paragraph_is_wrapped_whole(self) -> None:
        result = BodyRewriter.rewrite(IN_A_PARAGRAPH)

        assert Balance(result).balanced
        region = soup(result).select_one("div.math > .mvp-sphinx-scroll")
        assert region["role"] == "region"
        assert region.find("p", recursive=False)
        assert region.find("span", class_="eqno")
        assert result.startswith(
            '<div class="math">' + REGION_OPENING.search(result)[0]
        )

    @pytest.mark.parametrize(
        "markup",
        [
            UNNUMBERED,
            NUMBERED,
            IN_A_PARAGRAPH,
            f"<p>R&D &amp; &copy caf&eacute;</p>\n{NUMBERED}\n<p>end</p>",
            f"{UNNUMBERED}{NUMBERED}",
        ],
        ids=["unnumbered", "numbered", "in a paragraph", "entities", "two"],
    )
    def test_removing_the_inserted_tags_gives_back_the_original(self, markup) -> None:
        result = BodyRewriter.rewrite(markup)

        opened = re.sub(
            r"(?<=<a) aria-label=\"[^\"]*\"", "", REGION_OPENING.sub("", result)
        )
        assert opened.count("</div>") == markup.count("</div>") + len(regions(result))
        assert opened.replace("</div></div>", "</div>") == markup
