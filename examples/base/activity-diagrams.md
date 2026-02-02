# Activity Diagrams

Activity diagrams show workflows with decisions and parallel execution. They're ideal for:

- **Business processes**: Order fulfillment, approval workflows
- **Algorithms**: Code flow with branching logic
- **User workflows**: Registration, checkout flows
- **Parallel operations**: Concurrent task execution

Unlike state diagrams (which track one entity's lifecycle), activity diagrams show step-by-step processes with decision points and parallelism.

## Core Concepts

**Action**: A step in the workflow (rounded rectangle).

**Decision**: Branch based on conditions (if/else, switch).

**Fork/Join**: Split into parallel paths, then synchronize.

**Swimlane**: Organize actions by actor or department.

## Your First Activity Diagram

```python
from plantuml_compose import activity_diagram

with activity_diagram(title="Simple Process") as d:
    d.start()
    d.action("Receive Request")
    d.action("Process Request")
    d.action("Send Response")
    d.stop()

print(d.render())
```

## Actions

### Basic Actions

```python
from plantuml_compose import activity_diagram

with activity_diagram() as d:
    d.start()

    # Simple action
    d.action("Validate Input")

    # Action with styling
    d.action("Important Step", style={"background": "yellow"})

    d.stop()

print(d.render())
```

### Arrow Labels

```python
from plantuml_compose import activity_diagram

with activity_diagram() as d:
    d.start()
    d.action("Step 1")

    # Labeled arrow
    d.arrow("proceed")

    d.action("Step 2")

    # Styled arrow
    d.arrow(pattern="dashed", style={"color": "gray"})

    d.action("Step 3")
    d.stop()

print(d.render())
```

## Decisions

### If/Else

```python
from plantuml_compose import activity_diagram

with activity_diagram(title="Validation") as d:
    d.start()
    d.action("Get Input")

    with d.if_("Valid?", then_label="yes") as branch:
        branch.action("Process")

        with branch.else_("no") as else_branch:
            else_branch.action("Show Error")

    d.action("Continue")
    d.stop()

print(d.render())
```

### If/ElseIf/Else

```python
from plantuml_compose import activity_diagram

with activity_diagram(title="Grade Calculator") as d:
    d.start()
    d.action("Get Score")

    with d.if_("Score >= 90?", then_label="A") as branch:
        branch.action("Excellent!")

        with branch.elseif("Score >= 80?", then_label="B") as elif_b:
            elif_b.action("Good!")

        with branch.elseif("Score >= 70?", then_label="C") as elif_c:
            elif_c.action("Passing")

        with branch.else_("F") as else_branch:
            else_branch.action("Needs Improvement")

    d.stop()

print(d.render())
```

### Switch/Case

```python
from plantuml_compose import activity_diagram

with activity_diagram(title="Type Handler") as d:
    d.start()
    d.action("Get Request")

    with d.switch("Request Type?") as sw:
        with sw.case("GET") as get_case:
            get_case.action("Handle GET")

        with sw.case("POST") as post_case:
            post_case.action("Handle POST")

        with sw.case("DELETE") as delete_case:
            delete_case.action("Handle DELETE")

    d.action("Send Response")
    d.stop()

print(d.render())
```

## Loops

### While Loop

```python
from plantuml_compose import activity_diagram

with activity_diagram(title="Processing Loop") as d:
    d.start()
    d.action("Initialize")

    with d.while_("More items?", is_label="yes", endwhile_label="no") as loop:
        loop.action("Process Item")
        loop.action("Update Counter")

    d.action("Finalize")
    d.stop()

print(d.render())
```

### Repeat-While (Do-While)

```python
from plantuml_compose import activity_diagram

with activity_diagram(title="Retry Logic") as d:
    d.start()

    with d.repeat(condition="Success?", is_label="no", not_label="yes") as loop:
        loop.action("Attempt Operation")

    d.action("Done")
    d.stop()

print(d.render())
```

### Break from Loop

```python
from plantuml_compose import activity_diagram

with activity_diagram() as d:
    d.start()

    with d.while_("Processing") as loop:
        loop.action("Process Item")

        with loop.if_("Error?") as check:
            check.break_()  # Exit the loop

    d.stop()

print(d.render())
```

## Parallel Execution

### Fork and Join

```python
from plantuml_compose import activity_diagram

with activity_diagram(title="Parallel Tasks") as d:
    d.start()
    d.action("Receive Order")

    with d.fork() as f:
        with f.branch() as b1:
            b1.action("Check Inventory")

        with f.branch() as b2:
            b2.action("Process Payment")

        with f.branch() as b3:
            b3.action("Generate Invoice")

    d.action("Ship Order")
    d.stop()

print(d.render())
```

### Split (No Sync Bar)

```python
from plantuml_compose import activity_diagram

with activity_diagram() as d:
    d.start()

    with d.split() as s:
        with s.branch() as b1:
            b1.action("Path A")

        with s.branch() as b2:
            b2.action("Path B")

    d.stop()

print(d.render())
```

## Swimlanes

Organize actions by actor, department, or system:

```python
from plantuml_compose import activity_diagram

with activity_diagram(title="Order Process") as d:
    d.swimlane("Customer")
    d.start()
    d.action("Place Order")

    d.swimlane("Sales")
    d.action("Verify Order")

    d.swimlane("Warehouse")
    d.action("Pick Items")
    d.action("Pack Items")

    d.swimlane("Shipping")
    d.action("Ship Order")

    d.swimlane("Customer")
    d.action("Receive Order")
    d.stop()

print(d.render())
```

### Colored Swimlanes

```python
from plantuml_compose import activity_diagram

with activity_diagram() as d:
    d.swimlane("Frontend", color="LightBlue")
    d.start()
    d.action("User Input")

    d.swimlane("Backend", color="LightGreen")
    d.action("Process Request")

    d.swimlane("Database", color="LightYellow")
    d.action("Store Data")

    d.stop()

print(d.render())
```

## Grouping

### Partition

```python
from plantuml_compose import activity_diagram

with activity_diagram() as d:
    d.start()

    with d.partition("Validation", color="LightBlue") as p:
        p.action("Check Format")
        p.action("Verify Data")

    with d.partition("Processing") as p:
        p.action("Transform")
        p.action("Calculate")

    d.stop()

print(d.render())
```

### Group

```python
from plantuml_compose import activity_diagram

with activity_diagram() as d:
    d.start()

    with d.group("Authentication") as g:
        g.action("Get Credentials")
        g.action("Verify Token")

    d.action("Process Request")
    d.stop()

print(d.render())
```

## Flow Control

### Kill (Abnormal Termination)

```python
from plantuml_compose import activity_diagram

with activity_diagram() as d:
    d.start()
    d.action("Process")
    d.action("Detect Fatal Error")
    d.kill()  # X symbol - abnormal termination

print(d.render())
```

### End (Alternative Stop)

```python
from plantuml_compose import activity_diagram

with activity_diagram() as d:
    d.start()
    d.action("Normal Path")
    d.action("Complete")
    d.end()  # Circle with X - alternative to stop()

print(d.render())
```

### Detach (Async Path)

```python
from plantuml_compose import activity_diagram

with activity_diagram() as d:
    d.start()

    with d.fork() as f:
        with f.branch() as main:
            main.action("Main Flow")

        with f.branch() as async_branch:
            async_branch.action("Background Task")
            async_branch.detach()  # Continues independently

    d.action("Main Continues")
    d.stop()

print(d.render())
```

### Connectors (Goto-like)

```python
from plantuml_compose import activity_diagram

with activity_diagram() as d:
    d.start()
    d.action("Start Processing")

    d.connector("A")  # Define connector point

    d.action("Process Item")

    with d.if_("More?") as check:
        check.connector("A")  # Jump back to A

        with check.else_() as else_branch:
            else_branch.action("Done")

    d.stop()

print(d.render())
```

## Notes

```python
from plantuml_compose import activity_diagram

with activity_diagram() as d:
    d.start()

    d.action("Validate")
    d.note("Check all required fields", position="right")

    d.action("Process")
    d.note("May take time", position="left")

    # Floating note
    d.note("Important!", floating=True)

    d.stop()

print(d.render())
```

## Complete Example: Order Fulfillment

```python
from plantuml_compose import activity_diagram

with activity_diagram(title="Order Fulfillment Process") as d:
    d.swimlane("Customer")
    d.start()
    d.action("Place Order")

    d.swimlane("OrderSystem")
    d.action("Receive Order")

    with d.if_("Valid Order?", then_label="yes") as valid:
        valid.action("Create Order Record")

        with valid.fork() as f:
            with f.branch() as payment:
                payment.action("Process Payment")

            with f.branch() as inventory:
                inventory.action("Reserve Inventory")

        with valid.if_("Payment OK?", then_label="yes") as payment_check:
            payment_check.action("Pick Items")
            payment_check.action("Pack Order")
            payment_check.action("Ship Package")

            with payment_check.else_("no") as payment_else:
                payment_else.action("Release Inventory")
                payment_else.action("Cancel Order")

        with valid.else_("no") as valid_else:
            valid_else.action("Reject Order")

    d.stop()

print(d.render())
```

## Quick Reference

| Method | Description |
|--------|-------------|
| `d.start()` | Start node |
| `d.stop()` | Stop node (filled circle) |
| `d.end()` | End node (circle with X) |
| `d.action(label)` | Activity step |
| `d.arrow(label)` | Labeled arrow |
| `d.if_(condition)` | If/else decision |
| `d.switch(condition)` | Switch/case |
| `d.while_(condition)` | While loop |
| `d.repeat(condition)` | Repeat-while loop |
| `d.fork()` | Parallel fork/join |
| `d.split()` | Split without sync |
| `d.swimlane(name)` | Switch swimlane |
| `d.partition(name)` | Grouping with border |
| `d.group(name)` | Light grouping |
| `d.note(text)` | Add note |
| `d.break_()` | Exit loop |
| `d.kill()` | Abnormal termination |
| `d.detach()` | Async continuation |
| `d.connector(name)` | Jump point |

### Inside If/Switch/Loop

| Method | Description |
|--------|-------------|
| `branch.else_(label)` | Else branch |
| `branch.elseif(condition)` | Else-if branch |
| `sw.case(label)` | Switch case |
| `f.branch()` | Fork branch |
