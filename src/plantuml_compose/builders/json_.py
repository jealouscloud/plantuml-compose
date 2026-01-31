"""JSON and YAML diagram builders.

Provides context-manager based builders for JSON and YAML data visualization.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import yaml

from ..primitives.common import (
    JsonDiagramStyle,
    JsonDiagramStyleLike,
    YamlDiagramStyle,
    YamlDiagramStyleLike,
    coerce_json_diagram_style,
    coerce_yaml_diagram_style,
)
from ..primitives.json_ import JsonDiagram, YamlDiagram
from ..renderers import render as render_diagram

# Type alias for data that can be passed to json_diagram/yaml_diagram
JsonData = str | dict[str, Any] | list[Any]
YamlData = str | dict[str, Any] | list[Any]


class JsonDiagramBuilder:
    """Builder for JSON data visualization diagrams."""

    def __init__(
        self,
        data: JsonData,
        title: str | None,
        diagram_style: JsonDiagramStyleLike | None,
    ) -> None:
        if isinstance(data, str):
            self._data = data
        else:
            self._data = json.dumps(data, indent=2)
        self._title = title
        self._diagram_style = (
            coerce_json_diagram_style(diagram_style) if diagram_style else None
        )
        self._highlights: list[tuple[str, ...]] = []

    def highlight(self, *path: str) -> None:
        """Highlight a path in the JSON data.

        Args:
            *path: Keys forming the path to highlight

        Example:
            d.highlight("name")              # Top-level key
            d.highlight("user", "email")     # Nested: user.email
            d.highlight("items", "0")        # Array index

        Raises:
            ValueError: If path is empty
        """
        if not path:
            raise ValueError("Highlight path cannot be empty")
        self._highlights.append(path)

    def build(self) -> JsonDiagram:
        """Build the JSON diagram primitive."""
        return JsonDiagram(
            data=self._data,
            title=self._title,
            highlights=tuple(self._highlights),
            diagram_style=self._diagram_style,
        )

    def render(self) -> str:
        """Build and render the diagram to PlantUML text."""
        return render_diagram(self.build())


class YamlDiagramBuilder:
    """Builder for YAML data visualization diagrams."""

    def __init__(
        self,
        data: YamlData,
        title: str | None,
        diagram_style: YamlDiagramStyleLike | None,
    ) -> None:
        if isinstance(data, str):
            self._data = data
        else:
            self._data = yaml.dump(data, default_flow_style=False, sort_keys=False)
        self._title = title
        self._diagram_style = (
            coerce_yaml_diagram_style(diagram_style) if diagram_style else None
        )
        self._highlights: list[tuple[str, ...]] = []

    def highlight(self, *path: str) -> None:
        """Highlight a path in the YAML data.

        Args:
            *path: Keys forming the path to highlight

        Example:
            d.highlight("name")              # Top-level key
            d.highlight("server", "port")    # Nested: server.port
            d.highlight("items", "0")        # Array index

        Raises:
            ValueError: If path is empty
        """
        if not path:
            raise ValueError("Highlight path cannot be empty")
        self._highlights.append(path)

    def build(self) -> YamlDiagram:
        """Build the YAML diagram primitive."""
        return YamlDiagram(
            data=self._data,
            title=self._title,
            highlights=tuple(self._highlights),
            diagram_style=self._diagram_style,
        )

    def render(self) -> str:
        """Build and render the diagram to PlantUML text."""
        return render_diagram(self.build())


@contextmanager
def json_diagram(
    data: JsonData,
    *,
    title: str | None = None,
    diagram_style: JsonDiagramStyleLike | None = None,
) -> Iterator[JsonDiagramBuilder]:
    """Create a JSON data visualization diagram.

    Args:
        data: JSON data as string, dict, or list
        title: Diagram title
        diagram_style: CSS-style diagram styling

    Yields:
        JsonDiagramBuilder for adding highlights

    Example:
        with json_diagram({"name": "John", "age": 30}) as d:
            d.highlight("name")
        print(render(d.build()))

        # With styling
        with json_diagram(
            data,
            title="User Data",
            diagram_style={"node": {"background": "#E3F2FD"}}
        ) as d:
            d.highlight("email")
    """
    builder = JsonDiagramBuilder(data, title, diagram_style)
    yield builder


@contextmanager
def yaml_diagram(
    data: YamlData,
    *,
    title: str | None = None,
    diagram_style: YamlDiagramStyleLike | None = None,
) -> Iterator[YamlDiagramBuilder]:
    """Create a YAML data visualization diagram.

    Args:
        data: YAML data as string, dict, or list
        title: Diagram title
        diagram_style: CSS-style diagram styling

    Yields:
        YamlDiagramBuilder for adding highlights

    Example:
        with yaml_diagram("server:\\n  port: 8080") as d:
            d.highlight("server", "port")
        print(render(d.build()))

        # From dict
        with yaml_diagram({"server": {"port": 8080}}) as d:
            d.highlight("server", "port")
    """
    builder = YamlDiagramBuilder(data, title, diagram_style)
    yield builder
