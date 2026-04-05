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
![Diagram](https://www.plantuml.com/plantuml/svg/NOyn2y8m48Nt_8e31wT2JRLp1UqcT2z5ZkOeaP38tNNmtnjYkxY-x-CzNYUAh0j6LQDU0y73BupgKpG3fnVD2aKHiBLjg_fSrQqHr9KTVW2PO0v9o1bPuryoNbVdTG8K69zwcY2Wv9u6iYTc79ZUsTwvtVbbuoNQjb5_5KS1YcvZNc1E8J4vy14EzwQt_SrqMIX_lW00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodX2YZApqfDBb402nKh61aOcUaQcEWQc7551sVa5vKeb2GMPySg91OhHCUN6COgv2GM0vKPAwGaLXPpHVkcfcIMvgAeCOAfCOUgySdFIqTHOGnJOMW2KUAGcfS2TWq0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodX2YZApqfDBb402nKh61aOcUaQcEWQc7551nSKPUQLA1Z6AYGMAqJ7bm0PEOd584KAvQcfsSLm5KOm5KReAXnIyrB0zW00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodX2YZApqfDBb402nKh61aOcUaQcEWQc7551-GavkLbvgN7AYGMAqJ7bnZ6OgfIICnBKKZDIq686HfmEG05mAO30000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodX2YZApqfDBb402nKh61aOcUaQcEWQc755UsScP-UdfSKg91OhHCUN6CPYAb98p4jHA4ejBCqiIYrMC5L8IQmivd98pKi16mu0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodX2YZApqfDBb402nKh61aOcUaQcEWQc755kwGMPwRdnIea5Yj4nvSOnYha91O3bHWQAAGaLXPpGSGoYnNC35GLalDp2t9IIrAveeDIop9Jos6wZ62wZE6QZC2Q30sGTJcavgM0tGC0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NSun2y8m48RXFR_YmBaGJ-rSREaauXwA74ceaPZ0tJduxvMA2gultmDV9qgiCnLLS-9wZLvXIG9eiMtijh6jSJqdJPxo12JWphgU89EyHZi8z13pJad0rrmv1aW5LkFO3mCQTwny-r7yqCsNuZyzfFcY-toFfeibBE-U)



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
![Diagram](https://www.plantuml.com/plantuml/svg/LSv12i8m48NXVKyn5oYaKRkksWE8sr9aR8SI2Kd93149lRlQceNRuVyUqx1Wa0cTI749_a63m7fYq4hNfTgNgYwwbjXChWTaw6vIzU0TfACr0orWaJ_r0KPyyRUCPFsSKxsb9tzV89qnU9j1fNxYIj7GCuFTttPgCPen4xs9XjouVlm6)



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
![Diagram](https://www.plantuml.com/plantuml/svg/RSwz2i8m58RXFLTnRg1Dcse7fpeg3k8QWXoQeFrBIiuPzEuDnHO7rvUFXwyXniWFzCpY6aFlMeOb4QX2rLcnoufQwFFfTinALHb00dtdqi28b4PxiFWcyKsT7mWuWDPFvfaEKlPTnDozS9f7bxTXafjaXBwalREhgLQpsaprr_pXaj8uRvV_7m00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/LSx12e9G40NG_VkA-mE2MhZMy0EYhKYyV5CPziPcneL_dmf2xIwNo-6MQbxiuQEPEmk_g3DibI9Fyo99ZqbQkAQQGcyjlAAvMjPYyBei3WX-LXVP23SsuxUxq6VgXHH2Fi1t7Qd26ADmG7ro50FMlNDDJUF0yuxcEvgjw9zPtOq4Jvv4mN6OVv1oYTlvBm00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NOr12e0W403llc8_4AY4vmuzeBj8BBe4OHhk5lJxmcFNOPYPMB39XaL4BQtk50KwOh3Qka6FWtQAKQwMy05i135NfgJuAZ_YPxefr_EW8W6GmQzY0cJahsOqV3ghYKhgknS0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodX2YZApqfDBb402nKh61aOcUaQcEWQc755--JdfIkK91Pdnoea5Yj4nvSOnYha91Q3LIca95OMSq742X9BYrEB5VBpuBeDJJ6aobDJybABWRgu75BpKi1s0m00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/9Smn2e0m34RXlQV81GfLr5dm0kvI99XVKKg59WxUNj7ru_5wDIwsSJPpOpaFB4OVATMXxdneVEZSD71Ua1A4Lh1T1P5OQPgjYfHOtxebuLlTJxkI8C4WhaUMR_y0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/FSun2y8m40NWFR_YRKw56ALp9-VkeSXXWYWnLt8dnNzlYB7hku_tRXAbedVAgcOk_8mtHOi4phfniEV1ZiRF9QuBIE2lUboGI2eu8T17ZBzmIhozT-3-m7NGejvA-kiu268E_HOUigPAmHb2huZ2sxvcfWhRXry0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/PSx12i8m40JGUxvYVo2GHDjpmKClFVGUYeHaCP6O3SdgzmiL5VGwynXcwkmQNrnX5ckZAtg6FUfWb1cbEaer2hj6rn4qdEXMCp9ku3hOC-iDegiLovTh9UpYxiN7DpA_Q91A2piJBEdncJhyAps8Lv4wUChKC40gC5CEOi8IzjjF)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodX2YZApqfDBb402nKh61aOcUaQcEWQc755XoGMPoiunYea5Yj4nvSOnYha91O3bHWhf2HM5aEbdM3IHZ1fKwWqM0XgQc89n0JrOeNKl1Gk1o01jXq0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodX2YZApqfDBb402nKh61aOcUaQcEWQc755EvLcvgJ4AYGMAqJ7bnZ6AkGa5WDLc2ga95OMSqM7f1QNm2IDO9B6K4cNr8AS_4gOj35CsWWg3HQ2sfXO0Z5UlLWXDI-52sAQhXr47vS3K0piK000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodX2YZApqfDBb402nKh61aOcUaQcEWQc755XoGMPoiunYea5Yj4nvSOnYha91O3bPWgf2HM5aEbdM3IHZ1fOwWqM0XgQc89n0JrOeW8bqDgNWhOVW00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/RP112eCm44NtEKLsNGanqT1LST43bDATI0awY4MCE8F5srUZ4sZfzlzvZyyKI6wYrWr4uZRv5zGaGuHIAsqJbINAYl8AsBL39HtAyabf9Nk7wqak6xVWLi_G-v5xpNsgZeEG7Lv7k-E44eP6b0z0Oj8mQI9eVa0TmJlC7RmPpHZLSTJO-uNhF6xQQh4dNs8JnK6MN7Pi5VaQMMDPSuu3xR-18H75gWk__G00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NSqx2e0m48JXFgUO2mWnYBL7iBEG88jP10q9P3T5Rk-ZjFr-c9b4gUX1ITNC9P-yApuIEEl6pWwT7OsGrXAeWGfZZrau6Adf9-l2V3qco2as3nAic_OUaUJPwotUQ2PEuJky0G00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodX2YZApqfDBb402nKh61aOcUaQcEWQc771cHOAcSKAoJdvnQaf245B9C7eyFoYR8N4elpIl1I5ZFoSp9J4ok9OXSHYXUZu4iDOXPp4Og3HvWeWOIw7rBmKiDK0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/FOr12e0m40FlVKK-K71hzUmJl8g8BBQ88bQwU_7tYgAta0oJHfIpphohcZQdDKwAfnAumjMMdANAVD5vQFg7ah08fYr93ARl8cSRzu3ZrGnWGJyg3TXORXzv13x5D3Vq75u0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NSw_2i8m40Rm_PxYUu52KgIkNTq4nrBaI0vHmaLobw5lRocwkFxW-pERS_C7gpjTMtr9SXna6CCu3U4qX8cClRVC6xW9KgaccQphd_m2CU9fg6zHMYwQIizYODo-9IlOiDmzhYXi-z0PknhDelauyW40)



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
![Diagram](https://www.plantuml.com/plantuml/svg/DOr12iCW50Ntdk9T8A0XoJe7wAAxKa8e7vLe4GN_Wz3RjmIw6sOniogbyv1Acdjlx-Y9Iob6Eow3dGQxc3-w6LdXMsaz1kIAMpuIdx6KTfhj8VG9J15kPjeXYkr5jwE8_dfkGf2FcZNMS0s_)



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
![Diagram](https://www.plantuml.com/plantuml/svg/FOqn2eD044NxFSM_WB0kOcsN9aN0KaG6Tp0RP5Pcfl7s4Y7fFk_1-uCvgMyaxk6bzSEhuqQ655FVnAw9VVZD5E7rBr87KiPQzwgSKGJFihtzeSmIfl7G8Zw33DFYxOoTx5jjaUcqCB3a-_O2)



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
![Diagram](https://www.plantuml.com/plantuml/svg/HSsn2iCm38JXtKznBn2GGyaSw5fezn2AY8thraWW2qhVlY5BrW_-kxaxcnSMz_0mVUVDSL37IECqq6MWARWc_g6U5kcqJPjQJgY2Moqllwfn2yjTYbOf-AfzLd37ylIued7VjoDXhtkOiwJZ_0y0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NOyn2iCm34Ltdq8NC3XsaZb3rqA6RYOKqPWqnTZ14e7SlgsBEcJLUpo-1c8il61YLcF9h_1Wg2S2QsolJQjDh_mbqBga2P30txcP829zb0vcFEYBzn3p9jmARynFq1h69r802rehVml4uZfntR-rnNm8RWNRKydLqZMdbNCHkpiD6qAQwszl)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NOun2eD054JxFSLqLi9cIQmzWc0f4eQuA28g-oU5jy-YsAGR7k_1r2OcZLmbrwHjZX_XH8RWGrNwP-ahrpKJBUBHWuRkhJmMMdPU67YOQ-FEH6q9yzS4wf8AGro7kmvt7VxgEaldWny0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodX2YZApqfDBb402nKh61aOcUaQcEWQc755kwGMPwRdnIea5Yj4nvSOnYhavobKE-Pa9gVMAkGa5WDLcoga95OMWrIMfURa5y2K6a6KEkKdrIfKEoSMvUV0D1WQG7GufEQbWEq70000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodX2YZApqfDBb402nKh61aOcUaQcEWQc755kwGMPwRdnIea5Yj4nvSOnYhavobKE-Pa9gVMAkGa5WDL6neef2HM5dD5EvLcvgJ0L1f1L3hb9w6hW-dEB5R8Jqi3gOBPPsYAJzAC2s8QkfIfhe4XbqDgNWhOBm00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/7Sr12i8m48NXVKxnBb28nNPTmGEuBqM6PAYHEe6ySI7IkolT_elld-ZIV1Lp3xTMdveSHoBws8zTF7Tn38-I5KrPtoqfOV9IXlcgBAij46A--sb1DNmlMqcwOnF-YG5PFWoJMZuMFm00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/9Smz2e0m343XFQV81GhrXyuUmC5TYWGDHIrHce1uUqNdz_4wDIgMICpWBAkOpfGPB-Oztp2KO-FPy4EAjQ-3ywtp0SR-a8JdtoEIuZXP5J6Jlh3nkD2jqB4it_i1)



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
![Diagram](https://www.plantuml.com/plantuml/svg/9Sr12eGm30NGVK_nBo3KAguzWcj59DWmZDPMce1qJgyu-mUl5wMi7uggvipVgB9IO5pCUoZufNJ0cI6dZLV5QmNEkgwoRMKxCusFO8_pBsQGO5gqdX587jfOU2fYUex-JMu0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/7Sn12e0W4030kw_O3mWcuhadTEWM4fikKOc5kn3-ll0-pCY2LNOi8kgfHn6Ec0bUeYitDTNxf2ZG4OCrrclZjF5gcIl6Yn9ihUC0oB2iCWJ8oByT72Hih4OggVSV)



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
![Diagram](https://www.plantuml.com/plantuml/svg/7Or12i8m54JtESLS812Br6qN7i1zAV9jFbhxYP8_K7fxOxSpyzuCJgbyIY73jow5FeifDjNLTcmBN_W79Kj55cgurSzRP-BW75tg-fZECVLXlBO-cZpKD8FYwmHnZ7UU9fXuMr-QO_SmDDzn-GC0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/DOt12eCm44Jl-Ohv0I4HoTaVAFGkKfPcKLhTWBjL-lU6YCTvyuRfrMYpYSJCFRVyuRUX8aNhszZuhl7H7SnVlNaMh5aI_K6IiFxKCDFE8CF2L590ATKDZykgin6a65uMHYp5KGH_MJrBglSd)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgIK_CAodXoadCIozDJ4zLI4db2YZApqfDBb40InSh61aOcUaQcEWQc755EvQcfIScfSOg91OhHCUN6COgv2GM0zMOAwGaLXPpEQJcfO3D0m00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/JOrB2eGm40NtESMxG21-9ckFC2it8j9E6iaWBQGRnDihui9blO9NdHeLMqZCtBTiV_uPxabHXphwqFeGBvF5CBFjpF8I84aFVdnJkQ7FckULKKWM7a6AOR9gn4fwFSQ0H8UwZYNToHC0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NS_12eCm30RWUvuYiBEWTNgMAUuonkv5Hh15EsehRNROssyeJhRhdtm_IHMP0W_acE4M_4FtZ4iKKQIYJD9ZafOWws3Oz6Gxf8Zopbc7bk9dgK15hmXhP2BstlgW5Hg7XxQjcqQ0lFemxLHiDFzIyKylPXZvP9yQPEETtcZUuKZphDr-N5R0ElWjE7kheD9EBP-z0G00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/VPB1RiCW38RlUGgadhibj4aRgPhQad2Qfabx0ZT16Gk12JnLtTHtNyBeDArDi3ZmOt_Onbk7OB41ZHXj79wKU8ZygP3GMEZ8LqJ87ggsiUP3rymeOydnLQBeTMuqFa4doCvAK45uaP-293ISVW9c2xzw3S6rddbDdPKBJddXxnwb5a5DybLM3BXplpkfX4EZnHY3SvwpvNy6ptThcWQ64-zW0NjzB0zMSfxuEr_Gq1LoCAeE06rmwlrrcGJ7Nfv8jVGhkAAfuJGEPMpFhehYwOfU6WFMccE8_-EpIWSBFdS7PQfMrAFFf8FzrXtKl1piWgYiH5c1caYryBzritVdQ7CVXkpPcZTH8V7pvmYDQJQFb_CuYxP2rtu4lm40)



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
![Diagram](https://www.plantuml.com/plantuml/svg/VPHjQo8n4CVVvrCC7CUzshgkhjfIIgssHUY1z_X6v4XtHyqPaxrajbQat_sopxfS3nGqC_d__ZF9vDOIDxJcYeYH88dm9O2vvBJIPWUVnTfm4bgnQqi7YJSipvmAxjPtS6G0nEqs_m5mnwFjskXKnHCjjO4Fzxs7u67gOc_kknCIBMc5xsG_QXcNgHOJxhXkiKXzq8g-PNnuhfBUs7Mdj9GOeSX6t8NtY5jvO7EZVsD4aDTc8V23WUVtFN_0BAVKnFm0t214KbkCcNKMpbUA3Q4NX23i-QBxT84qrF_2OcDM0iOW53o9zOOU3Q9Yf3DXqJZezfkrzfQ9DbooZOWH35gTcWWjhBIcP_tA5ZErCjoIIIDN0C8uZGKjWLjO_ABk4hI2urYA2Dz0kZGB8JYCPKNKqRg-_z4XTub4GhOOcsWZ20knALgnLfLQSAPslDFFbUQerdGvPMyv5Gu-MK0Lbp776uQdk880uoGn-eNB2jLRmeOd2QfA9wXqF0_c6suHWYkOPIexL9JVHF0yjhXBXOnXF9_14p-WgVJwXVNSyd72ZPQLzMxJZtxBU-_4Ut_PEfaFaz7zO79P4N_CAbHOeARyHSGr9AWXOGlIpo3vIXbz1pFbn9kfgs230dPMKLFGe6RviDTcAzGwZm5V4PgQdfMeD6KpHAHtx2l-IOMxQR3ZRdvGSHMv0H8grdlcSY7BPSr1zAxW9vSYRWvXvdQLHk6x6st7hGmFp-_GUPVysldmNrqgZyBroBifjCeYcxzpDDdpb3jkaKSdLw3Tg54BDpp1kLZ2K-lQuRQlZAlpm1QFsetc2rRQb-thEZeHk6oVQVwU5G4frDPchyPYiI5Ax5MdinTRSO6lFBlR5svGEcljoOorP5NRd9nUhJ8_rNlaX_yB3jYjyv8_q7y1)



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
