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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGZEp2q0KQb5PQb5NCdvkGNvUQbv9GfAZWK5K54bhfJ4aiIanE9KXO3yufBqejJWG1yke7myH5v1LzSEIKR1IY4vFoylDRcacCiXDIy5Q1S0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/5Ov12i8m44NtSueX1t3Z1QhWGb1eZU9wcdvBC6rYCb6ylN7vuRt7xufArhe4Kgy1V0XOi2fVlmc5N5nINF_RxFeZM-ItTp0qYSee1Tp7edE67KxKCluXhg6IqkOZsT2hee8lCevUpmCLZLbciB5RtbVtX1fo8TQ9TtTBJOsPRmMPEgnJk_G3)



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
![Diagram](https://www.plantuml.com/plantuml/svg/5Or13a1034NtJZ5n02SGOMadRb2TYePffLFEhzRl_VV7wc3-bAj1BRSAYQTfcLFV5qRJIlOoqZ0q6Hmsg9HMobo38-3nWvZp3kYfHHK75h8kccqeMV4a2sSaoV7n0G00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/LOwn2iCm34HtVuNmdbyewHZ8u9AXisABOEf8GLQwXFvxdT8E7OzxxxY-6ghjQt6MhH1Cf4zI6DX86KjrB8d01vMqHyl2NyB3uG2Yh9imiO6_Xk5JvKWUi09k-H-uYpxQyezfPKB36Ij1a6gBqdGRJpFDxkMQ3brtEKDFdDh1Dm00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/JOun3i8m34NtdCBAtWLsr0eOa1Y039tTn5H8RHB5ZXXGxuuL5WOFzdlV-ZqB5gdhOkGb2y4mEhZ4Pq6MKhtKGiOlgOO6FWOWfa1WpyUTQfgDdcox0_YqvXGf2jYH9XXoje0CRvemPpKsdO224x9-U9mSt1BBNCZThyqiWLLXIGLd0hStc_c5eUiEZVwjYdkAGPj_0G00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/VP312i9034Jl-nLXxptK3v1AyI2ALZruJhj15zjisKsX8FrtjwrGzE0ba7d3P4WM1BrqJQt4IasGEnQqJ1vEldfG48zY7IjsXa3lkv8yar20lEw2aDVmKW0pFOupdHM0oZMjOs81lIbsK3YZ0GDWQzDVVdF-6I-EbeY6xy3Ldy19DoXOOeZ-2naRbfX1BMZRnxACTQH1xfwkvyDKXtenfHfBGPAiFsj6RE9BtW00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEpot8pqlDAr5m3F3aIaaiIKnAB4vLS84oaEIT4vCpKhc0gXHqTUqG2c02O6a5AuMYrCIKOh2edXv26L0YiRWoBvdB8JKl1MWl0000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEpot8pqlDAr5G2aujAaijKd1KmYBefCG5OSKxAkZgAa3PJWfM2aMf1JcPoOabcVbvN0wfUIb0Gm40)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LV39JqnHS4hCISnBpinBvqhEpot8pqlDAr5GGf99BL92bWbEBIfBBL8mn2PeX4tGM8aBP5eyp3G5NLqx1OXSl25kAIFSKiPS3gbvAK1l0000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEpot8pqlDAr48Jqr2uZa6U7Ab99Oa9YKMfoguG1bSG3KAkhefkdPWUI26yk0A75BpKe360W00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKhEpot8pqlDAr5m3F1KKFR9JCyeSSefJULAIIn9J4eiJbLmWJ4Wakv5gQbvN235khhHoab0fR6wTd15N0wfUIb0Sm40)



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
![Diagram](https://www.plantuml.com/plantuml/svg/HOun3i8m40Hxls8_a0-aG46YeOlumSM-m4dsEJeVIFm-1WNHRJ4xkrDpCd-M768jMrLMntc-XaHE2pN6vGX1gpDCxWz7NJ_CYDcaaBqXsYqQ3oRp-aL-pH4tfWJZBKka1dgHP5eoXox1C9p-6nDhwbzs)



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
![Diagram](https://www.plantuml.com/plantuml/svg/PP91Rm8X48Nl_8h9tlVarHYtgqsQc6PNqdeq21DBYh1bm1uQ_tk1xMgq1yBZyIrlyh9B2iA7U38iw60GEkzKb44x2sjxrjxP4zh0X0pEmnkX9oQDYmggDc_F2GZGhbuh9jrfS3R1q6oUO3utJgZw88om4lrYCNtMx3YyTsq5Fmp0EeN96WRWyM0nZExahriEhOaKq4yN0BUOgkbUWAC_QuaL208nwF_GplbFz7VSTx4AUc7Z6WDN8eY7ILIo3eBIvNR5eNCKZXvvloaFUKKFqDe82heLyWDXYqhJo6LLaYwCKf7Yc50-WuO80rNiAsBCJi-Xpx9YfMcewmNSQjwdcjdziH2fRfOhppfNa5RHURghBXDC9pxRZz4tf-Vx4iskglX_LOtRzTKbMfL-cLy0)



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
