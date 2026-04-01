# plantuml-compose

A Python library that makes creating PlantUML diagrams intuitive and type-safe.

## Why plantuml-compose?

PlantUML is powerful but its text syntax can be cryptic. What does `A -[#red,dashed]-> B` mean? What options are available for a state transition?

plantuml-compose solves this by providing:

- **Discoverable APIs**: Use your IDE's autocomplete to explore options
- **Type safety**: Catch errors before rendering, not after
- **Pure factory functions**: Compose diagrams declaratively with nesting
- **Comprehensive documentation**: Each diagram type explains *when* and *why* to use it

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram(title="Simple API Call")
p = d.participants
e = d.events

client = p.participant("Client")
server = p.participant("Server")
d.add(client, server)

d.phase("Request", [
    e.message(client, server, "GET /users"),
    e.reply(server, client, "200 OK"),
])

print(render(d))
```

## Installation

```bash
pip install plantuml-compose
```

Requires Python 3.13+.

## Supported Diagram Types

### Behavioral Diagrams

| Type | Use When | Guide |
|------|----------|-------|
| [**Sequence**](examples/sequence-diagrams.md) | Showing how multiple entities interact over time | API flows, protocols, object collaboration |
| [**State**](examples/state-diagrams.md) | Tracking one entity through its lifecycle | Order status, UI states, workflows |
| [**Activity**](examples/activity-diagrams.md) | Modeling process flow with decisions and parallelism | Business processes, algorithms |
| [**Use Case**](examples/usecase-diagrams.md) | Defining system boundaries and actor goals | Requirements, feature scoping |
| [**Timing**](examples/timing-diagrams.md) | Showing state changes against a time axis | Hardware signals, protocol timing |

### Structural Diagrams

| Type | Use When | Guide |
|------|----------|-------|
| [**Class**](examples/class-diagrams.md) | Documenting types, attributes, and relationships | Domain models, API types |
| [**Object**](examples/object-diagrams.md) | Showing specific instances and their values | Test scenarios, example data |
| [**Component**](examples/component-diagrams.md) | Illustrating system architecture | Services, modules, dependencies |
| [**Deployment**](examples/deployment-diagrams.md) | Mapping software to infrastructure | Servers, containers, cloud resources |
| [**Network**](examples/network-diagrams.md) | Visualizing network topology | IP addressing, network segments |

### Hierarchical Diagrams

| Type | Use When | Guide |
|------|----------|-------|
| [**Mind Map**](examples/mindmap-diagrams.md) | Brainstorming and organizing ideas | Feature planning, concept exploration |
| [**WBS**](examples/wbs-diagrams.md) | Breaking down work into deliverables | Project planning, task decomposition |
| [**Gantt**](examples/gantt-diagrams.md) | Scheduling tasks with dependencies | Project timelines, sprint planning |

### Advanced Features

| Feature | Description | Guide |
|---------|-------------|-------|
| [**Sub-diagrams**](examples/subdiagrams.md) | Embed diagrams inside notes and messages | Rich annotations, inline architecture |

## Quick Examples

### State Machine

```python
from plantuml_compose import state_diagram, render

d = state_diagram(title="Order Lifecycle")
el = d.elements
t = d.transitions

pending = el.state("Pending")
paid = el.state("Paid")
shipped = el.state("Shipped")
delivered = el.state("Delivered")

d.add(pending, paid, shipped, delivered)

d.connect(
    t.transition(el.initial(), pending),
    t.transition(pending, paid, label="payment received"),
    t.transition(paid, shipped, label="items packed"),
    t.transition(shipped, delivered, label="customer signs"),
    t.transition(delivered, el.final()),
)

print(render(d))
```

### Class Relationships

```python
from plantuml_compose import class_diagram, render

d = class_diagram(title="E-commerce Model")
el = d.elements
r = d.relationships

user = el.class_("User", members=(
    el.field("id", "int"),
    el.field("email", "str"),
))
order = el.class_("Order", members=(el.field("total", "Decimal"),))
item = el.class_("LineItem", members=(el.field("quantity", "int"),))

d.add(user, order, item)

d.connect(
    r.has(user, order, part_label="*"),
    r.contains(order, item, part_label="1..*"),
)

print(render(d))
```

### Project Timeline

```python
from plantuml_compose import gantt_diagram, render

d = gantt_diagram(title="Sprint 1")
tk = d.tasks

design = tk.task("Design API", days=3)
impl = tk.task("Implement endpoints", days=5)
tests = tk.task("Write tests", days=3)
docs = tk.task("Documentation", days=2)

d.add(design, impl, tests, docs)

print(render(d))
```

## Design Philosophy

1. **Honest APIs**: We only expose parameters that PlantUML actually renders. No frustrating options that silently do nothing.

2. **Progressive disclosure**: Simple things are simple. Advanced features are available but don't clutter the basics.

3. **Type hints everywhere**: Your IDE helps you write correct diagrams. Typos are caught immediately.

4. **Documentation that teaches**: Each diagram guide explains *when* to use that type, not just *how*.

## Development

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Generate example documentation
uv run python tools/generate_docs.py
```

## License

MIT
