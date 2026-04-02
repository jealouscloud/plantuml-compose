"""Diagram-specific style primitives.

Frozen dataclasses and TypedDicts for per-diagram-type styling (state,
component, sequence, activity, class, object, JSON, YAML, mindmap,
network, timing, gantt).  These were split out of common.py to keep
that module focused on the shared / base types.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias, TypedDict

from .common import (
    ColorLike,
    DiagramArrowStyle,
    DiagramArrowStyleLike,
    ElementStyle,
    ElementStyleLike,
    Gradient,
    _validate_style_dict_keys,
    coerce_color,
    coerce_diagram_arrow_style,
    coerce_element_style,
    _coerce_color_or_gradient,
)


# ---------------------------------------------------------------------------
# Shared coercion helpers (stereotypes / depths)
# ---------------------------------------------------------------------------


def _coerce_stereotypes(
    value: dict[str, ElementStyleLike] | None,
) -> dict[str, ElementStyle] | None:
    """Coerce a stereotypes dict from mixed types to ElementStyle objects."""
    if value is None:
        return None
    return {k: coerce_element_style(v) for k, v in value.items()}


def _coerce_depths(
    value: dict[int, ElementStyleLike] | None,
) -> dict[int, ElementStyle] | None:
    """Coerce a depths dict from mixed types to ElementStyle objects."""
    if value is None:
        return None
    return {k: coerce_element_style(v) for k, v in value.items()}


# ---------------------------------------------------------------------------
# State Diagram Styling
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class StateDiagramStyle:
    """Diagram-wide styling for state diagrams.

    This generates a PlantUML <style> block that sets default appearance
    for all elements in the diagram. Individual elements can still override
    these defaults with inline styles.

    Root-level properties apply to the diagram background and default fonts.
    Element-specific properties (state, arrow, note, title) let you style
    each element type independently.

    Example:
        with state_diagram(
            style=StateDiagramStyle(
                background="white",
                font_name="Arial",
                state=ElementStyle(
                    background="#E3F2FD",
                    line_color="#1976D2",
                ),
                arrow=DiagramArrowStyle(
                    line_color="#757575",
                ),
            )
        ) as d:
            ...

    This generates a <style> block in the PlantUML output that themes
    all states with blue backgrounds and gray arrows.
    """

    # Root-level properties
    background: ColorLike | Gradient | None = None
    font_name: str | None = None
    font_size: int | None = None
    font_color: ColorLike | None = None

    # Element-specific styles
    state: ElementStyle | None = None
    arrow: DiagramArrowStyle | None = None
    note: ElementStyle | None = None
    title: ElementStyle | None = None

    # Selector-based styles
    stereotypes: dict[str, ElementStyle] | None = None
    """Style elements by stereotype name.

    Keys are stereotype names (without << >>).
    Values are ElementStyle objects applied to elements with that stereotype.
    """


class StateDiagramStyleDict(TypedDict, total=False):
    """Dict form of StateDiagramStyle — passed as diagram_style= to state_diagram().

    Top-level keys set diagram background and default fonts.
    Element keys accept ElementStyleDict (see ElementStyleDict for all properties).

    Available keys:
        background:   Diagram background color
        font_name:    Default font family
        font_size:    Default font size
        font_color:   Default text color
        state:        Style for state boxes (ElementStyleDict)
        arrow:        Style for transitions (DiagramArrowStyleDict)
        note:         Style for notes (ElementStyleDict)
        title:        Style for the title (ElementStyleDict)
        stereotypes:  Style by stereotype name: {"name": ElementStyleDict}

    Example:
        state_diagram(diagram_style={
            "background": "white",
            "state": {"background": "#E3F2FD", "round_corner": 10, "padding": 8},
            "arrow": {"line_color": "gray", "font_size": 10},
            "note": {"background": "#FFF9C4"},
            "stereotypes": {
                "error": {"background": "#FFCDD2", "font_style": "bold"},
            },
        })
    """

    background: ColorLike | Gradient
    font_name: str
    font_size: int
    font_color: ColorLike
    state: ElementStyleLike
    arrow: DiagramArrowStyleLike
    note: ElementStyleLike
    title: ElementStyleLike
    stereotypes: dict[str, ElementStyleLike]


# Type alias for state diagram style arguments
StateDiagramStyleLike: TypeAlias = StateDiagramStyle | StateDiagramStyleDict

_STATE_DIAGRAM_STYLE_KEYS: frozenset[str] = frozenset({
    "background", "font_name", "font_size", "font_color",
    "state", "arrow", "note", "title", "stereotypes",
})


def coerce_state_diagram_style(
    value: StateDiagramStyleLike,
) -> StateDiagramStyle:
    """Convert a StateDiagramStyleLike value to a StateDiagramStyle object."""
    if isinstance(value, StateDiagramStyle):
        return value
    _validate_style_dict_keys(value, _STATE_DIAGRAM_STYLE_KEYS, "StateDiagramStyle")
    return StateDiagramStyle(
        background=_coerce_color_or_gradient(value.get("background")),
        font_name=value.get("font_name"),
        font_size=value.get("font_size"),
        font_color=coerce_color(value["font_color"])
        if "font_color" in value
        else None,
        state=coerce_element_style(value["state"])
        if "state" in value
        else None,
        arrow=coerce_diagram_arrow_style(value["arrow"])
        if "arrow" in value
        else None,
        note=coerce_element_style(value["note"]) if "note" in value else None,
        title=coerce_element_style(value["title"])
        if "title" in value
        else None,
        stereotypes=_coerce_stereotypes(value.get("stereotypes")),
    )


# ---------------------------------------------------------------------------
# Component Diagram Styling
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ComponentDiagramStyle:
    """Diagram-wide styling for component diagrams.

    This generates a PlantUML <style> block that sets default appearance
    for all elements in the diagram. Individual elements can still override
    these defaults with inline styles.

    Root-level properties apply to the diagram background and default fonts.
    Element-specific properties let you style each element type independently.

    Example:
        with component_diagram(
            diagram_style=ComponentDiagramStyle(
                background="white",
                font_name="Arial",
                component=ElementStyle(
                    background="#E3F2FD",
                    line_color="#1976D2",
                ),
                package=ElementStyle(background="#F5F5F5"),
                arrow=DiagramArrowStyle(
                    line_color="#757575",
                ),
            )
        ) as d:
            ...

    This generates a <style> block in the PlantUML output that themes
    all components with blue backgrounds, packages with gray backgrounds,
    and gray arrows.
    """

    # Root-level properties
    background: ColorLike | Gradient | None = None
    font_name: str | None = None
    font_size: int | None = None
    font_color: ColorLike | None = None

    # Element-specific styles
    component: ElementStyle | None = None
    interface: ElementStyle | None = None
    arrow: DiagramArrowStyle | None = None
    note: ElementStyle | None = None
    title: ElementStyle | None = None

    # Container-specific styles
    package: ElementStyle | None = None
    node: ElementStyle | None = None
    folder: ElementStyle | None = None
    frame: ElementStyle | None = None
    cloud: ElementStyle | None = None
    database: ElementStyle | None = None

    # Selector-based styles
    stereotypes: dict[str, ElementStyle] | None = None
    """Style elements by stereotype name.

    Keys are stereotype names (without << >>).
    Values are ElementStyle objects applied to elements with that stereotype.
    """


class ComponentDiagramStyleDict(TypedDict, total=False):
    """Dict form of ComponentDiagramStyle — passed as diagram_style= to component_diagram().

    Top-level keys set diagram background and default fonts.
    Element keys accept ElementStyleDict (see ElementStyleDict for all properties).

    Available keys:
        background:   Diagram background color
        font_name:    Default font family
        font_size:    Default font size
        font_color:   Default text color
        component:    Style for components (ElementStyleDict)
        interface:    Style for interfaces (ElementStyleDict)
        package:      Style for packages (ElementStyleDict)
        node:         Style for nodes (ElementStyleDict)
        folder:       Style for folders (ElementStyleDict)
        frame:        Style for frames (ElementStyleDict)
        cloud:        Style for clouds (ElementStyleDict)
        database:     Style for databases (ElementStyleDict)
        arrow:        Style for connections (DiagramArrowStyleDict)
        note:         Style for notes (ElementStyleDict)
        title:        Style for the title (ElementStyleDict)
        stereotypes:  Style by stereotype name: {"name": ElementStyleDict}

    Example:
        component_diagram(diagram_style={
            "background": "white",
            "component": {"background": "#E3F2FD", "line_color": "#1976D2"},
            "package": {"background": "#F5F5F5"},
            "arrow": {"line_color": "#757575"},
            "stereotypes": {
                "service": {"background": "#C8E6C9", "font_style": "bold"},
            },
        })
    """

    background: ColorLike | Gradient
    font_name: str
    font_size: int
    font_color: ColorLike
    component: ElementStyleLike
    interface: ElementStyleLike
    arrow: DiagramArrowStyleLike
    note: ElementStyleLike
    title: ElementStyleLike
    package: ElementStyleLike
    node: ElementStyleLike
    folder: ElementStyleLike
    frame: ElementStyleLike
    cloud: ElementStyleLike
    database: ElementStyleLike
    stereotypes: dict[str, ElementStyleLike]


# Type alias for component diagram style arguments
ComponentDiagramStyleLike: TypeAlias = (
    ComponentDiagramStyle | ComponentDiagramStyleDict
)

_COMPONENT_DIAGRAM_STYLE_KEYS: frozenset[str] = frozenset({
    "background", "font_name", "font_size", "font_color",
    "component", "interface", "arrow", "note", "title",
    "package", "node", "folder", "frame", "cloud", "database",
    "stereotypes",
})


def coerce_component_diagram_style(
    value: ComponentDiagramStyleLike,
) -> ComponentDiagramStyle:
    """Convert a ComponentDiagramStyleLike value to a ComponentDiagramStyle object."""
    if isinstance(value, ComponentDiagramStyle):
        return value
    _validate_style_dict_keys(
        value, _COMPONENT_DIAGRAM_STYLE_KEYS, "ComponentDiagramStyle"
    )
    return ComponentDiagramStyle(
        background=_coerce_color_or_gradient(value.get("background")),
        font_name=value.get("font_name"),
        font_size=value.get("font_size"),
        font_color=coerce_color(value["font_color"])
        if "font_color" in value
        else None,
        component=coerce_element_style(value["component"])
        if "component" in value
        else None,
        interface=coerce_element_style(value["interface"])
        if "interface" in value
        else None,
        arrow=coerce_diagram_arrow_style(value["arrow"])
        if "arrow" in value
        else None,
        note=coerce_element_style(value["note"]) if "note" in value else None,
        title=coerce_element_style(value["title"])
        if "title" in value
        else None,
        package=coerce_element_style(value["package"])
        if "package" in value
        else None,
        node=coerce_element_style(value["node"]) if "node" in value else None,
        folder=coerce_element_style(value["folder"])
        if "folder" in value
        else None,
        frame=coerce_element_style(value["frame"]) if "frame" in value else None,
        cloud=coerce_element_style(value["cloud"]) if "cloud" in value else None,
        database=coerce_element_style(value["database"])
        if "database" in value
        else None,
        stereotypes=_coerce_stereotypes(value.get("stereotypes")),
    )


# ---------------------------------------------------------------------------
# Sequence Diagram Styling
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SequenceDiagramStyle:
    """Diagram-wide styling for sequence diagrams.

    This generates a PlantUML <style> block that sets default appearance
    for all elements in the diagram. Individual elements can still override
    these defaults with inline styles.

    Root-level properties apply to the diagram background and default fonts.
    Element-specific properties (participant, arrow, note, etc.) let you
    style each element type independently.

    Example:
        with sequence_diagram(
            diagram_style=SequenceDiagramStyle(
                background="white",
                font_name="Arial",
                participant=ElementStyle(
                    background="#E3F2FD",
                    line_color="#1976D2",
                ),
                arrow=DiagramArrowStyle(
                    line_color="#757575",
                ),
            )
        ) as d:
            ...

    This generates a <style> block in the PlantUML output that themes
    all participants with blue backgrounds and gray arrows.
    """

    # Root-level properties
    background: ColorLike | Gradient | None = None
    font_name: str | None = None
    font_size: int | None = None
    font_color: ColorLike | None = None

    # Element-specific styles
    participant: ElementStyle | None = None
    actor: ElementStyle | None = None
    boundary: ElementStyle | None = None
    control: ElementStyle | None = None
    entity: ElementStyle | None = None
    database: ElementStyle | None = None
    collections: ElementStyle | None = None
    queue: ElementStyle | None = None
    arrow: DiagramArrowStyle | None = None
    lifeline: ElementStyle | None = None
    note: ElementStyle | None = None
    box: ElementStyle | None = None
    group: ElementStyle | None = None
    divider: ElementStyle | None = None
    reference: ElementStyle | None = None
    title: ElementStyle | None = None

    # Selector-based styles
    stereotypes: dict[str, ElementStyle] | None = None
    """Style elements by stereotype name."""


class SequenceDiagramStyleDict(TypedDict, total=False):
    """Dict form of SequenceDiagramStyle — passed as diagram_style= to sequence_diagram().

    Top-level keys set diagram background and default fonts.
    Element keys accept ElementStyleDict (see ElementStyleDict for all properties).

    Available keys:
        background:   Diagram background color
        font_name:    Default font family
        font_size:    Default font size
        font_color:   Default text color
        participant:  Style for participants (ElementStyleDict)
        actor:        Style for actors (ElementStyleDict)
        boundary:     Style for boundary participants (ElementStyleDict)
        control:      Style for control participants (ElementStyleDict)
        entity:       Style for entity participants (ElementStyleDict)
        database:     Style for database participants (ElementStyleDict)
        collections:  Style for collection participants (ElementStyleDict)
        queue:        Style for queue participants (ElementStyleDict)
        lifeline:     Style for lifelines (ElementStyleDict)
        note:         Style for notes (ElementStyleDict)
        box:          Style for participant boxes (ElementStyleDict)
        group:        Style for message groups (ElementStyleDict)
        divider:      Style for divider lines (ElementStyleDict)
        reference:    Style for reference frames (ElementStyleDict)
        arrow:        Style for messages (DiagramArrowStyleDict)
        title:        Style for the title (ElementStyleDict)
        stereotypes:  Style by stereotype name: {"name": ElementStyleDict}

    Example:
        sequence_diagram(diagram_style={
            "background": "white",
            "participant": {"background": "#E3F2FD", "line_color": "#1976D2"},
            "actor": {"background": "#FFF9C4"},
            "arrow": {"line_color": "#757575", "font_size": 10},
            "stereotypes": {
                "external": {"background": "#FFCDD2", "font_style": "italic"},
            },
        })
    """

    background: ColorLike | Gradient
    font_name: str
    font_size: int
    font_color: ColorLike
    participant: ElementStyleLike
    actor: ElementStyleLike
    boundary: ElementStyleLike
    control: ElementStyleLike
    entity: ElementStyleLike
    database: ElementStyleLike
    collections: ElementStyleLike
    queue: ElementStyleLike
    arrow: DiagramArrowStyleLike
    lifeline: ElementStyleLike
    note: ElementStyleLike
    box: ElementStyleLike
    group: ElementStyleLike
    divider: ElementStyleLike
    reference: ElementStyleLike
    title: ElementStyleLike
    stereotypes: dict[str, ElementStyleLike]


# Type alias for sequence diagram style arguments
SequenceDiagramStyleLike: TypeAlias = SequenceDiagramStyle | SequenceDiagramStyleDict

_SEQUENCE_DIAGRAM_STYLE_KEYS: frozenset[str] = frozenset({
    "background", "font_name", "font_size", "font_color",
    "participant", "actor", "boundary", "control", "entity",
    "database", "collections", "queue", "arrow", "lifeline",
    "note", "box", "group", "divider", "reference", "title",
    "stereotypes",
})


def coerce_sequence_diagram_style(
    value: SequenceDiagramStyleLike,
) -> SequenceDiagramStyle:
    """Convert a SequenceDiagramStyleLike value to a SequenceDiagramStyle object."""
    if isinstance(value, SequenceDiagramStyle):
        return value
    _validate_style_dict_keys(
        value, _SEQUENCE_DIAGRAM_STYLE_KEYS, "SequenceDiagramStyle"
    )
    return SequenceDiagramStyle(
        background=_coerce_color_or_gradient(value.get("background")),
        font_name=value.get("font_name"),
        font_size=value.get("font_size"),
        font_color=coerce_color(value["font_color"])
        if "font_color" in value
        else None,
        participant=coerce_element_style(value["participant"])
        if "participant" in value
        else None,
        actor=coerce_element_style(value["actor"]) if "actor" in value else None,
        boundary=coerce_element_style(value["boundary"])
        if "boundary" in value
        else None,
        control=coerce_element_style(value["control"])
        if "control" in value
        else None,
        entity=coerce_element_style(value["entity"]) if "entity" in value else None,
        database=coerce_element_style(value["database"])
        if "database" in value
        else None,
        collections=coerce_element_style(value["collections"])
        if "collections" in value
        else None,
        queue=coerce_element_style(value["queue"]) if "queue" in value else None,
        arrow=coerce_diagram_arrow_style(value["arrow"])
        if "arrow" in value
        else None,
        lifeline=coerce_element_style(value["lifeline"])
        if "lifeline" in value
        else None,
        note=coerce_element_style(value["note"]) if "note" in value else None,
        box=coerce_element_style(value["box"]) if "box" in value else None,
        group=coerce_element_style(value["group"]) if "group" in value else None,
        divider=coerce_element_style(value["divider"])
        if "divider" in value
        else None,
        reference=coerce_element_style(value["reference"])
        if "reference" in value
        else None,
        title=coerce_element_style(value["title"]) if "title" in value else None,
        stereotypes=_coerce_stereotypes(value.get("stereotypes")),
    )


# ---------------------------------------------------------------------------
# Activity Diagram Styling
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ActivityDiagramStyle:
    """Diagram-wide styling for activity diagrams.

    This generates a PlantUML <style> block that sets default appearance
    for all elements in the diagram.

    Example:
        with activity_diagram(
            diagram_style=ActivityDiagramStyle(
                background="white",
                activity=ElementStyle(background="#E3F2FD"),
                arrow=DiagramArrowStyle(line_color="#757575"),
            )
        ) as d:
            ...
    """

    # Root-level properties
    background: ColorLike | Gradient | None = None
    font_name: str | None = None
    font_size: int | None = None
    font_color: ColorLike | None = None

    # Element-specific styles
    activity: ElementStyle | None = None
    partition: ElementStyle | None = None
    swimlane: ElementStyle | None = None
    diamond: ElementStyle | None = None
    arrow: DiagramArrowStyle | None = None
    note: ElementStyle | None = None
    group: ElementStyle | None = None
    title: ElementStyle | None = None

    # Selector-based styles
    stereotypes: dict[str, ElementStyle] | None = None
    """Style elements by stereotype name."""


class ActivityDiagramStyleDict(TypedDict, total=False):
    """Dict form of ActivityDiagramStyle — passed as diagram_style= to activity_diagram().

    Top-level keys set diagram background and default fonts.
    Element keys accept ElementStyleDict (see ElementStyleDict for all properties).

    Available keys:
        background:   Diagram background color
        font_name:    Default font family
        font_size:    Default font size
        font_color:   Default text color
        activity:     Style for activity boxes (ElementStyleDict)
        partition:    Style for partitions (ElementStyleDict)
        swimlane:     Style for swimlanes (ElementStyleDict)
        diamond:      Style for decision/merge diamonds (ElementStyleDict)
        arrow:        Style for flow arrows (DiagramArrowStyleDict)
        note:         Style for notes (ElementStyleDict)
        group:        Style for groups (ElementStyleDict)
        title:        Style for the title (ElementStyleDict)
        stereotypes:  Style by stereotype name: {"name": ElementStyleDict}

    Example:
        activity_diagram(diagram_style={
            "background": "white",
            "activity": {"background": "#E3F2FD", "round_corner": 10},
            "diamond": {"background": "#FFF9C4"},
            "arrow": {"line_color": "gray", "font_size": 10},
            "stereotypes": {
                "slow": {"background": "#FFCDD2", "font_style": "bold"},
            },
        })
    """

    background: ColorLike | Gradient
    font_name: str
    font_size: int
    font_color: ColorLike
    activity: ElementStyleLike
    partition: ElementStyleLike
    swimlane: ElementStyleLike
    diamond: ElementStyleLike
    arrow: DiagramArrowStyleLike
    note: ElementStyleLike
    group: ElementStyleLike
    title: ElementStyleLike
    stereotypes: dict[str, ElementStyleLike]


# Type alias for activity diagram style arguments
ActivityDiagramStyleLike: TypeAlias = ActivityDiagramStyle | ActivityDiagramStyleDict

_ACTIVITY_DIAGRAM_STYLE_KEYS: frozenset[str] = frozenset({
    "background", "font_name", "font_size", "font_color",
    "activity", "partition", "swimlane", "diamond",
    "arrow", "note", "group", "title", "stereotypes",
})


def coerce_activity_diagram_style(
    value: ActivityDiagramStyleLike,
) -> ActivityDiagramStyle:
    """Convert an ActivityDiagramStyleLike value to an ActivityDiagramStyle object."""
    if isinstance(value, ActivityDiagramStyle):
        return value
    _validate_style_dict_keys(
        value, _ACTIVITY_DIAGRAM_STYLE_KEYS, "ActivityDiagramStyle"
    )
    return ActivityDiagramStyle(
        background=_coerce_color_or_gradient(value.get("background")),
        font_name=value.get("font_name"),
        font_size=value.get("font_size"),
        font_color=coerce_color(value["font_color"])
        if "font_color" in value
        else None,
        activity=coerce_element_style(value["activity"])
        if "activity" in value
        else None,
        partition=coerce_element_style(value["partition"])
        if "partition" in value
        else None,
        swimlane=coerce_element_style(value["swimlane"])
        if "swimlane" in value
        else None,
        diamond=coerce_element_style(value["diamond"])
        if "diamond" in value
        else None,
        arrow=coerce_diagram_arrow_style(value["arrow"])
        if "arrow" in value
        else None,
        note=coerce_element_style(value["note"]) if "note" in value else None,
        group=coerce_element_style(value["group"]) if "group" in value else None,
        title=coerce_element_style(value["title"]) if "title" in value else None,
        stereotypes=_coerce_stereotypes(value.get("stereotypes")),
    )


# ---------------------------------------------------------------------------
# Class Diagram Styling
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ClassDiagramStyle:
    """Diagram-wide styling for class diagrams.

    This generates a PlantUML <style> block that sets default appearance
    for all elements in the diagram.

    Example:
        with class_diagram(
            diagram_style=ClassDiagramStyle(
                background="white",
                class_=ElementStyle(background="#E3F2FD"),
                arrow=DiagramArrowStyle(line_color="#757575"),
            )
        ) as d:
            ...
    """

    # Root-level properties
    background: ColorLike | Gradient | None = None
    font_name: str | None = None
    font_size: int | None = None
    font_color: ColorLike | None = None

    # Element-specific styles (class_ because class is a keyword)
    class_: ElementStyle | None = None
    interface: ElementStyle | None = None
    abstract: ElementStyle | None = None
    enum: ElementStyle | None = None
    annotation: ElementStyle | None = None
    package: ElementStyle | None = None
    arrow: DiagramArrowStyle | None = None
    note: ElementStyle | None = None
    title: ElementStyle | None = None

    # Selector-based styles
    stereotypes: dict[str, ElementStyle] | None = None
    """Style elements by stereotype name."""


class ClassDiagramStyleDict(TypedDict, total=False):
    """Dict form of ClassDiagramStyle — passed as diagram_style= to class_diagram().

    Top-level keys set diagram background and default fonts.
    Element keys accept ElementStyleDict (see ElementStyleDict for all properties).

    Available keys:
        background:   Diagram background color
        font_name:    Default font family
        font_size:    Default font size
        font_color:   Default text color
        class_:       Style for classes (ElementStyleDict)
        interface:    Style for interfaces (ElementStyleDict)
        abstract:     Style for abstract classes (ElementStyleDict)
        enum:         Style for enumerations (ElementStyleDict)
        annotation:   Style for annotations (ElementStyleDict)
        package:      Style for packages (ElementStyleDict)
        arrow:        Style for relationships (DiagramArrowStyleDict)
        note:         Style for notes (ElementStyleDict)
        title:        Style for the title (ElementStyleDict)
        stereotypes:  Style by stereotype name: {"name": ElementStyleDict}

    Example:
        class_diagram(diagram_style={
            "background": "white",
            "class_": {"background": "#E3F2FD", "line_color": "#1976D2"},
            "interface": {"background": "#C8E6C9"},
            "arrow": {"line_color": "gray"},
            "stereotypes": {
                "entity": {"background": "#FFF9C4", "font_style": "bold"},
            },
        })
    """

    background: ColorLike | Gradient
    font_name: str
    font_size: int
    font_color: ColorLike
    class_: ElementStyleLike
    interface: ElementStyleLike
    abstract: ElementStyleLike
    enum: ElementStyleLike
    annotation: ElementStyleLike
    package: ElementStyleLike
    arrow: DiagramArrowStyleLike
    note: ElementStyleLike
    title: ElementStyleLike
    stereotypes: dict[str, ElementStyleLike]


# Type alias for class diagram style arguments
ClassDiagramStyleLike: TypeAlias = ClassDiagramStyle | ClassDiagramStyleDict

_CLASS_DIAGRAM_STYLE_KEYS: frozenset[str] = frozenset({
    "background", "font_name", "font_size", "font_color",
    "class_", "interface", "abstract", "enum", "annotation",
    "package", "arrow", "note", "title", "stereotypes",
})


def coerce_class_diagram_style(
    value: ClassDiagramStyleLike,
) -> ClassDiagramStyle:
    """Convert a ClassDiagramStyleLike value to a ClassDiagramStyle object."""
    if isinstance(value, ClassDiagramStyle):
        return value
    _validate_style_dict_keys(value, _CLASS_DIAGRAM_STYLE_KEYS, "ClassDiagramStyle")
    return ClassDiagramStyle(
        background=_coerce_color_or_gradient(value.get("background")),
        font_name=value.get("font_name"),
        font_size=value.get("font_size"),
        font_color=coerce_color(value["font_color"])
        if "font_color" in value
        else None,
        class_=coerce_element_style(value["class_"]) if "class_" in value else None,
        interface=coerce_element_style(value["interface"])
        if "interface" in value
        else None,
        abstract=coerce_element_style(value["abstract"])
        if "abstract" in value
        else None,
        enum=coerce_element_style(value["enum"]) if "enum" in value else None,
        annotation=coerce_element_style(value["annotation"])
        if "annotation" in value
        else None,
        package=coerce_element_style(value["package"])
        if "package" in value
        else None,
        arrow=coerce_diagram_arrow_style(value["arrow"])
        if "arrow" in value
        else None,
        note=coerce_element_style(value["note"]) if "note" in value else None,
        title=coerce_element_style(value["title"]) if "title" in value else None,
        stereotypes=_coerce_stereotypes(value.get("stereotypes")),
    )


# ---------------------------------------------------------------------------
# Object Diagram Styling
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ObjectDiagramStyle:
    """Diagram-wide styling for object diagrams.

    This generates a PlantUML <style> block that sets default appearance
    for all elements in the diagram.

    Note: PlantUML ignores arrow and note CSS selectors for object diagrams.
    Use inline styles for those elements if needed.
    """

    # Root-level properties
    background: ColorLike | Gradient | None = None
    font_name: str | None = None
    font_size: int | None = None
    font_color: ColorLike | None = None

    # Element-specific styles (only object and map render)
    object: ElementStyle | None = None
    map: ElementStyle | None = None
    title: ElementStyle | None = None

    # Selector-based styles
    stereotypes: dict[str, ElementStyle] | None = None
    """Style elements by stereotype name."""


class ObjectDiagramStyleDict(TypedDict, total=False):
    """Dict form of ObjectDiagramStyle — passed as diagram_style= to object_diagram().

    Top-level keys set diagram background and default fonts.
    Element keys accept ElementStyleDict (see ElementStyleDict for all properties).

    Note: PlantUML ignores arrow and note CSS for object diagrams.

    Available keys:
        background:   Diagram background color
        font_name:    Default font family
        font_size:    Default font size
        font_color:   Default text color
        object:       Style for objects (ElementStyleDict)
        map:          Style for map objects (ElementStyleDict)
        title:        Style for the title (ElementStyleDict)
        stereotypes:  Style by stereotype name: {"name": ElementStyleDict}

    Example:
        object_diagram(diagram_style={
            "background": "white",
            "object": {"background": "#E3F2FD", "line_color": "#1976D2"},
            "map": {"background": "#C8E6C9"},
            "stereotypes": {
                "config": {"background": "#FFF9C4"},
            },
        })
    """

    background: ColorLike | Gradient
    font_name: str
    font_size: int
    font_color: ColorLike
    object: ElementStyleLike
    map: ElementStyleLike
    title: ElementStyleLike
    stereotypes: dict[str, ElementStyleLike]


ObjectDiagramStyleLike: TypeAlias = ObjectDiagramStyle | ObjectDiagramStyleDict

_OBJECT_DIAGRAM_STYLE_KEYS: frozenset[str] = frozenset({
    "background", "font_name", "font_size", "font_color",
    "object", "map", "title", "stereotypes",
})


def coerce_object_diagram_style(
    value: ObjectDiagramStyleLike,
) -> ObjectDiagramStyle:
    """Convert an ObjectDiagramStyleLike value to an ObjectDiagramStyle object."""
    if isinstance(value, ObjectDiagramStyle):
        return value
    _validate_style_dict_keys(value, _OBJECT_DIAGRAM_STYLE_KEYS, "ObjectDiagramStyle")
    return ObjectDiagramStyle(
        background=_coerce_color_or_gradient(value.get("background")),
        font_name=value.get("font_name"),
        font_size=value.get("font_size"),
        font_color=coerce_color(value["font_color"])
        if "font_color" in value
        else None,
        object=coerce_element_style(value["object"]) if "object" in value else None,
        map=coerce_element_style(value["map"]) if "map" in value else None,
        title=coerce_element_style(value["title"]) if "title" in value else None,
        stereotypes=_coerce_stereotypes(value.get("stereotypes")),
    )


# ---------------------------------------------------------------------------
# JSON Diagram Styling
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class JsonDiagramStyle:
    """Diagram-wide styling for JSON diagrams.

    This generates a PlantUML <style> block that sets default appearance
    for JSON data visualization.
    """

    # Root-level properties
    background: ColorLike | Gradient | None = None
    font_name: str | None = None
    font_size: int | None = None
    font_color: ColorLike | None = None

    # Element-specific styles
    node: ElementStyle | None = None
    highlight: ElementStyle | None = None


class JsonDiagramStyleDict(TypedDict, total=False):
    """Dict form of JsonDiagramStyle — passed as diagram_style= to json_diagram().

    Top-level keys set diagram background and default fonts.
    Element keys accept ElementStyleDict (see ElementStyleDict for all properties).

    Available keys:
        background:   Diagram background color
        font_name:    Default font family
        font_size:    Default font size
        font_color:   Default text color
        node:         Style for data nodes (ElementStyleDict)
        highlight:    Style for highlighted nodes (ElementStyleDict)

    Example:
        json_diagram(diagram_style={
            "background": "white",
            "node": {"background": "#E3F2FD"},
            "highlight": {"background": "#FFF9C4"},
        })
    """

    background: ColorLike | Gradient
    font_name: str
    font_size: int
    font_color: ColorLike
    node: ElementStyleLike
    highlight: ElementStyleLike


JsonDiagramStyleLike: TypeAlias = JsonDiagramStyle | JsonDiagramStyleDict

_JSON_DIAGRAM_STYLE_KEYS: frozenset[str] = frozenset({
    "background", "font_name", "font_size", "font_color", "node", "highlight",
})


def coerce_json_diagram_style(
    value: JsonDiagramStyleLike,
) -> JsonDiagramStyle:
    """Convert a JsonDiagramStyleLike value to a JsonDiagramStyle object."""
    if isinstance(value, JsonDiagramStyle):
        return value
    _validate_style_dict_keys(value, _JSON_DIAGRAM_STYLE_KEYS, "JsonDiagramStyle")
    return JsonDiagramStyle(
        background=_coerce_color_or_gradient(value.get("background")),
        font_name=value.get("font_name"),
        font_size=value.get("font_size"),
        font_color=coerce_color(value["font_color"])
        if "font_color" in value
        else None,
        node=coerce_element_style(value["node"]) if "node" in value else None,
        highlight=coerce_element_style(value["highlight"])
        if "highlight" in value
        else None,
    )


# ---------------------------------------------------------------------------
# YAML Diagram Styling
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class YamlDiagramStyle:
    """Diagram-wide styling for YAML diagrams.

    This generates a PlantUML <style> block that sets default appearance
    for YAML data visualization.
    """

    # Root-level properties
    background: ColorLike | Gradient | None = None
    font_name: str | None = None
    font_size: int | None = None
    font_color: ColorLike | None = None

    # Element-specific styles
    node: ElementStyle | None = None
    highlight: ElementStyle | None = None


class YamlDiagramStyleDict(TypedDict, total=False):
    """Dict form of YamlDiagramStyle — passed as diagram_style= to yaml_diagram().

    Top-level keys set diagram background and default fonts.
    Element keys accept ElementStyleDict (see ElementStyleDict for all properties).

    Available keys:
        background:   Diagram background color
        font_name:    Default font family
        font_size:    Default font size
        font_color:   Default text color
        node:         Style for data nodes (ElementStyleDict)
        highlight:    Style for highlighted nodes (ElementStyleDict)

    Example:
        yaml_diagram(diagram_style={
            "background": "white",
            "node": {"background": "#E3F2FD"},
            "highlight": {"background": "#FFF9C4"},
        })
    """

    background: ColorLike | Gradient
    font_name: str
    font_size: int
    font_color: ColorLike
    node: ElementStyleLike
    highlight: ElementStyleLike


YamlDiagramStyleLike: TypeAlias = YamlDiagramStyle | YamlDiagramStyleDict

_YAML_DIAGRAM_STYLE_KEYS: frozenset[str] = frozenset({
    "background", "font_name", "font_size", "font_color", "node", "highlight",
})


def coerce_yaml_diagram_style(
    value: YamlDiagramStyleLike,
) -> YamlDiagramStyle:
    """Convert a YamlDiagramStyleLike value to a YamlDiagramStyle object."""
    if isinstance(value, YamlDiagramStyle):
        return value
    _validate_style_dict_keys(value, _YAML_DIAGRAM_STYLE_KEYS, "YamlDiagramStyle")
    return YamlDiagramStyle(
        background=_coerce_color_or_gradient(value.get("background")),
        font_name=value.get("font_name"),
        font_size=value.get("font_size"),
        font_color=coerce_color(value["font_color"])
        if "font_color" in value
        else None,
        node=coerce_element_style(value["node"]) if "node" in value else None,
        highlight=coerce_element_style(value["highlight"])
        if "highlight" in value
        else None,
    )


# ---------------------------------------------------------------------------
# MindMap Diagram Styling
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MindMapDiagramStyle:
    """Diagram-wide styling for MindMap diagrams.

    This generates a PlantUML <style> block that sets default appearance
    for MindMap tree visualization.
    """

    # Root-level properties
    background: ColorLike | Gradient | None = None
    font_name: str | None = None
    font_size: int | None = None
    font_color: ColorLike | None = None

    # Element-specific styles
    node: ElementStyle | None = None
    root_node: ElementStyle | None = None
    leaf_node: ElementStyle | None = None
    arrow: DiagramArrowStyle | None = None

    # Selector-based styles
    depths: dict[int, ElementStyle] | None = None
    """Style nodes by tree depth level.

    Keys are depth integers (0 = root, 1 = first children, etc.).
    Values are ElementStyle objects applied at that depth.
    """


class MindMapDiagramStyleDict(TypedDict, total=False):
    """Dict form of MindMapDiagramStyle — passed as diagram_style= to mindmap_diagram().

    Top-level keys set diagram background and default fonts.
    Element keys accept ElementStyleDict (see ElementStyleDict for all properties).

    Available keys:
        background:   Diagram background color
        font_name:    Default font family
        font_size:    Default font size
        font_color:   Default text color
        node:         Style for all nodes (ElementStyleDict)
        root_node:    Style for the root node (ElementStyleDict)
        leaf_node:    Style for leaf nodes (ElementStyleDict)
        arrow:        Style for branch connectors (DiagramArrowStyleDict)
        depths:       Style by tree depth: {0: ElementStyleDict, 1: ElementStyleDict, ...}

    Example:
        mindmap_diagram(diagram_style={
            "background": "white",
            "root_node": {"background": "#1976D2", "font_color": "white"},
            "node": {"background": "#E3F2FD"},
            "arrow": {"line_color": "gray"},
            "depths": {
                0: {"background": "#1976D2", "font_color": "white"},
                1: {"background": "#BBDEFB"},
            },
        })
    """

    background: ColorLike | Gradient
    font_name: str
    font_size: int
    font_color: ColorLike
    node: ElementStyleLike
    root_node: ElementStyleLike
    leaf_node: ElementStyleLike
    arrow: DiagramArrowStyleLike
    depths: dict[int, ElementStyleLike]


MindMapDiagramStyleLike: TypeAlias = MindMapDiagramStyle | MindMapDiagramStyleDict

_MINDMAP_DIAGRAM_STYLE_KEYS: frozenset[str] = frozenset({
    "background", "font_name", "font_size", "font_color",
    "node", "root_node", "leaf_node", "arrow", "depths",
})


def coerce_mindmap_diagram_style(
    value: MindMapDiagramStyleLike,
) -> MindMapDiagramStyle:
    """Convert a MindMapDiagramStyleLike value to a MindMapDiagramStyle object."""
    if isinstance(value, MindMapDiagramStyle):
        return value
    _validate_style_dict_keys(
        value, _MINDMAP_DIAGRAM_STYLE_KEYS, "MindMapDiagramStyle"
    )
    return MindMapDiagramStyle(
        background=_coerce_color_or_gradient(value.get("background")),
        font_name=value.get("font_name"),
        font_size=value.get("font_size"),
        font_color=coerce_color(value["font_color"])
        if "font_color" in value
        else None,
        node=coerce_element_style(value["node"]) if "node" in value else None,
        root_node=coerce_element_style(value["root_node"])
        if "root_node" in value
        else None,
        leaf_node=coerce_element_style(value["leaf_node"])
        if "leaf_node" in value
        else None,
        arrow=coerce_diagram_arrow_style(value["arrow"]) if "arrow" in value else None,
        depths=_coerce_depths(value.get("depths")),
    )


# ---------------------------------------------------------------------------
# Network Diagram Styling
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class NetworkDiagramStyle:
    """Diagram-wide styling for network diagrams (nwdiag).

    This generates a PlantUML <style> block that sets default appearance
    for network diagram elements.

    CSS selectors used:
        nwdiagDiagram: Root diagram styling
        network:       Network bar appearance
        server:        Node/server appearance
        group:         Group box appearance
        arrow:         Address label and connector styling

    Example:
        with network_diagram(
            diagram_style=NetworkDiagramStyle(
                background="white",
                network=ElementStyle(background="LightYellow"),
                server=ElementStyle(background="LightGreen"),
                group=ElementStyle(background="PaleGreen"),
            )
        ) as d:
            ...
    """

    # Root-level properties (nwdiagDiagram)
    background: ColorLike | Gradient | None = None
    font_name: str | None = None
    font_size: int | None = None
    font_color: ColorLike | None = None

    # Element-specific styles
    network: ElementStyle | None = None
    server: ElementStyle | None = None
    group: ElementStyle | None = None
    arrow: DiagramArrowStyle | None = None

    # Selector-based styles
    stereotypes: dict[str, ElementStyle] | None = None
    """Style elements by stereotype name."""


class NetworkDiagramStyleDict(TypedDict, total=False):
    """Dict form of NetworkDiagramStyle — passed as diagram_style= to network_diagram().

    Top-level keys set diagram background and default fonts.
    Element keys accept ElementStyleDict (see ElementStyleDict for all properties).

    Available keys:
        background:   Diagram background color
        font_name:    Default font family
        font_size:    Default font size
        font_color:   Default text color
        network:      Style for network bars (ElementStyleDict)
        server:       Style for server nodes (ElementStyleDict)
        group:        Style for group boxes (ElementStyleDict)
        arrow:        Style for address labels and connectors (DiagramArrowStyleDict)
        stereotypes:  Style by stereotype name: {"name": ElementStyleDict}

    Example:
        network_diagram(diagram_style={
            "background": "white",
            "network": {"background": "#E3F2FD"},
            "server": {"background": "#C8E6C9", "line_color": "#388E3C"},
            "arrow": {"font_size": 10},
            "stereotypes": {
                "firewall": {"background": "#FFCDD2"},
            },
        })
    """

    background: ColorLike | Gradient
    font_name: str
    font_size: int
    font_color: ColorLike
    network: ElementStyleLike
    server: ElementStyleLike
    group: ElementStyleLike
    arrow: DiagramArrowStyleLike
    stereotypes: dict[str, ElementStyleLike]


NetworkDiagramStyleLike: TypeAlias = NetworkDiagramStyle | NetworkDiagramStyleDict

_NETWORK_DIAGRAM_STYLE_KEYS: frozenset[str] = frozenset({
    "background", "font_name", "font_size", "font_color",
    "network", "server", "group", "arrow", "stereotypes",
})


def coerce_network_diagram_style(
    value: NetworkDiagramStyleLike,
) -> NetworkDiagramStyle:
    """Convert a NetworkDiagramStyleLike value to a NetworkDiagramStyle object."""
    if isinstance(value, NetworkDiagramStyle):
        return value
    _validate_style_dict_keys(
        value, _NETWORK_DIAGRAM_STYLE_KEYS, "NetworkDiagramStyle"
    )
    return NetworkDiagramStyle(
        background=_coerce_color_or_gradient(value.get("background")),
        font_name=value.get("font_name"),
        font_size=value.get("font_size"),
        font_color=coerce_color(value["font_color"])
        if "font_color" in value
        else None,
        network=coerce_element_style(value["network"])
        if "network" in value
        else None,
        server=coerce_element_style(value["server"]) if "server" in value else None,
        group=coerce_element_style(value["group"]) if "group" in value else None,
        arrow=coerce_diagram_arrow_style(value["arrow"]) if "arrow" in value else None,
        stereotypes=_coerce_stereotypes(value.get("stereotypes")),
    )


# ---------------------------------------------------------------------------
# Timing Diagram Styling
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TimingDiagramStyle:
    """Diagram-wide styling for timing diagrams.

    This generates a PlantUML <style> block that sets default appearance
    for timing diagram elements.

    CSS selectors used:
        timingDiagram: Root diagram styling
        robust:        Robust signal appearance
        concise:       Concise signal appearance
        clock:         Clock signal appearance
        binary:        Binary signal appearance
        analog:        Analog signal appearance
        highlight:     Highlight region appearance
        note:          Note appearance
        arrow:         Message arrow styling

    Example:
        with timing_diagram(
            diagram_style=TimingDiagramStyle(
                background="white",
                robust=ElementStyle(background="LightBlue"),
                highlight=ElementStyle(background="Yellow"),
            )
        ) as d:
            ...
    """

    # Root-level properties (timingDiagram)
    background: ColorLike | Gradient | None = None
    font_name: str | None = None
    font_size: int | None = None
    font_color: ColorLike | None = None

    # Element-specific styles
    robust: ElementStyle | None = None
    concise: ElementStyle | None = None
    clock: ElementStyle | None = None
    binary: ElementStyle | None = None
    analog: ElementStyle | None = None
    highlight: ElementStyle | None = None
    note: ElementStyle | None = None
    arrow: DiagramArrowStyle | None = None
    title: ElementStyle | None = None

    # Selector-based styles
    stereotypes: dict[str, ElementStyle] | None = None
    """Style elements by stereotype name."""


class TimingDiagramStyleDict(TypedDict, total=False):
    """Dict form of TimingDiagramStyle — passed as diagram_style= to timing_diagram().

    Top-level keys set diagram background and default fonts.
    Element keys accept ElementStyleDict (see ElementStyleDict for all properties).

    Available keys:
        background:   Diagram background color
        font_name:    Default font family
        font_size:    Default font size
        font_color:   Default text color
        robust:       Style for robust signals (ElementStyleDict)
        concise:      Style for concise signals (ElementStyleDict)
        clock:        Style for clock signals (ElementStyleDict)
        binary:       Style for binary signals (ElementStyleDict)
        analog:       Style for analog signals (ElementStyleDict)
        highlight:    Style for highlight regions (ElementStyleDict)
        note:         Style for notes (ElementStyleDict)
        arrow:        Style for message arrows (DiagramArrowStyleDict)
        title:        Style for the title (ElementStyleDict)
        stereotypes:  Style by stereotype name: {"name": ElementStyleDict}

    Example:
        timing_diagram(diagram_style={
            "background": "white",
            "robust": {"background": "#E3F2FD", "line_color": "#1976D2"},
            "concise": {"background": "#C8E6C9"},
            "highlight": {"background": "#FFF9C4"},
            "arrow": {"line_color": "gray"},
            "stereotypes": {
                "critical": {"line_color": "red", "font_style": "bold"},
            },
        })
    """

    background: ColorLike | Gradient
    font_name: str
    font_size: int
    font_color: ColorLike
    robust: ElementStyleLike
    concise: ElementStyleLike
    clock: ElementStyleLike
    binary: ElementStyleLike
    analog: ElementStyleLike
    highlight: ElementStyleLike
    note: ElementStyleLike
    arrow: DiagramArrowStyleLike
    title: ElementStyleLike
    stereotypes: dict[str, ElementStyleLike]


TimingDiagramStyleLike: TypeAlias = TimingDiagramStyle | TimingDiagramStyleDict

_TIMING_DIAGRAM_STYLE_KEYS: frozenset[str] = frozenset({
    "background", "font_name", "font_size", "font_color",
    "robust", "concise", "clock", "binary", "analog",
    "highlight", "note", "arrow", "title", "stereotypes",
})


def coerce_timing_diagram_style(
    value: TimingDiagramStyleLike,
) -> TimingDiagramStyle:
    """Convert a TimingDiagramStyleLike value to a TimingDiagramStyle object."""
    if isinstance(value, TimingDiagramStyle):
        return value
    _validate_style_dict_keys(
        value, _TIMING_DIAGRAM_STYLE_KEYS, "TimingDiagramStyle"
    )
    return TimingDiagramStyle(
        background=_coerce_color_or_gradient(value.get("background")),
        font_name=value.get("font_name"),
        font_size=value.get("font_size"),
        font_color=coerce_color(value["font_color"])
        if "font_color" in value
        else None,
        robust=coerce_element_style(value["robust"]) if "robust" in value else None,
        concise=coerce_element_style(value["concise"]) if "concise" in value else None,
        clock=coerce_element_style(value["clock"]) if "clock" in value else None,
        binary=coerce_element_style(value["binary"]) if "binary" in value else None,
        analog=coerce_element_style(value["analog"]) if "analog" in value else None,
        highlight=coerce_element_style(value["highlight"])
        if "highlight" in value
        else None,
        note=coerce_element_style(value["note"]) if "note" in value else None,
        arrow=coerce_diagram_arrow_style(value["arrow"]) if "arrow" in value else None,
        title=coerce_element_style(value["title"]) if "title" in value else None,
        stereotypes=_coerce_stereotypes(value.get("stereotypes")),
    )


# ---------------------------------------------------------------------------
# Gantt Diagram Styling
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GanttDiagramStyle:
    """Diagram-wide styling for Gantt charts.

    This generates a PlantUML <style> block that sets default appearance
    for all elements in the diagram.

    Example:
        with gantt_diagram(
            diagram_style=GanttDiagramStyle(
                task=ElementStyle(background="LightBlue"),
                milestone=ElementStyle(background="Gold"),
            )
        ) as d:
            ...
    """

    # Root-level properties
    background: ColorLike | Gradient | None = None
    font_name: str | None = None
    font_size: int | None = None
    font_color: ColorLike | None = None

    # Element-specific styles
    task: ElementStyle | None = None
    milestone: ElementStyle | None = None
    separator: ElementStyle | None = None
    note: ElementStyle | None = None
    arrow: DiagramArrowStyle | None = None
    undone: ElementStyle | None = None  # Incomplete portion styling
    today: ElementStyle | None = None  # Today marker styling

    # Selector-based styles
    stereotypes: dict[str, ElementStyle] | None = None
    """Style elements by stereotype name."""


class GanttDiagramStyleDict(TypedDict, total=False):
    """Dict form of GanttDiagramStyle — passed as diagram_style= to gantt_diagram().

    Top-level keys set diagram background and default fonts.
    Element keys accept ElementStyleDict (see ElementStyleDict for all properties).

    Available keys:
        background:   Diagram background color
        font_name:    Default font family
        font_size:    Default font size
        font_color:   Default text color
        task:         Style for tasks (ElementStyleDict)
        milestone:    Style for milestones (ElementStyleDict)
        separator:    Style for separators (ElementStyleDict)
        note:         Style for notes (ElementStyleDict)
        arrow:        Style for dependency arrows (DiagramArrowStyleDict)
        undone:       Style for incomplete task portions (ElementStyleDict)
        today:        Style for the today marker (ElementStyleDict)
        stereotypes:  Style by stereotype name: {"name": ElementStyleDict}

    Example:
        gantt_diagram(diagram_style={
            "background": "white",
            "task": {"background": "#E3F2FD", "line_color": "#1976D2"},
            "milestone": {"background": "#FFF9C4"},
            "arrow": {"line_color": "gray"},
            "undone": {"background": "#EEEEEE"},
            "stereotypes": {
                "critical": {"background": "#FFCDD2", "font_style": "bold"},
            },
        })
    """

    background: ColorLike | Gradient
    font_name: str
    font_size: int
    font_color: ColorLike
    task: ElementStyleLike
    milestone: ElementStyleLike
    separator: ElementStyleLike
    note: ElementStyleLike
    arrow: DiagramArrowStyleLike
    undone: ElementStyleLike
    today: ElementStyleLike
    stereotypes: dict[str, ElementStyleLike]


GanttDiagramStyleLike: TypeAlias = GanttDiagramStyle | GanttDiagramStyleDict

_GANTT_DIAGRAM_STYLE_KEYS: frozenset[str] = frozenset({
    "background", "font_name", "font_size", "font_color",
    "task", "milestone", "separator", "note", "arrow", "undone", "today",
    "stereotypes",
})


def coerce_gantt_diagram_style(
    value: GanttDiagramStyleLike,
) -> GanttDiagramStyle:
    """Convert a GanttDiagramStyleLike value to a GanttDiagramStyle object."""
    if isinstance(value, GanttDiagramStyle):
        return value
    _validate_style_dict_keys(value, _GANTT_DIAGRAM_STYLE_KEYS, "GanttDiagramStyle")
    return GanttDiagramStyle(
        background=_coerce_color_or_gradient(value.get("background")),
        font_name=value.get("font_name"),
        font_size=value.get("font_size"),
        font_color=coerce_color(value["font_color"])
        if "font_color" in value
        else None,
        task=coerce_element_style(value["task"]) if "task" in value else None,
        milestone=coerce_element_style(value["milestone"])
        if "milestone" in value
        else None,
        separator=coerce_element_style(value["separator"])
        if "separator" in value
        else None,
        note=coerce_element_style(value["note"]) if "note" in value else None,
        arrow=coerce_diagram_arrow_style(value["arrow"])
        if "arrow" in value
        else None,
        undone=coerce_element_style(value["undone"]) if "undone" in value else None,
        today=coerce_element_style(value["today"]) if "today" in value else None,
        stereotypes=_coerce_stereotypes(value.get("stereotypes")),
    )
