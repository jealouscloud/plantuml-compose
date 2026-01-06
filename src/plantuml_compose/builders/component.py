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
from typing import Iterator, Literal

from ..primitives.common import ColorLike, Label, Stereotype
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


class _BaseComponentBuilder:
    """Base class for component builders with shared methods."""

    def __init__(self) -> None:
        self._elements: list[ComponentElement] = []

    def component(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> str:
        """Add a component.

        Args:
            name: Component name
            alias: Short alias for relationships
            stereotype: Stereotype annotation (string or Stereotype object)
            color: Background color

        Returns:
            The alias if provided, otherwise the name (for use in relationships)
        """
        if not name:
            raise ValueError("Component name cannot be empty")
        stereo = Stereotype(name=stereotype) if isinstance(stereotype, str) else stereotype
        comp = Component(
            name=name,
            alias=alias,
            type="component",
            stereotype=stereo,
            color=color,
        )
        self._elements.append(comp)
        return alias or name

    def interface(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> str:
        """Add an interface.

        Args:
            name: Interface name
            alias: Short alias for relationships
            stereotype: Stereotype annotation (string or Stereotype object)
            color: Background color

        Returns:
            The alias if provided, otherwise the name
        """
        if not name:
            raise ValueError("Interface name cannot be empty")
        stereo = Stereotype(name=stereotype) if isinstance(stereotype, str) else stereotype
        iface = Interface(
            name=name,
            alias=alias,
            stereotype=stereo,
            color=color,
        )
        self._elements.append(iface)
        return alias or name

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
        source: str,
        target: str,
        *,
        type: RelationType = "association",
        label: str | Label | None = None,
        source_label: str | None = None,
        target_label: str | None = None,
        color: ColorLike | None = None,
    ) -> None:
        """Add a relationship between components.

        Args:
            source: Source component/interface
            target: Target component/interface
            type: Relationship type
            label: Relationship label
            source_label: Label near source
            target_label: Label near target
            color: Arrow color
        """
        label_obj = Label(label) if isinstance(label, str) else label
        rel = Relationship(
            source=source,
            target=target,
            type=type,
            label=label_obj,
            source_label=source_label,
            target_label=target_label,
            color=color,
        )
        self._elements.append(rel)

    def provides(
        self,
        component: str,
        interface: str,
        *,
        label: str | Label | None = None,
    ) -> None:
        """Component provides an interface (lollipop notation).

        Args:
            component: Component that provides
            interface: Interface being provided
            label: Optional label
        """
        label_obj = Label(label) if isinstance(label, str) else label
        rel = Relationship(
            source=component,
            target=interface,
            type="provides",
            label=label_obj,
        )
        self._elements.append(rel)

    def requires(
        self,
        component: str,
        interface: str,
        *,
        label: str | Label | None = None,
    ) -> None:
        """Component requires an interface.

        Args:
            component: Component that requires
            interface: Interface being required
            label: Optional label
        """
        label_obj = Label(label) if isinstance(label, str) else label
        rel = Relationship(
            source=component,
            target=interface,
            type="requires",
            label=label_obj,
        )
        self._elements.append(rel)

    def depends(
        self,
        source: str,
        target: str,
        *,
        label: str | Label | None = None,
    ) -> None:
        """Add a dependency (dotted arrow).

        Args:
            source: Dependent component
            target: Component being depended on
            label: Optional label
        """
        label_obj = Label(label) if isinstance(label, str) else label
        rel = Relationship(
            source=source,
            target=target,
            type="dependency",
            label=label_obj,
        )
        self._elements.append(rel)

    def link(
        self,
        source: str,
        target: str,
        *,
        label: str | Label | None = None,
        color: ColorLike | None = None,
    ) -> None:
        """Add a simple link (solid line).

        Args:
            source: Source component
            target: Target component
            label: Optional label
            color: Optional color
        """
        label_obj = Label(label) if isinstance(label, str) else label
        rel = Relationship(
            source=source,
            target=target,
            type="line",
            label=label_obj,
            color=color,
        )
        self._elements.append(rel)

    def arrow(
        self,
        source: str,
        target: str,
        *,
        label: str | Label | None = None,
        dotted: bool = False,
        color: ColorLike | None = None,
    ) -> None:
        """Add an arrow between components.

        Args:
            source: Source component
            target: Target component
            label: Optional label
            dotted: Use dotted line
            color: Optional color
        """
        label_obj = Label(label) if isinstance(label, str) else label
        rel = Relationship(
            source=source,
            target=target,
            type="dotted_arrow" if dotted else "arrow",
            label=label_obj,
            color=color,
        )
        self._elements.append(rel)

    def note(
        self,
        content: str | Label,
        *,
        position: Literal["left", "right", "top", "bottom"] = "right",
        target: str | None = None,
        floating: bool = False,
        color: ColorLike | None = None,
    ) -> None:
        """Add a note.

        Args:
            content: Note text
            position: "left", "right", "top", or "bottom"
            target: Component/interface to attach to
            floating: If True, creates a floating note
            color: Note background color
        """
        text = content.text if isinstance(content, Label) else content
        if not text:
            raise ValueError("Note content cannot be empty")
        content_label = Label(content) if isinstance(content, str) else content
        n = ComponentNote(
            content=content_label,
            position=position,
            target=target,
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
        stereotype: Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> Iterator["_ContainerBuilder"]:
        """Create a package container.

        Usage:
            with d.package("Domain") as pkg:
                pkg.component("Entity")
        """
        builder = _ContainerBuilder("package", name, stereotype, color)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def node(
        self,
        name: str,
        *,
        stereotype: Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> Iterator["_ContainerBuilder"]:
        """Create a node container.

        Usage:
            with d.node("Server") as n:
                n.component("App")
        """
        builder = _ContainerBuilder("node", name, stereotype, color)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def folder(
        self,
        name: str,
        *,
        stereotype: Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> Iterator["_ContainerBuilder"]:
        """Create a folder container."""
        builder = _ContainerBuilder("folder", name, stereotype, color)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def frame(
        self,
        name: str,
        *,
        stereotype: Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> Iterator["_ContainerBuilder"]:
        """Create a frame container."""
        builder = _ContainerBuilder("frame", name, stereotype, color)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def cloud(
        self,
        name: str,
        *,
        stereotype: Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> Iterator["_ContainerBuilder"]:
        """Create a cloud container."""
        builder = _ContainerBuilder("cloud", name, stereotype, color)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def database(
        self,
        name: str,
        *,
        stereotype: Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> Iterator["_ContainerBuilder"]:
        """Create a database container."""
        builder = _ContainerBuilder("database", name, stereotype, color)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def rectangle(
        self,
        name: str,
        *,
        stereotype: Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> Iterator["_ContainerBuilder"]:
        """Create a rectangle container."""
        builder = _ContainerBuilder("rectangle", name, stereotype, color)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def component_with_ports(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> Iterator["_ComponentWithPortsBuilder"]:
        """Create a component with ports.

        Usage:
            with d.component_with_ports("WebServer", alias="ws") as c:
                c.port("http")
                c.portin("requests")
                c.portout("responses")
        """
        builder = _ComponentWithPortsBuilder(name, alias, stereotype, color)
        yield builder
        self._elements.append(builder._build())


class _ContainerBuilder(_BaseComponentBuilder):
    """Builder for containers (package, node, folder, etc.)."""

    def __init__(
        self,
        type: ContainerType,
        name: str,
        stereotype: Stereotype | None,
        color: ColorLike | None,
    ) -> None:
        if not name:
            raise ValueError("Container name cannot be empty")
        super().__init__()
        self._type = type
        self._name = name
        self._stereotype = stereotype
        self._color = color

    def _build(self) -> Container:
        """Build the container."""
        return Container(
            name=self._name,
            type=self._type,
            elements=tuple(self._elements),
            stereotype=self._stereotype,
            color=self._color,
        )


class _ComponentWithPortsBuilder:
    """Builder for components with ports."""

    def __init__(
        self,
        name: str,
        alias: str | None,
        stereotype: Stereotype | None,
        color: ColorLike | None,
    ) -> None:
        self._name = name
        self._alias = alias
        self._stereotype = stereotype
        self._color = color
        self._elements: list[Port] = []

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
            color=self._color,
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
    """

    def __init__(
        self,
        *,
        title: str | None = None,
        style: ComponentStyle | None = None,
        hide_stereotype: bool = False,
    ) -> None:
        super().__init__()
        self._title = title
        self._style = style
        self._hide_stereotype = hide_stereotype

    def build(self) -> ComponentDiagram:
        """Build the complete component diagram."""
        return ComponentDiagram(
            elements=tuple(self._elements),
            title=self._title,
            style=self._style,
            hide_stereotype=self._hide_stereotype,
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
    hide_stereotype: bool = False,
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

    Args:
        title: Optional diagram title
        style: Component style ("uml1", "uml2", "rectangle")
        hide_stereotype: Hide all stereotypes

    Yields:
        A ComponentDiagramBuilder for adding diagram elements
    """
    builder = ComponentDiagramBuilder(
        title=title,
        style=style,
        hide_stereotype=hide_stereotype,
    )
    yield builder
