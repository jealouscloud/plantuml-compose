"""Object diagram renderer.

Pure functions that transform object diagram primitives to PlantUML text.
"""

from __future__ import annotations

from ..primitives.object_ import (
    Map,
    Object,
    ObjectDiagram,
    ObjectDiagramElement,
    ObjectNote,
    Relationship,
)
from .common import (
    escape_quotes,
    needs_quotes,
    quote_ref,
    render_caption,
    render_color,
    render_footer,
    render_header,
    render_label,
    render_legend,
    render_line_style_bracket,
    render_scale,
    render_stereotype,
)


def render_object_diagram(diagram: ObjectDiagram) -> str:
    """Render a complete object diagram to PlantUML text."""
    lines: list[str] = ["@startuml"]

    # Scale (affects output size)
    if diagram.scale:
        scale_str = render_scale(diagram.scale)
        if scale_str:
            lines.append(scale_str)

    if diagram.title:
        if "\n" in diagram.title:
            lines.append("title")
            for title_line in diagram.title.split("\n"):
                lines.append(f"  {escape_quotes(title_line)}")
            lines.append("end title")
        else:
            lines.append(f"title {escape_quotes(diagram.title)}")

    # Header and footer
    if diagram.header:
        lines.extend(render_header(diagram.header))
    if diagram.footer:
        lines.extend(render_footer(diagram.footer))

    # Caption (appears below diagram)
    if diagram.caption:
        lines.append(render_caption(diagram.caption))

    # Legend
    if diagram.legend:
        lines.extend(render_legend(diagram.legend))

    for elem in diagram.elements:
        lines.extend(_render_element(elem))

    lines.append("@enduml")
    return "\n".join(lines)


def _render_element(elem: ObjectDiagramElement, indent: int = 0) -> list[str]:
    """Render a single diagram element."""

    if isinstance(elem, Object):
        return _render_object(elem, indent)
    if isinstance(elem, Map):
        return _render_map(elem, indent)
    if isinstance(elem, Relationship):
        return _render_relationship(elem, indent)
    if isinstance(elem, ObjectNote):
        return _render_note(elem, indent)
    raise TypeError(f"Unknown element type: {type(elem).__name__}")


def _render_object(obj: Object, indent: int = 0) -> list[str]:
    """Render an object."""
    prefix = "  " * indent
    lines: list[str] = []

    parts: list[str] = ["object"]

    # Name with possible alias - PlantUML requires quotes when using alias
    if obj.alias:
        name = f'"{escape_quotes(obj.name)}"'
        parts.append(name)
        parts.append(f"as {obj.alias}")
    else:
        name = (
            f'"{escape_quotes(obj.name)}"'
            if needs_quotes(obj.name)
            else obj.name
        )
        parts.append(name)

    if obj.stereotype:
        parts.append(render_stereotype(obj.stereotype))

    # Style background as element color
    if obj.style and obj.style.background:
        color = render_color(obj.style.background)
        if not color.startswith("#"):
            color = f"#{color}"
        parts.append(color)

    if obj.fields:
        lines.append(f"{prefix}{' '.join(parts)} {{")
        for field in obj.fields:
            value = escape_quotes(field.value)
            lines.append(f"{prefix}  {field.name} = {value}")
        lines.append(f"{prefix}}}")
    else:
        lines.append(f"{prefix}{' '.join(parts)}")

    return lines


def _render_map(map_obj: Map, indent: int = 0) -> list[str]:
    """Render a map."""
    prefix = "  " * indent
    lines: list[str] = []

    parts: list[str] = ["map"]

    # Name with possible alias - PlantUML requires quotes when using alias
    if map_obj.alias:
        name = f'"{escape_quotes(map_obj.name)}"'
        parts.append(name)
        parts.append(f"as {map_obj.alias}")
    else:
        name = (
            f'"{escape_quotes(map_obj.name)}"'
            if needs_quotes(map_obj.name)
            else map_obj.name
        )
        parts.append(name)

    # Style background as element color
    if map_obj.style and map_obj.style.background:
        color = render_color(map_obj.style.background)
        if not color.startswith("#"):
            color = f"#{color}"
        parts.append(color)

    lines.append(f"{prefix}{' '.join(parts)} {{")
    for entry in map_obj.entries:
        if entry.link:
            lines.append(f"{prefix}  {entry.key} *-> {entry.link}")
        else:
            lines.append(f"{prefix}  {entry.key} => {entry.value}")
    lines.append(f"{prefix}}}")

    return lines


def _render_relationship(rel: Relationship, indent: int = 0) -> list[str]:
    """Render a relationship."""
    prefix = "  " * indent
    lines: list[str] = []

    # Get the base arrow based on type
    arrow_map = {
        "association": "--",
        "arrow": "-->",
        "extension": "<|--",
        "implementation": "<|..",
        "composition": "*--",
        "aggregation": "o--",
        "dependency": "..>",
        "line": "--",
        "dotted": "..",
    }
    base_arrow = arrow_map.get(rel.type, "--")

    # Build arrow with direction and style
    arrow = _build_arrow(base_arrow, rel.direction, rel.style)

    # Build the full relationship line
    parts: list[str] = [quote_ref(rel.source), arrow, quote_ref(rel.target)]

    # Relationship label
    if rel.label:
        label = render_label(rel.label)
        parts.append(f": {label}")

    lines.append(f"{prefix}{' '.join(parts)}")

    # Note on link
    if rel.note:
        note_text = render_label(rel.note)
        if "\n" in note_text:
            lines.append(f"{prefix}note on link")
            for note_line in note_text.split("\n"):
                lines.append(f"{prefix}  {note_line}")
            lines.append(f"{prefix}end note")
        else:
            lines.append(f"{prefix}note on link: {note_text}")

    return lines


def _build_arrow(base_arrow: str, direction: str | None, style) -> str:
    """Build arrow with direction and style modifiers."""
    # Direction modifier (first letter: u, d, l, r)
    dir_mod = ""
    if direction:
        dir_mod = direction[0]

    # Style modifier
    style_mod = ""
    if style:
        style_mod = render_line_style_bracket(style)

    # Build the modified arrow
    # For arrows like --> or ->
    if "->" in base_arrow:
        prefix_part = base_arrow.replace("->", "")
        if style_mod or dir_mod:
            return f"{prefix_part}-{style_mod}{dir_mod}->"
        return base_arrow

    # For dotted arrows like ..>
    if ".>" in base_arrow:
        prefix_part = base_arrow.replace(".>", "")
        if style_mod or dir_mod:
            return f"{prefix_part}.{style_mod}{dir_mod}.>"
        return base_arrow

    # For lines like -- or composition/aggregation
    if "--" in base_arrow:
        prefix_part = base_arrow.replace("--", "")
        if style_mod or dir_mod:
            return f"{prefix_part}-{style_mod}{dir_mod}-"
        return base_arrow

    # For dotted lines like ..
    if ".." in base_arrow:
        prefix_part = base_arrow.replace("..", "")
        if style_mod or dir_mod:
            return f"{prefix_part}.{style_mod}{dir_mod}."
        return base_arrow

    return base_arrow


def _render_note(note: ObjectNote, indent: int = 0) -> list[str]:
    """Render a note."""
    prefix = "  " * indent
    content = render_label(note.content)

    if note.target:
        pos = f"note {note.position} of {note.target}"
    else:
        pos = f"note {note.position}"

    color_part = ""
    if note.color:
        color = render_color(note.color)
        if not color.startswith("#"):
            color = f"#{color}"
        color_part = f" {color}"

    if "\n" in content:
        lines = [f"{prefix}{pos}{color_part}"]
        for line in content.split("\n"):
            lines.append(f"{prefix}  {line}")
        lines.append(f"{prefix}end note")
        return lines

    return [f"{prefix}{pos}{color_part}: {content}"]
