# Component Diagrams

Component diagrams show the structural organization of a system: modular units, the interfaces they expose, and how they connect. Use them for service architectures, plugin systems, and dependency mapping between subsystems.

## Quick Start

```python
from plantuml_compose import component_diagram, render

d = component_diagram(title="Web Stack")
el = d.elements
c = d.connections

api = el.component("API Gateway")
db = el.database("PostgreSQL")

d.add(api, db)
d.connect(c.arrow(api, db, "queries"))

print(render(d))
```

## Elements

All element factories live on `d.elements` (aliased as `el` by convention). Every factory returns an `EntityRef` that you pass to `d.add()`.

### Components

Components are the primary building blocks. They accept nested children as positional arguments:

```python
from plantuml_compose import component_diagram, render

d = component_diagram()
el = d.elements

# Simple component
api = el.component("API")

# Component with description
auth = el.component("Auth Service", description="Handles OAuth2 flows")

# Component with stereotype and inline style
cache = el.component("Cache",
    stereotype="infrastructure",
    style={"background": "#E8F5E9"},
)

# Component with nested children
app = el.component("Application",
    el.component("Controller"),
    el.component("Service Layer"),
    ref="app",
)

d.add(api, auth, cache, app)

print(render(d))
```

Component factory signature:

```text
el.component(
    name,
    *children,             # nested EntityRef elements
    ref=None,              # short alias for connections
    stereotype=None,       # str or Stereotype object
    style=None,            # StyleLike dict for inline visual override
    description=None,      # text shown below the component name
)
```

### Interfaces

Interfaces represent contracts exposed or consumed by components. They render as the small circle (lollipop) or socket notation:

```python
from plantuml_compose import component_diagram, render

d = component_diagram()
el = d.elements

rest = el.interface("REST")
graphql = el.interface("GraphQL", stereotype="api")

d.add(rest, graphql)

print(render(d))
```

### Ports

Ports appear as small squares on component boundaries. Add them as children of a component, then connect other elements to the ports:

```python
from plantuml_compose import component_diagram, render

d = component_diagram()
el = d.elements
c = d.connections

server = el.component("Server",
    el.portin("http_in"),      # input port (inward arrow)
    el.portout("log_out"),     # output port (outward arrow)
    el.port("mgmt"),           # bidirectional port
)
client = el.component("Client")
logger = el.component("Logger")
admin = el.component("Admin Console")

d.add(server, client, logger, admin)

# Connect through ports
d.connect(
    c.arrow(client, server.http_in, "request"),
    c.arrow(server.log_out, logger, "events"),
    c.arrow(admin, server.mgmt, "configure"),
)

print(render(d))
```

### Containers

Containers group components visually. All container types accept nested children as positional arguments:

```python
from plantuml_compose import component_diagram, render

d = component_diagram()
el = d.elements

# Available container types:
pkg    = el.package("Backend", el.component("API"))
db     = el.database("Storage", el.component("Engine"))
sky    = el.cloud("AWS", el.component("Lambda"))
hw     = el.node("Server", el.component("App"))
dir_   = el.folder("Config", el.component("Parser"))
frm    = el.frame("Subsystem", el.component("Core"))
rect   = el.rectangle("Group", el.component("Worker"))

d.add(pkg, db, sky, hw, dir_, frm, rect)

print(render(d))
```

All containers share this signature:

```text
el.package(  # or database, cloud, node, folder, frame, rectangle
    name,
    *children,
    ref=None,
    stereotype=None,
    style=None,
    description=None,     # text shown below the container name
)
```

### Bulk Element Creation

#### components() -- multiple components at once

```python
from plantuml_compose import component_diagram, render

d = component_diagram()
el = d.elements

api, db, cache = el.components("API", "Database", "Cache")

d.add(api, db, cache)

print(render(d))
```

#### interfaces() -- multiple interfaces at once

```python
from plantuml_compose import component_diagram, render

d = component_diagram()
el = d.elements

rest, graphql, grpc = el.interfaces("REST", "GraphQL", "gRPC")

d.add(rest, graphql, grpc)

print(render(d))
```

### Service Helper

`el.service()` creates a component with auto-connected provided/required interfaces in one call. It returns a `ServiceResult` with `elements` and `connections` you pass directly to `d.add()` and `d.connect()`:

```python
from plantuml_compose import component_diagram, render

d = component_diagram()
el = d.elements

svc = el.service("API Gateway",
    provides=("REST", "WebSocket"),
    requires=("Auth", "Logging"),
    stereotype="gateway",
    color="#C8E6C9",
)

# ServiceResult has .elements and .connections — spread them directly
d.add(*svc.elements)
d.connect(*svc.connections)

print(render(d))
```

## Connections

All connection factories live on `d.connections` (aliased as `c` by convention). Pass results to `d.connect()`.

### Connection Types

```python
from plantuml_compose import component_diagram, render

d = component_diagram()
el = d.elements
c = d.connections

api, db, cache, logger, monitor = el.components(
    "API", "Database", "Cache", "Logger", "Monitor"
)
iface = el.interface("REST")

d.add(api, db, cache, logger, monitor, iface)

d.connect(
    # Arrow (directed, solid line with arrowhead)
    c.arrow(api, db, "queries"),

    # Dependency (dotted arrow)
    c.dependency(api, cache, "reads"),

    # Link (undirected solid line, no arrowhead)
    c.link(logger, monitor, "shares data"),

    # Provides (lollipop notation)
    c.provides(api, iface),

    # Requires (socket notation)
    c.requires(cache, iface),
)

print(render(d))
```

### Common Parameters

Every connection method supports:

| Parameter | Description |
|---|---|
| `label` | Text on the connection (positional for arrow/dependency/link) |
| `source_label=` | Text at source end (arrow, dependency, link) |
| `target_label=` | Text at target end (arrow, dependency, link) |
| `style=` | `LineStyleLike` -- string (`"dashed"`), dict, or `LineStyle` |
| `direction=` | `"up"`, `"down"`, `"left"`, `"right"` -- layout hint |
| `length=` | Connection length (number of dashes) |

### Custom Arrow Heads

Override the default arrowheads on `arrow()` with `left_head=` and `right_head=`. Use `ArrowHead` enum values or friendly string names:

```python
from plantuml_compose import component_diagram, render, ArrowHead

d = component_diagram()
el = d.elements
c = d.connections

a, b, cx = el.components("Source", "Target", "Other")
d.add(a, b, cx)

d.connect(
    # Enum values
    c.arrow(a, b, "composition", left_head=ArrowHead.DIAMOND),
    # Friendly string names
    c.arrow(a, cx, "inheritance", right_head="closed_triangle"),
)

print(render(d))
```

### Bulk Connection Helpers

#### arrows() -- multiple arrows from tuples

```python
from plantuml_compose import component_diagram, render

d = component_diagram()
el = d.elements
c = d.connections

api, db, cache, logger = el.components("API", "Database", "Cache", "Logger")
d.add(api, db, cache, logger)

d.connect(c.arrows(
    (api, db),
    (api, cache, "reads"),
    (db, logger),
))

print(render(d))
```

#### arrows_from() -- fan-out from one source

```python
from plantuml_compose import component_diagram, render

d = component_diagram()
el = d.elements
c = d.connections

api, db, cache, queue = el.components("API", "Database", "Cache", "Queue")
d.add(api, db, cache, queue)

d.connect(c.arrows_from(api,
    db,
    (cache, "reads"),
    (queue, "publishes"),
    style="dashed",
    direction="down",
    length=3,
))

print(render(d))
```

#### lines() -- multiple undirected links from tuples

```python
from plantuml_compose import component_diagram, render

d = component_diagram()
el = d.elements
c = d.connections

logger, monitor, dashboard = el.components("Logger", "Monitor", "Dashboard")
d.add(logger, monitor, dashboard)

d.connect(c.lines(
    (logger, monitor),
    (monitor, dashboard),
))

print(render(d))
```

#### lines_from() -- fan-out undirected links from one source

```python
from plantuml_compose import component_diagram, render

d = component_diagram()
el = d.elements
c = d.connections

bus, worker1, worker2, worker3 = el.components("Bus", "Worker 1", "Worker 2", "Worker 3")
d.add(bus, worker1, worker2, worker3)

d.connect(c.lines_from(bus, worker1, worker2, worker3))

print(render(d))
```

#### chain() -- sequential connection pipeline

Creates arrows between consecutive components. Strings between `EntityRef` objects become labels:

```python
from plantuml_compose import component_diagram, render

d = component_diagram()
el = d.elements
c = d.connections

ui = el.component("UI")
api = el.component("API")
db = el.component("Database")

d.add(ui, api, db)

# Labeled chain: ui --HTTP--> api --SQL--> db
d.connect(c.chain(ui, "HTTP", api, "SQL", db))

print(render(d))
```

`chain()` accepts `style=`, `direction=`, and `length=` applied to all arrows.

All bulk helpers return lists that `d.connect()` flattens automatically.

## Notes

```python
from plantuml_compose import component_diagram, render

d = component_diagram()
el = d.elements

api = el.component("API")
d.add(api)

# Floating note
d.note("Architecture overview")

# Targeted note with position
d.note("Entry point", target=api, position="left")

# Colored note
d.note("Deprecated", target=api, position="top", color="#FFCDD2")

print(render(d))
```

**Positions**: `"right"` (default), `"left"`, `"top"`, `"bottom"`

## Layout and Organization

### Diagram-level options

```python
from plantuml_compose import component_diagram, render

d = component_diagram(
    layout="left_to_right",    # "top_to_bottom" (default) or "left_to_right"
    hide_unlinked=True,        # hide components with no connections
    hide_stereotype=True,      # suppress <<stereotype>> text display
)
el = d.elements
c = d.connections

api = el.component("API")
db = el.component("Database")
orphan = el.component("Unused")  # hidden by hide_unlinked
d.add(api, db, orphan)
d.connect(c.arrow(api, db, "queries"))

print(render(d))
```

## Styling

### Inline Element Style

Components and containers accept `style=` as a `StyleLike` dict:

```python
from plantuml_compose import component_diagram, render

d = component_diagram()
el = d.elements

api = el.component("API", style={
    "background": "#E3F2FD",
    "line": {"color": "#1976D2"},
    "text_color": "navy",
})

d.add(api)

print(render(d))
```

### Diagram-Wide Styling with diagram_style=

The `diagram_style=` parameter on `component_diagram()` applies styles globally. Pass a dict with any of these top-level keys:

| Key | Type | Description |
|---|---|---|
| `background` | color | Diagram background |
| `font_name` | str | Default font family |
| `font_size` | int | Default font size |
| `font_color` | color | Default text color |
| `component` | ElementStyleDict | Style for all components |
| `interface` | ElementStyleDict | Style for all interfaces |
| `package` | ElementStyleDict | Style for all packages |
| `node` | ElementStyleDict | Style for all nodes |
| `folder` | ElementStyleDict | Style for all folders |
| `frame` | ElementStyleDict | Style for all frames |
| `cloud` | ElementStyleDict | Style for all clouds |
| `database` | ElementStyleDict | Style for all databases |
| `arrow` | DiagramArrowStyleDict | Style for all connection arrows |
| `note` | ElementStyleDict | Style for all notes |
| `title` | ElementStyleDict | Style for the title |
| `stereotypes` | dict | Style by stereotype name |

**ElementStyleDict keys**: `background`, `line_color`, `font_color`, `font_name`, `font_size`, `font_style`, `round_corner`, `line_thickness`, `line_style`, `padding`, `margin`, `horizontal_alignment`, `max_width`, `shadowing`, `diagonal_corner`, `word_wrap`, `hyperlink_color`

**DiagramArrowStyleDict keys**: `line_color`, `line_thickness`, `line_pattern`, `font_color`, `font_name`, `font_size`

```python
from plantuml_compose import component_diagram, render

d = component_diagram(
    title="Styled Architecture",
    diagram_style={
        "background": "white",
        "component": {"background": "#E3F2FD", "line_color": "#1976D2"},
        "package": {"background": "#F5F5F5"},
        "database": {"background": "#FFF3E0"},
        "arrow": {"line_color": "#757575", "font_size": 11},
        "note": {"background": "#FFFDE7"},
        "stereotypes": {
            "service": {"background": "#C8E6C9", "font_style": "bold"},
        },
    },
)
el = d.elements
c = d.connections

pkg = el.package("Backend",
    el.component("API", stereotype="service"),
    el.component("Worker", stereotype="service"),
)
db = el.database("PostgreSQL")
d.add(pkg, db)
d.connect(c.arrow(pkg["API"], db, "queries"))

print(render(d))
```

## Advanced Features

### Diagram Metadata

```python
from plantuml_compose import component_diagram, render
from plantuml_compose.primitives.common import Header, Footer, Legend

d = component_diagram(
    title="Microservices",
    mainframe="Production Environment",
    caption="As of 2025-01-15",
    header=Header("Confidential", position="right"),
    footer="Architecture v2.1",
    legend=Legend("Blue = service\nGray = infrastructure", position="bottom"),
)
el = d.elements
c = d.connections

api = el.component("API")
db = el.database("DB")
d.add(api, db)
d.connect(c.arrow(api, db))

print(render(d))
```

### Deep Nesting

Containers can nest arbitrarily deep. Access children through chained attribute/bracket access:

```python
from plantuml_compose import component_diagram, render

d = component_diagram()
el = d.elements
c = d.connections

system = el.package("System",
    el.node("Server",
        el.component("API", ref="api"),
        el.component("Worker", ref="worker"),
    ),
    el.database("PostgreSQL", ref="pg"),
)

d.add(system)
d.connect(
    c.arrow(system.Server.api, system.pg, "queries"),
    c.arrow(system.Server.worker, system.pg, "writes"),
)

print(render(d))
```

### Refs and Child Access

Every element gets a **ref** — a short identifier for referencing in connections. By default, it's the sanitized name (spaces become underscores, special chars removed). Set `ref=` to override:

```python
from plantuml_compose import component_diagram, render

d = component_diagram()
el = d.elements
c = d.connections

# Default ref: "Auth_Service" (sanitized from name)
auth = el.component("Auth Service")

# Explicit ref
api = el.component("API Gateway", ref="api")

# Access children by ref (attribute) or name (bracket)
pkg = el.package("Backend",
    el.component("Users"),
    el.component("Orders"),
)

d.add(auth, api, pkg)

d.connect(
    c.arrow(api, pkg.Users, "REST"),       # child by ref
    c.arrow(api, pkg["Orders"], "gRPC"),   # child by name
    c.arrow(pkg.Users, auth, "validate"),
)

print(render(d))
```

You can also use raw strings instead of `EntityRef` objects:

```python
from plantuml_compose import component_diagram, render

d = component_diagram()
el = d.elements
c = d.connections

api = el.component("API")
db = el.database("PostgreSQL")
d.add(api, db)

# String refs work if you know the sanitized name
d.connect(c.arrow("API", "PostgreSQL", "queries"))

print(render(d))
```

## Quick Reference

### Element Factories

| Factory | Description |
|---|---|
| `el.component(name, *children)` | Software component |
| `el.interface(name)` | Interface (lollipop/socket) |
| `el.port(name)` | Bidirectional port |
| `el.portin(name)` | Input port |
| `el.portout(name)` | Output port |
| `el.package(name, *children)` | Tab folder container |
| `el.database(name, *children)` | Cylinder container |
| `el.cloud(name, *children)` | Cloud container |
| `el.node(name, *children)` | 3D box container |
| `el.folder(name, *children)` | Folder container |
| `el.frame(name, *children)` | Frame container |
| `el.rectangle(name, *children)` | Rectangle container |

### Connection Factories

| Factory | Arrow | Meaning |
|---|---|---|
| `c.arrow(src, tgt, label)` | `-->` | Directed connection |
| `c.dependency(src, tgt, label)` | `..>` | Dotted dependency |
| `c.link(src, tgt, label)` | `--` | Undirected link |
| `c.provides(src, tgt)` | `--(` | Lollipop (provides interface) |
| `c.requires(src, tgt)` | `--)` | Socket (requires interface) |

### Bulk Helpers

| Helper | Purpose |
|---|---|
| `el.components(*names)` | Create multiple components |
| `el.interfaces(*names)` | Create multiple interfaces |
| `el.service(name, provides=, requires=)` | Component with auto-wired interfaces |
| `c.arrows(*tuples)` | Multiple arrows |
| `c.arrows_from(src, *targets)` | Fan-out from one source |
| `c.lines(*tuples)` | Multiple undirected links |
| `c.lines_from(src, *targets)` | Fan-out undirected links |
| `c.chain(*items)` | Sequential pipeline |

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
| `style=` | None | Overall style: `"uml1"`, `"uml2"`, `"rectangle"` |
| `diagram_style=` | None | Global styling dict |
| `hide_stereotype=` | False | Suppress stereotype text |
| `hide_unlinked=` | False | Hide components with no connections |
