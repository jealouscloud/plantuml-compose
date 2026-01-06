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
from .common import escape_quotes, render_color, render_label, render_stereotype


def render_object_diagram(diagram: ObjectDiagram) -> str:
    """Render a complete object diagram to PlantUML text."""
    lines: list[str] = ["@startuml"]

    if diagram.title:
        if "\n" in diagram.title:
            lines.append("title")
            for title_line in diagram.title.split("\n"):
                lines.append(f"  {escape_quotes(title_line)}")
            lines.append("end title")
        else:
            lines.append(f"title {escape_quotes(diagram.title)}")

    for elem in diagram.elements:
        lines.extend(_render_element(elem))

    lines.append("@enduml")
    return "\n".join(lines)


def _render_element(elem: ObjectDiagramElement, indent: int = 0) -> list[str]:
    """Render a single diagram element."""
    prefix = "  " * indent

    if isinstance(elem, Object):
        return _render_object(elem, indent)
    if isinstance(elem, Map):
        return _render_map(elem, indent)
    if isinstance(elem, Relationship):
        return [f"{prefix}{_render_relationship(elem)}"]
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
        name = f'"{escape_quotes(obj.name)}"' if _needs_quotes(obj.name) else obj.name
        parts.append(name)

    if obj.stereotype:
        parts.append(render_stereotype(obj.stereotype))

    if obj.color:
        color = render_color(obj.color)
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
        name = f'"{escape_quotes(map_obj.name)}"' if _needs_quotes(map_obj.name) else map_obj.name
        parts.append(name)

    if map_obj.color:
        color = render_color(map_obj.color)
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


def _render_relationship(rel: Relationship) -> str:
    """Render a relationship."""
    # Get the arrow based on type
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
    arrow = arrow_map.get(rel.type, "--")

    # Add color if specified
    if rel.color:
        color = render_color(rel.color)
        if not color.startswith("#"):
            color = f"#{color}"
        # Insert color into arrow
        if "->" in arrow:
            arrow = arrow.replace("->", f"-[{color}]->")
        elif ".>" in arrow:
            arrow = arrow.replace(".>", f".[{color}].>")
        elif "--" in arrow:
            arrow = arrow.replace("--", f"-[{color}]-")
        elif ".." in arrow:
            arrow = arrow.replace("..", f".[{color}].")

    # Build the full relationship line
    parts: list[str] = [rel.source, arrow, rel.target]

    # Relationship label
    if rel.label:
        label = render_label(rel.label)
        parts.append(f": {label}")

    return " ".join(parts)


def _render_note(note: ObjectNote, indent: int = 0) -> list[str]:
    """Render a note."""
    prefix = "  " * indent
    content = render_label(note.content)

    pos = note.position
    if note.floating:
        pos = f"floating note {pos}"
    elif note.target:
        pos = f"note {pos} of {note.target}"
    else:
        pos = f"note {pos}"

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


def _needs_quotes(name: str) -> bool:
    """Check if a name needs to be quoted."""
    if not name:
        return True
    if not name[0].isalpha() and name[0] != "_":
        return True
    for char in name:
        if not (char.isalnum() or char == "_"):
            return True
    return False
