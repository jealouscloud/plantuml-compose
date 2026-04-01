# Component Diagrams

Component diagrams show how software pieces connect through interfaces. They're ideal for:

- **System architecture**: How modules connect at a high level
- **Service dependencies**: Which services depend on which
- **Interface contracts**: What each component provides or requires
- **Microservice boundaries**: Service decomposition

Unlike class diagrams (internal structure) or deployment diagrams (physical infrastructure), component diagrams focus on software modules and their connections.

## Core Concepts

**Component**: A modular unit of software (service, library, module).

**Interface**: A contract a component provides or requires.

**Package**: Grouping of related components.

**Relationships**:
- **Provides** (lollipop): Component exposes an interface
- **Requires** (socket): Component needs an interface
- **Link/Arrow**: General dependency or connection

## Your First Component Diagram

```python
from plantuml_compose import component_diagram, render

d = component_diagram(title="Simple System")
el = d.elements
c = d.connections

api = el.component("API Server")
db = el.component("Database")

d.add(api, db)
d.connect(c.arrow(api, db, "queries"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGZEp2q0KPN59QcvNCdvkGNvUQbv9GfAZW6U2i6fHMMfHKeAYSKAG6uyX8kao2Mn934fiJYL2o6heAjh1nTNi58eB4qjoamjvd98pKi1sWe0)



## Components

### Basic Components

```python
from plantuml_compose import component_diagram, render

d = component_diagram()
el = d.elements

# Simple component
api = el.component("API Gateway")

# With stereotype (text label only -- for cylinder shape, use el.database())
db = el.component("PostgreSQL", stereotype="database")

# With styling
cache = el.component("Redis", style={"background": "LightYellow"})

# With attached note
auth = el.component("Auth Service")

d.add(api, db, cache, auth)
d.note("Handles OAuth2", target=auth)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LO-n3e9044Jx-ueD_e6b8GGhDI4HfR8YAxV29SUjkLqa_hqGAQ2SDpEPJ2wAKOVUcuRxDmSA2icnlC09bKRy9e02awuNlOgLBDf6gcu5fAb5nISAPTagSIVh17Q5QpjzaFSyRbO6xQ2Y-74D_MScK2_015Q2E3U1Nnlh06SCrfF0TSPxarEmquCV)



### Bulk Component Creation

```python
from plantuml_compose import component_diagram, render

d = component_diagram()
el = d.elements
c = d.connections

# Create multiple at once
api, worker, scheduler = el.components("API", "Worker", "Scheduler")

d.add(api, worker, scheduler)
d.connect(
    c.arrow(api, worker),
    c.arrow(scheduler, worker),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEpot8pqlDAr5m3F14ueNd5sMd5Y4912TdfAQKvW35W0eLT7NjO4hW4iY23gbvAK3Z0G00)



## Interfaces

### Provided Interfaces (Lollipop)

A component provides an interface it exposes:

```python
from plantuml_compose import component_diagram, render

d = component_diagram(title="REST API")
el = d.elements
c = d.connections

api = el.component("API Server")
rest = el.interface("REST")

d.add(api, rest)
# API provides REST interface (lollipop notation)
d.connect(c.provides(api, rest))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGXo3GvHS0pmv4hEpot8pqlDAr5G0d8LWbEBobABb1GIYq6oyH0kLsPUIMfHMc8oH1yNGaP1LrS38kQGcfS2D1u0)



### Required Interfaces (Socket)

A component requires an interface it depends on:

```python
from plantuml_compose import component_diagram, render

d = component_diagram(title="Service Dependencies")
el = d.elements
c = d.connections

web = el.component("Web Frontend")
rest = el.interface("REST")

d.add(web, rest)
# Web requires REST interface (socket notation)
d.connect(c.requires(web, rest))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGXEBIhBJ4vLS4ajICrBISrBpamjvahEpot8pqlDAr5G2azDKd0hoiyh0SegAIGMAm05uc42N9b0gYWj4QW_o3KuX0jPJa5JLnSYwW3a0Iq40000)



### Connected Interfaces

```python
from plantuml_compose import component_diagram, render

d = component_diagram(title="Full Integration")
el = d.elements
c = d.connections

api = el.component("API Server")
web = el.component("Web App")
rest = el.interface("REST")

d.add(api, web, rest)
# API provides, Web requires
d.connect(
    c.provides(api, rest),
    c.requires(web, rest),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/JOx12i8m44Jl-OgX9pta7zg3GczY1Oybjgi4qatORlr-5oFKsypmPfXsrI2wBSbfr4GuRocXPwMN18sPtPINafbOqNIN7WF9cwH1M65shFOVkjC3NIbVmlHesaNRasUO2DVJS7Dx4TuVQlP3SVI-1YtnRBS-)



### Service Shortcut

Create a component with its interfaces in one call:

```python
from plantuml_compose import component_diagram, render

d = component_diagram(title="Service Interfaces")
el = d.elements

# Creates component + interfaces + relationships
api = el.service(
    "API Gateway",
    provides=("REST", "GraphQL"),
    requires=("Auth", "Cache"),
)

d.add(api, *api._data["_provided_interfaces"], *api._data["_required_interfaces"])
d.connect(*api._data["_service_relationships"])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGXEBIhBJ4vLyCmhIIrAIqnEBUPApiyjoCzBpIjHK78Cy5HmJon9BK-iL598B5O0ykEXVAvCc0w58DVW42uaAGLTNGs884ADUr5YGKQW3uOoc3X2fMDfIGQACarTNOWWGerpOd96AeOYYAX3QbuAq7y0)



## Packages

Group related components:

```python
from plantuml_compose import component_diagram, render

d = component_diagram(title="Layered Architecture")
el = d.elements
c = d.connections

frontend = el.package("Frontend",
    el.component("Web App"),
    el.component("Mobile App"),
)

backend = el.package("Backend",
    el.component("API", ref="api"),
    el.component("Worker"),
)

data = el.package("Data",
    el.component("PostgreSQL"),
    el.component("Redis"),
)

d.add(frontend, backend, data)
d.connect(
    c.arrow(backend.api, "PostgreSQL"),
    c.arrow(backend.api, "Redis"),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/PP312i9034Jl_OhWlRyWhOWWLAXww57IRQXBszqbcnv4_7U3fTBgAPFXpH2IHK6MSUWJiT8J5FWWfWPoDdShP6HaIWAQ3bk20tidv1fu9W363y4xSWARYch8GzW0Hb1zKxq6JhwsMZupq_h1Nj_odSx_xhmyhlRASqUyYErHy2TJ-YWjq_LShEmBDJPgKYiXJRTBRBOc9DCpz2Dl)



### Nested Packages

```python
from plantuml_compose import component_diagram, render

d = component_diagram()
el = d.elements

services = el.package("Services",
    el.package("Core",
        el.component("Auth"),
        el.component("Users"),
    ),
    el.package("Features",
        el.component("Orders"),
        el.component("Payments"),
    ),
)

d.add(services)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIf8JCvEJ4zL24ujAijCJYrMgEPIK809EkSNfO8551IIytCBylDIyqeK74jBCj24GejJYug1OhL8UjrI4qjAYw068YlsBqg1g4OM34Yip0NI44DgkHnIyrA0hWC0)



## Connections

### Arrows

```python
from plantuml_compose import component_diagram, render

d = component_diagram()
el = d.elements
c = d.connections

api, db, cache = el.components("API", "Database", "Cache")

d.add(api, db, cache)
d.connect(
    # Simple arrow
    c.arrow(api, db),
    # With label
    c.arrow(api, cache, "reads"),
    # With style
    c.arrow(api, db, style={"color": "blue"}),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEpot8pqlDAr5m3F14uhaabYGc9HQd8Wav9oPdf781bIdewjeX5C04mD8ALWf5gOafnL3HQEMadDBKM6Jb3gbvAK2B0G00)



### Links (No Arrow)

```python
from plantuml_compose import component_diagram, render

d = component_diagram()
el = d.elements
c = d.connections

server_a = el.component("Server A")
server_b = el.component("Server B")

d.add(server_a, server_b)
# Bidirectional link (no arrowhead)
d.connect(c.link(server_a, server_b, "sync"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEpot8pqlDAr5G2aujAaijKd1KKaWiLe1muXsnA712Lk341LEfeAiB5rImKYYkp4lcSaZDIm7Q0W00)



### Direction Hints

```python
from plantuml_compose import component_diagram, render

d = component_diagram()
el = d.elements
c = d.connections

center = el.component("Center")
left = el.component("Left")
right = el.component("Right")
top = el.component("Top")
bottom = el.component("Bottom")

d.add(center, left, right, top, bottom)
d.connect(
    c.arrow(center, left, direction="left"),
    c.arrow(center, right, direction="right"),
    c.arrow(center, top, direction="up"),
    c.arrow(center, bottom, direction="down"),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEpot8pqlDAr5m1XAfHKW2Fgbf9KZSeCpq36H-I7u14iyflwGaFvSBOeY2hcwEhXt40BX84L04OWPSg1Ge1386Bf02582Qv92Qbm9q8000)



## Notes

```python
from plantuml_compose import component_diagram, render

d = component_diagram()
el = d.elements

api = el.component("API")

d.add(api)

# Note on component
d.note("Main entry point", target=api)

# Note with position
d.note("Critical service", position="left", target=api)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/HOmn2e0m303tlYBlSAeuEGX-eTHK0srIqYZuUoiEhdV7-MP1xIpPHIbL6DbWN6V7OWXA-s4WwIK3B84OkjSRgX3RrsHCVp8f6SMGeQ5U5D5vvAtF7m00)



## Diagram Styling

Style all elements of a type using `diagram_style`:

```python
from plantuml_compose import component_diagram, render

d = component_diagram(
    diagram_style={
        "component": {"background": "#E3F2FD"},
        "package": {"background": "#E8F5E9"},
        "node": {"background": "#FFF3E0"},
        "database": {"background": "#FCE4EC"},
        "cloud": {"background": "#F3E5F5"},
        "arrow": {"line_color": "#757575"},
    }
)
el = d.elements
c = d.connections

backend = el.package("Backend",
    el.component("API", ref="api"),
)

server = el.node("Server",
    el.component("App", ref="app"),
)

db = el.database("PostgreSQL",
    el.component("Tables"),
)

aws = el.cloud("AWS",
    el.component("Lambda"),
)

d.add(backend, server, db, aws)
d.connect(c.dependency(backend.api, server.app))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/TT5HIyCm403Wz_wAWEzJh4M5CJQx18G-J2huV6sECfRcoYLLHFRVlTMuXq89UKZkut9tsOO87CVUPUiGlnrkifRwWJpwk3z2nz2hdqofw-LqKke5sbF7D7fRaYDMDpetzsOliRFiGQBGuQ9zCeL-JjQJNOJ6c5pV9TWw6ksYp7LXYYGjH6WWBASjzOCk4mPc-agoEdfCvh6uhCcSi_Ljcir_OvUKwEriDBl3g-2feHhv4taU7mQ9NwixK8WTO_rMpTmxD0w3qB-MTn_r35JGDnO4o8jgjTfCcRTIaFpZBm00)



Available style targets: `component`, `interface`, `package`, `node`, `folder`, `frame`, `cloud`, `database`, `arrow`, `note`, `title`.

## Complete Example: Microservices Architecture

```python
from plantuml_compose import component_diagram, render

d = component_diagram(title="E-Commerce Microservices")
el = d.elements
c = d.connections

# API Gateway
gateway = el.component("API Gateway", stereotype="gateway")

# Create interfaces
rest = el.interface("REST")
grpc = el.interface("gRPC")
events = el.interface("Events")

# Core services
core = el.package("Core Services",
    el.component("Auth Service", ref="auth"),
    el.component("User Service", ref="users"),
)

# Business services
business = el.package("Business Services",
    el.component("Order Service", ref="orders"),
    el.component("Inventory Service", ref="inventory"),
    el.component("Payment Service", ref="payments"),
)

# Infrastructure
infra = el.package("Infrastructure",
    el.component("PostgreSQL", stereotype="database", ref="db"),
    el.component("Redis", stereotype="cache", ref="cache"),
    el.component("RabbitMQ", stereotype="queue", ref="queue"),
)

d.add(gateway, rest, grpc, events, core, business, infra)
d.connect(
    # Gateway provides REST
    c.provides(gateway, rest),

    # Gateway to services
    c.arrow(gateway, core.auth, "authenticate"),
    c.arrow(gateway, business.orders, "order operations"),

    # Service to service (via gRPC)
    c.provides(core.users, grpc),
    c.requires(core.auth, grpc),

    # Event-driven connections
    c.provides(business.orders, events),
    c.requires(business.inventory, events),
    c.requires(business.payments, events),
    c.link(infra.queue, events, "transports"),

    # Data access
    c.arrow(core.users, infra.db),
    c.arrow(business.orders, infra.db),
    c.arrow(core.auth, infra.cache, "sessions"),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/TLFBRi8m4BpdAonExI4_W514Yr25LDG0xHajPWbMYPtQ6ofKyU_TF6iJUilEpAvd7vaw0ajbVef8qGd5F9wPF4ShKIoLjCQXFIk9Bf8cBun6JMBqb2x42n1-msKam0cEjsqi9fEi-KgII6b2Um0kjPvlthqmMwSpBvoVkQoB_39n_D0a5I0_8KCncXcBOjEwgP-ja6s7Y9z82DzZISTEtfXae5E7qW_kCP1MG2-z_bbuBftIw5neeqF_jV9czpSFrCXzCmjT3SFOIv3Ge_UJKhZarOUVqc9t-bZeWmL7jfHKyan3jwbnb5dSh5vvbNiWs853tgMlMUDUEQOboEE0WzrEqNB5z5U9PKLVRpQR1BiGOm4SSgwIB1beWrcnsDJJD0LQ86MqY_njrNTJNrVmn6CSDsXOh1AtjpSOS9tJaZUZzAc-tHvYYsH1ky9O6fXBlFaEp0HauB_Ycg6FXUDJg_kUejxpV_iB)



## Quick Reference

| Method | Description |
|--------|-------------|
| `el.component(name)` | Create component |
| `el.components(*names)` | Create multiple components |
| `el.interface(name)` | Create interface |
| `el.interfaces(*names)` | Create multiple interfaces |
| `el.service(name, provides, requires)` | Component with interfaces |
| `c.provides(component, interface)` | Lollipop connection |
| `c.requires(component, interface)` | Socket connection |
| `c.arrow(a, b)` | Arrow connection |
| `c.link(a, b)` | Line connection (no arrow) |
| `c.chain(a, b, c)` | Chain of arrows |
| `c.arrows_from(source, *targets)` | Fan-out arrows |
| `el.package(name, *children)` | Package container |
| `el.node(name, *children)` | Node container (3D box) |
| `el.database(name, *children)` | Database container (cylinder shape) |
| `el.cloud(name, *children)` | Cloud container |
| `d.note(text, target=ref)` | Add note |

> **Tip:** `stereotype="database"` adds a text label (`<<database>>`), not a cylinder shape. For the cylinder visual, use `el.database("name")` instead.
