"""JSON and YAML data diagram composers.

These are the simplest composers — just pass a data string and optional metadata.
No element namespaces or connections needed.

Example:
    from plantuml_compose import json_diagram, yaml_diagram, render

    d = json_diagram('''{
      "name": "Alice",
      "age": 30
    }''', title="User Data")

    print(render(d))
"""

from __future__ import annotations

from plantuml_compose.primitives.json_ import JsonDiagram, YamlDiagram
from plantuml_compose.primitives.styles import (
    JsonDiagramStyleLike,
    YamlDiagramStyleLike,
    coerce_json_diagram_style,
    coerce_yaml_diagram_style,
)


class JsonComposer:
    """Composer for JSON data visualization diagrams.

    Thin wrapper — stores the data and params, build() creates the primitive.
    """

    def __init__(
        self,
        data: str,
        *,
        title: str | None = None,
        mainframe: str | None = None,
        highlights: list[tuple[str, ...]] | None = None,
        diagram_style: JsonDiagramStyleLike | None = None,
    ) -> None:
        self._data = data
        self._title = title
        self._mainframe = mainframe
        self._highlights = tuple(highlights) if highlights else ()
        self._diagram_style = (
            coerce_json_diagram_style(diagram_style)
            if diagram_style is not None
            else None
        )

    def build(self) -> JsonDiagram:
        return JsonDiagram(
            data=self._data,
            title=self._title,
            mainframe=self._mainframe,
            highlights=self._highlights,
            diagram_style=self._diagram_style,
        )

    def render(self) -> str:
        """Build and render to PlantUML text."""
        from ..renderers import render as render_fn

        return render_fn(self.build())


class YamlComposer:
    """Composer for YAML data visualization diagrams.

    Thin wrapper — stores the data and params, build() creates the primitive.
    """

    def __init__(
        self,
        data: str,
        *,
        title: str | None = None,
        mainframe: str | None = None,
        highlights: list[tuple[str, ...]] | None = None,
        diagram_style: YamlDiagramStyleLike | None = None,
    ) -> None:
        self._data = data
        self._title = title
        self._mainframe = mainframe
        self._highlights = tuple(highlights) if highlights else ()
        self._diagram_style = (
            coerce_yaml_diagram_style(diagram_style)
            if diagram_style is not None
            else None
        )

    def build(self) -> YamlDiagram:
        return YamlDiagram(
            data=self._data,
            title=self._title,
            mainframe=self._mainframe,
            highlights=self._highlights,
            diagram_style=self._diagram_style,
        )

    def render(self) -> str:
        """Build and render to PlantUML text."""
        from ..renderers import render as render_fn

        return render_fn(self.build())


def json_diagram(
    data: str,
    *,
    title: str | None = None,
    mainframe: str | None = None,
    highlights: list[tuple[str, ...]] | None = None,
    diagram_style: JsonDiagramStyleLike | None = None,
) -> JsonComposer:
    """Create a JSON data visualization diagram composer.

    Example:
        d = json_diagram('''{
          "name": "Alice",
          "age": 30
        }''', title="User")
        print(render(d))
    """
    return JsonComposer(
        data,
        title=title,
        mainframe=mainframe,
        highlights=highlights,
        diagram_style=diagram_style,
    )


def yaml_diagram(
    data: str,
    *,
    title: str | None = None,
    mainframe: str | None = None,
    highlights: list[tuple[str, ...]] | None = None,
    diagram_style: YamlDiagramStyleLike | None = None,
) -> YamlComposer:
    """Create a YAML data visualization diagram composer.

    Example:
        d = yaml_diagram('''
        name: Alice
        age: 30
        ''', title="User")
        print(render(d))
    """
    return YamlComposer(
        data,
        title=title,
        mainframe=mainframe,
        highlights=highlights,
        diagram_style=diagram_style,
    )
