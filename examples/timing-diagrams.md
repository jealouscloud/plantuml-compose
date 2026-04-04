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
![Diagram](https://www.plantuml.com/plantuml/svg/FOp12i9034Jl-OhGSmyMVs31gthn0sHrGmriav9D-lskOZqCCxmP9ZNFvh5KSFPAU5Bnp4A6Pzu8BpnRTbO1qqSqn-6cOK_2gnOQC3UyhnDquQjdBfL62n6MUIonhDs_9JVyOKZJOKVx8Xt_wFC0YQHNzGq0)



The pattern: create a diagram, get `p` (participants) and `e` (events) namespaces, add participants with `d.add()`, then register state changes at time points with `d.at()`.

## Elements

### Participant Types

There are six participant types, each suited to a different kind of signal.

#### robust

Multi-state signals with full state labels and clear transition boundaries:

```text
p.robust("DataPath",
    states=("Idle", "Request", "Processing", "Response"),
    initial="Idle",
)
```

#### concise

Simplified, compact view with inline state names:

```text
p.concise("Status",
    states=("Off", "Starting", "Running"),
    initial="Off",
)
```

#### rectangle

Box-based rendering with state labels inside rectangles:

```text
p.rectangle("Phase",
    states=("Init", "Active", "Done"),
    initial="Init",
)
```

#### binary

High/low signal with only two states:

```text
p.binary("Enable")
```

Binary participants use `"high"` and `"low"` as state values in `e.state()`.

#### clock

Periodic square wave with configurable period, pulse width, and offset:

```text
p.clock("CLK", period=10)
p.clock("CLK2", period=20, pulse=5, offset=3)
```

Parameters: `name`, `period=`, `pulse=`, `offset=`, `ref=`, `stereotype=`, `compact=`

#### analog

Continuous signal with numeric values, rendered as a waveform:

```text
p.analog("Voltage", min_value=0, max_value=5, height=100)
```

Parameters: `name`, `ref=`, `stereotype=`, `compact=`, `min_value=`, `max_value=`, `height=`

### Common Participant Parameters

All participant types accept: `ref=`, `stereotype=`, `compact=`

```text
# Custom ref for programmatic access
p.robust("Data Bus", ref="dbus", states=("idle", "active"))

# Stereotype adds a label
p.robust("Signal", stereotype="input", states=("low", "high"))

# Per-participant compact mode
p.concise("S1", states=("A", "B"), compact=True)
```

### States: Tuple vs Dict

States can be provided as a tuple of names or a dict mapping internal names to display labels:

```text
# Tuple form: state names are used as-is
p.robust("Bus", states=("idle", "active", "error"))

# Dict form: keys are internal names, values are display labels
p.robust("Bus", states={
    "idle": "IDLE (0x00)",
    "active": "ACTIVE (0x01)",
    "error": "ERR (0xFF)",
})
```

### Initial State

Set the signal's value before the first `d.at()` time point:

```text
p.robust("Data", states=("idle", "active"), initial="idle")
```

## State Changes & Events

### d.at()

All events happen inside `d.at(time, ...)` calls. The time value can be an integer, a string (for date/time), or a relative offset.

```text
# Integer times
d.at(0,  e.state(signal, "Idle"))
d.at(10, e.state(signal, "Active"))
d.at(30, e.state(signal, "Idle"))

# String times (dates)
d.at("2026-04-01", e.state(signal, "Active"))

# Relative offsets
d.at("+100", e.state(signal, "Done"))

# Multiple events at the same time
d.at(20,
    e.state(bus, "active"),
    e.state(control, "high"),
    e.message(bus, control, "sync"),
)
```

### State Change with Color

Highlight a state transition with a background color:

```text
d.at(10, e.state(signal, "Error", color="red"))
d.at(20, e.state(signal, "Warning", color="#FFA726"))
```

### State Change with Comment

Add a comment annotation to a state transition:

```text
d.at(10, e.state(signal, "Active", comment="triggered by IRQ"))
```

### Messages Between Participants

Show a message arrow from one participant to another:

```text
d.at(15, e.message(sender, receiver, "request"))
```

With a time offset on the target (the message arrives at target's time + offset):

```text
d.at(15, e.message(sender, receiver, "async call",
                   target_time_offset=5))
```

Parameters: `source`, `target`, `label=`, `target_time_offset=`

### Intricated States

Show two states simultaneously (an ambiguous/transitioning region):

```text
d.at(25, e.intricated(signal, "state_a", "state_b"))
d.at(25, e.intricated(signal, "state_a", "state_b", color="yellow"))
```

Parameters: `participant`, `state1`, `state2`, `color=`

### Hidden States

Insert a gap or hidden region in a signal:

```text
d.at(40, e.hidden(signal))               # default "-" style
d.at(40, e.hidden(signal, style="hidden"))  # fully hidden
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

```text
d.at(50, e.state(signal, "Active"), name="phase2_start")
```

The `name=` parameter on `d.at()` creates a `TimeAnchor` that can be referenced by other timing constructs.

## Highlights

Highlight a time region with a colored background:

```text
d.highlight(start=10, end=30)
d.highlight(start=10, end=30, color="LightYellow")
d.highlight(start=10, end=30, color="#E8F5E9", caption="Critical Section")
```

Parameters: `start=`, `end=`, `color=`, `caption=`

## Constraints

Annotate timing requirements between two points on a participant:

```text
d.constraint(signal, start=10, end=30, label="{25 ms max}")
d.constraint(bus, start="phase_start", end="phase_end", label="{< 100 ns}")
```

Parameters: `participant`, `start=`, `end=`, `label=`

## Scale

Set the time-to-pixel mapping:

```text
d.scale(time_units=1, pixels=50)    # 1 time unit = 50 pixels
d.scale(time_units=10, pixels=100)  # 10 time units = 100 pixels
```

## Ticks (Analog)

Set tick mark intervals for analog participants:

```text
voltage = p.analog("Voltage", min_value=0, max_value=5)
d.add(voltage)
d.ticks(voltage, multiple=0.5)  # tick every 0.5 units
```

Parameters: `participant`, `multiple=`

## Notes

Attach notes to participants at specific times:

```text
d.note("Setup phase", participant=signal, position="top", time=0)
d.note("Critical transition", participant=signal, position="bottom", time=25)
```

Parameters: `content`, `participant`, `position=` (`"top"` or `"bottom"`), `time=`

The `time=` parameter is required for timing diagram notes.

## Layout & Organization

### Compact Mode

Reduce vertical space globally or per participant:

```text
# Global compact mode
d = timing_diagram(compact_mode=True)

# Per-participant compact mode
p.robust("S1", states=("A", "B"), compact=True)
p.concise("S2", states=("X", "Y"), compact=True)
```

### Hide Time Axis

```text
d = timing_diagram(hide_time_axis=True)
```

### Manual Time Axis

Use a manually-defined time axis instead of the automatic one:

```text
d = timing_diagram(manual_time_axis=True)
```

### Date Format

Set a custom date format for time axis labels:

```text
d = timing_diagram(date_format="yyyy-MM-dd HH:mm")
```

## Styling

### State-Level Colors

```text
d.at(10, e.state(signal, "Error", color="red"))
d.at(20, e.state(signal, "OK", color="#4CAF50"))
```

### Intricated State Colors

```text
d.at(25, e.intricated(signal, "A", "B", color="yellow"))
```

### Highlight Colors

```text
d.highlight(start=10, end=30, color="LightYellow")
d.highlight(start=40, end=60, color="#E8F5E9", caption="Safe zone")
```

### diagram_style

Theme the entire diagram with CSS-like selectors:

```text
d = timing_diagram(
    title="Styled Timing",
    diagram_style={
        "background": "white",
        "font_name": "Courier",
        "font_size": 12,
        "font_color": "#333333",
        "robust": {"background": "#E3F2FD", "line_color": "#1976D2"},
        "concise": {"background": "#C8E6C9", "line_color": "#388E3C"},
        "clock": {"line_color": "#9E9E9E"},
        "binary": {"line_color": "#FF5722"},
        "analog": {"line_color": "#3F51B5"},
        "highlight": {"background": "#FFF9C4"},
        "note": {"background": "#FFF8E1"},
        "arrow": {"line_color": "#757575"},
        "title": {"font_size": 18, "font_style": "bold"},
        "stereotypes": {
            "critical": {"line_color": "red", "font_style": "bold"},
            "internal": {"font_color": "#9E9E9E"},
        },
    },
)
```

Available selectors: `robust`, `concise`, `clock`, `binary`, `analog`, `highlight`, `note`, `arrow`, `title`, `stereotypes`

Root-level properties: `background`, `font_name`, `font_size`, `font_color`

Each element selector accepts an `ElementStyleDict` with keys like `background`, `line_color`, `font_color`, `font_name`, `font_size`, `font_style`, `round_corner`, `line_thickness`, `padding`, `margin`, `shadowing`.

The `arrow` selector accepts a `DiagramArrowStyleDict` with `line_color`, `line_thickness`, `line_style`.

## Advanced Features

### Diagram Metadata

```text
from plantuml_compose.primitives.common import Header, Footer, Legend

d = timing_diagram(
    title="Protocol Timing",
    mainframe="Bus Protocol v2.1",
    caption="Figure 5: Read cycle timing",
    header="Draft",
    footer="Confidential",
    legend="Colors indicate signal domains",
    theme="plain",
)
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
![Diagram](https://www.plantuml.com/plantuml/svg/VLDRQzim57xNhpYahnxp9TwI4efP78-mZ9PuJtqfigqcehQKIJ9TAFdlFL9acp4wZE1SldFvFbcPDbIPlcl9Ifjpo-w8uHqNXvpJWw8Tl1409QjU6sS2VAFroq79NZHhsKe5DvkaY8iSSnSyjHGrr-mZR54Ko_LymBQoVl787HVCOvOR-tbCnGLLvtz1qVBhbppse2C_75iyvZzZ5vl8eIzazTaJxMJ3SE7kH6k3h4tBe7pOmYz5XNvc2ahsksUYPkIwwAnSxtxCW6fuEaNmoiqHJannsK0K4h_dR5rwH4oyQhEVz-NM1nE21uveFmPv6EHHaCT1Vero34urs_BUrymnE_Sr-p3OHy4-3lQ9YxgQGV9PQQZfjIzB4P2wCjwqBD3CzAV0U6f18mKZkgP8EGfjmIA44__3Maqovz-Q42tNWrzRe1rRsufDidHmM_aweDmCaaNXm2SV6mo3IHPFsMZWiCTPoHIFntX4ilaKJ-1cPs_vks9CZ9WObmb7Bq4llH9uOgAntb-BZqgFylaDdI9Pd3h4fpihFDm2gu_IxIQaOL19OsG7yjdTxxg4pbvMnQm8qFGAdyt45AU3hIBJtubI6mbfY6zcKQIR9Gx8gQ7mWDTazKrGErZXS6I4kRSvL6V3z8Las0oVw3i0)



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
