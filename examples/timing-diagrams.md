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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGZEp2q0K-bvYJbSHVb9fSKb2aekYIM9IWg9nGhn1OPS3WPSG4eXirZ1CoKdbSl14CvtJ2x9B0EA6AEfICrB0Te00000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGZAJoejBb48papFIypXAeBmb5mIIn834aiob1GIYnNY2mov70ouW9H2Ph62PqfEAfU38PmVb5fOcbfSmkLW11SAACfFJYqkpinBvt8mGL9ON92VLmpKR8PcM6fU2j110000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LN3EpqlEB4vL2CvCpqlCuKg6SfM2In9BIekL51AB5U8B3BaS3BY0b49ciO9_MXgNWocC5mmoBJCldSl142uML9gN1nOoHTMKcfS2j1S0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LN3EoK_ELWZEJCzBpE5A1dEKm69A2ed52l45XWhbcIKP2WMfHPdvAGf61Z0rRed59SZgZ53K6Hee59Jc5ASg6CFKkwJc95QcfY1hCKOpMY4_BQqujKJ1bCiXDIy5w4G0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LN3Ap4iigbG8papFIypXIeBmb5pp4fDoKfKK4eiLuWiCuS91gSMf9L1H8ou70owWf49ciK9EVZcNWo6Scv6Pdi7bO88g3U8P8MHDOLomf2cQR6fU2j290000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LN3CIyp9JrS8pam7ChWI8JobiFoSaiJqL2M5n6A5-093BWS3BY2ba5ciOC3bO0Zd6EcPSZaOmRb0ZZ6SOwndpELWYgmlDIy5Q2y0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/FSx12i8m40JG-tx5q0yeYRNYSVq53rvbfKiIY6anA_NpMv3cC8StSnck9X_xlZDPigou5Sbpm9eiuYubACc_wHvpDWdQuQMsgXOuI9amGYgUYwSzI1NUEIpffxaYQWhHYDsnEU9Jmz0FnEV6aVZIuFihiPPf_xK1)



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
![Diagram](https://www.plantuml.com/plantuml/svg/FOx12W8n34Jl-OfXlw1Tr7Fz1_4grGrhiKqNcxA_RrJe8GnlXXaIciQtzf99asR6MMAkA_QaJrpIuzKe_ftfMhF6bIVSMNTcWKEK1TwauRPvieD-Av1UK0MbPqsRZSuKt2zE3Ox2FE18uJ30MtGQP1sMnHxx0000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGXAJIv9p4i7ie8pq_CISxYAu09ABeabYKwbnKeAYSKAyGM6N0u6N41A8RDOmJCb9vNBmH3ETqn9AKejBkPoC8OBWJHpEPYYQKdDIm7Q3G00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NOv12W8n34NtEKNe2RJWlgE2kDK3IARDej1EXqagpEtj34N4vNjv7-94QT6Q4-GI67t9Cta5ZPeORwcCbF3IvLB6AehcIae6IV0r7y6NoKTXD4ybhTAz1NU0TiOeU0-9mTal3rxZkvdJNx6XtV315DQ-sCMvojhxtu2dq1x_0000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/FOux3W8n34Hxdy9AZmGvGVWqT2iu03A92qlPR1GxIDoUmAweHlFU51FKg5cVCvXOPfouxQP194gbOdXUvahH8Aw9RNbsDNGNCd98Yezw6B94KKPtDxAk6_SGzZ0qYk8rPORW__qOJLwy3lmNt9ZIUrlymAdhw5pI-FO1)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuSh8J4bLACdCJTLDhCWivYh9BCb9LV38J4b9pLC80GehE8A4Y_AJIejB59I2CzFp4dEK51AB5U8B3BaS3BY0b49ciO8ZbuCHdEF4vM22B9EQbmAq2W00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/HSqn2uD038RXFRyYk1TqS4_73brwxXBfKG9tKIuvyETxHT3futsMZyovUCq9CclbX2uvFdWN0nTF4TydJutn-UUoBjKSko0_vTGX6yxR0DH36nJ3bue33Vq5dwf0uzt1rmqewhVT7W00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGWkIIn9LV0lIaajoinBvohAJoejBb5GSWlsLL98B5Q8Bp3a0cA5323RCoKdLISeDJ6bKiSnkIIpB5N79JylbSl10AmY4wA0oy4GpWUhvN8mWWj0j74vcC1582QOeXcHcfS2T240)



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
![Diagram](https://www.plantuml.com/plantuml/svg/JOx12O0m34NlcI9q0biT85V1anr0AXOir2estTzg3lKGo7lyV4APtStbYC21eqVBZZrERlKnmtsk9JEgJofq6PTBGntSwwx6BOgrNPFsxHFxYyubYJF_v7c9x86a8NnTf1jf8DF800sDwfbFM_tz0G00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/LOv12i9034NtEKNe2QR50umB5zq9FO1asj06ubGcQSNREu8Lt7tUutz-DAVYsrt1nPMnp-92YeEJiq5PqsQEpI1p9csG36-F5f9aAYziBfcIyXTtK1MAOJyfrznzigvFYE4mvz5bPuZTZrpBEhAPv1bY6uxM8lC2yHJ-LZXFzUSR)



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
![Diagram](https://www.plantuml.com/plantuml/svg/LOz12eD034NtEKMO4rJ5dOWjxQBRUe0IDTI1wOnCOiNRTqGgTFd-omz98qfHvxS3jUeOM-N8GTU91MBePb4qLrAwp6AmgiQbhf44drC6dVKKLpGtJvtZVvj37tnlXT6qIhgNvT05D2T8Ez0AtWV7qEG7dtkr7zu7yYrmOO4cAtyusjUussB31zEmfdxv2zAbYTaFwQal)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIhAJoejBb5G2ivCpqlCKL98B5Q8Bp3aSZ3W0b8AcSKAZbmEHd2E4vU32PpZpELWXgmiDIy5Q280)



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
![Diagram](https://www.plantuml.com/plantuml/svg/VOun2W9134Nxd2BiN415h0CYDcAXXLZ9o8Hr83kH98FNTsssj7fy7dmUUMIBFWb43M7SgwXnmMlaO0VJP_V0uJUx3vWT7-yrq0fcO7KygqrPC9tg-8gZCJUWpM9lsLfj8wOxY-W7QBkeWvaQfWiNeDtVEsvbxli2)



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
![Diagram](https://www.plantuml.com/plantuml/svg/LOv12a8n34JtEKNu9r1115SLtRZ-1v3O1YcqIMrJlRvPVN0rCFEOcJ2CkirQmB8LnjN86AzQAuiDwFgSmt1PyqkeB4W37sqFOGSkc0VUK-4pDlroHnK8XosvHCiVppg_9tj7vyXk90Z7ZRcfE66TP93ZAXYrjiB644v_6n1Oaj_y0G00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LV3CAodAJ4uiIKrH22u1KiLSHVb9fSKb2aekYIM9IWg9nGhn1OPS3WPSG4eXirWXB34dCuNBmGWkK6sWOrZBvM22hY8rBmLe3G00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LV38J4b9pLC8BaaiIItcAifFAYqkKL0ApapFIynHKaWiLeWlCEHoCE02KWgPnGgEoIMPPQbS3aPmaMhTMYu74mm5gNafG4i0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/DOun3i8m34LtdyBA2Keb5gPKiB2pev1OhKNQLBOBroU5CDb-_ydwNYs8RNC6Oyk4Dvu9XoLEHHHYBl69xhmFXq7nlXxmpJRXIi8bOT-1bCUcXkuIB3Id1z_js-dx6_pnTvdmE9A0RxoAo8hNbAcoVzhe48rVbTEIQhaF)



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
![Diagram](https://www.plantuml.com/plantuml/svg/RP312i8m38RlVOgmwovrKr1F6-xYrOj7gLrWnQwTROglRoTTX-WfuSkVBv36at0KHir8aKPeZHoiWzOf6aOa9PdKLZwWECsb0E7XDctW5SSmeLEsXuepP-_14nIT894oLOPjtgjPm-Vk-3dAcbHZ69I7SwznOMMK9dp1Pq2Vq-KsJ-Ph6U_vFqzazO-xvWk-2hMATnbtrgpf0_-MeEdZkzu0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NO_12i9034Jl-OhGks0hlNYGW5uyzA8V86itb8MuAvkqt--MQf4UNsOcmv2QopQ-12oOC7QiwWPMoEavgc5rJj5o4k5SeLDylEjLkl0KUlwU6w0z51M3ujKB0zKhtpdw40UWmyOoO_ENQ7zyuvx3j6JQZMdviJlDfNX4xym1bOOouWC0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NO-n2i9038RtF4NeAe8zkSL1ChWukAYxn3R8uRMMIohuzbwXdkZuvV_vaf0Q9nkx21Oi2Xv4bM-2EudyWlIuZcfOdQHl9LN8YfUXBkEZD1AU9N10AyWv1iLz6mMeBdnEt6iN3CZzTIPqNtJ-mxCTQEr_AxDrkPrsqgBskC61cxjaUpuqF_C6)



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
![Diagram](https://www.plantuml.com/plantuml/svg/HO_12i8m44Jl-nL3xq9ieGSH2TI3TxrBR8CDfad9Rl4W_NTJAVKqk_jc1bQpc2JJu4cSU8kR6rnueec19HaNXAdriNsXQ1OfO1ZtSO-tanwZJIvsA1Mb-9XOK9oDcDLJabQK1OvnjJADfAljS8c-8rrl-pa6kynQuRWx8JjnmATIWS5BTlx1QgNrd_QvQ2PjGvT_-080)



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
![Diagram](https://www.plantuml.com/plantuml/svg/LKwx2W8n4EptAuRp1-B1DLO16sszoahYPSajh8aaU_Zxfl70OXW6vkMRXMhRIyd4b76Hj6g7SSIDavJSg9RdrWp3B2a77H0Q7kyZUKUT80tNg4n-tFMvYiaIbFpqxrb_xHWTh61oEDnPjNnmsbEOUR4-J9vpxC--)



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
![Diagram](https://www.plantuml.com/plantuml/svg/LS_D2i8m303WUvuYp1UOWy7mL9oWWiB01v2gOGl4ThJfnQUt3ZRc8UI7ZuIOg3PeUWiegn1UaoYFkJXnFqWEZH3y8qN5ugPMgK0RyJvkmPIG4tB4isC5KorzDzX86TJ_amfCiqmEtX4CymqiKJrM9MukltOlYN0txMKh_B7AtgrqDV5wviT0vBBlWdzIZEpwbQqdsyoszS5AjgsGTMa4G-wLl_y2)



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
![Diagram](https://www.plantuml.com/plantuml/svg/FOr12e0m30JlUKNm1LNm7kqJV81KBLA8RJ4HVBxneATbTXQMHCEfry6WIJcYlqJBWTCQEC9P5aDifhJdm0q6mRcs8A_4rhctw2ngkYCBa0FJc0G7eFw74SYs7tcWc3SxV000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/POyn3i8m34NtdEAh9m0azZ2oCC01KD8QY9J4LUnoVjmWO62o_VN-a-n5GzEbPAT9C-74Ik8QnqKKmoNTQyW3Wk0wRvtVE1j8WkEKoVdTzpwCcfwMxF-9QaOep-1RbxoTY3Ho8K7eJJoeaQCwOSMxf_SYgtBvLC-aIwjYDgHL_-DjinzU)



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
![Diagram](https://www.plantuml.com/plantuml/svg/PP51IyCm68Rl-HKVtL64Tcqy397M1Zni1nbJTfCi3JOOav8lPOhutqstjAvwICBxv0rFGahqtFd-NHEll9PGFpx1VO-mbRo1dUC6kV3A6YAq5M-Gr9jr0XpXfSlWg7mBdNJADf2bnDb3ZnwIYh5jx2mdoAfT5M5E3ifmzmd9bYqYAoPMrUiHKeA2XpjbQJg08YoT-f0QINa2Av-ISfY221J2Vd-ALzb4AdecDtyx8HP3RDLh6m_HaMbxF2DA_zK2o2zLEHq9oozK-Ln5vwfYOdFLRorSDhu4Rg_l8AfW1LzBQX2u41BncmnT7OQ7iEajK0gBpP0Vd9Gcr1dt79wvLWqffMd2D_y0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/RP51QyCW5CVlVef7UXwOP6LaXs6Mm0XhwQWzxJ9i8elCQAQ6Rjz-cfckb1r4V-__upr5OXqpRXeaSi993lIbWODXohBM2QrGAtNx0GcjDiy9C0jlOmeduNeOkH6wWmmZeu-JTP1iTxI9JlPNREWk5dDq58gPRqWgkegrMsHRviTc68V2sc-Z-EBI8eAHZq5OwCLxZqXwPgbF7k-kye1PmDVepb1jQqJMPophUez8SUc6SnxFnVzGbuTocRYaiUVDGtWOt8FXdnEtpclvhpOdsPpOKIlBKRYdzCj1Yi5fA32iDe4VvSIzMEbXOAgxy8hPyuEZ-6GuLzxSBoq9Lvt_kny0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/VP51ImCn48Nlyok6_GDk5_PIYiHQaO87eO9uacmpx8RE9fBCAaNwtqsMM4NHGmxllI_XFQAYw23JoB2AScIw1B6ZTVt6wZxe4Ty1SQttXpxuoPbhppxWus25TgC_K0g3xwOeC_URlBFz86kUCdXAfxDEX-D_y6qWSeKUai7P_EF24p7xjna-mUhYt5-OS9U5mOTv39OrKCfM6oswGXtn-MK1fLHrutJ7LEm6L0qfHHjnQvX0DMTzjHVxcfps1v5basLkfHRjfymx4jr-Zx-sDJMAnxR6PNaOxobORq2HC-bZFW00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/TP1D2y8m38Rl_HLXTx6hUd076NwWua5HmQDK6wMmRjfa_dwxwIOYGa_FyoPDaX9hpwNBH4a8HZF2fV1ECqIBHU9SGXG9jfmXJ8FiZ3MXWRrrDhyANvnA2iaT-WVw23J1yHQtU99PpFcDbKZbC94oF152O0cM9iE6neE6RdnnHgAgV-tYFnKrLHKzQCjjFBHgnHRl9H8teZ_uY3FQ1vgl7zJFJ2_Q6LLRGGBpsHww-cORttlDLNiLl98IrYkHOcx2GPy0)



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
