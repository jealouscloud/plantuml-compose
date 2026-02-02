"""Work Breakdown Structure (WBS) diagram builders.

Provides context-manager based builders for WBS tree diagrams.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Literal

from ..primitives.common import (
    ColorLike,
    MindMapDiagramStyleLike,
    coerce_color,
    coerce_mindmap_diagram_style,
)
from .base import EmbeddableDiagramMixin
from ..primitives.wbs import (
    WBSArrow,
    WBSDiagram,
    WBSDiagramStyle,
    WBSDiagramStyleLike,
    WBSNode,
)
from ..renderers import render as render_diagram


class _WBSNodeBuilder:
    """Internal builder for accumulating node data and children."""

    def __init__(
        self,
        text: str,
        side: Literal["left", "right"] | None,
        alias: str | None,
        color: ColorLike | None,
        boxless: bool,
    ) -> None:
        self._text = text
        self._side = side
        self._alias = alias
        self._color = coerce_color(color) if color else None
        self._boxless = boxless
        self._children: list[WBSNode] = []

    def _add_child(self, child: WBSNode) -> None:
        """Add a built child node."""
        self._children.append(child)

    def build(self) -> WBSNode:
        """Build the node primitive with all children."""
        return WBSNode(
            text=self._text,
            children=tuple(self._children),
            side=self._side,
            alias=self._alias,
            color=self._color,
            boxless=self._boxless,
        )


class _WBSNodeContext:
    """Context manager that builds node on exit and adds to parent."""

    def __init__(
        self,
        builder: _WBSNodeBuilder,
        parent: _WBSNodeBuilder | WBSDiagramBuilder,
    ) -> None:
        self._builder = builder
        self._parent = parent

    def node(
        self,
        text: str,
        *,
        side: Literal["left", "right"] | None = None,
        alias: str | None = None,
        color: ColorLike | None = None,
        boxless: bool = False,
    ) -> _WBSNodeContext:
        """Add a child node that can have its own children.

        Args:
            text: Node text (can be multiline)
            side: Force left/right placement (None = auto)
            alias: Optional alias for arrow connections
            color: Background color
            boxless: If True, render without box outline

        Returns:
            Context manager for adding grandchildren
        """
        child_builder = _WBSNodeBuilder(text, side, alias, color, boxless)
        return _WBSNodeContext(child_builder, self._builder)

    def leaf(
        self,
        text: str,
        *,
        side: Literal["left", "right"] | None = None,
        alias: str | None = None,
        color: ColorLike | None = None,
        boxless: bool = False,
    ) -> None:
        """Add a leaf node (no children).

        Args:
            text: Node text (can be multiline)
            side: Force left/right placement (None = auto)
            alias: Optional alias for arrow connections
            color: Background color
            boxless: If True, render without box outline
        """
        node = WBSNode(
            text=text,
            children=(),
            side=side,
            alias=alias,
            color=coerce_color(color) if color else None,
            boxless=boxless,
        )
        self._builder._add_child(node)

    def __enter__(self) -> _WBSNodeContext:
        return self

    def __exit__(self, *args: object) -> None:
        node = self._builder.build()
        if isinstance(self._parent, _WBSNodeBuilder):
            self._parent._add_child(node)
        else:
            self._parent._add_root(node)


class WBSDiagramBuilder(EmbeddableDiagramMixin):
    """Builder for WBS tree diagrams."""

    _keep_diagram_markers = True

    def __init__(
        self,
        direction: Literal["top_to_bottom", "left_to_right", "right_to_left"] | None,
        diagram_style: WBSDiagramStyleLike | None,
    ) -> None:
        self._direction = direction
        self._diagram_style = (
            coerce_mindmap_diagram_style(diagram_style) if diagram_style else None
        )
        self._roots: list[WBSNode] = []
        self._arrows: list[WBSArrow] = []

    def node(
        self,
        text: str,
        *,
        alias: str | None = None,
        color: ColorLike | None = None,
        boxless: bool = False,
    ) -> _WBSNodeContext:
        """Add a root node.

        Args:
            text: Node text (can be multiline)
            alias: Optional alias for arrow connections
            color: Background color
            boxless: If True, render without box outline

        Returns:
            Context manager for adding children

        Note:
            Root nodes cannot have side specified.
        """
        builder = _WBSNodeBuilder(text, side=None, alias=alias, color=color, boxless=boxless)
        return _WBSNodeContext(builder, self)

    def arrow(self, from_alias: str, to_alias: str) -> None:
        """Add an arrow between two aliased nodes.

        Args:
            from_alias: Source node alias
            to_alias: Target node alias
        """
        self._arrows.append(WBSArrow(from_alias=from_alias, to_alias=to_alias))

    def _add_root(self, root: WBSNode) -> None:
        """Add a built root node."""
        self._roots.append(root)

    def build(self) -> WBSDiagram:
        """Build the WBS diagram primitive."""
        return WBSDiagram(
            roots=tuple(self._roots),
            arrows=tuple(self._arrows),
            direction=self._direction,
            diagram_style=self._diagram_style,
        )

    def render(self) -> str:
        """Build and render the diagram to PlantUML text."""
        return render_diagram(self.build())


@contextmanager
def wbs_diagram(
    *,
    direction: Literal["top_to_bottom", "left_to_right", "right_to_left"] | None = None,
    diagram_style: WBSDiagramStyleLike | None = None,
) -> Iterator[WBSDiagramBuilder]:
    """Create a Work Breakdown Structure diagram.

    Args:
        direction: Layout direction (default is top-down from root)
        diagram_style: CSS-style diagram styling

    Yields:
        WBSDiagramBuilder for adding root nodes

    Example:
        with wbs_diagram() as d:
            with d.node("Project") as proj:
                with proj.node("Phase 1") as p1:
                    p1.leaf("Task 1.1")
                    p1.leaf("Task 1.2")
                with proj.node("Phase 2", side="left") as p2:
                    p2.leaf("Task 2.1")
        print(d.render())

        # With arrows between nodes:
        with wbs_diagram() as d:
            with d.node("Root") as root:
                root.leaf("A", alias="a")
                root.leaf("B", alias="b")
            d.arrow("a", "b")
    """
    builder = WBSDiagramBuilder(direction, diagram_style)
    yield builder
