"""State diagram primitives.

All types are frozen dataclasses - immutable data with no behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

from .common import Direction, Label, LineStyle, Note, RegionSeparator, StateDiagramStyle, Style

if TYPE_CHECKING:
    from typing import Union

    # Forward reference for recursive types
    StateDiagramElement = Union[
        "StateNode",
        "PseudoState",
        "Transition",
        "CompositeState",
        "ConcurrentState",
        Note,
    ]


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


@dataclass(frozen=True)
class StateNode:
    """A state in a state diagram."""

    name: str
    alias: str | None = None
    description: Label | None = None
    style: Style | None = None
    note: Note | None = None

    @property
    def ref(self) -> str:
        """Reference name for use in transitions."""
        if self.alias:
            return self.alias
        # Replace spaces with underscores for PlantUML compatibility
        return self.name.replace(" ", "_")


@dataclass(frozen=True)
class PseudoState:
    """A pseudo-state (initial, final, choice, fork, join, history, etc.)."""

    kind: PseudoStateKind
    name: str | None = None  # For fork/join/choice that need identifiers
    style: Style | None = None


@dataclass(frozen=True)
class Transition:
    """A transition between states."""

    source: str  # State name, alias, "initial", or "final"
    target: str  # State name, alias, "initial", or "final"
    label: Label | None = None
    trigger: str | None = None  # Event name
    guard: str | None = None  # Condition in [brackets]
    effect: str | None = None  # Action after /
    style: LineStyle | None = None
    direction: Direction | None = None
    note: Label | None = None  # Note attached to the transition (note on link)


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
    style: Style | None = None
    note: Note | None = None

    @property
    def ref(self) -> str:
        """Reference name for use in transitions."""
        if self.alias:
            return self.alias
        return self.name.replace(" ", "_")


@dataclass(frozen=True)
class ConcurrentState:
    """A state with parallel regions (orthogonal regions)."""

    name: str
    alias: str | None = None
    regions: tuple[Region, ...] = field(default_factory=tuple)
    style: Style | None = None
    note: Note | None = None
    separator: RegionSeparator = RegionSeparator.HORIZONTAL

    @property
    def ref(self) -> str:
        """Reference name for use in transitions."""
        if self.alias:
            return self.alias
        return self.name.replace(" ", "_")


@dataclass(frozen=True)
class StateDiagram:
    """Complete state diagram."""

    elements: tuple["StateDiagramElement", ...] = field(default_factory=tuple)
    title: str | None = None
    hide_empty_description: bool = False
    style: StateDiagramStyle | None = None


# Re-export for type hints
StateDiagramElement = (
    StateNode | PseudoState | Transition | CompositeState | ConcurrentState | Note
)
