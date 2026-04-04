# Class Diagrams

Class diagrams show static structure: types, their attributes, methods, and relationships. Use them for domain modeling, API contracts, inheritance hierarchies, and entity-relationship schemas.

## Quick Start

```python
from plantuml_compose import class_diagram, render

d = class_diagram(title="Simple Model")
el = d.elements
r = d.relationships

user = el.class_("User", members=(
    el.field("name", "str"),
    el.method("save()"),
))
order = el.class_("Order")

d.add(user, order)
d.connect(r.has(user, order, part_label="*"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGZEp2q0KhxvAQavNCavYSN52g75gKKArLmA2dc9kQaALWh59KL0Jd5YMQg69bSjL95_KKfg4HTOgPQkheAIbX9Ko24rBmLeF000)



## Elements

All element factories live on `d.elements` (aliased as `el` by convention). Every factory returns an `EntityRef` that you pass to `d.add()`.

### Class Types

```python
from plantuml_compose import class_diagram, render

d = class_diagram()
el = d.elements

# Standard class
user = el.class_("User")

# Abstract class (italicized name)
base = el.abstract("BaseModel")

# Interface (<<interface>> stereotype)
repo = el.interface("Repository")

# Python protocol (typing.Protocol)
proto = el.protocol("Iterable")

# Java-style annotation (@interface)
ann = el.annotation("Deprecated")

# JPA/database entity
ent = el.entity("Customer")

# Exception class
err = el.exception("NotFoundError")

# Python metaclass
meta = el.metaclass("ABCMeta")

# C-style struct
point = el.struct("Point")

# Shorthand circle notation
c = el.circle("C")

# Shorthand diamond notation
d_node = el.diamond("D")

d.add(user, base, repo, proto, ann, ent, err, meta, point, c, d_node)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/9OzB2iCm34JtEeMFaYPfeOkKKkW155a5WoqPMORczZNDSZxmPgRcQDvB1ihOMdWtDi2zkI5vEBqP6syQEKCIP_iWSNXnrPPSxO1gwagQmts4k6S65557JofXvMfCw1o1nPCVOUdDjGmAVudhl_HGlscNU3LJWyAE9_WoBziGCDRqiUQfWm-KZ3A71MB2eXB32XDB71T-)



All class-type factories share the same signature:

```text
el.class_(
    name,
    *,
    ref=None,          # short alias for connections (default: sanitized name)
    stereotype=None,   # str or Stereotype object
    style=None,        # StyleLike dict for inline visual override
    generics=None,     # generic type parameter, e.g. "T"
    members=(),        # tuple of field/method/separator data
)
```

### Enums

Enums accept positional value strings instead of `members=`:

```python
from plantuml_compose import class_diagram, render

d = class_diagram()
el = d.elements

status = el.enum("OrderStatus", "PENDING", "SHIPPED", "DELIVERED")
color = el.enum("Color", "RED", "GREEN", "BLUE", stereotype="flags")

d.add(status, color)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhDAyrLy2zAIIqABaaiAIrMgEPIK0XmzNFnz7C7ie8zF0C2N5s0B1TN7yymro0WknQYoJa_9xz8mSOcBISnlTZE3gmn2ApKFSZLrGz8E_c4kW9LEwJcfG2j0W00)



### Generics

Attach a generic type parameter to any class-type element:

```python
from plantuml_compose import class_diagram, render

d = class_diagram()
el = d.elements

list_t = el.class_("List", generics="T")
map_t = el.interface("Map", generics="K, V")

d.add(list_t, map_t)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEIImkLl39B2wn2R7ZoimhIIrAIqnELV1DBB3nrb48i-DoICrB0Qe40000)



### Stereotypes with Spots

Pass a string for a simple stereotype, or a `Stereotype` with a `Spot` for a colored indicator circle:

```python
from plantuml_compose import class_diagram, render, Stereotype, Spot

d = class_diagram()
el = d.elements

# Simple string stereotype
svc = el.class_("OrderService", stereotype="service")

# Stereotype with colored spot (character, color)
ent = el.class_("User", stereotype=Stereotype("entity", Spot("E", "DodgerBlue")))

d.add(svc, ent)
```

### Members: Fields, Methods, Separators

Members are created via `el.field()`, `el.method()`, and `el.separator()`, then passed as a tuple to `members=`:

```python
from plantuml_compose import class_diagram, render

d = class_diagram()
el = d.elements

account = el.class_("Account", members=(
    el.field("id", "int"),
    el.field("balance", "Decimal", visibility="private"),
    el.field("RATE", "float", modifier="static"),
    el.separator(),
    el.method("deposit(amount)", "void", visibility="public"),
    el.method("__repr__()", "str", modifier="abstract"),
))

d.add(account)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/7Ouz2iCm34Ptdq9ZIia5EYNGNg1qDugiWi0_mLQw1DyzSXSXtjCdlgKfLZrIT1InDLY9of4LJWSW0HuWMMsTDuoOYGqycIHXD7XQLeKwlDVFoymt5lmVppRkWVVIH2TCu-7D_Az8637ScbOaxU1zvRrwFmrjq7MtS0vMvm80)



**Visibility values**: `"public"` (+), `"private"` (-), `"protected"` (#), `"package"` (~)

**Modifier values**: `"static"` (underlined), `"abstract"` (italicized)

#### Separator styles

```text
el.separator()                          # solid line (default)
el.separator(style="dotted")            # dotted line
el.separator(style="double")            # double line
el.separator(style="underline")         # underline
el.separator(style="solid", label="internals")  # labeled separator
```

### Bulk Member Creation

`el.fields()` and `el.methods()` create multiple members from tuples. Each tuple is `(name,)` or `(name, type)`:

```python
from plantuml_compose import class_diagram, render

d = class_diagram()
el = d.elements

node = el.class_("HtmlNode", members=(
    *el.fields(
        ("tag", "str"),
        ("attrs", "dict[str, Attr]"),
        ("children", "list[Node]"),
    ),
    el.separator(),
    *el.methods(
        ("render()", "str"),
        ("resolve()", "Generator[str]"),
        ("__html__()", "str"),
    ),
))

d.add(node)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/FOun3i8m34NtdC8ZbUW5cDe99YvGeIXAB1h9RIJRi23kpWz35yj-t__RatbIVsqIiYGpklaczrQOFe78qvCkPAxeaxiQfbApBq1dca4UKF9QfIZl4AMQBztU-JYYW1VMqt3aA5kJD__9bNVMv4rxOBV4kE9-ZCV-Dqm8m7i_)



### Packages

Packages group classes visually. Children are positional arguments. The `style=` keyword selects the container shape:

```python
from plantuml_compose import class_diagram, render

d = class_diagram()
el = d.elements
r = d.relationships

# Default package style (tab folder)
pkg = el.package("domain",
    el.class_("User"),
    el.class_("Order"),
)

# All package styles:
#   "package" (default), "node", "rectangle", "folder",
#   "frame", "cloud", "database"
infra = el.package("infrastructure",
    el.class_("PostgresRepo"),
    style="database",
    color="#E8EAF6",
)

d.add(pkg, infra)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/JOqn2eD044LxJp7W7OA5Y85egmWUu6Tt8gBkoini5N9tjvAK3nxljMeGIyTUd70R5YOV3wo1lWMHsw5AixBSC8ZFzBljDNm4QfAS9M6gwnSCRoWt3PLTrJtxnrzgZ6gBi4vynXnfEVYylW00)



Access nested children via attribute or bracket notation:

```text
d.connect(r.uses(pkg.User, infra.PostgresRepo))
# or bracket access for names with spaces/symbols:
# d.connect(r.uses(pkg["User"], infra["PostgresRepo"]))
```

## Relationships / Connections

All relationship factories live on `d.relationships` (aliased as `r` by convention). Pass results to `d.connect()`.

### Typed Relationships

```python
from plantuml_compose import class_diagram, render

d = class_diagram()
el = d.elements
r = d.relationships

parent = el.abstract("Animal")
dog = el.class_("Dog")
walkable = el.interface("Walkable")
leg = el.class_("Leg")
kennel = el.class_("Kennel")
food = el.class_("Food")
collar = el.class_("Collar")

d.add(parent, dog, walkable, leg, kennel, food, collar)

d.connect(
    # Extension (inheritance): child extends parent
    # Renders as: Animal <|-- Dog
    r.extends(dog, parent),

    # Implementation: class implements interface
    # Renders as: Walkable <|.. Dog
    r.implements(dog, walkable),

    # Composition (strong ownership, filled diamond)
    # has() for simple cases
    r.has(dog, leg, part_label="4"),

    # contains() when you need both whole_label and part_label
    r.contains(kennel, dog, whole_label="1", part_label="*"),

    # Aggregation (weak ownership, hollow diamond)
    r.aggregation(dog, collar, part_label="0..1"),

    # Composition (alias for has, same arrow)
    r.composition(kennel, food, part_label="*"),

    # Dependency (dotted arrow)
    r.uses(dog, food, label="eats"),

    # Association (solid arrow, generic link)
    r.association(dog, kennel, label="lives in"),

    # Arrow (same as association, simpler name)
    r.arrow(dog, food),

    # Lollipop (interface provision)
    r.lollipop(dog, walkable),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/HP0n3y8W48Nt_eeBapQ1QE9aJAFHkEZkV6tFXdY51D397oy5MWUIk_VUVGSSVK0NtYDNsFhWi0lGCNeF9wD7v2et5pjKsWHoJ-m87iWlR9cAUQUXL3SoXkQPgxLzAS-M6LsLaN3uIfc8CoSgIYKb7gYZAtOYOJCGn5PakHPBp4xzHgbe5Nm9py6qVqegrQG6za0OVDAaRCfjeyhwGnwqMPnbTBMM_zSUoVJnetu0)



### Common Parameters

Every relationship method supports:

| Parameter | Description |
|---|---|
| `label=` | Text on the arrow |
| `style=` | `LineStyleLike` -- string (`"dashed"`), dict, or `LineStyle` |
| `direction=` | `"up"`, `"down"`, `"left"`, `"right"` -- layout hint |
| `note=` | Inline note text on the relationship |
| `length=` | Arrow length (number of dashes, e.g. `length=3`) |

### Cardinality Labels

`source_label=` and `target_label=` add multiplicity text at each end:

```text
r.association(order, product,
    label="contains",
    source_label="1",
    target_label="*",
)
```

The `has()`, `contains()`, `aggregation()`, and `composition()` methods use semantic naming:

```text
r.has(order, item, part_label="*")
r.contains(order, item, whole_label="1", part_label="*")
r.aggregation(fleet, car, part_label="*")
```

### IE (Crow's Foot) Notation

For ER diagrams, use Information Engineering notation. All four support `source_label=` and `target_label=`:

```python
from plantuml_compose import class_diagram, render

d = class_diagram()
el = d.elements
r = d.relationships

customer = el.entity("Customer")
order = el.entity("Order")
item = el.entity("LineItem")
product = el.entity("Product")

d.add(customer, order, item, product)
d.connect(
    r.one_or_many(customer, order, label="places"),
    r.zero_or_many(order, item, label="contains"),
    r.exactly_one(item, product, label="references"),
    r.zero_or_one(customer, product, label="reviews"),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/NOz12iCm30JlUeK_a0_a5EYfK4Y_O6mL3B5K9BcbuFoz3ebJw76qEmkQrBnOoGiWMRAFknGrpYYTPua_k2N2gs7kV1UE9HXqoQrr67R5ZUwv-80AEwxSakwtC32PJwHmtkhc7ekj8FX0GTeMpldAVvLNmhV2X1JR2ry0)



### Association Classes

Link a class to an existing relationship to form an association class:

```python
from plantuml_compose import class_diagram, render

d = class_diagram()
el = d.elements
r = d.relationships

student = el.class_("Student")
course = el.class_("Course")
enrollment = el.class_("Enrollment", members=(
    el.field("grade", "str"),
    el.field("semester", "str"),
))

d.add(student, course, enrollment)
d.connect(
    r.association(student, course, label="enrolled in"),
    r.association_class(student, course, enrollment),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/JOun2iCm34LtdUAF3JGvG8OI23r1Js3gJoZO3aZoL7htcgAXuzCJJzhCatglHPubcU7XFRDvq7vsDGRScvwbr67n5k3Gb8aLvZh8M6bEZS578eHvlaLcAFuIp7WrkSJ6DVI4PVcx8HjR7dzz0G00)



### Generic Relationship

`r.relationship()` gives full control over all parameters when the convenience methods don't fit:

```text
r.relationship(a, b,
    type="composition",
    label="owns",
    source_label="1",
    target_label="*",
    style="dashed",
    direction="down",
    length=3,
    left_head="<|",
    right_head="*",
)
```

### Custom Arrow Heads

Override the default arrowheads with `left_head=` and `right_head=`:

```text
r.relationship(a, b, left_head="<|", right_head="*")
r.relationship(a, b, left_head="o", right_head="|>")
```

### Line Style

The `style=` parameter accepts a string shorthand, a dict, or a `LineStyle` object:

```text
# String shorthand
r.extends(child, parent, style="dashed")

# Dict form
r.uses(a, b, style={"pattern": "dotted", "color": "gray", "thickness": 2})
```

### Bulk Relationship Helpers

#### arrows() -- multiple arrows from tuples

```text
d.connect(r.arrows(
    (a, b),
    (b, c, "uses"),     # optional label as third element
    (c, d),
))
```

#### arrows_from() -- fan-out from one source

```text
d.connect(r.arrows_from(controller,
    model,
    (view, "renders"),   # mix bare targets and (target, label) tuples
    service,
    style="dashed",
    direction="down",
))
```

#### extends_from() -- multiple children, one parent

```text
d.connect(r.extends_from([dog, cat, bird], animal))
```

#### compositions_from() -- one whole, many parts

```text
d.connect(r.compositions_from(car, [engine, wheel, frame]))
```

All bulk helpers return lists that `d.connect()` flattens automatically.

## Notes

```python
from plantuml_compose import class_diagram, render

d = class_diagram()
el = d.elements

user = el.class_("User")
d.add(user)

# Floating note
d.note("This is the domain model")

# Targeted note with position and color
d.note("Primary entity", target=user, position="left", color="#FFFFCC")

# Note targeting a specific class member
d.note("Must be unique", target=user, member="id")

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/JOv12iCm30JlViM-mwTy8D13yW0tLcA1BLD9FkJt3Is4m1ndbftCa_feDMmrcM4rqY3T2Sf7yOYbiE722o7tbbZGUgRwbohjZhx_ieYNSajwWiJPpyVChKJE4VCmnvimX3-3maIIhmDV)



**Positions**: `"right"` (default), `"left"`, `"top"`, `"bottom"`

## Layout and Organization

### together()

Group elements for layout proximity (placed adjacent to each other):

```text
d.together(user, order, product)
```

### hide() / show() / remove() / restore()

Control element visibility at the diagram level:

```text
# Hide all empty member compartments
d.hide("empty members")

# Hide the circle icon on class names
d.hide("circle")

# Show methods compartment
d.show("methods")

# Remove elements entirely (reclaims space unlike hide)
d.remove("empty members")

# Restore previously removed/hidden elements
d.restore("methods")
```

### Diagram-level options

```python
from plantuml_compose import class_diagram, render

d = class_diagram(
    hide_empty_members=True,      # suppress empty field/method compartments
    hide_circle=True,             # remove the (C)/(I)/(A) circle icons
    namespace_separator=".",      # control package separator (None disables)
    layout="left_to_right",       # "top_to_bottom" (default) or "left_to_right"
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/9Sox3O0m30N0tbDu0cR8AY5vWANyP3yAjWU9zefBmUoyUvE6WygfRkT5hUOej3aaG0six9dJTPFBAXHzyT6EliFZfs9U6YHXrAzx0G00)



## Styling

### Inline Element Style

Any class-type element accepts `style=` as a `StyleLike` dict:

```text
user = el.class_("User", style={
    "background": "#E3F2FD",
    "line": {"color": "#1976D2"},
    "text_color": "navy",
})
```

### Diagram-Wide Styling with diagram_style=

The `diagram_style=` parameter on `class_diagram()` applies styles globally. Pass a dict with any of these top-level keys:

| Key | Type | Description |
|---|---|---|
| `background` | color | Diagram background |
| `font_name` | str | Default font family |
| `font_size` | int | Default font size |
| `font_color` | color | Default text color |
| `class_` | ElementStyleDict | Style for all classes |
| `interface` | ElementStyleDict | Style for all interfaces |
| `abstract` | ElementStyleDict | Style for all abstract classes |
| `enum` | ElementStyleDict | Style for all enums |
| `annotation` | ElementStyleDict | Style for all annotations |
| `package` | ElementStyleDict | Style for all packages |
| `arrow` | DiagramArrowStyleDict | Style for all relationship arrows |
| `note` | ElementStyleDict | Style for all notes |
| `title` | ElementStyleDict | Style for the title |
| `stereotypes` | dict | Style by stereotype name |

**ElementStyleDict keys**: `background`, `line_color`, `font_color`, `font_name`, `font_size`, `font_style`, `round_corner`, `line_thickness`, `line_style`, `padding`, `margin`, `horizontal_alignment`, `max_width`, `shadowing`, `diagonal_corner`, `word_wrap`, `hyperlink_color`

**DiagramArrowStyleDict keys**: `line_color`, `line_thickness`, `line_pattern`, `font_color`, `font_name`, `font_size`

```python
from plantuml_compose import class_diagram, render

d = class_diagram(
    title="Styled Domain",
    diagram_style={
        "background": "white",
        "class_": {"background": "#E3F2FD", "line_color": "#1976D2", "round_corner": 5},
        "interface": {"background": "#C8E6C9", "font_style": "italic"},
        "abstract": {"background": "#FFF9C4"},
        "enum": {"background": "#F3E5F5"},
        "annotation": {"background": "#FFECB3"},
        "package": {"background": "#F5F5F5"},
        "arrow": {"line_color": "#757575", "font_size": 11},
        "note": {"background": "#FFFDE7"},
        "stereotypes": {
            "entity": {"background": "#FFF9C4", "font_style": "bold"},
            "service": {"background": "#C8E6C9"},
        },
    },
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/ZPB1JiCm38RlVOf8t45TwKgb2KrhcnCdU0AlDIKYTL3YCWtKToSBgJO95L2KGtv__cKxtZe6o-EW4rQiKJpnKMCdQZE0ecJZJi_xfDNWNAsWjp28pqI87RIllJKZTPNHneh3YsBqUW03yPEvQZAvadM8FIZ2gAPbiQvNGNtyXYsX5RbN9dyLCTfdQ779jRfhrbKPOj8GXmQ4Oj2gZHQmTsoXvIK7AMLPtKOOQHmMmQp9vLmO41a6LeQMVPjgbqNypKUXN-n2vl9ixOtnbsBhffXhiDOS8danqY8_dVD8r0UAD8qvrqZ-guz_3kDod7kZkpdTeNrN__YEAPcIpKrSe2rIvvVi2m00)



## Advanced Features

### Diagram Metadata

```python
from plantuml_compose import class_diagram, render
from plantuml_compose.primitives.common import Header, Footer, Legend, Scale

d = class_diagram(
    title="Architecture",
    mainframe="System Overview",
    caption="Generated 2025-01-15",
    header=Header("Draft", position="right"),
    footer="Page %page%",
    legend=Legend("Green = stable\nRed = experimental", position="bottom"),
    scale=Scale(factor=1.5),  # or Scale(width=800)
    theme="plain",            # PlantUML built-in theme name
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/9KzB2i9G3Dpd577XKh52buA2u5BH4yJNQVlWVKeQVxStucQI6MP8PZ-Rg3roeYonz2ePVFlCXipd9_GPyQA5ZN1vIkwWEKW2D-kMB9fl1mrZD0HxA4ZZC1gFa0xAHvNUAA2OaxxMtxZ805vEZaiACbciXKyeK35qlDriszMcMJKj9Gme7T-hMSt4V5AWy8xztNk22rVtxnZl2Hgptv147lZ7QE_WdRu0)



### EntityRef Child Access

When elements are nested inside packages, access children by ref or name:

```python
from plantuml_compose import class_diagram, render

d = class_diagram()
el = d.elements
r = d.relationships

domain = el.package("domain",
    el.class_("User", ref="u"),
    el.class_("Big Order", ref="order"),
)
d.add(domain)

# By ref (attribute access)
d.connect(r.uses(domain.u, domain.order))

# By raw name (bracket access)
d.connect(r.uses(domain["User"], domain["Big Order"]))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIf8JCvEJ4zLICdFJSpCKwZcKb18paaiBbPG2YrEBL9II2nMA4M8EMMcA_WNfK0bya4ihbgkKWKzFJie3vdja9gN0hG30000)



### String References

You can use raw strings instead of `EntityRef` objects for relationships when referring to elements defined elsewhere:

```text
d.connect(r.extends("Child", "Parent"))
```

## Quick Reference

### Element Factories

| Factory | PlantUML | Notes |
|---|---|---|
| `el.class_(name)` | `class Name` | Standard class |
| `el.abstract(name)` | `abstract class Name` | Italic name |
| `el.interface(name)` | `interface Name` | <<interface>> |
| `el.protocol(name)` | `protocol Name` | typing.Protocol |
| `el.annotation(name)` | `annotation Name` | @interface |
| `el.entity(name)` | `entity Name` | Database entity |
| `el.exception(name)` | `exception Name` | Exception class |
| `el.metaclass(name)` | `metaclass Name` | Python metaclass |
| `el.struct(name)` | `struct Name` | C-style struct |
| `el.circle(name)` | `circle Name` | Circle shorthand |
| `el.diamond(name)` | `diamond Name` | Diamond shorthand |
| `el.enum(name, *values)` | `enum Name` | Fixed value set |
| `el.package(name, *children)` | `package Name {}` | Container |

### Relationship Factories

| Factory | Arrow | Meaning |
|---|---|---|
| `r.extends(child, parent)` | `<\|--` | Inheritance |
| `r.implements(child, iface)` | `<\|..` | Implementation |
| `r.has(whole, part)` | `*--` | Composition (simple) |
| `r.contains(whole, part)` | `*--` | Composition (both labels) |
| `r.composition(whole, part)` | `*--` | Composition |
| `r.aggregation(whole, part)` | `o--` | Aggregation |
| `r.association(src, tgt)` | `-->` | Association |
| `r.uses(src, tgt)` | `..>` | Dependency |
| `r.arrow(src, tgt)` | `-->` | Generic arrow |
| `r.lollipop(provider, consumer)` | `()-` | Interface lollipop |
| `r.zero_or_one(src, tgt)` | `\|o--` | IE: optional single |
| `r.exactly_one(src, tgt)` | `\|\|--` | IE: mandatory single |
| `r.zero_or_many(src, tgt)` | `}o--` | IE: optional multiple |
| `r.one_or_many(src, tgt)` | `}\|--` | IE: mandatory multiple |
| `r.association_class(src, tgt, cls)` | dotted | Links class to relationship |
| `r.relationship(src, tgt, type=)` | varies | Full control |

### Bulk Helpers

| Helper | Purpose |
|---|---|
| `el.fields(*tuples)` | Bulk field creation |
| `el.methods(*tuples)` | Bulk method creation |
| `r.arrows(*tuples)` | Multiple arrows |
| `r.arrows_from(src, *targets)` | Fan-out from one source |
| `r.extends_from([children], parent)` | Multiple children extend one parent |
| `r.compositions_from(whole, [parts])` | One whole composes many parts |

### Composer Options

| Parameter | Default | Description |
|---|---|---|
| `title=` | None | Diagram title |
| `mainframe=` | None | Frame around entire diagram |
| `caption=` | None | Caption below diagram |
| `header=` | None | Header text or Header object |
| `footer=` | None | Footer text or Footer object |
| `legend=` | None | Legend text or Legend object |
| `scale=` | None | Scale factor or Scale object |
| `theme=` | None | PlantUML theme name |
| `layout=` | None | `"top_to_bottom"` or `"left_to_right"` |
| `diagram_style=` | None | Global styling dict |
| `hide_empty_members=` | False | Suppress empty compartments |
| `hide_circle=` | False | Remove class-type icon circles |
| `namespace_separator=` | None | Package namespace separator |
