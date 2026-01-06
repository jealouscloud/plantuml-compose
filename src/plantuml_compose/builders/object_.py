"""Object diagram builder with context manager syntax.

Provides a fluent API for constructing object diagrams:

    with object_diagram(title="Order Example") as d:
        # Simple object
        customer = d.object("Customer", alias="cust")

        # Object with fields
        order = d.object_with_fields(
            "Order",
            alias="ord",
            fields={"id": "12345", "total": "$99.99"}
        )

        # Map (associative array)
        products = d.map("Products", alias="prod", entries={
            "item1": "Widget",
            "item2": "Gadget"
        })

        # Relationships
        d.arrow(customer, order)
        d.arrow(order, products)

    print(d.render())
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from ..primitives.common import ColorLike, Label, Stereotype
from ..primitives.object_ import (
    Field,
    Map,
    MapEntry,
    Object,
    ObjectDiagram,
    ObjectDiagramElement,
    ObjectNote,
    Relationship,
    RelationType,
)


class _BaseObjectBuilder:
    """Base class for object builders with shared methods."""

    def __init__(self) -> None:
        self._elements: list[ObjectDiagramElement] = []

    def object(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> str:
        """Add a simple object without fields.

        Args:
            name: Object name
            alias: Short alias for relationships
            stereotype: Stereotype annotation
            color: Background color

        Returns:
            The alias if provided, otherwise the name
        """
        if not name:
            raise ValueError("Object name cannot be empty")
        stereo = Stereotype(name=stereotype) if isinstance(stereotype, str) else stereotype
        obj = Object(
            name=name,
            alias=alias,
            stereotype=stereo,
            color=color,
        )
        self._elements.append(obj)
        return alias or name

    def object_with_fields(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
        fields: dict[str, str] | None = None,
    ) -> str:
        """Add an object with fields.

        Args:
            name: Object name
            alias: Short alias for relationships
            stereotype: Stereotype annotation
            color: Background color
            fields: Dictionary of field name -> value

        Returns:
            The alias if provided, otherwise the name
        """
        if not name:
            raise ValueError("Object name cannot be empty")
        stereo = Stereotype(name=stereotype) if isinstance(stereotype, str) else stereotype
        field_objs = tuple(Field(name=k, value=v) for k, v in (fields or {}).items())
        obj = Object(
            name=name,
            alias=alias,
            stereotype=stereo,
            color=color,
            fields=field_objs,
        )
        self._elements.append(obj)
        return alias or name

    def map(
        self,
        name: str,
        *,
        alias: str | None = None,
        color: ColorLike | None = None,
        entries: dict[str, str] | None = None,
        links: dict[str, str] | None = None,
    ) -> str:
        """Add a map (associative array).

        Args:
            name: Map name
            alias: Short alias for relationships
            color: Background color
            entries: Dictionary of key -> value
            links: Dictionary of key -> object reference (for *-> syntax)

        Returns:
            The alias if provided, otherwise the name
        """
        if not name:
            raise ValueError("Map name cannot be empty")
        entry_objs: list[MapEntry] = []

        # Add regular entries
        for key, value in (entries or {}).items():
            entry_objs.append(MapEntry(key=key, value=value))

        # Add linked entries
        for key, link in (links or {}).items():
            entry_objs.append(MapEntry(key=key, value="", link=link))

        map_obj = Map(
            name=name,
            alias=alias,
            color=color,
            entries=tuple(entry_objs),
        )
        self._elements.append(map_obj)
        return alias or name

    def relationship(
        self,
        source: str,
        target: str,
        *,
        type: RelationType = "association",
        label: str | Label | None = None,
        color: ColorLike | None = None,
    ) -> None:
        """Add a relationship between objects."""
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
        """Add an arrow between objects."""
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
        """Add a simple link between objects."""
        label_obj = Label(label) if isinstance(label, str) else label
        rel = Relationship(
            source=source,
            target=target,
            type="line",
            label=label_obj,
            color=color,
        )
        self._elements.append(rel)

    def composition(
        self,
        source: str,
        target: str,
        *,
        label: str | Label | None = None,
        color: ColorLike | None = None,
    ) -> None:
        """Add a composition relationship (*--)."""
        label_obj = Label(label) if isinstance(label, str) else label
        rel = Relationship(
            source=source,
            target=target,
            type="composition",
            label=label_obj,
            color=color,
        )
        self._elements.append(rel)

    def aggregation(
        self,
        source: str,
        target: str,
        *,
        label: str | Label | None = None,
        color: ColorLike | None = None,
    ) -> None:
        """Add an aggregation relationship (o--)."""
        label_obj = Label(label) if isinstance(label, str) else label
        rel = Relationship(
            source=source,
            target=target,
            type="aggregation",
            label=label_obj,
            color=color,
        )
        self._elements.append(rel)

    def extension(
        self,
        source: str,
        target: str,
        *,
        label: str | Label | None = None,
        color: ColorLike | None = None,
    ) -> None:
        """Add an extension relationship (<|--)."""
        label_obj = Label(label) if isinstance(label, str) else label
        rel = Relationship(
            source=source,
            target=target,
            type="extension",
            label=label_obj,
            color=color,
        )
        self._elements.append(rel)

    def implementation(
        self,
        source: str,
        target: str,
        *,
        label: str | Label | None = None,
        color: ColorLike | None = None,
    ) -> None:
        """Add an implementation relationship (<|..)."""
        label_obj = Label(label) if isinstance(label, str) else label
        rel = Relationship(
            source=source,
            target=target,
            type="implementation",
            label=label_obj,
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
        n = ObjectNote(
            content=content_label,
            position=position,  # type: ignore[arg-type]
            target=target,
            floating=floating,
            color=color,
        )
        self._elements.append(n)


class ObjectDiagramBuilder(_BaseObjectBuilder):
    """Builder for complete object diagrams.

    Usage:
        with object_diagram(title="Example") as d:
            customer = d.object("Customer", alias="cust")
            order = d.object_with_fields("Order", alias="ord", fields={"id": "123"})
            d.arrow(customer, order)

        print(d.render())
    """

    def __init__(
        self,
        *,
        title: str | None = None,
    ) -> None:
        super().__init__()
        self._title = title

    def build(self) -> ObjectDiagram:
        """Build the complete object diagram."""
        return ObjectDiagram(
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
def object_diagram(
    *,
    title: str | None = None,
) -> Iterator[ObjectDiagramBuilder]:
    """Create an object diagram with context manager syntax.

    Usage:
        with object_diagram(title="Order Example") as d:
            customer = d.object("Customer", alias="cust")
            order = d.object_with_fields(
                "Order",
                alias="ord",
                fields={"id": "12345", "total": "$99.99"}
            )
            d.arrow(customer, order)

        print(d.render())

    Args:
        title: Optional diagram title

    Yields:
        An ObjectDiagramBuilder for adding diagram elements
    """
    builder = ObjectDiagramBuilder(title=title)
    yield builder
