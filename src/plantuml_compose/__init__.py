"""PlantUML Compose - Type-safe PlantUML diagram generation in Python.

This library provides a Pythonic API for creating PlantUML diagrams with
full type safety. Instead of writing PlantUML text syntax directly, you
use Python builders that validate your diagram structure and generate
correct PlantUML output.

Supported diagram types:
    state_diagram:      State machines and lifecycles
    sequence_diagram:   Message flows between participants
    class_diagram:      Class structures and relationships
    activity_diagram:   Flowcharts and process flows
    component_diagram:  System architecture and dependencies
    deployment_diagram: Infrastructure and deployment topology
    usecase_diagram:    Requirements and user interactions
    object_diagram:     Instance snapshots with concrete values

Quick Start:
    from plantuml_compose import state_diagram

    # Create a diagram using the builder context manager
    with state_diagram(title="Traffic Light") as d:
        red = d.state("Red")
        yellow = d.state("Yellow")
        green = d.state("Green")

        d.initial(red)
        d.transition(red, green, label="timer")
        d.transition(green, yellow, label="timer")
        d.transition(yellow, red, label="timer")

    # Render to PlantUML text and save to file
    with open("diagram.puml", "w") as f:
        f.write(d.render())

The library is organized in three layers:
    Builders:    User-facing API with context managers (state_diagram, etc.)
    Primitives:  Immutable data classes representing diagram elements
    Renderers:   Pure functions that convert primitives to PlantUML text

For styling, use Color, Gradient, LineStyle, and Style classes. Most
APIs accept either the typed objects or convenient string shortcuts
(e.g., "red" instead of Color.named("red")).
"""

from .builders import (
    activity_diagram,
    class_diagram,
    component_diagram,
    deployment_diagram,
    object_diagram,
    sequence_diagram,
    state_diagram,
    usecase_diagram,
)
from .primitives import (
    Color,
    ColorLike,
    CompositeState,
    ConcurrentState,
    DiagramArrowStyle,
    DiagramArrowStyleLike,
    Direction,
    ElementStyle,
    ElementStyleLike,
    ExternalTheme,
    FontStyle,
    Gradient,
    Label,
    LabelLike,
    LinePattern,
    LineStyle,
    LineStyleLike,
    Note,
    NotePosition,
    PlantUMLBuiltinTheme,
    PseudoState,
    PseudoStateKind,
    Region,
    RegionSeparator,
    Spot,
    StateDiagram,
    StateDiagramStyle,
    StateDiagramStyleLike,
    StateNode,
    Stereotype,
    Style,
    StyleLike,
    ThemeLike,
    Transition,
)
from .renderers import link, render

__all__ = [
    # Builders
    "activity_diagram",
    "class_diagram",
    "component_diagram",
    "deployment_diagram",
    "object_diagram",
    "sequence_diagram",
    "state_diagram",
    "usecase_diagram",
    # Renderers
    "link",
    "render",
    # Common primitives
    "Color",
    "ColorLike",
    "DiagramArrowStyle",
    "DiagramArrowStyleLike",
    "Direction",
    "ElementStyle",
    "ElementStyleLike",
    "ExternalTheme",
    "FontStyle",
    "Gradient",
    "Label",
    "LabelLike",
    "LinePattern",
    "LineStyle",
    "LineStyleLike",
    "Note",
    "NotePosition",
    "PlantUMLBuiltinTheme",
    "RegionSeparator",
    "Spot",
    "StateDiagramStyle",
    "StateDiagramStyleLike",
    "Stereotype",
    "Style",
    "StyleLike",
    "ThemeLike",
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
