"""JSON and YAML diagram renderers.

Pure functions that transform JSON/YAML diagram primitives to PlantUML text.
"""

from __future__ import annotations

from ..primitives.common import JsonDiagramStyle, YamlDiagramStyle
from ..primitives.json_ import JsonDiagram, YamlDiagram
from .common import render_diagram_style


def render_json_diagram(diagram: JsonDiagram) -> str:
    """Render a complete JSON diagram to PlantUML text."""
    lines: list[str] = ["@startjson"]

    # Style block
    if diagram.diagram_style:
        lines.extend(_render_json_diagram_style(diagram.diagram_style))

    # Title
    if diagram.title:
        lines.append(f"title {diagram.title}")

    # Highlights (must come before data)
    for path in diagram.highlights:
        quoted_parts = [f'"{p}"' for p in path]
        lines.append(f"#highlight {' / '.join(quoted_parts)}")

    # Data (as-is)
    lines.append(diagram.data)

    lines.append("@endjson")
    return "\n".join(lines)


def render_yaml_diagram(diagram: YamlDiagram) -> str:
    """Render a complete YAML diagram to PlantUML text."""
    lines: list[str] = ["@startyaml"]

    # Style block
    if diagram.diagram_style:
        lines.extend(_render_yaml_diagram_style(diagram.diagram_style))

    # Title
    if diagram.title:
        lines.append(f"title {diagram.title}")

    # Highlights (must come before data)
    for path in diagram.highlights:
        quoted_parts = [f'"{p}"' for p in path]
        lines.append(f"#highlight {' / '.join(quoted_parts)}")

    # Data (as-is)
    lines.append(diagram.data)

    lines.append("@endyaml")
    return "\n".join(lines)


def _render_json_diagram_style(style: JsonDiagramStyle) -> list[str]:
    """Render a JsonDiagramStyle to PlantUML <style> block."""
    return render_diagram_style(
        diagram_type="jsonDiagram",
        root_background=style.background,
        root_font_name=style.font_name,
        root_font_size=style.font_size,
        root_font_color=style.font_color,
        element_styles=[
            ("node", style.node),
            ("highlight", style.highlight),
        ],
        arrow_style=None,
        title_style=None,
    )


def _render_yaml_diagram_style(style: YamlDiagramStyle) -> list[str]:
    """Render a YamlDiagramStyle to PlantUML <style> block."""
    return render_diagram_style(
        diagram_type="yamlDiagram",
        root_background=style.background,
        root_font_name=style.font_name,
        root_font_size=style.font_size,
        root_font_color=style.font_color,
        element_styles=[
            ("node", style.node),
            ("highlight", style.highlight),
        ],
        arrow_style=None,
        title_style=None,
    )
