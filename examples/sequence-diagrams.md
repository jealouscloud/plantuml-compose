# Sequence Diagrams

Sequence diagrams show how multiple entities interact over time. They are ideal for:

- **API request/response flows**: Client -> Server -> Database
- **Object collaboration**: How objects work together in a scenario
- **Protocol exchanges**: Authentication handshakes, message protocols
- **Multi-step processes**: Order processing, user registration flows

Unlike state diagrams (which track ONE entity), sequence diagrams show MULTIPLE participants exchanging messages.

## Quick Start

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram(title="Simple Request")
p = d.participants
e = d.events

client = p.participant("Client")
server = p.participant("Server")
d.add(client, server)

d.phase("Request", [
    e.message(client, server, "GET /data"),
    e.reply(server, client, "200 OK"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGZEp2q0Ka6fXQMfnILS1K39pEJCWiIy4WNddCpKF5IXuDIYijGYhlIY_D82k1u5g4e5NJke0WKh1NVN40NzbCIIHA0qL50NA0zLQQLWP62WuE_DbPgNmkK0980E0W00)



The pattern is:
1. Create a composer with `sequence_diagram()`
2. Get namespace shortcuts: `p = d.participants`, `e = d.events`
3. Create participants with `p.actor()`, `p.participant()`, etc.
4. Register them with `d.add()`
5. Build the timeline with `d.phase()`, `d.if_()`, `d.loop()`, etc.
6. Render with `render(d)`

## Elements

### Participant Types

Different shapes communicate the role of each participant:

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram(title="Participant Types")
p = d.participants
e = d.events

user = p.actor("User")
web = p.participant("Web App")
ctrl = p.control("Controller")
bound = p.boundary("API Gateway")
ent = p.entity("Order")
db = p.database("PostgreSQL")
coll = p.collections("Log Store")
q = p.queue("Task Queue")

d.add(user, web, ctrl, bound, ent, db, coll, q)

d.phase("Request Flow", [
    e.message(user, web, "Browse"),
    e.message(web, ctrl, "Handle"),
    e.message(ctrl, bound, "Route"),
    e.message(bound, ent, "Query"),
    e.message(ent, db, "SELECT"),
    e.message(db, coll, "Log"),
    e.message(coll, q, "Enqueue"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/JP7DReCm48JlVeeLzxv03rNIYFv8I4q2LOze0Ij2SMtNNWlnzXsSfd21dVrc5u_PHU4WwTie6SLeEaAD_UZP2ZMprr5nBoxGPzH1-GqildH7U-yBuaYeMzIgTrQ2CtIulGrcEfVim66cOdzyfrSMFV6SXw3RFwsqnUTd-WW3HWOMxZZYC2xA9UZwL64pjlKoEXkfgDo5QfnAvprGRLRg9-cagMWuNkcqr9aliirINO9BdiuQnYZqOjoaA4UZXwTx27gav-2cg87kBT0r4WnlR0Up63PTU3Q9O3gx98jdsuKfPmJ6YS8CVDC0QrhGkgpAGmEywSBpdnKMrE1h1tYD2bxQV1-usq7jyC1F_WK0)



| Factory | Shape | Use For |
|---------|-------|---------|
| `p.participant(name)` | Rectangle | Services, systems |
| `p.actor(name)` | Stick figure | Human users |
| `p.boundary(name)` | Circle + line | UI or API boundary |
| `p.control(name)` | Circle + arrow | Controller/logic |
| `p.entity(name)` | Circle + underline | Domain objects |
| `p.database(name)` | Cylinder | Databases |
| `p.collections(name)` | Stacked rectangles | Collections/groups |
| `p.queue(name)` | Queue shape | Message queues |

### Participant Options

All participant factories accept the same optional parameters:

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

# ref= provides an alias for long names
api = p.participant("API Gateway Service", ref="api")

# order= controls left-to-right positioning (lower = further left)
db = p.database("Database", order=30)
cache = p.database("Cache", order=20)
client = p.actor("Client", order=10)

d.add(client, cache, db, api)

d.phase("Lookup", [
    e.message(client, api, "Request"),
    e.message(api, cache, "Check cache"),
    e.reply(cache, api, "Miss"),
    e.message(api, db, "Query"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/JK_B2i8m4BpdAmRlXQgt7gHIGGG57r-mfeiDhKtCG-dVcrfRlImxCypiREuyMH_kZI3fjKNHA6uzj2tPOfwAaZnToJ4AaXL_-SKVlncNGLgcmiH09PMXc3DR7tVOakSNTRYmVIh9Cv036ILkLWU3lTPrC0BZwMJLYyXmvaTWvwFIuqWF5J8K5SiQiaUzxSCca-sWdFjvfdePJe5j9xWjHHv7VFaD)



| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Display name |
| `ref=` | `str \| None` | Alias for referencing |
| `style=` | `Style \| None` | Visual style object |
| `order=` | `int \| None` | Left-to-right ordering (lower = further left) |

## Messages

### Basic Messages

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

a = p.participant("A")
b = p.participant("B")
d.add(a, b)

d.phase("Messages", [
    # Solid arrow (synchronous)
    e.message(a, b, "sync call"),

    # Dotted return (reply sugar)
    e.reply(b, a, "response"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LSsn3S0W30J0tbFy0YoG8WBw3868XP28GHYAR1-tQVxrrxpNbURQJwDXNNCTIHR2RqKgi--1YrLJOIKWm9s8EA2lPEJKcc64CmscatLqKIQMcxo57Nm0)



### Message Line Styles and Arrow Heads

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

a = p.participant("A")
b = p.participant("B")
d.add(a, b)

d.phase("Arrow Styles", [
    # line_style: "solid" (default) or "dotted"
    e.message(a, b, "solid + normal", line_style="solid", arrow_head="normal"),
    e.message(a, b, "dotted + thin", line_style="dotted", arrow_head="thin"),
    e.message(a, b, "solid + lost", arrow_head="lost"),
    e.message(a, b, "solid + open", arrow_head="open"),
    e.message(a, b, "solid + circle", arrow_head="circle"),
    e.message(a, b, "no arrowhead", arrow_head="none"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LSyn3iCW30NGdLFylSe5EaGXL-ZQ1O7L83aOWQEsjoyfxS1YotxwahrKTKMFdKrkFVgONLBOOLhDeyYHOKkH9sxwPge6i9XchBYY2iU02vAKtN6NQUuMH9LEr2scN-Wrf5YgThWFUydq3yW0FXRFrEaBIU3EqpPomL0APccblVG1)



| `line_style` | PlantUML | Meaning |
|--------------|----------|---------|
| `"solid"` | `->` | Synchronous message |
| `"dotted"` | `-->` | Asynchronous or return |

| `arrow_head` | PlantUML | Meaning |
|--------------|----------|---------|
| `"normal"` | `>` | Standard filled arrow |
| `"thin"` | `>>` | Thin/async arrow |
| `"lost"` | `>x` | Message lost |
| `"open"` | `\` | Upper half arrow |
| `"circle"` | `>o` | Arrow with circle |
| `"none"` | (no head) | Plain line |

### Bidirectional Messages

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

a = p.participant("A")
b = p.participant("B")
d.add(a, b)

d.phase("Bidirectional", [
    e.message(a, b, "ping/pong", bidirectional=True),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LOn12i0W30JlUSL-eFHUIb5_8YeIq1Xi_7-zzZB3NCQz5gUjtaYtER56CVXV1QfpB4NWpBCauo6n4U1n7my2BYXBFNL8fIAPtCO-VW00)



### Incoming and Outgoing Messages

Messages from/to outside the diagram boundary:

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

server = p.participant("Server")
d.add(server)

d.phase("Boundary Messages", [
    # Message arriving from outside ([->)
    e.incoming(server, "External request"),

    # Message leaving to outside (->])
    e.outgoing(server, "Webhook callback"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/BSqn3eCm30NGtQVm1RW00qAL63jrOAWwc61HH4XIsq5m-tfW-NzuN_gz6edLFKBnNiDQA1c-M0uMM2JNWezSqqnouPDLQM45n7VJtIDiSJYD9L54uLzbDVVRckxZFlBqpNd3G35E53RWD4FluRT_)



### Message Styling

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

a = p.participant("A")
b = p.participant("B")
d.add(a, b)

d.phase("Styled", [
    # style= accepts LineStyleDict for per-message coloring
    e.message(a, b, "important", style={"color": "red", "bold": True}),
    e.message(b, a, "normal", style="#blue"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LOqx2e0m44JxFSM2hLx0Gf9SmL8ieWaIs7nODuMtTorjPXZUWp6tU9QU2PfsEbFpHT3-beEBQs-uoaCn0AB5QHiuXl6e5FPfGOSpfjmgY_egk4yugCSFMeMbSlO4iGGm6lht0W00)



### Activation Shorthand on Messages

The `activation=` parameter adds activation markers inline with a message:

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

client = p.actor("Client")
server = p.participant("Server")
db = p.database("DB")
d.add(client, server, db)

d.phase("With Activation", [
    # "activate" shows activation bar on target (++)
    e.message(client, server, "request", activation="activate"),
    e.message(server, db, "query", activation="activate"),
    # "deactivate" ends activation bar on source (--)
    e.message(db, server, "result", activation="deactivate"),
    e.message(server, client, "response", activation="deactivate"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LSun3i8m343HtQVmNkK23AY4t821sQGMH0f9S9nAlJsXBK8i7lpqBOzLIRGz8v3NB7YEWPD2wSlWGw6aU66PMM0YfHjLHcVXBhaLl0PzuCbhc4b3Je1xZUQuHyE01nH-DQxQULj-sDcLEiZImTbVOypQr1R_a-tsLqjEbO7J16CV_Vyt)



`activation=` values: `"activate"` (++), `"deactivate"` (--), `"create"` (**), `"destroy"` (!!).

### Message Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `source` | `EntityRef \| str` | required | Sender |
| `target` | `EntityRef \| str` | required | Receiver |
| `label` | `str \| None` | `None` | Message text |
| `line_style=` | `"solid" \| "dotted"` | `"solid"` | Line pattern |
| `arrow_head=` | `"normal" \| "thin" \| "lost" \| "open" \| "circle" \| "none"` | `"normal"` | Arrow head type |
| `style=` | `LineStyleLike \| None` | `None` | Color/bold override |
| `bidirectional=` | `bool` | `False` | Two-headed arrow |
| `activation=` | `ActivationAction \| None` | `None` | Inline activation shorthand |

## Events Inside Phases

All events are created from `e = d.events` and placed inside phase/block event lists.

### Lifecycle Events

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

client = p.actor("Client")
server = p.participant("Server")
worker = p.participant("Worker")
d.add(client, server, worker)

d.phase("Lifecycle", [
    e.message(client, server, "start"),

    # Explicit activate/deactivate
    e.activate(server),
    e.message(server, worker, "delegate"),
    e.activate(worker, color="#FFCCCC"),  # colored activation bar

    # Create a participant mid-flow
    e.create(worker),

    e.message(worker, server, "done"),
    e.deactivate(worker),
    e.deactivate(server),

    # Destroy a participant (X on lifeline)
    e.destroy(worker),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/NP2n3i8m34JtV8KbPdw00LMgr8cDWJbAJ1KHaiXrA_NlUq0ABHaivUxvRBaPr8gEpsYiqopKni19JO4ON2WsALrP9fQTTCloWDHB7WjTmftTx28RgkrqFDSkEj5x02paXyaghtcq8e0_UO0zH-u1RVbg7hgknOFZX7yw_XNO3lKvlJ8y_wNijUycdWULFAyG9syQ59nb0G00)



### Return

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

client = p.actor("Client")
server = p.participant("Server")
d.add(client, server)

d.phase("With Return", [
    e.message(client, server, "call()"),
    e.activate(server),
    e.return_("result"),
    e.deactivate(server),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/NOun3i9030Hxls9BAFX02XI97q2HshfOYILpEJc-l1yBXOPcBQzdhHttO8_-Dk8Ic-DXAZMefQb56zV0I_mGfyMttZ1fh7XATA-4ayRjVa8OKDZiSirR_jE3GtvvmB-n77kto7sMVqRgJ6DAzla0)



### Notes Inside Phases

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

a = p.participant("A")
b = p.participant("B")
d.add(a, b)

d.phase("With Notes", [
    # Note over a single participant
    e.note("Starting process", over=a),

    e.message(a, b, "request"),

    # Note over multiple participants
    e.note("Handshake complete", over=[a, b]),

    # Note shapes: "note" (default), "hnote" (hexagonal), "rnote" (rounded)
    e.note("Important!", over=b, shape="hnote"),

    # Positioned note (left/right of last message)
    e.note("Side note", position="left"),

    # Aligned with previous note
    e.note("Aligned note", over=a, aligned=True),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LK-x3i8m3Dpp5SSEOk-0caomi31qZXhJHkH5ulBzk224klXqzfrzxXlRoaiCgWZwqHUR67h3Z9fgNWe6ppEkcQaf80aYlwX2TxYjItoQK6eUgQrpZSC91XqgFHTglBNiOJgSRN9jjW_2c6C9n2IY-QyIoIMMN5b2x7x-G7UMWzxHXqlxkCsYWvyIkU-KabEz57dm3G00)



### Interaction Frames Inside Events

Blocks can be nested inside event lists for inline control flow:

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

client = p.actor("Client")
server = p.participant("Server")
d.add(client, server)

d.phase("Nested Blocks", [
    e.message(client, server, "login"),

    # Inline if/else inside a phase
    e.if_("valid credentials", [
        e.message(server, client, "200 OK"),
    ], "invalid", [
        e.message(server, client, "401 Unauthorized"),
    ]),

    # Inline loop
    e.loop("retry 3 times", [
        e.message(client, server, "ping"),
        e.reply(server, client, "pong"),
    ]),

    # Inline optional
    e.optional("if cached", [
        e.message(server, client, "cached response"),
    ]),

    # Inline parallel
    e.parallel([
        e.message(server, client, "data part 1"),
    ], None, [
        e.message(server, client, "data part 2"),
    ]),

    # Inline break
    e.break_("timeout", [
        e.message(server, client, "504 Timeout"),
    ]),

    # Inline critical
    e.critical("atomic", [
        e.message(client, server, "commit"),
        e.reply(server, client, "ack"),
    ]),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/XP9DJiGm38NtFSMx059d63QpG2DO8i42E819JSTg6aU9EnASdlI72YGg5l4YxtqliPDJDaeszBuYPvfmxuM3LR5iYfD8mV3CwSAfQfCE4O-SZHlSUNLThh3uSNMxs724rrP2aSWRBkIbWKlS59UG7n5yMmkqu4ViwnfF3qLbdnaI9d3BVAXtU0qqs5cJVFBeup1MhngHsD87hc7IytpU7vUC4jfVyJ_peqxYdAdH8EzmvCwyUQDPBKVdmcPUuJB7BQGXer4tx9Qs_tVkr-2tnDHDBUfWM-1DVS3BQfb1bwIyB7cGQIzkQpvE-rviSqBakYLnNATIoXVw0W00)



## Interaction Frames (Top-Level)

These are the same block types as the event-level versions, but registered directly on the composer (`d.if_()`, `d.loop()`, etc.) rather than inside event lists.

### Conditional: `d.if_()`

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

client = p.actor("Client")
api = p.participant("API")
d.add(client, api)

# Alternating label/events pairs after the primary branch
d.if_("authenticated", [
    e.message(api, client, "200 OK"),
], "expired token", [
    e.message(api, client, "401 Refresh"),
], "invalid", [
    e.message(api, client, "403 Forbidden"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/ROwz2W8n48JxFCMyW11_AWiv4GIvGl4DrkpABSRaIFR4npUYvJLJp7mpJ5UDYatFw2XOBZX4bMHkRAO67IaPzfUJesYWoOQMQI0JTlZwMEp-3MonyXxdtaci0dcFMeHX-I5fXjtu9QvoBrA7Nq7JYwBoBBh6CPURChSfIUow9ktn1m00)



### Loop: `d.loop()`

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

sensor = p.participant("Sensor")
controller = p.participant("Controller")
d.add(sensor, controller)

d.loop("every 5 seconds", [
    e.message(sensor, controller, "temperature reading"),
    e.reply(controller, sensor, "ack"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LOun2iD030HxlM8_u3ADYs384_82SIV2aRDqwEH0VXyLBfnc5vOPs6q6Unnxfv7TIXkiWQVeDF-R7gRXrhiuTRC1-OX_SSEKObeduPImt2yiLeJiGvpZS84BrwQlX2_8aiRfhk3o9j5AMqQ--W40)



### Optional: `d.optional()`

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

client = p.actor("Client")
cache = p.database("Cache")
d.add(client, cache)

d.optional("cache hit", [
    e.message(cache, client, "cached data"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKfCBialKd3EoKpDA-5AIIn9J4eiJbLmJapEIENABoXHI0Qn538oIxWK8A8AkdPGvGfM4DaK1P0-hjIy52u7804q5G00)



### Parallel: `d.parallel()`

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

server = p.participant("Server")
db = p.database("DB")
cache = p.database("Cache")
d.add(server, db, cache)

# Multiple parallel branches: primary + alternating label/events
d.parallel([
    e.message(server, db, "query"),
    e.reply(db, server, "result"),
], None, [
    e.message(server, cache, "invalidate"),
    e.reply(cache, server, "ok"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LKx93S903Fox2ZUG1l904T015PXa95OiI_1w8z4z4uY4yl4nbptKC8_so3Apfp7DLa8ly0KkauLThKBFn_zyil66LIswwRGxKA6zlXhyJPXBHsnZUtNKbaEGAtQcRnJvL1RBYHTM-WVk_C-xe4moiF3J3m00)



### Break: `d.break_()`

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

a = p.participant("A")
b = p.participant("B")
d.add(a, b)

d.loop("process items", [
    e.message(a, b, "next item"),
])

d.break_("error occurred", [
    e.message(b, a, "error response"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LOun3iCm30DtlO8Vw0Sw1B5_uZeQZ2QM82b0dbyrdRgG47a2k7eqY_FOITD77zfceFnTbNOHXPfqTiS8Ffo0WiU2YYScNt6dn7EZbt5xWyt48BsVPhmbNRzqIVhN6BlATBvVrfISy040)



### Critical: `d.critical()`

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

app = p.participant("App")
db = p.database("DB")
d.add(app, db)

d.critical("transaction", [
    e.message(app, db, "BEGIN"),
    e.message(app, db, "INSERT"),
    e.message(app, db, "COMMIT"),
    e.reply(db, app, "OK"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/NOux3e0m34Ftd28Nu08CY5-5AWH8m0L2or09IjM6-vEkBBRyxC5rOehytXS4SMTS8C_OX02Mc0vA9_OjcEYaemivaazas3qUCC-mg6I09RPgqFEFwNbJw_w3tJ9DEaD9XS3SbRYCS7eBjOYS-G00)



## Phase Grouping

`d.phase()` creates a labeled visual group around a set of events:

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram(title="Multi-Phase Flow")
p = d.participants
e = d.events

client = p.actor("Client")
api = p.participant("API")
db = p.database("DB")
d.add(client, api, db)

d.phase("Authentication", [
    e.message(client, api, "POST /login"),
    e.message(api, db, "verify credentials"),
    e.reply(db, api, "valid"),
    e.reply(api, client, "token"),
])

d.phase("Data Access", [
    e.message(client, api, "GET /data"),
    e.message(api, db, "SELECT"),
    e.reply(db, api, "rows"),
    e.reply(api, client, "JSON response"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/RP1DZi8m38NtEOKlKB5dWIYqCnh4JwLo0PCQi0X9bRWWRe-3oYmG6o_ytlFxv7aIZ39SdH4MHx0Pd73Hd34H_BXmDsWbH5Ww9Y-cLozRxj4BbCsVwL3maAtLmfnY67ee1pchaoqA1szWJ48nom6OGhDhzp1nuSHPpJkLgeKgDufyV82DrEKBw98QL2d-ipTqtBrJkXrlJq72XRmXtuqKbN91QIsbz0NXjrQ2ZFu1qDRhUhd_B8tXdhvrhjhT5YAbFlX4h-wv3lta4m00)



## Box Grouping

Group participants inside a visual box:

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

user = p.actor("User")
web = p.participant("Web")
api = p.participant("API")
db = p.database("DB")
d.add(user)

# Box groups participants with optional title and color
d.box("Backend Services", api, db, color="#LightBlue")
d.box("Frontend", web)

d.phase("Request", [
    e.message(user, web, "click"),
    e.message(web, api, "fetch"),
    e.message(api, db, "query"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/NOz12i8m44NtESLGrrx0XTHG1C65AE8wdOvji3OrcOZUtXy45su6vl7V7wPEwgBc-sZQyABAEhx9rD59ujEpf8eMUzyFQiSiXcX6rhEVtQIqEUn0EgUkTKceiQQ8QFasRMEO5AJwqoxI_eAEDKGw9uccZo7FT9H7bgHG2gJbkiHfHJnwle6M3H2d0Q-YF02M3R2nOD3Zk_IR6WDlVG00)



Participants inside a `d.box()` are removed from the top-level participant list and placed within the box.

## Notes

### Diagram-Level Notes

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

a = p.participant("A")
b = p.participant("B")
d.add(a, b)

# Note over a participant
d.note("Important service", target=a, position="over")

# Note to the left/right of a participant
d.note("Left side note", target=a, position="left")
d.note("Right side note", target=b, position="right")

# Note across all participants
d.note("System-wide note", across=True)

d.phase("Flow", [
    e.message(a, b, "hello"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/NO_12eCm44Jl-Ohv0NyWXw8U2eMUsYyGNJKGis6pAlvz4uL2UzfPtWpCr4axqNNn9kRhUXUxe6X-ljPCmcl4tVDkW0RL3IqiPlAU3ON115O2RoHeB1vBPD4IJ2IRw-d2daO5ZyNnB3AvWL38XSLDyybRYzUf_mnTBvoInVj8IakrVscT6-G17m00)



### Event-Level Notes

See the "Notes Inside Phases" section above for `e.note()` usage within event lists.

### Note Shapes

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

a = p.participant("A")
d.add(a)

d.phase("Note Shapes", [
    e.note("Standard note", over=a, shape="note"),
    e.note("Hexagonal note", over=a, shape="hnote"),
    e.note("Rounded note", over=a, shape="rnote"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LOun3e0m30FtlYBlO8ADYO6-8A9HGIf95LB4yoa8XYwsx9CbzuUXMjcJozMtPSl81eEBAYN394RWLynqE01-afoaC7JW3JcWXhUjS6teI1T6OKm_rWRFKZZGjoKEhgzIJzm0)



## Divider, Delay, and Space

### Divider

Horizontal line with a centered title, separating sections:

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

a = p.participant("A")
b = p.participant("B")
d.add(a, b)

d.phase("Phase 1", [
    e.message(a, b, "request"),
])

d.divider("Initialization Complete")

d.phase("Phase 2", [
    e.message(b, a, "notify"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LSun3i8m40J0_bwn7w204iaeDXKTNx321KvopiO-5-7r6Beqkzfcj5EpMAslYSfecQL4DVZT2lIikHVSNx4nZWHu72u8EAFoktCpOdsGSxYfcCGadsYI5TUybiJ6S6v7d0OHVeGVX6QJPViBquXnvGi0)



### Delay

Visual pause indicator (`...`):

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

a = p.participant("A")
b = p.participant("B")
d.add(a, b)

d.phase("Start", [
    e.message(a, b, "initiate"),
])

d.delay("5 minutes later")
d.delay()  # no message, just dots

d.phase("Resume", [
    e.message(b, a, "ready"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LOun2iGm30HxlM8_47TfhWYndv1xWRc888WTOyj5VdzokEOQBJliWDQciMfF9nLB-KY9MU7_Mg2ZNhtWFQO4U4mB0bwGB2fHcJZlv9oRaIHtvORJQ3KowC_UkFN4feUXUzChn_r-tDME_V05)



### Space

Explicit vertical spacing:

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

a = p.participant("A")
b = p.participant("B")
d.add(a, b)

d.phase("Spaced", [
    e.message(a, b, "first"),
])

d.space(45)   # 45 pixels of space
d.space()     # default spacing

d.phase("After Space", [
    e.message(b, a, "second"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LSqn3e0W30NGlQVe1TnqSJ305Jm10JGa2WJAriDReejBVtxoNweQsKhzlg18HXUBJOJwrmoSDVU2Ux4kU43KE6reSCKZraOGaWVcUM6Mu6-i3mhr9IBC45f42oxBV10bHnu_)



## Newpage and Ref

### Page Break

Split a long diagram across multiple pages:

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

a = p.participant("A")
b = p.participant("B")
d.add(a, b)

d.phase("Page 1", [
    e.message(a, b, "hello"),
])

d.newpage("Page 2 Title")

d.phase("Page 2", [
    e.message(b, a, "world"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIe0qfd9cGM9UIKAZYWy9wxqelpI0eM0nFHK1KCk1GL71Lqx1IS5AuMCr9oSVAxKl1IklDJo0f0qM8sHGaXcIKugiZOZe3Oda3P7eBRo_AAS5B0s1o01j1m0)



### Reference

Point to another diagram:

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

client = p.actor("Client")
api = p.participant("API")
auth = p.participant("Auth")
d.add(client, api, auth)

d.phase("Main Flow", [
    e.message(client, api, "request"),
])

# Reference spanning multiple participants
d.ref(api, auth, label="See: Authentication Flow Diagram")

d.phase("After Auth", [
    e.message(api, client, "response"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LOzD2W8n34RtFKKEe1UOXSoW22u4mHE4cXa3dRQcgLxVjCx6JSdV-nuTYw9eNOD3hqdW69YYkcn3zfmnAaototzVzUaMIJN35Jd2EQIFWus4_Q41C83Ggr9HH_7XX6P8RvAsslK0ExWJ3RqsZ3qgfryMd1WNmNLpJBCsi4cXHvjXSpL9oIaMwfRH7ll95m00)



## Autonumber

### At Diagram Creation

```python
from plantuml_compose import sequence_diagram, render

# Simple: just enable autonumbering
d = sequence_diagram(autonumber=True)
p = d.participants
e = d.events

a = p.participant("A")
b = p.participant("B")
d.add(a, b)

d.phase("Numbered", [
    e.message(a, b, "first"),
    e.message(b, a, "second"),
    e.message(a, b, "third"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LStB3O0W40JG-rQn3TY01mCKO0y8gvB89ylIlwitBfFCooHZkdYMaH_mGseP-I26ffH2Qhu8sgavkBYEXli_f0Y85fSD7Qvu9kwYu3wm2fr2BTD4xiGHID5ewEiB)



### Custom Autonumber

```python
from plantuml_compose import sequence_diagram, render
from plantuml_compose.primitives.sequence import Autonumber

# Start at 10, increment by 5, with format string
d = sequence_diagram(
    autonumber=Autonumber(start=10, increment=5, format="<b>[000]"),
)
p = d.participants
e = d.events

a = p.participant("A")
b = p.participant("B")
d.add(a, b)

d.phase("Custom Numbers", [
    e.message(a, b, "first"),   # [010]
    e.message(b, a, "second"),  # [015]
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKeiBSdFAyrDIYrIC3HGC5LGiacoYpOmC8XLuYe0AibCpYn8p2jHS4JXEN6b5-MN5YWubnQNvESg-87r5tCfA3WgwDefE2bOAQHb5XMN00MSG0AEG87YrEJyl1IkL21s0190gm40)



### Runtime Autonumber Control

Stop and resume numbering mid-diagram:

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

a = p.participant("A")
b = p.participant("B")
d.add(a, b)

# Start numbering
d.autonumber(start=1)

d.phase("Numbered", [
    e.message(a, b, "first"),
    e.message(b, a, "second"),
])

# Stop numbering
d.autonumber_stop()

d.phase("Unnumbered", [
    e.message(a, b, "no number"),
])

# Resume numbering from where it left off
d.autonumber_resume()

d.phase("Numbered Again", [
    e.message(b, a, "third"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/ROyn3i8m34NtdE9VW86L0JKv01i72AqfaOWJESxzCPIXhJhOrd-I_xU7fb6qvxUhDjEOQcI5twZWOjV2FJz8S7Qpb5vn-qcQ7E1nkYBWWcUIfWR25tW3ZSR2aoEhbKNJKlykT-O37ovOy7vJgFLCkmlWvvXu7Qkl94lgOCsU-m00)



`d.autonumber()` accepts: `start=`, `increment=`, `format=`.

## Activation (Timeline-Level)

In addition to event-level activation (`e.activate()` inside phases), you can use timeline-level methods directly on the composer:

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

client = p.actor("Client")
server = p.participant("Server")
d.add(client, server)

d.phase("Call", [
    e.message(client, server, "request"),
])
d.activate(server, color="#CCFFCC")

d.phase("Process", [
    e.message(server, client, "response"),
])
d.deactivate(server)

# Create and destroy at timeline level
d.create(server)
d.destroy(server)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/NSz12WCn20NGlQSGkku5kYW3mgmBFK58f0JI95KpqDlNAHaeNUhN9ovgGMmy2uHeJP1AvchGlPbZxg4Qtbas5dX86nqfb08un_1ydIbUKFWrM0sufjtAMp0-qXFHkX9DuoOjigepCtPcWZkZlLNbhvFuJu8e_5CbFoZjVPIBx_Wh7m00)



## Layout and Organization

### Hide Unlinked Participants

Remove participants that have no messages:

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram(hide_unlinked=True)
p = d.participants
e = d.events

a = p.participant("Active")
b = p.participant("Also Active")
unused = p.participant("Unused")
d.add(a, b, unused)

d.phase("Only Active", [
    e.message(a, b, "hello"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuSh8J4bLACtBoSpBJatXAW2APYPd5YJcbIWu9fTabgMY22avvXJdGoMK51AB5K3yU2mAG_DAYu76fHVbbnOe-EVbLC9CKu0o57Jja3KhM2bafERav7EbvgLmEG09eDC0)



### Actor Style

Change the visual style of all actors in the diagram:

```python
from plantuml_compose import sequence_diagram, render

# "default" = stick figure, "awesome" = person icon, "hollow" = outline figure
d = sequence_diagram(actor_style="awesome")
p = d.participants
e = d.events

user = p.actor("User")
admin = p.actor("Admin")
api = p.participant("API")
d.add(user, admin, api)

d.phase("Interaction", [
    e.message(user, api, "request"),
    e.message(admin, api, "admin request"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/HOv13i9024Ntd88BU04NfbrsPs8y06c98NQO4PWORozED6u8_FV_3vC7MVIoWzz56naLf3MgNUArCzAJlHQ68U7LsRxhl1LHI7_8AeqqS3ulSBFQ6ouQR6cJge0ZX8VJX-CHZH-TFL8V3Nz0u_nXrWsc7FdO6m00)



## Styling

### Diagram-Wide Styling (`diagram_style=`)

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram(
    title="Styled Sequence",
    diagram_style={
        # Root-level
        "background": "white",
        "font_name": "Arial",
        "font_size": 12,

        # Participant types
        "participant": {
            "background": "#E3F2FD",
            "line_color": "#1976D2",
            "round_corner": 5,
        },
        "actor": {
            "background": "#FFF9C4",
        },
        "database": {
            "background": "#E8F5E9",
            "line_color": "#388E3C",
        },
        "boundary": {"background": "#F3E5F5"},
        "control": {"background": "#FFF3E0"},
        "entity": {"background": "#E0F2F1"},
        "collections": {"background": "#FCE4EC"},
        "queue": {"background": "#F1F8E9"},

        # Messages
        "arrow": {
            "line_color": "#757575",
            "font_size": 10,
            "line_thickness": 1,
        },

        # Lifelines
        "lifeline": {
            "line_color": "#BDBDBD",
        },

        # Notes
        "note": {
            "background": "#FFF9C4",
            "line_color": "#F9A825",
        },

        # Boxes
        "box": {
            "background": "#F5F5F5",
            "line_color": "#9E9E9E",
        },

        # Groups
        "group": {
            "background": "#ECEFF1",
        },

        # Dividers
        "divider": {
            "background": "#CFD8DC",
            "font_style": "bold",
        },

        # References
        "reference": {
            "background": "#E8EAF6",
        },

        # Title
        "title": {
            "font_size": 16,
            "font_style": "bold",
        },

        # Stereotype-based styles
        "stereotypes": {
            "external": {
                "background": "#FFCDD2",
                "font_style": "italic",
            },
        },
    },
)
p = d.participants
e = d.events

client = p.actor("Client")
server = p.participant("Server")
d.add(client, server)

d.phase("Request", [
    e.message(client, server, "GET /data"),
    e.reply(server, client, "200 OK"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/XLJRRjmW47tdAv3wd6PjnnixYg9iCFIXLIjbymC4Jn8K5ZQ0Sscq_rwmsSrDR8LioJDdpendpd3kFBT-M2dafLU0b_v5GO-Ny3205e1ENJIS8PSCdUItbg_mAyBuWelxMsi6tHEZZCLFTz93i3EZ_M--0homagjaMCg_W8ioVAr3GYdacci_qdmb-aOhLh9kzFsI6fArQ8_dNJbQBoUmrM1n7IoRy73X0oh3o1XhoL52NaS7jozPS4LhjgKLeNXhr1xYYiuI5dJeOfQMpi9V5GdQSy-lkOCik64rRJ-te6eQMf5TPKg1yD9ebwsEq2EwnOS93jbyh63Dc2yYbRo1c3M1tnLmqSMJODfu-6_3FuIpTj6KzMuCpzdecaqJ-13TqdXITCIlizqZbErQxI18ZkyH1s5Tqv7HDqerIZvKf_f4OE46R5H_VbXqmUPR7LfhdhvsxhYEPsUzkfFYNeDpk7XBFEx8LapVuTc3rNoFz4YNzk6jREcvacAasA3UY645QS-c1N_zb6sU--qDEZrCopzj5b4oKA7twxi4-mWMJQEuZ5U4yo5uGkA3imJ09_W7lSA7KVF1dOm7mP-G9xYSpV2VdmXqZyx3Arn8_m00)



**`diagram_style=` selectors:**

| Selector | Target | Style Type |
|----------|--------|------------|
| `background` | Diagram background | `ColorLike \| Gradient` |
| `font_name` | Default font | `str` |
| `font_size` | Default font size | `int` |
| `font_color` | Default text color | `ColorLike` |
| `participant` | Participant boxes | `ElementStyleDict` |
| `actor` | Actor shapes | `ElementStyleDict` |
| `boundary` | Boundary participants | `ElementStyleDict` |
| `control` | Control participants | `ElementStyleDict` |
| `entity` | Entity participants | `ElementStyleDict` |
| `database` | Database participants | `ElementStyleDict` |
| `collections` | Collections participants | `ElementStyleDict` |
| `queue` | Queue participants | `ElementStyleDict` |
| `arrow` | Message arrows | `DiagramArrowStyleDict` |
| `lifeline` | Lifelines | `ElementStyleDict` |
| `note` | Notes | `ElementStyleDict` |
| `box` | Participant boxes | `ElementStyleDict` |
| `group` | Group frames | `ElementStyleDict` |
| `divider` | Dividers | `ElementStyleDict` |
| `reference` | Reference frames | `ElementStyleDict` |
| `title` | Diagram title | `ElementStyleDict` |
| `stereotypes` | By stereotype name | `dict[str, ElementStyleDict]` |

## Advanced Features

### Theme Support

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram(title="Themed Sequence", theme="cerulean-outline")
p = d.participants
e = d.events

a = p.actor("User")
b = p.participant("API")
d.add(a, b)

d.phase("Request", [
    e.message(a, b, "GET /"),
    e.reply(b, a, "200"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/7Ox12i8m68Fl_rF41oWEZpl8F8Xu4vqFKBgWXQwTxT_tjzqba7mXP2fgizOro46_N0d7N0DjDAbgy96YNWCnTxZWnLzbT1JhD6My2xDiRS0xlzcek3pkyicfRdZsPb71Ne8vTuOHj-kCOqkxCotTwOZJC0ZZ8bEJzkOF)



### Combining Features

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram(
    title="Authentication Flow",
    autonumber=True,
    actor_style="awesome",
)
p = d.participants
e = d.events

user = p.actor("User")
gateway = p.boundary("Gateway")
auth = p.control("Auth Service")
db = p.database("User DB")
d.add(user)

d.box("Backend", gateway, auth, db, color="#E8F5E9")

d.phase("Login", [
    e.message(user, gateway, "POST /login"),
    e.message(gateway, auth, "authenticate(credentials)"),
    e.activate(auth),
    e.message(auth, db, "findUser(email)"),
    e.reply(db, auth, "user record"),
])

d.if_("user found", [
    e.if_("password valid", [
        e.message(auth, gateway, "JWT token"),
        e.deactivate(auth),
        e.message(gateway, user, "200 + token"),
    ], "invalid", [
        e.message(auth, gateway, "auth failed"),
        e.deactivate(auth),
        e.message(gateway, user, "401 Unauthorized"),
    ]),
], "not found", [
    e.message(auth, gateway, "user not found"),
    e.deactivate(auth),
    e.message(gateway, user, "404 Not Found"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/dPDFImCn4CNl-HJ3UccHOfKAseFKqbOGKQ4j7cLsTrf3iqb9ijtMJ-yazg-r85wMtPStyvjvOJlEe_LbeOINNX7Sb_w3j9SPUcaq39IfX9j9FKUB1M3cZHtw5Hkn8cSA4bXweyiY9IjIiuIaYzcCT9x0MVzcSDs_5G2fANMETWKFwAd25KkPqTuQ1KdWmP3iGcQK0BeumFjQO6EE7bDq1CdOaOLUDvh2-tklAnZ4tPSYpXLLCRMcdCEJcKhDvR6eSRSXGnjUNuOZk53hyutEbdqm-t0N1DKoItduGENgNCKukM3zvx07BRZbUapkDf4w3ryrAb2g-dgoSDOuHfTXQ4kPiNdOKA3otzea11duBCpHkOeTi40bWtYCtotz-3O2R_XUeY-dKmiS11ApQyDLimddssfIV1TI_mKQ4eG9hqlvFx2jvYMCTUXXhFoCBK8MaQ-DtsPncXyZsxUU7k0tV0kUkNOGQmEvmm_-Jxu0)



## Quick Reference

### Diagram Constructor

```text
sequence_diagram(
    title=,            # str | None
    mainframe=,        # str | None
    caption=,          # str | None
    header=,           # str | Header | None
    footer=,           # str | Footer | None
    legend=,           # str | Legend | None
    scale=,            # float | Scale | None
    theme=,            # PlantUMLBuiltinTheme | ExternalTheme | None
    actor_style=,      # "default" | "awesome" | "hollow" | None
    autonumber=,       # bool | Autonumber | None
    hide_unlinked=,    # bool (default False)
    diagram_style=,    # SequenceDiagramStyleDict | SequenceDiagramStyle | None
)
```

### Composer Methods

| Method | Description |
|--------|-------------|
| `d.add(...)` | Register participants |
| `d.phase(label, events)` | Labeled group of events |
| `d.if_(label, events, *branches)` | Alt/else block |
| `d.optional(label, events)` | Opt block |
| `d.loop(label, events)` | Loop block |
| `d.parallel(events, *branches)` | Par block |
| `d.break_(label, events)` | Break block |
| `d.critical(label, events)` | Critical block |
| `d.box(title, *participants, color=)` | Participant box |
| `d.divider(label)` | Horizontal divider |
| `d.delay(message=)` | Delay indicator |
| `d.space(pixels=)` | Vertical spacing |
| `d.ref(*participants, label=)` | Reference frame |
| `d.newpage(title=)` | Page break |
| `d.note(content, target=, position=, across=, aligned=)` | Diagram-level note |
| `d.activate(participant, color=)` | Start activation bar |
| `d.deactivate(participant)` | End activation bar |
| `d.create(participant)` | Create participant mid-flow |
| `d.destroy(participant)` | Destroy participant |
| `d.autonumber(start=, increment=, format=)` | Start numbering |
| `d.autonumber_stop()` | Stop numbering |
| `d.autonumber_resume()` | Resume numbering |
| `render(d)` | Render to PlantUML text |

### Participant Factories (`p = d.participants`)

| Method | Shape |
|--------|-------|
| `p.participant(name, ref=, style=, order=)` | Rectangle |
| `p.actor(name, ref=, style=, order=)` | Stick figure |
| `p.boundary(name, ref=, style=, order=)` | Circle + line |
| `p.control(name, ref=, style=, order=)` | Circle + arrow |
| `p.entity(name, ref=, style=, order=)` | Circle + underline |
| `p.database(name, ref=, style=, order=)` | Cylinder |
| `p.collections(name, ref=, style=, order=)` | Stacked rectangles |
| `p.queue(name, ref=, style=, order=)` | Queue |

### Event Factories (`e = d.events`)

| Method | Description |
|--------|-------------|
| `e.message(src, tgt, label, line_style=, arrow_head=, style=, bidirectional=, activation=)` | Message arrow |
| `e.reply(src, tgt, label)` | Dotted return message |
| `e.incoming(tgt, label, ...)` | Message from outside `[->` |
| `e.outgoing(src, label, ...)` | Message to outside `->]` |
| `e.note(content, over=, position=, shape=, across=, aligned=)` | Note in event list |
| `e.activate(participant, color=)` | Start activation |
| `e.deactivate(participant)` | End activation |
| `e.create(participant)` | Create participant |
| `e.destroy(participant)` | Destroy participant |
| `e.return_(label=)` | Explicit return |
| `e.if_(label, events, *branches)` | Inline alt/else |
| `e.optional(label, events)` | Inline opt |
| `e.loop(label, events)` | Inline loop |
| `e.parallel(events, *branches)` | Inline par |
| `e.break_(label, events)` | Inline break |
| `e.critical(label, events)` | Inline critical |
