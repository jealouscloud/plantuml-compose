# plantuml-compose

A Python library that makes creating PlantUML diagrams intuitive and type-safe.

## Why plantuml-compose?

PlantUML is powerful but its text syntax can be cryptic. What does `A -[#red,dashed]-> B` mean? What options are available for a state transition?

plantuml-compose solves this by providing:

- **Discoverable APIs**: Use your IDE's autocomplete to explore options
- **Type safety**: Catch errors before rendering, not after
- **Context managers**: Natural Python patterns that mirror diagram structure
- **Comprehensive documentation**: Each diagram type explains *when* and *why* to use it

```python
from plantuml_compose import sequence_diagram

with sequence_diagram(title="Simple API Call") as d:
    client = d.participant("Client")
    server = d.participant("Server")

    d.message(client, server, "GET /users")
    d.message(server, client, "200 OK")

print(d.render())
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
from plantuml_compose import state_diagram

with state_diagram(title="Order Lifecycle") as d:
    pending = d.state("Pending")
    paid = d.state("Paid")
    shipped = d.state("Shipped")
    delivered = d.state("Delivered")

    d.arrow(d.start(), pending)
    d.arrow(pending, paid, label="payment received")
    d.arrow(paid, shipped, label="items packed")
    d.arrow(shipped, delivered, label="customer signs")
    d.arrow(delivered, d.end())

print(d.render())
```

### Class Relationships

```python
from plantuml_compose import class_diagram

with class_diagram(title="E-commerce Model") as d:
    user = d.class_("User", attributes=["id: int", "email: str"])
    order = d.class_("Order", attributes=["total: Decimal"])
    item = d.class_("LineItem", attributes=["quantity: int"])

    d.has(user, order, part_label="*")       # User has many Orders
    d.contains(order, item, part_label="1..*")  # Order contains LineItems

print(d.render())
```

### Project Timeline

```python
from plantuml_compose import gantt_diagram

with gantt_diagram(title="Sprint 1") as d:
    d.task("Design API", duration=3)
    d.task("Implement endpoints", duration=5)
    d.task("Write tests", duration=3)
    d.task("Documentation", duration=2)

print(d.render())
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
