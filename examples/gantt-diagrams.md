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
tk.task("Short task", days=3)
tk.task("Medium task", days=7)
tk.task("Long task", days=14)
```

#### Duration in Weeks

```python
tk.task("Sprint 1", weeks=2)
tk.task("Sprint 2", weeks=2)
```

#### Explicit Start and End Dates

```python
tk.task("Planning", start=date(2026, 4, 6), end=date(2026, 4, 10))
```

#### Start Date with Duration

```python
tk.task("Kickoff", start=date(2026, 4, 6), days=5)
```

#### Completion Percentage

```python
tk.task("Design", days=10, completion=60)   # 60% done
tk.task("Review", days=3, completion=100)   # fully complete
```

#### Colored Tasks

```python
tk.task("Critical", days=5, color="#FFCDD2")
tk.task("Normal", days=3, color="LightBlue")
```

#### Resources

Assign one or more people/teams to a task:

```python
tk.task("Design", days=5, resources=("Alice",))
tk.task("Develop", days=10, resources=("Bob", "Carol"))
tk.task("Review", days=2, resources=("Alice", "David"))
```

#### Task Links

Add a clickable URL to a task:

```python
tk.task("JIRA-123", days=5, link="https://jira.example.com/JIRA-123")
tk.task("Linked", days=3, link="https://example.com",
        link_color="blue", link_style="bold")
```

Parameters for link styling: `link=`, `link_color=`, `link_style=` (`"bold"`, `"dashed"`, `"dotted"`)

#### Task Notes

```python
tk.task("Audit", days=3, note="Requires read access to prod DB")
tk.task("Deploy", days=1, note="After hours only", note_position="right")
```

`note_position=` accepts `"bottom"` (default), `"left"`, `"right"`, `"top"`.

#### Working Days Flag

When `working_days=True`, the duration counts only working days (excluding closed days):

```python
tk.task("Development", days=10, working_days=True)
```

#### Pauses

Pause a task on specific dates or recurring days of the week:

```python
tk.task("Long task", days=20,
    pauses_on=(date(2026, 4, 15),),              # pause on a specific date
    pauses_on_days=("wednesday",),                # pause every Wednesday
)
```

#### Deleted Tasks

Mark a task as deleted (renders with strikethrough):

```python
tk.task("Cancelled feature", days=5, is_deleted=True)
```

#### Same Row As

Force a task onto the same row as another task:

```python
prep = tk.task("Prep", days=3)
followup = tk.task("Followup", days=2, on_same_row_as=prep)
```

#### All Task Parameters

`name`, `days=`, `weeks=`, `start=`, `end=`, `completion=`, `color=`, `resources=`, `link=`, `link_color=`, `link_style=`, `note=`, `note_position=`, `on_same_row_as=`, `pauses_on=`, `pauses_on_days=`, `is_deleted=`, `working_days=`

### Milestones

Zero-duration markers for significant events:

```python
tk.milestone("Phase 1 Complete")
tk.milestone("Launch", on=date(2026, 5, 1))
tk.milestone("Go Live", color="Gold")
tk.milestone("Sign-off", link="https://example.com/sign-off")
tk.milestone("Review", note="Stakeholder approval needed")
```

Parameters: `name`, `on=`, `color=`, `link=`, `note=`, `note_position=`

## Dependencies

### after

Task B starts after task A completes:

```python
dep.after(task_b, task_a)
```

Multiple predecessors -- pass a list:

```python
# deploy starts after both build and test complete
dep.after(deploy, [build, test])
```

### starts_with

Task B starts at the same time as task A:

```python
dep.starts_with(task_b, task_a)
```

### Connecting Dependencies

```python
d.connect(
    dep.after(develop, design),
    dep.after(test, develop),
    dep.after(deploy, [test, review]),
    dep.starts_with(docs, develop),
)
```

Lists returned by `dep.after(..., [list])` are flattened automatically by `d.connect()`.

## Calendar

### Closed Days (Weekends)

```python
d.close_days("saturday", "sunday")
```

Valid day names: `"monday"`, `"tuesday"`, `"wednesday"`, `"thursday"`, `"friday"`, `"saturday"`, `"sunday"`

### Closed Dates (Holidays)

```python
d.close_dates(date(2026, 12, 25), date(2026, 1, 1))
```

### Closed Date Range

```python
d.close_date_range(date(2026, 12, 24), date(2026, 12, 31))
```

### Open Date (Override)

Reopen a specific date that falls within a closed range:

```python
d.close_days("saturday", "sunday")
d.open_date(date(2026, 4, 11))  # this Saturday is a working day
```

### Colored Dates

Highlight specific dates with a background color:

```python
d.color_date(date(2026, 4, 15), "LightYellow")
```

### Colored Date Ranges

```python
d.color_date_range(date(2026, 4, 20), date(2026, 4, 24), "LightGreen")
```

### Today Marker

```python
d.today()                                        # default marker
d.today(date(2026, 4, 10))                       # explicit date
d.today(date(2026, 4, 10), color="LightCoral")   # with color
```

## Separators

### Horizontal Separators

Visual dividers between task groups:

```python
d.add(design, develop)
d.separator("Phase 2")        # labeled separator
d.add(test, deploy)
d.separator()                 # unlabeled separator
d.add(monitor)
```

Separators interleave with `d.add()` calls in order.

### Vertical Separators

Vertical lines after a specific task:

```python
d.add(phase1_task)
d.vertical_separator(phase1_task)
d.add(phase2_task)
```

## Resources

### Assigning Resources

```python
tk.task("Design", days=5, resources=("Alice",))
tk.task("Develop", days=10, resources=("Bob", "Carol"))
```

### Resource Off (Unavailable Dates)

```python
d.resource_off("Alice", date(2026, 4, 15), date(2026, 4, 16))
d.resource_off("Bob", date(2026, 5, 1))
```

### Hiding Resources

```python
# Hide resource names from task bars
d = gantt_diagram(start=date(2026, 4, 6), hide_resource_names=True)

# Hide the resource usage footbox
d = gantt_diagram(start=date(2026, 4, 6), hide_resource_footbox=True)

# Hide the entire footbox (dates)
d = gantt_diagram(start=date(2026, 4, 6), hide_footbox=True)
```

## Scale & Time Options

### Scale

Control the time granularity:

```python
d = gantt_diagram(start=date(2026, 4, 6), scale="daily")
d = gantt_diagram(start=date(2026, 4, 6), scale="weekly")
d = gantt_diagram(start=date(2026, 4, 6), scale="monthly")
d = gantt_diagram(start=date(2026, 4, 6), scale="quarterly")
d = gantt_diagram(start=date(2026, 4, 6), scale="yearly")
```

### Scale Zoom

Zoom the time axis:

```python
d = gantt_diagram(start=date(2026, 4, 6), scale="weekly", scale_zoom=2)
```

### Week Numbering

Display ISO week numbers:

```python
d = gantt_diagram(start=date(2026, 4, 6), week_numbering=True)

# Or start from a specific week number
d = gantt_diagram(start=date(2026, 4, 6), week_numbering=14)
```

### Calendar Date Display

Show calendar dates on the header:

```python
d = gantt_diagram(start=date(2026, 4, 6), show_calendar_date=True)
```

### Week Starts On

```python
d = gantt_diagram(start=date(2026, 4, 6), week_starts_on="monday")
```

### Language

Change day/month names to a different locale:

```python
d = gantt_diagram(start=date(2026, 4, 6), language="de")
d = gantt_diagram(start=date(2026, 4, 6), language="fr")
```

### Print Range

Limit the rendered date range:

```python
d = gantt_diagram(
    start=date(2026, 4, 6),
    print_range=(date(2026, 4, 6), date(2026, 5, 31)),
)
```

## Styling

### Task-Level Coloring

```python
tk.task("Critical", days=5, color="#FFCDD2")
tk.task("Normal", days=3, color="LightBlue")
tk.milestone("Done", color="Gold")
```

### diagram_style

Theme the entire chart with CSS-like selectors:

```python
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
