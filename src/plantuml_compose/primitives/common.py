"""Common primitives shared across all diagram types.

This module contains the foundational types used throughout plantuml-compose:

- **Colors**: Named colors (e.g., "red", "LightBlue"), hex codes ("#FF0000"),
  RGB values, and gradients for backgrounds and lines.

- **Labels**: Text content that can include PlantUML's Creole markup or HTML
  formatting for rich text in diagrams.

- **Styles**: Visual properties like background colors, line patterns (solid,
  dashed, dotted), and text styling that can be applied to diagram elements.

- **Notes**: Annotations that can be attached to elements or float freely
  in the diagram.

- **Stereotypes**: UML markers (shown as <<name>>) that classify elements,
  optionally with a colored "spot" character.

All types are frozen dataclasses - immutable data containers with no behavior.
This ensures diagrams are built from pure, predictable data structures.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypeAlias, TypedDict

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
NotePosition = Literal[
    "left", "right", "top", "bottom", "over", "across", "on link", "floating"
]


# Separator style for concurrent regions in state diagrams
# "horizontal" stacks regions vertically (--), "vertical" arranges side-by-side (||)
RegionSeparator = Literal["horizontal", "vertical"]


# Font style options
FontStyle = Literal["normal", "bold", "italic", "bold italic"]


@dataclass(frozen=True)
class Color:
    """Immutable color value for styling diagram elements.

    Colors can specify backgrounds, lines, text, and other visual properties.
    PlantUML supports named colors (CSS color names), hex codes, and RGB values.

    For convenience, most APIs accept plain strings ("red", "#FF0000") which
    are automatically converted to Color objects. Use factory methods when
    you need explicit construction:

        Color.named("red")       # CSS color name
        Color.hex("#FF0000")     # Hex code (with or without #)
        Color.rgb(255, 0, 0)     # RGB components (0-255 each)
        Color.rgba(255, 0, 0, 128)  # RGBA with transparency
    """

    value: str

    @classmethod
    def named(cls, name: str) -> Color:
        """Create from a CSS color name.

        PlantUML supports standard web colors like "red", "LightBlue",
        "DarkSlateGray", etc. Names are case-insensitive in PlantUML.
        """
        return cls(name)

    @classmethod
    def hex(cls, code: str) -> Color:
        """Create from a hex color code.

        Accepts with or without leading "#": "#FF0000" or "FF0000".
        The "#" prefix is normalized automatically.
        """
        if not code.startswith("#"):
            code = f"#{code}"
        return cls(code)

    @classmethod
    def rgb(cls, r: int, g: int, b: int) -> Color:
        """Create from RGB components.

        Each component is an integer from 0-255.
        """
        return cls(f"#{r:02X}{g:02X}{b:02X}")

    @classmethod
    def rgba(cls, r: int, g: int, b: int, a: int) -> Color:
        """Create from RGBA components with transparency.

        Each component is an integer from 0-255. Alpha 0 is fully transparent,
        255 is fully opaque. Note: PlantUML encodes alpha first (#AARRGGBB).
        """
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


def _coerce_color_or_gradient(
    value: ColorLike | Gradient | None,
) -> Color | Gradient | None:
    """Normalize dict inputs that may include Gradient objects."""
    if value is None:
        return None
    if isinstance(value, Gradient):
        return value
    return coerce_color(value)


@dataclass(frozen=True)
class Gradient:
    """Two-color gradient for element backgrounds.

    Gradients blend smoothly from a start color to an end color. The direction
    controls the angle of the blend:

        horizontal:    Left to right (|)
        vertical:      Top to bottom (-)
        diagonal_down: Top-left to bottom-right (/)
        diagonal_up:   Bottom-left to top-right (\\)

    Example:
        # Blue fading to white from left to right
        style={"background": Gradient("Blue", "White", "horizontal")}
    """

    start: ColorLike
    end: ColorLike
    direction: Literal[
        "horizontal", "vertical", "diagonal_down", "diagonal_up"
    ] = "horizontal"


@dataclass(frozen=True)
class LineStyle:
    """Visual styling for lines and arrows connecting elements.

    Controls how connection lines appear in the diagram:

        pattern:   Line pattern - "solid", "dashed", "dotted", or "hidden"
        color:     Line color (any ColorLike value)
        thickness: Line width in pixels
        bold:      If True, renders a thicker line

    Example:
        # Red dashed arrow
        d.transition(a, b, style=LineStyle(pattern="dashed", color="red"))
    """

    pattern: LinePattern = "solid"
    color: ColorLike | None = None
    thickness: int | None = None
    bold: bool = False


@dataclass(frozen=True)
class Label:
    """Text content for diagram elements, titles, and annotations.

    Labels can contain plain text or rich formatting using PlantUML's
    Creole markup or HTML subset:

        **bold**           Bold text
        //italic//         Italic text
        __underline__      Underlined text
        ~~strikethrough~~  Strikethrough text
        <color:red>text</color>  Colored text
        <size:18>text</size>     Sized text

    For simple text, you can pass strings directly to most APIs - they're
    automatically wrapped in Label objects.
    """

    text: str


# Type alias for label arguments - accepts Label objects or strings
LabelLike: TypeAlias = Label | str


@dataclass(frozen=True)
class Spot:
    """A colored circle with a single character, displayed in stereotypes.

    Spots appear as small colored circles with a letter inside, placed
    before the stereotype name. They provide quick visual classification.

    Renders as: << (S,#red) StereoName >>

    Example:
        # Service stereotype with blue "S" indicator
        Spot("S", "DodgerBlue")
    """

    char: str
    color: ColorLike


@dataclass(frozen=True)
class Stereotype:
    """UML stereotype marker that classifies diagram elements.

    In UML, stereotypes are shown as <<name>> and indicate that an element
    belongs to a particular category or has special semantics. Common examples:
    <<interface>>, <<abstract>>, <<service>>, <<entity>>.

    Stereotypes can optionally include a "spot" - a colored circle with a
    single character that provides quick visual identification.

    Example:
        # Simple stereotype
        Stereotype("service")

        # Stereotype with colored spot
        Stereotype("service", Spot("S", "DodgerBlue"))
    """

    name: str
    spot: Spot | None = None


@dataclass(frozen=True)
class Style:
    """Visual styling that can apply to any diagram element.

    Combines multiple visual properties into a single style specification:

        background:  Fill color or gradient for the element
        line:        Styling for the element's border/outline
        text_color:  Color for text within the element
        stereotype:  UML stereotype marker (<<name>>)

    Example:
        # Error state with red background and border
        d.state("Error", style=Style(
            background="#FFCDD2",
            line=LineStyle(color="red"),
            text_color="DarkRed",
        ))
    """

    background: ColorLike | Gradient | None = None
    line: "LineStyleLike | None" = None
    text_color: ColorLike | None = None
    stereotype: Stereotype | None = None


@dataclass(frozen=True)
class Note:
    """Annotation that can be attached to diagram elements.

    Notes appear as yellow sticky-note boxes containing explanatory text.
    They can be positioned relative to an element or float freely.

    Position options vary by diagram type but commonly include:
        left, right:  Beside an element
        top, bottom:  Above or below an element
        floating:     Not attached to any specific element

    The content can include Creole markup for rich text formatting.
    """

    content: LabelLike
    position: NotePosition = "right"


# =============================================================================
# Common Diagram Metadata (header, footer, caption, legend, scale)
# =============================================================================

# Header/Footer positioning
HeaderPosition = Literal["left", "center", "right"]

# Legend positioning
LegendPosition = Literal["left", "right", "top", "bottom", "center"]


@dataclass(frozen=True)
class Header:
    """Diagram header text displayed at the top margin.

    The header appears above the diagram content but within the rendered image.
    Supports multiline text and Creole markup.

        content:  Header text (can include Creole markup)
        position: Horizontal alignment ("left", "center", "right")
    """

    content: LabelLike
    position: HeaderPosition = "center"


@dataclass(frozen=True)
class Footer:
    """Diagram footer text displayed at the bottom margin.

    The footer appears below the diagram content but within the rendered image.
    Supports multiline text and Creole markup. Can include special variables
    like %page% and %lastpage% for page numbering.

        content:  Footer text (can include Creole markup)
        position: Horizontal alignment ("left", "center", "right")
    """

    content: LabelLike
    position: HeaderPosition = "center"


@dataclass(frozen=True)
class Legend:
    """A bordered legend box for diagram annotations.

    Legends are bordered boxes that can contain explanatory text, typically
    used for diagram keys or additional context. Supports multiline text
    and Creole markup.

        content:  Legend text (can include Creole markup)
        position: Where to place the legend relative to the diagram
    """

    content: LabelLike
    position: LegendPosition = "right"


@dataclass(frozen=True)
class Scale:
    """Diagram zoom/scale factor.

    Controls the output size of the rendered diagram. Only one scaling
    method should be specified:

        factor:     Multiply diagram size (e.g., 1.5, 0.5, 2/3)
        width:      Set exact width in pixels
        height:     Set exact height in pixels
        max_width:  Set maximum width (diagram scales down if needed)
        max_height: Set maximum height (diagram scales down if needed)

    For exact dimensions, use width/height. For proportional scaling that
    respects aspect ratio, use max_width/max_height.
    """

    factor: float | None = None
    width: int | None = None
    height: int | None = None
    max_width: int | None = None
    max_height: int | None = None


@dataclass(frozen=True)
class ElementStyle:
    """Comprehensive style properties for diagram elements.

    Used in diagram-wide style blocks to define default appearance for
    element types (states, notes, etc.). These properties map to PlantUML's
    CSS-like <style> block syntax.

        background:     Fill color
        line_color:     Border/outline color
        font_color:     Text color
        font_name:      Font family (e.g., "Arial", "Courier")
        font_size:      Font size in points
        font_style:     "normal", "bold", "italic", or "bold italic"
        round_corner:   Corner radius in pixels (0 for sharp corners)
        line_thickness: Border width in pixels
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
    """Style properties for all arrows in a diagram.

    Used in diagram-wide style blocks to set default arrow appearance.
    This affects transitions, relationships, and other connecting lines.

    Note: For styling individual arrows, use LineStyle on specific
    transitions. This class is for the <style> block's arrow { } section
    that sets diagram-wide defaults.
    """

    line_color: ColorLike | None = None
    line_thickness: int | None = None
    line_pattern: LinePattern | None = None


@dataclass(frozen=True)
class StateDiagramStyle:
    """Diagram-wide styling for state diagrams.

    This generates a PlantUML <style> block that sets default appearance
    for all elements in the diagram. Individual elements can still override
    these defaults with inline styles.

    Root-level properties apply to the diagram background and default fonts.
    Element-specific properties (state, arrow, note, title) let you style
    each element type independently.

    Example:
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

    This generates a <style> block in the PlantUML output that themes
    all states with blue backgrounds and gray arrows.
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

    background: ColorLike | Gradient
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
        background=_coerce_color_or_gradient(value.get("background")),
        line=coerce_line_style(value["line"]) if "line" in value else None,
        text_color=coerce_color(value["text_color"])
        if "text_color" in value
        else None,
        stereotype=value.get("stereotype"),
    )


def validate_style_background_only(
    style: StyleLike | None, element_type: str
) -> Style | None:
    """Coerce and validate that only background is set in style.

    Some diagram elements only support background color styling. This function
    validates that unsupported style properties are not provided.

    Args:
        style: The style to validate (dict or Style object)
        element_type: Name of the element type for error messages

    Returns:
        Coerced Style object or None

    Raises:
        ValueError: If unsupported style properties are provided
    """
    if style is None:
        return None

    style_obj = coerce_style(style)

    unsupported = []
    if style_obj.line is not None:
        unsupported.append("line")
    if style_obj.text_color is not None:
        unsupported.append("text_color")
    if style_obj.stereotype is not None:
        unsupported.append("stereotype")

    if unsupported:
        raise ValueError(
            f"{element_type} only supports 'background' styling. "
            f"Unsupported properties: {', '.join(unsupported)}"
        )

    return style_obj


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
        background=coerce_color(value["background"])
        if "background" in value
        else None,
        line_color=coerce_color(value["line_color"])
        if "line_color" in value
        else None,
        font_color=coerce_color(value["font_color"])
        if "font_color" in value
        else None,
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


def coerce_diagram_arrow_style(
    value: DiagramArrowStyleLike,
) -> DiagramArrowStyle:
    """Convert a DiagramArrowStyleLike value to a DiagramArrowStyle object."""
    if isinstance(value, DiagramArrowStyle):
        return value
    return DiagramArrowStyle(
        line_color=coerce_color(value["line_color"])
        if "line_color" in value
        else None,
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

    background: ColorLike | Gradient
    font_name: str
    font_size: int
    font_color: ColorLike
    state: ElementStyleLike
    arrow: DiagramArrowStyleLike
    note: ElementStyleLike
    title: ElementStyleLike


# Type alias for state diagram style arguments
StateDiagramStyleLike: TypeAlias = StateDiagramStyle | StateDiagramStyleDict


def coerce_state_diagram_style(
    value: StateDiagramStyleLike,
) -> StateDiagramStyle:
    """Convert a StateDiagramStyleLike value to a StateDiagramStyle object."""
    if isinstance(value, StateDiagramStyle):
        return value
    return StateDiagramStyle(
        background=_coerce_color_or_gradient(value.get("background")),
        font_name=value.get("font_name"),
        font_size=value.get("font_size"),
        font_color=coerce_color(value["font_color"])
        if "font_color" in value
        else None,
        state=coerce_element_style(value["state"])
        if "state" in value
        else None,
        arrow=coerce_diagram_arrow_style(value["arrow"])
        if "arrow" in value
        else None,
        note=coerce_element_style(value["note"]) if "note" in value else None,
        title=coerce_element_style(value["title"])
        if "title" in value
        else None,
    )


# ---------------------------------------------------------------------------
# Component Diagram Styling
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ComponentDiagramStyle:
    """Diagram-wide styling for component diagrams.

    This generates a PlantUML <style> block that sets default appearance
    for all elements in the diagram. Individual elements can still override
    these defaults with inline styles.

    Root-level properties apply to the diagram background and default fonts.
    Element-specific properties (component, interface, arrow, note, title)
    let you style each element type independently.

    Example:
        with component_diagram(
            style=ComponentDiagramStyle(
                background="white",
                font_name="Arial",
                component=ElementStyle(
                    background="#E3F2FD",
                    line_color="#1976D2",
                ),
                arrow=DiagramArrowStyle(
                    line_color="#757575",
                ),
            )
        ) as d:
            ...

    This generates a <style> block in the PlantUML output that themes
    all components with blue backgrounds and gray arrows.
    """

    # Root-level properties
    background: ColorLike | Gradient | None = None
    font_name: str | None = None
    font_size: int | None = None
    font_color: ColorLike | None = None

    # Element-specific styles
    component: ElementStyle | None = None
    interface: ElementStyle | None = None
    arrow: DiagramArrowStyle | None = None
    note: ElementStyle | None = None
    title: ElementStyle | None = None


class ComponentDiagramStyleDict(TypedDict, total=False):
    """Dict form of ComponentDiagramStyle for convenience.

    Example:
        with component_diagram(
            style={
                "background": "white",
                "font_name": "Arial",
                "component": {"background": "#E3F2FD", "line_color": "#1976D2"},
                "arrow": {"line_color": "#757575"},
            }
        ) as d:
            ...
    """

    background: ColorLike | Gradient
    font_name: str
    font_size: int
    font_color: ColorLike
    component: ElementStyleLike
    interface: ElementStyleLike
    arrow: DiagramArrowStyleLike
    note: ElementStyleLike
    title: ElementStyleLike


# Type alias for component diagram style arguments
ComponentDiagramStyleLike: TypeAlias = ComponentDiagramStyle | ComponentDiagramStyleDict


def coerce_component_diagram_style(
    value: ComponentDiagramStyleLike,
) -> ComponentDiagramStyle:
    """Convert a ComponentDiagramStyleLike value to a ComponentDiagramStyle object."""
    if isinstance(value, ComponentDiagramStyle):
        return value
    return ComponentDiagramStyle(
        background=_coerce_color_or_gradient(value.get("background")),
        font_name=value.get("font_name"),
        font_size=value.get("font_size"),
        font_color=coerce_color(value["font_color"])
        if "font_color" in value
        else None,
        component=coerce_element_style(value["component"])
        if "component" in value
        else None,
        interface=coerce_element_style(value["interface"])
        if "interface" in value
        else None,
        arrow=coerce_diagram_arrow_style(value["arrow"])
        if "arrow" in value
        else None,
        note=coerce_element_style(value["note"]) if "note" in value else None,
        title=coerce_element_style(value["title"])
        if "title" in value
        else None,
    )
