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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodX2YZApqfDBb402nKh61aOcUWQ608HLxHBQd5cUbwiGcAnGdHyYM6iGavYCL29gK9AOcKnIBeiDIU_02Pl19CtD80g08j1pKqiWPYXNgoGcfV25HsIMbm2qsaCqsaCrsYCfj48fj41I80T3W00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodX2YZApqfDBb402nKh61aOcUWQ608HLtHmHdvHYK99Od5sh49YiK9qV8bXh49EOZ5GcR52Ic9bCLUqRsfAPcakYXeZc1fpg1gV_Bnq51N6C1M69X0b3gbvAM3N0000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodX2YZApqfDBb402nKh61aOcUWQ608HLtHmGL5cNec2OQn2Oh52T7m9a96JM0nIf52UcffT35TX15DXX4k5CKo5CReAXzIy5B1B0000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodX2YZApqfDBb402nKh61aOcUWQ608HLtIWeK90Jc9UNcPUUgn2Oh52T7o9OIocGeN4l1I5rBmKX9YXALYpQqLgScb9PduUJBSHXcv3CtJTnhh6XbmEG06mym00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NP0n2y8m48Nt_8hRd8GcgRXsS74JSGj53dk4I9lMtZduxmsnALWuRdZltiVZ6XQSnMCKKPTvVD9384iCfZBrlj9fbBlIwnrc6YWAju0CxYwwXHuv7HwWmmyhTo8EFXRR5Fkus5bQs2W_mew1OgVSUPZwJ4S9uugm1Q7hbM4t3BCoRiGIeY_XUbilItzPMx9DMla7Nm00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/TP3D2i8m48Jl-nHxyrH8qdgL8YBqvZqKMTeGgf90TY--lI7zGKLXJpFp3SEsB9J4Kn21IuetDmWMYT4eqrHAvmDxSZpvq2Cnsgle7X_4ERB7aPuCzaZ3tOLnzStgQxK4YhRqaimTEyRCW3sd6EIDhd_GzL-wownF95FSvZNVyuhqmPkDBztLOUQWpLfvnWi0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodX2YZApqfDBb402nKh61aOcUWQ608HLxHBQd5cUbwiGcAnGdHyYM6iGavYCL29gK9AOcKnLxHJOd9sQbuAJDu89cze05K05eEQcrW2CKEzM06eXolQhIW_hmH9jp5CjmLSip6QPYEGPh08bmDG9zZv0000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NP3F2eCm38VlFaLkEmtyrvqTxW5ax2OomXhSHjSM4uIz_KIjZaB88NpvVMah5XoaHokID8DxqqDW7Z7aQLuUqsogf6qCMlkoVGV8qDubwy0WJv02ZLzU03XxFxYHTA3o3fxeFLa6b6Njm41M9-s5HZBEVyXAe8kGcQThw3nRhua3QgS9QlVnXeH2H1aBYus_4SlV0rIGPRjCHR9z-Kg6a3VDATQeG5PJcp_p1m00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NOx12i8m44Jl-Ohz0I59zLx4euBt46HfbbQfcv3T2lwziL04OKx3OzxqebXrH5OrrveVD2YibO2tVh-phiM44xrepkL9h15G8DpKHPXH6jTPIFWM4uuPQu8BaTvvt30VOS9IY7-3xc12SwMbkSwuy31jSFSF-w-z9qxhmmy0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/PSz12i8m40NGVKyn5n2IMFUrYkikt8KYOnf2D2IGcOs8TpUq3LI4MNqUdpyTCMPs69cR8QU7DGnpHA24QdT2bclqsP9tSGGaq3UM8wG8xsFmnduW81LzW0bVrEWUpTF6gLArq3xTAvHYbPUS8c_eVg4dp2dyuQibzj5Ls_uisDQlExfIF7_r1G00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodX2YZApqfDBb402nKh61aOcUWQ608HLxHlOcQU0bG-LY6nM24wliGmLY4_Jw7QCISpETNAqC10jLQXsYa_oSeKnCf9B0OQOMYWa99OMSmL7PoPaegktmYY7uSMXzIy5B2p0000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodX2YZApqfDBb402nKh61aOcUWQ608HLxHBQbbgJdv1RcfUIQn2Oh52T7o9OQn2Vfv2jMDEPd9ghK9EOZ5GYw61GafYPJ4NJ3IpM24_BGsa3cwO1Jv9Iow7rBmKi6i0)



### Hide Resource Names

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1), hide_resource_names=True) as d:
    d.task("Task 1", days=5, resources=["Alice"])
    d.task("Task 2", days=5, resources=["Bob"])

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodX2YZApqfDBb402nKh61aOcUWQ608HLqPcIgf2KMfnVcbHScgnGbvYRcenLtH8Od6sWc6iGcAnGdHy2P2HdwTGxPYJcPnQgv2JM0mqmbGX9R4Ifj88fj88ej8fFmbDdKDgNWhOAG00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NOr12e0W44Ntdc8k4AXq01STeBr833a4OHhE67Jxn6NmLe_7_uu5gnoOHTHQoqcxm50CLjjvqgQZ6ANLY2zW9TXJOOgAM_uPlz13gTmNPGc037uJ4o0XzpMZeUUi7EKuxZu0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NSqn2e0m30NGlQV81OHM71mTF82xY8GsYb9RIQBWxIsEmfyUd_yxKMHTCQcQWVDENk4ZWThMJMLTYH7KYmC-W4pWOnOAPk7j9tAbdumztHJpUL3I2L1WdDLD457AVWkbBQQZ5Bx_5m00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodX2YZApqfDBb402nKh61aOcUWQ608HLt5YIMbHIcAbGc9Hga9oJdvnQWfNSMaUcWXCWw6fGcOnkg218P9WTA2XGdX-KNQiGcAnGdHyYM6iGavYCT1ECmC5eA75N0wfUIbWHm40)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NKux2eGm5EnpYhc0a4JjzGRRYomF4vQLy09vByNUVZLe8qmpm_mcKIhw8LOrhvBtk2cQ9F3M3vrr1uoGrXBe1oeHMyeIWv7A3wK5dEzy3ysuMU_mbTkopCoL4gwf5IHOtkfM999pSxGuMiLCaKDxzGS0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NOwn2i9044Jx_Ohv0I49ect07x2m2o4iTuj6ufxixXN-lKSA2s6g1_DcHW-skBD6qDNAKr9WHuwX6uw7hcyXvwYM-GCsGTgAIoQl-aT-XHDMHtcBqdIngkc1s_gI6UoObkXdREnju8mcS1f5ytxW2m00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/PP2n2i9038RtUugyWD3MkXSSn4L518UZIEY5KhtcIfB5j_VeP5l8zF5z_v163SLwP3Dta_Icpc162bLHrRkYpEVy9Sc84HwednPGmR-iR26YPky00R_g_7cSabXUMcZLMflHeD2bc8G230nt2iuVqpX5iap-y_qstw_pan2nyqyK7hXVvFKshzVvLP1xSWrncF_m0m00)



### Gradient Colors

Use a slash to create a gradient effect:

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    d.task("Gradient Task", days=10, color="LightBlue/Blue")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodX2YZApqfDBb402nKh61aOcUWQ608HLxHxKM9APcfUYK98Od5sh49YiK9qV8bXh49EOZ5GfQ61GafYPJ4NH2opM24vFoU_A3L58JDFmISpFQF4AQSqLHz4S3cavgM0RGC0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/PT312i8m30RWUvyY5uz2rrN1smGHl8ZWiGmfQvYJhfKc5z_UMXaw1ZdzvFi9QOXjuju6Pd59yO4TGua8b5HwBQiymfmZm_KJesl14fWRLoruItbl0yw-I7oZWK2ke8lZqoEZCAS0kRPFI3H1jOIgmErCxlqOYU4G0qwoNigwoDrC7eSmqFrtgLuoNLWb_rs3mPL7l040)



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
![Diagram](https://www.plantuml.com/plantuml/svg/RS-z2i9040JW_fvYNo1_fpPMAQni4aHiZaEMowANdxkGNL7VtX0K18MfXk63ALbmaWi64LLFiIKdi5GCEjVh92_cA7FoT8TTTBU1Wg3u62mWWpbBOQ57dkSRQF39wbtvq35816Ek8YDliwo9ZbDwu33sbBeuMAjCDLA0etSToSVJlvx-wxL-mcylgm_LFYdqQePB2itowGK0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NOvD2i8m48NtESLSG6XZtLUyW0jtePGXyz1gI24p5Boz8UB2mbizllSpgd6nEsSpToth4z6eMKg-yyEXwwjSE4TRDj2DzJKHAuNP-eaIQ-LE9FnM5owS8rA2_65-ZpLhKH8a6AHsvzKUAFJT-EMEkzo8BEtc1m00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NP3D2eD038Jl-nHvWGL_UzOYFLkmfqLAq61jxQwOKF3jkzWkY91Jyirac8855ndGYgXwSK_g1BOLGn8bcOvYFyfKnEDWMq06SvUuXGdP8pdqkB8oNYbErfa2aGGY_H5QGqKVcjpy9YjGFv09j5RcZDsBR1zqQT35qT_wiZWhEo8x4jww8PRH3ZlRQndu_9ZrLZRXTZgaBFoVhOel)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodX2YZApqfDBb402nKh61aOcUWQ608HLtH8Od6sWc6iGcAnGdHy2P2HarWCL6Aia99OMGoLDe996w5BWuMWfYQMG4nGBrP8pKk1QZM6QJN6r6gCfjK8hXKibv9PN903LAgGdwTGd9YRgb2KNmvt9fS3K27OSm00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodX2YZApqfDBb402nKh61aOcUWQ608HLtH0Hc9nge9Xh49YiK9qV0cGaPDO35HZQA2GabXPp1MSMf1Ob5YINwIGLLfSef1O0b6bNgoGcfS2qsu4qsw4hXqY1hKNJJDMeutGZ3Q66MsCnMXZDAFXcXs01DZh0000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodX2YZApqfDBb402nKh61aOcUWQ608HLqb-IcAbGYP2pD2KApeWiRX48IInE3jM8R5O8Jg-n31M8GSeLgnWQA00L5_C5UrSMbIKceUgoWX3bLjfIMbHAeeYOtH53gbvAM1N0W00)



### Today Marker with Color

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    d.today(date(2024, 1, 15), color="Red")

    d.task("Development", days=30)

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodX2YZApqfDBb402nKh61aOcUWQ608HLqb-IcAbGYP2pD0K8PQSdvDVb9gYa9cd49IQmXNjabgMcfDVa9kQLnAha5Yi41rVOXYha9DO33JJs401gAkOoo4rBmLiAG00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NSwz2iCm30JWtK-X5oZORhjdwPvsDQ68H0GNeq1q_NlxfgPU2hU8-n3N6NZ5p0euP1IXSw3euu7wTRd92EeBgsj7rLR1peSjBdrxpJeFn4RfYZ1GOTlGaIP-cqkdbuntv4MRY4r4_oCNUMHvjdx_zw4JdUh23m00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodXAYZAp2ifJaxCILL8ISpCgUGAAChFIaqkKG2hALOmCZ0oqJKm12Akw934uknOXSHYXUZu4iDOXPp4Og02GnEWnifYBeVKl1ImaG00)



```python
from datetime import date
from plantuml_compose import gantt_diagram

# Weekly scale for longer projects
with gantt_diagram(start=date(2024, 1, 1), scale="weekly") as d:
    d.task("Task", weeks=8)

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodXAYZAp2ifJaxCILKeJqtDpgda2YZApqfDBb40AofMC38mCj4rC0GYhkYGnEBiM8N4OeNe-1B3M8MSn6AW0Wkmnc8kXzIy5B2P0000)



```python
from datetime import date
from plantuml_compose import gantt_diagram

# Monthly scale for very long projects
with gantt_diagram(start=date(2024, 1, 1), scale="monthly") as d:
    d.task("Long Project", start=date(2024, 1, 1), end=date(2024, 12, 31))

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodXAYZAp2ifJaxCILN8pSyhoSYfv0eeoizAJIvH0AigLZ0oC3BHDJ048gved_oyT0MeVAn2Oh52T7o9OIocIeN4l1I5rBmKg9YXaQwn8PS3K01iAG00)



### Scale Zoom

Adjust the zoom level:

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1), scale="weekly", scale_zoom=2) as d:
    d.task("Task", weeks=4)

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/7Op12O0m303_cI8B25ewG4VmuQ-8X1f4hQqq0T7fBOLxtfqJfQ8R9LMuovvK0aN6X_cCBtuvNsXWBFdWeDXSGTCRs_L31Vn4Siv8WdxHOSP8KWNRUW77QMth7m00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodX2YZApqfDBb402nKh61aOcUWQ608HLqPcIgf2Mdv-IL9-1LTqI69nje9Xh49YiK9qV0cGaPDO35Hlgf2IM5aCbJQ2IHkXIJkavgM0hGC0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodXAYZAp2ifJaxCILKeJqtDpgda2YZApqfDBb40AofMC38mCj4rC0GYhkYGnE9i1SDOXSHYXUZu4Y0Z9x4Of0IijHWgRmIJDqANTqZDIm7R2W00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NOv12iCm30JlUiL-e127FY1FoA6t48g8HKlYo639BVrzZQ6NWYwQNJIQpBduWzMTvf9tsHmT6SPXl5w6q8RU8eVzU5QSMID_m1fnLdCy-ILWHn9kMq0BZOozbbuhWYrbaqXMzOyiDxPZ1HkMkuSLgLreRdGbJQAnF_S5)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodXoadCIozDJ4zLI4db2YZApqfDBb40InSh61aOcUWQ608HLxHZQLfwObAgWc6iGcAnGdHy2P2HarWCL6Mga99OMOnGOGHJOOIcmY4rBmLi9m00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodX2YZApqfDBb402nKh61aOcUWQ608HK2OphqGXARMaF3Kr3qb28J4l1SurDkIAzahCAqqigbG8po_AZbL8B5Q8ZYynZ5N8IIm66wYGabXPp1NjbffKXA7C25sPGsfU2jXX0000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodX2YZApqfDBb402nKh61aOcUWQ608H5unfQAgGMQoGd9-JNvIQef2Pf-2JcPvHubwKcfe7LsDiY4sDKqvfAbUqLs9UQM9HfK9uVb5sh49YiK9qV8bXh49EOZ7GFg36bCJAOYw7rBmKi8C0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/POz12i8m54JtESLSG6W-BjfT3-12S2L5vDDyQYGaadpezGq5GwamYs66Dp1ZKSwwS5GrrvpUCYksg80wEfywMsMQxQ6f5NO0Py6SGihYu2CkVddfNK98gvbkd-oZmZx01TDJgpakz-3e8D6LtMWZwKVI7qbq9AdAZ3NOldm1)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodX2YZApqfDBb402nKh61aOcUWQ608HLxHBQbbgJdv1RcfUIQn2Oh52T7o9OQn2Jc8nK9sXgK9AOcKn5qIi8B6qEBLO8JyFhj_G0BUK8PT3QbuAs7e0)



### Pause on Days of Week

```python
from datetime import date
from plantuml_compose import gantt_diagram

with gantt_diagram(start=date(2024, 1, 1)) as d:
    # This task doesn't run on Fridays (team meeting day)
    d.task("Development", days=10, pauses_on=["friday"])

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/9Sn12e0W48NXlQUO2mGg7S151sWl4aDDKPYACmNTFYbugu_7xrYmoeP9H8qr7pGBVCHWjUqxRTgK7-YccCj9IG8WWv_418Z8xMSqBFYm-gtWnSIG4wnrRwuSfUNhlm00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/PT2n2eD0303G_RuYFr1Gs-uE7JgKuYvIeWQrFHFnejI_xvqWjHGoX92yXAHESTG6MTLaepofKbXB3f8eEHsYs8V9B-IwXWj01_b3um8iEjzoXXeNPrYKe1HLwSsTg7Q1U54hjgOHS1X6cT4QuXf2gmdUJ5Q6dbWtDDdGEFfNhrtJGYNzOEdTwRAdRZXnrMxAiO3MBoJ-tfz4FrGsbRQh09d53r8uOSUbFbs_yG40)



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
![Diagram](https://www.plantuml.com/plantuml/svg/TP2n2i8m48RtFCM1izYcEWX5rDRC3cvIv6X3hKqJISwXYEzk6be4KIw1XE-3_-UsZj1IZPg8fOvw9JSi_F86QuiTF1d07iksjkQXgymeOs4cTiDuGkZQeFoG3edW8lVivM_NAEd8QFdF5aAiisMmNonTZ5MErjnaIH1QEk0HNywZs1zsFWtHSG7eu7mX_r3elBA22ditOZvX_erpNsM2IG5NlD-b_WJ4d6sbhi8ctW00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/VPBHQy8m4CRVyrSSZ3sMfQbE1p9ShNaQmuUzYOoZ1kriavBS63BytvV6TCgSurf8l_j-NuwZKqTeQOEQY4qSxMlroC9NKU76OWDV3237ShUnvaElPwOs5cxai2lVaKRJ2pOAdco5jHS8tIumVr1vNinb7dhFbLPHJHz6zuNmwi6_JLKhHqQhQnbIplcuTplLeaNo-XNtd7SLtLx-DtXM_8n1Petxw3mRjSY4539wq5hpUUaP3RiAdWERtCMLBgnvLoL1sBO3mSKWuQb_sF6gwgIbd2rVkoscAq07opVoXngTnuRWlOuT9O-C-IsKfcbhHIf2eeV49IG2b9r3IGABBJe50f8aHcHzHFOxOXQntZ1OmHRRLkdJz8ApgTBhy0jz0m00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/VPHHRzCm58NV_Iik3nDFaPAqeUiUqDgXLPE6A1CmfAf2Nd9fpLmxs4vPDUs_OyTnacO5gGzHxlLtpZszpgKsL9aD5SOGmmn7kCS7pGp27HQesKR0KibVc1jIAYQCpgdj-OFuo0-agK3Dq936wJYA4_iZcffA5VG0L27aN6eiYAx4u4qua6J0T7XffEjY7IvDoUeEVrTCuGwj0rXGiqLhPhC6gc7rmoHha0AUbnzVW5FjdDGEzU3Sh2oLt6CHZgLhsDAoHA616izvgm55GQ88FZJ3Rwb6Y2Ao-lhTHgAHgdmR02ElQojVaEvUYTSDJJO3WTMzTVLJqHtg01jxcDT55MX9JIE-uGWsQc7VcAueRom7NdQQrtEN3O3Z5jWCVoLt9KU30Vbk65Xs5DWUkInTrBtKhfKKndRqom4tyGvddELuaSJnsGiyp-N3HUQUlDjnvtOoSDjg-vfRcEmCyiOoMSrf_kY4PykR87Zk1LkDvokg96-alU2e4pp_f-2D7McZg66oJNlQcoM0JqG-7J0dlI6iNlJUiroUjxGI-RONvUUPNJDj-diVUzMwSd81NSUHuBGLd5SRk6PFtG8coNzcwDRGjHqlTTpRcvBBG_y_JjAmXljFfUuSsZlk3QP3MdT75X9ksHxVjApHgmkRzl9pPVSPaLmgB809M2X4GIvjlVx0_GK0)



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
