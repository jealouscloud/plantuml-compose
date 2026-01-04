"""PlantUML Compose - Type-safe PlantUML diagram generation.

Usage:
    from plantuml_compose import state_diagram, render

    with state_diagram(title="Traffic Light") as d:
        red = d.state("Red")
        yellow = d.state("Yellow")
        green = d.state("Green")

        d.arrow(d.start(), red)
        d.arrow(red, green, "timer")
        d.arrow(green, yellow, "timer")
        d.arrow(yellow, red, "timer")

    print(render(d.build()))
"""

from .builders import state_diagram
from .primitives import (
    Color,
    CompositeState,
    ConcurrentState,
    Direction,
    Gradient,
    Label,
    LinePattern,
    LineStyle,
    Note,
    NotePosition,
    PseudoState,
    PseudoStateKind,
    Region,
    RegionSeparator,
    Spot,
    StateDiagram,
    StateNode,
    Stereotype,
    Style,
    Transition,
)
from .renderers import render

__all__ = [
    # Builders
    "state_diagram",
    # Renderers
    "render",
    # Common primitives
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
    # State primitives
    "CompositeState",
    "ConcurrentState",
    "PseudoState",
    "PseudoStateKind",
    "Region",
    "StateDiagram",
    "StateNode",
    "Transition",
]


def main() -> None:
    """CLI entry point."""
    print("Hello from plantuml-compose!")
