"""MindMap diagram builders.

Provides context-manager based builders for MindMap tree diagrams.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Literal

from ..primitives.common import (
    ColorLike,
    MindMapDiagramStyle,
    MindMapDiagramStyleLike,
    coerce_color,
    coerce_mindmap_diagram_style,
)
from ..primitives.mindmap import MindMapDiagram, MindMapNode
from ..renderers import render as render_diagram


class _MindMapNodeBuilder:
    """Internal builder for accumulating node data and children."""

    def __init__(
        self,
        text: str,
        side: Literal["left", "right"] | None,
        color: ColorLike | None,
        boxless: bool,
    ) -> None:
        self._text = text
        self._side = side
        self._color = coerce_color(color) if color else None
        self._boxless = boxless
        self._children: list[MindMapNode] = []

    def _add_child(self, child: MindMapNode) -> None:
        """Add a built child node."""
        self._children.append(child)

    def build(self) -> MindMapNode:
        """Build the node primitive with all children."""
        return MindMapNode(
            text=self._text,
            children=tuple(self._children),
            side=self._side,
            color=self._color,
            boxless=self._boxless,
        )


class _MindMapNodeContext:
    """Context manager that builds node on exit and adds to parent."""

    def __init__(
        self,
        builder: _MindMapNodeBuilder,
        parent: _MindMapNodeBuilder | MindMapDiagramBuilder,
    ) -> None:
        self._builder = builder
        self._parent = parent

    def node(
        self,
        text: str,
        *,
        side: Literal["left", "right"] | None = None,
        color: ColorLike | None = None,
        boxless: bool = False,
    ) -> _MindMapNodeContext:
        """Add a child node that can have its own children.

        Args:
            text: Node text (can be multiline)
            side: Force left/right placement (None = auto)
            color: Background color
            boxless: If True, render without box outline

        Returns:
            Context manager for adding grandchildren

        Example:
            with root.node("Branch") as branch:
                branch.node("Leaf")  # leaf via context
        """
        child_builder = _MindMapNodeBuilder(text, side, color, boxless)
        return _MindMapNodeContext(child_builder, self._builder)

    def leaf(
        self,
        text: str,
        *,
        side: Literal["left", "right"] | None = None,
        color: ColorLike | None = None,
        boxless: bool = False,
    ) -> None:
        """Add a leaf node (no children).

        Args:
            text: Node text (can be multiline)
            side: Force left/right placement (None = auto)
            color: Background color
            boxless: If True, render without box outline

        Example:
            with root.node("Branch") as branch:
                branch.leaf("Leaf 1")
                branch.leaf("Leaf 2")
        """
        node = MindMapNode(
            text=text,
            children=(),
            side=side,
            color=coerce_color(color) if color else None,
            boxless=boxless,
        )
        self._builder._add_child(node)

    def __enter__(self) -> _MindMapNodeContext:
        return self

    def __exit__(self, *args: object) -> None:
        node = self._builder.build()
        if isinstance(self._parent, _MindMapNodeBuilder):
            self._parent._add_child(node)
        else:
            self._parent._add_root(node)


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
        self._roots: list[MindMapNode] = []

    def node(
        self,
        text: str,
        *,
        color: ColorLike | None = None,
        boxless: bool = False,
    ) -> _MindMapNodeContext:
        """Add a root node.

        Args:
            text: Node text (can be multiline)
            color: Background color
            boxless: If True, render without box outline

        Returns:
            Context manager for adding children

        Note:
            Root nodes cannot have side specified (side is ignored on roots).

        Example:
            with mindmap_diagram() as d:
                with d.node("Central Topic") as root:
                    root.node("Leaf")
                    with root.node("Branch") as branch:
                        branch.node("Nested")
        """
        # Root nodes don't have side - it's determined by children
        builder = _MindMapNodeBuilder(text, side=None, color=color, boxless=boxless)
        return _MindMapNodeContext(builder, self)

    def _add_root(self, root: MindMapNode) -> None:
        """Add a built root node."""
        self._roots.append(root)

    def build(self) -> MindMapDiagram:
        """Build the MindMap diagram primitive."""
        return MindMapDiagram(
            roots=tuple(self._roots),
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
        MindMapDiagramBuilder for adding root nodes

    Example:
        with mindmap_diagram() as d:
            with d.node("Central Topic") as root:
                with root.node("Branch 1") as b1:
                    b1.node("Leaf 1.1")
                    b1.node("Leaf 1.2")
                with root.node("Branch 2", side="left") as b2:
                    b2.node("Leaf 2.1")
        print(d.render())

        # With styling:
        with mindmap_diagram(diagram_style={"node": {"background": "#E3F2FD"}}) as d:
            with d.node("Styled", color="#Orange") as root:
                root.node("Child")
    """
    builder = MindMapDiagramBuilder(direction, diagram_style)
    yield builder
