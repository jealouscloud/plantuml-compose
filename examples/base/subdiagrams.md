# Sub-Diagram Embedding

Sub-diagrams let you embed one diagram inside another. This is powerful for adding visual context to notes, messages, and legends without switching between separate diagrams.

**Use cases:**
- **Architectural context in sequence diagrams**: Show system architecture in a note while documenting message flows
- **Visual explanations**: Embed flowcharts or component diagrams in notes to clarify complex logic
- **Rich legends**: Include mini-diagrams in legends to explain symbols or patterns
- **Inline documentation**: Add visual context directly where it's needed

## How It Works

Any diagram builder has an `embed()` method that returns an `EmbeddedDiagram` object. This object can be placed wherever text content is accepted: notes, message labels, legends, etc.

PlantUML renders embedded diagrams using `{{ }}` wrapper syntax. The library handles all the formatting details for you.

## Your First Embedded Diagram

```python
from plantuml_compose import component_diagram, sequence_diagram

# Create an architecture diagram
with component_diagram() as arch:
    api = arch.component("API")
    db = arch.component("Database")
    arch.link(api, db)

# Embed it in a sequence diagram note
with sequence_diagram(title="Request Flow") as d:
    client = d.participant("Client")
    server = d.participant("Server")

    d.message(client, server, "request()")
    d.note(arch.embed(), of=server, position="right")
    d.message(server, client, "response")

print(d.render())
```

## Embedding in Notes

Notes are the most common place for embedded diagrams. They support multi-line content, making them ideal for showing detailed visuals.

### Sequence Diagram Notes

```python
from plantuml_compose import component_diagram, sequence_diagram

# Architecture to embed
with component_diagram() as arch:
    gw = arch.component("Gateway")
    svc = arch.component("Service")
    cache = arch.component("Cache")
    db = arch.component("DB")
    arch.link(gw, svc)
    arch.link(svc, cache)
    arch.link(svc, db)

# Main sequence diagram
with sequence_diagram(title="With Architecture Context") as d:
    user = d.actor("User")
    api = d.participant("API")
    backend = d.participant("Backend")

    d.message(user, api, "login()")
    d.note(arch.embed(), of=api, position="right")
    d.message(api, backend, "authenticate()")
    d.message(backend, api, "token")
    d.message(api, user, "success")

print(d.render())
```

### Activity Diagram Notes

```python
from plantuml_compose import activity_diagram, state_diagram

# State machine to embed
with state_diagram() as states:
    idle = states.state("Idle")
    processing = states.state("Processing")
    done = states.state("Done")
    states.arrow(states.start(), idle)
    states.arrow(idle, processing, label="start")
    states.arrow(processing, done, label="complete")

# Activity with embedded state diagram
with activity_diagram(title="Process With States") as d:
    d.start()
    d.action("Initialize")
    d.note(states.embed(), position="right")
    d.action("Process data")
    d.action("Save results")
    d.stop()

print(d.render())
```

### Component Diagram Notes

```python
from plantuml_compose import component_diagram, activity_diagram

# Workflow to embed
with activity_diagram() as flow:
    flow.start()
    flow.action("Validate input")
    flow.action("Transform data")
    flow.action("Return result")
    flow.stop()

# Component diagram with embedded workflow
with component_diagram(title="Service Architecture") as d:
    api = d.component("REST API")
    processor = d.component("Processor")
    storage = d.component("Storage")

    d.link(api, processor)
    d.link(processor, storage)

    d.note(flow.embed(), target=processor, position="right")

print(d.render())
```

## Embedding in Messages

Sequence message labels use **inline mode** - the embedded diagram appears on a single line using PlantUML's `%breakline()` syntax. This works but produces more compact output.

```python
from plantuml_compose import component_diagram, sequence_diagram

# Simple diagram for inline embedding
with component_diagram() as mini:
    mini.component("Data")

with sequence_diagram() as d:
    a = d.participant("Sender")
    b = d.participant("Receiver")

    # The embedded diagram appears in the message label
    d.message(a, b, mini.embed())

print(d.render())
```

## Embedding in Legends

Legends appear at the edges of diagrams and can contain embedded diagrams for visual explanations.

```python
from plantuml_compose import sequence_diagram, component_diagram
from plantuml_compose.primitives.common import Legend
from dataclasses import replace

# Legend content diagram
with component_diagram() as legend_content:
    legend_content.component("API", stereotype="service")
    legend_content.component("DB", stereotype="database")

# Main diagram
with sequence_diagram(title="API Documentation") as d:
    user = d.actor("User")
    api = d.participant("API")
    db = d.database("Database")

    d.message(user, api, "request")
    d.message(api, db, "query")
    d.message(db, api, "result")
    d.message(api, user, "response")

# Add legend with embedded diagram
diagram = replace(d.build(), legend=Legend(
    content=legend_content.embed(),
    position="right"
))

from plantuml_compose import render
print(render(diagram))
```

## Transparency Options

By default, embedded diagrams have transparent backgrounds so they blend into notes and legends. You can disable this if needed.

### Default (Transparent)

```python
from plantuml_compose import component_diagram, sequence_diagram

with component_diagram() as inner:
    inner.component("Transparent Background")

with sequence_diagram() as d:
    p = d.participant("Demo")
    # Default: transparent=True
    d.note(inner.embed(), of=p, position="right")

print(d.render())
```

### Opaque Background

```python
from plantuml_compose import component_diagram, sequence_diagram

with component_diagram() as inner:
    inner.component("With Background")

with sequence_diagram() as d:
    p = d.participant("Demo")
    # Explicit: transparent=False
    d.note(inner.embed(transparent=False), of=p, position="right")

print(d.render())
```

## Diagram Types You Can Embed

Any diagram type can be embedded, including specialized types like Gantt charts, mind maps, and JSON/YAML visualizations.

### Embed Class Diagram

```python
from plantuml_compose import class_diagram, sequence_diagram

with class_diagram() as model:
    user = model.class_("User")
    order = model.class_("Order")

with sequence_diagram() as d:
    api = d.participant("API")
    d.note(model.embed(), of=api, position="left")

print(d.render())
```

### Embed State Diagram

```python
from plantuml_compose import state_diagram, component_diagram

with state_diagram() as machine:
    a = machine.state("Ready")
    b = machine.state("Running")
    machine.arrow(a, b)

with component_diagram() as d:
    svc = d.component("Service")
    d.note(machine.embed(), target=svc, position="bottom")

print(d.render())
```

### Embed Mind Map

```python
from plantuml_compose import mindmap_diagram, sequence_diagram

with mindmap_diagram() as ideas:
    with ideas.node("Project") as root:
        root.leaf("Phase 1")
        root.leaf("Phase 2")
        root.leaf("Phase 3")

with sequence_diagram() as d:
    pm = d.participant("PM")
    dev = d.participant("Dev")
    d.message(pm, dev, "kickoff")
    d.note(ideas.embed(), of=pm, position="left")

print(d.render())
```

### Embed Gantt Chart

```python
from plantuml_compose import gantt_diagram, sequence_diagram

with gantt_diagram() as schedule:
    t1 = schedule.task("Design", days=5)
    t2 = schedule.task("Build", days=10, after=t1)
    t3 = schedule.task("Test", days=5, after=t2)

with sequence_diagram() as d:
    mgr = d.participant("Manager")
    team = d.participant("Team")
    d.message(mgr, team, "project plan")
    d.note(schedule.embed(), of=mgr, position="right")

print(d.render())
```

## Real-World Example: API Documentation

This example shows how sub-diagrams can enrich API documentation by combining sequence flows with architecture context.

```python
from plantuml_compose import (
    sequence_diagram,
    component_diagram,
    state_diagram
)

# System architecture
with component_diagram() as architecture:
    lb = architecture.component("Load Balancer")
    api1 = architecture.component("API-1")
    api2 = architecture.component("API-2")
    cache = architecture.component("Redis")
    db = architecture.component("PostgreSQL")

    architecture.link(lb, api1)
    architecture.link(lb, api2)
    architecture.link(api1, cache)
    architecture.link(api2, cache)
    architecture.link(api1, db)
    architecture.link(api2, db)

# Request state machine
with state_diagram() as request_states:
    received = request_states.state("Received")
    validated = request_states.state("Validated")
    processed = request_states.state("Processed")
    responded = request_states.state("Responded")

    request_states.arrow(request_states.start(), received)
    request_states.arrow(received, validated)
    request_states.arrow(validated, processed)
    request_states.arrow(processed, responded)

# Main API flow with embedded context
with sequence_diagram(title="User Registration API") as d:
    client = d.actor("Client")
    lb = d.participant("Load Balancer")
    api = d.participant("API Server")
    auth = d.participant("Auth Service")
    db = d.database("Database")

    # Show architecture context at the start
    d.note(architecture.embed(), of=lb, position="right")

    d.message(client, lb, "POST /register")
    d.message(lb, api, "forward request")

    # Show request lifecycle
    d.note(request_states.embed(), of=api, position="left")

    d.message(api, auth, "validate credentials")
    d.message(auth, api, "valid")
    d.message(api, db, "INSERT user")
    d.message(db, api, "created")
    d.message(api, lb, "201 Created")
    d.message(lb, client, "201 Created")

print(d.render())
```

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
| In notes | `d.note(other.embed(), of=participant)` |
| In messages | `d.message(a, b, other.embed())` |
| In legends | `Legend(content=other.embed())` |

Sub-diagrams make your documentation richer and more self-contained. Instead of referencing separate diagrams, you can include visual context exactly where it's needed.
