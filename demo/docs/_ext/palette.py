"""A small module documented on the API page, to show how autodoc output is drawn.

Nothing here is part of the theme.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

# The order is the order the API page documents them in.
__all__ = ["Mode", "Colour", "Palette", "contrast_ratio", "DEFAULT_THEMES"]  # noqa: RUF022

#: The themes the picker offers when none are named.
DEFAULT_THEMES: tuple[str, ...] = ("light", "dark")


class Mode(Enum):
    """Whether a theme is for light or dark surroundings."""

    LIGHT = "light"
    """A light background with dark text."""
    DARK = "dark"
    """A dark background with light text."""


@dataclass(frozen=True)
class Colour:
    """A colour in the OKLCH space.

    :param lightness: Perceived lightness, from 0 to 1.
    :param chroma: How colourful it is, from 0 upwards.
    :param hue: The hue angle in degrees.
    """

    lightness: float
    chroma: float
    hue: float

    def css(self) -> str:
        """Return the colour as a CSS ``oklch()`` value.

        >>> Colour(0.55, 0.2, 280).css()
        'oklch(55.0% 0.2 280)'
        """
        return f"oklch({self.lightness * 100:.1f}% {self.chroma} {self.hue})"


@dataclass
class Palette:
    """A named set of colours, as one daisyUI theme defines them.

    Args:
        name: The theme's name, as used in ``data-theme``.
        mode: Whether the theme is light or dark.
        colours: Colours by token name, such as ``"primary"``.

    Example:
        >>> palette = Palette("brand", Mode.LIGHT)
        >>> palette.add("primary", Colour(0.55, 0.2, 280))
    """

    name: str
    mode: Mode = Mode.LIGHT
    colours: dict[str, Colour] = field(default_factory=dict)

    def add(self, token: str, colour: Colour) -> None:
        """Set the colour for one token.

        Args:
            token: The token's name without the ``--color-`` prefix.
            colour: The colour to use.

        Raises:
            ValueError: If the token's name is empty.
        """
        if not token:
            raise ValueError("A token needs a name.")
        self.colours[token] = colour

    def to_css(self) -> str:
        """Return the palette as a CSS rule for its ``data-theme`` selector.

        Returns:
            One rule, setting a ``--color-*`` variable for each token.
        """
        decls = " ".join(f"--color-{k}: {v.css()};" for k, v in self.colours.items())
        return f'[data-theme="{self.name}"] {{ {decls} }}'

    @property
    def is_dark(self) -> bool:
        """Whether the palette is for dark mode."""
        return self.mode is Mode.DARK


def contrast_ratio(
    foreground: Colour, background: Colour, *, large_text: bool = False
) -> float:
    """Estimate the contrast between two colours from their lightness.

    A rough estimate for checking a palette, not a WCAG measurement.

    Args:
        foreground: The text colour.
        background: The colour behind the text.
        large_text: Whether the text is large, which needs less contrast.

    Returns:
        A ratio from 1 to 21.
    """
    high, low = sorted((foreground.lightness, background.lightness), reverse=True)
    ratio: float = (high**2.2 + 0.05) / (low**2.2 + 0.05)
    return round(ratio, 2)
