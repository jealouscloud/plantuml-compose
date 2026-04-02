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

from collections.abc import Mapping
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

    # Replace whitespace with underscores
    sanitized = name.replace(" ", "_").replace("\n", "_").replace("\r", "_").replace("\t", "_")

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


def _validate_style_dict_keys(
    value: Mapping[str, object],
    allowed_keys: frozenset[str],
    style_name: str,
) -> None:
    """Validate that a style dict contains only allowed keys.

    Raises:
        ValueError: If unknown keys are present, with helpful message
    """
    unknown = set(value.keys()) - allowed_keys
    if unknown:
        unknown_str = ", ".join(sorted(unknown))
        allowed_str = ", ".join(sorted(allowed_keys))
        raise ValueError(
            f"Unknown keys in {style_name}: {unknown_str}. "
            f"Allowed keys: {allowed_str}"
        )


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
class EmbeddedDiagram:
    """A sub-diagram for embedding in notes, messages, legends, etc.

    PlantUML supports embedding diagrams using {{ }} wrapper syntax. This allows
    rich diagram content inside notes, sequence messages, and legends.

    Sub-diagrams are rendered with transparent background by default so they
    blend naturally into their container.

    Example:
        # Create a component diagram to embed
        with component_diagram() as arch:
            api = arch.component("API")
            db = arch.component("DB")
            arch.link(api, db)

        # Embed it in a sequence diagram note
        with sequence_diagram() as d:
            alice = d.participant("Alice")
            d.note(alice, arch.embed(), position="right")

    Attributes:
        content: Inner PlantUML content (without @start/@end markers)
        transparent: If True, applies transparent background CSS styling
        embed_type: For specialized diagrams (json, yaml, mindmap, wbs,
            gantt, salt), the type name for {{type ... }} syntax.
            None for standard UML diagrams.
    """

    content: str
    transparent: bool = True
    embed_type: str | None = None

    def render(self, inline: bool = False) -> str:
        """Render the embedded diagram for placement in PlantUML.

        Args:
            inline: If True, use %breakline() for single-line contexts like
                   message labels and state descriptions. If False, use actual
                   newlines for multi-line contexts like notes and legends.

        Returns:
            PlantUML sub-diagram syntax with {{ }} wrapper
        """
        inner_lines: list[str] = []

        # Transparent styling only for standard diagrams —
        # specialized types don't support <style> inside {{type }}
        if self.transparent and not self.embed_type:
            inner_lines.append("<style>")
            inner_lines.append("root { BackgroundColor transparent }")
            inner_lines.append("</style>")

        # Add the content, preserving its structure
        inner_lines.append(self.content)

        # Build the wrapper: {{type for specialized, {{ for standard
        open_brace = f"{{{{{self.embed_type}" if self.embed_type else "{{"

        if inline:
            # For single-line contexts: join with %breakline()
            flattened_inner = " %breakline() ".join(
                line for part in inner_lines
                for line in part.split("\n")
                if line.strip()
            )
            return f"{open_brace} {flattened_inner}}}}}"
        else:
            return f"{open_brace}\n" + "\n".join(inner_lines) + "\n}}"


# Type alias for content that can include embedded diagrams
EmbeddableContent: TypeAlias = str | Label | EmbeddedDiagram


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

    The content can include Creole markup for rich text formatting,
    or an EmbeddedDiagram for sub-diagram content.
    """

    content: "EmbeddableContent"
    position: NotePosition = "right"


@dataclass(frozen=True)
class Newpage:
    """Page break directive that splits a diagram into multiple pages.

    PlantUML syntax:
        newpage                        (simple page break)
        newpage Title for new page     (page break with title for new page)

    Inserted between diagram elements to split output into separate pages.
    """

    title: str | None = None


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
    used for diagram keys or additional context. Supports multiline text,
    Creole markup, or embedded sub-diagrams.

        content:  Legend text (can include Creole markup) or EmbeddedDiagram
        position: Where to place the legend relative to the diagram
    """

    content: "EmbeddableContent"
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
    """Style properties for diagram elements (states, classes, notes, etc.).

    Maps to PlantUML's CSS-like ``<style>`` block properties. Use via
    diagram_style dicts on diagram constructors.

    All properties are optional — only set ones are rendered.

    Properties:
        background:           Fill color (str name, "#hex", or Color object)
        line_color:           Border/outline color
        font_color:           Text color
        font_name:            Font family (e.g., "Arial", "Courier")
        font_size:            Font size in points (e.g., 14)
        font_style:           "normal", "bold", "italic", or "bold italic"
        round_corner:         Corner radius in pixels (0 = sharp)
        line_thickness:       Border width in pixels
        line_style:           Border pattern: "solid", "dashed", "dotted", "hidden"
        padding:              Inner padding in pixels
        margin:               Outer margin in pixels
        horizontal_alignment: Text alignment: "left", "center", "right"
        max_width:            Maximum element width in pixels (text wraps)
        shadowing:            Drop shadow (True/False)
        diagonal_corner:      Diagonal corner cut in pixels
        word_wrap:            Word wrap width in pixels
        hyperlink_color:      Color for hyperlinked text

    Example (dict form in diagram_style):
        diagram_style={
            "state": {
                "background": "#E3F2FD",
                "line_color": "#1976D2",
                "round_corner": 10,
                "font_name": "Arial",
                "font_size": 12,
                "padding": 8,
                "shadowing": True,
            },
        }
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
    diagonal_corner: int | None = None
    word_wrap: int | None = None
    hyperlink_color: ColorLike | None = None


@dataclass(frozen=True)
class DiagramArrowStyle:
    """Style properties for all arrows/connections in a diagram.

    Sets diagram-wide default arrow appearance via the ``<style>`` block's
    ``arrow { }`` section. For styling individual arrows, use ``style=``
    on specific transitions/relationships instead.

    Properties:
        line_color:     Arrow line color
        line_thickness: Arrow line width in pixels
        line_pattern:   Line pattern: "solid", "dashed", "dotted", "hidden"
        font_color:     Arrow label text color
        font_name:      Arrow label font family
        font_size:      Arrow label font size in points

    Example (dict form in diagram_style):
        diagram_style={
            "arrow": {
                "line_color": "gray",
                "line_thickness": 2,
                "line_pattern": "dashed",
                "font_color": "blue",
                "font_size": 10,
            },
        }
    """

    line_color: ColorLike | None = None
    line_thickness: int | None = None
    line_pattern: LinePattern | None = None
    font_color: ColorLike | None = None
    font_name: str | None = None
    font_size: int | None = None


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
LineStyleLike: TypeAlias = LineStyle | LineStyleDict | str

_LINE_STYLE_KEYS: frozenset[str] = frozenset({"pattern", "color", "thickness", "bold"})
_LINE_PATTERN_SHORTHANDS: frozenset[str] = frozenset({
    "solid", "dashed", "dotted", "hidden",
})


def coerce_line_style(value: LineStyleLike) -> LineStyle:
    """Convert a LineStyleLike value to a LineStyle object.

    Accepts LineStyle, LineStyleDict, or string shorthand:
        "dashed", "dotted", "solid", "hidden" — line pattern
        "bold" — bold line
        "#red", "#FF0000" — line color
    """
    if isinstance(value, LineStyle):
        return value
    if isinstance(value, str):
        if value.startswith("#"):
            return LineStyle(color=coerce_color(value))
        if value in _LINE_PATTERN_SHORTHANDS:
            return LineStyle(pattern=value)
        if value == "bold":
            return LineStyle(bold=True)
        raise ValueError(
            f"Unknown line style shorthand: {value!r}. "
            f"Use one of: {', '.join(sorted(_LINE_PATTERN_SHORTHANDS))}, 'bold', or '#color'"
        )
    _validate_style_dict_keys(value, _LINE_STYLE_KEYS, "LineStyle")
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

_STYLE_KEYS: frozenset[str] = frozenset(
    {"background", "line", "text_color", "stereotype"}
)


def coerce_style(value: StyleLike | None) -> Style | None:
    """Convert a StyleLike value to a Style object.

    Returns None if value is None, allowing cleaner call sites:
        style=coerce_style(style)  # instead of coerce_style(style) if style else None
    """
    if value is None:
        return None
    if isinstance(value, Style):
        return value
    _validate_style_dict_keys(value, _STYLE_KEYS, "Style")
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
    """Dict form of ElementStyle — used inside diagram_style dicts.

    All keys are optional. Only set properties are rendered.

    Available keys:
        background:           str color name, "#hex", or Color
        line_color:           Border color
        font_color:           Text color
        font_name:            Font family (e.g., "Arial")
        font_size:            Font size in points (e.g., 14)
        font_style:           "normal" | "bold" | "italic" | "bold italic"
        round_corner:         Corner radius in pixels
        line_thickness:       Border width in pixels
        line_style:           "solid" | "dashed" | "dotted" | "hidden"
        padding:              Inner padding in pixels
        margin:               Outer margin in pixels
        horizontal_alignment: "left" | "center" | "right"
        max_width:            Max element width (text wraps)
        shadowing:            True/False for drop shadow
        diagonal_corner:      Diagonal corner cut in pixels
        word_wrap:            Word wrap width in pixels
        hyperlink_color:      Hyperlink text color

    Example:
        {"background": "#E3F2FD", "line_color": "#1976D2", "round_corner": 5, "padding": 8}
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
    diagonal_corner: int
    word_wrap: int
    hyperlink_color: ColorLike


# Type alias for element style arguments
ElementStyleLike: TypeAlias = ElementStyle | ElementStyleDict

_ELEMENT_STYLE_KEYS: frozenset[str] = frozenset({
    "background", "line_color", "font_color", "font_name", "font_size",
    "font_style", "round_corner", "line_thickness", "line_style",
    "padding", "margin", "horizontal_alignment", "max_width", "shadowing",
    "diagonal_corner", "word_wrap", "hyperlink_color",
})


def coerce_element_style(value: ElementStyleLike) -> ElementStyle:
    """Convert an ElementStyleLike value to an ElementStyle object."""
    if isinstance(value, ElementStyle):
        return value
    _validate_style_dict_keys(value, _ELEMENT_STYLE_KEYS, "ElementStyle")
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
        diagonal_corner=value.get("diagonal_corner"),
        word_wrap=value.get("word_wrap"),
        hyperlink_color=coerce_color(value["hyperlink_color"])
        if "hyperlink_color" in value
        else None,
    )


class DiagramArrowStyleDict(TypedDict, total=False):
    """Dict form of DiagramArrowStyle — used as the "arrow" key in diagram_style.

    Available keys:
        line_color:     Arrow line color
        line_thickness: Line width in pixels
        line_pattern:   "solid" | "dashed" | "dotted" | "hidden"
        font_color:     Arrow label text color
        font_name:      Arrow label font family
        font_size:      Arrow label font size in points

    Example:
        {"line_color": "gray", "line_thickness": 2, "font_color": "blue"}
    """

    line_color: ColorLike
    line_thickness: int
    line_pattern: LinePattern
    font_color: ColorLike
    font_name: str
    font_size: int


# Type alias for diagram arrow style arguments
DiagramArrowStyleLike: TypeAlias = DiagramArrowStyle | DiagramArrowStyleDict

_DIAGRAM_ARROW_STYLE_KEYS: frozenset[str] = frozenset({
    "line_color", "line_thickness", "line_pattern",
    "font_color", "font_name", "font_size",
})


def coerce_diagram_arrow_style(
    value: DiagramArrowStyleLike,
) -> DiagramArrowStyle:
    """Convert a DiagramArrowStyleLike value to a DiagramArrowStyle object."""
    if isinstance(value, DiagramArrowStyle):
        return value
    _validate_style_dict_keys(value, _DIAGRAM_ARROW_STYLE_KEYS, "DiagramArrowStyle")
    return DiagramArrowStyle(
        line_color=coerce_color(value["line_color"])
        if "line_color" in value
        else None,
        line_thickness=value.get("line_thickness"),
        line_pattern=value.get("line_pattern"),
        font_color=coerce_color(value["font_color"])
        if "font_color" in value
        else None,
        font_name=value.get("font_name"),
        font_size=value.get("font_size"),
    )


