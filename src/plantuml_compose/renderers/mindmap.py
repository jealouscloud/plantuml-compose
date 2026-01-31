"""MindMap diagram renderers.

Pure functions that transform MindMap diagram primitives to PlantUML text.
"""

from __future__ import annotations

from ..primitives.common import MindMapDiagramStyle
from ..primitives.mindmap import MindMapDiagram, MindMapNode
from .common import render_diagram_style


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

    # Nodes
    for node in diagram.nodes:
        lines.append(_render_node(node))

    lines.append("@endmindmap")
    return "\n".join(lines)


def _render_node(node: MindMapNode) -> str:
    """Render a single MindMapNode to PlantUML syntax."""
    # Determine prefix based on side (OrgMode vs arithmetic notation)
    if node.side == "right":
        prefix = "+" * node.depth
    elif node.side == "left":
        prefix = "-" * node.depth
    else:
        # OrgMode syntax
        prefix = "*" * node.depth

    # Color (must come before boxless modifier)
    color_part = f"[{node.color}]" if node.color else ""

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
