"""Class diagram composer.

Entities with members (fields/methods), plus typed relationships.
members= tuple replaces context manager with eb.method()/eb.field().

Example:
    d = class_diagram(title="Model", theme="plain")
    el = d.elements
    r = d.relationships

    base = el.abstract("BaseElement", members=(
        el.field("tag", "str"),
        el.separator(),
        el.method("render()", "str"),
    ))
    div = el.class_("div")

    d.add(base, div)
    d.connect(r.extends(div, base))

    puml = render(d)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ..primitives.common import (
    ClassDiagramStyleLike,
    ColorLike,
    Direction,
    Footer,
    Header,
    Label,
    LabelLike,
    LayoutDirection,
    LayoutEngine,
    Legend,
    LineStyleLike,
    LineType,
    Note,
    Scale,
    Stereotype,
    StyleLike,
    ThemeLike,
    coerce_class_diagram_style,
    coerce_line_style,
    sanitize_ref,
)
from ..primitives.class_ import (
    ClassDiagram,
    ClassDiagramElement,
    ClassNode,
    ClassNote,
    ClassType,
    Member,
    MemberModifier,
    Package,
    PackageStyle,
    Relationship,
    RelationType,
    Separator,
    SeparatorStyle,
    Visibility,
)
from .base import BaseComposer, EntityRef


def _coerce_stereotype(value: str | Stereotype | None) -> Stereotype | None:
    if value is None:
        return None
    if isinstance(value, Stereotype):
        return value
    return Stereotype(name=value)


# Member data types — returned by el.field(), el.method(), el.separator()
@dataclass(frozen=True)
class _FieldData:
    name: str
    type: str | None = None
    visibility: Visibility | None = None
    modifier: MemberModifier | None = None


@dataclass(frozen=True)
class _MethodData:
    name: str
    return_type: str | None = None
    visibility: Visibility | None = None
    modifier: MemberModifier | None = None


@dataclass(frozen=True)
class _SeparatorData:
    style: SeparatorStyle = "solid"
    label: str | None = None


_MemberData = _FieldData | _MethodData | _SeparatorData


@dataclass(frozen=True)
class _RelationshipData:
    source: EntityRef | str
    target: EntityRef | str
    type: RelationType
    label: str | None = None
    source_label: str | None = None
    target_label: str | None = None
    style: LineStyleLike | None = None
    direction: Direction | None = None


class ClassElementNamespace:
    """Factory namespace for class diagram elements."""

    # --- Element factories ---

    def class_(
        self,
        name: str,
        *,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
        generics: str | None = None,
        members: tuple[_MemberData, ...] = (),
    ) -> EntityRef:
        return self._make_class(
            name, "class", ref=ref, stereotype=stereotype,
            style=style, generics=generics, members=members,
        )

    def abstract(
        self,
        name: str,
        *,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
        generics: str | None = None,
        members: tuple[_MemberData, ...] = (),
    ) -> EntityRef:
        return self._make_class(
            name, "abstract", ref=ref, stereotype=stereotype,
            style=style, generics=generics, members=members,
        )

    def interface(
        self,
        name: str,
        *,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
        generics: str | None = None,
        members: tuple[_MemberData, ...] = (),
    ) -> EntityRef:
        return self._make_class(
            name, "interface", ref=ref, stereotype=stereotype,
            style=style, generics=generics, members=members,
        )

    def protocol(
        self,
        name: str,
        *,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
        generics: str | None = None,
        members: tuple[_MemberData, ...] = (),
    ) -> EntityRef:
        return self._make_class(
            name, "protocol", ref=ref, stereotype=stereotype,
            style=style, generics=generics, members=members,
        )

    def annotation(
        self,
        name: str,
        *,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
        generics: str | None = None,
        members: tuple[_MemberData, ...] = (),
    ) -> EntityRef:
        return self._make_class(
            name, "annotation", ref=ref, stereotype=stereotype,
            style=style, generics=generics, members=members,
        )

    def entity(
        self,
        name: str,
        *,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
        generics: str | None = None,
        members: tuple[_MemberData, ...] = (),
    ) -> EntityRef:
        return self._make_class(
            name, "entity", ref=ref, stereotype=stereotype,
            style=style, generics=generics, members=members,
        )

    def exception(
        self,
        name: str,
        *,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
        generics: str | None = None,
        members: tuple[_MemberData, ...] = (),
    ) -> EntityRef:
        return self._make_class(
            name, "exception", ref=ref, stereotype=stereotype,
            style=style, generics=generics, members=members,
        )

    def metaclass(
        self,
        name: str,
        *,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
        generics: str | None = None,
        members: tuple[_MemberData, ...] = (),
    ) -> EntityRef:
        return self._make_class(
            name, "metaclass", ref=ref, stereotype=stereotype,
            style=style, generics=generics, members=members,
        )

    def struct(
        self,
        name: str,
        *,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
        generics: str | None = None,
        members: tuple[_MemberData, ...] = (),
    ) -> EntityRef:
        return self._make_class(
            name, "struct", ref=ref, stereotype=stereotype,
            style=style, generics=generics, members=members,
        )

    def circle(
        self,
        name: str,
        *,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
        generics: str | None = None,
        members: tuple[_MemberData, ...] = (),
    ) -> EntityRef:
        return self._make_class(
            name, "circle", ref=ref, stereotype=stereotype,
            style=style, generics=generics, members=members,
        )

    def diamond(
        self,
        name: str,
        *,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
        generics: str | None = None,
        members: tuple[_MemberData, ...] = (),
    ) -> EntityRef:
        return self._make_class(
            name, "diamond", ref=ref, stereotype=stereotype,
            style=style, generics=generics, members=members,
        )

    def enum(
        self,
        name: str,
        *values: str,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> EntityRef:
        return EntityRef(
            name, ref=ref,
            data={
                "_type": "enum", "stereotype": stereotype, "style": style,
                "generics": None, "members": (), "enum_values": values,
            },
        )

    def package(
        self,
        name: str,
        *children: EntityRef,
        ref: str | None = None,
        style: PackageStyle = "package",
        color: ColorLike | None = None,
    ) -> EntityRef:
        return EntityRef(
            name, ref=ref,
            data={
                "_type": "package", "package_style": style, "color": color,
            },
            children=children,
        )

    # --- Member factories ---

    def field(
        self,
        name: str,
        type: str | None = None,
        *,
        visibility: Visibility | None = None,
        modifier: MemberModifier | None = None,
    ) -> _FieldData:
        return _FieldData(
            name=name, type=type,
            visibility=visibility, modifier=modifier,
        )

    def method(
        self,
        name: str,
        return_type: str | None = None,
        *,
        visibility: Visibility | None = None,
        modifier: MemberModifier | None = None,
    ) -> _MethodData:
        return _MethodData(
            name=name, return_type=return_type,
            visibility=visibility, modifier=modifier,
        )

    def separator(
        self,
        style: SeparatorStyle = "solid",
        label: str | None = None,
    ) -> _SeparatorData:
        return _SeparatorData(style=style, label=label)

    # --- Internal ---

    def _make_class(
        self,
        name: str,
        class_type: ClassType,
        *,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
        generics: str | None = None,
        members: tuple[_MemberData, ...] = (),
    ) -> EntityRef:
        return EntityRef(
            name, ref=ref,
            data={
                "_type": class_type, "stereotype": stereotype, "style": style,
                "generics": generics, "members": members, "enum_values": None,
            },
        )


class ClassRelationshipNamespace:
    """Factory namespace for class diagram relationships."""

    def extends(self, child: EntityRef | str, parent: EntityRef | str, *,
                label: str | None = None, style: LineStyleLike | None = None,
                direction: Direction | None = None) -> _RelationshipData:
        # source=parent, target=child: renders as "parent <|-- child"
        return _RelationshipData(source=parent, target=child, type="extension",
                                 label=label, style=style, direction=direction)

    def implements(self, child: EntityRef | str, parent: EntityRef | str, *,
                   label: str | None = None, style: LineStyleLike | None = None,
                   direction: Direction | None = None) -> _RelationshipData:
        # source=interface, target=implementer: renders as "interface <|.. implementer"
        return _RelationshipData(source=parent, target=child, type="implementation",
                                 label=label, style=style, direction=direction)

    def has(self, whole: EntityRef | str, part: EntityRef | str, *,
            label: str | None = None, part_label: str | None = None,
            style: LineStyleLike | None = None,
            direction: Direction | None = None) -> _RelationshipData:
        return _RelationshipData(source=whole, target=part, type="composition",
                                 label=label, target_label=part_label,
                                 style=style, direction=direction)

    def uses(self, source: EntityRef | str, target: EntityRef | str, *,
             label: str | None = None, style: LineStyleLike | None = None,
             direction: Direction | None = None) -> _RelationshipData:
        return _RelationshipData(source=source, target=target, type="dependency",
                                 label=label, style=style, direction=direction)

    def association(self, source: EntityRef | str, target: EntityRef | str, *,
                    label: str | None = None,
                    source_label: str | None = None,
                    target_label: str | None = None,
                    style: LineStyleLike | None = None,
                    direction: Direction | None = None) -> _RelationshipData:
        return _RelationshipData(source=source, target=target, type="association",
                                 label=label, source_label=source_label,
                                 target_label=target_label,
                                 style=style, direction=direction)

    def aggregation(self, whole: EntityRef | str, part: EntityRef | str, *,
                    label: str | None = None, part_label: str | None = None,
                    style: LineStyleLike | None = None,
                    direction: Direction | None = None) -> _RelationshipData:
        return _RelationshipData(source=whole, target=part, type="aggregation",
                                 label=label, target_label=part_label,
                                 style=style, direction=direction)

    def composition(self, whole: EntityRef | str, part: EntityRef | str, *,
                    label: str | None = None, part_label: str | None = None,
                    style: LineStyleLike | None = None,
                    direction: Direction | None = None) -> _RelationshipData:
        return _RelationshipData(source=whole, target=part, type="composition",
                                 label=label, target_label=part_label,
                                 style=style, direction=direction)

    def arrow(self, source: EntityRef | str, target: EntityRef | str, *,
              label: str | None = None, style: LineStyleLike | None = None,
              direction: Direction | None = None) -> _RelationshipData:
        return _RelationshipData(source=source, target=target, type="association",
                                 label=label, style=style, direction=direction)

    def lollipop(self, provider: EntityRef | str, consumer: EntityRef | str, *,
                 label: str | None = None, style: LineStyleLike | None = None,
                 direction: Direction | None = None) -> _RelationshipData:
        return _RelationshipData(source=provider, target=consumer, type="lollipop",
                                 label=label, style=style, direction=direction)

    def zero_or_one(self, source: EntityRef | str, target: EntityRef | str, *,
                    label: str | None = None,
                    source_label: str | None = None,
                    target_label: str | None = None,
                    style: LineStyleLike | None = None,
                    direction: Direction | None = None) -> _RelationshipData:
        return _RelationshipData(source=source, target=target, type="zero_or_one",
                                 label=label, source_label=source_label,
                                 target_label=target_label,
                                 style=style, direction=direction)

    def exactly_one(self, source: EntityRef | str, target: EntityRef | str, *,
                    label: str | None = None,
                    source_label: str | None = None,
                    target_label: str | None = None,
                    style: LineStyleLike | None = None,
                    direction: Direction | None = None) -> _RelationshipData:
        return _RelationshipData(source=source, target=target, type="exactly_one",
                                 label=label, source_label=source_label,
                                 target_label=target_label,
                                 style=style, direction=direction)

    def zero_or_many(self, source: EntityRef | str, target: EntityRef | str, *,
                     label: str | None = None,
                     source_label: str | None = None,
                     target_label: str | None = None,
                     style: LineStyleLike | None = None,
                     direction: Direction | None = None) -> _RelationshipData:
        return _RelationshipData(source=source, target=target, type="zero_or_many",
                                 label=label, source_label=source_label,
                                 target_label=target_label,
                                 style=style, direction=direction)

    def one_or_many(self, source: EntityRef | str, target: EntityRef | str, *,
                    label: str | None = None,
                    source_label: str | None = None,
                    target_label: str | None = None,
                    style: LineStyleLike | None = None,
                    direction: Direction | None = None) -> _RelationshipData:
        return _RelationshipData(source=source, target=target, type="one_or_many",
                                 label=label, source_label=source_label,
                                 target_label=target_label,
                                 style=style, direction=direction)


def _resolve_ref(item: EntityRef | str) -> str:
    if isinstance(item, EntityRef):
        return item._ref
    return item


def _build_members(
    members: tuple[_MemberData, ...],
) -> tuple[Member | Separator, ...]:
    result: list[Member | Separator] = []
    for m in members:
        if isinstance(m, _SeparatorData):
            result.append(Separator(style=m.style, label=m.label))
        elif isinstance(m, _FieldData):
            result.append(Member(
                name=m.name, visibility=m.visibility,
                type=m.type, modifier=m.modifier, is_method=False,
            ))
        elif isinstance(m, _MethodData):
            result.append(Member(
                name=m.name, visibility=m.visibility,
                type=m.return_type, modifier=m.modifier, is_method=True,
            ))
    return tuple(result)


def _build_element(ref: EntityRef) -> ClassDiagramElement:
    data = ref._data
    element_type = data.get("_type", "class")

    if element_type == "package":
        children = tuple(_build_element(c) for c in ref._children.values())
        alias = ref._ref if ref._ref != sanitize_ref(ref._name) else None
        return Package(
            name=ref._name,
            alias=alias,
            style=data.get("package_style", "package"),
            color=data.get("color"),
            elements=children,
        )

    # Class types
    alias = ref._ref if ref._ref != sanitize_ref(ref._name) else None
    members_data = data.get("members", ())
    enum_values = data.get("enum_values")

    return ClassNode(
        name=ref._name,
        alias=alias,
        type=element_type,
        generics=data.get("generics"),
        stereotype=_coerce_stereotype(data.get("stereotype")),
        members=_build_members(members_data) if members_data else (),
        style=data.get("style"),
        enum_values=tuple(enum_values) if enum_values else None,
    )


class ClassComposer(BaseComposer):
    """Composer for class diagrams."""

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
        diagram_style: ClassDiagramStyleLike | None = None,
        hide_empty_members: bool = False,
        hide_circle: bool = False,
    ) -> None:
        super().__init__(
            title=title, mainframe=mainframe, caption=caption,
            header=header, footer=footer, legend=legend, scale=scale,
        )
        self._theme = theme
        self._layout = layout
        self._diagram_style = (
            coerce_class_diagram_style(diagram_style)
            if diagram_style
            else None
        )
        self._hide_empty_members = hide_empty_members
        self._hide_circle = hide_circle
        self._elements_ns = ClassElementNamespace()
        self._relationships_ns = ClassRelationshipNamespace()

    @property
    def elements(self) -> ClassElementNamespace:
        return self._elements_ns

    @property
    def relationships(self) -> ClassRelationshipNamespace:
        return self._relationships_ns

    def build(self) -> ClassDiagram:
        all_elements: list[ClassDiagramElement] = []

        for item in self._elements:
            if isinstance(item, EntityRef):
                all_elements.append(_build_element(item))

        for conn in self._connections:
            if isinstance(conn, _RelationshipData):
                label = Label(conn.label) if conn.label else None
                all_elements.append(Relationship(
                    source=_resolve_ref(conn.source),
                    target=_resolve_ref(conn.target),
                    type=conn.type,
                    label=label,
                    source_label=conn.source_label,
                    target_label=conn.target_label,
                    style=conn.style,
                    direction=conn.direction,
                ))

        for note_data in self._notes:
            target = note_data["target"]
            all_elements.append(ClassNote(
                content=note_data["content"],
                position=note_data["position"],
                target=_resolve_ref(target) if target else None,
            ))

        return ClassDiagram(
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
            diagram_style=self._diagram_style,
            hide_empty_members=self._hide_empty_members,
            hide_circle=self._hide_circle,
        )


def class_diagram(
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
    diagram_style: ClassDiagramStyleLike | None = None,
    hide_empty_members: bool = False,
    hide_circle: bool = False,
) -> ClassComposer:
    """Create a class diagram composer.

    Example:
        d = class_diagram(title="Model")
        el = d.elements
        r = d.relationships
        base = el.abstract("Base", members=(el.method("run()"),))
        child = el.class_("Child")
        d.add(base, child)
        d.connect(r.extends(child, base))
        print(render(d))
    """
    return ClassComposer(
        title=title, mainframe=mainframe, caption=caption,
        header=header, footer=footer, legend=legend, scale=scale,
        theme=theme, layout=layout,
        diagram_style=diagram_style,
        hide_empty_members=hide_empty_members,
        hide_circle=hide_circle,
    )
