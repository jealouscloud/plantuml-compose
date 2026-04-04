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
