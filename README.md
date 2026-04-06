# plantuml-compose

A Python library that makes creating PlantUML diagrams intuitive and type-safe.

## Why plantuml-compose?

PlantUML is powerful but its text syntax can be cryptic. What does `A -[#red,dashed]-> B` mean? What options are available for a state transition?

plantuml-compose solves this by providing:

- **Discoverable APIs**: Use your IDE's autocomplete to explore options
- **Type safety**: Catch errors before rendering, not after
- **Pure factory functions**: Compose diagrams declaratively with nesting
- **Full PlantUML coverage**: Every diagram type, every feature

## Quick Start

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram(title="API Call")
p = d.participants
e = d.events

client = p.actor("Client")
server = p.participant("Server")
d.add(client, server)

d.phase("Request", [
    e.message(client, server, "GET /users"),
    e.reply(server, client, "200 OK"),
])

print(render(d))
```

## The Pattern

Every diagram follows the same shape:

```python
# 1. Create diagram — get namespace(s)
d = state_diagram(title="Lifecycle")
el = d.elements
t = d.transitions

# 2. Create elements via namespace factories
idle = el.state("Idle")
active = el.state("Active")

# 3. Register elements
d.add(idle, active)

# 4. Create and register connections
d.connect(
    t.transitions(
        (el.initial(), idle, "start"),
        (idle, active, "go"),
        (active, el.final(), "done"),
    )
)

# 5. Render
print(render(d))
```

**Namespaces** organize the API — type `d.elements.` or `d.transitions.` and your IDE shows every available factory method.

**Bulk helpers** reduce repetition:

```python
# Instead of individual calls:
t.transition(a, b, label="x"),
t.transition(b, c, label="y"),
t.transition(c, d, label="z"),

# Use the plural form:
t.transitions(
    (a, b, "x"),
    (b, c, "y"),
    (c, d, "z"),
)

# Or fan-out from one source:
r.arrows_from(api,
    (db, "queries"),
    (cache, "reads"),
    (queue, "publishes"),
)
```

## Styling

Two levels of styling are available on every diagram type.

**Inline styles** on individual elements and connections:

```python
# Element styling
el.state("Error", style={"background": "#FFCDD2", "line_color": "red"})

# Connection styling — string shorthand or dict
t.transition(a, b, style="dashed")
t.transition(a, b, style={"color": "red", "pattern": "dotted"})

# Arrow length (layout hint)
r.arrow(a, b, length=1)   # short: ->
r.arrow(a, b, length=3)   # long:  --->

# Custom arrow heads
r.arrow(a, b, left_head="o", right_head=">>")  # o-->>
```

**Diagram-wide styling** via `diagram_style=`:

```python
d = class_diagram(
    title="Model",
    diagram_style={
        "class_": {"background": "#E3F2FD", "round_corner": 10},
        "arrow": {"line_color": "gray", "font_size": 10},
        "note": {"background": "#FFF9C4"},
        "stereotypes": {
            "important": {"background": "pink", "font_style": "bold"},
        },
    },
)
```

Every element property is documented in `ElementStyleDict` — hover over it in your IDE to see all available keys (background, line_color, font_color, font_name, font_size, padding, margin, round_corner, shadowing, max_width, and more).

## Supported Diagram Types

### Behavioral

| Type | Use When | Guide |
|------|----------|-------|
| [**Sequence**](examples/sequence-diagrams.md) | Message flows between participants | API calls, protocols |
| [**State**](examples/state-diagrams.md) | Entity lifecycle tracking | Order status, workflows |
| [**Activity**](examples/activity-diagrams.md) | Process flow with decisions and parallelism | Business processes, algorithms |
| [**Use Case**](examples/usecase-diagrams.md) | System boundaries and actor goals | Requirements, features |
| [**Timing**](examples/timing-diagrams.md) | State changes over time | Hardware signals, protocol timing |

### Structural

| Type | Use When | Guide |
|------|----------|-------|
| [**Class**](examples/class-diagrams.md) | Types, attributes, and relationships | Domain models, API types |
| [**Object**](examples/object-diagrams.md) | Specific instances and values | Test scenarios, snapshots |
| [**Component**](examples/component-diagrams.md) | System architecture | Services, modules, dependencies |
| [**Deployment**](examples/deployment-diagrams.md) | Software on infrastructure | Servers, containers, cloud |
| [**Network**](examples/network-diagrams.md) | Network topology | IP addressing, segments |

### Hierarchical

| Type | Use When | Guide |
|------|----------|-------|
| [**Mind Map**](examples/mindmap-diagrams.md) | Brainstorming and organizing ideas | Feature planning, concepts |
| [**WBS**](examples/wbs-diagrams.md) | Breaking down work | Project planning, tasks |
| [**Gantt**](examples/gantt-diagrams.md) | Scheduling with dependencies | Timelines, sprint planning |

### Data & UI

| Type | Use When | Guide |
|------|----------|-------|
| [**JSON**](examples/json-yaml-diagrams.md) | Visualizing JSON data | API responses, config |
| [**YAML**](examples/json-yaml-diagrams.md) | Visualizing YAML data | Config files, specs |
| [**Salt**](examples/salt-diagrams.md) | UI wireframes | Forms, layouts, menus |

### Composition

| Feature | Guide |
|---------|-------|
| [**Sub-diagrams**](examples/subdiagrams.md) | Embed diagrams inside notes and messages |

## CLI: Markdown Processing

`puml-md` (also available as `plantuml-compose md`) processes markdown files, executing Python code blocks that import `plantuml_compose` and inserting rendered diagram images.

Given a markdown file containing:

````markdown
```python
from plantuml_compose import state_diagram, render

d = state_diagram(title="Example")
d.add(d.elements.state("Active"))
print(render(d))
```
````

Running `puml-md doc.md` produces the same file with a diagram image appended after the code block:

````markdown
```python
from plantuml_compose import state_diagram, render

d = state_diagram(title="Example")
d.add(d.elements.state("Active"))
print(render(d))
```

![Diagram](https://www.plantuml.com/plantuml/svg/...)
````

Re-running replaces existing diagram URLs rather than duplicating them.

```bash
puml-md doc.md            # file → stdout
puml-md -i doc.md         # in-place update
puml-md -id doc.md        # in-place + wrap code in <details>
puml-md --validate doc.md # check diagrams against the server
cat doc.md | puml-md      # stdin → stdout
```

| Flag | Description |
|------|-------------|
| `-i`, `--in-place` | Modify file in place |
| `-d`, `--details` | Wrap code blocks in collapsible `<details><summary>` |
| `--validate` | Check generated diagrams against the PlantUML server; exits non-zero on errors |
| `--server URL` | Custom PlantUML server (default: public server) |
| `--format FMT` | Output format: `svg`, `png`, `txt` (default: `svg`) |

## Installation

```bash
pip install plantuml-compose
```

Requires Python 3.13+.

## Development

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Validate output against PlantUML
plantuml --check-syntax output.puml
```

## License

MIT
