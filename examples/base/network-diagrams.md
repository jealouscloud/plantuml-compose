# Network Diagrams

Network diagrams (nwdiag) visualize the arrangement and interconnections of network infrastructure. They're excellent for:

- **Infrastructure documentation**: Map servers, networks, and connections
- **Network topology**: Show how devices connect across network segments
- **Cloud architecture**: Visualize VPCs, subnets, and services
- **Data center layout**: Document physical and logical network structure

A network diagram shows horizontal network bars with devices (nodes) connected to them. A device can appear on multiple networks, showing how it bridges different segments.

## Core Concepts

**Network**: A horizontal bar representing a network segment (like a VLAN, subnet, or LAN). Has an address range and can contain multiple nodes.

**Node**: A device on the network (server, database, router, etc.). Can have an IP address, shape, description, and color.

**Multi-homed node**: A node that appears on multiple networks, showing it has interfaces on each segment.

**Standalone node**: A node defined outside any network, useful for external elements like "internet" or "cloud".

**Peer link**: A direct connection between two nodes, bypassing network segments.

**Group**: A visual box around related nodes to show they belong together.

## Your First Network Diagram

```python
from plantuml_compose import network_diagram

with network_diagram(title="Simple Network") as d:
    with d.network("office", address="192.168.1.0/24") as office:
        office.node("server", address="192.168.1.10")
        office.node("workstation", address="192.168.1.100")

print(d.render())
```

This creates a network with two devices connected to it.

## Building Network Topologies

### Single Network with Multiple Nodes

```python
from plantuml_compose import network_diagram

with network_diagram() as d:
    with d.network("lan", address="10.0.0.0/24") as lan:
        lan.node("router", address="10.0.0.1")
        lan.node("server1", address="10.0.0.10")
        lan.node("server2", address="10.0.0.11")
        lan.node("printer", address="10.0.0.50")

print(d.render())
```

### Multiple Networks

```python
from plantuml_compose import network_diagram

with network_diagram(title="Office Network") as d:
    with d.network("dmz", address="10.0.1.0/24") as dmz:
        dmz.node("firewall", address="10.0.1.1")
        dmz.node("webserver", address="10.0.1.10")

    with d.network("internal", address="10.0.2.0/24") as internal:
        internal.node("appserver", address="10.0.2.10")
        internal.node("database", address="10.0.2.20")

print(d.render())
```

### Multi-Homed Nodes (Bridging Networks)

A node can appear on multiple networks by using the same name. This shows the device has interfaces on multiple network segments:

```python
from plantuml_compose import network_diagram

with network_diagram(title="Multi-Homed Server") as d:
    with d.network("public", address="203.0.113.0/24") as public:
        public.node("loadbalancer", address="203.0.113.10")

    with d.network("private", address="10.0.0.0/24") as private:
        # Same node name = same device, different interface
        private.node("loadbalancer", address="10.0.0.1")
        private.node("web1", address="10.0.0.10")
        private.node("web2", address="10.0.0.11")

print(d.render())
```

The `loadbalancer` appears on both networks, showing it bridges public and private segments.

## Node Attributes

### Node Shapes

Nodes can have different visual shapes to indicate their role:

```python
from plantuml_compose import network_diagram

with network_diagram(title="Node Shapes") as d:
    with d.network("infrastructure") as infra:
        infra.node("web", shape="node", description="Web Server")
        infra.node("db", shape="database", description="Database")
        infra.node("files", shape="storage", description="File Storage")
        infra.node("queue", shape="queue", description="Message Queue")

print(d.render())
```

Available shapes include: `node`, `database`, `storage`, `queue`, `cloud`, `folder`, `frame`, `component`, `package`, `actor`, `person`, `hexagon`, `card`, `file`, `artifact`, `collections`, `rectangle`, `usecase`, `label`, `agent`, `boundary`, `control`, `entity`, `interface`, `stack`.

### Node Descriptions

Add labels to describe what each node does:

```python
from plantuml_compose import network_diagram

with network_diagram() as d:
    with d.network("production", address="10.0.0.0/24") as prod:
        prod.node("app01", address="10.0.0.10", description="Primary App Server")
        prod.node("app02", address="10.0.0.11", description="Backup App Server")
        prod.node("db01", address="10.0.0.20", description="PostgreSQL Primary")

print(d.render())
```

### Node Colors

Highlight nodes with background colors:

```python
from plantuml_compose import network_diagram

with network_diagram(title="Server Status") as d:
    with d.network("cluster", address="10.0.0.0/24") as cluster:
        cluster.node("active", address="10.0.0.1", color="#90EE90", description="Active")
        cluster.node("standby", address="10.0.0.2", color="#FFE4B5", description="Standby")
        cluster.node("offline", address="10.0.0.3", color="#FFB6C1", description="Offline")

print(d.render())
```

### Combined Attributes

```python
from plantuml_compose import network_diagram

with network_diagram() as d:
    with d.network("backend", address="172.16.0.0/24") as backend:
        backend.node(
            "postgres",
            address="172.16.0.10",
            shape="database",
            description="PostgreSQL 15",
            color="#336791"
        )
        backend.node(
            "redis",
            address="172.16.0.20",
            shape="storage",
            description="Redis Cache",
            color="#DC382D"
        )

print(d.render())
```

## Network Descriptions

Networks can have descriptions that appear on the network bar:

```python
from plantuml_compose import network_diagram

with network_diagram(title="Data Center") as d:
    with d.network("dmz", address="10.0.1.0/24", description="DMZ Network") as dmz:
        dmz.node("fw", address="10.0.1.1", description="Firewall")
        dmz.node("lb", address="10.0.1.10", description="Load Balancer")

    with d.network("app", address="10.0.2.0/24", description="Application Tier") as app:
        app.node("web1", address="10.0.2.10")
        app.node("web2", address="10.0.2.11")

    with d.network("data", address="10.0.3.0/24", description="Data Tier") as data:
        data.node("db1", address="10.0.3.10", shape="database")

print(d.render())
```

## Network Colors

Color-code networks to visually distinguish them:

```python
from plantuml_compose import network_diagram

with network_diagram(title="Network Zones") as d:
    with d.network("untrusted", address="0.0.0.0/0", color="#FFCDD2", description="Untrusted") as ext:
        ext.node("internet", shape="cloud")

    with d.network("dmz", address="10.0.1.0/24", color="#FFF9C4", description="DMZ") as dmz:
        dmz.node("proxy", address="10.0.1.10")

    with d.network("trusted", address="10.0.2.0/24", color="#C8E6C9", description="Trusted") as trusted:
        trusted.node("app", address="10.0.2.10")
        trusted.node("db", address="10.0.2.20", shape="database")

print(d.render())
```

## Standalone Nodes and Peer Links

### Standalone Nodes

Create nodes that exist outside any network segment, like the internet or cloud services:

```python
from plantuml_compose import network_diagram

with network_diagram() as d:
    # Standalone node for external entity
    internet = d.node("internet", shape="cloud", description="Public Internet")

    with d.network("dmz", address="10.0.1.0/24") as dmz:
        dmz.node("firewall", address="10.0.1.1")
        dmz.node("web", address="10.0.1.10")

print(d.render())
```

### Peer Links

Connect nodes directly without going through a network segment:

```python
from plantuml_compose import network_diagram

with network_diagram(title="Internet Connection") as d:
    internet = d.node("internet", shape="cloud", description="Internet")

    with d.network("edge", address="203.0.113.0/24") as edge:
        edge.node("router", address="203.0.113.1", description="Edge Router")
        edge.node("firewall", address="203.0.113.2", description="Firewall")

    # Direct connection from internet to router
    d.link(internet, "router")

print(d.render())
```

### Multiple Peer Links

```python
from plantuml_compose import network_diagram

with network_diagram(title="Redundant Connections") as d:
    isp1 = d.node("ISP_A", shape="cloud", description="ISP Alpha")
    isp2 = d.node("ISP_B", shape="cloud", description="ISP Beta")

    with d.network("edge", address="10.0.0.0/24") as edge:
        edge.node("router1", address="10.0.0.1", description="Primary Router")
        edge.node("router2", address="10.0.0.2", description="Backup Router")

    d.link(isp1, "router1")
    d.link(isp2, "router2")

print(d.render())
```

## Groups

Visually group related nodes together:

### Basic Grouping

```python
from plantuml_compose import network_diagram

with network_diagram() as d:
    with d.network("cluster", address="10.0.0.0/24") as cluster:
        cluster.node("web1", address="10.0.0.10")
        cluster.node("web2", address="10.0.0.11")
        cluster.node("web3", address="10.0.0.12")
        cluster.node("db1", address="10.0.0.20", shape="database")

    # Group the web servers
    d.group("web1", "web2", "web3", description="Web Tier")

print(d.render())
```

### Colored Groups

```python
from plantuml_compose import network_diagram

with network_diagram(title="Service Groups") as d:
    with d.network("production", address="10.0.0.0/24") as prod:
        prod.node("app1", address="10.0.0.10")
        prod.node("app2", address="10.0.0.11")
        prod.node("cache1", address="10.0.0.20")
        prod.node("cache2", address="10.0.0.21")
        prod.node("db1", address="10.0.0.30", shape="database")
        prod.node("db2", address="10.0.0.31", shape="database")

    d.group("app1", "app2", color="#E3F2FD", description="Application Servers")
    d.group("cache1", "cache2", color="#FFF3E0", description="Cache Layer")
    d.group("db1", "db2", color="#E8F5E9", description="Database Cluster")

print(d.render())
```

### Groups with Node References

You can use the node references returned by `node()` calls:

```python
from plantuml_compose import network_diagram

with network_diagram() as d:
    with d.network("lan", address="10.0.0.0/24") as lan:
        w1 = lan.node("web1", address="10.0.0.10")
        w2 = lan.node("web2", address="10.0.0.11")
        db = lan.node("db", address="10.0.0.20", shape="database")

    # Group using references
    d.group(w1, w2, color="#BBDEFB", description="Web Servers")

print(d.render())
```

## Full-Width Networks

Force a network to span the full width of the diagram:

```python
from plantuml_compose import network_diagram

with network_diagram(title="Backbone Network") as d:
    with d.network("backbone", address="10.0.0.0/8", width="full", color="#E0E0E0") as backbone:
        backbone.node("core_switch", description="Core Switch")

    with d.network("vlan10", address="10.10.0.0/16") as vlan10:
        vlan10.node("core_switch")
        vlan10.node("server1", address="10.10.0.10")
        vlan10.node("server2", address="10.10.0.11")

    with d.network("vlan20", address="10.20.0.0/16") as vlan20:
        vlan20.node("core_switch")
        vlan20.node("workstation1", address="10.20.0.100")
        vlan20.node("workstation2", address="10.20.0.101")

print(d.render())
```

## Diagram Styling

Apply CSS-style themes to the entire diagram.

### Basic Styling

```python
from plantuml_compose import network_diagram

with network_diagram(
    title="Styled Network",
    diagram_style={
        "background": "white",
        "font_name": "Arial",
    }
) as d:
    with d.network("lan", address="10.0.0.0/24") as lan:
        lan.node("server", address="10.0.0.10")
        lan.node("client", address="10.0.0.100")

print(d.render())
```

### Network Bar Styling

Style all network bars:

```python
from plantuml_compose import network_diagram

with network_diagram(
    title="Custom Network Bars",
    diagram_style={
        "network": {
            "background": "#E3F2FD",
            "line_color": "#1976D2",
            "font_color": "#0D47A1",
        }
    }
) as d:
    with d.network("primary", address="10.0.0.0/24") as primary:
        primary.node("server1")
    with d.network("secondary", address="10.0.1.0/24") as secondary:
        secondary.node("server2")

print(d.render())
```

### Server/Node Styling

Style all nodes (called "server" in nwdiag):

```python
from plantuml_compose import network_diagram

with network_diagram(
    title="Custom Nodes",
    diagram_style={
        "server": {
            "background": "#FFF3E0",
            "line_color": "#E65100",
        }
    }
) as d:
    with d.network("lan") as lan:
        lan.node("app1", description="App Server 1")
        lan.node("app2", description="App Server 2")
        lan.node("db", shape="database", description="Database")

print(d.render())
```

### Group Styling

Style all groups:

```python
from plantuml_compose import network_diagram

with network_diagram(
    title="Styled Groups",
    diagram_style={
        "group": {
            "background": "#E8F5E9",
            "line_color": "#2E7D32",
        }
    }
) as d:
    with d.network("cluster", address="10.0.0.0/24") as cluster:
        cluster.node("node1")
        cluster.node("node2")
        cluster.node("node3")

    d.group("node1", "node2", description="Group A")

print(d.render())
```

### Combined Styling

```python
from plantuml_compose import network_diagram, NetworkDiagramStyle
from plantuml_compose.primitives.common import ElementStyle

with network_diagram(
    title="Fully Styled Diagram",
    diagram_style=NetworkDiagramStyle(
        background="#FAFAFA",
        network=ElementStyle(
            background="#E3F2FD",
            line_color="#1565C0",
        ),
        server=ElementStyle(
            background="#FFFFFF",
            line_color="#424242",
        ),
        group=ElementStyle(
            background="#F3E5F5",
            line_color="#7B1FA2",
        ),
    )
) as d:
    with d.network("production", address="10.0.0.0/24") as prod:
        prod.node("web1", address="10.0.0.10")
        prod.node("web2", address="10.0.0.11")
        prod.node("db", address="10.0.0.20", shape="database")

    d.group("web1", "web2", description="Web Tier")

print(d.render())
```

## Complete Examples

### Three-Tier Architecture

```python
from plantuml_compose import network_diagram

with network_diagram(title="Three-Tier Web Application") as d:
    internet = d.node("internet", shape="cloud", description="Internet")

    with d.network("dmz", address="10.0.1.0/24", description="DMZ", color="#FFECB3") as dmz:
        dmz.node("lb", address="10.0.1.10", description="Load Balancer")

    with d.network("app_tier", address="10.0.2.0/24", description="Application Tier", color="#C8E6C9") as app:
        app.node("lb", address="10.0.2.1")
        app.node("app1", address="10.0.2.10", description="App Server 1")
        app.node("app2", address="10.0.2.11", description="App Server 2")
        app.node("app3", address="10.0.2.12", description="App Server 3")

    with d.network("data_tier", address="10.0.3.0/24", description="Data Tier", color="#BBDEFB") as data:
        data.node("app1", address="10.0.3.10")
        data.node("app2", address="10.0.3.11")
        data.node("app3", address="10.0.3.12")
        data.node("db_primary", address="10.0.3.20", shape="database", description="Primary DB")
        data.node("db_replica", address="10.0.3.21", shape="database", description="Replica DB")

    d.link(internet, "lb")
    d.group("app1", "app2", "app3", color="#E8F5E9", description="App Cluster")
    d.group("db_primary", "db_replica", color="#E3F2FD", description="Database Cluster")

print(d.render())
```

### AWS VPC Architecture

```python
from plantuml_compose import network_diagram

with network_diagram(title="AWS VPC Architecture") as d:
    inet = d.node("internet", shape="cloud", description="Internet")

    with d.network("public_a", address="10.0.1.0/24", description="Public Subnet A") as pub_a:
        pub_a.node("nat_a", description="NAT Gateway")
        pub_a.node("alb", description="Application LB")

    with d.network("public_b", address="10.0.2.0/24", description="Public Subnet B") as pub_b:
        pub_b.node("nat_b", description="NAT Gateway")
        pub_b.node("alb")

    with d.network("private_a", address="10.0.10.0/24", description="Private Subnet A") as priv_a:
        priv_a.node("ecs_a", description="ECS Tasks")

    with d.network("private_b", address="10.0.20.0/24", description="Private Subnet B") as priv_b:
        priv_b.node("ecs_b", description="ECS Tasks")

    with d.network("data_a", address="10.0.100.0/24", description="Data Subnet A") as data_a:
        data_a.node("rds_primary", shape="database", description="RDS Primary")

    with d.network("data_b", address="10.0.200.0/24", description="Data Subnet B") as data_b:
        data_b.node("rds_standby", shape="database", description="RDS Standby")

    d.link(inet, "alb")

print(d.render())
```

### Home Network

```python
from plantuml_compose import network_diagram

with network_diagram(title="Home Network") as d:
    isp = d.node("ISP", shape="cloud", description="Internet Service Provider")

    with d.network("wan", description="WAN Connection") as wan:
        wan.node("modem", description="Cable Modem")

    with d.network("lan", address="192.168.1.0/24", description="Home LAN") as lan:
        lan.node("modem")
        lan.node("router", address="192.168.1.1", description="WiFi Router")
        lan.node("nas", address="192.168.1.10", shape="storage", description="NAS")
        lan.node("desktop", address="192.168.1.100", description="Desktop PC")
        lan.node("laptop", address="192.168.1.101", description="Laptop")
        lan.node("printer", address="192.168.1.200", description="Printer")

    d.link(isp, "modem")
    d.group("desktop", "laptop", color="#E3F2FD", description="Computers")

print(d.render())
```

### Kubernetes Cluster

```python
from plantuml_compose import network_diagram

with network_diagram(
    title="Kubernetes Cluster",
    diagram_style={
        "network": {"background": "#E8EAF6"},
        "server": {"background": "#FFFFFF"},
    }
) as d:
    with d.network("control_plane", address="10.0.0.0/24", description="Control Plane") as cp:
        cp.node("master1", address="10.0.0.10", description="Master 1")
        cp.node("master2", address="10.0.0.11", description="Master 2")
        cp.node("master3", address="10.0.0.12", description="Master 3")
        cp.node("etcd", address="10.0.0.20", shape="database", description="etcd")

    with d.network("worker_net", address="10.0.1.0/24", description="Worker Network") as workers:
        workers.node("worker1", address="10.0.1.10", description="Worker 1")
        workers.node("worker2", address="10.0.1.11", description="Worker 2")
        workers.node("worker3", address="10.0.1.12", description="Worker 3")
        workers.node("worker4", address="10.0.1.13", description="Worker 4")

    d.group("master1", "master2", "master3", color="#C8E6C9", description="HA Masters")
    d.group("worker1", "worker2", "worker3", "worker4", color="#BBDEFB", description="Worker Pool")

print(d.render())
```

## Quick Reference

### Diagram Creation

| Code | Description |
|------|-------------|
| `network_diagram()` | Create a network diagram |
| `title="..."` | Diagram title |
| `diagram_style={...}` | Apply CSS styling |

### Network Methods

| Method | Description |
|--------|-------------|
| `d.network(name)` | Create network (use as context manager) |
| `d.node(name)` | Create standalone node |
| `d.link(src, dst)` | Create peer link between nodes |
| `d.group(*nodes)` | Group nodes visually |

### Network Parameters

| Parameter | Description |
|-----------|-------------|
| `name` | Network name (required) |
| `address` | Network address (e.g., "10.0.0.0/24") |
| `description` | Label on network bar |
| `color` | Background color |
| `width="full"` | Span full diagram width |

### Node Parameters

| Parameter | Description |
|-----------|-------------|
| `name` | Node identifier (required) |
| `address` | IP address |
| `shape` | Visual shape (database, cloud, etc.) |
| `description` | Label on node |
| `color` | Background color |

### Group Parameters

| Parameter | Description |
|-----------|-------------|
| `*nodes` | Node names or refs to include |
| `color` | Background color |
| `description` | Group label |

### Diagram Style Keys

| Key | Description |
|-----|-------------|
| `background` | Diagram background color |
| `font_name` | Default font |
| `font_size` | Default font size |
| `font_color` | Default text color |
| `network` | Style for network bars |
| `server` | Style for nodes |
| `group` | Style for groups |
| `arrow` | Style for address labels |

### Element Style Keys

| Key | Description |
|-----|-------------|
| `background` | Fill color |
| `font_color` | Text color |
| `line_color` | Border color |
| `line_thickness` | Border width |

### Common Node Shapes

| Shape | Description |
|-------|-------------|
| `node` | Default rectangle |
| `database` | Cylinder (database) |
| `storage` | Storage device |
| `cloud` | Cloud shape |
| `queue` | Message queue |
| `folder` | Folder icon |
| `component` | Component box |
| `actor` | Stick figure |
| `person` | Person icon |
