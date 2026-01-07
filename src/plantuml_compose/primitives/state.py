"""State diagram primitives.

State diagrams (also called state machine diagrams) show how an object
transitions between different states in response to events. They're useful
for modeling:

- Lifecycle states (Created -> Active -> Archived)
- Workflow steps (Draft -> Review -> Published)
- Device modes (Off -> Standby -> Active)
- Connection states (Disconnected -> Connecting -> Connected)

Key concepts:
    State:      A condition or situation during an object's life
    Transition: A change from one state to another, triggered by an event
    Initial:    The starting point (filled circle: [*])
    Final:      The ending point (circle with dot inside: [*])
    Composite:  A state containing nested sub-states
    Concurrent: A state with parallel regions that execute simultaneously

All types are frozen dataclasses - immutable data with no behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal, TypeAlias

from .common import (
    Direction,
    Footer,
    Header,
    Label,
    LabelLike,
    Legend,
    LineStyle,
    LineStyleLike,
    Note,
    RegionSeparator,
    Scale,
    StateDiagramStyle,
    Style,
    StyleLike,
)


def _sanitize_ref(name: str) -> str:
    """Create a PlantUML-friendly identifier from a state name.

    Removes/replaces characters that are invalid in PlantUML identifiers:
    - Spaces become underscores
    - Quotes, apostrophes, and other special chars are removed
    """
    # Replace spaces with underscores
    sanitized = name.replace(" ", "_")
    # Remove characters that break PlantUML identifiers
    # Hyphen must be removed - PlantUML interprets it as arrow syntax
    for char in "\"'`()[]{}:;,.<>!@#$%^&*+=|\\/?~-":
        sanitized = sanitized.replace(char, "")
    return sanitized or "_"


class PseudoStateKind(Enum):
    """Types of pseudo-states in state diagrams.

    Pseudo-states are not true states but control points that affect
    how transitions flow through the diagram:

        INITIAL:     Starting point, shown as filled circle [*]
        FINAL:       Ending point, shown as bullseye [*]
        CHOICE:      Decision point, shown as diamond
        FORK:        Splits into parallel paths, shown as bar
        JOIN:        Merges parallel paths, shown as bar
        HISTORY:     Returns to previous state [H]
        DEEP_HISTORY: Returns to previous nested state [H*]

    Less common pseudo-states for specialized diagrams:
        ENTRY_POINT, EXIT_POINT: Named entry/exit for composite states
        INPUT_PIN, OUTPUT_PIN: Activity diagram connectors
        START, END: Alternative initial/final with <<start>>/<<end>>
    """

    INITIAL = "initial"  # [*] as source
    FINAL = "final"  # [*] as target
    CHOICE = "choice"  # Diamond
    FORK = "fork"  # Horizontal bar
    JOIN = "join"  # Horizontal bar
    HISTORY = "history"  # [H]
    DEEP_HISTORY = "deep_history"  # [H*]
    ENTRY_POINT = "entryPoint"
    EXIT_POINT = "exitPoint"
    INPUT_PIN = "inputPin"
    OUTPUT_PIN = "outputPin"
    SDL_RECEIVE = "sdlreceive"
    EXPANSION_INPUT = "expansionInput"
    EXPANSION_OUTPUT = "expansionOutput"
    START = "start"  # Explicit <<start>> stereotype
    END = "end"  # Explicit <<end>> stereotype


# Ergonomic string alternative to PseudoStateKind enum.
# We support both enum and string for convenience; kept in sync via test.
# fmt: off
PseudoStateKindStr = Literal[
    "initial", "final", "choice", "fork", "join", "history", "deep_history",
    "entryPoint", "exitPoint", "inputPin", "outputPin", "sdlreceive",
    "expansionInput", "expansionOutput", "start", "end",
]
# fmt: on
PseudoStateKindLike: TypeAlias = PseudoStateKind | PseudoStateKindStr


def coerce_pseudo_state_kind(value: PseudoStateKindLike) -> PseudoStateKind:
    """Convert a PseudoStateKindLike value to a PseudoStateKind enum."""
    if isinstance(value, PseudoStateKind):
        return value
    return PseudoStateKind(value)


@dataclass(frozen=True)
class StateNode:
    """A state in a state diagram.

    States represent conditions or situations during an object's life.
    Each state has a unique name and can include:

        name:        Display name (e.g., "Active", "Waiting for Input")
        alias:       Short identifier for transitions (auto-generated if omitted)
        description: Text shown inside the state box
        style:       Visual styling (background color, border, etc.)
        note:        Annotation attached to the state
    """

    name: str
    alias: str | None = None
    description: LabelLike | None = None
    style: StyleLike | None = None
    note: Note | None = None

    @property
    def _ref(self) -> str:
        """Internal identifier used when rendering transitions.

        Returns the alias if set, otherwise the name with spaces and special
        characters removed. You don't need this directly - just pass objects
        to flow(), transition(), etc. Exposed for debugging the PlantUML output.
        """
        if self.alias:
            return self.alias
        return _sanitize_ref(self.name)


@dataclass(frozen=True)
class PseudoState:
    """A pseudo-state (control point) in a state diagram.

    Unlike regular states, pseudo-states don't represent stable conditions.
    They're control points that affect how the system transitions:

        kind:  Type of pseudo-state (initial, final, choice, fork, etc.)
        name:  Optional identifier (needed for fork/join/choice references)
        style: Visual styling (limited support varies by pseudo-state type)
    """

    kind: PseudoStateKind
    name: str | None = None  # For fork/join/choice that need identifiers
    style: StyleLike | None = None


@dataclass(frozen=True)
class Transition:
    """A transition (arrow) between states.

    Transitions show how the system moves from one state to another.
    They can be labeled with:

        label:     Simple text on the arrow
        trigger:   The event that causes the transition (e.g., "buttonClick")
        guard:     Condition that must be true, shown in [brackets]
        effect:    Action performed during transition, shown after /

    Full UML transition syntax: trigger [guard] / effect

    Other properties:
        source:    Starting state (name, alias, or "initial")
        target:    Ending state (name, alias, or "final")
        style:     Arrow styling (color, line pattern, etc.)
        direction: Layout hint ("up", "down", "left", "right")
        note:      Annotation attached to the arrow
    """

    source: str  # State name, alias, "initial", or "final"
    target: str  # State name, alias, "initial", or "final"
    label: LabelLike | None = None
    trigger: str | None = None  # Event name
    guard: str | None = None  # Condition in [brackets]
    effect: str | None = None  # Action after /
    style: LineStyleLike | None = None
    direction: Direction | None = None
    note: LabelLike | None = (
        None  # Note attached to the transition (note on link)
    )


@dataclass(frozen=True)
class Region:
    """A region within a concurrent state.

    Regions are parallel sections of a concurrent state that execute
    simultaneously. Each region has its own set of states and transitions
    that operate independently.
    """

    elements: tuple["StateDiagramElement", ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class CompositeState:
    """A state containing nested sub-states.

    Composite states (also called "substates" or "nested states") allow
    hierarchical state machines. When entering a composite state, the
    system enters one of its nested states. Transitions can target either
    the composite state itself or specific nested states.

    Example: An "Active" state might contain "Idle", "Processing", and
    "Waiting" sub-states, with their own internal transitions.
    """

    name: str
    alias: str | None = None
    elements: tuple["StateDiagramElement", ...] = field(default_factory=tuple)
    style: StyleLike | None = None
    note: Note | None = None

    @property
    def _ref(self) -> str:
        """Internal identifier used when rendering transitions.

        Returns the alias if set, otherwise the name with spaces and special
        characters removed. You don't need this directly - just pass objects
        to flow(), transition(), etc. Exposed for debugging the PlantUML output.
        """
        if self.alias:
            return self.alias
        return _sanitize_ref(self.name)


@dataclass(frozen=True)
class ConcurrentState:
    """A state with parallel regions that execute simultaneously.

    Also called "orthogonal regions", concurrent states model situations
    where multiple independent aspects operate in parallel. Each region
    runs its own state machine independently.

    Example: A phone call might have concurrent regions for "Audio" (muted/
    unmuted) and "Video" (on/off), operating independently.

    The separator controls the visual layout:
        "horizontal": Regions stacked vertically (separated by --)
        "vertical":   Regions arranged side-by-side (separated by ||)
    """

    name: str
    alias: str | None = None
    regions: tuple[Region, ...] = field(default_factory=tuple)
    style: StyleLike | None = None
    note: Note | None = None
    separator: RegionSeparator = "horizontal"

    @property
    def _ref(self) -> str:
        """Internal identifier used when rendering transitions.

        Returns the alias if set, otherwise the name with spaces and special
        characters removed. You don't need this directly - just pass objects
        to flow(), transition(), etc. Exposed for debugging the PlantUML output.
        """
        if self.alias:
            return self.alias
        return _sanitize_ref(self.name)


@dataclass(frozen=True)
class StateDiagram:
    """A complete state diagram ready for rendering.

    Contains all states, transitions, and diagram-level settings.
    Usually created via the state_diagram() builder rather than directly.

        elements:               All diagram elements (states, transitions, notes)
        title:                  Optional diagram title
        hide_empty_description: If True, hides the separator line in empty states
        style:                  Diagram-wide styling (colors, fonts, etc.)
    """

    elements: tuple["StateDiagramElement", ...] = field(default_factory=tuple)
    title: str | None = None
    caption: str | None = None
    header: Header | None = None
    footer: Footer | None = None
    legend: Legend | None = None
    scale: Scale | None = None
    hide_empty_description: bool = False
    style: StateDiagramStyle | None = None


# Type alias for elements that can appear in a state diagram
StateDiagramElement: TypeAlias = (
    StateNode
    | PseudoState
    | Transition
    | CompositeState
    | ConcurrentState
    | Note
)
