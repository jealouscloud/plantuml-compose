"""Component diagram primitives.

Component diagrams show the physical structure of a system: the software
components, their interfaces, and dependencies. They're useful for:

- Documenting system architecture
- Showing service boundaries and APIs
- Visualizing package dependencies
- Planning deployment topology

Key concepts:
    Component: A modular software unit (service, library, module)
    Interface: A contract that components provide or require
    Port:      A connection point on a component
    Container: A grouping (package, node, folder) for organization

All types are frozen dataclasses - immutable data with no behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, Union

from .common import ColorLike, ComponentDiagramStyle, Direction, Label, LabelLike, LineStyle, Stereotype, Style

if TYPE_CHECKING:
    pass


# Component element types
ComponentType = Literal["component", "interface", "port", "portin", "portout"]

# Container visual styles
ContainerType = Literal[
    "package",    # Tab folder (default)
    "node",       # 3D box
    "folder",     # Folder icon
    "frame",      # Frame with title bar
    "cloud",      # Cloud shape
    "database",   # Cylinder
    "rectangle",  # Plain rectangle
]

# Relationship types - determine the arrow/connector style
RelationType = Literal[
    "provides",      # --( Lollipop: component provides interface
    "requires",      # )-- Socket: component requires interface
    "dependency",    # ..> Depends on (dotted arrow)
    "association",   # --  Connected (solid line)
    "line",          # --  Plain line
    "dotted",        # ..  Dotted line
    "arrow",         # --> Solid arrow
    "dotted_arrow",  # ..> Dotted arrow
]

# Overall diagram style
ComponentStyle = Literal["uml1", "uml2", "rectangle"]


def _sanitize_ref(name: str) -> str:
    """Convert a name to a valid PlantUML reference.

    PlantUML identifiers cannot contain spaces, so spaces are replaced with
    underscores. This allows names like "Web Server" to be referenced as
    "Web_Server" in relationships.
    """
    return name.replace(" ", "_")


@dataclass(frozen=True)
class Component:
    """A software component in the diagram.

    Components are modular units that encapsulate functionality behind
    interfaces. They're drawn as rectangles with a component icon.

        name:       Component name
        alias:      Short identifier for relationships
        type:       Element type (usually "component")
        stereotype: UML stereotype (e.g., <<service>>)
        style:      Visual styling (background, line, text_color)
        elements:   Nested ports or sub-components
    """

    name: str
    alias: str | None = None
    type: ComponentType = "component"
    stereotype: Stereotype | None = None
    style: Style | None = None
    # For nested elements (ports, inner components)
    elements: tuple["ComponentElement", ...] = field(default_factory=tuple)

    @property
    def _ref(self) -> str:
        """Reference name for use in relationships."""
        if self.alias:
            return self.alias
        return _sanitize_ref(self.name)


@dataclass(frozen=True)
class Interface:
    """An interface that components provide or require.

    Interfaces define contracts between components. They can be shown
    as lollipops (provided) or sockets (required) when connected.

        name:       Interface name
        alias:      Short identifier for relationships
        stereotype: UML stereotype
        style:      Visual styling (background, line, text_color)
    """

    name: str
    alias: str | None = None
    stereotype: Stereotype | None = None
    style: Style | None = None

    @property
    def _ref(self) -> str:
        """Reference name for use in relationships."""
        if self.alias:
            return self.alias
        return _sanitize_ref(self.name)


@dataclass(frozen=True)
class Port:
    """A connection point on a component.

    Ports are specific points where components connect to the outside
    world, often associated with interfaces.

        name:      Port name
        direction: "port" (bidirectional), "portin", or "portout"
    """

    name: str
    direction: Literal["port", "portin", "portout"] = "port"


@dataclass(frozen=True)
class Container:
    """A visual container grouping related components.

    Containers organize components into logical groups like packages,
    subsystems, or deployment nodes.

        name:       Container label
        type:       Visual shape ("package", "node", "cloud", etc.)
        elements:   Components inside the container
        stereotype: UML stereotype
        style:      Visual styling (background, line, text_color)
        alias:      Short identifier for relationships
    """

    name: str
    type: ContainerType = "package"
    elements: tuple["ComponentElement", ...] = field(default_factory=tuple)
    stereotype: Stereotype | None = None
    style: Style | None = None
    alias: str | None = None

    @property
    def _ref(self) -> str:
        """Reference name for use in relationships."""
        if self.alias:
            return self.alias
        return _sanitize_ref(self.name)


@dataclass(frozen=True)
class Relationship:
    """A connection between components or interfaces.

    Relationships show how components interact. The type determines
    the visual style:

        provides:   Component provides an interface (lollipop)
        requires:   Component needs an interface (socket)
        dependency: Depends on (dotted arrow)
        association: General connection (solid line)

        source/target: Component or interface references
        source/target_label: Labels at each end
        label:      Text on the relationship line
        style:      Line styling (color, pattern, thickness)
        direction:  Layout hint (left, right, up, down)
        note:       Note attached to the relationship
        left/right_head: Custom arrowhead symbols
    """

    source: str  # Component/interface name or alias
    target: str  # Component/interface name or alias
    type: RelationType = "association"
    label: Label | None = None
    source_label: str | None = None
    target_label: str | None = None
    style: LineStyle | None = None
    direction: Direction | None = None
    note: Label | None = None
    # Arrow head customization
    left_head: str | None = None  # e.g., "o", "*", "#", etc.
    right_head: str | None = None


@dataclass(frozen=True)
class ComponentNote:
    """A note annotation in a component diagram.

        content:  Note text
        position: Placement relative to target
        target:   Component to attach to (None for floating)
        floating: If True, not attached to any element
        color:    Note background color
    """

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
    """A complete component diagram ready for rendering.

    Contains all components, interfaces, relationships, and settings.
    Usually created via the component_diagram() builder.

        elements:        All diagram elements
        title:           Optional diagram title
        style:           Visual style ("uml1", "uml2", "rectangle")
        diagram_style:   CSS-like diagram styling (colors, fonts, etc.)
        hide_stereotype: If True, hide stereotype labels
    """

    elements: tuple[ComponentElement, ...] = field(default_factory=tuple)
    title: str | None = None
    style: ComponentStyle | None = None
    diagram_style: ComponentDiagramStyle | None = None
    # Skin parameters
    hide_stereotype: bool = False
