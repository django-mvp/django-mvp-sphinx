"""The page body is read for maths and nothing else."""

import pytest

from mvp_sphinx.page_body import has_maths


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
        assert has_maths(markup) is True

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
        assert has_maths(markup) is False
