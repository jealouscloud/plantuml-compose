"""Sequence diagram primitives.

All types are frozen dataclasses - immutable data with no behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, TypeAlias

from .common import (
    ColorLike,
    Label,
    LabelLike,
    LineStyleLike,
    Note,
    StyleLike,
)


# Participant shape types
ParticipantType = Literal[
    "participant",
    "actor",
    "boundary",
    "control",
    "entity",
    "database",
    "collections",
    "queue",
]

# Message arrow line styles
MessageLineStyle = Literal["solid", "dotted"]

# Message arrow head styles
MessageArrowHead = Literal[
    "normal",  # >
    "thin",  # >>
    "lost",  # x (message lost)
    "open",  # ) or ( - half arrows
    "circle",  # o
    "none",  # no arrow head
]

# Grouping block types (semantic keywords)
GroupType = Literal["alt", "opt", "loop", "par", "break", "critical", "group"]

# Note shape variants
NoteShape = Literal["note", "hnote", "rnote"]

# Activation actions for shorthand syntax
ActivationAction = Literal[
    "activate",  # ++
    "deactivate",  # --
    "create",  # **
    "destroy",  # !!
]


def _sanitize_participant_ref(name: str) -> str:
    """Create a PlantUML-friendly identifier from a participant name.

    For simple alphanumeric names, returns as-is.
    For names with spaces or special chars, they need quoting in output.
    """
    # If it's a simple identifier, return as-is
    if name.isidentifier():
        return name
    # Otherwise, we'll need to use "name" as alias syntax in renderer
    # Return a sanitized version for reference
    sanitized = name.replace(" ", "_")
    for char in "\"'`()[]{}:;,.<>!@#$%^&*+=|\\/?~-":
        sanitized = sanitized.replace(char, "")
    return sanitized or "_"


@dataclass(frozen=True)
class Participant:
    """A participant in a sequence diagram (lifeline)."""

    name: str
    alias: str | None = None
    type: ParticipantType = "participant"
    order: int | None = None  # Display order
    color: ColorLike | None = None
    description: LabelLike | None = None  # Multiline description

    @property
    def _ref(self) -> str:
        """Internal: Reference name for use in messages."""
        if self.alias:
            return self.alias
        return _sanitize_participant_ref(self.name)


@dataclass(frozen=True)
class Message:
    """A message between participants."""

    source: str  # Participant reference
    target: str  # Participant reference
    label: LabelLike | None = None
    line_style: MessageLineStyle = "solid"
    arrow_head: MessageArrowHead = "normal"
    bidirectional: bool = False
    # Arrow styling (bracket syntax: -[#red,bold]->)
    color: ColorLike | None = None
    thickness: int | None = None  # Pixels
    bold: bool = False
    # Activation shorthand
    activation: ActivationAction | None = None
    activation_color: ColorLike | None = None
    # Return message (for auto-return syntax)
    is_return: bool = False


@dataclass(frozen=True)
class Return:
    """Return message (auto-return from activation).

    Rendered as: return label
    """

    label: LabelLike | None = None


@dataclass(frozen=True)
class Activation:
    """Explicit activation/deactivation of a participant.

    For when you need explicit control, not message shorthand.
    """

    participant: str  # Participant reference
    action: Literal["activate", "deactivate", "destroy"]
    color: ColorLike | None = None  # Only for activate


@dataclass(frozen=True)
class GroupBlock:
    """A grouping block (alt, opt, loop, par, break, critical, group).

    Contains a sequence of elements and optional else branches.
    """

    type: GroupType
    label: LabelLike | None = None
    secondary_label: LabelLike | None = None  # For group [secondary]
    elements: tuple["SequenceDiagramElement", ...] = field(default_factory=tuple)
    else_blocks: tuple["ElseBlock", ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ElseBlock:
    """An else branch within an alt or par block."""

    label: LabelLike | None = None
    elements: tuple["SequenceDiagramElement", ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Box:
    """A box grouping participants together visually."""

    name: str | None = None
    color: ColorLike | None = None
    participants: tuple[Participant, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class SequenceNote:
    """A note in a sequence diagram.

    Sequence diagrams have specialized note positioning relative to participants.
    """

    content: LabelLike
    position: Literal["left", "right", "over"] = "right"
    participants: tuple[str, ...] = field(default_factory=tuple)  # For "over" - participant refs
    shape: NoteShape = "note"
    across: bool = False  # note across: spans all participants
    aligned: bool = False  # / note: aligned with previous


@dataclass(frozen=True)
class Reference:
    """A reference to another diagram.

    Rendered as: ref over Alice, Bob : See other diagram
    """

    participants: tuple[str, ...]  # Participant references
    label: LabelLike


@dataclass(frozen=True)
class Divider:
    """A divider line with title.

    Rendered as: == Title ==
    """

    title: str


@dataclass(frozen=True)
class Delay:
    """A delay indicator.

    Rendered as: ... or ...message...
    """

    message: str | None = None


@dataclass(frozen=True)
class Space:
    """Vertical spacing.

    Rendered as: ||| or ||N||
    """

    pixels: int | None = None  # None means default spacing


@dataclass(frozen=True)
class Autonumber:
    """Autonumber control.

    Rendered as: autonumber [start] [increment] [format]
    """

    action: Literal["start", "stop", "resume"] = "start"
    start: int | None = None
    increment: int | None = None
    format: str | None = None  # e.g., "<b>[000]"


@dataclass(frozen=True)
class SequenceDiagram:
    """Complete sequence diagram."""

    elements: tuple["SequenceDiagramElement", ...] = field(default_factory=tuple)
    title: str | None = None
    # Participants declared at top (for ordering)
    participants: tuple[Participant, ...] = field(default_factory=tuple)
    # Boxes containing participants
    boxes: tuple[Box, ...] = field(default_factory=tuple)
    # Diagram-wide settings
    autonumber: Autonumber | None = None
    hide_unlinked: bool = False  # hide unlinked participants


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
