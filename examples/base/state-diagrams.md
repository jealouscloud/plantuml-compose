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
from plantuml_compose import state_diagram

with state_diagram(title="Traffic Light") as d:
    red = d.state("Red")
    yellow = d.state("Yellow")
    green = d.state("Green")

    d.arrow(d.start(), red)
    d.arrow(red, green, label="timer")
    d.arrow(green, yellow, label="timer")
    d.arrow(yellow, red, label="timer")

print(d.render())
```

The `state_diagram()` context manager creates a builder. Inside, you:
1. Create states with `d.state()`
2. Connect them with `d.arrow()`
3. Use `d.start()` and `d.end()` for entry/exit points

## Creating States

### Basic States

```python
from plantuml_compose import state_diagram

with state_diagram() as d:
    # Simple state
    idle = d.state("Idle")

    # State with description
    processing = d.state("Processing", description="Handling request")

    # State with an alias (useful for long names)
    waiting = d.state("Waiting for User Input", alias="waiting")

    d.arrow(d.start(), idle)
    d.arrow(idle, processing)
    d.arrow(processing, waiting)

print(d.render())
```

### Bulk State Creation

When you have multiple simple states, create them all at once:

```python
from plantuml_compose import state_diagram

with state_diagram() as d:
    pending, paid, shipped, delivered = d.states(
        "Pending", "Paid", "Shipped", "Delivered"
    )

    d.arrow(d.start(), pending)
    d.arrow(pending, paid, label="payment received")
    d.arrow(paid, shipped, label="dispatched")
    d.arrow(shipped, delivered, label="arrived")
    d.arrow(delivered, d.end())

print(d.render())
```

## Transitions

### Basic Transitions

```python
from plantuml_compose import state_diagram

with state_diagram() as d:
    idle, active = d.states("Idle", "Active")

    # Simple transition
    d.arrow(idle, active)

    # Transition with label
    d.arrow(active, idle, label="timeout")

print(d.render())
```

### Chaining Multiple States

Pass multiple states to create a chain of transitions:

```python
from plantuml_compose import state_diagram

with state_diagram() as d:
    a, b, c, final = d.states("A", "B", "C", "D")

    # Creates: A → B → C → D (3 transitions)
    d.arrow(a, b, c, final)

print(d.render())
```

### Guards and Effects

```python
from plantuml_compose import state_diagram

with state_diagram() as d:
    idle, processing, error, done = d.states("Idle", "Processing", "Error", "Done")

    d.arrow(d.start(), idle)

    # Guard: condition that must be true
    d.arrow(idle, processing, label="submit", guard="valid input")

    # Effect: action performed during transition
    d.arrow(processing, done, label="complete", effect="sendNotification()")

    # Both guard and effect
    d.arrow(processing, error, guard="timeout", effect="logError()")

print(d.render())
```

### Flow Syntax

For more readable state sequences with interleaved labels:

```python
from plantuml_compose import state_diagram

with state_diagram() as d:
    idle, running, paused, stopped = d.states("Idle", "Running", "Paused", "Stopped")

    # More readable: state, "label", state, "label", state...
    d.flow(d.start(), idle, "start", running, "pause", paused, "stop", stopped, d.end())

print(d.render())
```

## Layout Direction

Control transition direction for better layouts:

```python
from plantuml_compose import state_diagram

with state_diagram() as d:
    a, b, c, main = d.states("A", "B", "C", "Main")

    d.arrow(d.start(), main)

    # Force direction: up, down, left, right (or shortcuts: u, d, l, r)
    d.arrow(main, a, direction="left")
    d.arrow(main, b, direction="right")
    d.arrow(main, c, direction="down")

print(d.render())
```

## Choice (Decision Points)

Use choice pseudo-states for conditional branching:

```python
from plantuml_compose import state_diagram

with state_diagram(title="Order Processing") as d:
    processing = d.state("Processing")
    success = d.state("Success")
    failure = d.state("Failure")

    # Choice creates a diamond shape
    check = d.choice("valid?")

    d.arrow(d.start(), processing)
    d.arrow(processing, check)
    d.arrow(check, success, label="yes")
    d.arrow(check, failure, label="no")

print(d.render())
```

## Fork and Join (Parallel Execution)

For concurrent activities that must all complete:

```python
from plantuml_compose import state_diagram

with state_diagram(title="Order Fulfillment") as d:
    received = d.state("Order Received")
    ready = d.state("Ready to Ship")

    # Parallel tasks
    pack = d.state("Packing")
    label_task = d.state("Labeling")
    invoice = d.state("Invoice")

    # Fork splits into parallel paths
    split = d.fork("split")
    # Join waits for all paths
    sync = d.join("sync")

    d.arrow(d.start(), received)
    d.arrow(received, split)

    # Three parallel branches
    d.arrow(split, pack)
    d.arrow(split, label_task)
    d.arrow(split, invoice)

    # All converge at join
    d.arrow(pack, sync)
    d.arrow(label_task, sync)
    d.arrow(invoice, sync)

    d.arrow(sync, ready)
    d.arrow(ready, d.end())

print(d.render())
```

### Parallel Builder (Automatic Fork/Join)

For simpler parallel structures, use the `parallel()` context manager:

```python
from plantuml_compose import state_diagram

with state_diagram(title="Payment Verification") as d:
    start_state = d.state("Start")
    complete = d.state("Complete")

    # Automatically creates fork and join
    with d.parallel("verification") as p:
        with p.branch() as b1:
            b1.state("Fraud Check")
        with p.branch() as b2:
            balance = b2.state("Balance Check")
            hold = b2.state("Hold Funds")
            b2.arrow(balance, hold)
        with p.branch() as b3:
            b3.state("Credit Check")

    d.arrow(d.start(), start_state)
    d.arrow(start_state, p.fork)
    d.arrow(p.join, complete)
    d.arrow(complete, d.end())

print(d.render())
```

## Composite States (Nested State Machines)

Group related states inside a parent state:

```python
from plantuml_compose import state_diagram

with state_diagram(title="Connection Lifecycle") as d:
    disconnected = d.state("Disconnected")

    # Composite state with nested elements
    with d.composite("Connected") as connected:
        idle = connected.state("Idle")
        active = connected.state("Active")

        connected.arrow(connected.start(), idle)
        connected.arrow(idle, active, label="request")
        connected.arrow(active, idle, label="complete")

    d.arrow(d.start(), disconnected)
    d.arrow(disconnected, connected, label="connect")
    d.arrow(connected, disconnected, label="disconnect")

print(d.render())
```

### Entry and Exit Points

Define specific entry/exit points on composite state boundaries:

```python
from plantuml_compose import state_diagram

with state_diagram(title="Processing with Boundaries") as d:
    waiting = d.state("Waiting")
    done = d.state("Done")

    with d.composite("Processing") as proc:
        # Entry point: small circle on boundary
        entry = proc.entry_point("in")
        # Exit point: circle with X on boundary
        exit_pt = proc.exit_point("out")

        validate = proc.state("Validate")
        transform = proc.state("Transform")

        proc.arrow(entry, validate)
        proc.arrow(validate, transform)
        proc.arrow(transform, exit_pt)

    d.arrow(d.start(), waiting)
    d.arrow(waiting, "in", label="start")
    d.arrow("out", done)
    d.arrow(done, d.end())

print(d.render())
```

## Concurrent States (Parallel Regions)

Show multiple independent state machines running simultaneously within a state:

```python
from plantuml_compose import state_diagram

with state_diagram(title="Keyboard Lock") as d:
    unlocked = d.state("Unlocked")

    # Concurrent state with parallel regions
    with d.concurrent("Locked") as locked:
        # First region: NumLock
        with locked.region() as r1:
            num_off = r1.state("NumLock Off")
            num_on = r1.state("NumLock On")
            r1.arrow(r1.start(), num_off)
            r1.arrow(num_off, num_on, label="press")
            r1.arrow(num_on, num_off, label="press")

        # Second region: CapsLock
        with locked.region() as r2:
            caps_off = r2.state("CapsLock Off")
            caps_on = r2.state("CapsLock On")
            r2.arrow(r2.start(), caps_off)
            r2.arrow(caps_off, caps_on, label="press")
            r2.arrow(caps_on, caps_off, label="press")

    d.arrow(d.start(), unlocked)
    d.arrow(unlocked, locked, label="lock")
    d.arrow(locked, unlocked, label="unlock")

print(d.render())
```

## History States

Return to the previous state within a composite:

```python
from plantuml_compose import state_diagram

with state_diagram(title="Media Player") as d:
    off = d.state("Off")

    with d.composite("On") as on:
        playing = on.state("Playing")
        paused = on.state("Paused")

        on.arrow(on.start(), playing)
        on.arrow(playing, paused, label="pause")
        on.arrow(paused, playing, label="play")

    # History returns to last active state within "On"
    d.arrow(d.start(), off)
    d.arrow(off, on, label="power on")
    d.arrow(on, off, label="power off")
    d.arrow(off, on.history(), label="resume")

print(d.render())
```

## Notes

Add explanatory notes to your diagram:

```python
from plantuml_compose import state_diagram

with state_diagram() as d:
    idle = d.state("Idle", note="Initial state after boot")
    active = d.state("Active")

    # Floating note
    d.note("System monitors activity", position="left")

    d.arrow(d.start(), idle)
    d.arrow(idle, active, label="activate", note="Requires authentication")

print(d.render())
```

## Styling

### State Styling

```python
from plantuml_compose import state_diagram, Style, Color, LineStyle

with state_diagram() as d:
    # Using dict syntax
    normal = d.state("Normal", style={"background": "#E3F2FD"})

    # Using Style object with LineStyle for border
    warning = d.state("Warning", style=Style(
        background=Color.named("yellow"),
        line=LineStyle(color="orange")
    ))

    # Dict with nested line style
    error = d.state("Error", style={"background": "#FFCDD2", "line": {"color": "red"}})

    d.arrow(d.start(), normal)
    d.arrow(normal, warning)
    d.arrow(warning, error)

print(d.render())
```

### Transition Styling

```python
from plantuml_compose import state_diagram, LineStyle

with state_diagram() as d:
    a, b, c = d.states("A", "B", "C")

    d.arrow(d.start(), a)

    # Dotted line
    d.arrow(a, b, style={"pattern": "dotted"})

    # Colored line
    d.arrow(b, c, style={"color": "blue"})

print(d.render())
```

### Diagram-Wide Styling

```python
from plantuml_compose import state_diagram

with state_diagram(
    title="Styled Diagram",
    diagram_style={
        "background": "white",
        "font_name": "Arial",
        "state": {"background": "#E8F5E9", "line_color": "#4CAF50"},
        "arrow": {"line_color": "#757575"},
    }
) as d:
    idle, active = d.states("Idle", "Active")

    d.arrow(d.start(), idle)
    d.arrow(idle, active)
    d.arrow(active, d.end())

print(d.render())
```

## Diagram Metadata

```python
from plantuml_compose import state_diagram

with state_diagram(
    title="Order State Machine",
    caption="Figure 1: Order lifecycle",
    header="ACME Corp",
    footer="Page 1",
    scale=1.5,  # 150% size
) as d:
    pending, complete = d.states("Pending", "Complete")

    d.arrow(d.start(), pending)
    d.arrow(pending, complete)
    d.arrow(complete, d.end())

print(d.render())
```

## SDL Receive States

For Specification and Description Language (SDL) diagrams:

```python
from plantuml_compose import state_diagram

with state_diagram() as d:
    idle = d.state("Idle")
    # SDL receive: concave polygon shape
    waiting = d.sdl_receive("Waiting for Message")
    processing = d.state("Processing")

    d.arrow(d.start(), idle)
    d.arrow(idle, waiting)
    d.arrow(waiting, processing, label="message received")
    d.arrow(processing, idle)

print(d.render())
```

## Complete Example: Order Processing System

```python
from plantuml_compose import state_diagram

with state_diagram(title="E-Commerce Order Lifecycle") as d:
    # Main states
    draft = d.state("Draft", description="Customer building cart")
    submitted = d.state("Submitted")
    cancelled = d.state("Cancelled")
    complete = d.state("Complete")

    # Validation choice
    valid_check = d.choice("valid?")

    # Processing composite with nested states
    with d.composite("Processing") as processing:
        payment = processing.state("Payment")
        fulfillment = processing.state("Fulfillment")
        shipping = processing.state("Shipping")

        processing.arrow(processing.start(), payment)
        processing.arrow(payment, fulfillment, label="paid")
        processing.arrow(fulfillment, shipping, label="packed")

    # Main flow
    d.arrow(d.start(), draft)
    d.arrow(draft, submitted, label="checkout")
    d.arrow(submitted, valid_check)
    d.arrow(valid_check, processing, label="valid")
    d.arrow(valid_check, cancelled, label="invalid")
    d.arrow(processing, complete, label="delivered")
    d.arrow(complete, d.end())

    # Cancellation from any processing state
    d.arrow(processing, cancelled, label="cancel")
    d.arrow(cancelled, d.end())

print(d.render())
```

## Quick Reference

| Method | Description |
|--------|-------------|
| `d.state(name)` | Create a state |
| `d.states(*names)` | Create multiple states |
| `d.arrow(a, b)` | Transition from a to b |
| `d.arrow(a, b, c)` | Chain: a → b → c |
| `d.flow(a, "label", b)` | Interleaved labels |
| `d.start()` | Initial pseudo-state |
| `d.end()` | Final pseudo-state |
| `d.choice(name)` | Decision diamond |
| `d.fork(name)` | Fork bar |
| `d.join(name)` | Join bar |
| `d.composite(name)` | Nested state machine |
| `d.concurrent(name)` | Parallel regions |
| `d.parallel(name)` | Auto fork/join |
| `d.note(text)` | Floating note |
| `d.history()` | History pseudo-state |
| `d.deep_history()` | Deep history pseudo-state |
