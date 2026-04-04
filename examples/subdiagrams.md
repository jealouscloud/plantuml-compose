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
![Diagram](https://www.plantuml.com/plantuml/svg/NL0n3i8m3Dpx2eymLEm8LOKY93O4BmYjXIBIE2Gk25NzEqwQ0SYGM7U-ypbrOELvw4t1cWt26Hy31eQ3eLVXXDAjTieoD4QZvH_eWlw9lhXv6jmiWDm6PPLPM8EVBHTBeIqn0aKyYq7EEAPd4_Xji4gr9s8OOQVQUxItNKE6FB1NDaY4E6AQHQilLKkz8nl9xUduX-mLgwiAc62XeIn_iIaQekrIHYbpVjaaxnGt2U8c_T9Mr7B9ltq0)


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
![Diagram](https://www.plantuml.com/plantuml/svg/NP71RiCW38RlF8MFso7QlPggfgaqxJPfcdP6hjMWKXo1wLP5VVSPcgvjE83vpM_3nog9ZP8FteWJJ_3jf8SsOk-4K78aw3W8_OgnA1pXAr4qWreSki46WVRZ_M6_jhYdi3Mxo7c0DajleBgWMPR3i03FEnUUdbKFB0Hyr6Gf0ph6iIwlIKwUbZMEp09ZBLoAXct7NcyYqOQadKcRdY-cbpiNyc7WK99lLkZ7dcRg9yMZGvgfdSL-hctMLPZAGDCyUAUuo3VpdJYvp-MAogK-MSD2Ge5Cj1IALLBQpQ6sgMokgNzimhg_MIlJ1QICI2cPmdobatxb7m00)


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
![Diagram](https://www.plantuml.com/plantuml/svg/JL3BQWCn3BpxAqIEXT1xAI7fuv1RwEOMIZ1UTMFgM47M1iAo_rufPBU-s9hnp5ZIkeXdwS_9IPI4q21VOq3OS3X5mI0zemjqlb36BB3u-cpsiDbj5-0B63Wgg0Gxfe2b45TS8yI-GpV9ORciT7Dbz2JD90WSkvC0_LHYW67GuxN8BU5AAoOI6E3DXz-EgS_jEoMD4lQvN3pRzwCPdcU73gpPspRX31xvCNSpzQ6jApWyVMjRgqbkrnt_E-05xYlKrueqZKNeg-qXePXz71tc5cmujzPAr_u7)


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
![Diagram](https://www.plantuml.com/plantuml/svg/JP71QiCm44Jl-eebnqBe3vIGfFJGMuX3Bw448MySKLaRLkj0CVxth1miT15lnpCZBzeciIn37unu2GWDyiCxX1sxcnTqCZ0QH_sT8aQ1rV6hES7kyBq2co0F5nqgmu79OKh4bTO8iUtGB7POhojVeImlraY2mBwx2T2rCWECenuVIVu3RfIOI624lNL_7TCGsqyAMYLiOxfRpjTFEV1U4hgmTl_Ou5k58fnouahS5-M8kdpKyVpsg_-sgJCBpdeTBJn_AHKlc3LjKs6Q3COMyfvcgwGly0G0)


![Diagram](https://www.plantuml.com/plantuml/svg/JP31YW8n38RlVOhWNRplog8kUzYREE9LGYUEPJlDaAOBCioxcmueSscIlz-VjDbbHT7IHwT18q53yXyymLxyFIXvBKBESpzmegImElqqPzWVVrU06MfnjM8178KzvSooq1fbmOxS2uVrUi6ziog_qCHA8A6xA_1j0GECentRh8z8NvO9iy881_H_dN19xJT7QwM2AGyeTVnK3PktO_wmnOyBnj2YpGbfAFfPfNErtLXwi0kSfHFP2X88vH9dA2iF5gR9KMgXFjJjBBCLFW40)



### Embedding in State Diagram Notes

State diagrams support embedded diagrams in note parameters. Pass a `Note` object with the embedded content:

```python
from plantuml_compose import state_diagram, component_diagram, render
from plantuml_compose.primitives.common import Note

# Architecture to embed
arch = component_diagram()
el = arch.elements
c = arch.connections
api = el.component("API")
db = el.component("DB")
arch.add(api, db)
arch.connect(c.link(api, db))

# State diagram with embedded architecture in a note
d = state_diagram(title="Service Lifecycle")
sel = d.elements
t = d.transitions

starting = sel.state("Starting",
    note=Note(content=arch.embed(), position="right"),
)
running = sel.state("Running")
d.add(starting, running)
d.connect(
    t.transition("[*]", starting),
    t.transition(starting, running, label="ready"),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LKz12i903BplAt8MnBk8QFKYU10zYeTb6-lYcaYQ2gNqxsQrAbx2p6GcJ1QrUj7cbfn6JGW7b4SC2Djunj26XCuCQdgsHQeSiJ69rKM1ppyPeEjip6fj4yuD2RD21uKFrqgueNB5YGLKFDLtBqWAVGvCled0jpjJNYntcp--BeoQ2EFn6_UzGoeXTndwxHkYtECuEfbh_Yls0IzrSC4K17tPkeLTiT-V)



## Embedding in Messages

Sequence message labels use **inline mode** - the embedded diagram appears on a single line using PlantUML's `%breakline()` syntax. This works but produces more compact output.

```text
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
![Diagram](https://www.plantuml.com/plantuml/svg/LP11YiCm34NtFeKkC7HVGaZRR6Oti-W1D8uePXmhbUL22Rdxo6bQEXiX_y_J_xZBYg9bZ4w3HeB3roVqxCj8IL439nVfGcbm0FDieybwZzJQ9imACnpH_rw4InfE75b01LEUK8o7fGAx5-5vd3XLewOqJIQv1K_jVwy_cZMWuW_cXxSipXfiFT2hfPoDTPQYmOS97nVT4u9-MrmjDi5t8RdRdGh1Hxkcxq7eMYYhwVLjyfCoxxeHB-cDoYM-GUlDLRRwbbWhTZRiH_y0)


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
![Diagram](https://www.plantuml.com/plantuml/svg/JOz12W8n34NtFKMO2tW1aK6zWUwbT88EjabfCugKkRjfPp7D8ldmyn_9cCKcMO8tKUVivcX9u8g1pJFn4k7sugy181O4_c3QFD0gfOrZbf_7KzE9MQ30sRftJTDqOSy995dAoaT5hrleqAKSXyXKpU7URUwK0Mo6pdhiLWEi5OeqjIkD2ZDgqwV-)


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
![Diagram](https://www.plantuml.com/plantuml/svg/HOun3eCm34Ltd-ABaw2A6tJeM4N1WeZ6Ze8f0-BkDM6e1p_hMyzolrgejkKF5MUAgGGn39oLfgfRmNFMdG1HO-YNwxs3rt4qHCr5XTtgNibcF49SBbN63c75bRt_MLFEqy4ojgla0_NU_8aV)


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
![Diagram](https://www.plantuml.com/plantuml/svg/JOv13W8n24NtFGKty0B6ZCxAbMuyGDCICx520upHD7DtcUfYMF3_3td0e1R5vcS9rNLAKuraSBoUmrruhZ0o6Ruj010R0hzG-XIyMkkoL_iKF7Glp0ODJZ4zLfxoo8K5J2Af7q3VlVoWtOPA9Qh2JL4syIBvdvSLGShzXU0c3Dxyvoy0)


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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIe0qfd9cGM9UIKA0RueN9VKCgxqelpI0WNlpEJi_BGqBWMW4WLTEv2CWfL2DbmqBxyaLI6_BBK8P8G245HNvsRcfUGc5e1vMWe1HVbPgSab41wGcv5OdAfWYCerGkKQWxcrjK0gDIy5R0KNaC7b02I03WS0)


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
![Diagram](https://www.plantuml.com/plantuml/svg/RP2n2i8m48RtFiLjJeAjk3X84LV1eLifShGXHD8qvAw2bBwxPqgW1JFaBdy-ld0fYJ7msDlCIpMjyUWOxkXGgx39AeLzfiCmUdXOTCuudK4YON-909p1X-6bMWOla01kO0N3Mv0a1LdJfCN9iQzlYens3I11_UIy0Ol412Vey4CBSXsDxH9H928_h92Onsa8a1VJZa2vRhcl574o7F-z4UEDe5WBvbcA7E94sIyjPPEV-m80)


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
![Diagram](https://www.plantuml.com/plantuml/svg/hLHDJm8n4BtlhvXuDDaW78qXA7eW8OeBUZ66r7R4ngLTsox64FwxizrTs1OE7kG0dJUlRpxBo3fcNBdE4oTTZl1aqK26AscTOKvg1TUpISAuqmR6kKJbae8kI2uBfXoSJJKJSCDofZYQCs0MAcJP8Y6Pf62EPjCmoLpMPaGhtOVdIOuraO1b0oI2EVR6BC9jSqXMHfT5a7G2eBH3qAGT9GJqsMxzpvLrFpaE_TbexM1BbV3FIaw9iSwfPD9JbfAZkc5NN-frRd6zBhJ2lpGYebFjQR_jGl-KTz1w1v4tGo5jXCsqTIk3yyUfTmIX8KqFGKvvwW0LfG8EyfNh2F6SA5nBZE1TrJ5Kmi-2ZlN-G3gCihY4sSDy0JtZ9-Xx5QKvxEmAqT-r-MP6WC6l4gqBfjrPgdyTDRqJ2f4XHxb1qO6UMIvf9mDiPZH7QmCiGql34WtsSlvA7Hk6WgtXFQ7ktlA-K7zlDOhTEF4CEdsikjfvMDJNJHC4k451VP0ih-OUiE9P-3j7mktR9CBaVdwNBQ2qVY9xHwn38PjYGwLuLGONVHZlkKTxqknOoAFwan5zqT_SBm00)


![Diagram](https://www.plantuml.com/plantuml/svg/hLHDQnin4BthLmmv5anY7qinITmU0g5rraakfHXL6ZkYYkH8iox5-BzdLjxTI4eFFVIoZDwyUQFvM5r6ae7QPol8a4LuY1YWmQs952GPx-1gUIEa8XzWOGqw4ZiECChif2Cuk_LImxMqqYaCPo0ZTCXwG4eoIy4Amxvdyd5zEbQqbfuIpoWy4HbOzu3GakHF6H4-zuPmdX22sJuH-4sL7-1muC-dI7yipjaAtXCS-ChgrpRurkc5jrmRL-iYtu8BX6CNS3v6AF-yymx_fTg2pELDfaEXq_U-sU2R5Ru6jOa5ilIHjW5NTxSC5mbXCXd4_uPtmfsxEmwo7LoTaxz8Cf0Ay7WKw3HqtHQdLO39lChx4PRVLlTm7j86SKUgQyspeJDvuyDl6JG4V6anqccI5ZTfaDbw_8SfyfwpTeCApHxr23nAQtYZCcGPlC8OCwJ1o9FG2Vd-uGStPfuB3MR2SxtHJfvSTxHxhJVzlCbPgxh6PJy1jsxVYuCAgBbU8sqK1QTkTegeH8T_YDqtNrTVcdje-G4G8rnhSB9KNAbIxy3iOWgBdlbk0VhLALcNN3G_Ggy0)



### Embed JSON Data

JSON and YAML diagrams use lightweight composers without an `embed()` method. Use `EmbeddedDiagram` directly with the rendered content, specifying `embed_type` so PlantUML uses the correct parser:

```python
from plantuml_compose import (
    json_diagram, sequence_diagram, render, EmbeddedDiagram,
)

# Create JSON content
jd = json_diagram('{"name": "Alice", "role": "admin", "active": true}')
rendered = jd.render()

# Strip @start/@end markers for embedding
lines = rendered.split("\n")
inner = "\n".join(
    line for line in lines
    if not line.strip().startswith("@start") and not line.strip().startswith("@end")
)

embedded_json = EmbeddedDiagram(content=inner, embed_type="json")

# Use in a sequence diagram note
d = sequence_diagram()
p = d.participants
e = d.events

api = p.participant("API")
d.add(api)

d.phase("Context", [
    e.note(embedded_json, over=api),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/9Oun2iCm34LtdK9uxWaw9NJgrYi8HnGNMpAA70eXTw_jQj3_l8y-MdOdyrOorAuffahYkBwUy3Pj5Hygpby7H55dr8DjfjZdF3-xojy6eSBXZc7DANAuOJ3D4z1MaWn0qTCna5lZQvvTGrYsMGxTmD9N_-O7)



The same pattern works for YAML diagrams with `embed_type="yaml"`.

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
| In sequence notes | `e.note(other.embed(), over=participant)` |
| In sequence messages | `e.message(a, b, other.embed())` |
| In state notes | `el.state("Name", note=Note(content=other.embed()))` |
| In component notes | `d.note(other.embed(), target=component)` |
| In legends | `Legend(content=other.embed())` |
| JSON/YAML embedding | `EmbeddedDiagram(content=inner, embed_type="json")` |

Sub-diagrams make your documentation richer and more self-contained. Instead of referencing separate diagrams, you can include visual context exactly where it's needed.
