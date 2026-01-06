"""Deployment diagram builder with context manager syntax.

Provides a fluent API for constructing deployment diagrams:

    with deployment_diagram(title="Infrastructure") as d:
        with d.node("Server") as server:
            server.component("App")
            server.database("PostgreSQL")

        d.arrow("App", "PostgreSQL", label="connects")

    print(d.render())
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Literal

from ..primitives.common import ColorLike, Label, Stereotype
from ..primitives.deployment import (
    DeploymentDiagram,
    DeploymentDiagramElement,
    DeploymentElement,
    DeploymentNote,
    ElementType,
    Relationship,
    RelationType,
)


class _BaseDeploymentBuilder:
    """Base class for deployment builders with shared methods."""

    def __init__(self) -> None:
        self._elements: list[DeploymentDiagramElement] = []

    def _add_element(
        self,
        name: str,
        type: ElementType,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> str:
        """Add an element of any type."""
        if not name:
            raise ValueError("Element name cannot be empty")
        stereo = Stereotype(name=stereotype) if isinstance(stereotype, str) else stereotype
        elem = DeploymentElement(
            name=name,
            type=type,
            alias=alias,
            stereotype=stereo,
            color=color,
        )
        self._elements.append(elem)
        return alias or name

    # Element type shortcuts
    def actor(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> str:
        """Add an actor."""
        return self._add_element(name, "actor", alias=alias, stereotype=stereotype, color=color)

    def agent(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> str:
        """Add an agent."""
        return self._add_element(name, "agent", alias=alias, stereotype=stereotype, color=color)

    def artifact(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> str:
        """Add an artifact."""
        return self._add_element(name, "artifact", alias=alias, stereotype=stereotype, color=color)

    def boundary(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> str:
        """Add a boundary."""
        return self._add_element(name, "boundary", alias=alias, stereotype=stereotype, color=color)

    def card(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> str:
        """Add a card."""
        return self._add_element(name, "card", alias=alias, stereotype=stereotype, color=color)

    def circle(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> str:
        """Add a circle."""
        return self._add_element(name, "circle", alias=alias, stereotype=stereotype, color=color)

    def cloud(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> str:
        """Add a cloud (simple, non-nested)."""
        return self._add_element(name, "cloud", alias=alias, stereotype=stereotype, color=color)

    def collections(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> str:
        """Add a collections element."""
        return self._add_element(name, "collections", alias=alias, stereotype=stereotype, color=color)

    def component(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> str:
        """Add a component."""
        return self._add_element(name, "component", alias=alias, stereotype=stereotype, color=color)

    def control(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> str:
        """Add a control element."""
        return self._add_element(name, "control", alias=alias, stereotype=stereotype, color=color)

    def database(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> str:
        """Add a database (simple, non-nested)."""
        return self._add_element(name, "database", alias=alias, stereotype=stereotype, color=color)

    def entity(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> str:
        """Add an entity."""
        return self._add_element(name, "entity", alias=alias, stereotype=stereotype, color=color)

    def file(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> str:
        """Add a file."""
        return self._add_element(name, "file", alias=alias, stereotype=stereotype, color=color)

    def folder(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> str:
        """Add a folder (simple, non-nested)."""
        return self._add_element(name, "folder", alias=alias, stereotype=stereotype, color=color)

    def frame(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> str:
        """Add a frame (simple, non-nested)."""
        return self._add_element(name, "frame", alias=alias, stereotype=stereotype, color=color)

    def hexagon(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> str:
        """Add a hexagon."""
        return self._add_element(name, "hexagon", alias=alias, stereotype=stereotype, color=color)

    def interface(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> str:
        """Add an interface."""
        return self._add_element(name, "interface", alias=alias, stereotype=stereotype, color=color)

    def label(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> str:
        """Add a label."""
        return self._add_element(name, "label", alias=alias, stereotype=stereotype, color=color)

    def package(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> str:
        """Add a package (simple, non-nested)."""
        return self._add_element(name, "package", alias=alias, stereotype=stereotype, color=color)

    def person(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> str:
        """Add a person."""
        return self._add_element(name, "person", alias=alias, stereotype=stereotype, color=color)

    def process(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> str:
        """Add a process."""
        return self._add_element(name, "process", alias=alias, stereotype=stereotype, color=color)

    def queue(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> str:
        """Add a queue."""
        return self._add_element(name, "queue", alias=alias, stereotype=stereotype, color=color)

    def rectangle(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> str:
        """Add a rectangle (simple, non-nested)."""
        return self._add_element(name, "rectangle", alias=alias, stereotype=stereotype, color=color)

    def stack(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> str:
        """Add a stack."""
        return self._add_element(name, "stack", alias=alias, stereotype=stereotype, color=color)

    def storage(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> str:
        """Add a storage element."""
        return self._add_element(name, "storage", alias=alias, stereotype=stereotype, color=color)

    def usecase(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> str:
        """Add a usecase."""
        return self._add_element(name, "usecase", alias=alias, stereotype=stereotype, color=color)

    # Relationship methods
    def relationship(
        self,
        source: str,
        target: str,
        *,
        type: RelationType = "association",
        label: str | Label | None = None,
        color: ColorLike | None = None,
    ) -> None:
        """Add a relationship between elements."""
        label_obj = Label(label) if isinstance(label, str) else label
        rel = Relationship(
            source=source,
            target=target,
            type=type,
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
        """Add an arrow between elements."""
        label_obj = Label(label) if isinstance(label, str) else label
        rel = Relationship(
            source=source,
            target=target,
            type="dotted_arrow" if dotted else "arrow",
            label=label_obj,
            color=color,
        )
        self._elements.append(rel)

    def link(
        self,
        source: str,
        target: str,
        *,
        label: str | Label | None = None,
        dotted: bool = False,
        color: ColorLike | None = None,
    ) -> None:
        """Add a link (no arrow) between elements."""
        label_obj = Label(label) if isinstance(label, str) else label
        rel = Relationship(
            source=source,
            target=target,
            type="dotted" if dotted else "line",
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
        """Add a note."""
        text = content.text if isinstance(content, Label) else content
        if not text:
            raise ValueError("Note content cannot be empty")
        content_label = Label(content) if isinstance(content, str) else content
        n = DeploymentNote(
            content=content_label,
            position=position,
            target=target,
            floating=floating,
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
        color: ColorLike | None = None,
    ) -> Iterator["_NestedElementBuilder"]:
        """Create a node with nested elements."""
        builder = _NestedElementBuilder("node", name, alias, stereotype, color)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def cloud_nested(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> Iterator["_NestedElementBuilder"]:
        """Create a cloud with nested elements."""
        builder = _NestedElementBuilder("cloud", name, alias, stereotype, color)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def database_nested(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> Iterator["_NestedElementBuilder"]:
        """Create a database with nested elements."""
        builder = _NestedElementBuilder("database", name, alias, stereotype, color)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def folder_nested(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> Iterator["_NestedElementBuilder"]:
        """Create a folder with nested elements."""
        builder = _NestedElementBuilder("folder", name, alias, stereotype, color)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def frame_nested(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> Iterator["_NestedElementBuilder"]:
        """Create a frame with nested elements."""
        builder = _NestedElementBuilder("frame", name, alias, stereotype, color)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def package_nested(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> Iterator["_NestedElementBuilder"]:
        """Create a package with nested elements."""
        builder = _NestedElementBuilder("package", name, alias, stereotype, color)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def rectangle_nested(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> Iterator["_NestedElementBuilder"]:
        """Create a rectangle with nested elements."""
        builder = _NestedElementBuilder("rectangle", name, alias, stereotype, color)
        yield builder
        self._elements.append(builder._build())


class _NestedElementBuilder(_BaseDeploymentBuilder):
    """Builder for elements with nested content."""

    def __init__(
        self,
        type: ElementType,
        name: str,
        alias: str | None,
        stereotype: str | Stereotype | None,
        color: ColorLike | None,
    ) -> None:
        if not name:
            raise ValueError("Element name cannot be empty")
        super().__init__()
        self._type = type
        self._name = name
        self._alias = alias
        self._stereotype = Stereotype(name=stereotype) if isinstance(stereotype, str) else stereotype
        self._color = color

    def _build(self) -> DeploymentElement:
        """Build the nested element."""
        return DeploymentElement(
            name=self._name,
            type=self._type,
            alias=self._alias,
            stereotype=self._stereotype,
            color=self._color,
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
    ) -> None:
        super().__init__()
        self._title = title

    def build(self) -> DeploymentDiagram:
        """Build the complete deployment diagram."""
        return DeploymentDiagram(
            elements=tuple(self._elements),
            title=self._title,
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

    Yields:
        A DeploymentDiagramBuilder for adding diagram elements
    """
    builder = DeploymentDiagramBuilder(title=title)
    yield builder
