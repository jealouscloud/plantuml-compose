"""Network diagram (nwdiag) builder.

Provides a fluent API for constructing network diagrams showing
the arrangement and interconnections of network components.

Example:
    from plantuml_compose import network_diagram

    with network_diagram(title="Office Network") as d:
        # Define networks with nodes
        with d.network("dmz", address="210.x.x.x/24") as dmz:
            dmz.node("web01", address="210.x.x.1")
            dmz.node("web02", address="210.x.x.2")

        with d.network("internal", address="172.x.x.x/24") as internal:
            internal.node("web01", address="172.x.x.1")
            internal.node("db01", address="172.x.x.100", shape="database")

        # Standalone nodes and peer connections
        inet = d.node("internet", shape="cloud")
        d.link(inet, "web01")

        # Visual grouping
        d.group("web01", "web02", color="#CCFFCC", description="Web Servers")

    print(d.render())
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator, Literal

from ..primitives.common import (
    ColorLike,
    Footer,
    Header,
    Legend,
    NetworkDiagramStyle,
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
from ..renderers.network import render_network_diagram


def _validate_not_empty(value: str, name: str) -> None:
    """Validate that a string is not empty."""
    if not value or not value.strip():
        raise ValueError(f"{name} cannot be empty")


@dataclass
class NodeRef:
    """Reference to a node for use in relationships."""

    name: str


class NetworkBuilder:
    """Builder for adding nodes to a network."""

    def __init__(
        self,
        name: str,
        address: str | None,
        description: str | None,
        color: ColorLike | None,
        width: Literal["full"] | None,
    ):
        self._name = name
        self._address = address
        self._description = description
        self._color = color
        self._width = width
        self._nodes: list[NetworkNode] = []

    def node(
        self,
        name: str,
        *,
        address: str | None = None,
        shape: NodeShape | None = None,
        description: str | None = None,
        color: ColorLike | None = None,
    ) -> NodeRef:
        """Add a node to this network.

        Args:
            name: Node identifier (e.g., "web01", "db01")
            address: IP address on this network
            shape: Visual shape (database, cloud, storage, etc.)
            description: Label shown on the node
            color: Background color

        Returns:
            Reference to the node for use in links
        """
        _validate_not_empty(name, "Node name")
        self._nodes.append(
            NetworkNode(
                name=name,
                address=address,
                shape=shape,
                description=description,
                color=color,
            )
        )
        return NodeRef(name)

    def _build(self) -> Network:
        """Build the network primitive."""
        return Network(
            name=self._name,
            address=self._address,
            description=self._description,
            color=self._color,
            width=self._width,
            nodes=tuple(self._nodes),
        )


class NetworkDiagramBuilder:
    """Builder for constructing network diagrams."""

    def __init__(
        self,
        title: str | None,
        caption: str | None,
        header: Header | None,
        footer: Footer | None,
        legend: Legend | None,
        scale: Scale | None,
        theme: ThemeLike | None,
        diagram_style: NetworkDiagramStyle | None,
    ):
        self._title = title
        self._caption = caption
        self._header = header
        self._footer = footer
        self._legend = legend
        self._scale = scale
        self._theme = theme
        self._diagram_style = diagram_style
        self._elements: list[NetworkElement] = []

    @contextmanager
    def network(
        self,
        name: str,
        *,
        address: str | None = None,
        description: str | None = None,
        color: ColorLike | None = None,
        width: Literal["full"] | None = None,
    ) -> Iterator[NetworkBuilder]:
        """Create a network segment.

        Args:
            name: Network name (e.g., "dmz", "internal")
            address: Network address in CIDR notation
            description: Label shown on the network bar
            color: Background color for the network bar
            width: Set to "full" for uniform width

        Yields:
            NetworkBuilder for adding nodes

        Example:
            with d.network("dmz", address="192.168.1.0/24") as dmz:
                dmz.node("server1", address="192.168.1.10")
                dmz.node("server2", address="192.168.1.11")
        """
        _validate_not_empty(name, "Network name")
        builder = NetworkBuilder(name, address, description, color, width)
        yield builder
        self._elements.append(builder._build())

    def node(
        self,
        name: str,
        *,
        shape: NodeShape | None = None,
        description: str | None = None,
        color: ColorLike | None = None,
    ) -> NodeRef:
        """Create a standalone node (not on a network).

        Standalone nodes are useful for elements like "internet"
        that connect via peer links rather than network segments.

        Args:
            name: Node identifier
            shape: Visual shape (cloud, database, etc.)
            description: Label shown on the node
            color: Background color

        Returns:
            Reference to the node for use in links

        Example:
            inet = d.node("internet", shape="cloud")
            d.link(inet, "router")
        """
        _validate_not_empty(name, "Node name")
        self._elements.append(
            StandaloneNode(
                name=name,
                shape=shape,
                description=description,
                color=color,
            )
        )
        return NodeRef(name)

    def link(
        self,
        source: str | NodeRef,
        target: str | NodeRef,
    ) -> None:
        """Create a peer link between two nodes.

        Peer links show direct connections without going through
        a network segment.

        Args:
            source: First node (name or reference)
            target: Second node (name or reference)

        Example:
            d.link("internet", "router")
            # or with references:
            inet = d.node("internet", shape="cloud")
            d.link(inet, "router")
        """
        source_name = source.name if isinstance(source, NodeRef) else source
        target_name = target.name if isinstance(target, NodeRef) else target
        _validate_not_empty(source_name, "Source node")
        _validate_not_empty(target_name, "Target node")
        self._elements.append(PeerLink(source=source_name, target=target_name))

    def group(
        self,
        *nodes: str | NodeRef,
        color: ColorLike | None = None,
        description: str | None = None,
    ) -> None:
        """Create a visual grouping of nodes.

        Groups provide a colored background behind related nodes.

        Args:
            *nodes: Node names or references to include (at least one required)
            color: Background color for the group
            description: Label for the group

        Raises:
            ValueError: If no nodes are provided

        Example:
            d.group("web01", "web02", color="#CCFFCC", description="Web Servers")
        """
        if not nodes:
            raise ValueError("Group must contain at least one node")
        node_names = tuple(
            n.name if isinstance(n, NodeRef) else n for n in nodes
        )
        self._elements.append(
            NetworkGroup(
                color=color,
                description=description,
                nodes=node_names,
            )
        )

    def build(self) -> NetworkDiagram:
        """Build the network diagram primitive."""
        return NetworkDiagram(
            elements=tuple(self._elements),
            title=self._title,
            caption=self._caption,
            header=self._header,
            footer=self._footer,
            legend=self._legend,
            scale=self._scale,
            theme=self._theme,
            diagram_style=self._diagram_style,
        )

    def render(self) -> str:
        """Render the diagram to PlantUML text.

        Convenience method equivalent to:
            from plantuml_compose.renderers import render
            render(d.build())
        """
        return render_network_diagram(self.build())


@contextmanager
def network_diagram(
    *,
    title: str | None = None,
    caption: str | None = None,
    header: Header | None = None,
    footer: Footer | None = None,
    legend: Legend | None = None,
    scale: Scale | None = None,
    theme: ThemeLike | None = None,
    diagram_style: NetworkDiagramStyleLike | None = None,
) -> Iterator[NetworkDiagramBuilder]:
    """Create a network diagram.

    Network diagrams show the arrangement and interconnections of
    network components including servers, routers, and devices.

    Args:
        title: Diagram title
        caption: Caption below diagram
        header: Header above diagram
        footer: Footer below diagram
        legend: Legend block
        scale: Diagram scale
        theme: PlantUML theme
        diagram_style: CSS-style diagram styling

    Yields:
        NetworkDiagramBuilder for constructing the diagram

    Example:
        with network_diagram(title="Data Center") as d:
            with d.network("dmz", address="10.0.1.0/24") as dmz:
                dmz.node("web01", address="10.0.1.10")
                dmz.node("web02", address="10.0.1.11")

            with d.network("internal", address="10.0.2.0/24") as internal:
                internal.node("web01", address="10.0.2.10")
                internal.node("db01", address="10.0.2.20", shape="database")

            inet = d.node("internet", shape="cloud")
            d.link(inet, "web01")

        print(d.render())
    """
    coerced_style = (
        coerce_network_diagram_style(diagram_style) if diagram_style else None
    )
    builder = NetworkDiagramBuilder(
        title=title,
        caption=caption,
        header=header,
        footer=footer,
        legend=legend,
        scale=scale,
        theme=theme,
        diagram_style=coerced_style,
    )
    yield builder
