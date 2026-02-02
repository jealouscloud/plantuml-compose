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

### Self-Messages

```python
from plantuml_compose import sequence_diagram

with sequence_diagram() as d:
    service = d.participant("Service")

    d.message(service, service, "internal processing")

print(d.render())
```

### Bidirectional Messages

```python
from plantuml_compose import sequence_diagram

with sequence_diagram() as d:
    a, b = d.participants("A", "B")

    d.message(a, b, "sync", bidirectional=True)

print(d.render())
```

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
