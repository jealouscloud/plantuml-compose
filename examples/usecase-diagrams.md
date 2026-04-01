# Use Case Diagrams

Use case diagrams show WHAT a system does from the user's perspective. They're ideal for:

- **Functional requirements**: What the system must do
- **System boundaries**: What's inside vs outside the system
- **Actor identification**: Who interacts with the system
- **Stakeholder communication**: High-level feature overview

Unlike sequence diagrams (HOW it works) or class diagrams (data structures), use case diagrams focus on goals and actors.

## Core Concepts

**Actor**: Someone or something outside the system that interacts with it (User, Admin, External API).

**Use Case**: A goal the system helps actors achieve (Login, Checkout, Search).

**System Boundary**: A rectangle showing what's inside the system.

**Relationships**:
- **Arrow**: Actor interacts with use case
- **Generalizes**: Inheritance (Admin is a type of User)
- **Requires** (<<include>>): Base ALWAYS needs the included use case
- **Optional For** (<<extends>>): Extension MAY be triggered during base

## Your First Use Case Diagram

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



## Actors

### Basic Actors

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram()
el = d.elements

# Simple actor
user = el.actor("Customer")

# With stereotype
admin = el.actor("Admin", stereotype="privileged")

# With styling
guest = el.actor("Guest", style={"background": "LightGray"})

d.add(user, admin, guest)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKfCBialKd0kBIx9pqqjWd8TKt8pynHiR0gACiioSrBJKrFixA1IxgMfnIKAoZwPwHabxaM9bLmEgNafG8C0)



### Actor Inheritance

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram()
el = d.elements
r = d.relationships

user = el.actor("User")
admin = el.actor("Admin")
super_admin = el.actor("Super Admin")

browse = el.usecase("Browse")
manage = el.usecase("Manage Users")
config = el.usecase("Configure System")

d.add(user, admin, super_admin, browse, manage, config)
d.connect(
    # Admin is a kind of User
    r.generalizes(admin, user),
    # Super Admin is a kind of Admin
    r.generalizes(super_admin, admin),

    r.arrow(user, browse),
    r.arrow(admin, manage),
    r.arrow(super_admin, config),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/PP312W8n34Jl-nMX9_VGFn1PzUnfyLp2RbmMR2jDYmX-lBOfMl6MlinqXWmSCSHahnrEqGSuCuKwxcUxkZghCTse8WN8KDv698bfGYRO78A_C_LVe4xeSA7oAwi-6uMOGXhXqRlBkgH0C3uuaXNnXngXNGc4xLDhQThK42gDyWwqte4qghOCVk9RTrx-nGtavlTjNW00)



## Use Cases

### Basic Use Cases

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram()
el = d.elements
r = d.relationships

user = el.actor("User")

# Simple use case
login = el.usecase("Login")

# With stereotype
checkout = el.usecase("Checkout", stereotype="critical")

# With styling
admin_panel = el.usecase("Admin Panel", style={"background": "LightBlue"})

d.add(user, login, checkout, admin_panel)
d.connect(
    r.arrow(user, login),
    r.arrow(user, checkout),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/HOun3i8m34NtdC8g2nbwWoegi7PWwOmirsejqaIAdVi3aL36z_xm_go6nUeP7PBb0gjoSLMPK1ckIzub-SwFW-cTgtcO9YfYGXX3wFjmsqv9yCJ4SV202asyce3B8ljXzrZP_J8mZW5QeUC_u6PEs_VL1m00)



## Relationships

### Actor to Use Case

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram()
el = d.elements
r = d.relationships

customer = el.actor("Customer")
browse = el.usecase("Browse Products")
search = el.usecase("Search")
checkout = el.usecase("Checkout")

d.add(customer, browse, search, checkout)
# Simple arrows
d.connect(
    r.arrow(customer, browse),
    r.arrow(customer, search),
    r.arrow(customer, checkout),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/POv92eL034JtVOhWobvu1H6zWE01FY4618T01lxr5QGHSLUyAXxLcQDwx5j2Sb4OmbnsrXJ6XCPGLxtA_mgZoXpaLcL0Wnl-2dpc4wFIaXymB4ohXETKtD0qxKVmAc_9cnLFwlYOhyCd)



### Connect Multiple

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram()
el = d.elements
r = d.relationships

customer = el.actor("Customer")
browse = el.usecase("Browse")
search = el.usecase("Search")
cart = el.usecase("Add to Cart")
checkout = el.usecase("Checkout")

d.add(customer, browse, search, cart, checkout)
# Connect actor to multiple use cases at once
d.connect(r.arrows_from(customer, browse, search, cart, checkout))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LSz12eGm343HVKyHNDc5Ln2T7c4E8A4D28uJI5AylXKfskrB-26J6ehb_USm6Wk4hCOxYSjA4PMW_mWVIlw1Bw74zGNTd18OGoYbpWCg55YCbmkUjR1It3YRT_K83CC8Tx-r-qHhxsOpg5qtqJ-LJqu0)



### Include (Requires)

A use case that ALWAYS needs another use case. "Checkout" always requires "Validate Cart".

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram(title="Include Relationship")
el = d.elements
r = d.relationships

customer = el.actor("Customer")

checkout = el.usecase("Checkout")
validate = el.usecase("Validate Cart")
process_payment = el.usecase("Process Payment")

d.add(customer, checkout, validate, process_payment)
d.connect(
    r.arrow(customer, checkout),
    # Checkout always validates cart (mandatory)
    r.include(checkout, validate),
    # Checkout always processes payment (mandatory)
    r.include(checkout, process_payment),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/NP2x2iCm34LtVuN8r0pf1vHW0fwwXGvTWt04CVMZMFBGlszAOzfa4uV3lLmDB9Yb1A_4YIUuHklBJ70ZZ-9IvCKz5Lf96KnXIO6oAamMcU1a5hAFLAJzeUQEtiqe16RDRLf0Xegc3_fJnvmiCSE8hq1napSuRL3LLkWw3RLGrGFEUXyF5-XxznsXzSux91_CWUAylk4D)



### Extends (Optional For)

A use case that MAY extend another use case. "Apply Coupon" optionally extends "Checkout".

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram(title="Extends Relationship")
el = d.elements
r = d.relationships

customer = el.actor("Customer")

checkout = el.usecase("Checkout")
apply_coupon = el.usecase("Apply Coupon")
gift_wrap = el.usecase("Gift Wrap")

d.add(customer, checkout, apply_coupon, gift_wrap)
d.connect(
    r.arrow(customer, checkout),
    # Apply coupon is optional during checkout
    r.extends(apply_coupon, checkout),
    # Gift wrap is optional during checkout
    r.extends(gift_wrap, checkout),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/VO_12eCm44Jl-Oh1KptO3oWY5YczU-bHGhh5q6X2TWFjtrShLayzBJFxcDcjMNIKD3WbLXpXyX8QxuoMd1RhH-vjKDg8ZsWIYnyegiHaD1CEJK_cwPFacvMTGt1lD3u5FsOvDEFhT8kp0w_s8RX57HPgbjqirTg3egYmLgXz2exR0YUK9IrNLvNwnVnXwcbE7ty0)



### Combined Example

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram(title="Order System")
el = d.elements
r = d.relationships

customer = el.actor("Customer")

place_order = el.usecase("Place Order")
validate = el.usecase("Validate Order")
authenticate = el.usecase("Authenticate")
express = el.usecase("Express Shipping")
insurance = el.usecase("Add Insurance")

d.add(customer, place_order, validate, authenticate, express, insurance)
d.connect(
    r.arrow(customer, place_order),
    # Place order always validates and authenticates
    r.include(place_order, validate),
    r.include(place_order, authenticate),
    # Express and insurance are optional
    r.extends(express, place_order),
    r.extends(insurance, place_order),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/VP712i8m38RlVOhWoHtq0MGKHJnuKX2yZj86L-ZgQ5BGjxVRd7GzU4hu-YNyeNjY5JXsJh1bXt091WFStiJO2QNv6U0OYPyT1X49jIA4zUhgbFwwgmeKmGYQ4MJQNJbh52_CcPNo8NABdgrERrMsu_Jg0nB1hRLzR_rZslAbpKopWOCnSFOKW_8Q9pkXveV4V0ziDd8HFEjXAukai8EwjbwxQ53AqitJ5sOPTT3pwS765wCtbEn5rF_gFjNqSHy0)



## System Boundaries

Group use cases inside a system boundary:

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram(title="E-Commerce System")
el = d.elements
r = d.relationships

customer = el.actor("Customer")
admin = el.actor("Admin")

system = el.rectangle("E-Commerce Platform",
    el.usecase("Browse Products", ref="browse"),
    el.usecase("Search", ref="search"),
    el.usecase("Checkout", ref="checkout"),
    el.usecase("Manage Inventory", ref="manage"),
)

d.add(customer, admin, system)
d.connect(
    r.arrow(customer, system.browse),
    r.arrow(customer, system.search),
    r.arrow(customer, system.checkout),
    r.arrow(admin, system.manage),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/PT112eCm40NGVKunP5KNNg7OIXTT50GF84ESgjGaa4nQfFJk3QOMnLtomi_FfF2CZeCU1Gyy4bpoqcfDJX7KasVI0XLR1sNmRAF_jgTM3qOuKeocYp6vobKZyjqwBU4j088dXPxW8C_ElkAYShODYhtC03qaR1PS1sf2f_fiJMLFwc43Rr3Uq617S3LFCl5nKxevQVDNyH7B493dnrtpvZ1rRsqf5_FmC-qw2Z9j_Cml)



### Packages

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram()
el = d.elements
r = d.relationships

user = el.actor("User")

shopping = el.package("Shopping",
    el.usecase("Browse", ref="browse"),
    el.usecase("Search"),
)

checkout_pkg = el.package("Checkout",
    el.usecase("Payment", ref="payment"),
    el.usecase("Shipping"),
)

d.add(user, shopping, checkout_pkg)
d.connect(
    r.arrow(user, shopping.browse),
    r.arrow(user, checkout_pkg.payment),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKfCBialKWWjJYtYAaXCpavCJrK8piWlACZCIrUevb9GA2rEJKuiJbNGS2hABozErKGM2avDB4hEqEIgXMjrpaXDpiulBK7L6f1OcPkQLuAgDoCJR0b8DyXs1LrTEmM87GW-L2ENGsfU2j2n0000)



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

# Note on an element
d.note("Requires valid payment", target=checkout)

# Note with position
d.note("Primary flow", position="left", target=checkout)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/NOux3i8m341tdy8Z3Bq00whK2o1kOAKEZKXYy8UgjuU1Ch2-zuOtcfDwj0gKN1IdC9V62c6So1WFqyBfBk57s1qEmnbt35sSKSjjSPJymoUyyZEAik6BQfdnGLlZ_iqhvx_wegMHRfYhh31odpzBRm00)



## Layout Options

### Left to Right

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram(title="Left to Right", layout="left_to_right")
el = d.elements
r = d.relationships

user = el.actor("User")
a = el.usecase("Use Case A")
b = el.usecase("Use Case B")
c = el.usecase("Use Case C")

d.add(user, a, b, c)
d.connect(r.arrows_from(user, a, b, c))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/ROyn3eCm34Ltdy9YeWDNG92idIeneoWOY9GIoJRtBvOwL3IRt_UJhJ-81jRpdK6JPi8dhOfQy9MsNI5_YOrmIKnHKpaWH2sCan33AHI34BRDXUXj79i71h7rR3oFDSdT95UJ_4toO3-nw_hVw_-PgsGU1ZgMg-a7)



### Direction Hints

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram()
el = d.elements
r = d.relationships

user = el.actor("User")
top = el.usecase("Top")
bottom = el.usecase("Bottom")
left = el.usecase("Left")
right = el.usecase("Right")

d.add(user, top, bottom, left, right)
d.connect(
    r.arrow(user, top, direction="up"),
    r.arrow(user, bottom, direction="down"),
    r.arrow(user, left, direction="left"),
    r.arrow(user, right, direction="right"),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKfCBialKWWjJYtYAYrEJKuiJbNG2Calq4JmdF9BIl9paGHyKjDAaBX1cUaPG3x820LTtL9TEmMWVXWt1SY5600JoG6AW4o0yOk0VB0HN0wfUIb09m40)



## Complete Example: Banking System

```python
from plantuml_compose import usecase_diagram, render

d = usecase_diagram(title="Online Banking System")
el = d.elements
r = d.relationships

# Actors
customer = el.actor("Customer")
teller = el.actor("Bank Teller")
admin = el.actor("Admin")

# System boundary with use cases
bank = el.rectangle("Online Banking",
    # Customer use cases
    el.usecase("Login", ref="login"),
    el.usecase("View Balance", ref="view_balance"),
    el.usecase("Transfer Funds", ref="transfer"),
    el.usecase("Pay Bills", ref="pay_bills"),

    # Shared requirements
    el.usecase("Authenticate", ref="authenticate"),
    el.usecase("Audit Log", ref="audit_log"),

    # Optional extensions
    el.usecase("Two-Factor Auth", ref="two_factor"),
    el.usecase("Email Receipt", ref="receipt"),

    # Admin use cases
    el.usecase("Manage Users", ref="manage_users"),
    el.usecase("View Reports", ref="view_reports"),
)

d.add(customer, teller, admin, bank)

d.connect(
    # Teller is a type of employee that can do customer things too
    r.generalizes(teller, customer),

    # Customer interactions
    r.arrows_from(customer, bank.login, bank.view_balance,
                  bank.transfer, bank.pay_bills),

    # All actions require authentication and logging
    r.include(bank.login, bank.authenticate),
    r.include(bank.transfer, bank.audit_log),
    r.include(bank.pay_bills, bank.audit_log),

    # Optional extensions
    r.extends(bank.two_factor, bank.authenticate),
    r.extends(bank.receipt, bank.transfer),
    r.extends(bank.receipt, bank.pay_bills),

    # Admin interactions
    r.arrows_from(admin, bank.manage_users, bank.view_reports),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/XPF1JiCm38RlVGgh9tOe3u2cQXjY9n1e3AvHb9eIaQPJucfCmBkJfXcj1nf7V_rYkt-KXIVfg6jCHfeCmhqrsYAif7tJjeR7WoTiCgceTN3TUMeRTAdCUmcsQ0ow7AIFXyHG9sLPDTfc4mxppw8O6pbK96qTvkPyS0uV6K3dKKcFS77RrjhEfYH_rhWFjf5MOJxhn_T49CBKhPFMluJXwyvMVf2FJ4J6z0TvW9Ks9fcX5B6SIikENj6ILfAGxxNiAaqG5XvEnrA4ac-qRujrYYXqIYljsu69dZ7_ff7Qm0OLwXqDTaGY8IRVIIjhX2UFBlt2G4GalqFSuAvrv2SX9f9zPSURWg8e8Tu2HonpzkKaOFPjZ3IsXCiIfe725SpdsYhJLLYM6Uyqo2dK4_Edxpc9n_pdR7md3AE2p5BktPDb_h77XRWOtqMCWbtDYDarBCAfy4A_0G00)



## Quick Reference

| Method | Description |
|--------|-------------|
| `el.actor(name)` | Create actor |
| `el.usecase(name)` | Create use case |
| `r.arrow(actor, usecase)` | Actor interacts with use case |
| `r.link(a, b)` | Simple association (no arrow) |
| `r.arrows_from(source, *targets)` | Connect one to many |
| `r.generalizes(child, parent)` | Inheritance relationship |
| `r.generalizes_from(children, parent)` | Multiple children inherit |
| `r.include(base, required)` | <<include>> relationship |
| `r.extends(ext, base)` | <<extends>> relationship |
| `el.rectangle(name, *children)` | System boundary |
| `el.package(name, *children)` | Package grouping |
| `d.note(text, target=ref)` | Add note |
