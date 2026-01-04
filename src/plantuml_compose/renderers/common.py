"""Common rendering utilities shared across all diagram types."""

from __future__ import annotations

from ..primitives.common import (
    Color,
    Gradient,
    Label,
    LinePattern,
    LineStyle,
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
