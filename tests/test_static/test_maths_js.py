"""The typesetting settings name only the page's own colours and classes."""

import json
import re
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

import mvp_sphinx

PACKAGE = Path(mvp_sphinx.__file__).parent
SETTINGS_FILE = PACKAGE / "static" / "mvp_sphinx" / "maths.js"
PAGE_TEMPLATE = PACKAGE / "templates" / "mvp_sphinx" / "page.html"

STRING = re.compile(r'"([^"]*)"')
COLOUR_VALUE = re.compile(
    r"^(#[0-9a-f]{3,8}|(rgb|hsl|hwb|lab|lch|oklab|oklch|color|color-mix)\()",
    re.IGNORECASE,
)
COLOUR_SETTING = re.compile(r'\bcolor\s*:\s*"([^"]*)"')
THEME_COLOUR = re.compile(r"^var\(--color-[\w-]+\)$")


@pytest.fixture(scope="module")
def settings() -> str:
    return SETTINGS_FILE.read_text()


class TestMathsSettings:
    def test_every_colour_named_is_a_theme_colour(self, settings) -> None:
        named = COLOUR_SETTING.findall(settings)

        assert named
        assert [value for value in named if not THEME_COLOUR.match(value)] == []

    def test_no_colour_is_written_as_a_literal(self, settings) -> None:
        literals = [
            value for value in STRING.findall(settings) if COLOUR_VALUE.match(value)
        ]

        assert STRING.findall(settings)
        assert literals == []

    @pytest.mark.parametrize("literal", ["#fff", "rgb(0 0 0)", "oklch(50% 0 0)"])
    def test_a_literal_colour_is_recognised_as_one(self, literal) -> None:
        assert COLOUR_VALUE.match(literal)

    def test_only_elements_sphinx_marked_as_maths_are_scanned(
        self, settings, reference_build
    ) -> None:
        scanned = re.search(r'elements\s*:\s*\["\.([\w-]+)"\]', settings)
        processed = re.search(r'processHtmlClass\s*:\s*"([^"]+)"', settings)
        page = json.loads((reference_build / "maths.fjson").read_text())
        body = BeautifulSoup(page["body"], "html.parser")

        notation = [
            text
            for text in body.find_all(string=re.compile(r"\\[(\[]"))
            if not text.find_parent("pre")
        ]
        assert scanned and processed
        assert processed[1] == scanned[1]
        assert notation
        assert [
            text for text in notation if not text.find_parent(class_=scanned[1])
        ] == []

    def test_the_class_to_ignore_is_the_one_the_content_scope_carries(
        self, settings
    ) -> None:
        ignored = re.search(r'ignoreHtmlClass\s*:\s*"([^"]+)"', settings)

        assert ignored
        assert re.search(
            rf'class="[^"]*\b{re.escape(ignored[1])}\b', PAGE_TEMPLATE.read_text()
        )
