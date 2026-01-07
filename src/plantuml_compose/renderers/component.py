"""Component diagram renderer.

Pure functions that transform component diagram primitives to PlantUML text.
"""

from __future__ import annotations

from ..primitives.component import (
    Component,
    ComponentDiagram,
    ComponentElement,
    ComponentNote,
    Container,
    Interface,
    Port,
    Relationship,
)
from .common import (
    escape_quotes,
    needs_quotes,
    quote_ref,
    render_caption,
    render_color,
    render_element_style,
    render_footer,
    render_header,
    render_label,
    render_legend,
    render_line_style_bracket,
    render_scale,
    render_stereotype,
)


def render_component_diagram(diagram: ComponentDiagram) -> str:
    """Render a complete component diagram to PlantUML text."""
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

    if diagram.style:
        lines.append(f"skinparam componentStyle {diagram.style}")

    if diagram.hide_stereotype:
        lines.append("hide stereotype")

    for elem in diagram.elements:
        lines.extend(_render_element(elem))

    lines.append("@enduml")
    return "\n".join(lines)


def _render_element(elem: ComponentElement, indent: int = 0) -> list[str]:
    """Render a single diagram element."""
    prefix = "  " * indent

    if isinstance(elem, Component):
        return _render_component(elem, indent)
    if isinstance(elem, Interface):
        return [f"{prefix}{_render_interface(elem)}"]
    if isinstance(elem, Port):
        return [f"{prefix}{elem.direction} {elem.name}"]
    if isinstance(elem, Container):
        return _render_container(elem, indent)
    if isinstance(elem, Relationship):
        return _render_relationship(elem, indent)
    if isinstance(elem, ComponentNote):
        return _render_note(elem, indent)
    raise TypeError(f"Unknown element type: {type(elem).__name__}")


def _render_component(comp: Component, indent: int = 0) -> list[str]:
    """Render a component."""
    prefix = "  " * indent
    lines: list[str] = []

    # Build component declaration
    parts: list[str] = []

    if comp.type in ("port", "portin", "portout"):
        # Port syntax
        return [f"{prefix}{comp.type} {comp.name}"]

    # Regular component/interface
    parts.append("component")

    # Name with possible alias
    name = f'"{escape_quotes(comp.name)}"' if needs_quotes(comp.name) else comp.name
    parts.append(name)

    if comp.alias:
        parts.append(f"as {comp.alias}")

    if comp.stereotype:
        parts.append(render_stereotype(comp.stereotype))

    if comp.style:
        style_str = render_element_style(comp.style)
        if style_str:
            parts.append(style_str)

    if comp.elements:
        lines.append(f"{prefix}{' '.join(parts)} {{")
        for inner in comp.elements:
            lines.extend(_render_element(inner, indent + 1))
        lines.append(f"{prefix}}}")
    else:
        lines.append(f"{prefix}{' '.join(parts)}")

    return lines


def _render_interface(iface: Interface) -> str:
    """Render an interface."""
    parts: list[str] = []

    # Interface can use () syntax or interface keyword
    parts.append("interface")

    name = f'"{escape_quotes(iface.name)}"' if needs_quotes(iface.name) else iface.name
    parts.append(name)

    if iface.alias:
        parts.append(f"as {iface.alias}")

    if iface.stereotype:
        parts.append(render_stereotype(iface.stereotype))

    if iface.style:
        style_str = render_element_style(iface.style)
        if style_str:
            parts.append(style_str)

    return " ".join(parts)


def _render_container(container: Container, indent: int = 0) -> list[str]:
    """Render a container (package, node, folder, etc.)."""
    prefix = "  " * indent
    lines: list[str] = []

    # Build container opening
    parts: list[str] = [container.type]

    name = f'"{escape_quotes(container.name)}"' if needs_quotes(container.name) else container.name
    parts.append(name)

    if container.stereotype:
        parts.append(render_stereotype(container.stereotype))

    if container.style:
        style_str = render_element_style(container.style)
        if style_str:
            parts.append(style_str)

    parts.append("{")
    lines.append(f"{prefix}{' '.join(parts)}")

    for elem in container.elements:
        lines.extend(_render_element(elem, indent + 1))

    lines.append(f"{prefix}}}")
    return lines


def _render_relationship(rel: Relationship, indent: int = 0) -> list[str]:
    """Render a relationship between components."""
    prefix = "  " * indent
    lines: list[str] = []

    # Build arrow based on type with direction and style
    arrow = _build_arrow(rel)

    # Build the full relationship line
    parts: list[str] = [quote_ref(rel.source)]

    # Source label
    if rel.source_label:
        parts.append(f'"{rel.source_label}"')

    parts.append(arrow)

    # Target label
    if rel.target_label:
        parts.append(f'"{rel.target_label}"')

    parts.append(quote_ref(rel.target))

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


def _build_arrow(rel: Relationship) -> str:
    """Build the arrow string for a relationship."""
    # Get base arrow for type
    base = _get_arrow_for_type(rel.type, rel.left_head, rel.right_head)

    # Direction modifier (first letter: u, d, l, r)
    dir_mod = rel.direction[0] if rel.direction else ""

    # Style modifier [#color,pattern,thickness=N]
    style_mod = ""
    if rel.style:
        style_mod = render_line_style_bracket(rel.style)

    # If no modifiers, return base arrow
    if not style_mod and not dir_mod:
        return base

    # Insert modifiers into arrow
    # Arrows can be: -->, ..>, --(, )--, --, ..
    if "->" in base:
        # Solid arrow: --> becomes -[style]dir->
        return base.replace("->", f"-{style_mod}{dir_mod}->")
    if ".>" in base:
        # Dotted arrow: ..> becomes .[style]dir.>
        return base.replace(".>", f".{style_mod}{dir_mod}.>")
    if "--(" in base:
        # Provides: --( becomes -[style]dir-(
        return base.replace("-(", f"-{style_mod}{dir_mod}-(")
    if ")--" in base:
        # Requires: )-- becomes )-[style]dir-
        return base.replace(")-", f"){style_mod}{dir_mod}-")
    if "--" in base:
        # Plain line: -- becomes -[style]dir-
        return base.replace("--", f"-{style_mod}{dir_mod}-")
    if ".." in base:
        # Dotted line: .. becomes .[style]dir.
        return base.replace("..", f".{style_mod}{dir_mod}.")

    return base


def _get_arrow_for_type(rel_type: str, left_head: str | None, right_head: str | None) -> str:
    """Get the arrow string for a relationship type."""
    base_arrows = {
        "provides": "--(",
        "requires": ")--",
        "dependency": "..>",
        "association": "--",
        "line": "--",
        "dotted": "..",
        "arrow": "-->",
        "dotted_arrow": "..>",
    }
    arrow = base_arrows.get(rel_type, "--")

    # Apply custom heads if specified
    if left_head or right_head:
        if ".." in arrow:
            base = ".."
            has_arrow = ">" in arrow
        else:
            base = "--"
            has_arrow = ">" in arrow

        left = left_head or ""
        right = right_head or (">" if has_arrow else "")
        arrow = f"{left}{base}{right}"

    return arrow


def _render_note(note: ComponentNote, indent: int = 0) -> list[str]:
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
