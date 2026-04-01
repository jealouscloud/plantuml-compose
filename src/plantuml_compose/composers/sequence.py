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
    ColorLike,
    EmbeddableContent,
    Footer,
    Header,
    Label,
    Legend,
    LineStyleLike,
    Newpage,
    Scale,
    Style,
    ThemeLike,
)
from ..primitives.sequence import (
    Activation,
    ActivationAction,
    Autonumber,
    Box,
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
    Reference,
    Return,
    SequenceDiagram,
    SequenceDiagramElement,
    SequenceNote,
    Space,
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
    style: LineStyleLike | None = None
    bidirectional: bool = False
    activation: ActivationAction | None = None


@dataclass(frozen=True)
class _EventNoteData:
    """Pure data from e.note() — a note inside a phase."""
    content: EmbeddableContent
    over: EntityRef | str | list[EntityRef | str] | None
    position: Literal["left", "right", "over"]
    shape: NoteShape


@dataclass(frozen=True)
class _ActivationData:
    """Pure data from e.activate() / e.deactivate() / e.create() / e.destroy()."""
    participant: EntityRef | str
    action: str  # "activate", "deactivate", "create", "destroy"
    color: ColorLike | None = None


@dataclass(frozen=True)
class _ReturnData:
    """Pure data from e.return_()."""
    label: str | None = None


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
_PhaseEvent = _MessageData | _EventNoteData | _BlockData | _ActivationData | _ReturnData


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

    def _make(
        self,
        name: str,
        type_: ParticipantType,
        *,
        ref: str | None = None,
        style: Style | None = None,
        order: int | None = None,
    ) -> EntityRef:
        data: dict[str, Any] = {"_type": type_}
        if style is not None:
            data["_style"] = style
        if order is not None:
            data["_order"] = order
        return EntityRef(name, ref=ref, data=data)

    def participant(self, name: str, *, ref: str | None = None,
                    style: Style | None = None, order: int | None = None) -> EntityRef:
        return self._make(name, "participant", ref=ref, style=style, order=order)

    def actor(self, name: str, *, ref: str | None = None,
              style: Style | None = None, order: int | None = None) -> EntityRef:
        return self._make(name, "actor", ref=ref, style=style, order=order)

    def boundary(self, name: str, *, ref: str | None = None,
                 style: Style | None = None, order: int | None = None) -> EntityRef:
        return self._make(name, "boundary", ref=ref, style=style, order=order)

    def control(self, name: str, *, ref: str | None = None,
                style: Style | None = None, order: int | None = None) -> EntityRef:
        return self._make(name, "control", ref=ref, style=style, order=order)

    def entity(self, name: str, *, ref: str | None = None,
               style: Style | None = None, order: int | None = None) -> EntityRef:
        return self._make(name, "entity", ref=ref, style=style, order=order)

    def database(self, name: str, *, ref: str | None = None,
                 style: Style | None = None, order: int | None = None) -> EntityRef:
        return self._make(name, "database", ref=ref, style=style, order=order)

    def collections(self, name: str, *, ref: str | None = None,
                    style: Style | None = None, order: int | None = None) -> EntityRef:
        return self._make(name, "collections", ref=ref, style=style, order=order)

    def queue(self, name: str, *, ref: str | None = None,
              style: Style | None = None, order: int | None = None) -> EntityRef:
        return self._make(name, "queue", ref=ref, style=style, order=order)


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
        style: LineStyleLike | None = None,
        bidirectional: bool = False,
        activation: ActivationAction | None = None,
    ) -> _MessageData:
        return _MessageData(
            source=source, target=target, label=label,
            line_style=line_style, arrow_head=arrow_head,
            style=style, bidirectional=bidirectional,
            activation=activation,
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
        over: EntityRef | str | list[EntityRef | str] | None = None,
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

    # --- Lifecycle / activation events (for use inside phase lists) ---

    def activate(
        self,
        participant: EntityRef | str,
        *,
        color: ColorLike | None = None,
    ) -> _ActivationData:
        """Activate a participant (show activation bar)."""
        return _ActivationData(
            participant=participant, action="activate", color=color,
        )

    def deactivate(self, participant: EntityRef | str) -> _ActivationData:
        """Deactivate a participant (end activation bar)."""
        return _ActivationData(participant=participant, action="deactivate")

    def create(self, participant: EntityRef | str) -> _ActivationData:
        """Mark a participant as created at this point."""
        return _ActivationData(participant=participant, action="create")

    def destroy(self, participant: EntityRef | str) -> _ActivationData:
        """Destroy a participant (X on lifeline)."""
        return _ActivationData(participant=participant, action="destroy")

    def return_(self, label: str | None = None) -> _ReturnData:
        """Explicit return from activation."""
        return _ReturnData(label=label)

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
    from ..primitives.common import sanitize_ref
    alias = entity_ref._ref if entity_ref._ref != sanitize_ref(entity_ref._name) else None
    return Participant(
        name=entity_ref._name,
        alias=alias,
        type=entity_ref._data.get("_type", "participant"),
        style=entity_ref._data.get("_style"),
        order=entity_ref._data.get("_order"),
    )


def _build_message(data: _MessageData) -> Message:
    return Message(
        source=_resolve_ref(data.source),
        target=_resolve_ref(data.target),
        label=Label(data.label) if data.label else None,
        line_style=data.line_style,
        arrow_head=data.arrow_head,
        style=data.style,
        bidirectional=data.bidirectional,
        activation=data.activation,
    )


def _build_event_note(data: _EventNoteData) -> SequenceNote:
    participants: tuple[str, ...] = ()
    if data.over is not None:
        if isinstance(data.over, list):
            participants = tuple(_resolve_ref(item) for item in data.over)
        else:
            participants = (_resolve_ref(data.over),)
    content = Label(data.content) if isinstance(data.content, str) else data.content
    return SequenceNote(
        content=content,
        position=data.position,
        participants=participants,
        shape=data.shape,
    )


def _build_activation(data: _ActivationData) -> Activation:
    return Activation(
        participant=_resolve_ref(data.participant),
        action=data.action,
        color=data.color,
    )


def _build_return(data: _ReturnData) -> Return:
    return Return(label=Label(data.label) if data.label else None)


def _build_event(event: _PhaseEvent) -> SequenceDiagramElement:
    """Convert a phase/block event to a primitive, recursively."""
    if isinstance(event, _MessageData):
        return _build_message(event)
    if isinstance(event, _EventNoteData):
        return _build_event_note(event)
    if isinstance(event, _BlockData):
        return _build_block(event)
    if isinstance(event, _ActivationData):
        return _build_activation(event)
    if isinstance(event, _ReturnData):
        return _build_return(event)
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
        autonumber: bool | Autonumber | None = None,
        hide_unlinked: bool = False,
    ) -> None:
        super().__init__(
            title=title, mainframe=mainframe, caption=caption,
            header=header, footer=footer, legend=legend, scale=scale,
        )
        self._theme = theme
        self._actor_style = actor_style
        self._hide_unlinked = hide_unlinked
        if autonumber is True:
            self._autonumber: Autonumber | None = Autonumber()
        elif isinstance(autonumber, Autonumber):
            self._autonumber = autonumber
        else:
            self._autonumber = None
        self._participants_ns = SequenceParticipantNamespace()
        self._events_ns = SequenceEventNamespace()
        self._timeline: list[Any] = []
        self._boxes: list[Box] = []

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

    def space(self, pixels: int | None = None) -> None:
        """Add explicit vertical spacing between elements."""
        self._timeline.append(Space(pixels=pixels))

    # --- Activation / lifecycle (timeline-level) ---

    def activate(
        self,
        participant: EntityRef | str,
        *,
        color: ColorLike | None = None,
    ) -> None:
        """Activate a participant (show activation bar)."""
        self._timeline.append(_ActivationData(
            participant=participant, action="activate", color=color,
        ))

    def deactivate(self, participant: EntityRef | str) -> None:
        """Deactivate a participant (end activation bar)."""
        self._timeline.append(_ActivationData(
            participant=participant, action="deactivate",
        ))

    def create(self, participant: EntityRef | str) -> None:
        """Mark a participant as created at this point."""
        self._timeline.append(_ActivationData(
            participant=participant, action="create",
        ))

    def destroy(self, participant: EntityRef | str) -> None:
        """Destroy a participant (X on lifeline)."""
        self._timeline.append(_ActivationData(
            participant=participant, action="destroy",
        ))

    # --- Participant grouping ---

    def box(
        self,
        title: str | None = None,
        *participant_refs: EntityRef,
        color: ColorLike | None = None,
    ) -> None:
        """Group participants in a visual box.

        Args:
            title: Optional box title
            *participant_refs: Participant EntityRefs to include in the box
            color: Background color for the box
        """
        participants = tuple(
            _build_participant(ref) for ref in participant_refs
        )
        self._boxes.append(Box(
            name=title,
            color=color,
            participants=participants,
        ))

    # --- Reference ---

    def ref(
        self,
        *participant_refs: EntityRef | str,
        label: str,
    ) -> None:
        """Add a reference to another diagram.

        Args:
            *participant_refs: Participants the reference spans
            label: Reference description
        """
        self._timeline.append(Reference(
            participants=tuple(_resolve_ref(p) for p in participant_refs),
            label=Label(label),
        ))

    # --- Autonumber (runtime) ---

    def autonumber(
        self,
        *,
        start: int | str | None = None,
        increment: int | None = None,
        format: str | None = None,
    ) -> None:
        """Add an autonumber directive to the timeline."""
        self._timeline.append(Autonumber(
            action="start",
            start=start,
            increment=increment,
            format=format,
        ))

    def autonumber_stop(self) -> None:
        """Stop automatic message numbering."""
        self._timeline.append(Autonumber(action="stop"))

    def autonumber_resume(self) -> None:
        """Resume automatic message numbering."""
        self._timeline.append(Autonumber(action="resume"))

    # --- Newpage ---

    def newpage(self, title: str | None = None) -> None:
        """Insert a page break."""
        self._timeline.append(Newpage(title=title))

    # --- Build ---

    def build(self) -> SequenceDiagram:
        # Collect participants not inside boxes
        box_participant_names: set[str] = set()
        for box in self._boxes:
            for bp in box.participants:
                box_participant_names.add(bp.name)

        participants: list[Participant] = []
        for item in self._elements:
            if isinstance(item, EntityRef):
                if item._name not in box_participant_names:
                    participants.append(_build_participant(item))

        elements: list[SequenceDiagramElement] = []

        # Timeline items
        for item in self._timeline:
            if isinstance(item, _BlockData):
                elements.append(_build_block(item))
            elif isinstance(item, _ActivationData):
                elements.append(_build_activation(item))
            elif isinstance(item, (Divider, Delay, Space, Reference, Autonumber, Newpage)):
                elements.append(item)

        # Diagram-level notes
        for note_data in self._notes:
            target = note_data["target"]
            participants_tuple: tuple[str, ...] = ()
            pos = note_data["position"]
            if target is not None:
                participants_tuple = (_resolve_ref(target),)
                # "left" and "right" are valid positioned-note positions;
                # anything else (including the BaseComposer default "right")
                # maps to "over" for sequence diagrams with a target.
                # Users must pass position="left" or position="right" explicitly
                # to get note left/right of participant.
                if pos not in ("left", "right", "over"):
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
            boxes=tuple(self._boxes),
            title=self._title,
            mainframe=self._mainframe,
            caption=self._caption,
            header=self._header,
            footer=self._footer,
            legend=self._legend,
            scale=self._scale,
            theme=self._theme,
            actor_style=self._actor_style,
            autonumber=self._autonumber,
            hide_unlinked=self._hide_unlinked,
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
    autonumber: bool | Autonumber | None = None,
    hide_unlinked: bool = False,
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
        theme=theme, actor_style=actor_style, autonumber=autonumber,
        hide_unlinked=hide_unlinked,
    )
