"""Component diagram primitives.

Frozen dataclasses representing all component diagram elements.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, Union

from .common import ColorLike, Label, LabelLike, Stereotype

if TYPE_CHECKING:
    pass


# Type aliases for component diagrams
ComponentType = Literal["component", "interface", "port", "portin", "portout"]
ContainerType = Literal["package", "node", "folder", "frame", "cloud", "database", "rectangle"]
RelationType = Literal[
    "provides",  # --( lollipop notation
    "requires",  # --(
    "dependency",  # ..>
    "association",  # --
    "line",  # --
    "dotted",  # ..
    "arrow",  # -->
    "dotted_arrow",  # ..>
]
ComponentStyle = Literal["uml1", "uml2", "rectangle"]


@dataclass(frozen=True)
class Component:
    """A component in the diagram."""

    name: str
    alias: str | None = None
    type: ComponentType = "component"
    stereotype: Stereotype | None = None
    color: ColorLike | None = None
    # For nested elements (ports, inner components)
    elements: tuple["ComponentElement", ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Interface:
    """An interface in the diagram."""

    name: str
    alias: str | None = None
    stereotype: Stereotype | None = None
    color: ColorLike | None = None


@dataclass(frozen=True)
class Port:
    """A port on a component."""

    name: str
    direction: Literal["port", "portin", "portout"] = "port"


@dataclass(frozen=True)
class Container:
    """A container (package, node, folder, etc.) grouping components."""

    name: str
    type: ContainerType = "package"
    elements: tuple["ComponentElement", ...] = field(default_factory=tuple)
    stereotype: Stereotype | None = None
    color: ColorLike | None = None


@dataclass(frozen=True)
class Relationship:
    """A relationship between components/interfaces."""

    source: str  # Component/interface name or alias
    target: str  # Component/interface name or alias
    type: RelationType = "association"
    label: Label | None = None
    source_label: str | None = None
    target_label: str | None = None
    color: ColorLike | None = None
    # Arrow head customization
    left_head: str | None = None  # e.g., "o", "*", "#", etc.
    right_head: str | None = None


@dataclass(frozen=True)
class ComponentNote:
    """A note attached to a component diagram element."""

    content: Label
    position: Literal["left", "right", "top", "bottom"] = "right"
    target: str | None = None  # Component/interface to attach to
    floating: bool = False
    color: ColorLike | None = None


# Union type for all component diagram elements
ComponentElement = Union[
    Component,
    Interface,
    Port,
    Container,
    Relationship,
    ComponentNote,
]


@dataclass(frozen=True)
class ComponentDiagram:
    """A complete component diagram."""

    elements: tuple[ComponentElement, ...] = field(default_factory=tuple)
    title: str | None = None
    style: ComponentStyle | None = None
    # Skin parameters
    hide_stereotype: bool = False
