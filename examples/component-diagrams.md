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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGXFJL88BabCpkPApiyjoCzBpIjHK78Cy5HmJon9BK-iL598B5O0ykEXVAwKn9B4fCJYL8M0_EAIzABKu40VXMgkMYuaDGgwkdR8qbOAXQMfHPcfnLmEgNafGBi1)



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
![Diagram](https://www.plantuml.com/plantuml/svg/LO_12i8m44Jl-Ogb_e4WA9JI8XK5GS6hK4AwfOLq4pORHSH_rvOUud4UipEpPH3D4aUhZ1kz8oI1wdfAL5P5wU66_1WCtkcegRKOu3BXDNJMFKC6Ei2acyMMdE-rwH7oVA2ETH2EHY9ZKS2gtXuszIxjzTuEHilWQ0hKtiDR0IHPZeITjSX_E5jQuQnVoFEOXJGpKHzL8hM_9xy0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuShCAqajIajCJbK8SWqEGUAw5oKMP0JwADZO91PasjbnEQJcfG0r0000)



### Ports

Ports appear as small squares on component boundaries. Add them as children of a component:

```python
from plantuml_compose import component_diagram, render

d = component_diagram()
el = d.elements

server = el.component("Server",
    el.portin("http_in"),      # input port (inward arrow)
    el.portout("log_out"),     # output port (outward arrow)
    el.port("mgmt"),           # bidirectional port
)

d.add(server)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEpot8pqlDAr48JYqgIorIgEPIK2Z8Boh9p5F8A2afYC_CWmhabvOevEIdnmDfg8X2Rdfk2LSjbqDgNWhGB000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NT0x2iCm30RWtQVGKPA6KWeT0XaoAxPYGcpBo4wXbDwzIhTwqg2FNu-kL9Hwn60osXqzmKKh9GTl0s0vPawKAlJZtNoCmueB5eAfifpu7rsJtnAfiu4F1_qyDU21SN6e8B7J498dIJieP-sl79os1axhvXineXII4mb6JJcMyYgLOiC6bdCL8Lin-K1m4pvoWsQM_PVLwSdwXIy0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEpot8pqlDAr5m3F14uhaabYGc9HQd8Wav9oPdf78vfEQb03K20000)



#### interfaces() -- multiple interfaces at once

```python
from plantuml_compose import component_diagram, render

d = component_diagram()
el = d.elements

rest, graphql, grpc = el.interfaces("REST", "GraphQL", "gRPC")

d.add(rest, graphql, grpc)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuShCAqajIajCJbK8SWqEGUAw5oKMP0Jw88ca1mKuSpcavgK0zG40)



### Service Helper

`el.service()` creates a component with auto-connected provided/required interfaces in one call:

```python
from plantuml_compose import component_diagram, render

d = component_diagram()
el = d.elements

gateway = el.service("API Gateway",
    provides=("REST", "WebSocket"),
    requires=("Auth", "Logging"),
    stereotype="gateway",
    color="#C8E6C9",
)

# Add the component, its generated interfaces, and their relationships
d.add(
    gateway,
    *gateway._data["_provided_interfaces"],
    *gateway._data["_required_interfaces"],
)
d.connect(*gateway._data["_service_relationships"])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEpot8pqlDAr5GSWpmL71FB4ajJwnKKaWiLW3ouw5y1HkRT0ZBpav1sTd2rSpPaYiphoIrA2qnELKXo3Ku18aRdfeKd9-SdLg29EPOMfA1nFN9Jq_Fp4ldGhP3LrS3OXAw8C8yP1bDNLs8gUY2CBCTKlDIW5u40000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/JSyn3i8m30NGFQVm24Dx08Qg21YGg8I02vZ6j95e0hPxVwm6KCR_RJ_9hIYopjFJzMbwfKXHONi-5ccFYdSKAgeTzcEPJsaOY8kYIp5eOXUY4Z-m9xWShZTdC5HLyoTX0--PE90iexfkCcqz4tfn6RQRdsWJ6P59m9ln1LTPpwThMrvYIz7RNny0)



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

Override the default arrowheads on `arrow()` with `left_head=` and `right_head=`:

```python
from plantuml_compose import component_diagram, render

d = component_diagram()
el = d.elements
c = d.connections

a, b = el.components("A", "B")
d.add(a, b)

d.connect(
    c.arrow(a, b, "custom", left_head="<|", right_head="*"),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEpot8pqlDAr5mH68xSJagsDJewcefE2bOAIIN5fVavt8vfEQb0BK00000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEpot8pqlDAr5m3F14uhaabYGc9HQd8Wav9oPd8FDzyjFJKukuWFeKT7Nj43fW0c3r2bOAHQc9ASLSC6cm55IhGsfU2j0H0000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEpot8pqlDAr5m3F14uhaabYGc9HQd8Wav9oPd8FC3IrDBKxc0sXHqerCIYpDIKs9JT7Nj45enfS16A5Wf5AKcfXHZaGSR2PGlA4tAoGGA5tCvfEQb0Dq90000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEpot8pqlDAr7moKzFJor24l3DpyiioKSMSKaipaZAJonAuO8eLj3LXQk2qY0XX3A7rBmKe2q0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEpot8pqlDAr5mAYr6uYc5vnTbfnOf62ef91OhG3ZnXbWK624hCCAYm1XPWJ4Nq1e5NLs4YQXy8pI-CPT3QbuAqA40)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEpot8pqlDAr48zKJYE0OWyrmIInAJ4ejJkK8z5NHrxK2o2bOA7Y4X0LmW9aW8fWGe7Xpem-MGcfS2D1u0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/BOr13e9040Jl-uf9_877FK5OIRpv1R8qiWdCRCO6u--LuBcgKisBWtDRbv1jhQPGIlku1pL2l3ndHcazpuN8t1nYEtmlU9_6WebYqv54kIdz8zMAygIq-eTowVikfMkKXEh80p661Zh-pby0)



**Positions**: `"right"` (default), `"left"`, `"top"`, `"bottom"`

## Layout and Organization

### Diagram-level options

```python
from plantuml_compose import component_diagram, render

d = component_diagram(
    layout="left_to_right",    # "top_to_bottom" (default) or "left_to_right"
    hide_unlinked=True,        # hide components with no connections
    hide_stereotype=True,      # suppress <<stereotype>> text display
    style="uml2",              # overall component style: "uml1", "uml2", "rectangle"
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/9Sl13O0m30J1Vwfm3LIG7gWW8WTO97Ra70-w1uddIhDviWJltbB3Jg5Bw75IgWOsgbkQbzeeKRfiteSRZ2kV1lcc9PrQ8PC8E9-1l_DjJUr2JHbMF_S2)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEpot8pqlDAr5m3F1KK7OrTZDoSx7EoSnBjJAqD3TpCR8kIQqeiSfBBAlaSaZDIm7g0G00)



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
            "infrastructure": {"background": "#FFECB3"},
        },
    },
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/VP5DQiCm48NtFeMW-xIEITn0A6biQTLTJZ2HL5TKbi9edD2MtBsIK7-Wk0opUVEz6Q6t2mH8qsWhCcGrEz2RrOezedmnf2LDgAjjIE939VruyauxwWqC22Fxg1ZRWtmTq4zETTvwP9VaY_etdAc_t0rln5BqUVPad2vglMdN_JAgrzZEavwp2o5wtXRm5ASmpBEhL8LLG724yD_YXjyL613zfP2_NjckKcLLU4S7ywvPNHVFmhXdX40uvU-RlyExVVFb2HhFHix2tJrVTvkVWoaGTlHMPV-rsjwMZ7RQgPZc9m00)



## Advanced Features

### Diagram Metadata

```python
from plantuml_compose import component_diagram, render
from plantuml_compose.primitives.common import Header, Footer, Legend, Scale

d = component_diagram(
    title="Microservices",
    mainframe="Production Environment",
    caption="As of 2025-01-15",
    header=Header("Confidential", position="right"),
    footer="Page %page%",
    legend=Legend("Blue = service\nGray = infrastructure", position="bottom"),
    scale=Scale(factor=1.5),
    theme="vibrant",
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/BKz1QiD03Bph5UeXnuGuu6CXJIaz1V85PItRWjsLqSg6_3vAsikCD68qqhavcQybGo6fer5Xl9aEQtBHYZzr4zDQk3fy-CmntUHk56rBb1cxGmyk7jLLacbZsoHn0vDfTfoP1ZRyrZhA43k4CgJWq4RL5zreOjmjWJj8jBn3lnhgYAVZgTyVkttNG-Q9wu1tTTS2Y9UyCdxYVrW8lqQF4DuFDBSuVZM6yFmvuHmGFpu1)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NOwz3i8m38JtF8LVe2_0WCg8n53KWTaqLXIL_E2uhH3Ak-E60Od1ak-xq-dw8iYoX8V9ECte2CPN4GhmDW0nMTN4At7J05CAEKMA0gVX35W0i_ypRebdpQktjK_jgcTHy8w5O4X57DDulUoPx5fpDTLe5NJTSKS7U2x4dehvTlpunbuKznIjZlu0)



### String References

You can use raw strings instead of `EntityRef` objects for connections:

```python
from plantuml_compose import component_diagram, render

d = component_diagram()
el = d.elements
c = d.connections

api = el.component("API")
db = el.database("PostgreSQL")
d.add(api, db)

d.connect(c.arrow("API", "PostgreSQL", "queries"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEpot8pqlDAr5m3F3aIaaiIKnAB4vL2CWlBaalIWqEz56evghb0iefwEhQ8GjRAHIMfXPbfXPpEQJcfG2D0W00)



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
