"""PlantUML Compose - Type-safe PlantUML diagram generation in Python.

This library provides a Pythonic API for creating PlantUML diagrams with
full type safety. Instead of writing PlantUML text syntax directly, you
use Python composers that validate your diagram structure and generate
correct PlantUML output.

Supported diagram types:
    state_diagram:      State machines and lifecycles
    sequence_diagram:   Message flows between participants
    class_diagram:      Class structures and relationships
    component_diagram:  System architecture and dependencies
    deployment_diagram: Infrastructure and deployment topology
    usecase_diagram:    Requirements and user interactions
    object_diagram:     Instance snapshots with concrete values
    mindmap_diagram:    Hierarchical mind maps
    wbs_diagram:        Work breakdown structures
    gantt_diagram:      Gantt charts and project schedules
    timing_diagram:     Timing diagrams
    network_diagram:    Network architecture diagrams
    salt_diagram:       Salt wireframe UI diagrams
    json_diagram:       JSON data visualization
    yaml_diagram:       YAML data visualization

Quick Start:
    from plantuml_compose import state_diagram, render

    d = state_diagram(title="Traffic Light")
    el = d.elements
    t = d.transitions

    red = el.state("Red")
    yellow = el.state("Yellow")
    green = el.state("Green")
    d.add(red, yellow, green)

    d.connect(
        t.transition("[*]", red),
        t.transition(red, green, label="timer"),
        t.transition(green, yellow, label="timer"),
        t.transition(yellow, red, label="timer"),
    )

    with open("diagram.puml", "w") as f:
        f.write(render(d))

The library is organized in three layers:
    Composers:   User-facing API with factory functions (state_diagram, etc.)
    Primitives:  Immutable data classes representing diagram elements
    Renderers:   Pure functions that convert primitives to PlantUML text

For styling, use Color, Gradient, LineStyle, and Style classes. Most
APIs accept either the typed objects or convenient string shortcuts
(e.g., "red" instead of Color.named("red")).
"""

from .composers import (
    activity_diagram,
    class_diagram,
    component_diagram,
    deployment_diagram,
    gantt_diagram,
    json_diagram,
    mindmap_diagram,
    network_diagram,
    object_diagram,
    salt_diagram,
    sequence_diagram,
    state_diagram,
    timing_diagram,
    usecase_diagram,
    wbs_diagram,
    yaml_diagram,
)
from .composers.base import EntityRef
from .primitives import (
    ArrowHead,
    ArrowHeadLike,
    Color,
    ColorLike,
    CompositeState,
    ConcurrentState,
    DiagramArrowStyle,
    DiagramArrowStyleLike,
    Direction,
    ElementStyle,
    ElementStyleLike,
    EmbeddableContent,
    EmbeddedDiagram,
    ExternalTheme,
    FontStyle,
    Gradient,
    JsonDiagram,
    JsonDiagramStyle,
    JsonDiagramStyleLike,
    Label,
    LabelLike,
    LayoutDirection,
    LayoutEngine,
    LinePattern,
    LineStyle,
    LineType,
    LineStyleLike,
    MindMapDiagram,
    MindMapDiagramStyle,
    MindMapDiagramStyleLike,
    MindMapNode,
    NetworkDiagramStyle,
    NetworkDiagramStyleLike,
    Newpage,
    Note,
    WBSArrow,
    WBSDiagram,
    WBSDiagramStyle,
    WBSNode,
    GanttClosedDateRange,
    GanttColoredDate,
    GanttColoredDateRange,
    GanttDiagram,
    GanttDiagramStyle,
    GanttDiagramStyleLike,
    GanttTask,
    GanttMilestone,
    GanttDependency,
    GanttOpenDate,
    GanttResource,
    GanttResourceOff,
    GanttSeparator,
    GanttVerticalSeparator,
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
    # Timing diagram
    HiddenState,
    IntricatedState,
    TimeAnchor,
    TimingConstraint,
    TimingDiagram,
    TimingDiagramStyle,
    TimingDiagramStyleLike,
    TimingHighlight,
    TimingInitialState,
    TimingMessage,
    TimingNote,
    TimingParticipant,
    TimingScale,
    TimingStateChange,
    TimingStateOrder,
    TimingTicks,
    Transition,
    # Salt
    SaltDiagram,
    SaltWidget,
    YamlDiagram,
    YamlDiagramStyle,
    YamlDiagramStyleLike,
)
from .renderers import link, render, render_url

__all__ = [
    # Composers
    "activity_diagram",
    "class_diagram",
    "component_diagram",
    "deployment_diagram",
    "gantt_diagram",
    "json_diagram",
    "mindmap_diagram",
    "network_diagram",
    "object_diagram",
    "salt_diagram",
    "sequence_diagram",
    "state_diagram",
    "timing_diagram",
    "usecase_diagram",
    "wbs_diagram",
    "yaml_diagram",
    # Composer base
    "EntityRef",
    # Renderers
    "link",
    "render",
    "render_url",
    # Common primitives
    "ArrowHead",
    "ArrowHeadLike",
    "Color",
    "ColorLike",
    "DiagramArrowStyle",
    "DiagramArrowStyleLike",
    "Direction",
    "ElementStyle",
    "ElementStyleLike",
    "EmbeddableContent",
    "EmbeddedDiagram",
    "ExternalTheme",
    "FontStyle",
    "Gradient",
    "JsonDiagramStyle",
    "JsonDiagramStyleLike",
    "Label",
    "LabelLike",
    "LayoutDirection",
    "LayoutEngine",
    "LinePattern",
    "LineStyle",
    "LineStyleLike",
    "LineType",
    "MindMapDiagram",
    "MindMapDiagramStyle",
    "MindMapDiagramStyleLike",
    "MindMapNode",
    "Newpage",
    "Note",
    "WBSArrow",
    "WBSDiagram",
    "WBSDiagramStyle",
    "WBSNode",
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
    "YamlDiagramStyle",
    "YamlDiagramStyleLike",
    # State primitives
    "CompositeState",
    "ConcurrentState",
    "PseudoState",
    "PseudoStateKind",
    "Region",
    "StateDiagram",
    "StateNode",
    "Transition",
    # JSON/YAML primitives
    "JsonDiagram",
    "YamlDiagram",
    # Gantt primitives
    "GanttClosedDateRange",
    "GanttColoredDate",
    "GanttColoredDateRange",
    "GanttDependency",
    "GanttDiagram",
    "GanttDiagramStyle",
    "GanttDiagramStyleLike",
    "GanttMilestone",
    "GanttOpenDate",
    "GanttResource",
    "GanttResourceOff",
    "GanttSeparator",
    "GanttTask",
    "GanttVerticalSeparator",
    # Network diagram
    "NetworkDiagramStyle",
    "NetworkDiagramStyleLike",
    # Timing diagram primitives
    "HiddenState",
    "IntricatedState",
    "TimeAnchor",
    "TimingConstraint",
    "TimingDiagram",
    "TimingDiagramStyle",
    "TimingDiagramStyleLike",
    "TimingHighlight",
    "TimingInitialState",
    "TimingMessage",
    "TimingNote",
    "TimingParticipant",
    "TimingScale",
    "TimingStateChange",
    "TimingStateOrder",
    "TimingTicks",
    # Salt
    "SaltDiagram",
    "SaltWidget",
]


def main() -> None:
    """CLI entry point."""
    print("Hello from plantuml-compose!")
