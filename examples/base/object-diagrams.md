# Object Diagrams

Object diagrams show specific instances at a point in time. They're ideal for:

- **Concrete examples**: Showing real data in class relationships
- **Debugging**: Visualizing data state
- **Test scenarios**: Illustrating expected data structures
- **Documentation**: Sample data for tutorials or specs

Unlike class diagrams (which show types), object diagrams show INSTANCES with actual values.

## Core Concepts

**Object**: An instance of a class with concrete values.

**Field**: An attribute with a specific value.

**Map**: A key-value collection (associative array).

**Link**: A relationship between specific instances.

The key difference from class diagrams:

| Class Diagram (types) | Object Diagram (instances) |
|-----------------------|---------------------------|
| `Order` | `order1 : Order` |
| `id: int` | `id = 12345` |
| `status: str` | `status = "paid"` |

## Your First Object Diagram

```python
from plantuml_compose import object_diagram

with object_diagram(title="Simple Example") as d:
    alice = d.object("alice : User")
    order = d.object("order1 : Order")

    d.arrow(alice, order, label="placed")

print(d.render())
```

## Objects

### Simple Objects

```python
from plantuml_compose import object_diagram

with object_diagram() as d:
    # Object with type annotation
    user = d.object("alice : User")

    # Object without type
    config = d.object("appConfig")

    # With alias for relationships
    admin = d.object("adminUser : Admin", alias="admin")

print(d.render())
```

### Objects with Fields

```python
from plantuml_compose import object_diagram

with object_diagram(title="Order Details") as d:
    order = d.object_with_fields(
        "order1 : Order",
        fields={
            "id": "12345",
            "status": '"paid"',
            "total": "$99.99",
            "created": "2024-01-15",
        }
    )

    customer = d.object_with_fields(
        "alice : Customer",
        fields={
            "id": "42",
            "email": '"alice@example.com"',
            "tier": '"gold"',
        }
    )

    d.arrow(customer, order, label="placed")

print(d.render())
```

### Styled Objects

```python
from plantuml_compose import object_diagram

with object_diagram() as d:
    active = d.object_with_fields(
        "activeOrder : Order",
        fields={"status": '"processing"'},
        style={"background": "LightGreen"}
    )

    error = d.object_with_fields(
        "failedOrder : Order",
        fields={"status": '"failed"'},
        style={"background": "LightCoral"}
    )

print(d.render())
```

## Maps (Key-Value Collections)

```python
from plantuml_compose import object_diagram

with object_diagram(title="Configuration") as d:
    config = d.map(
        "appConfig",
        entries={
            "env": '"production"',
            "debug": "false",
            "timeout": "30",
            "region": '"us-east-1"',
        }
    )

print(d.render())
```

### Maps with Linked Entries

```python
from plantuml_compose import object_diagram

with object_diagram(title="User Sessions") as d:
    alice = d.object_with_fields("alice : User", fields={"id": "1"})
    bob = d.object_with_fields("bob : User", fields={"id": "2"})

    # Map with links to other objects
    sessions = d.map(
        "activeSessions",
        entries={"count": "2"},
        links={
            "session_001": alice,
            "session_002": bob,
        }
    )

print(d.render())
```

## Relationships

### Simple Links

```python
from plantuml_compose import object_diagram

with object_diagram() as d:
    user = d.object("alice : User")
    cart = d.object("cart1 : Cart")
    order = d.object("order1 : Order")

    # Arrow (directed)
    d.arrow(user, cart, label="owns")
    d.arrow(user, order, label="placed")

    # Link (undirected)
    d.link(cart, order)

print(d.render())
```

### Relationship Types

```python
from plantuml_compose import object_diagram

with object_diagram(title="Relationships") as d:
    a = d.object("objA : A")
    b = d.object("objB : B")
    c = d.object("objC : C")
    d_obj = d.object("objD : D")

    # Different relationship types
    d.relationship(a, b, type="composition", label="contains")
    d.relationship(a, c, type="aggregation", label="has")
    d.relationship(a, d_obj, type="dependency", label="uses")

print(d.render())
```

### Direction Hints

```python
from plantuml_compose import object_diagram

with object_diagram() as d:
    center = d.object("center : Node")
    top = d.object("top : Node")
    bottom = d.object("bottom : Node")
    left = d.object("left : Node")
    right = d.object("right : Node")

    d.arrow(center, top, direction="up")
    d.arrow(center, bottom, direction="down")
    d.arrow(center, left, direction="left")
    d.arrow(center, right, direction="right")

print(d.render())
```

## Notes

```python
from plantuml_compose import object_diagram

with object_diagram() as d:
    order = d.object_with_fields(
        "order1 : Order",
        fields={"status": '"pending"', "total": "$150.00"}
    )

    # Note attached to object
    d.note("Awaiting payment confirmation", target=order)

    # Note with position
    d.note("Created today", position="left", target=order)

print(d.render())
```

## Complete Example: E-Commerce Snapshot

```python
from plantuml_compose import object_diagram

with object_diagram(title="Order System Snapshot") as d:
    # Customer instance
    customer = d.object_with_fields(
        "alice : Customer",
        fields={
            "id": "42",
            "email": '"alice@example.com"',
            "memberSince": "2020-03-15",
        }
    )

    # Active order
    order = d.object_with_fields(
        "order567 : Order",
        fields={
            "id": "567",
            "status": '"processing"',
            "total": "$299.99",
            "created": "2024-01-20",
        },
        style={"background": "LightBlue"}
    )

    # Line items
    item1 = d.object_with_fields(
        "item1 : LineItem",
        fields={
            "productId": "101",
            "quantity": "2",
            "price": "$49.99",
        }
    )

    item2 = d.object_with_fields(
        "item2 : LineItem",
        fields={
            "productId": "205",
            "quantity": "1",
            "price": "$199.99",
        }
    )

    # Product references
    product1 = d.object_with_fields(
        "laptop : Product",
        fields={
            "id": "101",
            "name": '"USB-C Adapter"',
        }
    )

    product2 = d.object_with_fields(
        "keyboard : Product",
        fields={
            "id": "205",
            "name": '"Mechanical Keyboard"',
        }
    )

    # Shipping address
    address = d.object_with_fields(
        "addr1 : Address",
        fields={
            "street": '"123 Main St"',
            "city": '"Springfield"',
            "zip": '"12345"',
        }
    )

    # Relationships
    d.arrow(customer, order, label="placed")
    d.relationship(order, item1, type="composition")
    d.relationship(order, item2, type="composition")
    d.arrow(item1, product1, label="references")
    d.arrow(item2, product2, label="references")
    d.arrow(order, address, label="ships to")

print(d.render())
```

## Quick Reference

| Method | Description |
|--------|-------------|
| `d.object(name)` | Simple object |
| `d.object_with_fields(name, fields)` | Object with field values |
| `d.map(name, entries)` | Key-value map |
| `d.arrow(a, b)` | Directed link |
| `d.link(a, b)` | Undirected link |
| `d.relationship(a, b, type)` | Typed relationship |
| `d.note(text, target)` | Add note |

### Field Format

Fields are passed as a dictionary where keys are field names and values are the string representation:

```python
fields={
    "id": "123",           # Number
    "name": '"Alice"',     # String (include quotes)
    "active": "true",      # Boolean
    "items": "[1, 2, 3]",  # Collection
}
```
