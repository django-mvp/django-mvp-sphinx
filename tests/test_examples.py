"""LiveExamples, which finds the examples the build wrote into a page's body."""

import pytest
from django.urls import set_script_prefix

from mvp_sphinx.examples import LiveExamples

BEFORE = '<h1>A page</h1>\n<p>Written before.</p>\n<div class="note">\n<p>Aside</p>\n</div>\n'
AFTER = '\n<p>Written after.</p>\n<div class="highlight-python">\n<pre>x = 1</pre>\n</div>\n'
FIRST_SOURCE = (
    '<div class="highlight-python notranslate"><div class="highlight">'
    '<pre><span class="n">x</span> <span class="o">=</span> 1\n</pre></div></div>\n'
)
SECOND_SOURCE = '<div class="highlight-html"><pre>&lt;b&gt;</pre></div>'


def example_markup(
    address: str = "/examples/status/",
    title: str = "A status page",
    sources: tuple[tuple[str, str], ...] = (("status.html", FIRST_SOURCE),),
) -> str:
    inner = "".join(
        f'<div class="mvp-sphinx-example-source" data-name="{name}">{html}</div>\n'
        for name, html in sources
    )
    return (
        f'<div class="mvp-sphinx-example" data-address="{address}" '
        f'data-title="{title}">\n{inner}</div>'
    )


class TestParts:
    def test_a_body_without_an_example_is_one_markup_part_unchanged(self) -> None:
        body = BEFORE + AFTER

        parts = LiveExamples.parts(body)

        assert parts == [{"html": body}]

    def test_a_body_with_one_example_is_markup_example_markup(self) -> None:
        body = BEFORE + example_markup() + AFTER

        parts = LiveExamples.parts(body)

        assert [next(iter(part)) for part in parts] == ["html", "example", "html"]
        assert parts[0]["html"] == BEFORE
        assert parts[2]["html"] == AFTER

    def test_the_example_carries_its_address_title_and_sources_in_order(self) -> None:
        markup = example_markup(
            sources=(("status.html", FIRST_SOURCE), ("views.py", SECOND_SOURCE))
        )

        example = LiveExamples.parts(BEFORE + markup + AFTER)[1]["example"]

        assert example["address"] == "/examples/status/"
        assert example["title"] == "A status page"
        assert example["sources"] == [
            {"name": "status.html", "html": FIRST_SOURCE},
            {"name": "views.py", "html": SECOND_SOURCE},
        ]

    def test_attribute_values_are_read_back_unescaped(self) -> None:
        markup = example_markup(title="Status of &quot;an order&quot; &amp; items")

        example = LiveExamples.parts(markup)[1]["example"]

        assert example["title"] == 'Status of "an order" & items'

    def test_a_div_inside_a_source_does_not_end_it_early(self) -> None:
        nested = "<div><div><p>deep</p></div></div><div></div>after the divs"
        markup = example_markup(sources=(("a.html", nested), ("b.html", "second")))

        example = LiveExamples.parts(markup)[1]["example"]

        assert [(s["name"], s["html"]) for s in example["sources"]] == [
            ("a.html", nested),
            ("b.html", "second"),
        ]

    def test_two_examples_get_different_ids(self) -> None:
        body = example_markup() + AFTER + example_markup()

        examples = [
            part["example"] for part in LiveExamples.parts(body) if "example" in part
        ]

        assert len(examples) == 2
        assert examples[0]["id"] != examples[1]["id"]

    def test_an_example_whose_wrapper_never_closes_is_left_in_the_page_as_markup(
        self,
    ) -> None:
        body = BEFORE + example_markup().removesuffix("</div>") + AFTER

        parts = LiveExamples.parts(body)

        assert parts == [{"html": body}]

    def test_an_example_after_a_damaged_one_is_not_lost_when_the_damage_comes_last(
        self,
    ) -> None:
        damaged = example_markup().removesuffix("</div>")
        body = example_markup() + AFTER + damaged

        parts = LiveExamples.parts(body)

        assert [next(iter(part)) for part in parts] == ["html", "example", "html"]
        assert parts[2]["html"] == AFTER + damaged

    @pytest.mark.parametrize(
        "separator", ["\x0c", "\x0b", "\u2028", "\u2029", "\x85", "\x1c", "\r"]
    )
    def test_a_line_separator_other_than_a_newline_does_not_shift_the_cuts(
        self, separator
    ) -> None:
        before = f"<p>be{separator}fore</p>\n"
        source = f"<div><pre>x{separator}y</pre></div>"
        body = before + example_markup(sources=(("a.py", source),)) * 2 + AFTER

        parts = LiveExamples.parts(body)

        assert parts[0]["html"] == before
        assert parts[1]["example"]["sources"][0]["html"] == source
        assert parts[3]["example"]["sources"][0]["html"] == source
        assert parts[4]["html"] == AFTER

    @pytest.mark.parametrize(
        "address",
        ["/examples/status/", "/examples/status/?a=1#frag", "/examples/%73tatus/"],
    )
    def test_an_address_the_urlconf_has_is_available(self, address) -> None:
        example = LiveExamples.parts(example_markup(address=address))[1]["example"]

        assert example["available"] is True

    def test_an_address_the_urlconf_lacks_is_not_available(self) -> None:
        example = LiveExamples.parts(example_markup(address="/examples/retired/"))[1][
            "example"
        ]

        assert example["available"] is False

    @pytest.mark.parametrize(
        "address", ["//host/examples/status/", "https://host/examples/status/"]
    )
    def test_an_address_on_another_site_is_not_available(self, address) -> None:
        example = LiveExamples.parts(example_markup(address=address))[1]["example"]

        assert example["available"] is False

    def test_the_sites_script_prefix_is_taken_off_before_the_address_is_resolved(
        self,
    ) -> None:
        set_script_prefix("/site/")
        try:
            behind = LiveExamples.parts(
                example_markup(address="/site/examples/status/")
            )
            outside = LiveExamples.parts(example_markup(address="/examples/status/"))
        finally:
            set_script_prefix("/")

        assert behind[1]["example"]["available"] is True
        assert outside[1]["example"]["available"] is False
