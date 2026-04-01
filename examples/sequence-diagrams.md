# Sequence Diagrams

Sequence diagrams show how multiple entities interact over time. They're ideal for:

- **API request/response flows**: Client → Server → Database
- **Object collaboration**: How objects work together in a scenario
- **Protocol exchanges**: Authentication handshakes, message protocols
- **Multi-step processes**: Order processing, user registration flows

Unlike state diagrams (which track ONE entity), sequence diagrams show MULTIPLE participants exchanging messages.

## Core Concepts

**Participant**: An entity that sends or receives messages. Can be a user, service, database, etc.

**Message**: Communication between participants, shown as arrows.

**Activation**: A vertical bar showing when a participant is actively processing.

**Grouping Blocks**: Combined fragments for control flow (alt, opt, loop, par, critical).

## Your First Sequence Diagram

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram(title="Simple Request")
p = d.participants
e = d.events

client = p.participant("Client")
server = p.participant("Server")
d.add(client, server)

d.phase("Request", [
    e.message(client, server, "request()"),
    e.reply(server, client, "response()"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGZEp2q0Ka6fXQMfnILS1K39pEJCWiIy4WNddCpKF5IXuDIYijGYBeYCWguTL431Ig48Oe269XTK22W9LGQIB2x8pojE1SewfEQb06q70000)



## Participant Types

Different shapes communicate the role of each participant:

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram(title="Participant Types")
p = d.participants
e = d.events

# Standard box
service = p.participant("Service")

# Stick figure - human users
user = p.actor("User")

# System boundary
api = p.boundary("API Gateway")

# Control logic
handler = p.control("Handler")

# Domain entity
order = p.entity("Order")

# Database cylinder
db = p.database("PostgreSQL")

# Message queue
mq = p.queue("RabbitMQ")

# Multiple instances
workers = p.collections("Workers")

d.add(service, user, api, handler, order, db, mq, workers)

d.phase("Flow", [
    e.message(user, api, "request"),
    e.message(api, handler, "process"),
    e.message(handler, order, "create"),
    e.message(handler, db, "save"),
    e.message(handler, mq, "publish"),
    e.message(mq, workers, "distribute"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LP31JWCn34Jl_WghTtw00sfFBHA8bXPnH4vYGKH8jhPJj7zV5srXESuyJsQKfHg9zQy2bgqmRbtbc0UgXeTnO8LXvknPJZaoKBGc-A8i45glYMJ4nMfxZsio_gPnWQJe-ctI45irQGKtL5Fn55Ul6_59aej4He7KovlQk_1-zm37pftncKB8zhZpV2aSBRUg-DhaaqNXKeytT_CUl4LXZwh1tFMZgTWF1ccHLU7gEFoPuIWAUs9E_XOvLZhzWzTrbqTxA5a_uDToFErqchAQvD3zxINNvBzz1W00)



### Bulk Participant Creation

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

client = p.participant("Client")
server = p.participant("Server")
db = p.participant("Database")
d.add(client, server, db)

d.phase("Flow", [
    e.message(client, server, "request"),
    e.message(server, db, "query"),
    e.reply(db, server, "result"),
    e.reply(server, client, "response"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIe0qfd9cGM9UIKApZcPgNabA4B1gKLbgKKeGYw99Ob9YSMfN13b2hfsK5KALWf5gOMbgSKbN501e1HCDL0IA5LKoGKNGDLNN9g3h0rgDbYc83yFQ9j3QbuAqC40)



## Messages

### Basic Messages

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

a = p.participant("Alice")
b = p.participant("Bob")
d.add(a, b)

d.phase("Messages", [
    # Solid line, filled arrow (synchronous)
    e.message(a, b, "hello()"),

    # Dotted line (response/return)
    e.message(b, a, "hi back", line_style="dotted"),

    # Open arrow head (asynchronous)
    e.message(a, b, "async event", arrow_head="open"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIe0qfd9cGM9UIKAZZcPoQae8axvILnWKGLTEn17mKeX8pKd9rz3aml4qmMAGgI1ufaAIOd9sJ3bCL3bYSMLUSaAgMMfUILS3gbvAK0x0G00)



### Self-Messages

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

service = p.participant("Service")
d.add(service)

d.phase("Internal", [
    e.message(service, service, "internal processing"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIe0qfd9cGM9UIKAmQb5PPd9gLnGMa7N3YQaOAMGcLUIMfINcADGK9IVd5fSd9cNpkMGcfS2D0G0)



### Bidirectional Messages

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

a = p.participant("A")
b = p.participant("B")
d.add(a, b)

d.phase("Sync", [
    e.message(a, b, "sync", arrow_head="bidirectional"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIe0qfd9cGM9UIKAZYWy9ov71HjTEmKd1Ik5uigyP2w7rBmKe1O0)



## Activation (Processing Bars)

Show when a participant is actively processing:

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram(title="Activation Bars")
p = d.participants
e = d.events

client = p.participant("Client")
server = p.participant("Server")
db = p.database("Database")
d.add(client, server, db)

d.phase("Request", [
    e.message(client, server, "request()"),
    e.activate(server),
    e.message(server, db, "query()"),
    e.activate(db),
    e.reply(db, server, "results"),
    e.deactivate(db),
    e.reply(server, client, "response()"),
    e.deactivate(server),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/PT0z3i8m30NWtQVm20CNO43bvmQSm3GU8eKqs4ubRez5qzAABKg-zsobKoEn-anWqHBZkRSuaiKXuuL4eVXhx6EXR7XDaRDjhkui8mi4CdgGCjxQ0IQBXrCZU4JXLsMrtHve6i9pl177SzwvOtclyTAze6sxrcGAWVy3l_wsrfUN8IlxW5MYxTDn3lub7m00)



### Colored Activation

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

a = p.participant("A")
b = p.participant("B")
d.add(a, b)

d.phase("Flow", [
    e.message(a, b, "process"),
    e.activate(b, color="yellow"),
    e.reply(b, a, "done"),
    e.deactivate(b),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIe0qfd9cGM9UIKAZYWy9ov71Lqx1IS5AuM2elparE9YhiJaaioon99KeA1oPMfEJduvbnD8ZIDGJKf-NYfNIYf22PT3QbuAq0e0)



### Create and Destroy

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram(title="Lifecycle")
p = d.participants
e = d.events

factory = p.participant("Factory")
worker = p.participant("Worker")
d.add(factory, worker)

d.phase("Lifecycle", [
    # Create shows the participant appearing
    e.create(worker),
    e.message(factory, worker, "new()"),
    e.message(factory, worker, "process()"),
    e.reply(worker, factory, "done"),
    # Destroy shows X on lifeline
    e.destroy(worker),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/ROun2iCm40HxlUBAfCW7N0HNgTAd5gSrY2WwSRfWz7kha0g3ovrPbbshURN_BpcBba3lk84R9xZIUUHOV3PwUJRHTc8VqI_KiS8RPXf5UZm7eOKozjlzqXGLHgtT3jJbx2qK9CC5L5DfStz53lti0G00)



## Return Messages

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

client = p.participant("Client")
server = p.participant("Server")
d.add(client, server)

d.phase("Flow", [
    e.message(client, server, "getData()"),
    e.activate(server),
    e.return_("data"),
    e.deactivate(server),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIe0qfd9cGM9UIKApZcPgNabA4B1gKLbgKLS41a5NJkeW8ALGdfgYKjYIQA69bTYSabcMM99AannKMf9QL6UGWfGbYib5LtM8JKl1MWn0000)



## Grouping Blocks

### Alt (If/Else)

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram(title="Login Flow")
p = d.participants
e = d.events

user = p.actor("User")
api = p.boundary("API")
db = p.database("DB")
d.add(user, api, db)

d.phase("Login", [
    e.message(user, api, "login(user, pass)"),
    e.message(api, db, "verify credentials"),
])

d.if_("valid credentials", [
    e.message(db, api, "user found"),
    e.message(api, user, "200 OK + token"),
], "invalid", [
    e.message(db, api, "not found"),
    e.message(api, user, "401 Unauthorized"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/TP112y514CNlyodUaL1_Sd8GaXB5nGSOTh1PkzgTF_7fxKgASfd3Usz-yvfHKevQdnsfLITOXeFrcBbm8zvfYDWaYRGDjJSSxnYlvsHOUSj9C9rGST4P5Xq3kBBSgBFMneLJQbBHipsTPFSgqUxls4KnujMoIyHESMLdpPUAalz02mxxKY0RRzxhx02zgi9gWHOqdCIJk5pA-XVm1-A3_c7qgousdcizXcWVOaXoQ9H7_iaJ)



### Opt (Optional)

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

client = p.participant("Client")
cache = p.participant("Cache")
server = p.participant("Server")
d.add(client, cache, server)

d.phase("Lookup", [
    e.message(client, cache, "get(key)"),
])

d.optional("cache hit", [
    e.message(cache, client, "cached value"),
])

d.phase("Fetch", [
    e.message(client, server, "fetch()"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LOun3eCm40JxUyMLKF012eJ44_82ooon5STOvcmflu_9KOJgfDdPrSs7c2pb7IYrwwrF9WelmIFA7HdhS2CFv8fCwl8mgS8ZFo7T2v-UzYHiVz1v8Rw4qzJEgEdArOG2Gbp_rdI-EHl4kgwdkUNjqIy0)



### Loop

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram(title="Batch Processing")
p = d.participants
e = d.events

processor = p.participant("Processor")
db = p.database("Database")
d.add(processor, db)

d.loop("for each item", [
    e.message(processor, db, "fetch next"),
    e.reply(db, processor, "item data"),
    e.message(processor, processor, "process"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/NO_H3S8m34J_FSKjm0BzG1LYWAxWfYvOIfCeCHBZunPe4J_MoNvt9_VDkDfZYMHgKN1X2tSCDGTfJTEDYfyrQE5attMkDB7no4rm_GYAEHVCkKBO0zHa8Hm6dCuxYWwph2r9dkRGldVcC7HR1jQY_w1VgBmrIPgez-6Vl000)



### Par (Parallel)

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram(title="Parallel Requests")
p = d.participants
e = d.events

client = p.participant("Client")
service_a = p.participant("Service A")
service_b = p.participant("Service B")
d.add(client, service_a, service_b)

d.parallel([
    e.message(client, service_a, "request A"),
], None, [
    e.message(client, service_b, "request B"),
])

d.phase("Responses", [
    e.reply(service_a, client, "response A"),
    e.reply(service_b, client, "response B"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/RP0n3i8m34Ltd-AhEnTWG4su0883e2XuY6JIuhYSdqIj52frjFt-i-MnM51RtaAMJ1Yte4641NV-B5oiq5pdAQOvPCDL4cVRjOO7wpT5XXiG2hRgwOuXluDyWn2d71VL9iQs0QTBD-4CNO-18vR2EEJy7-U9yukweM9Re35bddArEEhHGy3JM3NrDpy0)



### Critical (Atomic)

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram(title="Transaction")
p = d.participants
e = d.events

api = p.participant("API")
db = p.database("Database")
d.add(api, db)

d.critical("atomic operation", [
    e.message(api, db, "BEGIN"),
    e.message(api, db, "INSERT order"),
    e.message(api, db, "UPDATE inventory"),
    e.message(api, db, "COMMIT"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/ROzB2W8n44JtEKLVm0kua1cT85dC1uq7Q9Ci6cQIq6a5RsyKSPLDKL3lBQehWYoFRLL2iWQmZB6W4qfHvRgGeunHe5-CyYXunn9W-1Nbc2g1Aw2aZHoa71Y_BdmCs1t-BEpXgCzcQYvckkgBXSG-S1EuBKDlDL1yXYY9NqteD8-ZiIf4hxeQzTGR)



### Break

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

client = p.participant("Client")
api = p.participant("API")
d.add(client, api)

d.phase("Request", [
    e.message(client, api, "request"),
])

d.break_("validation failed", [
    e.message(api, client, "400 Bad Request"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIe0qfd9cGM9UIKApZcPgNabA4AE0PvS4645NJiGJy5AeIYri3Irk8GhgIWrCLkXB34dCoMn93C_Jo4jCJCdDOLB0QmEg1ogqKh1nC10mIanHI48gZCrBuNB0KW07G00)



### Custom Group

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

client = p.participant("Client")
auth = p.participant("Auth")
d.add(client, auth)

d.phase("Authentication", [
    e.message(client, auth, "redirect"),
    e.reply(auth, client, "code"),
    e.message(client, auth, "exchange code"),
    e.reply(auth, client, "access token"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/ROyn3i8m34NtdC8NO67iW8fw00w062p7QYsA4oMEnF5nep8WkjZMU_yF7gjXiVPQG_Oj91dLO5g5rNxGjTaIvf9QxgTh8JH92lVR1iwF07iFJfUUWG4AHobCvguJDtjc04gHZphyfWLrvc_WhuX4N2jOUh86rXX67_x21m00)



## Notes

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

client = p.participant("Client")
server = p.participant("Server")
d.add(client, server)

# Note on a participant
d.note("Initiates request", target=client)

d.phase("Exchange", [
    e.message(client, server, "request"),
    # Note over a participant inside a phase
    e.note("Handshake complete", over=client),
])

d.phase("Response", [
    e.message(server, client, "response"),
])

# Note on the right side
d.note("Processing done", target=server, position="right")

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/NOzD2i9038NtSueSG2_GXHJSw4xm14FxR8DjCavIp-_KZeAk0k_d8wyrZzcNUGgfNEuuHN4wJWpn7-cA_4GEeWxAF8nEUgkvXix2pj5XbF5OO1usX_Q7MgJcQxqHkcfRQ5SZ3PsYz3R6EwZJEKrmXDekd4fSEPPK37-_V22Nh1tCM0RgLH1QI5_slG00)



### Note Shapes

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

a = p.participant("A")
b = p.participant("B")
d.add(a, b)

d.phase("Flow", [
    # Standard note
    e.note("Regular note", over=a, shape="note"),

    e.message(a, b, "message"),

    # Hexagonal note
    e.note("Hexagonal", over=b, shape="hnote"),

    # Rectangular note
    e.note("Rectangle", over=a, shape="rnote"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/ROun2iCm40HxlM8_a0-eC9QgrFd18Lyk0kaaf3Fu-N5AcrJBCikmwpGQjjVY-favvKvg29SMdJPZZ2mVGtiZUBnOza83F-027WiYF2hFISAtUVHuya7IbCe_Kp9IAUnMrkqyyWK0)



## Dividers and Spacing

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram(title="Phased Flow")
p = d.participants
e = d.events

client = p.participant("Client")
server = p.participant("Server")
d.add(client, server)

d.divider("Phase 1: Setup")

d.phase("Setup", [
    e.message(client, server, "init()"),
    e.reply(server, client, "ready"),
])

d.divider("Phase 2: Processing")

d.phase("Processing", [
    e.message(client, server, "process()"),
])

d.delay("waiting for external system")

d.phase("Complete", [
    e.reply(server, client, "complete"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/TP1D2y8m38Rl_HKvwi7XnwrG6GYU1_w2iaKDT6r9C-UWFzxA1YBeCU_xv0caJc9PXjuf8N48pTqcxE3imgXYQQYbQBt0oH5w-Oeko0zaPSoy13jT8XaY6ADc73R7XG8Dv4bMQxNCfLaO3OoscrJEXstE7zrUGyEXnPJ8t_uuummKRLLLeoLvezV0W4z1zjP1cf9WNzfVXzlGHuU2gaRVbH-y0000)



## References

Link to other diagrams:

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

client = p.participant("Client")
auth = p.participant("Auth Service")
api = p.participant("API")
d.add(client, auth, api)

d.phase("Auth", [
    e.message(client, auth, "authenticate"),
])

d.ref(client, auth, label="See: Authentication Flow Diagram")

d.phase("Authorized", [
    e.reply(auth, client, "token"),
    e.message(client, api, "request + token"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/NOyn3i8m34NtdCBg2bmW0se5GkfMgGT0LZ1WaIPjufJh4o03ORBy_hU_tKR186coQiwL3S_e10wMoKc5cYx97KOAAnjg02EymRc0ojeDlVfkWDs-ie46p6rMsA2G2dG5lr8eWTj_yqYaFwnCi7Tmilu9HyPRm4bL_XnMOZM8Vv3xlMBeCmsq98e2cwAtv2xvznS0)



## Participant Boxes

Group related participants:

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram(title="System Architecture")
p = d.participants
e = d.events

user = p.actor("User")
web = p.participant("Web App")
api = p.participant("API")
worker = p.participant("Worker")
db = p.database("Database")
cache = p.participant("Cache")

d.add(user)
d.box("Frontend", web, color="LightBlue")
d.box("Backend", api, worker, color="LightGreen")
d.box("Data Layer", db, cache, color="LightYellow")

d.phase("Flow", [
    e.message(user, web, "click"),
    e.message(web, api, "request"),
    e.message(api, cache, "check cache"),
    e.message(api, db, "query"),
    e.reply(db, api, "result"),
    e.reply(api, web, "response"),
    e.reply(web, user, "display"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/NP71JiCm38RlUGghd7c17T0w9X3I3aW8JPoGcreqQfO4nn7qxN7BMaelaVt_yUS_oZuBifIBD-B44xmCMUW2DTlE2LafJAQ9tr0zS0n2eQtWvkG-EZduGWOWwRIpBc4GgCxKG9rI1PX1wtUjZOw00duX1xJzYl78H643gP-VDievSa_y7tH4GJZXG3optiZx-AMZhLeDPeBZjTZWxj5sjD3GIcHupRfWFE3sRauEEx3UsTxClLeQJcMcpq9PpDYfE077sntP7ko4lrfp17LrX0Up22jOBdvX_UrMFSMWwLVhfuGxQ5rE7WUprqVep_q0)



## Autonumbering

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram(autonumber=True)
p = d.participants
e = d.events

a = p.participant("A")
b = p.participant("B")
c = p.participant("C")
d.add(a, b, c)

d.phase("Numbered", [
    e.message(a, b, "first"),
    e.message(b, c, "second"),
    e.message(c, a, "third"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LSsx3S0W303HtbDuWIoG8k8p2G6YM0e6WTa_fgHyrvmP4hhCya6OKdcMEtTecYXI2oneDxbD7YmU5peyyQ4-1DoYLuuSAoVmorOjB_K49dFIrGy0)



### Autonumber Control

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

a = p.participant("A")
b = p.participant("B")
d.add(a, b)

d.autonumber(start=10)

d.phase("Numbered", [
    e.message(a, b, "numbered 10"),
    e.reply(b, a, "numbered 11"),
])

d.phase("Unnumbered", [
    e.message(a, b, "not numbered"),
])

d.phase("Resumed", [
    e.reply(b, a, "numbered 12"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIe0qfd9cGM9UIKAZYWy9wx4qfBylDBSfDGY1KC3BaS5NJi59mKh1OXGQWf8q0aaw8WYQ8YihxWalm19Ptu9N26oggBKujBSL6o66N4vfEQb01qA0000)



### Hierarchical Autonumber

For complex diagrams, use multi-level numbering (1.1.1, 1.1.2, 2.1.1, etc.):

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

client = p.participant("Client")
server = p.participant("Server")
db = p.participant("Database")
d.add(client, server, db)

# Start with hierarchical format
d.autonumber(start="1.1.1")

d.phase("Login", [
    e.message(client, server, "login"),       # 1.1.1
    e.message(server, db, "verify"),          # 1.1.2
])

d.phase("Confirmed", [
    e.reply(db, server, "confirmed"),       # 2.1.1
    e.reply(server, client, "token"),       # 2.1.2
])

d.phase("Data", [
    e.message(client, server, "request"),     # 2.2.1
    e.message(server, db, "query"),           # 2.2.2
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/RL1R3i902FpVKt01JVpjXwcF6tW2kgM6sBALiYQzlIIkfZKD7uGPPfXGJuPgUUZ3w9qZZoW6bvv9R0NTI5-aA-YAXWrE531RaZmqf73OUuMF7dR78eCA-dHd2MLquYjsoX7kvgKBIuHJ-AqiVMAIZdMWTk5LpbLWwK7oRtJUYgFqp3JPTY2dT0urIUkFUGC0)



Use level `"A"` to increment the first digit, `"B"` for the second. When a level is incremented, all digits to the right reset to 1.

## Participant Ordering

Control left-to-right order:

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

# Order determines position (lower = leftmost)
db = p.database("Database")
api = p.participant("API")
client = p.participant("Client")
d.add(db, api, client)

d.phase("Flow", [
    e.message(client, api, "request"),
    e.message(api, db, "query"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKf9B4bCIYnELN21CVABKbAB58ov2e0gCfCp2nBpIXGS0poXuaOeuiuvcQb02Y9bo0Nbwjg1DLWf5AKMbgOMbt21U411k1LM2a3neaekXzIy5A0Z0000)



## Message Styling

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

a = p.participant("A")
b = p.participant("B")
d.add(a, b)

d.phase("Styled", [
    # Colored message
    e.message(a, b, "important"),

    # Response
    e.reply(b, a, "response"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIe0qfd9cGM9UIKAZYWy9ov71TrevQBKb5XTEmKd1Ik5pDo2_A8Ie1oN4r0cAJy7BEC8b2bABIx8pojEvN98pKi16Wi0)



## Hide Unlinked Participants

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram()
p = d.participants
e = d.events

a = p.participant("Active")
b = p.participant("Also Active")
unused = p.participant("Unused")  # Won't appear if unlinked
d.add(a, b, unused)

d.phase("Hello", [
    e.message(a, b, "hello"),
])

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuSh8J4bLACtBoSpBJatXAW2APYPd5YJcbIWu9fTabgMY22avvXJdGoMK51AB5K3yU2mAG_DAYu76GMGKTEsG5IfOAMIavkJaSpcavgK0dG00)



## Complete Example: E-Commerce Checkout

```python
from plantuml_compose import sequence_diagram, render

d = sequence_diagram(title="Checkout Flow")
p = d.participants
e = d.events

user = p.actor("Customer")
web = p.boundary("Web UI")
api = p.control("API")
cart = p.entity("Cart")
payment = p.participant("Payment Service")
inventory = p.participant("Inventory")
db = p.database("Database")
d.add(user, web, api, cart, payment, inventory, db)

d.phase("Checkout", [
    e.message(user, web, "Click Checkout"),
    e.message(web, api, "POST /checkout"),
    e.activate(api),
    e.message(api, cart, "getItems()"),
    e.reply(cart, api, "items[]"),
])

d.divider("Validation")

d.loop("for each item", [
    e.message(api, inventory, "checkStock(item)"),
    e.reply(inventory, api, "available"),
])

d.divider("Payment")

d.phase("Charge", [
    e.message(api, payment, "charge(total)"),
])

d.if_("payment success", [
    e.reply(payment, api, "confirmed"),
    e.message(api, db, "createOrder()"),
    e.message(api, inventory, "reserveItems()"),
    e.reply(api, web, "200 OK"),
    e.message(web, user, "Order Confirmed!"),
], "payment failed", [
    e.reply(payment, api, "declined"),
    e.reply(api, web, "402 Payment Required"),
    e.message(web, user, "Payment Failed"),
])

d.deactivate(api)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/TLF1Ji904BtlLuoSu60anfC91bDZqdY0YEZ1639i1zomxUBk5CFVErtRHGXUccRcpNjlthJZmEYvBgrYmvOW-oIzSJN3etNV2ZKx3raTs9NarTBLLO5-3xqtMi8yxm46aDV5F5VQLUoTXVjfhgWIiZramgosyZ3QRB5Yw4rnNqeJPkHtHbESRskBjdOqa5SxQJc_LmKoBZ4GFBGlgdC5btUj1xY5p1gzIKkejYu8iINjwMJs0bUwQyjwPeTCqNI3461ZMf1hufof3Fs1YfL4OPhg-uSQZU0LhH5VnbKm6Ydht1PM4XUX_emm1T2IfZs48AhFsEbDlm4D17Le9ndSeR6uj2HX5erO5vqejQGdmKLgz6lgisEq0uMMOTjEXLfh2a6qJgUIeXnmPNn9nS5sbtNJzIH1JNn1lZyulvYd89pKnPOmwJZNmo5CdgHnE4iwuYr4RiWw5nUAh2Xt2wmaZcZjN_y5QMkgl_QJyCtmEkNtJ5-ryH5sraQ7U_mLRD8lwEX36KjDVfWV)



## Quick Reference

| Method | Description |
|--------|-------------|
| `p.participant(name)` | Create participant |
| `p.actor(name)` | Stick figure participant |
| `p.boundary(name)` | Boundary participant |
| `p.control(name)` | Control participant |
| `p.entity(name)` | Entity participant |
| `p.database(name)` | Database (cylinder) |
| `p.queue(name)` | Queue participant |
| `p.collections(name)` | Multiple instances |
| `d.add(...)` | Register participants |
| `e.message(a, b, label)` | Send message |
| `e.reply(a, b, label)` | Dotted return message |
| `e.return_(label)` | Return from activation |
| `e.activate(p)` | Start activation bar |
| `e.deactivate(p)` | End activation bar |
| `e.create(p)` | Create participant |
| `e.destroy(p)` | Destroy participant |
| `e.note(text, over=p)` | Note inside phase |
| `d.note(text, target=p)` | Note on diagram |
| `d.ref(*p, label=text)` | Reference another diagram |
| `d.phase(label, [...])` | Group events in a phase |
| `d.divider(title)` | Section divider |
| `d.delay(msg)` | Delay indicator |
| `d.if_(label, [...])` | If/else block |
| `d.optional(label, [...])` | Optional block |
| `d.loop(label, [...])` | Loop block |
| `d.parallel([...])` | Parallel block |
| `d.critical(label, [...])` | Atomic block |
| `d.break_(label, [...])` | Break block |
| `d.box(name, *refs, color)` | Group participants |
| `d.autonumber(start=n)` | Control numbering |
| `render(d)` | Render to PlantUML text |
