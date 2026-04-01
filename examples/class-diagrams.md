# Class Diagrams

Class diagrams show static structure: types, their attributes, methods, and relationships. They're ideal for:

- **Domain modeling**: User, Order, Product entities
- **API documentation**: Service interfaces and data types
- **Database schemas**: Entity relationships
- **Inheritance hierarchies**: Base classes and specializations

Unlike sequence diagrams (runtime behavior) or object diagrams (specific instances), class diagrams show the TYPES themselves.

## Core Concepts

**Class**: A type with optional attributes (fields) and operations (methods).

**Interface**: A contract defining required operations, no implementation.

**Enum**: A fixed set of named values.

**Relationships**:
- **Extension** (inheritance): Child extends Parent
- **Implementation**: Class implements Interface
- **Aggregation**: Whole "has" Part (part can exist alone)
- **Composition**: Whole "contains" Part (part dies with whole)
- **Dependency**: A "uses" B

## Your First Class Diagram

```python
from plantuml_compose import class_diagram, render

d = class_diagram(title="Simple Model")
el = d.elements
r = d.relationships

user = el.class_("User")
order = el.class_("Order")
d.add(user, order)

d.connect(r.has(user, order, part_label="*"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGZEp2q0KhxvAQavNCavYSN52g75gKLGfdzH2f0D4b1GCbHIoDVLLL3IKe8AEwJcfG0D0W00)



## Creating Classes

### Basic Classes

```python
from plantuml_compose import class_diagram, render

d = class_diagram()
el = d.elements

# Simple class
user = el.class_("User")

# Abstract class
shape = el.abstract("Shape")

# Interface
serializable = el.interface("Serializable")

# Enum with values
status = el.enum("Status", "PENDING", "ACTIVE", "CLOSED")

# Annotation
deprecated = el.annotation("Deprecated")

d.add(user, shape, serializable, status, deprecated)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/9Ov12i90303lUKMUKkaMAKWLrdfFjn4Njcb9iXV5lxlWRHZcC9qvgTUjG2faXhEn0YtcIidnx-AB3eOiplgan1XPCvNyfgKmiDGDevDNmmyWteOfZDEvqQc_Zu-XGN-vnY705qXaRsNU1GCVoecSL-XOrZRm0m00)



### Additional Class Types

```python
from plantuml_compose import class_diagram, render

d = class_diagram()
el = d.elements

# Entity (database/domain entity)
entity = el.entity("Customer")

# Exception
error = el.exception("ValidationError")

# Metaclass
meta = el.metaclass("Type")

# Protocol (Python-style interface)
proto = el.protocol("Iterable")

# Struct (value type)
point = el.struct("Point")

# Circle/Diamond (shorthand notations)
c = el.circle("C")
dm = el.diamond("D")

d.add(entity, error, meta, proto, point, c, dm)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/5Sqn3i8m30NGtQVmKIeL1hOEYDqu7YmvSUJyIlJsmFQsjor8uUn1Dk2uU3yNibkHVTGcF0U_9Bp9d_UgBEe6qP2r-7bDerc9r0n-m4hUORHGfuAFz05IBmtZdPfBpz7uHfkDzYk_)



### Generic Classes

```python
from plantuml_compose import class_diagram, render

d = class_diagram()
el = d.elements

# Generic class
collection = el.class_("Collection", generics="T")

# Bounded generic
comparable = el.class_("Comparable", generics="T extends Number")

d.add(collection, comparable)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEIImkLd3Epyb9JIx9pC-p2R63Y-KM91Ob9kMaseGef5QKfEQb52lubUOcfHRPSJa0UK3j0000)



### Classes with Members

```python
from plantuml_compose import class_diagram, render

d = class_diagram(title="User Model")
el = d.elements

user = el.class_("User", members=(
    # Fields
    el.field("id", "int", visibility="private"),
    el.field("email", "str", visibility="private"),
    el.field("created_at", "datetime", visibility="protected"),

    # Separator
    el.separator(),

    # Methods
    el.method("login(password: str)", "bool", visibility="public"),
    el.method("validate()", visibility="private"),
))
d.add(user)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/9Own2W9134JxV4N0vWwv7x2w7x2qbdW94iXkP3Tg8VxxPRK9CyERC6iFQl4i1g5XWfSk3S_EOh0PzVuFFe2uAEC9jSRGKaWjRO-Mzh0reH2-KcJ6AKEB36x9SpI_QvqU-UtjZN-bERcRkmtcHQQZCytmXLKgvveT)



### Visibility Modifiers

```python
from plantuml_compose import class_diagram, render

d = class_diagram()
el = d.elements

ex = el.class_("Example", members=(
    # Public: + (accessible everywhere)
    el.field("public_field", "str", visibility="public"),

    # Private: - (only in this class)
    el.field("private_field", "int", visibility="private"),

    # Protected: # (class and subclasses)
    el.field("protected_field", "bool", visibility="protected"),

    # Package: ~ (same package only)
    el.field("package_field", "float", visibility="package"),
))
d.add(ex)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/HSqn2e0m38NXlQS8E8eNS7Bn79AsKOgn3MqKGVJiTjBr-tcyeIXctJSsZh4K64_SX0ak0z3ARZcuQGx47deecgjsaiE1IX-7g9KRoKd9AVals9IubaVGhRZyWvaJghdDGD7NvnS0)



### Static and Abstract Members

```python
from plantuml_compose import class_diagram, render

d = class_diagram()
el = d.elements

logger = el.class_("Logger", members=(
    # Static field (underlined in UML)
    el.field("instance", "Logger", visibility="private", modifier="static"),

    # Static method
    el.method("getInstance()", "Logger", visibility="public", modifier="static"),

    # Abstract method (italic in UML)
    el.method("log(msg: str)", visibility="public", modifier="abstract"),
))
d.add(logger)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEIImkLl39JqzFBLAevb9Gg0PAbMGcroheAcJc0TbvoQaALb05oDBQ2kcf9PvG5HgQA6eIaufBYXAJIq2gSlBJDNABqwqKW4AQNBLS3gbvAK2B0G00)



### Member Separators

```python
from plantuml_compose import class_diagram, render

d = class_diagram()
el = d.elements

svc = el.class_("Service", members=(
    el.field("config", "Config"),
    el.field("logger", "Logger"),

    el.separator(label="lifecycle"),

    el.method("start()"),
    el.method("stop()"),

    el.separator(style="dotted", label="internal"),

    el.method("process()", visibility="private"),
))
d.add(svc)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/7Oun2iCm34Ltdq9ZCjW7o1JesgqdCAfY38eT9BTGGkuULTlxx_E5LXrPncVdW9nLuKNohKXm1W3iRQi55dWucE5U2ecPfuEP687hHlX39Wjc_E0qE_N38IMeRP2qpCR_rI4TITNQAwpKtlR03G00)



## Relationships

### Inheritance (extends)

```python
from plantuml_compose import class_diagram, render

d = class_diagram(title="Inheritance")
el = d.elements
r = d.relationships

animal = el.class_("Animal")
dog = el.class_("Dog")
cat = el.class_("Cat")
d.add(animal, dog, cat)

# Dog extends Animal
d.connect(
    r.extends(dog, animal),
    r.extends(cat, animal),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LV3CoqWjoYn9p4jEvKhEIImkLd3CoynDp85oNFBJeIpdn18kY9I2JOskBbW6cG-ITqZDIm4Q3G00)



### Implementation (implements)

```python
from plantuml_compose import class_diagram, render

d = class_diagram(title="Interface Implementation")
el = d.elements
r = d.relationships

comparable = el.interface("Comparable")
serializable = el.interface("Serializable")
user = el.class_("User")
d.add(comparable, serializable, user)

d.connect(
    r.implements(user, comparable),
    r.implements(user, serializable),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LV3CAqajIajC1h9o2t9ISrFpIX9BClFpk3BX4ixvkGM9HOb9EQb8Wi6fHPc9EPbLOE7adCJYOeNGujGYBeHY1PiQFJs88B9Y9667rBmKe4i0)



### Aggregation (has)

Aggregation means the part can exist independently. A Team has Players, but Players can exist without the Team.

```python
from plantuml_compose import class_diagram, render

d = class_diagram(title="Aggregation")
el = d.elements
r = d.relationships

team = el.class_("Team")
player = el.class_("Player")
d.add(team, player)

# One team has many players
d.connect(r.aggregation(team, player, part_label="*"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LN1CJozAJKyioSpFuqhEIImkLWX9JSo5CWDo4YjJYxX08WfAXaeA-Rgw2afQIZ1nXzIy5A190000)



### Composition (contains)

Composition means the part cannot exist without the whole. A House contains Rooms; if the House is destroyed, so are the Rooms.

```python
from plantuml_compose import class_diagram, render

d = class_diagram(title="Composition")
el = d.elements
r = d.relationships

order = el.class_("Order")
line_item = el.class_("LineItem")
d.add(order, line_item)

# One order contains one or more line items
d.connect(r.contains(order, line_item, whole_label="1", part_label="1..*"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LN3Epot8ByuioSpFuqhEIImkLl0lIaajWh9zClDIFKjISxd0WWfAXaeAMhgwG5fFJqi98UkGcfS2D180)



### Dependency (uses)

A depends on B if A uses B but doesn't own it.

```python
from plantuml_compose import class_diagram, render

d = class_diagram(title="Dependency")
el = d.elements
r = d.relationships

service = el.class_("OrderService")
logger = el.class_("Logger")
validator = el.class_("Validator")
d.add(service, logger, validator)

d.connect(
    r.uses(service, logger),
    r.uses(service, validator),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LN19BKZDIqdDIwxaIiv9B2vMy2zAIIqAJYqgoqnEXGhvvAUdfnP1EM69EPafYINvHLp8AXNqzEnWwZ344LeSW7O1xGO0)



### Association

A general relationship between classes.

```python
from plantuml_compose import class_diagram, render

d = class_diagram(title="Association")
el = d.elements
r = d.relationships

student = el.class_("Student")
course = el.class_("Course")
d.add(student, course)

# Students enroll in courses
d.connect(r.association(
    student, course,
    source_label="*",
    target_label="*",
    label="enrolls in",
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/BOn12e0m30JlUKNmAFG37gJY4tn1QNC8n0IQzF-AzhJC36psA3t6BH0SGdYuM-KIR0fLYZjUCHffJ3fjT2UO4fTrmPJsR_-46v9s4t5aXKpQtlC7)



### Relationship Labels

```python
from plantuml_compose import class_diagram, render

d = class_diagram()
el = d.elements
r = d.relationships

company = el.class_("Company")
employee = el.class_("Employee")
d.add(company, employee)

d.connect(r.has(
    company, employee,
    label="employs",
    part_label="1..*",
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEIImkLd3Epor8pAk4ybnp2tBoArDJkQ322ag6IWhvkhf0MazFImakhs2ba0fc5dCvfEQb08q30000)



Common cardinality notations:
- `1` - exactly one
- `*` - zero or more
- `0..1` - zero or one (optional)
- `1..*` - one or more
- `n..m` - between n and m

### Qualified Association

A qualified association shows how one class uses a key to access instances of another. For example, a Bank uses an account number to look up Accounts.

```python
from plantuml_compose import class_diagram, render

d = class_diagram(title="Qualified Association")
el = d.elements
r = d.relationships

bank = el.class_("Bank")
account = el.class_("Account")
d.add(bank, account)

# Bank uses accountNumber as a key to look up accounts
d.connect(r.association(
    bank, account,
    target_label="*",
    qualifier="accountNumber",
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGWiJSp9JCjCJL5mB2xEJyvCBCdCp-DApaaiBbPmIipBXZ8TavFpI_DAk4122j6949vVQMvIQb6iWgwkdOAIbX9SaKDgNWhG1W00)



The qualifier appears as a small box on the source side of the relationship.

### Association Class

When a relationship itself has attributes, use an association class. For example, when a Student enrolls in a Course, the Enrollment has its own properties (grade, enrollment date).

```python
from plantuml_compose import class_diagram, render

d = class_diagram(title="Association Class")
el = d.elements
r = d.relationships

student = el.class_("Student")
course = el.class_("Course")

# Enrollment captures attributes of the relationship
enrollment = el.class_("Enrollment", members=(
    el.field("grade", "str"),
    el.field("enrolled_at", "date"),
))

d.add(student, course, enrollment)

# Create the many-to-many relationship
d.connect(
    r.association(student, course, source_label="*", target_label="*"),
    r.association_class(student, course, enrollment),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/JOv12W8n34NtESLdLYhE7C25Z0oUm0D8c0OfT5feqfLuT-kGXPk4zn_yP5RZQcrBPD6IuAPQriWMIyQIM9NMtyJ3Mf1iJajfLSNXdcj9QUiMRm9UbOFW0hNQINOfuSdMiy0cz24lmt0QC8xNVNlbmTtPWoEcwUy2pP93__OB)



The association class is shown connected to the relationship line with a dashed line.

## Packages

Group related classes:

```python
from plantuml_compose import class_diagram, render

d = class_diagram(title="Package Structure")
el = d.elements
r = d.relationships

user = el.class_("User")
order = el.class_("Order")
domain = el.package("domain", user, order)

user_service = el.class_("UserService")
order_service = el.class_("OrderService")
services = el.package("services", user_service, order_service)

d.add(domain, services)

d.connect(
    r.uses(user_service, user),
    r.uses(order_service, order),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/NOvB2e0m34JtFKLEu1746oY81mXja6BzaAHknBjRh8gwd9StJ2fHP8rZCEer43He1-m9MkLeDJAPvI9k7j5Fi1a06r04EY5-GiqkfVsnqstrbkJdjnb_QpVSpKk1eYZpnDivQTwgQ7BfxmC0)



### Package Styles

```python
from plantuml_compose import class_diagram, render

d = class_diagram()
el = d.elements

user = el.class_("User")
models = el.package("models", user, style="rectangle")

user_svc = el.class_("UserService")
services = el.package("services", user_svc, style="folder")

logger = el.class_("Logger")
utils = el.package("utils", logger, style="cloud")

d.add(models, services, utils)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIf8JCvEJ4zLoCrFISqfLh2n2KfDBadCIyz9jRDJgEPIK4ZEIImkLWWjJYtYgeMh1lBACfDJGUhTydDIKeim50T3L23fAIt915lWd9DVceAYtYS_FHril4DgNWhGKG00)



### Nested Packages

```python
from plantuml_compose import class_diagram, render

d = class_diagram()
el = d.elements

user = el.class_("User")
order = el.class_("Order")
domain = el.package("domain", user, order)

controller = el.class_("UserController")
api = el.package("api", controller)

root = el.package("com.example", domain, api)
d.add(root)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIf8JCvEJ4zLK4hEpzLBhKZCBSX9LLAevb9GWCcavEScPkQ1XHGKadCIYuiLGejJYv2u_aKfO7ujagx4WamCBSxvUIL5-JavKCMrN0wfUIb0Hm00)



## Layout Hints

### Together Block

Keep related classes close:

```python
from plantuml_compose import class_diagram, render

d = class_diagram()
el = d.elements

a = el.class_("ModelA")
b = el.class_("ModelB")
c = el.class_("ModelC")
d.together(a, b, c)

sep = el.class_("Separate")
d.add(sep)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9JqyjoKWjKgZcKb18paaiBbRmpKz9pN54vJgXSfsvQhaWtE3KWiIYn99KBeVKl1IWWG00)



### Direction Hints

```python
from plantuml_compose import class_diagram, render

d = class_diagram()
el = d.elements
r = d.relationships

center = el.class_("Center")
left = el.class_("Left")
right = el.class_("Right")
up = el.class_("Up")
down = el.class_("Down")
d.add(center, left, right, up, down)

d.connect(
    r.association(center, left, direction="left"),
    r.association(center, right, direction="right"),
    r.association(center, up, direction="up"),
    r.association(center, down, direction="down"),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEIImkLd1EpIj9BO9oV5BJIg3CeCpq31Wxj03ASCalp-E2w53GpT6rWsY02HG11I3QO2AbG16WPXWt1SW56-6GcfS2T080)



## Notes

```python
from plantuml_compose import class_diagram, render

d = class_diagram()
el = d.elements

user = el.class_("User")
d.add(user)

# Note attached to a class
d.note("Primary domain entity", target=user)

# Note on specific position
d.note("Documentation here", position="left", target=user)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/JOqn3e0W301tNj5tE37u01SVq43H9j0cfGpyNgABwzqb5xkZ-MWrf8gzmzd9WgWJ65-tWvONRN0ODxG9MHko08cppw-iL7xXhccqfT5P1Muo2f4ahyK3)



## Hide/Show Elements

```python
from plantuml_compose import class_diagram, render

d = class_diagram()
el = d.elements

# Hide empty compartments
d.hide("empty members")

# Hide interface circles
d.hide("circle")

user = el.class_("User", members=(
    el.field("id", "int"),
))
serializable = el.interface("Serializable")
d.add(user, serializable)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/9On12e0m30JlUSM-mvD_41yGsnK3hKXI3oh-tOANEGpCZD7KsrcBR9O9rgDTgAmBFNwLp5EXfA8Hc8EEHm3B661xarSwwQicOgAR5hjrwS78FVVl1m00)



## Styling

### Class Styling

```python
from plantuml_compose import class_diagram, render

d = class_diagram()
el = d.elements

# Styled class
error = el.class_("Error", style={"background": "#FFCDD2"})

success = el.class_("Success", style={"background": "#C8E6C9"})

warning = el.class_("Warning", style={
    "background": "#FFF9C4",
    "line": {"color": "orange"},
})

d.add(error, success, warning)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEIImkLd0jAielKb1sStDsSJ62YWMN9YUd0cbbPmjNCsTBg6XuOb5UPbwwWd9IOdAsbPkRcwMpYNLEPbwgLNvHObvwAfT3QbuAq600)



## Complete Example: E-Commerce Domain Model

```python
from plantuml_compose import class_diagram, render

d = class_diagram(title="E-Commerce Domain Model")
el = d.elements
r = d.relationships

# Interfaces
auditable = el.interface("Auditable")

# Entities
user = el.class_("User", members=(
    el.field("id", "UUID", visibility="private"),
    el.field("email", "str", visibility="private"),
    el.field("name", "str"),
    el.separator(),
    el.method("authenticate(password)", "bool", visibility="public"),
))

order = el.class_("Order", members=(
    el.field("id", "UUID", visibility="private"),
    el.field("status", "OrderStatus"),
    el.field("total", "Decimal"),
    el.separator(),
    el.method("addItem(product, qty)", visibility="public"),
    el.method("calculateTotal()", "Decimal", visibility="private"),
))

product = el.class_("Product", members=(
    el.field("id", "UUID", visibility="private"),
    el.field("name", "str"),
    el.field("price", "Decimal"),
    el.field("stock", "int"),
))

line_item = el.class_("LineItem")
status = el.enum("OrderStatus", "PENDING", "PAID", "SHIPPED", "DELIVERED")

d.add(auditable, user, order, product, line_item, status)

# Relationships
d.connect(
    r.implements(user, auditable),
    r.implements(order, auditable),

    # User has many orders
    r.aggregation(user, order, part_label="*"),

    # Order contains line items (composition)
    r.contains(order, line_item, whole_label="1", part_label="1..*"),

    # Line item references product
    r.association(line_item, product, source_label="*", target_label="1"),

    # Order uses status
    r.uses(order, status),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/RL91JiCm4Bpx5LPERS6HUaMeQaKYY5HAH2btrrw4XHqNPoE4e7zdxORG0fTePzOpErvdtg8Cs3dBqA05Neehxnm41RpmJfg6tteDbfa68Jn9eXUTDYYt5fYoictvfeN0FnZdmcX-mJURgeW0I6m9jnW8DjB108IWpvdiy1aQD4eYZ7RazEQ37jEXhVUMxNltkw3_iwVKsBM4Kt-T4D7eKSQX1IZZfFsPfNM5u4Qxu7Mdy9o_uliuTfMqghEKu24gH-CZxNU2-g3vc-7aJhjW59nCRj6h5s9eSuFNqZGGWp1eEdUSFRdNvQgeLjUnMgG9wvkghijO5UMoUYplgTwpuG7uvMUUf_t_vf8pIo-JJJFkXU3P9ElfmqeZFudyDC-fDIJxBf90Y5awsE-Wb-Rvx6JlSsWq_K5V)



## Quick Reference

| Method | Description |
|--------|-------------|
| `el.class_(name)` | Create a class |
| `el.abstract(name)` | Create abstract class |
| `el.interface(name)` | Create interface |
| `el.enum(name, *values)` | Create enum |
| `el.annotation(name)` | Create annotation |
| `el.entity(name)` | Create entity |
| `el.exception(name)` | Create exception |
| `el.metaclass(name)` | Create metaclass |
| `el.protocol(name)` | Create protocol |
| `el.struct(name)` | Create struct |
| `el.circle(name)` | Create circle (shorthand) |
| `el.diamond(name)` | Create diamond (shorthand) |
| `el.package(name, *children)` | Package container |
| `el.field(name, type)` | Create field member |
| `el.method(name, return_type)` | Create method member |
| `el.separator(style, label)` | Create separator member |
| `r.extends(child, parent)` | Inheritance |
| `r.implements(class, interface)` | Implementation |
| `r.has(whole, part)` | Aggregation (hollow diamond) |
| `r.contains(whole, part)` | Composition (filled diamond) |
| `r.composition(whole, part)` | Composition (alias) |
| `r.aggregation(whole, part)` | Aggregation (alias) |
| `r.uses(user, used)` | Dependency |
| `r.association(a, b)` | Association |
| `r.association(a, b, qualifier=key)` | Qualified association |
| `r.association_class(a, b, cls)` | Link class to relationship |
| `d.together(*elements)` | Layout grouping |
| `d.note(text, target=class)` | Add note |
| `d.hide(target)` | Hide elements |
| `d.show(target)` | Show elements |

### Member Factory Methods

| Method | Description |
|--------|-------------|
| `el.field(name, type)` | Add field |
| `el.method(name, return_type)` | Add method |
| `el.field(name, type, modifier="static")` | Add static field |
| `el.method(name, return_type, modifier="static")` | Add static method |
| `el.method(name, return_type, modifier="abstract")` | Add abstract method |
| `el.separator(style, label)` | Add separator line |
