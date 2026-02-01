"""Class diagram renderer.

Pure functions that transform class diagram primitives to PlantUML text.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..primitives.class_ import (
    AssociationClass,
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
    _VISIBILITY_TO_SYMBOL,
)
from ..primitives.common import (
    ClassDiagramStyle,
    Note,
    Style,
    coerce_line_style,
    coerce_style,
)
from .common import (
    escape_quotes,
    quote_ref,
    render_caption,
    render_color_bare,
    render_color_hash,
    render_diagram_style,
    render_footer,
    render_header,
    render_label,
    render_layout_direction,
    render_layout_engine,
    render_legend,
    render_line_style_bracket,
    render_linetype,
    render_scale,
    render_stereotype,
    render_theme,
)


@dataclass
class _RenderContext:
    """Mutable context for tracking state during rendering."""

    note_counter: int = 0

    def next_note_alias(self) -> str:
        """Generate the next unique note alias."""
        self.note_counter += 1
        return f"N{self.note_counter}"


def render_class_diagram(diagram: ClassDiagram) -> str:
    """Render a complete class diagram to PlantUML text."""
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

    # Layout engine pragma
    engine_line = render_layout_engine(diagram.layout_engine)
    if engine_line:
        lines.append(engine_line)

    # Line routing style
    linetype_line = render_linetype(diagram.linetype)
    if linetype_line:
        lines.append(linetype_line)

    # Diagram-wide CSS styling
    if diagram.diagram_style:
        lines.extend(_render_class_diagram_style(diagram.diagram_style))

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
    ctx = _RenderContext()
    for elem in diagram.elements:
        lines.extend(_render_element(elem, ctx))

    lines.append("@enduml")
    return "\n".join(lines)


def _render_element(
    elem: ClassDiagramElement, ctx: _RenderContext
) -> list[str]:
    """Render a single diagram element."""
    if isinstance(elem, ClassNode):
        return _render_class_node(elem)
    if isinstance(elem, Relationship):
        return _render_relationship(elem)
    if isinstance(elem, AssociationClass):
        return _render_association_class(elem)
    if isinstance(elem, Package):
        return _render_package(elem, ctx)
    if isinstance(elem, Together):
        return _render_together(elem, ctx)
    if isinstance(elem, ClassNote):
        return _render_class_note(elem)
    if isinstance(elem, HideShow):
        return [f"{elem.action} {elem.target}"]
    if isinstance(elem, Note):
        return _render_floating_note(elem, ctx)
    raise TypeError(f"Unknown element type: {type(elem).__name__}")


def _render_class_inline_style(style: Style | dict) -> str:
    """Render inline style for a class node.

    PlantUML supports:
      - Simple: #E3F2FD (just background color)
      - Full: #back:E3F2FD;line:1976D2 (background and line)
      - With text: #back:E3F2FD;line:1976D2;text:333333

    Note: Colors in back:/line:/text: syntax must NOT have # prefix.
    """
    style_obj = coerce_style(style)

    # Collect style parts (render_color_bare returns without #)
    parts: list[str] = []

    if style_obj.background:
        parts.append(f"back:{render_color_bare(style_obj.background)}")

    if style_obj.line:
        line = coerce_line_style(style_obj.line)
        if line.color:
            parts.append(f"line:{render_color_bare(line.color)}")

    if style_obj.text_color:
        parts.append(f"text:{render_color_bare(style_obj.text_color)}")

    if not parts:
        return ""

    # Simple case: just background color, use short form (#color)
    if len(parts) == 1 and parts[0].startswith("back:"):
        bg = parts[0][5:]  # Remove "back:" prefix
        return f"#{bg}"

    # Full form with multiple properties (#back:color;line:color)
    return f"#{';'.join(parts)}"


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

    # Inline style (background color, line color)
    if node.style:
        decl += f" {_render_class_inline_style(node.style)}"

    # Enum values (multiline syntax required by PlantUML)
    if node.type == "enum" and node.enum_values and not node.members:
        lines.append(f"{decl} {{")
        for value in node.enum_values:
            lines.append(f"  {value}")
        lines.append("}")
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

    # Visibility (convert human-readable name to UML symbol)
    if member.visibility:
        parts.append(_VISIBILITY_TO_SYMBOL[member.visibility])

    # Name and type
    if member.type:
        if member.is_method:
            parts.append(f"{member.name} : {member.type}")
        else:
            parts.append(f"{member.name} : {member.type}")
    else:
        parts.append(member.name)

    return (
        " ".join(parts)
        if len(parts) > 1 and member.modifier
        else "".join(parts)
    )


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


def _render_relationship(rel: Relationship) -> list[str]:
    """Render a relationship between classes."""
    lines: list[str] = []

    # Build arrow based on relationship type
    arrow = _build_relationship_arrow(rel)

    # PlantUML syntax: source [qualifier] --> "label" target : label
    # Note: qualifier replaces source_label - they can't both be used
    parts: list[str] = [quote_ref(rel.source)]

    # Qualified association: adds a qualifier box at the source end
    # This replaces the source_label position
    if rel.qualifier:
        parts.append(f"[{rel.qualifier}]")
    elif rel.source_label:
        parts.append(f'"{rel.source_label}"')

    parts.append(arrow)

    if rel.target_label:
        parts.append(f'"{rel.target_label}"')

    parts.append(quote_ref(rel.target))

    # Relationship label (on the line)
    if rel.label:
        label_text = render_label(rel.label, inline=True)
        if rel.label_direction:
            label_text += f" {rel.label_direction}"
        parts.append(f": {label_text}")

    lines.append(" ".join(parts))

    # Note on link (must immediately follow the relationship)
    if rel.note:
        note_text = render_label(rel.note)
        if "\n" in note_text:
            lines.append("note on link")
            for line in note_text.split("\n"):
                lines.append(f"  {line}")
            lines.append("end note")
        else:
            lines.append(f"note on link : {note_text}")

    return lines


def _render_association_class(assoc: AssociationClass) -> list[str]:
    """Render an association class link.

    PlantUML syntax: (ClassA, ClassB) .. AssociationClass
    This links the AssociationClass to the relationship between ClassA and ClassB.
    """
    source = quote_ref(assoc.source)
    target = quote_ref(assoc.target)
    assoc_class = quote_ref(assoc.association_class)
    return [f"({source}, {target}) .. {assoc_class}"]


def _build_relationship_arrow(rel: Relationship) -> str:
    """Build the arrow string for a relationship."""
    # Direction modifier
    dir_mod = ""
    if rel.direction:
        dir_mod = rel.direction[0]  # First letter: u, d, l, r

    # Style modifier (bracket syntax)
    style_mod = ""
    if rel.style:
        style_mod = render_line_style_bracket(rel.style)

    # Handle lollipop interface specially (single dash, different syntax)
    # PlantUML syntax: bar ()- Foo
    if rel.type == "lollipop":
        if style_mod and dir_mod:
            return f"(){style_mod}{dir_mod}-"
        elif style_mod:
            return f"(){style_mod}-"
        elif dir_mod:
            return f"()-{dir_mod}-"
        return "()-"

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

    # Build arrow with direction and style modifiers
    # PlantUML syntax: A -[style,dir]-> B
    if "--" in base_arrow:
        idx = base_arrow.index("--")
        head = base_arrow[:idx]  # e.g., "<|", "*", "o", "", "-"
        tail = base_arrow[idx + 2 :]  # e.g., "", ">", ""
        # Build middle part with style and direction
        if style_mod and dir_mod:
            # Both: -[style,dir]-
            middle = f"-{style_mod}{dir_mod}-"
        elif style_mod:
            # Style only: -[style]-
            middle = f"-{style_mod}-"
        elif dir_mod:
            # Direction only: -dir-
            middle = f"-{dir_mod}-"
        else:
            middle = "--"
        return f"{head}{middle}{tail}"
    elif ".." in base_arrow:
        idx = base_arrow.index("..")
        head = base_arrow[:idx]  # e.g., "<|", ""
        tail = base_arrow[idx + 2 :]  # e.g., "", ">"
        # Build middle part with style and direction
        if style_mod and dir_mod:
            middle = f".{style_mod}{dir_mod}."
        elif style_mod:
            middle = f".{style_mod}."
        elif dir_mod:
            middle = f".{dir_mod}."
        else:
            middle = ".."
        return f"{head}{middle}{tail}"

    return base_arrow


def _render_package(pkg: Package, ctx: _RenderContext) -> list[str]:
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
        parts.append(render_color_hash(pkg.color))

    lines.append(f"{' '.join(parts)} {{")

    # Elements
    for elem in pkg.elements:
        for line in _render_element(elem, ctx):
            lines.append(f"  {line}")

    lines.append("}")
    return lines


def _render_together(together: Together, ctx: _RenderContext) -> list[str]:
    """Render a together block."""
    lines: list[str] = ["together {"]

    for elem in together.elements:
        for line in _render_element(elem, ctx):
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


def _render_floating_note(note: Note, ctx: _RenderContext) -> list[str]:
    """Render a floating note."""
    content = render_label(note.content)
    alias = ctx.next_note_alias()

    if "\n" in content:
        lines = [f"note as {alias}"]
        for line in content.split("\n"):
            lines.append(f"  {line}")
        lines.append("end note")
        return lines

    return [f'note "{content}" as {alias}']


def _render_class_diagram_style(style: ClassDiagramStyle) -> list[str]:
    """Render a ClassDiagramStyle to PlantUML <style> block."""
    return render_diagram_style(
        diagram_type="classDiagram",
        root_background=style.background,
        root_font_name=style.font_name,
        root_font_size=style.font_size,
        root_font_color=style.font_color,
        element_styles=[
            ("class", style.class_),
            ("interface", style.interface),
            ("abstract", style.abstract),
            ("enum", style.enum),
            ("annotation", style.annotation),
            ("package", style.package),
            ("note", style.note),
        ],
        arrow_style=style.arrow,
        title_style=style.title,
    )
