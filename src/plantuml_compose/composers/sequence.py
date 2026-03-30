"""Sequence diagram composer.

Temporal pattern with d.phase() grouping.

Example:
    d = sequence_diagram(title="PXE Boot", actor_style="awesome")
    p = d.participants
    e = d.events

    admin = p.actor("Admin")
    fastapi = p.participant("FastAPI (PXE Service)")
    d.add(admin, fastapi)

    d.phase("1. Provision Request", [
        e.message(admin, fastapi, "POST /add"),
        e.reply(fastapi, admin, "OK"),
    ])

    puml = render(d)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from ..primitives.common import (
    EmbeddableContent,
    Label,
    ThemeLike,
)
from ..primitives.sequence import (
    GroupBlock,
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
    """Resolve an EntityRef or raw string to a participant reference."""
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


# Union of things that go inside a phase list
_PhaseEvent = _MessageData | _EventNoteData


# ---------------------------------------------------------------------------
# Namespaces
# ---------------------------------------------------------------------------


class SequenceParticipantNamespace:
    """Factory namespace for sequence diagram participants."""

    def _make(
        self,
        name: str,
        type_: ParticipantType,
        *,
        ref: str | None = None,
    ) -> EntityRef:
        return EntityRef(
            name, ref=ref,
            data={"_type": type_},
        )

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
    """Factory namespace for sequence diagram events (messages, notes)."""

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
            source=source,
            target=target,
            label=label,
            line_style=line_style,
            arrow_head=arrow_head,
        )

    def reply(
        self,
        source: EntityRef | str,
        target: EntityRef | str,
        label: str | None = None,
    ) -> _MessageData:
        """Sugar for a dotted return message."""
        return _MessageData(
            source=source,
            target=target,
            label=label,
            line_style="dotted",
            arrow_head="normal",
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
            content=content,
            over=over,
            position=actual_position,
            shape=shape,
        )


# ---------------------------------------------------------------------------
# Composer
# ---------------------------------------------------------------------------


def _build_participant(entity_ref: EntityRef) -> Participant:
    """Convert an EntityRef to a Participant primitive."""
    return Participant(
        name=entity_ref._name,
        type=entity_ref._data.get("_type", "participant"),
    )


def _build_message(data: _MessageData) -> Message:
    """Convert a _MessageData to a Message primitive."""
    return Message(
        source=_resolve_ref(data.source),
        target=_resolve_ref(data.target),
        label=Label(data.label) if data.label else None,
        line_style=data.line_style,
        arrow_head=data.arrow_head,
    )


def _build_event_note(data: _EventNoteData) -> SequenceNote:
    """Convert a _EventNoteData to a SequenceNote primitive."""
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


def _build_phase_element(event: _PhaseEvent) -> SequenceDiagramElement:
    """Convert a phase event to a primitive."""
    if isinstance(event, _MessageData):
        return _build_message(event)
    if isinstance(event, _EventNoteData):
        return _build_event_note(event)
    raise TypeError(f"Unknown phase event type: {type(event)}")


class SequenceComposer(BaseComposer):
    """Composer for sequence diagrams."""

    def __init__(
        self,
        *,
        title: str | None = None,
        theme: ThemeLike = None,
        actor_style: ActorStyle | None = None,
    ) -> None:
        super().__init__()
        self._title = title
        self._theme = theme
        self._actor_style = actor_style
        self._participants_ns = SequenceParticipantNamespace()
        self._events_ns = SequenceEventNamespace()
        self._phases: list[Any] = []  # interleaved phases and diagram-level notes

    @property
    def participants(self) -> SequenceParticipantNamespace:
        return self._participants_ns

    @property
    def events(self) -> SequenceEventNamespace:
        return self._events_ns

    def phase(
        self,
        label: str,
        events: list[_PhaseEvent],
    ) -> None:
        """Register a temporal group (combined fragment)."""
        self._phases.append(("__phase__", label, events))

    def note(
        self,
        content: str,
        *,
        target: EntityRef | str | None = None,
        position: str = "right",
    ) -> None:
        """Diagram-level note (outside phases)."""
        self._notes.append({
            "content": content,
            "target": target,
            "position": position,
        })

    def build(self) -> SequenceDiagram:
        # Build participants from d.add() entities
        participants: list[Participant] = []
        for item in self._elements:
            if isinstance(item, EntityRef):
                participants.append(_build_participant(item))

        # Build diagram elements: phases become GroupBlocks, notes become SequenceNotes
        elements: list[SequenceDiagramElement] = []

        for phase_item in self._phases:
            if phase_item[0] == "__phase__":
                _, label, events = phase_item
                phase_elements = tuple(
                    _build_phase_element(ev) for ev in events
                )
                elements.append(GroupBlock(
                    type="group",
                    label=Label(label),
                    elements=phase_elements,
                ))

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
            theme=self._theme,
            actor_style=self._actor_style,
        )


def sequence_diagram(
    *,
    title: str | None = None,
    theme: ThemeLike = None,
    actor_style: ActorStyle | None = None,
) -> SequenceComposer:
    """Create a sequence diagram composer.

    Example:
        d = sequence_diagram(title="PXE Boot")
        p = d.participants
        e = d.events
        admin = p.actor("Admin")
        api = p.participant("API")
        d.add(admin, api)
        d.phase("Request", [
            e.message(admin, api, "POST /add"),
            e.reply(api, admin, "OK"),
        ])
        print(render(d))
    """
    return SequenceComposer(
        title=title,
        theme=theme,
        actor_style=actor_style,
    )
