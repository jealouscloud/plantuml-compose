# Mind Map Diagrams

Mind maps are tree diagrams that radiate outward from a central idea. They're excellent for:

- **Brainstorming**: Capture ideas and see connections
- **Note-taking**: Organize information hierarchically
- **Project planning**: Break down tasks into subtasks
- **Concept mapping**: Show relationships between ideas

A mind map starts with one central topic, then branches out to related subtopics, which can have their own branches.

## Core Concepts

**Root node**: The central topic at the center of the diagram.

**Branch**: A line connecting a parent node to a child node.

**Child node**: A subtopic that branches from a parent. Can have its own children.

**Leaf node**: A node with no children (end of a branch).

**Side**: Branches can go left or right from the root. By default, PlantUML balances them automatically.

## Your First Mind Map

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram() as d:
    with d.node("Project Planning") as root:
        root.leaf("Requirements")
        root.leaf("Timeline")
        root.leaf("Resources")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/9Sp13O0W34RXErDmPWf68CO52FunDRHeM_PNm_7b9Lysh-fCSd2zGuf5nuNciVGgGdA6bEA6PvA28Mv_xyJe95ZFnjG62ncViPmN)



This creates a simple mind map with one central topic and three branches.

## Building Node Hierarchies

### Leaf Nodes (No Children)

Use `leaf()` when a node has no children:

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram() as d:
    with d.node("Fruits") as root:
        root.leaf("Apple")
        root.leaf("Banana")
        root.leaf("Cherry")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgoStCIybDBE3IKd0hAiqiAURIqb9mB2Z8IGKnd1BpW134Siv8BIggv7981Qg6w000)



### Nested Branches

Use `node()` as a context manager to add children to a branch:

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram() as d:
    with d.node("Animals") as root:
        with root.node("Mammals") as mammals:
            mammals.leaf("Dog")
            mammals.leaf("Cat")
            mammals.leaf("Elephant")
        with root.node("Birds") as birds:
            birds.leaf("Eagle")
            birds.leaf("Sparrow")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgoStCIybDBE3IKd3CoynDp2dcqj9Iy4tCXJAr55poqy6qSs89c7RDIIt8ICm3SHISCejI8AfS4zDpKi6iu8B4egBySYw7LA314CC1)



### Deep Nesting

You can nest as deeply as needed:

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram() as d:
    with d.node("Software Development") as root:
        with root.node("Frontend") as frontend:
            with frontend.node("Frameworks") as frameworks:
                frameworks.leaf("React")
                frameworks.leaf("Vue")
                frameworks.leaf("Angular")
            frontend.leaf("CSS")
            frontend.leaf("HTML")
        with root.node("Backend") as backend:
            backend.leaf("Python")
            backend.leaf("Node.js")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/DOwz3i8m38JtF4Nc33n3WGen0484TRSQyzV6hXoNYhUdIM6wxtIdqrL9GJG-AKGOZBEURpg1eAtnZJqF4KcDStOdJ8eKPiu68auiNShMsGj2gmis8owmfllOWvJ-rlkY--lnaCSsq7R_hVD77qm5JnnmzKgcchFVeoy0)



## Controlling Branch Direction

By default, branches spread left and right automatically. You can force a branch to one side:

### Force Left Side

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram() as d:
    with d.node("Central Topic") as root:
        with root.node("Left Branch 1", side="left") as left1:
            left1.leaf("Item A")
        with root.node("Left Branch 2", side="left") as left2:
            left2.leaf("Item B")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgoStCIybDBE3IKd1EpIifIinH2Calo4pcqjLLy4bDAr5mAahCIyvGC0GAw2fubgJcAZYYonaXv9ou75A1va7C1000)



### Force Right Side

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram() as d:
    with d.node("Central Topic") as root:
        with root.node("Right Branch 1", side="right") as right1:
            right1.leaf("Item A")
        with root.node("Right Branch 2", side="right") as right2:
            right2.leaf("Item B")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgoStCIybDBE3IKd1EpIifIinH2Calo4pcqjPM2CfCpoXHS2fAp4lEK304YcWhU9QavYeuOaWQ8IITk1nIWIP2J0K0)



### Mixed Sides

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram() as d:
    with d.node("Pros and Cons") as root:
        with root.node("Pros", side="right") as pros:
            pros.leaf("Fast")
            pros.leaf("Reliable")
            pros.leaf("Affordable")
        with root.node("Cons", side="left") as cons:
            cons.leaf("Learning curve")
            cons.leaf("Limited support")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/9Or12iCm30JlVeNEDVv3Ig2d7af_eCPA4CIoaPI-FyO-xSp2ieivgXUMNB251toq6g1aMAjOY74KFIEyq7p0bqx6tqb3dljUDGzDQOvIXpUX2ii1swL_cXKNTifWLsjLFIpKF-Vl3G00)



## Node Colors

Add background colors to any node:

### Single Node Color

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram() as d:
    with d.node("Topic", color="LightBlue") as root:
        root.leaf("Normal child")
        root.leaf("Another child", color="LightGreen")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgoStCIybDBE3IYbRsoKpFA77AAKsDLGZ9ByXCvjBIKl3BByfDp558piZCIG7oeOhSYr9Jys8L7FFoIp9IYw2o3gb0ao2c0G00)



### Color-Coded Categories

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram() as d:
    with d.node("Project Status") as root:
        with root.node("Completed", color="#90EE90") as done:
            done.leaf("Research")
            done.leaf("Design")
        with root.node("In Progress", color="#FFE4B5") as progress:
            progress.leaf("Development")
        with root.node("Blocked", color="#FFB6C1") as blocked:
            blocked.leaf("Testing")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/BOwz2i8m54RtF4N0BLC55RgLr1JSHDqaGqWlCPe_Sgy-lxLc_3uEXpCWcKhHfpcQmWG_r_m4I_nAXjx8XBXl-awfljDypB4489YNL_0B89Xg7-iu0dgNLdgQr4xkDJ-bdyjLG6p81q8k4H8rJXx6hUOoPFjgpXiW-UJO04lEF-aB)



### Hex Colors

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram() as d:
    with d.node("Colors", color="#E3F2FD") as root:
        root.leaf("Blue", color="#2196F3")
        root.leaf("Green", color="#4CAF50")
        root.leaf("Orange", color="#FF9800")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgoStCIybDBE3IYbPsDNOpSdE9LN3EpyalAkRI0WeP6LgQkHd7AZZbbAQ21KoS7TrC3M8Lt8jIK_F08cvkbXO6G17_eiIyz5GkXrIWUH0p0G00)



## Boxless Nodes

Remove the box outline from nodes for a cleaner look:

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram() as d:
    with d.node("Main Topic") as root:
        root.leaf("Normal node")
        root.leaf("Boxless node", boxless=True)
        with root.node("Boxless branch", boxless=True) as branch:
            branch.leaf("Child of boxless")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgoStCIybDBE3IKl1DpCnJ2Calo4pcqj9IyCiloatCKSZBJqa5SkCLdF8hSbABYp45aeeIyv8pW49Q2iuPcJaf2lbf2aaGEIw7LA3X40i0)



### All Boxless

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram() as d:
    with d.node("Outline Style", boxless=True) as root:
        with root.node("Category A", boxless=True) as a:
            a.leaf("Item 1", boxless=True)
            a.leaf("Item 2", boxless=True)
        with root.node("Category B", boxless=True) as b:
            b.leaf("Item 3", boxless=True)

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgoStCIybDBE3IYbVmBot9oSnBLGWkgSn9vT82YZWdbgIcvnTLAZW2kK2-Pqbghe8X4ji8LPaJafGnbqCgq6Y8yG00)



## Multiline Text

Node text can span multiple lines using `\n`:

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram() as d:
    with d.node("Project\nOverview") as root:
        root.leaf("Phase 1\nResearch\n2 weeks")
        root.leaf("Phase 2\nDevelopment\n4 weeks")
        root.leaf("Phase 3\nTesting\n2 weeks")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/POsn3a0m54NtznLccpAn6En4_41JDnGjwNkftoSna5ZFoScfMNGGP_tez45fsOLzWH5g8qAqE2jARpXhHf9H3uOEPYQLdC3A7wceGSIs7mvUgFZvd0QmM3-zROrx-eml)



## Diagram Direction

Control the overall layout direction:

### Top to Bottom

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram(direction="top_to_bottom") as d:
    with d.node("Root") as root:
        root.leaf("Child 1")
        root.leaf("Child 2")
        root.leaf("Child 3")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgoStCIybDBE0goIzGACbNICelASdFLKZ9B4fDBidCp-FIKWZApo_Xqj9ISCx8p4bHC4GmZH1COow7LA0v4BC0)



### Left to Right

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram(direction="left_to_right") as d:
    with d.node("Start") as root:
        with root.node("Step 1") as s1:
            s1.leaf("Detail A")
        with root.node("Step 2") as s2:
            s2.leaf("Detail B")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgoStCIybDBE3AIKqhKIZ9LoZAJCyeKKZ9B4fDBidCp-FIKWW6AUFI0Z5I2nGCWImj1PVKaiJC70L7kB0Hih0JbqCgq5I8oG00)



### Right to Left

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram(direction="right_to_left") as d:
    with d.node("End Goal") as root:
        root.leaf("Requirement 1")
        root.leaf("Requirement 2")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgoStCIybDBE0goapFA54eoLV8IKqhKKZ9B4fDBidCp-FIKd3DIr5mpq_CuTBIKWXABIm5IkMcvfKe6A8B674vf08DWnW80000)



## Styling with diagram_style

Apply consistent styling across the entire diagram:

### Basic Styling

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram(diagram_style={
    "background": "#FAFAFA",
    "font_name": "Arial",
}) as d:
    with d.node("Styled Map") as root:
        root.leaf("Child 1")
        root.leaf("Child 2")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgoStCIybDBE2oAIwfp4cruuBoNJ8JquiISnMgkHGKd1AJizEByalpKfppS_AB59JT744GAEEMdrVYbvYRgk1Ob9cOmrNBPQCFDKPB8HZ4I57m1PgjfQNWd96Paw9WY60QSJca0cs2s0O0)



### Node Styling

Style all nodes at once:

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram(diagram_style={
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
![Diagram](https://www.plantuml.com/plantuml/svg/JOwz3e8m58Nt-nGtSMDHC3WHWmKxEVe2D_GAnFwGKWPZU7SRRABRTtvoSkeva0zcjChG1DKSNfhFa7GxKk_9u1iGhLEy0QAWxjbxjrZLEEqyxgv7MSXsowIp8RbvUIgRGtHNMA7Qf-aCXLuOxmCRXYmgJxORy18vmnlJ0_CV5dyD0JN7Lzzd7m00)



### Root Node Styling

Style the root node differently:

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram(diagram_style={
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
![Diagram](https://www.plantuml.com/plantuml/svg/VK_B2i8m4BpdAnQyvMBKYqAHOZLuwi4_24r8WabMqXKHwRyRqju43mCx3uRPTYILAVgaetgmPgHtC4UsyBDNDgi87mQGK9jw09pKSBSPdqbt6333IagvkuZYJGKPaVg_uSDUYEf9J3IhB-V9r8A9DUjb1OUhjouKaD5mAxsCS-WnHnLWS3vesFmeMzQQCdv-u0i0)



### Leaf Node Styling

Style leaf nodes (nodes without children):

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram(diagram_style={
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
![Diagram](https://www.plantuml.com/plantuml/svg/HOx12i8m38RlUOg0jrw4YQWmP9lRy20UV8Emrbdi6cdhGMJlRgq5R_d-FoHVvGEvC6ah9tf0wSFBg3raRZMDZYPy0w9HT3spL0aG6nhke-EdbGSsx73HRVjrjqjTppRajEWsxQg8wGmpbCjyNk25EO0GU2IFmqqRwPIDBF0Kts3z7vllLcqy8oK5g5HK--bz0000)



### Arrow Styling

Customize the connecting lines:

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram(diagram_style={
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
![Diagram](https://www.plantuml.com/plantuml/svg/JOwz2i9048JxVOe1ksl4T4AGO69dwGiiSJ67zoDx2oAIT_VK83BDDrynJ5UCrQ9FvyWtQeizWknewOFdYtB4am1MpVSF0KUVfCyXArRRmpi_UvhyU4rI2fhgPfgfNI-R3hqaKmxa7FRAQPomgUmmYB7_rmrrKWzyJxm0)



### Combined Styling

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram(diagram_style={
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
    with d.node("Styled Mind Map") as root:
        with root.node("Category A") as a:
            a.leaf("Item 1")
            a.leaf("Item 2")
        with root.node("Category B") as b:
            b.leaf("Item 3")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/VP312e9048Rl-nG3tRnK2kP1GbrT2B9BJx3aPfBknBeX4hvxgov8438CpCp_ySFyKQkvqaqbYuQ_IDZglXP7OlUqugNY3Nm8GC9lprBXMnOKQrImoMZ6sDue4Win8NyWoj8WfKORJ2j4VLc1NTzplM3I64ezNxj7fOKrg0M_hncmU2mBSwMmi-Ivai8o_kwG1id432JSseSTk8v30Rdv778JXUC0vLgKg7g8pUR0IOi6zile_Z398dWa4YQ_ESCl)



## Complete Examples

### Project Breakdown

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram() as d:
    with d.node("Website Redesign") as root:
        with root.node("Research", side="left") as research:
            research.leaf("User interviews")
            research.leaf("Competitor analysis")
            research.leaf("Analytics review")
        with root.node("Design", side="left") as design:
            design.leaf("Wireframes")
            design.leaf("Mockups")
            design.leaf("Prototype")
        with root.node("Development", side="right") as dev:
            dev.leaf("Frontend")
            dev.leaf("Backend")
            dev.leaf("Database")
        with root.node("Launch", side="right") as launch:
            launch.leaf("Testing")
            launch.leaf("Deployment")
            launch.leaf("Monitoring")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/FL11JiD03Bpd5NicoXyAL9oeX12ePpSPYjMilRBTeloUtOHocncFnoFlFCWYiqoPIlUGZZWv1z8x9ZYVfHk6YXrautV5G_fqM689s8tnuwlshBaWEDGI2SsBywO_DX8yUZ8qTmlRtsE7T6J3br76vZxeUBcM3R-PXiPIqFLzNRbXrf8XKMcVNaphVPbMyaJZvOxt57GYNvTUwIgrSfC_uC5otYmeiox_KGULLhjDTpNbxm-_)



### Decision Tree

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram() as d:
    with d.node("Should I learn Python?") as root:
        with root.node("Yes", side="right", color="#C8E6C9") as yes:
            yes.leaf("Many job opportunities")
            yes.leaf("Easy to learn")
            yes.leaf("Versatile language")
        with root.node("Consider", side="left", color="#FFF9C4") as maybe:
            maybe.leaf("Time investment")
            maybe.leaf("Your goals")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/BOv12u9044Rl-oi6l2NU8lAKi2Xq288Y4F4muQ0RwupiZe7_Fj6Et_lWyOge67Hqt8qucGCy1fbz1rVmX87XlkWWV35fsYJsN9vita9DSTqft90N-CWRP9eawCnEtVygCIwWiaisyg8GKPqdyCZzZ3sPB6kIggfoUsp12aVNKLXX1ayt4ZZ-KjIHM3TMonoW5_JH5BJ6xi4_)



### Study Notes

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram(diagram_style={
    "root_node": {"background": "#1976D2", "font_color": "white"},
    "node": {"background": "#E3F2FD"},
}) as d:
    with d.node("Python Basics") as root:
        with root.node("Data Types") as types:
            types.leaf("int, float")
            types.leaf("str")
            types.leaf("list, tuple")
            types.leaf("dict, set")
        with root.node("Control Flow") as flow:
            flow.leaf("if/elif/else")
            flow.leaf("for loops")
            flow.leaf("while loops")
        with root.node("Functions") as funcs:
            funcs.leaf("def keyword")
            funcs.leaf("Parameters")
            funcs.leaf("Return values")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/VP3TQiCm38NlynI2tOL1MGiRWpBAclbobB4NCB7IcYfMiEM6CFhkK-soortuvzCvI0VjajWeemzkj5EpJR8GlZLtxhmzHZl2JmCGs67v0BpR_doCd8FRCt64Xu-DMPjEjQkUo2oV_vYVNb-UktNH30UfrVda1Kk3QxDTtLEqS5Zan45x9D-dfcsXisBXUvdmHYtu88ym45ifc2IMbtpIkkI9iB3plNB2cmlsEZGoWI6UQvDXXLIkLEs31YBcgSxGQ8H_32Q7NZo7AZeSu8pBpD4LFbZT5mh6Ad-Xv1ZWOYbhuXtgLkjcVm40)



### Org Chart

```python
from plantuml_compose import mindmap_diagram

with mindmap_diagram(direction="top_to_bottom") as d:
    with d.node("CEO", color="#FFD54F") as ceo:
        with ceo.node("CTO") as cto:
            cto.leaf("Engineering")
            cto.leaf("QA")
        with ceo.node("CFO") as cfo:
            cfo.leaf("Accounting")
            cfo.leaf("Finance")
        with ceo.node("COO") as coo:
            coo.leaf("Operations")
            coo.leaf("HR")

print(d.render())
```
![Diagram](https://www.plantuml.com/plantuml/svg/DOwn2iCm34HtVuMWc-TsJqWZkfc6RgM3wuYWmP9nrFzlOzFfEDw3ks6tM2sph3aMPrh05DvgfXbMhfICLPn_dX2lbpE-O9g3ynwcnn4UPjbOY2hBrlfzR1Gx7LFIZzWV8akKHCq8tGY5QZmszbPlYnlezwN_-G80)



## Quick Reference

### Diagram Creation

| Code | Description |
|------|-------------|
| `mindmap_diagram()` | Create a mind map |
| `direction="top_to_bottom"` | Vertical layout |
| `direction="left_to_right"` | Horizontal (left start) |
| `direction="right_to_left"` | Horizontal (right start) |
| `diagram_style={...}` | Apply styling |

### Node Methods

| Method | Description |
|--------|-------------|
| `d.node(text)` | Add root node (use as context manager) |
| `root.node(text)` | Add child branch (use as context manager) |
| `root.leaf(text)` | Add leaf node (no children) |

### Node Parameters

| Parameter | Description |
|-----------|-------------|
| `text` | Node label (required) |
| `side="left"` | Force to left side |
| `side="right"` | Force to right side |
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
