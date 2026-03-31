"""Sequence diagram composer.

Temporal pattern with d.phase() grouping and interaction frames
(d.if_(), d.loop(), d.optional(), d.parallel(), etc.).

Example:
    d = sequence_diagram(title="PXE Boot", actor_style="awesome")
    p = d.participants
    e = d.events

    admin = p.actor("Admin")
    api = p.participant("API")
    d.add(admin, api)

    d.phase("Request", [
        e.message(admin, api, "POST /add"),
        e.reply(api, admin, "OK"),
    ])

    d.if_("valid", [
        e.message(api, admin, "200"),
    ], "invalid", [
        e.message(api, admin, "401"),
    ])

    puml = render(d)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from ..primitives.common import (
    EmbeddableContent,
    Footer,
    Header,
    Label,
    Legend,
    Scale,
    ThemeLike,
)
from ..primitives.sequence import (
    Delay,
    Divider,
    ElseBlock,
    GroupBlock,
    GroupType,
    Message,
    MessageArrowHead,
    MessageLineStyle,
    NoteShape,
    Participant,
    ParticipantType,
    SequenceDiagram,
    SequenceDiagramElement,
    SequenceNote,
)
from ..primitives.usecase import ActorStyle
from .base import BaseComposer, EntityRef


def _resolve_ref(item: EntityRef | str) -> str:
    if isinstance(item, EntityRef):
        return item._ref
    return item


# ---------------------------------------------------------------------------
# Internal data types returned by namespace factories
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _MessageData:
    """Pure data from e.message() / e.reply()."""
    source: EntityRef | str
    target: EntityRef | str
    label: str | None
    line_style: MessageLineStyle
    arrow_head: MessageArrowHead


@dataclass(frozen=True)
class _EventNoteData:
    """Pure data from e.note() — a note inside a phase."""
    content: EmbeddableContent
    over: EntityRef | str | None
    position: Literal["left", "right", "over"]
    shape: NoteShape


@dataclass(frozen=True)
class _BlockData:
    """Pure data for an interaction frame (alt/opt/loop/par/break/critical).

    Frozen — .else_() would return a new copy, but we use alternating
    positional args instead so this is just the final built data.
    """
    type: GroupType
    label: str | None
    events: tuple[Any, ...]  # _PhaseEvent items (recursive — blocks can contain blocks)
    else_branches: tuple[tuple[str | None, tuple[Any, ...]], ...] = ()


# Union of things that go inside event lists
_PhaseEvent = _MessageData | _EventNoteData | _BlockData


def _make_block(
    block_type: GroupType,
    label: str | None,
    events: list[_PhaseEvent],
    *extra_branches: Any,
) -> _BlockData:
    """Build a _BlockData from alternating label/events args.

    Usage:
        _make_block("alt", "cond1", [events1], "cond2", [events2], "cond3", [events3])

    The first label+events is the primary. Remaining pairs are else branches.
    """
    else_branches: list[tuple[str | None, tuple[_PhaseEvent, ...]]] = []

    # Parse alternating label/events pairs from extra_branches
    i = 0
    while i < len(extra_branches):
        branch_label = extra_branches[i]
        if i + 1 < len(extra_branches):
            branch_events = extra_branches[i + 1]
            else_branches.append((branch_label, tuple(branch_events)))
            i += 2
        else:
            # Odd arg — label with no events, skip
            break

    return _BlockData(
        type=block_type,
        label=label,
        events=tuple(events),
        else_branches=tuple(else_branches),
    )


# ---------------------------------------------------------------------------
# Namespaces
# ---------------------------------------------------------------------------


class SequenceParticipantNamespace:
    """Factory namespace for sequence diagram participants."""

    def _make(self, name: str, type_: ParticipantType, *,
              ref: str | None = None) -> EntityRef:
        return EntityRef(name, ref=ref, data={"_type": type_})

    def participant(self, name: str, *, ref: str | None = None) -> EntityRef:
        return self._make(name, "participant", ref=ref)

    def actor(self, name: str, *, ref: str | None = None) -> EntityRef:
        return self._make(name, "actor", ref=ref)

    def boundary(self, name: str, *, ref: str | None = None) -> EntityRef:
        return self._make(name, "boundary", ref=ref)

    def control(self, name: str, *, ref: str | None = None) -> EntityRef:
        return self._make(name, "control", ref=ref)

    def entity(self, name: str, *, ref: str | None = None) -> EntityRef:
        return self._make(name, "entity", ref=ref)

    def database(self, name: str, *, ref: str | None = None) -> EntityRef:
        return self._make(name, "database", ref=ref)

    def collections(self, name: str, *, ref: str | None = None) -> EntityRef:
        return self._make(name, "collections", ref=ref)

    def queue(self, name: str, *, ref: str | None = None) -> EntityRef:
        return self._make(name, "queue", ref=ref)


class SequenceEventNamespace:
    """Factory namespace for sequence events and interaction frame blocks."""

    def message(
        self,
        source: EntityRef | str,
        target: EntityRef | str,
        label: str | None = None,
        *,
        line_style: MessageLineStyle = "solid",
        arrow_head: MessageArrowHead = "normal",
    ) -> _MessageData:
        return _MessageData(
            source=source, target=target, label=label,
            line_style=line_style, arrow_head=arrow_head,
        )

    def reply(
        self,
        source: EntityRef | str,
        target: EntityRef | str,
        label: str | None = None,
    ) -> _MessageData:
        """Sugar for a dotted return message."""
        return _MessageData(
            source=source, target=target, label=label,
            line_style="dotted", arrow_head="normal",
        )

    def note(
        self,
        content: EmbeddableContent,
        *,
        over: EntityRef | str | None = None,
        position: Literal["left", "right"] = "right",
        shape: NoteShape = "note",
    ) -> _EventNoteData:
        actual_position: Literal["left", "right", "over"] = (
            "over" if over is not None else position
        )
        return _EventNoteData(
            content=content, over=over,
            position=actual_position, shape=shape,
        )

    # --- Interaction frame blocks (for nesting inside event lists) ---

    def if_(self, label: str | None, events: list[_PhaseEvent],
            *extra_branches: Any) -> _BlockData:
        """Conditional branches (renders as alt/else)."""
        return _make_block("alt", label, events, *extra_branches)

    def optional(self, label: str | None,
                 events: list[_PhaseEvent]) -> _BlockData:
        """Optional block — may or may not execute (renders as opt)."""
        return _make_block("opt", label, events)

    def loop(self, label: str | None,
             events: list[_PhaseEvent]) -> _BlockData:
        """Repeated execution (renders as loop)."""
        return _make_block("loop", label, events)

    def parallel(self, events: list[_PhaseEvent],
                 *extra_branches: Any) -> _BlockData:
        """Concurrent paths (renders as par). No label on primary."""
        return _make_block("par", None, events, *extra_branches)

    def break_(self, label: str | None,
               events: list[_PhaseEvent]) -> _BlockData:
        """Break out of enclosing block (renders as break)."""
        return _make_block("break", label, events)

    def critical(self, label: str | None,
                 events: list[_PhaseEvent]) -> _BlockData:
        """Atomic section (renders as critical)."""
        return _make_block("critical", label, events)


# ---------------------------------------------------------------------------
# Build helpers
# ---------------------------------------------------------------------------


def _build_participant(entity_ref: EntityRef) -> Participant:
    return Participant(
        name=entity_ref._name,
        type=entity_ref._data.get("_type", "participant"),
    )


def _build_message(data: _MessageData) -> Message:
    return Message(
        source=_resolve_ref(data.source),
        target=_resolve_ref(data.target),
        label=Label(data.label) if data.label else None,
        line_style=data.line_style,
        arrow_head=data.arrow_head,
    )


def _build_event_note(data: _EventNoteData) -> SequenceNote:
    participants: tuple[str, ...] = ()
    if data.over is not None:
        participants = (_resolve_ref(data.over),)
    content = Label(data.content) if isinstance(data.content, str) else data.content
    return SequenceNote(
        content=content,
        position=data.position,
        participants=participants,
        shape=data.shape,
    )


def _build_event(event: _PhaseEvent) -> SequenceDiagramElement:
    """Convert a phase/block event to a primitive, recursively."""
    if isinstance(event, _MessageData):
        return _build_message(event)
    if isinstance(event, _EventNoteData):
        return _build_event_note(event)
    if isinstance(event, _BlockData):
        return _build_block(event)
    raise TypeError(f"Unknown event type: {type(event)}")


def _build_block(data: _BlockData) -> GroupBlock:
    """Convert a _BlockData to a GroupBlock primitive, recursively."""
    elements = tuple(_build_event(ev) for ev in data.events)
    else_blocks = tuple(
        ElseBlock(
            label=Label(label) if label else None,
            elements=tuple(_build_event(ev) for ev in branch_events),
        )
        for label, branch_events in data.else_branches
    )
    return GroupBlock(
        type=data.type,
        label=Label(data.label) if data.label else None,
        elements=elements,
        else_blocks=else_blocks,
    )


# ---------------------------------------------------------------------------
# Composer
# ---------------------------------------------------------------------------


class SequenceComposer(BaseComposer):
    """Composer for sequence diagrams."""

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
        actor_style: ActorStyle | None = None,
    ) -> None:
        super().__init__(
            title=title, mainframe=mainframe, caption=caption,
            header=header, footer=footer, legend=legend, scale=scale,
        )
        self._theme = theme
        self._actor_style = actor_style
        self._participants_ns = SequenceParticipantNamespace()
        self._events_ns = SequenceEventNamespace()
        self._timeline: list[Any] = []

    @property
    def participants(self) -> SequenceParticipantNamespace:
        return self._participants_ns

    @property
    def events(self) -> SequenceEventNamespace:
        return self._events_ns

    # --- Temporal registration ---

    def phase(self, label: str, events: list[_PhaseEvent]) -> None:
        """Register a labeled group (renders as group)."""
        self._timeline.append(_BlockData(
            type="group", label=label, events=tuple(events),
        ))

    def if_(self, label: str | None, events: list[_PhaseEvent],
            *extra_branches: Any) -> None:
        """Register conditional branches (renders as alt/else)."""
        self._timeline.append(_make_block("alt", label, events, *extra_branches))

    def optional(self, label: str | None,
                 events: list[_PhaseEvent]) -> None:
        """Register optional block (renders as opt)."""
        self._timeline.append(_make_block("opt", label, events))

    def loop(self, label: str | None,
             events: list[_PhaseEvent]) -> None:
        """Register loop block (renders as loop)."""
        self._timeline.append(_make_block("loop", label, events))

    def parallel(self, events: list[_PhaseEvent],
                 *extra_branches: Any) -> None:
        """Register parallel block (renders as par)."""
        self._timeline.append(_make_block("par", None, events, *extra_branches))

    def break_(self, label: str | None,
               events: list[_PhaseEvent]) -> None:
        """Register break block."""
        self._timeline.append(_make_block("break", label, events))

    def critical(self, label: str | None,
                 events: list[_PhaseEvent]) -> None:
        """Register critical block."""
        self._timeline.append(_make_block("critical", label, events))

    def divider(self, label: str) -> None:
        """Add a horizontal divider line with a centered title."""
        self._timeline.append(Divider(title=label))

    def delay(self, message: str | None = None) -> None:
        """Add a visual delay indicator (...)."""
        self._timeline.append(Delay(message=message))

    # --- Build ---

    def build(self) -> SequenceDiagram:
        participants: list[Participant] = []
        for item in self._elements:
            if isinstance(item, EntityRef):
                participants.append(_build_participant(item))

        elements: list[SequenceDiagramElement] = []

        # Timeline items → GroupBlocks, Dividers, Delays
        for item in self._timeline:
            if isinstance(item, _BlockData):
                elements.append(_build_block(item))
            elif isinstance(item, (Divider, Delay)):
                elements.append(item)

        # Diagram-level notes
        for note_data in self._notes:
            target = note_data["target"]
            participants_tuple: tuple[str, ...] = ()
            pos = note_data["position"]
            if target is not None:
                participants_tuple = (_resolve_ref(target),)
                pos = "over"
            content = note_data["content"]
            content_label = Label(content) if isinstance(content, str) else content
            elements.append(SequenceNote(
                content=content_label,
                position=pos,
                participants=participants_tuple,
            ))

        return SequenceDiagram(
            elements=tuple(elements),
            participants=tuple(participants),
            title=self._title,
            mainframe=self._mainframe,
            caption=self._caption,
            header=self._header,
            footer=self._footer,
            legend=self._legend,
            scale=self._scale,
            theme=self._theme,
            actor_style=self._actor_style,
        )


def sequence_diagram(
    *,
    title: str | None = None,
    mainframe: str | None = None,
    caption: str | None = None,
    header: str | Header | None = None,
    footer: str | Footer | None = None,
    legend: str | Legend | None = None,
    scale: float | Scale | None = None,
    theme: ThemeLike = None,
    actor_style: ActorStyle | None = None,
) -> SequenceComposer:
    """Create a sequence diagram composer.

    Example:
        d = sequence_diagram(title="Auth Flow")
        p = d.participants
        e = d.events

        client, api = d.add(p.actor("Client"), p.participant("API"))

        d.if_("valid credentials", [
            e.message(api, client, "200 OK"),
        ], "invalid", [
            e.message(api, client, "401"),
        ])

        print(render(d))
    """
    return SequenceComposer(
        title=title, mainframe=mainframe, caption=caption,
        header=header, footer=footer, legend=legend, scale=scale,
        theme=theme, actor_style=actor_style,
    )
