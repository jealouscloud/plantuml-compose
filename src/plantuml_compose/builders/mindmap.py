"""MindMap diagram builders.

Provides context-manager based builders for MindMap tree diagrams.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Literal

from ..primitives.common import (
    MindMapDiagramStyle,
    MindMapDiagramStyleLike,
    coerce_mindmap_diagram_style,
)
from ..primitives.mindmap import MindMapDiagram, MindMapNode
from ..renderers import render as render_diagram


class MindMapDiagramBuilder:
    """Builder for MindMap tree diagrams."""

    def __init__(
        self,
        direction: Literal["top_to_bottom", "left_to_right", "right_to_left"] | None,
        diagram_style: MindMapDiagramStyleLike | None,
    ) -> None:
        self._direction = direction
        self._diagram_style = (
            coerce_mindmap_diagram_style(diagram_style) if diagram_style else None
        )
        self._nodes: list[MindMapNode] = []

    def node(
        self,
        text: str,
        *,
        depth: int = 1,
        side: Literal["left", "right"] | None = None,
        color: str | None = None,
        boxless: bool = False,
    ) -> None:
        """Add a node to the mindmap.

        Args:
            text: Node text (can be multiline)
            depth: Tree depth (1 = root, 2 = branch, etc.)
            side: Force left/right placement (None = OrgMode auto-placement)
            color: Background color (e.g. "#Orange", "#FF5500")
            boxless: If True, render without box outline

        Example:
            d.node("Central Topic")
            d.node("Branch 1", depth=2)
            d.node("Leaf 1.1", depth=3)
            d.node("Leaf 1.2", depth=3)
            d.node("Branch 2", depth=2, side="left")

        Raises:
            ValueError: If depth < 1
        """
        if depth < 1:
            raise ValueError(f"Depth must be >= 1, got {depth}")
        self._nodes.append(
            MindMapNode(
                text=text,
                depth=depth,
                side=side,
                color=color,
                boxless=boxless,
            )
        )

    def build(self) -> MindMapDiagram:
        """Build the MindMap diagram primitive."""
        return MindMapDiagram(
            nodes=tuple(self._nodes),
            direction=self._direction,
            diagram_style=self._diagram_style,
        )

    def render(self) -> str:
        """Build and render the diagram to PlantUML text."""
        return render_diagram(self.build())


@contextmanager
def mindmap_diagram(
    *,
    direction: Literal["top_to_bottom", "left_to_right", "right_to_left"] | None = None,
    diagram_style: MindMapDiagramStyleLike | None = None,
) -> Iterator[MindMapDiagramBuilder]:
    """Create a MindMap tree diagram.

    Args:
        direction: Layout direction (default is left-right from root)
        diagram_style: CSS-style diagram styling

    Yields:
        MindMapDiagramBuilder for adding nodes

    Example:
        with mindmap_diagram() as d:
            d.node("Central Topic")
            d.node("Branch 1", depth=2)
            d.node("Leaf 1.1", depth=3)
            d.node("Leaf 1.2", depth=3)
            d.node("Branch 2", depth=2, side="left")
            d.node("Leaf 2.1", depth=3)
        print(d.render())

        # With arithmetic notation (explicit left/right):
        with mindmap_diagram() as d:
            d.node("Root")
            d.node("Right 1", depth=2, side="right")
            d.node("Right 1.1", depth=3, side="right")
            d.node("Left 1", depth=2, side="left")
            d.node("Left 1.1", depth=3, side="left")
    """
    builder = MindMapDiagramBuilder(direction, diagram_style)
    yield builder
