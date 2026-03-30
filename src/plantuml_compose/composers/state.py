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
    PseudoState,
    PseudoStateKind,
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
    guard: str | None
    style: LineStyleLike | None
    direction: Direction | None


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
        # Convert string description to Label for storage
        desc = description

        # Convert string note to Note for storage
        note_obj = note

        return EntityRef(
            name, ref=ref,
            data={
                "_type": "composite" if children else "state",
                "description": desc,
                "style": style,
                "note": note_obj,
                "note_position": note_position,
            },
            children=children,
        )


class StateTransitionNamespace:
    """Factory namespace for state diagram transitions."""

    def transition(
        self,
        source: EntityRef | str,
        target: EntityRef | str,
        *,
        label: str | None = None,
        guard: str | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
    ) -> _TransitionData:
        return _TransitionData(
            source=source, target=target,
            label=label, guard=guard,
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

    desc = data.get("description")
    desc_label = Label(desc) if isinstance(desc, str) else desc

    style_obj = _coerce_style(data.get("style"))

    note_raw = data.get("note")
    note_position = data.get("note_position", "right")
    note_obj = (
        Note(Label(note_raw), note_position)
        if isinstance(note_raw, str)
        else note_raw
    )

    alias = ref._ref if ref._ref != sanitize_ref(ref._name) else None

    if element_type == "composite":
        # Build children recursively
        child_elements: list[StateDiagramElement] = []
        for child in ref._children.values():
            child_elements.append(_build_element(child))
        return CompositeState(
            name=ref._name,
            alias=alias,
            elements=tuple(child_elements),
            style=style_obj,
            note=note_obj,
        )

    # Default: simple state
    return StateNode(
        name=ref._name,
        alias=alias,
        description=desc_label,
        style=style_obj,
        note=note_obj,
    )


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
                    guard=conn.guard,
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
