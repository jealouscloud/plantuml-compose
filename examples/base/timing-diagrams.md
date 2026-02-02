# Timing Diagrams

Timing diagrams show how signals change over time. They're essential for:

- **Hardware design**: Clock signals, data buses, reset sequences
- **Protocol analysis**: Communication timing between components
- **State machine visualization**: When states change relative to time
- **Digital logic debugging**: Understanding signal relationships and timing constraints

A timing diagram shows time on the horizontal axis and signal values on the vertical axis, with each signal as a separate row (called a "participant").

## Core Concepts

**Participant**: A signal line being tracked. Types include robust (multiple named states), concise (simplified), clock (periodic), binary (high/low), analog (continuous), and rectangle (labeled boxes).

**State**: The current value of a signal at a point in time. For example, "Idle", "Active", "high", "low".

**Time**: Either numeric units (0, 10, 50) or date/time strings. All state changes happen at specific times.

**Anchor**: A named time point you can reference later. Useful for aligning events across signals.

**Constraint**: An annotation showing timing requirements between two points.

## Your First Timing Diagram

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="Simple Signal") as d:
    signal = d.robust("Data")

    d.state(signal, "Idle", at=0)
    d.state(signal, "Active", at=10)
    d.state(signal, "Idle", at=30)

print(d.render())
```

The `timing_diagram()` context manager creates a builder. Inside, you:
1. Create participants (signal lines) with `d.robust()`, `d.concise()`, etc.
2. Set states at specific times with `d.state()`
3. Optionally add messages, constraints, and highlights

## Participant Types

PlantUML supports six types of participants, each suited to different signal types.

### Robust Participants

Robust participants show complex, multi-state signals with clear state labels:

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="Robust Signal") as d:
    data = d.robust("DataPath")

    d.state(data, "Idle", at=0)
    d.state(data, "Request", at=10)
    d.state(data, "Processing", at=20)
    d.state(data, "Response", at=40)
    d.state(data, "Idle", at=60)

print(d.render())
```

### Concise Participants

Concise participants show a simplified, compact view with state names inline:

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="Concise Signal") as d:
    status = d.concise("Status")

    d.state(status, "Off", at=0)
    d.state(status, "Starting", at=5)
    d.state(status, "Running", at=15)
    d.state(status, "Off", at=50)

print(d.render())
```

### Clock Signals

Clock signals automatically generate periodic waveforms. You specify the period (and optionally pulse width and offset):

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="Clock Signal") as d:
    # Basic clock with period of 20 time units
    clk = d.clock("Clock", period=20)

    # Clock with custom pulse width (high time)
    fast_clk = d.clock("FastClock", period=10, pulse=3)

    # Clock with offset (phase shift)
    delayed_clk = d.clock("DelayedClock", period=20, offset=5)

print(d.render())
```

### Binary Signals

Binary signals have only two states: high and low. Ideal for digital signals:

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="Binary Signal") as d:
    enable = d.binary("Enable")
    reset = d.binary("Reset")

    d.state(enable, "low", at=0)
    d.state(enable, "high", at=10)
    d.state(enable, "low", at=40)

    d.state(reset, "high", at=0)
    d.state(reset, "low", at=5)
    d.state(reset, "high", at=50)

print(d.render())
```

### Analog Signals

Analog signals show continuous value transitions rather than discrete states:

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="Analog Signal") as d:
    voltage = d.analog("Voltage")

    d.state(voltage, "0", at=0)
    d.state(voltage, "2.5", at=10)
    d.state(voltage, "5", at=20)
    d.state(voltage, "3.3", at=30)
    d.state(voltage, "0", at=50)

print(d.render())
```

#### Analog Range and Height

Specify the value range and visual height for analog signals:

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="Analog with Range") as d:
    # Define voltage with explicit range 0-5V and custom height
    voltage = d.analog("Voltage", min_value=0, max_value=5, height=100)

    d.state(voltage, "0", at=0)
    d.state(voltage, "3.3", at=20)
    d.state(voltage, "5", at=40)
    d.state(voltage, "1.8", at=60)

print(d.render())
```

#### Analog Tick Marks

Add tick marks to analog signals to show value divisions:

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="Analog with Ticks") as d:
    voltage = d.analog("Voltage", min_value=0, max_value=10)

    # Add tick marks every 2 units
    d.ticks(voltage, multiple=2)

    d.state(voltage, "0", at=0)
    d.state(voltage, "5", at=20)
    d.state(voltage, "10", at=40)
    d.state(voltage, "2", at=60)

print(d.render())
```

### Rectangle Participants

Rectangle participants display states as labeled rectangles, similar to robust but with a different visual style:

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="Rectangle Signal") as d:
    data = d.rectangle("DataBus")

    d.state(data, "Idle", at=0)
    d.state(data, "Address", at=10)
    d.state(data, "Data", at=30)
    d.state(data, "Idle", at=50)

print(d.render())
```

## Compact Mode

Compact mode reduces vertical space by displaying states more compactly. You can enable it globally or per-participant.

### Global Compact Mode

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="Global Compact", compact_mode=True) as d:
    data = d.robust("Data")
    status = d.concise("Status")

    d.state(data, "Idle", at=0)
    d.state(data, "Active", at=20)
    d.state(data, "Idle", at=50)

    d.state(status, "Ready", at=0)
    d.state(status, "Busy", at=20)
    d.state(status, "Ready", at=50)

print(d.render())
```

### Per-Participant Compact Mode

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="Per-Participant Compact") as d:
    # Only this participant is compact
    data = d.robust("Data", compact=True)
    status = d.concise("Status")

    d.state(data, "Idle", at=0)
    d.state(data, "Active", at=20)

    d.state(status, "Ready", at=0)
    d.state(status, "Busy", at=20)

print(d.render())
```

## Time Axis Control

Control whether the time axis is shown and how it behaves.

### Hiding the Time Axis

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="Hidden Time Axis", hide_time_axis=True) as d:
    signal = d.robust("Signal")

    d.state(signal, "A", at=0)
    d.state(signal, "B", at=20)
    d.state(signal, "A", at=40)

print(d.render())
```

### Manual Time Axis

Use manual time axis when you want full control over time display:

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="Manual Time Axis", manual_time_axis=True) as d:
    signal = d.robust("Signal")

    d.state(signal, "Init", at=0)
    d.state(signal, "Run", at=100)
    d.state(signal, "Stop", at=500)

print(d.render())
```

## State Ordering

Define the order in which states appear on the vertical axis for robust participants.

### Basic State Order

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="State Ordering") as d:
    fsm = d.robust("FSM")

    # Define states in display order (top to bottom)
    d.define_states(fsm, "Idle", "Ready", "Active", "Done")

    d.state(fsm, "Idle", at=0)
    d.state(fsm, "Ready", at=10)
    d.state(fsm, "Active", at=20)
    d.state(fsm, "Done", at=40)
    d.state(fsm, "Idle", at=50)

print(d.render())
```

### State Labels

Assign display labels that differ from state names:

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="State Labels") as d:
    state = d.robust("State")

    # Define states with display labels
    d.define_states(
        state, "S0", "S1", "S2", "S3",
        labels={"S0": "Idle", "S1": "Start", "S2": "Run", "S3": "Stop"}
    )

    d.state(state, "S0", at=0)
    d.state(state, "S1", at=10)
    d.state(state, "S2", at=20)
    d.state(state, "S3", at=40)

print(d.render())
```

## Initial States

Set a participant's state before the timeline begins:

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="Initial States") as d:
    signal = d.robust("Signal")
    enable = d.binary("Enable")

    # Set initial states (shown before @0)
    d.initial_state(signal, "Idle")
    d.initial_state(enable, "low")

    # Then show transitions at specific times
    d.state(signal, "Active", at=0)
    d.state(signal, "Processing", at=20)

    d.state(enable, "high", at=10)
    d.state(enable, "low", at=40)

print(d.render())
```

## Stereotypes

Add stereotypes to categorize participants (works with robust, concise, binary, and rectangle types):

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="Stereotypes") as d:
    # Hardware signals
    data = d.robust("DataBus", stereotype="<<hw>>")
    enable = d.binary("Enable", stereotype="<<hw>>")

    # Software signals
    status = d.concise("Status", stereotype="<<sw>>")

    d.state(data, "Idle", at=0)
    d.state(data, "Active", at=20)

    d.state(enable, "low", at=0)
    d.state(enable, "high", at=15)

    d.state(status, "Ready", at=0)
    d.state(status, "Busy", at=25)

print(d.render())
```

## State Changes

### Basic State Changes

Set a participant's state at a specific time:

```python
from plantuml_compose import timing_diagram

with timing_diagram() as d:
    signal = d.robust("Signal")

    d.state(signal, "A", at=0)
    d.state(signal, "B", at=20)
    d.state(signal, "C", at=40)
    d.state(signal, "A", at=60)

print(d.render())
```

### Colored States

Add color to highlight specific states:

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="Colored States") as d:
    status = d.robust("Status")

    d.state(status, "Normal", at=0, color="LightGreen")
    d.state(status, "Warning", at=20, color="Yellow")
    d.state(status, "Error", at=40, color="Red")
    d.state(status, "Normal", at=60, color="LightGreen")

print(d.render())
```

### State Comments

Add inline comments/annotations to state changes:

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="State Comments") as d:
    signal = d.robust("Signal")

    d.state(signal, "Idle", at=0, comment="power on")
    d.state(signal, "Active", at=20, comment="request received")
    d.state(signal, "Done", at=50, comment="transaction complete")
    d.state(signal, "Idle", at=70)

print(d.render())
```

### Intricated States

Intricated states show undefined or transitioning values between two possibilities. This is useful for signals in metastable or don't-care regions:

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="Intricated States") as d:
    data = d.robust("Data")

    d.state(data, "Valid", at=0)
    d.intricated(data, "0", "1", at=20)  # Undefined between 0 and 1
    d.state(data, "Valid", at=40)

print(d.render())
```

### Hidden States

Hidden states create gaps in the signal, useful for showing time breaks or don't-care regions:

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="Hidden States") as d:
    signal = d.robust("Signal")

    d.state(signal, "Active", at=0)
    d.hidden(signal, at=20, style="-")  # Dash style
    d.state(signal, "Active", at=40)

print(d.render())
```

## Time Anchors

Anchors let you name specific time points and reference them later. This is especially useful for aligning events across multiple signals.

### Creating Anchors

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="Time Anchors") as d:
    clk = d.clock("Clock", period=20)
    data = d.robust("Data")

    # Create named anchor at time 0
    start = d.anchor("start", at=0)

    # Create anchor at time 50
    trigger = d.anchor("trigger", at=50)

    d.state(data, "Idle", at=start)
    d.state(data, "Active", at=trigger)

print(d.render())
```

### Anchor Arithmetic

Anchors support Python arithmetic, making it easy to express relative timing:

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="Anchor Arithmetic") as d:
    clk = d.clock("Clock", period=20)
    data = d.robust("Data")
    ack = d.robust("Ack")

    # Define a reference point
    start = d.anchor("start", at=0)

    # Use arithmetic to express timing relative to start
    d.state(data, "Idle", at=start)
    d.state(data, "Request", at=start + 20)
    d.state(data, "Data", at=start + 40)
    d.state(data, "Idle", at=start + 80)

    # Ack responds 10 units after each data change
    d.state(ack, "Idle", at=start)
    d.state(ack, "Wait", at=start + 30)
    d.state(ack, "Done", at=start + 50)
    d.state(ack, "Idle", at=start + 90)

print(d.render())
```

## Messages

Messages show communication between participants at specific times.

### Basic Messages

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="Messages") as d:
    controller = d.robust("Controller")
    device = d.robust("Device")

    d.state(controller, "Idle", at=0)
    d.state(controller, "Sending", at=10)
    d.state(controller, "Idle", at=30)

    d.state(device, "Idle", at=0)
    d.state(device, "Receiving", at=15)
    d.state(device, "Idle", at=35)

    # Message from controller to device
    d.message(controller, device, "data", at=10)

print(d.render())
```

### Messages with Time Offset

The `target_offset` parameter lets you show message propagation delay:

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="Message Delay") as d:
    sender = d.robust("Sender")
    receiver = d.robust("Receiver")

    d.state(sender, "Idle", at=0)
    d.state(sender, "Transmit", at=10)
    d.state(sender, "Idle", at=20)

    d.state(receiver, "Idle", at=0)
    d.state(receiver, "Receive", at=25)
    d.state(receiver, "Idle", at=35)

    # Message arrives 15 time units after being sent
    d.message(sender, receiver, "packet", at=10, target_offset=15)

print(d.render())
```

## Timing Constraints

Constraints annotate timing requirements between two time points on a participant:

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="Timing Constraints") as d:
    clk = d.clock("Clock", period=20)
    data = d.robust("Data")

    d.state(data, "Setup", at=0)
    d.state(data, "Hold", at=30)
    d.state(data, "Done", at=60)

    # Show timing constraint from time 0 to 30
    d.constraint(data, start=0, end=30, label="{30ns setup}")

    # Show another constraint
    d.constraint(data, start=30, end=60, label="{30ns hold}")

print(d.render())
```

## Highlighting Time Regions

Highlight important time periods with colored regions:

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="Highlighted Regions") as d:
    signal = d.robust("Signal")

    d.state(signal, "Idle", at=0)
    d.state(signal, "Critical", at=20)
    d.state(signal, "Idle", at=50)

    # Highlight the critical region
    d.highlight(start=20, end=50, color="Yellow", caption="Critical Section")

print(d.render())
```

### Multiple Highlights

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="Multiple Highlights") as d:
    state = d.robust("State")

    d.state(state, "Init", at=0)
    d.state(state, "Phase1", at=20)
    d.state(state, "Phase2", at=50)
    d.state(state, "Done", at=80)

    d.highlight(start=0, end=20, color="LightBlue", caption="Initialization")
    d.highlight(start=20, end=50, color="LightGreen", caption="Processing")
    d.highlight(start=50, end=80, color="LightCoral", caption="Cleanup")

print(d.render())
```

## Scale

Control how time maps to visual width:

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="Custom Scale") as d:
    signal = d.robust("Signal")

    # 100 time units = 200 pixels
    d.scale(time_units=100, pixels=200)

    d.state(signal, "A", at=0)
    d.state(signal, "B", at=50)
    d.state(signal, "C", at=100)

print(d.render())
```

## Notes

Add explanatory notes to participants at specific times:

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="Notes") as d:
    signal = d.robust("Signal")

    d.state(signal, "Idle", at=0)
    d.state(signal, "Active", at=20)
    d.state(signal, "Idle", at=50)

    d.note(signal, "Signal becomes active here", at=20, position="top")
    d.note(signal, "Returns to idle", at=50, position="bottom")

print(d.render())
```

## Complete Example: CPU Bus Transaction

Here's a realistic example showing a CPU bus read transaction:

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="CPU Bus Read Transaction") as d:
    clk = d.clock("CLK", period=10)
    addr = d.robust("ADDR")
    data = d.robust("DATA")
    rd = d.binary("RD#")
    ack = d.binary("ACK#")

    # Scale for readability
    d.scale(time_units=100, pixels=400)

    # Define key time points
    t0 = d.anchor("t0", at=0)

    # Address phase
    d.state(addr, "XX", at=t0)
    d.state(addr, "A5", at=t0 + 10)  # Address valid on clock edge
    d.state(addr, "XX", at=t0 + 60)

    # Read strobe
    d.state(rd, "high", at=t0)
    d.state(rd, "low", at=t0 + 15)   # Assert read
    d.state(rd, "high", at=t0 + 55)  # Deassert read

    # Data phase
    d.state(data, "XX", at=t0)
    d.state(data, "D3", at=t0 + 35)  # Data valid after delay
    d.state(data, "XX", at=t0 + 60)

    # Acknowledge
    d.state(ack, "high", at=t0)
    d.state(ack, "low", at=t0 + 40)  # Slave acknowledges
    d.state(ack, "high", at=t0 + 55)

    # Timing constraints
    d.constraint(addr, start=t0 + 10, end=t0 + 35, label="{25ns access}")

    # Highlight data valid window
    d.highlight(start=35, end=55, color="LightGreen", caption="Data Valid")

print(d.render())
```

## Complete Example: SPI Communication

```python
from plantuml_compose import timing_diagram

with timing_diagram(title="SPI Transaction") as d:
    sclk = d.clock("SCLK", period=20)
    mosi = d.robust("MOSI")
    miso = d.robust("MISO")
    cs = d.binary("CS#")

    d.scale(time_units=200, pixels=500)

    # Chip select
    d.state(cs, "high", at=0)
    d.state(cs, "low", at=10)
    d.state(cs, "high", at=170)

    # Master sends command
    d.state(mosi, "Z", at=0)
    d.state(mosi, "CMD", at=10)
    d.state(mosi, "ADDR", at=50)
    d.state(mosi, "Z", at=90)

    # Slave responds
    d.state(miso, "Z", at=0)
    d.state(miso, "Z", at=90)
    d.state(miso, "DATA", at=90)
    d.state(miso, "Z", at=170)

    # Show data transfer
    d.message(mosi, miso, "request", at=50)
    d.message(miso, mosi, "response", at=130)

    d.highlight(start=10, end=90, color="LightBlue", caption="Command")
    d.highlight(start=90, end=170, color="LightGreen", caption="Response")

print(d.render())
```

## Diagram Styling

Customize the appearance with `diagram_style`:

```python
from plantuml_compose import timing_diagram

with timing_diagram(
    title="Styled Timing Diagram",
    diagram_style={
        "background": "WhiteSmoke",
        "robust": {"background": "LightBlue"},
        "binary": {"background": "LightGreen"},
        "highlight": {"background": "Yellow"},
    }
) as d:
    data = d.robust("Data")
    enable = d.binary("Enable")

    d.state(data, "Idle", at=0)
    d.state(data, "Active", at=20)
    d.state(data, "Idle", at=50)

    d.state(enable, "low", at=0)
    d.state(enable, "high", at=15)
    d.state(enable, "low", at=55)

    d.highlight(start=20, end=50, caption="Active Period")

print(d.render())
```

## Using Date/Time Values

For real-world timing, use date or time strings instead of numeric units:

```python
from plantuml_compose import timing_diagram

with timing_diagram(
    title="Date-Based Timing",
    date_format="HH:mm:ss"
) as d:
    server = d.robust("Server")
    client = d.robust("Client")

    d.state(server, "Idle", at="09:00:00")
    d.state(server, "Processing", at="09:00:15")
    d.state(server, "Idle", at="09:01:00")

    d.state(client, "Waiting", at="09:00:00")
    d.state(client, "Request", at="09:00:10")
    d.state(client, "Received", at="09:00:45")
    d.state(client, "Idle", at="09:01:00")

    d.message(client, server, "GET /api", at="09:00:10")
    d.message(server, client, "200 OK", at="09:00:30")

print(d.render())
```

## Quick Reference

| Method | Purpose | Key Parameters |
|--------|---------|----------------|
| `d.robust(name)` | Multi-state signal | `alias`, `stereotype`, `compact` |
| `d.concise(name)` | Simplified signal | `alias`, `stereotype`, `compact` |
| `d.clock(name, period)` | Periodic signal | `period`, `pulse`, `offset`, `stereotype` |
| `d.binary(name)` | High/low signal | `alias`, `stereotype`, `compact` |
| `d.analog(name)` | Continuous signal | `min_value`, `max_value`, `height`, `alias` |
| `d.rectangle(name)` | Rectangle-style signal | `alias`, `stereotype`, `compact` |
| `d.state(participant, state, at)` | Set state | `at`, `color`, `comment` |
| `d.initial_state(participant, state)` | Pre-timeline state | |
| `d.define_states(participant, *states)` | Define state order | `labels` |
| `d.ticks(participant, multiple)` | Analog tick marks | |
| `d.anchor(name, at)` | Named time point | Returns `AnchorRef` |
| `d.intricated(participant, s1, s2, at)` | Undefined state | `color` |
| `d.hidden(participant, at)` | Gap in signal | `style` |
| `d.message(src, dst, label, at)` | Inter-signal message | `target_offset` |
| `d.constraint(participant, start, end, label)` | Timing annotation | |
| `d.highlight(start, end)` | Colored region | `color`, `caption` |
| `d.scale(time_units, pixels)` | Visual scaling | |
| `d.note(participant, text, at)` | Explanatory note | `position` |
