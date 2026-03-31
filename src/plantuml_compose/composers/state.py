"""State diagram composer.

Entities + transitions pattern for state diagrams.

Example:
    d = state_diagram(title="Server Lifecycle")
    el = d.elements
    t = d.transitions

    firmware = el.state("Firmware", description="lifecycle-lemur firmware module")
    os_install = el.state("OS", description="Installing Alma Linux 8")
    ready = el.state("Ready", description="Available for assignment")

    d.add(firmware, os_install, ready)
    d.connect(
        t.transition("[*]", firmware, label="Server racked"),
        t.transition(firmware, os_install, label="Firmware complete"),
        t.transition(os_install, ready, label="OS install complete"),
    )

    puml = render(d)
"""

from __future__ import annotations

from dataclasses import dataclass

from ..primitives.common import (
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
    NotePosition,
    Scale,
    StateDiagramStyle,
    StateDiagramStyleLike,
    StyleLike,
    ThemeLike,
    coerce_line_style,
    coerce_state_diagram_style,
    coerce_style,
    sanitize_ref,
)
from ..primitives.state import (
    CompositeState,
    ConcurrentState,
    PseudoState,
    PseudoStateKind,
    Region,
    StateDiagram,
    StateDiagramElement,
    StateNode,
    Transition,
)
from .base import BaseComposer, EntityRef


# Pseudo-state string markers recognized as initial/final
_PSEUDO_STRINGS = frozenset({"[*]", "initial", "final"})


def _coerce_style(value: dict | StyleLike | None):
    if value is None:
        return None
    return coerce_style(value)


@dataclass(frozen=True)
class _TransitionData:
    """Internal transition data."""
    source: EntityRef | str
    target: EntityRef | str
    label: str | None
    trigger: str | None
    guard: str | None
    effect: str | None
    style: LineStyleLike | None
    direction: Direction | None


class _RegionData:
    """Data for a concurrent region — a list of EntityRefs."""
    __slots__ = ("elements",)

    def __init__(self, elements: tuple[EntityRef, ...]) -> None:
        self.elements = elements


class StateElementNamespace:
    """Factory namespace for state diagram elements."""

    def state(
        self,
        name: str,
        *children: EntityRef,
        ref: str | None = None,
        description: str | Label | None = None,
        style: StyleLike | None = None,
        note: str | Note | None = None,
        note_position: NotePosition = "right",
    ) -> EntityRef:
        """Create a state element.

        If children are provided, the state becomes a composite state
        containing nested sub-states.
        """
        return EntityRef(
            name, ref=ref,
            data={
                "_type": "composite" if children else "state",
                "description": description,
                "style": style,
                "note": note,
                "note_position": note_position,
            },
            children=children,
        )

    def choice(self, name: str, *, ref: str | None = None,
               style: StyleLike | None = None) -> EntityRef:
        """Decision point (rendered as diamond)."""
        return EntityRef(name, ref=ref, data={
            "_type": "pseudo", "_kind": PseudoStateKind.CHOICE, "style": style,
        })

    def fork(self, name: str, *, ref: str | None = None,
             style: StyleLike | None = None) -> EntityRef:
        """Fork bar — splits into parallel paths."""
        return EntityRef(name, ref=ref, data={
            "_type": "pseudo", "_kind": PseudoStateKind.FORK, "style": style,
        })

    def join(self, name: str, *, ref: str | None = None,
             style: StyleLike | None = None) -> EntityRef:
        """Join bar — merges parallel paths."""
        return EntityRef(name, ref=ref, data={
            "_type": "pseudo", "_kind": PseudoStateKind.JOIN, "style": style,
        })

    def history(self, *, ref: str | None = None) -> EntityRef:
        """Shallow history pseudo-state [H]."""
        return EntityRef("[H]", ref=ref, data={
            "_type": "pseudo", "_kind": PseudoStateKind.HISTORY, "style": None,
        })

    def deep_history(self, *, ref: str | None = None) -> EntityRef:
        """Deep history pseudo-state [H*]."""
        return EntityRef("[H*]", ref=ref, data={
            "_type": "pseudo", "_kind": PseudoStateKind.DEEP_HISTORY, "style": None,
        })

    def concurrent(
        self,
        name: str,
        *regions: _RegionData,
        ref: str | None = None,
        style: StyleLike | None = None,
    ) -> EntityRef:
        """Concurrent state with parallel regions.

        Each region is created with el.region(*states):
            el.concurrent("Active",
                el.region(el.state("Audio"), el.state("Video")),
                el.region(el.state("Network")),
            )
        """
        return EntityRef(name, ref=ref, data={
            "_type": "concurrent", "style": style, "regions": regions,
        })

    def region(self, *elements: EntityRef) -> _RegionData:
        """Define a region within a concurrent state."""
        return _RegionData(elements=elements)


class StateTransitionNamespace:
    """Factory namespace for state diagram transitions."""

    def transition(
        self,
        source: EntityRef | str,
        target: EntityRef | str,
        *,
        label: str | None = None,
        trigger: str | None = None,
        guard: str | None = None,
        effect: str | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
    ) -> _TransitionData:
        return _TransitionData(
            source=source, target=target,
            label=label, trigger=trigger, guard=guard, effect=effect,
            style=style, direction=direction,
        )


def _resolve_ref(item: EntityRef | str) -> str:
    """Resolve an EntityRef or string to a transition reference.

    Handles "[*]" as initial/final pseudo-state marker.
    """
    if isinstance(item, str):
        # "[*]" is passed through directly for the renderer
        if item in _PSEUDO_STRINGS:
            return item
        return item
    return item._ref


def _build_element(ref: EntityRef) -> StateDiagramElement:
    """Convert an EntityRef to a state diagram primitive."""
    data = ref._data
    element_type = data.get("_type", "state")

    style_obj = _coerce_style(data.get("style"))
    alias = ref._ref if ref._ref != sanitize_ref(ref._name) else None

    if element_type == "pseudo":
        return PseudoState(
            kind=data["_kind"],
            name=ref._name if ref._name not in ("[H]", "[H*]") else None,
            style=style_obj,
        )

    if element_type == "concurrent":
        regions_data = data.get("regions", ())
        built_regions = tuple(
            Region(elements=tuple(_build_element(el) for el in rd.elements))
            for rd in regions_data
        )
        note_obj = _build_note(data)
        return ConcurrentState(
            name=ref._name,
            alias=alias,
            regions=built_regions,
            style=style_obj,
            note=note_obj,
        )

    if element_type == "composite":
        child_elements: list[StateDiagramElement] = []
        for child in ref._children.values():
            child_elements.append(_build_element(child))
        note_obj = _build_note(data)
        return CompositeState(
            name=ref._name,
            alias=alias,
            elements=tuple(child_elements),
            style=style_obj,
            note=note_obj,
        )

    # Default: simple state
    desc = data.get("description")
    desc_label = Label(desc) if isinstance(desc, str) else desc
    note_obj = _build_note(data)
    return StateNode(
        name=ref._name,
        alias=alias,
        description=desc_label,
        style=style_obj,
        note=note_obj,
    )


def _build_note(data: dict) -> Note | None:
    """Extract note from entity data."""
    note_raw = data.get("note")
    note_position = data.get("note_position", "right")
    if isinstance(note_raw, str):
        return Note(Label(note_raw), note_position)
    return note_raw


class StateComposer(BaseComposer):
    """Composer for state diagrams."""

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
        hide_empty_description: bool = False,
    ) -> None:
        super().__init__(
            title=title, mainframe=mainframe, caption=caption,
            header=header, footer=footer, legend=legend, scale=scale,
        )
        self._theme = theme
        self._layout = layout
        self._hide_empty_description = hide_empty_description
        self._elements_ns = StateElementNamespace()
        self._transitions_ns = StateTransitionNamespace()

    @property
    def elements(self) -> StateElementNamespace:
        return self._elements_ns

    @property
    def transitions(self) -> StateTransitionNamespace:
        return self._transitions_ns

    def build(self) -> StateDiagram:
        all_elements: list[StateDiagramElement] = []

        # Build entity elements
        for item in self._elements:
            if isinstance(item, EntityRef):
                all_elements.append(_build_element(item))

        # Build transitions
        for conn in self._connections:
            if isinstance(conn, _TransitionData):
                all_elements.append(Transition(
                    source=_resolve_ref(conn.source),
                    target=_resolve_ref(conn.target),
                    label=Label(conn.label) if conn.label else None,
                    trigger=conn.trigger,
                    guard=conn.guard,
                    effect=conn.effect,
                    style=coerce_line_style(conn.style) if conn.style else None,
                    direction=conn.direction,
                ))

        # Build notes (floating notes via d.note())
        for note_data in self._notes:
            target = note_data["target"]
            content = note_data["content"]
            content_label = Label(content) if isinstance(content, str) else content
            position = note_data.get("position", "right")
            all_elements.append(Note(
                content=content_label,
                position=position,
            ))

        return StateDiagram(
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
            hide_empty_description=self._hide_empty_description,
        )


def state_diagram(
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
    hide_empty_description: bool = False,
) -> StateComposer:
    """Create a state diagram composer.

    Example:
        d = state_diagram(title="Lifecycle")
        el = d.elements
        t = d.transitions
        idle = el.state("Idle")
        active = el.state("Active")
        d.add(idle, active)
        d.connect(t.transition("[*]", idle, label="start"))
        d.connect(t.transition(idle, active, label="go"))
        print(render(d))
    """
    return StateComposer(
        title=title, mainframe=mainframe, caption=caption,
        header=header, footer=footer, legend=legend, scale=scale,
        theme=theme, layout=layout,
        hide_empty_description=hide_empty_description,
    )
