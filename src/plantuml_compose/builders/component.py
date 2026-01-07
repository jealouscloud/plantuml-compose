"""Component diagram builder with context manager syntax.

Provides a fluent API for constructing component diagrams:

    with component_diagram(title="System Architecture") as d:
        api = d.component("API Server")
        db = d.component("Database", stereotype="database")

        d.provides(api, "REST")
        d.requires(api, db, label="queries")

        with d.package("Infrastructure") as pkg:
            pkg.component("Load Balancer")

    print(d.render())
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Literal, TypeAlias, Union

from ..primitives.common import (
    ColorLike,
    ComponentDiagramStyle,
    ComponentDiagramStyleLike,
    Direction,
    Footer,
    Header,
    Label,
    Legend,
    LineStyleLike,
    NotePosition,
    sanitize_ref,
    Scale,
    Stereotype,
    StyleLike,
    coerce_component_diagram_style,
    coerce_line_style,
    coerce_style,
)
from ..primitives.component import (
    Component,
    ComponentDiagram,
    ComponentElement,
    ComponentNote,
    ComponentStyle,
    Container,
    ContainerType,
    Interface,
    Port,
    Relationship,
    RelationType,
)


# Type alias for objects that can be used as relationship endpoints
# Includes primitives (Component, Interface, Container) and their builders
ComponentRef: TypeAlias = Union[
    str,
    "Component",
    "Interface",
    "Container",
    "_ContainerBuilder",
    "_ComponentWithPortsBuilder",
]


class _BaseComponentBuilder:
    """Base class for component builders with shared methods."""

    def __init__(self) -> None:
        self._elements: list[ComponentElement] = []

    def _to_ref(self, target: ComponentRef) -> str:
        """Convert a component reference to its string form.

        Accepts strings, primitives (Component, Interface, Container), and
        builders (_ContainerBuilder, _ComponentWithPortsBuilder). This allows
        relationship methods to accept any of these types ergonomically.

        Args:
            target: Component reference (string, primitive, or builder)

        Returns:
            String reference suitable for use in relationships

        Example:
            with d.package("Backend") as backend:
                api = d.component("API")

            # All of these work:
            d.arrow("Frontend", api)        # String and Component
            d.arrow(backend, api)           # Builder and Component
            d.arrow(backend, "Database")    # Builder and string
        """
        if isinstance(target, str):
            return target
        # Primitives and builders both have _ref property
        if hasattr(target, "_ref"):
            ref = getattr(target, "_ref")
            if isinstance(ref, str):
                return ref
        return str(target)

    def component(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
        note: str | None = None,
        note_position: NotePosition = "right",
    ) -> Component:
        """Add a component.

        Args:
            name: Component name
            alias: Short alias for relationships
            stereotype: Stereotype annotation (string or Stereotype object)
            style: Visual styling (dict or Style with background, line, text_color)
            note: Optional note content (creates attached note)
            note_position: Position of note ("left", "right", "top", "bottom")

        Returns:
            The created Component (use in relationships via _to_ref or its _ref property)

        Example:
            api = d.component("API Server", note="Main entry point")
            d.component("Error", style={"background": "red", "text_color": "white"})
            d.arrow(api, db)  # Can pass Component directly
        """
        if not name:
            raise ValueError("Component name cannot be empty")
        stereo = Stereotype(name=stereotype) if isinstance(stereotype, str) else stereotype
        style_obj = coerce_style(style) if style else None
        comp = Component(
            name=name,
            alias=alias,
            type="component",
            stereotype=stereo,
            style=style_obj,
        )
        self._elements.append(comp)

        # Add note if provided
        if note:
            self._elements.append(ComponentNote(
                content=Label(note),
                position=note_position,  # type: ignore[arg-type]
                target=comp._ref,
            ))

        return comp

    def interface(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
        note: str | None = None,
        note_position: NotePosition = "right",
    ) -> Interface:
        """Add an interface.

        Args:
            name: Interface name
            alias: Short alias for relationships
            stereotype: Stereotype annotation (string or Stereotype object)
            style: Visual styling (dict or Style with background, line, text_color)
            note: Optional note content (creates attached note)
            note_position: Position of note ("left", "right", "top", "bottom")

        Returns:
            The created Interface (use in relationships via _to_ref or its _ref property)

        Example:
            rest = d.interface("REST API", note="HTTP endpoints")
            d.interface("IError", style={"background": "red"})
            d.provides(api, rest)  # Can pass Interface directly
        """
        if not name:
            raise ValueError("Interface name cannot be empty")
        stereo = Stereotype(name=stereotype) if isinstance(stereotype, str) else stereotype
        style_obj = coerce_style(style) if style else None
        iface = Interface(
            name=name,
            alias=alias,
            stereotype=stereo,
            style=style_obj,
        )
        self._elements.append(iface)

        # Add note if provided
        if note:
            self._elements.append(ComponentNote(
                content=Label(note),
                position=note_position,  # type: ignore[arg-type]
                target=iface._ref,
            ))

        return iface

    def components(
        self,
        *names: str,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> tuple[Component, ...]:
        """Create and register multiple components at once.

        Args:
            *names: Component names
            stereotype: Optional stereotype applied to all components
            color: Optional color applied to all components

        Returns:
            Tuple of created Components in order

        Example:
            api, db, cache = d.components("API", "Database", "Cache")
            d.arrow(api, db)
            d.arrow(api, cache)
        """
        return tuple(
            self.component(name, stereotype=stereotype, color=color)
            for name in names
        )

    def interfaces(
        self,
        *names: str,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> tuple[Interface, ...]:
        """Create and register multiple interfaces at once.

        Args:
            *names: Interface names
            stereotype: Optional stereotype applied to all interfaces
            color: Optional color applied to all interfaces

        Returns:
            Tuple of created Interfaces in order

        Example:
            rest, graphql, grpc = d.interfaces("REST", "GraphQL", "gRPC")
        """
        return tuple(
            self.interface(name, stereotype=stereotype, color=color)
            for name in names
        )

    def service(
        self,
        name: str,
        *,
        alias: str | None = None,
        provides: tuple[str, ...] | list[str] | None = None,
        requires: tuple[str, ...] | list[str] | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> Component:
        """Create a service component with its provided and required interfaces.

        A convenience method that creates a component along with its interface
        declarations and relationships in a single call. Reduces boilerplate for
        common service-oriented patterns.

        Args:
            name: Service component name
            alias: Short alias for relationships
            provides: Interface names this service provides (lollipop connections)
            requires: Interface names this service requires (socket connections)
            stereotype: Stereotype annotation (e.g., "service")
            color: Background color

        Returns:
            The created Component

        Example:
            # Instead of:
            api = d.component("API Gateway")
            rest = d.interface("REST")
            auth = d.interface("Auth")
            d.provides(api, rest)
            d.requires(api, auth)

            # Use:
            api = d.service("API Gateway",
                provides=("REST",),
                requires=("Auth",))
        """
        # Create the component
        comp = self.component(
            name,
            alias=alias,
            stereotype=stereotype,
            color=color,
        )

        # Create provided interfaces and relationships
        if provides:
            for iface_name in provides:
                iface = self.interface(iface_name)
                self.provides(comp, iface)

        # Create required interfaces and relationships
        if requires:
            for iface_name in requires:
                iface = self.interface(iface_name)
                self.requires(comp, iface)

        return comp

    def port(
        self,
        name: str,
        *,
        direction: str = "port",
    ) -> str:
        """Add a port (typically inside a component context).

        Args:
            name: Port name
            direction: "port", "portin", or "portout"

        Returns:
            The port name
        """
        if not name:
            raise ValueError("Port name cannot be empty")
        p = Port(name=name, direction=direction)  # type: ignore[arg-type]
        self._elements.append(p)
        return name

    def relationship(
        self,
        source: ComponentRef,
        target: ComponentRef,
        *,
        type: RelationType = "association",
        label: str | Label | None = None,
        source_label: str | None = None,
        target_label: str | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | Label | None = None,
    ) -> None:
        """Add a relationship between components.

        Args:
            source: Source component/interface (string, primitive, or builder)
            target: Target component/interface (string, primitive, or builder)
            type: Relationship type
            label: Relationship label
            source_label: Label near source
            target_label: Label near target
            style: Line style (dict or LineStyle with color, pattern, thickness)
            direction: Layout direction hint ("up", "down", "left", "right")
            note: Optional note attached to relationship
        """
        label_obj = Label(label) if isinstance(label, str) else label
        style_obj = coerce_line_style(style) if style else None
        note_obj = Label(note) if isinstance(note, str) else note
        rel = Relationship(
            source=self._to_ref(source),
            target=self._to_ref(target),
            type=type,
            label=label_obj,
            source_label=source_label,
            target_label=target_label,
            style=style_obj,
            direction=direction,
            note=note_obj,
        )
        self._elements.append(rel)

    def provides(
        self,
        component: ComponentRef,
        interface: ComponentRef,
        *,
        label: str | Label | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | Label | None = None,
    ) -> None:
        """Component provides an interface (lollipop notation).

        Args:
            component: Component that provides (string, primitive, or builder)
            interface: Interface being provided (string, primitive, or builder)
            label: Optional label
            style: Line style (dict or LineStyle with color, pattern, thickness)
            direction: Layout direction hint ("up", "down", "left", "right")
            note: Optional note attached to relationship
        """
        label_obj = Label(label) if isinstance(label, str) else label
        style_obj = coerce_line_style(style) if style else None
        note_obj = Label(note) if isinstance(note, str) else note
        rel = Relationship(
            source=self._to_ref(component),
            target=self._to_ref(interface),
            type="provides",
            label=label_obj,
            style=style_obj,
            direction=direction,
            note=note_obj,
        )
        self._elements.append(rel)

    def requires(
        self,
        component: ComponentRef,
        interface: ComponentRef,
        *,
        label: str | Label | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | Label | None = None,
    ) -> None:
        """Component requires an interface.

        Args:
            component: Component that requires (string, primitive, or builder)
            interface: Interface being required (string, primitive, or builder)
            label: Optional label
            style: Line style (dict or LineStyle with color, pattern, thickness)
            direction: Layout direction hint ("up", "down", "left", "right")
            note: Optional note attached to relationship
        """
        label_obj = Label(label) if isinstance(label, str) else label
        style_obj = coerce_line_style(style) if style else None
        note_obj = Label(note) if isinstance(note, str) else note
        rel = Relationship(
            source=self._to_ref(component),
            target=self._to_ref(interface),
            type="requires",
            label=label_obj,
            style=style_obj,
            direction=direction,
            note=note_obj,
        )
        self._elements.append(rel)

    def depends(
        self,
        source: ComponentRef,
        target: ComponentRef,
        *,
        label: str | Label | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | Label | None = None,
    ) -> None:
        """Add a dependency (dotted arrow).

        Args:
            source: Dependent component (string, primitive, or builder)
            target: Component being depended on (string, primitive, or builder)
            label: Optional label
            style: Line style (dict or LineStyle with color, pattern, thickness)
            direction: Layout direction hint ("up", "down", "left", "right")
            note: Optional note attached to relationship
        """
        label_obj = Label(label) if isinstance(label, str) else label
        style_obj = coerce_line_style(style) if style else None
        note_obj = Label(note) if isinstance(note, str) else note
        rel = Relationship(
            source=self._to_ref(source),
            target=self._to_ref(target),
            type="dependency",
            label=label_obj,
            style=style_obj,
            direction=direction,
            note=note_obj,
        )
        self._elements.append(rel)

    def link(
        self,
        source: ComponentRef,
        target: ComponentRef,
        *,
        label: str | Label | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | Label | None = None,
    ) -> None:
        """Add a simple link (solid line).

        Args:
            source: Source component (string, primitive, or builder)
            target: Target component (string, primitive, or builder)
            label: Optional label
            style: Line style (dict or LineStyle with color, pattern, thickness)
            direction: Layout direction hint ("up", "down", "left", "right")
            note: Optional note attached to relationship
        """
        label_obj = Label(label) if isinstance(label, str) else label
        style_obj = coerce_line_style(style) if style else None
        note_obj = Label(note) if isinstance(note, str) else note
        rel = Relationship(
            source=self._to_ref(source),
            target=self._to_ref(target),
            type="line",
            label=label_obj,
            style=style_obj,
            direction=direction,
            note=note_obj,
        )
        self._elements.append(rel)

    def arrow(
        self,
        *components: ComponentRef,
        label: str | Label | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | Label | None = None,
    ) -> list[Relationship]:
        """Add arrows between consecutive components.

        Args:
            *components: Two or more components to connect. Creates arrows:
                         components[0]->components[1], components[1]->components[2], etc.
            label: Optional label (applied to all arrows)
            style: Line style (dict or LineStyle with color, pattern, thickness)
            direction: Layout direction hint ("up", "down", "left", "right")
            note: Optional note attached to arrows

        Returns:
            List of created Relationships

        Examples:
            d.arrow(a, b)           # Single arrow: a -> b
            d.arrow(a, b, c)        # Chain: a -> b -> c (2 arrows)
            d.arrow(a, b, label="calls")  # All arrows labeled "calls"
            d.arrow(a, b, style={"color": "red", "pattern": "dashed"})
            d.arrow(a, b, direction="left", note="Important!")
        """
        if len(components) < 2:
            raise ValueError("arrow() requires at least 2 components")

        label_obj = Label(label) if isinstance(label, str) else label
        style_obj = coerce_line_style(style) if style else None
        note_obj = Label(note) if isinstance(note, str) else note

        # Determine arrow type from style pattern
        arrow_type: RelationType = "arrow"
        if style_obj and style_obj.pattern in ("dashed", "dotted"):
            arrow_type = "dotted_arrow"

        relationships: list[Relationship] = []
        for source, target in zip(components[:-1], components[1:]):
            rel = Relationship(
                source=self._to_ref(source),
                target=self._to_ref(target),
                type=arrow_type,
                label=label_obj,
                style=style_obj,
                direction=direction,
                note=note_obj,
            )
            self._elements.append(rel)
            relationships.append(rel)

        return relationships

    def chain(
        self,
        *items: ComponentRef | str,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
    ) -> list[Relationship]:
        """Create a chain of arrows with interleaved labels.

        A more ergonomic way to define a sequence of connected components with labels.
        Components are objects (Component, Interface, builders), labels are plain strings.

        Args:
            *items: Alternating components and labels. Labels between components
                    become arrow labels.
            style: Line style (dict or LineStyle with color, pattern, thickness)
            direction: Layout direction hint ("up", "down", "left", "right")

        Returns:
            List of created Relationships

        Examples:
            # Simple chain with labels
            d.chain(ui, "HTTP", api, "SQL", db)
            # Creates: ui --HTTP--> api --SQL--> db

            # Can omit labels for unlabeled arrows
            d.chain(a, b, c)  # Creates: a --> b --> c

            # Mix labeled and unlabeled
            d.chain(a, "call", b, c, "store", d)
            # Creates: a --call--> b --> c --store--> d

            # With styling
            d.chain(a, b, c, style={"color": "red", "pattern": "dashed"})

        Raises:
            ValueError: If items doesn't start with a component or has consecutive labels
        """
        if len(items) < 2:
            raise ValueError("chain() requires at least 2 components")

        style_obj = coerce_line_style(style) if style else None

        # Determine arrow type from style pattern
        arrow_type: RelationType = "arrow"
        if style_obj and style_obj.pattern in ("dashed", "dotted"):
            arrow_type = "dotted_arrow"

        relationships: list[Relationship] = []
        i = 0
        current_component: ComponentRef | None = None

        while i < len(items):
            item = items[i]

            # Check if this item is a component-like (not a label string)
            is_component = (
                not isinstance(item, str)
                or hasattr(item, "_ref")
            )

            if is_component:
                if current_component is not None:
                    # Create unlabeled arrow from previous component
                    rel = Relationship(
                        source=self._to_ref(current_component),
                        target=self._to_ref(item),
                        type=arrow_type,
                        style=style_obj,
                        direction=direction,
                    )
                    self._elements.append(rel)
                    relationships.append(rel)
                current_component = item
                i += 1
            elif isinstance(item, str):
                # This is a label - must have a current component and next item must be a component
                if current_component is None:
                    raise ValueError("chain() must start with a component, not a label")
                if i + 1 >= len(items):
                    raise ValueError("chain() cannot end with a label")

                next_item = items[i + 1]

                # Create arrow with label
                rel = Relationship(
                    source=self._to_ref(current_component),
                    target=self._to_ref(next_item),
                    type=arrow_type,
                    label=Label(item),
                    style=style_obj,
                    direction=direction,
                )
                self._elements.append(rel)
                relationships.append(rel)
                current_component = next_item
                i += 2  # Skip both label and next component
            else:
                raise ValueError(f"chain() received unexpected item type: {type(item)}")

        if len(relationships) == 0:
            raise ValueError("chain() requires at least 2 components")

        return relationships

    def note(
        self,
        content: str | Label,
        *,
        position: Literal["left", "right", "top", "bottom"] = "right",
        target: ComponentRef | None = None,
        floating: bool = False,
        color: ColorLike | None = None,
    ) -> None:
        """Add a note.

        Args:
            content: Note text
            position: "left", "right", "top", or "bottom"
            target: Component/interface to attach to (string, primitive, or builder)
            floating: If True, creates a floating note
            color: Note background color
        """
        text = content.text if isinstance(content, Label) else content
        if not text:
            raise ValueError("Note content cannot be empty")
        content_label = Label(content) if isinstance(content, str) else content
        target_ref = self._to_ref(target) if target is not None else None
        n = ComponentNote(
            content=content_label,
            position=position,
            target=target_ref,
            floating=floating,
            color=color,
        )
        self._elements.append(n)

    # Container context managers
    @contextmanager
    def package(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> Iterator["_ContainerBuilder"]:
        """Create a package container.

        Usage:
            with d.package("Domain", alias="dom") as pkg:
                pkg.component("Entity")

            d.arrow(dom, other)  # Reference by alias
        """
        builder = _ContainerBuilder("package", name, stereotype, style, alias)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def node(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> Iterator["_ContainerBuilder"]:
        """Create a node container.

        Usage:
            with d.node("Server", alias="srv") as n:
                n.component("App")
        """
        builder = _ContainerBuilder("node", name, stereotype, style, alias)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def folder(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> Iterator["_ContainerBuilder"]:
        """Create a folder container."""
        builder = _ContainerBuilder("folder", name, stereotype, style, alias)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def frame(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> Iterator["_ContainerBuilder"]:
        """Create a frame container."""
        builder = _ContainerBuilder("frame", name, stereotype, style, alias)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def cloud(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> Iterator["_ContainerBuilder"]:
        """Create a cloud container."""
        builder = _ContainerBuilder("cloud", name, stereotype, style, alias)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def database(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> Iterator["_ContainerBuilder"]:
        """Create a database container."""
        builder = _ContainerBuilder("database", name, stereotype, style, alias)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def rectangle(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> Iterator["_ContainerBuilder"]:
        """Create a rectangle container."""
        builder = _ContainerBuilder("rectangle", name, stereotype, style, alias)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def component_with_ports(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> Iterator["_ComponentWithPortsBuilder"]:
        """Create a component with ports.

        Usage:
            with d.component_with_ports("WebServer", alias="ws") as c:
                c.port("http")
                c.portin("requests")
                c.portout("responses")
        """
        builder = _ComponentWithPortsBuilder(name, alias, stereotype, style)
        yield builder
        self._elements.append(builder._build())


class _ContainerBuilder(_BaseComponentBuilder):
    """Builder for containers (package, node, folder, etc.)."""

    def __init__(
        self,
        type: ContainerType,
        name: str,
        stereotype: Stereotype | None,
        style: StyleLike | None,
        alias: str | None = None,
    ) -> None:
        if not name:
            raise ValueError("Container name cannot be empty")
        super().__init__()
        self._type = type
        self._name = name
        self._stereotype = stereotype
        self._style = coerce_style(style) if style else None
        self._alias = alias

    @property
    def _ref(self) -> str:
        """Reference name for use in relationships."""
        if self._alias:
            return self._alias
        return sanitize_ref(self._name)

    def _build(self) -> Container:
        """Build the container."""
        return Container(
            name=self._name,
            type=self._type,
            elements=tuple(self._elements),
            stereotype=self._stereotype,
            style=self._style,
            alias=self._alias,
        )


class _ComponentWithPortsBuilder:
    """Builder for components with ports."""

    def __init__(
        self,
        name: str,
        alias: str | None,
        stereotype: Stereotype | None,
        style: StyleLike | None,
    ) -> None:
        self._name = name
        self._alias = alias
        self._stereotype = stereotype
        self._style = coerce_style(style) if style else None
        self._elements: list[Port] = []

    @property
    def _ref(self) -> str:
        """Reference name for use in relationships."""
        if self._alias:
            return self._alias
        return sanitize_ref(self._name)

    def port(self, name: str) -> str:
        """Add a bidirectional port."""
        p = Port(name=name, direction="port")
        self._elements.append(p)
        return name

    def portin(self, name: str) -> str:
        """Add an input port."""
        p = Port(name=name, direction="portin")
        self._elements.append(p)
        return name

    def portout(self, name: str) -> str:
        """Add an output port."""
        p = Port(name=name, direction="portout")
        self._elements.append(p)
        return name

    def _build(self) -> Component:
        """Build the component."""
        return Component(
            name=self._name,
            alias=self._alias,
            type="component",
            stereotype=self._stereotype,
            style=self._style,
            elements=tuple(self._elements),
        )


class ComponentDiagramBuilder(_BaseComponentBuilder):
    """Builder for complete component diagrams.

    Usage:
        with component_diagram(title="System") as d:
            api = d.component("API")
            db = d.component("Database")
            d.arrow(api, db, label="queries")

        diagram = d.build()
        print(render(diagram))

    With dict-based styling (no extra imports needed):
        with component_diagram(
            diagram_style={
                "background": "white",
                "font_name": "Arial",
                "component": {"background": "#E3F2FD", "line_color": "#1976D2"},
                "arrow": {"line_color": "#757575"},
            }
        ) as d:
            d.component("Styled")
    """

    def __init__(
        self,
        *,
        title: str | None = None,
        style: ComponentStyle | None = None,
        diagram_style: ComponentDiagramStyleLike | None = None,
        hide_stereotype: bool = False,
        caption: str | None = None,
        header: str | Header | None = None,
        footer: str | Footer | None = None,
        legend: str | Legend | None = None,
        scale: float | Scale | None = None,
    ) -> None:
        super().__init__()
        self._title = title
        self._style = style
        # Coerce diagram_style dict to ComponentDiagramStyle object
        self._diagram_style = (
            coerce_component_diagram_style(diagram_style)
            if diagram_style is not None
            else None
        )
        self._hide_stereotype = hide_stereotype
        self._caption = caption
        self._header = Header(header) if isinstance(header, str) else header
        self._footer = Footer(footer) if isinstance(footer, str) else footer
        self._legend = Legend(legend) if isinstance(legend, str) else legend
        self._scale = Scale(factor=scale) if isinstance(scale, (int, float)) else scale

    def build(self) -> ComponentDiagram:
        """Build the complete component diagram."""
        return ComponentDiagram(
            elements=tuple(self._elements),
            title=self._title,
            style=self._style,
            diagram_style=self._diagram_style,
            hide_stereotype=self._hide_stereotype,
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
def component_diagram(
    *,
    title: str | None = None,
    style: ComponentStyle | None = None,
    diagram_style: ComponentDiagramStyleLike | None = None,
    hide_stereotype: bool = False,
    caption: str | None = None,
    header: str | Header | None = None,
    footer: str | Footer | None = None,
    legend: str | Legend | None = None,
    scale: float | Scale | None = None,
) -> Iterator[ComponentDiagramBuilder]:
    """Create a component diagram with context manager syntax.

    Usage:
        with component_diagram(title="System Architecture") as d:
            api = d.component("API Server")
            db = d.component("Database")

            with d.package("Backend") as pkg:
                pkg.component("Service")

            d.arrow(api, db, label="queries")

        print(d.render())

    With dict-based styling (no extra imports needed):
        with component_diagram(
            diagram_style={
                "background": "white",
                "font_name": "Arial",
                "component": {"background": "#E3F2FD", "line_color": "#1976D2"},
                "arrow": {"line_color": "#757575"},
            }
        ) as d:
            d.component("Styled")

    Args:
        title: Optional diagram title
        style: Component style ("uml1", "uml2", "rectangle")
        diagram_style: CSS-like diagram styling (dict or ComponentDiagramStyle object)
        hide_stereotype: Hide all stereotypes
        caption: Optional diagram caption
        header: Optional header text or Header object
        footer: Optional footer text or Footer object
        legend: Optional legend text or Legend object
        scale: Optional scale factor or Scale object

    Yields:
        A ComponentDiagramBuilder for adding diagram elements
    """
    builder = ComponentDiagramBuilder(
        title=title,
        style=style,
        diagram_style=diagram_style,
        hide_stereotype=hide_stereotype,
        caption=caption,
        header=header,
        footer=footer,
        legend=legend,
        scale=scale,
    )
    yield builder
