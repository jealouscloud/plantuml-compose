# Use Case Diagrams

Use case diagrams show what a system does from the user's perspective. They capture functional requirements, system boundaries, and actor interactions.

## Quick Start

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram(title="Simple System")
el = d.elements
r = d.relationships

user = el.actor("User")
login = el.usecase("Login")
browse = el.usecase("Browse")

d.add(user, login, browse)
d.connect(
    r.arrow(user, login),
    r.arrow(user, browse),
)

print(render(d))
```

The pattern: create a diagram, get the `el` (elements) and `r` (relationships) namespaces, build elements, `d.add()` them, then `d.connect()` relationships.

## Elements

### Actors

```python
from plantuml_compose import usecase_diagram

d = usecase_diagram()
el = d.elements

# Basic actor
user = el.actor("Customer")

# With a stereotype
admin = el.actor("Admin", stereotype="privileged")

# With background color
guest = el.actor("Guest", style={"background": "LightGray"})

# Business actor (rendered with a different icon)
partner = el.actor("Partner", business=True)

# With an explicit ref for programmatic access
api = el.actor("External API", ref="ext_api")

d.add(user, admin, guest, partner, api)
```

Parameters: `name`, `ref=`, `stereotype=`, `style=`, `business=`

### Use Cases

```python
from plantuml_compose import usecase_diagram

d = usecase_diagram()
el = d.elements

# Basic use case
login = el.usecase("Login")

# With stereotype
checkout = el.usecase("Checkout", stereotype="critical")

# With background color
reports = el.usecase("Admin Panel", style={"background": "LightBlue"})

# Business use case
audit = el.usecase("Audit Trail", business=True)

d.add(login, checkout, reports, audit)
```

Parameters: `name`, `ref=`, `stereotype=`, `style=`, `business=`

### Containers: Package and Rectangle

Containers group use cases inside a system boundary. Children are passed as positional args and accessed by `ref` or name.

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram(title="E-Commerce")
el = d.elements
r = d.relationships

customer = el.actor("Customer")
admin = el.actor("Admin")

# Rectangle as system boundary
system = el.rectangle("E-Commerce Platform",
    el.usecase("Browse Products", ref="browse"),
    el.usecase("Search", ref="search"),
    el.usecase("Checkout", ref="checkout"),
    el.usecase("Manage Inventory", ref="manage"),
)

d.add(customer, admin, system)
d.connect(
    r.arrow(customer, system.browse),       # access child by ref
    r.arrow(customer, system.search),
    r.arrow(customer, system.checkout),
    r.arrow(admin, system.manage),
)

print(render(d))
```

Packages work the same way:

```text
shopping = el.package("Shopping",
    el.usecase("Browse", ref="browse"),
    el.usecase("Search", ref="search"),
    stereotype="frontend",
    style={"background": "#F5F5F5"},
)

# Access children by name with bracket syntax
shopping["Browse"]   # equivalent to shopping.browse
```

Both `package()` and `rectangle()` accept `stereotype=` and `style=`.

## Relationships / Connections

### arrow

A directed association between two elements. The most common relationship type.

```text
r.arrow(customer, login)
r.arrow(customer, login, "authenticates")  # with label
r.arrow(customer, login, direction="right")  # layout hint
r.arrow(customer, login, length=2)  # longer arrow
r.arrow(customer, login, style="dashed")  # line style
r.arrow(customer, login, style={"color": "red", "pattern": "dashed"})
```

Parameters: `source`, `target`, `label=`, `style=`, `direction=`, `length=`, `left_head=`, `right_head=`

### generalizes

Inheritance: child is-a parent. Renders as a triangle-headed arrow.

```text
# Admin inherits from User
r.generalizes(admin, user)
r.generalizes(admin, user, direction="up")
```

Parameters: `child`, `parent`, `style=`, `direction=`, `length=`

### include

The base use case always invokes the required use case. Renders with `<<include>>` label.

```text
# Checkout always validates the cart
r.include(checkout, validate_cart)
```

Parameters: `base`, `required`, `style=`, `direction=`, `length=`

### extends

The extension optionally extends the base use case. Renders with `<<extends>>` label.

```text
# Apply Coupon optionally extends Checkout
r.extends(apply_coupon, checkout)
```

Parameters: `extension`, `base`, `style=`, `direction=`, `length=`

### link

An undirected line between two elements (no arrowhead by default).

```text
r.link(actor_a, actor_b)
r.link(actor_a, actor_b, "collaborates")  # with label
r.link(actor_a, actor_b, left_head="|>", right_head="*")  # custom heads
```

Parameters: `source`, `target`, `label=`, `style=`, `direction=`, `length=`, `left_head=`, `right_head=`

### Custom Arrow Heads

Both `arrow()` and `link()` support `left_head=` and `right_head=` for custom arrowhead shapes. Common PlantUML head values include `|>`, `*`, `o`, `#`, `x`, `+`, `^`, `>>`.

```text
r.arrow(a, b, left_head="|>", right_head="*")
r.link(a, b, left_head="o", right_head="#")
```

### Bulk Methods

#### arrows()

Multiple independent arrows from `(source, target)` or `(source, target, label)` tuples:

```text
d.connect(r.arrows(
    (customer, browse),
    (customer, search),
    (customer, checkout, "buys"),
    (admin, manage),
))
```

#### arrows_from()

Fan-out from one source to many targets. Targets can be bare refs or `(target, label)` tuples:

```text
d.connect(r.arrows_from(customer,
    browse,
    search,
    (checkout, "buys"),
    style="dashed",
    direction="right",
    length=2,
))
```

Parameters: `source`, `*targets`, `style=`, `direction=`, `length=`

#### generalizes_from()

Multiple children inherit from one parent:

```text
d.connect(r.generalizes_from(
    [oncall_eng, platform_eng, network_eng],
    engineer,
    direction="up",
))
```

Parameters: `children`, `parent`, `style=`, `direction=`, `length=`

## Notes

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram()
el = d.elements
r = d.relationships

customer = el.actor("Customer")
checkout = el.usecase("Checkout")
d.add(customer, checkout)
d.connect(r.arrow(customer, checkout))

# Note on an element (default position is "right")
d.note("Requires valid payment", target=checkout)

# With explicit position
d.note("Primary flow", target=checkout, position="left")

# With color
d.note("Warning!", target=checkout, position="top", color="LightCoral")

# Floating note (no target)
d.note("System v2.1")

print(render(d))
```

Parameters: `content`, `target=`, `position=` (left/right/top/bottom), `color=`

## Layout & Organization

### Layout Direction

Set the overall diagram flow direction:

```python
from plantuml_compose import usecase_diagram

# Default is top to bottom
d = usecase_diagram(layout="left_to_right")
```

Valid values: `"left_to_right"`, `"top_to_bottom"`

### Direction Hints on Relationships

Fine-tune individual connection placement:

```text
d.connect(
    r.arrow(user, top_uc, direction="up"),
    r.arrow(user, bottom_uc, direction="down"),
    r.arrow(user, left_uc, direction="left"),
    r.arrow(user, right_uc, direction="right"),
)
```

### Arrow Length

Increase arrow length to push elements apart:

```text
r.arrow(a, b, length=2)   # longer than default
r.arrow(a, b, length=3)   # even longer
```

## Styling

### Actor Style

Change the visual representation of all actors:

```python
from plantuml_compose import usecase_diagram

# Stick figure (default)
d = usecase_diagram(actor_style="default")

# Awesome (person icon)
d = usecase_diagram(actor_style="awesome")

# Hollow (outline only)
d = usecase_diagram(actor_style="hollow")
```

### Element-Level Styles

Use `style={"background": "..."}` on individual elements:

```text
el.actor("VIP", style={"background": "Gold"})
el.usecase("Critical Path", style={"background": "#FFCDD2"})
el.package("Core", el.usecase("X", ref="x"), style={"background": "LightCyan"})
```

### Line Styles on Relationships

```text
# String shorthand
r.arrow(a, b, style="dashed")
r.arrow(a, b, style="dotted")

# Dict form with full control
r.arrow(a, b, style={"color": "red", "pattern": "dashed", "bold": True})
```

### diagram_style

Theme the entire diagram with a `<style>` block. Pass a dict with element selectors:

```python
from plantuml_compose import usecase_diagram

d = usecase_diagram(
    title="Styled Diagram",
    diagram_style={
        "background": "white",
        "font_name": "Arial",
        "font_size": 13,
        "font_color": "#333333",
        "actor": {"background": "#E3F2FD", "line_color": "#1976D2"},
        "usecase": {"background": "#FFF9C4", "line_color": "#F9A825"},
        "package": {"background": "#F5F5F5"},
        "rectangle": {"background": "#FAFAFA", "line_color": "#BDBDBD"},
        "arrow": {"line_color": "#757575"},
        "note": {"background": "#FFF8E1"},
        "title": {"font_size": 18, "font_style": "bold"},
        "stereotypes": {
            "critical": {"background": "#FFCDD2", "font_style": "bold"},
            "external": {"line_color": "#9E9E9E", "font_style": "italic"},
        },
    },
)
```

Available selectors: `actor`, `usecase`, `package`, `rectangle`, `arrow`, `note`, `title`, `stereotypes`

Root-level properties: `background`, `font_name`, `font_size`, `font_color`

Each element selector accepts an `ElementStyleDict` with keys like `background`, `line_color`, `font_color`, `font_name`, `font_size`, `font_style`, `round_corner`, `line_thickness`, `padding`, `margin`, `shadowing`.

The `arrow` selector accepts a `DiagramArrowStyleDict` with `line_color`, `line_thickness`, `line_style`.

The `stereotypes` key maps stereotype names to `ElementStyleDict` values, styling all elements bearing that stereotype.

## Advanced Features

### Diagram Metadata

```python
from plantuml_compose import usecase_diagram, render
from plantuml_compose.primitives.common import Header, Footer, Legend

d = usecase_diagram(
    title="My System",
    mainframe="System Overview",
    caption="Figure 1: Use case overview",
    header="Draft v0.3",
    footer="Confidential",
    legend="Arrows = interactions",
    scale=1.5,
    theme="plain",
)
```

### Complete Example

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram(
    title="Online Banking",
    layout="left_to_right",
    actor_style="awesome",
    diagram_style={
        "actor": {"background": "#E3F2FD"},
        "usecase": {"background": "#FFFDE7"},
        "arrow": {"line_color": "#616161"},
    },
)
el = d.elements
r = d.relationships

customer = el.actor("Customer")
teller = el.actor("Bank Teller")
admin = el.actor("Admin")

bank = el.rectangle("Online Banking",
    el.usecase("Login", ref="login"),
    el.usecase("View Balance", ref="balance"),
    el.usecase("Transfer Funds", ref="transfer"),
    el.usecase("Pay Bills", ref="bills"),
    el.usecase("Authenticate", ref="auth"),
    el.usecase("Audit Log", ref="audit"),
    el.usecase("Two-Factor Auth", ref="tfa"),
    el.usecase("Email Receipt", ref="receipt"),
    el.usecase("Manage Users", ref="manage"),
    el.usecase("View Reports", ref="reports"),
)

d.add(customer, teller, admin, bank)

d.connect(
    r.generalizes(teller, customer),

    r.arrows_from(customer,
        bank.login, bank.balance, bank.transfer, bank.bills),

    r.include(bank.login, bank.auth),
    r.include(bank.transfer, bank.audit),
    r.include(bank.bills, bank.audit),

    r.extends(bank.tfa, bank.auth),
    r.extends(bank.receipt, bank.transfer),
    r.extends(bank.receipt, bank.bills),

    r.arrows_from(admin, bank.manage, bank.reports),
)

d.note("MFA required for transfers > $1000",
       target=bank.tfa, position="right", color="LightYellow")

print(render(d))
```

## Quick Reference

| Method | Description |
|--------|-------------|
| `el.actor(name)` | Create an actor |
| `el.actor(name, business=True)` | Business actor variant |
| `el.usecase(name)` | Create a use case |
| `el.usecase(name, business=True)` | Business use case variant |
| `el.rectangle(name, *children)` | System boundary |
| `el.package(name, *children)` | Package grouping |
| `r.arrow(source, target)` | Directed association |
| `r.link(source, target)` | Undirected line |
| `r.generalizes(child, parent)` | Inheritance |
| `r.include(base, required)` | `<<include>>` dependency |
| `r.extends(extension, base)` | `<<extends>>` dependency |
| `r.arrows(*(src, tgt), ...)` | Bulk arrows from tuples |
| `r.arrows_from(src, *targets)` | Fan-out from one source |
| `r.generalizes_from(children, parent)` | Multiple children inherit |
| `d.add(*elements)` | Register elements |
| `d.connect(*relationships)` | Register connections |
| `d.note(text, target=, position=, color=)` | Attach a note |

### Element Parameters

| Parameter | Applies to | Description |
|-----------|-----------|-------------|
| `ref=` | All elements | Short name for programmatic access |
| `stereotype=` | actor, usecase, package, rectangle | UML `<<name>>` marker |
| `style=` | All elements | `{"background": "..."}` |
| `business=` | actor, usecase | Business variant rendering |

### Relationship Parameters

| Parameter | Applies to | Description |
|-----------|-----------|-------------|
| `label` | arrow, link | Text on the connection |
| `style=` | All relationships | `"dashed"` or `{"color": "red", ...}` |
| `direction=` | All relationships | `"up"`, `"down"`, `"left"`, `"right"` |
| `length=` | All relationships | Arrow length (int) |
| `left_head=` | arrow, link | Custom left arrowhead |
| `right_head=` | arrow, link | Custom right arrowhead |

### Diagram Options

| Parameter | Description |
|-----------|-------------|
| `title=` | Diagram title |
| `mainframe=` | Mainframe label |
| `caption=` | Caption text below diagram |
| `header=` | Header text |
| `footer=` | Footer text |
| `legend=` | Legend text |
| `scale=` | Scale factor (float) |
| `theme=` | PlantUML theme name |
| `layout=` | `"left_to_right"` or `"top_to_bottom"` |
| `actor_style=` | `"default"`, `"awesome"`, `"hollow"` |
| `diagram_style=` | Dict of CSS-like style selectors |
