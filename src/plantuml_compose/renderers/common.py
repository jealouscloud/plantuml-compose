"""Common rendering utilities shared across all diagram types."""

from __future__ import annotations

from ..primitives.common import (
    Color,
    Footer,
    Gradient,
    Header,
    Label,
    Legend,
    LineStyle,
    LineStyleLike,
    Scale,
    Stereotype,
    Style,
    StyleLike,
    coerce_line_style,
    coerce_style,
)


def escape_quotes(text: str) -> str:
    """Replace double quotes with Unicode escape for PlantUML compatibility.

    We use <U+0022> which PlantUML renders as a literal double quote.
    """
    return text.replace('"', "<U+0022>")


def render_color(color: Color | Gradient | str) -> str:
    """Convert a color to PlantUML string."""
    if isinstance(color, str):
        return color
    if isinstance(color, Color):
        return color.value
    if isinstance(color, Gradient):
        sep = {
            "horizontal": "|",
            "vertical": "-",
            "diagonal_down": "/",
            "diagonal_up": "\\",
        }[color.direction]
        return f"{render_color(color.start)}{sep}{render_color(color.end)}"
    raise TypeError(f"Unknown color type: {type(color)}")


def render_label(label: Label | str | None) -> str:
    """Convert a label to string."""
    if label is None:
        return ""
    if isinstance(label, str):
        return escape_quotes(label)
    return escape_quotes(label.text)


def render_line_style_bracket(style: LineStyleLike) -> str:
    """Render line style as bracket modifier: [#red,dashed,thickness=2]"""
    style = coerce_line_style(style)
    parts: list[str] = []

    if style.color:
        color_str = render_color(style.color)
        if not color_str.startswith("#"):
            color_str = f"#{color_str}"
        parts.append(color_str)

    if style.pattern != "solid":
        parts.append(style.pattern)

    if style.bold:
        parts.append("bold")

    if style.thickness:
        parts.append(f"thickness={style.thickness}")

    return f"[{','.join(parts)}]" if parts else ""


def render_element_style(style: StyleLike) -> str:
    """Render Style as PlantUML inline format for any element.

    PlantUML element style syntax options:
    1. Background only: #color or #color1-color2 (gradient)
    2. Line only: ##[pattern]color or ##color
    3. Multiple properties: #back;line:color;text:color (semicolon-separated)

    When only background and/or line are specified, uses space-separated format.
    When text_color is specified, uses semicolon format (background optional).

    Works for states, components, interfaces, and other diagram elements.
    """
    style = coerce_style(style)

    # Coerce line style if present
    line = coerce_line_style(style.line) if style.line else None

    # Check what we have
    background = style.background
    text_color = style.text_color
    has_background = background is not None
    has_line = line is not None and (
        line.color is not None or line.pattern != "solid"
    )
    has_text = text_color is not None

    # If we only have background and/or line, use space-separated format
    if not has_text:
        parts: list[str] = []

        if has_background:
            bg = render_color(background)  # type: ignore[arg-type]
            if not bg.startswith("#"):
                bg = f"#{bg}"
            parts.append(bg)

        if has_line and line:
            color = render_color(line.color) if line.color else ""
            pattern = ""
            if line.pattern != "solid":
                pattern = f"[{line.pattern}]"

            if color or pattern:
                if color.startswith("#"):
                    color = color[1:]  # Remove leading # for hex colors
                parts.append(f"##{pattern}{color}")

        return " ".join(parts)

    # Use semicolon format for text color (with optional background/line)
    props: list[str] = []

    if has_background:
        bg = render_color(background)  # type: ignore[arg-type]
        if not bg.startswith("#"):
            bg = f"#{bg}"
        props.append(bg)

    if has_line and line:
        if line.pattern != "solid":
            props.append(f"line.{line.pattern}")
        if line.color:
            color = render_color(line.color)
            props.append(f"line:{color}")

    if text_color is not None:
        tc = render_color(text_color)
        props.append(f"text:{tc}")

    # Join with semicolons, prefix with # if we have background, else just #
    if props:
        result = ";".join(props)
        if not result.startswith("#"):
            result = f"#{result}"
        return result
    return ""


def render_stereotype(stereotype: Stereotype) -> str:
    """Render Stereotype as PlantUML format: <<name>> or << (C,#color) name >>"""
    if stereotype.spot:
        color = render_color(stereotype.spot.color)
        if not color.startswith("#"):
            color = f"#{color}"
        return f"<< ({stereotype.spot.char},{color}) {stereotype.name} >>"
    return f"<<{stereotype.name}>>"


# =============================================================================
# Common Diagram Metadata Rendering
# =============================================================================


def render_header(header: Header) -> list[str]:
    """Render header directive.

    PlantUML syntax:
        header Text           (left-aligned, single line)
        center header Text    (centered, single line)
        right header Text     (right-aligned, single line)
        header\\n...\\nendheader  (multiline block)
    """
    text = render_label(header.content)

    if header.position == "center":
        prefix = "center header"
    elif header.position == "right":
        prefix = "right header"
    else:
        prefix = "header"

    if "\n" in text:
        lines = [prefix]
        lines.extend(f"  {line}" for line in text.split("\n"))
        lines.append("endheader")
        return lines
    return [f"{prefix} {text}"]


def render_footer(footer: Footer) -> list[str]:
    """Render footer directive.

    PlantUML syntax:
        footer Text           (left-aligned, single line)
        center footer Text    (centered, single line)
        right footer Text     (right-aligned, single line)
        footer\\n...\\nendfooter  (multiline block)

    Supports special variables like %page% and %lastpage%.
    """
    text = render_label(footer.content)

    if footer.position == "center":
        prefix = "center footer"
    elif footer.position == "right":
        prefix = "right footer"
    else:
        prefix = "footer"

    if "\n" in text:
        lines = [prefix]
        lines.extend(f"  {line}" for line in text.split("\n"))
        lines.append("endfooter")
        return lines
    return [f"{prefix} {text}"]


def render_legend(legend: Legend) -> list[str]:
    """Render legend block.

    PlantUML syntax:
        legend [left|right|top|bottom|center]
          content
        endlegend

    Legends are always multiline blocks in PlantUML.
    """
    text = render_label(legend.content)

    # Build opening line with position
    if legend.position == "right":
        opening = "legend"  # right is default
    else:
        opening = f"legend {legend.position}"

    lines = [opening]
    for line in text.split("\n"):
        lines.append(f"  {line}")
    lines.append("endlegend")
    return lines


def render_scale(scale: Scale) -> str:
    """Render scale directive.

    PlantUML syntax:
        scale 1.5              (factor)
        scale 2/3              (fraction - but we use float)
        scale 200 width        (exact width)
        scale 100 height       (exact height)
        scale 200*100          (exact width and height)
        scale max 1024 width   (max width)
        scale max 768 height   (max height)
        scale max 1024*768     (max width and height)
    """
    # Max dimensions take priority
    if scale.max_width is not None and scale.max_height is not None:
        return f"scale max {scale.max_width}*{scale.max_height}"
    if scale.max_width is not None:
        return f"scale max {scale.max_width} width"
    if scale.max_height is not None:
        return f"scale max {scale.max_height} height"

    # Exact dimensions
    if scale.width is not None and scale.height is not None:
        return f"scale {scale.width}*{scale.height}"
    if scale.width is not None:
        return f"scale {scale.width} width"
    if scale.height is not None:
        return f"scale {scale.height} height"

    # Factor
    if scale.factor is not None:
        return f"scale {scale.factor}"

    return ""


def render_caption(caption: str) -> str:
    """Render caption directive.

    PlantUML syntax:
        caption Figure 1: Description

    Caption appears below the diagram.
    """
    return f"caption {escape_quotes(caption)}"
