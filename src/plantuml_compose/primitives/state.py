"""State diagram primitives.

All types are frozen dataclasses - immutable data with no behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal, TypeAlias

from .common import (
    Direction,
    Label,
    LabelLike,
    LineStyle,
    LineStyleLike,
    Note,
    RegionSeparator,
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
    for char in "\"'`()[]{}:;,.<>!@#$%^&*+=|\\/?~":
        sanitized = sanitized.replace(char, "")
    return sanitized or "_"


class PseudoStateKind(Enum):
    """Pseudo-state types that affect rendering."""

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
    """A state in a state diagram."""

    name: str
    alias: str | None = None
    description: LabelLike | None = None
    style: StyleLike | None = None
    note: Note | None = None

    @property
    def _ref(self) -> str:
        """Internal: Reference name for use in transitions."""
        if self.alias:
            return self.alias
        # Replace spaces and double quotes for PlantUML compatibility
        return _sanitize_ref(self.name)


@dataclass(frozen=True)
class PseudoState:
    """A pseudo-state (initial, final, choice, fork, join, history, etc.)."""

    kind: PseudoStateKind
    name: str | None = None  # For fork/join/choice that need identifiers
    style: StyleLike | None = None


@dataclass(frozen=True)
class Transition:
    """A transition between states."""

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
    """A region within a concurrent state."""

    elements: tuple["StateDiagramElement", ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class CompositeState:
    """A state containing nested states."""

    name: str
    alias: str | None = None
    elements: tuple["StateDiagramElement", ...] = field(default_factory=tuple)
    style: StyleLike | None = None
    note: Note | None = None

    @property
    def _ref(self) -> str:
        """Internal: Reference name for use in transitions."""
        if self.alias:
            return self.alias
        return _sanitize_ref(self.name)


@dataclass(frozen=True)
class ConcurrentState:
    """A state with parallel regions (orthogonal regions)."""

    name: str
    alias: str | None = None
    regions: tuple[Region, ...] = field(default_factory=tuple)
    style: StyleLike | None = None
    note: Note | None = None
    separator: RegionSeparator = "horizontal"

    @property
    def _ref(self) -> str:
        """Internal: Reference name for use in transitions."""
        if self.alias:
            return self.alias
        return _sanitize_ref(self.name)


@dataclass(frozen=True)
class StateDiagram:
    """Complete state diagram."""

    elements: tuple["StateDiagramElement", ...] = field(default_factory=tuple)
    title: str | None = None
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
