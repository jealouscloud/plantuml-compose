"""Common primitives shared across all diagram types.

All types here are frozen dataclasses - immutable data with no behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal, TypeAlias, get_args

# All color names supported by PlantUML (extracted via test_codegen.py)
# fmt: off
PlantUMLColor = Literal[
    "AliceBlue", "AntiqueWhite", "Aqua", "Aquamarine", "Azure", "Beige", "Bisque",
    "Black", "BlanchedAlmond", "Blue", "BlueViolet", "Brown", "BurlyWood",
    "CadetBlue", "Chartreuse", "Chocolate", "Coral", "CornflowerBlue", "Cornsilk",
    "Crimson", "Cyan", "DarkBlue", "DarkCyan", "DarkGoldenRod", "DarkGray",
    "DarkGreen", "DarkGrey", "DarkKhaki", "DarkMagenta", "DarkOliveGreen",
    "DarkOrchid", "DarkRed", "DarkSalmon", "DarkSeaGreen", "DarkSlateBlue",
    "DarkSlateGray", "DarkSlateGrey", "DarkTurquoise", "DarkViolet", "Darkorange",
    "DeepPink", "DeepSkyBlue", "DimGray", "DimGrey", "DodgerBlue", "FireBrick",
    "FloralWhite", "ForestGreen", "Fuchsia", "Gainsboro", "GhostWhite", "Gold",
    "GoldenRod", "Gray", "Green", "GreenYellow", "Grey", "HoneyDew", "HotPink",
    "IndianRed", "Indigo", "Ivory", "Khaki", "Lavender", "LavenderBlush",
    "LawnGreen", "LemonChiffon", "LightBlue", "LightCoral", "LightCyan",
    "LightGoldenRodYellow", "LightGray", "LightGreen", "LightGrey", "LightPink",
    "LightSalmon", "LightSeaGreen", "LightSkyBlue", "LightSlateGray",
    "LightSlateGrey", "LightSteelBlue", "LightYellow", "Lime", "LimeGreen",
    "Linen", "Magenta", "Maroon", "MediumAquaMarine", "MediumBlue", "MediumOrchid",
    "MediumPurple", "MediumSeaGreen", "MediumSlateBlue", "MediumSpringGreen",
    "MediumTurquoise", "MediumVioletRed", "MidnightBlue", "MintCream", "MistyRose",
    "Moccasin", "NavajoWhite", "Navy", "OldLace", "Olive", "OliveDrab", "Orange",
    "OrangeRed", "Orchid", "PaleGoldenRod", "PaleGreen", "PaleTurquoise",
    "PaleVioletRed", "PapayaWhip", "PeachPuff", "Peru", "Pink", "Plum",
    "PowderBlue", "Purple", "Red", "RosyBrown", "RoyalBlue", "SaddleBrown",
    "Salmon", "SandyBrown", "SeaGreen", "SeaShell", "Sienna", "Silver", "SkyBlue",
    "SlateBlue", "SlateGray", "SlateGrey", "Snow", "SpringGreen", "SteelBlue",
    "Tan", "Teal", "Thistle", "Tomato", "Turquoise", "Violet", "Wheat", "White",
    "WhiteSmoke", "Yellow", "YellowGreen",
]
# fmt: on


# Layout direction hints for arrows and elements
Direction = Literal["up", "down", "left", "right"]


# Line/arrow pattern styles
LinePattern = Literal["solid", "dashed", "dotted", "hidden"]


# Note positioning options (superset - validated per diagram type)
NotePosition = Literal["left", "right", "top", "bottom", "over", "across", "on link", "floating"]


# Separator style for concurrent regions in state diagrams
# "horizontal" stacks regions vertically (--), "vertical" arranges side-by-side (||)
RegionSeparator = Literal["horizontal", "vertical"]


# Font style options
FontStyle = Literal["normal", "bold", "italic", "bold italic"]


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


# Type alias for color arguments - accepts Color objects or strings
ColorLike: TypeAlias = Color | PlantUMLColor | str


def coerce_color(value: ColorLike) -> Color:
    """Convert a ColorLike value to a Color object.

    Args:
        value: Color object, PlantUML color name, or hex string

    Returns:
        Color object

    Examples:
        coerce_color(Color.named("red"))  # passthrough
        coerce_color("red")                # -> Color.named("red")
        coerce_color("#FF0000")            # -> Color.hex("#FF0000")
    """
    if isinstance(value, Color):
        return value
    if value.startswith("#"):
        return Color.hex(value)
    return Color.named(value)


@dataclass(frozen=True)
class Gradient:
    """Two-color gradient.

    Direction determines the separator character in PlantUML:
        horizontal: | (red|green)
        vertical: - (red-green)
        diagonal_down: / (red/green)
        diagonal_up: \\ (red\\green)
    """

    start: ColorLike
    end: ColorLike
    direction: Literal["horizontal", "vertical", "diagonal_down", "diagonal_up"] = (
        "horizontal"
    )


@dataclass(frozen=True)
class LineStyle:
    """Visual styling for lines and arrows."""

    pattern: LinePattern = "solid"
    color: ColorLike | None = None
    thickness: int | None = None
    bold: bool = False


@dataclass(frozen=True)
class Label:
    """Text label with optional markup.

    PlantUML supports Creole and HTML markup in labels.
    We pass through as-is without validation.
    """

    text: str


# Type alias for label arguments - accepts Label objects or strings
LabelLike: TypeAlias = Label | str


@dataclass(frozen=True)
class Spot:
    """Stereotype spot - a colored circle with a single character.

    Renders as: << (S,#red) StereoName >>
    """

    char: str
    color: ColorLike


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

    background: ColorLike | Gradient | None = None
    line: "LineStyleLike | None" = None
    text_color: ColorLike | None = None
    stereotype: Stereotype | None = None


@dataclass(frozen=True)
class Note:
    """Annotation that can be attached to elements."""

    content: LabelLike
    position: NotePosition = "right"


@dataclass(frozen=True)
class ElementStyle:
    """Style properties for diagram elements (states, notes, etc.).

    Used within StateDiagramStyle to define element-specific styling.
    """

    background: ColorLike | None = None
    line_color: ColorLike | None = None
    font_color: ColorLike | None = None
    font_name: str | None = None
    font_size: int | None = None
    font_style: FontStyle | None = None
    round_corner: int | None = None
    line_thickness: int | None = None


@dataclass(frozen=True)
class DiagramArrowStyle:
    """Style properties for arrows in diagram-wide styles.

    Note: This is different from LineStyle which is for individual arrows.
    This is for the <style> block's arrow { } section.
    """

    line_color: ColorLike | None = None
    line_thickness: int | None = None
    line_pattern: LinePattern | None = None


@dataclass(frozen=True)
class StateDiagramStyle:
    """Typed CSS-like style for state diagrams.

    Usage:
        with state_diagram(
            style=StateDiagramStyle(
                background="white",
                font_name="Arial",
                state=ElementStyle(
                    background="#E3F2FD",
                    line_color="#1976D2",
                ),
                arrow=DiagramArrowStyle(
                    line_color="#757575",
                ),
            )
        ) as d:
            ...

    Generates:
        <style>
        stateDiagram {
            BackgroundColor white
            FontName Arial
            state {
                BackgroundColor #E3F2FD
                LineColor #1976D2
            }
            arrow {
                LineColor #757575
            }
        }
        </style>
    """

    # Root-level properties
    background: ColorLike | Gradient | None = None
    font_name: str | None = None
    font_size: int | None = None
    font_color: ColorLike | None = None

    # Element-specific styles
    state: ElementStyle | None = None
    arrow: DiagramArrowStyle | None = None
    note: ElementStyle | None = None
    title: ElementStyle | None = None


# TypedDict for dict-style LineStyle specification
from typing import TypedDict


class LineStyleDict(TypedDict, total=False):
    """Dict form of LineStyle for convenience.

    Example:
        d.arrow(a, b, style={"color": "red", "pattern": "dashed"})
    """

    pattern: LinePattern
    color: ColorLike
    thickness: int
    bold: bool


# Type alias for line style arguments
LineStyleLike: TypeAlias = LineStyle | LineStyleDict


def coerce_line_style(value: LineStyleLike) -> LineStyle:
    """Convert a LineStyleLike value to a LineStyle object."""
    if isinstance(value, LineStyle):
        return value
    return LineStyle(
        pattern=value.get("pattern", "solid"),
        color=coerce_color(value["color"]) if "color" in value else None,
        thickness=value.get("thickness"),
        bold=value.get("bold", False),
    )


class StyleDict(TypedDict, total=False):
    """Dict form of Style for convenience.

    Example:
        d.state("Error", style={"background": "#FFCDD2", "text_color": "red"})
    """

    background: ColorLike
    line: LineStyleLike
    text_color: ColorLike
    stereotype: Stereotype


# Type alias for style arguments
StyleLike: TypeAlias = Style | StyleDict


def coerce_style(value: StyleLike) -> Style:
    """Convert a StyleLike value to a Style object."""
    if isinstance(value, Style):
        return value
    return Style(
        background=coerce_color(value["background"]) if "background" in value else None,
        line=coerce_line_style(value["line"]) if "line" in value else None,
        text_color=coerce_color(value["text_color"]) if "text_color" in value else None,
        stereotype=value.get("stereotype"),
    )


class ElementStyleDict(TypedDict, total=False):
    """Dict form of ElementStyle for convenience.

    Example:
        state={"background": "#E3F2FD", "line_color": "#1976D2", "round_corner": 5}
    """

    background: ColorLike
    line_color: ColorLike
    font_color: ColorLike
    font_name: str
    font_size: int
    font_style: FontStyle
    round_corner: int
    line_thickness: int


# Type alias for element style arguments
ElementStyleLike: TypeAlias = ElementStyle | ElementStyleDict


def coerce_element_style(value: ElementStyleLike) -> ElementStyle:
    """Convert an ElementStyleLike value to an ElementStyle object."""
    if isinstance(value, ElementStyle):
        return value
    return ElementStyle(
        background=coerce_color(value["background"]) if "background" in value else None,
        line_color=coerce_color(value["line_color"]) if "line_color" in value else None,
        font_color=coerce_color(value["font_color"]) if "font_color" in value else None,
        font_name=value.get("font_name"),
        font_size=value.get("font_size"),
        font_style=value.get("font_style"),
        round_corner=value.get("round_corner"),
        line_thickness=value.get("line_thickness"),
    )


class DiagramArrowStyleDict(TypedDict, total=False):
    """Dict form of DiagramArrowStyle for convenience.

    Example:
        arrow={"line_color": "#757575", "line_thickness": 2}
    """

    line_color: ColorLike
    line_thickness: int
    line_pattern: LinePattern


# Type alias for diagram arrow style arguments
DiagramArrowStyleLike: TypeAlias = DiagramArrowStyle | DiagramArrowStyleDict


def coerce_diagram_arrow_style(value: DiagramArrowStyleLike) -> DiagramArrowStyle:
    """Convert a DiagramArrowStyleLike value to a DiagramArrowStyle object."""
    if isinstance(value, DiagramArrowStyle):
        return value
    return DiagramArrowStyle(
        line_color=coerce_color(value["line_color"]) if "line_color" in value else None,
        line_thickness=value.get("line_thickness"),
        line_pattern=value.get("line_pattern"),
    )


class StateDiagramStyleDict(TypedDict, total=False):
    """Dict form of StateDiagramStyle for convenience.

    Example:
        with state_diagram(
            style={
                "background": "white",
                "font_name": "Arial",
                "state": {"background": "#E3F2FD", "line_color": "#1976D2"},
                "arrow": {"line_color": "#757575"},
            }
        ) as d:
            ...
    """

    background: ColorLike
    font_name: str
    font_size: int
    font_color: ColorLike
    state: ElementStyleLike
    arrow: DiagramArrowStyleLike
    note: ElementStyleLike
    title: ElementStyleLike


# Type alias for state diagram style arguments
StateDiagramStyleLike: TypeAlias = StateDiagramStyle | StateDiagramStyleDict


def coerce_state_diagram_style(value: StateDiagramStyleLike) -> StateDiagramStyle:
    """Convert a StateDiagramStyleLike value to a StateDiagramStyle object."""
    if isinstance(value, StateDiagramStyle):
        return value
    return StateDiagramStyle(
        background=coerce_color(value["background"]) if "background" in value else None,
        font_name=value.get("font_name"),
        font_size=value.get("font_size"),
        font_color=coerce_color(value["font_color"]) if "font_color" in value else None,
        state=coerce_element_style(value["state"]) if "state" in value else None,
        arrow=coerce_diagram_arrow_style(value["arrow"]) if "arrow" in value else None,
        note=coerce_element_style(value["note"]) if "note" in value else None,
        title=coerce_element_style(value["title"]) if "title" in value else None,
    )
