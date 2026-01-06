"""Class diagram renderer.

Pure functions that transform class diagram primitives to PlantUML text.
"""

from __future__ import annotations

from ..primitives.class_ import (
    ClassDiagram,
    ClassDiagramElement,
    ClassNode,
    ClassNote,
    HideShow,
    Member,
    Package,
    Relationship,
    Separator,
    Together,
)
from ..primitives.common import Note
from .common import escape_quotes, render_color, render_label, render_stereotype


def render_class_diagram(diagram: ClassDiagram) -> str:
    """Render a complete class diagram to PlantUML text."""
    lines: list[str] = ["@startuml"]

    if diagram.title:
        if "\n" in diagram.title:
            lines.append("title")
            for title_line in diagram.title.split("\n"):
                lines.append(f"  {escape_quotes(title_line)}")
            lines.append("end title")
        else:
            lines.append(f"title {escape_quotes(diagram.title)}")

    # Namespace separator
    if diagram.namespace_separator is not None:
        if diagram.namespace_separator == "none":
            lines.append("set separator none")
        else:
            lines.append(f"set separator {diagram.namespace_separator}")

    # Hide directives
    if diagram.hide_empty_members:
        lines.append("hide empty members")
    if diagram.hide_circle:
        lines.append("hide circle")

    # Main elements
    for elem in diagram.elements:
        lines.extend(_render_element(elem))

    lines.append("@enduml")
    return "\n".join(lines)


def _render_element(elem: ClassDiagramElement) -> list[str]:
    """Render a single diagram element."""
    if isinstance(elem, ClassNode):
        return _render_class_node(elem)
    if isinstance(elem, Relationship):
        return [_render_relationship(elem)]
    if isinstance(elem, Package):
        return _render_package(elem)
    if isinstance(elem, Together):
        return _render_together(elem)
    if isinstance(elem, ClassNote):
        return _render_class_note(elem)
    if isinstance(elem, HideShow):
        return [f"{elem.action} {elem.target}"]
    if isinstance(elem, Note):
        return _render_floating_note(elem)
    raise TypeError(f"Unknown element type: {type(elem).__name__}")


def _render_class_node(node: ClassNode) -> list[str]:
    """Render a class node declaration."""
    lines: list[str] = []

    # Build class type keyword
    if node.type == "abstract":
        type_keyword = "abstract class"
    else:
        type_keyword = node.type

    # Build declaration
    name_part = node.name
    if node.generics:
        name_part += f"<{node.generics}>"

    # Alias
    if node.alias or not node.name.isidentifier():
        escaped = escape_quotes(node.name)
        if node.generics:
            decl = f'{type_keyword} "{escaped}<{node.generics}>" as {node._ref}'
        else:
            decl = f'{type_keyword} "{escaped}" as {node._ref}'
    else:
        decl = f"{type_keyword} {name_part}"

    # Stereotype
    if node.stereotype:
        decl += f" {render_stereotype(node.stereotype)}"

    # Enum values (shorthand syntax)
    if node.type == "enum" and node.enum_values and not node.members:
        values = ", ".join(node.enum_values)
        decl += f" {{ {values} }}"
        lines.append(decl)
        return lines

    # Members
    if node.members:
        lines.append(f"{decl} {{")
        for member in node.members:
            if isinstance(member, Member):
                lines.append(f"  {_render_member(member)}")
            elif isinstance(member, Separator):
                lines.append(f"  {_render_separator(member)}")
        lines.append("}")
    else:
        lines.append(decl)

    # Note
    if node.note:
        lines.extend(_render_attached_note(node.note, node._ref))

    return lines


def _render_member(member: Member) -> str:
    """Render a class member."""
    parts: list[str] = []

    # Modifier (static, abstract, etc.)
    if member.modifier:
        parts.append(f"{{{member.modifier}}}")

    # Visibility
    if member.visibility:
        parts.append(member.visibility)

    # Name and type
    if member.type:
        if member.is_method:
            parts.append(f"{member.name} : {member.type}")
        else:
            parts.append(f"{member.name} : {member.type}")
    else:
        parts.append(member.name)

    return " ".join(parts) if len(parts) > 1 and member.modifier else "".join(parts)


def _render_separator(sep: Separator) -> str:
    """Render a separator within a class."""
    style_map = {
        "solid": "--",
        "dotted": "..",
        "double": "==",
        "underline": "__",
    }
    marker = style_map[sep.style]
    if sep.label:
        return f"{marker} {sep.label} {marker}"
    return marker


def _render_relationship(rel: Relationship) -> str:
    """Render a relationship between classes."""
    # Build arrow based on relationship type
    arrow = _build_relationship_arrow(rel)

    # Build with cardinalities and label
    parts: list[str] = [rel.source]

    # Source cardinality
    if rel.source_cardinality:
        parts.append(f'"{rel.source_cardinality}"')

    parts.append(arrow)

    # Target cardinality
    if rel.target_cardinality:
        parts.append(f'"{rel.target_cardinality}"')

    parts.append(rel.target)

    # Label
    if rel.label:
        label_text = render_label(rel.label)
        if rel.label_direction:
            label_text += f" {rel.label_direction}"
        parts.append(f": {label_text}")

    return " ".join(parts)


def _build_relationship_arrow(rel: Relationship) -> str:
    """Build the arrow string for a relationship."""
    # Direction modifier
    dir_mod = ""
    if rel.direction:
        dir_mod = rel.direction[0]  # First letter: u, d, l, r

    # Relationship type to arrow mapping
    arrow_map = {
        "extension": "<|--",
        "implementation": "<|..",
        "composition": "*--",
        "aggregation": "o--",
        "association": "-->",
        "dependency": "..>",
        "line": "--",
        "dotted": "..",
    }
    base_arrow = arrow_map[rel.type]

    # Insert direction modifier if present
    if dir_mod and "--" in base_arrow:
        # For arrows like "<|--" or "*--", insert direction after first part
        idx = base_arrow.index("--")
        return base_arrow[:idx] + f"-{dir_mod}-"
    elif dir_mod and ".." in base_arrow:
        idx = base_arrow.index("..")
        return base_arrow[:idx] + f".{dir_mod}."

    return base_arrow


def _render_package(pkg: Package) -> list[str]:
    """Render a package with its elements."""
    lines: list[str] = []

    # Opening
    parts = ["package"]

    # Name
    if not pkg.name.isidentifier():
        parts.append(f'"{escape_quotes(pkg.name)}"')
    else:
        parts.append(pkg.name)

    # Alias
    if pkg.alias:
        parts.append(f"as {pkg.alias}")

    # Style (if not default)
    if pkg.style != "package":
        parts.append(f"<<{pkg.style.capitalize()}>>")

    # Color
    if pkg.color:
        color = render_color(pkg.color)
        if not color.startswith("#"):
            color = f"#{color}"
        parts.append(color)

    lines.append(f"{' '.join(parts)} {{")

    # Elements
    for elem in pkg.elements:
        for line in _render_element(elem):
            lines.append(f"  {line}")

    lines.append("}")
    return lines


def _render_together(together: Together) -> list[str]:
    """Render a together block."""
    lines: list[str] = ["together {"]

    for elem in together.elements:
        for line in _render_element(elem):
            lines.append(f"  {line}")

    lines.append("}")
    return lines


def _render_class_note(note: ClassNote) -> list[str]:
    """Render a note attached to a class or member."""
    content = render_label(note.content)

    # Position prefix
    if note.target:
        if note.member:
            # Note on specific member
            prefix = f"note {note.position} of {note.target}::{note.member}"
        else:
            prefix = f"note {note.position} of {note.target}"
    else:
        prefix = f"note {note.position}"

    if "\n" in content:
        lines = [prefix]
        for line in content.split("\n"):
            lines.append(f"  {line}")
        lines.append("end note")
        return lines

    return [f"{prefix}: {content}"]


def _render_attached_note(note: Note, target: str) -> list[str]:
    """Render a note attached to an element (from node.note)."""
    content = render_label(note.content)
    prefix = f"note {note.position} of {target}"

    if "\n" in content:
        lines = [prefix]
        for line in content.split("\n"):
            lines.append(f"  {line}")
        lines.append("end note")
        return lines

    return [f"{prefix}: {content}"]


def _render_floating_note(note: Note) -> list[str]:
    """Render a floating note."""
    content = render_label(note.content)

    if "\n" in content:
        lines = ["note as N"]
        for line in content.split("\n"):
            lines.append(f"  {line}")
        lines.append("end note")
        return lines

    return [f'note "{content}" as N']
