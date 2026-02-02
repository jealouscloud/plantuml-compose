# Gantt Chart Diagrams

Gantt charts are bar charts that visualize project schedules. They're essential for:

- **Project planning**: See tasks, durations, and deadlines at a glance
- **Resource management**: Track who's working on what and when
- **Dependency tracking**: Understand which tasks block others
- **Progress monitoring**: Show completion status of ongoing work

A Gantt chart shows time on the horizontal axis and tasks on the vertical axis, with bars representing task duration.

## Core Concepts

**Task**: A unit of work with a name, duration, and optionally a start/end date.

**Milestone**: A significant point in time (zero duration), often marking phase completion.

**Dependency**: A relationship where one task must complete before another starts.

**Resource**: A person or team assigned to work on tasks.

**Project start**: The baseline date from which relative task positions are calculated.

## Your First Gantt Chart

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    design = d.task("Design", days=5)
    develop = d.task("Develop", days=10, after=design)
    test = d.task("Test", days=3, after=develop)

print(d.render())
```

This creates a simple project with three sequential tasks. Each task starts after the previous one completes.

## Task Duration

### Duration in Days

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    d.task("Short task", days=3)
    d.task("Medium task", days=7)
    d.task("Long task", days=14)

print(d.render())
```

### Duration in Weeks

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    d.task("Sprint 1", weeks=2)
    d.task("Sprint 2", weeks=2)
    d.task("Sprint 3", weeks=2)

print(d.render())
```

### Explicit Start and End Dates

When using explicit dates for tasks, you must also set a project start date:

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    d.task("Q1 Planning", start=date(2024, 1, 1), end=date(2024, 1, 15))
    d.task("Q1 Execution", start=date(2024, 1, 16), end=date(2024, 3, 31))

print(d.render())
```

## Task Dependencies

### Sequential Tasks (after)

Use `after=` to make a task start when another completes:

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    requirements = d.task("Requirements", days=5)
    design = d.task("Design", days=7, after=requirements)
    implementation = d.task("Implementation", days=14, after=design)
    testing = d.task("Testing", days=5, after=implementation)

print(d.render())
```

### Multiple Dependencies

A task can depend on multiple predecessors:

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    design = d.task("Design", days=5)

    # These two tasks start after design, but run in parallel
    backend = d.task("Backend", days=10, after=design)
    frontend = d.task("Frontend", days=10, after=design)

    # Integration waits for BOTH backend and frontend
    integration = d.task("Integration", days=5, after=[backend, frontend])

print(d.render())
```

### Parallel Tasks Starting Together (starts_with)

Use `starts_with=` to make tasks begin at the same time:

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    design = d.task("Design", days=5)

    backend = d.task("Backend", days=10, after=design)
    # Frontend starts at the same time as Backend
    frontend = d.task("Frontend", days=8, starts_with=backend)

print(d.render())
```

## Milestones

Milestones mark significant points in time with zero duration:

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    planning = d.task("Planning", days=5)
    d.milestone("Plan Approved", after=planning)

    development = d.task("Development", days=20, after=planning)
    d.milestone("Code Complete", after=development)

    testing = d.task("Testing", days=10, after=development)
    d.milestone("Release", after=testing)

print(d.render())
```

### Milestone on Specific Date

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    d.task("Development", days=30)
    d.milestone("Board Meeting", on=date(2024, 1, 15))
    d.milestone("Product Launch", on=date(2024, 2, 1))

print(d.render())
```

## Working with Resources

### Assigning Resources to Tasks

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    d.task("Design", days=5, resources=["Alice"])
    d.task("Backend", days=10, resources=["Bob"])
    d.task("Frontend", days=10, resources=["Carol"])
    d.task("Testing", days=5, resources=["Alice", "Bob"])

print(d.render())
```

### Resource Allocation Percentage

Specify how much of a resource's time is allocated:

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    # Alice at 100%, Bob at 50%
    d.task("Main Project", days=10, resources=[("Alice", 100), ("Bob", 50)])
    # Bob's other 50%
    d.task("Side Project", days=10, resources=[("Bob", 50)])

print(d.render())
```

### Resource Days Off

Mark when specific resources are unavailable:

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    d.task("Development", days=10, resources=["Alice"])

    # Alice is on vacation these days
    d.resource_off("Alice", date(2024, 1, 8), date(2024, 1, 9))

print(d.render())
```

### Hide Resource Names

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1), hide_resource_names=True) as d:
    d.task("Task 1", days=5, resources=["Alice"])
    d.task("Task 2", days=5, resources=["Bob"])

print(d.render())
```

## Calendar and Working Days

### Close Weekends

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    d.close_weekends()  # Saturday and Sunday are non-working

    d.task("Development", days=10)  # Actual calendar span will be longer

print(d.render())
```

### Close Specific Days of the Week

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    # Company only works Monday-Thursday
    d.close_days("friday", "saturday", "sunday")

    d.task("Development", days=8)  # 8 working days = 2 weeks

print(d.render())
```

### Close Specific Dates (Holidays)

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    d.close_weekends()
    # Company holidays
    d.close_dates(date(2024, 1, 1), date(2024, 1, 15))

    d.task("Q1 Work", days=60)

print(d.render())
```

### Close a Date Range

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    d.close_weekends()
    # Company shutdown for the holidays
    d.close_date_range(date(2024, 12, 23), date(2024, 12, 31))

    d.task("Annual Project", days=250)

print(d.render())
```

### Reopen Specific Dates

Override a closed day to make it working:

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    d.close_weekends()
    # Special Saturday work day
    d.open_date(date(2024, 1, 6))

    d.task("Crunch Time", days=7)

print(d.render())
```

## Task Appearance

### Task Colors

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    d.task("Normal Task", days=5)
    d.task("Important Task", days=5, color="Red")
    d.task("Completed Task", days=5, color="Green")
    d.task("Warning Task", days=5, color="Orange")

print(d.render())
```

### Gradient Colors

Use a slash to create a gradient effect:

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    d.task("Gradient Task", days=10, color="LightBlue/Blue")

print(d.render())
```

### Task Completion Progress

Show how much of a task is complete:

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    d.task("Not Started", days=5, completed=0)
    d.task("In Progress", days=5, completed=60)
    d.task("Almost Done", days=5, completed=90)
    d.task("Finished", days=5, completed=100)

print(d.render())
```

### Task Links

Make tasks clickable:

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    d.task("View Documentation", days=5, link="https://docs.example.com")
    d.task("Open Ticket", days=5, link="https://jira.example.com/PROJ-123")

print(d.render())
```

### Deleted Tasks

Mark tasks as deleted (shown with strikethrough):

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    d.task("Active Task", days=5)
    d.task("Cancelled Task", days=5, deleted=True)
    d.task("Another Active", days=5)

print(d.render())
```

## Visual Organization

### Separators Between Task Groups

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    d.task("Design", days=5)
    d.task("Prototype", days=3)

    d.separator("Development Phase")

    d.task("Backend", days=10)
    d.task("Frontend", days=10)

    d.separator("Testing Phase")

    d.task("QA", days=5)
    d.task("UAT", days=3)

print(d.render())
```

### Tasks on Same Row

Display tasks on the same row to save space:

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    task1 = d.task("Task 1", days=3)
    task2 = d.task("Task 2", days=3, after=task1)
    # Task 3 goes on same row as Task 1 (they don't overlap)
    d.task("Task 3", days=3, after=task2, same_row_as=task1)

print(d.render())
```

### Vertical Separators

Add vertical lines at specific points:

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    phase1 = d.task("Phase 1", days=10)
    d.vertical_separator(after=phase1)

    phase2 = d.task("Phase 2", days=10, after=phase1)
    d.vertical_separator(after=phase2)

    d.task("Phase 3", days=10, after=phase2)

print(d.render())
```

## Today Marker

### Mark Today's Date

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    d.today(date(2024, 1, 15))

    d.task("Past Task", days=10)
    d.task("Current Task", days=10)
    d.task("Future Task", days=10)

print(d.render())
```

### Today Marker with Color

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    d.today(date(2024, 1, 15), color="Red")

    d.task("Development", days=30)

print(d.render())
```

## Chart Display Options

### Chart Title

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1), title="Q1 2024 Project Plan") as d:
    d.task("Planning", days=5)
    d.task("Execution", days=20)
    d.task("Review", days=5)

print(d.render())
```

### Time Scale

Control the granularity of the time axis:

```python
from datetime import date
from plantuml_compose import gantt_diagram

# Daily scale (default)
with gantt_diagram(start=date(2024, 1, 1), scale="daily") as d:
    d.task("Task", days=14)

print(d.render())
```

```python
from datetime import date
from plantuml_compose import gantt_diagram

# Weekly scale for longer projects
with gantt_diagram(start=date(2024, 1, 1), scale="weekly") as d:
    d.task("Task", weeks=8)

print(d.render())
```

```python
from datetime import date
from plantuml_compose import gantt_diagram

# Monthly scale for very long projects
with gantt_diagram(start=date(2024, 1, 1), scale="monthly") as d:
    d.task("Long Project", start=date(2024, 1, 1), end=date(2024, 12, 31))

print(d.render())
```

### Scale Zoom

Adjust the zoom level:

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1), scale="weekly", scale_zoom=2) as d:
    d.task("Task", weeks=4)

print(d.render())
```

### Hide Footer

Remove the date footer below the chart:

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1), hide_footbox=True) as d:
    d.task("Task 1", days=5)
    d.task("Task 2", days=5)

print(d.render())
```

### Week Numbering

Show week numbers instead of dates:

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1), week_numbering=True) as d:
    d.task("Task 1", weeks=2)
    d.task("Task 2", weeks=2)

print(d.render())
```

### Week Starts On

Configure which day starts the week:

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1), week_starts_on="monday") as d:
    d.close_weekends()
    d.task("Task", weeks=2)

print(d.render())
```

### Language/Locale

Set the language for date formatting:

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1), language="de") as d:
    d.task("Aufgabe 1", days=5)
    d.task("Aufgabe 2", days=5)

print(d.render())
```

### Print Range

Limit the visible date range:

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(
    start=date(2024, 1, 1),
    print_range=(date(2024, 1, 1), date(2024, 1, 31))
) as d:
    d.task("January Work", days=20)
    d.task("February Work", days=20)  # Won't be visible

print(d.render())
```

## Date Coloring

### Color Specific Dates

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    # Highlight important dates
    d.color_date(date(2024, 1, 15), "LightGreen")
    d.color_date(date(2024, 1, 31), "LightBlue")

    d.task("January Work", days=31)

print(d.render())
```

### Color Date Ranges

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    # Highlight a sprint period
    d.color_date_range(date(2024, 1, 8), date(2024, 1, 19), "LightYellow")

    d.task("Sprint 1", start=date(2024, 1, 8), end=date(2024, 1, 19))
    d.task("Sprint 2", start=date(2024, 1, 22), end=date(2024, 2, 2))

print(d.render())
```

## Task Pauses

### Pause on Specific Dates

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    # Task pauses during the company retreat
    d.task("Development", days=15, pauses_on=[date(2024, 1, 10), date(2024, 1, 11)])

print(d.render())
```

### Pause on Days of Week

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    # This task doesn't run on Fridays (team meeting day)
    d.task("Development", days=10, pauses_on=["friday"])

print(d.render())
```

## Task Notes

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    d.task("Design", days=5, note="Needs stakeholder approval")
    d.task("Development", days=10, note="High complexity")
    d.milestone("Launch", on=date(2024, 1, 20), note="Public announcement")

print(d.render())
```

## Diagram Styling

### Basic Styling

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(
    start=date(2024, 1, 1),
    diagram_style={
        "background": "#FAFAFA",
        "task": {"background": "#E3F2FD"},
        "milestone": {"background": "#FFF9C4"},
    }
) as d:
    d.task("Task 1", days=5)
    d.task("Task 2", days=5)
    d.milestone("Done", on=date(2024, 1, 12))

print(d.render())
```

### Comprehensive Styling

```python
from datetime import date
from plantuml_compose import gantt_diagram
from plantuml_compose.primitives.gantt import GanttDiagramStyle
from plantuml_compose.primitives.common import ElementStyle, DiagramArrowStyle

with gantt_diagram(
    start=date(2024, 1, 1),
    diagram_style=GanttDiagramStyle(
        background="#F5F5F5",
        font_name="Arial",
        task=ElementStyle(background="#BBDEFB", line_color="#1976D2"),
        milestone=ElementStyle(background="#FFE082"),
        separator=ElementStyle(background="#E0E0E0"),
        arrow=DiagramArrowStyle(line_color="#757575"),
        undone=ElementStyle(background="#FFCDD2"),  # Incomplete portion
        today=ElementStyle(line_color="#D32F2F"),
    )
) as d:
    d.today(date(2024, 1, 10))
    d.task("Task 1", days=5, completed=80)
    d.task("Task 2", days=5, completed=30)
    d.separator("Phase 2")
    d.task("Task 3", days=5)
    d.milestone("Complete", on=date(2024, 1, 20))

print(d.render())
```

## Complete Project Example

Here's a realistic project plan combining multiple features:

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(
    start=date(2024, 1, 1),
    title="Website Redesign Project",
    scale="weekly",
) as d:
    # Configure calendar
    d.close_weekends()
    d.close_dates(date(2024, 1, 15))  # Holiday
    d.today(date(2024, 1, 22))

    # Planning Phase
    requirements = d.task("Requirements Gathering", weeks=2, resources=["PM"])
    d.milestone("Requirements Approved", after=requirements)

    d.separator("Design Phase")

    # Design Phase - parallel work
    ux = d.task("UX Research", weeks=2, after=requirements, resources=["UX Team"])
    wireframes = d.task("Wireframes", weeks=1, after=ux, resources=["Designer"])
    mockups = d.task("Visual Design", weeks=2, after=wireframes, resources=["Designer"])
    d.milestone("Design Complete", after=mockups)

    d.separator("Development Phase")

    # Development - parallel tracks
    frontend = d.task("Frontend Development", weeks=4, after=mockups,
                      resources=[("Alice", 100), ("Bob", 50)], completed=25)
    backend = d.task("Backend API", weeks=3, after=mockups,
                     resources=[("Bob", 50), ("Carol", 100)])
    integration = d.task("Integration", weeks=2, after=[frontend, backend],
                        resources=["Alice", "Carol"])

    d.separator("Launch Phase")

    # Testing and launch
    qa = d.task("QA Testing", weeks=2, after=integration, resources=["QA Team"])
    fixes = d.task("Bug Fixes", weeks=1, after=qa, resources=["Alice", "Carol"])
    deploy = d.task("Deployment", days=2, after=fixes, resources=["DevOps"])

    d.milestone("Go Live!", after=deploy, color="Green")

print(d.render())
```

## Summary

Key points for working with Gantt charts:

1. **Always set a project start date** for relative task positioning
2. **Use `after=` for dependencies** - single task or list of tasks
3. **Use `starts_with=` for parallel tasks** that should begin together
4. **Close weekends and holidays** to reflect actual working days
5. **Assign resources** to track who does what
6. **Add milestones** to mark important dates
7. **Use separators** to organize related tasks visually
8. **Show progress** with the `completed=` parameter
9. **Style your chart** to match your presentation needs

The Gantt diagram builder provides a fluent, type-safe API that generates correct PlantUML syntax while preventing common mistakes through validation.
