# WBS Diagrams (Work Breakdown Structure)

WBS diagrams decompose projects into hierarchical components. They're the standard tool for:

- **Project planning**: Break large projects into manageable pieces
- **Scope definition**: Clearly show what's included in a project
- **Task assignment**: Organize work packages for team members
- **Cost estimation**: Estimate costs at each level of breakdown

A WBS starts with the project goal at the top, then breaks it down into deliverables, which break down into work packages.

## Core Concepts

**Root node**: The project or main deliverable at the top of the hierarchy.

**Branch**: A major component or phase that breaks down further.

**Work package**: The lowest level - actual tasks that can be assigned and estimated.

**Side**: Branches can extend left or right from parent nodes to balance the diagram.

## Your First WBS Diagram

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("Website Project") as root:
        root.leaf("Requirements")
        root.leaf("Design")
        root.leaf("Development")
        root.leaf("Testing")

print(d.render())
```

This creates a simple WBS with one project and four deliverables.

## Building the Hierarchy

### Leaf Nodes (Work Packages)

Use `leaf()` for nodes with no children - typically the actual work packages:

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("Mobile App") as root:
        root.leaf("User Research")
        root.leaf("UI Design")
        root.leaf("Backend API")
        root.leaf("Testing")

print(d.render())
```

### Nested Breakdown

Use `node()` as a context manager to create sub-hierarchies:

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("Software Project") as root:
        with root.node("Planning") as planning:
            planning.leaf("Requirements")
            planning.leaf("Architecture")
        with root.node("Development") as dev:
            dev.leaf("Frontend")
            dev.leaf("Backend")
        with root.node("Testing") as test:
            test.leaf("Unit Tests")
            test.leaf("Integration")

print(d.render())
```

### Deep Hierarchies

WBS diagrams often have 3-4 levels of breakdown:

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("Product Launch") as root:
        with root.node("Marketing") as marketing:
            with marketing.node("Digital") as digital:
                digital.leaf("Social Media")
                digital.leaf("Email Campaign")
                digital.leaf("PPC Ads")
            with marketing.node("Traditional") as trad:
                trad.leaf("Print Ads")
                trad.leaf("Events")
        with root.node("Sales") as sales:
            sales.leaf("Training")
            sales.leaf("Collateral")

print(d.render())
```

## Controlling Branch Direction

By default, branches spread evenly. You can force branches to one side:

### Force Left

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("Project") as root:
        with root.node("Phase A", side="left") as a:
            a.leaf("Task A1")
            a.leaf("Task A2")
        with root.node("Phase B", side="left") as b:
            b.leaf("Task B1")

print(d.render())
```

### Force Right

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("Project") as root:
        with root.node("Phase A", side="right") as a:
            a.leaf("Task A1")
        with root.node("Phase B", side="right") as b:
            b.leaf("Task B1")
            b.leaf("Task B2")

print(d.render())
```

### Balanced Layout

Mix sides to create a balanced diagram:

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("Conference Planning") as root:
        with root.node("Venue", side="left") as venue:
            venue.leaf("Location")
            venue.leaf("Catering")
            venue.leaf("AV Setup")
        with root.node("Content", side="right") as content:
            content.leaf("Speakers")
            content.leaf("Schedule")
            content.leaf("Materials")

print(d.render())
```

## Node Colors

Highlight important nodes or show status with colors:

### Single Node Color

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("Project", color="LightBlue") as root:
        root.leaf("Critical Task", color="Salmon")
        root.leaf("Normal Task")

print(d.render())
```

### Status Colors

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("Sprint 1") as root:
        with root.node("Completed", color="#90EE90") as done:
            done.leaf("Design")
            done.leaf("Backend")
        with root.node("In Progress", color="#FFE4B5") as wip:
            wip.leaf("Frontend")
        with root.node("Not Started", color="#E0E0E0") as todo:
            todo.leaf("Testing")
            todo.leaf("Deployment")

print(d.render())
```

### Hex Colors

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("Priorities", color="#E3F2FD") as root:
        root.leaf("High", color="#F44336")
        root.leaf("Medium", color="#FF9800")
        root.leaf("Low", color="#4CAF50")

print(d.render())
```

## Boxless Nodes

Remove box outlines for a cleaner look:

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("Main Topic") as root:
        root.leaf("With box")
        root.leaf("Without box", boxless=True)
        with root.node("Boxless branch", boxless=True) as branch:
            branch.leaf("Child node")

print(d.render())
```

### All Boxless

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("Outline Style", boxless=True) as root:
        with root.node("Category A", boxless=True) as a:
            a.leaf("Item 1", boxless=True)
            a.leaf("Item 2", boxless=True)
        with root.node("Category B", boxless=True) as b:
            b.leaf("Item 3", boxless=True)

print(d.render())
```

## Multiline Text

Node text can span multiple lines using `\n`:

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("Q1 Goals") as root:
        root.leaf("Launch MVP\nby March 15")
        root.leaf("Hire 3 engineers\nfor backend team")
        root.leaf("Close Series A\n$5M target")

print(d.render())
```

## Arrows Between Nodes

WBS diagrams can show dependencies between work packages using aliases and arrows:

### Basic Arrows

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("Project") as root:
        root.leaf("Design", alias="design")
        root.leaf("Develop", alias="dev")
        root.leaf("Test", alias="test")

    d.arrow("design", "dev")
    d.arrow("dev", "test")

print(d.render())
```

### Complex Dependencies

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("Release") as root:
        with root.node("Backend", side="left") as backend:
            backend.leaf("API Design", alias="api")
            backend.leaf("Database", alias="db")
            backend.leaf("Services", alias="svc")
        with root.node("Frontend", side="right") as frontend:
            frontend.leaf("UI Design", alias="ui")
            frontend.leaf("Components", alias="comp")
            frontend.leaf("Integration", alias="integ")

    # Backend dependencies
    d.arrow("api", "svc")
    d.arrow("db", "svc")

    # Frontend dependencies
    d.arrow("ui", "comp")
    d.arrow("comp", "integ")

    # Cross-team dependency
    d.arrow("svc", "integ")

print(d.render())
```

## Styling with diagram_style

Apply consistent styling across the entire diagram:

### Basic Styling

```python
from plantuml_compose import wbs_diagram

with wbs_diagram(diagram_style={
    "background": "#FAFAFA",
    "font_name": "Arial",
}) as d:
    with d.node("Styled WBS") as root:
        root.leaf("Child 1")
        root.leaf("Child 2")

print(d.render())
```

### Node Styling

```python
from plantuml_compose import wbs_diagram

with wbs_diagram(diagram_style={
    "node": {
        "background": "#E3F2FD",
        "font_color": "#1565C0",
    }
}) as d:
    with d.node("Blue Theme") as root:
        with root.node("Branch A") as a:
            a.leaf("Leaf 1")
            a.leaf("Leaf 2")
        root.leaf("Branch B")

print(d.render())
```

### Root Node Styling

Style the root node differently from other nodes:

```python
from plantuml_compose import wbs_diagram

with wbs_diagram(diagram_style={
    "root_node": {
        "background": "#FF9800",
        "font_color": "white",
    },
    "node": {
        "background": "#FFF3E0",
    }
}) as d:
    with d.node("Highlighted Root") as root:
        root.leaf("Normal child 1")
        root.leaf("Normal child 2")

print(d.render())
```

### Leaf Node Styling

Style work packages (leaf nodes) differently:

```python
from plantuml_compose import wbs_diagram

with wbs_diagram(diagram_style={
    "leaf_node": {
        "background": "#E8F5E9",
        "font_color": "#2E7D32",
    }
}) as d:
    with d.node("Root") as root:
        with root.node("Has children") as branch:
            branch.leaf("Leaf A")
            branch.leaf("Leaf B")
        root.leaf("Also a leaf")

print(d.render())
```

### Arrow Styling

Customize the connecting lines:

```python
from plantuml_compose import wbs_diagram

with wbs_diagram(diagram_style={
    "arrow": {
        "line_color": "#9E9E9E",
        "line_thickness": 2,
    }
}) as d:
    with d.node("Central") as root:
        with root.node("Branch 1") as b1:
            b1.leaf("Detail")
        root.leaf("Branch 2")

print(d.render())
```

### Combined Styling

```python
from plantuml_compose import wbs_diagram

with wbs_diagram(diagram_style={
    "background": "#ECEFF1",
    "root_node": {
        "background": "#263238",
        "font_color": "white",
    },
    "node": {
        "background": "#CFD8DC",
    },
    "leaf_node": {
        "background": "#FAFAFA",
    },
    "arrow": {
        "line_color": "#607D8B",
    }
}) as d:
    with d.node("Styled WBS") as root:
        with root.node("Category A") as a:
            a.leaf("Item 1")
            a.leaf("Item 2")
        with root.node("Category B") as b:
            b.leaf("Item 3")

print(d.render())
```

## Complete Examples

### Software Project WBS

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("E-Commerce Platform") as root:
        with root.node("Planning", side="left") as plan:
            plan.leaf("Requirements")
            plan.leaf("Architecture")
            plan.leaf("Timeline")
        with root.node("Development", side="left") as dev:
            with dev.node("Frontend") as fe:
                fe.leaf("Product Pages")
                fe.leaf("Cart")
                fe.leaf("Checkout")
            with dev.node("Backend") as be:
                be.leaf("User API")
                be.leaf("Product API")
                be.leaf("Order API")
        with root.node("Testing", side="right") as test:
            test.leaf("Unit Tests")
            test.leaf("Integration")
            test.leaf("UAT")
        with root.node("Deployment", side="right") as deploy:
            deploy.leaf("Infrastructure")
            deploy.leaf("CI/CD")
            deploy.leaf("Monitoring")

print(d.render())
```

### Event Planning WBS

```python
from plantuml_compose import wbs_diagram

with wbs_diagram(diagram_style={
    "root_node": {"background": "#1976D2", "font_color": "white"},
    "node": {"background": "#E3F2FD"},
}) as d:
    with d.node("Annual Conference") as root:
        with root.node("Venue") as venue:
            venue.leaf("Location Search")
            venue.leaf("Contract")
            venue.leaf("Layout")
        with root.node("Program") as prog:
            prog.leaf("Keynotes")
            prog.leaf("Breakouts")
            prog.leaf("Workshops")
        with root.node("Marketing") as mktg:
            mktg.leaf("Website")
            mktg.leaf("Email")
            mktg.leaf("Social")
        with root.node("Operations") as ops:
            ops.leaf("Registration")
            ops.leaf("Catering")
            ops.leaf("AV Equipment")

print(d.render())
```

### Construction Project with Dependencies

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("House Construction") as root:
        with root.node("Foundation", side="left") as found:
            found.leaf("Survey", alias="survey")
            found.leaf("Excavation", alias="excav")
            found.leaf("Pour Concrete", alias="pour")
        with root.node("Structure", side="right") as struct:
            struct.leaf("Framing", alias="frame")
            struct.leaf("Roofing", alias="roof")
            struct.leaf("Exterior", alias="ext")

    # Foundation sequence
    d.arrow("survey", "excav")
    d.arrow("excav", "pour")

    # Structure sequence
    d.arrow("pour", "frame")
    d.arrow("frame", "roof")
    d.arrow("frame", "ext")

print(d.render())
```

### Product Roadmap

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("2024 Roadmap") as root:
        with root.node("Q1", color="#BBDEFB") as q1:
            q1.leaf("MVP Launch")
            q1.leaf("Beta Testing")
        with root.node("Q2", color="#C8E6C9") as q2:
            q2.leaf("User Feedback")
            q2.leaf("Performance")
        with root.node("Q3", color="#FFF9C4") as q3:
            q3.leaf("New Features")
            q3.leaf("Integrations")
        with root.node("Q4", color="#FFCCBC") as q4:
            q4.leaf("Scale")
            q4.leaf("Enterprise")

print(d.render())
```

## Quick Reference

### Diagram Creation

| Code | Description |
|------|-------------|
| `wbs_diagram()` | Create a WBS diagram |
| `diagram_style={...}` | Apply styling |

### Node Methods

| Method | Description |
|--------|-------------|
| `d.node(text)` | Add root node (use as context manager) |
| `root.node(text)` | Add child branch (use as context manager) |
| `root.leaf(text)` | Add leaf node (no children) |
| `d.arrow(from, to)` | Add arrow between aliased nodes |

### Node Parameters

| Parameter | Description |
|-----------|-------------|
| `text` | Node label (required) |
| `side="left"` | Force to left side |
| `side="right"` | Force to right side |
| `alias="name"` | ID for arrow connections |
| `color="..."` | Background color |
| `boxless=True` | Remove box outline |

### Diagram Style Keys

| Key | Description |
|-----|-------------|
| `background` | Diagram background color |
| `font_name` | Default font |
| `font_size` | Default font size |
| `font_color` | Default text color |
| `node` | Style for all nodes |
| `root_node` | Style for root node only |
| `leaf_node` | Style for leaf nodes only |
| `arrow` | Style for connecting lines |

### Node/Arrow Style Keys

| Key | Description |
|-----|-------------|
| `background` | Fill color |
| `font_color` | Text color |
| `line_color` | Border/line color |
| `line_thickness` | Border/line width |

## WBS vs Mind Map

Both are tree diagrams, but serve different purposes:

| WBS | Mind Map |
|-----|----------|
| Project decomposition | Idea exploration |
| Top-down (goal to tasks) | Central topic outward |
| Formal structure | Freeform brainstorming |
| Supports dependencies (arrows) | No arrows |
| Work packages at leaves | Ideas at any level |

Use WBS when you need to break down work for planning and tracking. Use mind maps for brainstorming and exploring concepts.
