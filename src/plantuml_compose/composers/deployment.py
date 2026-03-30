"""Deployment diagram composer.

Same entity + connection model as component, with recursive nesting.
All element types (node, artifact, database, storage, etc.) are
created from one unified element factory pattern.

Example:
    d = deployment_diagram(title="DC Topology")
    el = d.elements
    c = d.connections

    rack = el.frame("Rack",
        el.node("ToR Switch", ref="tor"),
        el.node("Host",
            el.artifact("app"),
        ),
    )
    d.add(rack)
    d.connect(c.arrow(rack.tor, rack["Host"]))
    puml = render(d)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ..primitives.common import (
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
    source: EntityRef | str
    target: EntityRef | str
    type: RelationType
    label: str | None
    style: LineStyleLike | None
    direction: Direction | None


class DeploymentElementNamespace:
    """Factory namespace for deployment diagram elements.

    Every method creates an element that can have children via positional args.
    """

    def _make(
        self,
        name: str,
        element_type: ElementType,
        *children: EntityRef,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> EntityRef:
        return EntityRef(
            name, ref=ref,
            data={
                "_type": element_type,
                "stereotype": stereotype,
                "style": style,
            },
            children=children,
        )

    def node(self, name: str, *children: EntityRef, ref: str | None = None,
             stereotype: str | Stereotype | None = None,
             style: StyleLike | None = None) -> EntityRef:
        return self._make(name, "node", *children, ref=ref,
                          stereotype=stereotype, style=style)

    def artifact(self, name: str, *children: EntityRef, ref: str | None = None,
                 stereotype: str | Stereotype | None = None,
                 style: StyleLike | None = None) -> EntityRef:
        return self._make(name, "artifact", *children, ref=ref,
                          stereotype=stereotype, style=style)

    def component(self, name: str, *children: EntityRef, ref: str | None = None,
                  stereotype: str | Stereotype | None = None,
                  style: StyleLike | None = None) -> EntityRef:
        return self._make(name, "component", *children, ref=ref,
                          stereotype=stereotype, style=style)

    def database(self, name: str, *children: EntityRef, ref: str | None = None,
                 stereotype: str | Stereotype | None = None,
                 style: StyleLike | None = None) -> EntityRef:
        return self._make(name, "database", *children, ref=ref,
                          stereotype=stereotype, style=style)

    def storage(self, name: str, *children: EntityRef, ref: str | None = None,
                stereotype: str | Stereotype | None = None,
                style: StyleLike | None = None) -> EntityRef:
        return self._make(name, "storage", *children, ref=ref,
                          stereotype=stereotype, style=style)

    def cloud(self, name: str, *children: EntityRef, ref: str | None = None,
              stereotype: str | Stereotype | None = None,
              style: StyleLike | None = None) -> EntityRef:
        return self._make(name, "cloud", *children, ref=ref,
                          stereotype=stereotype, style=style)

    def frame(self, name: str, *children: EntityRef, ref: str | None = None,
              stereotype: str | Stereotype | None = None,
              style: StyleLike | None = None) -> EntityRef:
        return self._make(name, "frame", *children, ref=ref,
                          stereotype=stereotype, style=style)

    def folder(self, name: str, *children: EntityRef, ref: str | None = None,
               stereotype: str | Stereotype | None = None,
               style: StyleLike | None = None) -> EntityRef:
        return self._make(name, "folder", *children, ref=ref,
                          stereotype=stereotype, style=style)

    def package(self, name: str, *children: EntityRef, ref: str | None = None,
                stereotype: str | Stereotype | None = None,
                style: StyleLike | None = None) -> EntityRef:
        return self._make(name, "package", *children, ref=ref,
                          stereotype=stereotype, style=style)

    def rectangle(self, name: str, *children: EntityRef, ref: str | None = None,
                  stereotype: str | Stereotype | None = None,
                  style: StyleLike | None = None) -> EntityRef:
        return self._make(name, "rectangle", *children, ref=ref,
                          stereotype=stereotype, style=style)

    def queue(self, name: str, *children: EntityRef, ref: str | None = None,
              stereotype: str | Stereotype | None = None,
              style: StyleLike | None = None) -> EntityRef:
        return self._make(name, "queue", *children, ref=ref,
                          stereotype=stereotype, style=style)

    def stack(self, name: str, *children: EntityRef, ref: str | None = None,
              stereotype: str | Stereotype | None = None,
              style: StyleLike | None = None) -> EntityRef:
        return self._make(name, "stack", *children, ref=ref,
                          stereotype=stereotype, style=style)

    def file(self, name: str, *children: EntityRef, ref: str | None = None,
             stereotype: str | Stereotype | None = None,
             style: StyleLike | None = None) -> EntityRef:
        return self._make(name, "file", *children, ref=ref,
                          stereotype=stereotype, style=style)

    def actor(self, name: str, *children: EntityRef, ref: str | None = None,
              stereotype: str | Stereotype | None = None,
              style: StyleLike | None = None) -> EntityRef:
        return self._make(name, "actor", *children, ref=ref,
                          stereotype=stereotype, style=style)

    def interface(self, name: str, *children: EntityRef, ref: str | None = None,
                  stereotype: str | Stereotype | None = None,
                  style: StyleLike | None = None) -> EntityRef:
        return self._make(name, "interface", *children, ref=ref,
                          stereotype=stereotype, style=style)


class DeploymentConnectionNamespace:
    """Factory namespace for deployment connections."""

    def arrow(self, source: EntityRef | str, target: EntityRef | str,
              label: str | None = None, *, style: LineStyleLike | None = None,
              direction: Direction | None = None) -> _RelationshipData:
        return _RelationshipData(source=source, target=target, type="arrow",
                                 label=label, style=style, direction=direction)

    def line(self, source: EntityRef | str, target: EntityRef | str,
             label: str | None = None, *, style: LineStyleLike | None = None,
             direction: Direction | None = None) -> _RelationshipData:
        return _RelationshipData(source=source, target=target, type="line",
                                 label=label, style=style, direction=direction)

    def dependency(self, source: EntityRef | str, target: EntityRef | str,
                   label: str | None = None, *, style: LineStyleLike | None = None,
                   direction: Direction | None = None) -> _RelationshipData:
        return _RelationshipData(source=source, target=target, type="dependency",
                                 label=label, style=style, direction=direction)

    def arrows(self, *tuples: tuple) -> list[_RelationshipData]:
        return [self.arrow(s, t, *rest) for s, t, *rest in tuples]

    def lines(self, *tuples: tuple[EntityRef | str, EntityRef | str]) -> list[_RelationshipData]:
        return [self.line(s, t) for s, t in tuples]


def _resolve_ref(item: EntityRef | str) -> str:
    if isinstance(item, EntityRef):
        return item._ref
    return item


def _build_element(ref: EntityRef) -> DeploymentElement:
    """Recursively convert EntityRef tree to DeploymentElement."""
    data = ref._data
    children = tuple(_build_element(c) for c in ref._children.values())
    alias = ref._ref if ref._ref != sanitize_ref(ref._name) else None
    return DeploymentElement(
        name=ref._name,
        type=data.get("_type", "node"),
        alias=alias,
        stereotype=_coerce_stereotype(data.get("stereotype")),
        style=_coerce_style(data.get("style")),
        elements=children,
    )


class DeploymentComposer(BaseComposer):
    """Composer for deployment diagrams."""

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
        self._elements_ns = DeploymentElementNamespace()
        self._connections_ns = DeploymentConnectionNamespace()

    @property
    def elements(self) -> DeploymentElementNamespace:
        return self._elements_ns

    @property
    def connections(self) -> DeploymentConnectionNamespace:
        return self._connections_ns

    def build(self) -> DeploymentDiagram:
        all_elements: list[DeploymentDiagramElement] = []

        for item in self._elements:
            if isinstance(item, EntityRef):
                all_elements.append(_build_element(item))

        for conn in self._connections:
            if isinstance(conn, _RelationshipData):
                all_elements.append(Relationship(
                    source=_resolve_ref(conn.source),
                    target=_resolve_ref(conn.target),
                    type=conn.type,
                    label=Label(conn.label) if conn.label else None,
                    style=coerce_line_style(conn.style) if conn.style else None,
                    direction=conn.direction,
                ))

        for note_data in self._notes:
            target = note_data["target"]
            all_elements.append(DeploymentNote(
                content=note_data["content"],
                position=note_data["position"],
                target=_resolve_ref(target) if target else None,
                color=note_data.get("color"),
            ))

        return DeploymentDiagram(
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


def deployment_diagram(
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
) -> DeploymentComposer:
    """Create a deployment diagram composer.

    Example:
        d = deployment_diagram(title="DC Topology")
        el = d.elements
        c = d.connections
        rack = el.frame("Rack", el.node("Host", el.artifact("app")))
        d.add(rack)
        print(render(d))
    """
    return DeploymentComposer(
        title=title, mainframe=mainframe, caption=caption,
        header=header, footer=footer, legend=legend, scale=scale,
        theme=theme, layout=layout,
    )
