"""JSON and YAML diagram primitives.

Frozen dataclasses representing JSON and YAML data visualization diagrams.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .common import JsonDiagramStyle, YamlDiagramStyle


@dataclass(frozen=True)
class JsonDiagram:
    """A JSON data visualization diagram.

    Renders structured JSON data as a visual tree/table.

        data:          JSON string to visualize
        title:         Diagram title
        highlights:    Paths to highlight (each path is a tuple of keys)
        diagram_style: CSS-style diagram styling
    """

    data: str
    title: str | None = None
    highlights: tuple[tuple[str, ...], ...] = field(default_factory=tuple)
    diagram_style: JsonDiagramStyle | None = None


@dataclass(frozen=True)
class YamlDiagram:
    """A YAML data visualization diagram.

    Renders structured YAML data as a visual tree/table.

        data:          YAML string to visualize
        title:         Diagram title
        highlights:    Paths to highlight (each path is a tuple of keys)
        diagram_style: CSS-style diagram styling
    """

    data: str
    title: str | None = None
    highlights: tuple[tuple[str, ...], ...] = field(default_factory=tuple)
    diagram_style: YamlDiagramStyle | None = None
