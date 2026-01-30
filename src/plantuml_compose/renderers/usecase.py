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
from .common import (
    escape_quotes,
    needs_quotes,
    quote_ref,
    render_caption,
    render_color,
    render_footer,
    render_header,
    render_label,
    render_layout_direction,
    render_legend,
    render_line_style_bracket,
    render_scale,
    render_stereotype,
    render_theme,
)


def render_usecase_diagram(diagram: UseCaseDiagram) -> str:
    """Render a complete use case diagram to PlantUML text."""
    lines: list[str] = ["@startuml"]

    # Theme comes first
    theme_line = render_theme(diagram.theme)
    if theme_line:
        lines.append(theme_line)

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

    # Layout direction
    layout_line = render_layout_direction(diagram.layout)
    if layout_line:
        lines.append(layout_line)

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
        return _render_relationship(elem, indent)
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
    name = (
        f'"{escape_quotes(actor.name)}"'
        if needs_quotes(actor.name)
        else actor.name
    )
    parts.append(name)

    if actor.alias:
        parts.append(f"as {actor.alias}")
    elif actor._ref != actor.name:
        # Add implicit alias when ref differs from name to prevent duplicates in containers
        parts.append(f"as {actor._ref}")

    if actor.stereotype:
        parts.append(render_stereotype(actor.stereotype))

    # Style background as element color
    if actor.style and actor.style.background:
        color = render_color(actor.style.background)
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
    name = (
        f'"{escape_quotes(usecase.name)}"'
        if needs_quotes(usecase.name)
        else usecase.name
    )
    parts.append(f"({name})")

    if usecase.alias:
        parts.append(f"as {usecase.alias}")
    elif usecase._ref != usecase.name:
        # Add implicit alias when ref differs from name to prevent duplicates in containers
        parts.append(f"as {usecase._ref}")

    if usecase.stereotype:
        parts.append(render_stereotype(usecase.stereotype))

    # Style background as element color
    if usecase.style and usecase.style.background:
        color = render_color(usecase.style.background)
        if not color.startswith("#"):
            color = f"#{color}"
        parts.append(color)

    return " ".join(parts)


def _render_container(container: Container, indent: int = 0) -> list[str]:
    """Render a container (rectangle/package)."""
    prefix = "  " * indent
    lines: list[str] = []

    parts: list[str] = [container.type]

    name = (
        f'"{escape_quotes(container.name)}"'
        if needs_quotes(container.name)
        else container.name
    )
    parts.append(name)

    if container.stereotype:
        parts.append(render_stereotype(container.stereotype))

    # Style background as element color
    if container.style and container.style.background:
        color = render_color(container.style.background)
        if not color.startswith("#"):
            color = f"#{color}"
        parts.append(color)

    parts.append("{")
    lines.append(f"{prefix}{' '.join(parts)}")

    for elem in container.elements:
        lines.extend(_render_element(elem, indent + 1))

    lines.append(f"{prefix}}}")
    return lines


def _render_relationship(rel: Relationship, indent: int = 0) -> list[str]:
    """Render a relationship."""
    prefix = "  " * indent
    lines: list[str] = []

    # Get the base arrow based on type
    arrow_map = {
        "association": "->",
        "arrow": "-->",
        "extension": "<|--",
        "include": ".>",
        "extends": ".>",
        "dependency": "..>",
        "line": "--",
    }
    base_arrow = arrow_map.get(rel.type, "->")

    # Build arrow with direction and style
    arrow = _build_arrow(base_arrow, rel.direction, rel.style)

    # Build the full relationship line
    parts: list[str] = [quote_ref(rel.source), arrow, quote_ref(rel.target)]

    # Relationship label
    if rel.label:
        label = render_label(rel.label, inline=True)
        parts.append(f": {label}")
    elif rel.type == "include":
        parts.append(": <<include>>")
    elif rel.type == "extends":
        parts.append(": <<extends>>")

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
    # For arrows like -> or -->
    if "->" in base_arrow:
        prefix_part = base_arrow.replace("->", "")
        if style_mod or dir_mod:
            return f"{prefix_part}-{style_mod}{dir_mod}->"
        return base_arrow

    # For dotted arrows like .>
    if ".>" in base_arrow:
        if style_mod or dir_mod:
            return f".{style_mod}{dir_mod}.>"
        return base_arrow

    # For lines like --
    if base_arrow == "--":
        if style_mod or dir_mod:
            return f"-{style_mod}{dir_mod}-"
        return base_arrow

    return base_arrow


def _render_note(note: UseCaseNote, indent: int = 0) -> list[str]:
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
