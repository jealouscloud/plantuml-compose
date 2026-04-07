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
    ArrowHeadLike,
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
    coerce_arrow_head,
    coerce_line_style,
    coerce_style,
    sanitize_ref,
)
from ..primitives.styles import (
    ComponentDiagramStyleLike,
    coerce_component_diagram_style,
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
    Port,
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
    length: int | None = None
    left_head: ArrowHeadLike | None = None
    right_head: ArrowHeadLike | None = None


class ServiceResult:
    """Result from el.service() — a component with auto-connected interfaces.

    Use directly with d.add() and d.connect():

        svc = el.service("API", provides=("REST",), requires=("Auth",))
        d.add(*svc.elements)
        d.connect(*svc.connections)

    Attributes:
        component:   The service component EntityRef
        elements:    All elements to register (component + interfaces)
        connections: All provides/requires relationships
    """

    __slots__ = ("component", "elements", "connections")

    def __init__(
        self,
        component: EntityRef,
        elements: tuple,
        connections: tuple,
    ) -> None:
        self.component = component
        self.elements = elements
        self.connections = connections


class ComponentElementNamespace:
    """Factory namespace for component diagram elements."""

    def component(
        self,
        name: str,
        *children: EntityRef,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
        description: str | None = None,
    ) -> EntityRef:
        return EntityRef(
            name, ref=ref,
            data={
                "_type": "component",
                "stereotype": stereotype,
                "style": style,
                "children": children,
                "description": description,
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
        description: str | None = None,
    ) -> EntityRef:
        return self._container(
            name, "package", *children,
            ref=ref, stereotype=stereotype, style=style,
            description=description,
        )

    def database(
        self,
        name: str,
        *children: EntityRef,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
        description: str | None = None,
    ) -> EntityRef:
        return self._container(
            name, "database", *children,
            ref=ref, stereotype=stereotype, style=style,
            description=description,
        )

    def cloud(
        self,
        name: str,
        *children: EntityRef,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
        description: str | None = None,
    ) -> EntityRef:
        return self._container(
            name, "cloud", *children,
            ref=ref, stereotype=stereotype, style=style,
            description=description,
        )

    def node(
        self,
        name: str,
        *children: EntityRef,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
        description: str | None = None,
    ) -> EntityRef:
        return self._container(
            name, "node", *children,
            ref=ref, stereotype=stereotype, style=style,
            description=description,
        )

    def folder(
        self,
        name: str,
        *children: EntityRef,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
        description: str | None = None,
    ) -> EntityRef:
        return self._container(
            name, "folder", *children,
            ref=ref, stereotype=stereotype, style=style,
            description=description,
        )

    def frame(
        self,
        name: str,
        *children: EntityRef,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
        description: str | None = None,
    ) -> EntityRef:
        return self._container(
            name, "frame", *children,
            ref=ref, stereotype=stereotype, style=style,
            description=description,
        )

    def rectangle(
        self,
        name: str,
        *children: EntityRef,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
        description: str | None = None,
    ) -> EntityRef:
        return self._container(
            name, "rectangle", *children,
            ref=ref, stereotype=stereotype, style=style,
            description=description,
        )

    # --- Universal nestable types (can contain children) ---

    def artifact(
        self, name: str, *children: EntityRef, ref: str | None = None,
        stereotype: str | Stereotype | None = None, style: StyleLike | None = None,
        description: str | None = None,
    ) -> EntityRef:
        return self._container(name, "artifact", *children, ref=ref,
                               stereotype=stereotype, style=style, description=description)

    def card(
        self, name: str, *children: EntityRef, ref: str | None = None,
        stereotype: str | Stereotype | None = None, style: StyleLike | None = None,
        description: str | None = None,
    ) -> EntityRef:
        return self._container(name, "card", *children, ref=ref,
                               stereotype=stereotype, style=style, description=description)

    def file(
        self, name: str, *children: EntityRef, ref: str | None = None,
        stereotype: str | Stereotype | None = None, style: StyleLike | None = None,
        description: str | None = None,
    ) -> EntityRef:
        return self._container(name, "file", *children, ref=ref,
                               stereotype=stereotype, style=style, description=description)

    def hexagon(
        self, name: str, *children: EntityRef, ref: str | None = None,
        stereotype: str | Stereotype | None = None, style: StyleLike | None = None,
        description: str | None = None,
    ) -> EntityRef:
        return self._container(name, "hexagon", *children, ref=ref,
                               stereotype=stereotype, style=style, description=description)

    def process(
        self, name: str, *children: EntityRef, ref: str | None = None,
        stereotype: str | Stereotype | None = None, style: StyleLike | None = None,
        description: str | None = None,
    ) -> EntityRef:
        return self._container(name, "process", *children, ref=ref,
                               stereotype=stereotype, style=style, description=description)

    def queue(
        self, name: str, *children: EntityRef, ref: str | None = None,
        stereotype: str | Stereotype | None = None, style: StyleLike | None = None,
        description: str | None = None,
    ) -> EntityRef:
        return self._container(name, "queue", *children, ref=ref,
                               stereotype=stereotype, style=style, description=description)

    def stack(
        self, name: str, *children: EntityRef, ref: str | None = None,
        stereotype: str | Stereotype | None = None, style: StyleLike | None = None,
        description: str | None = None,
    ) -> EntityRef:
        return self._container(name, "stack", *children, ref=ref,
                               stereotype=stereotype, style=style, description=description)

    def storage(
        self, name: str, *children: EntityRef, ref: str | None = None,
        stereotype: str | Stereotype | None = None, style: StyleLike | None = None,
        description: str | None = None,
    ) -> EntityRef:
        return self._container(name, "storage", *children, ref=ref,
                               stereotype=stereotype, style=style, description=description)

    # --- Universal leaf types (cannot contain children) ---

    def _leaf(
        self, name: str, element_type: str, *,
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
        )

    def actor(self, name: str, *, ref: str | None = None,
              stereotype: str | Stereotype | None = None,
              style: StyleLike | None = None) -> EntityRef:
        return self._leaf(name, "actor", ref=ref, stereotype=stereotype, style=style)

    def agent(self, name: str, *, ref: str | None = None,
              stereotype: str | Stereotype | None = None,
              style: StyleLike | None = None) -> EntityRef:
        return self._leaf(name, "agent", ref=ref, stereotype=stereotype, style=style)

    def boundary(self, name: str, *, ref: str | None = None,
                 stereotype: str | Stereotype | None = None,
                 style: StyleLike | None = None) -> EntityRef:
        return self._leaf(name, "boundary", ref=ref, stereotype=stereotype, style=style)

    def circle(self, name: str, *, ref: str | None = None,
               stereotype: str | Stereotype | None = None,
               style: StyleLike | None = None) -> EntityRef:
        return self._leaf(name, "circle", ref=ref, stereotype=stereotype, style=style)

    def collections(self, name: str, *, ref: str | None = None,
                    stereotype: str | Stereotype | None = None,
                    style: StyleLike | None = None) -> EntityRef:
        return self._leaf(name, "collections", ref=ref, stereotype=stereotype, style=style)

    def control(self, name: str, *, ref: str | None = None,
                stereotype: str | Stereotype | None = None,
                style: StyleLike | None = None) -> EntityRef:
        return self._leaf(name, "control", ref=ref, stereotype=stereotype, style=style)

    def entity(self, name: str, *, ref: str | None = None,
               stereotype: str | Stereotype | None = None,
               style: StyleLike | None = None) -> EntityRef:
        return self._leaf(name, "entity", ref=ref, stereotype=stereotype, style=style)

    def label_(self, name: str, *, ref: str | None = None,
               stereotype: str | Stereotype | None = None,
               style: StyleLike | None = None) -> EntityRef:
        return self._leaf(name, "label", ref=ref, stereotype=stereotype, style=style)

    def person(self, name: str, *, ref: str | None = None,
               stereotype: str | Stereotype | None = None,
               style: StyleLike | None = None) -> EntityRef:
        return self._leaf(name, "person", ref=ref, stereotype=stereotype, style=style)

    def usecase(self, name: str, *, ref: str | None = None,
                stereotype: str | Stereotype | None = None,
                style: StyleLike | None = None) -> EntityRef:
        return self._leaf(name, "usecase", ref=ref, stereotype=stereotype, style=style)

    # --- Ports ---

    def port(self, name: str) -> EntityRef:
        """Create a bidirectional port.

        Ports appear as small squares on component boundaries. Add as children
        of a component.

        Args:
            name: Port name

        Returns:
            EntityRef for the port
        """
        return EntityRef(
            name,
            data={"_type": "port", "_direction": "port"},
        )

    def portin(self, name: str) -> EntityRef:
        """Create an input port (with inward arrow).

        Args:
            name: Port name

        Returns:
            EntityRef for the port
        """
        return EntityRef(
            name,
            data={"_type": "port", "_direction": "portin"},
        )

    def portout(self, name: str) -> EntityRef:
        """Create an output port (with outward arrow).

        Args:
            name: Port name

        Returns:
            EntityRef for the port
        """
        return EntityRef(
            name,
            data={"_type": "port", "_direction": "portout"},
        )

    def components(
        self,
        *names: str,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> tuple[EntityRef, ...]:
        """Create multiple components at once.

        Args:
            *names: Component names
            stereotype: Optional stereotype applied to all
            style: Optional style applied to all

        Returns:
            Tuple of EntityRefs in order

        Example:
            api, db, cache = el.components("API", "Database", "Cache")
        """
        return tuple(
            self.component(name, stereotype=stereotype, style=style)
            for name in names
        )

    def interfaces(
        self,
        *names: str,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> tuple[EntityRef, ...]:
        """Create multiple interfaces at once.

        Args:
            *names: Interface names
            stereotype: Optional stereotype applied to all
            style: Optional style applied to all

        Returns:
            Tuple of EntityRefs in order

        Example:
            rest, graphql, grpc = el.interfaces("REST", "GraphQL", "gRPC")
        """
        return tuple(
            self.interface(name, stereotype=stereotype, style=style)
            for name in names
        )

    def service(
        self,
        name: str,
        *,
        ref: str | None = None,
        provides: tuple[str, ...] | list[str] | None = None,
        requires: tuple[str, ...] | list[str] | None = None,
        stereotype: str | Stereotype | None = None,
        color: ColorLike | None = None,
    ) -> "ServiceResult":
        """Create a service component with auto-connected interfaces.

        Returns a ServiceResult with three fields you pass directly
        to d.add() and d.connect():

            svc = el.service("API", provides=("REST",), requires=("Auth",))
            d.add(*svc.elements)
            d.connect(*svc.connections)

        Args:
            name: Service component name
            ref: Optional short reference name
            provides: Interface names this service provides (lollipop)
            requires: Interface names this service requires (socket)
            stereotype: Stereotype label
            color: Background color for the component
        """
        style_val: StyleLike | None = {"background": color} if color else None
        comp = self.component(
            name, ref=ref, stereotype=stereotype, style=style_val,
        )

        provided_ifaces: list[EntityRef] = []
        required_ifaces: list[EntityRef] = []
        relationships: list[_RelationshipData] = []

        if provides:
            for iface_name in provides:
                iface = self.interface(iface_name)
                provided_ifaces.append(iface)
                relationships.append(_RelationshipData(
                    source=comp, target=iface, type="provides",
                    label=None, source_label=None, target_label=None,
                    style=None, direction=None,
                    length=None, left_head=None, right_head=None,
                ))

        if requires:
            for iface_name in requires:
                iface = self.interface(iface_name)
                required_ifaces.append(iface)
                relationships.append(_RelationshipData(
                    source=comp, target=iface, type="requires",
                    label=None, source_label=None, target_label=None,
                    style=None, direction=None,
                    length=None, left_head=None, right_head=None,
                ))

        return ServiceResult(
            component=comp,
            elements=(comp, *provided_ifaces, *required_ifaces),
            connections=tuple(relationships),
        )

    def _container(
        self,
        name: str,
        container_type: ContainerType,
        *children: EntityRef,
        ref: str | None = None,
        stereotype: str | Stereotype | None = None,
        style: StyleLike | None = None,
        description: str | None = None,
    ) -> EntityRef:
        return EntityRef(
            name, ref=ref,
            data={
                "_type": "container",
                "_container_type": container_type,
                "stereotype": stereotype,
                "style": style,
                "description": description,
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
        source_label: str | None = None,
        target_label: str | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        length: int | None = None,
        left_head: ArrowHeadLike | None = None,
        right_head: ArrowHeadLike | None = None,
    ) -> _RelationshipData:
        return _RelationshipData(
            source=source, target=target, type="arrow",
            label=label, source_label=source_label, target_label=target_label,
            style=style, direction=direction, length=length,
            left_head=left_head, right_head=right_head,
        )

    def dependency(
        self,
        source: EntityRef | str,
        target: EntityRef | str,
        label: str | None = None,
        *,
        source_label: str | None = None,
        target_label: str | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        length: int | None = None,
    ) -> _RelationshipData:
        return _RelationshipData(
            source=source, target=target, type="dependency",
            label=label, source_label=source_label, target_label=target_label,
            style=style, direction=direction, length=length,
        )

    def link(
        self,
        source: EntityRef | str,
        target: EntityRef | str,
        label: str | None = None,
        *,
        source_label: str | None = None,
        target_label: str | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        length: int | None = None,
    ) -> _RelationshipData:
        return _RelationshipData(
            source=source, target=target, type="association",
            label=label, source_label=source_label, target_label=target_label,
            style=style, direction=direction, length=length,
        )

    def provides(
        self,
        source: EntityRef | str,
        target: EntityRef | str,
        label: str | None = None,
        *,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        length: int | None = None,
    ) -> _RelationshipData:
        return _RelationshipData(
            source=source, target=target, type="provides",
            label=label, source_label=None, target_label=None,
            style=style, direction=direction, length=length,
        )

    def requires(
        self,
        source: EntityRef | str,
        target: EntityRef | str,
        label: str | None = None,
        *,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        length: int | None = None,
    ) -> _RelationshipData:
        return _RelationshipData(
            source=source, target=target, type="requires",
            label=label, source_label=None, target_label=None,
            style=style, direction=direction, length=length,
        )

    def arrows(
        self,
        *tuples: tuple[EntityRef | str, EntityRef | str, str | None],
    ) -> list[_RelationshipData]:
        return [
            self.arrow(s, t, lbl) for s, t, *rest in tuples
            for lbl in [rest[0] if rest else None]
        ]

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

        Instead of:
            c.arrow(api, db, "queries"),
            c.arrow(api, cache, "reads"),
            c.arrow(api, queue, "publishes"),

        Write:
            c.arrows_from(api,
                (db, "queries"),
                (cache, "reads"),
                (queue, "publishes"),
            )
        """
        results: list[_RelationshipData] = []
        for t in targets:
            if isinstance(t, tuple):
                target, label = t
            else:
                target, label = t, None
            results.append(self.arrow(source, target, label,
                                      style=style, direction=direction,
                                      length=length))
        return results

    def lines_from(
        self,
        source: EntityRef | str,
        *targets: EntityRef | str,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        length: int | None = None,
    ) -> list[_RelationshipData]:
        """Fan-out lines (no arrowhead): one source, many targets.

        Same as arrows_from() but creates undirected links.

        Returns a list that d.connect() flattens automatically.
        """
        return [self.link(source, t, style=style, direction=direction,
                          length=length)
                for t in targets]

    def lines(
        self,
        *tuples: tuple[EntityRef | str, EntityRef | str],
    ) -> list[_RelationshipData]:
        return [self.link(s, t) for s, t in tuples]

    def chain(
        self,
        *items: EntityRef | str,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        length: int | None = None,
    ) -> list[_RelationshipData]:
        """Create a chain of arrows with interleaved labels.

        Components are EntityRefs, labels are plain strings without a _ref.
        Strings that match an EntityRef are treated as labels in this context;
        use EntityRef objects for components.

        Args:
            *items: Alternating components and labels. Labels between
                    components become arrow labels.
            style: Line style applied to all arrows
            direction: Layout direction hint for all arrows

        Returns:
            List of _RelationshipData for d.connect()

        Examples:
            c.chain(ui, "HTTP", api, "SQL", db)
            # Creates: ui --HTTP--> api --SQL--> db

            c.chain(a, b, c)  # unlabeled: a --> b --> c

            c.chain(a, "call", b, c, "store", d)
            # a --call--> b --> c --store--> d
        """
        if len(items) < 2:
            raise ValueError("chain() requires at least 2 components")

        relationships: list[_RelationshipData] = []
        i = 0
        current: EntityRef | None = None

        while i < len(items):
            item = items[i]

            # An EntityRef is always a component; a plain str is a label
            is_component = isinstance(item, EntityRef)

            if is_component:
                if current is not None:
                    # Unlabeled arrow from previous to this
                    relationships.append(self.arrow(
                        current, item, style=style, direction=direction,
                        length=length,
                    ))
                current = item
                i += 1
            elif isinstance(item, str):
                if current is None:
                    raise ValueError(
                        "chain() must start with a component, not a label"
                    )
                if i + 1 >= len(items):
                    raise ValueError("chain() cannot end with a label")
                next_item = items[i + 1]
                relationships.append(self.arrow(
                    current, next_item, item,
                    style=style, direction=direction,
                    length=length,
                ))
                current = next_item
                i += 2
            else:
                raise ValueError(
                    f"chain() received unexpected item type: {type(item)}"
                )

        if len(relationships) == 0:
            raise ValueError("chain() requires at least 2 components")

        return relationships


def _resolve_ref(item: EntityRef | str) -> str:
    if isinstance(item, EntityRef):
        return item._ref
    return item


def _build_element(ref: EntityRef) -> ComponentElement:
    """Convert an EntityRef to a component primitive."""
    data = ref._data
    element_type = data.get("_type", "component")

    if element_type == "port":
        return Port(
            name=ref._name,
            direction=data.get("_direction", "port"),
        )

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
            description=data.get("description"),
        )

    # Default: component or universal leaf type (actor, agent, etc.)
    children = tuple(_build_element(c) for c in ref._children.values())
    alias = ref._ref if ref._ref != sanitize_ref(ref._name) else None
    return Component(
        name=ref._name,
        alias=alias,
        type=element_type,
        stereotype=_coerce_stereotype(data.get("stereotype")),
        style=_coerce_style(data.get("style")),
        description=data.get("description"),
        elements=children,
    )


class ComponentComposer(BaseComposer):
    """Composer for component diagrams."""

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
        style: ComponentStyle | None = None,
        diagram_style: ComponentDiagramStyleLike | None = None,
        hide_stereotype: bool = False,
        hide_unlinked: bool = False,
    ) -> None:
        super().__init__(
            title=title, mainframe=mainframe, caption=caption,
            header=header, footer=footer, legend=legend, scale=scale,
        )
        self._theme = theme
        self._layout = layout
        self._style = style
        self._diagram_style = (
            coerce_component_diagram_style(diagram_style)
            if diagram_style
            else None
        )
        self._hide_stereotype = hide_stereotype
        self._hide_unlinked = hide_unlinked
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
                    length=conn.length,
                    left_head=coerce_arrow_head(conn.left_head),
                    right_head=coerce_arrow_head(conn.right_head),
                ))

        # Build notes
        for note_data in self._notes:
            target = note_data["target"]
            all_elements.append(ComponentNote(
                content=note_data["content"],
                position=note_data["position"],
                target=_resolve_ref(target) if target else None,
                color=note_data.get("color"),
            ))

        return ComponentDiagram(
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
            style=self._style,
            diagram_style=self._diagram_style,
            hide_stereotype=self._hide_stereotype,
            hide_unlinked=self._hide_unlinked,
        )


def component_diagram(
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
    style: ComponentStyle | None = None,
    diagram_style: ComponentDiagramStyleLike | None = None,
    hide_stereotype: bool = False,
    hide_unlinked: bool = False,
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
        mainframe=mainframe,
        caption=caption,
        header=header,
        footer=footer,
        legend=legend,
        scale=scale,
        theme=theme,
        layout=layout,
        style=style,
        diagram_style=diagram_style,
        hide_stereotype=hide_stereotype,
        hide_unlinked=hide_unlinked,
    )
