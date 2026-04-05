# Activity Diagrams

Activity diagrams show workflows with decisions and parallel execution. They are ideal for:

- **Business processes**: Order fulfillment, approval workflows
- **Algorithms**: Code flow with branching logic
- **User workflows**: Registration, checkout flows
- **Parallel operations**: Concurrent task execution

Unlike state diagrams (which track one entity's lifecycle), activity diagrams show step-by-step processes with decision points and parallelism.

## Quick Start

```python
from plantuml_compose import activity_diagram, render

d = activity_diagram(title="Order Process")
el = d.elements

d.add(
    el.start(),
    el.action("Receive Order"),
    el.action("Process Order"),
    el.action("Ship Order"),
    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LV0lIaajKWWeoazEBIxc0ajoMGMb9gTcba4bhRcieD9mVd16PW6CKroINy3ba9gN0ZGJ0000)



The pattern is:
1. Create a composer with `activity_diagram()`
2. Get the namespace: `el = d.elements`
3. Build the flow with `d.add(el.start(), el.action(...), el.stop())`
4. Everything is sequential -- items are rendered in the order added
5. Render with `render(d)`

## Elements

### Actions

The basic building block. Actions are rounded rectangles by default, with optional SDL shapes and stereotypes:

```python
from plantuml_compose import activity_diagram, render, Gradient

d = activity_diagram()
el = d.elements

d.add(
    el.start(),

    # Basic action
    el.action("Process Request"),

    # Action with inline style (background color)
    el.action("Critical Step", style={"background": "#FFCDD2"}),

    # Action with gradient background (two colors)
    el.action("Gradient Step", style={"background": Gradient(start="#4CAF50", end="#81C784")}),

    # Action with UML stereotype
    el.action("Read Input", stereotype="input"),

    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8pkAm2YlAJKukB5O9I2qjJYqkikPJTt9nTN8oid8ioIpAJ4tCKWajI2u329iwERgO6DHQ6pkOM9bRkHOafcQbv9L1Pgw3Kn1G5pxo2qX9h6vjC46rd1xGYlu3B8JKl1MWV0000)



### SDL Shapes

Actions can use SDL (Specification and Description Language) shapes:

```python
from plantuml_compose import activity_diagram, render

d = activity_diagram()
el = d.elements

d.add(
    el.start(),
    el.action("Standard Action", shape="default"),       # :text;  rounded rectangle
    el.action("Start/End Shape", shape="start_end"),      # :text|  stadium/pill
    el.action("Receive Event", shape="receive"),           # :text<  left-pointing flag
    el.action("Send Signal", shape="send"),                # :text>  right-pointing flag
    el.action("Data Flow", shape="slant"),                 # :text/  parallelogram
    el.action("Document", shape="document"),               # :text]  wavy bottom
    el.action("Database Op", shape="database"),            # :text}  cylinder
    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8pkAo2InBpKXABKXGSaqioy_EimI959VgkUIaAmHc91QarN5P1gScfcMMf2gvbgNabDa0LgI39pFIyn1mxBYkNn9941RUS_79z83i_kJGNg2WM8foKM9ogu5zG2xGilu3B0QWDQ3C0)



| Shape | PlantUML | Visual |
|-------|----------|--------|
| `"default"` | `:text;` | Rounded rectangle |
| `"start_end"` | `:text\|` | Stadium/pill |
| `"receive"` | `:text<` | Left-pointing flag |
| `"send"` | `:text>` | Right-pointing flag |
| `"slant"` | `:text/` | Parallelogram |
| `"document"` | `:text]` | Document (wavy bottom) |
| `"database"` | `:text}` | Cylinder |

### Stereotypes on Actions

UML stereotypes classify actions visually:

```python
from plantuml_compose import activity_diagram, render

d = activity_diagram()
el = d.elements

d.add(
    el.start(),
    el.action("Read Config", stereotype="input"),
    el.action("Transform Data", stereotype="process"),
    el.action("Send Notification", stereotype="sendSignal"),
    el.action("Wait for Response", stereotype="timeEvent"),
    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/7Ox12iCm34Fl-Gf_HrTAOTjrXtQmiscTOcZi4Blx_Zcx2Jr9Q3R7vbSvqr-aOI7SuQwI-RYD8qkzV9hIy6uebhKLUA1ZaDfq8xFELf8TNkgSUKDdbS0Mtig7uDaJ7sI7QCD2LbMC8k5SwFabwVFcMjCSbJZo0m00)



### Action Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `label` | `str \| Label` | required | Action text |
| `shape=` | `ActionShape` | `"default"` | SDL shape type |
| `style=` | `StyleLike \| None` | `None` | Background color/gradient only |
| `stereotype=` | `str \| None` | `None` | UML stereotype (<<name>>) |

### Start, Stop, and End

```python
from plantuml_compose import activity_diagram, render

d = activity_diagram()
el = d.elements

d.add(
    el.start(),       # Filled black circle
    el.action("Do something"),
    el.stop(),        # Filled circle with border (normal termination)
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8pkAnSyXMAytDJIp8oyzAjWOBv1LmEgNafG1K0)



```python
from plantuml_compose import activity_diagram, render

d = activity_diagram()
el = d.elements

d.add(
    el.start(),
    el.action("Do something"),
    el.end(),         # Circle with X (alternative termination)
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8pkAnSyXMAytDJIp8oyzAjkLBpKhWSW0HG0G00)



## Arrows

Customize the arrows between actions:

```python
from plantuml_compose import activity_diagram, render

d = activity_diagram()
el = d.elements

d.add(
    el.start(),
    el.action("Step 1"),

    # Arrow with a label
    el.arrow("next step"),
    el.action("Step 2"),

    # Dashed arrow
    el.arrow("async", pattern="dashed"),
    el.action("Step 3"),

    # Dotted arrow
    el.arrow(pattern="dotted"),
    el.action("Step 4"),

    # Hidden arrow (connects but invisible)
    el.arrow(pattern="hidden"),
    el.action("Step 5"),

    # Styled arrow (color and bold)
    el.arrow("important", style={"color": "red", "bold": True}),
    el.action("Step 6"),

    # Color-only string shorthand
    el.arrow(style="#blue"),
    el.action("Step 7"),

    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/HOxB2eCm44Nt-Of0jtNHfs2W-0zTIXUnCw0G9o4PeVrxnq5nDvnpvtBRmZxpF0MZXsdUZCbUdAcgboNyiIq2tCQlmZlmPK3uYFVbJz_TtTH5PdKRlAzm606G3lXOuIaZdFiOj6YSKipiYVUofqRwCEFnLZlP69DfaK06Bm00)



| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `label` | `str \| Label \| None` | `None` | Arrow label text |
| `pattern=` | `"solid" \| "dashed" \| "dotted" \| "hidden"` | `"solid"` | Line pattern |
| `style=` | `LineStyleLike \| None` | `None` | Color, bold, thickness |

## Control Flow

### If/ElseIf/Else

```python
from plantuml_compose import activity_diagram, render

d = activity_diagram()
el = d.elements

d.add(
    el.start(),

    # Simple if/else
    el.if_("Valid?", [
        el.action("Process"),
    ], "no", [
        el.action("Reject"),
    ], then_label="yes"),

    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8pk3BJ53J24dCoK-mr5KeoKlCKD2fJYpMv51Ii0ehoarEBYwsvKdEAKnKqylB1ea6fMQd99K31l9JCDA0P-GLS3a0sq400)



```python
from plantuml_compose import activity_diagram, render

d = activity_diagram()
el = d.elements

d.add(
    el.start(),

    # If/elseif/else chain
    # Extra branches are alternating (label, events) pairs
    # Non-last branches with string labels become elseif conditions
    # The last branch becomes the else
    el.if_("Score >= 90?", [
        el.action("Grade: A"),
    ], "Score >= 80?", [
        el.action("Grade: B"),
    ], "Score >= 70?", [
        el.action("Grade: C"),
    ], None, [
        el.action("Grade: F"),
    ], then_label="A"),

    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8pk3BJ53I2a_EBKXNiR1Ki3Umr5KeoKlCKD1mrkHGKhDoB4bDIhHGShRbISufJKTHQmDGYgNF2eiuSYpfdY3ea4JUWI5vAPXhGLVa5N0v0Dj290000)



The first positional `events` list is the "then" branch. Additional branches are alternating `(label, events)` pairs. The last branch is the "else". Use `then_label=` to label the "then" arrow.

### Switch/Case

```python
from plantuml_compose import activity_diagram, render

d = activity_diagram()
el = d.elements

d.add(
    el.start(),

    # Cases are (label, events) tuples as positional args
    el.switch("Request Type?",
        ("GET", [el.action("Handle GET")]),
        ("POST", [el.action("Handle POST")]),
        ("DELETE", [el.action("Handle DELETE")]),
    ),

    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8pk8hBCqkICnGqWb8BIrEBInH2AWjIxJMvaXEBKnKqt5r3DBaK5Amy4lDISb8LW5nhg4o0Vp2A58WFatDnzN4DSKMMXOXOSwNcfK3i0rgUNy3b0EG3NG80)



### While Loop

```python
from plantuml_compose import activity_diagram, render

d = activity_diagram()
el = d.elements

d.add(
    el.start(),

    el.while_("Items remaining?", [
        el.action("Process next item"),
    ],
        is_label="yes",            # label on the "true" path
        endwhile_label="no more",  # label on the "exit" path
        backward_action="increment counter",  # label on the backward arrow
    ),

    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/BOqn3iCm30DtlO9Z_8LaQDPk-OBh2AdGM2ua1Mb_7wFeHe0ytkoHBOwwqo_G-PITCTo3gyEuPb7HxPOWZk7BdWWO5sk5tQ7y2KYVJlJ8vNLcMp6Abiwn1aexDDWcObt_lzfGct7gjlQckHTTVG40)



| Parameter | Type | Description |
|-----------|------|-------------|
| `condition` | `str` | Loop condition text |
| `events` | `list` | Loop body |
| `is_label=` | `str \| None` | "True" path label |
| `endwhile_label=` | `str \| None` | "Exit" path label |
| `backward_action=` | `str \| None` | Backward arrow label |

### Repeat (Do-While)

```python
from plantuml_compose import activity_diagram, render

d = activity_diagram()
el = d.elements

d.add(
    el.start(),

    el.repeat([
        el.action("Attempt connection"),
    ],
        condition="Connected?",        # exit condition
        is_label="no",                 # label for "repeat" path
        not_label="yes, done",         # label for "exit" path
        backward_action="wait 5s",     # backward arrow label
        start_label="retry loop",      # label at the top of the loop
    ),

    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/DOun3iCW40HxNh4bI6dJG657UGc1auACxn1SXFnxMudIRJ6ZsNLexFhPg_aEqwbHLFXEsWzKaHOCu1-gj3T54cPAMeI3USMqpTWp_8n5SH_XRyztgGJx_C6K5uSoO5aSM1Jse7535YPtLQMPbJXV5qu0)



| Parameter | Type | Description |
|-----------|------|-------------|
| `events` | `list` | Loop body |
| `condition=` | `str \| None` | Exit condition |
| `is_label=` | `str \| None` | "Repeat" path label |
| `not_label=` | `str \| None` | "Exit" path label |
| `backward_action=` | `str \| None` | Backward arrow label |
| `start_label=` | `str \| None` | Label at loop start |

### Break

Break out of an enclosing loop:

```python
from plantuml_compose import activity_diagram, render

d = activity_diagram()
el = d.elements

d.add(
    el.start(),

    el.while_("Processing?", [
        el.action("Process item"),
        el.if_("Error?", [
            el.action("Log error"),
            el.break_(),   # exits the while loop
        ], "no", [
            el.action("Continue"),
        ]),
    ]),

    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/BOun3eD030Hxly8bzmKeG8hIKUGB91YmSjYHpoZVZpdIM3khrNg7ufFviMUe0huRPyBcOVgYKbZMFW5Y-sTafxqBWnTixcPgVKBVICAArAWhqkbsbPz6qpiKvHALekbAtLISvQ0pH3Bp0d7htzYW7nW2Oz0F)



## Parallel Execution

### Fork (With Synchronization Bar)

Fork splits into parallel branches and synchronizes at the end:

```python
from plantuml_compose import activity_diagram, render

d = activity_diagram()
el = d.elements

d.add(
    el.start(),

    # Each branch is a list of elements as positional args
    el.fork(
        [el.action("Task A1"), el.action("Task A2")],
        [el.action("Task B1")],
        [el.action("Task C1"), el.action("Task C2"), el.action("Task C3")],
    ),

    el.action("All tasks complete"),
    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8pkDBoYxAv51IiGXABinKS3QqHR2DhiAH2OdfYPXvSsCaGgx0paavd8oIsiJLNQbwA0jWQAyUS78KIe72nGd9-Ra5EQacgDT0P-GLS3a0rG3S10000)



#### Fork End Styles

Control how the fork block ends:

```python
from plantuml_compose import activity_diagram, render

d = activity_diagram()
el = d.elements

d.add(
    el.start(),

    # "fork" (default): end fork (synchronization bar)
    el.fork(
        [el.action("Path 1")],
        [el.action("Path 2")],
        end_style="fork",
    ),

    el.action("After fork sync"),
    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8pkDBoYxAv51Ii0X9BCXGChS5yXSJqnCmykAYHDLTgNee2MAMLOrf9QX6OhL1ScPTi3JGclu3B0QW0Q2O0)



| `end_style` | PlantUML | Meaning |
|-------------|----------|---------|
| `"fork"` | `end fork` | Synchronization bar (default) |
| `"merge"` | `end merge` | Merge without sync |
| `"or"` | `fork again` | OR semantics |
| `"and"` | `end fork {and}` | AND semantics |

### Split (No Synchronization Bar)

Parallel paths without a visible sync bar:

```python
from plantuml_compose import activity_diagram, render

d = activity_diagram()
el = d.elements

d.add(
    el.start(),

    el.split(
        [el.action("Path 1"), el.action("Merge back")],
        [el.action("Path 2"), el.action("Merge back")],
    ),

    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8pk8eBSZ9Bk1GKh08IIp8K3Ar1JD_KelHKXQJ4v6nhYBn2OdfYPXvSbH66gjIy50M8ISKb-GLS3a0-q0e0)



## Organization

### Swimlanes

Vertical partitions showing responsibility:

```python
from plantuml_compose import activity_diagram, render

d = activity_diagram(title="Order Process")
el = d.elements

d.add(
    # Swimlane declarations must come before start in PlantUML
    el.swimlane("Customer"),
    el.start(),
    el.action("Place Order"),

    # display_name= shows a different label in the header
    el.swimlane("warehouse", display_name="Warehouse Team"),
    el.action("Pick Items"),
    el.action("Pack Order"),

    # color= sets the lane background
    el.swimlane("shipping", color="#E8F5E9", display_name="Shipping"),
    el.action("Ship Package"),

    el.swimlane("Customer"),
    el.action("Receive Package"),

    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/JOx12i8m44Jl-nKBVeEWwQKW5JnPgk0vf4CRR9gIJVMIZpUL5hszOTwmMqhK8Svke6ZZ0Bw65e7hu0r4A9rcYTuX9FfwfEf1czKgABrrGEzdGUB7Xdo7TbcqvicN22T53Zg7RRIh3kTzTKpIsscoOvVujXAfXNYnTOVY_xngO61V-9MvcQZ4sERdFm00)



| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Lane identifier (used to switch back) |
| `color` | `ColorLike \| None` | Lane background color |
| `display_name=` | `str \| None` | Visual label (instead of `name`) |

### Partition

Visual grouping box around activities:

```python
from plantuml_compose import activity_diagram, render

d = activity_diagram()
el = d.elements

d.add(
    el.start(),

    el.partition("Validation", [
        el.action("Check input"),
        el.action("Verify credentials"),
    ], color="#E3F2FD"),

    el.partition("Processing", [
        el.action("Transform data"),
        el.action("Save results"),
    ]),

    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/JOwn3i9034Ft-uge_05iTAa4T4O2TOzwAKHSSrMIGqA8VwSj2ujb3tvsOuxgPKnXDM6QXPspGDLXueYBhs1pshNRzWZl0B0_tAb_0CjKl5voHyh32tgbIEACoUhm-IUTDVTandAhVeIhejYGTOHv05V81Py4IbQIhtNpF8M69CxVlW00)



#### Partition Keyword Variants

The same grouping box rendered with different PlantUML keywords:

```python
from plantuml_compose import activity_diagram, render

d = activity_diagram()
el = d.elements

d.add(
    el.start(),

    # partition (default keyword)
    el.partition("Standard Partition", [
        el.action("Step 1"),
    ]),

    # package keyword
    el.package("Package Group", [
        el.action("Step 2"),
    ]),

    # rectangle keyword
    el.rectangle("Rectangle Group", [
        el.action("Step 3"),
    ], color="#FFF9C4"),

    # card keyword
    el.card("Card Group", [
        el.action("Step 4"),
    ]),

    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8pk0g0H6P9PdwUWb9mIM9UIc9HYa80J4n9ePfBGS4gk2IrGC7GcgiMg3evEp4zLK4f0CfmByelBK1MPWHILfIQ33GhFGUeC0ZEX2fLTdDpitGsGT9Y3DAI3B9OoHb4OfXf0b9GN99VmEMGcfS2T3i0)



### Group

Minimal visual grouping (lighter than partition):

```python
from plantuml_compose import activity_diagram, render

d = activity_diagram()
el = d.elements

d.add(
    el.start(),

    el.group("Setup Phase", [
        el.action("Initialize"),
        el.action("Configure"),
    ]),

    el.group("Execution Phase", [
        el.action("Run"),
        el.action("Verify"),
    ]),

    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8pkDAByaiB589JIu1aG4PYSQf2DPU2WfLdNcP9Pc9EPbMgDOZhd9-NbfbUMWJarKArk5Qa9fUMPERd8MiBAiq3gmzBBSfCgmGfBYx9B-1oICrB0Le90000)



## Notes

### Positioned Notes

Attached to the adjacent action:

```python
from plantuml_compose import activity_diagram, render

d = activity_diagram()
el = d.elements

d.add(
    el.start(),

    el.action("Process Data"),
    el.note("This step takes ~5 seconds", "right"),

    el.action("Save Results"),
    el.note("Writes to PostgreSQL", "left"),

    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/BOqn3i8m40JxUyLzWiOqAIWf0a6Yjf9BOc5yaNT3oTknKBefPZGT62ltTvO_IEYhZmRe9JAUfJXDQrfM1dsi2GhQfemlWtvF2XkzJ90mn8_ftR1dugYopIrwriJcqhLtSAastAvjvPjqLgRs_G40)



### Floating Notes

Independent notes not attached to any action:

```python
from plantuml_compose import activity_diagram, render

d = activity_diagram()
el = d.elements

d.add(
    el.start(),

    el.note("System overview:\nThis flow handles\norder processing", "right", floating=True),

    el.action("Step 1"),
    el.action("Step 2"),

    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/BOr12iCm30JlUeM-q1wJI_wGVi3KszZWM4PI4_hxYf3RCWopYtbI_-wDha6V9ibhtxYBWxLknObv_PbZPpcWHyKv1NgLQXpsoINrt631H3EKXyeRPX4Xz7o5Q5eTWn_pFPvptCcW9OJu_WC0)



| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `content` | `str \| Label` | required | Note text |
| `position` | `"left" \| "right"` | `"right"` | Which side |
| `floating=` | `bool` | `False` | Float independently |

## Connectors, Goto, and Label

### Connectors

Named circle connectors for jump points:

```python
from plantuml_compose import activity_diagram, render

d = activity_diagram()
el = d.elements

d.add(
    el.start(),
    el.action("Step 1"),
    el.connector("A"),        # creates connector point "(A)"

    el.action("Step 2"),
    el.connector("A"),        # jump back to connector A

    el.action("Step 3"),
    el.connector("B", color="red"),  # colored connector
    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8pkAo2Ir8B50ojkJGSDQ4S8sIEiJMNSb5gYfM6aoPGHtu1bqDgNWfGEm00)



### Goto and Label (Experimental)

```python
from plantuml_compose import activity_diagram, render

d = activity_diagram()
el = d.elements

d.add(
    el.start(),
    el.label("retry"),       # label target
    el.action("Attempt"),
    el.if_("Success?", [
        el.action("Done"),
    ], "no", [
        el.goto("retry"),    # jump to label
    ], then_label="yes"),
    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/BOsx3O0m30LxJ-4oh0058B414mHuVAGGHx4fs9w0w4vNt7LgFjjr1lg0WfyGECFoJNLlXZDPGyVARhpc6QfjnROZihkX5J7NWqGqXA1W5-LLcvZy2SJbM4jQ4dM5o-S1)



## Kill and Detach

### Kill

Abrupt termination (X symbol):

```python
from plantuml_compose import activity_diagram, render

d = activity_diagram()
el = d.elements

d.add(
    el.start(),
    el.if_("Fatal error?", [
        el.action("Log fatal"),
        el.kill(),           # abrupt stop
    ], "no", [
        el.action("Continue"),
    ]),
    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/7Omn3e0W303tlg8ZV446IKoS_0I9HOcrDL3-BxhTvPABpLArVZFy02MZMvCbHgfLw-pHJX90d3OzC7yb3BiACn0tGYVglxoeM95E0KZsaiTE7uY3n_i5)



### Detach

Detach from flow (for async continuations where the path just disappears):

```python
from plantuml_compose import activity_diagram, render

d = activity_diagram()
el = d.elements

d.add(
    el.start(),
    el.fork(
        [
            el.action("Main path"),
            el.action("Finish"),
        ],
        [
            el.action("Fire-and-forget"),
            el.detach(),    # this path ends without connecting back
        ],
    ),
    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8pkDBoYxAv51IiV1CpynGA4aioh44yjyoyp68W4oIha9WEb8E85gNg9kQbw0A5qrDBG2fJKaiIapEuKlDI5C0c5PVa5t0v0Bb06m00)



## Styling

### Inline Action Styling

Only background color (and gradient) is supported on actions:

```python
from plantuml_compose import activity_diagram, render
from plantuml_compose.primitives.common import Gradient

d = activity_diagram()
el = d.elements

d.add(
    el.start(),

    # Solid background color
    el.action("Normal", style={"background": "#E3F2FD"}),

    # Named color
    el.action("Warning", style={"background": "yellow"}),

    # Gradient background
    el.action("Gradient", style={"background": Gradient(
        start="#4CAF50", end="#81C784", direction="horizontal",
    )}),

    # Gradient via constructor
    el.action("Gradient Dict", style={
        "background": Gradient(start="#FF5722", end="#FF8A65"),
    }),

    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8pk9HTZTsCt5oi_FABSXDphBcKArDpSlBBhS8JY_8oyzA10YREZcwc1ZKMXixc5YPMxaM9APcfUIL02JStKtCZenetDmj7CrEuX89BPZ9GjhWalu3B8JKl1MWL0000)



### Diagram-Wide Styling (`diagram_style=`)

```python
from plantuml_compose import activity_diagram, render

d = activity_diagram(
    title="Styled Activity",
    diagram_style={
        # Root-level: diagram background and fonts
        "background": "white",
        "font_name": "Arial",
        "font_size": 12,
        "font_color": "#333333",

        # Activity boxes
        "activity": {
            "background": "#E3F2FD",
            "line_color": "#1976D2",
            "round_corner": 10,
            "padding": 8,
        },

        # Decision/merge diamonds
        "diamond": {
            "background": "#FFF9C4",
            "line_color": "#F9A825",
        },

        # Flow arrows
        "arrow": {
            "line_color": "#757575",
            "font_size": 10,
            "line_thickness": 1,
        },

        # Partitions
        "partition": {
            "background": "#F5F5F5",
            "line_color": "#9E9E9E",
        },

        # Swimlanes
        "swimlane": {
            "line_color": "#BDBDBD",
        },

        # Notes
        "note": {
            "background": "#FFF9C4",
            "line_color": "#F9A825",
        },

        # Groups
        "group": {
            "background": "#ECEFF1",
        },

        # Title
        "title": {
            "font_size": 16,
            "font_style": "bold",
        },

        # Stereotype-based styles
        "stereotypes": {
            "slow": {
                "background": "#FFCDD2",
                "font_style": "bold",
            },
            "critical": {
                "background": "#FF8A80",
                "line_color": "#D32F2F",
            },
        },
    },
)
el = d.elements

d.add(
    el.start(),
    el.action("Process"),
    el.if_("OK?", [
        el.action("Done"),
    ], "no", [
        el.action("Retry", stereotype="slow"),
    ]),
    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/fLFBRi8m4BpxAonnWKjBGda44EKHV6dL8kWFkF425ewD75D44VzUsxYqWkRKh2B5avdPjNSzB0pLPfSBPBWHW1Vc883XKMRu1pS7r2ySC40q02cdAqrpV4GOZscsMMcrasoYXD9ul-O6B4wKD2yq1ppId8e0BFWdu2WEgxEWql2FnRxjlU-jSsNQ8359_RzdBY6WKT9kfR57vsUobg1nLFVGZ3B6vGftxEfatwtTA3TSoR8afEdYEaaoTH4yYZtF1PKGB7xHngcBG6ESvagoqaI499E7QmUIZ3fnCpX8PU0VSiVVbXxcP4f859XKQxM_tKwxwUA2lgrvjf5G53Zos4z7wy7dBjFsS3CgoglkZ3hrwpnf8xQT_VOenAMMF_IJD3JRPtTpYT-LO5vyGanbknoayVhpC1-lQcsLg_ltOT3zVK3TcLQPtMuFyIMklZuzrh1PWxJaRgeaz1280d1Lgfg3vc3qeTVlk_870mIIyQKrKbiqjD_sSdq1)



**`diagram_style=` selectors:**

| Selector | Target | Style Type |
|----------|--------|------------|
| `background` | Diagram background | `ColorLike \| Gradient` |
| `font_name` | Default font | `str` |
| `font_size` | Default font size | `int` |
| `font_color` | Default text color | `ColorLike` |
| `activity` | Activity boxes | `ElementStyleDict` |
| `partition` | Partitions | `ElementStyleDict` |
| `swimlane` | Swimlanes | `ElementStyleDict` |
| `diamond` | Decision/merge diamonds | `ElementStyleDict` |
| `arrow` | Flow arrows | `DiagramArrowStyleDict` |
| `note` | Notes | `ElementStyleDict` |
| `group` | Groups | `ElementStyleDict` |
| `title` | Diagram title | `ElementStyleDict` |
| `stereotypes` | By stereotype name | `dict[str, ElementStyleDict]` |

## Advanced Features

### Theme Support

```python
from plantuml_compose import activity_diagram, render

d = activity_diagram(title="Themed Activity", theme="cerulean-outline")
el = d.elements

d.add(
    el.start(),
    el.action("Step 1"),
    el.action("Step 2"),
    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuL8ioKZDJLL8JYqgpKbDpDFDBot9oSnBvIh9BCb9LGW1IQOeE2QNP9PbbbHoWRLnMGMNf1Oe65f36KRMGF7y0Yw7rBmKe940)



### Layout Engine

Use the Smetana layout engine for local rendering without Graphviz:

```python
from plantuml_compose import activity_diagram, render

d = activity_diagram(layout_engine="smetana")
el = d.elements

d.add(
    el.start(),
    el.action("Process"),
    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuL8iA4fCpqrKo4cip2yjKIZEJIr9p4la0ijpMGKKvIUd5XTR0_dv1LmEgNafG3q0)



### Line Type

Control arrow routing style:

```python
from plantuml_compose import activity_diagram, render

# "ortho" = right-angle routing, "polyline" = angled routing
d = activity_diagram(linetype="ortho")
el = d.elements

d.add(
    el.start(),
    el.if_("Check?", [
        el.action("A"),
    ], None, [
        el.action("B"),
    ]),
    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/7Smz3e0W343XlQVeg5VGmR-J42sX0Gg1EdXxgzitlBorgsjwvmGzibJNNCR4GlfKmj8q5FWBO8_34UYCouWQI01nscQWrEdZRfIBlTMbmcgsvmi0)



### Vertical If Layout

Force if/else diamonds to render vertically instead of horizontally:

```python
from plantuml_compose import activity_diagram, render

d = activity_diagram(vertical_if=True)
el = d.elements

d.add(
    el.start(),
    el.if_("Condition?", [
        el.action("True path"),
    ], None, [
        el.action("False path"),
    ]),
    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/DOqz2e0m34Rtd29kUWKTB0Y2kxW7JRLGszAczpSARe_7zsEAK9PwUsXIflCch8Ktpk9syel56E1BWBFOJZ4SJbmCOuToSG34VisLCP5S0x0l_AgP57wd3QiJCO5HrgC7)



### Diagram Metadata

```python
from plantuml_compose import activity_diagram, render

d = activity_diagram(
    title="Order Processing Workflow",
    mainframe="Order Module",
    caption="Figure 3: Complete order flow",
    header="ACME Corp",
    footer="Page 1",
    scale=1.5,
    legend="Color guide:\nBlue = normal\nRed = error",
)
el = d.elements

d.add(
    el.start(),
    el.action("Process"),
    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/DKzB2W8n3Dtd53c18E9cHF23xWO7DwxBD5EBQLCoBLxVEEWglBnFyWvpTLfROaWkvabT8hof9yLUV6E2UNHCk5vjeSRAVt9G6McUOmxu47rDB6yOALUZdkI-YkEvl-1PjFptayXt32vO78okr2WPhp4q9Tnqfas5gHBASc69P0gKFQ2HB8gXHK-TmHCtmZrcqUJOy9syGL8L1JFyR4irw7w_xWnBWOCnLlS3)



### Complete Example

```python
from plantuml_compose import activity_diagram, render

d = activity_diagram(
    title="CI/CD Pipeline",
    diagram_style={
        "activity": {"background": "#E3F2FD", "round_corner": 8},
        "diamond": {"background": "#FFF9C4"},
        "arrow": {"line_color": "#546E7A"},
    },
)
el = d.elements

d.add(
    el.swimlane("Developer"),
    el.start(),
    el.action("Push to Git"),

    el.swimlane("CI Server", color="#F5F5F5"),
    el.action("Clone Repository"),

    el.fork(
        [
            el.action("Run Unit Tests"),
            el.action("Run Integration Tests"),
        ],
        [
            el.action("Lint Code"),
            el.action("Check Types"),
        ],
        [
            el.action("Build Docker Image"),
        ],
    ),

    el.if_("All Passed?", [
        el.swimlane("CD Server", color="#E8F5E9"),
        el.action("Deploy to Staging"),

        el.repeat([
            el.action("Run Smoke Tests"),
        ],
            condition="Tests pass?",
            is_label="retry",
            not_label="pass",
            backward_action="wait 30s",
        ),

        el.action("Deploy to Production"),
        el.note("Blue/green deployment", "right"),
    ], "no", [
        el.swimlane("Developer"),
        el.action("Fix Issues"),
        el.action("Notify Team", stereotype="sendSignal"),
    ], then_label="yes"),

    el.stop(),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/TLBHRjf047o_hrWfB_14bOGs0KGJR5nPgYe4wGTSyM9Md6-jkpNKAldthXrG55NLoT9vRsPlPlQUejWWJUMCa3Y491ybAQoeHaSUpInAwt1kx5ReIDAcPCjWA_XZ0Awr_WTWORU7Cd3ZYuGT1xXPtcMtMTgVhT_AmME01wsywbUGhTWN_sDdMVQOt5-mDWG-NP3VLTS5Cxx_lFpot6DUpMnqqNfEyOYEQmndqxiparKJzo0CtqYcvdoJZRjrJdBOO3Xsk4dYs2EiiUP8mg6TcXs7WxQUh1iFFpq9l62KEBsMSY-eKGYnlvvq3B2b9T-1LAT0mWNsb6IFsmEyj3N-0rmqv0f8UNlGTFBAbif03QONG3iOF3i7AniZ5b-787lqC6Wn3jN8yY4RBn_FEh6h4UsNOksuxUnkn9Raoqv0m1gjz07syZSL7_3TqY-D_sH30PEJLQjtd-8x2KvxqfSnwC5Ggn2LGH460IMqG_0iCEZAmu-thm8NpROBgEkbA8H0vLuci70DZig0wgJeuHLwCUYYtk9v-662sZAZtv37sE1R-ZzOQDUgTbjDPxEeKMsezDRDvrrijDEXSssUTA_F-Yy0)



## Quick Reference

### Diagram Constructor

```text
activity_diagram(
    title=,            # str | None
    mainframe=,        # str | None
    caption=,          # str | None
    header=,           # str | Header | None
    footer=,           # str | Footer | None
    legend=,           # str | Legend | None
    scale=,            # float | Scale | None
    theme=,            # PlantUMLBuiltinTheme | ExternalTheme | None
    layout_engine=,    # "smetana" | None
    linetype=,         # "ortho" | "polyline" | None
    diagram_style=,    # ActivityDiagramStyleDict | ActivityDiagramStyle | None
    vertical_if=,      # bool (default False)
)
```

### Composer Methods

| Method | Description |
|--------|-------------|
| `d.add(...)` | Register flow elements (sequential order) |
| `d.render()` | Shortcut: build and render to PlantUML text |
| `render(d)` | Render to PlantUML text |

### Element Factories (`el = d.elements`)

**Simple Elements:**

| Method | Description |
|--------|-------------|
| `el.start()` | Start node (filled circle) |
| `el.stop()` | Stop node (filled circle with border) |
| `el.end()` | End node (circle with X) |
| `el.action(label, shape=, style=, stereotype=)` | Action step |
| `el.arrow(label=, pattern=, style=)` | Custom arrow |
| `el.note(content, position, floating=)` | Note annotation |
| `el.kill()` | Abrupt termination (X) |
| `el.detach()` | Detach from flow |
| `el.break_()` | Break out of enclosing loop |
| `el.connector(name, color=)` | Named connector circle |
| `el.goto(label)` | Goto statement (experimental) |
| `el.label(name)` | Label for goto (experimental) |

**Swimlanes and Partitions:**

| Method | Description |
|--------|-------------|
| `el.swimlane(name, color=, display_name=)` | Switch to swimlane |
| `el.partition(name, events, color=)` | Partition grouping |
| `el.package(name, events, color=)` | Package grouping |
| `el.rectangle(name, events, color=)` | Rectangle grouping |
| `el.card(name, events, color=)` | Card grouping |
| `el.group(name, events)` | Minimal grouping |

**Control Flow:**

| Method | Description |
|--------|-------------|
| `el.if_(condition, events, *branches, then_label=)` | If/elseif/else |
| `el.switch(condition, *cases)` | Switch/case |
| `el.while_(condition, events, is_label=, endwhile_label=, backward_action=)` | While loop |
| `el.repeat(events, condition=, is_label=, not_label=, backward_action=, start_label=)` | Do-while loop |

**Parallel:**

| Method | Description |
|--------|-------------|
| `el.fork(*branches, end_style=)` | Fork/join parallel (end_style: "fork", "merge", "or", "and") |
| `el.split(*branches)` | Split parallel (no sync bar) |

### Inline Style Dicts

**`style=` on actions (StyleDict, background only):**
```text
{"background": "#E3F2FD"}
{"background": Gradient(start="#4CAF50", end="#81C784", direction="horizontal")}
```

**`style=` on arrows (LineStyleDict):**
```text
{"color": "red", "pattern": "dashed", "thickness": 2, "bold": True}
```
