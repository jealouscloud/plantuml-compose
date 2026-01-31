"""Gantt chart diagram primitives.

Frozen dataclasses representing Gantt chart elements.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Literal, TypeAlias, TypedDict

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


# Day of week type
DayOfWeek = Literal[
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
]


@dataclass(frozen=True)
class GanttResource:
    """A resource (person/team) that can be assigned to tasks.

    Attributes:
        name: Resource identifier (e.g., "Alice", "Dev Team")
        off_days: Dates when this resource is unavailable
        allocation: Optional allocation percentage (e.g., 50 for 50%)
    """

    name: str
    off_days: tuple[date, ...] = field(default_factory=tuple)
    allocation: int | None = None


@dataclass(frozen=True)
class GanttTask:
    """A task in a Gantt chart.

    Attributes:
        name: Task display name
        duration_days: Duration in days
        duration_weeks: Duration in weeks (alternative to days)
        start_date: Explicit start date (optional, defaults to project start)
        end_date: Explicit end date
        alias: Short alias for referencing in dependencies
        completion: Completion percentage (0-100)
        color: Task bar color (can be "color" or "color1/color2" for fill/border)
        resources: Resources assigned to this task
        starts_after: Task alias this task starts after
        starts_with: Task alias this task starts with (same time)
        then: Task alias this task follows (alternative to starts_after)
        link: URL to link to
        on_same_row_as: Task alias to display on same row
        pauses_on: Dates when this task pauses
        pauses_on_days: Days of week when this task pauses
        is_deleted: If True, task is marked as deleted
        note: Note text to attach to this task
        note_position: Position of the note (bottom, left, right, top)
    """

    name: str
    duration_days: int | None = None
    duration_weeks: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    alias: str | None = None
    completion: int | None = None
    color: str | None = None  # "Color" or "Color1/Color2" format
    resources: tuple[GanttResource, ...] = field(default_factory=tuple)
    starts_after: str | None = None
    starts_with: str | None = None
    then: str | None = None
    link: str | None = None
    on_same_row_as: str | None = None
    pauses_on: tuple[date, ...] = field(default_factory=tuple)
    pauses_on_days: tuple[DayOfWeek, ...] = field(default_factory=tuple)
    is_deleted: bool = False
    note: str | None = None
    note_position: Literal["bottom", "left", "right", "top"] = "bottom"


@dataclass(frozen=True)
class GanttMilestone:
    """A milestone in a Gantt chart.

    Attributes:
        name: Milestone display name
        date: Specific date for the milestone
        happens_at: Task alias whose end triggers this milestone
        alias: Short alias for referencing
        color: Milestone marker color
        link: URL to link to
        note: Note text to attach to this milestone
        note_position: Position of the note (bottom, left, right, top)
    """

    name: str
    date: date | None = None
    happens_at: str | None = None
    alias: str | None = None
    color: str | None = None
    link: str | None = None
    note: str | None = None
    note_position: Literal["bottom", "left", "right", "top"] = "bottom"


@dataclass(frozen=True)
class GanttDependency:
    """A dependency arrow between tasks.

    Note: PlantUML Gantt arrows don't support inline styling.
    For styled links, use task.starts_after with link_color/link_style instead.

    Attributes:
        from_alias: Source task alias
        to_alias: Target task alias
    """

    from_alias: str
    to_alias: str


@dataclass(frozen=True)
class GanttSeparator:
    """A visual separator between task groups.

    Attributes:
        label: Optional text label for the separator
    """

    label: str | None = None


@dataclass(frozen=True)
class GanttClosedDateRange:
    """A date range that is closed (non-working).

    Attributes:
        start: Start date of the closed range
        end: End date of the closed range (inclusive)
    """

    start: date
    end: date


@dataclass(frozen=True)
class GanttOpenDate:
    """A date that is reopened (made working) even if in a closed range.

    Attributes:
        date: The date to reopen
    """

    date: date


@dataclass(frozen=True)
class GanttColoredDate:
    """A date with custom coloring.

    Attributes:
        date: The date to color
        color: The color to apply
    """

    date: date
    color: ColorLike


@dataclass(frozen=True)
class GanttColoredDateRange:
    """A date range with custom coloring.

    Attributes:
        start: Start date of the colored range
        end: End date of the colored range (inclusive)
        color: The color to apply
    """

    start: date
    end: date
    color: ColorLike


@dataclass(frozen=True)
class GanttVerticalSeparator:
    """A vertical separator line at a specific task's end.

    Attributes:
        after: Task alias after which to place the separator
    """

    after: str


@dataclass(frozen=True)
class GanttResourceOff:
    """Record that a resource is off on specific dates.

    Attributes:
        resource: Resource name
        dates: Dates when the resource is off
    """

    resource: str
    dates: tuple[date, ...]


# Type alias for elements that can appear in a Gantt chart
GanttElement = (
    GanttTask
    | GanttMilestone
    | GanttDependency
    | GanttSeparator
    | GanttVerticalSeparator
    | GanttResourceOff
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


class GanttDiagramStyleDict(TypedDict, total=False):
    """Dict form of GanttDiagramStyle for convenience."""

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


GanttDiagramStyleLike: TypeAlias = GanttDiagramStyle | GanttDiagramStyleDict

_GANTT_DIAGRAM_STYLE_KEYS: frozenset[str] = frozenset({
    "background", "font_name", "font_size", "font_color",
    "task", "milestone", "separator", "note", "arrow", "undone", "today",
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
    )


@dataclass(frozen=True)
class GanttDiagram:
    """A Gantt chart diagram.

    Attributes:
        elements: Ordered sequence of chart elements
        project_start: Project start date
        title: Chart title
        scale: Time scale for display
        scale_zoom: Zoom factor for the scale
        hide_footbox: Hide the footer with dates
        today: Mark today's date (or specific date)
        today_color: Color for today marker
        closed_days: Days of week that are closed
        closed_dates: Specific dates that are closed
        closed_date_ranges: Date ranges that are closed
        open_dates: Dates that are reopened
        colored_dates: Dates with custom coloring
        colored_date_ranges: Date ranges with custom coloring
        language: Locale for date formatting
        week_numbering: Enable week numbering (True/int for starting week)
        show_calendar_date: Show calendar dates
        week_starts_on: Day of week the week starts on
        min_days_in_first_week: Minimum days in the first week
        print_range: Range of dates to print (start, end)
        hide_resource_names: Hide resource names
        hide_resource_footbox: Hide resource footbox
        diagram_style: Diagram-wide styling
    """

    elements: tuple[GanttElement, ...] = field(default_factory=tuple)
    project_start: date | None = None
    title: str | None = None
    scale: Literal["daily", "weekly", "monthly", "quarterly", "yearly"] | None = None
    scale_zoom: int | None = None
    hide_footbox: bool = False
    today: date | None = None
    today_color: ColorLike | None = None
    closed_days: tuple[DayOfWeek, ...] = field(default_factory=tuple)
    closed_dates: tuple[date, ...] = field(default_factory=tuple)
    closed_date_ranges: tuple[GanttClosedDateRange, ...] = field(default_factory=tuple)
    open_dates: tuple[date, ...] = field(default_factory=tuple)
    colored_dates: tuple[GanttColoredDate, ...] = field(default_factory=tuple)
    colored_date_ranges: tuple[GanttColoredDateRange, ...] = field(default_factory=tuple)
    language: str | None = None
    week_numbering: int | bool | None = None
    show_calendar_date: bool = False
    week_starts_on: DayOfWeek | None = None
    min_days_in_first_week: int | None = None
    print_range: tuple[date, date] | None = None
    hide_resource_names: bool = False
    hide_resource_footbox: bool = False
    diagram_style: GanttDiagramStyle | None = None
