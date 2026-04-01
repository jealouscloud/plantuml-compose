# Sub-Diagram Embedding

Sub-diagrams let you embed one diagram inside another. This is powerful for adding visual context to notes, messages, and legends without switching between separate diagrams.

**Use cases:**
- **Architectural context in sequence diagrams**: Show system architecture in a note while documenting message flows
- **Visual explanations**: Embed flowcharts or component diagrams in notes to clarify complex logic
- **Rich legends**: Include mini-diagrams in legends to explain symbols or patterns
- **Inline documentation**: Add visual context directly where it's needed

## How It Works

Any diagram composer has an `embed()` method that returns an `EmbeddedDiagram` object. This object can be placed wherever text content is accepted: notes, message labels, legends, etc.

PlantUML renders embedded diagrams using `{{ }}` wrapper syntax. The library handles all the formatting details for you.

## Your First Embedded Diagram

```python
from plantuml_compose import component_diagram, sequence_diagram, render

# Create an architecture diagram
arch = component_diagram()
el = arch.elements
c = arch.connections

api = el.component("API")
db = el.component("Database")
arch.add(api, db)
arch.connect(c.link(api, db))

# Embed it in a sequence diagram note
d = sequence_diagram(title="Request Flow")
p = d.participants
e = d.events

client = p.participant("Client")
server = p.participant("Server")
d.add(client, server)

d.phase("Flow", [
    e.message(client, server, "request()"),
    e.note(arch.embed(), over=server),
    e.message(server, client, "response"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LL3D2i8m3BxtANBKm_0kCgOJmPle4zGjQh4sCyqK6NjtKpP5BwNz_lAbHHJBqjwy4ISUOO_t5gF0njFJD4gvoZKs29JUOP0_w83yG3O30ra-0Z077b8cKnD84DYTBm9q-ZW0kawFHPINnrnlJ2JGmSfMrpDJ6-gIF348sn1rOehlas7sTLHqQoWaOhdR_htNLkpHHbHGASYoNwJl3OOQKYipjjNUumQfTzGKLHQgqazv0m00)



## Embedding in Notes

Notes are the most common place for embedded diagrams. They support multi-line content, making them ideal for showing detailed visuals.

### Sequence Diagram Notes

```python
from plantuml_compose import component_diagram, sequence_diagram, render

# Architecture to embed
arch = component_diagram()
el = arch.elements
c = arch.connections

gw = el.component("Gateway")
svc = el.component("Service")
cache = el.component("Cache")
db = el.component("DB")
arch.add(gw, svc, cache, db)
arch.connect(
    c.link(gw, svc),
    c.link(svc, cache),
    c.link(svc, db),
)

# Main sequence diagram
d = sequence_diagram(title="With Architecture Context")
p = d.participants
e = d.events

user = p.actor("User")
api = p.participant("API")
backend = p.participant("Backend")
d.add(user, api, backend)

d.phase("Auth", [
    e.message(user, api, "login()"),
    e.note(arch.embed(), over=api),
    e.message(api, backend, "authenticate()"),
    e.message(backend, api, "token"),
    e.message(api, user, "success"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LP71QiCm38RlVWeTrqFOlOpIDeFHss2KdOsgnMQk5MnvMmbvzyaXASt5IB_qIVpoFejDKgx1Y9T0yEd5mI6Xyq8e9H6q78N-n5WKJd3Eb4olY4VVsoXmU3-jygF5RueNKnkXsTKwR25mv-FJnaGMWkGx9y1V4mim3FgyPBa5sccKc0M6QKwNkCHBoq4NIx8nwoBI7MC5dky4yhNdM0jlLkZNtbRQ1wKVZxJIMejkhRmUDPrnQ9e7Qewgk60FqiIDer7BKCsPwbTjpsTGwxQ8qmqUTRXUO2dSJoEi-O9DLzj2BeYKizbhf_xDFm00)



### State Diagram in Component Notes

```python
from plantuml_compose import state_diagram, component_diagram, render

# State machine to embed
states = state_diagram()
sel = states.elements
t = states.transitions

idle = sel.state("Idle")
processing = sel.state("Processing")
done = sel.state("Done")
states.add(idle, processing, done)
states.connect(
    t.transition("[*]", idle),
    t.transition(idle, processing, label="start"),
    t.transition(processing, done, label="complete"),
)

# Component diagram with embedded state machine
d = component_diagram(title="Service Architecture")
el = d.elements
c = d.connections

api = el.component("REST API")
processor = el.component("Processor")
storage = el.component("Storage")
d.add(api, processor, storage)
d.connect(
    c.link(api, processor),
    c.link(processor, storage),
)

d.note(states.embed(), target=processor, position="right")

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/JP31YW8n38RlVOhWNRplog8kUzYREE9LGYUEPJlDaAOBCioxcmueSscIlz-VjDbbHT7IHwT18q53yXyymLxyFIXvBKBESpzmegImElqqPzWVVrU06MfnjM8178KzvSooq1fbmOxS2uVrUi6ziog_qCHA8A6xA_1j0GECentRh8z8NvO9iy881_H_dN19xJT7QwM2AGyeTVnK3PktO_wmnOyBnj2YpGbfAFfPfNErtLXwi0kSfHFP2X88vH9dA2iF5gR9KMgXFjJjBBCLFW40)



### Component Diagram Notes

```python
from plantuml_compose import component_diagram, state_diagram, render

# State machine to embed as workflow
flow = state_diagram()
sel = flow.elements
t = flow.transitions

validate = sel.state("Validate")
transform = sel.state("Transform")
result = sel.state("Return")
flow.add(validate, transform, result)
flow.connect(
    t.transition("[*]", validate),
    t.transition(validate, transform),
    t.transition(transform, result),
    t.transition(result, "[*]"),
)

# Component diagram with embedded workflow
d = component_diagram(title="Service Architecture")
el = d.elements
c = d.connections

api = el.component("REST API")
processor = el.component("Processor")
storage = el.component("Storage")
d.add(api, processor, storage)
d.connect(
    c.link(api, processor),
    c.link(processor, storage),
)

d.note(flow.embed(), target=processor, position="right")

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/JP31YW8n38RlVOhWNRplog8kUzYREE9LGYUEPJlDaAOBCioxcmueSscIlz-VjDbbHT7IHwT18q53yXyymLxyFIXvBKBESpzmegImElqqPzWVVrU06MfnjM8178KzvSooq1fbmOxS2uVrUi6ziog_qCHA8A6xA_1j0GECentRh8z8NvO9iy881_H_dN19xJT7QwM2AGyeTVnK3PktO_wmnOyBnj2YpGbfAFfPfNErtLXwi0kSfHFP2X88vH9dA2iF5gR9KMgXFjJjBBCLFW40)



## Embedding in Messages

Sequence message labels use **inline mode** - the embedded diagram appears on a single line using PlantUML's `%breakline()` syntax. This works but produces more compact output.

```python
from plantuml_compose import component_diagram, sequence_diagram, render

# Simple diagram for inline embedding
mini = component_diagram()
el = mini.elements
mini.add(el.component("Data"))

d = sequence_diagram()
p = d.participants
e = d.events

a = p.participant("Sender")
b = p.participant("Receiver")
d.add(a, b)

# The embedded diagram appears in the message label
d.phase("Transfer", [
    e.message(a, b, mini.embed()),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/ROv12i9034NtFKKsWYx4lPHIr1Fe2U8qoD1fCcHIGShStOWW55nzU3zv_BuOgirJQh9d334Z6zo81z8LkbAW-7JuxM3V_H0SOLdQOgz47MpkIZYcoBJTWOeOB732C3vKPXxEaaJ15BcudDnRrn_juPydo9I5F-SNDAorwNs4Ztu3)



## Embedding in Legends

Legends appear at the edges of diagrams and can contain embedded diagrams for visual explanations.

```python
from plantuml_compose import sequence_diagram, component_diagram, render
from plantuml_compose.primitives.common import Legend
from dataclasses import replace

# Legend content diagram
legend_content = component_diagram()
el = legend_content.elements
legend_content.add(
    el.component("API", stereotype="service"),
    el.component("DB", stereotype="database"),
)

# Main diagram
d = sequence_diagram(title="API Documentation")
p = d.participants
e = d.events

user = p.actor("User")
api = p.participant("API")
db = p.database("Database")
d.add(user, api, db)

d.phase("Query", [
    e.message(user, api, "request"),
    e.message(api, db, "query"),
    e.message(db, api, "result"),
    e.message(api, user, "response"),
])

# Add legend with embedded diagram
diagram = replace(d.build(), legend=Legend(
    content=legend_content.embed(),
    position="right"
))

print(render(diagram))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LP0nRiCm34Ltde8NAB8NXf6aNhfrwG5OcGY4og9BKG42mtSlvIH6kmZK_thy7peM8xKw9R1eYV7qyOw3X3fnDh8e6H9VE8-0k2n-TCLkYNkVLCHmmJE5xujApUER954qfLncKkTnRS1X9u9Ci-Hcj9IkAwpN6BZ_xmrdjqOo-g9ozzOLlC6Z1mNpb4zdmLCiXZZJVICy8HmU0xHd-D9lUQ-e_5Ev6BIRYyzNxhYkDzY5FqIfQGUsRPleLNtxqVlup_q2)



## Transparency Options

By default, embedded diagrams have transparent backgrounds so they blend into notes and legends. You can disable this if needed.

### Default (Transparent)

```python
from plantuml_compose import component_diagram, sequence_diagram, render

inner = component_diagram()
el = inner.elements
inner.add(el.component("Transparent Background"))

d = sequence_diagram()
p = d.participants
e = d.events

participant = p.participant("Demo")
d.add(participant)

# Default: transparent=True
d.phase("Show", [
    e.note(inner.embed(), over=participant),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/JOv12iCm30JlVeN81_A1KaBJ9_HUZEEcfhPaPELGZFyUcKAJYxHejSDEHIpBbgB9keCBsQB0tISoIEA1m_eMeDVl152hZakHR_HNLKmaKE5ctMTbsd2PAHA3iCMYGA-irWFZF-4ePS9k38_Jrq4Om1OuMS_3qdXhnkC2lPkPL6dp7G00)



### Opaque Background

```python
from plantuml_compose import component_diagram, sequence_diagram, render

inner = component_diagram()
el = inner.elements
inner.add(el.component("With Background"))

d = sequence_diagram()
p = d.participants
e = d.events

participant = p.participant("Demo")
d.add(participant)

# Explicit: transparent=False
d.phase("Show", [
    e.note(inner.embed(transparent=False), over=participant),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/HOt13e0W34FlV4NZbnZZFtWq1568iX4S9-A_E-B1IzkyTEjuYorIqsMoUdGnMnBCFh4X5eyIZo3W_KD0QogEKsRoMXoMA06JTUTHkD8smDxeRFsP7ZoFyRIXVpIZ9jrx0G00)



## Diagram Types You Can Embed

Any diagram type can be embedded, including specialized types like Gantt charts, mind maps, and JSON/YAML visualizations.

### Embed Class Diagram

```python
from plantuml_compose import class_diagram, sequence_diagram, render

model = class_diagram()
el = model.elements
model.add(
    el.class_("User"),
    el.class_("Order"),
)

d = sequence_diagram()
p = d.participants
e = d.events

api = p.participant("API")
d.add(api)

d.phase("Context", [
    e.note(model.embed(), over=api, position="left"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/FKux3i8m3Drp2j-02o1KO6A2XGD4YOigZ5tPxe2YtBrkXoxlO-czvy4ygoy_IdFmLAOviyFrzKWiZa0uEiYu7m1Q2pYR_maleLJ4eS4jb-z7PU5w5n85rymMRHX5VGkSZaIXR0PlGptCK-lkUa_85RRLD8IAbrO0)



### Embed State Diagram

```python
from plantuml_compose import state_diagram, component_diagram, render

machine = state_diagram()
el = machine.elements
t = machine.transitions

a = el.state("Ready")
b = el.state("Running")
machine.add(a, b)
machine.connect(t.transition(a, b))

d = component_diagram()
cel = d.elements
svc = cel.component("Service")
d.add(svc)
d.note(machine.embed(), target=svc, position="bottom")

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/JOxH2SCm34J_FOKM25sWXD1kq4xWsce8jQKWAuLWl7lbVgJz4NSFxdHJKI-wvUG2vvK9IU6Eybu2Ec95UB0gP-3dWG5gjNCkkYSSJGcpGeMB3wzPUADuvSG2AfxAwgLNjXuu7GbxQjKtz77_kOreeTdybyCmZ7-iDOSKeKzoaobR_040)



### Embed Mind Map

```python
from plantuml_compose import mindmap_diagram, sequence_diagram, render

ideas = mindmap_diagram()
n = ideas.nodes
ideas.add(n.node("Project",
    n.leaf("Phase 1"),
    n.leaf("Phase 2"),
    n.leaf("Phase 3"),
))

d = sequence_diagram()
p = d.participants
e = d.events

pm = p.participant("PM")
dev = p.participant("Dev")
d.add(pm, dev)

d.phase("Kickoff", [
    e.message(pm, dev, "kickoff"),
    e.note(ideas.embed(), over=pm, position="left"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LO_12i8m38RlVOgS1H7r9ZA6UXti5KgNQbtNZ3OJPEpTJJmClIJ_H_Z_97LXctaQeXcb1nT6cnZQvWzl-39j0zjA5PoW3wudxqqYHeZe6SYh1s2UfPmBloDMeZ8HmmmNw_fxfYbrLugKWRDDHHQWP2zgsAsE-dlF458ts55u0ssc9pfMBV2m1M7_2uTVE6e4YdaDM1OZ37ggqOcy-W40)



### Embed Gantt Chart

```python
from plantuml_compose import gantt_diagram, sequence_diagram, render

schedule = gantt_diagram()
tk = schedule.tasks
dep = schedule.dependencies

t1 = tk.task("Design", days=5)
t2 = tk.task("Build", days=10)
t3 = tk.task("Test", days=5)
schedule.add(t1, t2, t3)
schedule.connect(
    dep.after(t2, t1),
    dep.after(t3, t2),
)

d = sequence_diagram()
p = d.participants
e = d.events

mgr = p.participant("Manager")
team = p.participant("Team")
d.add(mgr, team)

d.phase("Planning", [
    e.message(mgr, team, "project plan"),
    e.note(schedule.embed(), over=mgr),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/PL2nJiCm4Dtz5MzZgg15NH2geiBArgsgq2annjIr8zzbgAByEsT3WYeMdzzxzzwThc6XBCCbc5whRtrFKV16aPpDDzp1qiNy2bZjAiOJ-fo-R2le0qKJarXaxpu5wMD90SPHdsUMQx0x_UMK12Fsr9vTJaFiNb986P8fiewqEcqgXll5qTGrdUuXYewlbhsB9n3Z-2xh4mAnCBRewCgbOJ_uqCtwPjRN3qj3PMieW-GdvOvXOrVKWsMPtO__qojvOzxycHijywBJP1IXdCKKNk_y3G00)



## Real-World Example: API Documentation

This example shows how sub-diagrams can enrich API documentation by combining sequence flows with architecture context.

```python
from plantuml_compose import (
    sequence_diagram,
    component_diagram,
    state_diagram,
    render,
)

# System architecture
architecture = component_diagram()
el = architecture.elements
c = architecture.connections

lb = el.component("Load Balancer")
api1 = el.component("API-1")
api2 = el.component("API-2")
cache = el.component("Redis")
db = el.component("PostgreSQL")
architecture.add(lb, api1, api2, cache, db)
architecture.connect(
    c.link(lb, api1),
    c.link(lb, api2),
    c.link(api1, cache),
    c.link(api2, cache),
    c.link(api1, db),
    c.link(api2, db),
)

# Request state machine
request_states = state_diagram()
sel = request_states.elements
t = request_states.transitions

received = sel.state("Received")
validated = sel.state("Validated")
processed = sel.state("Processed")
responded = sel.state("Responded")
request_states.add(received, validated, processed, responded)
request_states.connect(
    t.transition("[*]", received),
    t.transition(received, validated),
    t.transition(validated, processed),
    t.transition(processed, responded),
)

# Main API flow with embedded context
d = sequence_diagram(title="User Registration API")
p = d.participants
e = d.events

client = p.actor("Client")
lb_p = p.participant("Load Balancer")
api = p.participant("API Server")
auth = p.participant("Auth Service")
db_p = p.database("Database")
d.add(client, lb_p, api, auth, db_p)

# Show architecture context at the start
d.phase("Registration", [
    e.note(architecture.embed(), over=lb_p),
    e.message(client, lb_p, "POST /register"),
    e.message(lb_p, api, "forward request"),
    e.note(request_states.embed(), over=api, position="left"),
    e.message(api, auth, "validate credentials"),
    e.message(auth, api, "valid"),
    e.message(api, db_p, "INSERT user"),
    e.message(db_p, api, "created"),
    e.message(api, lb_p, "201 Created"),
    e.message(lb_p, client, "201 Created"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/hLHDQnin4BthLmmv5anY7qinITmU0g5rraakfHXL6ZkYYkH8iox5-BzdLjxTI4eFFVIoZDwyUQFvM5r6ae7QPol8a4LuY1YWmQs952GPx-1gUIEa8XzWOGqw4ZiECChif2Cuk_LImxMqqYaCPo0ZTCXwG4eoIy4Amxvdyd5zEbQqbfuIpoWy4HbOzu3GakHF6H4-zuPmdX22sJuH-4sL7-1muC-dI7yipjaAtXCS-ChgrpRurkc5jrmRL-iYtu8BX6CNS3v6AF-yymx_fTg2pELDfaEXq_U-sU2R5Ru6jOa5ilIHjW5NTxSC5mbXCXd4_uPtmfsxEmwo7LoTaxz8Cf0Ay7WKw3HqtHQdLO39lChx4PRVLlTm7j86SKUgQyspeJDvuyDl6JG4V6anqccI5ZTfaDbw_8SfyfwpTeCApHxr23nAQtYZCcGPlC8OCwJ1o9FG2Vd-uGStPfuB3MR2SxtHJfvSTxHxhJVzlCbPgxh6PJy1jsxVYuCAgBbU8sqK1QTkTegeH8T_YDqtNrTVcdje-G4G8rnhSB9KNAbIxy3iOWgBdlbk0VhLALcNN3G_Ggy0)



## Working with EmbeddedDiagram Directly

For advanced use cases, you can work with `EmbeddedDiagram` directly. This is useful when you have raw PlantUML content that wasn't built using the library.

```python
from plantuml_compose import EmbeddedDiagram

# Create an embedded diagram from raw PlantUML content
embedded = EmbeddedDiagram(
    content="component API\ncomponent DB\nAPI --> DB",
    transparent=True
)

# Render for multi-line context (notes, legends)
multiline_output = embedded.render(inline=False)

# Render for inline context (message labels)
inline_output = embedded.render(inline=True)
```

The multi-line format (for notes, legends) produces:

```text
{{
<style>root { BackgroundColor transparent }</style>
component API
component DB
API --> DB
}}
```

The inline format (for message labels) produces:

```text
{{<style>root { BackgroundColor transparent }</style> %breakline() component API %breakline() component DB %breakline() API --> DB}}
```

## Summary

| Feature | Usage |
|---------|-------|
| Basic embedding | `diagram.embed()` |
| Opaque background | `diagram.embed(transparent=False)` |
| In notes | `e.note(other.embed(), over=participant)` |
| In messages | `e.message(a, b, other.embed())` |
| In legends | `Legend(content=other.embed())` |

Sub-diagrams make your documentation richer and more self-contained. Instead of referencing separate diagrams, you can include visual context exactly where it's needed.
