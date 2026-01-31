"""Work Breakdown Structure (WBS) diagram renderers.

Pure functions that transform WBS diagram primitives to PlantUML text.
"""

from __future__ import annotations

from typing import Literal

from ..primitives.wbs import WBSArrow, WBSDiagram, WBSDiagramStyle, WBSNode
from .common import render_color_hash, render_diagram_style

Side = Literal["left", "right"] | None


def render_wbs_diagram(diagram: WBSDiagram) -> str:
    """Render a complete WBS diagram to PlantUML text."""
    lines: list[str] = ["@startwbs"]

    # Style block
    if diagram.diagram_style:
        lines.extend(_render_wbs_diagram_style(diagram.diagram_style))

    # Note: WBS does NOT support diagram-wide direction like mindmap.
    # Individual node direction is controlled via side="left"/"right" on nodes,
    # which renders as <> markers. The direction field is ignored for WBS.

    # Render all root nodes and their children
    for root in diagram.roots:
        _render_node_recursive(root, depth=1, lines=lines, inherited_side=None)

    # Arrows between aliased nodes
    for arrow in diagram.arrows:
        lines.append(f"{arrow.from_alias} -> {arrow.to_alias}")

    lines.append("@endwbs")
    return "\n".join(lines)


def _render_node_recursive(
    node: WBSNode,
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


def _render_node(node: WBSNode, depth: int, effective_side: Side) -> str:
    """Render a single WBSNode to PlantUML syntax.

    PlantUML WBS syntax order: depth + boxless + direction + color + text
    Example: **_<[#Orange] text
    """
    # Base prefix (OrgMode style)
    prefix = "*" * depth

    # Boxless modifier (must come before direction marker)
    if node.boxless:
        prefix += "_"

    # Direction marker (WBS-specific: comes after boxless)
    if effective_side == "left":
        prefix += "<"
    elif effective_side == "right":
        prefix += ">"

    # Color (comes after direction)
    color_part = f"[{render_color_hash(node.color)}]" if node.color else ""

    # Alias (shown as: "Text" as alias)
    if node.alias:
        text_part = f'"{node.text}" as {node.alias}'
    else:
        text_part = node.text

    # Handle multiline text (only if no alias - aliases don't support multiline)
    if "\n" in node.text and not node.alias:
        return f"{prefix}{color_part}:{text_part};"
    else:
        return f"{prefix}{color_part} {text_part}"


def _render_wbs_diagram_style(style: WBSDiagramStyle) -> list[str]:
    """Render a WBSDiagramStyle to PlantUML <style> block."""
    # WBS uses wbsDiagram as the CSS selector
    return render_diagram_style(
        diagram_type="wbsDiagram",
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
