# Mind Map Diagrams

Mind maps are tree diagrams that radiate outward from a central idea. They're excellent for:

- **Brainstorming**: Capture ideas and see connections
- **Note-taking**: Organize information hierarchically
- **Project planning**: Break down tasks into subtasks
- **Concept mapping**: Show relationships between ideas

A mind map starts with one central topic, then branches out to related subtopics, which can have their own branches.

## Core Concepts

**Root node**: The central topic at the center of the diagram.

**Branch**: A line connecting a parent node to a child node.

**Child node**: A subtopic that branches from a parent. Can have its own children.

**Leaf node**: A node with no children (end of a branch).

**Side**: Branches can go left or right from the root. By default, PlantUML balances them automatically.

## Your First Mind Map

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram() as d:
    with d.node("Project Planning") as root:
        root.leaf("Requirements")
        root.leaf("Timeline")
        root.leaf("Resources")

print(d.render())
```

This creates a simple mind map with one central topic and three branches.

## Building Node Hierarchies

### Leaf Nodes (No Children)

Use `leaf()` when a node has no children:

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram() as d:
    with d.node("Fruits") as root:
        root.leaf("Apple")
        root.leaf("Banana")
        root.leaf("Cherry")

print(d.render())
```

### Nested Branches

Use `node()` as a context manager to add children to a branch:

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram() as d:
    with d.node("Animals") as root:
        with root.node("Mammals") as mammals:
            mammals.leaf("Dog")
            mammals.leaf("Cat")
            mammals.leaf("Elephant")
        with root.node("Birds") as birds:
            birds.leaf("Eagle")
            birds.leaf("Sparrow")

print(d.render())
```

### Deep Nesting

You can nest as deeply as needed:

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram() as d:
    with d.node("Software Development") as root:
        with root.node("Frontend") as frontend:
            with frontend.node("Frameworks") as frameworks:
                frameworks.leaf("React")
                frameworks.leaf("Vue")
                frameworks.leaf("Angular")
            frontend.leaf("CSS")
            frontend.leaf("HTML")
        with root.node("Backend") as backend:
            backend.leaf("Python")
            backend.leaf("Node.js")

print(d.render())
```

## Controlling Branch Direction

By default, branches spread left and right automatically. You can force a branch to one side:

### Force Left Side

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram() as d:
    with d.node("Central Topic") as root:
        with root.node("Left Branch 1", side="left") as left1:
            left1.leaf("Item A")
        with root.node("Left Branch 2", side="left") as left2:
            left2.leaf("Item B")

print(d.render())
```

### Force Right Side

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram() as d:
    with d.node("Central Topic") as root:
        with root.node("Right Branch 1", side="right") as right1:
            right1.leaf("Item A")
        with root.node("Right Branch 2", side="right") as right2:
            right2.leaf("Item B")

print(d.render())
```

### Mixed Sides

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram() as d:
    with d.node("Pros and Cons") as root:
        with root.node("Pros", side="right") as pros:
            pros.leaf("Fast")
            pros.leaf("Reliable")
            pros.leaf("Affordable")
        with root.node("Cons", side="left") as cons:
            cons.leaf("Learning curve")
            cons.leaf("Limited support")

print(d.render())
```

## Node Colors

Add background colors to any node:

### Single Node Color

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram() as d:
    with d.node("Topic", color="LightBlue") as root:
        root.leaf("Normal child")
        root.leaf("Another child", color="LightGreen")

print(d.render())
```

### Color-Coded Categories

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram() as d:
    with d.node("Project Status") as root:
        with root.node("Completed", color="#90EE90") as done:
            done.leaf("Research")
            done.leaf("Design")
        with root.node("In Progress", color="#FFE4B5") as progress:
            progress.leaf("Development")
        with root.node("Blocked", color="#FFB6C1") as blocked:
            blocked.leaf("Testing")

print(d.render())
```

### Hex Colors

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram() as d:
    with d.node("Colors", color="#E3F2FD") as root:
        root.leaf("Blue", color="#2196F3")
        root.leaf("Green", color="#4CAF50")
        root.leaf("Orange", color="#FF9800")

print(d.render())
```

## Boxless Nodes

Remove the box outline from nodes for a cleaner look:

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram() as d:
    with d.node("Main Topic") as root:
        root.leaf("Normal node")
        root.leaf("Boxless node", boxless=True)
        with root.node("Boxless branch", boxless=True) as branch:
            branch.leaf("Child of boxless")

print(d.render())
```

### All Boxless

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram() as d:
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
from plantuml_compose import mindmap_diagram

with mindmap_diagram() as d:
    with d.node("Project\nOverview") as root:
        root.leaf("Phase 1\nResearch\n2 weeks")
        root.leaf("Phase 2\nDevelopment\n4 weeks")
        root.leaf("Phase 3\nTesting\n2 weeks")

print(d.render())
```

## Diagram Direction

Control the overall layout direction:

### Top to Bottom

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram(direction="top_to_bottom") as d:
    with d.node("Root") as root:
        root.leaf("Child 1")
        root.leaf("Child 2")
        root.leaf("Child 3")

print(d.render())
```

### Left to Right

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram(direction="left_to_right") as d:
    with d.node("Start") as root:
        with root.node("Step 1") as s1:
            s1.leaf("Detail A")
        with root.node("Step 2") as s2:
            s2.leaf("Detail B")

print(d.render())
```

### Right to Left

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram(direction="right_to_left") as d:
    with d.node("End Goal") as root:
        root.leaf("Requirement 1")
        root.leaf("Requirement 2")

print(d.render())
```

## Styling with diagram_style

Apply consistent styling across the entire diagram:

### Basic Styling

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram(diagram_style={
    "background": "#FAFAFA",
    "font_name": "Arial",
}) as d:
    with d.node("Styled Map") as root:
        root.leaf("Child 1")
        root.leaf("Child 2")

print(d.render())
```

### Node Styling

Style all nodes at once:

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram(diagram_style={
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

Style the root node differently:

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram(diagram_style={
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

Style leaf nodes (nodes without children):

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram(diagram_style={
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
from plantuml_compose import mindmap_diagram

with mindmap_diagram(diagram_style={
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
from plantuml_compose import mindmap_diagram

with mindmap_diagram(diagram_style={
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
    with d.node("Styled Mind Map") as root:
        with root.node("Category A") as a:
            a.leaf("Item 1")
            a.leaf("Item 2")
        with root.node("Category B") as b:
            b.leaf("Item 3")

print(d.render())
```

## Complete Examples

### Project Breakdown

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram() as d:
    with d.node("Website Redesign") as root:
        with root.node("Research", side="left") as research:
            research.leaf("User interviews")
            research.leaf("Competitor analysis")
            research.leaf("Analytics review")
        with root.node("Design", side="left") as design:
            design.leaf("Wireframes")
            design.leaf("Mockups")
            design.leaf("Prototype")
        with root.node("Development", side="right") as dev:
            dev.leaf("Frontend")
            dev.leaf("Backend")
            dev.leaf("Database")
        with root.node("Launch", side="right") as launch:
            launch.leaf("Testing")
            launch.leaf("Deployment")
            launch.leaf("Monitoring")

print(d.render())
```

### Decision Tree

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram() as d:
    with d.node("Should I learn Python?") as root:
        with root.node("Yes", side="right", color="#C8E6C9") as yes:
            yes.leaf("Many job opportunities")
            yes.leaf("Easy to learn")
            yes.leaf("Versatile language")
        with root.node("Consider", side="left", color="#FFF9C4") as maybe:
            maybe.leaf("Time investment")
            maybe.leaf("Your goals")

print(d.render())
```

### Study Notes

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram(diagram_style={
    "root_node": {"background": "#1976D2", "font_color": "white"},
    "node": {"background": "#E3F2FD"},
}) as d:
    with d.node("Python Basics") as root:
        with root.node("Data Types") as types:
            types.leaf("int, float")
            types.leaf("str")
            types.leaf("list, tuple")
            types.leaf("dict, set")
        with root.node("Control Flow") as flow:
            flow.leaf("if/elif/else")
            flow.leaf("for loops")
            flow.leaf("while loops")
        with root.node("Functions") as funcs:
            funcs.leaf("def keyword")
            funcs.leaf("Parameters")
            funcs.leaf("Return values")

print(d.render())
```

### Org Chart

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram(direction="top_to_bottom") as d:
    with d.node("CEO", color="#FFD54F") as ceo:
        with ceo.node("CTO") as cto:
            cto.leaf("Engineering")
            cto.leaf("QA")
        with ceo.node("CFO") as cfo:
            cfo.leaf("Accounting")
            cfo.leaf("Finance")
        with ceo.node("COO") as coo:
            coo.leaf("Operations")
            coo.leaf("HR")

print(d.render())
```

## Quick Reference

### Diagram Creation

| Code | Description |
|------|-------------|
| `mindmap_diagram()` | Create a mind map |
| `direction="top_to_bottom"` | Vertical layout |
| `direction="left_to_right"` | Horizontal (left start) |
| `direction="right_to_left"` | Horizontal (right start) |
| `diagram_style={...}` | Apply styling |

### Node Methods

| Method | Description |
|--------|-------------|
| `d.node(text)` | Add root node (use as context manager) |
| `root.node(text)` | Add child branch (use as context manager) |
| `root.leaf(text)` | Add leaf node (no children) |

### Node Parameters

| Parameter | Description |
|-----------|-------------|
| `text` | Node label (required) |
| `side="left"` | Force to left side |
| `side="right"` | Force to right side |
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
