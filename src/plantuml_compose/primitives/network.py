"""Network diagram (nwdiag) primitives.

Network diagrams show the arrangement and interconnections of network
components including servers, routers, switches, and other devices.
Based on nwdiag syntax integrated into PlantUML.

Key concepts:
    Network: A network segment with an address range containing nodes
    Node: A device (server, database, router, etc.) on one or more networks
    Group: A visual grouping of nodes with optional color/description
    PeerLink: A direct connection between two nodes

All types are frozen dataclasses - immutable data with no behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from .common import (
    ColorLike,
    Footer,
    Header,
    Legend,
    NetworkDiagramStyle,
    Scale,
    ThemeLike,
)


# Node shapes available in nwdiag
NodeShape = Literal[
    "node",  # Default
    "actor",
    "agent",
    "artifact",
    "boundary",
    "card",
    "cloud",
    "collections",
    "component",
    "control",
    "database",
    "entity",
    "file",
    "folder",
    "frame",
    "hexagon",
    "interface",
    "label",
    "package",
    "person",
    "queue",
    "stack",
    "rectangle",
    "storage",
    "usecase",
]


@dataclass(frozen=True)
class NetworkNode:
    """A device or server on a network.

    Nodes represent devices like servers, databases, routers, etc.
    A node can appear on multiple networks with different addresses.

        name:        Node identifier (e.g., "web01", "db01")
        address:     IP address or addresses on this network
        shape:       Visual shape (database, cloud, storage, etc.)
        description: Label shown on the node (supports icons)
        color:       Background color
    """

    name: str
    address: str | None = None  # Can be comma-separated for multiple
    shape: NodeShape | None = None
    description: str | None = None
    color: ColorLike | None = None


@dataclass(frozen=True)
class Network:
    """A network segment containing nodes.

    Networks are shown as horizontal bars connecting nodes.
    Nodes can appear on multiple networks.

        name:        Network name (e.g., "dmz", "internal")
        address:     Network address in CIDR notation (e.g., "192.168.1.0/24")
        description: Label shown on the network bar
        color:       Background color for the network bar
        width:       Set to "full" for uniform width across networks
        nodes:       Nodes on this network
    """

    name: str
    address: str | None = None
    description: str | None = None
    color: ColorLike | None = None
    width: Literal["full"] | None = None
    nodes: tuple[NetworkNode, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class NetworkGroup:
    """A visual grouping of nodes.

    Groups provide a colored background behind related nodes
    with an optional description label.

        color:       Background color for the group
        description: Label for the group
        nodes:       Node names in the group
    """

    color: ColorLike | None = None
    description: str | None = None
    nodes: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class PeerLink:
    """A direct connection between two nodes.

    Peer links show direct connections without going through
    a network segment. Useful for router-to-internet links.

        source: First node name
        target: Second node name
    """

    source: str
    target: str


@dataclass(frozen=True)
class StandaloneNode:
    """A node defined outside of any network.

    Used for nodes like "internet" that connect via peer links
    rather than being on a network segment.

        name:        Node identifier
        shape:       Visual shape
        description: Label shown on the node
        color:       Background color
    """

    name: str
    shape: NodeShape | None = None
    description: str | None = None
    color: ColorLike | None = None


# Union of elements that can appear in a network diagram
NetworkElement = Network | NetworkGroup | PeerLink | StandaloneNode


@dataclass(frozen=True)
class NetworkDiagram:
    """A complete network diagram ready for rendering.

    Contains networks, nodes, groups, and peer connections.
    Usually created via the network_diagram() builder rather than directly.

        elements:      Networks, groups, peer links, standalone nodes
        title:         Diagram title
        caption:       Caption below diagram
        header:        Header above diagram
        footer:        Footer below diagram
        legend:        Legend block
        scale:         Diagram scale
        theme:         PlantUML theme
        diagram_style: CSS-style diagram styling
    """

    elements: tuple[NetworkElement, ...] = field(default_factory=tuple)
    title: str | None = None
    caption: str | None = None
    header: Header | None = None
    footer: Footer | None = None
    legend: Legend | None = None
    scale: Scale | None = None
    theme: ThemeLike | None = None
    diagram_style: NetworkDiagramStyle | None = None
