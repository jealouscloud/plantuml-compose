"""Deployment diagram builder with context manager syntax.

When to Use
-----------
Deployment diagrams show WHERE software runs on hardware/infrastructure.
Use when:

- Documenting production architecture
- Planning infrastructure (servers, containers, cloud resources)
- Showing network topology
- Visualizing artifacts on nodes

NOT for:
- Software module structure (use component diagram)
- Code organization (use class diagram)
- Runtime interactions (use sequence diagram)

Key Concepts
------------
Node:       Execution environment (server, VM, container, device)
Artifact:   Deployable unit (WAR, JAR, Docker image, executable)
Component:  Software piece running on a node

Node types (stereotypes):

    <<device>>      Physical hardware (server, router)
    <<executionEnvironment>>  VM, container runtime
    <<artifact>>    Deployable file

Nesting shows containment:

    ┌─────── node "Production Server" ──────┐
    │                                        │
    │  ┌──── node "Docker" ─────┐            │
    │  │  [API Container]       │            │
    │  │  [Worker Container]    │            │
    │  └────────────────────────┘            │
    │                                        │
    │  ((PostgreSQL))                        │
    └────────────────────────────────────────┘

Connections show network/communication:

    [Load Balancer] ──> [API Server]
    [API Server] ──> [Database]

Example
-------
    with deployment_diagram(title="Infrastructure") as d:
        with d.node("Server") as server:
            server.component("App")
            server.database("PostgreSQL")

        d.arrow("App", "PostgreSQL", label="connects")

    print(render(d.build()))
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Literal

from ..primitives.common import (
    ColorLike,
    Direction,
    Footer,
    Header,
    Label,
    Legend,
    LineStyleLike,
    Scale,
    Stereotype,
    StyleLike,
    coerce_direction,
    coerce_line_style,
    validate_style_background_only,
)
from ..primitives.deployment import (
    DeploymentDiagram,
    DeploymentDiagramElement,
    DeploymentElement,
    DeploymentNote,
    ElementType,
    Relationship,
    RelationType,
)


# Type alias for objects that can be used as relationship endpoints
DeploymentRef = DeploymentElement | str


class _BaseDeploymentBuilder:
    """Base class for deployment builders with shared methods."""

    def __init__(self) -> None:
        self._elements: list[DeploymentDiagramElement] = []
        self._refs: set[str] = set()  # Track valid element references

    def _register_ref(self, elem: DeploymentElement) -> None:
        """Register an element's ref for validation."""
        self._refs.add(elem._ref)
        if elem.alias:
            self._refs.add(elem.alias)

    def _validate_ref(self, ref: str, param_name: str) -> None:
        """Validate that a string reference exists in the diagram.

        Args:
            ref: The reference string to validate
            param_name: Parameter name for error message

        Raises:
            ValueError: If ref is not found in registered elements
        """
        if ref not in self._refs:
            available = sorted(self._refs) if self._refs else ["(none)"]
            raise ValueError(
                f'{param_name} "{ref}" not found. '
                f"Available: {', '.join(available)}"
            )

    def _to_ref(self, target: DeploymentRef) -> str:
        """Convert a deployment element reference to its string form.

        Accepts strings or DeploymentElement primitives.
        """
        if isinstance(target, str):
            return target
        return target._ref

    def _add_element(
        self,
        name: str,
        type: ElementType,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> DeploymentElement:
        """Add an element of any type."""
        if not name:
            raise ValueError("Element name cannot be empty")
        stereo = (
            Stereotype(name=stereotype) if isinstance(stereotype, str) else stereotype
        )
        style_obj = validate_style_background_only(style, "DeploymentElement")
        elem = DeploymentElement(
            name=name,
            type=type,
            alias=alias,
            stereotype=stereo,
            style=style_obj,
        )
        self._elements.append(elem)
        self._register_ref(elem)
        return elem

    # Element type shortcuts
    def actor(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> DeploymentElement:
        """Add an actor."""
        return self._add_element(
            name, "actor", alias=alias, stereotype=stereotype, style=style
        )

    def agent(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> DeploymentElement:
        """Add an agent."""
        return self._add_element(
            name, "agent", alias=alias, stereotype=stereotype, style=style
        )

    def artifact(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> DeploymentElement:
        """Add an artifact."""
        return self._add_element(
            name, "artifact", alias=alias, stereotype=stereotype, style=style
        )

    def boundary(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> DeploymentElement:
        """Add a boundary."""
        return self._add_element(
            name, "boundary", alias=alias, stereotype=stereotype, style=style
        )

    def card(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> DeploymentElement:
        """Add a card."""
        return self._add_element(
            name, "card", alias=alias, stereotype=stereotype, style=style
        )

    def circle(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> DeploymentElement:
        """Add a circle."""
        return self._add_element(
            name, "circle", alias=alias, stereotype=stereotype, style=style
        )

    def cloud(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> DeploymentElement:
        """Add a cloud (simple, non-nested)."""
        return self._add_element(
            name, "cloud", alias=alias, stereotype=stereotype, style=style
        )

    def collections(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> DeploymentElement:
        """Add a collections element."""
        return self._add_element(
            name, "collections", alias=alias, stereotype=stereotype, style=style
        )

    def component(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> DeploymentElement:
        """Add a component."""
        return self._add_element(
            name, "component", alias=alias, stereotype=stereotype, style=style
        )

    def control(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> DeploymentElement:
        """Add a control element."""
        return self._add_element(
            name, "control", alias=alias, stereotype=stereotype, style=style
        )

    def database(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> DeploymentElement:
        """Add a database (simple, non-nested)."""
        return self._add_element(
            name, "database", alias=alias, stereotype=stereotype, style=style
        )

    def entity(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> DeploymentElement:
        """Add an entity."""
        return self._add_element(
            name, "entity", alias=alias, stereotype=stereotype, style=style
        )

    def file(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> DeploymentElement:
        """Add a file."""
        return self._add_element(
            name, "file", alias=alias, stereotype=stereotype, style=style
        )

    def folder(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> DeploymentElement:
        """Add a folder (simple, non-nested)."""
        return self._add_element(
            name, "folder", alias=alias, stereotype=stereotype, style=style
        )

    def frame(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> DeploymentElement:
        """Add a frame (simple, non-nested)."""
        return self._add_element(
            name, "frame", alias=alias, stereotype=stereotype, style=style
        )

    def hexagon(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> DeploymentElement:
        """Add a hexagon."""
        return self._add_element(
            name, "hexagon", alias=alias, stereotype=stereotype, style=style
        )

    def interface(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> DeploymentElement:
        """Add an interface."""
        return self._add_element(
            name, "interface", alias=alias, stereotype=stereotype, style=style
        )

    def label(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> DeploymentElement:
        """Add a label."""
        return self._add_element(
            name, "label", alias=alias, stereotype=stereotype, style=style
        )

    def package(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> DeploymentElement:
        """Add a package (simple, non-nested)."""
        return self._add_element(
            name, "package", alias=alias, stereotype=stereotype, style=style
        )

    def person(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> DeploymentElement:
        """Add a person."""
        return self._add_element(
            name, "person", alias=alias, stereotype=stereotype, style=style
        )

    def process(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> DeploymentElement:
        """Add a process."""
        return self._add_element(
            name, "process", alias=alias, stereotype=stereotype, style=style
        )

    def queue(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> DeploymentElement:
        """Add a queue."""
        return self._add_element(
            name, "queue", alias=alias, stereotype=stereotype, style=style
        )

    def rectangle(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> DeploymentElement:
        """Add a rectangle (simple, non-nested)."""
        return self._add_element(
            name, "rectangle", alias=alias, stereotype=stereotype, style=style
        )

    def stack(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> DeploymentElement:
        """Add a stack."""
        return self._add_element(
            name, "stack", alias=alias, stereotype=stereotype, style=style
        )

    def storage(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> DeploymentElement:
        """Add a storage element."""
        return self._add_element(
            name, "storage", alias=alias, stereotype=stereotype, style=style
        )

    def usecase(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> DeploymentElement:
        """Add a usecase."""
        return self._add_element(
            name, "usecase", alias=alias, stereotype=stereotype, style=style
        )

    # Relationship methods
    def relationship(
        self,
        source: DeploymentRef,
        target: DeploymentRef,
        *,
        type: RelationType = "association",
        label: str | Label | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | Label | None = None,
    ) -> None:
        """Add a relationship between elements.

        Args:
            source: Source element (string or DeploymentElement)
            target: Target element (string or DeploymentElement)
            type: Relationship type
            label: Optional label
            style: Line style (color, pattern, thickness)
            direction: Layout direction hint (up, down, left, right)
            note: Note attached to the relationship
        """
        # Validate string refs
        if isinstance(source, str):
            self._validate_ref(source, "source")
        if isinstance(target, str):
            self._validate_ref(target, "target")

        label_obj = Label(label) if isinstance(label, str) else label
        style_obj = coerce_line_style(style) if style else None
        note_obj = Label(note) if isinstance(note, str) else note
        direction_val = coerce_direction(direction)
        rel = Relationship(
            source=self._to_ref(source),
            target=self._to_ref(target),
            type=type,
            label=label_obj,
            style=style_obj,
            direction=direction_val,
            note=note_obj,
        )
        self._elements.append(rel)

    def arrow(
        self,
        source: DeploymentRef,
        target: DeploymentRef,
        *,
        label: str | Label | None = None,
        dotted: bool = False,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | Label | None = None,
    ) -> None:
        """Add an arrow between elements.

        Args:
            source: Source element (string or DeploymentElement)
            target: Target element (string or DeploymentElement)
            label: Optional label
            dotted: Use dotted arrow style
            style: Line style (color, pattern, thickness)
            direction: Layout direction hint (up, down, left, right)
            note: Note attached to the arrow
        """
        # Validate string refs
        if isinstance(source, str):
            self._validate_ref(source, "source")
        if isinstance(target, str):
            self._validate_ref(target, "target")

        label_obj = Label(label) if isinstance(label, str) else label
        style_obj = coerce_line_style(style) if style else None
        note_obj = Label(note) if isinstance(note, str) else note
        direction_val = coerce_direction(direction)
        rel = Relationship(
            source=self._to_ref(source),
            target=self._to_ref(target),
            type="dotted_arrow" if dotted else "arrow",
            label=label_obj,
            style=style_obj,
            direction=direction_val,
            note=note_obj,
        )
        self._elements.append(rel)

    def link(
        self,
        source: DeploymentRef,
        target: DeploymentRef,
        *,
        label: str | Label | None = None,
        dotted: bool = False,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | Label | None = None,
    ) -> None:
        """Add a link (no arrow) between elements.

        Args:
            source: Source element (string or DeploymentElement)
            target: Target element (string or DeploymentElement)
            label: Optional label
            dotted: Use dotted line style
            style: Line style (color, pattern, thickness)
            direction: Layout direction hint (up, down, left, right)
            note: Note attached to the link
        """
        # Validate string refs
        if isinstance(source, str):
            self._validate_ref(source, "source")
        if isinstance(target, str):
            self._validate_ref(target, "target")

        label_obj = Label(label) if isinstance(label, str) else label
        style_obj = coerce_line_style(style) if style else None
        note_obj = Label(note) if isinstance(note, str) else note
        direction_val = coerce_direction(direction)
        rel = Relationship(
            source=self._to_ref(source),
            target=self._to_ref(target),
            type="dotted" if dotted else "line",
            label=label_obj,
            style=style_obj,
            direction=direction_val,
            note=note_obj,
        )
        self._elements.append(rel)

    def connect(
        self,
        hub: DeploymentRef,
        spokes: list[DeploymentRef],
        *,
        label: str | Label | None = None,
        dotted: bool = False,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
    ) -> None:
        """Connect a hub element to multiple spoke elements.

        Creates arrows from hub to each spoke. Useful for hub-and-spoke patterns
        like a load balancer connecting to multiple servers.

        Args:
            hub: Central element
            spokes: List of elements to connect to
            label: Optional label for all arrows
            dotted: Use dotted arrow style
            style: Line style (color, pattern, thickness)
            direction: Layout direction hint (up, down, left, right)
        """
        for spoke in spokes:
            self.arrow(
                hub, spoke, label=label, dotted=dotted, style=style, direction=direction
            )

    def note(
        self,
        content: str | Label,
        *,
        position: Literal["left", "right", "top", "bottom"] = "right",
        target: DeploymentRef | None = None,
        color: ColorLike | None = None,
    ) -> None:
        """Add a note."""
        text = content.text if isinstance(content, Label) else content
        if not text:
            raise ValueError("Note content cannot be empty")
        content_label = Label(content) if isinstance(content, str) else content
        target_ref = self._to_ref(target) if target else None
        n = DeploymentNote(
            content=content_label,
            position=position,
            target=target_ref,
            color=color,
        )
        self._elements.append(n)

    # Context managers for nested elements
    @contextmanager
    def node_nested(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> Iterator["_NestedElementBuilder"]:
        """Create a node with nested elements."""
        builder = _NestedElementBuilder("node", name, alias, stereotype, style)
        yield builder
        elem = builder._build()
        self._elements.append(elem)
        self._register_ref(elem)
        self._refs.update(builder._refs)

    @contextmanager
    def cloud_nested(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> Iterator["_NestedElementBuilder"]:
        """Create a cloud with nested elements."""
        builder = _NestedElementBuilder("cloud", name, alias, stereotype, style)
        yield builder
        elem = builder._build()
        self._elements.append(elem)
        self._register_ref(elem)
        self._refs.update(builder._refs)

    @contextmanager
    def database_nested(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> Iterator["_NestedElementBuilder"]:
        """Create a database with nested elements."""
        builder = _NestedElementBuilder("database", name, alias, stereotype, style)
        yield builder
        elem = builder._build()
        self._elements.append(elem)
        self._register_ref(elem)
        self._refs.update(builder._refs)

    @contextmanager
    def folder_nested(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> Iterator["_NestedElementBuilder"]:
        """Create a folder with nested elements."""
        builder = _NestedElementBuilder("folder", name, alias, stereotype, style)
        yield builder
        elem = builder._build()
        self._elements.append(elem)
        self._register_ref(elem)
        self._refs.update(builder._refs)

    @contextmanager
    def frame_nested(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> Iterator["_NestedElementBuilder"]:
        """Create a frame with nested elements."""
        builder = _NestedElementBuilder("frame", name, alias, stereotype, style)
        yield builder
        elem = builder._build()
        self._elements.append(elem)
        self._register_ref(elem)
        self._refs.update(builder._refs)

    @contextmanager
    def package_nested(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> Iterator["_NestedElementBuilder"]:
        """Create a package with nested elements."""
        builder = _NestedElementBuilder("package", name, alias, stereotype, style)
        yield builder
        elem = builder._build()
        self._elements.append(elem)
        self._register_ref(elem)
        self._refs.update(builder._refs)

    @contextmanager
    def rectangle_nested(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> Iterator["_NestedElementBuilder"]:
        """Create a rectangle with nested elements."""
        builder = _NestedElementBuilder("rectangle", name, alias, stereotype, style)
        yield builder
        elem = builder._build()
        self._elements.append(elem)
        self._register_ref(elem)
        self._refs.update(builder._refs)


class _NestedElementBuilder(_BaseDeploymentBuilder):
    """Builder for elements with nested content."""

    def __init__(
        self,
        type: ElementType,
        name: str,
        alias: str | None,
        stereotype: str | Stereotype | None,
        style: StyleLike | None,
    ) -> None:
        if not name:
            raise ValueError("Element name cannot be empty")
        super().__init__()
        self._type = type
        self._name = name
        self._alias = alias
        self._stereotype = (
            Stereotype(name=stereotype) if isinstance(stereotype, str) else stereotype
        )
        self._style = validate_style_background_only(style, "DeploymentElement")

    def _build(self) -> DeploymentElement:
        """Build the nested element."""
        return DeploymentElement(
            name=self._name,
            type=self._type,
            alias=self._alias,
            stereotype=self._stereotype,
            style=self._style,
            elements=tuple(self._elements),
        )


class DeploymentDiagramBuilder(_BaseDeploymentBuilder):
    """Builder for complete deployment diagrams.

    Usage:
        with deployment_diagram(title="Infrastructure") as d:
            with d.node_nested("Server") as server:
                server.component("App")
                server.database("PostgreSQL")

            d.arrow("App", "PostgreSQL", label="connects")

        diagram = d.build()
        print(render(diagram))
    """

    def __init__(
        self,
        *,
        title: str | None = None,
        caption: str | None = None,
        header: str | Header | None = None,
        footer: str | Footer | None = None,
        legend: str | Legend | None = None,
        scale: float | Scale | None = None,
    ) -> None:
        super().__init__()
        self._title = title
        self._caption = caption
        self._header = Header(header) if isinstance(header, str) else header
        self._footer = Footer(footer) if isinstance(footer, str) else footer
        self._legend = Legend(legend) if isinstance(legend, str) else legend
        self._scale = Scale(factor=scale) if isinstance(scale, (int, float)) else scale

    def build(self) -> DeploymentDiagram:
        """Build the complete deployment diagram."""
        return DeploymentDiagram(
            elements=tuple(self._elements),
            title=self._title,
            caption=self._caption,
            header=self._header,
            footer=self._footer,
            legend=self._legend,
            scale=self._scale,
        )

    def render(self) -> str:
        """Build and render the diagram to PlantUML text.

        Convenience method combining build() and render() in one call.
        """
        from ..renderers import render

        return render(self.build())


@contextmanager
def deployment_diagram(
    *,
    title: str | None = None,
    caption: str | None = None,
    header: str | Header | None = None,
    footer: str | Footer | None = None,
    legend: str | Legend | None = None,
    scale: float | Scale | None = None,
) -> Iterator[DeploymentDiagramBuilder]:
    """Create a deployment diagram with context manager syntax.

    Usage:
        with deployment_diagram(title="Infrastructure") as d:
            with d.node_nested("Server") as server:
                server.component("App")
                server.database("PostgreSQL")

            d.arrow("App", "PostgreSQL", label="connects")

        print(d.render())

    Args:
        title: Optional diagram title
        caption: Optional diagram caption
        header: Optional header text or Header object
        footer: Optional footer text or Footer object
        legend: Optional legend text or Legend object
        scale: Optional scale factor or Scale object

    Yields:
        A DeploymentDiagramBuilder for adding diagram elements
    """
    builder = DeploymentDiagramBuilder(
        title=title,
        caption=caption,
        header=header,
        footer=footer,
        legend=legend,
        scale=scale,
    )
    yield builder
