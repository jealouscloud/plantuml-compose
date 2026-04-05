# Timing Diagrams

Timing diagrams show how signals change over time. They are well suited for hardware design, protocol analysis, state machine visualization, and debugging signal relationships.

## Quick Start

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(title="Container Live Migration")
p = d.participants
e = d.events

source = p.robust("Source Node",
    states=("idle", "running", "dumping"),
    initial="running",
)
d.add(source)

d.at(10, e.state(source, "dumping"))
d.at(30, e.state(source, "idle"))

print(render(d))
```

The pattern: create a diagram, get `p` (participants) and `e` (events) namespaces, add participants with `d.add()`, then register state changes at time points with `d.at()`.

## Elements

### Participant Types

There are six participant types, each suited to a different kind of signal.

#### robust

Multi-state signals with full state labels and clear transition boundaries:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram()
p = d.participants
e = d.events

sig = p.robust("DataPath",
    states=("Idle", "Request", "Processing", "Response"),
    initial="Idle",
)
d.add(sig)

d.at(10, e.state(sig, "Request"))
d.at(20, e.state(sig, "Processing"))
d.at(40, e.state(sig, "Response"))

print(render(d))
```

#### concise

Simplified, compact view with inline state names:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram()
p = d.participants
e = d.events

sig = p.concise("Status",
    states=("Off", "Starting", "Running"),
    initial="Off",
)
d.add(sig)

d.at(5, e.state(sig, "Starting"))
d.at(15, e.state(sig, "Running"))

print(render(d))
```

#### rectangle

Box-based rendering with state labels inside rectangles:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram()
p = d.participants
e = d.events

sig = p.rectangle("Phase",
    states=("Init", "Active", "Done"),
    initial="Init",
)
d.add(sig)

d.at(10, e.state(sig, "Active"))
d.at(30, e.state(sig, "Done"))

print(render(d))
```

#### binary

High/low signal with only two states:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram()
p = d.participants
e = d.events

sig = p.binary("Enable")
d.add(sig)

d.at(0, e.state(sig, "low"))
d.at(10, e.state(sig, "high"))
d.at(30, e.state(sig, "low"))

print(render(d))
```

Binary participants use `"high"` and `"low"` as state values in `e.state()`.

#### clock

Periodic square wave with configurable period, pulse width, and offset:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram()
p = d.participants

clk = p.clock("CLK", period=10)
clk2 = p.clock("CLK2", period=20, pulse=5, offset=3)
d.add(clk, clk2)

print(render(d))
```

Parameters: `name`, `period=`, `pulse=`, `offset=`, `ref=`, `stereotype=`, `compact=`

#### analog

Continuous signal with numeric values, rendered as a waveform:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram()
p = d.participants
e = d.events

sig = p.analog("Voltage", min_value=0, max_value=5, height=100)
d.add(sig)

d.at(0, e.state(sig, "0"))
d.at(10, e.state(sig, "3"))
d.at(20, e.state(sig, "5"))
d.at(30, e.state(sig, "2"))

print(render(d))
```

Parameters: `name`, `ref=`, `stereotype=`, `compact=`, `min_value=`, `max_value=`, `height=`

### Common Participant Parameters

All participant types accept: `ref=`, `stereotype=`, `compact=`

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram()
p = d.participants
e = d.events

bus = p.robust("Data Bus", ref="dbus",
    states=("idle", "active"), initial="idle")
sig = p.robust("Signal",
    states=("low", "high"), initial="low")
s1 = p.concise("S1", states=("A", "B"), initial="A", compact=True)
d.add(bus, sig, s1)

d.at(10, e.state(bus, "active"))
d.at(10, e.state(sig, "high"))
d.at(10, e.state(s1, "B"))

print(render(d))
```

### States: Tuple vs Dict

States can be provided as a tuple of names or a dict mapping internal names to display labels:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram()
p = d.participants
e = d.events

bus = p.robust("Bus", states={
    "idle": "IDLE (0x00)",
    "active": "ACTIVE (0x01)",
    "error": "ERR (0xFF)",
}, initial="idle")
d.add(bus)

d.at(10, e.state(bus, "active"))
d.at(30, e.state(bus, "error"))

print(render(d))
```

### Initial State

Set the signal's value before the first `d.at()` time point:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram()
p = d.participants
e = d.events

sig = p.robust("Data", states=("idle", "active"), initial="idle")
d.add(sig)

d.at(20, e.state(sig, "active"))

print(render(d))
```

## State Changes & Events

### d.at()

All events happen inside `d.at(time, ...)` calls. The time value can be an integer, a string (for date/time), or a relative offset.

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram()
p = d.participants
e = d.events

bus = p.robust("Bus", states=("idle", "active"), initial="idle")
ctrl = p.binary("Control")
d.add(bus, ctrl)

# Integer times
d.at(0, e.state(ctrl, "low"))
d.at(10, e.state(bus, "active"))
d.at(30, e.state(bus, "idle"))

# Multiple events at the same time
d.at(20,
    e.state(bus, "active"),
    e.state(ctrl, "high"),
    e.message(bus, ctrl, "sync"),
)

print(render(d))
```

### State Change with Color

Highlight a state transition with a background color:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram()
p = d.participants
e = d.events

sig = p.robust("Signal",
    states=("OK", "Warning", "Error"),
    initial="OK",
)
d.add(sig)

d.at(10, e.state(sig, "Error", color="red"))
d.at(20, e.state(sig, "Warning", color="#FFA726"))
d.at(30, e.state(sig, "OK"))

print(render(d))
```

### State Change with Comment

Add a comment annotation to a state transition:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram()
p = d.participants
e = d.events

sig = p.robust("Signal",
    states=("Idle", "Active"),
    initial="Idle",
)
d.add(sig)

d.at(10, e.state(sig, "Active", comment="triggered by IRQ"))
d.at(30, e.state(sig, "Idle"))

print(render(d))
```

### Messages Between Participants

Show a message arrow from one participant to another:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram()
p = d.participants
e = d.events

sender = p.robust("Sender", states=("idle", "sending"), initial="idle")
receiver = p.robust("Receiver", states=("idle", "receiving"), initial="idle")
d.add(sender, receiver)

d.at(10, e.state(sender, "sending"))
d.at(15, e.message(sender, receiver, "request"))
d.at(20, e.state(receiver, "receiving"))

print(render(d))
```

With a time offset on the target (the message arrives at target's time + offset):

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram()
p = d.participants
e = d.events

sender = p.robust("Sender", states=("idle", "sending"), initial="idle")
receiver = p.robust("Receiver", states=("idle", "receiving"), initial="idle")
d.add(sender, receiver)

d.at(10, e.state(sender, "sending"))
d.at(15, e.message(sender, receiver, "async call",
                   target_time_offset=5))
d.at(20, e.state(receiver, "receiving"))

print(render(d))
```

Parameters: `source`, `target`, `label=`, `target_time_offset=`

### Intricated States

Show two states simultaneously (an ambiguous/transitioning region):

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram()
p = d.participants
e = d.events

sig = p.robust("Signal",
    states=("state_a", "state_b", "state_c"),
    initial="state_a",
)
d.add(sig)

d.at(10, e.state(sig, "state_b"))
d.at(25, e.intricated(sig, "state_a", "state_b", color="yellow"))
d.at(35, e.state(sig, "state_c"))

print(render(d))
```

Parameters: `participant`, `state1`, `state2`, `color=`

### Hidden States

Insert a gap or hidden region in a signal:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram()
p = d.participants
e = d.events

sig = p.robust("Signal",
    states=("idle", "active"),
    initial="idle",
)
d.add(sig)

d.at(10, e.state(sig, "active"))
d.at(30, e.hidden(sig))
d.at(50, e.state(sig, "idle"))

print(render(d))
```

Parameters: `participant`, `style=` (`"-"` or `"hidden"`)

## Time Values

Time values used in `d.at()`, `d.highlight()`, `d.constraint()`, and `d.note()` can be:

| Type | Example | Description |
|------|---------|-------------|
| Integer | `0`, `10`, `100` | Numeric time units |
| String | `"2026-04-01"` | Date/time strings |
| Relative | `"+50"` | Relative to previous time |
| Named anchor | `"start_phase2"` | Reference a named anchor |

## Named Anchors

Name a time point for later reference:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram()
p = d.participants
e = d.events

sig = p.robust("Signal",
    states=("Idle", "Active", "Done"),
    initial="Idle",
)
d.add(sig)

d.at(10, e.state(sig, "Active"), name="phase2_start")
d.at(50, e.state(sig, "Done"))

print(render(d))
```

The `name=` parameter on `d.at()` creates a `TimeAnchor` that can be referenced by other timing constructs.

## Highlights

Highlight a time region with a colored background:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram()
p = d.participants
e = d.events

sig = p.robust("Signal",
    states=("Idle", "Active"),
    initial="Idle",
)
d.add(sig)

d.at(10, e.state(sig, "Active"))
d.at(30, e.state(sig, "Idle"))

d.highlight(start=10, end=30, color="#E8F5E9", caption="Critical Section")

print(render(d))
```

Parameters: `start=`, `end=`, `color=`, `caption=`

## Constraints

Annotate timing requirements between two points on a participant:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram()
p = d.participants
e = d.events

sig = p.robust("Signal",
    states=("Idle", "Active"),
    initial="Idle",
)
d.add(sig)

d.at(10, e.state(sig, "Active"))
d.at(30, e.state(sig, "Idle"))

d.constraint(sig, start=10, end=30, label="{25 ms max}")

print(render(d))
```

Parameters: `participant`, `start=`, `end=`, `label=`

## Scale

Set the time-to-pixel mapping:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram()
p = d.participants
e = d.events

sig = p.robust("Signal",
    states=("Idle", "Active"),
    initial="Idle",
)
d.add(sig)

d.at(10, e.state(sig, "Active"))
d.at(30, e.state(sig, "Idle"))

d.scale(time_units=10, pixels=100)

print(render(d))
```

## Ticks (Analog)

Set tick mark intervals for analog participants:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram()
p = d.participants
e = d.events

voltage = p.analog("Voltage", min_value=0, max_value=5)
d.add(voltage)

d.at(0, e.state(voltage, "0"))
d.at(10, e.state(voltage, "3"))
d.at(20, e.state(voltage, "5"))
d.at(30, e.state(voltage, "2"))

d.ticks(voltage, multiple=1)

print(render(d))
```

Parameters: `participant`, `multiple=`

## Notes

Attach notes to participants at specific times:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram()
p = d.participants
e = d.events

sig = p.robust("Signal",
    states=("Idle", "Active"),
    initial="Idle",
)
d.add(sig)

d.at(0, e.state(sig, "Idle"))
d.at(25, e.state(sig, "Active"))

d.note("Setup phase", participant=sig, position="top", time=0)
d.note("Critical transition", participant=sig, position="bottom", time=25)

print(render(d))
```

Parameters: `content`, `participant`, `position=` (`"top"` or `"bottom"`), `time=`

The `time=` parameter is required for timing diagram notes.

## Layout & Organization

### Compact Mode

Reduce vertical space globally or per participant:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(compact_mode=True)
p = d.participants
e = d.events

s1 = p.robust("S1", states=("A", "B"), initial="A")
s2 = p.concise("S2", states=("X", "Y"), initial="X")
d.add(s1, s2)

d.at(10, e.state(s1, "B"))
d.at(10, e.state(s2, "Y"))

print(render(d))
```

### Hide Time Axis

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(hide_time_axis=True)
p = d.participants
e = d.events

sig = p.robust("Signal", states=("Off", "On"), initial="Off")
d.add(sig)

d.at(10, e.state(sig, "On"))

print(render(d))
```

### Manual Time Axis

Use a manually-defined time axis instead of the automatic one:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(manual_time_axis=True)
p = d.participants
e = d.events

sig = p.robust("Signal", states=("Off", "On"), initial="Off")
d.add(sig)

d.at(10, e.state(sig, "On"))
d.at(30, e.state(sig, "Off"))

print(render(d))
```

### Date Format

Set a custom date format for time axis labels:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(date_format="yyyy-MM-dd")
p = d.participants
e = d.events

sig = p.robust("Signal", states=("Off", "On"), initial="Off")
d.add(sig)

d.at(10, e.state(sig, "On"))
d.at(30, e.state(sig, "Off"))

print(render(d))
```

## Styling

### State-Level Colors

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram()
p = d.participants
e = d.events

sig = p.robust("Signal",
    states=("OK", "Error"),
    initial="OK",
)
d.add(sig)

d.at(10, e.state(sig, "Error", color="red"))
d.at(20, e.state(sig, "OK", color="#4CAF50"))

print(render(d))
```

### Intricated State Colors

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram()
p = d.participants
e = d.events

sig = p.robust("Signal",
    states=("A", "B", "C"),
    initial="A",
)
d.add(sig)

d.at(10, e.state(sig, "B"))
d.at(25, e.intricated(sig, "A", "B", color="yellow"))
d.at(35, e.state(sig, "C"))

print(render(d))
```

### Highlight Colors

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram()
p = d.participants
e = d.events

sig = p.robust("Signal",
    states=("Idle", "Active"),
    initial="Idle",
)
d.add(sig)

d.at(10, e.state(sig, "Active"))
d.at(30, e.state(sig, "Idle"))
d.at(40, e.state(sig, "Active"))
d.at(60, e.state(sig, "Idle"))

d.highlight(start=10, end=30, color="LightYellow")
d.highlight(start=40, end=60, color="#E8F5E9", caption="Safe zone")

print(render(d))
```

### diagram_style

Theme the entire diagram with CSS-like selectors:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(
    title="Styled Timing",
    diagram_style={
        "background": "white",
        "font_name": "Courier",
        "font_size": 12,
        "font_color": "#333333",
        "robust": {"background": "#E3F2FD", "line_color": "#1976D2"},
        "concise": {"background": "#C8E6C9", "line_color": "#388E3C"},
        "highlight": {"background": "#FFF9C4"},
        "note": {"background": "#FFF8E1"},
        "arrow": {"line_color": "#757575"},
    },
)
p = d.participants
e = d.events

sig = p.robust("Bus", states=("idle", "active"), initial="idle")
status = p.concise("Status", states=("off", "on"), initial="off")
d.add(sig, status)

d.at(10, e.state(sig, "active"), e.state(status, "on"))
d.at(30, e.state(sig, "idle"), e.state(status, "off"))

print(render(d))
```

Available selectors: `robust`, `concise`, `clock`, `binary`, `analog`, `highlight`, `note`, `arrow`, `title`, `stereotypes`

Root-level properties: `background`, `font_name`, `font_size`, `font_color`

Each element selector accepts an `ElementStyleDict` with keys like `background`, `line_color`, `font_color`, `font_name`, `font_size`, `font_style`, `round_corner`, `line_thickness`, `padding`, `margin`, `shadowing`.

The `arrow` selector accepts a `DiagramArrowStyleDict` with `line_color`, `line_thickness`, `line_style`.

## Advanced Features

### Diagram Metadata

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(
    title="Protocol Timing",
    mainframe="Bus Protocol v2.1",
    caption="Figure 5: Read cycle timing",
    header="Draft",
    footer="Confidential",
    legend="Colors indicate signal domains",
)
p = d.participants
e = d.events

sig = p.robust("Bus", states=("idle", "active"), initial="idle")
d.add(sig)

d.at(10, e.state(sig, "active"))
d.at(30, e.state(sig, "idle"))

print(render(d))
```

### Complete Example

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(
    title="SPI Transfer Sequence",
    compact_mode=True,
    diagram_style={
        "robust": {"background": "#E3F2FD"},
        "concise": {"background": "#FFF9C4"},
        "binary": {"line_color": "#1976D2"},
        "clock": {"line_color": "#9E9E9E"},
        "highlight": {"background": "#FFF8E1"},
    },
)
p = d.participants
e = d.events

clk = p.clock("SCLK", period=10)
cs = p.binary("CS")
mosi = p.robust("MOSI", states=("Z", "D0", "D1", "D2", "D3"), initial="Z")
miso = p.robust("MISO", states=("Z", "R0", "R1", "R2", "R3"), initial="Z")
status = p.concise("Status", states=("idle", "setup", "transfer", "done"))

d.add(clk, cs, mosi, miso, status)

# Setup
d.at(0,
    e.state(status, "idle"),
    e.state(cs, "high"),
    name="t0",
)

# Begin transfer
d.at(5,
    e.state(cs, "low"),
    e.state(status, "setup"),
)

d.at(10,
    e.state(mosi, "D0"),
    e.state(status, "transfer"),
)
d.at(20, e.state(mosi, "D1"), e.state(miso, "R0"))
d.at(30, e.state(mosi, "D2"), e.state(miso, "R1"))
d.at(40,
    e.state(mosi, "D3", color="LightGreen"),
    e.state(miso, "R2"),
)
d.at(50, e.state(miso, "R3"))

# End transfer
d.at(55,
    e.state(cs, "high"),
    e.state(mosi, "Z"),
    e.state(miso, "Z"),
    e.state(status, "done"),
    name="t_end",
)

d.highlight(start=10, end=50, color="#E8F5E9", caption="Data Phase")

d.constraint(mosi, start=10, end=50, label="{4 bytes}")

d.at(25, e.message(mosi, miso, "echo"))

d.note("CS must be low during transfer",
       participant=cs, position="bottom", time=30)

d.scale(time_units=10, pixels=80)

print(render(d))
```

## Quick Reference

| Method | Description |
|--------|-------------|
| `p.robust(name, states=, initial=)` | Multi-state signal |
| `p.concise(name, states=, initial=)` | Compact state signal |
| `p.rectangle(name, states=, initial=)` | Box-style signal |
| `p.binary(name)` | High/low signal |
| `p.clock(name, period=)` | Periodic square wave |
| `p.analog(name)` | Continuous waveform |
| `d.add(*participants)` | Register participants |
| `d.at(time, *events, name=)` | Events at a time point |
| `e.state(p, state)` | Change participant state |
| `e.message(src, tgt, label=)` | Inter-participant message |
| `e.intricated(p, s1, s2)` | Ambiguous/transitioning state |
| `e.hidden(p)` | Gap in signal |
| `d.highlight(start=, end=)` | Highlighted time region |
| `d.constraint(p, start=, end=, label=)` | Timing constraint |
| `d.scale(time_units=, pixels=)` | Time-to-pixel mapping |
| `d.ticks(p, multiple=)` | Analog tick interval |
| `d.note(text, participant=, time=, position=)` | Note on a signal |

### Participant Parameters

| Parameter | Applies to | Description |
|-----------|-----------|-------------|
| `states=` | robust, concise, rectangle | Tuple of names or dict of name-to-label |
| `initial=` | robust, concise, rectangle | Starting state before first `d.at()` |
| `ref=` | All types | Short name for programmatic access |
| `stereotype=` | All types | Label annotation |
| `compact=` | All types | Per-participant compact mode |
| `period=` | clock | Square wave period |
| `pulse=` | clock | Pulse width |
| `offset=` | clock | Phase offset |
| `min_value=` | analog | Minimum Y-axis value |
| `max_value=` | analog | Maximum Y-axis value |
| `height=` | analog | Height in pixels |

### Event Parameters

| Parameter | Applies to | Description |
|-----------|-----------|-------------|
| `color=` | state, intricated | Background color for the state region |
| `comment=` | state | Annotation text on the transition |
| `target_time_offset=` | message | Time offset at the target end |
| `style=` | hidden | `"-"` (default) or `"hidden"` |

### Diagram Options

| Parameter | Description |
|-----------|-------------|
| `title=` | Diagram title |
| `mainframe=` | Mainframe label |
| `caption=` | Caption text below diagram |
| `header=` | Header text |
| `footer=` | Footer text |
| `legend=` | Legend text |
| `theme=` | PlantUML theme name |
| `date_format=` | Custom date format string |
| `diagram_style=` | Dict of CSS-like style selectors |
| `compact_mode=` | Global compact mode (bool) |
| `hide_time_axis=` | Hide the time axis (bool) |
| `manual_time_axis=` | Manual time axis (bool) |
