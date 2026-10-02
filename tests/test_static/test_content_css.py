"""The package stylesheet keeps to the theme: no literal colour, scoped, readable."""

import json
import math
import re
from importlib.resources import files
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

import mvp_sphinx

STYLESHEET = Path(mvp_sphinx.__file__).parent / "static" / "mvp_sphinx" / "content.css"
THEME_STYLESHEET = files("mvp") / "static" / "css" / "django-mvp.css"
SCOPE = ".mvp-sphinx-content"
MINIMUM_CONTRAST = 4.5
THEMES = ["light", "dark"]

COLOUR_PROPERTY = re.compile(
    r"^(--mvp-sphinx-.*|(.*-)?color|background(-color)?|border(-[a-z]+)*"
    r"|outline(-[a-z]+)*|box-shadow|text-decoration(-color)?|fill|stroke)$"
)
ALLOWED_KEYWORDS = re.compile(r"\b(solid|none|currentcolor|inherit)\b")
LENGTH = re.compile(r"-?\d*\.?\d+(%|px|rem|em)?")


class Stylesheet:
    """The rules of a stylesheet, read without a CSS parser."""

    def __init__(self, text: str) -> None:
        self.rules = self.scan(re.sub(r"/\*.*?\*/", "", text, flags=re.S))

    @classmethod
    def scan(cls, text: str) -> list[tuple[str, dict[str, str]]]:
        """Return (selector, declarations) for every rule, flattening @media."""
        rules = []
        for prelude, body in cls.blocks(text):
            if prelude.startswith("@media") or prelude.startswith("@supports"):
                rules.extend(cls.scan(body))
            elif not prelude.startswith("@"):
                rules.append((prelude, cls.declarations(body)))
        return rules

    @staticmethod
    def blocks(text: str) -> list[tuple[str, str]]:
        found, depth, start, prelude_from = [], 0, 0, 0
        for position, character in enumerate(text):
            if character == "{":
                if depth == 0:
                    start = position + 1
                    prelude = text[prelude_from:position].strip()
                depth += 1
            elif character == "}":
                depth -= 1
                if depth == 0:
                    found.append((prelude, text[start:position]))
                    prelude_from = position + 1
        return found

    @staticmethod
    def declarations(body: str) -> dict[str, str]:
        declared, depth, current = {}, 0, ""
        for character in f"{body};":
            depth += {"(": 1, ")": -1}.get(character, 0)
            if character == ";" and depth == 0:
                name, separator, value = current.partition(":")
                if value:
                    value = (
                        " ".join(value.split()).replace("( ", "(").replace(" )", ")")
                    )
                    declared[name.strip()] = value
                current = ""
            else:
                current += character
        return declared

    def properties(self) -> dict[str, str]:
        """Return the package's own custom properties, by name."""
        return {
            name: value
            for selector, declared in self.rules
            for name, value in declared.items()
            if name.startswith("--mvp-sphinx-")
        }


class ColourMath:
    """Resolve theme colours and measure the contrast between two of them."""

    OKLCH = re.compile(r"oklch\(\s*([\d.]+)%\s+([\d.]+)\s+([\d.]+)\s*\)")

    @classmethod
    def theme(cls, name: str) -> dict[str, tuple[float, float, float]]:
        """Read one of django-mvp's themes: its `--color-*` values as OKLab."""
        text = THEME_STYLESHEET.read_text()
        for match in re.finditer(rf"\[data-theme={name}\]\s*\{{([^}}]*)\}}", text):
            if "--color-base-100" in match.group(1):
                return {
                    f"--color-{role}": cls.from_oklch(value)
                    for role, value in re.findall(
                        r"--color-([\w-]+):(oklch\([^)]*\))", match.group(1)
                    )
                }
        raise AssertionError(f"django-mvp defines no {name} theme")

    @classmethod
    def from_oklch(cls, value: str) -> tuple[float, float, float]:
        lightness, chroma, hue = map(float, cls.OKLCH.fullmatch(value).groups())
        radians = math.radians(hue)
        return (lightness / 100, chroma * math.cos(radians), chroma * math.sin(radians))

    @classmethod
    def arguments(cls, text: str) -> list[str]:
        """Split a function's arguments at the commas outside nested brackets."""
        parts, depth, current = [], 0, ""
        for character in text:
            depth += {"(": 1, ")": -1}.get(character, 0)
            if character == "," and depth == 0:
                parts.append(current.strip())
                current = ""
            else:
                current += character
        return [*parts, current.strip()]

    @classmethod
    def resolve(cls, value, own, theme):
        """Turn `var()` and `color-mix(in oklab, ...)` into an OKLab colour."""
        value = value.strip()
        if value.startswith("var("):
            name = value[4:-1].strip()
            return cls.resolve(own[name], own, theme) if name in own else theme[name]
        assert value.startswith("color-mix(in oklab,"), value
        first, second = cls.arguments(value[len("color-mix(") : -1])[1:]
        (one, share_one), (two, share_two) = cls.weighted(first), cls.weighted(second)
        if share_one is None and share_two is None:
            share_one = share_two = 50.0
        share_one = 100 - share_two if share_one is None else share_one
        share_two = 100 - share_one if share_two is None else share_two
        total = share_one + share_two
        a, b = cls.resolve(one, own, theme), cls.resolve(two, own, theme)
        return tuple(
            (x * share_one + y * share_two) / total for x, y in zip(a, b, strict=True)
        )

    @staticmethod
    def weighted(argument: str) -> tuple[str, float | None]:
        match = re.fullmatch(r"(.*?)\s+([\d.]+)%", argument)
        return (match.group(1), float(match.group(2))) if match else (argument, None)

    @classmethod
    def luminance(cls, lab: tuple[float, float, float]) -> float:
        """Return WCAG relative luminance of an OKLab colour."""
        lightness, a, b = lab
        l_, m_, s_ = (
            lightness + 0.3963377774 * a + 0.2158037573 * b,
            lightness - 0.1055613458 * a - 0.0638541728 * b,
            lightness - 0.0894841775 * a - 1.2914855480 * b,
        )
        long, medium, short = l_**3, m_**3, s_**3
        red = 4.0767416621 * long - 3.3077115913 * medium + 0.2309699292 * short
        green = -1.2684380046 * long + 2.6097574011 * medium - 0.3413193965 * short
        blue = -0.0041960863 * long - 0.7034186147 * medium + 1.7076147010 * short
        red, green, blue = (min(1.0, max(0.0, c)) for c in (red, green, blue))
        return 0.2126 * red + 0.7152 * green + 0.0722 * blue

    @classmethod
    def contrast(cls, one, two) -> float:
        lighter, darker = sorted((cls.luminance(one), cls.luminance(two)), reverse=True)
        return (lighter + 0.05) / (darker + 0.05)


@pytest.fixture(scope="module")
def stylesheet() -> Stylesheet:
    return Stylesheet(STYLESHEET.read_text())


def literal_colours(value: str) -> str:
    """Return what is left of a declaration once the allowed forms are removed."""
    while match := re.search(r"(var|color-mix)\(", value):
        depth, end = 1, match.end()
        while depth:
            depth += {"(": 1, ")": -1}.get(value[end], 0)
            end += 1
        value = value[: match.start()] + value[end:]
    value = ALLOWED_KEYWORDS.sub("", value)
    return LENGTH.sub("", value).replace(",", "").strip()


class TestContentStylesheet:
    def test_no_colour_is_written_as_a_literal(self, stylesheet) -> None:
        coloured = [
            (selector, name, value)
            for selector, declared in stylesheet.rules
            for name, value in declared.items()
            if COLOUR_PROPERTY.match(name)
        ]

        assert coloured
        assert [c for c in coloured if literal_colours(c[2])] == []

    @pytest.mark.parametrize("literal", ["#fff", "rgb(0 0 0)", "oklch(50% 0 0)", "red"])
    def test_a_literal_colour_is_recognised_as_one(self, literal) -> None:
        assert literal_colours(f"1px solid {literal}")

    def test_every_selector_is_scoped_to_the_page_content(self, stylesheet) -> None:
        selectors = [
            selector.strip()
            for prelude, declared in stylesheet.rules
            for selector in prelude.split(",")
        ]

        assert selectors
        assert [s for s in selectors if not s.startswith(SCOPE)] == []

    @pytest.mark.parametrize("theme", THEMES)
    def test_body_text_is_readable_on_every_admonition(self, stylesheet, theme) -> None:
        own, colours = stylesheet.properties(), ColourMath.theme(theme)
        backgrounds = [
            name
            for name in own
            if name.startswith("--mvp-sphinx-admonition-") and name.endswith("-bg")
        ]
        text = colours["--color-base-content"]

        assert backgrounds
        unreadable = [
            name
            for name in backgrounds
            if ColourMath.contrast(
                text, ColourMath.resolve(f"var({name})", own, colours)
            )
            < MINIMUM_CONTRAST
        ]
        assert unreadable == []

    @pytest.mark.parametrize("theme", THEMES)
    def test_muted_text_is_readable_on_the_page_and_every_admonition(
        self, stylesheet, theme
    ) -> None:
        own, colours = stylesheet.properties(), ColourMath.theme(theme)
        surfaces = ["var(--color-base-100)"] + [
            f"var({name})"
            for name in own
            if name.startswith("--mvp-sphinx-admonition-") and name.endswith("-bg")
        ]

        assert "--mvp-sphinx-muted" in own
        assert len(surfaces) > 1
        muted = ColourMath.resolve("var(--mvp-sphinx-muted)", own, colours)
        unreadable = [
            surface
            for surface in surfaces
            if ColourMath.contrast(muted, ColourMath.resolve(surface, own, colours))
            < MINIMUM_CONTRAST
        ]
        assert unreadable == []


class TestCodeStylesheet:
    SURFACES = ["--mvp-sphinx-code-bg", "--mvp-sphinx-code-emphasis-bg"]
    TOKEN_GROUPS = [
        "comment",
        "keyword",
        "string",
        "number",
        "name",
        "inserted",
        "deleted",
        "error",
    ]

    @staticmethod
    def text_roles(own: dict[str, str]) -> list[str]:
        return [
            name
            for name in own
            if name.startswith("--mvp-sphinx-code-") and not name.endswith("-bg")
        ]

    def test_every_token_group_and_the_line_numbers_have_a_colour(
        self, stylesheet
    ) -> None:
        roles = self.text_roles(stylesheet.properties())

        expected = [f"--mvp-sphinx-code-{group}" for group in self.TOKEN_GROUPS]
        expected += ["--mvp-sphinx-code-text", "--mvp-sphinx-code-line-number"]
        assert set(expected) <= set(roles)

    @pytest.mark.parametrize("theme", THEMES)
    @pytest.mark.parametrize("surface", SURFACES)
    def test_code_text_is_readable_on_the_code_background(
        self, stylesheet, theme, surface
    ) -> None:
        own, colours = stylesheet.properties(), ColourMath.theme(theme)
        background = ColourMath.resolve(f"var({surface})", own, colours)

        roles = self.text_roles(own)
        unreadable = [
            name
            for name in roles
            if ColourMath.contrast(
                ColourMath.resolve(f"var({name})", own, colours), background
            )
            < MINIMUM_CONTRAST
        ]
        assert roles
        assert unreadable == []


class TestSphinxHooks:
    REFERENCE_HOOKS = (
        "sig-object",
        "sig-name",
        "sig-prename",
        "sig-param",
        "default_value",
        "field-list",
        "colon",
        "math",
        "eqno",
    )
    GUIDE_HOOKS = ("viewcode-link", "autosummary", "property", "sig-return-icon")
    NAMED_BY_TAG = {"sig-param": "dt.sig-object em"}

    @staticmethod
    def bodies(build: Path) -> list[BeautifulSoup]:
        return [
            BeautifulSoup(json.loads(page.read_text()).get("body", ""), "html.parser")
            for page in build.rglob("*.fjson")
        ]

    @staticmethod
    def entry(soups: list[BeautifulSoup], entry_id: str):
        found = [soup.find("dt", id=entry_id) for soup in soups]
        return next(each for each in found if each)

    def test_every_hook_is_in_a_selector_of_the_stylesheet(self, stylesheet) -> None:
        selectors = " ".join(selector for selector, declared in stylesheet.rules)

        missing = [
            hook
            for hook in (*self.REFERENCE_HOOKS, *self.GUIDE_HOOKS)
            if hook not in self.NAMED_BY_TAG
            and not re.search(rf"\.{re.escape(hook)}(?![\w-])", selectors)
        ]
        assert missing == []

    def test_a_parameter_is_selected_by_its_tag_in_the_stylesheet(
        self, stylesheet
    ) -> None:
        selectors = [selector for selector, declared in stylesheet.rules]

        assert any(
            selector.strip().endswith(self.NAMED_BY_TAG["sig-param"])
            for prelude in selectors
            for selector in prelude.split(",")
        )

    @pytest.mark.parametrize("build", ["reference_build", "demo_guide_build"])
    def test_every_em_in_a_signature_is_a_parameter(self, request, build) -> None:
        soups = self.bodies(request.getfixturevalue(build))

        emphasised = [
            each for soup in soups for each in soup.select("dt.sig-object em")
        ]
        assert emphasised
        assert [e for e in emphasised if "sig-param" not in e["class"]] == []

    @pytest.mark.parametrize("hook", REFERENCE_HOOKS)
    def test_a_hand_written_hook_is_in_a_page_body_of_the_reference_build(
        self, reference_build, hook
    ) -> None:
        soups = self.bodies(reference_build)

        assert any(soup.select(f".{hook}") for soup in soups)

    @pytest.mark.parametrize("hook", GUIDE_HOOKS)
    def test_a_generated_hook_is_in_a_page_body_of_the_demo_guide_build(
        self, demo_guide_build, hook
    ) -> None:
        soups = self.bodies(demo_guide_build)

        assert any(soup.select(f".{hook}") for soup in soups)

    def test_another_languages_entry_is_drawn_as_a_signature_with_a_name(
        self, reference_build
    ) -> None:
        entry = self.entry(self.bodies(reference_build), "buildAddress")

        assert "sig-object" in entry["class"]
        assert entry.select_one(".sig-name")

    @pytest.mark.parametrize(
        "entry_id", ["demo.links.page_address", "demo.links.NotAGuideAddress"]
    )
    def test_a_hand_written_and_a_generated_entry_carry_the_same_classes(
        self, reference_build, demo_guide_build, entry_id
    ) -> None:
        written = self.entry(self.bodies(reference_build), entry_id)
        generated = self.entry(self.bodies(demo_guide_build), entry_id)

        assert set(written["class"]) == set(generated["class"])


class TestReferenceStylesheet:
    @staticmethod
    def colours(stylesheet: Stylesheet, hook: str) -> list[tuple[str, str]]:
        return [
            (selector, declared["color"])
            for selector, declared in stylesheet.rules
            if hook in selector
            and "color" in declared
            and declared["color"] != "inherit"
        ]

    @pytest.mark.parametrize("theme", THEMES)
    def test_signature_text_is_readable_on_the_code_background(
        self, stylesheet, theme
    ) -> None:
        own, colours = stylesheet.properties(), ColourMath.theme(theme)
        background = ColourMath.resolve("var(--mvp-sphinx-code-bg)", own, colours)

        rules = self.colours(stylesheet, "sig-object")
        unreadable = [
            selector
            for selector, value in rules
            if ColourMath.contrast(ColourMath.resolve(value, own, colours), background)
            < MINIMUM_CONTRAST
        ]
        assert rules
        assert unreadable == []

    @pytest.mark.parametrize("theme", THEMES)
    def test_field_list_text_is_readable_on_the_page_and_every_admonition(
        self, stylesheet, theme
    ) -> None:
        own, colours = stylesheet.properties(), ColourMath.theme(theme)
        surfaces = ["var(--color-base-100)"] + [
            f"var({name})"
            for name in own
            if name.startswith("--mvp-sphinx-admonition-") and name.endswith("-bg")
        ]

        rules = self.colours(stylesheet, "field-list")
        unreadable = [
            (selector, surface)
            for selector, value in rules
            for surface in surfaces
            if ColourMath.contrast(
                ColourMath.resolve(value, own, colours),
                ColourMath.resolve(surface, own, colours),
            )
            < MINIMUM_CONTRAST
        ]
        assert rules
        assert len(surfaces) > 1
        assert unreadable == []
