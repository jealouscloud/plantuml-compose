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
    AssociationClass,
    ClassDiagram,
    ClassDiagramElement,
    ClassNode,
    ClassNote,
    ClassType,
    HideShow,
    Member,
    MemberModifier,
    Package,
    PackageStyle,
    Relationship,
    RelationType,
    Separator,
    SeparatorStyle,
    Together,
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
    note: str | None = None
    qualifier: str | None = None
    length: int | None = None


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

    def fields(
        self,
        *tuples: tuple[str] | tuple[str, str],
    ) -> tuple[_FieldData, ...]:
        """Bulk field creation from (name,) or (name, type) tuples.

        Returns a tuple for direct use in members=().

        Instead of:
            el.field("tag", "str"),
            el.field("attrs", "dict[str, Attr]"),
            el.field("children", "list[Node]"),

        Write:
            el.fields(
                ("tag", "str"),
                ("attrs", "dict[str, Attr]"),
                ("children", "list[Node]"),
            )
        """
        results: list[_FieldData] = []
        for tup in tuples:
            if len(tup) == 2:
                results.append(self.field(tup[0], tup[1]))
            else:
                results.append(self.field(tup[0]))
        return tuple(results)

    def methods(
        self,
        *tuples: tuple[str] | tuple[str, str],
    ) -> tuple[_MethodData, ...]:
        """Bulk method creation from (name,) or (name, return_type) tuples.

        Returns a tuple for direct use in members=().

        Instead of:
            el.method("render()", "str"),
            el.method("resolve()", "Generator[str]"),
            el.method("__html__()", "str"),

        Write:
            el.methods(
                ("render()", "str"),
                ("resolve()", "Generator[str]"),
                ("__html__()", "str"),
            )
        """
        results: list[_MethodData] = []
        for tup in tuples:
            if len(tup) == 2:
                results.append(self.method(tup[0], tup[1]))
            else:
                results.append(self.method(tup[0]))
        return tuple(results)

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

    def relationship(self, source: EntityRef | str, target: EntityRef | str, *,
                     type: RelationType = "association",
                     label: str | None = None,
                     source_label: str | None = None,
                     target_label: str | None = None,
                     style: LineStyleLike | None = None,
                     direction: Direction | None = None,
                     note: str | None = None,
                     qualifier: str | None = None,
                     length: int | None = None) -> _RelationshipData:
        """Create a relationship with explicit type.

        For when the convenience methods don't fit your needs.
        """
        return _RelationshipData(source=source, target=target, type=type,
                                 label=label, source_label=source_label,
                                 target_label=target_label,
                                 style=style, direction=direction,
                                 note=note, qualifier=qualifier,
                                 length=length)

    def extends(self, child: EntityRef | str, parent: EntityRef | str, *,
                label: str | None = None, style: LineStyleLike | None = None,
                direction: Direction | None = None,
                note: str | None = None,
                length: int | None = None) -> _RelationshipData:
        # source=parent, target=child: renders as "parent <|-- child"
        return _RelationshipData(source=parent, target=child, type="extension",
                                 label=label, style=style, direction=direction,
                                 note=note, length=length)

    def implements(self, child: EntityRef | str, parent: EntityRef | str, *,
                   label: str | None = None, style: LineStyleLike | None = None,
                   direction: Direction | None = None,
                   note: str | None = None,
                   length: int | None = None) -> _RelationshipData:
        # source=interface, target=implementer: renders as "interface <|.. implementer"
        return _RelationshipData(source=parent, target=child, type="implementation",
                                 label=label, style=style, direction=direction,
                                 note=note, length=length)

    def has(self, whole: EntityRef | str, part: EntityRef | str, *,
            label: str | None = None, part_label: str | None = None,
            style: LineStyleLike | None = None,
            direction: Direction | None = None,
            note: str | None = None,
            length: int | None = None) -> _RelationshipData:
        return _RelationshipData(source=whole, target=part, type="composition",
                                 label=label, target_label=part_label,
                                 style=style, direction=direction,
                                 note=note, length=length)

    def contains(self, whole: EntityRef | str, part: EntityRef | str, *,
                 whole_label: str | None = None,
                 part_label: str | None = None,
                 label: str | None = None,
                 style: LineStyleLike | None = None,
                 direction: Direction | None = None,
                 note: str | None = None,
                 length: int | None = None) -> _RelationshipData:
        """Create a composition relationship (filled diamond).

        Composition means the part cannot exist independently of the whole.
        Uses whole_label/part_label naming (vs has() which uses part_label only).
        """
        return _RelationshipData(source=whole, target=part, type="composition",
                                 label=label, source_label=whole_label,
                                 target_label=part_label,
                                 style=style, direction=direction,
                                 note=note, length=length)

    def uses(self, source: EntityRef | str, target: EntityRef | str, *,
             label: str | None = None, style: LineStyleLike | None = None,
             direction: Direction | None = None,
             note: str | None = None,
             length: int | None = None) -> _RelationshipData:
        return _RelationshipData(source=source, target=target, type="dependency",
                                 label=label, style=style, direction=direction,
                                 note=note, length=length)

    def association(self, source: EntityRef | str, target: EntityRef | str, *,
                    label: str | None = None,
                    source_label: str | None = None,
                    target_label: str | None = None,
                    style: LineStyleLike | None = None,
                    direction: Direction | None = None,
                    note: str | None = None,
                    qualifier: str | None = None,
                    length: int | None = None) -> _RelationshipData:
        return _RelationshipData(source=source, target=target, type="association",
                                 label=label, source_label=source_label,
                                 target_label=target_label,
                                 style=style, direction=direction,
                                 note=note, qualifier=qualifier,
                                 length=length)

    def aggregation(self, whole: EntityRef | str, part: EntityRef | str, *,
                    label: str | None = None, part_label: str | None = None,
                    style: LineStyleLike | None = None,
                    direction: Direction | None = None,
                    note: str | None = None,
                    length: int | None = None) -> _RelationshipData:
        return _RelationshipData(source=whole, target=part, type="aggregation",
                                 label=label, target_label=part_label,
                                 style=style, direction=direction,
                                 note=note, length=length)

    def composition(self, whole: EntityRef | str, part: EntityRef | str, *,
                    label: str | None = None, part_label: str | None = None,
                    style: LineStyleLike | None = None,
                    direction: Direction | None = None,
                    note: str | None = None,
                    length: int | None = None) -> _RelationshipData:
        return _RelationshipData(source=whole, target=part, type="composition",
                                 label=label, target_label=part_label,
                                 style=style, direction=direction,
                                 note=note, length=length)

    def arrow(self, source: EntityRef | str, target: EntityRef | str, *,
              label: str | None = None, style: LineStyleLike | None = None,
              direction: Direction | None = None,
              note: str | None = None,
              length: int | None = None) -> _RelationshipData:
        return _RelationshipData(source=source, target=target, type="association",
                                 label=label, style=style, direction=direction,
                                 note=note, length=length)

    def lollipop(self, provider: EntityRef | str, consumer: EntityRef | str, *,
                 label: str | None = None, style: LineStyleLike | None = None,
                 direction: Direction | None = None,
                 note: str | None = None,
                 length: int | None = None) -> _RelationshipData:
        return _RelationshipData(source=provider, target=consumer, type="lollipop",
                                 label=label, style=style, direction=direction,
                                 note=note, length=length)

    def zero_or_one(self, source: EntityRef | str, target: EntityRef | str, *,
                    label: str | None = None,
                    source_label: str | None = None,
                    target_label: str | None = None,
                    style: LineStyleLike | None = None,
                    direction: Direction | None = None,
                    note: str | None = None,
                    length: int | None = None) -> _RelationshipData:
        return _RelationshipData(source=source, target=target, type="zero_or_one",
                                 label=label, source_label=source_label,
                                 target_label=target_label,
                                 style=style, direction=direction,
                                 note=note, length=length)

    def exactly_one(self, source: EntityRef | str, target: EntityRef | str, *,
                    label: str | None = None,
                    source_label: str | None = None,
                    target_label: str | None = None,
                    style: LineStyleLike | None = None,
                    direction: Direction | None = None,
                    note: str | None = None,
                    length: int | None = None) -> _RelationshipData:
        return _RelationshipData(source=source, target=target, type="exactly_one",
                                 label=label, source_label=source_label,
                                 target_label=target_label,
                                 style=style, direction=direction,
                                 note=note, length=length)

    def zero_or_many(self, source: EntityRef | str, target: EntityRef | str, *,
                     label: str | None = None,
                     source_label: str | None = None,
                     target_label: str | None = None,
                     style: LineStyleLike | None = None,
                     direction: Direction | None = None,
                     note: str | None = None,
                     length: int | None = None) -> _RelationshipData:
        return _RelationshipData(source=source, target=target, type="zero_or_many",
                                 label=label, source_label=source_label,
                                 target_label=target_label,
                                 style=style, direction=direction,
                                 note=note, length=length)

    def one_or_many(self, source: EntityRef | str, target: EntityRef | str, *,
                    label: str | None = None,
                    source_label: str | None = None,
                    target_label: str | None = None,
                    style: LineStyleLike | None = None,
                    direction: Direction | None = None,
                    note: str | None = None,
                    length: int | None = None) -> _RelationshipData:
        return _RelationshipData(source=source, target=target, type="one_or_many",
                                 label=label, source_label=source_label,
                                 target_label=target_label,
                                 style=style, direction=direction,
                                 note=note, length=length)

    def association_class(self, source: EntityRef | str,
                          target: EntityRef | str,
                          association: EntityRef | str) -> dict:
        """Link a class to a relationship, making it an association class.

        Note: You should also create a regular relationship between source and
        target. This method just adds the dotted line from that relationship
        to the association class.
        """
        return {
            "_type": "association_class",
            "source": source,
            "target": target,
            "association": association,
        }


    # --- Bulk methods ---

    def arrows(
        self,
        *tuples: tuple[EntityRef | str, EntityRef | str]
        | tuple[EntityRef | str, EntityRef | str, str],
    ) -> list[_RelationshipData]:
        """Bulk arrows from (source, target) or (source, target, label) tuples.

        Equivalent to calling arrow() once per tuple, but as a
        single declaration block.

        Returns a list that d.connect() flattens automatically.
        """
        results: list[_RelationshipData] = []
        for tup in tuples:
            if len(tup) == 3:
                s, t, lbl = tup
                results.append(self.arrow(s, t, label=lbl))
            else:
                s, t = tup
                results.append(self.arrow(s, t))
        return results

    def arrows_from(
        self,
        source: EntityRef | str,
        *targets: EntityRef | str | tuple[EntityRef | str, str],
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        length: int | None = None,
    ) -> list[_RelationshipData]:
        """Fan-out: one source, many targets.

        Equivalent to calling arrow() once per target, but without
        repeating the source. Targets can be bare (unlabeled) or
        (target, label) tuples. Mix freely.

        Returns a list that d.connect() flattens automatically.
        """
        results: list[_RelationshipData] = []
        for t in targets:
            if isinstance(t, tuple):
                target, label = t
            else:
                target, label = t, None
            results.append(self.arrow(source, target, label=label,
                                      style=style, direction=direction,
                                      length=length))
        return results

    def extends_from(
        self,
        children: list[EntityRef | str],
        parent: EntityRef | str,
        *,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        length: int | None = None,
    ) -> list[_RelationshipData]:
        """Multiple children extend one parent.

        Equivalent to calling extends() once per child, but without
        repeating the parent.

        Returns a list that d.connect() flattens automatically.

        Instead of:
            r.extends(div, base),
            r.extends(span, base),
            r.extends(p, base),

        Write:
            r.extends_from([div, span, p], base)
        """
        return [self.extends(child, parent, style=style, direction=direction,
                             length=length)
                for child in children]

    def compositions_from(
        self,
        whole: EntityRef | str,
        parts: list[EntityRef | str],
        *,
        label: str | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        length: int | None = None,
    ) -> list[_RelationshipData]:
        """One whole composes many parts.

        Equivalent to calling composition() once per part, but without
        repeating the whole.

        Returns a list that d.connect() flattens automatically.

        Instead of:
            r.composition(order, line_item),
            r.composition(order, payment),
            r.composition(order, shipping),

        Write:
            r.compositions_from(order, [line_item, payment, shipping])
        """
        return [self.composition(whole, part, label=label,
                                 style=style, direction=direction,
                                 length=length)
                for part in parts]


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
        namespace_separator: str | None = None,
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
        self._namespace_separator = namespace_separator
        self._elements_ns = ClassElementNamespace()
        self._relationships_ns = ClassRelationshipNamespace()

    @property
    def elements(self) -> ClassElementNamespace:
        return self._elements_ns

    @property
    def relationships(self) -> ClassRelationshipNamespace:
        return self._relationships_ns

    def note(
        self,
        content: str,
        *,
        target: EntityRef | str | None = None,
        position: str = "right",
        color: ColorLike | None = None,
        member: str | None = None,
    ) -> None:
        """Attach a note to the diagram, a target entity, or a specific member.

        The member= parameter targets a specific class member using
        PlantUML's ``note right of A::counter`` syntax.

        Example:
            d.note("Important field", target=user, member="id")
        """
        self._notes.append({
            "content": content,
            "target": target,
            "position": position,
            "color": color,
            "member": member,
        })

    def together(self, *elements: EntityRef) -> None:
        """Group elements for layout proximity.

        Elements in a together block are placed adjacent to each other.
        """
        self._elements.append(("__together__", elements))

    def hide(self, target: str) -> None:
        """Hide elements (e.g., "empty members", "circle").

        Example:
            d.hide("empty members")
            d.hide("circle")
        """
        self._elements.append(("__hideshow__", "hide", target))

    def show(self, target: str) -> None:
        """Show elements.

        Example:
            d.show("methods")
        """
        self._elements.append(("__hideshow__", "show", target))

    def remove(self, target: str) -> None:
        """Remove elements (like hide, but also removes the space they occupied).

        Example:
            d.remove("empty members")
            d.remove("ClassName methods")
        """
        self._elements.append(("__hideshow__", "remove", target))

    def restore(self, target: str) -> None:
        """Restore previously removed/hidden elements.

        Example:
            d.restore("methods")
        """
        self._elements.append(("__hideshow__", "restore", target))

    def build(self) -> ClassDiagram:
        all_elements: list[ClassDiagramElement] = []

        for item in self._elements:
            if isinstance(item, EntityRef):
                all_elements.append(_build_element(item))
            elif isinstance(item, tuple) and len(item) >= 2:
                if item[0] == "__together__":
                    together_refs = item[1]
                    together_elements = tuple(
                        _build_element(ref) for ref in together_refs
                    )
                    all_elements.append(Together(elements=together_elements))
                elif item[0] == "__hideshow__":
                    all_elements.append(HideShow(action=item[1], target=item[2]))

        for conn in self._connections:
            if isinstance(conn, _RelationshipData):
                label = Label(conn.label) if conn.label else None
                note = Label(conn.note) if conn.note else None
                all_elements.append(Relationship(
                    source=_resolve_ref(conn.source),
                    target=_resolve_ref(conn.target),
                    type=conn.type,
                    label=label,
                    source_label=conn.source_label,
                    target_label=conn.target_label,
                    style=conn.style,
                    direction=conn.direction,
                    note=note,
                    qualifier=conn.qualifier,
                    length=conn.length,
                ))
            elif isinstance(conn, dict) and conn.get("_type") == "association_class":
                all_elements.append(AssociationClass(
                    source=_resolve_ref(conn["source"]),
                    target=_resolve_ref(conn["target"]),
                    association_class=_resolve_ref(conn["association"]),
                ))

        for note_data in self._notes:
            target = note_data["target"]
            all_elements.append(ClassNote(
                content=note_data["content"],
                position=note_data["position"],
                target=_resolve_ref(target) if target else None,
                member=note_data.get("member"),
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
            namespace_separator=self._namespace_separator,
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
    namespace_separator: str | None = None,
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
        namespace_separator=namespace_separator,
    )
