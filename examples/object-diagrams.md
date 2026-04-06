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
![Diagram](https://www.plantuml.com/plantuml/svg/FOx12i8m44Jl-OgXHo5YG4K4eTg3ftgm_a1i5rj9av9i2oh-ksaLRyjZviscWRNdlZM26pQ4Wln07eNLNQWT2tUzKyb8XgUqhYAvKDZY5Ay4Ei0gl0J0ZhKvxtFii5xYU8Ye3rJbr4Qosepa_JTb5wacI-OiwyQIdrGbZtIqTVKZTFf6OMvY_TUEIpCflocHagtYony0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/JP11Ry8m38Nl_HKMx3OnjHaSEdKLYEka7IREKTO4oDGsaMEGqCH_dzr2n-tvytlHYzU93DAfQxFm_UCQWfbfVUFW3NR9uGnCWW5eBVFTP6BSXdxl3_yfs_bUB9pSY1wZeYPFGEkmOCEdYC4m8gq70hyPWBVm3eLwNQvuu79qIWogtNEUArL7u-rTyvu2cPRNJsNvKfOC6dI6d3oXShLSvCMYM6NNgK74OAN0byFphS60j1u9L5L4tncyrFN3GHoIf3OYRYSHfFL0OFxX3qVQ1kGkyeNa-2bFbuVUHtPClQ_PslMMR_u7)



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
![Diagram](https://www.plantuml.com/plantuml/svg/JOv12i8m44NtESLGTqB1ubefkFK2hihKJcCmJK8oKn7ftKtYnjdzn_-ywHDZP5ciOiEMuEBTRBH4PEETMZ00Xl23y540v5OudQ49qKzoBwKcqub6qONFQ1Dbm6OXBrpGyP1p99shTIcf9KpSTetQgc15iGoxgz4Flf6r_bLD6Cpmf7VTxFDLppW4JEcFRQedD-N_lm00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NOz12eCm44NtESN7PQ6WBWkAToXTXoJE8XAJuenkIk_Ua5AnBcVUc_dyWSKiiiv1YPT0U30jk1EpJv5LiXCvGMM2TuHReHKCeooqBlPB0Nv4XqQzzmkRxD7FuzbkipsR9umJlz4lid2NrYZe-km0_2MwhXjShlqn-e-sXUv1-Vj0SSpDFW00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuSfFoafDBb5GIip9J4vLi588BKujKb98B5O02yJ7W_XmHVb5AQb5Xa1L_Y06M1b4A3uUBCA5f4b1DpebiJWZDILMrmvL5L1_GKvYSceAbqDgNWhG4G00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuSfFoafDBb5GoYzAIIqoLB1Iy0Snb1GIYnKWGl7nO16umioIr5oGEf_Cl5HF81ki52mO7myJuqBHgg2bgukk0cX0SdvUIM9cNZ6NGsfU2j0f0000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuSfFoafDBb5GIirBLx1IS4aj08hdfkQLA2aa5Yi01UFZ4M9mnOavcScfGEMkkGKv-PMfgM35OC7uU9WO5vfcXNnTNNGrG2Co4ekv75BpKe1k0G00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuSfFoafDBb5GIip9J4vLi588BKujKb98B5O02yJ7W_WmHOa51SxvUMcPwLn8aWgwkWW9e055gOafnLmEgNafGEC1)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuSfFoafDBb5GAaujAaijCbImKWW6ivGK4eiLe8BnyH0nDCL6s1GRmHMZQLRGrKLN0jHVb5gGavcSM99QpEMGcfS2T140)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuSfFoafDBb5GIaeiJbMmKd3EpqlBJ5TII2nM08d4nqC4uCeAYl9JWCe2W1IIKf1eV3n2a0jTGC6cHbSNnKIW8QaL9QbvASLS3a0Iw1G0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuSfFoafDBb5GodHEJCv8LR1I0DDA2ed52X2X-7Wm1LTOb9gIMMm8L1W4OY1KGyJZun72N9X22ZOrUdge1WDDoimjo4dDJSqhAUPoICrB0JeB0000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuSfFoafDBb5GoijFINLKi5Bm0z9A2ed52c21-7WG7qMH4xeY9wWY90qA-RgwDNOeiWwfUIb0-m00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/PP3B2eCm44Nt-Oh1fH31hOlYeXkXqFx1e6OiQJKfoKZftpV61pJTNSwSkGDJUsuTpzCeRFUWdY6pJf4heOBh4Z9eFQm8CP93r4pJubsqeIRag4Q8kBD3Vcjr9mxspLarznpb5I9kJFpSWLpAlpfZcS0Q6BLvLb0MHIuI1QGyfSNXhAF19zlT1rxRl3cBcemAR_W2)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NP0z3iCW34PtJc5bpz2rGvMe1yZKsQBW8LKI94pLwzTselmm6JyU_YmwBZwNxpovzFvGAD3uQGm4TtWnvGOyWm54xNSfvKZv9jQW1zDMX6Xa5uDCL-yfrJG3YDeVaJ7Qi5ugCQ-foX0tv4vBGDi-ghJwzXGYOzDlONTvO5ALqD4IvH_-)



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
![Diagram](https://www.plantuml.com/plantuml/svg/PP0n3i8m34NtdCBgtg4h0ohY09sOhH1xA4fRAGwS7zj5fT39yVUJdvLUQYprEUMmt1-SAZGnZudX13VXqa0Ky03H-WrQ2d7fb1hiuTWQ8NgoWKct6tVLwfW7YDP_bKI-xAALHLQhPOYVAEoEW9RQyv_kCDvh3iFVtIhEuujLMKFFC-bdl040)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuSfFoafDBb5GAglIpSjFITKrC5ImKl03ifGK4eiLogf0WWQ6yV4W8RXYvn1TGx12v_oyaiJClDGYi6hd44EGKhWWgdeZhEgDSAetnghU65azglCKj7HJT34S0JGb8x-uf1YdOYDI51jZK-oGcfS234i0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuSfFoafDBb5GIYytLB1I2CelBKajKb98B5O02iJ7G_WArLmA2fa52hOAXWPw86Z8LGlNM0pM65oUMPAS0TPO3D88uICfCa9NP8H5aJ6w8cEu8cJdw4Qd91PdfAR4fkZQ8Li7r9sSdvS7DAmOdteZ4jKROrFla9gN0Wm_0000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/RP2z2i9048JxUufHIvluKmKL9QrWeQd3wcrYDDw5oqO9uhjxCGYAThl3jplCB2iX9_MbK7P_ueEWRvrcDqA8JJlqGHKwAKbU2kuAy5TILvXZ5W-3O3nUb6nqRhBtgXxAM66uF3jAYAsXiZfQWT2P3KWmceQJ0F4k-k1Wqs-h4AiRvUB_egJcmaOwkk3q7nmv9c4DiPgQZXHR_e0Oh5kto3egVCehErrpJorz0j_34m00)



Parameters: `content`, `target=`, `position=` (left/right/top/bottom), `color=`

## Layout & Organization

### Layout Direction

```python
from plantuml_compose import object_diagram, render

d = object_diagram(layout="left_to_right")

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuSf9JIjHACbNACfCpoXHICaiIaqkoSpFut98pKi1oWC0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NP0n3i8m34NtdiBgtWime0wi3C018gUnrA92HMBJw-Eu9IACVlz9_yjzOemiZxbP_9q6XdOK3mUuBi8KMy042fpRxYAjbAKRnVSkAN1kkuiKidD2He-9p0egVK7H1Xn6ofKKfcIQ4UtCe6Wl8J4DlP_uV37Je9exQtwsGYVTiTfLXK73QawLpffMAweqQlhVtDCpw1i_)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuSfFoafDBb5GoijFINLKi5Bm0z9A2ed52c21-7WG7qMH4xeY9wWY90qAkhfsA78EgNafGDi0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/RSz12u9048RX-_wA3prs4I6eI172kWITEiksZhQckxAxUed-U-9I97HzP-Q1oQpZnWrTo_Ij8U4GSE7aIDZXOaeo0RY5JqKn5uHdMT_ToH0fF1am2MwmIB2_hg8eZjFUQ47MIbL_2djz-OhBbie5xzEIFsZ3s_-yN_-XEzv3Q5N96c6-EQxpxNpuG99YdEOPgNBwy0q0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuSfFoafDBb5GoijFINLKi5Bm0z9A2ed52c21-7WG7qMH4xeY9wWY90qAkj4fYSKPgIcnkdOeQXnIyrA0jW80)



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
![Diagram](https://www.plantuml.com/plantuml/svg/TP51JiCm44NtFiMeNGT4GO5MgLKrgTaWDfp0ZQV1nV5KjXE4KE-ERT85GbruuJzl_f-nDpv85uRUiA23GNWBNmOLD5fsJlQiykdE6UsFs8P9XMy6i9NjH-TeiAecGmu-ttN0gF-I6VaFpNVtOY6QN7lH5YVrRlbODekedkFfvUbQT_sqA-lbnDsqJWVTIdED5g9kiYk081loPh0dexB1cLMtVvQ3cKSteeCLl9B26KWFterGLPSWpdDKUe4rb0_FssYIfct97dINQsX7M7CuEKef3ZjDDWc3Br3w41kIPL7mIzCgGb9vja6huY_y0000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/BOv12W8n34NtFKKyWAACRWH1K1Gt8gW7Y6rq2cqoj9c5jpTLD_qD_v6NRLKiEkRaCaP-5im4fvPLo-XrB0HNHIKtqPwi6v9XhdfC18lPocbK-rsA1AEZC5mPXzgBEa-iLA0d31QdDZ0ccC9Uu2mA-sYA-1XjznzzYhGu4bCnPO37k_cudJVraWUfnkBmzHpYgntNhMrP8C2KnEEtGON5SjtDuNxRkKGluk30T9Y50spWjoasrbdt9xRscES3)



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
![Diagram](https://www.plantuml.com/plantuml/svg/VPHHRzem4CVVyobERPysfKlIqWr4gmBRf6gjDWdrOK-HIGxmwjYPVLc7fdxtNHmoGWeJgd3_Fljtzxypjuw4fQfG0KbI25zjZXRc6qTOm5oBqgqD1MHA80CBGsGAoAN5ZAJHmTZHHk5DO1O_MFaenSgA0lu408tYbm1JaJsjhAbqFZFAM3ZzFAa_lFV2V-U2B_k5ns9d7pvTpOO-zYKOlziZmebGCaCOmQnod1hQ4n0El9YchUPlbZbSmsN2Aoo4LFpF-F5j52N9ZO--nT-YA1MUPwPeDpYsm6A1TYurGwuXYP8eZ2x2UC2fj1cOsh71rNjEmfldCsZ5D6qCFRsNgpLDLOMxP7YRb-m_LQwJJcbDXiv9lUhaGOP4dVDPCXoU3uSTlEH6nSo-bnhlUEtnNapJLlDClZUlChghqN4Ki_Ap4fgxlgahym7ILtbsUG2H748a_q4aqM0V4NSHSRyCaOkIsAWHV6ikQHhPg6cw5NVcDHLeKM37kiVvD9p1f3dqpxqTv0at2oDitgEqyW5CKqKFyu3PMcYPSKU-R8yUW8ayjtLZ9lpD_TpMmrgQRYMFSMGHgNDxd5p0Wv0QvjGPWAmniLNcxAHUBIMgBhe_zs5uyseIHr0gaM4Uz3VUX65_Rex6T1eVz6UjXhxgsmWiBj4YloCNz4UdFl6w1tj7-eaqa3qpH-3MidJyL09j2C7MBmxCyiXR_8vAcMTkpxEGn5x2ib9BgLI1ce9Rr3d_9lu5)



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
