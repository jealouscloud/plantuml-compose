"""Deployment diagram renderer.

Pure functions that transform deployment diagram primitives to PlantUML text.
"""

from __future__ import annotations

from ..primitives.deployment import (
    DeploymentDiagram,
    DeploymentDiagramElement,
    DeploymentElement,
    DeploymentNote,
    Relationship,
)
from .common import escape_quotes, render_color, render_label, render_stereotype


def render_deployment_diagram(diagram: DeploymentDiagram) -> str:
    """Render a complete deployment diagram to PlantUML text."""
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


def _render_element(elem: DeploymentDiagramElement, indent: int = 0) -> list[str]:
    """Render a single diagram element."""
    prefix = "  " * indent

    if isinstance(elem, DeploymentElement):
        return _render_deployment_element(elem, indent)
    if isinstance(elem, Relationship):
        return [f"{prefix}{_render_relationship(elem)}"]
    if isinstance(elem, DeploymentNote):
        return _render_note(elem, indent)
    raise TypeError(f"Unknown element type: {type(elem).__name__}")


def _render_deployment_element(elem: DeploymentElement, indent: int = 0) -> list[str]:
    """Render a deployment element."""
    prefix = "  " * indent
    lines: list[str] = []

    parts: list[str] = [elem.type]

    # Name with possible alias
    name = f'"{escape_quotes(elem.name)}"' if _needs_quotes(elem.name) else elem.name
    parts.append(name)

    if elem.alias:
        parts.append(f"as {elem.alias}")

    if elem.stereotype:
        parts.append(render_stereotype(elem.stereotype))

    if elem.color:
        color = render_color(elem.color)
        if not color.startswith("#"):
            color = f"#{color}"
        parts.append(color)

    if elem.elements:
        lines.append(f"{prefix}{' '.join(parts)} {{")
        for inner in elem.elements:
            lines.extend(_render_element(inner, indent + 1))
        lines.append(f"{prefix}}}")
    else:
        lines.append(f"{prefix}{' '.join(parts)}")

    return lines


def _render_relationship(rel: Relationship) -> str:
    """Render a relationship between elements."""
    # Build arrow based on type
    arrow_map = {
        "association": "--",
        "dependency": "..>",
        "arrow": "-->",
        "dotted_arrow": "..>",
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


def _render_note(note: DeploymentNote, indent: int = 0) -> list[str]:
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
