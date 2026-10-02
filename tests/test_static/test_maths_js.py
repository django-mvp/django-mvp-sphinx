"""The typesetting settings name only the page's own colours and classes."""

import re
from pathlib import Path

import pytest

import mvp_sphinx
from tests.test_static.test_content_css import STYLESHEET, Stylesheet

PACKAGE = Path(mvp_sphinx.__file__).parent
SETTINGS_FILE = PACKAGE / "static" / "mvp_sphinx" / "maths.js"
PAGE_TEMPLATE = PACKAGE / "templates" / "mvp_sphinx" / "page.html"

STRING = re.compile(r'"([^"]*)"')
COLOUR_VALUE = re.compile(
    r"^(#[0-9a-f]{3,8}|(rgb|hsl|hwb|lab|lch|oklab|oklch|color|color-mix)\()",
    re.IGNORECASE,
)
COLOUR_SETTING = re.compile(r'\bcolor\s*:\s*"([^"]*)"')
CUSTOM_PROPERTY = re.compile(r"^var\((--mvp-sphinx-[\w-]+)\)$")


@pytest.fixture(scope="module")
def settings() -> str:
    return SETTINGS_FILE.read_text()


class TestMathsSettings:
    def test_every_colour_named_is_a_property_the_stylesheet_defines(
        self, settings
    ) -> None:
        defined = Stylesheet(STYLESHEET.read_text()).properties()

        named = COLOUR_SETTING.findall(settings)
        assert named
        assert [
            value
            for value in named
            if not (match := CUSTOM_PROPERTY.match(value)) or match[1] not in defined
        ] == []

    def test_no_colour_is_written_as_a_literal(self, settings) -> None:
        literals = [
            value for value in STRING.findall(settings) if COLOUR_VALUE.match(value)
        ]

        assert STRING.findall(settings)
        assert literals == []

    @pytest.mark.parametrize("literal", ["#fff", "rgb(0 0 0)", "oklch(50% 0 0)"])
    def test_a_literal_colour_is_recognised_as_one(self, literal) -> None:
        assert COLOUR_VALUE.match(literal)

    def test_the_class_to_process_is_the_one_sphinx_gives_maths(self, settings) -> None:
        assert re.search(r'processHtmlClass\s*:\s*"math"', settings)

    def test_the_class_to_ignore_is_the_one_the_content_scope_carries(
        self, settings
    ) -> None:
        ignored = re.search(r'ignoreHtmlClass\s*:\s*"([^"]+)"', settings)

        assert ignored
        assert re.search(
            rf'class="[^"]*\b{re.escape(ignored[1])}\b', PAGE_TEMPLATE.read_text()
        )
        assert f".{ignored[1]}" in STYLESHEET.read_text()
