# State Diagrams

State diagrams show how a single entity changes over time. They're ideal for modeling:

- **Object lifecycles**: Order (pending → paid → shipped → delivered)
- **Workflow stages**: Document (draft → review → approved → published)
- **UI states**: Button (idle → hover → pressed → disabled)
- **Protocol states**: Connection (disconnected → connecting → connected)

A state diagram tracks ONE thing through its possible conditions. If you need to show multiple entities interacting, use a sequence diagram instead.

## Core Concepts

**State**: A condition during an entity's life. "Logged In", "Processing", "Awaiting Payment".

**Transition**: Movement from one state to another, triggered by an event.

**Guard**: A condition that must be true for the transition to occur. Written in brackets: `[if authorized]`.

**Effect**: An action performed during the transition. Written with a slash: `/ sendNotification()`.

## Your First State Diagram

```python
from plantuml_compose import state_diagram, render

d = state_diagram(title="Traffic Light")
el = d.elements
t = d.transitions

red = el.state("Red")
yellow = el.state("Yellow")
green = el.state("Green")
d.add(red, yellow, green)

d.connect(
    t.transition(el.initial(), red),
    t.transition(red, green, label="timer"),
    t.transition(green, yellow, label="timer"),
    t.transition(yellow, red, label="timer"),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGWfIanBoqnMyCbCpoZX0agMf2e4fQP0MP6fEJdvvL2EUr5gQXvNj5QiWgwk7LWH48FPO1a5AuMIpDpK8Yu83oGEqGwNW7AXkk723gbvAK070G00)



The `state_diagram()` function creates a composer. You then:
1. Create states with `el.state()`
2. Register them with `d.add()`
3. Connect them with `d.connect(t.transition(...))`
4. Use `el.initial()` and `el.final()` for entry/exit points

## Creating States

### Basic States

```python
from plantuml_compose import state_diagram, render

d = state_diagram()
el = d.elements
t = d.transitions

# Simple state
idle = el.state("Idle")

# State with description
processing = el.state("Processing", description="Handling request")

# State with an alias (useful for long names)
waiting = el.state("Waiting for User Input", ref="waiting")

d.add(idle, processing, waiting)

d.connect(
    t.transition(el.initial(), idle),
    t.transition(idle, processing),
    t.transition(processing, waiting),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8oIb8LF5DoKg7CWAByvDJYuioyT2u4Ky5AmICnBoK7n2nABInDBIw1AbSAJymi0GcdvHSfX1Qd5YbuvXMKbYWf91Ohb4EakAArOXLqTUqWje08C0-xHI0Pc3w7rBmKe1i1)



### Bulk State Creation

When you have multiple simple states, create them all at once:

```python
from plantuml_compose import state_diagram, render

d = state_diagram()
el = d.elements
t = d.transitions

pending = el.state("Pending")
paid = el.state("Paid")
shipped = el.state("Shipped")
delivered = el.state("Delivered")
d.add(pending, paid, shipped, delivered)

d.connect(
    t.transition(el.initial(), pending),
    t.transition(pending, paid, label="payment received"),
    t.transition(paid, shipped, label="dispatched"),
    t.transition(shipped, delivered, label="arrived"),
    t.transition(delivered, el.final()),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8oIb8L0bBpKZBpqc6ynCmKA3Cu8xEW81N6SqdDoInBBGBoexLY5NHrxU0QeJH43AXTmKgX8B4oDpMlHA4eDJaLg2k52omEKW0r5AWc9REu8B4aEGCe2nC4AO3R0rIIM5G4reqG0wa0si_b0BGJw0K0)



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
    # Simple transition
    t.transition(idle, active),
    # Transition with label
    t.transition(active, idle, label="timeout"),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8oIb8LF5DoKg5Cn-IIpB9KBf28Wgwk7OmFeS0YO2ahXPBCtDJyqX8kXzIy5A190000)



### Chaining Multiple States

Use `t.transitions()` to create multiple transitions in a compact form:

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

# Creates: A → B → C → D (3 transitions)
d.connect(t.transitions(
    (a, b),
    (b, c),
    (c, final),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8oIb8L7A6q4vHsXj8kN8uAkhfsG74dCEtCvGocNRWSKlDIWFe1)



### Guards and Effects

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

    # Guard: condition that must be true
    t.transition(idle, processing, label="submit", guard="valid input"),

    # Effect: action performed during transition
    t.transition(processing, done, label="complete", effect="sendNotification()"),

    # Both guard and effect
    t.transition(processing, error, guard="timeout", effect="logError()"),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/NO-n3i8m34JtVeL7GAhO6L0765WGUzMX9AQobCHLulJxSK8a48jrFjqxsKEIEKhshbCX23VhiCb7P8CfKLYQSOsHOzCN3jYDXmdw_lo1ogZRbuCJfFpq931kioCB5DOiK_UJA43fqgXXlphKxYCa3FREGYyoin27tVwVgRSeD0fvP2rLol5IRKqFMg1FlG40)



### Bulk Transitions

For more readable state sequences with labels:

```python
from plantuml_compose import state_diagram, render

d = state_diagram()
el = d.elements
t = d.transitions

idle = el.state("Idle")
running = el.state("Running")
paused = el.state("Paused")
stopped = el.state("Stopped")
d.add(idle, running, paused, stopped)

d.connect(
    t.transition(el.initial(), idle),
    t.transitions(
        (idle, running, "start"),
        (running, paused, "pause"),
        (paused, stopped, "stop"),
        (stopped, el.final()),
    ),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8oIb8LF5DoKg7CeDAylCoyT2Wl8B6qE3K5oWakoIye0FAYjM8LT7Nj8Bf019W7rQXWfG0sd0l61yb1Z05A5O0ON50kI0Pg9bXNVW4NZ0kI0bh3vP2Qbm9q9W00)



## Layout Direction

Control transition direction for better layouts:

```python
from plantuml_compose import state_diagram, render

d = state_diagram()
el = d.elements
t = d.transitions

a = el.state("A")
b = el.state("B")
c = el.state("C")
main = el.state("Main")
d.add(a, b, c, main)

d.connect(
    t.transition(el.initial(), main),

    # Force direction: up, down, left, right
    t.transition(main, a, direction="left"),
    t.transition(main, b, direction="right"),
    t.transition(main, c, direction="down"),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8oIb8L7A6q4vHsXjA-YPbvND5QiGgwkdOG3eXGqCq1SXsXx28WsmdAJW6odRaSKlDIW6O30000)



## Choice (Decision Points)

Use choice pseudo-states for conditional branching:

```python
from plantuml_compose import state_diagram, render

d = state_diagram(title="Order Processing")
el = d.elements
t = d.transitions

processing = el.state("Processing")
success = el.state("Success")
failure = el.state("Failure")

# Choice creates a diamond shape
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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LV0lIaajKWWeoazEBIxEp4ld0igNf68A19ScWmIWFBV4p9pIebGeJwaiCISpnLv98R5O0SnKiB59piZFJ4wri-EArefLqDMrGpOHmGJBWBLmGJI2-52h5AmKAbEBaSIXbWB5y_Av75BpKe2-0000)



## Fork and Join (Parallel Execution)

For concurrent activities that must all complete:

```python
from plantuml_compose import state_diagram, render

d = state_diagram(title="Order Fulfillment")
el = d.elements
t = d.transitions

received = el.state("Order Received")
ready = el.state("Ready to Ship")

# Parallel tasks
pack = el.state("Packing")
label_task = el.state("Labeling")
invoice = el.state("Invoice")

# Fork splits into parallel paths
split = el.fork("split")
# Join waits for all paths
sync = el.join("sync")

d.add(received, ready, pack, label_task, invoice, split, sync)

d.connect(
    t.transition(el.initial(), received),
    t.transition(received, split),

    # Three parallel branches
    t.transition(split, pack),
    t.transition(split, label_task),
    t.transition(split, invoice),

    # All converge at join
    t.transition(pack, sync),
    t.transition(label_task, sync),
    t.transition(invoice, sync),

    t.transition(sync, ready),
    t.transition(ready, el.final()),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/NP5D2eCm58JtEKLmMV068guAXKABNPOYQV9iKzD4z2bu-yRy6EmkC_CnJ99gH3RWz5K49IgWbq70G8-JQgLINz18B810Cn_Km47E83BAHiysqOfW3Kmi50szlMNlEESqQ9hL2TYLyKxgLr1dzWILv4dFHdA8ZMEl9BecTw95qPgXAyijNpJtiJtOz6EajkdzyA1vNlxFt4j7k5hYorUzZTkSD72puiW0-o8xW4GsEG5DXXkwgltJx9JBxHr81LhO3_e1)



### Fan-out Transitions

For one source going to many targets, use `transitions_from()`:

```python
from plantuml_compose import state_diagram, render

d = state_diagram(title="Payment Verification")
el = d.elements
t = d.transitions

start_state = el.state("Start")
complete = el.state("Complete")
fraud = el.state("Fraud Check")
balance = el.state("Balance Check")
credit = el.state("Credit Check")

split = el.fork("verification")
sync = el.join("sync")

d.add(start_state, complete, fraud, balance, credit, split, sync)

d.connect(
    t.transition(el.initial(), start_state),
    t.transition(start_state, split),

    # Fan-out from fork to three parallel checks
    t.transitions_from(split, fraud, balance, credit),

    # All converge
    t.transitions_from(sync, complete, style=None,
        direction=None),
    t.transition(fraud, sync),
    t.transition(balance, sync),
    t.transition(credit, sync),
    t.transition(complete, el.final()),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/bLB12i8m3BttAu97mJ-G8Gx4eo1u4HbbZLZjMkaomR-tZHksL0zUskJbzRsKPDMJz3HqHf0cWx2JpmujmG6zFkjMadPM10uXx2DpZ6lNtGqIZkdiaT2Ri_Et6SWU2XIMotXLbIXBYqK56oy7rTGNR6-JCaF046kcb2JcvvderMdxmsOjZRGjvaOZc5XzfMsTKR0PhEgP4zE6Kv7HsISfViA_EgqzAarv1syiwJCZfSaFgsypYuLoPX4DCujNcDbnVcB5zoBmMJh4raKfmf-PbcOA60sgOeLMXHry0G00)



## Composite States (Nested State Machines)

Group related states inside a parent state by passing children to `el.state()`:

```python
from plantuml_compose import state_diagram, render

d = state_diagram(title="Connection Lifecycle")
el = d.elements
t = d.transitions

disconnected = el.state("Disconnected")

# Composite state with nested elements
idle = el.state("Idle")
active = el.state("Active")
connected = el.state("Connected", idle, active)

d.add(disconnected, connected)

d.connect(
    t.transition(el.initial(), disconnected),
    t.transition(disconnected, connected, label="connect"),
    t.transition(connected, disconnected, label="disconnect"),
    # Transitions within the composite
    t.transition(el.initial(), idle),
    t.transition(idle, active, label="request"),
    t.transition(active, idle, label="complete"),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LP3D2i8m3CVlUOgSXRt03h9HBu9l81wapQ3GjRfcWeZlRjgkQa_jx_yHGeR8ruNNsG5RTeGgU4-QRV1uiXFfftO4ac72Wuswk6GsILN65o0MxMYaKM6KKO-4vzq5ksvVtVHaBW7iSQ7xIf75swIQ5a-7-UQ82TvGvpJB_4DsVtkbSlw3QX9DfKVpHHZ86xd71m00)



### Entry and Exit Points

Define specific entry/exit points on composite state boundaries:

```python
from plantuml_compose import state_diagram, render

d = state_diagram(title="Processing with Boundaries")
el = d.elements
t = d.transitions

waiting = el.state("Waiting")
done = el.state("Done")

validate = el.state("Validate")
transform = el.state("Transform")
proc = el.state("Processing", validate, transform)

d.add(waiting, done, proc)

d.connect(
    t.transition(el.initial(), waiting),
    t.transition(waiting, validate, label="start"),
    t.transition(validate, transform),
    t.transition(transform, done),
    t.transition(done, el.final()),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/NP312i8m38RlVOgmex0Na566-00xY1x4Gt5L0riAROQA-EwcSPl3I_FdpvUqJPtOHHxwpZ1ovw69uUnJGhh27Va6cp1GwoBwP8Ha3mU7BDKnsmRoernqlWp0rooG2d09aA2gF75yDW69hVqHOM1596RcWVoFx5s7hOZPs4L7wH9YBuvCBakxP2Qf_XATjLRaFlCsnzL9i-bROrHFHgz1zsFouxAb_ys7Pj9iQa-jhEy3)



## Concurrent States (Parallel Regions)

Show multiple independent state machines running simultaneously within a state:

```python
from plantuml_compose import state_diagram, render

d = state_diagram(title="Keyboard Lock")
el = d.elements
t = d.transitions

unlocked = el.state("Unlocked")

# Concurrent state with parallel regions
num_off = el.state("NumLock Off")
num_on = el.state("NumLock On")
caps_off = el.state("CapsLock Off")
caps_on = el.state("CapsLock On")

locked = el.concurrent("Locked",
    el.region(num_off, num_on),
    el.region(caps_off, caps_on),
)

d.add(unlocked, locked)

d.connect(
    t.transition(el.initial(), unlocked),
    t.transition(unlocked, locked, label="lock"),
    t.transition(locked, unlocked, label="unlock"),

    # NumLock region transitions
    t.transition(el.initial(), num_off),
    t.transition(num_off, num_on, label="press"),
    t.transition(num_on, num_off, label="press"),

    # CapsLock region transitions
    t.transition(el.initial(), caps_off),
    t.transition(caps_off, caps_on, label="press"),
    t.transition(caps_on, caps_off, label="press"),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/RP712i8m44Jl-OgXHo4_q8CKF5hqv4b4ear1RBUbIGyY_hjfJDjDyBOp-tOpP0jZrM37jX7sOHkDlNxTEZLKABlxKxYcrJXHuuIkWYozm5i0FoCxZEraubZN6PH1q5Ud_q0KC-IGy-O2ARV985Dnbv2Z7xGn7A9q0uEaN7FiL6-YjBCHnrqnIYWUE9dbCkdppDnDjopOHyoFBFy_5zuDPyWnUQ9S6mkLO_IbA3HLxiHV)



## History States

Return to the previous state within a composite:

```python
from plantuml_compose import state_diagram, render

d = state_diagram(title="Media Player")
el = d.elements
t = d.transitions

off = el.state("Off")

playing = el.state("Playing")
paused = el.state("Paused")
on = el.state("On", playing, paused)

h = el.history()

d.add(off, on, h)

d.connect(
    t.transition(el.initial(), off),
    t.transition(off, on, label="power on"),
    t.transition(on, off, label="power off"),

    # Inside composite
    t.transition(el.initial(), playing),
    t.transition(playing, paused, label="pause"),
    t.transition(paused, playing, label="play"),

    # History returns to last active state within "On"
    t.transition(off, h, label="resume"),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/JOyx2iCm38PtdK9p8HVeK39sAUqUCXYi58EZ55kcb9AxLweJua7m_Gy9ky_YafGvWWI9X3VomU4ZkWybq4m8xzEq4-CN4AkmJk3deLt9v5KEfn6xxj8KDghkluPdV1bOM8rcmq8bM64_PK_GgSoMBszAk32esWg7svI7wwX-ebncWfxOwqz_)



## Notes

Add explanatory notes to your diagram:

```python
from plantuml_compose import state_diagram, render

d = state_diagram()
el = d.elements
t = d.transitions

idle = el.state("Idle", note="Initial state after boot")
active = el.state("Active")
d.add(idle, active)

# Floating note
d.note("System monitors activity", position="left")

d.connect(
    t.transition(el.initial(), idle),
    t.transition(idle, active, label="activate"),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/BOwn3eCm34JtV8NdIln0XegEhErOTKZ15Al1LiC5YRzl82pMsRfxvtP1ICXpT4M0gHiYExMYadmca8t7oLEd0WcHgYsCu4HlCvovMmzPpsJa4PuUsmAUQROIjBHGs1s2pJqlBsgQQwtQnx5L0FdgAyZACgKe-lLqvr-Mn8MJCR52-W0nTIthKDx_0m00)



## Styling

### State Styling

```python
from plantuml_compose import state_diagram, render

d = state_diagram()
el = d.elements
t = d.transitions

# Using dict syntax
normal = el.state("Normal", style={"background": "#E3F2FD"})

# Using Style object with LineStyle for border
warning = el.state("Warning", style={"background": "yellow"})

# Dict with nested line style
error = el.state("Error", style={"background": "#FFCDD2", "line": {"color": "red"}})

d.add(normal, warning, error)

d.connect(
    t.transition(el.initial(), normal),
    t.transition(normal, warning),
    t.transition(warning, error),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8oIb8L_FABSXDp59HTZTsCt5oWWk69HNcPUUaAofMfEJdvvTOvcNcfLlb5YNdfgL0LhaL5-KKAocvkpYukHX3vejGKhcYjM0LTNJkegLnGmq4YK2EvO4Q3nC26S3cavgK0tGC0)



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
    t.transition(el.initial(), a),

    # Dotted line
    t.transition(a, b, style={"pattern": "dotted"}),

    # Colored line
    t.transition(b, c, style={"color": "blue"}),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8oIb8L7A6q4vHsvehMYbNGrRK3oZWgw4Qdv9UKfAR40lbEN4v0ld9IJcagYElCvP2Qbm8q2000)



### Diagram-Wide Styling

```python
from plantuml_compose import state_diagram, render

d = state_diagram(title="Styled Diagram")
el = d.elements
t = d.transitions

idle = el.state("Idle")
active = el.state("Active")
d.add(idle, active)

d.connect(
    t.transition(el.initial(), idle),
    t.transition(idle, active),
    t.transition(active, el.final()),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/PP3D2i8m48JlUOe5RqBHWqM5Kbfh2u9uyIWUGhFKO9f0khM8zDrDqnm42VdPRsPWIDOHjzItYYKTlHMcp072e-IDvIry6C21ry_6cbwBmYXZONX8GiShe-d2MuJSIguSy4aV-GyjobqLbtkldQN6G3T5NiLhHqUtkRLc2FaVppQUblUCB5c5cYH98LodGK2eEtU7ar0OddbDyeNijhn35AMpCXr-2k9yUU9yB4Cjt7zy0G00)



## Diagram Metadata

```python
from plantuml_compose import state_diagram, render

d = state_diagram(
    title="Order State Machine",
    caption="Figure 1: Order lifecycle",
    header="ACME Corp",
    footer="Page 1",
    scale=1.5,  # 150% size
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
![Diagram](https://www.plantuml.com/plantuml/svg/FO-n2iCm34HtVONdGWeTkdGeAQRTGW8TImVXA8d1iOsj3FtxAi79fDExqu7gp9XucHraWuxKvNm5jYogJJqbzMPaKWsQoNe2Gvu5JeIhzz3DK-cGuiw74DRHuIX5O32o3LwzxBWa0RTIwUn0vcSSGTxAE_AzzMFPT9YZ8oRudBwggkw7NUR6Zj0kDYeNK4jAlla3)



## SDL Receive States

For Specification and Description Language (SDL) diagrams:

```python
from plantuml_compose import state_diagram, render

d = state_diagram()
el = d.elements
t = d.transitions

idle = el.state("Idle")
waiting = el.state("Waiting for Message")
processing = el.state("Processing")
d.add(idle, waiting, processing)

d.connect(
    t.transition(el.initial(), idle),
    t.transition(idle, waiting),
    t.transition(waiting, processing, label="message received"),
    t.transition(processing, idle),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8oIb8LF5DoKg5CfV34p9BCl7I5jFmY1T_KukB4z5GbXSHY1QXuF50y7YgkO6DJd99Jb9gScbcMQcS7DI6WA3yPA0zKonMj5QkWgsi7CHz4W7bOJEB2PZf8BS8m1Ik5NAW4rCOKBYHPk3KEgNafG9y10000)



## Complete Example: Order Processing System

```python
from plantuml_compose import state_diagram, render

d = state_diagram(title="E-Commerce Order Lifecycle")
el = d.elements
t = d.transitions

# Main states
draft = el.state("Draft", description="Customer building cart")
submitted = el.state("Submitted")
cancelled = el.state("Cancelled")
complete = el.state("Complete")

# Validation choice
valid_check = el.choice("valid?")

# Processing composite with nested states
payment = el.state("Payment")
fulfillment = el.state("Fulfillment")
shipping = el.state("Shipping")
processing = el.state("Processing", payment, fulfillment, shipping)

d.add(draft, submitted, cancelled, complete, valid_check, processing)

d.connect(
    # Main flow
    t.transition(el.initial(), draft),
    t.transition(draft, submitted, label="checkout"),
    t.transition(submitted, valid_check),
    t.transition(valid_check, processing, label="valid"),
    t.transition(valid_check, cancelled, label="invalid"),
    t.transition(processing, complete, label="delivered"),
    t.transition(complete, el.final()),

    # Inside processing composite
    t.transition(el.initial(), payment),
    t.transition(payment, fulfillment, label="paid"),
    t.transition(fulfillment, shipping, label="packed"),

    # Cancellation from any processing state
    t.transition(processing, cancelled, label="cancel"),
    t.transition(cancelled, el.final()),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/PPBFQiCm3CRlVWhHuo0lK4fMoBRJe8CUnmwkhQoYSXmSkr36tdsAw_mPlGJfq--J9P7z47M8oR6A51dXjMgySnWCmY5O3F1EBPgROLH2HeINeDkeyXUsqAGXUi7Xb8WjTTzWf5r1Z-daA4Qq9MzqPv1voRth6UFKUNFLJFPv0tg07C9kPywU3DPrGJw2DpWCupi_2g28-kQmYtF-bhWbvd_QyKnzBpOHFf--eAhgbQr4MLsPPRrUanLWBOxGr2qJvY8B_QgfxVe-cPsE8B0vexdu5DKYZaXULjrNpfCjMsuVYlCHfKRTlReoPAJSLGYBJ5SCCk4iZeGC-s1QzJKvLeiqUVROMVbN_W00)



## Quick Reference

| Method | Description |
|--------|-------------|
| `el.state(name)` | Create a state |
| `el.state(name, *children)` | Create composite state |
| `el.initial()` | Initial pseudo-state `[*]` |
| `el.final()` | Final pseudo-state `[*]` |
| `el.choice(name)` | Decision diamond |
| `el.fork(name)` | Fork bar |
| `el.join(name)` | Join bar |
| `el.concurrent(name, *regions)` | Parallel regions |
| `el.region(*states)` | Region within concurrent state |
| `el.history()` | History pseudo-state |
| `el.deep_history()` | Deep history pseudo-state |
| `d.add(...)` | Register elements |
| `d.connect(...)` | Register transitions |
| `d.note(text)` | Floating note |
| `t.transition(a, b)` | Single transition |
| `t.transitions(...)` | Bulk transitions from tuples |
| `t.transitions_from(src, ...)` | Fan-out from one source |
| `render(d)` | Render to PlantUML text |
