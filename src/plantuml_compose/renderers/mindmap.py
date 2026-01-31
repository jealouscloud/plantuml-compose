"""MindMap diagram renderers.

Pure functions that transform MindMap diagram primitives to PlantUML text.
"""

from __future__ import annotations

from typing import Literal

from ..primitives.common import MindMapDiagramStyle
from ..primitives.mindmap import MindMapDiagram, MindMapNode
from .common import render_color_hash, render_diagram_style

Side = Literal["left", "right"] | None


def render_mindmap_diagram(diagram: MindMapDiagram) -> str:
    """Render a complete MindMap diagram to PlantUML text."""
    lines: list[str] = ["@startmindmap"]

    # Style block
    if diagram.diagram_style:
        lines.extend(_render_mindmap_diagram_style(diagram.diagram_style))

    # Direction
    if diagram.direction:
        direction_str = diagram.direction.replace("_", " ") + " direction"
        lines.append(direction_str)

    # Render all root nodes and their children
    for root in diagram.roots:
        _render_node_recursive(root, depth=1, lines=lines, inherited_side=None)

    lines.append("@endmindmap")
    return "\n".join(lines)


def _render_node_recursive(
    node: MindMapNode,
    depth: int,
    lines: list[str],
    inherited_side: Side,
) -> None:
    """Recursively render a node and all its children."""
    # Determine effective side: node's own side, or inherited from parent
    effective_side = node.side if node.side else inherited_side
    lines.append(_render_node(node, depth, effective_side))
    for child in node.children:
        _render_node_recursive(child, depth + 1, lines, effective_side)


def _render_node(node: MindMapNode, depth: int, effective_side: Side) -> str:
    """Render a single MindMapNode to PlantUML syntax."""
    # Determine prefix based on side (OrgMode vs arithmetic notation)
    if effective_side == "right":
        prefix = "+" * depth
    elif effective_side == "left":
        prefix = "-" * depth
    else:
        # OrgMode syntax
        prefix = "*" * depth

    # Color (must come before boxless modifier)
    color_part = f"[{render_color_hash(node.color)}]" if node.color else ""

    # Boxless modifier (comes after color)
    boxless_part = "_" if node.boxless else ""

    # Handle multiline text
    if "\n" in node.text:
        # Multiline syntax: *[#color]_:text\nmore;
        return f"{prefix}{color_part}{boxless_part}:{node.text};"
    else:
        return f"{prefix}{color_part}{boxless_part} {node.text}"


def _render_mindmap_diagram_style(style: MindMapDiagramStyle) -> list[str]:
    """Render a MindMapDiagramStyle to PlantUML <style> block."""
    return render_diagram_style(
        diagram_type="mindmapDiagram",
        root_background=style.background,
        root_font_name=style.font_name,
        root_font_size=style.font_size,
        root_font_color=style.font_color,
        element_styles=[
            ("node", style.node),
            ("rootNode", style.root_node),
            ("leafNode", style.leaf_node),
        ],
        arrow_style=style.arrow,
        title_style=None,
    )
