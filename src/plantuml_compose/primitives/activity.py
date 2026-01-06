"""Activity diagram primitives.

All types are frozen dataclasses - immutable data with no behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, TypeAlias

from .common import (
    ColorLike,
    Direction,
    Label,
    LabelLike,
    LineStyleLike,
    Note,
)


# SDL shape types for actions
ActionShape = Literal[
    "default",  # :action;
    "start_end",  # :action|
    "receive",  # :action<
    "send",  # :action>
    "slant",  # :action/
    "document",  # :action]
    "database",  # :action}
]

# Arrow styles
ArrowStyle = Literal["solid", "dashed", "dotted", "hidden"]


@dataclass(frozen=True)
class Start:
    """Start node.

    Rendered as: start
    """

    pass


@dataclass(frozen=True)
class Stop:
    """Stop node (filled circle).

    Rendered as: stop
    """

    pass


@dataclass(frozen=True)
class End:
    """End node (circle with X).

    Rendered as: end
    """

    pass


@dataclass(frozen=True)
class Action:
    """An action in an activity diagram.

    Rendered as: :Action text;
    """

    label: LabelLike
    shape: ActionShape = "default"
    color: ColorLike | None = None  # Background color


@dataclass(frozen=True)
class Arrow:
    """Arrow with optional label and styling.

    Rendered as: -> or -[style]->
    """

    label: LabelLike | None = None
    color: ColorLike | None = None
    style: ArrowStyle = "solid"


@dataclass(frozen=True)
class If:
    """Conditional branching.

    Rendered as:
    if (condition?) then (yes)
      ...
    elseif (other?) then (yes)
      ...
    else (no)
      ...
    endif
    """

    condition: str
    then_label: str | None = None  # Label for "then" branch (e.g., "yes")
    then_elements: tuple["ActivityElement", ...] = field(default_factory=tuple)
    elseif_branches: tuple["ElseIfBranch", ...] = field(default_factory=tuple)
    else_label: str | None = None  # Label for "else" branch (e.g., "no")
    else_elements: tuple["ActivityElement", ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ElseIfBranch:
    """An elseif branch within an If."""

    condition: str
    then_label: str | None = None
    elements: tuple["ActivityElement", ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Switch:
    """Switch/case statement.

    Rendered as:
    switch (test?)
    case (A)
      ...
    case (B)
      ...
    endswitch
    """

    condition: str
    cases: tuple["Case", ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Case:
    """A case within a Switch."""

    label: str
    elements: tuple["ActivityElement", ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class While:
    """While loop.

    Rendered as:
    while (condition?) is (yes)
      ...
    endwhile (no)
    """

    condition: str
    is_label: str | None = None  # "is (yes)"
    elements: tuple["ActivityElement", ...] = field(default_factory=tuple)
    endwhile_label: str | None = None  # "endwhile (no)"


@dataclass(frozen=True)
class Repeat:
    """Repeat-while loop.

    Rendered as:
    repeat :start label;
      ...
    backward :back action;
    repeat while (condition?) is (yes) not (no)
    """

    elements: tuple["ActivityElement", ...] = field(default_factory=tuple)
    condition: str | None = None  # None means infinite
    start_label: str | None = None  # "repeat :label;"
    backward_action: str | None = None  # "backward :action;"
    is_label: str | None = None  # "is (yes)"
    not_label: str | None = None  # "not (no)"


@dataclass(frozen=True)
class Break:
    """Break out of loop.

    Rendered as: break
    """

    pass


@dataclass(frozen=True)
class Fork:
    """Fork into parallel branches.

    Rendered as:
    fork
      ...
    fork again
      ...
    end fork
    """

    branches: tuple[tuple["ActivityElement", ...], ...] = field(default_factory=tuple)
    end_style: Literal["fork", "merge", "or", "and"] = "fork"


@dataclass(frozen=True)
class Split:
    """Split into branches (no synchronization bar).

    Rendered as:
    split
      ...
    split again
      ...
    end split
    """

    branches: tuple[tuple["ActivityElement", ...], ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Kill:
    """Kill terminator (X symbol).

    Rendered as: kill
    """

    pass


@dataclass(frozen=True)
class Detach:
    """Detach from flow.

    Rendered as: detach
    """

    pass


@dataclass(frozen=True)
class Connector:
    """Connector for goto-like jumps.

    Rendered as: (A)
    """

    name: str


@dataclass(frozen=True)
class Goto:
    """Goto label (experimental).

    Rendered as: goto labelName
    """

    label: str


@dataclass(frozen=True)
class Label:
    """Label for goto (experimental).

    Rendered as: label labelName
    """

    name: str


@dataclass(frozen=True)
class Swimlane:
    """Swimlane (vertical partition).

    Rendered as: |Lane Name|
    or: |#color|Lane Name|
    """

    name: str
    color: ColorLike | None = None


@dataclass(frozen=True)
class Partition:
    """Partition (grouping with border).

    Rendered as:
    partition "Name" {
      ...
    }
    """

    name: str
    elements: tuple["ActivityElement", ...] = field(default_factory=tuple)
    color: ColorLike | None = None


@dataclass(frozen=True)
class Group:
    """Group (lighter grouping).

    Rendered as:
    group Name
      ...
    end group
    """

    name: str
    elements: tuple["ActivityElement", ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ActivityNote:
    """A note in an activity diagram."""

    content: LabelLike
    position: Literal["left", "right"] = "right"
    floating: bool = False


@dataclass(frozen=True)
class ActivityDiagram:
    """Complete activity diagram."""

    elements: tuple["ActivityElement", ...] = field(default_factory=tuple)
    title: str | None = None


# Type alias for elements that can appear in an activity diagram
ActivityElement: TypeAlias = (
    Start
    | Stop
    | End
    | Action
    | Arrow
    | If
    | Switch
    | While
    | Repeat
    | Break
    | Fork
    | Split
    | Kill
    | Detach
    | Connector
    | Goto
    | Label
    | Swimlane
    | Partition
    | Group
    | ActivityNote
    | Note
)
