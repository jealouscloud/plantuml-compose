"""Gantt chart diagram renderers.

Pure functions that transform Gantt diagram primitives to PlantUML text.
"""

from __future__ import annotations

from datetime import date

from ..primitives.gantt import (
    GanttDependency,
    GanttDiagram,
    GanttDiagramStyle,
    GanttMilestone,
    GanttResourceOff,
    GanttSeparator,
    GanttTask,
    GanttVerticalSeparator,
)
from .common import (
    render_color,
    render_diagram_style,
)


def render_gantt_diagram(diagram: GanttDiagram) -> str:
    """Render a complete Gantt chart to PlantUML text."""
    lines: list[str] = ["@startgantt"]

    # Title
    if diagram.title:
        lines.append(f"title {diagram.title}")

    # Language (must come early)
    if diagram.language:
        lines.append(f"language {diagram.language}")

    # Diagram style
    if diagram.diagram_style:
        lines.extend(_render_gantt_diagram_style(diagram.diagram_style))

    # Scale with optional week numbering / calendar date
    if diagram.scale:
        scale_line = f"printscale {diagram.scale}"
        if diagram.scale_zoom:
            scale_line += f" zoom {diagram.scale_zoom}"
        # Week numbering applies to weekly scale
        if diagram.scale == "weekly" and diagram.week_numbering is not None:
            if diagram.week_numbering is True:
                pass  # Default week numbering, no extra syntax needed
            elif isinstance(diagram.week_numbering, int):
                scale_line += f" with week numbering from {diagram.week_numbering}"
        # Calendar date display (works with any scale)
        if diagram.show_calendar_date:
            scale_line += " with calendar date"
        lines.append(scale_line)
    elif diagram.week_numbering is not None or diagram.show_calendar_date:
        # If no scale specified but week_numbering or calendar_date requested,
        # default to weekly scale
        scale_line = "printscale weekly"
        # Only add "with week numbering from X" if it's a specific starting number.
        # Note: isinstance(True, int) returns True in Python, so exclude bool explicitly
        if isinstance(diagram.week_numbering, int) and diagram.week_numbering is not True:
            scale_line += f" with week numbering from {diagram.week_numbering}"
        if diagram.show_calendar_date:
            scale_line += " with calendar date"
        lines.append(scale_line)

    # Project start date
    if diagram.project_start:
        lines.append(f"Project starts {_format_date(diagram.project_start)}")

    # Week start day (with optional min days)
    if diagram.week_starts_on:
        week_line = f"weeks starts on {diagram.week_starts_on}"
        if diagram.min_days_in_first_week is not None:
            week_line += f" and must have at least {diagram.min_days_in_first_week} days"
        lines.append(week_line)

    # Minimum days in first week (only if week_starts_on is not set)
    if diagram.min_days_in_first_week is not None and diagram.week_starts_on is None:
        lines.append(f"weeks starts and must have at least {diagram.min_days_in_first_week} days")

    # Print range
    if diagram.print_range:
        start, end = diagram.print_range
        lines.append(f"printbetween {_format_date(start)} and {_format_date(end)}")

    # Closed days of week
    for day in diagram.closed_days:
        lines.append(f"{day} are closed")

    # Closed specific dates
    for closed_date in diagram.closed_dates:
        lines.append(f"{_format_date(closed_date)} is closed")

    # Closed date ranges
    for closed_range in diagram.closed_date_ranges:
        lines.append(
            f"{_format_date(closed_range.start)} to "
            f"{_format_date(closed_range.end)} is closed"
        )

    # Open dates (reopen closed days)
    for open_date in diagram.open_dates:
        lines.append(f"{_format_date(open_date)} is open")

    # Colored dates
    for colored_date in diagram.colored_dates:
        lines.append(
            f"{_format_date(colored_date.date)} is colored in "
            f"{render_color(colored_date.color)}"
        )

    # Colored date ranges
    for colored_range in diagram.colored_date_ranges:
        lines.append(
            f"{_format_date(colored_range.start)} to "
            f"{_format_date(colored_range.end)} are colored in "
            f"{render_color(colored_range.color)}"
        )

    # Today marker
    if diagram.today:
        lines.append(f"today is {_format_date(diagram.today)}")
    if diagram.today_color:
        lines.append(f"today is colored in {render_color(diagram.today_color)}")

    # Hide footbox
    if diagram.hide_footbox:
        lines.append("hide footbox")

    # Hide resource names
    if diagram.hide_resource_names:
        lines.append("hide resources names")

    # Hide resource footbox
    if diagram.hide_resource_footbox:
        lines.append("hide resources footbox")

    # Render elements
    for element in diagram.elements:
        if isinstance(element, GanttTask):
            lines.extend(_render_task(element))
        elif isinstance(element, GanttMilestone):
            lines.extend(_render_milestone(element))
        elif isinstance(element, GanttDependency):
            lines.append(_render_dependency(element))
        elif isinstance(element, GanttSeparator):
            lines.append(_render_separator(element))
        elif isinstance(element, GanttVerticalSeparator):
            lines.append(_render_vertical_separator(element))
        elif isinstance(element, GanttResourceOff):
            lines.extend(_render_resource_off(element))

    lines.append("@endgantt")
    return "\n".join(lines)


def _format_date(d: date) -> str:
    """Format a date for PlantUML Gantt (YYYY-MM-DD)."""
    return d.strftime("%Y-%m-%d")


def _render_task(task: GanttTask) -> list[str]:
    """Render a GanttTask to PlantUML lines."""
    lines: list[str] = []

    # Build task definition line
    # Format: [Task Name] as [alias] on {Resource} lasts/requires N days
    parts: list[str] = [f"[{task.name}]"]

    if task.alias:
        parts.append(f"as [{task.alias}]")

    # Resources: first one gets "on", subsequent ones are just {name}
    for i, resource in enumerate(task.resources):
        if resource.allocation:
            res_str = f"{{{resource.name}:{resource.allocation}%}}"
        else:
            res_str = f"{{{resource.name}}}"
        if i == 0:
            parts.append(f"on {res_str}")
        else:
            parts.append(res_str)

    # Duration or dates
    if task.duration_weeks is not None:
        unit = "week" if task.duration_weeks == 1 else "weeks"
        parts.append(f"lasts {task.duration_weeks} {unit}")
    elif task.duration_days is not None:
        unit = "day" if task.duration_days == 1 else "days"
        parts.append(f"lasts {task.duration_days} {unit}")
    elif task.start_date and task.end_date:
        parts.append(f"starts {_format_date(task.start_date)}")
        parts.append(f"and ends {_format_date(task.end_date)}")
    elif task.start_date:
        parts.append(f"starts {_format_date(task.start_date)}")
    elif task.end_date:
        parts.append(f"ends {_format_date(task.end_date)}")

    lines.append(" ".join(parts))

    # Additional task properties (separate lines)
    task_ref = f"[{task.alias}]" if task.alias else f"[{task.name}]"

    # then sequencing (alternative to starts_after)
    if task.then:
        lines.append(f"{task_ref} starts at [{task.then}]'s end")
    elif task.starts_after:
        lines.append(f"{task_ref} starts at [{task.starts_after}]'s end")

    if task.starts_with:
        lines.append(f"{task_ref} starts at [{task.starts_with}]'s start")

    if task.completion is not None:
        lines.append(f"{task_ref} is {task.completion}% complete")

    if task.color:
        lines.append(f"{task_ref} is colored in {task.color}")

    if task.link:
        lines.append(f"{task_ref} links to [[{task.link}]]")

    if task.on_same_row_as:
        lines.append(f"{task_ref} displays on same row as [{task.on_same_row_as}]")

    for pause_date in task.pauses_on:
        lines.append(f"{task_ref} pauses on {_format_date(pause_date)}")

    for pause_day in task.pauses_on_days:
        lines.append(f"{task_ref} pauses on {pause_day}")

    if task.is_deleted:
        lines.append(f"{task_ref} is deleted")

    # Resource off days
    for resource in task.resources:
        for off_date in resource.off_days:
            lines.append(f"{{{resource.name}}} is off on {_format_date(off_date)}")

    # Note (must come after task definition)
    if task.note:
        lines.extend(_render_note(task.note, task.note_position))

    return lines


def _render_milestone(milestone: GanttMilestone) -> list[str]:
    """Render a GanttMilestone to PlantUML lines."""
    lines: list[str] = []
    parts: list[str] = [f"[{milestone.name}]"]

    if milestone.alias:
        parts.append(f"as [{milestone.alias}]")

    if milestone.date:
        parts.append(f"happens {_format_date(milestone.date)}")
    elif milestone.happens_at:
        parts.append(f"happens at [{milestone.happens_at}]'s end")

    lines.append(" ".join(parts))

    # Milestone reference for additional properties
    milestone_ref = f"[{milestone.alias}]" if milestone.alias else f"[{milestone.name}]"

    # Color must be on separate line
    if milestone.color:
        lines.append(f"{milestone_ref} is colored in {milestone.color}")

    # Link
    if milestone.link:
        lines.append(f"{milestone_ref} links to [[{milestone.link}]]")

    # Note (must come after milestone definition)
    if milestone.note:
        lines.extend(_render_note(milestone.note, milestone.note_position))

    return lines


def _render_dependency(dep: GanttDependency) -> str:
    """Render a GanttDependency to PlantUML."""
    return f"[{dep.from_alias}] -> [{dep.to_alias}]"


def _render_separator(sep: GanttSeparator) -> str:
    """Render a GanttSeparator to PlantUML."""
    if sep.label:
        return f"-- {sep.label} --"
    return "----"


def _render_vertical_separator(sep: GanttVerticalSeparator) -> str:
    """Render a GanttVerticalSeparator to PlantUML."""
    return f"Separator just at [{sep.after}]'s end"


def _render_resource_off(resource_off: GanttResourceOff) -> list[str]:
    """Render GanttResourceOff to PlantUML lines."""
    lines: list[str] = []
    for off_date in resource_off.dates:
        lines.append(f"{{{resource_off.resource}}} is off on {_format_date(off_date)}")
    return lines


def _render_note(text: str, position: str) -> list[str]:
    """Render a note block to PlantUML lines.

    PlantUML Gantt requires a blank line after 'end note' before the next element.
    """
    lines: list[str] = [f"note {position}"]
    lines.extend(text.split("\n"))
    lines.append("end note")
    lines.append("")  # Required blank line
    return lines


def _render_gantt_diagram_style(style: GanttDiagramStyle) -> list[str]:
    """Render GanttDiagramStyle as PlantUML <style> block."""
    element_styles: list[tuple[str, object]] = [
        ("task", style.task),
        ("milestone", style.milestone),
        ("separator", style.separator),
        ("note", style.note),
        ("undone", style.undone),
        ("today", style.today),
    ]

    return render_diagram_style(
        diagram_type="ganttDiagram",
        root_background=style.background,
        root_font_name=style.font_name,
        root_font_size=style.font_size,
        root_font_color=style.font_color,
        element_styles=element_styles,  # type: ignore[arg-type]
        arrow_style=style.arrow,
        title_style=None,
    )
