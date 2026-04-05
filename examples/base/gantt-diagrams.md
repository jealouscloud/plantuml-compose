# Gantt Chart Diagrams

Gantt charts visualize project schedules with tasks as horizontal bars along a time axis. They show durations, dependencies, milestones, and resource assignments.

## Quick Start

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(title="Migration", start=date(2026, 4, 6))
tk = d.tasks
dep = d.dependencies

d.close_days("saturday", "sunday")

audit = tk.task("Audit", days=3)
prep = tk.task("Prepare", days=5, color="#E3F2FD")
d.add(audit, prep)

d.connect(dep.after(prep, audit))

print(render(d))
```

The pattern: create a diagram with a project `start` date, get `tk` (tasks) and `dep` (dependencies) namespaces, build tasks, `d.add()` them, and wire dependencies with `d.connect()`.

## Elements

### Tasks

#### Duration in Days

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6))
tk = d.tasks

short = tk.task("Short task", days=3)
medium = tk.task("Medium task", days=7)
long = tk.task("Long task", days=14)
d.add(short, medium, long)

print(render(d))
```

#### Duration in Weeks

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6))
tk = d.tasks

sprint1 = tk.task("Sprint 1", weeks=2)
sprint2 = tk.task("Sprint 2", weeks=2)
d.add(sprint1, sprint2)

print(render(d))
```

#### Explicit Start and End Dates

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6))
tk = d.tasks

planning = tk.task("Planning", start=date(2026, 4, 6), end=date(2026, 4, 10))
d.add(planning)

print(render(d))
```

#### Start Date with Duration

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6))
tk = d.tasks

kickoff = tk.task("Kickoff", start=date(2026, 4, 6), days=5)
d.add(kickoff)

print(render(d))
```

#### Completion Percentage

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6))
tk = d.tasks

design = tk.task("Design", days=10, completion=60)
review = tk.task("Review", days=3, completion=100)
d.add(design, review)

print(render(d))
```

#### Colored Tasks

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6))
tk = d.tasks

critical = tk.task("Critical", days=5, color="#FFCDD2")
normal = tk.task("Normal", days=3, color="LightBlue")
d.add(critical, normal)

print(render(d))
```

#### Resources

Assign one or more people/teams to a task:

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6))
tk = d.tasks

design = tk.task("Design", days=5, resources=("Alice",))
develop = tk.task("Develop", days=10, resources=("Bob", "Carol"))
review = tk.task("Review", days=2, resources=("Alice", "David"))
d.add(design, develop, review)

print(render(d))
```

#### Task Links

Add a clickable URL to a task:

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6))
tk = d.tasks

jira = tk.task("JIRA-123", days=5, link="https://jira.example.com/JIRA-123")
linked = tk.task("Linked", days=3, link="https://example.com",
                 link_color="blue", link_style="bold")
d.add(jira, linked)

print(render(d))
```

Parameters for link styling: `link=`, `link_color=`, `link_style=` (`"bold"`, `"dashed"`, `"dotted"`)

#### Task Notes

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6))
tk = d.tasks

audit = tk.task("Audit", days=3, note="Requires read access to prod DB")
deploy = tk.task("Deploy", days=1, note="After hours only")
d.add(audit, deploy)

print(render(d))
```

`note_position=` accepts `"bottom"` (default), `"left"`, `"right"`, `"top"`.

#### Working Days Flag

When `working_days=True`, the duration counts only working days (excluding closed days):

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6))
tk = d.tasks

d.close_days("saturday", "sunday")
dev = tk.task("Development", days=10, working_days=True)
d.add(dev)

print(render(d))
```

#### Pauses

Pause a task on specific dates or recurring days of the week:

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6))
tk = d.tasks

task = tk.task("Long task", days=20,
    pauses_on=(date(2026, 4, 15),),
    pauses_on_days=("wednesday",),
)
d.add(task)

print(render(d))
```

#### Deleted Tasks

Mark a task as deleted (renders with strikethrough):

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6))
tk = d.tasks

cancelled = tk.task("Cancelled feature", days=5, is_deleted=True)
d.add(cancelled)

print(render(d))
```

#### Same Row As

Force a task onto the same row as another task:

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6))
tk = d.tasks
dep = d.dependencies

prep = tk.task("Prep", days=3)
followup = tk.task("Followup", days=2, on_same_row_as=prep)
d.add(prep, followup)
d.connect(dep.after(followup, prep))

print(render(d))
```

#### All Task Parameters

`name`, `days=`, `weeks=`, `start=`, `end=`, `completion=`, `color=`, `resources=`, `link=`, `link_color=`, `link_style=`, `note=`, `note_position=`, `on_same_row_as=`, `pauses_on=`, `pauses_on_days=`, `is_deleted=`, `working_days=`

### Milestones

Zero-duration markers for significant events:

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6))
tk = d.tasks

m1 = tk.milestone("Phase 1 Complete", on=date(2026, 4, 10))
m2 = tk.milestone("Launch", on=date(2026, 5, 1))
m3 = tk.milestone("Go Live", on=date(2026, 5, 15), color="Gold")
d.add(m1, m2, m3)

print(render(d))
```

Parameters: `name`, `on=`, `color=`, `link=`, `note=`, `note_position=`

## Dependencies

### after

Task B starts after task A completes:

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6))
tk = d.tasks
dep = d.dependencies

task_a = tk.task("Task A", days=3)
task_b = tk.task("Task B", days=5)
d.add(task_a, task_b)
d.connect(dep.after(task_b, task_a))

print(render(d))
```

Multiple predecessors -- pass a list:

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6))
tk = d.tasks
dep = d.dependencies

build = tk.task("Build", days=5)
test = tk.task("Test", days=3)
deploy = tk.task("Deploy", days=2)
d.add(build, test, deploy)
d.connect(dep.after(deploy, [build, test]))

print(render(d))
```

### starts_with

Task B starts at the same time as task A:

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6))
tk = d.tasks
dep = d.dependencies

task_a = tk.task("Task A", days=5)
task_b = tk.task("Task B", days=3)
d.add(task_a, task_b)
d.connect(dep.starts_with(task_b, task_a))

print(render(d))
```

### Connecting Dependencies

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6))
tk = d.tasks
dep = d.dependencies

design = tk.task("Design", days=5)
develop = tk.task("Develop", days=10)
test = tk.task("Test", days=3)
review = tk.task("Review", days=2)
deploy = tk.task("Deploy", days=1)
docs = tk.task("Docs", days=8)
d.add(design, develop, test, review, deploy, docs)

d.connect(
    dep.after(develop, design),
    dep.after(test, develop),
    dep.after(deploy, [test, review]),
    dep.starts_with(docs, develop),
)

print(render(d))
```

Lists returned by `dep.after(..., [list])` are flattened automatically by `d.connect()`.

## Calendar

### Closed Days (Weekends)

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6))
tk = d.tasks

d.close_days("saturday", "sunday")

task = tk.task("Weekdays only", days=10)
d.add(task)

print(render(d))
```

Valid day names: `"monday"`, `"tuesday"`, `"wednesday"`, `"thursday"`, `"friday"`, `"saturday"`, `"sunday"`

### Closed Dates (Holidays)

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6))
tk = d.tasks

d.close_dates(date(2026, 4, 8), date(2026, 4, 9))

task = tk.task("Work around holidays", days=7)
d.add(task)

print(render(d))
```

### Closed Date Range

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 12, 15))
tk = d.tasks

d.close_date_range(date(2026, 12, 24), date(2026, 12, 31))

task = tk.task("Year-end project", days=14)
d.add(task)

print(render(d))
```

### Open Date (Override)

Reopen a specific date that falls within a closed range:

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6))
tk = d.tasks

d.close_days("saturday", "sunday")
d.open_date(date(2026, 4, 11))  # this Saturday is a working day

task = tk.task("Includes a Saturday", days=7)
d.add(task)

print(render(d))
```

### Colored Dates

Highlight specific dates with a background color:

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6))
tk = d.tasks

d.color_date(date(2026, 4, 15), "LightYellow")

task = tk.task("Watch the 15th", days=14)
d.add(task)

print(render(d))
```

### Colored Date Ranges

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6))
tk = d.tasks

d.color_date_range(date(2026, 4, 20), date(2026, 4, 24), "LightGreen")

task = tk.task("Sprint", days=21)
d.add(task)

print(render(d))
```

### Today Marker

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6))
tk = d.tasks

d.today(date(2026, 4, 10), color="LightCoral")

task = tk.task("Ongoing work", days=10)
d.add(task)

print(render(d))
```

## Separators

### Horizontal Separators

Visual dividers between task groups:

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6))
tk = d.tasks

design = tk.task("Design", days=5)
develop = tk.task("Develop", days=10)
test = tk.task("Test", days=3)
deploy = tk.task("Deploy", days=2)
monitor = tk.task("Monitor", days=5)

d.add(design, develop)
d.separator("Phase 2")
d.add(test, deploy)
d.separator("Phase 3")
d.add(monitor)

print(render(d))
```

Separators interleave with `d.add()` calls in order.

### Vertical Separators

Vertical lines after a specific task:

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6))
tk = d.tasks

phase1 = tk.task("Phase 1", days=5)
phase2 = tk.task("Phase 2", days=5)

d.add(phase1)
d.vertical_separator(phase1)
d.add(phase2)

print(render(d))
```

## Resources

### Assigning Resources

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6))
tk = d.tasks

design = tk.task("Design", days=5, resources=("Alice",))
develop = tk.task("Develop", days=10, resources=("Bob", "Carol"))
d.add(design, develop)

print(render(d))
```

### Resource Off (Unavailable Dates)

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6))
tk = d.tasks

design = tk.task("Design", days=10, resources=("Alice",))
build = tk.task("Build", days=10, resources=("Bob",))
d.add(design, build)

d.resource_off("Alice", date(2026, 4, 15), date(2026, 4, 16))
d.resource_off("Bob", date(2026, 5, 1))

print(render(d))
```

### Hiding Resources

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6), hide_resource_names=True)
tk = d.tasks

task = tk.task("Design", days=5, resources=("Alice",))
d.add(task)

print(render(d))
```

## Scale & Time Options

### Scale

Control the time granularity:

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6), scale="weekly")
tk = d.tasks

task = tk.task("Long project", days=30)
d.add(task)

print(render(d))
```

Valid values: `"daily"`, `"weekly"`, `"monthly"`, `"quarterly"`, `"yearly"`

### Scale Zoom

Zoom the time axis:

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6), scale="weekly", scale_zoom=2)
tk = d.tasks

task = tk.task("Zoomed project", days=30)
d.add(task)

print(render(d))
```

### Week Numbering

Display ISO week numbers:

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6), week_numbering=True)
tk = d.tasks

task = tk.task("Tracked by week", days=14)
d.add(task)

print(render(d))
```

### Calendar Date Display

Show calendar dates on the header:

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6), show_calendar_date=True)
tk = d.tasks

task = tk.task("Date-labeled task", days=7)
d.add(task)

print(render(d))
```

### Week Starts On

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6), week_starts_on="monday")
tk = d.tasks

task = tk.task("Monday start", days=10)
d.add(task)

print(render(d))
```

### Language

Change day/month names to a different locale:

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6), language="de")
tk = d.tasks

task = tk.task("Aufgabe", days=7)
d.add(task)

print(render(d))
```

### Print Range

Limit the rendered date range:

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(
    start=date(2026, 4, 6),
    print_range=(date(2026, 4, 6), date(2026, 5, 31)),
)
tk = d.tasks

task = tk.task("Visible range", days=60)
d.add(task)

print(render(d))
```

## Styling

### Task-Level Coloring

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(start=date(2026, 4, 6))
tk = d.tasks

critical = tk.task("Critical", days=5, color="#FFCDD2")
normal = tk.task("Normal", days=3, color="LightBlue")
done = tk.milestone("Done", on=date(2026, 4, 15), color="Gold")
d.add(critical, normal, done)

print(render(d))
```

### diagram_style

Theme the entire chart with CSS-like selectors:

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(
    start=date(2026, 4, 6),
    diagram_style={
        "background": "white",
        "font_name": "Arial",
        "font_size": 12,
        "font_color": "#333333",
        "task": {"background": "#E3F2FD", "line_color": "#1976D2"},
        "milestone": {"background": "#FFF9C4", "line_color": "#F9A825"},
        "separator": {"background": "#ECEFF1", "font_style": "bold"},
        "note": {"background": "#FFF8E1"},
        "arrow": {"line_color": "#757575"},
        "undone": {"background": "#EEEEEE"},
        "today": {"background": "#FFCCBC", "line_color": "#FF5722"},
        "stereotypes": {
            "critical": {"background": "#FFCDD2", "font_style": "bold"},
            "blocked": {"background": "#F5F5F5", "font_color": "#9E9E9E"},
        },
    },
)

print(render(d))
```

Available selectors: `task`, `milestone`, `separator`, `note`, `arrow`, `undone`, `today`, `stereotypes`

Root-level properties: `background`, `font_name`, `font_size`, `font_color`

Each element selector accepts an `ElementStyleDict` with keys like `background`, `line_color`, `font_color`, `font_name`, `font_size`, `font_style`, `round_corner`, `line_thickness`, `padding`, `margin`, `shadowing`.

The `arrow` selector accepts a `DiagramArrowStyleDict` with `line_color`, `line_thickness`, `line_style`.

The `undone` selector styles the incomplete portion of partially-completed tasks.

The `today` selector styles the today marker line.

## Advanced Features

### Complete Example

```python
from datetime import date
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(
    title="Q2 Platform Migration",
    start=date(2026, 4, 6),
    scale="weekly",
    hide_resource_footbox=True,
    diagram_style={
        "task": {"background": "#E3F2FD"},
        "milestone": {"background": "Gold"},
        "separator": {"font_style": "bold"},
    },
)
tk = d.tasks
dep = d.dependencies

d.close_days("saturday", "sunday")
d.close_dates(date(2026, 5, 25))  # Memorial Day
d.today(date(2026, 4, 14), color="LightCoral")

# Phase 1
audit = tk.task("Infrastructure Audit", days=5,
                resources=("Alice",), completion=100)
design = tk.task("Architecture Design", days=8,
                 resources=("Alice", "Bob"), completion=75)
approve = tk.milestone("Design Approval")

d.add(audit, design, approve)
d.connect(dep.after(design, audit), dep.after(approve, design))

d.separator("Phase 2: Implementation")

build_api = tk.task("Build API Layer", days=15,
                    resources=("Bob", "Carol"), color="#C8E6C9")
build_ui = tk.task("Build UI", days=12,
                   resources=("David",), color="#C8E6C9")
migrate = tk.task("Data Migration", days=5,
                  resources=("Carol",),
                  note="Requires maintenance window",
                  working_days=True)

d.add(build_api, build_ui, migrate)
d.connect(
    dep.after(build_api, approve),
    dep.starts_with(build_ui, build_api),
    dep.after(migrate, build_api),
)

d.separator("Phase 3: Validation")

test = tk.task("Integration Testing", days=10,
               resources=("Alice", "David"))
perf = tk.task("Performance Testing", days=5,
               resources=("Bob",),
               pauses_on_days=("friday",))
launch = tk.milestone("Go Live", color="Gold",
                      link="https://wiki.example.com/go-live")

d.add(test, perf, launch)
d.connect(
    dep.after(test, [build_api, build_ui, migrate]),
    dep.after(perf, test),
    dep.after(launch, perf),
)

d.resource_off("Alice", date(2026, 5, 5), date(2026, 5, 6))

d.color_date_range(date(2026, 6, 1), date(2026, 6, 5), "LightGreen")

print(render(d))
```

## Quick Reference

| Method | Description |
|--------|-------------|
| `tk.task(name, days=)` | Task with day duration |
| `tk.task(name, weeks=)` | Task with week duration |
| `tk.task(name, start=, end=)` | Task with explicit dates |
| `tk.task(name, start=, days=)` | Task with start + duration |
| `tk.milestone(name)` | Zero-duration marker |
| `dep.after(task, predecessor)` | Sequential dependency |
| `dep.after(task, [pred1, pred2])` | Multiple predecessors |
| `dep.starts_with(task, other)` | Concurrent start |
| `d.add(*elements)` | Register tasks/milestones |
| `d.connect(*dependencies)` | Register dependencies |
| `d.separator(text=)` | Horizontal divider |
| `d.vertical_separator(after=)` | Vertical divider |
| `d.close_days(*days)` | Mark weekdays as non-working |
| `d.close_dates(*dates)` | Mark specific dates as closed |
| `d.close_date_range(start, end)` | Close a date range |
| `d.open_date(date)` | Re-open a closed date |
| `d.color_date(date, color)` | Highlight a date |
| `d.color_date_range(start, end, color)` | Highlight a date range |
| `d.today(date=, color=)` | Mark today's date |
| `d.resource_off(name, *dates)` | Resource unavailable |

### Task Parameters

| Parameter | Description |
|-----------|-------------|
| `days=` | Duration in calendar days |
| `weeks=` | Duration in weeks |
| `start=` | Explicit start date |
| `end=` | Explicit end date |
| `completion=` | Percentage complete (0-100) |
| `color=` | Bar color |
| `resources=` | Tuple of resource names |
| `link=` | Clickable URL |
| `link_color=` | Link text color |
| `link_style=` | `"bold"`, `"dashed"`, `"dotted"` |
| `note=` | Inline note text |
| `note_position=` | `"bottom"`, `"left"`, `"right"`, `"top"` |
| `on_same_row_as=` | Force onto same row as another task |
| `pauses_on=` | Tuple of dates to pause |
| `pauses_on_days=` | Tuple of day names to pause weekly |
| `is_deleted=` | Strikethrough rendering |
| `working_days=` | Count only working days for duration |

### Diagram Options

| Parameter | Description |
|-----------|-------------|
| `title=` | Chart title |
| `mainframe=` | Mainframe label |
| `start=` | Project start date |
| `theme=` | PlantUML theme name |
| `diagram_style=` | Dict of CSS-like style selectors |
| `scale=` | `"daily"`, `"weekly"`, `"monthly"`, `"quarterly"`, `"yearly"` |
| `scale_zoom=` | Integer zoom level |
| `language=` | Locale for day/month names (`"de"`, `"fr"`, ...) |
| `week_numbering=` | `True` or starting week number (int) |
| `show_calendar_date=` | Show dates in header |
| `week_starts_on=` | Day name (`"monday"`, etc.) |
| `print_range=` | `(start_date, end_date)` tuple |
| `hide_footbox=` | Hide the date footbox |
| `hide_resource_names=` | Hide resource labels on task bars |
| `hide_resource_footbox=` | Hide the resource usage footbox |
