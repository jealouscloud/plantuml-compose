"""Component diagram composer.

Entities + connections — the flagship structural pattern.

Example:
    d = component_diagram(title="Wazuh Trips", theme="vibrant")
    el = d.elements
    c = d.connections

    wazuh = el.package("Wazuh",
        el.component("Agents", ref="agents"),
        el.database("OpenSearch"),
    )

    d.add(wazuh)

    d.connect(
        c.arrow(wazuh.agents, wazuh.opensearch, "events"),
    )

    puml = render(d)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ..primitives.common import (
    ColorLike,
    ComponentDiagramStyleLike,
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
    coerce_component_diagram_style,
    coerce_line_style,
    coerce_style,
    sanitize_ref,
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
    return coerce_style(value)


@dataclass(frozen=True)
class _RelationshipData:
    """Internal connection data."""
    source: EntityRef | str
    target: EntityRef | str
    type: RelationType
    label: str | None
    source_label: str | None
    target_label: str | None
    style: LineStyleLike | None
    direction: Direction | None


class ComponentElementNamespace:
    """Factory namespace for component diagram elements."""

    def component(
        self,
        name: str,
        *children: EntityRef,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> EntityRef:
        return EntityRef(
            name, ref=ref,
            data={
                "_type": "component",
                "stereotype": stereotype,
                "style": style,
                "children": children,
            },
            children=children,
        )

    def interface(
        self,
        name: str,
        *,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> EntityRef:
        return EntityRef(
            name, ref=ref,
            data={
                "_type": "interface",
                "stereotype": stereotype,
                "style": style,
            },
        )

    def package(
        self,
        name: str,
        *children: EntityRef,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> EntityRef:
        return self._container(
            name, "package", *children,
            ref=ref, stereotype=stereotype, style=style,
        )

    def database(
        self,
        name: str,
        *children: EntityRef,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> EntityRef:
        return self._container(
            name, "database", *children,
            ref=ref, stereotype=stereotype, style=style,
        )

    def cloud(
        self,
        name: str,
        *children: EntityRef,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> EntityRef:
        return self._container(
            name, "cloud", *children,
            ref=ref, stereotype=stereotype, style=style,
        )

    def node(
        self,
        name: str,
        *children: EntityRef,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> EntityRef:
        return self._container(
            name, "node", *children,
            ref=ref, stereotype=stereotype, style=style,
        )

    def folder(
        self,
        name: str,
        *children: EntityRef,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> EntityRef:
        return self._container(
            name, "folder", *children,
            ref=ref, stereotype=stereotype, style=style,
        )

    def frame(
        self,
        name: str,
        *children: EntityRef,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> EntityRef:
        return self._container(
            name, "frame", *children,
            ref=ref, stereotype=stereotype, style=style,
        )

    def rectangle(
        self,
        name: str,
        *children: EntityRef,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> EntityRef:
        return self._container(
            name, "rectangle", *children,
            ref=ref, stereotype=stereotype, style=style,
        )

    def _container(
        self,
        name: str,
        container_type: ContainerType,
        *children: EntityRef,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> EntityRef:
        return EntityRef(
            name, ref=ref,
            data={
                "_type": "container",
                "_container_type": container_type,
                "stereotype": stereotype,
                "style": style,
            },
            children=children,
        )


class ComponentConnectionNamespace:
    """Factory namespace for component diagram connections."""

    def arrow(
        self,
        source: EntityRef | str,
        target: EntityRef | str,
        label: str | None = None,
        *,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
    ) -> _RelationshipData:
        return _RelationshipData(
            source=source, target=target, type="arrow",
            label=label, source_label=None, target_label=None,
            style=style, direction=direction,
        )

    def dependency(
        self,
        source: EntityRef | str,
        target: EntityRef | str,
        label: str | None = None,
        *,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
    ) -> _RelationshipData:
        return _RelationshipData(
            source=source, target=target, type="dependency",
            label=label, source_label=None, target_label=None,
            style=style, direction=direction,
        )

    def link(
        self,
        source: EntityRef | str,
        target: EntityRef | str,
        label: str | None = None,
        *,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
    ) -> _RelationshipData:
        return _RelationshipData(
            source=source, target=target, type="association",
            label=label, source_label=None, target_label=None,
            style=style, direction=direction,
        )

    def arrows(
        self,
        *tuples: tuple[EntityRef | str, EntityRef | str, str | None],
    ) -> list[_RelationshipData]:
        return [
            self.arrow(s, t, lbl) for s, t, *rest in tuples
            for lbl in [rest[0] if rest else None]
        ]

    def lines(
        self,
        *tuples: tuple[EntityRef | str, EntityRef | str],
    ) -> list[_RelationshipData]:
        return [self.link(s, t) for s, t in tuples]


def _resolve_ref(item: EntityRef | str) -> str:
    if isinstance(item, EntityRef):
        return item._ref
    return item


def _build_element(ref: EntityRef) -> ComponentElement:
    """Convert an EntityRef to a component primitive."""
    data = ref._data
    element_type = data.get("_type", "component")

    if element_type == "interface":
        return Interface(
            name=ref._name,
            alias=ref._ref if ref._ref != sanitize_ref(ref._name) else None,
            stereotype=_coerce_stereotype(data.get("stereotype")),
            style=_coerce_style(data.get("style")),
        )

    if element_type == "container":
        children = tuple(_build_element(c) for c in ref._children.values())
        alias = ref._ref if ref._ref != sanitize_ref(ref._name) else None
        return Container(
            name=ref._name,
            type=data.get("_container_type", "package"),
            elements=children,
            stereotype=_coerce_stereotype(data.get("stereotype")),
            style=_coerce_style(data.get("style")),
            alias=alias,
        )

    # Default: component
    children = tuple(_build_element(c) for c in ref._children.values())
    alias = ref._ref if ref._ref != sanitize_ref(ref._name) else None
    return Component(
        name=ref._name,
        alias=alias,
        type="component",
        stereotype=_coerce_stereotype(data.get("stereotype")),
        style=_coerce_style(data.get("style")),
        elements=children,
    )


class ComponentComposer(BaseComposer):
    """Composer for component diagrams."""

    def __init__(
        self,
        *,
        title: str | None = None,
        theme: ThemeLike = None,
        layout: LayoutDirection | None = None,
        style: ComponentStyle | None = None,
        diagram_style: ComponentDiagramStyleLike | None = None,
        hide_stereotype: bool = False,
    ) -> None:
        super().__init__()
        self._title = title
        self._theme = theme
        self._layout = layout
        self._style = style
        self._diagram_style = (
            coerce_component_diagram_style(diagram_style)
            if diagram_style
            else None
        )
        self._hide_stereotype = hide_stereotype
        self._elements_ns = ComponentElementNamespace()
        self._connections_ns = ComponentConnectionNamespace()

    @property
    def elements(self) -> ComponentElementNamespace:
        return self._elements_ns

    @property
    def connections(self) -> ComponentConnectionNamespace:
        return self._connections_ns

    def build(self) -> ComponentDiagram:
        all_elements: list[ComponentElement] = []

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
                    source_label=conn.source_label,
                    target_label=conn.target_label,
                    style=coerce_line_style(conn.style) if conn.style else None,
                    direction=conn.direction,
                ))

        # Build notes
        for note_data in self._notes:
            target = note_data["target"]
            all_elements.append(ComponentNote(
                content=note_data["content"],
                position=note_data["position"],
                target=_resolve_ref(target) if target else None,
            ))

        return ComponentDiagram(
            elements=tuple(all_elements),
            title=self._title,
            theme=self._theme,
            layout=self._layout,
            style=self._style,
            diagram_style=self._diagram_style,
            hide_stereotype=self._hide_stereotype,
        )


def component_diagram(
    *,
    title: str | None = None,
    theme: ThemeLike = None,
    layout: LayoutDirection | None = None,
    style: ComponentStyle | None = None,
    diagram_style: ComponentDiagramStyleLike | None = None,
    hide_stereotype: bool = False,
) -> ComponentComposer:
    """Create a component diagram composer.

    Example:
        d = component_diagram(title="Architecture")
        el = d.elements
        c = d.connections
        api = el.component("API")
        db = el.database("PostgreSQL")
        d.add(api, db)
        d.connect(c.arrow(api, db, "queries"))
        print(render(d))
    """
    return ComponentComposer(
        title=title,
        theme=theme,
        layout=layout,
        style=style,
        diagram_style=diagram_style,
        hide_stereotype=hide_stereotype,
    )
