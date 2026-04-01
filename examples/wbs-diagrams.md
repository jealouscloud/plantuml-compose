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
from plantuml_compose import wbs_diagram, render

d = wbs_diagram()
n = d.nodes

d.add(n.node("Website Project",
    n.leaf("Requirements"),
    n.leaf("Design"),
    n.leaf("Development"),
    n.leaf("Testing"),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAKygvj9I24zDAiuiILK8AChFIaqkuTBIKWXABIpDB4hDJSqhAGRnNLABCzFp8Aoor9py0f0CY1kIMboIcPVEvP2Qbm8q3G00)



This creates a simple WBS with one project and four deliverables.

## Building the Hierarchy

### Leaf Nodes (Work Packages)

Use `leaf()` for nodes with no children - typically the actual work packages:

```python
from plantuml_compose import wbs_diagram, render

d = wbs_diagram()
n = d.nodes

d.add(n.node("Mobile App",
    n.leaf("User Research"),
    n.leaf("UI Design"),
    n.leaf("Backend API"),
    n.leaf("Testing"),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAKygvj9IyCrFoin9LN0iAE3Iqb88BKujKWXABKvDB4hE00juAhYa5cUcvu4uJed9sQbvAGgE0PuWRaXgSKbcNZgN0r0CQ1W0)



### Nested Breakdown

Use `node()` with child arguments to create sub-hierarchies:

```python
from plantuml_compose import wbs_diagram, render

d = wbs_diagram()
n = d.nodes

d.add(n.node("Software Project",
    n.node("Planning",
        n.leaf("Requirements"),
        n.leaf("Architecture"),
    ),
    n.node("Development",
        n.leaf("Frontend"),
        n.leaf("Backend"),
    ),
    n.node("Testing",
        n.leaf("Unit Tests"),
        n.leaf("Integration"),
    ),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/DOvB3i8m34JtEONNEKL128bTnUS0RcfAeDZWkFJwTLEn6u_VZAOfXcfpLqA4YznjHYLeLPwKBCG8xOZCcGVN4SxqdRBIczXADNQQ7jaSdPHM-a0_6kMp0lL_L64Zxkknn_JQD5ofsB_qnjcgiLMUF30eMXOEZUC-RG40)



### Deep Hierarchies

WBS diagrams often have 3-4 levels of breakdown:

```python
from plantuml_compose import wbs_diagram, render

d = wbs_diagram()
n = d.nodes

d.add(n.node("Product Launch",
    n.node("Marketing",
        n.node("Digital",
            n.leaf("Social Media"),
            n.leaf("Email Campaign"),
            n.leaf("PPC Ads"),
        ),
        n.node("Traditional",
            n.leaf("Print Ads"),
            n.leaf("Events"),
        ),
    ),
    n.node("Sales",
        n.leaf("Training"),
        n.leaf("Collateral"),
    ),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/FOv13i8m30JlVONFUKLHu4QbIEK39h62HUeWnuNlarALstfNuzsn6Qfzxcrm4BIcDHfSSPNu69o32VL9nfBxuU3CcGtBfXtCDJ8Mc2WnxivbGIxWSNaXPzcz43oSKllXDyN4nbME5q5Px8Wx_oQnJSECXVuCoz7lQobef9qVIL8V_GK0)



## Controlling Branch Direction

By default, branches spread evenly. You can force branches to one side:

### Force Left

```python
from plantuml_compose import wbs_diagram, render

d = wbs_diagram()
n = d.nodes

d.add(n.node("Project",
    n.node("Phase A", side="left",
        n.leaf("Task A1"),
        n.leaf("Task A2"),
    ),
    n.node("Phase B", side="left",
        n.leaf("Task B1"),
    ),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAKygvj9I22ZApqfDBk7Iqh9H2CX8B4vLS0IoWPoGnE9i1KT3P8uHaYed90adGow7rBmKe840)



### Force Right

```python
from plantuml_compose import wbs_diagram, render

d = wbs_diagram()
n = d.nodes

d.add(n.node("Project",
    n.node("Phase A", side="right",
        n.leaf("Task A1"),
    ),
    n.node("Phase B", side="right",
        n.leaf("Task B1"),
        n.leaf("Task B2"),
    ),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAKygvj9I22ZApqfDBk7Iqh9J2CX8B4vLS0IoWPoGnE9i1KT390ad90adGsIE4PT3QbuAq400)



### Balanced Layout

Mix sides to create a balanced diagram:

```python
from plantuml_compose import wbs_diagram, render

d = wbs_diagram()
n = d.nodes

d.add(n.node("Conference Planning",
    n.node("Venue", side="left",
        n.leaf("Location"),
        n.leaf("Catering"),
        n.leaf("AV Setup"),
    ),
    n.node("Content", side="right",
        n.leaf("Speakers"),
        n.leaf("Schedule"),
        n.leaf("Materials"),
    ),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/BSx12eCm40JGUxvYp_c68XQl5GJ1-ngdhHWsacpextTjUfl73iFsHJdhPotEqv3aYGm9e2coo2ulv_sD5aY59OkF55Zt94q3At9hcUuBpT1wchfhIo5wNJgQJ_21NFuARsmrecdyRN0iheTiziWN)



## Node Colors

Highlight important nodes or show status with colors:

### Single Node Color

```python
from plantuml_compose import wbs_diagram, render

d = wbs_diagram()
n = d.nodes

d.add(n.node("Project", color="LightBlue",
    n.leaf("Critical Task", color="Salmon"),
    n.leaf("Normal Task"),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAKygvjAALlR9JCyeSSefJOrL22ZApqfDBk7I0We79-RavkV5AZWNPPPa9YVcA8Ga5cS3PHJyyejoOLo7rBmKe340)



### Status Colors

```python
from plantuml_compose import wbs_diagram, render

d = wbs_diagram()
n = d.nodes

d.add(n.node("Sprint 1",
    n.node("Completed", color="#90EE90",
        n.leaf("Design"),
        n.leaf("Backend"),
    ),
    n.node("In Progress", color="#FFE4B5",
        n.leaf("Frontend"),
    ),
    n.node("Not Started", color="#E0E0E0",
        n.leaf("Testing"),
        n.leaf("Deployment"),
    ),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAKygvj9I22ueoimhKJ3aqjAALhOqS7MrD8XLSCxFBSX9BKbD0OfgARYa5cUcvu6PJed9sQbvAM35Rcwk9awciGgUUGe1HVdfHQd5nM0rRaNvUIKmHQu681Yhu9TVeX0CiXLgPaXgSKbcNZhK_8AS_ChSrBmIBWUWFg2x0000)



### Hex Colors

```python
from plantuml_compose import wbs_diagram, render

d = wbs_diagram()
n = d.nodes

d.add(n.node("Priorities", color="#E3F2FD",
    n.leaf("High", color="#F44336"),
    n.leaf("Medium", color="#FF9800"),
    n.leaf("Low", color="#4CAF50"),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAKygvjAALdOrTZDoSubL22ZAp2_ABCbC1Oe2XTrCJ8oDpM8LF3BJCo02RfOM1WQn2hwfAPcbkM0X4sT7DrEWa4z-EPT3QbuAq4G0)



## Boxless Nodes

Remove box outlines for a cleaner look:

```python
from plantuml_compose import wbs_diagram, render

d = wbs_diagram()
n = d.nodes

d.add(n.node("Main Topic",
    n.leaf("With box"),
    n.leaf("Without box", boxless=True),
    n.node("Boxless branch", boxless=True,
        n.leaf("Child node"),
    ),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAKygvj9Iy4tCp5C8oI_8JERIqb88pop9K4ZAhm2ouy6S_D8IEDyflo8djRXO8QaeCIyv0oYafU2SaPcJef2NdvBAvP2Qbm8q4W00)



### All Boxless

```python
from plantuml_compose import wbs_diagram, render

d = wbs_diagram()
n = d.nodes

d.add(n.node("Outline Style", boxless=True,
    n.node("Category A", boxless=True,
        n.leaf("Item 1", boxless=True),
        n.leaf("Item 2", boxless=True),
    ),
    n.node("Category B", boxless=True,
        n.leaf("Item 3", boxless=True),
    ),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAKygvjAAL_0lBSd9p4jL22wfp4dbqWAAE2UMfARd5rKgE0AvGBvdIMgkWY4IsmXLcHEIb36NGsfU2j1e0000)



## Multiline Text

Node text can span multiple lines using `\n`:

```python
from plantuml_compose import wbs_diagram, render

d = wbs_diagram()
n = d.nodes

d.add(n.node("Q1 Goals",
    n.leaf("Launch MVP\nby March 15"),
    n.leaf("Hire 3 engineers\nfor backend team"),
    n.leaf("Close Series A\n$5M target"),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAKygvj9I23HKSCzFp04ojQny4alpaZCKVCC2k98g5NmJYu0SGrDha9H7Pb6gWh52QbvwPbvgQb4nLrf-aK9IOd9sQbwAGabgOYvObNDEVd6gGd1gKMPgiO8ZbugfhmBGflJK4cik1w12e8q0)



## Arrows Between Nodes

WBS diagrams can show dependencies between work packages using refs and arrows:

### Basic Arrows

```python
from plantuml_compose import wbs_diagram, render

d = wbs_diagram()
n = d.nodes
c = d.connections

design = n.leaf("Design", ref="design")
dev = n.leaf("Develop", ref="dev")
test = n.leaf("Test", ref="test")

d.add(n.node("Project", design, dev, test))

d.connect(
    c.arrow(design, dev),
    c.arrow(dev, test),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAKygvj9I22ZApqfDBk7Iqb9GSaajpapFKr98B5P80JEXecMfEVa5KE4oi5X8Qd49MA04oE22A5RGjGFB0p682PPnICrB0Te30000)



### Complex Dependencies

```python
from plantuml_compose import wbs_diagram, render

d = wbs_diagram()
n = d.nodes
c = d.connections

api = n.leaf("API Design", ref="api")
db = n.leaf("Database", ref="db")
svc = n.leaf("Services", ref="svc")
ui = n.leaf("UI Design", ref="ui")
comp = n.leaf("Components", ref="comp")
integ = n.leaf("Integration", ref="integ")

d.add(n.node("Release",
    n.node("Backend", side="left", api, db, svc),
    n.node("Frontend", side="right", ui, comp, integ),
))

# Backend dependencies
d.connect(
    c.arrow(api, svc),
    c.arrow(db, svc),
)

# Frontend dependencies
d.connect(
    c.arrow(ui, comp),
    c.arrow(comp, integ),
)

# Cross-team dependency
d.connect(c.arrow(svc, integ))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/LO_H2i8m34NVznMXZmN_GCRK8UnD53yWRSCeQZkQRlw-MLSHNqBkkRbfsd76bD-66mrNUX8oDLhluOZsGS59Bq8TBWFqn7uC2f019r-D7ZCQoHJiJAKtIektn8NoOWMtS4unvBgo1NN_spZxYa_nDSL08MzXAx8wWwJ7XDd7BU9NtSWfi6lB8yvykxcmabtBAhPfCN-YasFauny0)



## Styling with diagram_style

Apply consistent styling across the entire diagram:

### Basic Styling

```python
from plantuml_compose import wbs_diagram, render

d = wbs_diagram(diagram_style={
    "background": "#FAFAFA",
    "font_name": "Arial",
})
n = d.nodes

d.add(n.node("Styled WBS",
    n.leaf("Child 1"),
    n.leaf("Child 2"),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgAKygvh8fBgdCIRNZ0h9TCXFJYn9p5Qgv51IS4fEpquloI_DIdFDpyeiKbDqSGH0euvQVL-ANc9kgu5YKcPZ3LSjbemyrGaiX6CH8KGXt2kRIqb9mpiZCIL4mH32Dk1nIyrA0DW40)



### Node Styling

```python
from plantuml_compose import wbs_diagram, render

d = wbs_diagram(diagram_style={
    "node": {
        "background": "#E3F2FD",
        "font_color": "#1565C0",
    }
})
n = d.nodes

d.add(n.node("Blue Theme",
    n.node("Branch A",
        n.leaf("Leaf 1"),
        n.leaf("Leaf 2"),
    ),
    n.leaf("Branch B"),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/JOvD2i8m48NtSue1TzbeAtLLfAOrAvTUO6p6LamJI5AabDxTK0gw-zuFZrU5I3v-7W7A42V3PqZSlAZpDE0CYDPfNW5HKllkl1kjhfrn7dVNeyfLisRAsRYvMN4gwaDo5rYWt6-p0gKP6Uyz3mmYAK-sxV6IME2DwOdP3_E_XeIAhKwllW00)



### Root Node Styling

Style the root node differently from other nodes:

```python
from plantuml_compose import wbs_diagram, render

d = wbs_diagram(diagram_style={
    "root_node": {
        "background": "#FF9800",
        "font_color": "white",
    },
    "node": {
        "background": "#FFF3E0",
    }
})
n = d.nodes

d.add(n.node("Highlighted Root",
    n.leaf("Normal child 1"),
    n.leaf("Normal child 2"),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/VOwz2W8n48JxVOe5kpH6RHGEEVm9LbVu1l4ISi5S5fALG-JUtH3j18k1ORvXc3QpJZpTCZIPdy7keVYJroxf4L-06CdOQX0Fkh-xH8zeZXGeuK8fjJdBmkQYHCJTt_9kAsLbYY9_qcdmREl03Cto-q3WnRiX5B4rU2sx80Hsb4OTi1zyCBZwITRGscZA-JS0)



### Leaf Node Styling

Style work packages (leaf nodes) differently:

```python
from plantuml_compose import wbs_diagram, render

d = wbs_diagram(diagram_style={
    "leaf_node": {
        "background": "#E8F5E9",
        "font_color": "#2E7D32",
    }
})
n = d.nodes

d.add(n.node("Root",
    n.node("Has children",
        n.leaf("Leaf A"),
        n.leaf("Leaf B"),
    ),
    n.leaf("Also a leaf"),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/HKvB2i8m5Do_KmouoqPGH8KYRMsB2t7X3PvDhCMO1qb4H7ftOocucnypauV8FhukWR8GtzRiAE6gvyxp0ny2hE7hIRGP2L1oU--yF9tUYnMFMRrfLlLsz1fnSL8NzRfQBf8wq43PVAfME8j4KWe73cXllTNUkCGLZca6nH-MlrHXWu372vGRfzErBm00)



### Arrow Styling

Customize the connecting lines:

```python
from plantuml_compose import wbs_diagram, render

d = wbs_diagram(diagram_style={
    "arrow": {
        "line_color": "#9E9E9E",
        "line_thickness": 2,
    }
})
n = d.nodes

d.add(n.node("Central",
    n.node("Branch 1",
        n.leaf("Detail"),
    ),
    n.leaf("Branch 2"),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/JOun2i9044NxESK7kst4T4AGO69dwGN6E9Z5THPc5e98xkug8lARnoiUl_F2LkQpK-lbaMH7bOV8L-CxdWImMPu_11oZIfzJDgosX_T-zZJ5yQRYZgQwXHPgrzzUG2zQZ1E5WBsnZXCsbGC6AHp_TKETwAKUU040)



### Combined Styling

```python
from plantuml_compose import wbs_diagram, render

d = wbs_diagram(diagram_style={
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
})
n = d.nodes

d.add(n.node("Styled WBS",
    n.node("Category A",
        n.leaf("Item 1"),
        n.leaf("Item 2"),
    ),
    n.node("Category B",
        n.leaf("Item 3"),
    ),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/VP112u9048Nl-oi6kdaf5So3XBgw44GN3vstt4pI7LWtHCB_tceB4eGC0s_cVJoOYJlDbUwl7OawFJJYG8pEQbuftiAR0AJyzgmKlcH9iK45cvpcZBd6aLYA6Va3KPQ56JNUQ5eXwlCAx0M-vuUpnr3gxxP_r5hOW4Rm-re0IwQoC5SAUqkUQYai4-psMPZEp4YYhJtMWM8I9LpIWZWEKAv5XMg0n4mE7BLemLsazyEaY-6JMCZIlEu3)



## Complete Examples

### Software Project WBS

```python
from plantuml_compose import wbs_diagram, render

d = wbs_diagram()
n = d.nodes

d.add(n.node("E-Commerce Platform",
    n.node("Planning", side="left",
        n.leaf("Requirements"),
        n.leaf("Architecture"),
        n.leaf("Timeline"),
    ),
    n.node("Development", side="left",
        n.node("Frontend",
            n.leaf("Product Pages"),
            n.leaf("Cart"),
            n.leaf("Checkout"),
        ),
        n.node("Backend",
            n.leaf("User API"),
            n.leaf("Product API"),
            n.leaf("Order API"),
        ),
    ),
    n.node("Testing", side="right",
        n.leaf("Unit Tests"),
        n.leaf("Integration"),
        n.leaf("UAT"),
    ),
    n.node("Deployment", side="right",
        n.leaf("Infrastructure"),
        n.leaf("CI/CD"),
        n.leaf("Monitoring"),
    ),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/NL11Ri8m4Bpp2fyZ8JvGHOIabNAe6g7m0ECimIBUXVKQrD_NZWD8lUsCPsPdlVMYMHv7lohKvxecvu0Dg6xISY9sgwBuI03HuXX1H7ku1SlW0CLdfc9pjW960aDcUkjWiWYplO4xJ7HDXlpwnOG2E2IKufc6O4HrUWI_S7KizHpFO2uK5kzEcylRUl30gkhQVqblveU7bw9KFNXPxYZL0QtCZC-uZPr6rc895q7Lpwu6hXFzFkiduOcr5mwlWqjLjvkwoUCtnM3Yj6SRcyQl_GC0)



### Event Planning WBS

```python
from plantuml_compose import wbs_diagram, render

d = wbs_diagram(diagram_style={
    "root_node": {"background": "#1976D2", "font_color": "white"},
    "node": {"background": "#E3F2FD"},
})
n = d.nodes

d.add(n.node("Annual Conference",
    n.node("Venue",
        n.leaf("Location Search"),
        n.leaf("Contract"),
        n.leaf("Layout"),
    ),
    n.node("Program",
        n.leaf("Keynotes"),
        n.leaf("Breakouts"),
        n.leaf("Workshops"),
    ),
    n.node("Marketing",
        n.leaf("Website"),
        n.leaf("Email"),
        n.leaf("Social"),
    ),
    n.node("Operations",
        n.leaf("Registration"),
        n.leaf("Catering"),
        n.leaf("AV Equipment"),
    ),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/VP1BQyD038Jl_XM2tdmfJQ2b44eUJYvzqa1wLjQgizYHKgrCC2N_lTxTzjh3mgUPGOns7WpLpljGp88D7JqK8rSU6yKZV1S0B3Kb05YYQnkLdkkLTA9mjPvk9fjgz2xZKn5x-ITyStztMqsIjn6sh9uFtYWjk1Ipwzy69IoOU-nW9Vn9IkoeA4lO4VSHIdWIX-Q5OKkexf2qCMkApd801-aZmfjAF2MfZpIm68KqB9Mm7KDv-X1jmq5ESO9dr9RCSvCjseTOClBwYBvBj1NdCIAydaXJcxpfdHeVB2kv61hftxB53jPVlJyTYQsO4zVZR_y0)



### Construction Project with Dependencies

```python
from plantuml_compose import wbs_diagram, render

d = wbs_diagram()
n = d.nodes
c = d.connections

survey = n.leaf("Survey", ref="survey")
excav = n.leaf("Excavation", ref="excav")
pour = n.leaf("Pour Concrete", ref="pour")
frame = n.leaf("Framing", ref="frame")
roof = n.leaf("Roofing", ref="roof")
ext = n.leaf("Exterior", ref="ext")

d.add(n.node("House Construction",
    n.node("Foundation", side="left", survey, excav, pour),
    n.node("Structure", side="right", frame, roof, ext),
))

# Foundation sequence
d.connect(
    c.arrow(survey, excav),
    c.arrow(excav, pour),
)

# Structure sequence
d.connect(
    c.arrow(pour, frame),
    c.arrow(frame, roof),
    c.arrow(frame, ext),
)

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/FP112eD034NtdYAu7EWDYWX5wRBK4qmr5XUTb4p6sjjt4iTkGjx_uIUaZU9PFezOERXIYWWN2b4uZR9Gg9mxGqyfJBvWvdf8lEAt1XyXMblqRXlzQeFceMAnRfHOaqT6GNFVMSbc0uCjIumwsa3TityjuMb3S-uF_Kuq7phdliZT9iWBSLafrNuId9foW5L5swX5OK-sgcY1VzAO5iEKt_83)



### Product Roadmap

```python
from plantuml_compose import wbs_diagram, render

d = wbs_diagram()
n = d.nodes

d.add(n.node("2024 Roadmap",
    n.node("Q1", color="#BBDEFB",
        n.leaf("MVP Launch"),
        n.leaf("Beta Testing"),
    ),
    n.node("Q2", color="#C8E6C9",
        n.leaf("User Feedback"),
        n.leaf("Performance"),
    ),
    n.node("Q3", color="#FFF9C4",
        n.leaf("New Features"),
        n.leaf("Integrations"),
    ),
    n.node("Q4", color="#FFCCBC",
        n.leaf("Scale"),
        n.leaf("Enterprise"),
    ),
))

print(render(d))
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
| `n.node(text, *children)` | Create a branch node with children |
| `n.leaf(text)` | Create a leaf node (no children) |
| `d.add(root_node)` | Register the root node tree |
| `c.arrow(source, target)` | Create a dependency arrow |
| `d.connect(...)` | Register arrows |

### Node Parameters

| Parameter | Description |
|-----------|-------------|
| `text` | Node label (required) |
| `side="left"` | Force to left side |
| `side="right"` | Force to right side |
| `ref="name"` | ID for arrow connections |
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
