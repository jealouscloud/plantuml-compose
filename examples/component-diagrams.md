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
from plantuml_compose import component_diagram

with component_diagram(title="Simple System") as d:
    api = d.component("API Server")
    db = d.component("Database")

    d.arrow(api, db, label="queries")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGZEp2q0KPN59QcvNCdvkGNvUQbv9GfAZW6U2i6fHMMfHKeAYSKAG6uyX8kao2Mn934fiJYL2o6heAjh1nTNi58eB4qjoamjvd98pKi1sWe0)



## Components

### Basic Components

```python
from plantuml_compose import component_diagram

with component_diagram() as d:
    # Simple component
    api = d.component("API Gateway")

    # With stereotype
    db = d.component("PostgreSQL", stereotype="database")

    # With styling
    cache = d.component("Redis", style={"background": "LightYellow"})

    # With attached note
    auth = d.component("Auth Service", note="Handles OAuth2")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/LO-n3e9044Jx-ueD_e6b8GGhDI4HfR8YAxV29SUjkLqa_hqGAQ2SDpEPJ2wAKOVUcuRxDmSA2icnlC09bKRy9e02awuNlOgLBDf6gcu5fAb5nISAPTagSIVh17Q5QpjzaFSyRbO6xQ2Y-74D_MScK2_015Q2E3U1Nnlh06SCrfF0TSPxarEmquCV)



### Bulk Component Creation

```python
from plantuml_compose import component_diagram

with component_diagram() as d:
    # Create multiple at once
    api, worker, scheduler = d.components("API", "Worker", "Scheduler")

    d.arrow(api, worker)
    d.arrow(scheduler, worker)

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEpot8pqlDAr5m3F14ueNd5sMd5Y4912TdfAQKvW35W0eLT7NjO4hW4iY23gbvAK3Z0G00)



## Interfaces

### Provided Interfaces (Lollipop)

A component provides an interface it exposes:

```python
from plantuml_compose import component_diagram

with component_diagram(title="REST API") as d:
    api = d.component("API Server")
    rest = d.interface("REST")

    # API provides REST interface (lollipop notation)
    d.provides(api, rest)

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGXo3GvHS0pmv4hEpot8pqlDAr5G0d8LWbEBobABb1GIYq6oyH0kLsPUIMfHMc8oH1yNGaP1LrS38kQGcfS2D1u0)



### Required Interfaces (Socket)

A component requires an interface it depends on:

```python
from plantuml_compose import component_diagram

with component_diagram(title="Service Dependencies") as d:
    web = d.component("Web Frontend")
    rest = d.interface("REST")

    # Web requires REST interface (socket notation)
    d.requires(web, rest)

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGXEBIhBJ4vLS4ajICrBISrBpamjvahEpot8pqlDAr5G2azDKd0hoiyh0SegAIGMAm05uc42N9b0gYWj4QW_o3KuX0jPJa5JLnSYwW3a0Iq40000)



### Connected Interfaces

```python
from plantuml_compose import component_diagram

with component_diagram(title="Full Integration") as d:
    api = d.component("API Server")
    web = d.component("Web App")
    rest = d.interface("REST")

    # API provides, Web requires
    d.provides(api, rest)
    d.requires(web, rest)

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/JOx12i8m44Jl-OgX9pta7zg3GczY1Oybjgi4qatORlr-5oFKsypmPfXsrI2wBSbfr4GuRocXPwMN18sPtPINafbOqNIN7WF9cwH1M65shFOVkjC3NIbVmlHesaNRasUO2DVJS7Dx4TuVQlP3SVI-1YtnRBS-)



### Service Shortcut

Create a component with its interfaces in one call:

```python
from plantuml_compose import component_diagram

with component_diagram(title="Service Interfaces") as d:
    # Creates component + interfaces + relationships
    api = d.service(
        "API Gateway",
        provides=("REST", "GraphQL"),
        requires=("Auth", "Cache"),
    )

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGXEBIhBJ4vLyCmhIIrAIqnEBUPApiyjoCzBpIjHK78Cy5HmJon9BK-iL598B5O0ykEXVAvCc0w58DVW42uaAGLTNGs884ADUr5YGKQW3uOoc3X2fMDfIGQACarTNOWWGerpOd96AeOYYAX3QbuAq7y0)



## Packages

Group related components:

```python
from plantuml_compose import component_diagram

with component_diagram(title="Layered Architecture") as d:
    with d.package("Frontend") as frontend:
        frontend.component("Web App")
        frontend.component("Mobile App")

    with d.package("Backend") as backend:
        api = backend.component("API")
        worker = backend.component("Worker")

    with d.package("Data") as data:
        data.component("PostgreSQL")
        data.component("Redis")

    d.arrow(api, "PostgreSQL")
    d.arrow(api, "Redis")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/PP312i9034Jl_OhWlRyWhOWWLAXww57IRQXBszqbcnv4_7U3fTBgAPFXpH2IHK6MSUWJiT8J5FWWfWPoDdShP6HaIWAQ3bk20tidv1fu9W363y4xSWARYch8GzW0Hb1zKxq6JhwsMZupq_h1Nj_odSx_xhmyhlRASqUyYErHy2TJ-YWjq_LShEmBDJPgKYiXJRTBRBOc9DCpz2Dl)



### Nested Packages

```python
from plantuml_compose import component_diagram

with component_diagram() as d:
    with d.package("Services") as services:
        with services.package("Core") as core:
            core.component("Auth")
            core.component("Users")

        with services.package("Features") as features:
            features.component("Orders")
            features.component("Payments")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIf8JCvEJ4zL24ujAijCJYrMgEPIK809EkSNfO8551IIytCBylDIyqeK74jBCj24GejJYug1OhL8UjrI4qjAYw068YlsBqg1g4OM34Yip0NI44DgkHnIyrA0hWC0)



## Connections

### Arrows

```python
from plantuml_compose import component_diagram

with component_diagram() as d:
    api, db, cache = d.components("API", "Database", "Cache")

    # Simple arrow
    d.arrow(api, db)

    # With label
    d.arrow(api, cache, label="reads")

    # With style
    d.arrow(api, db, style={"color": "blue"})

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEpot8pqlDAr5m3F14uhaabYGc9HQd8Wav9oPdf781bIdewjeX5C04mD8ALWf5gOafnL3HQEMadDBKM6Jb3gbvAK2B0G00)



### Links (No Arrow)

```python
from plantuml_compose import component_diagram

with component_diagram() as d:
    server_a = d.component("Server A")
    server_b = d.component("Server B")

    # Bidirectional link (no arrowhead)
    d.link(server_a, server_b, label="sync")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEpot8pqlDAr5G2aujAaijKd1KKaWiLe1muXsnA712Lk341LEfeAiB5rImKYYkp4lcSaZDIm7Q0W00)



### Direction Hints

```python
from plantuml_compose import component_diagram

with component_diagram() as d:
    center = d.component("Center")
    left = d.component("Left")
    right = d.component("Right")
    top = d.component("Top")
    bottom = d.component("Bottom")

    d.arrow(center, left, direction="left")
    d.arrow(center, right, direction="right")
    d.arrow(center, top, direction="up")
    d.arrow(center, bottom, direction="down")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEpot8pqlDAr5m1XAfHKW2Fgbf9KZSeCpq36H-I7u14iyflwGaFvSBOeY2hcwEhXt40BX84L04OWPSg1Ge1386Bf02582Qv92Qbm9q8000)



## Notes

```python
from plantuml_compose import component_diagram

with component_diagram() as d:
    api = d.component("API")

    # Note on component
    d.note("Main entry point", target=api)

    # Note with position
    d.note("Critical service", position="left", target=api)

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/HOmn2e0m303tlYBlSAeuEGX-eTHK0srIqYZuUoiEhdV7-MP1xIpPHIbL6DbWN6V7OWXA-s4WwIK3B84OkjSRgX3RrsHCVp8f6SMGeQ5U5D5vvAtF7m00)



## Diagram Styling

Style all elements of a type using `diagram_style`:

```python
from plantuml_compose import component_diagram

with component_diagram(
    diagram_style={
        "component": {"background": "#E3F2FD"},
        "package": {"background": "#E8F5E9"},
        "node": {"background": "#FFF3E0"},
        "database": {"background": "#FCE4EC"},
        "cloud": {"background": "#F3E5F5"},
        "arrow": {"line_color": "#757575"},
    }
) as d:
    with d.package("Backend") as backend:
        api = backend.component("API")

    with d.node("Server") as server:
        app = server.component("App")

    with d.database("PostgreSQL") as db:
        db.component("Tables")

    with d.cloud("AWS") as aws:
        aws.component("Lambda")

    d.depends(api, app)

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/TT5HIyCm403Wz_wAWEzJh4M5CJQx18G-J2huV6sECfRcoYLLHFRVlTMuXq89UKZkut9tsOO87CVUPUiGlnrkifRwWJpwk3z2nz2hdqofw-LqKke5sbF7D7fRaYDMDpetzsOliRFiGQBGuQ9zCeL-JjQJNOJ6c5pV9TWw6ksYp7LXYYGjH6WWBASjzOCk4mPc-agoEdfCvh6uhCcSi_Ljcir_OvUKwEriDBl3g-2feHhv4taU7mQ9NwixK8WTO_rMpTmxD0w3qB-MTn_r35JGDnO4o8jgjTfCcRTIaFpZBm00)



Available style targets: `component`, `interface`, `package`, `node`, `folder`, `frame`, `cloud`, `database`, `arrow`, `note`, `title`.

## Complete Example: Microservices Architecture

```python
from plantuml_compose import component_diagram

with component_diagram(title="E-Commerce Microservices") as d:
    # API Gateway
    gateway = d.component("API Gateway", stereotype="gateway")

    # Create interfaces
    rest = d.interface("REST")
    grpc = d.interface("gRPC")
    events = d.interface("Events")

    # Gateway provides REST
    d.provides(gateway, rest)

    # Core services
    with d.package("Core Services") as core:
        auth = core.component("Auth Service")
        users = core.component("User Service")

    # Business services
    with d.package("Business Services") as business:
        orders = business.component("Order Service")
        inventory = business.component("Inventory Service")
        payments = business.component("Payment Service")

    # Infrastructure
    with d.package("Infrastructure") as infra:
        db = infra.component("PostgreSQL", stereotype="database")
        cache = infra.component("Redis", stereotype="cache")
        queue = infra.component("RabbitMQ", stereotype="queue")

    # Gateway to services
    d.arrow(gateway, auth, label="authenticate")
    d.arrow(gateway, orders, label="order operations")

    # Service to service (via gRPC)
    d.provides(users, grpc)
    d.requires(auth, grpc)

    # Event-driven connections
    d.provides(orders, events)
    d.requires(inventory, events)
    d.requires(payments, events)
    d.link(queue, events, label="transports")

    # Data access
    d.arrow(users, db)
    d.arrow(orders, db)
    d.arrow(auth, cache, label="sessions")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/TLFBRi8m4BpdAonExI4_W514Yr25LDG0xHajPWbMYPtQ6ofKyU_TF6iJUilEpAvd7vaw0ajbVef8qGd5F9wPF4ShKIoLjCQXFIk9Bf8cBun6JMBqb2x42n1-msKam0cEjsqi9fEi-KgII6b2Um0kjPvlthqmMwSpBvoVkQoB_39n_D0a5I0_8KCncXcBOjEwgP-ja6s7Y9z82DzZISTEtfXae5E7qW_kCP1MG2-z_bbuBftIw5neeqF_jV9czpSFrCXzCmjT3SFOIv3Ge_UJKhZarOUVqc9t-bZeWmL7jfHKyan3jwbnb5dSh5vvbNiWs853tgMlMUDUEQOboEE0WzrEqNB5z5U9PKLVRpQR1BiGOm4SSgwIB1beWrcnsDJJD0LQ86MqY_njrNTJNrVmn6CSDsXOh1AtjpSOS9tJaZUZzAc-tHvYYsH1ky9O6fXBlFaEp0HauB_Ycg6FXUDJg_kUejxpV_iB)



## Quick Reference

| Method | Description |
|--------|-------------|
| `d.component(name)` | Create component |
| `d.components(*names)` | Create multiple components |
| `d.interface(name)` | Create interface |
| `d.interfaces(*names)` | Create multiple interfaces |
| `d.service(name, provides, requires)` | Component with interfaces |
| `d.provides(component, interface)` | Lollipop connection |
| `d.requires(component, interface)` | Socket connection |
| `d.arrow(a, b)` | Arrow connection |
| `d.link(a, b)` | Line connection (no arrow) |
| `d.package(name)` | Package container |
| `d.note(text, target)` | Add note |
