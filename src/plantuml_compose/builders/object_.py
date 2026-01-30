"""Object diagram builder with context manager syntax.

When to Use
-----------
Object diagrams show instances at a specific point in time.
Use when:

- Showing concrete examples of class relationships
- Visualizing data state for debugging
- Illustrating test scenarios
- Documenting sample data structures

NOT for:
- General type structure (use class diagram)
- Behavior over time (use sequence or state diagram)
- System architecture (use component diagram)

Key Concepts
------------
Object:     An instance of a class with concrete values
Field:      Attribute with a specific value
Map:        Key-value collection (associative array)

Object notation:

    ┌────────────────────┐
    │ objectName : Type  │   <- underlined in UML
    ├────────────────────┤
    │ id = 12345         │   <- actual values
    │ status = "active"  │
    └────────────────────┘

Versus class diagram:

    Class Diagram (types):     Object Diagram (instances):
    ┌─────────────┐            ┌─────────────────┐
    │   Order     │            │ order1 : Order  │
    ├─────────────┤            ├─────────────────┤
    │ -id: int    │            │ id = 12345      │
    │ -status: str│            │ status = "paid" │
    └─────────────┘            └─────────────────┘

Relationships show links between specific instances:

    ┌────────────────┐         ┌─────────────────┐
    │ alice : User   │────────>│ order1 : Order  │
    └────────────────┘         └─────────────────┘

Example
-------
    with object_diagram(title="Order Example") as d:
        customer = d.object("Customer", alias="cust")
        order = d.object_with_fields(
            "Order", alias="ord",
            fields={"id": "12345", "total": "$99.99"}
        )

        d.arrow(customer, order)

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


# Type alias for objects that can be used as relationship endpoints
ObjectRef = Object | Map | str


class _BaseObjectBuilder:
    """Base class for object builders with shared methods."""

    def __init__(self) -> None:
        self._elements: list[ObjectDiagramElement] = []
        self._refs: set[str] = set()  # Track valid element references

    def _register_ref(self, elem: Object | Map) -> None:
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
                f'{param_name} "{ref}" not found. Available: {", ".join(available)}'
            )

    def _to_ref(self, target: ObjectRef) -> str:
        """Convert an object reference to its string form.

        Accepts strings, Object, or Map primitives.
        """
        if isinstance(target, str):
            return target
        return target._ref

    def object(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> Object:
        """Add a simple object without fields.

        Args:
            name: Object name
            alias: Optional short name to use instead of the auto-generated
                reference (e.g., "ord" instead of "order_123")
            stereotype: Label shown in «guillemets» above the name to
                categorize the object (e.g., "entity" renders as «entity»)
            style: Visual style (background, line, text_color)

        Returns:
            The created Object

        Example:
            customer = d.object("alice : Customer")
        """
        if not name:
            raise ValueError("Object name cannot be empty")
        stereo = (
            Stereotype(name=stereotype)
            if isinstance(stereotype, str)
            else stereotype
        )
        style_obj = validate_style_background_only(style, "Object")
        obj = Object(
            name=name,
            alias=alias,
            stereotype=stereo,
            style=style_obj,
        )
        self._elements.append(obj)
        self._register_ref(obj)
        return obj

    def object_with_fields(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
        fields: dict[str, str] | None = None,
    ) -> Object:
        """Add an object with fields.

        Args:
            name: Object name
            alias: Optional short name to use instead of the auto-generated
                reference (e.g., "ord" instead of "order_123")
            stereotype: Label shown in «guillemets» above the name to
                categorize the object (e.g., "entity" renders as «entity»)
            style: Visual style (background, line, text_color)
            fields: Dictionary of field name -> value

        Returns:
            The created Object

        Example:
            order = d.object_with_fields(
                "order1 : Order",
                fields={"id": "12345", "total": "$99.99"}
            )
        """
        if not name:
            raise ValueError("Object name cannot be empty")
        stereo = (
            Stereotype(name=stereotype)
            if isinstance(stereotype, str)
            else stereotype
        )
        style_obj = validate_style_background_only(style, "Object")
        field_objs = tuple(
            Field(name=k, value=v) for k, v in (fields or {}).items()
        )
        obj = Object(
            name=name,
            alias=alias,
            stereotype=stereo,
            style=style_obj,
            fields=field_objs,
        )
        self._elements.append(obj)
        self._register_ref(obj)
        return obj

    def map(
        self,
        name: str,
        *,
        alias: str | None = None,
        style: StyleLike | None = None,
        entries: dict[str, str] | None = None,
        links: dict[str, ObjectRef] | None = None,
    ) -> Map:
        """Add a map (associative array).

        Args:
            name: Map name
            alias: Optional short name to use instead of the auto-generated
                reference (e.g., "ord" instead of "order_123")
            style: Visual style (background, line, text_color)
            entries: Key-value pairs displayed as text (key => value)
            links: Key-object pairs displayed with arrows from key to target
                object. The key text links to the referenced Object or Map.

        Returns:
            The created Map

        Example:
            # Simple key-value entries
            config = d.map("config", entries={"env": "prod", "debug": "false"})

            # Entries with object references (arrows from key to object)
            user = d.object_("User")
            refs = d.map("refs", links={"owner": user})
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
            entry_objs.append(
                MapEntry(key=key, value="", link=self._to_ref(link))
            )

        map_obj = Map(
            name=name,
            alias=alias,
            style=style_obj,
            entries=tuple(entry_objs),
        )
        self._elements.append(map_obj)
        self._register_ref(map_obj)
        return map_obj

    def relationship(
        self,
        source: ObjectRef,
        target: ObjectRef,
        *,
        type: RelationType = "association",
        label: str | Label | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | Label | None = None,
    ) -> None:
        """Add a relationship between objects.

        Args:
            source: Source object (string, Object, or Map)
            target: Target object (string, Object, or Map)
            type: Relationship type
            label: Optional label
            style: Line style (color, pattern, thickness)
            direction: Layout direction hint (up, down, left, right)
            note: Note attached to the relationship

        Example:
            d.relationship(user, order, type="composition")
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
        source: ObjectRef,
        target: ObjectRef,
        *,
        label: str | Label | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | Label | None = None,
    ) -> None:
        """Add an arrow between objects.

        Args:
            source: Source object (string, Object, or Map)
            target: Target object (string, Object, or Map)
            label: Optional label
            style: Line style (color, pattern, thickness)
            direction: Layout direction hint (up, down, left, right)
            note: Note attached to the arrow

        Example:
            d.arrow(customer, order, label="places")
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
            type="arrow",
            label=label_obj,
            style=style_obj,
            direction=direction_val,
            note=note_obj,
        )
        self._elements.append(rel)

    def link(
        self,
        source: ObjectRef,
        target: ObjectRef,
        *,
        label: str | Label | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | Label | None = None,
    ) -> None:
        """Add a simple link between objects.

        Args:
            source: Source object (string, Object, or Map)
            target: Target object (string, Object, or Map)
            label: Optional label
            style: Line style (color, pattern, thickness)
            direction: Layout direction hint (up, down, left, right)
            note: Note attached to the link

        Example:
            d.link(user1, user2, label="knows")
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
            type="line",
            label=label_obj,
            style=style_obj,
            direction=direction_val,
            note=note_obj,
        )
        self._elements.append(rel)

    def composition(
        self,
        source: ObjectRef,
        target: ObjectRef,
        *,
        label: str | Label | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | Label | None = None,
    ) -> None:
        """Add a composition relationship (*--).

        Args:
            source: Source object (whole) - string, Object, or Map
            target: Target object (part) - string, Object, or Map
            label: Optional label
            style: Line style (color, pattern, thickness)
            direction: Layout direction hint (up, down, left, right)
            note: Note attached to the relationship

        Example:
            d.composition(house, room)  # room is part of house
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
            type="composition",
            label=label_obj,
            style=style_obj,
            direction=direction_val,
            note=note_obj,
        )
        self._elements.append(rel)

    def aggregation(
        self,
        source: ObjectRef,
        target: ObjectRef,
        *,
        label: str | Label | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | Label | None = None,
    ) -> None:
        """Add an aggregation relationship (o--).

        Args:
            source: Source object (whole) - string, Object, or Map
            target: Target object (part) - string, Object, or Map
            label: Optional label
            style: Line style (color, pattern, thickness)
            direction: Layout direction hint (up, down, left, right)
            note: Note attached to the relationship

        Example:
            d.aggregation(team, player)  # player belongs to team
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
            type="aggregation",
            label=label_obj,
            style=style_obj,
            direction=direction_val,
            note=note_obj,
        )
        self._elements.append(rel)

    def extension(
        self,
        source: ObjectRef,
        target: ObjectRef,
        *,
        label: str | Label | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | Label | None = None,
    ) -> None:
        """Add an extension relationship (<|--).

        Args:
            source: Child object - string, Object, or Map
            target: Parent object - string, Object, or Map
            label: Optional label
            style: Line style (color, pattern, thickness)
            direction: Layout direction hint (up, down, left, right)
            note: Note attached to the relationship

        Example:
            d.extension(dog, animal)  # dog extends animal
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
            type="extension",
            label=label_obj,
            style=style_obj,
            direction=direction_val,
            note=note_obj,
        )
        self._elements.append(rel)

    def implementation(
        self,
        source: ObjectRef,
        target: ObjectRef,
        *,
        label: str | Label | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | Label | None = None,
    ) -> None:
        """Add an implementation relationship (<|..).

        Args:
            source: Implementing object - string, Object, or Map
            target: Interface object - string, Object, or Map
            label: Optional label
            style: Line style (color, pattern, thickness)
            direction: Layout direction hint (up, down, left, right)
            note: Note attached to the relationship

        Example:
            d.implementation(arraylist, list)
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
            type="implementation",
            label=label_obj,
            style=style_obj,
            direction=direction_val,
            note=note_obj,
        )
        self._elements.append(rel)

    def connect(
        self,
        hub: ObjectRef,
        spokes: list[ObjectRef],
        *,
        label: str | Label | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
    ) -> None:
        """Connect a hub object to multiple spoke objects.

        Creates arrows from hub to each spoke. Useful for hub-and-spoke patterns.

        Args:
            hub: Central object
            spokes: List of objects to connect to
            label: Optional label for all arrows
            style: Line style (color, pattern, thickness)
            direction: Layout direction hint (up, down, left, right)

        Example:
            d.connect(server, [client1, client2, client3])
        """
        for spoke in spokes:
            self.arrow(
                hub, spoke, label=label, style=style, direction=direction
            )

    def note(
        self,
        content: str | Label,
        *,
        position: Literal["left", "right", "top", "bottom"] = "right",
        target: ObjectRef | None = None,
        color: ColorLike | None = None,
    ) -> None:
        """Add a note.

        Example:
            d.note("Current state", target=order)
        """
        text = content.text if isinstance(content, Label) else content
        if not text:
            raise ValueError("Note content cannot be empty")
        content_label = Label(content) if isinstance(content, str) else content
        target_ref = self._to_ref(target) if target else None
        n = ObjectNote(
            content=content_label,
            position=position,
            target=target_ref,
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
        theme: str | None = None,
    ) -> None:
        super().__init__()
        self._title = title
        self._caption = caption
        self._header = Header(header) if isinstance(header, str) else header
        self._footer = Footer(footer) if isinstance(footer, str) else footer
        self._legend = Legend(legend) if isinstance(legend, str) else legend
        self._scale = (
            Scale(factor=scale) if isinstance(scale, (int, float)) else scale
        )
        self._theme = theme

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
            theme=self._theme,
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
    theme: str | None = None,
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
        theme: Optional PlantUML theme name (e.g., "cerulean", "amiga")

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
        theme=theme,
    )
    yield builder
