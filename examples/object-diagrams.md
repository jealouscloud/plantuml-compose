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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGZEp2q0KguLYI2QApyfApMvH44fCISpELN1IY6qEBL8II6nM04i41yFuiCLvHUbf1OP0bNvWnXWPH2X-7Ym21UI9WLTNJjKMQ2-Wfp4vDGKBeVKl1IWYm00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuSfFoafDBb5GIip9J4vLi588BKujKb98B5O02yJ7W_WmHOa51SxvUMcPwGXTARcPUI0bG9sE83P4AuZ5vP2QbmAq0G00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NP1DYy8m443l-HM3x4qgRQo7YfR2UlVakOp98974b6OA2ul_tT6g5M-JDrzlqYJ6deVW5Jls1FlUKWyxOdG-gNWyas6OnJijO3scPu09HjIsOyE_0d0Mjb3ePRcIXupb8GdO7EPvhdNTeRElMF8S6RsaVwfgKLK2J4_8T1-XSrrcUP4LAtLz6w1tXaJWTqWSmzFX0TlsnIQBKaj4GMxuC7XKD_I7eVEqC35ywZXfdqfFqK-oL_Mz9ylgh_lNq7aqP5L35ok_UGC0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuSfFoafDBb5GIamkoInBzIzAIIrIi580qqeAYSKAIEBnyH1fPP_Cz8mIzwBKr3o5QYu51Q1P9QN52hOADg7Q1WP6HdO5HVd9gSN5cNdfC16kMhX5QOcPEQafc1OXYQDQv9nVb9Y3tIA87YHB75BpKe2-0W00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/9SrB2iCm30JGlKuXl0-qT9qIw4dKM346_x2bRaBlNhbPpcE6sOPG5yq994fYVDLonA2T9DO2cHfIQnVY2OXSFhW-qRLUlUwpv4mzlpLCFoWDDf2OkQfCUjmiTmvM_IzrB4n3bhk3BsnSl9t_0000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NOz12eCm44NtESN7PQ6WBWkAToXTXoJE8XAJuenkIk_Ua5AnBcVUc_dyWSKiiiv1YPT0U30jk1EpJv5LiXCvGMM2TuHReHKCeooqBlPB0Nv4XqQzzmkRxD7FuzbkipsR9umJlz4lid2NrYZe-km0_2MwhXjShlqn-e-sXUv1-Vj0SSpDFW00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuSfFoafDBb5GIip9J4vLi588BKujKb98B5O02yJ7W_XmHSb0JOP0HSv06gm8B10V3-B35UKNfQGMWLJvWnXWPH2X-7Ym21UIoGgwkdR8XW1rvPVd5MCeGJ40gAWW9p4vDOKBMQUkBfer3gbvAK0V0W00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/JSzT2i8m3C3nzvuYx57O3k23h1ydy0AXpi8gjHMJtNyP6krJ2B_mXyp4yStRinZEN19SKucSMwKrlyYqsoCj38DC2sUm0qI2Oq6qFJf1f-WGNOzUq2jwHDzZ40oA0J6ORnvEuwWrkLbQvPWh_RXz-EW9h_4lqtJHcCX6YSoSwbr-t040)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NP1D3a1038NtJj7OpmKin0bSGJ3rbw4owlxAY5INVT-Nl9TM1xUHppLar2tOC-GzRemH2gZ9Omxj0IbfcZluDAPTEt8QeIDcMhMJ4gC575XBzssKE8_Jptc2LzBZmBdJbMgBWLxWRuJXGRZgDpGArSqLRbuUTm40)



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
![Diagram](https://www.plantuml.com/plantuml/svg/RO_12i8m44Jl-OgXU1CaBNWfAYr-W2VFPMssDT8c9TqYHVnteyM3u6rtc3SxMun2GQQ-K_vourgG-60ufCXnUWy9QCGYLTL7mKC1aP9fn1wxyrhhB3iCx8nrxNUD5l52NNIiqgtUQAsUodbX1DjU1Rxv3SrHtibAJC10SyzEK7lNsD2JMEyMjEFc7taCJC8c7ZGqgo8MYU-y0000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/VPJ1Rjim38RlVWgYwsc32rjDDYHOYxGz5Mkn0aRFWYAnYJPRzYGPM3RitKVBSQEesKvHVb7yVf6KLyuBw_kcphpsDS9Ngz12jNCU6wYCwDoszLcx_eRImvcejKHOmbtlVDkWFGFX88YSJnhypW2qWYkOCLfX8tHDVpu_VoWAngv3z0f_YgQhyKAspRH1iGqsQxILDWIv0bQm8YykytAU_Nbrq0x-vXy_aObWDJYOHCv7--yUz6RhR-iU3sPecvPqMz-xo4vdMudEQRE9VFZMYy7pELiiBXOBKgH5uL6DhcPvKUQiY5nfgbP9bXwqmNjQ1rT1v7pIWXN2gLxw-o5JMPIa_EY5eTBlXjGXG8VBdyy2-HZ1JY7OVn2ic1yZoXXHBX96BJhVTWHv6dC4nYXoljSE5Htz6z5WLC_dwZQ_Wnj5Xz2-blI0-8wxTIkiIY2JV08ptY71FABS2gCbjUdB_kW9c53A3csveLzgyZYjWyRvNWeOvosYZxANx18UXJPG-MWgv5Z2IQceZcRpeh5MKT0ltHqdciqZO-bJoVFhDyExXAuM4bMMRhpFytIc_XaJ3KMMpk40JPkw18ilQ95UdilIgHeEl6tGqP7Knt0agVGIt5PtZXvNjaAZw9Fp5m00)



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
