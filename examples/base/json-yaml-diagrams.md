# JSON and YAML Diagrams

JSON and YAML diagrams render structured data as visual tree/table layouts. They're useful for:

- **Configuration visualization**: Display config files, API responses, or data schemas as diagrams
- **Documentation**: Embed structured data in architecture docs with syntax highlighting
- **Data exploration**: Highlight specific paths to draw attention to key values
- **Quick diagrams**: The simplest diagram type -- just pass a data string and render

These are the simplest composers in the library. There are no elements, no connections, and no namespaces -- just a data string and optional metadata.

## Core Concepts

**Data string**: The raw JSON or YAML text to visualize. Passed directly as the first argument.

**Highlights**: Paths into the data structure to visually emphasize. Each path is a tuple of keys.

**When to use JSON vs YAML**: Both render identically -- choose based on your source data format. If you already have JSON, use `json_diagram()`. If you have YAML config, use `yaml_diagram()`.

## Your First JSON Diagram

```python
from plantuml_compose import json_diagram, render

d = json_diagram('''{
  "name": "Alice",
  "age": 30,
  "active": true
}''')

print(render(d))
```

This renders the JSON structure as a visual tree with keys and values displayed in a table-like layout.

## Your First YAML Diagram

```python
from plantuml_compose import yaml_diagram, render

d = yaml_diagram('''
name: Alice
age: 30
active: true
''')

print(render(d))
```

The output is visually the same as the JSON version -- PlantUML renders both formats identically.

## Nested Data

Both composers handle arbitrarily nested structures.

### Nested JSON

```python
from plantuml_compose import json_diagram, render

d = json_diagram('''{
  "server": {
    "hostname": "web01",
    "ip": "10.0.1.5",
    "ports": [80, 443, 8080],
    "tls": {
      "enabled": true,
      "cert_path": "/etc/ssl/server.pem"
    }
  }
}''')

print(render(d))
```

### Nested YAML

```python
from plantuml_compose import yaml_diagram, render

d = yaml_diagram('''
server:
  hostname: web01
  ip: 10.0.1.5
  ports:
    - 80
    - 443
    - 8080
  tls:
    enabled: true
    cert_path: /etc/ssl/server.pem
''')

print(render(d))
```

## Highlighting Paths

Highlights draw attention to specific keys in the data. Each highlight is a tuple of strings representing the path from root to the target key.

### Single Highlight

```python
from plantuml_compose import json_diagram, render

d = json_diagram('''{
  "name": "Alice",
  "role": "admin",
  "department": "Engineering"
}''', highlights=[
    ("role",),
])

print(render(d))
```

This highlights the `"role"` key and its value.

### Multiple Highlights

```python
from plantuml_compose import json_diagram, render

d = json_diagram('''{
  "database": {
    "host": "db.internal",
    "port": 5432,
    "name": "app_prod",
    "credentials": {
      "user": "app_svc",
      "password": "********"
    }
  }
}''', highlights=[
    ("database", "host"),
    ("database", "credentials", "password"),
])

print(render(d))
```

Each tuple traces the key path from root. Here, `("database", "host")` highlights the `host` field inside `database`, and `("database", "credentials", "password")` highlights the nested `password` field.

### YAML Highlights

Highlights work identically with YAML diagrams.

```python
from plantuml_compose import yaml_diagram, render

d = yaml_diagram('''
app:
  name: my-service
  version: 2.1.0
  replicas: 3
  image: registry.internal/my-service:2.1.0
''', highlights=[
    ("app", "version"),
    ("app", "replicas"),
])

print(render(d))
```

## Title and Mainframe

### Title

Add a title above the diagram.

```python
from plantuml_compose import json_diagram, render

d = json_diagram('''{
  "cluster": "prod-us-east",
  "nodes": 5,
  "status": "healthy"
}''', title="Cluster Status")

print(render(d))
```

### Mainframe

Wrap the diagram in a labeled frame.

```python
from plantuml_compose import yaml_diagram, render

d = yaml_diagram('''
service: nginx
port: 443
upstream:
  - web01:8080
  - web02:8080
''', mainframe="Load Balancer Config")

print(render(d))
```

### Title and Mainframe Together

```python
from plantuml_compose import json_diagram, render

d = json_diagram('''{
  "pipeline": "deploy-prod",
  "stages": ["build", "test", "deploy"],
  "trigger": "merge to main"
}''', title="CI Pipeline", mainframe="Deployment")

print(render(d))
```

## Styling with diagram_style

Both JSON and YAML diagrams support the same styling options via `diagram_style=`.

### Background and Fonts

```python
from plantuml_compose import json_diagram, render

d = json_diagram('''{
  "env": "production",
  "debug": false,
  "log_level": "INFO"
}''', diagram_style={
    "background": "#FAFAFA",
    "font_name": "Arial",
    "font_size": 14,
})

print(render(d))
```

### Node Styling

Style the data nodes (keys and values).

```python
from plantuml_compose import json_diagram, render

d = json_diagram('''{
  "name": "web-proxy",
  "port": 8080,
  "workers": 4
}''', diagram_style={
    "node": {
        "background": "#E3F2FD",
        "font_color": "#1565C0",
    },
})

print(render(d))
```

### Highlight Styling

When using highlights, you can control how the highlighted nodes look.

```python
from plantuml_compose import json_diagram, render

d = json_diagram('''{
  "host": "db.internal",
  "port": 5432,
  "ssl": true,
  "pool_size": 20
}''',
    highlights=[("ssl",), ("pool_size",)],
    diagram_style={
        "highlight": {
            "background": "#FFF9C4",
        },
    },
)

print(render(d))
```

### Combined Styling

```python
from plantuml_compose import yaml_diagram, render

d = yaml_diagram('''
cluster:
  name: prod-east
  region: us-east-1
  nodes:
    - id: node-01
      role: control-plane
    - id: node-02
      role: worker
    - id: node-03
      role: worker
''',
    title="Cluster Inventory",
    highlights=[("cluster", "name")],
    diagram_style={
        "background": "#ECEFF1",
        "font_name": "Monospace",
        "node": {
            "background": "#FAFAFA",
        },
        "highlight": {
            "background": "#C8E6C9",
            "font_color": "#1B5E20",
        },
    },
)

print(render(d))
```

## Complete Examples

### API Response

```python
from plantuml_compose import json_diagram, render

d = json_diagram('''{
  "status": 200,
  "data": {
    "users": [
      {"id": 1, "name": "Alice", "role": "admin"},
      {"id": 2, "name": "Bob", "role": "user"},
      {"id": 3, "name": "Carol", "role": "user"}
    ],
    "total": 3,
    "page": 1
  }
}''',
    title="GET /api/users",
    highlights=[("data", "total")],
)

print(render(d))
```

### Kubernetes Deployment

```python
from plantuml_compose import yaml_diagram, render

d = yaml_diagram('''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-frontend
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-frontend
  template:
    spec:
      containers:
        - name: nginx
          image: nginx:1.27
          ports:
            - containerPort: 80
''',
    title="web-frontend Deployment",
    highlights=[
        ("spec", "replicas"),
    ],
    diagram_style={
        "node": {"background": "#E8F5E9"},
        "highlight": {"background": "#FFF9C4"},
    },
)

print(render(d))
```

### Ansible Inventory

```python
from plantuml_compose import yaml_diagram, render

d = yaml_diagram('''
all:
  children:
    webservers:
      hosts:
        web01:
          ansible_host: 10.0.1.10
        web02:
          ansible_host: 10.0.1.11
    databases:
      hosts:
        db01:
          ansible_host: 10.0.2.10
          pg_role: primary
        db02:
          ansible_host: 10.0.2.11
          pg_role: replica
''',
    title="Ansible Inventory",
    mainframe="Infrastructure",
)

print(render(d))
```

## Embedding in Other Diagrams

JSON and YAML diagrams can be embedded as subdiagrams inside other diagram types. See [subdiagrams.md](subdiagrams.md) for details on embedding.

## Quick Reference

### Diagram Creation

| Code | Description |
|------|-------------|
| `json_diagram(data)` | Create a JSON diagram from a JSON string |
| `yaml_diagram(data)` | Create a YAML diagram from a YAML string |
| `title="..."` | Diagram title |
| `mainframe="..."` | Frame label around the diagram |
| `highlights=[...]` | Paths to highlight (list of string tuples) |
| `diagram_style={...}` | Apply styling |

### Highlight Paths

Each highlight is a tuple of strings tracing the path from the root to the target key.

| Highlight | Targets |
|-----------|---------|
| `("key",)` | Top-level key |
| `("parent", "child")` | Nested key |
| `("a", "b", "c")` | Deeply nested key |

### Diagram Style Keys

| Key | Description |
|-----|-------------|
| `background` | Diagram background color |
| `font_name` | Default font family |
| `font_size` | Default font size |
| `font_color` | Default text color |
| `node` | Style for data nodes (dict) |
| `highlight` | Style for highlighted nodes (dict) |

### Node / Highlight Style Keys

| Key | Description |
|-----|-------------|
| `background` | Fill color |
| `font_color` | Text color |
| `line_color` | Border color |
| `line_thickness` | Border width |
