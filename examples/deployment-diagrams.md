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
![Diagram](https://www.plantuml.com/plantuml/svg/7Oqn3i9030Hxls8_a0zGe8YaG8W221ymEUSKSObFTwP0A7_7Ih75h7QqRJKkzbaIsMn9q7TuQjQayKjJuKNmuF6D7m6h1i5Pg-q4k3TFF1euPoysJs3Z5rV1pMUno72_WYjof8rsiscEJZZWqfywQcKDVlq7)



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
![Diagram](https://www.plantuml.com/plantuml/svg/7OzBRW8n44JtVOgM3p1d084YHG84cWLITZrsUJIAVxJj46uVasrzNgbsjOcs7WEbxC3cZeLdw0_Kq30sBxQnUMAHKgQd3DNcM792Qho_VfAJ9ejKy3NNjYhcsubgooeh-F8namsvEzxVP_8g4NmyVv7FmK7va9FVLYfYlzzfCy0JVYMM04CAsoIj0Nm8lJOeFJew-8nQHxgEaT7ZaxoWbVmM_W5luFII60pjaDouzGS0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/9L11JWCn3Bpd5POVW0Glw095ue1QTOiukudPHZLnv2I5_XwlUlFCo3EZsRHEriUF18fT3N1R4dmsDWoqSEc07rgoAxaiCAqCXfEEaiXky9QDVqaaHB84UAHsWHS_CSHiKHZSh6ekFKGLuTYpbWPVQXUsvbpffW9pF7CQmXRSFVSRx2mvEFCVBLhWeACx53gn05wV7XunLFzt2L_vkglDOvPSUErSJIEt1dWFWVqTO_0IRDyK6V2mdOymxTynZCQH6gy-LVG6Kwsuxf1Nx-UH9S7SsRaDb-GR_GC0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuShBJqbL24ujAaijKgZcKb0eo2ygoSnJo2WfAOZFp8CAv9UMAEJafyS3QQY8GcvwRWbNBPT3QbuAq1W0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuShBJqbLK4eiAD0jJYqgIotIDJ2CoRDGICulIYtMKJ0sSdTI27BqZSaBJIhDAobLC3BICp1Hud98pKi1wWO0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/3Sn12e0m30NHlQS8kb7m2295N2fuXQy9HMXJI2lexUrw7kDoWPKdXaOJ2xLR0jE20Bt4MfeczRU-yzmm2avaeSFk2FjgeduVkpMn5rl28mD5v296LJjHhjCV)



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
![Diagram](https://www.plantuml.com/plantuml/svg/PP3D2i8m48JlUOgXzmfUFKYrFOY8-FC4Qn9Bj4rAak91-kvk__JW8P3zTcOODWkHV6phIjmzrHf9GP6GQnkrJ_0MW7MAyONa4ykHp6pdGiHcPW07cJl9Y8GQitWG1r00___sB-UVsdybupYeEZ4-MRbM8I-EK_hFouMZaMmBEeR1BfMTN8hBtoXedBXQwVNrVEW5JIawmJsGfciUiCA-sEQ2VGFfDoiuRqfZqRHL9J9j5T_a0m00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/HOr13a1040Jlyuhv00zm45bE4YSl6DaE4dPZTdY_JH3Nhkhk9fcedVj68Nhm2BsWvCLaaWJk7CcCO3p4i5fKUWGkYZephhZlNFk7dvR1WhmxGUoZPVbM5CUvAX8r23u_tm00)



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
    c.arrow(a, b, "custom", left_head="closed_triangle", right_head="diamond"),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuShBJqbLK0fEBIfBBL9mL4BbEobnGLZnZWerThgwMWfGhfE2bK9oQN59VYwNGsfU2j0W0000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuShBJqbL24ujAaijuaf9B4bCIYnELN1nue88AUX6foGMPwIcnEhQ0KKLh1GWN8NYaigSL2w7rBmKe240)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuShBJqbL24ujAaijuaf9B4bCIYnELN1nWeWx9oPdf2A4dHAJiqiBk22g5NHrxK0AaNXWvGfM2aMfYId5N2vEO46e9eVKl1IWVG00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuShBJqbL22xFB4dEWB2LWbEBobAB50oLKFb6Ibp59Vb5YUb0vOv-N10j2hhHAOd56QafiIcwkdOA4ANnXdXbZN38ElefM2ba1Zi7Ut8vfEQb01q70000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuShBJqbLK0ekpon9pb1mL4BbEw7ndPMu8AnuHmLTNGKesmacw8GawCpba9gN0hG10000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuShBJqbLK0h93r88BiyiISvGWefuv1UNA1YYy8nGUCPAN41TyH1T2hgw2Y3HU4DiWaRO18sv75BpKe1E0000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/HSun2eD050JGFgSOo0qihOI8fGHoWYKxcWNtV_d-5N9xLmoac-BDCDtcmRpavIOQYHTjfzNiXANvuosUfh6yFQc0iYTJoHI_oCB9eTElTjgKWtrnRbt2TVq3t8VXqVTDYv6C6yewMwYoeyHwuG00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuSf9JIjHACbNACfCpoXHICaiIaqkoSpFut98pKi1oWC0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuShBJqbL24ujAaijKb1sDNOpSdFXSaZDIm7A0G00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/VPBBJiCm44Nt-GfBx25fcgIHAbJgs2jsy0Dkx0OBnrESYQg0-kyuaNa8v6hapVZCdOVkRa3XSEnDiXrmCke-aUfaOEgLnKQBpecUV2I4x4NxsZaOhQHWm97pYqRbynQaMe3_o0tB-Oetoz-ZjYfaixegcvNFNlpplVLHj1YJu9pNT1rWAL0SnA2km3bB__PZPP6bQP1e3OmoEk-65wmEvD5l7kzKp1780S69BivIjcOqi6-Z6kFtsh07NWRI0bvRj67LzmaTd0FvQ-sgc6F9Sh3ufDyLoR9GSzkB0PMBwTCDAsdzKpiRWnp0oAzovpsYMn6VZz5zli2NP7iNZ8KQlSmY9iapd3pRJSbEMUdjzma0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/9O_12i9034Jl-Ofuy5Xf2pqAOXMF2k87nDsqNTZTb6ts_urwcGalcO6SDgMYDKL85F9KA36-disLDcqwsEd21jPeEzWSHSRkC806jUbHn5UdGJ9UHYXXNXGN9iy5HybJy9mrK0HdRcmI-Tg3PiRzQhe7H-ilVkFCXPGzzcq_D6tNT0D4dZbxV8kg940ynyfuH2TfhSe6xeNo_4MRIh4-iFD_24uczjC7)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuShBJqbL24ujAaijuaf9B4bCIYnELN21ChWW4WgwkdPmCGKh1IyN9sSkXzIy5A010000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/XLAnJWCn3Dtp5TRj7NeJwe0ANK1qE7H5pBd4TpqrZK-E3mRKVyS954HLYIM9ttj-jfEiarYM-HYCZ18GdcuIRCAS1Da4x0M4WCTXB-17HYSZHTEpFQfoxf0Z2YRuC02HF4AreIXC0PfW8rQ5071qd2XY5AZkcaTeaT-GAx09x3HUA52Slu1QjqS_1-ISaNAWWjDFoLVYWtBBSpKTP-ojqs8D-HMyOrTAwRwynciBvrQMrtph_tthgtn9_vBmeJYVZ0iqUwYsP3tSMxqZzoq9dV5MR6SJGaD91iRsUPkPQJ1gIWmlIPyaBx1Ot6e2hE1XjsjQeyUCb05_pxN94vLe6bIhTaOR-Gkef03vrXNIlo1erXYzVeXF)



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
