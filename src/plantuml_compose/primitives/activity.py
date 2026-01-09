"""Activity diagram primitives.

Activity diagrams show the flow of actions and decisions in a process. They're
essentially flowcharts with UML notation, useful for documenting:

- Business processes and workflows
- Algorithm logic and decision trees
- Use case flows
- Multi-threaded or parallel processes

Key concepts:
    Action:     A single step or task (rounded rectangle)
    Decision:   A branch point with conditions (diamond via if/switch)
    Fork/Join:  Parallel execution paths (horizontal bars)
    Swimlane:   Vertical partition showing responsibility
    Start/Stop: Entry and exit points (circles)

All types are frozen dataclasses - immutable data with no behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, TypeAlias

from .common import (
    ColorLike,
    Direction,
    Footer,
    Header,
    Label,
    LabelLike,
    Legend,
    LineStyle,
    Note,
    Scale,
    Style,
)


# SDL shape types for actions - controls the visual shape
ActionShape = Literal[
    "default",    # :action;  Rounded rectangle (standard)
    "start_end",  # :action|  Stadium/pill shape
    "receive",    # :action<  Left-pointing flag (receive event)
    "send",       # :action>  Right-pointing flag (send event)
    "slant",      # :action/  Slanted parallelogram (data flow)
    "document",   # :action]  Document shape (wavy bottom)
    "database",   # :action}  Cylinder shape (database operation)
]

# Arrow line styles
ArrowStyle = Literal["solid", "dashed", "dotted", "hidden"]


@dataclass(frozen=True)
class Start:
    """The starting point of an activity flow.

    Rendered as a filled black circle. Every activity diagram should
    have exactly one start node where execution begins.
    """

    pass


@dataclass(frozen=True)
class Stop:
    """A normal termination point (filled circle).

    Indicates successful completion of the activity. Use Stop when the
    process ends normally. A diagram can have multiple stop nodes.
    """

    pass


@dataclass(frozen=True)
class End:
    """A flow termination point (circle with X).

    Similar to Stop but typically indicates an abnormal or alternative
    ending, such as cancellation or error termination.
    """

    pass


@dataclass(frozen=True)
class Action:
    """A single step or task in the activity flow.

    Actions are the basic building blocks, representing work being done.
    Each action has a label describing the task.

        label: Description of the action
        shape: Visual shape (affects meaning - see ActionShape)
        style: Visual style (background, line, text_color)
    """

    label: LabelLike
    shape: ActionShape = "default"
    style: Style | None = None


@dataclass(frozen=True)
class Arrow:
    """A flow connector between activities.

    Arrows show the direction of flow. They can have labels (for
    conditions or descriptions) and styling.

        label:      Text on the arrow
        pattern:    Line pattern ("solid", "dashed", "dotted", "hidden")
        line_style: Visual styling (color, thickness, bold)
        plain:      If True, removes arrow decoration
    """

    label: LabelLike | None = None
    pattern: ArrowStyle = "solid"
    line_style: LineStyle | None = None
    plain: bool = False  # Removes arrow decoration


@dataclass(frozen=True)
class If:
    """Conditional branching (if/elseif/else).

    Creates a decision diamond that splits the flow based on conditions.
    Each branch contains its own sequence of actions.

        condition:       The test expression (shown in diamond)
        then_label:      Label for the "then" path (e.g., "yes")
        then_elements:   Actions when condition is true
        elseif_branches: Additional conditional branches
        else_label:      Label for the "else" path (e.g., "no")
        else_elements:   Actions when all conditions are false
    """

    condition: str
    then_label: str | None = None  # Label for "then" branch (e.g., "yes")
    then_elements: tuple["ActivityElement", ...] = field(default_factory=tuple)
    elseif_branches: tuple["ElseIfBranch", ...] = field(default_factory=tuple)
    else_label: str | None = None  # Label for "else" branch (e.g., "no")
    else_elements: tuple["ActivityElement", ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ElseIfBranch:
    """An additional conditional branch within an If block.

    Each elseif tests another condition if the previous ones were false.
    """

    condition: str
    then_label: str | None = None
    elements: tuple["ActivityElement", ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Switch:
    """Multi-way branching based on a value (switch/case).

    Unlike If (which tests conditions), Switch compares a value against
    multiple options. Useful for menu selections or state-based logic.

        condition: The value being tested
        cases:     The possible values and their actions
    """

    condition: str
    cases: tuple["Case", ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Case:
    """A single case within a Switch block.

    Represents one possible value and the actions to take when matched.
    """

    label: str
    elements: tuple["ActivityElement", ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class While:
    """Pre-test loop (while condition is true, repeat).

    The condition is checked before each iteration. If false initially,
    the body never executes.

        condition:      Loop test expression
        is_label:       Label for continuing (e.g., "yes")
        elements:       Loop body actions
        endwhile_label: Label for exiting (e.g., "no")
    """

    condition: str
    is_label: str | None = None  # "is (yes)"
    elements: tuple["ActivityElement", ...] = field(default_factory=tuple)
    endwhile_label: str | None = None  # "endwhile (no)"


@dataclass(frozen=True)
class Repeat:
    """Post-test loop (repeat until condition is false).

    The body executes at least once before the condition is checked.
    Supports a backward action that runs before repeating.

        elements:        Loop body actions
        condition:       Exit test (None = infinite loop)
        start_label:     Label at loop start
        backward_action: Action before repeating
        is_label:        Label for repeating
        not_label:       Label for exiting
    """

    elements: tuple["ActivityElement", ...] = field(default_factory=tuple)
    condition: str | None = None  # None means infinite
    start_label: str | None = None  # "repeat :label;"
    backward_action: str | None = None  # "backward :action;"
    is_label: str | None = None  # "is (yes)"
    not_label: str | None = None  # "not (no)"


@dataclass(frozen=True)
class Break:
    """Exit from the enclosing loop.

    Immediately terminates the current While or Repeat loop and
    continues with the flow after the loop.
    """

    pass


@dataclass(frozen=True)
class Fork:
    """Parallel execution (fork/join with synchronization bars).

    Splits the flow into parallel branches that execute simultaneously.
    All branches must complete before the flow continues (join).

        branches:  Tuple of branch contents (each branch is a tuple of elements)
        end_style: How branches merge:
                   "fork"  - All must complete (AND join)
                   "merge" - First to complete continues
                   "or"    - Any subset can complete
                   "and"   - Explicit AND join
    """

    branches: tuple[tuple["ActivityElement", ...], ...] = field(default_factory=tuple)
    end_style: Literal["fork", "merge", "or", "and"] = "fork"


@dataclass(frozen=True)
class Split:
    """Branching without synchronization bars.

    Similar to Fork but without the visual synchronization bars.
    Use when showing diverging paths that don't need explicit join semantics.
    """

    branches: tuple[tuple["ActivityElement", ...], ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Kill:
    """Forced termination (X symbol).

    Abruptly ends the flow, typically indicating an error or abort
    condition. Different from Stop which indicates normal completion.
    """

    pass


@dataclass(frozen=True)
class Detach:
    """Detach from the current flow.

    The detached path continues independently without affecting the
    main flow. Useful for background processes or fire-and-forget actions.
    """

    pass


@dataclass(frozen=True)
class Connector:
    """A named connector point for jumps.

    Creates a reference point that can be targeted by Goto or used
    to show flow connections between distant parts of the diagram.
    Rendered as a circle with the name inside.
    """

    name: str


@dataclass(frozen=True)
class Goto:
    """Jump to a labeled point (experimental PlantUML feature).

    Transfers flow to the specified label. Use sparingly as it can
    make diagrams harder to follow.
    """

    label: str


@dataclass(frozen=True)
class GotoLabel:
    """A target label for Goto jumps (experimental).

    Defines a named point in the flow that can be the target of
    a Goto instruction.
    """

    name: str


@dataclass(frozen=True)
class Swimlane:
    """A vertical partition showing responsibility or actor.

    Swimlanes divide the diagram into columns, each representing
    a different role, system, or department. Actions placed after
    a swimlane declaration appear in that lane.

        name:  Lane label (shown at top)
        color: Lane background color
    """

    name: str
    color: ColorLike | None = None


@dataclass(frozen=True)
class Partition:
    """A bordered region grouping related activities.

    Partitions draw a box around a set of activities to show they
    belong together, with a title in the border.

        name:     Partition label
        elements: Activities inside the partition
        color:    Background color
    """

    name: str
    elements: tuple["ActivityElement", ...] = field(default_factory=tuple)
    color: ColorLike | None = None


@dataclass(frozen=True)
class Group:
    """A lightweight grouping of activities.

    Similar to Partition but with less visual weight. Groups
    activities without a strong border.
    """

    name: str
    elements: tuple["ActivityElement", ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ActivityNote:
    """A note annotation in an activity diagram.

        content:  Note text (can include Creole markup)
        position: "left" or "right" of the flow
        floating: If True, not attached to specific element
    """

    content: LabelLike
    position: Literal["left", "right"] = "right"
    floating: bool = False


@dataclass(frozen=True)
class ActivityDiagram:
    """A complete activity diagram ready for rendering.

    Contains all actions, decisions, and control flow elements.
    Usually created via the activity_diagram() builder rather than directly.

        elements: All diagram elements in flow order
        title:    Optional diagram title
    """

    elements: tuple["ActivityElement", ...] = field(default_factory=tuple)
    title: str | None = None
    caption: str | None = None
    header: Header | None = None
    footer: Footer | None = None
    legend: Legend | None = None
    scale: Scale | None = None


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
    | GotoLabel
    | Swimlane
    | Partition
    | Group
    | ActivityNote
    | Note
)
