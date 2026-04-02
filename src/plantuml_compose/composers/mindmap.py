"""Mindmap diagram composer.

Pure nesting — the simplest composition pattern. No connections namespace.

Example:
    d = mindmap_diagram()
    n = d.nodes

    d.add(n.node("Infrastructure",
        n.node("Platforms", color="#E3F2FD",
            n.leaf("Shared Hosting"),
            n.leaf("HAVPS"),
        ),
        n.node("Tools", side="left",
            n.leaf("Netbox", boxless=True),
        ),
    ))

    puml = render(d)
"""

from __future__ import annotations

from typing import Literal

from ..primitives.common import (
    ColorLike,
    coerce_color,
)
from ..primitives.styles import (
    MindMapDiagramStyleLike,
    coerce_mindmap_diagram_style,
)
from ..primitives.mindmap import MindMapDiagram, MindMapNode
from .base import BaseComposer, EntityRef


class MindMapNodeNamespace:
    """Factory namespace for mindmap nodes."""

    def node(
        self,
        text: str,
        *children: EntityRef,
        ref: str | None = None,
        color: ColorLike | None = None,
        side: Literal["left", "right"] | None = None,
        boxless: bool = False,
    ) -> EntityRef:
        """Create a node that can have children."""
        return EntityRef(
            text,
            ref=ref,
            data={"color": color, "side": side, "boxless": boxless},
            children=children,
        )

    def leaf(
        self,
        text: str,
        *,
        ref: str | None = None,
        color: ColorLike | None = None,
        side: Literal["left", "right"] | None = None,
        boxless: bool = False,
    ) -> EntityRef:
        """Create a leaf node (no children)."""
        return EntityRef(
            text,
            ref=ref,
            data={"color": color, "side": side, "boxless": boxless},
        )


def _build_node(ref: EntityRef) -> MindMapNode:
    """Recursively convert an EntityRef tree to MindMapNode primitives."""
    data = ref._data
    color = coerce_color(data["color"]) if data.get("color") else None
    children = tuple(_build_node(child) for child in ref._children.values())
    return MindMapNode(
        text=ref._name,
        children=children,
        side=data.get("side"),
        color=color,
        boxless=data.get("boxless", False),
    )


class MindMapComposer(BaseComposer):
    """Composer for mindmap diagrams."""

    def __init__(
        self,
        *,
        direction: Literal["top_to_bottom", "left_to_right", "right_to_left"] | None = None,
        diagram_style: MindMapDiagramStyleLike | None = None,
        mainframe: str | None = None,
    ) -> None:
        super().__init__(mainframe=mainframe)
        self._direction = direction
        self._diagram_style = (
            coerce_mindmap_diagram_style(diagram_style)
            if diagram_style
            else None
        )
        self._nodes_ns = MindMapNodeNamespace()

    @property
    def nodes(self) -> MindMapNodeNamespace:
        return self._nodes_ns

    def build(self) -> MindMapDiagram:
        roots = tuple(
            _build_node(el) for el in self._elements
            if isinstance(el, EntityRef)
        )
        return MindMapDiagram(
            roots=roots,
            mainframe=self._mainframe,
            direction=self._direction,
            diagram_style=self._diagram_style,
        )


def mindmap_diagram(
    *,
    direction: Literal["top_to_bottom", "left_to_right", "right_to_left"] | None = None,
    diagram_style: MindMapDiagramStyleLike | None = None,
    mainframe: str | None = None,
) -> MindMapComposer:
    """Create a mindmap diagram composer.

    Returns a MindMapComposer — no context manager needed.

    Example:
        d = mindmap_diagram()
        n = d.nodes
        d.add(n.node("Root", n.leaf("Child")))
        print(render(d))
    """
    return MindMapComposer(
        direction=direction,
        diagram_style=diagram_style,
        mainframe=mainframe,
    )
