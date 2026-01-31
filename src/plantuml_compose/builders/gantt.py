"""Gantt chart diagram builders.

Provides context-manager based builders for Gantt chart diagrams.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from typing import Literal

from ..primitives.gantt import (
    DayOfWeek,
    GanttClosedDateRange,
    GanttColoredDate,
    GanttColoredDateRange,
    GanttDependency,
    GanttDiagram,
    GanttDiagramStyle,
    GanttDiagramStyleLike,
    GanttElement,
    GanttMilestone,
    GanttResource,
    GanttResourceOff,
    GanttSeparator,
    GanttTask,
    GanttVerticalSeparator,
    coerce_gantt_diagram_style,
)
from ..renderers import render as render_diagram


class ElementRef:
    """Reference to a Gantt element (task or milestone) for use in dependencies.

    Users should treat this as an opaque reference. Pass it to `after=` parameters
    to establish dependencies between tasks. The internal alias is an implementation
    detail that should not be accessed directly.
    """

    __slots__ = ("_alias", "_name")

    def __init__(self, alias: str, name: str) -> None:
        self._alias = alias
        self._name = name

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self._name!r}>"


# Type aliases for clarity in API
TaskRef = ElementRef
MilestoneRef = ElementRef


class GanttDiagramBuilder:
    """Builder for Gantt chart diagrams."""

    # Explicit type annotations to preserve Literal types
    _scale: Literal["daily", "weekly", "monthly", "quarterly", "yearly"] | None
    _week_starts_on: DayOfWeek | None

    def __init__(
        self,
        project_start: date | None,
        title: str | None,
        scale: Literal["daily", "weekly", "monthly", "quarterly", "yearly"] | None,
        scale_zoom: int | None,
        hide_footbox: bool,
        language: str | None,
        week_numbering: int | bool | None,
        show_calendar_date: bool,
        week_starts_on: DayOfWeek | None,
        min_days_in_first_week: int | None,
        print_range: tuple[date, date] | None,
        hide_resource_names: bool,
        hide_resource_footbox: bool,
        diagram_style: GanttDiagramStyle | None,
    ) -> None:
        self._project_start = project_start
        self._title = title
        self._scale = scale
        self._scale_zoom = scale_zoom
        self._hide_footbox = hide_footbox
        self._language = language
        self._week_numbering = week_numbering
        self._show_calendar_date = show_calendar_date
        self._week_starts_on = week_starts_on
        self._min_days_in_first_week = min_days_in_first_week
        self._print_range = print_range
        self._hide_resource_names = hide_resource_names
        self._hide_resource_footbox = hide_resource_footbox
        self._diagram_style = diagram_style
        self._elements: list[GanttElement] = []
        self._closed_days: set[DayOfWeek] = set()
        self._closed_dates: set[date] = set()
        self._closed_date_ranges: list[GanttClosedDateRange] = []
        self._open_dates: set[date] = set()
        self._colored_dates: list[GanttColoredDate] = []
        self._colored_date_ranges: list[GanttColoredDateRange] = []
        self._today: date | None = None
        self._today_color: str | None = None
        self._alias_counter = 0

    def _generate_alias(self) -> str:
        """Generate a unique internal alias."""
        self._alias_counter += 1
        return f"_t{self._alias_counter}"

    def _resolve_after(
        self, after: TaskRef | MilestoneRef | list[TaskRef | MilestoneRef] | None
    ) -> str | list[str] | None:
        """Resolve after parameter to alias string(s)."""
        if after is None:
            return None
        if isinstance(after, list):
            return [ref._alias for ref in after]
        return after._alias

    def task(
        self,
        name: str,
        *,
        days: int | None = None,
        weeks: int | None = None,
        start: date | None = None,
        end: date | None = None,
        after: TaskRef | MilestoneRef | list[TaskRef | MilestoneRef] | None = None,
        starts_with: TaskRef | MilestoneRef | None = None,
        then: TaskRef | MilestoneRef | None = None,
        resources: list[str | tuple[str, int]] | None = None,
        completed: int | None = None,
        color: str | None = None,
        link: str | None = None,
        same_row_as: TaskRef | None = None,
        pauses_on: list[date | DayOfWeek] | None = None,
        deleted: bool = False,
        note: str | None = None,
    ) -> TaskRef:
        """Add a task to the diagram.

        Args:
            name: Task display name
            days: Duration in days
            weeks: Duration in weeks (converted to days)
            start: Explicit start date
            end: Explicit end date
            after: Task(s) this task starts after
            starts_with: Task this task starts at the same time as
            then: Task this task follows (alternative to after, mutually exclusive)
            resources: List of resource names or (name, allocation%) tuples
            completed: Completion percentage (0-100)
            color: Task bar color ("Color" or "Color1/Color2" for fill/border)
            link: URL to link to
            same_row_as: Task to display on the same row as
            pauses_on: Dates or days of week when this task pauses
            deleted: Mark task as deleted
            note: Note text to attach to this task (displays below)

        Returns:
            TaskRef for use in dependencies

        Raises:
            ValueError: If both days and weeks specified, or both after and then

        Example:
            design = d.task("Design", weeks=2)
            impl = d.task("Implementation", weeks=3, after=design)
            # With explicit dates
            testing = d.task("Testing", start=date(2024, 2, 1), end=date(2024, 2, 15))
            # With resource allocation
            dev = d.task("Development", weeks=4, resources=[("Alice", 100), ("Bob", 50)])
        """
        if days is not None and weeks is not None:
            raise ValueError("Specify either days or weeks, not both")

        if after is not None and then is not None:
            raise ValueError("Specify either after or then, not both")

        alias = self._generate_alias()

        # Build resources with optional allocation
        resource_objs: list[GanttResource] = []
        for r in resources or []:
            if isinstance(r, tuple):
                resource_objs.append(GanttResource(name=r[0], allocation=r[1]))
            else:
                resource_objs.append(GanttResource(name=r))

        # Handle after - can be single ref or list
        starts_after: str | None = None
        after_resolved = self._resolve_after(after)
        if isinstance(after_resolved, str):
            starts_after = after_resolved
        elif isinstance(after_resolved, list) and len(after_resolved) >= 1:
            # First dependency goes to starts_after, rest become arrows
            starts_after = after_resolved[0]

        # Handle then sequencing
        then_alias: str | None = None
        if then is not None:
            then_alias = then._alias

        # Handle starts_with
        starts_with_alias: str | None = None
        if starts_with is not None:
            starts_with_alias = starts_with._alias

        # Handle same_row_as
        same_row_alias: str | None = None
        if same_row_as is not None:
            same_row_alias = same_row_as._alias

        # Handle pauses_on - separate dates from days of week
        pause_dates: list[date] = []
        pause_days: list[DayOfWeek] = []
        for item in pauses_on or []:
            if isinstance(item, date):
                pause_dates.append(item)
            else:
                pause_days.append(item)

        task = GanttTask(
            name=name,
            duration_days=days,
            duration_weeks=weeks,
            start_date=start,
            end_date=end,
            alias=alias,
            completion=completed,
            color=color,
            resources=tuple(resource_objs),
            starts_after=starts_after,
            starts_with=starts_with_alias,
            then=then_alias,
            link=link,
            on_same_row_as=same_row_alias,
            pauses_on=tuple(pause_dates),
            pauses_on_days=tuple(pause_days),
            is_deleted=deleted,
            note=note,
        )
        self._elements.append(task)

        # If multiple after dependencies, add arrows for the extras
        if isinstance(after_resolved, list) and len(after_resolved) > 1:
            for dep_alias in after_resolved[1:]:
                self._elements.append(GanttDependency(from_alias=dep_alias, to_alias=alias))

        return TaskRef(alias=alias, name=name)

    def milestone(
        self,
        name: str,
        *,
        on: date | None = None,
        after: TaskRef | MilestoneRef | None = None,
        color: str | None = None,
        link: str | None = None,
        note: str | None = None,
    ) -> MilestoneRef:
        """Add a milestone to the diagram.

        Args:
            name: Milestone display name
            on: Specific date for the milestone
            after: Task whose completion triggers this milestone
            color: Milestone marker color
            link: URL to link to
            note: Note text to attach to this milestone (displays below)

        Returns:
            MilestoneRef for use in dependencies
        """
        alias = self._generate_alias()
        happens_at = after._alias if after else None

        milestone = GanttMilestone(
            name=name,
            date=on,
            happens_at=happens_at,
            alias=alias,
            color=color,
            link=link,
            note=note,
        )
        self._elements.append(milestone)
        return MilestoneRef(alias=alias, name=name)

    def separator(self, label: str | None = None) -> None:
        """Add a visual separator between task groups.

        Args:
            label: Optional text label for the separator
        """
        self._elements.append(GanttSeparator(label=label))

    def vertical_separator(self, after: TaskRef | MilestoneRef) -> None:
        """Add a vertical separator line after a specific task or milestone.

        Args:
            after: Task or milestone after which to place the separator
        """
        self._elements.append(GanttVerticalSeparator(after=after._alias))

    def close_weekends(self) -> None:
        """Mark weekends (Saturday and Sunday) as closed."""
        self._closed_days.add("saturday")
        self._closed_days.add("sunday")

    def close_days(self, *days: DayOfWeek) -> None:
        """Mark days of the week as closed (non-working).

        Args:
            days: Days of week to close
        """
        self._closed_days.update(days)

    def close_dates(self, *dates: date) -> None:
        """Mark specific dates as closed (holidays, etc.).

        Args:
            dates: Specific dates to mark as closed
        """
        self._closed_dates.update(dates)

    def close_date_range(self, start: date, end: date) -> None:
        """Mark a date range as closed (non-working).

        Args:
            start: Start date of the closed range
            end: End date of the closed range (inclusive)
        """
        self._closed_date_ranges.append(GanttClosedDateRange(start=start, end=end))

    def open_date(self, d: date) -> None:
        """Reopen a date that was previously closed.

        Use this to make specific dates working even if they fall within
        a closed range or on a closed day of the week.

        Args:
            d: The date to reopen
        """
        self._open_dates.add(d)

    def open_dates(self, *dates: date) -> None:
        """Reopen multiple dates that were previously closed.

        Args:
            dates: The dates to reopen
        """
        self._open_dates.update(dates)

    def color_date(self, d: date, color: str) -> None:
        """Apply a custom color to a specific date.

        Args:
            d: The date to color
            color: The color to apply
        """
        self._colored_dates.append(GanttColoredDate(date=d, color=color))

    def color_date_range(self, start: date, end: date, color: str) -> None:
        """Apply a custom color to a date range.

        Args:
            start: Start date of the colored range
            end: End date of the colored range (inclusive)
            color: The color to apply
        """
        self._colored_date_ranges.append(
            GanttColoredDateRange(start=start, end=end, color=color)
        )

    def resource_off(self, resource: str, *dates: date) -> None:
        """Mark dates when a resource is unavailable.

        Args:
            resource: Resource name
            dates: Dates when the resource is off
        """
        self._elements.append(GanttResourceOff(resource=resource, dates=tuple(dates)))

    def today(self, today_date: date, color: str | None = None) -> None:
        """Mark today's date on the chart.

        Args:
            today_date: The date to mark as today
            color: Color for the today marker
        """
        self._today = today_date
        self._today_color = color

    def build(self) -> GanttDiagram:
        """Build the Gantt diagram primitive."""
        return GanttDiagram(
            elements=tuple(self._elements),
            project_start=self._project_start,
            title=self._title,
            scale=self._scale,
            scale_zoom=self._scale_zoom,
            hide_footbox=self._hide_footbox,
            today=self._today,
            today_color=self._today_color,
            closed_days=tuple(self._closed_days),
            closed_dates=tuple(self._closed_dates),
            closed_date_ranges=tuple(self._closed_date_ranges),
            open_dates=tuple(self._open_dates),
            colored_dates=tuple(self._colored_dates),
            colored_date_ranges=tuple(self._colored_date_ranges),
            language=self._language,
            week_numbering=self._week_numbering,
            show_calendar_date=self._show_calendar_date,
            week_starts_on=self._week_starts_on,
            min_days_in_first_week=self._min_days_in_first_week,
            print_range=self._print_range,
            hide_resource_names=self._hide_resource_names,
            hide_resource_footbox=self._hide_resource_footbox,
            diagram_style=self._diagram_style,
        )

    def render(self) -> str:
        """Build and render the diagram to PlantUML text."""
        return render_diagram(self.build())


@contextmanager
def gantt_diagram(
    *,
    start: date | None = None,
    title: str | None = None,
    scale: Literal["daily", "weekly", "monthly", "quarterly", "yearly"] | None = None,
    scale_zoom: int | None = None,
    hide_footbox: bool = False,
    language: str | None = None,
    week_numbering: int | bool | None = None,
    show_calendar_date: bool = False,
    week_starts_on: DayOfWeek | None = None,
    min_days_in_first_week: int | None = None,
    print_range: tuple[date, date] | None = None,
    hide_resource_names: bool = False,
    hide_resource_footbox: bool = False,
    diagram_style: GanttDiagramStyleLike | None = None,
) -> Iterator[GanttDiagramBuilder]:
    """Create a Gantt chart diagram.

    Args:
        start: Project start date
        title: Chart title
        scale: Time scale for display (daily, weekly, monthly, quarterly, yearly)
        scale_zoom: Zoom factor for the scale
        hide_footbox: Hide the footer with dates
        language: Locale for date formatting (e.g., "de", "ja")
        week_numbering: Enable week numbering (True or starting week number)
        show_calendar_date: Show calendar dates on tasks
        week_starts_on: Day of week that starts the week
        min_days_in_first_week: Minimum days required in the first week
        print_range: Range of dates to print (start, end)
        hide_resource_names: Hide resource names from tasks
        hide_resource_footbox: Hide resource footbox
        diagram_style: Diagram-wide styling (GanttDiagramStyle or dict)

    Yields:
        GanttDiagramBuilder for adding tasks and milestones

    Example:
        from datetime import date

        with gantt_diagram(start=date(2024, 1, 1)) as d:
            d.close_weekends()

            design = d.task("Design", weeks=2, resources=["Alice"])
            backend = d.task("Backend", weeks=3, after=design, resources=["Bob"])
            frontend = d.task("Frontend", weeks=3, after=design)

            integration = d.task("Integration", weeks=1, after=[backend, frontend])
            testing = d.task("Testing", weeks=2, after=integration)

            d.milestone("Release", after=testing)

        print(d.render())
    """
    # Coerce diagram style if provided as dict
    style: GanttDiagramStyle | None = None
    if diagram_style is not None:
        style = coerce_gantt_diagram_style(diagram_style)

    builder = GanttDiagramBuilder(
        project_start=start,
        title=title,
        scale=scale,
        scale_zoom=scale_zoom,
        hide_footbox=hide_footbox,
        language=language,
        week_numbering=week_numbering,
        show_calendar_date=show_calendar_date,
        week_starts_on=week_starts_on,
        min_days_in_first_week=min_days_in_first_week,
        print_range=print_range,
        hide_resource_names=hide_resource_names,
        hide_resource_footbox=hide_resource_footbox,
        diagram_style=style,
    )
    yield builder
