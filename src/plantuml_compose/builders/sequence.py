"""Sequence diagram builder with context manager syntax.

When to Use
-----------
Sequence diagrams show how multiple entities interact over time. Use when:

- Documenting request/response flows (HTTP, API calls)
- Showing object collaboration in a scenario
- Illustrating protocol exchanges
- Explaining complex multi-step processes

NOT for:
- Single entity changing states (use state diagram)
- Static structure (use class diagram)
- System architecture (use component diagram)

Key Concepts
------------
Participant:  An entity that sends/receives messages (User, API, Database)
Message:      Communication between participants (arrows)
Activation:   Period when participant is processing (vertical bar)

              User          API           DB
               │             │             │
               │──request──► │             │
               │             ├────query───►│
               │             │◄───result───│
               │◄──response──│             │
               │             │             │

Grouping Blocks (combined fragments):

    alt:      Alternative paths (if/else)
    opt:      Optional section (if without else)
    loop:     Repeated section
    par:      Parallel execution
    critical: Atomic section

IMPORTANT: Inside blocks, use the block's builder for messages:

    with d.alt("condition") as alt:
        alt.message(a, b)     # Correct - use alt.message()
        # d.message(a, b)     # Wrong! Would raise an error

Example
-------
    with sequence_diagram(title="Order Flow") as d:
        user = d.participant("User")
        api = d.boundary("API")
        db = d.database("Database")

        d.message(user, api, "POST /orders")
        d.activate(api)
        d.message(api, db, "INSERT")
        d.message(db, api, "OK")
        d.message(api, user, "201 Created")
        d.deactivate(api)

    print(render(d.build()))

Example with Blocks
-------------------
    with sequence_diagram() as d:
        user = d.participant("User")
        api = d.participant("API")

        d.message(user, api, "login")

        # Alternative paths - use block's builder for messages!
        with d.alt("valid credentials") as alt:
            alt.message(api, user, "success")
            with alt.else_("invalid"):
                alt.message(api, user, "error")

        # Optional section
        with d.opt("remember me") as opt:
            opt.message(api, user, "set cookie")
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Literal

from ..primitives.common import (
    ColorLike,
    Footer,
    Header,
    Label,
    LabelLike,
    Legend,
    LineStyle,
    LineStyleLike,
    Scale,
    StyleLike,
    coerce_line_style,
    validate_style_background_only,
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
        style: LineStyleLike | None = None,
    ) -> Message:
        """Create and register a message between participants.

        Args:
            source: Source participant (Participant object or reference string)
            target: Target participant (Participant object or reference string)
            label: Message label text
            line_style: "solid" or "dotted"
            arrow_head: Arrow head style
            bidirectional: If True, arrow points both directions
            style: Arrow style (color, bold)

        Returns:
            The created Message

        For activation control, use explicit methods:
            d.activate(participant)    # Start activation bar
            d.deactivate(participant)  # End activation bar
            d.destroy(participant)     # Destroy participant with X
        """
        label_obj = Label(label) if isinstance(label, str) else label
        style_obj = coerce_line_style(style) if style else None
        msg = Message(
            source=self._to_ref(source),
            target=self._to_ref(target),
            label=label_obj,
            line_style=line_style,
            arrow_head=arrow_head,
            bidirectional=bidirectional,
            style=style_obj,
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
        position: Literal["left", "right"] = "right",
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
            position: "left" or "right" (use `over` parameter for "over" notes)
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

        note_pos: Literal["left", "right", "over"] = "over" if over else position
        note = SequenceNote(
            content=content_label,
            position=note_pos,
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
                alt.message(api, user, "200 OK")
                with alt.else_("error") as else_block:
                    else_block.message(api, user, "500 Error")
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
        caption: str | None = None,
        header: str | Header | None = None,
        footer: str | Footer | None = None,
        legend: str | Legend | None = None,
        scale: float | Scale | None = None,
        autonumber: bool = False,
        hide_unlinked: bool = False,
    ) -> None:
        super().__init__()
        self._title = title
        self._caption = caption
        self._header = Header(header) if isinstance(header, str) else header
        self._footer = Footer(footer) if isinstance(footer, str) else footer
        self._legend = Legend(legend) if isinstance(legend, str) else legend
        self._scale = Scale(factor=scale) if isinstance(scale, (int, float)) else scale
        self._autonumber = Autonumber() if autonumber else None
        self._hide_unlinked = hide_unlinked
        self._participants: list[Participant] = []
        self._boxes: list[Box] = []
        # Track block context for detecting d.message() inside blocks
        self._block_stack: list[str] = []

    # Override message() to detect calls inside block contexts
    def message(
        self,
        source: Participant | str,
        target: Participant | str,
        label: str | Label | None = None,
        *,
        line_style: MessageLineStyle = "solid",
        arrow_head: MessageArrowHead = "normal",
        bidirectional: bool = False,
        style: LineStyleLike | None = None,
    ) -> Message:
        """Create and register a message between participants.

        Args:
            source: Source participant (Participant object or reference string)
            target: Target participant (Participant object or reference string)
            label: Message label text
            line_style: "solid" or "dotted"
            arrow_head: Arrow head style
            bidirectional: If True, arrow points both directions
            style: Arrow style (color, bold)

        Returns:
            The created Message

        For activation control, use explicit methods:
            d.activate(participant)    # Start activation bar
            d.deactivate(participant)  # End activation bar
            d.destroy(participant)     # Destroy participant with X

        Raises:
            RuntimeError: If called inside a block context (alt, opt, loop, etc.)
        """
        if self._block_stack:
            block_type = self._block_stack[-1]
            raise RuntimeError(
                f"d.message() called inside '{block_type}' block.\n\n"
                f"Messages inside blocks must use the block's builder:\n\n"
                f"    with d.{block_type}(...) as {block_type}:\n"
                f"        {block_type}.message(...)  # Correct\n\n"
                f"If you want the message outside the block, "
                f"move it before or after the 'with' statement."
            )
        return super().message(
            source,
            target,
            label,
            line_style=line_style,
            arrow_head=arrow_head,
            bidirectional=bidirectional,
            style=style,
        )

    # Override block context managers to track block stack
    @contextmanager
    def alt(self, label: str | Label | None = None) -> Iterator[_AltBuilder]:
        """Create an alt (alternative) grouping block.

        Usage:
            with d.alt("success") as alt:
                alt.message(api, user, "200 OK")
                with alt.else_("error") as else_block:
                    else_block.message(api, user, "500 Error")
        """
        self._block_stack.append("alt")
        try:
            builder = _AltBuilder("alt", label)
            yield builder
            self._elements.append(builder._build())
        finally:
            self._block_stack.pop()

    @contextmanager
    def opt(self, label: str | Label | None = None) -> Iterator[_GroupBuilder]:
        """Create an opt (optional) grouping block."""
        self._block_stack.append("opt")
        try:
            builder = _GroupBuilder("opt", label)
            yield builder
            self._elements.append(builder._build())
        finally:
            self._block_stack.pop()

    @contextmanager
    def loop(self, label: str | Label | None = None) -> Iterator[_GroupBuilder]:
        """Create a loop grouping block."""
        self._block_stack.append("loop")
        try:
            builder = _GroupBuilder("loop", label)
            yield builder
            self._elements.append(builder._build())
        finally:
            self._block_stack.pop()

    @contextmanager
    def par(self, label: str | Label | None = None) -> Iterator[_AltBuilder]:
        """Create a par (parallel) grouping block.

        par blocks can have else branches like alt.
        """
        self._block_stack.append("par")
        try:
            builder = _AltBuilder("par", label)
            yield builder
            self._elements.append(builder._build())
        finally:
            self._block_stack.pop()

    @contextmanager
    def break_(self, label: str | Label | None = None) -> Iterator[_GroupBuilder]:
        """Create a break grouping block."""
        self._block_stack.append("break")
        try:
            builder = _GroupBuilder("break", label)
            yield builder
            self._elements.append(builder._build())
        finally:
            self._block_stack.pop()

    @contextmanager
    def critical(self, label: str | Label | None = None) -> Iterator[_GroupBuilder]:
        """Create a critical grouping block."""
        self._block_stack.append("critical")
        try:
            builder = _GroupBuilder("critical", label)
            yield builder
            self._elements.append(builder._build())
        finally:
            self._block_stack.pop()

    @contextmanager
    def group(
        self,
        label: str | Label | None = None,
        secondary: str | Label | None = None,
    ) -> Iterator[_GroupBuilder]:
        """Create a custom group with optional secondary label.

        Rendered as: group Label [Secondary]
        """
        self._block_stack.append("group")
        try:
            builder = _GroupBuilder("group", label, secondary)
            yield builder
            self._elements.append(builder._build())
        finally:
            self._block_stack.pop()

    def participant(
        self,
        name: str,
        *,
        alias: str | None = None,
        type: ParticipantType = "participant",
        order: int | None = None,
        style: StyleLike | None = None,
        description: str | Label | None = None,
    ) -> Participant:
        """Create and register a participant.

        Args:
            name: Display name
            alias: Optional short reference name
            type: Participant shape type
            order: Display order (lower = leftmost)
            style: Visual style (background, line, text_color)
            description: Multiline description shown under the participant

        Returns:
            The created Participant
        """
        if not name:
            raise ValueError("Participant name cannot be empty")
        desc_label = Label(description) if isinstance(description, str) else description
        style_obj = validate_style_background_only(style, "Participant")
        p = Participant(
            name=name,
            alias=alias,
            type=type,
            order=order,
            style=style_obj,
            description=desc_label,
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
        style: StyleLike | None = None,
        description: str | Label | None = None,
    ) -> Participant:
        """Create an actor participant (stick figure)."""
        return self.participant(
            name, alias=alias, type="actor", order=order, style=style, description=description
        )

    def boundary(
        self,
        name: str,
        *,
        alias: str | None = None,
        order: int | None = None,
        style: StyleLike | None = None,
        description: str | Label | None = None,
    ) -> Participant:
        """Create a boundary participant."""
        return self.participant(
            name, alias=alias, type="boundary", order=order, style=style, description=description
        )

    def control(
        self,
        name: str,
        *,
        alias: str | None = None,
        order: int | None = None,
        style: StyleLike | None = None,
        description: str | Label | None = None,
    ) -> Participant:
        """Create a control participant."""
        return self.participant(
            name, alias=alias, type="control", order=order, style=style, description=description
        )

    def entity(
        self,
        name: str,
        *,
        alias: str | None = None,
        order: int | None = None,
        style: StyleLike | None = None,
        description: str | Label | None = None,
    ) -> Participant:
        """Create an entity participant."""
        return self.participant(
            name, alias=alias, type="entity", order=order, style=style, description=description
        )

    def database(
        self,
        name: str,
        *,
        alias: str | None = None,
        order: int | None = None,
        style: StyleLike | None = None,
        description: str | Label | None = None,
    ) -> Participant:
        """Create a database participant (cylinder)."""
        return self.participant(
            name, alias=alias, type="database", order=order, style=style, description=description
        )

    def collections(
        self,
        name: str,
        *,
        alias: str | None = None,
        order: int | None = None,
        style: StyleLike | None = None,
        description: str | Label | None = None,
    ) -> Participant:
        """Create a collections participant."""
        return self.participant(
            name, alias=alias, type="collections", order=order, style=style, description=description
        )

    def queue(
        self,
        name: str,
        *,
        alias: str | None = None,
        order: int | None = None,
        style: StyleLike | None = None,
        description: str | Label | None = None,
    ) -> Participant:
        """Create a queue participant."""
        return self.participant(
            name, alias=alias, type="queue", order=order, style=style, description=description
        )

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
            caption=self._caption,
            header=self._header,
            footer=self._footer,
            legend=self._legend,
            scale=self._scale,
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
        style: StyleLike | None = None,
        description: str | Label | None = None,
    ) -> Participant:
        """Create a participant within this box."""
        if not name:
            raise ValueError("Participant name cannot be empty")
        desc_label = Label(description) if isinstance(description, str) else description
        style_obj = validate_style_background_only(style, "Participant")
        p = Participant(
            name=name,
            alias=alias,
            type=type,
            order=order,
            style=style_obj,
            description=desc_label,
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
    caption: str | None = None,
    header: str | Header | None = None,
    footer: str | Footer | None = None,
    legend: str | Legend | None = None,
    scale: float | Scale | None = None,
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
        caption: Optional caption below the diagram
        header: Optional header text (string or Header object)
        footer: Optional footer text (string or Footer object)
        legend: Optional legend content (string or Legend object)
        scale: Optional scale factor (float) or Scale object
        autonumber: Enable automatic message numbering
        hide_unlinked: Hide participants with no messages

    Yields:
        A SequenceDiagramBuilder for adding diagram elements
    """
    builder = SequenceDiagramBuilder(
        title=title,
        caption=caption,
        header=header,
        footer=footer,
        legend=legend,
        scale=scale,
        autonumber=autonumber,
        hide_unlinked=hide_unlinked,
    )
    yield builder
