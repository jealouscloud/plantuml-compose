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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgoIjFoKnCvoh9BCb9LGZEp2q0Kdwf9UNvHTbS43c5QYu5XJo8a49-MbfcSYfOI44XCIMbABMuMC5MGSdGqaZFqCn2pr3FGD_8HCaQB5-SMbIMMgGGZLMTeO5IB4GPo62WMqeoy_DmgeKghkMgvN98pKk1k0m0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgoIjFoKnCvu9G2jLS2WfvgINb-KNP2Zc9UM2-Wa9YIafHQd6nWgs2ag617XZg6vaeMOCbY_9BIrAB5A8n5HagnKAK5ASMbQKM6M9LOu2go0Yh8hX91KMPUJXiCuMQLCjLo-MGcfS2yH40)



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
![Diagram](https://www.plantuml.com/plantuml/svg/ZP2n2i9038RtUuhGtNgfRY9qT75o58Uq5-Jml9OqRGVfkwkjGi4E4iYG_oDVIDueYSRUUReQzHeOZcrGlpfKTtPmOkbOp9J3mm14rhwI6zHj4NmvZW38EU6cWJqacTsaDaLyzNMsJNPZ7Yfo1GMA9GkS5scqoUKD3tE7-8wKVoLeqx7-C7nGdBO3z5pW8c1dHBP8uFV2mUGStVIK9m00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/TP1H2i8m38RVUugm0yos-2R2Jg0741yocqgnrf462yhkBgmm1cwFoV_nvoDT5cH9nGMyAmaI2SxUXnl1YQIy-A5g1by5aEeAtFCppG3e75FES8J6w5QtfjKxksyEK-W3Ky4OuVAFcUPQeK9z9duJhrAwOkFYU4X2d31k6DYb0Gx3LhcTom4S2lQOQOsoiyAeEagklkC7)



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
![Diagram](https://www.plantuml.com/plantuml/svg/ROyn2y8m58Jt_8eZizHKt8hGrSszEAHzJmt6f2Gf0QN_tTguwNIFk-yENXkJ3ibbClegYk0b0ECI1yS9NRpfaN70OFr46n378PWn6UyMKvwctfe1noykpyrINeximntqUAvZW2OA7EEdKQjALNMbjhkzRDRmOW9dRIswNwmkYq3c_c-k2Z2BMRJigBpm1W00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/PT2n3e90383X_PwYOVODZ0c3STF4C3WOXy8Ll4WER7io6DxTWzDWmdZz-tMuN1HP_M0TDaQTjWIdpX8KT-n9J0hmDW2UTEZu0SxNZA8SAWrCSm8Og8IhJ0PsuEE13LYIYbslhlDnbbtYHa7y8ivkszdOFs9HiKHPi_qt_53jMfB5YNQCpPeTuXeKAVxeCr2WXSxF5JoII3HmdcgIenbDJjwcl_W0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/RP2n2i8m48RtFCMHMRGfRY9KPmUbepZ4vYYXc1oNr2BITrSImQ7XXeFxZu-FlmbHStIJiReNUS5R03YCa-S1YBqPksYzIsS0RGnZ2B07gQfrcaszbRiS4bKAhiiVLSaL60mTMqgmRtHc-z3yWWCHjCXFP7dxO-eYHYqnHzqD8nKevbvsgKikFiIUiRsSuAULAREOHOFEv6O-)



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
![Diagram](https://www.plantuml.com/plantuml/svg/RP312e9054NtynMFQHkbPe54O8PkMxYC5ZOpnf3CnCnJYV3VKuSMfRpTlOV3vSKM2uEgvRAu4vHO2SY5QOI170kiBN4Ll0c04jXgym1MrHPxOiW02iwDi1OEG7rlDTuw2EdUbGnb8-0oXNow12uiC_A9KgkXEOvmdpDTQJCaYyXBqyYZLsVhjof-UytfWgakT_IFBylICDb-VReiAwbcvssclhEZ_tp9xkGxNqSw4Wl5tSS-)



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
![Diagram](https://www.plantuml.com/plantuml/svg/TP0z3u8m48PtViK5Lu8K53N6X0H61pz6ut2q3JIObhHD60p_tK8NZJfTydxSaxl2MDHM3anW4_W1pm10SZietK6DjEEIpHe0CgQvCN20a6pIcEHn4YVBT1NkPxjNnZOk0BTVGPA44PWMU-vaXXPhD3m2nWtLehT2oIb-yZkkvoEGjIjGzL1wCXPPbczs9BnxbkPC_06bxo1ZbSRcctEP-oNIbdzGgZBRffMdZC4O5Evw_vSN)



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
![Diagram](https://www.plantuml.com/plantuml/svg/VP51Ry8m38Nl_HLMpwXhsjscIGmG9-2qqoOERksDY916IQH8eFxtaGPDQEquEdxF-PuzTnwjru4aVcTUUiMmGe-mPEtPPga1bmn0im-TFGATpaCDW4IMdODNo4LPb8KeogVgENyPciIkjT9usUaeM6q_O9Sct0HV0Jx74qG--sjTIyi1bShtoQYQIMCvTcuw95YWGjsoJVR-BWaQyq-Iwa6IDsEKR74et-LrRb85RiIOgufS-rz5DQaGOpIADvXcgnzjEThke6YAgKwxSWSqV7sCNpNe-CRGPtFMbEx-0m00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/VP71Qi9048RlUOeXNejD5X6b58IakRMdUb5wM3D3NOoxo-u4suhlRXBNqf8eUvjlPlRZduLdwLWVKCdFY1LN16_41-Dsi3AQV7H1S8m0T02rPbTx9kog0AMfZ8DdY4T5aUMvY9-wiaHqv7qBad7t7fE0a7pfb6LbT8kNruK1AytacjzWxRVIKjDILgR6ZvQU_eZW_cT0ePXdaxv2sXgaZOEO34lahwi0h3DVtx3k3wT9t7Eu5KKsUvbcyniUuex7-xyefBLz4_5hqanlXhX8uWUuXeUIvKPw2kwdQ44QBtSz0m00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/XP4n2y8m48Nt_egZxjfa4444KLnT74Ka9gU6XaIIQ0VfVzSqRQaOaTlUUydxZbiwpwpNbP3iaddf5SAAyV9aDC8MVMLicKKNdXc0ZXASkamG0RXHni82yj6c29FF6va9OT6vO91YtCnardgL5FuQdFDTgLRZnkBHLTBpA-m5EcxbpKkZGspzzc3NUFaXnEi1paCnJOeMvhCr5a_8zBiZ2Wxj0os1VU8TAM9NbwBf54aJqJGH_KSKFdYV9Mp-XKKZLiyroD8VsPwkpfQeHRpc2m00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/TO_12i8m44Jl-OgX7n3Juas4_eTusB2h1cCiII1WwRzR6mz1yBGxpEmRTaoPOWw57LrL7PWL42INPxo37wzD0yGS9IKSqVL66zrhinlstM4pBovA8U-hAc8_oz9mvjPOOTFqct0XImpa_zGDRTtt762BKxhH96kEAPEb9ETANjGeWUjBRm00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/TP0n2y8m48Nt_8eZiwrDTIj2GHHSNOj3QCuQ34b9KZf8_xj9Oq6eBWVtxhsFnzNES-lrA2JlY9TU8LoqHwlHmz5eZQsNHfDaW1S1aCkvSG_U8noWLMOG6n3eMYlxw0yYNJ3qLdsdiWoi6S8IrI2CnZu1HOSp780BOT6vI2YBNLxaZ8MvBVUqckyf3CrF7wEh6gU8liwXr0JWBYsENAa_a78DENyIYJ2HYTIeHNhA6m00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/ZP31QeD054NtynKNrqrJ9RjGY7RLdTYbb33u7ZfePsJcYPIIVs_Kj4cnYp2xE-SUBkyGH7kn8nbTAp7ICGgcmPAsWXTdBLTYd0rgGV2bWDUt_9YY38tk6S-eEZVG0uX3vKq_qUSmEaD8kxxHqVl-qidkwMGiDvKKcmsy6uHzVDNyPicKMPRH-HPCDS_x04taEOJ96Jyzpc-RxABz_7dHeLnJSRJQb7lpeVqdYhcrBFjn9FyvahKZqrKxz7yK9tLI1xQqdFKR)



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
![Diagram](https://www.plantuml.com/plantuml/svg/RP312i8m38RlUuhGi-XQlOdWGmWUn4EsX5cKRYGTEyZUtTcf6pX222HVaZyvQaI9eIEFLJO6U6O0WMDNontAHwkH9UK0a4XO5GvWRBvEjd4xiq_5ZWiBbt_4vkRw8zmYOMV4Tf5mNuAMbxZSh41lsF2G98nOe79gwGUlf6wRpmt4Mefleg_3k__C1Pmyo-o8IUmaQfpKPqSEDBxf1G00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/XP9FIyGm4CNl_HH3lOecgO8YmifkuyMRH_4mcmoxmTA497KHsUzk_nahHYNaa9atxuLViWeHVMmFsk2kY2Os18_aNuqYkFUsSw6OUl1U0BGK3zQ_WFDMToeQsuvb0DJQKmXm2oLdP-Cw5nVbpTHqZiFJJmbdvNDIYAo2VoeKgZrbNGJxfidwYEIZjrcJYfMd4FReg2zgZBZ5G6aawrdntqQE_TuDx6OuoZRM3vCdTIM5tCnOD0NbZHifziqxvngZS3mEBq0-BFXzSVexGKfPrIoVi1xum0E-aI-NL9Vq_hd_bRoih_Fkcna1h9ikn1JH0qyO9_DZiQ9MJx_g0m00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/POxDRi9038Jl-nHMxhH9MauL4eYVAX82rFPMUd2p9eq8NkHrG5N5kzS9vLJvCBBc6u_7KL6Kpxx6oXsmvftWWM0s7SmngjDQ6uAD1D-MMWU6eWEYYgsja2k9bGI-2Bt9TBrQ5BFvwgsOB6_MBeHEDbWHPAx4OtzcQJUWFNfKyf2d-N2GFhY6AcBl09w5Y6444-iyqPPV31h1goBxpszdp1zvVHj-BCAavo1xQ93x7G2z5uhHWacMtlLpdpycJxqPIKxsrVj_A4kJZuwvk8iRMycrunS0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/ROxD2i8m48JlUOgb3s2hUBDA_S5ZBnx5mz8iDJHDOBDQHFhkrgGtPTd3p7mCKmL15ZTeWwqgWxmixLIIf-aPUtWhW0CsNSl-uVJHMyymt8tGv9-zanfxWZqRj6fKPJvtY15BSFaA3JN9uBcRYsEZInPOT543eDPC8S0MicMnY9UlrjacXe7uIGpNNsXPPBV4DDQGa__C38tJn8gSJaC-)



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
![Diagram](https://www.plantuml.com/plantuml/svg/TOx12i8m44Jl-OgbthM9eaXLQbjx4lyXcAK4sqGsgIBYlrlIW8Z8ih0x0pClTrwIDtUbPSCspZzQtB7nhOObsS6J0HZqTqkNS0CKydnfoFP6bRQr19F3l1Pr5RoZDXXLlbujAn7KsXeVrRHQhFPyK5_inJQpMEcrRn7AtddRmIcs5P9SXFcYk9Bk93qYZLIAq3dOGiBJQPYPM2HPC1tI3ObdeU-JuF1iZVgVmNypH1QPSpHgX7e3)



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
![Diagram](https://www.plantuml.com/plantuml/svg/VO-x3i8m34NtV8K5AnAq21OUAgzEY8KHCHXYbQXj4YM62g7-EwKD2mE39J_ElROJp-XOLr9X9kQUdmKjHLTkct1Omai0U78FScqAiCPhdZbprt9Z2kEWdwRfU3TgPtkbANHtqqaq-dHhKOlvC7Ypue9WS_TiIZWOIJwiQyqrSMLS3WNgi0ojZU3KO5UdB2kZOG6zbRLmx4wAUkVP5up_WV4Nb1Su-HjQQW29Z1VqD80VuJOCEj7dWuIqx2vz0m00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/VOvH2u8m58NVzoikzPwfHOKMLbellVKBXhl8S6soJIJ2_vwRWlGIbmldt0lVEPcnL5lPCKuhaXhx5dWYeys7rVG57m9GQTKsNW5SQ5axBzbL2QLXMUnls-BWVmykSRf6nIwFe-7QavwamOIst0g4fpCCxevgfZXFbsWxfMieHMiiwYcHCgRH63Z28bol_0JHPf7ufrGCmrb6iumJd_xRdg4fDMyiLzBnV0Ku_s6v-XbADhRy0W00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/TL7BJiCm4BpdArRXYjBKvL54GOKyJZr0U-20E3ZrDhNgsf5jY0hAl-CwYLIrYgKzU6OyinhFZQNQoffnMWOpOmy2duFschhHT0z_0S0hNUzAhRubIvHG6kejj-XmYRPMUkSrbwghR9AJF7LSuyQW_a4z9CtzwQGHevOMrE2WyJI_pHuyj-0IEvHaz-c4z1uRhh6cGWmd9cbApZsIEp8bK-_H1BDHruZbLY2iZXS6nG6MIc1NaxVlUs3xtowECgRH67Y2S1n7SJIEuX6v2HyzkQdXaw5PQrvPhkHHb7VRXb-jfCRYGlFXi9LliLKr9ybSMjIIYe5uSXfFg-h2-yLXfzu0p2rWjhH2H_V_SGrdpzwKiQN6rVkYNwa9vYXPsyq_)



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
![Diagram](https://www.plantuml.com/plantuml/svg/TL0xJyCm4DxpAqvXHJHs6nXQK9-Us41YG0nEV2fMWntP3b65-jzn71TGI7swmT_ZNalhk76g5PBlauLrnmeValwxzMdu1tmb06jU7lP6DqfiTAKDNB5L5vvHw5fj3a4rejjD6MNRm3rAXH4b-Ms-oJnwycdHVAAvL825Dommert40fs-lkYVxdAM3_rtQy9MlV-KB2PnRoTTXS2QgZh2KmS9Y4U89mbDpXlNHekcT5Ahs9iBOT1Qk8UKP3SX9dIMpWFPOa7WzR-4PEdRZuAEAiXP8OendcRfDTXtNgC71NUyu1Q3OtWSWROqiWuZU_yB5l0iqVoPy7UIUJpE4fNeb_y6)



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
![Diagram](https://www.plantuml.com/plantuml/svg/ZPHVIyCm5CNV-oakzTNLjb7P6CBiFn0KH0U2GqRQXAsOjI7D72hxxZPhnsgRLX-Rt7FkkRyadHKI2vdjI8fNXambep1V2qf7yvGAUA4nt7BEqWJBDC-CgWw-3O0qarHaLCAYM6DEuGOIbc_9EH1Q92BbghvSDE_gElDjsbIDHi1YjL9-x7Bn3cJpTV05I7AM2oKzYwBGzv0vFInZGWGj2hNXs9PjEPPzuLxMcwscmSDhlS5YM7ILZcrsWjxdc8276SuIAggq-qO-pFbIAYRjaFuulFOdFI7TWP0DiA1e3oHsBQTA12g7eotGZ5HsW6SgFihKJRshrJk3UhUXHrgzEwX7NQ84Iwn7wdb167azID7GkPUMJPPwM4Z16iI158x1WP4QkAuWyPABT8F5fwxELGTpV2DgvXWNj8FgiJO8l8Qhe8SRedLr_kFwL1iSNHN-bSYtl8Cy74TNuQJteeBFjeNynVN4xyJfZnueSgEW_-JK2Ar69xHjA5MhlJ6Z6Qb-Ipy0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/VPDHQy8m58NV-oj2VHtJf28EtT3Moc1i-BQ7CKPiBgvOcvB4oHZ-zxL9jfcPsDBIDESxDvpapgIYGjK7Lj9DD9NgiuAxo0mNxIFe3dr52DMW3bnizJT2AIss6y7tDSjunGNgvUDylXorSyVsaI0-G8IaItrfwJ6Qzcr5LQeAqCD-3Q8j1H9brLug47OfpXeANYl1gxUceZNOCfGn0LAYMnJZmRM--sGOJ_Ga0rc8ib4bhpj1PdYqwdWhsT6k6aOlvqPu45_zjtZKSeJZrrESU74Sn8cB9rwS1F7a1mTLC1zBkfNBTzf0-vDHHTTKmfbRHnkduqd8tGl4MpiC98ml9FoiOVHalAp6E7eYnjw8hSTln0OdNXm7SUBYYHSdGJnnyQ4NJuBuy2_NhWSQ6sMXEw6LzR9nFifk_27Upv7PQEcUKUV4EUVdSgqqNUJBzEA6hJYltDroidUIT7APs7wUGSrCntu3)



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
![Diagram](https://www.plantuml.com/plantuml/svg/VP91Jy9048Nl_HMJUXMarHWDCO4KYIJOD7BWG3oitGbkQ7SskmiS3F_TRRTLXEAjkpFlUpDlEpAMQIltNB1rO8Kj45weH4ZHxabl0b-1hm1WjiXWPJwPGdY2lA0jlmQE9jT2MK7INOOpQL5BjB10lHCvGgPf9pZgy7tO47ezA8bZMPsbDu4zaxK3dFAMunGIaXBpwYOSrZsr75OdhGdxSBE_LZLlTZWoA7uC6ESQZQaKqMFSZ-uV-b5_S1FVDV0JQft5V9mUM_jFJLktAwmwWL5u5irIJ0MyrI8_dvkEcKlwWGEqKHjBcgtnZ9YE5ot9LJQMr4NQu7oUIIF9aXPICFKVesEdUQrezKeBUJcIk6k8p4j-7spjObNDK-LKaAwwhfvlf_5qqlr22PMg2jM4Vw8uNid33y489VV_ypS0)



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
