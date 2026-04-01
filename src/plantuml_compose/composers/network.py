"""Network diagram composer.

Multi-membership pattern — placing the same node name in multiple
networks IS the connection model.

Example:
    d = network_diagram(title="Security Levels")
    n = d.networks

    d.add(n.node("Internet", shape="cloud"))

    d.add(
        n.network("SL1",
            n.node("Internet"),
            n.node("shared", address="203.0.113.0/26"),
            address="Public IP", color="#E3F2FD",
        ),
    )

    puml = render(d)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from ..primitives.common import (
    ColorLike,
    Footer,
    Header,
    Legend,
    NetworkDiagramStyleLike,
    Scale,
    ThemeLike,
    coerce_network_diagram_style,
)
from ..primitives.network import (
    Network,
    NetworkDiagram,
    NetworkElement,
    NetworkGroup,
    NetworkNode,
    NodeShape,
    PeerLink,
    StandaloneNode,
)
from .base import BaseComposer, EntityRef


def _resolve_ref(item: EntityRef | str) -> str:
    """Resolve an EntityRef or raw string to a node name."""
    if isinstance(item, EntityRef):
        return item._name
    return item


# ---------------------------------------------------------------------------
# Internal data types returned by namespace factories
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _NodeData:
    """Pure data for a node inside a network or standalone."""
    name: str
    address: str | None = None
    shape: NodeShape | None = None
    description: str | None = None
    color: ColorLike | None = None


@dataclass(frozen=True)
class _NetworkData:
    """Pure data for a network with its nodes."""
    name: str
    children: tuple[_NodeData, ...]
    address: str | None = None
    color: ColorLike | None = None
    description: str | None = None
    width: Literal["full"] | None = None


@dataclass(frozen=True)
class _GroupData:
    """Pure data for a node grouping."""
    node_names: tuple[str, ...]
    color: ColorLike | None = None
    description: str | None = None


# ---------------------------------------------------------------------------
# Namespace
# ---------------------------------------------------------------------------


class NetworkNamespace:
    """Factory namespace for network diagram elements."""

    def node(
        self,
        name: str,
        *,
        address: str | None = None,
        shape: NodeShape | None = None,
        description: str | None = None,
        color: ColorLike | None = None,
    ) -> EntityRef:
        """Create a node reference.

        As a standalone d.add() argument, creates a StandaloneNode.
        Inside a network's children, creates a NetworkNode.
        """
        return EntityRef(
            name,
            data={
                "_type": "node",
                "address": address,
                "shape": shape,
                "description": description,
                "color": color,
            },
        )

    def network(
        self,
        name: str,
        *children: EntityRef,
        address: str | None = None,
        color: ColorLike | None = None,
        description: str | None = None,
        width: Literal["full"] | None = None,
    ) -> EntityRef:
        """Create a network with nodes as children."""
        return EntityRef(
            name,
            data={
                "_type": "network",
                "children": children,
                "address": address,
                "color": color,
                "description": description,
                "width": width,
            },
        )

    def group(
        self,
        *node_names: str,
        color: ColorLike | None = None,
        description: str | None = None,
    ) -> EntityRef:
        """Create a visual grouping of nodes."""
        return EntityRef(
            f"__group_{'_'.join(node_names)}",
            data={
                "_type": "group",
                "node_names": node_names,
                "color": color,
                "description": description,
            },
        )


# ---------------------------------------------------------------------------
# Composer
# ---------------------------------------------------------------------------


class NetworkComposer(BaseComposer):
    """Composer for network diagrams."""

    def __init__(
        self,
        *,
        title: str | None = None,
        mainframe: str | None = None,
        caption: str | None = None,
        header: str | Header | None = None,
        footer: str | Footer | None = None,
        legend: str | Legend | None = None,
        scale: float | Scale | None = None,
        theme: ThemeLike = None,
        diagram_style: NetworkDiagramStyleLike | None = None,
    ) -> None:
        super().__init__(
            title=title, mainframe=mainframe, caption=caption,
            header=header, footer=footer, legend=legend, scale=scale,
        )
        self._theme = theme
        self._diagram_style = (
            coerce_network_diagram_style(diagram_style)
            if diagram_style
            else None
        )
        self._networks_ns = NetworkNamespace()
        self._links: list[PeerLink] = []

    @property
    def networks(self) -> NetworkNamespace:
        return self._networks_ns

    def link(self, source: EntityRef | str, target: EntityRef | str) -> None:
        """Add a peer link between two nodes."""
        self._links.append(PeerLink(
            source=_resolve_ref(source),
            target=_resolve_ref(target),
        ))

    def build(self) -> NetworkDiagram:
        elements: list[NetworkElement] = []

        for item in self._elements:
            if isinstance(item, EntityRef):
                data = item._data
                elem_type = data.get("_type")

                if elem_type == "node":
                    # Standalone node
                    elements.append(StandaloneNode(
                        name=item._name,
                        shape=data.get("shape"),
                        description=data.get("description"),
                        color=data.get("color"),
                    ))

                elif elem_type == "network":
                    # Network with children
                    children = data.get("children", ())
                    nodes: list[NetworkNode] = []
                    for child in children:
                        if isinstance(child, EntityRef):
                            child_data = child._data
                            nodes.append(NetworkNode(
                                name=child._name,
                                address=child_data.get("address"),
                                shape=child_data.get("shape"),
                                description=child_data.get("description"),
                                color=child_data.get("color"),
                            ))
                    elements.append(Network(
                        name=item._name,
                        address=data.get("address"),
                        description=data.get("description"),
                        color=data.get("color"),
                        width=data.get("width"),
                        nodes=tuple(nodes),
                    ))

                elif elem_type == "group":
                    elements.append(NetworkGroup(
                        color=data.get("color"),
                        description=data.get("description"),
                        nodes=data.get("node_names", ()),
                    ))

        # Peer links
        for peer_link in self._links:
            elements.append(peer_link)

        return NetworkDiagram(
            elements=tuple(elements),
            title=self._title,
            mainframe=self._mainframe,
            caption=self._caption,
            header=self._header,
            footer=self._footer,
            legend=self._legend,
            scale=self._scale,
            theme=self._theme,
            diagram_style=self._diagram_style,
        )


def network_diagram(
    *,
    title: str | None = None,
    mainframe: str | None = None,
    caption: str | None = None,
    header: str | Header | None = None,
    footer: str | Footer | None = None,
    legend: str | Legend | None = None,
    scale: float | Scale | None = None,
    theme: ThemeLike = None,
    diagram_style: NetworkDiagramStyleLike | None = None,
) -> NetworkComposer:
    """Create a network diagram composer.

    Example:
        d = network_diagram(title="Security Levels")
        n = d.networks
        d.add(n.node("Internet", shape="cloud"))
        d.add(n.network("DMZ",
            n.node("Internet"),
            n.node("web01", address="10.0.1.10"),
            address="10.0.1.0/24",
        ))
        print(render(d))
    """
    return NetworkComposer(
        title=title, mainframe=mainframe, caption=caption,
        header=header, footer=footer, legend=legend, scale=scale,
        theme=theme, diagram_style=diagram_style,
    )
