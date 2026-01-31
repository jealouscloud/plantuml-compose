"""Sequence diagram primitives.

Sequence diagrams show interactions between participants over time. Messages
flow from left to right, and time progresses from top to bottom. They're
ideal for documenting:

- API call flows and request/response patterns
- User interaction scenarios
- System integration protocols
- Method call sequences in code

Key concepts:
    Participant: An entity (user, service, object) that sends/receives messages
    Lifeline:    The vertical dashed line showing a participant's existence
    Message:     Communication from one participant to another (arrows)
    Activation:  A narrow rectangle showing when a participant is active
    Fragment:    A grouping like alt (if/else), loop, or opt (optional)

All types are frozen dataclasses - immutable data with no behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, TypeAlias

from .common import (
    ColorLike,
    Footer,
    Header,
    LabelLike,
    LayoutEngine,
    Legend,
    LineStyleLike,
    LineType,
    sanitize_ref,
    Scale,
    SequenceDiagramStyle,
    Style,
    ThemeLike,
)


# Participant shape types - visual representation in the diagram
ParticipantType = Literal[
    "participant",  # Default rectangle
    "actor",  # Stick figure (human user)
    "boundary",  # UI or external interface (circle with line)
    "control",  # Controller/logic (circle with arrow)
    "entity",  # Data/domain object (circle with line below)
    "database",  # Database (cylinder)
    "collections",  # Collection/group (stacked rectangles)
    "queue",  # Message queue
]

# Message arrow line styles
MessageLineStyle = Literal[
    "solid",  # -> Synchronous message
    "dotted",  # --> Asynchronous or return message
]

# Message arrow head styles
MessageArrowHead = Literal[
    "normal",  # >   Standard filled arrow
    "thin",  # >>  Thin/async arrow
    "lost",  # >x  Message lost (didn't reach target)
    "open",  # \   Upper half arrow (async-style)
    "circle",  # >o  Arrow with circle
    "none",  #     No arrowhead (just a line)
]

# Grouping block types (combined fragment operators)
GroupType = Literal[
    "alt",  # Alternative: if/else branches
    "opt",  # Optional: may or may not execute
    "loop",  # Loop: repeated execution
    "par",  # Parallel: concurrent execution
    "break",  # Break: exit enclosing fragment
    "critical",  # Critical: atomic region (no interruption)
    "group",  # Custom group with arbitrary label
]

# Note shape variants
NoteShape = Literal[
    "note",  # Standard rectangular note
    "hnote",  # Hexagonal note
    "rnote",  # Rounded note
]

# Activation actions for shorthand syntax on messages
ActivationAction = Literal[
    "activate",  # ++ Start activation bar
    "deactivate",  # -- End activation bar
    "create",  # ** Create new participant
    "destroy",  # !! Destroy participant (X on lifeline)
]


@dataclass(frozen=True)
class Participant:
    """An entity that sends or receives messages in a sequence diagram.

    Participants appear as columns with a header box and vertical lifeline.
    Each message arrow connects one participant to another.

        name:        Display name in the header box
        alias:       Short identifier for referencing in messages
        type:        Visual shape ("actor", "database", "participant", etc.)
        order:       Display position (lower numbers = left side)
        style:       Visual style (background, line, text_color)
        description: Multi-line text in the header (below name)
    """

    name: str
    alias: str | None = None
    type: ParticipantType = "participant"
    order: int | None = None  # Display order
    style: Style | None = None
    description: LabelLike | None = None  # Multiline description

    @property
    def _ref(self) -> str:
        """Internal: Reference name for use in messages."""
        if self.alias:
            return self.alias
        return sanitize_ref(self.name)


@dataclass(frozen=True)
class Message:
    """An arrow between participants representing communication.

    Messages are the core of sequence diagrams, showing how participants
    interact over time. Each message renders as an arrow with optional label.

        source/target:  Participant references
        label:          Text on the arrow
        line_style:     "solid" (sync) or "dotted" (async/return)
        arrow_head:     Arrow style ("normal", "thin", "lost", etc.)
        bidirectional:  If True, arrow points both directions
        activation:     Shorthand to activate/deactivate target
        slant:          Pixels to shift arrow head down (requires teoz mode)
        parallel:       If True, runs parallel with previous message (requires teoz)

    Arrow styling via style:
        color:     Arrow color
        thickness: Line width in pixels
        bold:      If True, thicker line
    """

    source: str  # Participant reference
    target: str  # Participant reference
    label: LabelLike | None = None
    line_style: MessageLineStyle = "solid"
    arrow_head: MessageArrowHead = "normal"
    bidirectional: bool = False
    # Arrow styling (bracket syntax: -[#red,bold]->)
    style: LineStyleLike | None = None
    # Activation shorthand
    activation: ActivationAction | None = None
    activation_color: ColorLike | None = None
    # Teoz features (require teoz=True on diagram)
    slant: int | None = None  # Pixels to shift arrow head down (shows timing delay)
    parallel: bool = False  # If True, message runs parallel with previous (& prefix)


@dataclass(frozen=True)
class Return:
    """A return message from the current activation.

    Used inside an activation block to show the response. Renders as
    a dotted arrow back to the caller with an optional label.
    """

    label: LabelLike | None = None


@dataclass(frozen=True)
class Activation:
    """Explicit control over a participant's activation bar.

    Activation bars are narrow rectangles on the lifeline showing when
    a participant is actively processing. Usually managed implicitly
    via message shortcuts (++, --), but this allows explicit control.

        participant: Which participant to activate/deactivate/destroy/create
        action:      "activate", "deactivate", "destroy", or "create"
        color:       Activation bar color (only for activate)

    The "create" action marks a participant as created at this point.
    Before creation, the participant's lifeline doesn't exist.
    """

    participant: str  # Participant reference
    action: Literal["activate", "deactivate", "destroy", "create"]
    color: ColorLike | None = None  # Only for activate


@dataclass(frozen=True)
class GroupBlock:
    """A combined fragment (alt, opt, loop, par, etc.) grouping messages.

    Fragments are boxes around message sequences that add control flow
    semantics. Each type has specific meaning:

        alt:      Alternative paths (if/else)
        opt:      Optional (may or may not execute)
        loop:     Repeated execution
        par:      Parallel execution
        break:    Exit enclosing fragment
        critical: Atomic region
        group:    Custom labeled grouping

    Use else_blocks for alt/par branches.
    """

    type: GroupType
    label: LabelLike | None = None
    secondary_label: LabelLike | None = None  # For group [secondary]
    elements: tuple["SequenceDiagramElement", ...] = field(
        default_factory=tuple
    )
    else_blocks: tuple["ElseBlock", ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ElseBlock:
    """An alternative branch within an alt or par block.

    Represents an "else" or additional parallel track with its own
    label and message sequence.
    """

    label: LabelLike | None = None
    elements: tuple["SequenceDiagramElement", ...] = field(
        default_factory=tuple
    )


@dataclass(frozen=True)
class Box:
    """A visual container grouping related participants.

    Boxes draw a rectangle around participants to show they belong
    together (e.g., "Frontend Services", "Database Cluster").
    """

    name: str | None = None
    color: ColorLike | None = None
    participants: tuple[Participant, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class SequenceNote:
    """A note annotation in a sequence diagram.

    Notes can be positioned relative to participants:

        position: "left", "right", or "over"
        participants: Which participant(s) the note relates to
        across: If True, spans all participants
        aligned: If True, aligns with the previous note
        shape: "note" (rectangle), "hnote" (hexagon), "rnote" (rounded)
    """

    content: LabelLike
    position: Literal["left", "right", "over"] = "right"
    participants: tuple[str, ...] = field(
        default_factory=tuple
    )  # For "over" - participant refs
    shape: NoteShape = "note"
    across: bool = False  # note across: spans all participants
    aligned: bool = False  # / note: aligned with previous


@dataclass(frozen=True)
class Reference:
    """A reference box pointing to another diagram or interaction.

    Rendered as a box spanning the specified participants with a
    label like "See Authentication Flow" or "ref: LoginSequence".
    """

    participants: tuple[str, ...]  # Participant references
    label: LabelLike


@dataclass(frozen=True)
class Divider:
    """A horizontal divider line with a centered title.

    Dividers separate logical phases of an interaction, rendered as
    a double line spanning the diagram with text like "== Phase 2 ==".
    """

    title: str


@dataclass(frozen=True)
class Delay:
    """A visual indicator of time passing.

    Rendered as "..." or "...message..." to show a pause or delay
    in the interaction before the next message.
    """

    message: str | None = None


@dataclass(frozen=True)
class Space:
    """Explicit vertical spacing between elements.

    Adds blank space in the diagram. Use when automatic spacing
    isn't sufficient for visual clarity.

        pixels: Space height (None for default spacing)
    """

    pixels: int | None = None  # None means default spacing


@dataclass(frozen=True)
class Autonumber:
    """Control for automatic message numbering.

    Adds sequence numbers (1, 2, 3...) to messages for easy reference.

        action:    "start", "stop", or "resume"
        start:     Starting number
        increment: Step between numbers
        format:    Display format (e.g., "<b>[000]" for bold three-digit)
    """

    action: Literal["start", "stop", "resume"] = "start"
    start: int | None = None
    increment: int | None = None
    format: str | None = None  # e.g., "<b>[000]"


@dataclass(frozen=True)
class SequenceDiagram:
    """A complete sequence diagram ready for rendering.

    Contains all participants, messages, and diagram-level settings.
    Usually created via the sequence_diagram() builder rather than directly.

        elements:      Messages, notes, groups, and other content
        participants:  Declared participants (controls ordering)
        boxes:         Visual groupings of participants
        title:         Optional diagram title
        autonumber:    Message numbering settings
        hide_unlinked: If True, hide participants with no messages
    """

    elements: tuple["SequenceDiagramElement", ...] = field(
        default_factory=tuple
    )
    title: str | None = None
    caption: str | None = None
    header: Header | None = None
    footer: Footer | None = None
    legend: Legend | None = None
    scale: Scale | None = None
    theme: ThemeLike = None
    layout_engine: LayoutEngine | None = None
    linetype: LineType | None = None
    # Participants declared at top (for ordering)
    participants: tuple[Participant, ...] = field(default_factory=tuple)
    # Boxes containing participants
    boxes: tuple[Box, ...] = field(default_factory=tuple)
    # Diagram-wide settings
    autonumber: Autonumber | None = None
    hide_unlinked: bool = False  # hide unlinked participants
    teoz: bool = False  # Enable teoz rendering for parallel messages and anchors
    diagram_style: SequenceDiagramStyle | None = None  # CSS-like diagram styling


# Type alias for elements that can appear in a sequence diagram
SequenceDiagramElement: TypeAlias = (
    Message
    | Return
    | Activation
    | GroupBlock
    | SequenceNote
    | Reference
    | Divider
    | Delay
    | Space
    | Autonumber
)
