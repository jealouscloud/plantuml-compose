"""Work Breakdown Structure (WBS) diagram primitives.

Frozen dataclasses representing WBS tree diagrams.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from .common import ColorLike, MindMapDiagramStyle, MindMapDiagramStyleLike

# WBS reuses MindMap styling since they have the same CSS selectors
WBSDiagramStyle = MindMapDiagramStyle
WBSDiagramStyleLike = MindMapDiagramStyleLike


@dataclass(frozen=True)
class WBSNode:
    """A node in a WBS diagram.

        text:     Node text (can be multiline)
        children: Child nodes
        side:     Force left/right placement (None = auto)
        alias:    Optional alias for arrow connections
        color:    Background color
        boxless:  If True, render without box outline
    """

    text: str
    children: tuple[WBSNode, ...] = field(default_factory=tuple)
    side: Literal["left", "right"] | None = None
    alias: str | None = None
    color: ColorLike | None = None
    boxless: bool = False


@dataclass(frozen=True)
class WBSArrow:
    """An arrow connecting two aliased WBS nodes.

        from_alias: Source node alias
        to_alias:   Target node alias
    """

    from_alias: str
    to_alias: str


@dataclass(frozen=True)
class WBSDiagram:
    """A Work Breakdown Structure diagram.

        roots:         Root node(s) - typically one, but multi-root is supported
        arrows:        Arrows connecting aliased nodes
        direction:     Layout direction
        diagram_style: CSS-style diagram styling
    """

    roots: tuple[WBSNode, ...] = field(default_factory=tuple)
    arrows: tuple[WBSArrow, ...] = field(default_factory=tuple)
    direction: Literal["top_to_bottom", "left_to_right", "right_to_left"] | None = None
    diagram_style: WBSDiagramStyle | None = None
