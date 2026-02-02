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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuIh9BCb9LGZEp2q0KW55-ScfnSLSO5akgw3KvDJCibI5eDJ2qjJY4cikAwW2997WrBmK8BUu83-lEDKQg3E_WCi1A0Oq6m00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8pkAp24dCoKn9BKXKyymfAIwovb2jJStBoowqySmloYqeIyqeKWajI2wo1olCBk1nIyrA0UW40)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8pkAo2Ir8B50ojkNHrxHGAYlAJKrDJhA6YHa3HQENqeiHAdPJ4uepKb5XTEwYKiJLGVtu1bqDgNWhGC000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/7Oqn2iCm34LtdKAZSmLxQA24qArGw6uQXGXSASWoeRUlyVhUv_svUZPltmBENWZVkV2MdLLW68WhEJxaR9w0TmnZS9lG3n8CFweJ8CQdwOTgJK2b4WRHGL-7NhYOgNKX6-yGxohEqYZrl9umTzpF_m00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/RS_12i8m30RWUvuYthQRDtL3dGuTNaJm2SgQQI5jHvk9Zs-fXo5u-yd_GP8cYWeoMGOnmeHTK9gmLTnFhCG7o3rK7GdUUn-e1ZDWaIFkjhXPxakK9pai3YKWLgTtJypaP543SQGVlPxrCUlEU_qFhcROPdXJCHht-58ipdbu9T8HBtOC_aKsxKorqsP8H_iHcfJJOny0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/LOun3i8m34Ltdy9ZUuLae0DH6P10RIuGjPQe5D9GkqBS7jCK2JR__sJxDInXaVKUGIQ9XFwL2KyXZP4Ms1YObWGxUgp4Oe6VammthFPYMpZKC0Gch5hdQq0qvG1gj3kvNle_zCbVTdHdvzqlBOq5IcFv1wRNMIqupub9DMJEq6Ydwcy0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/BOv12iCm30JlUeMEyHViGmE5Gg25Nle0auXMu4Z1KYZjw-iKNtUMsHtDS_LzBU3iXV1UTIOpbYTULJVuOuYJi7Ck_AK4xnUtud3JIiXEgvq2ik7m8Gk06Bi2fyRI4Jos9JlXMNTngWb8bkuG3H0lBDritXR7XjkV7m00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/BOr12W8n34NtEKMMxHLc5exWKX3q1AK63SmafVc3pEqjulhntbi2fMFVLe9Y5RuB-i5NVscb7w8kJGg8UJe3iZNmhKalKBVv3_dprk6cnrwhH9moQt0opsmEJeT4fkdY9lDeUgD5x3cMNm00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8pkCepCdDI5JG2YlAJKukBC_FIDRaK5AoWN0NFajHSQw10Pfg2XcjHKNwHlQP2IKPg7b18GI6fA3Kn6yXApKl9JEC2ac2pWERc5t0v0Bb0Im00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NSun3i8m38NXtQVmETAb4WDYeW8kOAKF6YLDAiTKwkr9YrYOF-j_xgk9sdjEPC4IU12Lb93u8JLMEfJS3HvX1LzrX7RqB1g9sPqc-CYNl29RqUqBB2y9UUT1YqUjhRdDxUAVpyXGCUo14ZmwGXxvQBlx59RVMhMoKD-iVVa1)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8pk8eBSZ9Bk1GKh08IIp8K7AqX0Wg9wOcPUN1X9skkrBmK1OZQufBy0Yu781ze2000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/HOwn2iCm34HtVOM_8ra2dJhLDD3Enb4RKJisaXme-EFhbk9iTwTtd2PHnrfY02KDQ2wy81lBoQC8r5CHJH6vme-3mGRd_zG8TNO1fS9mGwR7kyTtnxYc8jXEblpBd1MZZCsumzHvfPnfUpReAtlxs1okw97sljVo31DkI_lt0m00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/HSwn2i9040JG_hxYmBz8cX144In4iR1Suw3YUHjtzqYp7vyp8BOpZs4wDH8hxnHyjN_U7zQd0jy8PqE-ULZgq9mL4dTvBDR-u5Q0x3qDhmKs1-41gl68Ju7-tGKfyUHhChgIeigJiI1-WxRkynYwkb0lp000)



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
![Diagram](https://www.plantuml.com/plantuml/svg/JOwn2iCm34HtVOLm_w9PGXCwTUXGiWj7IKGTEzZo44h_lNQwP3aU1--uDYb5pQk30s0h8Ih1end8oKYL3LuUCYzwSvdn0uZNRc7xndk8AsbJYu6ZJ3lsfDJ0zpppZC5oIk9dytTVaNoQYdg87JcR7IbNBMdOe6K_baC_)



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
![Diagram](https://www.plantuml.com/plantuml/svg/7Osn3eCm30LtVuM_WomWXgweghf7y2WHDAQsCo34lnVOJZVSrUPHlNmNke4-AcNbflY4xAcFdYJpJipL0ywjOhXyN2nSxWrDuyOlcP437LHrAZtC-8bVWNaugx9IZJoSYpy0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8pkAm2YlAJKukBhRciN59BKfDB5DmIIn9p55oBYlABhBcoCtDok1nIyrA0EW00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8pkApyyejo4tCK0X9BCgovh9ppSmjoKajIhRbIyrAu7804K2a0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/9OrB3e0W34JtFKNF8HkYYJjtNg01H09ImoTUtugxoPky6LqRbTQl12F0mIK2uhHHoBWcVjH0I5x0LynaeY_SiyMTQbJ2h6jaJd22XlxB2-SMSdTLoJJVeAMNdnS0)



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
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAStDuG8pkAo2GPH2G55-ScfnSMPUkZMNXgCcbnLKGC6p93NNcYipJK73DxyerLvJeIGZDOzBGG6aA3MdE1N8j7B9pqkrvahDIybC0vgQNy3b06G3hG00)



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
![Diagram](https://www.plantuml.com/plantuml/svg/JOun3i8m34Ltdy9S8ooLc1YGcDYjnccjEd5nt87RDq8CR6zuUlzFFSZZg0fVWFGYbKp1LsWMZ2xB6WblAyyRaYewlmznpbY4DNT8JxUPU__vocNe3_fWqCOOKXcA6eMq1V-BzxgR1xMuZ6NROUAMnuqJ)



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
![Diagram](https://www.plantuml.com/plantuml/svg/NP51YiCm34NtFeMMoHMInHGA0sKM3IrqBnobzTInYwqK0Zdyo8dT3btPVFqlFTcxo1Xu6grYmvRW67eAy3tPmLWxacFeWjSKerhsKsG_KbZKcb5DPr7dHAkMzJpFaMbSL7CYJURvgfe1gWjQqs_2Lmry8mVLJB5M0Cq-47APBbaV-bRqmOUx76B85D3XdAXA4V2AncsM4qKAClBWdkBmOKucSdtfaXXo78u_dmXfXj5tE0X_RBE08kGDLk5yCmz8AbvfxMuZGULyNGWiOVmWIDkXqsJVdGJA3Ef_MAA_fBbODeCyzqFjv2xVymS0)



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
