"""MindMap diagram primitives.

Frozen dataclasses representing MindMap tree diagrams.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from .common import MindMapDiagramStyle


@dataclass(frozen=True)
class MindMapNode:
    """A node in a MindMap diagram.

        text:    Node text (can be multiline)
        depth:   Tree depth (1 = root, 2 = branch, etc.)
        side:    Force node to left/right side (None = OrgMode auto-placement)
        color:   Background color
        boxless: If True, render without box outline
    """

    text: str
    depth: int = 1
    side: Literal["left", "right"] | None = None
    color: str | None = None
    boxless: bool = False


@dataclass(frozen=True)
class MindMapDiagram:
    """A MindMap tree diagram.

        nodes:         Sequence of nodes in tree order
        direction:     Layout direction
        diagram_style: CSS-style diagram styling
    """

    nodes: tuple[MindMapNode, ...] = field(default_factory=tuple)
    direction: Literal["top_to_bottom", "left_to_right", "right_to_left"] | None = None
    diagram_style: MindMapDiagramStyle | None = None
