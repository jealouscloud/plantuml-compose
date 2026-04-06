# Object Diagrams

Object diagrams show specific instances and their relationships at a point in time. They capture concrete data snapshots, making them useful for debugging, test scenarios, and documentation with real values.

## Quick Start

```python
from plantuml_compose import object_diagram, render

d = object_diagram(title="Server Snapshot")
el = d.elements
r = d.relationships

node = el.object("vz-node-01 : Node", ref="n1", fields={
    "totalRAM": "64 GB",
    "usedMem": "58 GB",
})
ct = el.object("CT-101 : Container", ref="ct101", fields={
    "physpages.l": "8 GB",
})

d.add(node, ct)
d.connect(r.composition(node, ct))

print(render(d))
```

The pattern: create a diagram, get `el` (elements) and `r` (relationships) namespaces, build elements with `d.add()`, then wire them with `d.connect()`.

## Elements

### Objects

```python
from plantuml_compose import object_diagram, render

d = object_diagram()
el = d.elements

# Object with type annotation (instance : Type)
user = el.object("alice : User")

# Object without type
config = el.object("appConfig")

# With an explicit ref for relationships
admin = el.object("adminUser : Admin", ref="admin")

# With field values
order = el.object("order1 : Order", fields={
    "id": "12345",
    "status": '"paid"',       # include quotes for string values
    "total": "$99.99",
    "created": "2024-01-15",
})

# With stereotype
server = el.object("prod1 : Server", stereotype="primary")

# With background color
critical = el.object("alert1 : Alert",
    fields={"severity": '"high"'},
    style={"background": "LightCoral"},
)

d.add(user, config, admin, order, server, critical)

print(render(d))
```

Parameters: `name`, `ref=`, `fields=`, `stereotype=`, `style=`

### Maps

Maps are associative arrays displayed as key-value tables.

```python
from plantuml_compose import object_diagram, render

d = object_diagram(title="Configuration")
el = d.elements

# Map with plain entries
config = el.map("appConfig", entries={
    "env": '"production"',
    "debug": "false",
    "timeout": "30",
    "region": '"us-east-1"',
})

# Map with style
secrets = el.map("vault", entries={
    "api_key": '"****"',
    "db_pass": '"****"',
}, style={"background": "LightYellow"})

d.add(config, secrets)

print(render(d))
```

Parameters: `name`, `ref=`, `entries=`, `links=`, `style=`

### Maps with Linked Entries

Map entries can link to other objects, rendering as arrows from the map key to the target.

```python
from plantuml_compose import object_diagram, render

d = object_diagram(title="User Sessions")
el = d.elements

alice = el.object("alice : User", fields={"id": "1"})
bob = el.object("bob : User", fields={"id": "2"})

sessions = el.map("activeSessions",
    entries={"count": "2"},
    links={
        "session_001": alice,
        "session_002": bob,
    },
)

d.add(alice, bob, sessions)
print(render(d))
```

## Relationships / Connections

### arrow

A directed association.

```python
from plantuml_compose import object_diagram, render

d = object_diagram()
el = d.elements
r = d.relationships

user = el.object("alice : User")
order = el.object("order1 : Order")
d.add(user, order)

d.connect(r.arrow(user, order, "placed", style="dashed"))

print(render(d))
```

Parameters: `source`, `target`, `label=`, `style=`, `direction=`, `note=`, `length=`, `left_head=`, `right_head=`

### composition

Strong ownership -- the child cannot exist without the parent. Renders with a filled diamond.

```python
from plantuml_compose import object_diagram, render

d = object_diagram()
el = d.elements
r = d.relationships

order = el.object("order1 : Order")
line_item = el.object("item1 : LineItem")
d.add(order, line_item)

d.connect(r.composition(order, line_item, "contains"))

print(render(d))
```

Parameters: `source`, `target`, `label=`, `style=`, `direction=`, `note=`, `length=`

### aggregation

Weak ownership -- the child can exist independently. Renders with an open diamond.

```python
from plantuml_compose import object_diagram, render

d = object_diagram()
el = d.elements
r = d.relationships

department = el.object("eng : Department")
employee = el.object("alice : Employee")
d.add(department, employee)

d.connect(r.aggregation(department, employee, "has"))

print(render(d))
```

Parameters: `source`, `target`, `label=`, `style=`, `direction=`, `note=`, `length=`

### association

A plain directed connection (single arrowhead).

```python
from plantuml_compose import object_diagram, render

d = object_diagram()
el = d.elements
r = d.relationships

user = el.object("alice : User")
config = el.object("appConfig")
d.add(user, config)

d.connect(r.association(user, config, "reads"))

print(render(d))
```

Parameters: `source`, `target`, `label=`, `style=`, `direction=`, `note=`, `length=`

### link

An undirected line (no arrowheads by default).

```python
from plantuml_compose import object_diagram, render

d = object_diagram()
el = d.elements
r = d.relationships

a = el.object("server1 : Server")
b = el.object("server2 : Server")
d.add(a, b)

d.connect(r.link(a, b, "replicates"))

print(render(d))
```

Parameters: `source`, `target`, `label=`, `style=`, `direction=`, `note=`, `length=`, `left_head=`, `right_head=`

### extension

Inheritance arrow (triangle head).

```python
from plantuml_compose import object_diagram, render

d = object_diagram()
el = d.elements
r = d.relationships

parent_obj = el.object("base : Config")
child_obj = el.object("prod : ProdConfig")
d.add(parent_obj, child_obj)

d.connect(r.extension(child_obj, parent_obj, "extends"))

print(render(d))
```

Parameters: `source`, `target`, `label=`, `style=`, `direction=`, `note=`, `length=`

### implementation

Implementation arrow (dashed line, triangle head).

```python
from plantuml_compose import object_diagram, render

d = object_diagram()
el = d.elements
r = d.relationships

interface_obj = el.object("iCache : Cache")
concrete = el.object("redis1 : RedisCache")
d.add(interface_obj, concrete)

d.connect(r.implementation(concrete, interface_obj, "implements"))

print(render(d))
```

Parameters: `source`, `target`, `label=`, `style=`, `direction=`, `note=`, `length=`

### Custom Arrow Heads

Both `arrow()` and `link()` support `left_head=` and `right_head=` for custom arrowhead shapes. Common values: `|>`, `*`, `o`, `#`, `x`, `+`, `^`, `>>`.

```python
from plantuml_compose import object_diagram, render

d = object_diagram()
el = d.elements
r = d.relationships

a = el.object("nodeA : Node")
b = el.object("nodeB : Node")
d.add(a, b)

d.connect(r.arrow(a, b, left_head="hollow_diamond", right_head="closed_triangle"))

print(render(d))
```

### Inline Notes on Relationships

Every relationship type supports a `note=` parameter that renders a note attached to the connection line.

```python
from plantuml_compose import object_diagram, render

d = object_diagram()
el = d.elements
r = d.relationships

order = el.object("order1 : Order")
item = el.object("item1 : LineItem")
product = el.object("widget : Product")
d.add(order, item, product)

d.connect(
    r.composition(order, item, note="1..*"),
    r.arrow(item, product, "refs", note="by product ID"),
)

print(render(d))
```

### Bulk Methods

#### arrows()

Multiple arrows from `(source, target)` or `(source, target, label)` tuples:

```python
from plantuml_compose import object_diagram, render

d = object_diagram()
el = d.elements
r = d.relationships

user = el.object("alice : User")
order = el.object("order1 : Order")
cart = el.object("cart1 : Cart")
address = el.object("addr1 : Address")
d.add(user, order, cart, address)

d.connect(r.arrows(
    (user, order),
    (user, cart, "owns"),
    (order, address),
))

print(render(d))
```

#### arrows_from()

Fan-out from one source to many targets. Targets can be bare refs or `(target, label)` tuples:

```python
from plantuml_compose import object_diagram, render

d = object_diagram()
el = d.elements
r = d.relationships

user = el.object("alice : User")
order = el.object("order1 : Order")
cart = el.object("cart1 : Cart")
address = el.object("addr1 : Address")
d.add(user, order, cart, address)

d.connect(r.arrows_from(user,
    order,
    cart,
    (address, "lives at"),
    direction="down",
))

print(render(d))
```

Parameters: `source`, `*targets`, `style=`, `direction=`, `length=`

#### compositions_from()

One parent composes many children:

```python
from plantuml_compose import object_diagram, render

d = object_diagram()
el = d.elements
r = d.relationships

node = el.object("vz-node-01 : Node")
ct101 = el.object("CT-101 : Container")
ct102 = el.object("CT-102 : Container")
ct103 = el.object("CT-103 : Container")
d.add(node, ct101, ct102, ct103)

d.connect(r.compositions_from(
    node, [ct101, ct102, ct103],
    label="hosts",
    direction="down",
))

print(render(d))
```

Parameters: `parent`, `children`, `label=`, `style=`, `direction=`, `length=`

### hub()

The `hub()` method on the composer creates a hub-and-spoke pattern, connecting one central object to many spokes. Unlike bulk methods, this is called directly on the diagram, not on the relationships namespace.

```python
from plantuml_compose import object_diagram, render

d = object_diagram()
el = d.elements
r = d.relationships

router = el.object("gw1 : Router", fields={"ip": "10.0.0.1"})
switch1 = el.object("sw1 : Switch")
switch2 = el.object("sw2 : Switch")
switch3 = el.object("sw3 : Switch")
d.add(router, switch1, switch2, switch3)

d.hub(router, [switch1, switch2, switch3],
      label="connects",
      style="dashed",
      direction="down")

print(render(d))
```

Parameters: `hub`, `spokes`, `label=`, `style=`, `direction=`

## Notes

```python
from plantuml_compose import object_diagram, render

d = object_diagram()
el = d.elements

order = el.object("order1 : Order", fields={"status": '"pending"'})
d.add(order)

# Note attached to an object (default position is "right")
d.note("Awaiting payment", target=order)

# With explicit position
d.note("Created today", target=order, position="left")

# With color
d.note("Overdue!", target=order, position="top", color="LightCoral")

# Floating note (no target)
d.note("Snapshot taken at 14:30 UTC")

print(render(d))
```

Parameters: `content`, `target=`, `position=` (left/right/top/bottom), `color=`

## Layout & Organization

### Layout Direction

```python
from plantuml_compose import object_diagram, render

d = object_diagram(layout="left_to_right")

print(render(d))
```

Valid values: `"left_to_right"`, `"top_to_bottom"`

### Direction Hints on Relationships

```python
from plantuml_compose import object_diagram, render

d = object_diagram()
el = d.elements
r = d.relationships

center = el.object("hub : Router")
top_node = el.object("web : Server")
bottom_node = el.object("db : Database")
left_node = el.object("cache : Redis")
right_node = el.object("queue : RabbitMQ")
d.add(center, top_node, bottom_node, left_node, right_node)

d.connect(
    r.arrow(center, top_node, direction="up"),
    r.arrow(center, bottom_node, direction="down"),
    r.arrow(center, left_node, direction="left"),
    r.arrow(center, right_node, direction="right"),
)

print(render(d))
```

### Arrow Length

```python
from plantuml_compose import object_diagram, render

d = object_diagram()
el = d.elements
r = d.relationships

a = el.object("nodeA : Node")
b = el.object("nodeB : Node")
d.add(a, b)

d.connect(r.arrow(a, b, length=2))

print(render(d))
```

## Styling

### Element-Level Styles

```python
from plantuml_compose import object_diagram, render

d = object_diagram()
el = d.elements

active = el.object("active : Order",
    fields={"status": '"processing"'},
    style={"background": "LightGreen"},
)
failed = el.object("failed : Order",
    fields={"status": '"failed"'},
    style={"background": "LightCoral"},
)
config = el.map("config", entries={"k": "v"}, style={"background": "#E8F5E9"})

d.add(active, failed, config)

print(render(d))
```

### Line Styles on Relationships

```python
from plantuml_compose import object_diagram, render

d = object_diagram()
el = d.elements
r = d.relationships

a = el.object("nodeA : Node")
b = el.object("nodeB : Node")
d.add(a, b)

d.connect(r.arrow(a, b, style="dashed"))

print(render(d))
```

### diagram_style

Theme the entire diagram with CSS-like selectors:

```python
from plantuml_compose import object_diagram, render

d = object_diagram(
    title="Styled Diagram",
    diagram_style={
        "background": "white",
        "object": {"background": "#E3F2FD", "line_color": "#1976D2"},
        "map": {"background": "#C8E6C9"},
        "stereotypes": {
            "critical": {"background": "#FFCDD2", "font_style": "bold"},
        },
    },
)
el = d.elements
r = d.relationships

server = el.object("server : Node", ref="srv", fields={"ram": "64GB"}, stereotype="critical")
config = el.map("config", entries={"env": "prod", "region": "us-east"})
d.add(server, config)
d.connect(r.arrow(server, config, "reads"))

print(render(d))
```

Available selectors: `object`, `map`, `title`, `stereotypes`

Root-level properties: `background`, `font_name`, `font_size`, `font_color`

Note: PlantUML ignores `arrow` and `note` CSS selectors for object diagrams. Use inline `style=` and `note=` on individual relationships instead.

## Advanced Features

### Diagram Metadata

```python
from plantuml_compose import object_diagram, render
from plantuml_compose.primitives.common import Header, Footer, Legend, Scale

d = object_diagram(
    title="Production Snapshot",
    mainframe="Infrastructure State",
    caption="Figure 3: Node allocation at 14:30 UTC",
    header="Internal - Do Not Distribute",
    footer=Footer("Generated by plantuml-compose"),
    legend="Diamond = composition",
    scale=Scale(factor=1.5),
    theme="plain",
)

print(render(d))
```

### Complete Example

```python
from plantuml_compose import object_diagram, render

d = object_diagram(
    title="Order System Snapshot",
    layout="top_to_bottom",
    diagram_style={
        "object": {"background": "#FAFAFA"},
        "stereotypes": {
            "active": {"background": "#C8E6C9"},
        },
    },
)
el = d.elements
r = d.relationships

customer = el.object("alice : Customer", fields={
    "id": "42",
    "email": '"alice@example.com"',
    "memberSince": "2020-03-15",
})

order = el.object("order567 : Order",
    fields={
        "id": "567",
        "status": '"processing"',
        "total": "$299.99",
    },
    style={"background": "LightBlue"},
)

item1 = el.object("item1 : LineItem", fields={
    "productId": "101", "quantity": "2", "price": "$49.99",
})
item2 = el.object("item2 : LineItem", fields={
    "productId": "205", "quantity": "1", "price": "$199.99",
})

product1 = el.object("adapter : Product", fields={
    "id": "101", "name": '"USB-C Adapter"',
})
product2 = el.object("keyboard : Product", fields={
    "id": "205", "name": '"Mechanical Keyboard"',
})

address = el.object("addr1 : Address", fields={
    "street": '"123 Main St"',
    "city": '"Springfield"',
})

d.add(customer, order, item1, item2, product1, product2, address)

d.connect(
    r.arrow(customer, order, "placed"),
    r.compositions_from(order, [item1, item2]),
    r.arrow(item1, product1, "references"),
    r.arrow(item2, product2, "references"),
    r.arrow(order, address, "ships to"),
)

d.note("Awaiting fulfillment", target=order, color="LightYellow")

print(render(d))
```

## Quick Reference

| Method | Description |
|--------|-------------|
| `el.object(name)` | Create an object |
| `el.object(name, fields={...})` | Object with field values |
| `el.map(name, entries={...})` | Key-value map |
| `el.map(name, links={...})` | Map with linked entries |
| `r.arrow(a, b)` | Directed link |
| `r.link(a, b)` | Undirected line |
| `r.composition(a, b)` | Filled diamond (strong ownership) |
| `r.aggregation(a, b)` | Open diamond (weak ownership) |
| `r.association(a, b)` | Plain directed connection |
| `r.extension(a, b)` | Inheritance triangle |
| `r.implementation(a, b)` | Dashed inheritance |
| `r.arrows(*(src, tgt), ...)` | Bulk arrows from tuples |
| `r.arrows_from(src, *targets)` | Fan-out from one source |
| `r.compositions_from(parent, children)` | Bulk compositions |
| `d.hub(hub, spokes)` | Hub-and-spoke pattern |
| `d.add(*elements)` | Register elements |
| `d.connect(*relationships)` | Register connections |
| `d.note(text, target=, position=, color=)` | Attach a note |

### Element Parameters

| Parameter | Applies to | Description |
|-----------|-----------|-------------|
| `ref=` | object, map | Short name for programmatic access |
| `fields=` | object | `{"field": "value"}` dict |
| `entries=` | map | `{"key": "value"}` dict |
| `links=` | map | `{"key": entity_ref}` dict with arrows |
| `stereotype=` | object | UML `<<name>>` marker |
| `style=` | object, map | `{"background": "..."}` |

### Relationship Parameters

| Parameter | Applies to | Description |
|-----------|-----------|-------------|
| `label` | All relationships | Text on the connection |
| `style=` | All relationships | `"dashed"` or `{"color": "red", ...}` |
| `direction=` | All relationships | `"up"`, `"down"`, `"left"`, `"right"` |
| `length=` | All relationships | Arrow length (int) |
| `note=` | All relationships | Inline note on the connection |
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
| `diagram_style=` | Dict of CSS-like style selectors |

### Field Format

Fields are passed as dicts where keys are field names and values are string representations:

```text
fields={
    "id": "123",           # Number
    "name": '"Alice"',     # String (include quotes)
    "active": "true",      # Boolean
    "items": "[1, 2, 3]",  # Collection
}
```
