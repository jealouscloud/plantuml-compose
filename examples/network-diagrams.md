# Network Diagrams

Network diagrams (nwdiag) visualize the arrangement and interconnections of network infrastructure. They're excellent for:

- **Infrastructure documentation**: Map servers, networks, and connections
- **Network topology**: Show how devices connect across network segments
- **Cloud architecture**: Visualize VPCs, subnets, and services
- **Data center layout**: Document physical and logical network structure

## Core Concepts

**Network**: A horizontal bar representing a network segment (like a VLAN, subnet, or LAN). Has an address range and can contain multiple nodes.

**Node**: A device on the network (server, database, router, etc.). Can have an IP address, shape, description, and color.

**Multi-membership model**: A node that appears in multiple networks automatically shows connections between those network segments. This is how you express connectivity -- there are no explicit "connect node to network" calls.

**Standalone node**: A node defined outside any network via `d.add(n.node(...))`, useful for external elements like "internet" or "cloud".

**Peer link**: A direct connection between two nodes, bypassing network segments.

**Group**: A visual box around related nodes to show they belong together.

## Your First Network Diagram

```python
from plantuml_compose import network_diagram, render

d = network_diagram(title="Simple Network")
n = d.networks

d.add(
    n.network("office", address="192.168.1.0/24",
        n.node("server", address="192.168.1.10"),
        n.node("workstation", address="192.168.1.100"),
    ),
)

print(render(d))
```

This creates a network with two devices connected to it.

## The Multi-Membership Model

The fundamental pattern in network diagrams: **placing the same node name in multiple networks IS the connection model**. There is no separate "connect" call for nodes to networks.

### Single Network with Multiple Nodes

```python
from plantuml_compose import network_diagram, render

d = network_diagram()
n = d.networks

d.add(
    n.network("lan", address="10.0.0.0/24",
        n.node("router", address="10.0.0.1"),
        n.node("server1", address="10.0.0.10"),
        n.node("server2", address="10.0.0.11"),
        n.node("printer", address="10.0.0.50"),
    ),
)

print(render(d))
```

### Multi-Homed Nodes (Bridging Networks)

A node can appear on multiple networks by using the same name. This shows the device has interfaces on multiple network segments:

```python
from plantuml_compose import network_diagram, render

d = network_diagram(title="Multi-Homed Server")
n = d.networks

d.add(
    n.network("public", address="203.0.113.0/24",
        n.node("loadbalancer", address="203.0.113.10"),
    ),
    n.network("private", address="10.0.0.0/24",
        # Same node name = same device, different interface
        n.node("loadbalancer", address="10.0.0.1"),
        n.node("web1", address="10.0.0.10"),
        n.node("web2", address="10.0.0.11"),
    ),
)

print(render(d))
```

The `loadbalancer` appears on both networks, showing it bridges public and private segments. Each occurrence can have its own address for that interface.

### Multiple Networks

```python
from plantuml_compose import network_diagram, render

d = network_diagram(title="Office Network")
n = d.networks

d.add(
    n.network("dmz", address="10.0.1.0/24",
        n.node("firewall", address="10.0.1.1"),
        n.node("webserver", address="10.0.1.10"),
    ),
    n.network("internal", address="10.0.2.0/24",
        n.node("appserver", address="10.0.2.10"),
        n.node("database", address="10.0.2.20"),
    ),
)

print(render(d))
```

## Standalone Nodes

Create nodes outside any network with `d.add(n.node(...))`. These are useful for external entities like the internet or cloud services:

```python
from plantuml_compose import network_diagram, render

d = network_diagram()
n = d.networks

# Standalone node for external entity
d.add(n.node("internet", shape="cloud", description="Public Internet"))

d.add(
    n.network("dmz", address="10.0.1.0/24",
        n.node("firewall", address="10.0.1.1"),
        n.node("web", address="10.0.1.10"),
    ),
)

print(render(d))
```

Standalone nodes accept all the same parameters as network-interior nodes: `shape`, `address`, `description`, and `color`.

## Node Attributes

### Node Shapes

Nodes can have different visual shapes to indicate their role:

```python
from plantuml_compose import network_diagram, render

d = network_diagram(title="Node Shapes")
n = d.networks

d.add(
    n.network("infrastructure",
        n.node("web", shape="node", description="Web Server"),
        n.node("db", shape="database", description="Database"),
        n.node("files", shape="storage", description="File Storage"),
        n.node("queue", shape="queue", description="Message Queue"),
    ),
)

print(render(d))
```

All available shapes:

| Shape | Shape | Shape |
|-------|-------|-------|
| `node` (default) | `database` | `storage` |
| `cloud` | `queue` | `folder` |
| `frame` | `component` | `package` |
| `actor` | `person` | `agent` |
| `boundary` | `control` | `entity` |
| `interface` | `artifact` | `collections` |
| `card` | `file` | `hexagon` |
| `rectangle` | `usecase` | `label` |
| `stack` | | |

### Node Descriptions

Add labels to describe what each node does:

```python
from plantuml_compose import network_diagram, render

d = network_diagram()
n = d.networks

d.add(
    n.network("production", address="10.0.0.0/24",
        n.node("app01", address="10.0.0.10", description="Primary App Server"),
        n.node("app02", address="10.0.0.11", description="Backup App Server"),
        n.node("db01", address="10.0.0.20", description="PostgreSQL Primary"),
    ),
)

print(render(d))
```

### Node Colors

Highlight nodes with background colors:

```python
from plantuml_compose import network_diagram, render

d = network_diagram(title="Server Status")
n = d.networks

d.add(
    n.network("cluster", address="10.0.0.0/24",
        n.node("active", address="10.0.0.1", color="#90EE90", description="Active"),
        n.node("standby", address="10.0.0.2", color="#FFE4B5", description="Standby"),
        n.node("offline", address="10.0.0.3", color="#FFB6C1", description="Offline"),
    ),
)

print(render(d))
```

### Combined Attributes

```python
from plantuml_compose import network_diagram, render

d = network_diagram()
n = d.networks

d.add(
    n.network("backend", address="172.16.0.0/24",
        n.node(
            "postgres",
            address="172.16.0.10",
            shape="database",
            description="PostgreSQL 15",
            color="#336791",
        ),
        n.node(
            "redis",
            address="172.16.0.20",
            shape="storage",
            description="Redis Cache",
            color="#DC382D",
        ),
    ),
)

print(render(d))
```

## Network Properties

### Network Descriptions

Networks can have descriptions that appear on the network bar:

```python
from plantuml_compose import network_diagram, render

d = network_diagram(title="Data Center")
n = d.networks

d.add(
    n.network("dmz", address="10.0.1.0/24", description="DMZ Network",
        n.node("fw", address="10.0.1.1", description="Firewall"),
        n.node("lb", address="10.0.1.10", description="Load Balancer"),
    ),
    n.network("app", address="10.0.2.0/24", description="Application Tier",
        n.node("web1", address="10.0.2.10"),
        n.node("web2", address="10.0.2.11"),
    ),
    n.network("data", address="10.0.3.0/24", description="Data Tier",
        n.node("db1", address="10.0.3.10", shape="database"),
    ),
)

print(render(d))
```

### Network Colors

Color-code networks to visually distinguish them:

```python
from plantuml_compose import network_diagram, render

d = network_diagram(title="Network Zones")
n = d.networks

d.add(
    n.network("untrusted", address="0.0.0.0/0", color="#FFCDD2", description="Untrusted",
        n.node("internet", shape="cloud"),
    ),
    n.network("dmz", address="10.0.1.0/24", color="#FFF9C4", description="DMZ",
        n.node("proxy", address="10.0.1.10"),
    ),
    n.network("trusted", address="10.0.2.0/24", color="#C8E6C9", description="Trusted",
        n.node("app", address="10.0.2.10"),
        n.node("db", address="10.0.2.20", shape="database"),
    ),
)

print(render(d))
```

### Full-Width Networks

Force a network to span the full width of the diagram with `width="full"`:

```python
from plantuml_compose import network_diagram, render

d = network_diagram(title="Backbone Network")
n = d.networks

d.add(
    n.network("backbone", address="10.0.0.0/8", width="full", color="#E0E0E0",
        n.node("core_switch", description="Core Switch"),
    ),
    n.network("vlan10", address="10.10.0.0/16",
        n.node("core_switch"),
        n.node("server1", address="10.10.0.10"),
        n.node("server2", address="10.10.0.11"),
    ),
    n.network("vlan20", address="10.20.0.0/16",
        n.node("core_switch"),
        n.node("workstation1", address="10.20.0.100"),
        n.node("workstation2", address="10.20.0.101"),
    ),
)

print(render(d))
```

### Anonymous Networks

Pass `name=None` (or `name=""`) to create an unnamed network. This is useful for simple connectivity without labeling:

```python
from plantuml_compose import network_diagram, render

d = network_diagram()
n = d.networks

d.add(
    n.network("dmz", address="10.0.1.0/24",
        n.node("firewall"),
        n.node("web"),
    ),
    n.network(name=None,
        n.node("web"),
        n.node("app"),
    ),
    n.network("internal", address="10.0.2.0/24",
        n.node("app"),
        n.node("db", shape="database"),
    ),
)

print(render(d))
```

The anonymous network connects `web` and `app` without showing a named bar.

## Peer Links

Connect nodes directly without going through a network segment using `d.link()`:

```python
from plantuml_compose import network_diagram, render

d = network_diagram(title="Internet Connection")
n = d.networks

d.add(n.node("internet", shape="cloud", description="Internet"))

d.add(
    n.network("edge", address="203.0.113.0/24",
        n.node("router", address="203.0.113.1", description="Edge Router"),
        n.node("firewall", address="203.0.113.2", description="Firewall"),
    ),
)

# Direct connection from internet to router
d.link("internet", "router")

print(render(d))
```

### Multiple Peer Links

```python
from plantuml_compose import network_diagram, render

d = network_diagram(title="Redundant Connections")
n = d.networks

d.add(
    n.node("ISP_A", shape="cloud", description="ISP Alpha"),
    n.node("ISP_B", shape="cloud", description="ISP Beta"),
)

d.add(
    n.network("edge", address="10.0.0.0/24",
        n.node("router1", address="10.0.0.1", description="Primary Router"),
        n.node("router2", address="10.0.0.2", description="Backup Router"),
    ),
)

d.link("ISP_A", "router1")
d.link("ISP_B", "router2")

print(render(d))
```

## Groups

Visually group related nodes together:

### Basic Grouping

```python
from plantuml_compose import network_diagram, render

d = network_diagram()
n = d.networks

d.add(
    n.network("cluster", address="10.0.0.0/24",
        n.node("web1", address="10.0.0.10"),
        n.node("web2", address="10.0.0.11"),
        n.node("web3", address="10.0.0.12"),
        n.node("db1", address="10.0.0.20", shape="database"),
    ),
)

# Group the web servers
d.add(n.group("web1", "web2", "web3", description="Web Tier"))

print(render(d))
```

### Colored Groups with Descriptions

```python
from plantuml_compose import network_diagram, render

d = network_diagram(title="Service Groups")
n = d.networks

d.add(
    n.network("production", address="10.0.0.0/24",
        n.node("app1", address="10.0.0.10"),
        n.node("app2", address="10.0.0.11"),
        n.node("cache1", address="10.0.0.20"),
        n.node("cache2", address="10.0.0.21"),
        n.node("db1", address="10.0.0.30", shape="database"),
        n.node("db2", address="10.0.0.31", shape="database"),
    ),
)

d.add(
    n.group("app1", "app2", color="#E3F2FD", description="Application Servers"),
    n.group("cache1", "cache2", color="#FFF3E0", description="Cache Layer"),
    n.group("db1", "db2", color="#E8F5E9", description="Database Cluster"),
)

print(render(d))
```

## Diagram Metadata

Network diagrams support title, mainframe, header, footer, legend, and caption:

```python
from plantuml_compose import network_diagram, render
from plantuml_compose.primitives.common import Header, Footer, Legend

d = network_diagram(
    title="Production Infrastructure",
    mainframe="DC-East",
    caption="Last updated 2025-03",
    header=Header(content="CONFIDENTIAL"),
    footer=Footer(content="Page 1"),
    legend=Legend(content="Green = Active\\nRed = Standby", position="right"),
)
n = d.networks

d.add(
    n.network("lan", address="10.0.0.0/24",
        n.node("server", address="10.0.0.10"),
    ),
)

print(render(d))
```

## Styling with diagram_style

Apply CSS-style themes to the entire diagram. The `diagram_style=` parameter accepts a dict with these selectors:

- **Top-level**: `background`, `font_name`, `font_size`, `font_color`
- **`network`**: Style for network bars
- **`server`**: Style for nodes (nwdiag calls them "servers")
- **`group`**: Style for group boxes
- **`arrow`**: Style for address labels and connectors
- **`stereotypes`**: Style by stereotype name

### Basic Styling

```python
from plantuml_compose import network_diagram, render

d = network_diagram(
    title="Styled Network",
    diagram_style={
        "background": "white",
        "font_name": "Arial",
    },
)
n = d.networks

d.add(
    n.network("lan", address="10.0.0.0/24",
        n.node("server", address="10.0.0.10"),
        n.node("client", address="10.0.0.100"),
    ),
)

print(render(d))
```

### Network Bar Styling

```python
from plantuml_compose import network_diagram, render

d = network_diagram(
    title="Custom Network Bars",
    diagram_style={
        "network": {
            "background": "#E3F2FD",
            "line_color": "#1976D2",
            "font_color": "#0D47A1",
        }
    },
)
n = d.networks

d.add(
    n.network("primary", address="10.0.0.0/24",
        n.node("server1"),
    ),
    n.network("secondary", address="10.0.1.0/24",
        n.node("server2"),
    ),
)

print(render(d))
```

### Server/Node Styling

Style all nodes (called "server" in nwdiag CSS):

```python
from plantuml_compose import network_diagram, render

d = network_diagram(
    title="Custom Nodes",
    diagram_style={
        "server": {
            "background": "#FFF3E0",
            "line_color": "#E65100",
        }
    },
)
n = d.networks

d.add(
    n.network("lan",
        n.node("app1", description="App Server 1"),
        n.node("app2", description="App Server 2"),
        n.node("db", shape="database", description="Database"),
    ),
)

print(render(d))
```

### Group Styling

```python
from plantuml_compose import network_diagram, render

d = network_diagram(
    title="Styled Groups",
    diagram_style={
        "group": {
            "background": "#E8F5E9",
            "line_color": "#2E7D32",
        }
    },
)
n = d.networks

d.add(
    n.network("cluster", address="10.0.0.0/24",
        n.node("node1"),
        n.node("node2"),
        n.node("node3"),
    ),
)

d.add(n.group("node1", "node2", description="Group A"))

print(render(d))
```

### Stereotype-Based Styling

Apply styles to nodes by stereotype name. This lets you style categories of nodes consistently:

```python
from plantuml_compose import network_diagram, render

d = network_diagram(
    title="Styled by Role",
    diagram_style={
        "background": "white",
        "network": {"background": "#E3F2FD"},
        "server": {"background": "#FFFFFF"},
        "stereotypes": {
            "firewall": {"background": "#FFCDD2", "line_color": "#C62828"},
            "database": {"background": "#E8F5E9", "line_color": "#2E7D32"},
        },
    },
)
n = d.networks

d.add(
    n.network("dmz", address="10.0.1.0/24",
        n.node("fw", description="Firewall"),
        n.node("web", description="Web Server"),
    ),
    n.network("internal", address="10.0.2.0/24",
        n.node("app", description="App Server"),
        n.node("db", shape="database", description="PostgreSQL"),
    ),
)

print(render(d))
```

### Combined Styling

```python
from plantuml_compose import network_diagram, render

d = network_diagram(
    title="Fully Styled Diagram",
    diagram_style={
        "background": "#FAFAFA",
        "network": {
            "background": "#E3F2FD",
            "line_color": "#1565C0",
        },
        "server": {
            "background": "#FFFFFF",
            "line_color": "#424242",
        },
        "group": {
            "background": "#F3E5F5",
            "line_color": "#7B1FA2",
        },
    },
)
n = d.networks

d.add(
    n.network("production", address="10.0.0.0/24",
        n.node("web1", address="10.0.0.10"),
        n.node("web2", address="10.0.0.11"),
        n.node("db", address="10.0.0.20", shape="database"),
    ),
)

d.add(n.group("web1", "web2", description="Web Tier"))

print(render(d))
```

## Complete Examples

### Three-Tier Architecture

```python
from plantuml_compose import network_diagram, render

d = network_diagram(title="Three-Tier Web Application")
n = d.networks

d.add(n.node("internet", shape="cloud", description="Internet"))

d.add(
    n.network("dmz", address="10.0.1.0/24", description="DMZ", color="#FFECB3",
        n.node("lb", address="10.0.1.10", description="Load Balancer"),
    ),
    n.network("app_tier", address="10.0.2.0/24", description="Application Tier", color="#C8E6C9",
        n.node("lb", address="10.0.2.1"),
        n.node("app1", address="10.0.2.10", description="App Server 1"),
        n.node("app2", address="10.0.2.11", description="App Server 2"),
        n.node("app3", address="10.0.2.12", description="App Server 3"),
    ),
    n.network("data_tier", address="10.0.3.0/24", description="Data Tier", color="#BBDEFB",
        n.node("app1", address="10.0.3.10"),
        n.node("app2", address="10.0.3.11"),
        n.node("app3", address="10.0.3.12"),
        n.node("db_primary", address="10.0.3.20", shape="database", description="Primary DB"),
        n.node("db_replica", address="10.0.3.21", shape="database", description="Replica DB"),
    ),
)

d.link("internet", "lb")
d.add(
    n.group("app1", "app2", "app3", color="#E8F5E9", description="App Cluster"),
    n.group("db_primary", "db_replica", color="#E3F2FD", description="Database Cluster"),
)

print(render(d))
```

### Kubernetes Cluster

```python
from plantuml_compose import network_diagram, render

d = network_diagram(
    title="Kubernetes Cluster",
    diagram_style={
        "network": {"background": "#E8EAF6"},
        "server": {"background": "#FFFFFF"},
    },
)
n = d.networks

d.add(
    n.network("control_plane", address="10.0.0.0/24", description="Control Plane",
        n.node("master1", address="10.0.0.10", description="Master 1"),
        n.node("master2", address="10.0.0.11", description="Master 2"),
        n.node("master3", address="10.0.0.12", description="Master 3"),
        n.node("etcd", address="10.0.0.20", shape="database", description="etcd"),
    ),
    n.network("worker_net", address="10.0.1.0/24", description="Worker Network",
        n.node("worker1", address="10.0.1.10", description="Worker 1"),
        n.node("worker2", address="10.0.1.11", description="Worker 2"),
        n.node("worker3", address="10.0.1.12", description="Worker 3"),
        n.node("worker4", address="10.0.1.13", description="Worker 4"),
    ),
)

d.add(
    n.group("master1", "master2", "master3", color="#C8E6C9", description="HA Masters"),
    n.group("worker1", "worker2", "worker3", "worker4", color="#BBDEFB", description="Worker Pool"),
)

print(render(d))
```

### Home Network

```python
from plantuml_compose import network_diagram, render

d = network_diagram(title="Home Network")
n = d.networks

d.add(n.node("ISP", shape="cloud", description="Internet Service Provider"))

d.add(
    n.network("wan", description="WAN Connection",
        n.node("modem", description="Cable Modem"),
    ),
    n.network("lan", address="192.168.1.0/24", description="Home LAN",
        n.node("modem"),
        n.node("router", address="192.168.1.1", description="WiFi Router"),
        n.node("nas", address="192.168.1.10", shape="storage", description="NAS"),
        n.node("desktop", address="192.168.1.100", description="Desktop PC"),
        n.node("laptop", address="192.168.1.101", description="Laptop"),
        n.node("printer", address="192.168.1.200", description="Printer"),
    ),
)

d.link("ISP", "modem")
d.add(n.group("desktop", "laptop", color="#E3F2FD", description="Computers"))

print(render(d))
```

## Quick Reference

### Diagram Creation

| Code | Description |
|------|-------------|
| `network_diagram()` | Create a network diagram |
| `title="..."` | Diagram title |
| `mainframe="..."` | Mainframe label |
| `caption="..."` | Caption below diagram |
| `header=...` | Header (str or Header object) |
| `footer=...` | Footer (str or Footer object) |
| `legend=...` | Legend (str or Legend object) |
| `diagram_style={...}` | Apply CSS styling |

### Network Methods

| Method | Description |
|--------|-------------|
| `n.network(name, *nodes)` | Create network with nodes |
| `n.network(name=None, *nodes)` | Create anonymous (unnamed) network |
| `n.node(name)` | Create a node (standalone or inside network) |
| `n.group(*node_names)` | Group nodes visually |
| `d.add(...)` | Register elements |
| `d.link(src, dst)` | Create peer link between nodes |

### Network Parameters

| Parameter | Description |
|-----------|-------------|
| `name` | Network name (None for anonymous) |
| `address` | Network address (e.g., "10.0.0.0/24") |
| `description` | Label on network bar |
| `color` | Background color |
| `width="full"` | Span full diagram width |

### Node Parameters

| Parameter | Description |
|-----------|-------------|
| `name` | Node identifier (required) |
| `address` | IP address |
| `shape` | Visual shape (see shapes table above) |
| `description` | Label on node |
| `color` | Background color |

### Group Parameters

| Parameter | Description |
|-----------|-------------|
| `*nodes` | Node names to include |
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
| `stereotypes` | Dict of `{"name": style}` for stereotype-based styling |

### Element Style Keys

| Key | Description |
|-----|-------------|
| `background` | Fill color |
| `font_color` | Text color |
| `line_color` | Border color |
| `line_thickness` | Border width |
