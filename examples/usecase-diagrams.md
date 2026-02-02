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
from plantuml_compose import usecase_diagram

with usecase_diagram(title="Simple System") as d:
    user = d.actor("User")
    login = d.usecase("Login")
    browse = d.usecase("Browse")

    d.arrow(user, login)
    d.arrow(user, browse)

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGZEp2q0KPN59QcvN8d99Vb52g75gKLSfSMfoOd5gGeQFldfcNcQ2BvJKNvvSQec5qYLWgwkdG9O0O8BaUToICrB0Le30000)



## Actors

### Basic Actors

```python
from plantuml_compose import usecase_diagram

with usecase_diagram() as d:
    # Simple actor
    user = d.actor("Customer")

    # With stereotype
    admin = d.actor("Admin", stereotype="privileged")

    # With styling
    guest = d.actor("Guest", style={"background": "LightGray"})

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKfCBialKd0kBIx9pqqjWd8TKt8pynHiR0gACiioSrBJKrFixA1IxgMfnIKAoZwPwHabxaM9bLmEgNafG8C0)



### Actor Inheritance

```python
from plantuml_compose import usecase_diagram

with usecase_diagram() as d:
    user = d.actor("User")
    admin = d.actor("Admin")
    super_admin = d.actor("Super Admin")

    browse = d.usecase("Browse")
    manage = d.usecase("Manage Users")
    config = d.usecase("Configure System")

    # Admin is a kind of User
    d.generalizes(admin, user)
    # Super Admin is a kind of Admin
    d.generalizes(super_admin, admin)

    d.arrow(user, browse)
    d.arrow(admin, manage)
    d.arrow(super_admin, config)

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/PP312W8n34Jl-nMX9_VGFn1PzUnfyLp2RbmMR2jDYmX-lBOfMl6MlinqXWmSCSHahnrEqGSuCuKwxcUxkZghCTse8WN8KDv698bfGYRO78A_C_LVe4xeSA7oAwi-6uMOGXhXqRlBkgH0C3uuaXNnXngXNGc4xLDhQThK42gDyWwqte4qghOCVk9RTrx-nGtavlTjNW00)



## Use Cases

### Basic Use Cases

```python
from plantuml_compose import usecase_diagram

with usecase_diagram() as d:
    user = d.actor("User")

    # Simple use case
    login = d.usecase("Login")

    # With stereotype
    checkout = d.usecase("Checkout", stereotype="critical")

    # With styling
    admin_panel = d.usecase("Admin Panel", style={"background": "LightBlue"})

    d.arrow(user, login)
    d.arrow(user, checkout)

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/HOun3i8m34NtdC8g2nbwWoegi7PWwOmirsejqaIAdVi3aL36z_xm_go6nUeP7PBb0gjoSLMPK1ckIzub-SwFW-cTgtcO9YfYGXX3wFjmsqv9yCJ4SV202asyce3B8ljXzrZP_J8mZW5QeUC_u6PEs_VL1m00)



## Relationships

### Actor to Use Case

```python
from plantuml_compose import usecase_diagram

with usecase_diagram() as d:
    customer = d.actor("Customer")
    browse = d.usecase("Browse Products")
    search = d.usecase("Search")
    checkout = d.usecase("Checkout")

    # Simple arrows
    d.arrow(customer, browse)
    d.arrow(customer, search)
    d.arrow(customer, checkout)

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/POv92eL034JtVOhWobvu1H6zWE01FY4618T01lxr5QGHSLUyAXxLcQDwx5j2Sb4OmbnsrXJ6XCPGLxtA_mgZoXpaLcL0Wnl-2dpc4wFIaXymB4ohXETKtD0qxKVmAc_9cnLFwlYOhyCd)



### Connect Multiple

```python
from plantuml_compose import usecase_diagram

with usecase_diagram() as d:
    customer = d.actor("Customer")
    browse = d.usecase("Browse")
    search = d.usecase("Search")
    cart = d.usecase("Add to Cart")
    checkout = d.usecase("Checkout")

    # Connect actor to multiple use cases at once
    d.connect(customer, [browse, search, cart, checkout])

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/LSz12eGm343HVKyHNDc5Ln2T7c4E8A4D28uJI5AylXKfskrB-26J6ehb_USm6Wk4hCOxYSjA4PMW_mWVIlw1Bw74zGNTd18OGoYbpWCg55YCbmkUjR1It3YRT_K83CC8Tx-r-qHhxsOpg5qtqJ-LJqu0)



### Include (Requires)

A use case that ALWAYS needs another use case. "Checkout" always requires "Validate Cart".

```python
from plantuml_compose import usecase_diagram

with usecase_diagram(title="Include Relationship") as d:
    customer = d.actor("Customer")

    checkout = d.usecase("Checkout")
    validate = d.usecase("Validate Cart")
    process_payment = d.usecase("Process Payment")

    d.arrow(customer, checkout)

    # Checkout always validates cart (mandatory)
    d.requires(checkout, validate)
    # Checkout always processes payment (mandatory)
    d.requires(checkout, process_payment)

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/NP2x2iCm34LtVuN8r0pf1vHW0fwwXGvTWt04CVMZMFBGlszAOzfa4uV3lLmDB9Yb1A_4YIUuHklBJ70ZZ-9IvCKz5Lf96KnXIO6oAamMcU1a5hAFLAJzeUQEtiqe16RDRLf0Xegc3_fJnvmiCSE8hq1napSuRL3LLkWw3RLGrGFEUXyF5-XxznsXzSux91_CWUAylk4D)



### Extends (Optional For)

A use case that MAY extend another use case. "Apply Coupon" optionally extends "Checkout".

```python
from plantuml_compose import usecase_diagram

with usecase_diagram(title="Extends Relationship") as d:
    customer = d.actor("Customer")

    checkout = d.usecase("Checkout")
    apply_coupon = d.usecase("Apply Coupon")
    gift_wrap = d.usecase("Gift Wrap")

    d.arrow(customer, checkout)

    # Apply coupon is optional during checkout
    d.optional_for(apply_coupon, checkout)
    # Gift wrap is optional during checkout
    d.optional_for(gift_wrap, checkout)

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/VO_12eCm44Jl-Oh1KptO3oWY5YczU-bHGhh5q6X2TWFjtrShLayzBJFxcDcjMNIKD3WbLXpXyX8QxuoMd1RhH-vjKDg8ZsWIYnyegiHaD1CEJK_cwPFacvMTGt1lD3u5FsOvDEFhT8kp0w_s8RX57HPgbjqirTg3egYmLgXz2exR0YUK9IrNLvNwnVnXwcbE7ty0)



### Combined Example

```python
from plantuml_compose import usecase_diagram

with usecase_diagram(title="Order System") as d:
    customer = d.actor("Customer")

    place_order = d.usecase("Place Order")
    validate = d.usecase("Validate Order")
    authenticate = d.usecase("Authenticate")
    express = d.usecase("Express Shipping")
    insurance = d.usecase("Add Insurance")

    d.arrow(customer, place_order)

    # Place order always validates and authenticates
    d.requires(place_order, validate)
    d.requires(place_order, authenticate)

    # Express and insurance are optional
    d.optional_for(express, place_order)
    d.optional_for(insurance, place_order)

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/VP712i8m38RlVOhWoHtq0MGKHJnuKX2yZj86L-ZgQ5BGjxVRd7GzU4hu-YNyeNjY5JXsJh1bXt091WFStiJO2QNv6U0OYPyT1X49jIA4zUhgbFwwgmeKmGYQ4MJQNJbh52_CcPNo8NABdgrERrMsu_Jg0nB1hRLzR_rZslAbpKopWOCnSFOKW_8Q9pkXveV4V0ziDd8HFEjXAukai8EwjbwxQ53AqitJ5sOPTT3pwS765wCtbEn5rF_gFjNqSHy0)



## System Boundaries

Group use cases inside a system boundary:

```python
from plantuml_compose import usecase_diagram

with usecase_diagram(title="E-Commerce System") as d:
    customer = d.actor("Customer")
    admin = d.actor("Admin")

    with d.rectangle("E-Commerce Platform") as system:
        browse = system.usecase("Browse Products")
        search = system.usecase("Search")
        checkout = system.usecase("Checkout")
        manage = system.usecase("Manage Inventory")

    d.arrow(customer, browse)
    d.arrow(customer, search)
    d.arrow(customer, checkout)
    d.arrow(admin, manage)

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/PT112eCm40NGVKunP5KNNg7OIXTT50GF84ESgjGaa4nQfFJk3QOMnLtomi_FfF2CZeCU1Gyy4bpoqcfDJX7KasVI0XLR1sNmRAF_jgTM3qOuKeocYp6vobKZyjqwBU4j088dXPxW8C_ElkAYShODYhtC03qaR1PS1sf2f_fiJMLFwc43Rr3Uq617S3LFCl5nKxevQVDNyH7B493dnrtpvZ1rRsqf5_FmC-qw2Z9j_Cml)



### Packages

```python
from plantuml_compose import usecase_diagram

with usecase_diagram() as d:
    user = d.actor("User")

    with d.package("Shopping") as shopping:
        shopping.usecase("Browse")
        shopping.usecase("Search")

    with d.package("Checkout") as checkout_pkg:
        checkout_pkg.usecase("Payment")
        checkout_pkg.usecase("Shipping")

    d.arrow(user, "Browse")
    d.arrow(user, "Payment")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKfCBialKWWjJYtYAaXCpavCJrK8piWlACZCIrUevb9GA2rEJKuiJbNGS2hABozErKGM2avDB4hEqEIgXMjrpaXDpiulBK7L6f1OcPkQLuAgDoCJR0b8DyXs1LrTEmM87GW-L2ENGsfU2j2n0000)



## Notes

```python
from plantuml_compose import usecase_diagram

with usecase_diagram() as d:
    customer = d.actor("Customer")
    checkout = d.usecase("Checkout")

    d.arrow(customer, checkout)

    # Note on an element
    d.note("Requires valid payment", target=checkout)

    # Note with position
    d.note("Primary flow", position="left", target=checkout)

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/NOux3i8m341tdy8Z3Bq00whK2o1kOAKEZKXYy8UgjuU1Ch2-zuOtcfDwj0gKN1IdC9V62c6So1WFqyBfBk57s1qEmnbt35sSKSjjSPJymoUyyZEAik6BQfdnGLlZ_iqhvx_wegMHRfYhh31odpzBRm00)



## Layout Options

### Left to Right

```python
from plantuml_compose import usecase_diagram

with usecase_diagram(title="Left to Right", layout="left_to_right") as d:
    user = d.actor("User")
    a = d.usecase("Use Case A")
    b = d.usecase("Use Case B")
    c = d.usecase("Use Case C")

    d.connect(user, [a, b, c])

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/ROyn3eCm34Ltdy9YeWDNG92idIeneoWOY9GIoJRtBvOwL3IRt_UJhJ-81jRpdK6JPi8dhOfQy9MsNI5_YOrmIKnHKpaWH2sCan33AHI34BRDXUXj79i71h7rR3oFDSdT95UJ_4toO3-nw_hVw_-PgsGU1ZgMg-a7)



### Direction Hints

```python
from plantuml_compose import usecase_diagram

with usecase_diagram() as d:
    user = d.actor("User")
    top = d.usecase("Top")
    bottom = d.usecase("Bottom")
    left = d.usecase("Left")
    right = d.usecase("Right")

    d.arrow(user, top, direction="up")
    d.arrow(user, bottom, direction="down")
    d.arrow(user, left, direction="left")
    d.arrow(user, right, direction="right")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKfCBialKWWjJYtYAYrEJKuiJbNG2Calq4JmdF9BIl9paGHyKjDAaBX1cUaPG3x820LTtL9TEmMWVXWt1SY5600JoG6AW4o0yOk0VB0HN0wfUIb09m40)



## Complete Example: Banking System

```python
from plantuml_compose import usecase_diagram

with usecase_diagram(title="Online Banking System") as d:
    # Actors
    customer = d.actor("Customer")
    teller = d.actor("Bank Teller")
    admin = d.actor("Admin")

    # Teller is a type of employee that can do customer things too
    d.generalizes(teller, customer)

    with d.rectangle("Online Banking") as bank:
        # Customer use cases
        login = bank.usecase("Login")
        view_balance = bank.usecase("View Balance")
        transfer = bank.usecase("Transfer Funds")
        pay_bills = bank.usecase("Pay Bills")

        # Shared requirements
        authenticate = bank.usecase("Authenticate")
        audit_log = bank.usecase("Audit Log")

        # Optional extensions
        two_factor = bank.usecase("Two-Factor Auth")
        receipt = bank.usecase("Email Receipt")

        # Admin use cases
        manage_users = bank.usecase("Manage Users")
        view_reports = bank.usecase("View Reports")

    # Customer interactions
    d.connect(customer, [login, view_balance, transfer, pay_bills])

    # All actions require authentication and logging
    d.requires(login, authenticate)
    d.requires(transfer, audit_log)
    d.requires(pay_bills, audit_log)

    # Optional extensions
    d.optional_for(two_factor, authenticate)
    d.optional_for(receipt, transfer)
    d.optional_for(receipt, pay_bills)

    # Admin interactions
    d.connect(admin, [manage_users, view_reports])

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/XPF1JiCm38RlVGgh9tOe3u2cQXjY9n1e3AvHb9eIaQPJucfCmBkJfXcj1nf7V_rYkt-KXIVfg6jCHfeCmhqrsYAif7tJjeR7WoTiCgceTN3TUMeRTAdCUmcsQ0ow7AIFXyHG9sLPDTfc4mxppw8O6pbK96qTvkPyS0uV6K3dKKcFS77RrjhEfYH_rhWFjf5MOJxhn_T49CBKhPFMluJXwyvMVf2FJ4J6z0TvW9Ks9fcX5B6SIikENj6ILfAGxxNiAaqG5XvEnrA4ac-qRujrYYXqIYljsu69dZ7_ff7Qm0OLwXqDTaGY8IRVIIjhX2UFBlt2G4GalqFSuAvrv2SX9f9zPSURWg8e8Tu2HonpzkKaOFPjZ3IsXCiIfe725SpdsYhJLLYM6Uyqo2dK4_Edxpc9n_pdR7md3AE2p5BktPDb_h77XRWOtqMCWbtDYDarBCAfy4A_0G00)



## Quick Reference

| Method | Description |
|--------|-------------|
| `d.actor(name)` | Create actor |
| `d.usecase(name)` | Create use case |
| `d.arrow(actor, usecase)` | Actor interacts with use case |
| `d.link(a, b)` | Simple association (no arrow) |
| `d.connect(hub, spokes)` | Connect one to many |
| `d.generalizes(child, parent)` | Inheritance relationship |
| `d.requires(base, required)` | <<include>> relationship |
| `d.optional_for(ext, base)` | <<extends>> relationship |
| `d.rectangle(name)` | System boundary |
| `d.package(name)` | Package grouping |
| `d.note(text, target)` | Add note |
