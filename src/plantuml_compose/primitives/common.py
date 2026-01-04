"""Common primitives shared across all diagram types.

All types here are frozen dataclasses - immutable data with no behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal


class Direction(Enum):
    """Layout direction hints for arrows and elements."""

    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


class LinePattern(Enum):
    """Line/arrow pattern styles."""

    SOLID = "solid"
    DASHED = "dashed"
    DOTTED = "dotted"
    HIDDEN = "hidden"


class NotePosition(Enum):
    """Note positioning options (superset - validated per diagram type)."""

    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"
    OVER = "over"  # Sequence: spans participants
    ACROSS = "across"  # Sequence: all participants
    ON_LINK = "on link"  # On a connection
    FLOATING = "floating"  # Detached


@dataclass(frozen=True)
class Color:
    """Immutable color value.

    Use factory methods for construction:
        Color.named("red")
        Color.hex("#FF0000")
        Color.rgb(255, 0, 0)
    """

    value: str

    @classmethod
    def named(cls, name: str) -> Color:
        """Create a named color (e.g., 'red', 'LightBlue')."""
        return cls(name)

    @classmethod
    def hex(cls, code: str) -> Color:
        """Create a hex color (e.g., '#FF0000' or 'FF0000')."""
        if not code.startswith("#"):
            code = f"#{code}"
        return cls(code)

    @classmethod
    def rgb(cls, r: int, g: int, b: int) -> Color:
        """Create a color from RGB values (0-255)."""
        return cls(f"#{r:02X}{g:02X}{b:02X}")

    @classmethod
    def rgba(cls, r: int, g: int, b: int, a: int) -> Color:
        """Create a color from RGBA values (0-255). Alpha is first in PlantUML."""
        return cls(f"#{a:02X}{r:02X}{g:02X}{b:02X}")


@dataclass(frozen=True)
class Gradient:
    """Two-color gradient.

    Direction determines the separator character in PlantUML:
        horizontal: | (red|green)
        vertical: - (red-green)
        diagonal_down: / (red/green)
        diagonal_up: \\ (red\\green)
    """

    start: Color
    end: Color
    direction: Literal["horizontal", "vertical", "diagonal_down", "diagonal_up"] = (
        "horizontal"
    )


@dataclass(frozen=True)
class LineStyle:
    """Visual styling for lines and arrows."""

    pattern: LinePattern = LinePattern.SOLID
    color: Color | None = None
    thickness: int | None = None
    bold: bool = False


@dataclass(frozen=True)
class Label:
    """Text label with optional markup.

    PlantUML supports Creole and HTML markup in labels.
    We pass through as-is without validation.
    """

    text: str


@dataclass(frozen=True)
class Spot:
    """Stereotype spot - a colored circle with a single character.

    Renders as: << (S,#red) StereoName >>
    """

    char: str
    color: Color


@dataclass(frozen=True)
class Stereotype:
    """Stereotype marker for UML elements.

    Can include an optional spot (colored character circle).
    """

    name: str
    spot: Spot | None = None


@dataclass(frozen=True)
class Style:
    """Visual styling that can apply to any element."""

    background: Color | Gradient | None = None
    line: LineStyle | None = None
    text_color: Color | None = None
    stereotype: Stereotype | None = None


@dataclass(frozen=True)
class Note:
    """Annotation that can be attached to elements."""

    content: Label
    position: NotePosition = NotePosition.RIGHT
