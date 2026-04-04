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
    n.network("office",
        n.node("server", address="192.168.1.10"),
        n.node("workstation", address="192.168.1.100"),
        address="192.168.1.0/24",
    ),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGZEp2q0Kdwf9UNvHTbSUUKfcOdf2jLS2Wfv4265_BIqpEHKi922Gc9AIb5gSR62hOAIeQMHdg6PXPwXde6-aOcIDLY-EBMeBBL88HghEaC3fLY8Cf31G8UKPERduLGBLLpBLSlba9gN0dGo0000)



This creates a network with two devices connected to it.

## The Multi-Membership Model

The fundamental pattern in network diagrams: **placing the same node name in multiple networks IS the connection model**. There is no separate "connect" call for nodes to networks.

### Single Network with Multiple Nodes

```python
from plantuml_compose import network_diagram, render

d = network_diagram()
n = d.networks

d.add(
    n.network("lan",
        n.node("router", address="10.0.0.1"),
        n.node("server1", address="10.0.0.10"),
        n.node("server2", address="10.0.0.11"),
        n.node("printer", address="10.0.0.50"),
        address="10.0.0.0/24",
    ),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuSehJybCJ5Uevb9Go4ijASylobR8ISm3ynKK4bDIYbABYnLi5PGC3VJ0KD_8HCaQB5cKNrgIMgGGZQd8K2aMegGujQWijSWGgne3L4L6M1N1JIeeoip3OPifrAHQhbekXzIy5A2l0000)



### Multi-Homed Nodes (Bridging Networks)

A node can appear on multiple networks by using the same name. This shows the device has interfaces on multiple network segments:

```python
from plantuml_compose import network_diagram, render

d = network_diagram(title="Multi-Homed Server")
n = d.networks

d.add(
    n.network("public",
        n.node("loadbalancer", address="203.0.113.10"),
        address="203.0.113.0/24",
    ),
    n.network("private",
        # Same node name = same device, different interface
        n.node("loadbalancer", address="10.0.0.1"),
        n.node("web1", address="10.0.0.10"),
        n.node("web2", address="10.0.0.11"),
        address="10.0.0.0/24",
    ),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/ZP2n2i9038RtUuhGtNgfRY9qT75o58Uq5-JmUfKqRGVfkrkhGi4E4iYG_oDVIDueYRPLCEerC1pRe7vrg2jsS6BfM4pidQShF0n0PErhkS6zBO8lfn40EIVSDB279BERrAQ8OrzdssGtvQ4cLr2WMBB0UP56crnUy31tYEz8-LU2Dftg3yC7nVTsW9uBN0JiZCWM2VnUE9YSeni_zWG0)



The `loadbalancer` appears on both networks, showing it bridges public and private segments. Each occurrence can have its own address for that interface.

### Multiple Networks

```python
from plantuml_compose import network_diagram, render

d = network_diagram(title="Office Network")
n = d.networks

d.add(
    n.network("dmz",
        n.node("firewall", address="10.0.1.1"),
        n.node("webserver", address="10.0.1.10"),
        address="10.0.1.0/24",
    ),
    n.network("internal",
        n.node("appserver", address="10.0.2.10"),
        n.node("database", address="10.0.2.20"),
        address="10.0.2.0/24",
    ),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/TP1H2i8m38RVUugm0yok-2R2Jg07a3raDfDYLqSQBIYxkxB26BWz9lduy_7NKP3bsNibJZp1kUlSbU14aXvyLo5PXpVuA82GLs3xzpG3eBLCCS8HYagNkgnAlJFxuZ0TEyUKq7ku_6DLqMGeKHk9NyIhbCxOk7ZkWX07z1i6Pcc0mx0LRkPm08k2BKPQeyoiCAgQWltrz0K0)



## Standalone Nodes

Create nodes outside any network with `d.add(n.node(...))`. These are useful for external entities like the internet or cloud services:

```python
from plantuml_compose import network_diagram, render

d = network_diagram()
n = d.networks

# Standalone node for external entity
d.add(n.node("internet", shape="cloud", description="Public Internet"))

d.add(
    n.network("dmz",
        n.node("firewall", address="10.0.1.1"),
        n.node("web", address="10.0.1.10"),
        address="10.0.1.0/24",
    ),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/RO-n2i8m68JtFCNHMMeYRaNewkPUEgJzVpMOfYL92IXzTsFhfjjnzzt1rI5g7-V12fV8w1jU0Z0kidSSqOIxdXWdz7QSQGVYq7ipHJEwR1QNkREcn_cB5ssLorcaqJz0mtCT0pIHvn0-3ILBMQfIxW_7ebh3g_6SjBLeVZ6rBGA9kx-vt815BA9cH_d66m00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/PT2n3e9030RW_PwYOVODZ0c3STF4C3WOXy8Ll8W7jZqP3E_k0H9C6Dl__peq5KNMyAoDEgq9JeqboExOaXZVMOSLV0o09-qQVe3p9QCeXq83qnW1T9J3LGO3E_3nm0OiIS6kLTVuk4ikiP4HlucJstOqzezOLCnHrcp_2sPKkffaSQ8DOxLcXrY3R0fd-WeKQA7Zk8974ea6paCwoTxq9YLluuU-)



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
    n.network("production",
        n.node("app01", address="10.0.0.10", description="Primary App Server"),
        n.node("app02", address="10.0.0.11", description="Backup App Server"),
        n.node("db01", address="10.0.0.20", description="PostgreSQL Primary"),
        address="10.0.0.0/24",
    ),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/RT2n2i8m40RWFKznP1PjYfi8rRc3qb4SOkyeeJO9bzGYqdUtj893mstt7ny_LuIeEVRTKzW1ZMxW8m0inS5n2vuTzdKqpivh08t8508SGQfiEyyktyl34dgVARYjRrGcDu0KQZP-ngRemgRJ_8QJzr0HluZb_S_aIKQjcREkszud57oak-IfBYx4Xgcwbl2hjIYZ64L15gVlV040)



### Node Colors

Highlight nodes with background colors:

```python
from plantuml_compose import network_diagram, render

d = network_diagram(title="Server Status")
n = d.networks

d.add(
    n.network("cluster",
        n.node("active", address="10.0.0.1", color="#90EE90", description="Active"),
        n.node("standby", address="10.0.0.2", color="#FFE4B5", description="Standby"),
        n.node("offline", address="10.0.0.3", color="#FFB6C1", description="Offline"),
        address="10.0.0.0/24",
    ),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/RP312e9054NtynKFsqQfMH0HcA7R5YwZXJbZ34qpCVDK8lptHeSMfRpTlOV3vSK62utrGn3aA1ZaJ3TCGuu5reR8blBY1cy281csIj-X5BL1I_GPG46fPiR07hp0Nmot32DlvyeIUSFWF8O2RmwKcLBp9t8b--Omm3OlbL2wJsPRFqstldTnDZjKqkjhIXUETRcZVtnPbaR9-kjJLIMud9ot6ljEZlxp9PjZu7mTwKZC9BMV_000)



### Combined Attributes

```python
from plantuml_compose import network_diagram, render

d = network_diagram()
n = d.networks

d.add(
    n.network("backend",
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
        address="172.16.0.0/24",
    ),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/TP2x3e8m58RtFiL9NGbIKD0O4n8O7RoCnk506o0W9MqDW-7TBR1erFM_d2_dZxL1PHxtXhGzhx209m5eXUcbgY73l1OjdpG0v5m9hM4Fb4M-oqBNSxsblwAxoUwaDeKDmFLNa7dK0LrY9wpCqM26MZZ0XSvLrPbAjcFyED-ud0x0rhQGoqQgqLW4GHXj6RtDB2LuzGValuEqaGgBRyvvwYUOb-A3aYR1nazdoa064jllxJOl)



## Network Properties

### Network Descriptions

Networks can have descriptions that appear on the network bar:

```python
from plantuml_compose import network_diagram, render

d = network_diagram(title="Data Center")
n = d.networks

d.add(
    n.network("dmz",
        n.node("fw", address="10.0.1.1", description="Firewall"),
        n.node("lb", address="10.0.1.10", description="Load Balancer"),
        address="10.0.1.0/24",
        description="DMZ Network",
    ),
    n.network("app",
        n.node("web1", address="10.0.2.10"),
        n.node("web2", address="10.0.2.11"),
        address="10.0.2.0/24",
        description="Application Tier",
    ),
    n.network("data",
        n.node("db1", address="10.0.3.10", shape="database"),
        address="10.0.3.0/24",
        description="Data Tier",
    ),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/VP8nRy8m48Nt_8fJvYgD0nkgH2dg14nCHGoNtBLODOvb6ra2yTyRnwX2JSfuzdldxzrvxZnQVpggp4kl69Re4TvOUxQP3YJn2ouPW6OVMliDT3ptDG0IMNOENY0NPL4MeYYVgsa-wo-9NMEbyRBLKR1SVy0cTRW9FWFiXXr4_lJN-Yuj1rGgtoUZgaUDvT2vQf5WWGfrmpRPhtT9q9X_abGFahmQesI3VRcLNT-a2boB8LSLkVQ_YcfK8OPe57SmpZPvDELekuEYCQP9cfKxeE7kC3vLe-CRmpMRiwRkD_m0)



### Network Colors

Color-code networks to visually distinguish them:

```python
from plantuml_compose import network_diagram, render

d = network_diagram(title="Network Zones")
n = d.networks

d.add(
    n.network("untrusted",
        n.node("internet", shape="cloud"),
        address="0.0.0.0/0",
        color="#FFCDD2",
        description="Untrusted",
    ),
    n.network("dmz",
        n.node("proxy", address="10.0.1.10"),
        address="10.0.1.0/24",
        color="#FFF9C4",
        description="DMZ",
    ),
    n.network("trusted",
        n.node("app", address="10.0.2.10"),
        n.node("db", address="10.0.2.20", shape="database"),
        address="10.0.2.0/24",
        color="#C8E6C9",
        description="Trusted",
    ),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/VP5DQyCm38Rl-HKYkuurCMMib44WMMxRQRkqzE16OZDBRMChT1_qlyy9Rcb9EdpJ8yaFhmhFqd6tQnDMt1Ay4E-D-uILqUGJlKSbt-4t0T0HT9fTvvbmg08qfZKE7Y6zgUkogaIw7CeIqP7tFSZkXZVB8aBoZLEMbT4zVZikZ5Xf9XT-WxN_a9P2IzEQ3ZSzFPo9uEvdGg5UbFEnGjuRvC51pASbgkTL1DQPhszOZuVpB1qvN8kYV7YwBnTNFCG_7gyNKKXhnoRYP1AcjrDSPEaj7CD3oN8hFKNtGrAGnd3lFm00)



### Full-Width Networks

Force a network to span the full width of the diagram with `width="full"`:

```python
from plantuml_compose import network_diagram, render

d = network_diagram(title="Backbone Network")
n = d.networks

d.add(
    n.network("backbone",
        n.node("core_switch", description="Core Switch"),
        address="10.0.0.0/8",
        width="full",
        color="#E0E0E0",
    ),
    n.network("vlan10",
        n.node("core_switch"),
        n.node("server1", address="10.10.0.10"),
        n.node("server2", address="10.10.0.11"),
        address="10.10.0.0/16",
    ),
    n.network("vlan20",
        n.node("core_switch"),
        n.node("workstation1", address="10.20.0.100"),
        n.node("workstation2", address="10.20.0.101"),
        address="10.20.0.0/16",
    ),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/XP4n2y8m48Nt_egZxjfa4444KLnT78j8J4uDZOaaQJk8_zscQKMn8hUzzvBt7RTqdbbVNbNYfLS8AyQBez48M_IriKMYQo7P6Uu9W8uI7FjC406uKSR20jBH9WkJpbkP2M7HkM2GRDpEPDPvjHJ-4fnJgLIdSMFnu6hf-GLoWOvRUVFIw11RDnxiMY_TX_ZZ3QTIJ9EiW_biZSKJCltkY893Mw4ba0-y8rdiwbDqE4M6YUWm4Vr753veRX8s_yAY4Ul5zPQbFx8lkaUoH2sQGpy1)



### Anonymous Networks

Pass `name=None` (or `name=""`) to create an unnamed network. This is useful for simple connectivity without labeling:

```python
from plantuml_compose import network_diagram, render

d = network_diagram()
n = d.networks

d.add(
    n.network("dmz",
        n.node("firewall"),
        n.node("web"),
        address="10.0.1.0/24",
    ),
    n.network(None,
        n.node("web"),
        n.node("app"),
    ),
    n.network("internal",
        n.node("app"),
        n.node("db", shape="database"),
        address="10.0.2.0/24",
    ),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/TO_12i8m44Jl-Ogb7n3Juas4_eTusB2h1jCODf60fVzkR3q4mTiEC_k66LD6oS_9gr38uHLc1H0ubuVSWQRNgW6GI3WbE4BN6srqhyrks7U7rRmuuOBURwgm_HnBmvbRey9Y_4sua5a2-ZzrGrltVGSW2wTqmyWrHvZHOkBpHbxKo87gh3S0)



The anonymous network connects `web` and `app` without showing a named bar.

## Peer Links

Connect nodes directly without going through a network segment using `d.link()`:

```python
from plantuml_compose import network_diagram, render

d = network_diagram(title="Internet Connection")
n = d.networks

d.add(n.node("internet", shape="cloud", description="Internet"))

d.add(
    n.network("edge",
        n.node("router", address="203.0.113.1", description="Edge Router"),
        n.node("firewall", address="203.0.113.2", description="Firewall"),
        address="203.0.113.0/24",
    ),
)

# Direct connection from internet to router
d.link("internet", "router")

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/TP0z2y8m48Rt_8eZiwrjTIj2GHHSNOj3QCuQZ9UIf7IG_dVJBn2got7SlUzp7uNpmlhsfPbNNYDSoACbz70qH5XvPOXH9vMeuSq0rD8ktKCq20Uej6db1YIwogfcq8SYNp3ybWTNI3fZdu2onX438AIqwDoWpP9TdCHf6k8ss_Dyx5lJ1WAKFtKfNmqy3UZhQ9fc0joLnKve_GUIhI7dsJ4H-kzxesXUAMSzAv1aUDa7)



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
    n.network("edge",
        n.node("router1", address="10.0.0.1", description="Primary Router"),
        n.node("router2", address="10.0.0.2", description="Backup Router"),
        address="10.0.0.0/24",
    ),
)

d.link("ISP_A", "router1")
d.link("ISP_B", "router2")

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/ZL1D2u904BtlhnWyzwLqaw3ir4ti616BCzYYxihkB1BHVy-iZB13pEtD-vXvQyVIigyhmOehWepGQvIQOMkqffoLqKxe5fKiu2e0Tllqj863Eyk6O0LvPJnE0CdbLZKFTWS67GasLNEMmJ5-QP9_D0dnIwA9MsDB82oepmMGY9QSUt33nQoVURGCudvfZMUo8Hp6h30OPQLMrT9U8EjLpyItH_JB8nfx938lVVDbSHlwcKxV5tt-7x0e5ZUn9erTxNS0)



## Groups

Visually group related nodes together:

### Basic Grouping

```python
from plantuml_compose import network_diagram, render

d = network_diagram()
n = d.networks

d.add(
    n.network("cluster",
        n.node("web1", address="10.0.0.10"),
        n.node("web2", address="10.0.0.11"),
        n.node("web3", address="10.0.0.12"),
        n.node("db1", address="10.0.0.20", shape="database"),
        address="10.0.0.0/24",
    ),
)

# Group the web servers
d.add(n.group("web1", "web2", "web3", description="Web Tier"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/RP1D2y8m38Rl-nMXPz6rUXDXFqBm81woDSpYx4hIiOFilplhnmQEaCkRvyrN8H4vTlScyxrrMCCZ0_0K-vPlK3MTHEAa0Q2rJ29m0ANpTOgDsQbzAlPKQZZ_8pfNbnzX5Waz8xQBXFaITdc8oTKAv8g1Hj5Yn1A5acKOi-Qs2vyRB4d5BaJN-fV_H2KS7V7iY6dPQQbtfo4hoDlnLKy0)



### Colored Groups with Descriptions

```python
from plantuml_compose import network_diagram, render

d = network_diagram(title="Service Groups")
n = d.networks

d.add(
    n.network("production",
        n.node("app1", address="10.0.0.10"),
        n.node("app2", address="10.0.0.11"),
        n.node("cache1", address="10.0.0.20"),
        n.node("cache2", address="10.0.0.21"),
        n.node("db1", address="10.0.0.30", shape="database"),
        n.node("db2", address="10.0.0.31", shape="database"),
        address="10.0.0.0/24",
    ),
)

d.add(
    n.group("app1", "app2", color="#E3F2FD", description="Application Servers"),
    n.group("cache1", "cache2", color="#FFF3E0", description="Cache Layer"),
    n.group("db1", "db2", color="#E8F5E9", description="Database Cluster"),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/XP91JyGW48Nl_HKJl1e5ged6cApPBLwyUJGUM9Zi4h4Ge6wCsVzkswrO8wiX79XvynxvO16J3AbxjLKooI8yOdWp2k4-kCx7gjrf8pVmKG6qc7Okl80FJdSg6TUEPG2fTS0OuHO8esVZEkSNvERGz9x1qsy9e-GvAtXHmRuKIgej5bqu_Q4f-l3iezT5avgIKuXRwR4lQfdaMaRC8qNFcXqRsVTxCx2Ru2XdNHWcJvfQSB6Qi6YCAXW_KkoRTzvRe-Hu75u0Gvpn--RqTu8GecveEM4vy847-Ow1pAdEwVrp_ojnsLoNtLSJ0bZQBgOSqGFF60_c-sg1hUw_soS0)



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
    n.network("lan",
        n.node("server", address="10.0.0.10"),
        address="10.0.0.0/24",
    ),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/PP31Qy9G3CRlxwy8lQjjjvr4KDIDWgXikxaTihxObRLvafSgO_Y_BotpD788uVlb-qBcKL6qQnlNOir7mPPWjHojCQhJMXk2lGJVbLe7Xg87eegDdP0hYPK4FWczjULk-rYirjlNOh6vISSG-hR7YY1p9Pu6curvG7VogEGXJ_E7KNhd6gg8lGDu4YA66Imiyqnl_6pG35uKsNzyEsF-IBxu6YluiHKclGJvWWPvc07GUw4ORJ79ql5Ga_m-cGvY93dRLOV_K9OcxprpTLStjn3xooy0)



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
    n.network("lan",
        n.node("server", address="10.0.0.10"),
        n.node("client", address="10.0.0.100"),
        address="10.0.0.0/24",
    ),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/RO_D3e9038Jl-nGD3o1Wl8a6V-AHYqVZeM4RtB3i9jqYCOPt5nTkcgQ7cNwPJCiWoD9tLXL1NfRsoWtQO7EUbh63jm8uOjqsx7kdJzvwXk5XX2R_ufrKs14SsA1LeohI9KECM8BhLsYeI0RFxH8S4zriWKKNDG1gpHG2x239irMSTBr9jl4OY9_4SFk5yYovpqnj3JdvpopGE5KioUdfsmy0)



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
    n.network("primary",
        n.node("server1"),
        address="10.0.0.0/24",
    ),
    n.network("secondary",
        n.node("server2"),
        address="10.0.1.0/24",
    ),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/TP312i8m44Jl-Of5xxQfnIAjectjIVo7q2mbs2QoIHMH_hib14H4beNb3SmCUx1Ea1k7dXNMFNlSC_sGIdJrl2G6U340ZUvXwEflW5AqruxCg6LbUaEmFAsRfAczTbOQ0-NRR5CddZP6kq3ZEisEVAOJcrWHXKYdN8zGZTQP0IuXhHHaGvcl5ZTIWw1dQ2Ea9BGMTh3WySfFbAIBt8iMwOx4Sv_tSR3O6Yt_U_1VZoGFdG-evVojDm00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/VP0z2m8n38Rt_egWgw2dwE87vzTDuk8e3j66izXhIvjJHFplrhCk3Ww1a3plcuyyC7gkAoqcWU-QPiBSfC9o5SDZ1Gy14CXVoJSfm09FbzBRsiYbrTP3koYAmRhNz3RAKAgkHyEizwu-nLDCkicR5Mk2PHtOLh2raa8QrvWRuflr5z1eqZ1qBeDzn4vUELRMm1HQS-TWzrafQnt6Nx3_3-n_GNc4VJYZemX8P3nYe0xy25UfyH6zByZ9oFYa5m00)



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
    n.network("cluster",
        n.node("node1"),
        n.node("node2"),
        n.node("node3"),
        address="10.0.0.0/24",
    ),
)

d.add(n.group("node1", "node2", description="Group A"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/VP312e9048Rl-nI3tJErgD32IklIhITOt44MrrtPNP48tprt4QHB30F_pC3t_qnkBDMsRmN9Z7qBF1CvC4xhOcfDM_WGW5ghllCAu4ghnisItPHG6bRbuRuhZ_xsv1BdRLpkYoIUjYCPIHREQCkjG7YvWS73KSriv-aIxQ1q0vNeZKKzErB6D1e39mYYpTfN66-3r1-bOXWjCbvaadhtt_GCJQLvPxcIZkSZmEKFoyNFKRBfGLy0)



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
    n.network("dmz",
        n.node("fw", description="Firewall"),
        n.node("web", description="Web Server"),
        address="10.0.1.0/24",
    ),
    n.network("internal",
        n.node("app", description="App Server"),
        n.node("db", shape="database", description="PostgreSQL"),
        address="10.0.2.0/24",
    ),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/TL8zJyCm5DppAvx2YjBKvIE8WWfDCtK0CZ0W1gT-JQswTcIxH0Nbl-EwYLGrYYKFlZlVFPqzCvPgkz-9O6hiGU1p86l6QPcwhUaE_WA0LxhQbbhj9PiheJJK6sxHuH9jhVJMQ_gggyKa8rdgkCPjW_e7zP0qywkLHenQMb23WyP9ThjuyDoIIsnHihXF9wJpM7EDDHLYE76UfkJIOtv74f9uZoQOZjf6BBS28JyU61G7-502svgyVTS3s_ssSPGnZSR04uJZE8gZSHIFo4tuwCbr3LyCpKhpod8bZwAidJRyFabgB7gQJuVbliMJgZbBvjAYbbGCn9FpU5fLFUyNXvrx0p0tWDdG2XtTlSSrN5nxKyQM6lFtPJTI4ynGClUT_W40)



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
    n.network("production",
        n.node("web1", address="10.0.0.10"),
        n.node("web2", address="10.0.0.11"),
        n.node("db", address="10.0.0.20", shape="database"),
        address="10.0.0.0/24",
    ),
)

d.add(n.group("web1", "web2", description="Web Tier"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/TLBBJiCm4BpdArRXYcYSDd1egVhqYHj871079rwrLbqxiXsY2lNVSOmBAAHUxMLsPXyZBwnZnZL7cSoiEqcS9whbWkqsFWqxmcS2i6BLOMTqe_XQIstWXYwxy1M5hjNc45W3lEsOvdGJQaz2OKH9SL-iCu-UVLeq7sYkDQ3XzHjCyYvYWuvVNzMFjmKj-lg75Q7BR_qvcOtYtKuuYK0RAK_mt44SeWdHaZ3aSd5jD6yg9xIAindd1gs5HqX9TXTYb4_IQIYsM19u-qyXMVh-myW76UJ2uELGFS_IMx1xLgC7ENEiP1Q3ecyEHriPKOULlVuLItWHQFvi-Bl9D9gpGCNzt_W2)



## Complete Examples

### Three-Tier Architecture

```python
from plantuml_compose import network_diagram, render

d = network_diagram(title="Three-Tier Web Application")
n = d.networks

d.add(n.node("internet", shape="cloud", description="Internet"))

d.add(
    n.network("dmz",
        n.node("lb", address="10.0.1.10", description="Load Balancer"),
        address="10.0.1.0/24",
        description="DMZ",
        color="#FFECB3",
    ),
    n.network("app_tier",
        n.node("lb", address="10.0.2.1"),
        n.node("app1", address="10.0.2.10", description="App Server 1"),
        n.node("app2", address="10.0.2.11", description="App Server 2"),
        n.node("app3", address="10.0.2.12", description="App Server 3"),
        address="10.0.2.0/24",
        description="Application Tier",
        color="#C8E6C9",
    ),
    n.network("data_tier",
        n.node("app1", address="10.0.3.10"),
        n.node("app2", address="10.0.3.11"),
        n.node("app3", address="10.0.3.12"),
        n.node("db_primary", address="10.0.3.20", shape="database", description="Primary DB"),
        n.node("db_replica", address="10.0.3.21", shape="database", description="Replica DB"),
        address="10.0.3.0/24",
        description="Data Tier",
        color="#BBDEFB",
    ),
)

d.link("internet", "lb")
d.add(
    n.group("app1", "app2", "app3", color="#E8F5E9", description="App Cluster"),
    n.group("db_primary", "db_replica", color="#E3F2FD", description="Database Cluster"),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/ZPHTIyCm58Rl-oiEzTRLDb7P6CBi5mWAeWF18IDjmbRCsf2c3XN_kytMkTellIl9UT_pdYT9PxaYKXKRRgX4SGRpjMHiD4-OX2SMmRKGF8c9IhBKIBSq8IluD02IL36PCWMBV4q4Wok8ULRGKw0iZsKYT7svQDvKTURBj5IL7zjClWBTVEnS0EACPr8NdeHXuBdOdEwM2QMIvRdUS6pBjXpBFaFdrMQZXN_tN6tm21PjfMERhLYt6Q7W4axIcCbzjgzQFYB4Kca2pP3UEBZq9ZqXqK386aRGR0SI8ylP9mATm-aiw1Yfx02FJBwLgUjwrAbt1lMefiUTUZIenssYb2ZIZTHr_I1qUv3YeNClBUiiks5X3MiG1zOu1WV6Uk2gWaPB8PCDaUzTTKWVpE55w9aZahCMgllAm7ThhfBjRaYdg_CVruVAuE2gyQzaLeWMyc0SNWIJteiA7YzozOlhaT-HqnyzS8X2l__az0YDHaUqJIY7LZz_dT6eV3fJuykOiPIM_wvl)



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
    n.network("control_plane",
        n.node("master1", address="10.0.0.10", description="Master 1"),
        n.node("master2", address="10.0.0.11", description="Master 2"),
        n.node("master3", address="10.0.0.12", description="Master 3"),
        n.node("etcd", address="10.0.0.20", shape="database", description="etcd"),
        address="10.0.0.0/24",
        description="Control Plane",
    ),
    n.network("worker_net",
        n.node("worker1", address="10.0.1.10", description="Worker 1"),
        n.node("worker2", address="10.0.1.11", description="Worker 2"),
        n.node("worker3", address="10.0.1.12", description="Worker 3"),
        n.node("worker4", address="10.0.1.13", description="Worker 4"),
        address="10.0.1.0/24",
        description="Worker Network",
    ),
)

d.add(
    n.group("master1", "master2", "master3", color="#C8E6C9", description="HA Masters"),
    n.group("worker1", "worker2", "worker3", "worker4", color="#BBDEFB", description="Worker Pool"),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/VPHTQy8m68Nl-ok2tevfKX67RcXhPJ0slDl562CsBwuOcvAaap7yxqlJR3CpjIMbRSvptd3oCLUQIbtlUJHJ-fF3NLGUM46tIzCatQEl2A4Iz478dNr7AA7vRYj5NR9KS25HFvjaYzNOz1rDKo0_G7P9L_QoqcCq6xYAkj0Sq4Ez0MbAWK8fhvK6wORYZI4NfPQ2lrMSbk3AKCOaA8LkKGyFh-qz8AFUr7OoKBaiAbs8iX6aBO_M3UyaUzfKm-Zbt0WFUrV_BHwj7E7UwobEWZZkn8cFnq6STEBn3muwPo6MD2DNxxG2yvDHJJTKmPbRGxTEnvEGcmV8D_FPaJ2-aF2pXT5Jw-KqhMCWOXoCs7dyHjpY98ZZJfpuU1p4IISU-_WeYCUT-EWlrsOFL2xAtEu48-kdasoSteH3l5-WTgALlqQz5UUjdykracIPhPAB4xOMWlkpvMNl9UdbCdNxUGubCmV9Dm00)



### Home Network

```python
from plantuml_compose import network_diagram, render

d = network_diagram(title="Home Network")
n = d.networks

d.add(n.node("ISP", shape="cloud", description="Internet Service Provider"))

d.add(
    n.network("wan",
        n.node("modem", description="Cable Modem"),
        description="WAN Connection",
    ),
    n.network("lan",
        n.node("modem"),
        n.node("router", address="192.168.1.1", description="WiFi Router"),
        n.node("nas", address="192.168.1.10", shape="storage", description="NAS"),
        n.node("desktop", address="192.168.1.100", description="Desktop PC"),
        n.node("laptop", address="192.168.1.101", description="Laptop"),
        n.node("printer", address="192.168.1.200", description="Printer"),
        address="192.168.1.0/24",
        description="Home LAN",
    ),
)

d.link("ISP", "modem")
d.add(n.group("desktop", "laptop", color="#E3F2FD", description="Computers"))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/VP91Jy9048Nl_HMJUXMarHWDCO4KYIJODFR0WNXOkvEweTtPx2vmCFntjotL2iNRPdVUDs_UxCHOfkssB3mhR87mGYL2Z7PFUkF9FHSiXoyFO94ci3QVJ24yGLRGbby3HvDfeQmWwIxzXRIe9Lf8KUz4Xf1esWcEsdyVEu9ieB1diYR2gNurZI4YAJ6hRlnnNLCInnBM9wKH-t1UNwkt1dxeD2X-6Z3EDHfJAOB7S1ZSFmo3uUWcl3l2JwZrxCjft6tT73LjtMomxWK6_baKAp4Ny5QB6d_E7JENz2C7QACrbZJByOmOJzEMv5usbjH5skZSp-meIQ8MKZ3r7wDdfcMjQFLA2tavah3FHD98VXUMkrZLSLKP5QIhggldstaud_LlAA9ILQ4Q_qyKtP5QUFLX1uDsYGTlWfAxR_uD)



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
