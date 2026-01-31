"""MindMap diagram primitives.

Frozen dataclasses representing MindMap tree diagrams.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from .common import ColorLike, MindMapDiagramStyle


@dataclass(frozen=True)
class MindMapNode:
    """A node in a MindMap diagram.

        text:     Node text (can be multiline)
        children: Child nodes
        side:     Force left/right placement (None = auto, ignored on root)
        color:    Background color
        boxless:  If True, render without box outline
    """

    text: str
    children: tuple[MindMapNode, ...] = field(default_factory=tuple)
    side: Literal["left", "right"] | None = None
    color: ColorLike | None = None
    boxless: bool = False


@dataclass(frozen=True)
class MindMapDiagram:
    """A MindMap tree diagram.

        roots:         Root node(s) - typically one, but multi-root is supported
        direction:     Layout direction
        diagram_style: CSS-style diagram styling
    """

    roots: tuple[MindMapNode, ...] = field(default_factory=tuple)
    direction: Literal["top_to_bottom", "left_to_right", "right_to_left"] | None = None
    diagram_style: MindMapDiagramStyle | None = None
