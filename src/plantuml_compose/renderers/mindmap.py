"""MindMap diagram renderers.

Pure functions that transform MindMap diagram primitives to PlantUML text.
"""

from __future__ import annotations

from ..primitives.common import MindMapDiagramStyle
from ..primitives.mindmap import MindMapDiagram, MindMapNode
from .common import render_color, render_diagram_style


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
        _render_node_recursive(root, depth=1, lines=lines)

    lines.append("@endmindmap")
    return "\n".join(lines)


def _render_node_recursive(
    node: MindMapNode,
    depth: int,
    lines: list[str],
) -> None:
    """Recursively render a node and all its children."""
    lines.append(_render_node(node, depth))
    for child in node.children:
        _render_node_recursive(child, depth + 1, lines)


def _render_node(node: MindMapNode, depth: int) -> str:
    """Render a single MindMapNode to PlantUML syntax."""
    # Determine prefix based on side (OrgMode vs arithmetic notation)
    if node.side == "right":
        prefix = "+" * depth
    elif node.side == "left":
        prefix = "-" * depth
    else:
        # OrgMode syntax
        prefix = "*" * depth

    # Color (must come before boxless modifier)
    color_part = f"[{render_color(node.color)}]" if node.color else ""

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
