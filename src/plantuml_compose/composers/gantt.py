"""Gantt chart diagram composer.

Order-dependent with explicit dependencies via d.connect().

Example:
    d = gantt_diagram(title="Migration", start=date(2026, 4, 6))
    tk = d.tasks
    dep = d.dependencies

    d.close_days("saturday", "sunday")

    audit = tk.task("Audit", days=3)
    prep = tk.task("Prepare", days=5, color="#E3F2FD")
    d.add(audit, prep)

    d.connect(dep.after(prep, audit))

    puml = render(d)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Literal

from ..primitives.common import (
    ColorLike,
    ThemeLike,
)
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
    GanttOpenDate,
    GanttResource,
    GanttResourceOff,
    GanttSeparator,
    GanttTask,
    GanttVerticalSeparator,
    coerce_gantt_diagram_style,
)
from .base import BaseComposer, EntityRef


def _resolve_ref(item: EntityRef | str) -> str:
    """Resolve an EntityRef or raw string to a task alias."""
    if isinstance(item, EntityRef):
        return item._ref
    return item


# ---------------------------------------------------------------------------
# Internal data types returned by namespace factories
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _DependencyData:
    """Pure data for a dependency between tasks."""
    task: str | EntityRef
    predecessor: str | EntityRef | list[str | EntityRef]
    dep_type: Literal["after", "starts_with"]


# ---------------------------------------------------------------------------
# Namespaces
# ---------------------------------------------------------------------------


class GanttTaskNamespace:
    """Factory namespace for gantt diagram tasks and milestones."""

    _alias_counter: int = 0

    def _generate_alias(self) -> str:
        self._alias_counter += 1
        return f"_t{self._alias_counter}"

    def task(
        self,
        name: str,
        *,
        days: int | None = None,
        weeks: int | None = None,
        start: date | None = None,
        end: date | None = None,
        completion: int | None = None,
        color: str | None = None,
        resources: tuple[str, ...] = (),
        link: str | None = None,
        pauses_on: tuple[date, ...] = (),
        pauses_on_days: tuple[DayOfWeek, ...] = (),
        is_deleted: bool = False,
        working_days: bool = False,
        link_color: str | None = None,
        link_style: Literal["bold", "dashed", "dotted"] | None = None,
        note: str | None = None,
        note_position: Literal["bottom", "left", "right", "top"] = "bottom",
    ) -> EntityRef:
        alias = self._generate_alias()
        return EntityRef(
            name, ref=alias,
            data={
                "_type": "task",
                "days": days,
                "weeks": weeks,
                "start": start,
                "end": end,
                "completion": completion,
                "color": color,
                "resources": resources,
                "link": link,
                "pauses_on": pauses_on,
                "pauses_on_days": pauses_on_days,
                "is_deleted": is_deleted,
                "working_days": working_days,
                "link_color": link_color,
                "link_style": link_style,
                "note": note,
                "note_position": note_position,
                "_alias": alias,
            },
        )

    def milestone(
        self,
        name: str,
        *,
        on: date | None = None,
        color: str | None = None,
        link: str | None = None,
        note: str | None = None,
        note_position: Literal["bottom", "left", "right", "top"] = "bottom",
    ) -> EntityRef:
        alias = self._generate_alias()
        return EntityRef(
            name, ref=alias,
            data={
                "_type": "milestone",
                "on": on,
                "color": color,
                "link": link,
                "note": note,
                "note_position": note_position,
                "_alias": alias,
            },
        )


class GanttDependencyNamespace:
    """Factory namespace for gantt diagram dependencies."""

    def after(
        self,
        task: EntityRef | str,
        predecessor: EntityRef | str | list[EntityRef | str],
    ) -> _DependencyData | list[_DependencyData]:
        """B starts after A: dep.after(B, A).

        If predecessor is a list, returns a list of dependencies.
        """
        if isinstance(predecessor, list):
            return [
                _DependencyData(task=task, predecessor=p, dep_type="after")
                for p in predecessor
            ]
        return _DependencyData(
            task=task,
            predecessor=predecessor,
            dep_type="after",
        )

    def starts_with(
        self,
        task: EntityRef | str,
        other: EntityRef | str,
    ) -> _DependencyData:
        """B starts at the same time as A: dep.starts_with(B, A)."""
        return _DependencyData(
            task=task,
            predecessor=other,
            dep_type="starts_with",
        )


# ---------------------------------------------------------------------------
# Composer
# ---------------------------------------------------------------------------


class GanttComposer(BaseComposer):
    """Composer for gantt diagrams."""

    def __init__(
        self,
        *,
        title: str | None = None,
        mainframe: str | None = None,
        start: date | None = None,
        theme: ThemeLike = None,
        diagram_style: GanttDiagramStyleLike | None = None,
        hide_footbox: bool = False,
    ) -> None:
        super().__init__(title=title, mainframe=mainframe)
        self._start = start
        self._theme = theme
        self._diagram_style = (
            coerce_gantt_diagram_style(diagram_style) if diagram_style else None
        )
        self._hide_footbox = hide_footbox
        self._tasks_ns = GanttTaskNamespace()
        self._dependencies_ns = GanttDependencyNamespace()
        self._closed_days: list[DayOfWeek] = []
        self._closed_date_ranges: list[GanttClosedDateRange] = []
        self._open_dates: list[date] = []
        self._colored_dates: list[GanttColoredDate] = []
        self._colored_date_ranges: list[GanttColoredDateRange] = []
        self._today: date | None = None
        self._today_color: ColorLike | None = None

    @property
    def tasks(self) -> GanttTaskNamespace:
        return self._tasks_ns

    @property
    def dependencies(self) -> GanttDependencyNamespace:
        return self._dependencies_ns

    def separator(self, text: str = "") -> None:
        """Add a separator — interleaves with d.add() in order."""
        self._elements.append(("__separator__", text))

    def close_days(self, *days: DayOfWeek) -> None:
        """Mark days of the week as closed (non-working)."""
        self._closed_days.extend(days)

    def close_date_range(self, start: date, end: date) -> None:
        """Mark a date range as closed."""
        self._closed_date_ranges.append(GanttClosedDateRange(start=start, end=end))

    def open_date(self, d: date) -> None:
        """Reopen a specific date (overrides close_days/close_date_range)."""
        self._open_dates.append(d)

    def color_date(self, d: date, color: ColorLike) -> None:
        """Color a specific date on the chart."""
        self._colored_dates.append(GanttColoredDate(date=d, color=color))

    def color_date_range(self, start: date, end: date, color: ColorLike) -> None:
        """Color a date range on the chart."""
        self._colored_date_ranges.append(
            GanttColoredDateRange(start=start, end=end, color=color))

    def vertical_separator(self, after: EntityRef | str) -> None:
        """Add a vertical separator after a task."""
        self._elements.append(("__vsep__", after))

    def today(self, today_date: date | None = None, color: ColorLike | None = None) -> None:
        """Mark today's date on the chart."""
        self._today = today_date
        self._today_color = color

    def connect(self, *connections: Any) -> None:
        """Register dependencies.

        Accepts variadic args or a single list.
        """
        for c in connections:
            if isinstance(c, list):
                self._connections.extend(c)
            else:
                self._connections.append(c)

    def build(self) -> GanttDiagram:
        elements: list[GanttElement] = []

        # Build a mapping from EntityRef to alias for dependency resolution
        alias_map: dict[int, str] = {}

        # Process elements in order (preserves d.add() / d.separator() interleaving)
        for item in self._elements:
            if isinstance(item, tuple) and item[0] == "__separator__":
                elements.append(GanttSeparator(
                    label=item[1] if item[1] else None,
                ))
            elif isinstance(item, tuple) and item[0] == "__vsep__":
                elements.append(GanttVerticalSeparator(
                    after=_resolve_ref(item[1]),
                ))
            elif isinstance(item, EntityRef):
                data = item._data
                alias = data.get("_alias", item._ref)
                alias_map[id(item)] = alias

                if data.get("_type") == "milestone":
                    elements.append(GanttMilestone(
                        name=item._name,
                        alias=alias,
                        date=data.get("on"),
                        color=data.get("color"),
                        link=data.get("link"),
                        note=data.get("note"),
                        note_position=data.get("note_position", "bottom"),
                    ))
                else:
                    # Task — pass all params through
                    resources = tuple(
                        GanttResource(name=r) for r in data.get("resources", ())
                    )
                    elements.append(GanttTask(
                        name=item._name,
                        alias=alias,
                        duration_days=data.get("days"),
                        duration_weeks=data.get("weeks"),
                        start_date=data.get("start"),
                        end_date=data.get("end"),
                        completion=data.get("completion"),
                        color=data.get("color"),
                        resources=resources,
                        link=data.get("link"),
                        pauses_on=data.get("pauses_on", ()),
                        pauses_on_days=data.get("pauses_on_days", ()),
                        is_deleted=data.get("is_deleted", False),
                        working_days=data.get("working_days", False),
                        link_color=data.get("link_color"),
                        link_style=data.get("link_style"),
                        note=data.get("note"),
                        note_position=data.get("note_position", "bottom"),
                    ))

        # Process dependencies — resolve to aliases and attach
        # We need to figure out starts_after and starts_with on the tasks,
        # and also create GanttDependency arrows for additional predecessors.
        #
        # Strategy: collect all dependencies, then retroactively set
        # starts_after / starts_with on tasks by rebuilding the elements list.

        dep_after: dict[str, list[str]] = {}  # task_alias -> [predecessor_aliases]
        dep_starts_with: dict[str, str] = {}  # task_alias -> other_alias

        for conn in self._connections:
            if isinstance(conn, _DependencyData):
                task_alias = self._resolve_alias(conn.task)
                if conn.dep_type == "after":
                    pred_alias = self._resolve_alias(conn.predecessor)
                    dep_after.setdefault(task_alias, []).append(pred_alias)
                elif conn.dep_type == "starts_with":
                    other_alias = self._resolve_alias(conn.predecessor)
                    dep_starts_with[task_alias] = other_alias

        # Rebuild elements with dependencies applied
        rebuilt: list[GanttElement] = []
        for elem in elements:
            if isinstance(elem, GanttTask) and elem.alias:
                alias = elem.alias
                starts_after = None
                starts_with_val = dep_starts_with.get(alias)
                after_list = dep_after.get(alias, [])

                if after_list:
                    starts_after = after_list[0]

                rebuilt.append(GanttTask(
                    name=elem.name,
                    alias=elem.alias,
                    duration_days=elem.duration_days,
                    duration_weeks=elem.duration_weeks,
                    start_date=elem.start_date,
                    end_date=elem.end_date,
                    completion=elem.completion,
                    color=elem.color,
                    resources=elem.resources,
                    link=elem.link,
                    pauses_on=elem.pauses_on,
                    pauses_on_days=elem.pauses_on_days,
                    is_deleted=elem.is_deleted,
                    working_days=elem.working_days,
                    link_color=elem.link_color,
                    link_style=elem.link_style,
                    note=elem.note,
                    note_position=elem.note_position,
                    starts_after=starts_after,
                    starts_with=starts_with_val,
                ))

                # Additional dependencies become GanttDependency arrows
                for extra_pred in after_list[1:]:
                    rebuilt.append(GanttDependency(
                        from_alias=extra_pred,
                        to_alias=alias,
                    ))

            elif isinstance(elem, GanttMilestone) and elem.alias:
                alias = elem.alias
                after_list = dep_after.get(alias, [])
                happens_at = after_list[0] if after_list else None

                rebuilt.append(GanttMilestone(
                    name=elem.name,
                    alias=elem.alias,
                    date=elem.date,
                    color=elem.color,
                    link=elem.link,
                    note=elem.note,
                    note_position=elem.note_position,
                    happens_at=happens_at,
                ))

                # Additional dependencies
                for extra_pred in after_list[1:]:
                    rebuilt.append(GanttDependency(
                        from_alias=extra_pred,
                        to_alias=alias,
                    ))
            else:
                rebuilt.append(elem)

        return GanttDiagram(
            elements=tuple(rebuilt),
            project_start=self._start,
            title=self._title,
            mainframe=self._mainframe,
            closed_days=tuple(self._closed_days),
            closed_date_ranges=tuple(self._closed_date_ranges),
            open_dates=tuple(self._open_dates),
            colored_dates=tuple(self._colored_dates),
            colored_date_ranges=tuple(self._colored_date_ranges),
            today=self._today,
            today_color=self._today_color,
            hide_footbox=self._hide_footbox,
            diagram_style=self._diagram_style,
        )

    def _resolve_alias(self, item: EntityRef | str) -> str:
        """Resolve to alias string."""
        if isinstance(item, EntityRef):
            alias = item._data.get("_alias")
            if alias:
                return alias
            return item._ref
        return item


def gantt_diagram(
    *,
    title: str | None = None,
    mainframe: str | None = None,
    start: date | None = None,
    theme: ThemeLike = None,
    diagram_style: GanttDiagramStyleLike | None = None,
    hide_footbox: bool = False,
) -> GanttComposer:
    """Create a gantt diagram composer.

    Example:
        d = gantt_diagram(title="Migration", start=date(2026, 4, 6))
        tk = d.tasks
        dep = d.dependencies
        d.close_days("saturday", "sunday")
        audit = tk.task("Audit", days=3)
        prep = tk.task("Prepare", days=5)
        d.add(audit, prep)
        d.connect(dep.after(prep, audit))
        print(render(d))
    """
    return GanttComposer(
        title=title, mainframe=mainframe,
        start=start, theme=theme,
        diagram_style=diagram_style,
        hide_footbox=hide_footbox,
    )
