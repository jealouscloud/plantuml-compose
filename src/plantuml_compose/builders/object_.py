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
from typing import Iterator, Literal

from ..primitives.common import (
    ColorLike,
    Direction,
    Footer,
    Header,
    Label,
    Legend,
    LineStyle,
    LineStyleLike,
    Scale,
    Stereotype,
    StyleLike,
    coerce_line_style,
    validate_style_background_only,
)
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
        style: StyleLike | None = None,
    ) -> str:
        """Add a simple object without fields.

        Args:
            name: Object name
            alias: Short alias for relationships
            stereotype: Stereotype annotation
            style: Visual style (background, line, text_color)

        Returns:
            The alias if provided, otherwise the name
        """
        if not name:
            raise ValueError("Object name cannot be empty")
        stereo = Stereotype(name=stereotype) if isinstance(stereotype, str) else stereotype
        style_obj = validate_style_background_only(style, "Object")
        obj = Object(
            name=name,
            alias=alias,
            stereotype=stereo,
            style=style_obj,
        )
        self._elements.append(obj)
        return alias or name

    def object_with_fields(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
        fields: dict[str, str] | None = None,
    ) -> str:
        """Add an object with fields.

        Args:
            name: Object name
            alias: Short alias for relationships
            stereotype: Stereotype annotation
            style: Visual style (background, line, text_color)
            fields: Dictionary of field name -> value

        Returns:
            The alias if provided, otherwise the name
        """
        if not name:
            raise ValueError("Object name cannot be empty")
        stereo = Stereotype(name=stereotype) if isinstance(stereotype, str) else stereotype
        style_obj = validate_style_background_only(style, "Object")
        field_objs = tuple(Field(name=k, value=v) for k, v in (fields or {}).items())
        obj = Object(
            name=name,
            alias=alias,
            stereotype=stereo,
            style=style_obj,
            fields=field_objs,
        )
        self._elements.append(obj)
        return alias or name

    def map(
        self,
        name: str,
        *,
        alias: str | None = None,
        style: StyleLike | None = None,
        entries: dict[str, str] | None = None,
        links: dict[str, str] | None = None,
    ) -> str:
        """Add a map (associative array).

        Args:
            name: Map name
            alias: Short alias for relationships
            style: Visual style (background, line, text_color)
            entries: Dictionary of key -> value
            links: Dictionary of key -> object reference (for *-> syntax)

        Returns:
            The alias if provided, otherwise the name
        """
        if not name:
            raise ValueError("Map name cannot be empty")
        style_obj = validate_style_background_only(style, "Map")
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
            style=style_obj,
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
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | Label | None = None,
    ) -> None:
        """Add a relationship between objects.

        Args:
            source: Source object
            target: Target object
            type: Relationship type
            label: Optional label
            style: Line style (color, pattern, thickness)
            direction: Layout direction hint (up, down, left, right)
            note: Note attached to the relationship
        """
        label_obj = Label(label) if isinstance(label, str) else label
        style_obj = coerce_line_style(style) if style else None
        note_obj = Label(note) if isinstance(note, str) else note
        rel = Relationship(
            source=source,
            target=target,
            type=type,
            label=label_obj,
            style=style_obj,
            direction=direction,
            note=note_obj,
        )
        self._elements.append(rel)

    def arrow(
        self,
        source: str,
        target: str,
        *,
        label: str | Label | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | Label | None = None,
    ) -> None:
        """Add an arrow between objects.

        Args:
            source: Source object
            target: Target object
            label: Optional label
            style: Line style (color, pattern, thickness)
            direction: Layout direction hint (up, down, left, right)
            note: Note attached to the arrow
        """
        label_obj = Label(label) if isinstance(label, str) else label
        style_obj = coerce_line_style(style) if style else None
        note_obj = Label(note) if isinstance(note, str) else note
        rel = Relationship(
            source=source,
            target=target,
            type="arrow",
            label=label_obj,
            style=style_obj,
            direction=direction,
            note=note_obj,
        )
        self._elements.append(rel)

    def link(
        self,
        source: str,
        target: str,
        *,
        label: str | Label | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | Label | None = None,
    ) -> None:
        """Add a simple link between objects.

        Args:
            source: Source object
            target: Target object
            label: Optional label
            style: Line style (color, pattern, thickness)
            direction: Layout direction hint (up, down, left, right)
            note: Note attached to the link
        """
        label_obj = Label(label) if isinstance(label, str) else label
        style_obj = coerce_line_style(style) if style else None
        note_obj = Label(note) if isinstance(note, str) else note
        rel = Relationship(
            source=source,
            target=target,
            type="line",
            label=label_obj,
            style=style_obj,
            direction=direction,
            note=note_obj,
        )
        self._elements.append(rel)

    def composition(
        self,
        source: str,
        target: str,
        *,
        label: str | Label | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | Label | None = None,
    ) -> None:
        """Add a composition relationship (*--).

        Args:
            source: Source object (whole)
            target: Target object (part)
            label: Optional label
            style: Line style (color, pattern, thickness)
            direction: Layout direction hint (up, down, left, right)
            note: Note attached to the relationship
        """
        label_obj = Label(label) if isinstance(label, str) else label
        style_obj = coerce_line_style(style) if style else None
        note_obj = Label(note) if isinstance(note, str) else note
        rel = Relationship(
            source=source,
            target=target,
            type="composition",
            label=label_obj,
            style=style_obj,
            direction=direction,
            note=note_obj,
        )
        self._elements.append(rel)

    def aggregation(
        self,
        source: str,
        target: str,
        *,
        label: str | Label | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | Label | None = None,
    ) -> None:
        """Add an aggregation relationship (o--).

        Args:
            source: Source object (whole)
            target: Target object (part)
            label: Optional label
            style: Line style (color, pattern, thickness)
            direction: Layout direction hint (up, down, left, right)
            note: Note attached to the relationship
        """
        label_obj = Label(label) if isinstance(label, str) else label
        style_obj = coerce_line_style(style) if style else None
        note_obj = Label(note) if isinstance(note, str) else note
        rel = Relationship(
            source=source,
            target=target,
            type="aggregation",
            label=label_obj,
            style=style_obj,
            direction=direction,
            note=note_obj,
        )
        self._elements.append(rel)

    def extension(
        self,
        source: str,
        target: str,
        *,
        label: str | Label | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | Label | None = None,
    ) -> None:
        """Add an extension relationship (<|--).

        Args:
            source: Child object
            target: Parent object
            label: Optional label
            style: Line style (color, pattern, thickness)
            direction: Layout direction hint (up, down, left, right)
            note: Note attached to the relationship
        """
        label_obj = Label(label) if isinstance(label, str) else label
        style_obj = coerce_line_style(style) if style else None
        note_obj = Label(note) if isinstance(note, str) else note
        rel = Relationship(
            source=source,
            target=target,
            type="extension",
            label=label_obj,
            style=style_obj,
            direction=direction,
            note=note_obj,
        )
        self._elements.append(rel)

    def implementation(
        self,
        source: str,
        target: str,
        *,
        label: str | Label | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | Label | None = None,
    ) -> None:
        """Add an implementation relationship (<|..).

        Args:
            source: Implementing object
            target: Interface object
            label: Optional label
            style: Line style (color, pattern, thickness)
            direction: Layout direction hint (up, down, left, right)
            note: Note attached to the relationship
        """
        label_obj = Label(label) if isinstance(label, str) else label
        style_obj = coerce_line_style(style) if style else None
        note_obj = Label(note) if isinstance(note, str) else note
        rel = Relationship(
            source=source,
            target=target,
            type="implementation",
            label=label_obj,
            style=style_obj,
            direction=direction,
            note=note_obj,
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
        n = ObjectNote(
            content=content_label,
            position=position,
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

    def build(self) -> ObjectDiagram:
        """Build the complete object diagram."""
        return ObjectDiagram(
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
def object_diagram(
    *,
    title: str | None = None,
    caption: str | None = None,
    header: str | Header | None = None,
    footer: str | Footer | None = None,
    legend: str | Legend | None = None,
    scale: float | Scale | None = None,
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
        caption: Optional diagram caption
        header: Optional header text or Header object
        footer: Optional footer text or Footer object
        legend: Optional legend text or Legend object
        scale: Optional scale factor or Scale object

    Yields:
        An ObjectDiagramBuilder for adding diagram elements
    """
    builder = ObjectDiagramBuilder(
        title=title,
        caption=caption,
        header=header,
        footer=footer,
        legend=legend,
        scale=scale,
    )
    yield builder
