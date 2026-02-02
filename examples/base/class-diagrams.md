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
from plantuml_compose import class_diagram

with class_diagram(title="Simple Model") as d:
    user = d.class_("User")
    order = d.class_("Order")

    d.has(user, order, whole_label="1", part_label="*")

print(d.render())
```

## Creating Classes

### Basic Classes

```python
from plantuml_compose import class_diagram

with class_diagram() as d:
    # Simple class
    user = d.class_("User")

    # Abstract class
    shape = d.abstract("Shape")

    # Interface
    serializable = d.interface("Serializable")

    # Enum with values
    status = d.enum("Status", "PENDING", "ACTIVE", "CLOSED")

    # Annotation
    deprecated = d.annotation("Deprecated")

print(d.render())
```

### Additional Class Types

```python
from plantuml_compose import class_diagram

with class_diagram() as d:
    # Entity (database/domain entity)
    entity = d.entity("Customer")

    # Exception
    error = d.exception("ValidationError")

    # Metaclass
    meta = d.metaclass("Type")

    # Protocol (Python-style interface)
    proto = d.protocol("Iterable")

    # Struct (value type)
    point = d.struct("Point")

    # Circle/Diamond (shorthand notations)
    c = d.circle("C")
    d_ = d.diamond("D")

print(d.render())
```

### Generic Classes

```python
from plantuml_compose import class_diagram

with class_diagram() as d:
    # Generic class
    collection = d.class_("Collection", generics="T")

    # Bounded generic
    comparable = d.class_("Comparable", generics="T extends Number")

print(d.render())
```

### Classes with Members

```python
from plantuml_compose import class_diagram

with class_diagram(title="User Model") as d:
    with d.class_with_members("User") as user:
        # Fields
        user.field("id", "int", visibility="private")
        user.field("email", "str", visibility="private")
        user.field("created_at", "datetime", visibility="protected")

        # Separator
        user.separator()

        # Methods
        user.method("login(password: str)", "bool", visibility="public")
        user.method("validate()", visibility="private")

print(d.render())
```

### Visibility Modifiers

```python
from plantuml_compose import class_diagram

with class_diagram() as d:
    with d.class_with_members("Example") as ex:
        # Public: + (accessible everywhere)
        ex.field("public_field", "str", visibility="public")

        # Private: - (only in this class)
        ex.field("private_field", "int", visibility="private")

        # Protected: # (class and subclasses)
        ex.field("protected_field", "bool", visibility="protected")

        # Package: ~ (same package only)
        ex.field("package_field", "float", visibility="package")

print(d.render())
```

### Static and Abstract Members

```python
from plantuml_compose import class_diagram

with class_diagram() as d:
    with d.class_with_members("Logger") as logger:
        # Static field (underlined in UML)
        logger.static_field("instance", "Logger", visibility="private")

        # Static method
        logger.static_method("getInstance()", "Logger", visibility="public")

        # Abstract method (italic in UML)
        logger.abstract_method("log(msg: str)", visibility="public")

print(d.render())
```

### Member Separators

```python
from plantuml_compose import class_diagram

with class_diagram() as d:
    with d.class_with_members("Service") as svc:
        svc.field("config", "Config")
        svc.field("logger", "Logger")

        svc.separator(label="lifecycle")

        svc.method("start()")
        svc.method("stop()")

        svc.separator(style="dotted", label="internal")

        svc.method("process()", visibility="private")

print(d.render())
```

## Relationships

### Inheritance (extends)

```python
from plantuml_compose import class_diagram

with class_diagram(title="Inheritance") as d:
    animal = d.class_("Animal")
    dog = d.class_("Dog")
    cat = d.class_("Cat")

    # Dog extends Animal
    d.extends(dog, animal)
    d.extends(cat, animal)

print(d.render())
```

### Implementation (implements)

```python
from plantuml_compose import class_diagram

with class_diagram(title="Interface Implementation") as d:
    comparable = d.interface("Comparable")
    serializable = d.interface("Serializable")
    user = d.class_("User")

    d.implements(user, comparable)
    d.implements(user, serializable)

print(d.render())
```

### Aggregation (has)

Aggregation means the part can exist independently. A Team has Players, but Players can exist without the Team.

```python
from plantuml_compose import class_diagram

with class_diagram(title="Aggregation") as d:
    team = d.class_("Team")
    player = d.class_("Player")

    # One team has many players
    d.has(team, player, whole_label="1", part_label="*")

print(d.render())
```

### Composition (contains)

Composition means the part cannot exist without the whole. A House contains Rooms; if the House is destroyed, so are the Rooms.

```python
from plantuml_compose import class_diagram

with class_diagram(title="Composition") as d:
    order = d.class_("Order")
    line_item = d.class_("LineItem")

    # One order contains one or more line items
    d.contains(order, line_item, whole_label="1", part_label="1..*")

print(d.render())
```

### Dependency (uses)

A depends on B if A uses B but doesn't own it.

```python
from plantuml_compose import class_diagram

with class_diagram(title="Dependency") as d:
    service = d.class_("OrderService")
    logger = d.class_("Logger")
    validator = d.class_("Validator")

    d.uses(service, logger)
    d.uses(service, validator)

print(d.render())
```

### Association

A general relationship between classes.

```python
from plantuml_compose import class_diagram

with class_diagram(title="Association") as d:
    student = d.class_("Student")
    course = d.class_("Course")

    # Students enroll in courses
    d.associates(
        student, course,
        source_label="*",
        target_label="*",
        label="enrolls in"
    )

print(d.render())
```

### Relationship Labels

```python
from plantuml_compose import class_diagram

with class_diagram() as d:
    company = d.class_("Company")
    employee = d.class_("Employee")

    d.has(
        company, employee,
        whole_label="1",      # One company
        part_label="1..*",    # One or more employees
        label="employs"       # Relationship name
    )

print(d.render())
```

Common cardinality notations:
- `1` - exactly one
- `*` - zero or more
- `0..1` - zero or one (optional)
- `1..*` - one or more
- `n..m` - between n and m

### Qualified Association

A qualified association shows how one class uses a key to access instances of another. For example, a Bank uses an account number to look up Accounts.

```python
from plantuml_compose import class_diagram

with class_diagram(title="Qualified Association") as d:
    bank = d.class_("Bank")
    account = d.class_("Account")

    # Bank uses accountNumber as a key to look up accounts
    d.associates(
        bank, account,
        target_label="*",
        qualifier="accountNumber"
    )

print(d.render())
```

The qualifier appears as a small box on the source side of the relationship.

### Association Class

When a relationship itself has attributes, use an association class. For example, when a Student enrolls in a Course, the Enrollment has its own properties (grade, enrollment date).

```python
from plantuml_compose import class_diagram

with class_diagram(title="Association Class") as d:
    student = d.class_("Student")
    course = d.class_("Course")

    # Enrollment captures attributes of the relationship
    with d.class_with_members("Enrollment") as enrollment:
        enrollment.field("grade", "str")
        enrollment.field("enrolled_at", "date")

    # Create the many-to-many relationship
    d.associates(student, course, source_label="*", target_label="*")

    # Link Enrollment as the association class
    d.association_class(student, course, enrollment)

print(d.render())
```

The association class is shown connected to the relationship line with a dashed line.

## Packages

Group related classes:

```python
from plantuml_compose import class_diagram

with class_diagram(title="Package Structure") as d:
    with d.package("domain") as domain:
        user = domain.class_("User")
        order = domain.class_("Order")

    with d.package("services") as services:
        user_service = services.class_("UserService")
        order_service = services.class_("OrderService")

    d.uses(user_service, user)
    d.uses(order_service, order)

print(d.render())
```

### Package Styles

```python
from plantuml_compose import class_diagram

with class_diagram() as d:
    with d.package("models", style="rectangle") as models:
        models.class_("User")

    with d.package("services", style="folder") as services:
        services.class_("UserService")

    with d.package("utils", style="cloud") as utils:
        utils.class_("Logger")

print(d.render())
```

### Nested Packages

```python
from plantuml_compose import class_diagram

with class_diagram() as d:
    with d.package("com.example") as root:
        with root.package("domain") as domain:
            domain.class_("User")
            domain.class_("Order")

        with root.package("api") as api:
            api.class_("UserController")

print(d.render())
```

## Layout Hints

### Together Block

Keep related classes close:

```python
from plantuml_compose import class_diagram

with class_diagram() as d:
    with d.together() as group:
        group.class_("ModelA")
        group.class_("ModelB")
        group.class_("ModelC")

    d.class_("Separate")

print(d.render())
```

### Direction Hints

```python
from plantuml_compose import class_diagram

with class_diagram() as d:
    center = d.class_("Center")
    left = d.class_("Left")
    right = d.class_("Right")
    up = d.class_("Up")
    down = d.class_("Down")

    d.associates(center, left, direction="left")
    d.associates(center, right, direction="right")
    d.associates(center, up, direction="up")
    d.associates(center, down, direction="down")

print(d.render())
```

## Notes

```python
from plantuml_compose import class_diagram

with class_diagram() as d:
    user = d.class_("User")

    # Note attached to a class
    d.note("Primary domain entity", of=user)

    # Note on specific position
    d.note("Documentation here", position="left", of=user)

print(d.render())
```

## Hide/Show Elements

```python
from plantuml_compose import class_diagram

with class_diagram() as d:
    # Hide empty compartments
    d.hide("empty members")

    # Hide interface circles
    d.hide("circle")

    with d.class_with_members("User") as user:
        user.field("id", "int")

    d.interface("Serializable")

print(d.render())
```

## Styling

### Class Styling

```python
from plantuml_compose import class_diagram

with class_diagram() as d:
    # Styled class
    error = d.class_("Error", style={"background": "#FFCDD2"})

    success = d.class_("Success", style={"background": "#C8E6C9"})

    warning = d.class_("Warning", style={
        "background": "#FFF9C4",
        "line": {"color": "orange"}
    })

print(d.render())
```

## Complete Example: E-Commerce Domain Model

```python
from plantuml_compose import class_diagram

with class_diagram(title="E-Commerce Domain Model") as d:
    # Interfaces
    auditable = d.interface("Auditable")

    # Entities
    with d.class_with_members("User") as user:
        user.field("id", "UUID", visibility="private")
        user.field("email", "str", visibility="private")
        user.field("name", "str")
        user.separator()
        user.method("authenticate(password)", "bool", visibility="public")

    with d.class_with_members("Order") as order:
        order.field("id", "UUID", visibility="private")
        order.field("status", "OrderStatus")
        order.field("total", "Decimal")
        order.separator()
        order.method("addItem(product, qty)", visibility="public")
        order.method("calculateTotal()", "Decimal", visibility="private")

    with d.class_with_members("Product") as product:
        product.field("id", "UUID", visibility="private")
        product.field("name", "str")
        product.field("price", "Decimal")
        product.field("stock", "int")

    line_item = d.class_("LineItem")
    status = d.enum("OrderStatus", "PENDING", "PAID", "SHIPPED", "DELIVERED")

    # Relationships
    d.implements(user, auditable)
    d.implements(order, auditable)

    # User has many orders
    d.has(user, order, whole_label="1", part_label="*")

    # Order contains line items (composition)
    d.contains(order, line_item, whole_label="1", part_label="1..*")

    # Line item references product
    d.associates(line_item, product, source_label="*", target_label="1")

    # Order uses status
    d.uses(order, status)

print(d.render())
```

## Quick Reference

| Method | Description |
|--------|-------------|
| `d.class_(name)` | Create a class |
| `d.abstract(name)` | Create abstract class |
| `d.interface(name)` | Create interface |
| `d.enum(name, *values)` | Create enum |
| `d.annotation(name)` | Create annotation |
| `d.entity(name)` | Create entity |
| `d.exception(name)` | Create exception |
| `d.metaclass(name)` | Create metaclass |
| `d.protocol(name)` | Create protocol |
| `d.struct(name)` | Create struct |
| `d.circle(name)` | Create circle (shorthand) |
| `d.diamond(name)` | Create diamond (shorthand) |
| `d.class_with_members(name)` | Class with member builder |
| `d.extends(child, parent)` | Inheritance |
| `d.implements(class, interface)` | Implementation |
| `d.has(whole, part)` | Aggregation (hollow diamond) |
| `d.contains(whole, part)` | Composition (filled diamond) |
| `d.uses(user, used)` | Dependency |
| `d.associates(a, b)` | Association |
| `d.associates(a, b, qualifier=key)` | Qualified association |
| `d.association_class(a, b, cls)` | Link class to relationship |
| `d.package(name)` | Package container |
| `d.together()` | Layout grouping |
| `d.note(text, of=class)` | Add note |
| `d.hide(target)` | Hide elements |
| `d.show(target)` | Show elements |

### Member Builder Methods

| Method | Description |
|--------|-------------|
| `field(name, type)` | Add field |
| `method(name, return_type)` | Add method |
| `static_field(name, type)` | Add static field |
| `static_method(name, return_type)` | Add static method |
| `abstract_method(name, return_type)` | Add abstract method |
| `separator(style, label)` | Add separator line |
