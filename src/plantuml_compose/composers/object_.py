"""Object diagram composer.

Entities + connections pattern for object diagrams.

Example:
    d = object_diagram(title="Server Snapshot")
    el = d.elements
    r = d.relationships

    node = el.object("vz-node-01 : Node", ref="n1", fields={
        "totalRAM": "64 GB",
        "usedMem": "58 GB",
    })
    ct = el.object("CT-101 : Container", ref="ct101", fields={
        "physpages.l": "8 GB",
    })

    d.add(node, ct)
    d.connect(r.composition(node, ct))

    puml = render(d)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ..primitives.common import (
    ColorLike,
    Direction,
    Footer,
    Header,
    Label,
    LayoutDirection,
    LayoutEngine,
    Legend,
    LineStyle,
    LineStyleLike,
    LineType,
    Scale,
    Stereotype,
    Style,
    StyleLike,
    ThemeLike,
    coerce_line_style,
    coerce_style,
    sanitize_ref,
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
from .base import BaseComposer, EntityRef


def _coerce_stereotype(value: str | Stereotype | None) -> Stereotype | None:
    if value is None:
        return None
    if isinstance(value, Stereotype):
        return value
    return Stereotype(name=value)


def _coerce_style(value: dict | Style | StyleLike | None) -> Style | None:
    if value is None:
        return None
    if isinstance(value, Style):
        return value
    return validate_style_background_only(value, "Object")


@dataclass(frozen=True)
class _RelationshipData:
    """Internal connection data."""
    source: EntityRef | str
    target: EntityRef | str
    type: RelationType
    label: str | None
    style: LineStyleLike | None
    direction: Direction | None
    note: str | None = None


class ObjectElementNamespace:
    """Factory namespace for object diagram elements."""

    def object(
        self,
        name: str,
        *,
        ref: str | None = None,
        fields: dict[str, str] | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> EntityRef:
        """Create an object element.

        If fields are provided, the object is created with those field values.
        """
        return EntityRef(
            name, ref=ref,
            data={
                "_type": "object",
                "fields": fields,
                "stereotype": stereotype,
                "style": style,
            },
        )

    def map(
        self,
        name: str,
        *,
        ref: str | None = None,
        entries: dict[str, str] | None = None,
        links: dict[str, EntityRef | str] | None = None,
        style: StyleLike | None = None,
    ) -> EntityRef:
        """Create a map (associative array) element.

        Args:
            name: Map name
            ref: Optional short reference name
            entries: Key-value pairs displayed as text (key => value)
            links: Key-object pairs with arrows from key to target object
            style: Visual style (background only)
        """
        return EntityRef(
            name, ref=ref,
            data={
                "_type": "map",
                "entries": entries,
                "links": links,
                "style": style,
            },
        )


class ObjectRelationshipNamespace:
    """Factory namespace for object diagram connections."""

    def arrow(
        self,
        source: EntityRef | str,
        target: EntityRef | str,
        label: str | None = None,
        *,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | None = None,
    ) -> _RelationshipData:
        return _RelationshipData(
            source=source, target=target, type="arrow",
            label=label, style=style, direction=direction,
            note=note,
        )

    def composition(
        self,
        source: EntityRef | str,
        target: EntityRef | str,
        label: str | None = None,
        *,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | None = None,
    ) -> _RelationshipData:
        return _RelationshipData(
            source=source, target=target, type="composition",
            label=label, style=style, direction=direction,
            note=note,
        )

    def aggregation(
        self,
        source: EntityRef | str,
        target: EntityRef | str,
        label: str | None = None,
        *,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | None = None,
    ) -> _RelationshipData:
        return _RelationshipData(
            source=source, target=target, type="aggregation",
            label=label, style=style, direction=direction,
            note=note,
        )

    def association(
        self,
        source: EntityRef | str,
        target: EntityRef | str,
        label: str | None = None,
        *,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | None = None,
    ) -> _RelationshipData:
        return _RelationshipData(
            source=source, target=target, type="association",
            label=label, style=style, direction=direction,
            note=note,
        )

    def link(
        self,
        source: EntityRef | str,
        target: EntityRef | str,
        label: str | None = None,
        *,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | None = None,
    ) -> _RelationshipData:
        return _RelationshipData(
            source=source, target=target, type="line",
            label=label, style=style, direction=direction,
            note=note,
        )

    def extension(
        self,
        source: EntityRef | str,
        target: EntityRef | str,
        label: str | None = None,
        *,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | None = None,
    ) -> _RelationshipData:
        return _RelationshipData(
            source=source, target=target, type="extension",
            label=label, style=style, direction=direction,
            note=note,
        )

    def implementation(
        self,
        source: EntityRef | str,
        target: EntityRef | str,
        label: str | None = None,
        *,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | None = None,
    ) -> _RelationshipData:
        return _RelationshipData(
            source=source, target=target, type="implementation",
            label=label, style=style, direction=direction,
            note=note,
        )


def _resolve_ref(item: EntityRef | str) -> str:
    if isinstance(item, EntityRef):
        return item._ref
    return item


def _build_element(ref: EntityRef) -> ObjectDiagramElement:
    """Convert an EntityRef to an object diagram primitive."""
    data = ref._data
    element_type = data.get("_type", "object")

    if element_type == "map":
        entry_objs: list[MapEntry] = []
        # Regular entries
        for k, v in (data.get("entries") or {}).items():
            entry_objs.append(MapEntry(key=k, value=v))
        # Linked entries
        for k, link_ref in (data.get("links") or {}).items():
            entry_objs.append(
                MapEntry(key=k, value="", link=_resolve_ref(link_ref))
            )
        style = _coerce_style(data.get("style"))
        alias = ref._ref if ref._ref != sanitize_ref(ref._name) else None
        return Map(
            name=ref._name,
            alias=alias,
            style=style,
            entries=tuple(entry_objs),
        )

    # Default: object
    fields = data.get("fields") or {}
    field_objs = tuple(
        Field(name=k, value=v) for k, v in fields.items()
    )
    alias = ref._ref if ref._ref != sanitize_ref(ref._name) else None
    return Object(
        name=ref._name,
        alias=alias,
        stereotype=_coerce_stereotype(data.get("stereotype")),
        style=_coerce_style(data.get("style")),
        fields=field_objs,
    )


class ObjectComposer(BaseComposer):
    """Composer for object diagrams."""

    def __init__(
        self,
        *,
        title: str | None = None,
        mainframe: str | None = None,
        caption: str | None = None,
        header: str | Header | None = None,
        footer: str | Footer | None = None,
        legend: str | Legend | None = None,
        scale: float | Scale | None = None,
        theme: ThemeLike = None,
        layout: LayoutDirection | None = None,
    ) -> None:
        super().__init__(
            title=title, mainframe=mainframe, caption=caption,
            header=header, footer=footer, legend=legend, scale=scale,
        )
        self._theme = theme
        self._layout = layout
        self._elements_ns = ObjectElementNamespace()
        self._relationships_ns = ObjectRelationshipNamespace()

    @property
    def elements(self) -> ObjectElementNamespace:
        return self._elements_ns

    @property
    def relationships(self) -> ObjectRelationshipNamespace:
        return self._relationships_ns

    def hub(
        self,
        hub: EntityRef | str,
        spokes: list[EntityRef | str],
        *,
        label: str | None = None,
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
            direction: Layout direction hint
        """
        r = self._relationships_ns
        for spoke in spokes:
            self._connections.append(
                r.arrow(hub, spoke, label, style=style, direction=direction)
            )

    def build(self) -> ObjectDiagram:
        all_elements: list[ObjectDiagramElement] = []

        # Build entity elements
        for item in self._elements:
            if isinstance(item, EntityRef):
                all_elements.append(_build_element(item))

        # Build relationships
        for conn in self._connections:
            if isinstance(conn, _RelationshipData):
                all_elements.append(Relationship(
                    source=_resolve_ref(conn.source),
                    target=_resolve_ref(conn.target),
                    type=conn.type,
                    label=Label(conn.label) if conn.label else None,
                    style=coerce_line_style(conn.style) if conn.style else None,
                    direction=conn.direction,
                    note=Label(conn.note) if conn.note else None,
                ))

        # Build notes
        for note_data in self._notes:
            target = note_data["target"]
            all_elements.append(ObjectNote(
                content=note_data["content"],
                position=note_data["position"],
                target=_resolve_ref(target) if target else None,
                color=note_data.get("color"),
            ))

        return ObjectDiagram(
            elements=tuple(all_elements),
            title=self._title,
            mainframe=self._mainframe,
            caption=self._caption,
            header=self._header,
            footer=self._footer,
            legend=self._legend,
            scale=self._scale,
            theme=self._theme,
            layout=self._layout,
        )


def object_diagram(
    *,
    title: str | None = None,
    mainframe: str | None = None,
    caption: str | None = None,
    header: str | Header | None = None,
    footer: str | Footer | None = None,
    legend: str | Legend | None = None,
    scale: float | Scale | None = None,
    theme: ThemeLike = None,
    layout: LayoutDirection | None = None,
) -> ObjectComposer:
    """Create an object diagram composer.

    Example:
        d = object_diagram(title="Snapshot")
        el = d.elements
        r = d.relationships
        node = el.object("Node", fields={"ram": "64GB"})
        ct = el.object("Container", fields={"mem": "8GB"})
        d.add(node, ct)
        d.connect(r.composition(node, ct))
        print(render(d))
    """
    return ObjectComposer(
        title=title, mainframe=mainframe, caption=caption,
        header=header, footer=footer, legend=legend, scale=scale,
        theme=theme, layout=layout,
    )
