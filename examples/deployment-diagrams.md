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
from plantuml_compose import deployment_diagram, render

d = deployment_diagram(title="Simple Server")
el = d.elements
c = d.connections

server = el.component("App Server")
db = el.database("PostgreSQL")

d.add(server, db)
d.connect(c.arrow(server, db, "connects"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGZEp2q0KQb5PQb5NCdvkGNvUQbv9GfAZWK5K54bhfJ4aiIanE9KXO3yufBqejJWG1yke7myH5v1LzSEIKR1IY4vFoylDRcacCiXDIy5Q1S0)



## Element Types

### Basic Elements

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram(title="Element Types")
el = d.elements

# Component (software module)
api = el.component("API Service")

# Database (cylinder shape)
db = el.database("PostgreSQL")

# Artifact (deployable file)
war = el.artifact("app.war")

# Queue
mq = el.queue("RabbitMQ")

# Storage
s3 = el.storage("S3 Bucket")

# Cloud
aws = el.cloud("AWS")

# Actor (user/external system)
user = el.actor("User")

d.add(api, db, war, mq, s3, aws, user)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/5Ov12i8m44NtSueX1t3Z1QhWGb1eZU9wcdvBC6rYCb6ylN7vuRt7xufArhe4Kgy1V0XOi2fVlmc5N5nINF_RxFeZM-ItTp0qYSee1Tp7edE67KxKCluXhg6IqkOZsT2hee8lCevUpmCLZLbciB5RtbVtX1fo8TQ9TtTBJOsPRmMPEgnJk_G3)



### Stereotypes

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram()
el = d.elements

# Custom stereotypes
api = el.component("API", stereotype="microservice")
db = el.database("Redis", stereotype="cache")
docker = el.artifact("container.tar", stereotype="docker")

d.add(api, db, docker)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/5Or13a1034NtJZ5n02SGOMadRb2TYePffLFEhzRl_VV7wc3-bAj1BRSAYQTfcLFV5qRJIlOoqZ0q6Hmsg9HMobo38-3nWvZp3kYfHHK75h8kccqeMV4a2sSaoV7n0G00)



## Nested Elements (Nodes)

Show containment with nested structures:

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram(title="Server Internals")
el = d.elements
c = d.connections

server = el.node("Production Server",
    el.component("API Service", ref="api"),
    el.component("Worker Service"),
    el.database("PostgreSQL", ref="db"),
)

d.add(server)
d.connect(c.arrow(server.api, server.db))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LOwn2iCm34HtVuNmdbyewHZ8u9AXisABOEf8GLQwXFvxdT8E7OzxxxY-6ghjQt6MhH1Cf4zI6DX86KjrB8d01vMqHyl2NyB3uG2Yh9imiO6_Xk5JvKWUi09k-H-uYpxQyezfPKB36Ij1a6gBqdGRJpFDxkMQ3brtEKDFdDh1Dm00)



### Cloud Nested

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram(title="AWS Infrastructure")
el = d.elements
c = d.connections

aws = el.cloud("AWS",
    el.node("EC2 Instance",
        el.component("Web App", ref="webapp"),
    ),
    el.database("RDS PostgreSQL", ref="rds"),
    el.storage("S3"),
)

d.add(aws)
d.connect(
    c.arrow(aws.webapp, aws.rds),
    c.arrow(aws.webapp, aws["S3"]),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/JOun3i8m34NtdCBAtWLsr0eOa1Y039tTn5H8RHB5ZXXGxuuL5WOFzdlV-ZqB5gdhOkGb2y4mEhZ4Pq6MKhtKGiOlgOO6FWOWfa1WpyUTQfgDdcox0_YqvXGf2jYH9XXoje0CRvemPpKsdO224x9-U9mSt1BBNCZThyqiWLLXIGLd0hStc_c5eUiEZVwjYdkAGPj_0G00)



### Multi-Level Nesting

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram(title="Container Orchestration")
el = d.elements
c = d.connections

k8s = el.node("Kubernetes Cluster",
    el.node("Node 1",
        el.component("API Pod", ref="api1"),
        el.component("Worker Pod"),
    ),
    el.node("Node 2",
        el.component("API Pod"),
        el.database("Redis Pod"),
    ),
)

ext_db = el.database("External PostgreSQL", ref="extdb")

d.add(k8s, ext_db)
d.connect(c.arrow(k8s.api1, ext_db))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/VP312i9034Jl-nLXxptK3v1AyI2ALZruJhj15zjisKsX8FrtjwrGzE0ba7d3P4WM1BrqJQt4IasGEnQqJ1vEldfG48zY7IjsXa3lkv8yar20lEw2aDVmKW0pFOupdHM0oZMjOs81lIbsK3YZ0GDWQzDVVdF-6I-EbeY6xy3Ldy19DoXOOeZ-2naRbfX1BMZRnxACTQH1xfwkvyDKXtenfHfBGPAiFsj6RE9BtW00)



## Connections

### Arrows

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram()
el = d.elements
c = d.connections

api = el.component("API")
db = el.database("Database")
cache = el.component("Cache")

d.add(api, db, cache)
d.connect(
    # Simple arrow
    c.arrow(api, db),
    # With label
    c.arrow(api, cache, "reads"),
    # Dotted arrow
    c.arrow(api, db, "async", style={"line_pattern": "dotted"}),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEpot8pqlDAr5m3F3aIaaiIKnAB4vLS84oaEIT4vCpKhc0gXHqTUqG2c02O6a5AuMYrCIKOh2edXv26L0YiRWoBvdB8JKl1MWl0000)



### Links (No Direction)

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram()
el = d.elements
c = d.connections

server_a = el.component("Server A")
server_b = el.component("Server B")

d.add(server_a, server_b)
# Bidirectional link
d.connect(c.line(server_a, server_b, "replication"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEpot8pqlDAr5G2aujAaijKd1KmYBefCG5OSKxAkZgAa3PJWfM2aMf1JcPoOabcVbvN0wfUIb0Gm40)



### Hub and Spoke (arrows_from)

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram(title="Load Balancing")
el = d.elements
c = d.connections

lb = el.component("Load Balancer")
s1 = el.component("Server 1")
s2 = el.component("Server 2")
s3 = el.component("Server 3")

d.add(lb, s1, s2, s3)
# Connect lb to all servers
d.connect(c.arrows_from(lb, s1, s2, s3))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LV39JqnHS4hCISnBpinBvqhEpot8pqlDAr5GGf99BL92bWbEBIfBBL8mn2PeX4tGM8aBP5eyp3G5NLqx1OXSl25kAIFSKiPS3gbvAK1l0000)



### Direction Hints

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram()
el = d.elements
c = d.connections

web = el.component("Web")
api = el.component("API")
db = el.database("Database")

d.add(web, api, db)
d.connect(
    c.arrow(web, api, direction="down"),
    c.arrow(api, db, direction="down"),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEpot8pqlDAr48Jqr2uZa6U7Ab99Oa9YKMfoguG1bSG3KAkhefkdPWUI26yk0A75BpKe360W00)



## Styling

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram()
el = d.elements
c = d.connections

# Styled elements
api = el.component("API", style={"background": "LightBlue"})
db = el.database("Database", style={"background": "LightGreen"})

d.add(api, db)
# Styled connection
d.connect(c.arrow(api, db, style={"color": "blue"}))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEpot8pqlDAr5m3F1KKFR9JCyeSSefJULAIIn9J4eiJbLmWJ4Wakv5gQbvN235khhHoab0fR6wTd15N0wfUIb0Sm40)



## Notes

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram()
el = d.elements
c = d.connections

api = el.component("API")
db = el.database("Database")

d.add(api, db)

d.note("Primary instance", target=api)
d.note("Read replicas available", target=db, position="left")

d.connect(c.arrow(api, db))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/HOun3i8m40Hxls8_a0-aG46YeOlumSM-m4dsEJeVIFm-1WNHRJ4xkrDpCd-M768jMrLMntc-XaHE2pN6vGX1gpDCxWz7NJ_CYDcaaBqXsYqQ3oRp-aL-pH4tfWJZBKka1dgHP5eoXox1C9p-6nDhwbzs)



## Complete Example: Production Infrastructure

```python
from plantuml_compose import deployment_diagram, render

d = deployment_diagram(title="Production Environment")
el = d.elements
c = d.connections

# External users
user = el.actor("Users")

# CDN and Load Balancer
cdn = el.cloud("CloudFront CDN")
lb = el.component("ALB", stereotype="load-balancer")

# Application tier
vpc = el.cloud("AWS VPC",
    el.node("App Subnet",
        el.node("ECS Cluster",
            el.component("API Service", ref="api"),
            el.component("Worker Service", ref="worker"),
        ),
    ),
    el.node("Data Subnet",
        el.database("RDS PostgreSQL", ref="rds"),
        el.database("ElastiCache Redis", ref="redis"),
    ),
)

# External services
s3 = el.storage("S3 Assets")
sqs = el.queue("SQS Queue")

d.add(user, cdn, lb, vpc, s3, sqs)

# Connections
d.connect(
    c.arrow(user, cdn),
    c.arrow(cdn, lb),
    c.arrow(lb, vpc.api),
    c.arrow(vpc.api, vpc.rds),
    c.arrow(vpc.api, vpc.redis),
    c.arrow(vpc.api, s3),
    c.arrow(vpc.api, sqs),
    c.arrow(sqs, vpc.worker),
    c.arrow(vpc.worker, vpc.rds),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/PP91Rm8X48Nl_8h9tlVarHYtgqsQc6PNqdeq21DBYh1bm1uQ_tk1xMgq1yBZyIrlyh9B2iA7U38iw60GEkzKb44x2sjxrjxP4zh0X0pEmnkX9oQDYmggDc_F2GZGhbuh9jrfS3R1q6oUO3utJgZw88om4lrYCNtMx3YyTsq5Fmp0EeN96WRWyM0nZExahriEhOaKq4yN0BUOgkbUWAC_QuaL208nwF_GplbFz7VSTx4AUc7Z6WDN8eY7ILIo3eBIvNR5eNCKZXvvloaFUKKFqDe82heLyWDXYqhJo6LLaYwCKf7Yc50-WuO80rNiAsBCJi-Xpx9YfMcewmNSQjwdcjdziH2fRfOhppfNa5RHURghBXDC9pxRZz4tf-Vx4iskglX_LOtRzTKbMfL-cLy0)



## Quick Reference

### Basic Elements

| Method | Description |
|--------|-------------|
| `el.component(name)` | Software component |
| `el.database(name)` | Database (cylinder) |
| `el.artifact(name)` | Deployable file |
| `el.storage(name)` | Storage system |
| `el.queue(name)` | Message queue |
| `el.cloud(name)` | Cloud |
| `el.actor(name)` | User/external system |
| `el.file(name)` | File |
| `el.folder(name)` | Folder |

### Nesting

| Pattern | Description |
|---------|-------------|
| `el.node(name, *children)` | Node with children |
| `el.cloud(name, *children)` | Cloud with children |
| `el.database(name, *children)` | Database with children |
| `el.folder(name, *children)` | Folder with children |
| `el.frame(name, *children)` | Frame with children |
| `el.package(name, *children)` | Package with children |
| `el.rectangle(name, *children)` | Rectangle with children |

### Connections

| Method | Description |
|--------|-------------|
| `c.arrow(a, b)` | Arrow connection |
| `c.line(a, b)` | Line (no arrow) |
| `c.arrows_from(source, *targets)` | Fan-out arrows |
| `d.note(text, target=ref)` | Add note |
