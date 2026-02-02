# Deployment Diagrams

Deployment diagrams show WHERE software runs on hardware and infrastructure. They're ideal for:

- **Production architecture**: Server topology and connectivity
- **Infrastructure planning**: Cloud resources, containers, VMs
- **Network topology**: How systems connect
- **Artifact deployment**: What runs where

Unlike component diagrams (software modules) or class diagrams (code structure), deployment diagrams focus on physical or virtual infrastructure.

## Core Concepts

**Node**: An execution environment (server, VM, container, device).

**Artifact**: A deployable unit (WAR, JAR, Docker image, executable).

**Component**: A software piece running on a node.

**Database**: A data storage system.

Nesting shows containment: a Docker container inside a VM inside a physical server.

## Your First Deployment Diagram

```python
from plantuml_compose import deployment_diagram

with deployment_diagram(title="Simple Server") as d:
    server = d.component("App Server")
    db = d.database("PostgreSQL")

    d.arrow(server, db, label="connects")

print(d.render())
```

## Element Types

### Basic Elements

```python
from plantuml_compose import deployment_diagram

with deployment_diagram(title="Element Types") as d:
    # Component (software module)
    api = d.component("API Service")

    # Database (cylinder shape)
    db = d.database("PostgreSQL")

    # Artifact (deployable file)
    war = d.artifact("app.war")

    # Queue
    mq = d.queue("RabbitMQ")

    # Storage
    s3 = d.storage("S3 Bucket")

    # Cloud
    aws = d.cloud("AWS")

    # Actor (user/external system)
    user = d.actor("User")

print(d.render())
```

### Stereotypes

```python
from plantuml_compose import deployment_diagram

with deployment_diagram() as d:
    # Custom stereotypes
    api = d.component("API", stereotype="microservice")
    db = d.database("Redis", stereotype="cache")
    docker = d.artifact("container.tar", stereotype="docker")

print(d.render())
```

## Nested Elements (Nodes)

Show containment with nested structures:

```python
from plantuml_compose import deployment_diagram

with deployment_diagram(title="Server Internals") as d:
    with d.node_nested("Production Server") as server:
        api = server.component("API Service", alias="api")
        server.component("Worker Service")
        db = server.database("PostgreSQL", alias="db")

    d.arrow(api, db)

print(d.render())
```

### Cloud Nested

```python
from plantuml_compose import deployment_diagram

with deployment_diagram(title="AWS Infrastructure") as d:
    with d.cloud_nested("AWS") as aws:
        with aws.node_nested("EC2 Instance") as ec2:
            webapp = ec2.component("Web App", alias="webapp")

        rds = aws.database("RDS PostgreSQL", alias="rds")
        s3 = aws.storage("S3")

    d.arrow(webapp, rds)
    d.arrow(webapp, s3)

print(d.render())
```

### Multi-Level Nesting

```python
from plantuml_compose import deployment_diagram

with deployment_diagram(title="Container Orchestration") as d:
    with d.node_nested("Kubernetes Cluster") as k8s:
        with k8s.node_nested("Node 1") as node1:
            api1 = node1.component("API Pod", alias="api1")
            node1.component("Worker Pod")

        with k8s.node_nested("Node 2") as node2:
            node2.component("API Pod")
            node2.database("Redis Pod")

    ext_db = d.database("External PostgreSQL", alias="extdb")
    d.arrow(api1, ext_db)

print(d.render())
```

## Connections

### Arrows

```python
from plantuml_compose import deployment_diagram

with deployment_diagram() as d:
    api = d.component("API")
    db = d.database("Database")
    cache = d.component("Cache")

    # Simple arrow
    d.arrow(api, db)

    # With label
    d.arrow(api, cache, label="reads")

    # Dotted arrow
    d.arrow(api, db, dotted=True, label="async")

print(d.render())
```

### Links (No Direction)

```python
from plantuml_compose import deployment_diagram

with deployment_diagram() as d:
    server_a = d.component("Server A")
    server_b = d.component("Server B")

    # Bidirectional link
    d.link(server_a, server_b, label="replication")

print(d.render())
```

### Hub and Spoke (Connect)

```python
from plantuml_compose import deployment_diagram

with deployment_diagram(title="Load Balancing") as d:
    lb = d.component("Load Balancer")
    s1 = d.component("Server 1")
    s2 = d.component("Server 2")
    s3 = d.component("Server 3")

    # Connect lb to all servers
    d.connect(lb, [s1, s2, s3])

print(d.render())
```

### Direction Hints

```python
from plantuml_compose import deployment_diagram

with deployment_diagram() as d:
    web = d.component("Web")
    api = d.component("API")
    db = d.database("Database")

    d.arrow(web, api, direction="down")
    d.arrow(api, db, direction="down")

print(d.render())
```

## Styling

```python
from plantuml_compose import deployment_diagram

with deployment_diagram() as d:
    # Styled elements
    api = d.component("API", style={"background": "LightBlue"})
    db = d.database("Database", style={"background": "LightGreen"})

    # Styled connection
    d.arrow(api, db, style={"color": "blue"})

print(d.render())
```

## Notes

```python
from plantuml_compose import deployment_diagram

with deployment_diagram() as d:
    api = d.component("API")
    db = d.database("Database")

    d.note("Primary instance", target=api)
    d.note("Read replicas available", target=db, position="left")

    d.arrow(api, db)

print(d.render())
```

## Complete Example: Production Infrastructure

```python
from plantuml_compose import deployment_diagram

with deployment_diagram(title="Production Environment") as d:
    # External users
    user = d.actor("Users")

    # CDN and Load Balancer
    cdn = d.cloud("CloudFront CDN")
    lb = d.component("ALB", stereotype="load-balancer")

    # Application tier
    with d.cloud_nested("AWS VPC") as vpc:
        with vpc.node_nested("App Subnet") as app:
            with app.node_nested("ECS Cluster") as ecs:
                api = ecs.component("API Service", alias="api")
                worker = ecs.component("Worker Service", alias="worker")

        with vpc.node_nested("Data Subnet") as data:
            rds = data.database("RDS PostgreSQL", alias="rds")
            redis = data.database("ElastiCache Redis", alias="redis")

    # External services
    s3 = d.storage("S3 Assets")
    sqs = d.queue("SQS Queue")

    # Connections
    d.arrow(user, cdn)
    d.arrow(cdn, lb)
    d.arrow(lb, api)

    d.arrow(api, rds)
    d.arrow(api, redis)
    d.arrow(api, s3)
    d.arrow(api, sqs)
    d.arrow(sqs, worker)
    d.arrow(worker, rds)

print(d.render())
```

## Quick Reference

### Basic Elements

| Method | Description |
|--------|-------------|
| `d.component(name)` | Software component |
| `d.database(name)` | Database (cylinder) |
| `d.artifact(name)` | Deployable file |
| `d.storage(name)` | Storage system |
| `d.queue(name)` | Message queue |
| `d.cloud(name)` | Cloud (simple) |
| `d.actor(name)` | User/external system |
| `d.file(name)` | File |
| `d.folder(name)` | Folder |

### Nested Elements

| Method | Description |
|--------|-------------|
| `d.node_nested(name)` | Node with children |
| `d.cloud_nested(name)` | Cloud with children |
| `d.database_nested(name)` | Database with children |
| `d.folder_nested(name)` | Folder with children |
| `d.frame_nested(name)` | Frame with children |
| `d.package_nested(name)` | Package with children |
| `d.rectangle_nested(name)` | Rectangle with children |

### Connections

| Method | Description |
|--------|-------------|
| `d.arrow(a, b)` | Arrow connection |
| `d.link(a, b)` | Line (no arrow) |
| `d.connect(hub, spokes)` | Hub to multiple |
| `d.note(text, target)` | Add note |
