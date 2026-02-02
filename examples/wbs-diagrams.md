# WBS Diagrams (Work Breakdown Structure)

WBS diagrams decompose projects into hierarchical components. They're the standard tool for:

- **Project planning**: Break large projects into manageable pieces
- **Scope definition**: Clearly show what's included in a project
- **Task assignment**: Organize work packages for team members
- **Cost estimation**: Estimate costs at each level of breakdown

A WBS starts with the project goal at the top, then breaks it down into deliverables, which break down into work packages.

## Core Concepts

**Root node**: The project or main deliverable at the top of the hierarchy.

**Branch**: A major component or phase that breaks down further.

**Work package**: The lowest level - actual tasks that can be assigned and estimated.

**Side**: Branches can extend left or right from parent nodes to balance the diagram.

## Your First WBS Diagram

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("Website Project") as root:
        root.leaf("Requirements")
        root.leaf("Design")
        root.leaf("Development")
        root.leaf("Testing")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAKygvj9I24zDAiuiILK8AChFIaqkuTBIKWXABIpDB4hDJSqhAGRnNLABCzFp8Aoor9py0f0CY1kIMboIcPVEvP2Qbm8q3G00)



This creates a simple WBS with one project and four deliverables.

## Building the Hierarchy

### Leaf Nodes (Work Packages)

Use `leaf()` for nodes with no children - typically the actual work packages:

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("Mobile App") as root:
        root.leaf("User Research")
        root.leaf("UI Design")
        root.leaf("Backend API")
        root.leaf("Testing")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAKygvj9IyCrFoin9LN0iAE3Iqb88BKujKWXABKvDB4hE00juAhYa5cUcvu4uJed9sQbvAGgE0PuWRaXgSKbcNZgN0r0CQ1W0)



### Nested Breakdown

Use `node()` as a context manager to create sub-hierarchies:

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("Software Project") as root:
        with root.node("Planning") as planning:
            planning.leaf("Requirements")
            planning.leaf("Architecture")
        with root.node("Development") as dev:
            dev.leaf("Frontend")
            dev.leaf("Backend")
        with root.node("Testing") as test:
            test.leaf("Unit Tests")
            test.leaf("Integration")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/DOvB3i8m34JtEONNEKL128bTnUS0RcfAeDZWkFJwTLEn6u_VZAOfXcfpLqA4YznjHYLeLPwKBCG8xOZCcGVN4SxqdRBIczXADNQQ7jaSdPHM-a0_6kMp0lL_L64Zxkknn_JQD5ofsB_qnjcgiLMUF30eMXOEZUC-RG40)



### Deep Hierarchies

WBS diagrams often have 3-4 levels of breakdown:

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("Product Launch") as root:
        with root.node("Marketing") as marketing:
            with marketing.node("Digital") as digital:
                digital.leaf("Social Media")
                digital.leaf("Email Campaign")
                digital.leaf("PPC Ads")
            with marketing.node("Traditional") as trad:
                trad.leaf("Print Ads")
                trad.leaf("Events")
        with root.node("Sales") as sales:
            sales.leaf("Training")
            sales.leaf("Collateral")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/FOv13i8m30JlVONFUKLHu4QbIEK39h62HUeWnuNlarALstfNuzsn6Qfzxcrm4BIcDHfSSPNu69o32VL9nfBxuU3CcGtBfXtCDJ8Mc2WnxivbGIxWSNaXPzcz43oSKllXDyN4nbME5q5Px8Wx_oQnJSECXVuCoz7lQobef9qVIL8V_GK0)



## Controlling Branch Direction

By default, branches spread evenly. You can force branches to one side:

### Force Left

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("Project") as root:
        with root.node("Phase A", side="left") as a:
            a.leaf("Task A1")
            a.leaf("Task A2")
        with root.node("Phase B", side="left") as b:
            b.leaf("Task B1")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAKygvj9I22ZApqfDBk7Iqh9H2CX8B4vLS0IoWPoGnE9i1KT3P8uHaYed90adGow7rBmKe840)



### Force Right

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("Project") as root:
        with root.node("Phase A", side="right") as a:
            a.leaf("Task A1")
        with root.node("Phase B", side="right") as b:
            b.leaf("Task B1")
            b.leaf("Task B2")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAKygvj9I22ZApqfDBk7Iqh9J2CX8B4vLS0IoWPoGnE9i1KT390ad90adGsIE4PT3QbuAq400)



### Balanced Layout

Mix sides to create a balanced diagram:

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("Conference Planning") as root:
        with root.node("Venue", side="left") as venue:
            venue.leaf("Location")
            venue.leaf("Catering")
            venue.leaf("AV Setup")
        with root.node("Content", side="right") as content:
            content.leaf("Speakers")
            content.leaf("Schedule")
            content.leaf("Materials")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/BSx12eCm40JGUxvYp_c68XQl5GJ1-ngdhHWsacpextTjUfl73iFsHJdhPotEqv3aYGm9e2coo2ulv_sD5aY59OkF55Zt94q3At9hcUuBpT1wchfhIo5wNJgQJ_21NFuARsmrecdyRN0iheTiziWN)



## Node Colors

Highlight important nodes or show status with colors:

### Single Node Color

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("Project", color="LightBlue") as root:
        root.leaf("Critical Task", color="Salmon")
        root.leaf("Normal Task")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAKygvjAALlR9JCyeSSefJOrL22ZApqfDBk7I0We79-RavkV5AZWNPPPa9YVcA8Ga5cS3PHJyyejoOLo7rBmKe340)



### Status Colors

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("Sprint 1") as root:
        with root.node("Completed", color="#90EE90") as done:
            done.leaf("Design")
            done.leaf("Backend")
        with root.node("In Progress", color="#FFE4B5") as wip:
            wip.leaf("Frontend")
        with root.node("Not Started", color="#E0E0E0") as todo:
            todo.leaf("Testing")
            todo.leaf("Deployment")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAKygvj9I22ueoimhKJ3aqjAALhOqS7MrD8XLSCxFBSX9BKbD0OfgARYa5cUcvu6PJed9sQbvAM35Rcwk9awciGgUUGe1HVdfHQd5nM0rRaNvUIKmHQu681Yhu9TVeX0CiXLgPaXgSKbcNZhK_8AS_ChSrBmIBWUWFg2x0000)



### Hex Colors

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("Priorities", color="#E3F2FD") as root:
        root.leaf("High", color="#F44336")
        root.leaf("Medium", color="#FF9800")
        root.leaf("Low", color="#4CAF50")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAKygvjAALdOrTZDoSubL22ZAp2_ABCbC1Oe2XTrCJ8oDpM8LF3BJCo02RfOM1WQn2hwfAPcbkM0X4sT7DrEWa4z-EPT3QbuAq4G0)



## Boxless Nodes

Remove box outlines for a cleaner look:

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("Main Topic") as root:
        root.leaf("With box")
        root.leaf("Without box", boxless=True)
        with root.node("Boxless branch", boxless=True) as branch:
            branch.leaf("Child node")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAKygvj9Iy4tCp5C8oI_8JERIqb88pop9K4ZAhm2ouy6S_D8IEDyflo8djRXO8QaeCIyv0oYafU2SaPcJef2NdvBAvP2Qbm8q4W00)



### All Boxless

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("Outline Style", boxless=True) as root:
        with root.node("Category A", boxless=True) as a:
            a.leaf("Item 1", boxless=True)
            a.leaf("Item 2", boxless=True)
        with root.node("Category B", boxless=True) as b:
            b.leaf("Item 3", boxless=True)

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAKygvjAAL_0lBSd9p4jL22wfp4dbqWAAE2UMfARd5rKgE0AvGBvdIMgkWY4IsmXLcHEIb36NGsfU2j1e0000)



## Multiline Text

Node text can span multiple lines using `\n`:

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("Q1 Goals") as root:
        root.leaf("Launch MVP\nby March 15")
        root.leaf("Hire 3 engineers\nfor backend team")
        root.leaf("Close Series A\n$5M target")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAKygvj9I23HKSCzFp04ojQny4alpaZCKVCC2k98g5NmJYu0SGrDha9H7Pb6gWh52QbvwPbvgQb4nLrf-aK9IOd9sQbwAGabgOYvObNDEVd6gGd1gKMPgiO8ZbugfhmBGflJK4cik1w12e8q0)



## Arrows Between Nodes

WBS diagrams can show dependencies between work packages using aliases and arrows:

### Basic Arrows

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("Project") as root:
        root.leaf("Design", alias="design")
        root.leaf("Develop", alias="dev")
        root.leaf("Test", alias="test")

    d.arrow("design", "dev")
    d.arrow("dev", "test")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAKygvj9I22ZApqfDBk7Iqb9GSaajpapFKr98B5P80JEXecMfEVa5KE4oi5X8Qd49MA04oE22A5RGjGFB0p682PPnICrB0Te30000)



### Complex Dependencies

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("Release") as root:
        with root.node("Backend", side="left") as backend:
            backend.leaf("API Design", alias="api")
            backend.leaf("Database", alias="db")
            backend.leaf("Services", alias="svc")
        with root.node("Frontend", side="right") as frontend:
            frontend.leaf("UI Design", alias="ui")
            frontend.leaf("Components", alias="comp")
            frontend.leaf("Integration", alias="integ")

    # Backend dependencies
    d.arrow("api", "svc")
    d.arrow("db", "svc")

    # Frontend dependencies
    d.arrow("ui", "comp")
    d.arrow("comp", "integ")

    # Cross-team dependency
    d.arrow("svc", "integ")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/LO_H2i8m34NVznMXZmN_GCRK8UnD53yWRSCeQZkQRlw-MLSHNqBkkRbfsd76bD-66mrNUX8oDLhluOZsGS59Bq8TBWFqn7uC2f019r-D7ZCQoHJiJAKtIektn8NoOWMtS4unvBgo1NN_spZxYa_nDSL08MzXAx8wWwJ7XDd7BU9NtSWfi6lB8yvykxcmabtBAhPfCN-YasFauny0)



## Styling with diagram_style

Apply consistent styling across the entire diagram:

### Basic Styling

```python
from plantuml_compose import wbs_diagram

with wbs_diagram(diagram_style={
    "background": "#FAFAFA",
    "font_name": "Arial",
}) as d:
    with d.node("Styled WBS") as root:
        root.leaf("Child 1")
        root.leaf("Child 2")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAKygvh8fBgdCIRNZ0h9TCXFJYn9p5Qgv51IS4fEpquloI_DIdFDpyeiKbDqSGH0euvQVL-ANc9kgu5YKcPZ3LSjbemyrGaiX6CH8KGXt2kRIqb9mpiZCIL4mH32Dk1nIyrA0DW40)



### Node Styling

```python
from plantuml_compose import wbs_diagram

with wbs_diagram(diagram_style={
    "node": {
        "background": "#E3F2FD",
        "font_color": "#1565C0",
    }
}) as d:
    with d.node("Blue Theme") as root:
        with root.node("Branch A") as a:
            a.leaf("Leaf 1")
            a.leaf("Leaf 2")
        root.leaf("Branch B")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/JOvD2i8m48NtSue1TzbeAtLLfAOrAvTUO6p6LamJI5AabDxTK0gw-zuFZrU5I3v-7W7A42V3PqZSlAZpDE0CYDPfNW5HKllkl1kjhfrn7dVNeyfLisRAsRYvMN4gwaDo5rYWt6-p0gKP6Uyz3mmYAK-sxV6IME2DwOdP3_E_XeIAhKwllW00)



### Root Node Styling

Style the root node differently from other nodes:

```python
from plantuml_compose import wbs_diagram

with wbs_diagram(diagram_style={
    "root_node": {
        "background": "#FF9800",
        "font_color": "white",
    },
    "node": {
        "background": "#FFF3E0",
    }
}) as d:
    with d.node("Highlighted Root") as root:
        root.leaf("Normal child 1")
        root.leaf("Normal child 2")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/VOwz2W8n48JxVOe5kpH6RHGEEVm9LbVu1l4ISi5S5fALG-JUtH3j18k1ORvXc3QpJZpTCZIPdy7keVYJroxf4L-06CdOQX0Fkh-xH8zeZXGeuK8fjJdBmkQYHCJTt_9kAsLbYY9_qcdmREl03Cto-q3WnRiX5B4rU2sx80Hsb4OTi1zyCBZwITRGscZA-JS0)



### Leaf Node Styling

Style work packages (leaf nodes) differently:

```python
from plantuml_compose import wbs_diagram

with wbs_diagram(diagram_style={
    "leaf_node": {
        "background": "#E8F5E9",
        "font_color": "#2E7D32",
    }
}) as d:
    with d.node("Root") as root:
        with root.node("Has children") as branch:
            branch.leaf("Leaf A")
            branch.leaf("Leaf B")
        root.leaf("Also a leaf")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/HKvB2i8m5Do_KmouoqPGH8KYRMsB2t7X3PvDhCMO1qb4H7ftOocucnypauV8FhukWR8GtzRiAE6gvyxp0ny2hE7hIRGP2L1oU--yF9tUYnMFMRrfLlLsz1fnSL8NzRfQBf8wq43PVAfME8j4KWe73cXllTNUkCGLZca6nH-MlrHXWu372vGRfzErBm00)



### Arrow Styling

Customize the connecting lines:

```python
from plantuml_compose import wbs_diagram

with wbs_diagram(diagram_style={
    "arrow": {
        "line_color": "#9E9E9E",
        "line_thickness": 2,
    }
}) as d:
    with d.node("Central") as root:
        with root.node("Branch 1") as b1:
            b1.leaf("Detail")
        root.leaf("Branch 2")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/JOun2i9044NxESK7kst4T4AGO69dwGN6E9Z5THPc5e98xkug8lARnoiUl_F2LkQpK-lbaMH7bOV8L-CxdWImMPu_11oZIfzJDgosX_T-zZJ5yQRYZgQwXHPgrzzUG2zQZ1E5WBsnZXCsbGC6AHp_TKETwAKUU040)



### Combined Styling

```python
from plantuml_compose import wbs_diagram

with wbs_diagram(diagram_style={
    "background": "#ECEFF1",
    "root_node": {
        "background": "#263238",
        "font_color": "white",
    },
    "node": {
        "background": "#CFD8DC",
    },
    "leaf_node": {
        "background": "#FAFAFA",
    },
    "arrow": {
        "line_color": "#607D8B",
    }
}) as d:
    with d.node("Styled WBS") as root:
        with root.node("Category A") as a:
            a.leaf("Item 1")
            a.leaf("Item 2")
        with root.node("Category B") as b:
            b.leaf("Item 3")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/VP112u9048Nl-oi6kdaf5So3XBgw44GN3vstt4pI7LWtHCB_tceB4eGC0s_cVJoOYJlDbUwl7OawFJJYG8pEQbuftiAR0AJyzgmKlcH9iK45cvpcZBd6aLYA6Va3KPQ56JNUQ5eXwlCAx0M-vuUpnr3gxxP_r5hOW4Rm-re0IwQoC5SAUqkUQYai4-psMPZEp4YYhJtMWM8I9LpIWZWEKAv5XMg0n4mE7BLemLsazyEaY-6JMCZIlEu3)



## Complete Examples

### Software Project WBS

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("E-Commerce Platform") as root:
        with root.node("Planning", side="left") as plan:
            plan.leaf("Requirements")
            plan.leaf("Architecture")
            plan.leaf("Timeline")
        with root.node("Development", side="left") as dev:
            with dev.node("Frontend") as fe:
                fe.leaf("Product Pages")
                fe.leaf("Cart")
                fe.leaf("Checkout")
            with dev.node("Backend") as be:
                be.leaf("User API")
                be.leaf("Product API")
                be.leaf("Order API")
        with root.node("Testing", side="right") as test:
            test.leaf("Unit Tests")
            test.leaf("Integration")
            test.leaf("UAT")
        with root.node("Deployment", side="right") as deploy:
            deploy.leaf("Infrastructure")
            deploy.leaf("CI/CD")
            deploy.leaf("Monitoring")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/NL11Ri8m4Bpp2fyZ8JvGHOIabNAe6g7m0ECimIBUXVKQrD_NZWD8lUsCPsPdlVMYMHv7lohKvxecvu0Dg6xISY9sgwBuI03HuXX1H7ku1SlW0CLdfc9pjW960aDcUkjWiWYplO4xJ7HDXlpwnOG2E2IKufc6O4HrUWI_S7KizHpFO2uK5kzEcylRUl30gkhQVqblveU7bw9KFNXPxYZL0QtCZC-uZPr6rc895q7Lpwu6hXFzFkiduOcr5mwlWqjLjvkwoUCtnM3Yj6SRcyQl_GC0)



### Event Planning WBS

```python
from plantuml_compose import wbs_diagram

with wbs_diagram(diagram_style={
    "root_node": {"background": "#1976D2", "font_color": "white"},
    "node": {"background": "#E3F2FD"},
}) as d:
    with d.node("Annual Conference") as root:
        with root.node("Venue") as venue:
            venue.leaf("Location Search")
            venue.leaf("Contract")
            venue.leaf("Layout")
        with root.node("Program") as prog:
            prog.leaf("Keynotes")
            prog.leaf("Breakouts")
            prog.leaf("Workshops")
        with root.node("Marketing") as mktg:
            mktg.leaf("Website")
            mktg.leaf("Email")
            mktg.leaf("Social")
        with root.node("Operations") as ops:
            ops.leaf("Registration")
            ops.leaf("Catering")
            ops.leaf("AV Equipment")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/VP1BQyD038Jl_XM2tdmfJQ2b44eUJYvzqa1wLjQgizYHKgrCC2N_lTxTzjh3mgUPGOns7WpLpljGp88D7JqK8rSU6yKZV1S0B3Kb05YYQnkLdkkLTA9mjPvk9fjgz2xZKn5x-ITyStztMqsIjn6sh9uFtYWjk1Ipwzy69IoOU-nW9Vn9IkoeA4lO4VSHIdWIX-Q5OKkexf2qCMkApd801-aZmfjAF2MfZpIm68KqB9Mm7KDv-X1jmq5ESO9dr9RCSvCjseTOClBwYBvBj1NdCIAydaXJcxpfdHeVB2kv61hftxB53jPVlJyTYQsO4zVZR_y0)



### Construction Project with Dependencies

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("House Construction") as root:
        with root.node("Foundation", side="left") as found:
            found.leaf("Survey", alias="survey")
            found.leaf("Excavation", alias="excav")
            found.leaf("Pour Concrete", alias="pour")
        with root.node("Structure", side="right") as struct:
            struct.leaf("Framing", alias="frame")
            struct.leaf("Roofing", alias="roof")
            struct.leaf("Exterior", alias="ext")

    # Foundation sequence
    d.arrow("survey", "excav")
    d.arrow("excav", "pour")

    # Structure sequence
    d.arrow("pour", "frame")
    d.arrow("frame", "roof")
    d.arrow("frame", "ext")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/FP112eD034NtdYAu7EWDYWX5wRBK4qmr5XUTb4p6sjjt4iTkGjx_uIUaZU9PFezOERXIYWWN2b4uZR9Gg9mxGqyfJBvWvdf8lEAt1XyXMblqRXlzQeFceMAnRfHOaqT6GNFVMSbc0uCjIumwsa3TityjuMb3S-uF_Kuq7phdliZT9iWBSLafrNuId9foW5L5swX5OK-sgcY1VzAO5iEKt_83)



### Product Roadmap

```python
from plantuml_compose import wbs_diagram

with wbs_diagram() as d:
    with d.node("2024 Roadmap") as root:
        with root.node("Q1", color="#BBDEFB") as q1:
            q1.leaf("MVP Launch")
            q1.leaf("Beta Testing")
        with root.node("Q2", color="#C8E6C9") as q2:
            q2.leaf("User Feedback")
            q2.leaf("Performance")
        with root.node("Q3", color="#FFF9C4") as q3:
            q3.leaf("New Features")
            q3.leaf("Integrations")
        with root.node("Q4", color="#FFCCBC") as q4:
            q4.leaf("Scale")
            q4.leaf("Enterprise")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/BO_B2i8m44Nt_Og0kwoq5h4xIMn0KAdFZRYOfcCjshHCKlhxXi7Tt7lFMSp61w0mLJwH8fsdcJZtK7Sm958-Pafj2wEUuhI8KOh3lHHx69rzSrGOG5pHXzOrZEjriT9vn5FURnv96CIw0llXfaHwzTI1iyY2CIRNMHIMF1znYZo4aT1piNC16uBGzix_1QsLZaB6-yN25_ag8aa3jHwJ3Rew_lC3)



## Quick Reference

### Diagram Creation

| Code | Description |
|------|-------------|
| `wbs_diagram()` | Create a WBS diagram |
| `diagram_style={...}` | Apply styling |

### Node Methods

| Method | Description |
|--------|-------------|
| `d.node(text)` | Add root node (use as context manager) |
| `root.node(text)` | Add child branch (use as context manager) |
| `root.leaf(text)` | Add leaf node (no children) |
| `d.arrow(from, to)` | Add arrow between aliased nodes |

### Node Parameters

| Parameter | Description |
|-----------|-------------|
| `text` | Node label (required) |
| `side="left"` | Force to left side |
| `side="right"` | Force to right side |
| `alias="name"` | ID for arrow connections |
| `color="..."` | Background color |
| `boxless=True` | Remove box outline |

### Diagram Style Keys

| Key | Description |
|-----|-------------|
| `background` | Diagram background color |
| `font_name` | Default font |
| `font_size` | Default font size |
| `font_color` | Default text color |
| `node` | Style for all nodes |
| `root_node` | Style for root node only |
| `leaf_node` | Style for leaf nodes only |
| `arrow` | Style for connecting lines |

### Node/Arrow Style Keys

| Key | Description |
|-----|-------------|
| `background` | Fill color |
| `font_color` | Text color |
| `line_color` | Border/line color |
| `line_thickness` | Border/line width |

## WBS vs Mind Map

Both are tree diagrams, but serve different purposes:

| WBS | Mind Map |
|-----|----------|
| Project decomposition | Idea exploration |
| Top-down (goal to tasks) | Central topic outward |
| Formal structure | Freeform brainstorming |
| Supports dependencies (arrows) | No arrows |
| Work packages at leaves | Ideas at any level |

Use WBS when you need to break down work for planning and tracking. Use mind maps for brainstorming and exploring concepts.
