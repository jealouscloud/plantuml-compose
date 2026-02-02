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
