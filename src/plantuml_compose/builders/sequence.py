"""Sequence diagram builder with context manager syntax.

Provides a fluent API for constructing sequence diagrams:

    with sequence_diagram(title="Order Flow") as d:
        user = d.participant("User")
        api = d.participant("API", type="boundary")
        db = d.database("Database")

        d.message(user, api, "POST /orders")
        d.message(api, db, "INSERT")

        with d.alt("success") as alt:
            d.message(api, user, "200 OK")
            with alt.else_("error"):
                d.message(api, user, "500 Error")

    print(render(d.build()))
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from ..primitives.common import (
    ColorLike,
    Label,
    LabelLike,
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


class _BaseSequenceBuilder:
    """Base class for sequence builders with shared methods."""

    def __init__(self) -> None:
        self._elements: list[SequenceDiagramElement] = []

    def message(
        self,
        source: Participant | str,
        target: Participant | str,
        label: str | Label | None = None,
        *,
        line_style: MessageLineStyle = "solid",
        arrow_head: MessageArrowHead = "normal",
        bidirectional: bool = False,
        activate: ActivationAction | None = None,
        activate_color: ColorLike | None = None,
    ) -> Message:
        """Create and register a message between participants.

        Args:
            source: Source participant (Participant object or reference string)
            target: Target participant (Participant object or reference string)
            label: Message label text
            line_style: "solid" or "dotted"
            arrow_head: Arrow head style
            bidirectional: If True, arrow points both directions
            activate: Activation shorthand (++, --, **, !!)
            activate_color: Color for activation bar

        Returns:
            The created Message
        """
        label_obj = Label(label) if isinstance(label, str) else label
        msg = Message(
            source=self._to_ref(source),
            target=self._to_ref(target),
            label=label_obj,
            line_style=line_style,
            arrow_head=arrow_head,
            bidirectional=bidirectional,
            activation=activate,
            activation_color=activate_color,
        )
        self._elements.append(msg)
        return msg

    def return_(self, label: str | Label | None = None) -> Return:
        """Create a return message (auto-return from activation).

        Rendered as: return label
        """
        label_obj = Label(label) if isinstance(label, str) else label
        ret = Return(label=label_obj)
        self._elements.append(ret)
        return ret

    def activate(
        self,
        participant: Participant | str,
        color: ColorLike | None = None,
    ) -> Activation:
        """Explicitly activate a participant."""
        act = Activation(
            participant=self._to_ref(participant),
            action="activate",
            color=color,
        )
        self._elements.append(act)
        return act

    def deactivate(self, participant: Participant | str) -> Activation:
        """Explicitly deactivate a participant."""
        act = Activation(
            participant=self._to_ref(participant),
            action="deactivate",
        )
        self._elements.append(act)
        return act

    def destroy(self, participant: Participant | str) -> Activation:
        """Destroy a participant (X on lifeline)."""
        act = Activation(
            participant=self._to_ref(participant),
            action="destroy",
        )
        self._elements.append(act)
        return act

    def note(
        self,
        content: str | Label,
        position: str = "right",
        *,
        of: Participant | str | None = None,
        over: tuple[Participant | str, ...] | None = None,
        shape: NoteShape = "note",
        across: bool = False,
        aligned: bool = False,
    ) -> SequenceNote:
        """Create and register a note.

        Args:
            content: Note text
            position: "left", "right", or "over"
            of: Participant for left/right notes
            over: Participants for "over" notes
            shape: "note", "hnote" (hexagonal), or "rnote" (rectangular)
            across: If True, spans all participants
            aligned: If True, aligns with previous note

        Returns:
            The created SequenceNote
        """
        text = content.text if isinstance(content, Label) else content
        if not text:
            raise ValueError("Note content cannot be empty")
        content_label = Label(content) if isinstance(content, str) else content

        participants: tuple[str, ...] = ()
        if of:
            participants = (self._to_ref(of),)
        elif over:
            participants = tuple(self._to_ref(p) for p in over)

        note_pos = "over" if over else position
        note = SequenceNote(
            content=content_label,
            position=note_pos,  # type: ignore[arg-type]
            participants=participants,
            shape=shape,
            across=across,
            aligned=aligned,
        )
        self._elements.append(note)
        return note

    def ref(
        self,
        *participants: Participant | str,
        label: str | Label,
    ) -> Reference:
        """Create a reference to another diagram.

        Args:
            *participants: Participants the reference spans
            label: Reference description

        Returns:
            The created Reference
        """
        label_obj = Label(label) if isinstance(label, str) else label
        ref = Reference(
            participants=tuple(self._to_ref(p) for p in participants),
            label=label_obj,
        )
        self._elements.append(ref)
        return ref

    def divider(self, title: str) -> Divider:
        """Create a divider line with title.

        Rendered as: == Title ==
        """
        if not title:
            raise ValueError("Divider title cannot be empty")
        div = Divider(title=title)
        self._elements.append(div)
        return div

    def delay(self, message: str | None = None) -> Delay:
        """Create a delay indicator.

        Rendered as: ... or ...message...
        """
        d = Delay(message=message)
        self._elements.append(d)
        return d

    def space(self, pixels: int | None = None) -> Space:
        """Create vertical spacing.

        Rendered as: ||| or ||N||
        """
        s = Space(pixels=pixels)
        self._elements.append(s)
        return s

    def autonumber(
        self,
        action: str = "start",
        *,
        start: int | None = None,
        increment: int | None = None,
        format: str | None = None,
    ) -> Autonumber:
        """Control autonumbering.

        Args:
            action: "start", "stop", or "resume"
            start: Starting number
            increment: Increment value
            format: Format string (e.g., "<b>[000]")

        Returns:
            The created Autonumber
        """
        auto = Autonumber(
            action=action,  # type: ignore[arg-type]
            start=start,
            increment=increment,
            format=format,
        )
        self._elements.append(auto)
        return auto

    # Grouping context managers
    @contextmanager
    def alt(self, label: str | Label | None = None) -> Iterator[_AltBuilder]:
        """Create an alt (alternative) grouping block.

        Usage:
            with d.alt("success") as alt:
                d.message(api, user, "200 OK")
                with alt.else_("error"):
                    d.message(api, user, "500 Error")
        """
        builder = _AltBuilder("alt", label)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def opt(self, label: str | Label | None = None) -> Iterator[_GroupBuilder]:
        """Create an opt (optional) grouping block."""
        builder = _GroupBuilder("opt", label)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def loop(self, label: str | Label | None = None) -> Iterator[_GroupBuilder]:
        """Create a loop grouping block."""
        builder = _GroupBuilder("loop", label)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def par(self, label: str | Label | None = None) -> Iterator[_AltBuilder]:
        """Create a par (parallel) grouping block.

        par blocks can have else branches like alt.
        """
        builder = _AltBuilder("par", label)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def break_(self, label: str | Label | None = None) -> Iterator[_GroupBuilder]:
        """Create a break grouping block."""
        builder = _GroupBuilder("break", label)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def critical(self, label: str | Label | None = None) -> Iterator[_GroupBuilder]:
        """Create a critical grouping block."""
        builder = _GroupBuilder("critical", label)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def group(
        self,
        label: str | Label | None = None,
        secondary: str | Label | None = None,
    ) -> Iterator[_GroupBuilder]:
        """Create a custom group with optional secondary label.

        Rendered as: group Label [Secondary]
        """
        builder = _GroupBuilder("group", label, secondary)
        yield builder
        self._elements.append(builder._build())

    def _to_ref(self, participant: Participant | str) -> str:
        """Convert a participant to its reference string."""
        if isinstance(participant, str):
            return participant
        return participant._ref


class _GroupBuilder(_BaseSequenceBuilder):
    """Builder for grouping blocks (opt, loop, break, critical, group)."""

    def __init__(
        self,
        group_type: GroupType,
        label: str | Label | None,
        secondary: str | Label | None = None,
    ) -> None:
        super().__init__()
        self._group_type = group_type
        self._label = Label(label) if isinstance(label, str) else label
        self._secondary = Label(secondary) if isinstance(secondary, str) else secondary

    def _build(self) -> GroupBlock:
        """Build the group block primitive."""
        return GroupBlock(
            type=self._group_type,
            label=self._label,
            secondary_label=self._secondary,
            elements=tuple(self._elements),
        )


class _AltBuilder(_GroupBuilder):
    """Builder for alt/par blocks that support else branches."""

    def __init__(
        self,
        group_type: GroupType,
        label: str | Label | None,
    ) -> None:
        super().__init__(group_type, label)
        self._else_blocks: list[ElseBlock] = []

    @contextmanager
    def else_(self, label: str | Label | None = None) -> Iterator[_ElseBuilder]:
        """Create an else branch.

        Usage:
            with d.alt("condition") as alt:
                d.message(a, b, "then")
                with alt.else_("other"):
                    d.message(a, b, "else")
        """
        builder = _ElseBuilder(label)
        yield builder
        self._else_blocks.append(builder._build())

    def _build(self) -> GroupBlock:
        """Build the group block primitive with else branches."""
        return GroupBlock(
            type=self._group_type,
            label=self._label,
            elements=tuple(self._elements),
            else_blocks=tuple(self._else_blocks),
        )


class _ElseBuilder(_BaseSequenceBuilder):
    """Builder for else branches within alt/par blocks."""

    def __init__(self, label: str | Label | None) -> None:
        super().__init__()
        self._label = Label(label) if isinstance(label, str) else label

    def _build(self) -> ElseBlock:
        """Build the else block primitive."""
        return ElseBlock(
            label=self._label,
            elements=tuple(self._elements),
        )


class SequenceDiagramBuilder(_BaseSequenceBuilder):
    """Builder for complete sequence diagrams.

    Usage:
        with sequence_diagram(title="Order Flow") as d:
            user = d.participant("User")
            api = d.boundary("API")
            db = d.database("Database")

            d.message(user, api, "request")
            d.message(api, db, "query")

        diagram = d.build()
        print(render(diagram))
    """

    def __init__(
        self,
        *,
        title: str | None = None,
        autonumber: bool = False,
        hide_unlinked: bool = False,
    ) -> None:
        super().__init__()
        self._title = title
        self._autonumber = Autonumber() if autonumber else None
        self._hide_unlinked = hide_unlinked
        self._participants: list[Participant] = []
        self._boxes: list[Box] = []

    def participant(
        self,
        name: str,
        *,
        alias: str | None = None,
        type: ParticipantType = "participant",
        order: int | None = None,
        color: ColorLike | None = None,
    ) -> Participant:
        """Create and register a participant.

        Args:
            name: Display name
            alias: Optional short reference name
            type: Participant shape type
            order: Display order (lower = leftmost)
            color: Background color

        Returns:
            The created Participant
        """
        if not name:
            raise ValueError("Participant name cannot be empty")
        p = Participant(
            name=name,
            alias=alias,
            type=type,
            order=order,
            color=color,
        )
        self._participants.append(p)
        return p

    def participants(
        self,
        *names: str,
        type: ParticipantType = "participant",
    ) -> tuple[Participant, ...]:
        """Create multiple participants at once.

        Returns:
            Tuple of created Participants

        Example:
            user, api, db = d.participants("User", "API", "Database")
        """
        return tuple(self.participant(name, type=type) for name in names)

    # Convenience methods for common participant types
    def actor(
        self,
        name: str,
        *,
        alias: str | None = None,
        order: int | None = None,
        color: ColorLike | None = None,
    ) -> Participant:
        """Create an actor participant (stick figure)."""
        return self.participant(name, alias=alias, type="actor", order=order, color=color)

    def boundary(
        self,
        name: str,
        *,
        alias: str | None = None,
        order: int | None = None,
        color: ColorLike | None = None,
    ) -> Participant:
        """Create a boundary participant."""
        return self.participant(name, alias=alias, type="boundary", order=order, color=color)

    def control(
        self,
        name: str,
        *,
        alias: str | None = None,
        order: int | None = None,
        color: ColorLike | None = None,
    ) -> Participant:
        """Create a control participant."""
        return self.participant(name, alias=alias, type="control", order=order, color=color)

    def entity(
        self,
        name: str,
        *,
        alias: str | None = None,
        order: int | None = None,
        color: ColorLike | None = None,
    ) -> Participant:
        """Create an entity participant."""
        return self.participant(name, alias=alias, type="entity", order=order, color=color)

    def database(
        self,
        name: str,
        *,
        alias: str | None = None,
        order: int | None = None,
        color: ColorLike | None = None,
    ) -> Participant:
        """Create a database participant (cylinder)."""
        return self.participant(name, alias=alias, type="database", order=order, color=color)

    def collections(
        self,
        name: str,
        *,
        alias: str | None = None,
        order: int | None = None,
        color: ColorLike | None = None,
    ) -> Participant:
        """Create a collections participant."""
        return self.participant(name, alias=alias, type="collections", order=order, color=color)

    def queue(
        self,
        name: str,
        *,
        alias: str | None = None,
        order: int | None = None,
        color: ColorLike | None = None,
    ) -> Participant:
        """Create a queue participant."""
        return self.participant(name, alias=alias, type="queue", order=order, color=color)

    @contextmanager
    def box(
        self,
        name: str | None = None,
        color: ColorLike | None = None,
    ) -> Iterator["_BoxBuilder"]:
        """Create a box to group participants.

        Usage:
            with d.box("Backend", color="LightBlue") as backend:
                api = backend.participant("API")
                db = backend.database("Database")
        """
        builder = _BoxBuilder(name, color)
        yield builder
        self._boxes.append(builder._build())

    def build(self) -> SequenceDiagram:
        """Build the complete sequence diagram."""
        # Collect participants from boxes
        box_participants = set()
        for box in self._boxes:
            for p in box.participants:
                box_participants.add(p.name)

        # Standalone participants (not in boxes)
        standalone = tuple(p for p in self._participants if p.name not in box_participants)

        return SequenceDiagram(
            elements=tuple(self._elements),
            title=self._title,
            participants=standalone,
            boxes=tuple(self._boxes),
            autonumber=self._autonumber,
            hide_unlinked=self._hide_unlinked,
        )

    def render(self) -> str:
        """Build and render the diagram to PlantUML text.

        Convenience method combining build() and render() in one call.
        """
        from ..renderers import render
        return render(self.build())


class _BoxBuilder:
    """Builder for participant boxes."""

    def __init__(self, name: str | None, color: ColorLike | None) -> None:
        self._name = name
        self._color = color
        self._participants: list[Participant] = []

    def participant(
        self,
        name: str,
        *,
        alias: str | None = None,
        type: ParticipantType = "participant",
        order: int | None = None,
        color: ColorLike | None = None,
    ) -> Participant:
        """Create a participant within this box."""
        if not name:
            raise ValueError("Participant name cannot be empty")
        p = Participant(
            name=name,
            alias=alias,
            type=type,
            order=order,
            color=color,
        )
        self._participants.append(p)
        return p

    # Convenience methods for common participant types
    def actor(self, name: str, **kwargs) -> Participant:
        """Create an actor participant within this box."""
        return self.participant(name, type="actor", **kwargs)

    def boundary(self, name: str, **kwargs) -> Participant:
        """Create a boundary participant within this box."""
        return self.participant(name, type="boundary", **kwargs)

    def control(self, name: str, **kwargs) -> Participant:
        """Create a control participant within this box."""
        return self.participant(name, type="control", **kwargs)

    def entity(self, name: str, **kwargs) -> Participant:
        """Create an entity participant within this box."""
        return self.participant(name, type="entity", **kwargs)

    def database(self, name: str, **kwargs) -> Participant:
        """Create a database participant within this box."""
        return self.participant(name, type="database", **kwargs)

    def collections(self, name: str, **kwargs) -> Participant:
        """Create a collections participant within this box."""
        return self.participant(name, type="collections", **kwargs)

    def queue(self, name: str, **kwargs) -> Participant:
        """Create a queue participant within this box."""
        return self.participant(name, type="queue", **kwargs)

    def _build(self) -> Box:
        """Build the box primitive."""
        return Box(
            name=self._name,
            color=self._color,
            participants=tuple(self._participants),
        )


@contextmanager
def sequence_diagram(
    *,
    title: str | None = None,
    autonumber: bool = False,
    hide_unlinked: bool = False,
) -> Iterator[SequenceDiagramBuilder]:
    """Create a sequence diagram with context manager syntax.

    Usage:
        with sequence_diagram(title="Order Flow") as d:
            user = d.actor("User")
            api = d.boundary("API")
            db = d.database("Database")

            d.message(user, api, "POST /orders")

            with d.alt("success") as alt:
                d.message(api, user, "200 OK")
                with alt.else_("error"):
                    d.message(api, user, "500 Error")

        print(d.render())

    Args:
        title: Optional diagram title
        autonumber: Enable automatic message numbering
        hide_unlinked: Hide participants with no messages

    Yields:
        A SequenceDiagramBuilder for adding diagram elements
    """
    builder = SequenceDiagramBuilder(
        title=title,
        autonumber=autonumber,
        hide_unlinked=hide_unlinked,
    )
    yield builder
