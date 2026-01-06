"""Use case diagram builder with context manager syntax.

Provides a fluent API for constructing use case diagrams:

    with usecase_diagram(title="Shopping System") as d:
        # Actors
        user = d.actor("Customer")
        admin = d.actor("Admin")

        # Use cases
        browse = d.usecase("Browse Products")
        checkout = d.usecase("Checkout")

        # Relationships
        d.arrow(user, browse)
        d.arrow(user, checkout)
        d.includes(checkout, "Validate Cart")

    print(d.render())
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from ..primitives.common import ColorLike, Label, Stereotype
from ..primitives.usecase import (
    Actor,
    ActorStyle,
    Container,
    ContainerType,
    Relationship,
    RelationType,
    UseCase,
    UseCaseDiagram,
    UseCaseDiagramElement,
    UseCaseNote,
)


class _BaseUseCaseBuilder:
    """Base class for use case builders with shared methods."""

    def __init__(self) -> None:
        self._elements: list[UseCaseDiagramElement] = []

    def actor(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
        business: bool = False,
    ) -> str:
        """Add an actor.

        Args:
            name: Actor name
            alias: Short alias for relationships
            stereotype: Stereotype annotation
            color: Background color
            business: Use business variant (actor/)

        Returns:
            The alias if provided, otherwise the name
        """
        if not name:
            raise ValueError("Actor name cannot be empty")
        stereo = Stereotype(name=stereotype) if isinstance(stereotype, str) else stereotype
        a = Actor(
            name=name,
            alias=alias,
            stereotype=stereo,
            color=color,
            business=business,
        )
        self._elements.append(a)
        return alias or name

    def usecase(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
        business: bool = False,
    ) -> str:
        """Add a use case.

        Args:
            name: Use case name
            alias: Short alias for relationships
            stereotype: Stereotype annotation
            color: Background color
            business: Use business variant (usecase/)

        Returns:
            The alias if provided, otherwise the use case reference
        """
        if not name:
            raise ValueError("Use case name cannot be empty")
        stereo = Stereotype(name=stereotype) if isinstance(stereotype, str) else stereotype
        uc = UseCase(
            name=name,
            alias=alias,
            stereotype=stereo,
            color=color,
            business=business,
        )
        self._elements.append(uc)
        return alias or f"({name})"

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
        color: ColorLike | None = None,
    ) -> None:
        """Add an arrow between elements.

        Args:
            source: Source element
            target: Target element
            label: Optional label
            color: Arrow color
        """
        label_obj = Label(label) if isinstance(label, str) else label
        rel = Relationship(
            source=source,
            target=target,
            type="arrow",
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
        color: ColorLike | None = None,
    ) -> None:
        """Add a simple link (no arrow) between elements."""
        label_obj = Label(label) if isinstance(label, str) else label
        rel = Relationship(
            source=source,
            target=target,
            type="association",
            label=label_obj,
            color=color,
        )
        self._elements.append(rel)

    def includes(
        self,
        source: str,
        target: str,
        *,
        color: ColorLike | None = None,
    ) -> None:
        """Add an include relationship.

        Args:
            source: Base use case
            target: Included use case
            color: Arrow color
        """
        rel = Relationship(
            source=source,
            target=target,
            type="include",
            color=color,
        )
        self._elements.append(rel)

    def extends(
        self,
        source: str,
        target: str,
        *,
        color: ColorLike | None = None,
    ) -> None:
        """Add an extends relationship.

        Args:
            source: Extending use case
            target: Base use case
            color: Arrow color
        """
        rel = Relationship(
            source=source,
            target=target,
            type="extends",
            color=color,
        )
        self._elements.append(rel)

    def generalizes(
        self,
        child: str,
        parent: str,
        *,
        color: ColorLike | None = None,
    ) -> None:
        """Add a generalization (extension) relationship.

        Args:
            child: Child actor/use case
            parent: Parent actor/use case
            color: Arrow color
        """
        rel = Relationship(
            source=child,
            target=parent,
            type="extension",
            color=color,
        )
        self._elements.append(rel)

    def note(
        self,
        content: str | Label,
        *,
        position: str = "right",
        target: str | None = None,
        floating: bool = False,
        color: ColorLike | None = None,
    ) -> None:
        """Add a note."""
        text = content.text if isinstance(content, Label) else content
        if not text:
            raise ValueError("Note content cannot be empty")
        content_label = Label(content) if isinstance(content, str) else content
        n = UseCaseNote(
            content=content_label,
            position=position,  # type: ignore[arg-type]
            target=target,
            floating=floating,
            color=color,
        )
        self._elements.append(n)

    @contextmanager
    def rectangle(
        self,
        name: str,
        *,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> Iterator["_ContainerBuilder"]:
        """Create a rectangle container.

        Usage:
            with d.rectangle("System") as r:
                r.usecase("Feature")
        """
        builder = _ContainerBuilder("rectangle", name, stereotype, color)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def package(
        self,
        name: str,
        *,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> Iterator["_ContainerBuilder"]:
        """Create a package container.

        Usage:
            with d.package("Module") as p:
                p.usecase("Feature")
        """
        builder = _ContainerBuilder("package", name, stereotype, color)
        yield builder
        self._elements.append(builder._build())


class _ContainerBuilder(_BaseUseCaseBuilder):
    """Builder for containers."""

    def __init__(
        self,
        type: ContainerType,
        name: str,
        stereotype: str | Stereotype | None,
        color: ColorLike | None,
    ) -> None:
        if not name:
            raise ValueError("Container name cannot be empty")
        super().__init__()
        self._type = type
        self._name = name
        self._stereotype = Stereotype(name=stereotype) if isinstance(stereotype, str) else stereotype
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


class UseCaseDiagramBuilder(_BaseUseCaseBuilder):
    """Builder for complete use case diagrams.

    Usage:
        with usecase_diagram(title="Shopping") as d:
            user = d.actor("Customer")
            browse = d.usecase("Browse")
            d.arrow(user, browse)

        print(d.render())
    """

    def __init__(
        self,
        *,
        title: str | None = None,
        actor_style: ActorStyle | None = None,
        left_to_right: bool = False,
    ) -> None:
        super().__init__()
        self._title = title
        self._actor_style = actor_style
        self._left_to_right = left_to_right

    def build(self) -> UseCaseDiagram:
        """Build the complete use case diagram."""
        return UseCaseDiagram(
            elements=tuple(self._elements),
            title=self._title,
            actor_style=self._actor_style,
            left_to_right=self._left_to_right,
        )

    def render(self) -> str:
        """Build and render the diagram to PlantUML text.

        Convenience method combining build() and render() in one call.
        """
        from ..renderers import render

        return render(self.build())


@contextmanager
def usecase_diagram(
    *,
    title: str | None = None,
    actor_style: ActorStyle | None = None,
    left_to_right: bool = False,
) -> Iterator[UseCaseDiagramBuilder]:
    """Create a use case diagram with context manager syntax.

    Usage:
        with usecase_diagram(title="Shopping System") as d:
            user = d.actor("Customer")
            browse = d.usecase("Browse Products")
            d.arrow(user, browse)

        print(d.render())

    Args:
        title: Optional diagram title
        actor_style: Actor style ("default", "awesome", "hollow")
        left_to_right: Use left to right layout direction

    Yields:
        A UseCaseDiagramBuilder for adding diagram elements
    """
    builder = UseCaseDiagramBuilder(
        title=title,
        actor_style=actor_style,
        left_to_right=left_to_right,
    )
    yield builder
