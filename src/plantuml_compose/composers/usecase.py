"""Use case diagram composer.

Entities + connections pattern for use case diagrams.

Example:
    d = usecase_diagram(title="Incident Management")
    el = d.elements
    r = d.relationships

    engineer = el.actor("Engineer")
    lifecycle = el.package("Incident Lifecycle",
        el.usecase("View Active Alerts", ref="view_alerts"),
        el.usecase("Open Incident", ref="open_incident"),
    )

    d.add(engineer, lifecycle)
    d.connect(
        r.arrow(engineer, lifecycle.view_alerts),
        r.arrow(engineer, lifecycle.open_incident),
    )

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
    return validate_style_background_only(value, "UseCase")


@dataclass(frozen=True)
class _RelationshipData:
    """Internal connection data."""
    source: EntityRef | str
    target: EntityRef | str
    type: RelationType
    label: str | None
    style: LineStyleLike | None
    direction: Direction | None


class UseCaseElementNamespace:
    """Factory namespace for use case diagram elements."""

    def actor(
        self,
        name: str,
        *,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
        business: bool = False,
    ) -> EntityRef:
        return EntityRef(
            name, ref=ref,
            data={
                "_type": "actor",
                "stereotype": stereotype,
                "style": style,
                "business": business,
            },
        )

    def usecase(
        self,
        name: str,
        *,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
        business: bool = False,
    ) -> EntityRef:
        return EntityRef(
            name, ref=ref,
            data={
                "_type": "usecase",
                "stereotype": stereotype,
                "style": style,
                "business": business,
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


class UseCaseRelationshipNamespace:
    """Factory namespace for use case diagram connections."""

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
            label=label, style=style, direction=direction,
        )

    def generalizes(
        self,
        child: EntityRef | str,
        parent: EntityRef | str,
        *,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
    ) -> _RelationshipData:
        """Generalization: child is-a parent.

        Maps to PlantUML extension type with source=child, target=parent.
        This matches the old builder's generalizes() which sets
        source=child, target=parent, type="extension".
        """
        return _RelationshipData(
            source=child, target=parent, type="extension",
            label=None, style=style, direction=direction,
        )

    def include(
        self,
        base: EntityRef | str,
        required: EntityRef | str,
        *,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
    ) -> _RelationshipData:
        """Include: base always invokes required."""
        return _RelationshipData(
            source=base, target=required, type="include",
            label=None, style=style, direction=direction,
        )

    def extends(
        self,
        extension: EntityRef | str,
        base: EntityRef | str,
        *,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
    ) -> _RelationshipData:
        """Extends: extension optionally extends base."""
        return _RelationshipData(
            source=extension, target=base, type="extends",
            label=None, style=style, direction=direction,
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
            label=label, style=style, direction=direction,
        )


def _resolve_ref(item: EntityRef | str) -> str:
    if isinstance(item, EntityRef):
        return item._ref
    return item


def _build_element(ref: EntityRef) -> UseCaseDiagramElement:
    """Convert an EntityRef to a use case diagram primitive."""
    data = ref._data
    element_type = data.get("_type", "usecase")

    if element_type == "actor":
        alias = ref._ref if ref._ref != sanitize_ref(ref._name) else None
        return Actor(
            name=ref._name,
            alias=alias,
            stereotype=_coerce_stereotype(data.get("stereotype")),
            style=_coerce_style(data.get("style")),
            business=data.get("business", False),
        )

    if element_type == "container":
        children = tuple(_build_element(c) for c in ref._children.values())
        alias = None  # Containers don't use alias in usecase primitives
        return Container(
            name=ref._name,
            type=data.get("_container_type", "package"),
            elements=children,
            stereotype=_coerce_stereotype(data.get("stereotype")),
            style=_coerce_style(data.get("style")),
        )

    # Default: usecase
    alias = ref._ref if ref._ref != sanitize_ref(ref._name) else None
    return UseCase(
        name=ref._name,
        alias=alias,
        stereotype=_coerce_stereotype(data.get("stereotype")),
        style=_coerce_style(data.get("style")),
        business=data.get("business", False),
    )


class UseCaseComposer(BaseComposer):
    """Composer for use case diagrams."""

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
        actor_style: ActorStyle | None = None,
    ) -> None:
        super().__init__(
            title=title, mainframe=mainframe, caption=caption,
            header=header, footer=footer, legend=legend, scale=scale,
        )
        self._theme = theme
        self._layout = layout
        self._actor_style = actor_style
        self._elements_ns = UseCaseElementNamespace()
        self._relationships_ns = UseCaseRelationshipNamespace()

    @property
    def elements(self) -> UseCaseElementNamespace:
        return self._elements_ns

    @property
    def relationships(self) -> UseCaseRelationshipNamespace:
        return self._relationships_ns

    def build(self) -> UseCaseDiagram:
        all_elements: list[UseCaseDiagramElement] = []

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
                ))

        # Build notes
        for note_data in self._notes:
            target = note_data["target"]
            all_elements.append(UseCaseNote(
                content=note_data["content"],
                position=note_data["position"],
                target=_resolve_ref(target) if target else None,
                color=note_data.get("color"),
            ))

        return UseCaseDiagram(
            elements=tuple(all_elements),
            title=self._title,
            mainframe=self._mainframe,
            caption=self._caption,
            header=self._header,
            footer=self._footer,
            legend=self._legend,
            scale=self._scale,
            theme=self._theme,
            actor_style=self._actor_style,
            layout=self._layout,
        )


def usecase_diagram(
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
    actor_style: ActorStyle | None = None,
) -> UseCaseComposer:
    """Create a use case diagram composer.

    Example:
        d = usecase_diagram(title="Shopping")
        el = d.elements
        r = d.relationships
        user = el.actor("Customer")
        browse = el.usecase("Browse")
        d.add(user, browse)
        d.connect(r.arrow(user, browse))
        print(render(d))
    """
    return UseCaseComposer(
        title=title, mainframe=mainframe, caption=caption,
        header=header, footer=footer, legend=legend, scale=scale,
        theme=theme, layout=layout, actor_style=actor_style,
    )
