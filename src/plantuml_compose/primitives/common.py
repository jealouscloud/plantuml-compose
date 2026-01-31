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
from typing import Any, Literal, TypeAlias, TypedDict, get_args


def validate_literal_type(
    value: str, literal_type: Any, param_name: str
) -> str:
    """Validate a value against a Literal type using get_args().

    This extracts valid values from the Literal type definition, ensuring
    the validation stays in sync with the type hint automatically.

    Args:
        value: The value to validate
        literal_type: The Literal type (e.g., Literal["a", "b", "c"])
        param_name: Name of the parameter for error messages

    Returns:
        The validated value

    Raises:
        ValueError: If value is not one of the Literal's allowed values

    Example:
        ForkEndStyle = Literal["fork", "merge", "or", "and"]
        validate_literal_type("fork", ForkEndStyle, "end_style")  # OK
        validate_literal_type("bad", ForkEndStyle, "end_style")   # ValueError
    """
    valid = get_args(literal_type)
    if value not in valid:
        raise ValueError(f"{param_name} must be one of {valid}, got '{value}'")
    return value


def sanitize_ref(name: str) -> str:
    """Convert a name to a valid PlantUML reference.

    PlantUML identifiers have restrictions on allowed characters:
    - Simple alphanumeric names (valid Python identifiers) pass through as-is
    - Spaces become underscores
    - Special characters that conflict with PlantUML syntax are removed

    Examples:
        sanitize_ref("User") -> "User"
        sanitize_ref("Web Server") -> "Web_Server"
        sanitize_ref("User<Admin>") -> "UserAdmin"
        sanitize_ref("@#$") -> "_"  # fallback for all-special input
    """
    # Fast path: simple identifiers need no transformation
    if name.isidentifier():
        return name

    # Replace spaces with underscores
    sanitized = name.replace(" ", "_")

    # Remove characters that break PlantUML identifiers
    # This includes quotes, brackets, operators, and punctuation that
    # PlantUML interprets as syntax (e.g., hyphen for arrows)
    for char in "\"'`()[]{}:;,.<>!@#$%^&*+=|\\/?~-":
        sanitized = sanitized.replace(char, "")

    # Ensure we always return a valid identifier
    return sanitized or "_"


# All built-in themes supported by PlantUML (v1.2025.0)
# Validated by test_plantuml_limitations.py::test_builtin_themes_match_plantuml
# fmt: off
PlantUMLBuiltinTheme = Literal[
    "_none_", "amiga", "aws-orange", "black-knight", "bluegray", "blueprint",
    "carbon-gray", "cerulean", "cerulean-outline", "cloudscape-design",
    "crt-amber", "crt-green", "cyborg", "cyborg-outline", "hacker", "lightgray",
    "mars", "materia", "materia-outline", "metal", "mimeograph", "minty", "mono",
    "plain", "reddress-darkblue", "reddress-darkgreen", "reddress-darkorange",
    "reddress-darkred", "reddress-lightblue", "reddress-lightgreen",
    "reddress-lightorange", "reddress-lightred", "sandstone", "silver", "sketchy",
    "sketchy-outline", "spacelab", "spacelab-white", "sunlust", "superhero",
    "superhero-outline", "toy", "united", "vibrant",
]
# fmt: on


@dataclass(frozen=True)
class ExternalTheme:
    """Theme loaded from a local path or remote URL.

    Use this when you want to load a theme that is not built into PlantUML:

        # Local theme file
        theme=ExternalTheme("mytheme", source="/path/to/themes")

        # Remote theme from URL
        theme=ExternalTheme("amiga", source="https://raw.githubusercontent.com/...")

    The source should be a directory path (local) or base URL (remote).
    PlantUML will look for {source}/{name}.puml
    """

    name: str
    source: str  # Local path or remote URL


# Type alias for theme arguments
ThemeLike = PlantUMLBuiltinTheme | ExternalTheme | None


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

# Diagram layout direction (affects overall flow of the diagram)
LayoutDirection = Literal["top_to_bottom", "left_to_right"]

# Layout engine selection (smetana is pure Java alternative to GraphViz)
LayoutEngine = Literal["smetana"]

# Line routing style for arrows
LineType = Literal["ortho", "polyline"]


# =============================================================================
# Validation Helpers
# =============================================================================


def validate_literal(
    value: str,
    options: dict[str, str],
    param_name: str,
) -> str:
    """Validate a value with teaching error message showing all valid options.

    This function provides helpful error messages that list all valid options
    when an invalid value is provided, teaching users the API as they use it.

    Note: Validation is case-insensitive - 'Public', 'PUBLIC', and 'public'
    are all accepted and normalized to lowercase.

    Args:
        value: The input value to validate (case-insensitive)
        options: Dict mapping valid inputs to their descriptions (for errors)
                 or to canonical values (for coercion)
        param_name: Name of the parameter for error messages

    Returns:
        The validated value (lowercased and stripped)

    Raises:
        ValueError: If value not in options, with message listing all options

    Example:
        >>> validate_literal("up", {"up": "Place above", "down": "Place below"}, "direction")
        'up'
        >>> validate_literal("UP", {"up": "Place above", "down": "Place below"}, "direction")
        'up'  # Case-insensitive
        >>> validate_literal("diagonal", {"up": "Place above", "down": "Place below"}, "direction")
        ValueError: Invalid direction 'diagonal'.

        Valid options:
          'up' - Place above
          'down' - Place below
    """
    normalized = value.lower().strip()
    if normalized not in options:
        opts_list = "\n".join(f"  '{k}' - {v}" for k, v in options.items())
        raise ValueError(
            f"Invalid {param_name} '{value}'.\n\nValid options:\n{opts_list}"
        )
    return normalized


# Direction shortcuts and their canonical values
_DIRECTION_SHORTCUTS: dict[str, str] = {
    "u": "up",
    "d": "down",
    "l": "left",
    "r": "right",
}

# Direction options for validation errors
DIRECTION_OPTIONS: dict[str, str] = {
    "up": "Place target above source",
    "down": "Place target below source",
    "left": "Place target left of source",
    "right": "Place target right of source",
    "u": "Shortcut for 'up'",
    "d": "Shortcut for 'down'",
    "l": "Shortcut for 'left'",
    "r": "Shortcut for 'right'",
}


def coerce_direction(value: str | None) -> Direction | None:
    """Coerce direction value with shortcut support and helpful errors.

    Accepts both full names (up, down, left, right) and shortcuts (u, d, l, r).
    Provides a helpful error message listing all valid options if invalid.

    Args:
        value: Direction value or None

    Returns:
        Canonical direction value ('up', 'down', 'left', 'right') or None

    Raises:
        ValueError: If value is not a valid direction

    Example:
        >>> coerce_direction("u")
        'up'
        >>> coerce_direction("left")
        'left'
        >>> coerce_direction(None)
        None
    """
    if value is None:
        return None

    normalized = validate_literal(value, DIRECTION_OPTIONS, "direction")

    # Convert shortcuts to canonical values
    return _DIRECTION_SHORTCUTS.get(normalized, normalized)  # type: ignore[return-value]


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


def _validate_color_component(value: int, name: str) -> int:
    """Validate that a color component is an integer in the range 0-255."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(
            f"{name} must be an integer, got {type(value).__name__}"
        )
    if not 0 <= value <= 255:
        raise ValueError(f"{name} must be 0-255, got {value}")
    return value


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

        Raises:
            TypeError: If any component is not an integer.
            ValueError: If any component is outside the 0-255 range.
        """
        _validate_color_component(r, "r")
        _validate_color_component(g, "g")
        _validate_color_component(b, "b")
        return cls(f"#{r:02X}{g:02X}{b:02X}")

    @classmethod
    def rgba(cls, r: int, g: int, b: int, a: int) -> Color:
        """Create from RGBA components with transparency.

        Each component is an integer from 0-255. Alpha 0 is fully transparent,
        255 is fully opaque. Note: PlantUML encodes alpha first (#AARRGGBB).

        Raises:
            TypeError: If any component is not an integer.
            ValueError: If any component is outside the 0-255 range.
        """
        _validate_color_component(r, "r")
        _validate_color_component(g, "g")
        _validate_color_component(b, "b")
        _validate_color_component(a, "a")
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


_GRADIENT_DIRECTIONS = (
    "horizontal",
    "vertical",
    "diagonal_down",
    "diagonal_up",
)


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

    Raises:
        ValueError: If direction is not one of the valid options.
    """

    start: ColorLike
    end: ColorLike
    direction: Literal[
        "horizontal", "vertical", "diagonal_down", "diagonal_up"
    ] = "horizontal"

    def __post_init__(self) -> None:
        if self.direction not in _GRADIENT_DIRECTIONS:
            raise ValueError(
                f"direction must be one of {_GRADIENT_DIRECTIONS}, "
                f"got '{self.direction}'"
            )


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

    def __post_init__(self) -> None:
        """Validate that char is a single character."""
        if len(self.char) != 1:
            raise ValueError(
                f"Spot char must be a single character, got {len(self.char)}: {self.char!r}"
            )


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


# Horizontal text alignment options
HorizontalAlignment = Literal["left", "center", "right"]


@dataclass(frozen=True)
class ElementStyle:
    """Comprehensive style properties for diagram elements.

    Used in diagram-wide style blocks to define default appearance for
    element types (states, notes, etc.). These properties map to PlantUML's
    CSS-like <style> block syntax.

        background:           Fill color
        line_color:           Border/outline color
        font_color:           Text color
        font_name:            Font family (e.g., "Arial", "Courier")
        font_size:            Font size in points
        font_style:           "normal", "bold", "italic", or "bold italic"
        round_corner:         Corner radius in pixels (0 for sharp corners)
        line_thickness:       Border width in pixels
        line_style:           Border pattern ("solid", "dashed", "dotted", "hidden")
        padding:              Inner padding in pixels
        margin:               Outer margin in pixels
        horizontal_alignment: Text alignment ("left", "center", "right")
        max_width:            Maximum element width in pixels
        shadowing:            Whether to show drop shadow (True/False)
    """

    background: ColorLike | None = None
    line_color: ColorLike | None = None
    font_color: ColorLike | None = None
    font_name: str | None = None
    font_size: int | None = None
    font_style: FontStyle | None = None
    round_corner: int | None = None
    line_thickness: int | None = None
    line_style: LinePattern | None = None
    padding: int | None = None
    margin: int | None = None
    horizontal_alignment: HorizontalAlignment | None = None
    max_width: int | None = None
    shadowing: bool | None = None


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


def coerce_style(value: StyleLike | None) -> Style | None:
    """Convert a StyleLike value to a Style object.

    Returns None if value is None, allowing cleaner call sites:
        style=coerce_style(style)  # instead of coerce_style(style) if style else None
    """
    if value is None:
        return None
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
    line_style: LinePattern
    padding: int
    margin: int
    horizontal_alignment: HorizontalAlignment
    max_width: int
    shadowing: bool


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
        line_style=value.get("line_style"),
        padding=value.get("padding"),
        margin=value.get("margin"),
        horizontal_alignment=value.get("horizontal_alignment"),
        max_width=value.get("max_width"),
        shadowing=value.get("shadowing"),
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
ComponentDiagramStyleLike: TypeAlias = (
    ComponentDiagramStyle | ComponentDiagramStyleDict
)


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


# ---------------------------------------------------------------------------
# Sequence Diagram Styling
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SequenceDiagramStyle:
    """Diagram-wide styling for sequence diagrams.

    This generates a PlantUML <style> block that sets default appearance
    for all elements in the diagram. Individual elements can still override
    these defaults with inline styles.

    Root-level properties apply to the diagram background and default fonts.
    Element-specific properties (participant, arrow, note, etc.) let you
    style each element type independently.

    Example:
        with sequence_diagram(
            diagram_style=SequenceDiagramStyle(
                background="white",
                font_name="Arial",
                participant=ElementStyle(
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
    all participants with blue backgrounds and gray arrows.
    """

    # Root-level properties
    background: ColorLike | Gradient | None = None
    font_name: str | None = None
    font_size: int | None = None
    font_color: ColorLike | None = None

    # Element-specific styles
    participant: ElementStyle | None = None
    actor: ElementStyle | None = None
    boundary: ElementStyle | None = None
    control: ElementStyle | None = None
    entity: ElementStyle | None = None
    database: ElementStyle | None = None
    collections: ElementStyle | None = None
    queue: ElementStyle | None = None
    arrow: DiagramArrowStyle | None = None
    lifeline: ElementStyle | None = None
    note: ElementStyle | None = None
    box: ElementStyle | None = None
    group: ElementStyle | None = None
    divider: ElementStyle | None = None
    reference: ElementStyle | None = None
    title: ElementStyle | None = None


class SequenceDiagramStyleDict(TypedDict, total=False):
    """Dict form of SequenceDiagramStyle for convenience.

    Example:
        with sequence_diagram(
            diagram_style={
                "background": "white",
                "font_name": "Arial",
                "participant": {"background": "#E3F2FD", "line_color": "#1976D2"},
                "arrow": {"line_color": "#757575"},
            }
        ) as d:
            ...
    """

    background: ColorLike | Gradient
    font_name: str
    font_size: int
    font_color: ColorLike
    participant: ElementStyleLike
    actor: ElementStyleLike
    boundary: ElementStyleLike
    control: ElementStyleLike
    entity: ElementStyleLike
    database: ElementStyleLike
    collections: ElementStyleLike
    queue: ElementStyleLike
    arrow: DiagramArrowStyleLike
    lifeline: ElementStyleLike
    note: ElementStyleLike
    box: ElementStyleLike
    group: ElementStyleLike
    divider: ElementStyleLike
    reference: ElementStyleLike
    title: ElementStyleLike


# Type alias for sequence diagram style arguments
SequenceDiagramStyleLike: TypeAlias = SequenceDiagramStyle | SequenceDiagramStyleDict


def coerce_sequence_diagram_style(
    value: SequenceDiagramStyleLike,
) -> SequenceDiagramStyle:
    """Convert a SequenceDiagramStyleLike value to a SequenceDiagramStyle object."""
    if isinstance(value, SequenceDiagramStyle):
        return value
    return SequenceDiagramStyle(
        background=_coerce_color_or_gradient(value.get("background")),
        font_name=value.get("font_name"),
        font_size=value.get("font_size"),
        font_color=coerce_color(value["font_color"])
        if "font_color" in value
        else None,
        participant=coerce_element_style(value["participant"])
        if "participant" in value
        else None,
        actor=coerce_element_style(value["actor"]) if "actor" in value else None,
        boundary=coerce_element_style(value["boundary"])
        if "boundary" in value
        else None,
        control=coerce_element_style(value["control"])
        if "control" in value
        else None,
        entity=coerce_element_style(value["entity"]) if "entity" in value else None,
        database=coerce_element_style(value["database"])
        if "database" in value
        else None,
        collections=coerce_element_style(value["collections"])
        if "collections" in value
        else None,
        queue=coerce_element_style(value["queue"]) if "queue" in value else None,
        arrow=coerce_diagram_arrow_style(value["arrow"])
        if "arrow" in value
        else None,
        lifeline=coerce_element_style(value["lifeline"])
        if "lifeline" in value
        else None,
        note=coerce_element_style(value["note"]) if "note" in value else None,
        box=coerce_element_style(value["box"]) if "box" in value else None,
        group=coerce_element_style(value["group"]) if "group" in value else None,
        divider=coerce_element_style(value["divider"])
        if "divider" in value
        else None,
        reference=coerce_element_style(value["reference"])
        if "reference" in value
        else None,
        title=coerce_element_style(value["title"]) if "title" in value else None,
    )


# ---------------------------------------------------------------------------
# Activity Diagram Styling
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ActivityDiagramStyle:
    """Diagram-wide styling for activity diagrams.

    This generates a PlantUML <style> block that sets default appearance
    for all elements in the diagram.

    Example:
        with activity_diagram(
            diagram_style=ActivityDiagramStyle(
                background="white",
                activity=ElementStyle(background="#E3F2FD"),
                arrow=DiagramArrowStyle(line_color="#757575"),
            )
        ) as d:
            ...
    """

    # Root-level properties
    background: ColorLike | Gradient | None = None
    font_name: str | None = None
    font_size: int | None = None
    font_color: ColorLike | None = None

    # Element-specific styles
    activity: ElementStyle | None = None
    partition: ElementStyle | None = None
    swimlane: ElementStyle | None = None
    diamond: ElementStyle | None = None
    arrow: DiagramArrowStyle | None = None
    note: ElementStyle | None = None
    group: ElementStyle | None = None
    title: ElementStyle | None = None


class ActivityDiagramStyleDict(TypedDict, total=False):
    """Dict form of ActivityDiagramStyle for convenience."""

    background: ColorLike | Gradient
    font_name: str
    font_size: int
    font_color: ColorLike
    activity: ElementStyleLike
    partition: ElementStyleLike
    swimlane: ElementStyleLike
    diamond: ElementStyleLike
    arrow: DiagramArrowStyleLike
    note: ElementStyleLike
    group: ElementStyleLike
    title: ElementStyleLike


# Type alias for activity diagram style arguments
ActivityDiagramStyleLike: TypeAlias = ActivityDiagramStyle | ActivityDiagramStyleDict


def coerce_activity_diagram_style(
    value: ActivityDiagramStyleLike,
) -> ActivityDiagramStyle:
    """Convert an ActivityDiagramStyleLike value to an ActivityDiagramStyle object."""
    if isinstance(value, ActivityDiagramStyle):
        return value
    return ActivityDiagramStyle(
        background=_coerce_color_or_gradient(value.get("background")),
        font_name=value.get("font_name"),
        font_size=value.get("font_size"),
        font_color=coerce_color(value["font_color"])
        if "font_color" in value
        else None,
        activity=coerce_element_style(value["activity"])
        if "activity" in value
        else None,
        partition=coerce_element_style(value["partition"])
        if "partition" in value
        else None,
        swimlane=coerce_element_style(value["swimlane"])
        if "swimlane" in value
        else None,
        diamond=coerce_element_style(value["diamond"])
        if "diamond" in value
        else None,
        arrow=coerce_diagram_arrow_style(value["arrow"])
        if "arrow" in value
        else None,
        note=coerce_element_style(value["note"]) if "note" in value else None,
        group=coerce_element_style(value["group"]) if "group" in value else None,
        title=coerce_element_style(value["title"]) if "title" in value else None,
    )


# ---------------------------------------------------------------------------
# Class Diagram Styling
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ClassDiagramStyle:
    """Diagram-wide styling for class diagrams.

    This generates a PlantUML <style> block that sets default appearance
    for all elements in the diagram.

    Example:
        with class_diagram(
            diagram_style=ClassDiagramStyle(
                background="white",
                class_=ElementStyle(background="#E3F2FD"),
                arrow=DiagramArrowStyle(line_color="#757575"),
            )
        ) as d:
            ...
    """

    # Root-level properties
    background: ColorLike | Gradient | None = None
    font_name: str | None = None
    font_size: int | None = None
    font_color: ColorLike | None = None

    # Element-specific styles (class_ because class is a keyword)
    class_: ElementStyle | None = None
    interface: ElementStyle | None = None
    abstract: ElementStyle | None = None
    enum: ElementStyle | None = None
    annotation: ElementStyle | None = None
    package: ElementStyle | None = None
    arrow: DiagramArrowStyle | None = None
    note: ElementStyle | None = None
    title: ElementStyle | None = None


class ClassDiagramStyleDict(TypedDict, total=False):
    """Dict form of ClassDiagramStyle for convenience."""

    background: ColorLike | Gradient
    font_name: str
    font_size: int
    font_color: ColorLike
    class_: ElementStyleLike
    interface: ElementStyleLike
    abstract: ElementStyleLike
    enum: ElementStyleLike
    annotation: ElementStyleLike
    package: ElementStyleLike
    arrow: DiagramArrowStyleLike
    note: ElementStyleLike
    title: ElementStyleLike


# Type alias for class diagram style arguments
ClassDiagramStyleLike: TypeAlias = ClassDiagramStyle | ClassDiagramStyleDict


def coerce_class_diagram_style(
    value: ClassDiagramStyleLike,
) -> ClassDiagramStyle:
    """Convert a ClassDiagramStyleLike value to a ClassDiagramStyle object."""
    if isinstance(value, ClassDiagramStyle):
        return value
    return ClassDiagramStyle(
        background=_coerce_color_or_gradient(value.get("background")),
        font_name=value.get("font_name"),
        font_size=value.get("font_size"),
        font_color=coerce_color(value["font_color"])
        if "font_color" in value
        else None,
        class_=coerce_element_style(value["class_"]) if "class_" in value else None,
        interface=coerce_element_style(value["interface"])
        if "interface" in value
        else None,
        abstract=coerce_element_style(value["abstract"])
        if "abstract" in value
        else None,
        enum=coerce_element_style(value["enum"]) if "enum" in value else None,
        annotation=coerce_element_style(value["annotation"])
        if "annotation" in value
        else None,
        package=coerce_element_style(value["package"])
        if "package" in value
        else None,
        arrow=coerce_diagram_arrow_style(value["arrow"])
        if "arrow" in value
        else None,
        note=coerce_element_style(value["note"]) if "note" in value else None,
        title=coerce_element_style(value["title"]) if "title" in value else None,
    )


# ---------------------------------------------------------------------------
# Object Diagram Styling
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ObjectDiagramStyle:
    """Diagram-wide styling for object diagrams.

    This generates a PlantUML <style> block that sets default appearance
    for all elements in the diagram.

    Note: PlantUML ignores arrow and note CSS selectors for object diagrams.
    Use inline styles for those elements if needed.
    """

    # Root-level properties
    background: ColorLike | Gradient | None = None
    font_name: str | None = None
    font_size: int | None = None
    font_color: ColorLike | None = None

    # Element-specific styles (only object and map render)
    object: ElementStyle | None = None
    map: ElementStyle | None = None
    title: ElementStyle | None = None


class ObjectDiagramStyleDict(TypedDict, total=False):
    """Dict form of ObjectDiagramStyle for convenience."""

    background: ColorLike | Gradient
    font_name: str
    font_size: int
    font_color: ColorLike
    object: ElementStyleLike
    map: ElementStyleLike
    title: ElementStyleLike


ObjectDiagramStyleLike: TypeAlias = ObjectDiagramStyle | ObjectDiagramStyleDict


def coerce_object_diagram_style(
    value: ObjectDiagramStyleLike,
) -> ObjectDiagramStyle:
    """Convert an ObjectDiagramStyleLike value to an ObjectDiagramStyle object."""
    if isinstance(value, ObjectDiagramStyle):
        return value
    return ObjectDiagramStyle(
        background=_coerce_color_or_gradient(value.get("background")),
        font_name=value.get("font_name"),
        font_size=value.get("font_size"),
        font_color=coerce_color(value["font_color"])
        if "font_color" in value
        else None,
        object=coerce_element_style(value["object"]) if "object" in value else None,
        map=coerce_element_style(value["map"]) if "map" in value else None,
        title=coerce_element_style(value["title"]) if "title" in value else None,
    )
