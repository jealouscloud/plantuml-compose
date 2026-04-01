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
from plantuml_compose import timing_diagram, render

d = timing_diagram(title="Simple Signal")
p = d.participants
e = d.events

signal = p.robust("Data", states=("Idle", "Active"), initial="Idle")
d.add(signal)

d.at(10, e.state(signal, "Active"))
d.at(30, e.state(signal, "Idle"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGZEp2q0K-bvYJbSHVb9fSKb2aekYIM9IWg9nGhn1OPS3WPSG4eXirZ1CoKdbSl14CvtJ2x9B0EA6AEfICrB0Te00000)



The `timing_diagram()` creates a composer. Inside, you:
1. Create participants (signal lines) with `p.robust()`, `p.concise()`, etc.
2. Set states at specific times with `d.at(time, e.state(...))`
3. Optionally add messages, constraints, and highlights

## Participant Types

PlantUML supports six types of participants, each suited to different signal types.

### Robust Participants

Robust participants show complex, multi-state signals with clear state labels:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(title="Robust Signal")
p = d.participants
e = d.events

data = p.robust("DataPath", states=("Idle", "Request", "Processing", "Response"))
d.add(data)

d.at(0, e.state(data, "Idle"))
d.at(10, e.state(data, "Request"))
d.at(20, e.state(data, "Processing"))
d.at(40, e.state(data, "Response"))
d.at(60, e.state(data, "Idle"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGZAJoejBb48papFIypXAeBmb5mIIn834aiob1GIYnNY2mov70ouW9H2Ph62PqfEAfU38PmVb5fOcbfSmkLW11SAACfFJYqkpinBvt8mGL9ON92VLmpKR8PcM6fU2j110000)



### Concise Participants

Concise participants show a simplified, compact view with state names inline:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(title="Concise Signal")
p = d.participants
e = d.events

status = p.concise("Status")
d.add(status)

d.at(0, e.state(status, "Off"))
d.at(5, e.state(status, "Starting"))
d.at(15, e.state(status, "Running"))
d.at(50, e.state(status, "Off"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LN3EpqlEB4vL2CvCpqlCuKg6SfM2In9BIekL51AB5U8B3BaS3BY0b49ciO9_MXgNWocC5mmoBJCldSl142uML9gN1nOoHTMKcfS2j1S0)



### Clock Signals

Clock signals automatically generate periodic waveforms. You specify the period (and optionally pulse width and offset):

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(title="Clock Signal")
p = d.participants

# Basic clock with period of 20 time units
clk = p.clock("Clock", period=20)

# Clock with custom pulse width (high time)
fast_clk = p.clock("FastClock", period=10, pulse=3)

# Clock with offset (phase shift)
delayed_clk = p.clock("DelayedClock", period=20, offset=5)

d.add(clk, fast_clk, delayed_clk)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LN3EoK_ELWZEJCzBpE5A1dEKm69A2ed52l45XWhbcIKP2WMfHPdvAGf61Z0rRed59SZgZ53K6Hee59Jc5ASg6CFKkwJc95QcfY1hCKOpMY4_BQqujKJ1bCiXDIy5w4G0)



### Binary Signals

Binary signals have only two states: high and low. Ideal for digital signals:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(title="Binary Signal")
p = d.participants
e = d.events

enable = p.binary("Enable")
reset = p.binary("Reset")
d.add(enable, reset)

d.at(0, e.state(enable, "low"), e.state(reset, "high"))
d.at(5, e.state(reset, "low"))
d.at(10, e.state(enable, "high"))
d.at(40, e.state(enable, "low"))
d.at(50, e.state(reset, "high"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LN3Ap4iigbG8papFIypXIeBmb5pp4fDoKfKK4eiLuWiCuS91gSMf9L1H8ou70owWf49ciK9EVZcNWo6Scv6Pdi7bO88g3U8P8MHDOLomf2cQR6fU2j290000)



### Analog Signals

Analog signals show continuous value transitions rather than discrete states:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(title="Analog Signal")
p = d.participants
e = d.events

voltage = p.analog("Voltage")
d.add(voltage)

d.at(0, e.state(voltage, "0"))
d.at(10, e.state(voltage, "2.5"))
d.at(20, e.state(voltage, "5"))
d.at(30, e.state(voltage, "3.3"))
d.at(50, e.state(voltage, "0"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LN3CIyp9JrS8pam7ChWI8JobiFoSaiJqL2M5n6A5-093BWS3BY2ba5ciOC3bO0Zd6EcPSZaOmRb0ZZ6SOwndpELWYgmlDIy5Q2y0)



#### Analog Range and Height

Specify the value range and visual height for analog signals:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(title="Analog with Range")
p = d.participants
e = d.events

# Define voltage with explicit range 0-5V and custom height
voltage = p.analog("Voltage", min_value=0, max_value=5, height=100)
d.add(voltage)

d.at(0, e.state(voltage, "0"))
d.at(20, e.state(voltage, "3.3"))
d.at(40, e.state(voltage, "5"))
d.at(60, e.state(voltage, "1.8"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/FSx12i8m40JG-tx5q0yeYRNYSVq53rvbfKiIY6anA_NpMv3cC8StSnck9X_xlZDPigou5Sbpm9eiuYubACc_wHvpDWdQuQMsgXOuI9amGYgUYwSzI1NUEIpffxaYQWhHYDsnEU9Jmz0FnEV6aVZIuFihiPPf_xK1)



#### Analog Tick Marks

Add tick marks to analog signals to show value divisions:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(title="Analog with Ticks")
p = d.participants
e = d.events

voltage = p.analog("Voltage", min_value=0, max_value=10)
d.add(voltage)

# Add tick marks every 2 units
d.ticks(voltage, multiple=2)

d.at(0, e.state(voltage, "0"))
d.at(20, e.state(voltage, "5"))
d.at(40, e.state(voltage, "10"))
d.at(60, e.state(voltage, "2"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/FOx12W8n34Jl-OfXlw1Tr7Fz1_4grGrhiKqNcxA_RrJe8GnlXXaIciQtzf99asR6MMAkA_QaJrpIuzKe_ftfMhF6bIVSMNTcWKEK1TwauRPvieD-Av1UK0MbPqsRZSuKt2zE3Ox2FE18uJ30MtGQP1sMnHxx0000)



### Rectangle Participants

Rectangle participants display states as labeled rectangles, similar to robust but with a different visual style:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(title="Rectangle Signal")
p = d.participants
e = d.events

data = p.rectangle("DataBus")
d.add(data)

d.at(0, e.state(data, "Idle"))
d.at(10, e.state(data, "Address"))
d.at(30, e.state(data, "Data"))
d.at(50, e.state(data, "Idle"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGXAJIv9p4i7ie8pq_CISxYAu09ABeabYKwbnKeAYSKAyGM6N0u6N41A8RDOmJCb9vNBmH3ETqn9AKejBkPoC8OBWJHpEPYYQKdDIm7Q3G00)



## Compact Mode

Compact mode reduces vertical space by displaying states more compactly. You can enable it globally or per-participant.

### Global Compact Mode

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(title="Global Compact", compact_mode=True)
p = d.participants
e = d.events

data = p.robust("Data")
status = p.concise("Status")
d.add(data, status)

d.at(0, e.state(data, "Idle"), e.state(status, "Ready"))
d.at(20, e.state(data, "Active"), e.state(status, "Busy"))
d.at(50, e.state(data, "Idle"), e.state(status, "Ready"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/NOv12W8n34NtEKNe2RJWlgE2kDK3IARDej1EXqagpEtj34N4vNjv7-94QT6Q4-GI67t9Cta5ZPeORwcCbF3IvLB6AehcIae6IV0r7y6NoKTXD4ybhTAz1NU0TiOeU0-9mTal3rxZkvdJNx6XtV315DQ-sCMvojhxtu2dq1x_0000)



### Per-Participant Compact Mode

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(title="Per-Participant Compact")
p = d.participants
e = d.events

# Only this participant is compact
data = p.robust("Data", compact=True)
status = p.concise("Status")
d.add(data, status)

d.at(0, e.state(data, "Idle"), e.state(status, "Ready"))
d.at(20, e.state(data, "Active"), e.state(status, "Busy"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/FOux3W8n34Hxdy9AZmGvGVWqT2iu03A92qlPR1GxIDoUmAweHlFU51FKg5cVCvXOPfouxQP194gbOdXUvahH8Aw9RNbsDNGNCd98Yezw6B94KKPtDxAk6_SGzZ0qYk8rPORW__qOJLwy3lmNt9ZIUrlymAdhw5pI-FO1)



## Time Axis Control

Control whether the time axis is shown and how it behaves.

### Hiding the Time Axis

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(title="Hidden Time Axis", hide_time_axis=True)
p = d.participants
e = d.events

signal = p.robust("Signal")
d.add(signal)

d.at(0, e.state(signal, "A"))
d.at(20, e.state(signal, "B"))
d.at(40, e.state(signal, "A"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuSh8J4bLACdCJTLDhCWivYh9BCb9LV38J4b9pLC80GehE8A4Y_AJIejB59I2CzFp4dEK51AB5U8B3BaS3BY0b49ciO8ZbuCHdEF4vM22B9EQbmAq2W00)



### Manual Time Axis

Use manual time axis when you want full control over time display:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(title="Manual Time Axis", manual_time_axis=True)
p = d.participants
e = d.events

signal = p.robust("Signal")
d.add(signal)

d.at(0, e.state(signal, "Init"))
d.at(100, e.state(signal, "Run"))
d.at(500, e.state(signal, "Stop"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/HSqn2uD038RXFRyYk1TqS4_73brwxXBfKG9tKIuvyETxHT3futsMZyovUCq9CclbX2uvFdWN0nTF4TydJutn-UUoBjKSko0_vTGX6yxR0DH36nJ3bue33Vq5dwf0uzt1rmqewhVT7W00)



## State Ordering

Define the order in which states appear on the vertical axis for robust participants.

### Basic State Order

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(title="State Ordering")
p = d.participants
e = d.events

# Define states in display order (top to bottom) via the states parameter
fsm = p.robust("FSM", states=("Idle", "Ready", "Active", "Done"))
d.add(fsm)

d.at(0, e.state(fsm, "Idle"))
d.at(10, e.state(fsm, "Ready"))
d.at(20, e.state(fsm, "Active"))
d.at(40, e.state(fsm, "Done"))
d.at(50, e.state(fsm, "Idle"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGWkIIn9LV0lIaajoinBvohAJoejBb5GSWlsLL98B5Q8Bp3a0cA5323RCoKdLISeDJ6bKiSnkIIpB5N79JylbSl10AmY4wA0oy4GpWUhvN8mWWj0j74vcC1582QOeXcHcfS2T240)



## Initial States

Set a participant's state before the timeline begins:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(title="Initial States")
p = d.participants
e = d.events

signal = p.robust("Signal", initial="Idle")
enable = p.binary("Enable")
d.add(signal, enable)

# Then show transitions at specific times
d.at(0, e.state(signal, "Active"), e.state(enable, "low"))
d.at(10, e.state(enable, "high"))
d.at(20, e.state(signal, "Processing"))
d.at(40, e.state(enable, "low"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LOv12i9034NtEKNe2QR50umB5zq9FO1asj06ubGcQSNREu8Lt7tUutz-DAVYsrt1nPMnp-92YeEJiq5PqsQEpI1p9csG36-F5f9aAYziBfcIyXTtK1MAOJyfrznzigvFYE4mvz5bPuZTZrpBEhAPv1bY6uxM8lC2yHJ-LZXFzUSR)



## Stereotypes

Add stereotypes to categorize participants (works with robust, concise, binary, and rectangle types):

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(title="Stereotypes")
p = d.participants
e = d.events

# Hardware signals
data = p.robust("DataBus", stereotype="<<hw>>")
enable = p.binary("Enable", stereotype="<<hw>>")

# Software signals
status = p.concise("Status", stereotype="<<sw>>")

d.add(data, enable, status)

d.at(0, e.state(data, "Idle"), e.state(enable, "low"), e.state(status, "Ready"))
d.at(15, e.state(enable, "high"))
d.at(20, e.state(data, "Active"))
d.at(25, e.state(status, "Busy"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LOz12eD034NtEKMO4rJ5dOWjxQBRUe0IDTI1wOnCOiNRTqGgTFd-omz98qfHvxS3jUeOM-N8GTU91MBePb4qLrAwp6AmgiQbhf44drC6dVKKLpGtJvtZVvj37tnlXT6qIhgNvT05D2T8Ez0AtWV7qEG7dtkr7zu7yYrmOO4cAtyusjUussB31zEmfdxv2zAbYTaFwQal)



## State Changes

### Basic State Changes

Set a participant's state at a specific time:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram()
p = d.participants
e = d.events

signal = p.robust("Signal")
d.add(signal)

d.at(0, e.state(signal, "A"))
d.at(20, e.state(signal, "B"))
d.at(40, e.state(signal, "C"))
d.at(60, e.state(signal, "A"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIhAJoejBb5G2ivCpqlCKL98B5Q8Bp3aSZ3W0b8AcSKAZbmEHd2E4vU32PpZpELWXgmiDIy5Q280)



### Colored States

Add color to highlight specific states:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(title="Colored States")
p = d.participants
e = d.events

status = p.robust("Status")
d.add(status)

d.at(0, e.state(status, "Normal", color="LightGreen"))
d.at(20, e.state(status, "Warning", color="Yellow"))
d.at(40, e.state(status, "Error", color="Red"))
d.at(60, e.state(status, "Normal", color="LightGreen"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/VOun2W9134Nxd2BiN415h0CYDcAXXLZ9o8Hr83kH98FNTsssj7fy7dmUUMIBFWb43M7SgwXnmMlaO0VJP_V0uJUx3vWT7-yrq0fcO7KygqrPC9tg-8gZCJUWpM9lsLfj8wOxY-W7QBkeWvaQfWiNeDtVEsvbxli2)



### Intricated States

Intricated states show undefined or transitioning values between two possibilities. This is useful for signals in metastable or don't-care regions:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(title="Intricated States")
p = d.participants
e = d.events

data = p.robust("Data")
d.add(data)

d.at(0, e.state(data, "Valid"))
d.at(20, e.intricated(data, "0", "1"))  # Undefined between 0 and 1
d.at(40, e.state(data, "Valid"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LV3CAodAJ4uiIKrH22u1KiLSHVb9fSKb2aekYIM9IWg9nGhn1OPS3WPSG4eXirWXB34dCuNBmGWkK6sWOrZBvM22hY8rBmLe3G00)



### Hidden States

Hidden states create gaps in the signal, useful for showing time breaks or don't-care regions:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(title="Hidden States")
p = d.participants
e = d.events

signal = p.robust("Signal")
d.add(signal)

d.at(0, e.state(signal, "Active"))
d.at(20, e.hidden(signal, style="-"))  # Dash style
d.at(40, e.state(signal, "Active"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LV38J4b9pLC8BaaiIItcAifFAYqkKL0ApapFIynHKaWiLeWlCEHoCE02KWgPnGgEoIMPPQbS3aPmaMhTMYu74mm5gNafG4i0)



## Messages

Messages show communication between participants at specific times.

### Basic Messages

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(title="Messages")
p = d.participants
e = d.events

controller = p.robust("Controller")
device = p.robust("Device")
d.add(controller, device)

d.at(0,
    e.state(controller, "Idle"),
    e.state(device, "Idle"),
)
d.at(10,
    e.state(controller, "Sending"),
    e.message(controller, device, "data"),
)
d.at(15, e.state(device, "Receiving"))
d.at(30, e.state(controller, "Idle"))
d.at(35, e.state(device, "Idle"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/NO_12i9034Jl-OhGks0hlNYGW5uyzA8V86itb8MuAvkqt--MQf4UNsOcmv2QopQ-12oOC7QiwWPMoEavgc5rJj5o4k5SeLDylEjLkl0KUlwU6w0z51M3ujKB0zKhtpdw40UWmyOoO_ENQ7zyuvx3j6JQZMdviJlDfNX4xym1bOOouWC0)



## Timing Constraints

Constraints annotate timing requirements between two time points on a participant:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(title="Timing Constraints")
p = d.participants
e = d.events

clk = p.clock("Clock", period=20)
data = p.robust("Data")
d.add(clk, data)

d.at(0, e.state(data, "Setup"))
d.at(30, e.state(data, "Hold"))
d.at(60, e.state(data, "Done"))

# Show timing constraint from time 0 to 30
d.constraint(data, start=0, end=30, label="{30ns setup}")

# Show another constraint
d.constraint(data, start=30, end=60, label="{30ns hold}")

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/HO_12i8m44Jl-nL3xq9ieGSH2TI3TxrBR8CDfad9Rl4W_NTJAVKqk_jc1bQpc2JJu4cSU8kR6rnueec19HaNXAdriNsXQ1OfO1ZtSO-tanwZJIvsA1Mb-9XOK9oDcDLJabQK1OvnjJADfAljS8c-8rrl-pa6kynQuRWx8JjnmATIWS5BTlx1QgNrd_QvQ2PjGvT_-080)



## Highlighting Time Regions

Highlight important time periods with colored regions:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(title="Highlighted Regions")
p = d.participants
e = d.events

signal = p.robust("Signal")
d.add(signal)

d.at(0, e.state(signal, "Idle"))
d.at(20, e.state(signal, "Critical"))
d.at(50, e.state(signal, "Idle"))

# Highlight the critical region
d.highlight(start=20, end=50, color="Yellow", caption="Critical Section")

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LKwx2W8n4EptAuRp1-B1DLO16sszoahYPSajh8aaU_Zxfl70OXW6vkMRXMhRIyd4b76Hj6g7SSIDavJSg9RdrWp3B2a77H0Q7kyZUKUT80tNg4n-tFMvYiaIbFpqxrb_xHWTh61oEDnPjNnmsbEOUR4-J9vpxC--)



### Multiple Highlights

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(title="Multiple Highlights")
p = d.participants
e = d.events

state = p.robust("State")
d.add(state)

d.at(0, e.state(state, "Init"))
d.at(20, e.state(state, "Phase1"))
d.at(50, e.state(state, "Phase2"))
d.at(80, e.state(state, "Done"))

d.highlight(start=0, end=20, color="LightBlue", caption="Initialization")
d.highlight(start=20, end=50, color="LightGreen", caption="Processing")
d.highlight(start=50, end=80, color="LightCoral", caption="Cleanup")

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LS_D2i8m303WUvuYp1UOWy7mL9oWWiB01v2gOGl4ThJfnQUt3ZRc8UI7ZuIOg3PeUWiegn1UaoYFkJXnFqWEZH3y8qN5ugPMgK0RyJvkmPIG4tB4isC5KorzDzX86TJ_amfCiqmEtX4CymqiKJrM9MukltOlYN0txMKh_B7AtgrqDV5wviT0vBBlWdzIZEpwbQqdsyoszS5AjgsGTMa4G-wLl_y2)



## Scale

Control how time maps to visual width:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(title="Custom Scale")
p = d.participants
e = d.events

signal = p.robust("Signal")
d.add(signal)

# 100 time units = 200 pixels
d.scale(time_units=100, pixels=200)

d.at(0, e.state(signal, "A"))
d.at(50, e.state(signal, "B"))
d.at(100, e.state(signal, "C"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/FOr12e0m30JlUKNm1LNm7kqJV81KBLA8RJ4HVBxneATbTXQMHCEfry6WIJcYlqJBWTCQEC9P5aDifhJdm0q6mRcs8A_4rhctw2ngkYCBa0FJc0G7eFw74SYs7tcWc3SxV000)



## Complete Example: CPU Bus Transaction

Here's a realistic example showing a CPU bus read transaction:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(title="CPU Bus Read Transaction")
p = d.participants
e = d.events

clk = p.clock("CLK", period=10)
addr = p.robust("ADDR")
data = p.robust("DATA")
rd = p.binary("RD#")
ack = p.binary("ACK#")
d.add(clk, addr, data, rd, ack)

# Scale for readability
d.scale(time_units=100, pixels=400)

# Address phase
d.at(0,
    e.state(addr, "XX"),
    e.state(data, "XX"),
    e.state(rd, "high"),
    e.state(ack, "high"),
)
d.at(10, e.state(addr, "A5"))       # Address valid on clock edge
d.at(15, e.state(rd, "low"))        # Assert read
d.at(35, e.state(data, "D3"))       # Data valid after delay
d.at(40, e.state(ack, "low"))       # Slave acknowledges
d.at(55,
    e.state(rd, "high"),             # Deassert read
    e.state(ack, "high"),
)
d.at(60,
    e.state(addr, "XX"),
    e.state(data, "XX"),
)

# Timing constraints
d.constraint(addr, start=10, end=35, label="{25ns access}")

# Highlight data valid window
d.highlight(start=35, end=55, color="LightGreen", caption="Data Valid")

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/PP51IyCm68Rl-HKVtL64Tcqy397M1Zni1nbJTfCi3JOOav8lPOhutqstjAvwICBxv0rFGahqtFd-NHEll9PGFpx1VO-mbRo1dUC6kV3A6YAq5M-Gr9jr0XpXfSlWg7mBdNJADf2bnDb3ZnwIYh5jx2mdoAfT5M5E3ifmzmd9bYqYAoPMrUiHKeA2XpjbQJg08YoT-f0QINa2Av-ISfY221J2Vd-ALzb4AdecDtyx8HP3RDLh6m_HaMbxF2DA_zK2o2zLEHq9oozK-Ln5vwfYOdFLRorSDhu4Rg_l8AfW1LzBQX2u41BncmnT7OQ7iEajK0gBpP0Vd9Gcr1dt79wvLWqffMd2D_y0)



## Complete Example: SPI Communication

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(title="SPI Transaction")
p = d.participants
e = d.events

sclk = p.clock("SCLK", period=20)
mosi = p.robust("MOSI")
miso = p.robust("MISO")
cs = p.binary("CS#")
d.add(sclk, mosi, miso, cs)

d.scale(time_units=200, pixels=500)

# Initial states
d.at(0,
    e.state(cs, "high"),
    e.state(mosi, "Z"),
    e.state(miso, "Z"),
)

# Chip select and command
d.at(10,
    e.state(cs, "low"),
    e.state(mosi, "CMD"),
)
d.at(50,
    e.state(mosi, "ADDR"),
    e.message(mosi, miso, "request"),
)
d.at(90,
    e.state(mosi, "Z"),
    e.state(miso, "DATA"),
)
d.at(130, e.message(miso, mosi, "response"))
d.at(170,
    e.state(cs, "high"),
    e.state(miso, "Z"),
)

d.highlight(start=10, end=90, color="LightBlue", caption="Command")
d.highlight(start=90, end=170, color="LightGreen", caption="Response")

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/RP51QyCW5CVlVef7UXwOP6LaXs6Mm0XhwQWzxJ9i8elCQAQ6Rjz-cfckb1r4V-__upr5OXqpRXeaSi993lIbWODXohBM2QrGAtNx0GcjDiy9C0jlOmeduNeOkH6wWmmZeu-JTP1iTxI9JlPNREWk5dDq58gPRqWgkegrMsHRviTc68V2sc-Z-EBI8eAHZq5OwCLxZqXwPgbF7k-kye1PmDVepb1jQqJMPophUez8SUc6SnxFnVzGbuTocRYaiUVDGtWOt8FXdnEtpclvhpOdsPpOKIlBKRYdzCj1Yi5fA32iDe4VvSIzMEbXOAgxy8hPyuEZ-6GuLzxSBoq9Lvt_kny0)



## Diagram Styling

Customize the appearance with `diagram_style`:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(
    title="Styled Timing Diagram",
    diagram_style={
        "background": "WhiteSmoke",
        "robust": {"background": "LightBlue"},
        "binary": {"background": "LightGreen"},
        "highlight": {"background": "Yellow"},
    },
)
p = d.participants
e = d.events

data = p.robust("Data")
enable = p.binary("Enable")
d.add(data, enable)

d.at(0, e.state(data, "Idle"), e.state(enable, "low"))
d.at(15, e.state(enable, "high"))
d.at(20, e.state(data, "Active"))
d.at(50, e.state(data, "Idle"))
d.at(55, e.state(enable, "low"))

d.highlight(start=20, end=50, caption="Active Period")

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/VP51ImCn48Nlyok6_GDk5_PIYiHQaO87eO9uacmpx8RE9fBCAaNwtqsMM4NHGmxllI_XFQAYw23JoB2AScIw1B6ZTVt6wZxe4Ty1SQttXpxuoPbhppxWus25TgC_K0g3xwOeC_URlBFz86kUCdXAfxDEX-D_y6qWSeKUai7P_EF24p7xjna-mUhYt5-OS9U5mOTv39OrKCfM6oswGXtn-MK1fLHrutJ7LEm6L0qfHHjnQvX0DMTzjHVxcfps1v5basLkfHRjfymx4jr-Zx-sDJMAnxR6PNaOxobORq2HC-bZFW00)



## Using Date/Time Values

For real-world timing, use date or time strings instead of numeric units:

```python
from plantuml_compose import timing_diagram, render

d = timing_diagram(
    title="Date-Based Timing",
    date_format="HH:mm:ss",
)
p = d.participants
e = d.events

server = p.robust("Server")
client = p.robust("Client")
d.add(server, client)

d.at("09:00:00",
    e.state(server, "Idle"),
    e.state(client, "Waiting"),
)
d.at("09:00:10",
    e.state(client, "Request"),
    e.message(client, server, "GET /api"),
)
d.at("09:00:15", e.state(server, "Processing"))
d.at("09:00:30", e.message(server, client, "200 OK"))
d.at("09:00:45", e.state(client, "Received"))
d.at("09:01:00",
    e.state(server, "Idle"),
    e.state(client, "Idle"),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/TP1D2y8m38Rl_HLXTx6hUd076NwWua5HmQDK6wMmRjfa_dwxwIOYGa_FyoPDaX9hpwNBH4a8HZF2fV1ECqIBHU9SGXG9jfmXJ8FiZ3MXWRrrDhyANvnA2iaT-WVw23J1yHQtU99PpFcDbKZbC94oF152O0cM9iE6neE6RdnnHgAgV-tYFnKrLHKzQCjjFBHgnHRl9H8teZ_uY3FQ1vgl7zJFJ2_Q6LLRGGBpsHww-cORttlDLNiLl98IrYkHOcx2GPy0)



## Quick Reference

| Method | Purpose | Key Parameters |
|--------|---------|----------------|
| `p.robust(name)` | Multi-state signal | `states`, `initial`, `ref`, `stereotype`, `compact` |
| `p.concise(name)` | Simplified signal | `states`, `initial`, `ref`, `stereotype`, `compact` |
| `p.clock(name, period)` | Periodic signal | `period`, `pulse`, `offset`, `ref`, `stereotype` |
| `p.binary(name)` | High/low signal | `ref`, `stereotype`, `compact` |
| `p.analog(name)` | Continuous signal | `min_value`, `max_value`, `height`, `ref` |
| `p.rectangle(name)` | Rectangle-style signal | `states`, `initial`, `ref`, `stereotype`, `compact` |
| `d.at(time, events...)` | Set states at time | `name` (for anchors) |
| `e.state(participant, state)` | State change event | `color` |
| `e.intricated(participant, s1, s2)` | Undefined state event | `color` |
| `e.hidden(participant)` | Gap in signal event | `style` |
| `e.message(src, dst, label)` | Inter-signal message | |
| `d.constraint(participant, start, end, label)` | Timing annotation | |
| `d.highlight(start, end)` | Colored region | `color`, `caption` |
| `d.scale(time_units, pixels)` | Visual scaling | |
| `d.ticks(participant, multiple)` | Analog tick marks | |
