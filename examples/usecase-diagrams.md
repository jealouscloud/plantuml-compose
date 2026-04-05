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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGZEp2q0KPN59QcvN8d99Vb52g75gKLSfSMfoOd5gGeQFldfcNcQ2BvJKNvvSQec5qYLWgwkdG9O0O8BaUToICrB0Le30000)



The pattern: create a diagram, get the `el` (elements) and `r` (relationships) namespaces, build elements, `d.add()` them, then `d.connect()` relationships.

## Elements

### Actors

```python
from plantuml_compose import usecase_diagram, render

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

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/FOtH2a1044NVVSN41_W1YIGf3_v0avsOsbsQdHL_Jv77UqwTMmL5qUXiWhDk0aqCkZcIRzR6iOUYs8KFjhIGASjFTP62GZRmicedUBquX_7f-J-GjgUIUBHGZtqA681EdN3df29ldjyR)



Parameters: `name`, `ref=`, `stereotype=`, `style=`, `business=`

### Use Cases

```python
from plantuml_compose import usecase_diagram, render

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

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/HSun2iCm38NXFQSGwL9FlO09QR9cw90z25iaeeuDjdJ_DWQJKP_uuOr5C8kUeTD23Wl1SqaxHtFVyq7kcrGCMEio2piCmt3_-xS_ES878uNU01Qei5M0nyBx8LDGQiNhIjIpm9gHMtB1Lg4RAVh_eXy0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/LP313i8W38RlF4N3IGzx1JDTF7WmCV49QbUtnG4958qnlhi4cMwtzliB7wKEWbwY6PKCCZBigyOPmvvO8OdpqCGWBe7IRbipMEMP16sNvlN_09n6bAlpHiDB0SJ0X85XfNVUFL9nygwD946l0GDSCfpFdHazzJaCkPo7JSzqSr5oJALPM8veiMCus3lRzDBdLsCoLMyrxG5LjPda2rQS2_OJvRKpAXVMRDlqQny0)



Packages work the same way:

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram()
el = d.elements
r = d.relationships

customer = el.actor("Customer")
shopping = el.package("Shopping",
    el.usecase("Browse", ref="browse"),
    el.usecase("Search", ref="search"),
    stereotype="frontend",
    style={"background": "#F5F5F5"},
)

d.add(customer, shopping)
d.connect(
    r.arrow(customer, shopping.browse),
    r.arrow(customer, shopping["Search"]),  # bracket access by name
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LKxB2i8m4BplLmnuqKEFtaee2lv0ls0RrrQqITXDy23-kpLOKEOop8EPpZ9hBlETsEUeE1RBSHQbnFx6ew2VOahNCA9jBnf3bd1s3flJ_WCy2IWcdasmFMXycEp0Xg7INxCNLZzLqogb5wrZQ1gtLlwqRx9RHfUBRm00)



Both `package()` and `rectangle()` accept `stereotype=` and `style=`.

## Relationships / Connections

### arrow

A directed association between two elements. The most common relationship type.

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram()
el = d.elements
r = d.relationships

customer = el.actor("Customer")
login = el.usecase("Login")
d.add(customer, login)

d.connect(
    r.arrow(customer, login, "authenticates"),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKfCBialKd0kBIx9pqqjuYejJarEB4vLqF39Jy_Cq-I2IIZewjefWCKKh1GIIqioKlDACfCJIrABkHnIyrA09W40)



Parameters: `source`, `target`, `label=`, `style=`, `direction=`, `length=`, `left_head=`, `right_head=`

### generalizes

Inheritance: child is-a parent. Renders as a triangle-headed arrow.

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram()
el = d.elements
r = d.relationships

user = el.actor("User")
admin = el.actor("Admin")
login = el.usecase("Login")
d.add(user, admin, login)

d.connect(
    r.generalizes(admin, user),
    r.arrow(user, login),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKfCBialKWWjJYs2CXrJSZFpk4gBKvCJYrCLD7poqpFpDBb02XHiQdHreV9WlgwkdG9OdiiXDIy5Q1e0)



Parameters: `child`, `parent`, `style=`, `direction=`, `length=`

### include

The base use case always invokes the required use case. Renders with `<<include>>` label.

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram()
el = d.elements
r = d.relationships

customer = el.actor("Customer")
checkout = el.usecase("Checkout")
validate_cart = el.usecase("Validate Cart")
d.add(customer, checkout, validate_cart)

d.connect(
    r.arrow(customer, checkout),
    r.include(checkout, validate_cart),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LOun2iCm40JxUyNYAYwS1mGZ3Fg3st181p6MBT3T_Jzs8KAwPTWTTb7ZPduKucIr8RfQFQIHgoHMmID-9EtLRVoXOUMoPJP1lCR325PqzBuHTGscAQ0Rg0SymtyVByppTgRYMKAWHSvyNVe2)



Parameters: `base`, `required`, `style=`, `direction=`, `length=`

### extends

The extension optionally extends the base use case. Renders with `<<extends>>` label.

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram()
el = d.elements
r = d.relationships

customer = el.actor("Customer")
checkout = el.usecase("Checkout")
apply_coupon = el.usecase("Apply Coupon")
d.add(customer, checkout, apply_coupon)

d.connect(
    r.arrow(customer, checkout),
    r.extends(apply_coupon, checkout),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKfCBialKd0kBIx9pqqjuYejJarEB4vLq73EI4tEpYyjqKG8AJaM5EHKAZZdbnRavobfAYGMAu15uY4YN31357HrxHHW-hcGbIZe8IGKh1HiR58hIbBpKehjxBWSW3JGFG00)



Parameters: `extension`, `base`, `style=`, `direction=`, `length=`

### link

An undirected line between two elements (no arrowhead by default).

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram()
el = d.elements
r = d.relationships

actor_a = el.actor("Developer")
actor_b = el.actor("Tester")
d.add(actor_a, actor_b)

d.connect(
    r.link(actor_a, actor_b, "collaborates"),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKfCBialKd19BKlDoIz8BOBoGrABIu0SkB22hYvKJC5A8Ja_9oSnARyeiIIrcCiXDIy5Q0u0)



Parameters: `source`, `target`, `label=`, `style=`, `direction=`, `length=`, `left_head=`, `right_head=`

### Custom Arrow Heads

Both `arrow()` and `link()` support `left_head=` and `right_head=` for custom arrowhead shapes. Common PlantUML head values include `|>`, `*`, `o`, `#`, `x`, `+`, `^`, `>>`.

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram()
el = d.elements
r = d.relationships

a = el.actor("Client")
b = el.usecase("Service")
d.add(a, b)

d.connect(
    r.arrow(a, b, right_head="closed_triangle"),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKfCBialKd3EoKpDA-4gBKvDJYnELT08JYqgoqnErUI2I2ZewjROAK05kHnIyrA0MW40)



### Bulk Methods

#### arrows()

Multiple independent arrows from `(source, target)` or `(source, target, label)` tuples:

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram()
el = d.elements
r = d.relationships

customer = el.actor("Customer")
admin = el.actor("Admin")
browse = el.usecase("Browse")
search = el.usecase("Search")
checkout = el.usecase("Checkout")
manage = el.usecase("Manage")
d.add(customer, admin, browse, search, checkout, manage)

d.connect(r.arrows(
    (customer, browse),
    (customer, search),
    (customer, checkout, "buys"),
    (admin, manage),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKfCBialKd0kBIx9pqqjWd8TKt8pyxXAYrEJ4ujJ5JISYlBBYrCr4GB1gOb5oHb80iuPgSdP-QKbI4A-YNc9wK1DCACLT7Nj520ceOf134CLWvcdOAMGL5fPp0Ls45W6OYoNGsfU2j3v0000)



#### arrows_from()

Fan-out from one source to many targets. Targets can be bare refs or `(target, label)` tuples:

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram()
el = d.elements
r = d.relationships

customer = el.actor("Customer")
browse = el.usecase("Browse")
search = el.usecase("Search")
checkout = el.usecase("Checkout")
d.add(customer, browse, search, checkout)

d.connect(r.arrows_from(customer,
    browse,
    search,
    (checkout, "buys"),
    direction="right",
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKfCBialKd0kBIx9pqqjuYejJarEB4vLq70goYylJjL420Id9XObPo09E6Ua9cVdbvPeSi5qA-WMwTefG7IY2K9qemd2J52mKaWghIpcSaZDIm6w2G00)



Parameters: `source`, `*targets`, `style=`, `direction=`, `length=`

#### generalizes_from()

Multiple children inherit from one parent:

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram()
el = d.elements
r = d.relationships

engineer = el.actor("Engineer")
oncall_eng = el.actor("On-Call Eng")
platform_eng = el.actor("Platform Eng")
network_eng = el.actor("Network Eng")
d.add(engineer, oncall_eng, platform_eng, network_eng)

d.connect(r.generalizes_from(
    [oncall_eng, platform_eng, network_eng],
    engineer,
    direction="up",
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKfCBialKd3DIy_CIqqjWdAL_FDqdHDpSa3YIWg9nGh-UI1kF90BKn6GarYIbb-K2rS24q1Mv9TQKfvVb0rN0-M3bS2iLB2fqItLHRO1JGR5O3GvP0CTKlDIW3u20000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NO-n3e9044Jx-uerDbfWeYM58Q6r85fORs21YtUtkBU7uU_LA8ROldcPoHHHKJHvPx1M5YXJLFOa9aMgCH9iofxg6oVTcZc3B3l2Z4rW9H3RzPh3POfA7iR3Rh_WmErFp-5CzsI58epeR0C3Jfx2jyPH-sTNOZtA1AtZnyTH7fOAh4_lZP85NGvNb613jp85XURrwWa0)



Parameters: `content`, `target=`, `position=` (left/right/top/bottom), `color=`

## Layout & Organization

### Layout Direction

Set the overall diagram flow direction:

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram(layout="left_to_right")
el = d.elements
r = d.relationships

user = el.actor("User")
login = el.usecase("Login")
browse = el.usecase("Browse")
d.add(user, login, browse)
d.connect(r.arrow(user, login), r.arrow(user, browse))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/HOqx2e0m343td2AZ3hs256TN3r3QM0lQG9BYzVqD7H_lmVDgGQoT1noq6HgZbBmRfY8KhN2548q5LoM1fXI34WuBvrB7phFmfJJ2Mw5p4tv1nz-3fvgUrGq0)



Valid values: `"left_to_right"`, `"top_to_bottom"`

### Direction Hints on Relationships

Fine-tune individual connection placement:

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram()
el = d.elements
r = d.relationships

user = el.actor("User")
top_uc = el.usecase("Reports")
bottom_uc = el.usecase("Settings")
left_uc = el.usecase("Help")
right_uc = el.usecase("Dashboard")
d.add(user, top_uc, bottom_uc, left_uc, right_uc)

d.connect(
    r.arrow(user, top_uc, direction="up"),
    r.arrow(user, bottom_uc, direction="down"),
    r.arrow(user, left_uc, direction="left"),
    r.arrow(user, right_uc, direction="right"),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/JSun3e0W38NXdLCmwk0L38E3iyO3L6ZK18MqvVvYWihulk7FCon0aawlm4eWlJ2IIemM67KpOGmatFuoeyXnRJMDw6Cr1-1z3K2kLKzCTwdhTGaLSLdUK26VwGcLINb-8MNmSldY3G00)



### Arrow Length

Increase arrow length to push elements apart:

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram()
el = d.elements
r = d.relationships

a = el.actor("User")
b = el.usecase("Feature")
d.add(a, b)

d.connect(r.arrow(a, b, length=2))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKfCBialKWWjJYtYAYrEJKuiJbNGS4jDB2ajIjNa0WahwEhQAK15k1nIyrA0kW00)



## Styling

### Actor Style

Change the visual representation of all actors:

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram(actor_style="awesome")
el = d.elements
r = d.relationships

user = el.actor("User")
login = el.usecase("Login")
d.add(user, login)
d.connect(r.arrow(user, login))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIhEpimhI2nAp5L8J2x9BmekgSn9LKWiJotEpqtb0WifX1Qd5d6L5gSc9nQdAcZuvATdvcboWGGLT7Nj5C1yBeVKl1IWSG00)



### Element-Level Styles

Use `style={"background": "..."}` on individual elements:

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram()
el = d.elements

vip = el.actor("VIP", style={"background": "Gold"})
critical = el.usecase("Critical Path", style={"background": "#FFCDD2"})
core = el.package("Core", el.usecase("X", ref="x"), style={"background": "LightCyan"})
d.add(vip, critical, core)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKfCBialKWZp351GTi_FIU4gBKvDJYnELT1GSYxABCbCJinH24WioL3IL4WiLe09nOE459JTt9nTN8ou2XAJinFJKnMSyujI5PHzCjCpIfmh4_CKghaK5E36HO0DgE2gvN98pKi1sWm0)



### Line Styles on Relationships

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram()
el = d.elements
r = d.relationships

a = el.actor("User")
b = el.usecase("Feature")
d.add(a, b)

d.connect(r.arrow(a, b, style="dashed"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKfCBialKWWjJYtYAYrEJKuiJbNGS4jDB2ajIjNa0Wahw4Qd91PdfAR4wjefG6Mu75BpKe2w0G00)



### diagram_style

Theme the entire diagram with a `<style>` block. Pass a dict with element selectors:

```python
from plantuml_compose import usecase_diagram, render

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
el = d.elements
r = d.relationships

user = el.actor("User")
checkout = el.usecase("Checkout", stereotype="critical")
d.add(user, checkout)
d.connect(r.arrow(user, checkout))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/VPBBRi8m44Nt_WfBRDe5hO1IY1H5G89NLJTLFs3gZ8A5OrVEHFGX_hrsS2YYIZFAmZFtdl5ZLWs1exRMB6teKsF6sWObD5Weg1pK_9jnlW6vhvnjJPbRRHq_x1IXpmjhw1bgv6kdGCV4Y_f2Ffd5rSamcdMVpu4almxGlzZHTYQcekXgJyfWp4wInMCnzTcZ_-FkXWX2Y2H_k2Q8PBsSpYFXtNkW6YRCGqIjGqbWAZsiNeUuxhSfGaI6iVJVTfVRIHI2S_OGbHUmnJn4rDn9fqX9qCF4lEWkApv6U5F-PdNP0_23q9apuA9HiWrnPLK4MidEV6IbbMsDXZelAJhVo--xBuTQ7rbw7oVivEpg9Ozpnaw3yTgWwoUGt-Gxb7lRqYrFq_xWMSQ2Y8_76U_hR8Mcz3Fy0m00)



Available selectors: `actor`, `usecase`, `package`, `rectangle`, `arrow`, `note`, `title`, `stereotypes`

Root-level properties: `background`, `font_name`, `font_size`, `font_color`

Each element selector accepts an `ElementStyleDict` with keys like `background`, `line_color`, `font_color`, `font_name`, `font_size`, `font_style`, `round_corner`, `line_thickness`, `padding`, `margin`, `shadowing`.

The `arrow` selector accepts a `DiagramArrowStyleDict` with `line_color`, `line_thickness`, `line_style`.

The `stereotypes` key maps stereotype names to `ElementStyleDict` values, styling all elements bearing that stereotype.

## Advanced Features

### Diagram Metadata

```python
from plantuml_compose import usecase_diagram, render
from plantuml_compose.primitives.common import Scale

d = usecase_diagram(
    title="My System",
    mainframe="System Overview",
    caption="Figure 1: Use case overview",
    header="Draft v0.3",
    footer="Confidential",
    legend="Arrows = interactions",
    scale=Scale(factor=1.5),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/DKxB2i903BplL-GBYY9U1A6YU9CUn0y8ssmDx4EoQKl_tXJQoqp8J6RILaNHCKMNa7CGJ0JlfIebw2QIYMbsrMCaE3PdfwmslPRDuZnb9O4lOM_q40mAqw4vxK8ePQLxoO5xMp56v_6dN38yUHZ5OY_mgGGU3ShU66cWt3k0cqYPAro1rppqwsLrfcsEri2U_mC0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/TLJ1Qjmm4BtxAmQdX_RWTjD22y6ORBBhquQMD2taL1Hxx8Z8qbOQuuOs_vwHB6yZmc8CcdbFRqPlP9yx4fR6GMMbeqU5LJOwR8J3ZHIz5GFypG14GyQ65S25Q1vwQqRTNXh5sPFjf_fZlM7iYT-u-HYthklDzala2clD59axgJ5oFf_w9t2Uil93x8eaAOIlMZ6HTVM3r7sci2CW0rRszmIjjDYGD3fpZEw5xpvq_jrBW9ZGcG6p-J2NeoEER0npBmatg1JQ78GB9NxDSQIisq7gp9SGkcUzF6qc3oTPplzsPtgfttabvLSleVodn8ctAQ4Rp0FdRWuIreqLsdLeeMR_tCoZc4k8tyGZN4Yb8kVEBryIrYFTeoRP2CB049n85DPZAmcuvJpY7AQzJAQeemsyEJRJYOIq7OHKS8qDoZtD53i72UrAQD4Z_71eOyT3oBosw1htnf9Rf4B0Ts8P7PJ_YY8Pr04fYYhwdgGMcvFamTEK6bmC6l2-2fR16PIbr8qQMwpuHYxp2R0tCCM3mZ6GlKjayGyXJvcHQ9b73nMECkOQAHpkQJX3zFL_Ol5G6yBuqPZEpn5ETZwwPHlDT0PNzPgvlqV-e5heUEXB9mugU7EwMgsoSwx6Vurd)



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
