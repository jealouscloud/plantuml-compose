"""Use case diagram renderer.

Pure functions that transform use case diagram primitives to PlantUML text.
"""

from __future__ import annotations

from ..primitives.usecase import (
    Actor,
    Container,
    Relationship,
    UseCase,
    UseCaseDiagram,
    UseCaseDiagramElement,
    UseCaseNote,
)
from .common import escape_quotes, render_color, render_label, render_stereotype


def render_usecase_diagram(diagram: UseCaseDiagram) -> str:
    """Render a complete use case diagram to PlantUML text."""
    lines: list[str] = ["@startuml"]

    if diagram.title:
        if "\n" in diagram.title:
            lines.append("title")
            for title_line in diagram.title.split("\n"):
                lines.append(f"  {escape_quotes(title_line)}")
            lines.append("end title")
        else:
            lines.append(f"title {escape_quotes(diagram.title)}")

    if diagram.left_to_right:
        lines.append("left to right direction")

    if diagram.actor_style and diagram.actor_style != "default":
        lines.append(f"skinparam actorStyle {diagram.actor_style}")

    for elem in diagram.elements:
        lines.extend(_render_element(elem))

    lines.append("@enduml")
    return "\n".join(lines)


def _render_element(elem: UseCaseDiagramElement, indent: int = 0) -> list[str]:
    """Render a single diagram element."""
    prefix = "  " * indent

    if isinstance(elem, Actor):
        return [f"{prefix}{_render_actor(elem)}"]
    if isinstance(elem, UseCase):
        return [f"{prefix}{_render_usecase(elem)}"]
    if isinstance(elem, Container):
        return _render_container(elem, indent)
    if isinstance(elem, Relationship):
        return [f"{prefix}{_render_relationship(elem)}"]
    if isinstance(elem, UseCaseNote):
        return _render_note(elem, indent)
    raise TypeError(f"Unknown element type: {type(elem).__name__}")


def _render_actor(actor: Actor) -> str:
    """Render an actor."""
    parts: list[str] = []

    # Actor type with optional business variant
    keyword = "actor/" if actor.business else "actor"
    parts.append(keyword)

    # Name
    name = f'"{escape_quotes(actor.name)}"' if _needs_quotes(actor.name) else actor.name
    parts.append(name)

    if actor.alias:
        parts.append(f"as {actor.alias}")

    if actor.stereotype:
        parts.append(render_stereotype(actor.stereotype))

    if actor.color:
        color = render_color(actor.color)
        if not color.startswith("#"):
            color = f"#{color}"
        parts.append(color)

    return " ".join(parts)


def _render_usecase(usecase: UseCase) -> str:
    """Render a use case."""
    parts: list[str] = []

    # Usecase type with optional business variant
    keyword = "usecase/" if usecase.business else "usecase"
    parts.append(keyword)

    # Name (use cases are typically in parentheses in PlantUML syntax)
    name = f'"{escape_quotes(usecase.name)}"' if _needs_quotes(usecase.name) else usecase.name
    parts.append(f"({name})")

    if usecase.alias:
        parts.append(f"as {usecase.alias}")

    if usecase.stereotype:
        parts.append(render_stereotype(usecase.stereotype))

    if usecase.color:
        color = render_color(usecase.color)
        if not color.startswith("#"):
            color = f"#{color}"
        parts.append(color)

    return " ".join(parts)


def _render_container(container: Container, indent: int = 0) -> list[str]:
    """Render a container (rectangle/package)."""
    prefix = "  " * indent
    lines: list[str] = []

    parts: list[str] = [container.type]

    name = f'"{escape_quotes(container.name)}"' if _needs_quotes(container.name) else container.name
    parts.append(name)

    if container.stereotype:
        parts.append(render_stereotype(container.stereotype))

    if container.color:
        color = render_color(container.color)
        if not color.startswith("#"):
            color = f"#{color}"
        parts.append(color)

    parts.append("{")
    lines.append(f"{prefix}{' '.join(parts)}")

    for elem in container.elements:
        lines.extend(_render_element(elem, indent + 1))

    lines.append(f"{prefix}}}")
    return lines


def _render_relationship(rel: Relationship) -> str:
    """Render a relationship."""
    # Get the arrow based on type
    arrow_map = {
        "association": "->",
        "arrow": "-->",
        "extension": "<|--",
        "include": ".>",
        "extends": ".>",
        "dependency": "..>",
        "line": "--",
    }
    arrow = arrow_map.get(rel.type, "->")

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

    # Build the full relationship line
    parts: list[str] = [rel.source, arrow, rel.target]

    # Relationship label
    if rel.label:
        label = render_label(rel.label)
        parts.append(f": {label}")
    elif rel.type == "include":
        parts.append(": <<include>>")
    elif rel.type == "extends":
        parts.append(": <<extends>>")

    return " ".join(parts)


def _render_note(note: UseCaseNote, indent: int = 0) -> list[str]:
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
