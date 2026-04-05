# State Diagrams

State diagrams show how a single entity changes over time. They are ideal for modeling:

- **Object lifecycles**: Order (pending -> paid -> shipped -> delivered)
- **Workflow stages**: Document (draft -> review -> approved -> published)
- **UI states**: Button (idle -> hover -> pressed -> disabled)
- **Protocol states**: Connection (disconnected -> connecting -> connected)

A state diagram tracks ONE thing through its possible conditions. If you need to show multiple entities interacting, use a sequence diagram instead.

## Quick Start

```python
from plantuml_compose import state_diagram, render

d = state_diagram(title="Traffic Light")
el = d.elements
t = d.transitions

red = el.state("Red")
green = el.state("Green")
yellow = el.state("Yellow")
d.add(red, green, yellow)

d.connect(
    t.transition(el.initial(), red),
    t.transition(red, green, label="timer"),
    t.transition(green, yellow, label="timer"),
    t.transition(yellow, red, label="timer"),
)

print(render(d))
```

The pattern is:
1. Create a composer with `state_diagram()`
2. Get namespace shortcuts: `el = d.elements`, `t = d.transitions`
3. Create elements with `el.state()`, `el.choice()`, etc.
4. Register them with `d.add()`
5. Connect them with `d.connect(t.transition(...))`
6. Render with `render(d)`

## Elements

### States

```python
from plantuml_compose import state_diagram, render

d = state_diagram()
el = d.elements
t = d.transitions

# Simple state
idle = el.state("Idle")

# State with description (shown inside the state box)
processing = el.state("Processing", description="Handling request")

# State with a ref alias (useful for long names in transitions)
waiting = el.state("Waiting for User Input", ref="waiting")

# State with inline style
error = el.state("Error", style={"background": "#FFCDD2", "line": {"color": "red"}})

# State with a note
done = el.state("Done", note="Terminal state", note_position="left")

d.add(idle, processing, waiting, error, done)

d.connect(
    t.transition(el.initial(), idle),
    t.transition(idle, processing),
    t.transition(processing, waiting),
    t.transition(waiting, error),
    t.transition(error, done),
)

print(render(d))
```

**Parameters for `el.state()`:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | State name (displayed label) |
| `*children` | `EntityRef` | Nested states (makes it a composite state) |
| `ref=` | `str \| None` | Alias for use in transitions |
| `description=` | `str \| Label \| None` | Text shown inside the state |
| `style=` | `StyleDict \| None` | Visual style (background, line, text_color) |
| `note=` | `str \| Note \| None` | Note text attached to the state |
| `note_position=` | `NotePosition` | `"left"`, `"right"` (default), `"top"`, `"bottom"` |

### Initial and Final Pseudo-States

```python
from plantuml_compose import state_diagram, render

d = state_diagram()
el = d.elements
t = d.transitions

active = el.state("Active")
d.add(active)

d.connect(
    # el.initial() returns "[*]" — the filled circle start marker
    t.transition(el.initial(), active, label="boot"),
    # el.final() also returns "[*]" — PlantUML uses context to render as end
    t.transition(active, el.final(), label="shutdown"),
)

print(render(d))
```

### Choice (Decision Points)

Rendered as a diamond shape for conditional branching:

```python
from plantuml_compose import state_diagram, render

d = state_diagram()
el = d.elements
t = d.transitions

processing = el.state("Processing")
success = el.state("Success")
failure = el.state("Failure")
check = el.choice("valid?")

d.add(processing, success, failure, check)

d.connect(
    t.transition(el.initial(), processing),
    t.transition(processing, check),
    t.transition(check, success, label="yes"),
    t.transition(check, failure, label="no"),
)

print(render(d))
```

### Fork and Join (Parallel Execution)

Fork splits into concurrent paths; join waits for all to complete:

```python
from plantuml_compose import state_diagram, render

d = state_diagram()
el = d.elements
t = d.transitions

received = el.state("Received")
ready = el.state("Ready")
pack = el.state("Packing")
label_task = el.state("Labeling")

split = el.fork("split")
sync = el.join("sync")

d.add(received, ready, pack, label_task, split, sync)

d.connect(
    t.transition(el.initial(), received),
    t.transition(received, split),
    t.transition(split, pack),
    t.transition(split, label_task),
    t.transition(pack, sync),
    t.transition(label_task, sync),
    t.transition(sync, ready),
    t.transition(ready, el.final()),
)

print(render(d))
```

### History and Deep History

Return to the previously active sub-state within a composite:

```python
from plantuml_compose import state_diagram, render

d = state_diagram()
el = d.elements
t = d.transitions

off = el.state("Off")
playing = el.state("Playing")
paused = el.state("Paused")
on = el.state("On", playing, paused)

# Shallow history: remembers the last active direct child
h = el.history()

# Deep history: remembers the full nested state path
dh = el.deep_history()

d.add(off, on, h, dh)

d.connect(
    t.transition(el.initial(), off),
    t.transition(off, on, label="power on"),
    t.transition(on, off, label="power off"),
    t.transition(el.initial(), playing),
    t.transition(playing, paused, label="pause"),
    t.transition(paused, playing, label="play"),
    # Resume returns to the last state within "On"
    t.transition(off, h, label="resume"),
)

print(render(d))
```

### Entry and Exit Points

Named boundary points on composite states:

```python
from plantuml_compose import state_diagram, render

d = state_diagram()
el = d.elements
t = d.transitions

waiting = el.state("Waiting")
done = el.state("Done")
validate = el.state("Validate")
transform = el.state("Transform")

# Named entry/exit points
enter = el.entry_point("enter")
leave = el.exit_point("leave")

proc = el.state("Processing", validate, transform, enter, leave)
d.add(waiting, done, proc)

d.connect(
    t.transition(el.initial(), waiting),
    t.transition(waiting, enter, label="start"),
    t.transition(enter, validate),
    t.transition(validate, transform),
    t.transition(transform, leave),
    t.transition(leave, done),
    t.transition(done, el.final()),
)

print(render(d))
```

### Composite States (Nesting)

Pass child states as positional arguments to create nested state machines:

```python
from plantuml_compose import state_diagram, render

d = state_diagram()
el = d.elements
t = d.transitions

disconnected = el.state("Disconnected")
idle = el.state("Idle")
active = el.state("Active")
connected = el.state("Connected", idle, active)

d.add(disconnected, connected)

d.connect(
    t.transition(el.initial(), disconnected),
    t.transition(disconnected, connected, label="connect"),
    t.transition(connected, disconnected, label="disconnect"),
    t.transition(el.initial(), idle),
    t.transition(idle, active, label="request"),
    t.transition(active, idle, label="complete"),
)

print(render(d))
```

### Concurrent States (Parallel Regions)

Show multiple independent sub-machines running simultaneously. Each region is defined with `el.region()`:

```python
from plantuml_compose import state_diagram, render

d = state_diagram()
el = d.elements
t = d.transitions

unlocked = el.state("Unlocked")

num_off = el.state("NumLock Off")
num_on = el.state("NumLock On")
caps_off = el.state("CapsLock Off")
caps_on = el.state("CapsLock On")

# separator="horizontal" (default): regions stacked with -- separator
# separator="vertical": regions side-by-side with || separator
locked = el.concurrent("Locked",
    el.region(num_off, num_on),
    el.region(caps_off, caps_on),
    separator="horizontal",
)

d.add(unlocked, locked)

d.connect(
    t.transition(el.initial(), unlocked),
    t.transition(unlocked, locked, label="lock"),
    t.transition(locked, unlocked, label="unlock"),
    t.transition(el.initial(), num_off),
    t.transition(num_off, num_on, label="press"),
    t.transition(num_on, num_off, label="press"),
    t.transition(el.initial(), caps_off),
    t.transition(caps_off, caps_on, label="press"),
    t.transition(caps_on, caps_off, label="press"),
)

print(render(d))
```

### All Pseudo-State Factories

| Method | Description |
|--------|-------------|
| `el.initial()` | Start marker `[*]` (returns string) |
| `el.final()` | End marker `[*]` (returns string) |
| `el.choice(name)` | Decision diamond |
| `el.fork(name)` | Fork bar (split into parallel) |
| `el.join(name)` | Join bar (merge parallel) |
| `el.history()` | Shallow history `[H]` |
| `el.deep_history()` | Deep history `[H*]` |
| `el.entry_point(name)` | Named entry point on composite boundary |
| `el.exit_point(name)` | Named exit point on composite boundary |

All pseudo-states that return `EntityRef` accept `ref=` and `style=` (except `history` and `deep_history` which only accept `ref=`).

## Transitions

### Basic Transitions

```python
from plantuml_compose import state_diagram, render

d = state_diagram()
el = d.elements
t = d.transitions

idle = el.state("Idle")
active = el.state("Active")
d.add(idle, active)

d.connect(
    t.transition(idle, active),
    t.transition(active, idle, label="timeout"),
)

print(render(d))
```

### Trigger, Guard, and Effect

PlantUML renders UML-standard transition labels as `trigger [guard] / effect`:

```python
from plantuml_compose import state_diagram, render

d = state_diagram()
el = d.elements
t = d.transitions

idle = el.state("Idle")
processing = el.state("Processing")
error = el.state("Error")
done = el.state("Done")
d.add(idle, processing, error, done)

d.connect(
    t.transition(el.initial(), idle),

    # trigger: the event that causes the transition
    # guard: condition in brackets that must be true
    # effect: action performed during the transition
    t.transition(idle, processing,
        label="submit",
        guard="valid input",
        effect="startProcessing()",
    ),

    t.transition(processing, done,
        label="complete",
        effect="sendNotification()",
    ),

    t.transition(processing, error,
        trigger="failure",
        guard="timeout",
        effect="logError()",
    ),
)

print(render(d))
```

### Transition Notes

Attach a note directly to a transition:

```python
from plantuml_compose import state_diagram, render

d = state_diagram()
el = d.elements
t = d.transitions

a = el.state("A")
b = el.state("B")
d.add(a, b)

d.connect(
    t.transition(a, b, label="go", note="This transition is critical"),
)

print(render(d))
```

### Transition Styling

```python
from plantuml_compose import state_diagram, render

d = state_diagram()
el = d.elements
t = d.transitions

a = el.state("A")
b = el.state("B")
c = el.state("C")
d.add(a, b, c)

d.connect(
    # Dotted line style
    t.transition(a, b, style={"pattern": "dotted"}),

    # Colored line
    t.transition(b, c, style={"color": "blue", "bold": True}),

    # String shorthand: just a color name
    t.transition(c, a, style="#red"),
)

print(render(d))
```

**`style=` accepts:** `LineStyleDict` (`{"pattern": ..., "color": ..., "thickness": ..., "bold": ...}`), `LineStyle` object, or a string shorthand (`"dashed"`, `"dotted"`, `"bold"`, `"#color"`).

### Direction and Length

```python
from plantuml_compose import state_diagram, render

d = state_diagram()
el = d.elements
t = d.transitions

center = el.state("Center")
up = el.state("Up")
down = el.state("Down")
left = el.state("Left")
right = el.state("Right")
d.add(center, up, down, left, right)

d.connect(
    # Force layout direction: "up", "down", "left", "right"
    t.transition(center, up, direction="up"),
    t.transition(center, down, direction="down"),
    t.transition(center, left, direction="left"),
    t.transition(center, right, direction="right"),

    # length= controls arrow length (number of dashes in PlantUML)
    # Higher values push states further apart
    t.transition(up, right, length=3),
)

print(render(d))
```

### Bulk Transitions: `t.transitions()`

Create multiple transitions from `(source, target)` or `(source, target, label)` tuples:

```python
from plantuml_compose import state_diagram, render

d = state_diagram()
el = d.elements
t = d.transitions

a = el.state("A")
b = el.state("B")
c = el.state("C")
final = el.state("D")
d.add(a, b, c, final)

d.connect(t.transitions(
    (el.initial(), a, "start"),
    (a, b, "step 1"),
    (b, c, "step 2"),
    (c, final),
    (final, el.final()),
))

print(render(d))
```

### Fan-Out: `t.transitions_from()`

One source to many targets. Targets can be bare or `(target, label)` tuples, mixed freely:

```python
from plantuml_compose import state_diagram, render

d = state_diagram()
el = d.elements
t = d.transitions

active = el.state("Active")
expired = el.state("Expired")
revoked = el.state("Revoked")
renewed = el.state("Renewed")
d.add(active, expired, revoked, renewed)

d.connect(
    t.transition(el.initial(), active),
    # Fan-out: active -> three targets with labels
    t.transitions_from(active,
        (expired, "TTL exceeded"),
        (revoked, "Key compromise"),
        (renewed, "Renewal window"),
        style={"color": "gray"},
        direction="down",
    ),
)

print(render(d))
```

`transitions_from()` accepts `style=`, `direction=`, and `length=` which apply to all generated transitions.

### Transition Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `source` | `EntityRef \| str` | Source state or `"[*]"` |
| `target` | `EntityRef \| str` | Target state or `"[*]"` |
| `label=` | `str \| None` | Transition label text |
| `trigger=` | `str \| None` | Event that triggers the transition |
| `guard=` | `str \| None` | Condition in brackets |
| `effect=` | `str \| None` | Action after slash |
| `style=` | `LineStyleLike \| None` | Line style (color, pattern, etc.) |
| `direction=` | `Direction \| None` | `"up"`, `"down"`, `"left"`, `"right"` |
| `note=` | `str \| None` | Note attached to the transition |
| `length=` | `int \| None` | Arrow length (pushes states apart) |

## Notes

### Notes on States

Attach notes directly when creating a state:

```python
from plantuml_compose import state_diagram, render

d = state_diagram()
el = d.elements
t = d.transitions

idle = el.state("Idle", note="Default state after boot", note_position="right")
active = el.state("Active", note="System is processing", note_position="left")
d.add(idle, active)

d.connect(
    t.transition(el.initial(), idle),
    t.transition(idle, active),
)

print(render(d))
```

### Floating Notes

Use `d.note()` for notes not attached to any specific element:

```python
from plantuml_compose import state_diagram, render

d = state_diagram()
el = d.elements
t = d.transitions

idle = el.state("Idle")
d.add(idle)

d.note("System overview:\nThis diagram shows the\nmain lifecycle states", position="left")

d.connect(
    t.transition(el.initial(), idle),
    t.transition(idle, el.final()),
)

print(render(d))
```

## Layout and Organization

### Layout Direction

By default, state diagrams flow top-to-bottom. Use `layout=` to change:

```python
from plantuml_compose import state_diagram, render

# Left-to-right layout
d = state_diagram(layout="left_to_right")
el = d.elements
t = d.transitions

a = el.state("A")
b = el.state("B")
c = el.state("C")
d.add(a, b, c)

d.connect(
    t.transition(el.initial(), a),
    t.transition(a, b),
    t.transition(b, c),
    t.transition(c, el.final()),
)

print(render(d))
```

`layout=` accepts `"top_to_bottom"` (default) or `"left_to_right"`.

### Hide Empty Descriptions

Remove the dashed line in states that have no description:

```python
from plantuml_compose import state_diagram, render

d = state_diagram(hide_empty_description=True)
el = d.elements
t = d.transitions

a = el.state("A")
b = el.state("B")
d.add(a, b)

d.connect(
    t.transition(el.initial(), a),
    t.transition(a, b),
    t.transition(b, el.final()),
)

print(render(d))
```

## Styling

### Inline State Styling

```python
from plantuml_compose import state_diagram, render

d = state_diagram()
el = d.elements
t = d.transitions

# StyleDict: background, line, text_color, stereotype
normal = el.state("Normal", style={"background": "#E3F2FD"})

# Nested line style for border control
warning = el.state("Warning", style={
    "background": "yellow",
    "line": {"color": "orange", "pattern": "dashed"},
})

# Full style with text color
error = el.state("Error", style={
    "background": "#FFCDD2",
    "text_color": "red",
    "line": {"color": "red", "bold": True},
})

d.add(normal, warning, error)

d.connect(
    t.transition(el.initial(), normal),
    t.transition(normal, warning),
    t.transition(warning, error),
)

print(render(d))
```

### Diagram-Wide Styling (`diagram_style=`)

Apply consistent styles across all elements using a `<style>` block:

```python
from plantuml_compose import state_diagram, render

d = state_diagram(
    title="Styled State Machine",
    diagram_style={
        # Root-level: diagram background and default fonts
        "background": "white",
        "font_name": "Arial",
        "font_size": 12,
        "font_color": "#333333",

        # State boxes
        "state": {
            "background": "#E3F2FD",
            "line_color": "#1976D2",
            "round_corner": 10,
            "padding": 8,
            "font_size": 11,
        },

        # Transition arrows
        "arrow": {
            "line_color": "#757575",
            "font_size": 10,
            "line_thickness": 1,
        },

        # Notes
        "note": {
            "background": "#FFF9C4",
            "line_color": "#F9A825",
        },

        # Title
        "title": {
            "font_size": 16,
            "font_style": "bold",
        },

        # Stereotype-based styles
        "stereotypes": {
            "error": {
                "background": "#FFCDD2",
                "line_color": "#D32F2F",
                "font_style": "bold",
            },
            "success": {
                "background": "#C8E6C9",
                "line_color": "#388E3C",
            },
        },
    },
)
el = d.elements
t = d.transitions

idle = el.state("Idle")
active = el.state("Active")
d.add(idle, active)

d.connect(
    t.transition(el.initial(), idle),
    t.transition(idle, active, label="go"),
    t.transition(active, el.final()),
)

print(render(d))
```

**`diagram_style=` selectors:**

| Selector | Target | Style Type |
|----------|--------|------------|
| `background` | Diagram background | `ColorLike \| Gradient` |
| `font_name` | Default font | `str` |
| `font_size` | Default font size | `int` |
| `font_color` | Default text color | `ColorLike` |
| `state` | State boxes | `ElementStyleDict` |
| `arrow` | Transition arrows | `DiagramArrowStyleDict` |
| `note` | Notes | `ElementStyleDict` |
| `title` | Diagram title | `ElementStyleDict` |
| `stereotypes` | By stereotype name | `dict[str, ElementStyleDict]` |

**`ElementStyleDict` keys:** `background`, `line_color`, `font_color`, `font_name`, `font_size`, `font_style`, `round_corner`, `line_thickness`, `line_style`, `padding`, `margin`, `horizontal_alignment`, `max_width`, `shadowing`, `diagonal_corner`, `word_wrap`, `hyperlink_color`

**`DiagramArrowStyleDict` keys:** `line_color`, `line_thickness`, `line_pattern`, `font_color`, `font_name`, `font_size`

## Advanced Features

### Theme Support

Use a built-in PlantUML theme or an external theme file:

```python
from plantuml_compose import state_diagram, render

# Built-in theme
d = state_diagram(title="Themed Diagram", theme="cerulean-outline")
el = d.elements
t = d.transitions

a = el.state("A")
b = el.state("B")
d.add(a, b)

d.connect(
    t.transition(el.initial(), a),
    t.transition(a, b),
    t.transition(b, el.final()),
)

print(render(d))
```

```python
from plantuml_compose import state_diagram, render

# Another built-in theme
d = state_diagram(
    title="Blueprint Theme",
    theme="blueprint",
)
el = d.elements
t = d.transitions

a = el.state("A")
d.add(a)
d.connect(t.transition(el.initial(), a), t.transition(a, el.final()))

print(render(d))
```

Built-in themes include: `_none_`, `amiga`, `aws-orange`, `black-knight`, `bluegray`, `blueprint`, `carbon-gray`, `cerulean`, `cerulean-outline`, `hacker`, `mars`, `materia`, `mono`, `plain`, and many more.

### Diagram Metadata

```python
from plantuml_compose import state_diagram, render
from plantuml_compose.primitives.common import Scale

d = state_diagram(
    title="Order State Machine",
    mainframe="Order Module",
    caption="Figure 1: Order lifecycle",
    header="ACME Corp",
    footer="Page 1",
    scale=Scale(factor=1.5),
    legend="Color coding:\nBlue = normal\nRed = error",
)
el = d.elements
t = d.transitions

pending = el.state("Pending")
complete = el.state("Complete")
d.add(pending, complete)

d.connect(
    t.transition(el.initial(), pending),
    t.transition(pending, complete),
    t.transition(complete, el.final()),
)

print(render(d))
```

## Quick Reference

### Diagram Constructor

```text
state_diagram(
    title=,            # str | None
    mainframe=,        # str | None
    caption=,          # str | None
    header=,           # str | Header | None
    footer=,           # str | Footer | None
    legend=,           # str | Legend | None
    scale=,            # float | Scale | None
    theme=,            # PlantUMLBuiltinTheme | ExternalTheme | None
    layout=,           # "top_to_bottom" | "left_to_right" | None
    hide_empty_description=,  # bool (default False)
    diagram_style=,    # StateDiagramStyleDict | StateDiagramStyle | None
)
```

### Composer Methods

| Method | Description |
|--------|-------------|
| `d.add(...)` | Register elements |
| `d.connect(...)` | Register transitions (accepts single, list, or mixed) |
| `d.note(text, position=)` | Floating note |
| `render(d)` | Render to PlantUML text |

### Element Factories (`el = d.elements`)

| Method | Returns | Description |
|--------|---------|-------------|
| `el.state(name, *children, ref=, description=, style=, note=, note_position=)` | `EntityRef` | State (or composite if children given) |
| `el.initial()` | `str` | Initial pseudo-state `[*]` |
| `el.final()` | `str` | Final pseudo-state `[*]` |
| `el.choice(name, ref=, style=)` | `EntityRef` | Decision diamond |
| `el.fork(name, ref=, style=)` | `EntityRef` | Fork bar |
| `el.join(name, ref=, style=)` | `EntityRef` | Join bar |
| `el.history(ref=)` | `EntityRef` | Shallow history `[H]` |
| `el.deep_history(ref=)` | `EntityRef` | Deep history `[H*]` |
| `el.entry_point(name, ref=, style=)` | `EntityRef` | Named entry point |
| `el.exit_point(name, ref=, style=)` | `EntityRef` | Named exit point |
| `el.concurrent(name, *regions, ref=, style=, separator=)` | `EntityRef` | Concurrent state |
| `el.region(*elements)` | `_RegionData` | Region within a concurrent state |

### Transition Factories (`t = d.transitions`)

| Method | Returns | Description |
|--------|---------|-------------|
| `t.transition(source, target, label=, trigger=, guard=, effect=, style=, direction=, note=, length=)` | `_TransitionData` | Single transition |
| `t.transitions((src, tgt), (src, tgt, label), ...)` | `list` | Bulk from tuples |
| `t.transitions_from(source, tgt, (tgt, label), ..., style=, direction=, length=)` | `list` | Fan-out from one source |

### Inline Style Dicts

**`style=` on states (StyleDict):**
```python
{"background": "#E3F2FD", "text_color": "navy", "line": {"color": "blue", "pattern": "dashed"}}
```

**`style=` on transitions (LineStyleDict):**
```python
{"color": "red", "pattern": "dotted", "thickness": 2, "bold": True}
```
