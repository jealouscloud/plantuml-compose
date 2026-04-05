# Deployment Diagrams

Deployment diagrams show where software runs on hardware and infrastructure. Use them for datacenter topologies, cloud architectures, production layouts, and network maps. They support the widest range of element types of any diagram, with arbitrary nesting depth.

## Quick Start

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram(title="DC Topology")
el = d.elements
c = d.connections

rack = el.frame("Rack",
    el.node("Host", el.artifact("app")),
    el.database("PostgreSQL", ref="pg"),
)

d.add(rack)
d.connect(c.arrow(rack.Host, rack.pg, "JDBC"))

print(render(d))
```

## Elements

All element factories live on `d.elements` (aliased as `el` by convention). Every factory returns an `EntityRef` that you pass to `d.add()`. Every element type supports nesting via positional `*children` arguments.

### Infrastructure Elements

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram()
el = d.elements

server   = el.node("Web Server")          # 3D box (primary infrastructure shape)
app      = el.artifact("webapp.war")       # Deployable artifact
comp     = el.component("API")             # Software component
db       = el.database("PostgreSQL")       # Cylinder
store    = el.storage("NFS")               # Storage unit
sky      = el.cloud("AWS")                 # Cloud shape
frm      = el.frame("DMZ")                # Frame with title bar
dir_     = el.folder("Config")             # Folder icon
pkg      = el.package("com.example")       # Tab folder
rect     = el.rectangle("Cluster")         # Plain rectangle
q        = el.queue("Messages")            # Queue shape
stk      = el.stack("Layers")              # Stack shape
f        = el.file("config.yaml")          # File icon

d.add(server, app, comp, db, store, sky, frm, dir_, pkg, rect, q, stk, f)

print(render(d))
```

### Actor and Agent Elements

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram()
el = d.elements

user     = el.actor("End User")            # Stick figure
bot      = el.agent("Monitoring Agent")     # Agent shape
wall     = el.boundary("Firewall")          # Boundary notation
card_    = el.card("Task Card")             # Card shape
dot      = el.circle("Endpoint")            # Circle
group    = el.collections("Workers")        # Stacked copies
ctl      = el.control("Scheduler")          # Control circle
ent      = el.entity("Order")               # Entity with underline
hex_     = el.hexagon("Router")             # Hexagon shape
lbl      = el.label_("v2.1")               # Plain text label
person_  = el.person("DevOps Engineer")     # Person shape
proc     = el.process("Worker Process")     # Process shape
iface    = el.interface("REST API")         # Interface circle
uc       = el.usecase("Deploy App")         # Usecase ellipse
act      = el.action("Build Step")          # Action shape

d.add(user, bot, wall, card_, dot, group, ctl, ent, hex_, lbl, person_, proc, iface, uc, act)

print(render(d))
```

### Ports

Ports appear as small squares on element boundaries. Add them as children of any element:

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram()
el = d.elements

server = el.node("Server",
    el.portin("http_in"),      # input port (inward arrow)
    el.portout("log_out"),     # output port (outward arrow)
    el.port("mgmt"),           # bidirectional port
)

d.add(server)

print(render(d))
```

### Common Element Signature

All element factories share the same signature:

```text
el.node(  # or any element type
    name,
    *children,             # nested EntityRef elements
    ref=None,              # short alias for connections (default: sanitized name)
    stereotype=None,       # str or Stereotype object
    style=None,            # StyleLike dict for inline visual override
    description=None,      # text shown below the element name
)
```

### Element Descriptions

Any element can show descriptive text below its name:

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram()
el = d.elements

server = el.node("app-server-01",
    description="8 cores, 32GB RAM\nUbuntu 22.04",
)

d.add(server)

print(render(d))
```

### Stereotypes

Pass a string for simple stereotypes, or a `Stereotype` with a `Spot` for a colored indicator:

```python
from plantuml_compose import deployment_diagram, render, Stereotype, Spot

d = deployment_diagram()
el = d.elements

# Simple string stereotype
lb = el.node("Load Balancer", stereotype="nginx")

# Stereotype with colored spot
primary = el.database("Primary", stereotype=Stereotype("master", Spot("M", "DodgerBlue")))

d.add(lb, primary)

print(render(d))
```

### Deep Nesting

Elements can nest arbitrarily deep. Access children through chained attribute or bracket access:

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram()
el = d.elements
c = d.connections

dc = el.frame("Data Center",
    el.node("Rack 1",
        el.node("Host A",
            el.artifact("api.jar", ref="api"),
            el.artifact("worker.jar", ref="worker"),
        ),
    ),
    el.cloud("CDN",
        el.artifact("static assets", ref="cdn"),
    ),
    el.database("PostgreSQL", ref="pg"),
)

d.add(dc)
d.connect(
    c.arrow(dc["Rack 1"]["Host A"].api, dc.pg, "JDBC"),
    c.arrow(dc.CDN.cdn, dc["Rack 1"]["Host A"].api, "origin pull"),
)

print(render(d))
```

## Connections

All connection factories live on `d.connections` (aliased as `c` by convention). Pass results to `d.connect()`.

### Connection Types

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram()
el = d.elements
c = d.connections

server = el.node("Server")
db = el.database("DB")
monitor = el.agent("Monitor")

d.add(server, db, monitor)

d.connect(
    # Arrow (directed, solid line with arrowhead)
    c.arrow(server, db, "JDBC"),

    # Line (undirected, no arrowhead)
    c.line(server, monitor, "heartbeat"),

    # Dependency (dotted arrow)
    c.dependency(server, db, "requires"),
)

print(render(d))
```

### Common Parameters

Every connection method supports:

| Parameter | Description |
|---|---|
| `label` | Text on the connection (positional argument) |
| `style=` | `LineStyleLike` -- string (`"dashed"`), dict, or `LineStyle` |
| `direction=` | `"up"`, `"down"`, `"left"`, `"right"` -- layout hint |
| `length=` | Connection length (number of dashes) |

### Custom Arrow Heads

Override the default arrowheads on `arrow()` and `line()` with `left_head=` and `right_head=`:

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram()
el = d.elements
c = d.connections

a = el.node("Server A")
b = el.node("Server B")
d.add(a, b)

d.connect(
    c.arrow(a, b, "custom", left_head="<|", right_head="*"),
)

print(render(d))
```

### Line Style

The `style=` parameter accepts a string shorthand, a dict, or a `LineStyle` object:

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram()
el = d.elements
c = d.connections

server = el.node("Server")
db = el.database("DB")
d.add(server, db)

d.connect(
    c.arrow(server, db, "dashed style", style="dashed"),
)

print(render(d))
```

### Bulk Connection Helpers

#### arrows() -- multiple arrows from tuples

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram()
el = d.elements
c = d.connections

server = el.node("Server")
db = el.database("DB")
cache = el.node("Cache")
backup = el.database("Backup")
d.add(server, db, cache, backup)

d.connect(c.arrows(
    (server, db),
    (server, cache, "reads"),
    (db, backup),
))

print(render(d))
```

#### arrows_from() -- fan-out from one source

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram()
el = d.elements
c = d.connections

switch = el.node("Switch")
server1 = el.node("Server 1")
server2 = el.node("Server 2")
storage = el.storage("SAN")
d.add(switch, server1, server2, storage)

d.connect(c.arrows_from(switch,
    server1,
    server2,
    (storage, "iSCSI"),
    style="dashed",
    direction="down",
    length=3,
))

print(render(d))
```

#### lines() -- multiple undirected links from tuples

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram()
el = d.elements
c = d.connections

switch_a = el.node("Switch A")
switch_b = el.node("Switch B")
switch_c = el.node("Switch C")
d.add(switch_a, switch_b, switch_c)

d.connect(c.lines(
    (switch_a, switch_b),
    (switch_b, switch_c),
))

print(render(d))
```

#### lines_from() -- fan-out undirected links from one source

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram()
el = d.elements
c = d.connections

tor_switch = el.node("ToR Switch")
host1 = el.node("Host 1")
host2 = el.node("Host 2")
host3 = el.node("Host 3")
d.add(tor_switch, host1, host2, host3)

d.connect(c.lines_from(tor_switch, host1, host2, host3))

print(render(d))
```

All bulk helpers return lists that `d.connect()` flattens automatically.

## Notes

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram()
el = d.elements

server = el.node("Server")
d.add(server)

# Floating note
d.note("Production environment")

# Targeted note with position
d.note("Primary node", target=server, position="left")

# Colored note
d.note("Needs upgrade", target=server, position="top", color="#FFCDD2")

print(render(d))
```

**Positions**: `"right"` (default), `"left"`, `"top"`, `"bottom"`

## Layout and Organization

### Layout Direction

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram(
    layout="left_to_right",    # "top_to_bottom" (default) or "left_to_right"
)

print(render(d))
```

## Styling

### Inline Element Style

Any element accepts `style=` as a `StyleLike` dict:

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram()
el = d.elements

server = el.node("Server", style={
    "background": "#E3F2FD",
    "line": {"color": "#1976D2"},
    "text_color": "navy",
})

d.add(server)

print(render(d))
```

### Diagram-Wide Styling with diagram_style=

The `diagram_style=` parameter on `deployment_diagram()` applies styles globally. Pass a dict with any of these top-level keys:

| Key | Type | Description |
|---|---|---|
| `background` | color | Diagram background |
| `font_name` | str | Default font family |
| `font_size` | int | Default font size |
| `font_color` | color | Default text color |
| `node` | ElementStyleDict | Style for all nodes |
| `artifact` | ElementStyleDict | Style for all artifacts |
| `database` | ElementStyleDict | Style for all databases |
| `cloud` | ElementStyleDict | Style for all clouds |
| `component` | ElementStyleDict | Style for all components |
| `frame` | ElementStyleDict | Style for all frames |
| `storage` | ElementStyleDict | Style for all storage elements |
| `folder` | ElementStyleDict | Style for all folders |
| `package` | ElementStyleDict | Style for all packages |
| `rectangle` | ElementStyleDict | Style for all rectangles |
| `queue` | ElementStyleDict | Style for all queues |
| `stack` | ElementStyleDict | Style for all stacks |
| `arrow` | DiagramArrowStyleDict | Style for all connection arrows |
| `note` | ElementStyleDict | Style for all notes |
| `title` | ElementStyleDict | Style for the title |
| `stereotypes` | dict | Style by stereotype name |

**ElementStyleDict keys**: `background`, `line_color`, `font_color`, `font_name`, `font_size`, `font_style`, `round_corner`, `line_thickness`, `line_style`, `padding`, `margin`, `horizontal_alignment`, `max_width`, `shadowing`, `diagonal_corner`, `word_wrap`, `hyperlink_color`

**DiagramArrowStyleDict keys**: `line_color`, `line_thickness`, `line_pattern`, `font_color`, `font_name`, `font_size`

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram(
    title="Styled Topology",
    diagram_style={
        "background": "white",
        "node": {"background": "#E3F2FD", "line_color": "#1976D2"},
        "artifact": {"background": "#FFF9C4"},
        "database": {"background": "#FFF3E0", "line_color": "#E65100"},
        "cloud": {"background": "#E8F5E9"},
        "frame": {"background": "#F5F5F5"},
        "storage": {"background": "#FCE4EC"},
        "queue": {"background": "#E8EAF6"},
        "arrow": {"line_color": "#757575", "font_size": 11},
        "note": {"background": "#FFFDE7"},
        "stereotypes": {
            "master": {"background": "#C8E6C9", "font_style": "bold"},
            "replica": {"background": "#FFECB3"},
        },
    },
)

print(render(d))
```

## Advanced Features

### Diagram Metadata

```python
from plantuml_compose import deployment_diagram, render
from plantuml_compose.primitives.common import Header, Footer, Legend, Scale

d = deployment_diagram(
    title="Production DC",
    mainframe="US-East-1",
    caption="Generated 2025-01-15",
    header=Header("Confidential", position="right"),
    footer="Page %page%",
    legend=Legend("Blue = compute\nOrange = storage", position="bottom"),
    scale=Scale(factor=1.5),
    theme="plain",
)

print(render(d))
```

### String References

You can use raw strings instead of `EntityRef` objects for connections:

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram()
el = d.elements
c = d.connections

server = el.node("Server")
db = el.database("Database")
d.add(server, db)

d.connect(c.arrow("Server", "Database", "JDBC"))

print(render(d))
```

### Full Topology Example

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram(title="K8s Cluster", layout="left_to_right")
el = d.elements
c = d.connections

cluster = el.frame("Kubernetes",
    el.node("Control Plane",
        el.component("API Server", ref="api"),
        el.component("etcd", ref="etcd"),
        el.component("Scheduler", ref="sched"),
    ),
    el.node("Worker 1",
        el.artifact("Pod: web", ref="web1"),
        el.artifact("Pod: api", ref="api1"),
    ),
    el.node("Worker 2",
        el.artifact("Pod: web", ref="web2"),
        el.artifact("Pod: worker", ref="wrk"),
    ),
)

lb = el.cloud("Load Balancer", ref="lb")
db = el.database("PostgreSQL", ref="pg")
user = el.actor("User")

d.add(cluster, lb, db, user)

d.connect(
    c.arrow(user, lb, "HTTPS"),
    c.arrows_from(lb, cluster["Worker 1"].web1, cluster["Worker 2"].web2),
    c.arrow(cluster["Worker 1"].api1, db, "SQL"),
    c.arrow(cluster["Worker 2"].wrk, db, "SQL"),
    c.arrow(cluster["Control Plane"].api, cluster["Control Plane"].etcd, "state"),
)

print(render(d))
```

## Quick Reference

### Element Factories

All elements share the signature `el.<type>(name, *children, ref=, stereotype=, style=, description=)`.

| Factory | Shape |
|---|---|
| `el.node(name)` | 3D box |
| `el.artifact(name)` | Artifact icon |
| `el.component(name)` | Component |
| `el.database(name)` | Cylinder |
| `el.storage(name)` | Storage unit |
| `el.cloud(name)` | Cloud |
| `el.frame(name)` | Frame with title |
| `el.folder(name)` | Folder icon |
| `el.package(name)` | Tab folder |
| `el.rectangle(name)` | Plain rectangle |
| `el.queue(name)` | Queue |
| `el.stack(name)` | Stack |
| `el.file(name)` | File icon |
| `el.actor(name)` | Stick figure |
| `el.interface(name)` | Interface circle |
| `el.agent(name)` | Agent |
| `el.boundary(name)` | Boundary |
| `el.card(name)` | Card |
| `el.circle(name)` | Circle |
| `el.collections(name)` | Stacked copies |
| `el.control(name)` | Control |
| `el.entity(name)` | Entity |
| `el.hexagon(name)` | Hexagon |
| `el.label_(name)` | Plain text |
| `el.person(name)` | Person |
| `el.process(name)` | Process |
| `el.usecase(name)` | Ellipse |
| `el.action(name)` | Action |
| `el.port(name)` | Bidirectional port |
| `el.portin(name)` | Input port |
| `el.portout(name)` | Output port |

### Connection Factories

| Factory | Arrow | Meaning |
|---|---|---|
| `c.arrow(src, tgt, label)` | `-->` | Directed connection |
| `c.line(src, tgt, label)` | `--` | Undirected connection |
| `c.dependency(src, tgt, label)` | `..>` | Dotted dependency |

### Bulk Helpers

| Helper | Purpose |
|---|---|
| `c.arrows(*tuples)` | Multiple arrows |
| `c.arrows_from(src, *targets)` | Fan-out from one source |
| `c.lines(*tuples)` | Multiple undirected links |
| `c.lines_from(src, *targets)` | Fan-out undirected links |

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
