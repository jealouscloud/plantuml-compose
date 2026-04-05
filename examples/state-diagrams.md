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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGWfIanBoqnMyCbCpoZX0agMf2e4fQP0MUv5gQbvK7PaQavEVZbNj5QiWgwk7LWH48FPO6KALWebcRcfHLmG7aWSeWKk0UL2TSE57LBpKe0E0W00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/RP0n2y8m48Nt_8gZRa8NnmfIi9PsSr0Sn26OgnJIYrwk-FTDqeYBI_BklSVb8xKNpJ9FLWKX2BsncEMHtHsz7-cXVX8gw3GP6oNZQqOlkLvSz2ZH7Xp3sID3JyzP2j0UtakKcmVcK5crxRvfDjkm2Yj6ayF64IfoGLaS1DoGd0fEoDD8saAggUlw1cMvMtZZaQR_o37v4kGxUOb3BJHnJa_NI2PynmS0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8oIb8L79DBCijIkQArOXLqTUsWN0KhXQJy_18kA0ya0L9WfL2SKLgIab-Un-MGcfS2D0G0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8oIb8L0ehoarEBYpFpqg42mQN9804epoqnCwUqA1NAKofBpCbCiLTII2nM03CLR6oIC_8parFjxBYYjM8LT7Nja4r4CC4oO2rS48qWFjGg1Ik5ojHY976efK3nl7mkXzIy5A1p0G00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8oIb8LWbAJKpFBKbFWtCIKIYWx834vEpCl7ShpIKnApK5mbOeBSZ9Bb1GIYnN0B0KRcxJyecmxExXyPLuoH1h80CfcvMVc0MMZjM8LT7Nj4FR2661Hi55S40D1VBWJu29mPq2b8Dg0Ld31P10YO9iXbe5y1IR1VA0Zk1nIyrA0mG00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8oIb8L_DFIOAmyXMek1GK89o0diJ8pBnt1JomjJatXgkMArefLqDMr0-i3OWWxJy5AeI2_FBL88J-F2yY3Aa280XN3DC9CXj8GCR3f8EKW1XUKYwGQ90LamMsCzeW52XMb5fVcfd8vfEQb03q40000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/HP312i8m38RlUOgmex0Na55sy05s43s8X-AY5BeMsYYA-EwsQTTTcl__-jCa7IFhmC_5GX9CUDQ6ZNjKT_2Egfo2lr6CwGw_W5ZWILip9z70CMWNxpuiZNJac4A7Eg8e78PKmsVonh5IMywIVf7aHENSs_0Q-y5bTyM-Lst2MeMLb_Seoq1ncRVvLY5q6x8fuT8NIlViPVjyY4lzOIGtfx_w0m00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8oIb8LN3ABa_FpybAJIr9Je4BECBv2DPU20aJCCoKd5SvnJ2x9B4lbgkMArefLqDMrGpK4cGEMHPXdfG2LuN96KO6YnKeX1Sw5sm2s7qI0UH0705KMfHQMfXQNS445O2h15kKMvAIMf78vfEQb0BqB0000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/RP6z2iCm38HtFON8MCWBP2Y1hA6TEfLIJECiJTGGsrFekrTn_4-tkzEdmyAjqcBLPfw0XPPue-dpUil1sTuQt03n2AgBcVSGh-DOeL3e_9Fz7uXoXXYfwyXrOb5Pcm_okeXHGH5yuNvwSEavFjqBcxeB6jmpwECWK0qQAqDHUbAYyndnth9AfI29Yks0-ERilDGKqrYUPcL3W5f90t_X3m00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8oIb8LF5DoKg5Cn-IIpB9KBf28Wgwk7OmFeS0YO2ahXPBCtDJyqX8kXzIy5A190000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/PO-n3i8m34JtV8L7GAhO6L0765WGUzKXj6vbAOchnE7xST9AHMA9BhRVdTqciL6oTqQ583n6XvjyHHum9GhpLhZ7o77JDmvekbCFJNDTeVBKtyx11L9-UnBeFjRH21IMB3sSeQRkWuUZ-Q6AIV5NV62_EDGyHJ2CJnQQQB127FwPkfz2aoMN8q8dv97NGCTpRIlLgf4U_0K0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8oIb8L7A6q4vUZWgwkdOAJWfL2UZvNNZvGB3zF8ISpBzjA8IGZirYXf2WnhpYp91Ce2kGb5m6PoOavN0wfUIb0um00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8oIb8L7A6q4vHsvd9Kq8rEoIyfIKs9rRK3YZi1-Sf9EQMfEadvEM0nPovda5WHH8KZbqDgNWhGH000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8oIb8Ld5FpIbABe9pG0YZ39Ryy3yhqIKqhWJA3CjCpIhWWEXHqItNjG1fWt1GW5wmD9f03501hXWaK0GKWHeGMAEZgmdaEgNafG0S10000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8oIb8L7A6q4vHsXj8kND5QiGgwkdOAZWfM2c1DN8vWlXEOdrgWOCZb11PmXWaOSJc31LouNC0qq0GkXzIy5A1j0000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8oIb8L79DBCijIeHpNYeBCejGKA2yejIm_6ucNbreEv4LhnIhewjh1D48e1TrevVIYnChO5A0Cr1G5AuMG41-5r8harDGKe4OiAg4s05LwfrOg9EVd5XJbvsOMfs9N2xOVg1RCIinHAC_CIyalvt98pKi1-WS0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/BOwn2iCm34HtVuNcG7uWGqYXI-UE9OEJoAd1iOfr2VJlwzfUnEdGkzEai0dd4KmMO7fiWKsKh9BVto1nnHhepiwU0LJFh0CdMaJGkDiAVpKoi2jWzGPwVXLya5Vw95bPrSVTlBgP-dwiXVzHjXOpSTpoJpy0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/9Kwx2iD03Dlz5PeB-O4E9MldP2iTZfpJCzm3pcv2_hvEkWX95f97jT3jMp8vCSOpPgRNxOrXUFp52PTobshpJERL29WEDIve6_TDUB-xDITHH0cV7WeqjLrXYVrGWbHaMNav5g-xjfIuHfoDD3hp7tu0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuSf9JIjHACbNACfCpoXHICaiIaqkoSpFum8gA4bLS8JIJb3QcIjQArP1LzSEAEC8ffsudC2qCvSpc0RASpcavgK0pGO0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuSh8J4bLICqjAAbKI4ajJYxAB2Z9pC_Z0igNf2euGcadhcYjM0LTNJkWY2EOTk9o0jD0SIw7rBmKe540)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8oIb8L_FABSXDp59HTZTsCt5oWWk69HNcPUUaAofMfEJdvvTOvcNcfUYc9nHcfAM2sLNvHObvwAbIrQr5HVf62ifkRiukB4KI-2AYm9BMY1CJWYjQALT3LjODQnGMr4IG2jOSBPXz836mQbqDgNWhGaG00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/TP9HIyCm4CVVyoaEzYPCrzPjhOonsIuWg8Zw9Zx497HXQG9fwb3PTpTDKpScRMcQ-r_kTvVaLhKbnZQLH8lQVac-H4wml12aDAI27mHmI-YkDBfHBDTI6zXlXULEnrhPHr9nM1j1P11Un3U7A0vM5p1A_ECqp_RG_zZH9i4nBhplNYWUr2YRpuhOgqT-vEtdBjWeRY2QUEc9C2PK2Qcp3kvJUZWVnZZBhy_puMoTnjCGJepH-n1_icO-RTy_zNKhw4xnkeRehCv9u5no1pB3XUH5sE99aYA9tNaSWUtjm8UMh6VM3QLjqW5gdcvcUNPEJT9qa-GUSK1CqwRYodg45LRsPtNSmMoeW0DQN8MEwIAzdxbVUyKFX6vTqgwPu8x9VhgcLdnoz7Rn3kFnilEqWxSw9zn0gL6Ojx9RZ5PSCTUblm00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuL8ioKZDJLL8JYqgpKbDpDFDBot9oSnBvIh9BCb9LGW1IQOek6GcfXSbvd81TPMaAZX2QIUkQArO1LrTEw288vXsud82qq1nBeVKl1IW1G00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuL8ioKZDJLL8oYbDBIZAp2lXAiaioKbLS8Bn5K90ybn0zIMf2evSqLgn2hgwTa2M8vW6yhaSKlDIW4O10000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/FL2nQiD03Dtr5PeBANJe4cX9QvhDDBHZwI3kPET0TpAoFFJlgnWxa_JUqtiIEirEvaiLg5JQO5GPFospOQzv4OOvaJ0-FJw35vTT_7PonfxIjJI6nCs3l3BTjBUk_y1ERThvGVLMBZH642IQl6Z3SnaN2-AuHKePEFsbM2aySik04I9gc3INDXu3lyl2-89DhP84_k8SaCtK81oRRrvlkqGRjWrrMYTXP_Xv-CN3uVKkRtNbxaDxixBXW5DCnO_-0G00)



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
