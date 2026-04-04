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
from plantuml_compose import mindmap_diagram, render

d = mindmap_diagram()
n = d.nodes

d.add(n.node("Project Planning",
    n.leaf("Requirements"),
    n.leaf("Timeline"),
    n.leaf("Resources"),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/9Sp13O0W34RXErDmPWf68CO52FunDRHeM_PNm_7b9Lysh-fCSd2zGuf5nuNciVGgGdA6bEA6PvA28Mv_xyJe95ZFnjG62ncViPmN)



This creates a simple mind map with one central topic and three branches.

## Building Node Hierarchies

### Leaf Nodes (No Children)

Use `leaf()` when a node has no children:

```python
from plantuml_compose import mindmap_diagram, render

d = mindmap_diagram()
n = d.nodes

d.add(n.node("Fruits",
    n.leaf("Apple"),
    n.leaf("Banana"),
    n.leaf("Cherry"),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgoStCIybDBE3IKd0hAiqiAURIqb9mB2Z8IGKnd1BpW134Siv8BIggv7981Qg6w000)



### Nested Branches

Use `node()` with child arguments to add children to a branch:

```python
from plantuml_compose import mindmap_diagram, render

d = mindmap_diagram()
n = d.nodes

d.add(n.node("Animals",
    n.node("Mammals",
        n.leaf("Dog"),
        n.leaf("Cat"),
        n.leaf("Elephant"),
    ),
    n.node("Birds",
        n.leaf("Eagle"),
        n.leaf("Sparrow"),
    ),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgoStCIybDBE3IKd3CoynDp2dcqj9Iy4tCXJAr55poqy6qSs89c7RDIIt8ICm3SHISCejI8AfS4zDpKi6iu8B4egBySYw7LA314CC1)



### Deep Nesting

You can nest as deeply as needed:

```python
from plantuml_compose import mindmap_diagram, render

d = mindmap_diagram()
n = d.nodes

d.add(n.node("Software Development",
    n.node("Frontend",
        n.node("Frameworks",
            n.leaf("React"),
            n.leaf("Vue"),
            n.leaf("Angular"),
        ),
        n.leaf("CSS"),
        n.leaf("HTML"),
    ),
    n.node("Backend",
        n.leaf("Python"),
        n.leaf("Node.js"),
    ),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/DOwz3i8m38JtF4Nc33n3WGen0484TRSQyzV6hXoNYhUdIM6wxtIdqrL9GJG-AKGOZBEURpg1eAtnZJqF4KcDStOdJ8eKPiu68auiNShMsGj2gmis8owmfllOWvJ-rlkY--lnaCSsq7R_hVD77qm5JnnmzKgcchFVeoy0)



## Controlling Branch Direction

By default, branches spread left and right automatically. You can force a branch to one side:

### Force Left Side

```python
from plantuml_compose import mindmap_diagram, render

d = mindmap_diagram()
n = d.nodes

d.add(n.node("Central Topic",
    n.node("Left Branch 1",
        n.leaf("Item A"),
        side="left",
    ),
    n.node("Left Branch 2",
        n.leaf("Item B"),
        side="left",
    ),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgoStCIybDBE3IKd1EpIifIinH2Calo4pcqjLLy4bDAr5mAahCIyvGC0GAw2fubgJcAZYYonaXv9ou75A1va7C1000)



### Force Right Side

```python
from plantuml_compose import mindmap_diagram, render

d = mindmap_diagram()
n = d.nodes

d.add(n.node("Central Topic",
    n.node("Right Branch 1",
        n.leaf("Item A"),
        side="right",
    ),
    n.node("Right Branch 2",
        n.leaf("Item B"),
        side="right",
    ),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgoStCIybDBE3IKd1EpIifIinH2Calo4pcqjPM2CfCpoXHS2fAp4lEK304YcWhU9QavYeuOaWQ8IITk1nIWIP2J0K0)



### Mixed Sides

```python
from plantuml_compose import mindmap_diagram, render

d = mindmap_diagram()
n = d.nodes

d.add(n.node("Pros and Cons",
    n.node("Pros",
        n.leaf("Fast"),
        n.leaf("Reliable"),
        n.leaf("Affordable"),
        side="right",
    ),
    n.node("Cons",
        n.leaf("Learning curve"),
        n.leaf("Limited support"),
        side="left",
    ),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/9Or12iCm30JlVeNEDVv3Ig2d7af_eCPA4CIoaPI-FyO-xSp2ieivgXUMNB251toq6g1aMAjOY74KFIEyq7p0bqx6tqb3dljUDGzDQOvIXpUX2ii1swL_cXKNTifWLsjLFIpKF-Vl3G00)



## Node Colors

Add background colors to any node:

### Single Node Color

```python
from plantuml_compose import mindmap_diagram, render

d = mindmap_diagram()
n = d.nodes

d.add(n.node("Topic",
    n.leaf("Normal child"),
    n.leaf("Another child", color="LightGreen"),
    color="LightBlue",
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgoStCIybDBE3IYbRsoKpFA77AAKsDLGZ9ByXCvjBIKl3BByfDp558piZCIG7oeOhSYr9Jys8L7FFoIp9IYw2o3gb0ao2c0G00)



### Color-Coded Categories

```python
from plantuml_compose import mindmap_diagram, render

d = mindmap_diagram()
n = d.nodes

d.add(n.node("Project Status",
    n.node("Completed",
        n.leaf("Research"),
        n.leaf("Design"),
        color="#90EE90",
    ),
    n.node("In Progress",
        n.leaf("Development"),
        color="#FFE4B5",
    ),
    n.node("Blocked",
        n.leaf("Testing"),
        color="#FFB6C1",
    ),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/BOwz2i8m54RtF4N0BLC55RgLr1JSHDqaGqWlCPe_Sgy-lxLc_3uEXpCWcKhHfpcQmWG_r_m4I_nAXjx8XBXl-awfljDypB4489YNL_0B89Xg7-iu0dgNLdgQr4xkDJ-bdyjLG6p81q8k4H8rJXx6hUOoPFjgpXiW-UJO04lEF-aB)



### Hex Colors

```python
from plantuml_compose import mindmap_diagram, render

d = mindmap_diagram()
n = d.nodes

d.add(n.node("Colors",
    n.leaf("Blue", color="#2196F3"),
    n.leaf("Green", color="#4CAF50"),
    n.leaf("Orange", color="#FF9800"),
    color="#E3F2FD",
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgoStCIybDBE3IYbPsDNOpSdE9LN3EpyalAkRI0WeP6LgQkHd7AZZbbAQ21KoS7TrC3M8Lt8jIK_F08cvkbXO6G17_eiIyz5GkXrIWUH0p0G00)



## Boxless Nodes

Remove the box outline from nodes for a cleaner look:

```python
from plantuml_compose import mindmap_diagram, render

d = mindmap_diagram()
n = d.nodes

d.add(n.node("Main Topic",
    n.leaf("Normal node"),
    n.leaf("Boxless node", boxless=True),
    n.node("Boxless branch",
        n.leaf("Child of boxless"),
        boxless=True,
    ),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgoStCIybDBE3IKl1DpCnJ2Calo4pcqj9IyCiloatCKSZBJqa5SkCLdF8hSbABYp45aeeIyv8pW49Q2iuPcJaf2lbf2aaGEIw7LA3X40i0)



### All Boxless

```python
from plantuml_compose import mindmap_diagram, render

d = mindmap_diagram()
n = d.nodes

d.add(n.node("Outline Style",
    n.node("Category A",
        n.leaf("Item 1", boxless=True),
        n.leaf("Item 2", boxless=True),
        boxless=True,
    ),
    n.node("Category B",
        n.leaf("Item 3", boxless=True),
        boxless=True,
    ),
    boxless=True,
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgoStCIybDBE3IYbVmBot9oSnBLGWkgSn9vT82YZWdbgIcvnTLAZW2kK2-Pqbghe8X4ji8LPaJafGnbqCgq6Y8yG00)



## Multiline Text

Node text can span multiple lines using `\n`:

```python
from plantuml_compose import mindmap_diagram, render

d = mindmap_diagram()
n = d.nodes

d.add(n.node("Project\nOverview",
    n.leaf("Phase 1\nResearch\n2 weeks"),
    n.leaf("Phase 2\nDevelopment\n4 weeks"),
    n.leaf("Phase 3\nTesting\n2 weeks"),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/POsn3a0m54NtznLccpAn6En4_41JDnGjwNkftoSna5ZFoScfMNGGP_tez45fsOLzWH5g8qAqE2jARpXhHf9H3uOEPYQLdC3A7wceGSIs7mvUgFZvd0QmM3-zROrx-eml)



## Diagram Direction

Control the overall layout direction:

### Top to Bottom

```python
from plantuml_compose import mindmap_diagram, render

d = mindmap_diagram(direction="top_to_bottom")
n = d.nodes

d.add(n.node("Root",
    n.leaf("Child 1"),
    n.leaf("Child 2"),
    n.leaf("Child 3"),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgoStCIybDBE0goIzGACbNICelASdFLKZ9B4fDBidCp-FIKWZApo_Xqj9ISCx8p4bHC4GmZH1COow7LA0v4BC0)



### Left to Right

```python
from plantuml_compose import mindmap_diagram, render

d = mindmap_diagram(direction="left_to_right")
n = d.nodes

d.add(n.node("Start",
    n.node("Step 1",
        n.leaf("Detail A"),
    ),
    n.node("Step 2",
        n.leaf("Detail B"),
    ),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgoStCIybDBE3AIKqhKIZ9LoZAJCyeKKZ9B4fDBidCp-FIKWW6AUFI0Z5I2nGCWImj1PVKaiJC70L7kB0Hih0JbqCgq5I8oG00)



### Right to Left

```python
from plantuml_compose import mindmap_diagram, render

d = mindmap_diagram(direction="right_to_left")
n = d.nodes

d.add(n.node("End Goal",
    n.leaf("Requirement 1"),
    n.leaf("Requirement 2"),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgoStCIybDBE0goapFA54eoLV8IKqhKKZ9B4fDBidCp-FIKd3DIr5mpq_CuTBIKWXABIm5IkMcvfKe6A8B674vf08DWnW80000)



## Styling with diagram_style

Apply consistent styling across the entire diagram:

### Basic Styling

```python
from plantuml_compose import mindmap_diagram, render

d = mindmap_diagram(diagram_style={
    "background": "#FAFAFA",
    "font_name": "Arial",
})
n = d.nodes

d.add(n.node("Styled Map",
    n.leaf("Child 1"),
    n.leaf("Child 2"),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/SoWkIImgoStCIybDBE2oAIwfp4cruuBoNJ8JquiISnMgkHGKd1AJizEByalpKfppS_AB59JT744GAEEMdrVYbvYRgk1Ob9cOmrNBPQCFDKPB8HZ4I57m1PgjfQNWd96Paw9WY60QSJca0cs2s0O0)



### Node Styling

Style all nodes at once:

```python
from plantuml_compose import mindmap_diagram, render

d = mindmap_diagram(diagram_style={
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
![Diagram](https://www.plantuml.com/plantuml/svg/JOwz3e8m58Nt-nGtSMDHC3WHWmKxEVe2D_GAnFwGKWPZU7SRRABRTtvoSkeva0zcjChG1DKSNfhFa7GxKk_9u1iGhLEy0QAWxjbxjrZLEEqyxgv7MSXsowIp8RbvUIgRGtHNMA7Qf-aCXLuOxmCRXYmgJxORy18vmnlJ0_CV5dyD0JN7Lzzd7m00)



### Root Node Styling

Style the root node differently:

```python
from plantuml_compose import mindmap_diagram, render

d = mindmap_diagram(diagram_style={
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
![Diagram](https://www.plantuml.com/plantuml/svg/VK_B2i8m4BpdAnQyvMBKYqAHOZLuwi4_24r8WabMqXKHwRyRqju43mCx3uRPTYILAVgaetgmPgHtC4UsyBDNDgi87mQGK9jw09pKSBSPdqbt6333IagvkuZYJGKPaVg_uSDUYEf9J3IhB-V9r8A9DUjb1OUhjouKaD5mAxsCS-WnHnLWS3vesFmeMzQQCdv-u0i0)



### Leaf Node Styling

Style leaf nodes (nodes without children):

```python
from plantuml_compose import mindmap_diagram, render

d = mindmap_diagram(diagram_style={
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
![Diagram](https://www.plantuml.com/plantuml/svg/HOx12i8m38RlUOg0jrw4YQWmP9lRy20UV8Emrbdi6cdhGMJlRgq5R_d-FoHVvGEvC6ah9tf0wSFBg3raRZMDZYPy0w9HT3spL0aG6nhke-EdbGSsx73HRVjrjqjTppRajEWsxQg8wGmpbCjyNk25EO0GU2IFmqqRwPIDBF0Kts3z7vllLcqy8oK5g5HK--bz0000)



### Arrow Styling

Customize the connecting lines:

```python
from plantuml_compose import mindmap_diagram, render

d = mindmap_diagram(diagram_style={
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
![Diagram](https://www.plantuml.com/plantuml/svg/JOwz2i9048JxVOe1ksl4T4AGO69dwGiiSJ67zoDx2oAIT_VK83BDDrynJ5UCrQ9FvyWtQeizWknewOFdYtB4am1MpVSF0KUVfCyXArRRmpi_UvhyU4rI2fhgPfgfNI-R3hqaKmxa7FRAQPomgUmmYB7_rmrrKWzyJxm0)



### Combined Styling

```python
from plantuml_compose import mindmap_diagram, render

d = mindmap_diagram(diagram_style={
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

d.add(n.node("Styled Mind Map",
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
![Diagram](https://www.plantuml.com/plantuml/svg/VP312e9048Rl-nG3tRnK2kP1GbrT2B9BJx3aPfBknBeX4hvxgov8438CpCp_ySFyKQkvqaqbYuQ_IDZglXP7OlUqugNY3Nm8GC9lprBXMnOKQrImoMZ6sDue4Win8NyWoj8WfKORJ2j4VLc1NTzplM3I64ezNxj7fOKrg0M_hncmU2mBSwMmi-Ivai8o_kwG1id432JSseSTk8v30Rdv778JXUC0vLgKg7g8pUR0IOi6zile_Z398dWa4YQ_ESCl)


### Depth-Based Styling

Style nodes by their tree depth level. Keys are integers where 0 = root, 1 = first children, 2 = grandchildren, etc. This is a powerful way to create visual hierarchy without setting colors on individual nodes:

```python
from plantuml_compose import mindmap_diagram, render

d = mindmap_diagram(diagram_style={
    "depths": {
        0: {"background": "#1976D2", "font_color": "white"},
        1: {"background": "#BBDEFB"},
        2: {"background": "#E3F2FD"},
    },
})
n = d.nodes

d.add(n.node("Architecture",
    n.node("Frontend",
        n.leaf("React"),
        n.leaf("TypeScript"),
    ),
    n.node("Backend",
        n.leaf("Python"),
        n.leaf("PostgreSQL"),
    ),
))

print(render(d))
```

Depth styles can be combined with other selectors. More specific selectors (like `root_node` or individual `color=`) take precedence.



## Mainframe

Add a titled border around the entire diagram with `mainframe=`:

```python
from plantuml_compose import mindmap_diagram, render

d = mindmap_diagram(mainframe="Project Overview")
n = d.nodes

d.add(n.node("Website Redesign",
    n.leaf("Research"),
    n.leaf("Design"),
    n.leaf("Development"),
))

print(render(d))
```

## Complete Examples

### Project Breakdown

```python
from plantuml_compose import mindmap_diagram, render

d = mindmap_diagram()
n = d.nodes

d.add(n.node("Website Redesign",
    n.node("Research",
        n.leaf("User interviews"),
        n.leaf("Competitor analysis"),
        n.leaf("Analytics review"),
        side="left",
    ),
    n.node("Design",
        n.leaf("Wireframes"),
        n.leaf("Mockups"),
        n.leaf("Prototype"),
        side="left",
    ),
    n.node("Development",
        n.leaf("Frontend"),
        n.leaf("Backend"),
        n.leaf("Database"),
        side="right",
    ),
    n.node("Launch",
        n.leaf("Testing"),
        n.leaf("Deployment"),
        n.leaf("Monitoring"),
        side="right",
    ),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/FL11JiD03Bpd5NicoXyAL9oeX12ePpSPYjMilRBTeloUtOHocncFnoFlFCWYiqoPIlUGZZWv1z8x9ZYVfHk6YXrautV5G_fqM689s8tnuwlshBaWEDGI2SsBywO_DX8yUZ8qTmlRtsE7T6J3br76vZxeUBcM3R-PXiPIqFLzNRbXrf8XKMcVNaphVPbMyaJZvOxt57GYNvTUwIgrSfC_uC5otYmeiox_KGULLhjDTpNbxm-_)



### Decision Tree

```python
from plantuml_compose import mindmap_diagram, render

d = mindmap_diagram()
n = d.nodes

d.add(n.node("Should I learn Python?",
    n.node("Yes",
        n.leaf("Many job opportunities"),
        n.leaf("Easy to learn"),
        n.leaf("Versatile language"),
        side="right",
        color="#C8E6C9",
    ),
    n.node("Consider",
        n.leaf("Time investment"),
        n.leaf("Your goals"),
        side="left",
        color="#FFF9C4",
    ),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/BOv12u9044Rl-oi6l2NU8lAKi2Xq288Y4F4muQ0RwupiZe7_Fj6Et_lWyOge67Hqt8qucGCy1fbz1rVmX87XlkWWV35fsYJsN9vita9DSTqft90N-CWRP9eawCnEtVygCIwWiaisyg8GKPqdyCZzZ3sPB6kIggfoUsp12aVNKLXX1ayt4ZZ-KjIHM3TMonoW5_JH5BJ6xi4_)



### Study Notes

```python
from plantuml_compose import mindmap_diagram, render

d = mindmap_diagram(diagram_style={
    "root_node": {"background": "#1976D2", "font_color": "white"},
    "node": {"background": "#E3F2FD"},
})
n = d.nodes

d.add(n.node("Python Basics",
    n.node("Data Types",
        n.leaf("int, float"),
        n.leaf("str"),
        n.leaf("list, tuple"),
        n.leaf("dict, set"),
    ),
    n.node("Control Flow",
        n.leaf("if/elif/else"),
        n.leaf("for loops"),
        n.leaf("while loops"),
    ),
    n.node("Functions",
        n.leaf("def keyword"),
        n.leaf("Parameters"),
        n.leaf("Return values"),
    ),
))

print(render(d))
```
![Diagram](https://www.plantuml.com/plantuml/svg/VP3TQiCm38NlynI2tOL1MGiRWpBAclbobB4NCB7IcYfMiEM6CFhkK-soortuvzCvI0VjajWeemzkj5EpJR8GlZLtxhmzHZl2JmCGs67v0BpR_doCd8FRCt64Xu-DMPjEjQkUo2oV_vYVNb-UktNH30UfrVda1Kk3QxDTtLEqS5Zan45x9D-dfcsXisBXUvdmHYtu88ym45ifc2IMbtpIkkI9iB3plNB2cmlsEZGoWI6UQvDXXLIkLEs31YBcgSxGQ8H_32Q7NZo7AZeSu8pBpD4LFbZT5mh6Ad-Xv1ZWOYbhuXtgLkjcVm40)



### Org Chart

```python
from plantuml_compose import mindmap_diagram, render

d = mindmap_diagram(direction="top_to_bottom")
n = d.nodes

d.add(n.node("CEO",
    n.node("CTO",
        n.leaf("Engineering"),
        n.leaf("QA"),
    ),
    n.node("CFO",
        n.leaf("Accounting"),
        n.leaf("Finance"),
    ),
    n.node("COO",
        n.leaf("Operations"),
        n.leaf("HR"),
    ),
    color="#FFD54F",
))

print(render(d))
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
| `mainframe="..."` | Add titled border |
| `diagram_style={...}` | Apply styling |

### Node Methods

| Method | Description |
|--------|-------------|
| `n.node(text, *children)` | Create a branch node with children |
| `n.leaf(text)` | Create a leaf node (no children) |
| `d.add(root_node)` | Register the root node tree |

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
| `depths` | Dict of `{depth_int: style}` for depth-based styling |

### Node/Arrow Style Keys

| Key | Description |
|-----|-------------|
| `background` | Fill color |
| `font_color` | Text color |
| `line_color` | Border/line color |
| `line_thickness` | Border/line width |

### Hyperlinks

Add clickable links to nodes using the top-level `link()` utility:

```python
from plantuml_compose import mindmap_diagram, render, link

d = mindmap_diagram()
n = d.nodes

d.add(n.node("Project",
    n.leaf("Docs " + link("https://docs.example.com")),
    n.leaf("Repo " + link("https://github.com/example")),
))

print(render(d))
```
