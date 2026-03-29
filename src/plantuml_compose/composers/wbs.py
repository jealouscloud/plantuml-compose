"""WBS (Work Breakdown Structure) diagram composer.

Nesting via factory positional args, plus d.connect() for cross-branch
dependency arrows. Node references replace string aliases.

Example:
    d = wbs_diagram()
    n = d.nodes
    c = d.connections

    cabling = n.leaf("Cabling")
    edge = n.leaf("Edge routers")

    d.add(n.node("Project",
        n.node("Physical", cabling),
        n.node("Network", edge),
    ))

    d.connect(c.arrow(cabling, edge))

    puml = render(d)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ..primitives.common import (
    ColorLike,
    MindMapDiagramStyleLike,
    coerce_color,
    coerce_mindmap_diagram_style,
)
from ..primitives.wbs import WBSArrow, WBSDiagram, WBSNode
from .base import BaseComposer, EntityRef


@dataclass(frozen=True)
class _WBSArrowData:
    """Internal connection data for a WBS arrow."""
    source: EntityRef
    target: EntityRef


class WBSNodeNamespace:
    """Factory namespace for WBS nodes."""

    def node(
        self,
        text: str,
        *children: EntityRef,
        ref: str | None = None,
        color: ColorLike | None = None,
        side: Literal["left", "right"] | None = None,
        boxless: bool = False,
    ) -> EntityRef:
        return EntityRef(
            text,
            ref=ref,
            data={
                "color": color, "side": side, "boxless": boxless,
                "_explicit_ref": ref is not None,
            },
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
        return EntityRef(
            text,
            ref=ref,
            data={
                "color": color, "side": side, "boxless": boxless,
                "_explicit_ref": ref is not None,
            },
        )


class WBSConnectionNamespace:
    """Factory namespace for WBS connections."""

    def arrow(self, source: EntityRef, target: EntityRef) -> _WBSArrowData:
        return _WBSArrowData(source=source, target=target)

    def arrows(
        self, *tuples: tuple[EntityRef, EntityRef],
    ) -> list[_WBSArrowData]:
        return [_WBSArrowData(source=s, target=t) for s, t in tuples]


def _needs_alias(ref: EntityRef) -> bool:
    """Check if a node needs an explicit alias.

    Only set alias when the ref differs from what the renderer would
    generate from the text — i.e., the name has special chars, or
    an explicit ref= was provided that differs from sanitize_ref(name).
    """
    from ..primitives.common import sanitize_ref
    return ref._ref != ref._name and ref._ref != sanitize_ref(ref._name) or ref._data.get("_explicit_ref", False)


def _build_node(ref: EntityRef, has_arrows: bool = False) -> WBSNode:
    """Recursively convert an EntityRef tree to WBSNode primitives."""
    data = ref._data
    color = coerce_color(data["color"]) if data.get("color") else None
    children = tuple(
        _build_node(child, has_arrows=has_arrows)
        for child in ref._children.values()
    )
    # Only set alias when arrows exist (they need aliases to reference nodes)
    # or when an explicit ref= was provided
    alias = ref._ref if (has_arrows or data.get("_explicit_ref")) else None
    return WBSNode(
        text=ref._name,
        children=children,
        side=data.get("side"),
        alias=alias,
        color=color,
        boxless=data.get("boxless", False),
    )


class WBSComposer(BaseComposer):
    """Composer for WBS diagrams."""

    def __init__(
        self,
        *,
        diagram_style: MindMapDiagramStyleLike | None = None,
        mainframe: str | None = None,
    ) -> None:
        super().__init__()
        self._diagram_style = (
            coerce_mindmap_diagram_style(diagram_style)
            if diagram_style
            else None
        )
        self._mainframe = mainframe
        self._nodes_ns = WBSNodeNamespace()
        self._connections_ns = WBSConnectionNamespace()

    @property
    def nodes(self) -> WBSNodeNamespace:
        return self._nodes_ns

    @property
    def connections(self) -> WBSConnectionNamespace:
        return self._connections_ns

    def build(self) -> WBSDiagram:
        has_arrows = len(self._connections) > 0
        roots = tuple(
            _build_node(el, has_arrows=has_arrows)
            for el in self._elements
            if isinstance(el, EntityRef)
        )
        arrows = tuple(
            WBSArrow(from_alias=c.source._ref, to_alias=c.target._ref)
            for c in self._connections
            if isinstance(c, _WBSArrowData)
        )
        return WBSDiagram(
            roots=roots,
            arrows=arrows,
            mainframe=self._mainframe,
            diagram_style=self._diagram_style,
        )


def wbs_diagram(
    *,
    diagram_style: MindMapDiagramStyleLike | None = None,
    mainframe: str | None = None,
) -> WBSComposer:
    """Create a WBS diagram composer.

    Example:
        d = wbs_diagram()
        n = d.nodes
        c = d.connections
        a = n.leaf("Task A")
        b = n.leaf("Task B")
        d.add(n.node("Project", a, b))
        d.connect(c.arrow(a, b))
        print(render(d))
    """
    return WBSComposer(diagram_style=diagram_style, mainframe=mainframe)
