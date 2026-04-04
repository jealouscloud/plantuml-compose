# Salt Wireframe Diagrams

Salt wireframes are UI mockup diagrams for sketching user interfaces. They're useful for:

- **Wireframing**: Quickly sketch a form, dialog, or settings panel
- **Requirements communication**: Show stakeholders what a screen will look like before building it
- **Prototyping**: Lay out widgets in grids to explore different arrangements
- **Documentation**: Include UI sketches alongside technical docs

Salt diagrams use a widget-based model. You create individual widgets (buttons, text fields, checkboxes) and arrange them in grids, tabs, and group boxes.

## Core Concepts

**Widget**: A UI element like a button, checkbox, text field, or dropdown.

**Grid**: A table-like layout that arranges widgets in rows and columns. Border style controls which grid lines are drawn.

**Row**: A single row inside a grid. Each cell in a row holds a widget (or nested grid).

**Container**: A grouping widget (tabs, scrollbar, group box) that wraps other widgets.

## Your First Salt Wireframe

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram()
w = d.widgets

d.add(
    w.text("Username"),
    w.text_field("admin", width=20),
    w.text("Password"),
    w.text_field("", width=20),
    w.button("Login"),
)

print(render(d))
```

This creates a simple vertical layout with labels, text fields, and a button stacked top to bottom.

## Basic Widgets

### Text Labels

Plain text labels for headings, instructions, or field names.

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram()
w = d.widgets

d.add(
    w.text("Welcome to the application"),
    w.text("Please fill out the form below"),
)

print(render(d))
```

### Buttons

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram()
w = d.widgets

d.add(
    w.button("OK"),
    w.button("Cancel"),
    w.button("Apply"),
)

print(render(d))
```

### Checkboxes

Checkboxes support a `checked` parameter to show them in a selected state.

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram()
w = d.widgets

d.add(
    w.checkbox("Enable notifications", checked=True),
    w.checkbox("Send email alerts"),
    w.checkbox("Dark mode"),
)

print(render(d))
```

### Radio Buttons

Radio buttons use `selected` to indicate the active choice.

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram()
w = d.widgets

d.add(
    w.radio("Small"),
    w.radio("Medium", selected=True),
    w.radio("Large"),
)

print(render(d))
```

### Text Fields

Text fields accept a default `value` and a `width` in approximate characters.

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram()
w = d.widgets

d.add(
    w.text_field("default text", width=25),
    w.text_field("", width=30),
)

print(render(d))
```

### Dropdowns

Dropdowns list selectable options. The first item is displayed as the selected value.

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram()
w = d.widgets

d.add(
    w.dropdown("Option A", "Option B", "Option C"),
)

print(render(d))
```

### Open Dropdowns

Set `open=True` to show the dropdown in its expanded state, revealing all choices.

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram()
w = d.widgets

d.add(
    w.dropdown("Red", "Green", "Blue", open=True),
)

print(render(d))
```

## Separators

Separators draw horizontal divider lines between widgets. Four styles are available.

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram()
w = d.widgets

d.add(
    w.text("Section A"),
    w.separator(".."),   # Dotted
    w.text("Section B"),
    w.separator("=="),   # Double line
    w.text("Section C"),
    w.separator("~~"),   # Wave
    w.text("Section D"),
    w.separator("--"),   # Dashed
    w.text("Section E"),
)

print(render(d))
```

The default style is `".."` (dotted), so `w.separator()` with no argument produces a dotted line.

## Grid Layout

Grids are the primary layout mechanism. They arrange widgets in a table with rows and columns.

### Basic Grid

The first argument to `grid()` is the border style. Use `"#"` for all lines (the default).

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram()
w = d.widgets

d.add(
    w.grid("#",
        w.row(w.text("Name"), w.text_field("", width=20)),
        w.row(w.text("Email"), w.text_field("", width=20)),
        w.row(w.text("Role"), w.dropdown("Admin", "User", "Guest")),
    ),
)

print(render(d))
```

### Grid Border Styles

Four border styles control which grid lines appear.

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram(title="Grid Style: # (all lines)")
w = d.widgets

d.add(
    w.grid("#",
        w.row(w.text("A"), w.text("B")),
        w.row(w.text("C"), w.text("D")),
    ),
)

print(render(d))
```

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram(title="Grid Style: ! (vertical lines only)")
w = d.widgets

d.add(
    w.grid("!",
        w.row(w.text("A"), w.text("B")),
        w.row(w.text("C"), w.text("D")),
    ),
)

print(render(d))
```

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram(title="Grid Style: - (horizontal lines only)")
w = d.widgets

d.add(
    w.grid("-",
        w.row(w.text("A"), w.text("B")),
        w.row(w.text("C"), w.text("D")),
    ),
)

print(render(d))
```

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram(title="Grid Style: + (external lines only)")
w = d.widgets

d.add(
    w.grid("+",
        w.row(w.text("A"), w.text("B")),
        w.row(w.text("C"), w.text("D")),
    ),
)

print(render(d))
```

### Rows with Pipe Separators

Each `row()` defines one row of the grid. Cells in a row are separated by pipes in the rendered output.

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram()
w = d.widgets

d.add(
    w.grid("#",
        w.row(w.text("Header 1"), w.text("Header 2"), w.text("Header 3")),
        w.row(w.text("Row 1 A"), w.text("Row 1 B"), w.text("Row 1 C")),
        w.row(w.text("Row 2 A"), w.text("Row 2 B"), w.text("Row 2 C")),
    ),
)

print(render(d))
```

### Nested Grids Inside Cells

A cell in a row can contain another grid, enabling complex nested layouts.

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram()
w = d.widgets

d.add(
    w.grid("#",
        w.row(
            w.text("Contact Info"),
            w.grid("#",
                w.row(w.text("Phone"), w.text_field("555-0100", width=12)),
                w.row(w.text("Email"), w.text_field("user@example.com", width=12)),
            ),
        ),
        w.row(
            w.text("Actions"),
            w.grid("#",
                w.row(w.button("Save"), w.button("Cancel")),
            ),
        ),
    ),
)

print(render(d))
```

## Menu Bar

Menu bars display a horizontal menu with optional sub-items. Sub-items are specified as `(parent, child)` tuples.

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram()
w = d.widgets

d.add(
    w.menu("File", "Edit", "View", "Help",
        sub_items=(
            ("File", "New"),
            ("File", "Open"),
            ("File", "Save"),
            ("Edit", "Undo"),
            ("Edit", "Redo"),
        ),
    ),
)

print(render(d))
```

## Tab Bar

Tab bars show multiple tabs with the content of the active tab displayed below.

### Horizontal Tabs

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram()
w = d.widgets

d.add(
    w.tab_bar("General", "Advanced", "About",
        content=(
            w.text("General settings go here"),
            w.checkbox("Auto-save", checked=True),
            w.checkbox("Show tooltips"),
        ),
    ),
)

print(render(d))
```

### Vertical Tabs

Set `vertical=True` to stack tabs vertically on the side.

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram()
w = d.widgets

d.add(
    w.tab_bar("Tab 1", "Tab 2", "Tab 3",
        vertical=True,
        content=(
            w.text("Content for the active vertical tab"),
            w.button("Action"),
        ),
    ),
)

print(render(d))
```

## Group Box

A group box draws a titled border around a set of widgets.

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram()
w = d.widgets

d.add(
    w.group_box("Network Settings",
        w.text("Hostname"),
        w.text_field("server01", width=20),
        w.checkbox("Use DHCP", checked=True),
        w.text("DNS Server"),
        w.text_field("8.8.8.8", width=15),
    ),
)

print(render(d))
```

## Scrollbar

Scrollbar containers wrap content and add scrollbars. Three styles control which scrollbars appear.

### Both Scrollbars

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram()
w = d.widgets

d.add(
    w.scrollbar("S",
        w.text("Line 1"),
        w.text("Line 2"),
        w.text("Line 3"),
        w.text("Line 4"),
    ),
)

print(render(d))
```

### Vertical Scrollbar Only

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram()
w = d.widgets

d.add(
    w.scrollbar("SI",
        w.text("Scrollable content (vertical only)"),
    ),
)

print(render(d))
```

### Horizontal Scrollbar Only

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram()
w = d.widgets

d.add(
    w.scrollbar("S-",
        w.text("Scrollable content (horizontal only)"),
    ),
)

print(render(d))
```

## Tree Widget

Tree widgets display hierarchical data. Each node is a `(depth, label)` tuple where depth 1 is the root level.

### Basic Tree

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram()
w = d.widgets

d.add(
    w.tree(
        (1, "Root"),
        (2, "Child A"),
        (3, "Grandchild A1"),
        (3, "Grandchild A2"),
        (2, "Child B"),
        (3, "Grandchild B1"),
    ),
)

print(render(d))
```

### Tree Styles

Five tree line styles are available: `T`, `T!`, `T-`, `T+`, `T#`.

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram(title="Tree style: T (default)")
w = d.widgets

d.add(
    w.tree(
        (1, "Root"), (2, "Child"), (3, "Leaf"),
        style="T",
    ),
)

print(render(d))
```

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram(title="Tree style: T!")
w = d.widgets

d.add(
    w.tree(
        (1, "Root"), (2, "Child"), (3, "Leaf"),
        style="T!",
    ),
)

print(render(d))
```

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram(title="Tree style: T-")
w = d.widgets

d.add(
    w.tree(
        (1, "Root"), (2, "Child"), (3, "Leaf"),
        style="T-",
    ),
)

print(render(d))
```

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram(title="Tree style: T+")
w = d.widgets

d.add(
    w.tree(
        (1, "Root"), (2, "Child"), (3, "Leaf"),
        style="T+",
    ),
)

print(render(d))
```

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram(title="Tree style: T#")
w = d.widgets

d.add(
    w.tree(
        (1, "Root"), (2, "Child"), (3, "Leaf"),
        style="T#",
    ),
)

print(render(d))
```

## Title and Mainframe

### Title

Add a title above the diagram.

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram(title="Login Form")
w = d.widgets

d.add(
    w.text_field("username", width=20),
    w.text_field("", width=20),
    w.button("Sign In"),
)

print(render(d))
```

### Mainframe

Wrap the entire diagram in a labeled frame.

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram(mainframe="User Preferences")
w = d.widgets

d.add(
    w.checkbox("Dark mode"),
    w.checkbox("Notifications", checked=True),
    w.button("Save"),
)

print(render(d))
```

## Header, Footer, Caption, and Legend

These add contextual text around the diagram.

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram(
    title="Settings Panel",
    caption="Figure 1: Application settings wireframe",
    header="Draft - Internal Use Only",
    footer="Page 1 of 3",
    legend="Checkboxes indicate enabled features",
)
w = d.widgets

d.add(
    w.checkbox("Feature A", checked=True),
    w.checkbox("Feature B"),
    w.button("Apply"),
)

print(render(d))
```

## Complete Examples

### Login Dialog

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram(title="Login")
w = d.widgets

d.add(
    w.grid("#",
        w.row(w.text("Username"), w.text_field("", width=20)),
        w.row(w.text("Password"), w.text_field("", width=20)),
    ),
    w.separator("--"),
    w.checkbox("Remember me"),
    w.grid("-",
        w.row(w.button("Login"), w.button("Cancel")),
    ),
)

print(render(d))
```

### Application Window

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram(mainframe="My Application")
w = d.widgets

d.add(
    w.menu("File", "Edit", "View", "Help",
        sub_items=(
            ("File", "New"),
            ("File", "Open"),
            ("File", "Save"),
            ("File", "Exit"),
            ("Edit", "Cut"),
            ("Edit", "Copy"),
            ("Edit", "Paste"),
            ("Help", "About"),
        ),
    ),
    w.tab_bar("Dashboard", "Settings", "Logs",
        content=(
            w.grid("#",
                w.row(w.text("Status"), w.text("Online")),
                w.row(w.text("Uptime"), w.text("14 days")),
                w.row(w.text("CPU"), w.text("23%")),
            ),
        ),
    ),
)

print(render(d))
```

### Server Provisioning Form

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram(title="New Server")
w = d.widgets

d.add(
    w.group_box("Server Details",
        w.grid("#",
            w.row(w.text("Hostname"), w.text_field("", width=20)),
            w.row(w.text("IP Address"), w.text_field("10.0.0.", width=15)),
            w.row(w.text("OS"), w.dropdown("RHEL 9", "Ubuntu 24.04", "Debian 12")),
            w.row(w.text("Size"), w.dropdown("Small", "Medium", "Large")),
        ),
    ),
    w.separator("=="),
    w.group_box("Options",
        w.checkbox("Enable monitoring", checked=True),
        w.checkbox("Auto-patch"),
        w.radio("Production", selected=True),
        w.radio("Staging"),
    ),
    w.separator("=="),
    w.grid("-",
        w.row(w.button("Provision"), w.button("Cancel")),
    ),
)

print(render(d))
```

### File Browser with Tree and Scrollbar

```python
from plantuml_compose import salt_diagram, render

d = salt_diagram(title="File Browser")
w = d.widgets

d.add(
    w.scrollbar("SI",
        w.tree(
            (1, "home"),
            (2, "user"),
            (3, "Documents"),
            (3, "Downloads"),
            (3, "Projects"),
            (4, "webapp"),
            (4, "api-server"),
            (2, "shared"),
            (3, "templates"),
            style="T",
        ),
    ),
)

print(render(d))
```

## Quick Reference

### Diagram Creation

| Code | Description |
|------|-------------|
| `salt_diagram()` | Create a salt wireframe |
| `title="..."` | Diagram title |
| `mainframe="..."` | Frame label around the diagram |
| `caption="..."` | Caption text below |
| `header="..."` | Header text above |
| `footer="..."` | Footer text below |
| `legend="..."` | Legend box |

### Widget Methods

| Method | Description |
|--------|-------------|
| `w.text(text)` | Plain text label |
| `w.button(label)` | Button widget |
| `w.checkbox(label, checked=False)` | Checkbox |
| `w.radio(label, selected=False)` | Radio button |
| `w.text_field(value="", width=10)` | Text input field |
| `w.dropdown(*items, open=False)` | Dropdown / combobox |
| `w.separator(style="..")` | Horizontal divider |

### Layout and Container Methods

| Method | Description |
|--------|-------------|
| `w.grid(style, *children)` | Grid layout container |
| `w.row(*cells)` | Single row inside a grid |
| `w.menu(*items, sub_items=())` | Menu bar with optional sub-items |
| `w.tab_bar(*tabs, content=(), vertical=False)` | Tab bar container |
| `w.group_box(title, *children)` | Titled group box |
| `w.scrollbar(style, *children)` | Scrollbar container |
| `w.tree(*nodes, style="T")` | Tree widget (nodes are `(depth, label)` tuples) |

### Grid Styles

| Style | Draws |
|-------|-------|
| `"#"` | All lines (complete grid) |
| `"!"` | Vertical lines only |
| `"-"` | Horizontal lines only |
| `"+"` | External lines only (outer border) |

### Separator Styles

| Style | Appearance |
|-------|------------|
| `".."` | Dotted |
| `"=="` | Double line |
| `"~~"` | Wave |
| `"--"` | Dashed |

### Scrollbar Styles

| Style | Scrollbars |
|-------|------------|
| `"S"` | Both (vertical and horizontal) |
| `"SI"` | Vertical only |
| `"S-"` | Horizontal only |

### Tree Styles

| Style | Description |
|-------|-------------|
| `"T"` | Default tree lines |
| `"T!"` | Variant 1 |
| `"T-"` | Variant 2 |
| `"T+"` | Variant 3 |
| `"T#"` | Variant 4 |
