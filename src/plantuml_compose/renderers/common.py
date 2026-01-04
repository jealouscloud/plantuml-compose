"""Common rendering utilities shared across all diagram types."""

from __future__ import annotations

from ..primitives.common import (
    Color,
    Gradient,
    Label,
    LinePattern,
    LineStyle,
    Stereotype,
    Style,
)


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
        return label
    return label.text


def render_line_style_bracket(style: LineStyle) -> str:
    """Render line style as bracket modifier: [#red,dashed,thickness=2]"""
    parts: list[str] = []

    if style.color:
        color_str = render_color(style.color)
        if not color_str.startswith("#"):
            color_str = f"#{color_str}"
        parts.append(color_str)

    if style.pattern != LinePattern.SOLID:
        parts.append(style.pattern.value)

    if style.bold:
        parts.append("bold")

    if style.thickness:
        parts.append(f"thickness={style.thickness}")

    return f"[{','.join(parts)}]" if parts else ""


def render_state_style(style: Style) -> str:
    """Render Style as PlantUML inline format.

    PlantUML state style syntax options:
    1. Background only: #color or #color1-color2 (gradient)
    2. Line only: ##[pattern]color or ##color
    3. Multiple properties: #back;line:color;text:color (semicolon-separated)

    The semicolon format requires a background color. If we have other
    properties without a background, we use the individual syntaxes.
    """
    # Check what we have
    has_background = style.background is not None
    has_line = style.line is not None and (
        style.line.color is not None or style.line.pattern != LinePattern.SOLID
    )
    has_text = style.text_color is not None

    # If we only have background and/or line, use space-separated format
    if not has_text:
        parts: list[str] = []

        if has_background:
            bg = render_color(style.background)
            if not bg.startswith("#"):
                bg = f"#{bg}"
            parts.append(bg)

        if has_line:
            color = render_color(style.line.color) if style.line.color else ""
            pattern = ""
            if style.line.pattern != LinePattern.SOLID:
                pattern = f"[{style.line.pattern.value}]"

            if color or pattern:
                if color.startswith("#"):
                    color = color[1:]  # Remove leading # for hex colors
                parts.append(f"##{pattern}{color}")

        return " ".join(parts)

    # If we have text color, we need semicolon format which requires background
    # Use white as default if no background specified
    bg = render_color(style.background) if style.background else "white"
    if not bg.startswith("#"):
        bg = f"#{bg}"

    props = [bg]

    if has_line:
        if style.line.pattern != LinePattern.SOLID:
            props.append(f"line.{style.line.pattern.value}")
        if style.line.color:
            color = render_color(style.line.color)
            props.append(f"line:{color}")

    if has_text:
        tc = render_color(style.text_color)
        props.append(f"text:{tc}")

    return ";".join(props)


def render_stereotype(stereotype: Stereotype) -> str:
    """Render Stereotype as PlantUML format: <<name>> or << (C,#color) name >>"""
    if stereotype.spot:
        color = render_color(stereotype.spot.color)
        if not color.startswith("#"):
            color = f"#{color}"
        return f"<< ({stereotype.spot.char},{color}) {stereotype.name} >>"
    return f"<<{stereotype.name}>>"
