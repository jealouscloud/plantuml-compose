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
from plantuml_compose import sequence_diagram

with sequence_diagram(title="Simple Request") as d:
    client = d.participant("Client")
    server = d.participant("Server")

    d.message(client, server, "request()")
    d.message(server, client, "response()")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGZEp2q0Ka6fXQMfnILS1K39pEJCWiIy4WNddCpKF5IXuDIYijGYBeYCWguTL431Ig48Oe269XTK22W9LGQIB2x8pojE1SewfEQb06q70000)



## Participant Types

Different shapes communicate the role of each participant:

```python
from plantuml_compose import sequence_diagram

with sequence_diagram(title="Participant Types") as d:
    # Standard box
    service = d.participant("Service")

    # Stick figure - human users
    user = d.actor("User")

    # System boundary
    api = d.boundary("API Gateway")

    # Control logic
    handler = d.control("Handler")

    # Domain entity
    order = d.entity("Order")

    # Database cylinder
    db = d.database("PostgreSQL")

    # Message queue
    mq = d.queue("RabbitMQ")

    # Multiple instances
    workers = d.collections("Workers")

    d.message(user, api, "request")
    d.message(api, handler, "process")
    d.message(handler, order, "create")
    d.message(handler, db, "save")
    d.message(handler, mq, "publish")
    d.message(mq, workers, "distribute")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/LP31JWCn34Jl_WghTtw00sfFBHA8bXPnH4vYGKH8jhPJj7zV5srXESuyJsQKfHg9zQy2bgqmRbtbc0UgXeTnO8LXvknPJZaoKBGc-A8i45glYMJ4nMfxZsio_gPnWQJe-ctI45irQGKtL5Fn55Ul6_59aej4He7KovlQk_1-zm37pftncKB8zhZpV2aSBRUg-DhaaqNXKeytT_CUl4LXZwh1tFMZgTWF1ccHLU7gEFoPuIWAUs9E_XOvLZhzWzTrbqTxA5a_uDToFErqchAQvD3zxINNvBzz1W00)



### Bulk Participant Creation

```python
from plantuml_compose import sequence_diagram

with sequence_diagram() as d:
    client, server, db = d.participants("Client", "Server", "Database")

    d.message(client, server, "request")
    d.message(server, db, "query")
    d.message(db, server, "result")
    d.message(server, client, "response")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIe0qfd9cGM9UIKApZcPgNabA4B1gKLbgKKeGYw99Ob9YSMfN13b2hfsK5KALWf5gOMbgSKbN501e1HCDL0IA5LKoGKNGDLNN9g3h0rgDbYc83yFQ9j3QbuAqC40)



## Messages

### Basic Messages

```python
from plantuml_compose import sequence_diagram

with sequence_diagram() as d:
    a, b = d.participants("Alice", "Bob")

    # Solid line, filled arrow (synchronous)
    d.message(a, b, "hello()")

    # Dotted line (response/return)
    d.message(b, a, "hi back", line_style="dotted")

    # Open arrow head (asynchronous)
    d.message(a, b, "async event", arrow_head="open")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIe0qfd9cGM9UIKAZZcPoQae8axvILnWKGLTEn17mKeX8pKd9rz3aml4qmMAGgI1ufaAIOd9sJ3bCL3bYSMLUSaAgMMfUILS3gbvAK0x0G00)



### Self-Messages

```python
from plantuml_compose import sequence_diagram

with sequence_diagram() as d:
    service = d.participant("Service")

    d.message(service, service, "internal processing")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIe0qfd9cGM9UIKAmQb5PPd9gLnGMa7N3YQaOAMGcLUIMfINcADGK9IVd5fSd9cNpkMGcfS2D0G0)



### Bidirectional Messages

```python
from plantuml_compose import sequence_diagram

with sequence_diagram() as d:
    a, b = d.participants("A", "B")

    d.message(a, b, "sync", bidirectional=True)

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIe0qfd9cGM9UIKAZYWy9ov71HjTEmKd1Ik5uigyP2w7rBmKe1O0)



## Activation (Processing Bars)

Show when a participant is actively processing:

```python
from plantuml_compose import sequence_diagram

with sequence_diagram(title="Activation Bars") as d:
    client = d.participant("Client")
    server = d.participant("Server")
    db = d.database("Database")

    d.message(client, server, "request()")
    d.activate(server)

    d.message(server, db, "query()")
    d.activate(db)
    d.message(db, server, "results")
    d.deactivate(db)

    d.message(server, client, "response()")
    d.deactivate(server)

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/PT0z3i8m30NWtQVm20CNO43bvmQSm3GU8eKqs4ubRez5qzAABKg-zsobKoEn-anWqHBZkRSuaiKXuuL4eVXhx6EXR7XDaRDjhkui8mi4CdgGCjxQ0IQBXrCZU4JXLsMrtHve6i9pl177SzwvOtclyTAze6sxrcGAWVy3l_wsrfUN8IlxW5MYxTDn3lub7m00)



### Colored Activation

```python
from plantuml_compose import sequence_diagram

with sequence_diagram() as d:
    a, b = d.participants("A", "B")

    d.message(a, b, "process")
    d.activate(b, color="yellow")
    d.message(b, a, "done")
    d.deactivate(b)

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIe0qfd9cGM9UIKAZYWy9ov71Lqx1IS5AuM2elparE9YhiJaaioon99KeA1oPMfEJduvbnD8ZIDGJKf-NYfNIYf22PT3QbuAq0e0)



### Create and Destroy

```python
from plantuml_compose import sequence_diagram

with sequence_diagram(title="Lifecycle") as d:
    factory = d.participant("Factory")
    worker = d.participant("Worker")

    # Create shows the participant appearing
    d.create(worker)
    d.message(factory, worker, "new()")

    d.message(factory, worker, "process()")
    d.message(worker, factory, "done")

    # Destroy shows X on lifeline
    d.destroy(worker)

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/ROun2iCm40HxlUBAfCW7N0HNgTAd5gSrY2WwSRfWz7kha0g3ovrPbbshURN_BpcBba3lk84R9xZIUUHOV3PwUJRHTc8VqI_KiS8RPXf5UZm7eOKozjlzqXGLHgtT3jJbx2qK9CC5L5DfStz53lti0G00)



## Return Messages

```python
from plantuml_compose import sequence_diagram

with sequence_diagram() as d:
    client = d.participant("Client")
    server = d.participant("Server")

    d.message(client, server, "getData()")
    d.activate(server)
    d.return_("data")
    d.deactivate(server)

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIe0qfd9cGM9UIKApZcPgNabA4B1gKLbgKLS41a5NJkeW8ALGdfgYKjYIQA69bTYSabcMM99AannKMf9QL6UGWfGbYib5LtM8JKl1MWn0000)



## Grouping Blocks

### Alt (If/Else)

```python
from plantuml_compose import sequence_diagram

with sequence_diagram(title="Login Flow") as d:
    user = d.actor("User")
    api = d.boundary("API")
    db = d.database("DB")

    d.message(user, api, "login(user, pass)")
    d.message(api, db, "verify credentials")

    with d.alt("valid credentials") as alt:
        alt.message(db, api, "user found")
        alt.message(api, user, "200 OK + token")

        with alt.else_("invalid") as invalid:
            invalid.message(db, api, "not found")
            invalid.message(api, user, "401 Unauthorized")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/TP112y514CNlyodUaL1_Sd8GaXB5nGSOTh1PkzgTF_7fxKgASfd3Usz-yvfHKevQdnsfLITOXeFrcBbm8zvfYDWaYRGDjJSSxnYlvsHOUSj9C9rGST4P5Xq3kBBSgBFMneLJQbBHipsTPFSgqUxls4KnujMoIyHESMLdpPUAalz02mxxKY0RRzxhx02zgi9gWHOqdCIJk5pA-XVm1-A3_c7qgousdcizXcWVOaXoQ9H7_iaJ)



### Opt (Optional)

```python
from plantuml_compose import sequence_diagram

with sequence_diagram() as d:
    client = d.participant("Client")
    cache = d.participant("Cache")
    server = d.participant("Server")

    d.message(client, cache, "get(key)")

    with d.opt("cache hit") as opt:
        opt.message(cache, client, "cached value")

    d.message(client, server, "fetch()")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/LOun3eCm40JxUyMLKF012eJ44_82ooon5STOvcmflu_9KOJgfDdPrSs7c2pb7IYrwwrF9WelmIFA7HdhS2CFv8fCwl8mgS8ZFo7T2v-UzYHiVz1v8Rw4qzJEgEdArOG2Gbp_rdI-EHl4kgwdkUNjqIy0)



### Loop

```python
from plantuml_compose import sequence_diagram

with sequence_diagram(title="Batch Processing") as d:
    processor = d.participant("Processor")
    db = d.database("Database")

    with d.loop("for each item") as loop:
        loop.message(processor, db, "fetch next")
        loop.message(db, processor, "item data")
        loop.message(processor, processor, "process")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/NO_H3S8m34J_FSKjm0BzG1LYWAxWfYvOIfCeCHBZunPe4J_MoNvt9_VDkDfZYMHgKN1X2tSCDGTfJTEDYfyrQE5attMkDB7no4rm_GYAEHVCkKBO0zHa8Hm6dCuxYWwph2r9dkRGldVcC7HR1jQY_w1VgBmrIPgez-6Vl000)



### Par (Parallel)

```python
from plantuml_compose import sequence_diagram

with sequence_diagram(title="Parallel Requests") as d:
    client = d.participant("Client")
    service_a = d.participant("Service A")
    service_b = d.participant("Service B")

    with d.par("concurrent") as par:
        par.message(client, service_a, "request A")

        with par.else_("") as par2:
            par2.message(client, service_b, "request B")

    d.message(service_a, client, "response A")
    d.message(service_b, client, "response B")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/RP0n3i8m34Ltd-AhEnTWG4su0883e2XuY6JIuhYSdqIj52frjFt-i-MnM51RtaAMJ1Yte4641NV-B5oiq5pdAQOvPCDL4cVRjOO7wpT5XXiG2hRgwOuXluDyWn2d71VL9iQs0QTBD-4CNO-18vR2EEJy7-U9yukweM9Re35bddArEEhHGy3JM3NrDpy0)



### Critical (Atomic)

```python
from plantuml_compose import sequence_diagram

with sequence_diagram(title="Transaction") as d:
    api = d.participant("API")
    db = d.database("Database")

    with d.critical("atomic operation") as crit:
        crit.message(api, db, "BEGIN")
        crit.message(api, db, "INSERT order")
        crit.message(api, db, "UPDATE inventory")
        crit.message(api, db, "COMMIT")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/ROzB2W8n44JtEKLVm0kua1cT85dC1uq7Q9Ci6cQIq6a5RsyKSPLDKL3lBQehWYoFRLL2iWQmZB6W4qfHvRgGeunHe5-CyYXunn9W-1Nbc2g1Aw2aZHoa71Y_BdmCs1t-BEpXgCzcQYvckkgBXSG-S1EuBKDlDL1yXYY9NqteD8-ZiIf4hxeQzTGR)



### Break

```python
from plantuml_compose import sequence_diagram

with sequence_diagram() as d:
    client = d.participant("Client")
    api = d.participant("API")

    d.message(client, api, "request")

    with d.break_("validation failed") as brk:
        brk.message(api, client, "400 Bad Request")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIe0qfd9cGM9UIKApZcPgNabA4AE0PvS4645NJiGJy5AeIYri3Irk8GhgIWrCLkXB34dCoMn93C_Jo4jCJCdDOLB0QmEg1ogqKh1nC10mIanHI48gZCrBuNB0KW07G00)



### Custom Group

```python
from plantuml_compose import sequence_diagram

with sequence_diagram() as d:
    client = d.participant("Client")
    auth = d.participant("Auth")

    with d.group("Authentication", "OAuth2") as grp:
        grp.message(client, auth, "redirect")
        grp.message(auth, client, "code")
        grp.message(client, auth, "exchange code")
        grp.message(auth, client, "access token")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/ROyn3i8m34NtdC8NO67iW8fw00w062p7QYsA4oMEnF5nep8WkjZMU_yF7gjXiVPQG_Oj91dLO5g5rNxGjTaIvf9QxgTh8JH92lVR1iwF07iFJfUUWG4AHobCvguJDtjc04gHZphyfWLrvc_WhuX4N2jOUh86rXX67_x21m00)



## Notes

```python
from plantuml_compose import sequence_diagram

with sequence_diagram() as d:
    client = d.participant("Client")
    server = d.participant("Server")

    # Note on a participant
    d.note("Initiates request", of=client)

    d.message(client, server, "request")

    # Note spanning multiple participants
    d.note("Handshake complete", over=(client, server))

    d.message(server, client, "response")

    # Note on the right side
    d.note("Processing done", position="right", of=server)

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/NOzD2i9038NtSueSG2_GXHJSw4xm14FxR8DjCavIp-_KZeAk0k_d8wyrZzcNUGgfNEuuHN4wJWpn7-cA_4GEeWxAF8nEUgkvXix2pj5XbF5OO1usX_Q7MgJcQxqHkcfRQ5SZ3PsYz3R6EwZJEKrmXDekd4fSEPPK37-_V22Nh1tCM0RgLH1QI5_slG00)



### Note Shapes

```python
from plantuml_compose import sequence_diagram

with sequence_diagram() as d:
    a, b = d.participants("A", "B")

    # Standard note
    d.note("Regular note", of=a, shape="note")

    d.message(a, b, "message")

    # Hexagonal note
    d.note("Hexagonal", of=b, shape="hnote")

    # Rectangular note
    d.note("Rectangle", of=a, shape="rnote")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/ROun2iCm40HxlM8_a0-eC9QgrFd18Lyk0kaaf3Fu-N5AcrJBCikmwpGQjjVY-favvKvg29SMdJPZZ2mVGtiZUBnOza83F-027WiYF2hFISAtUVHuya7IbCe_Kp9IAUnMrkqyyWK0)



## Dividers and Spacing

```python
from plantuml_compose import sequence_diagram

with sequence_diagram(title="Phased Flow") as d:
    client = d.participant("Client")
    server = d.participant("Server")

    d.divider("Phase 1: Setup")

    d.message(client, server, "init()")
    d.message(server, client, "ready")

    d.space(30)  # 30 pixel gap

    d.divider("Phase 2: Processing")

    d.message(client, server, "process()")

    d.delay("waiting for external system")

    d.message(server, client, "complete")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/TP1D2y8m38Rl_HKvwi7XnwrG6GYU1_w2iaKDT6r9C-UWFzxA1YBeCU_xv0caJc9PXjuf8N48pTqcxE3imgXYQQYbQBt0oH5w-Oeko0zaPSoy13jT8XaY6ADc73R7XG8Dv4bMQxNCfLaO3OoscrJEXstE7zrUGyEXnPJ8t_uuummKRLLLeoLvezV0W4z1zjP1cf9WNzfVXzlGHuU2gaRVbH-y0000)



## References

Link to other diagrams:

```python
from plantuml_compose import sequence_diagram

with sequence_diagram() as d:
    client = d.participant("Client")
    auth = d.participant("Auth Service")
    api = d.participant("API")

    d.message(client, auth, "authenticate")

    d.ref(client, auth, label="See: Authentication Flow Diagram")

    d.message(auth, client, "token")
    d.message(client, api, "request + token")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/NOyn3i8m34NtdCBg2bmW0se5GkfMgGT0LZ1WaIPjufJh4o03ORBy_hU_tKR186coQiwL3S_e10wMoKc5cYx97KOAAnjg02EymRc0ojeDlVfkWDs-ie46p6rMsA2G2dG5lr8eWTj_yqYaFwnCi7Tmilu9HyPRm4bL_XnMOZM8Vv3xlMBeCmsq98e2cwAtv2xvznS0)



## Participant Boxes

Group related participants:

```python
from plantuml_compose import sequence_diagram

with sequence_diagram(title="System Architecture") as d:
    user = d.actor("User")

    with d.box("Frontend", color="LightBlue") as frontend:
        web = frontend.participant("Web App")

    with d.box("Backend", color="LightGreen") as backend:
        api = backend.participant("API")
        worker = backend.participant("Worker")

    with d.box("Data Layer", color="LightYellow") as data:
        db = data.database("Database")
        cache = data.participant("Cache")

    d.message(user, web, "click")
    d.message(web, api, "request")
    d.message(api, cache, "check cache")
    d.message(api, db, "query")
    d.message(db, api, "result")
    d.message(api, web, "response")
    d.message(web, user, "display")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/NP71JiCm38RlUGghd7c17T0w9X3I3aW8JPoGcreqQfO4nn7qxN7BMaelaVt_yUS_oZuBifIBD-B44xmCMUW2DTlE2LafJAQ9tr0zS0n2eQtWvkG-EZduGWOWwRIpBc4GgCxKG9rI1PX1wtUjZOw00duX1xJzYl78H643gP-VDievSa_y7tH4GJZXG3optiZx-AMZhLeDPeBZjTZWxj5sjD3GIcHupRfWFE3sRauEEx3UsTxClLeQJcMcpq9PpDYfE077sntP7ko4lrfp17LrX0Up22jOBdvX_UrMFSMWwLVhfuGxQ5rE7WUprqVep_q0)



## Autonumbering

```python
from plantuml_compose import sequence_diagram

with sequence_diagram(autonumber=True) as d:
    a, b, c = d.participants("A", "B", "C")

    d.message(a, b, "first")
    d.message(b, c, "second")
    d.message(c, a, "third")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/LSsx3S0W303HtbDuWIoG8k8p2G6YM0e6WTa_fgHyrvmP4hhCya6OKdcMEtTecYXI2oneDxbD7YmU5peyyQ4-1DoYLuuSAoVmorOjB_K49dFIrGy0)



### Autonumber Control

```python
from plantuml_compose import sequence_diagram

with sequence_diagram() as d:
    a, b = d.participants("A", "B")

    d.autonumber("start", start=10)
    d.message(a, b, "numbered 10")
    d.message(b, a, "numbered 11")

    d.autonumber("stop")
    d.message(a, b, "not numbered")

    d.autonumber("resume")
    d.message(b, a, "numbered 12")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIe0qfd9cGM9UIKAZYWy9wx4qfBylDBSfDGY1KC3BaS5NJi59mKh1OXGQWf8q0aaw8WYQ8YihxWalm19Ptu9N26oggBKujBSL6o66N4vfEQb01qA0000)



### Hierarchical Autonumber

For complex diagrams, use multi-level numbering (1.1.1, 1.1.2, 2.1.1, etc.):

```python
from plantuml_compose import sequence_diagram

with sequence_diagram() as d:
    client, server, db = d.participants("Client", "Server", "Database")

    # Start with hierarchical format
    d.autonumber("start", start="1.1.1")
    d.message(client, server, "login")       # 1.1.1
    d.message(server, db, "verify")          # 1.1.2

    # Increment first level (resets lower levels)
    d.autonumber("inc", level="A")
    d.message(db, server, "confirmed")       # 2.1.1
    d.message(server, client, "token")       # 2.1.2

    # Increment second level (resets third level)
    d.autonumber("inc", level="B")
    d.message(client, server, "request")     # 2.2.1
    d.message(server, db, "query")           # 2.2.2

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/RL1R3i902FpVKt01JVpjXwcF6tW2kgM6sBALiYQzlIIkfZKD7uGPPfXGJuPgUUZ3w9qZZoW6bvv9R0NTI5-aA-YAXWrE531RaZmqf73OUuMF7dR78eCA-dHd2MLquYjsoX7kvgKBIuHJ-AqiVMAIZdMWTk5LpbLWwK7oRtJUYgFqp3JPTY2dT0urIUkFUGC0)



Use level `"A"` to increment the first digit, `"B"` for the second. When a level is incremented, all digits to the right reset to 1.

## Participant Ordering

Control left-to-right order:

```python
from plantuml_compose import sequence_diagram

with sequence_diagram() as d:
    # Order determines position (lower = leftmost)
    db = d.database("Database", order=3)
    api = d.participant("API", order=2)
    client = d.participant("Client", order=1)

    d.message(client, api, "request")
    d.message(api, db, "query")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuKf9B4bCIYnELN21CVABKbAB58ov2e0gCfCp2nBpIXGS0poXuaOeuiuvcQb02Y9bo0Nbwjg1DLWf5AKMbgOMbt21U411k1LM2a3neaekXzIy5A0Z0000)



## Message Styling

```python
from plantuml_compose import sequence_diagram

with sequence_diagram() as d:
    a, b = d.participants("A", "B")

    # Colored message
    d.message(a, b, "important", style={"color": "red"})

    # Bold message
    d.message(b, a, "response", style={"bold": True})

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIe0qfd9cGM9UIKAZYWy9ov71TrevQBKb5XTEmKd1Ik5pDo2_A8Ie1oN4r0cAJy7BEC8b2bABIx8pojEvN98pKi16Wi0)



## Hide Unlinked Participants

```python
from plantuml_compose import sequence_diagram

with sequence_diagram(hide_unlinked=True) as d:
    a = d.participant("Active")
    b = d.participant("Also Active")
    unused = d.participant("Unused")  # Won't appear

    d.message(a, b, "hello")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuSh8J4bLACtBoSpBJatXAW2APYPd5YJcbIWu9fTabgMY22avvXJdGoMK51AB5K3yU2mAG_DAYu76GMGKTEsG5IfOAMIavkJaSpcavgK0dG00)



## Complete Example: E-Commerce Checkout

```python
from plantuml_compose import sequence_diagram

with sequence_diagram(title="Checkout Flow") as d:
    user = d.actor("Customer")
    web = d.boundary("Web UI")
    api = d.control("API")
    cart = d.entity("Cart")
    payment = d.participant("Payment Service")
    inventory = d.participant("Inventory")
    db = d.database("Database")

    d.message(user, web, "Click Checkout")
    d.message(web, api, "POST /checkout")
    d.activate(api)

    d.message(api, cart, "getItems()")
    d.message(cart, api, "items[]")

    d.divider("Validation")

    with d.loop("for each item") as loop:
        loop.message(api, inventory, "checkStock(item)")
        loop.message(inventory, api, "available")

    d.divider("Payment")

    d.message(api, payment, "charge(total)")

    with d.alt("payment success") as alt:
        alt.message(payment, api, "confirmed")
        alt.message(api, db, "createOrder()")
        alt.message(api, inventory, "reserveItems()")
        alt.message(api, web, "200 OK")
        alt.message(web, user, "Order Confirmed!")

        with alt.else_("payment failed") as failed:
            failed.message(payment, api, "declined")
            failed.message(api, web, "402 Payment Required")
            failed.message(web, user, "Payment Failed")

    d.deactivate(api)

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/TLF1Ji904BtlLuoSu60anfC91bDZqdY0YEZ1639i1zomxUBk5CFVErtRHGXUccRcpNjlthJZmEYvBgrYmvOW-oIzSJN3etNV2ZKx3raTs9NarTBLLO5-3xqtMi8yxm46aDV5F5VQLUoTXVjfhgWIiZramgosyZ3QRB5Yw4rnNqeJPkHtHbESRskBjdOqa5SxQJc_LmKoBZ4GFBGlgdC5btUj1xY5p1gzIKkejYu8iINjwMJs0bUwQyjwPeTCqNI3461ZMf1hufof3Fs1YfL4OPhg-uSQZU0LhH5VnbKm6Ydht1PM4XUX_emm1T2IfZs48AhFsEbDlm4D17Le9ndSeR6uj2HX5erO5vqejQGdmKLgz6lgisEq0uMMOTjEXLfh2a6qJgUIeXnmPNn9nS5sbtNJzIH1JNn1lZyulvYd89pKnPOmwJZNmo5CdgHnE4iwuYr4RiWw5nUAh2Xt2wmaZcZjN_y5QMkgl_QJyCtmEkNtJ5-ryH5sraQ7U_mLRD8lwEX36KjDVfWV)



## Quick Reference

| Method | Description |
|--------|-------------|
| `d.participant(name)` | Create participant |
| `d.actor(name)` | Stick figure participant |
| `d.boundary(name)` | Boundary participant |
| `d.control(name)` | Control participant |
| `d.entity(name)` | Entity participant |
| `d.database(name)` | Database (cylinder) |
| `d.queue(name)` | Queue participant |
| `d.collections(name)` | Multiple instances |
| `d.message(a, b, label)` | Send message |
| `d.return_(label)` | Return message |
| `d.activate(p)` | Start activation bar |
| `d.deactivate(p)` | End activation bar |
| `d.create(p)` | Create participant |
| `d.destroy(p)` | Destroy participant |
| `d.note(text, of=p)` | Add note |
| `d.ref(*p, label=text)` | Reference another diagram |
| `d.divider(title)` | Section divider |
| `d.delay(msg)` | Delay indicator |
| `d.space(px)` | Vertical spacing |
| `d.autonumber(action)` | Control numbering |
| `d.alt(label)` | If/else block |
| `d.opt(label)` | Optional block |
| `d.loop(label)` | Loop block |
| `d.par(label)` | Parallel block |
| `d.critical(label)` | Atomic block |
| `d.break_(label)` | Break block |
| `d.group(label)` | Custom group |
| `d.box(name, color)` | Group participants |
