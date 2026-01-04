"""Primitive types for PlantUML diagrams.

All types are frozen dataclasses - immutable data with no behavior.
"""

from .common import (
    Color,
    Direction,
    Gradient,
    Label,
    LinePattern,
    LineStyle,
    Note,
    NotePosition,
    RegionSeparator,
    Spot,
    Stereotype,
    Style,
)
from .state import (
    CompositeState,
    ConcurrentState,
    PseudoState,
    PseudoStateKind,
    Region,
    StateDiagram,
    StateDiagramElement,
    StateNode,
    Transition,
)

__all__ = [
    # Common
    "Color",
    "Direction",
    "Gradient",
    "Label",
    "LinePattern",
    "LineStyle",
    "Note",
    "NotePosition",
    "RegionSeparator",
    "Spot",
    "Stereotype",
    "Style",
    # State
    "CompositeState",
    "ConcurrentState",
    "PseudoState",
    "PseudoStateKind",
    "Region",
    "StateDiagram",
    "StateDiagramElement",
    "StateNode",
    "Transition",
]
