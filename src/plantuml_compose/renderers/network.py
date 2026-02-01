"""Network diagram (nwdiag) renderer.

Pure functions that transform network diagram primitives to PlantUML text.
"""

from __future__ import annotations

from ..primitives.network import (
    Network,
    NetworkDiagram,
    NetworkElement,
    NetworkGroup,
    NetworkNode,
    PeerLink,
    StandaloneNode,
)
from ..primitives.common import NetworkDiagramStyle
from .common import (
    render_caption,
    render_color,
    render_diagram_style,
    render_footer,
    render_header,
    render_legend,
    render_scale,
    render_theme,
)


def render_network_diagram(diagram: NetworkDiagram) -> str:
    """Render a complete network diagram to PlantUML text."""
    lines: list[str] = ["@startuml"]

    # Theme comes first
    theme_line = render_theme(diagram.theme)
    if theme_line:
        lines.append(theme_line)

    # Diagram style (CSS block)
    if diagram.diagram_style:
        style_block = _render_network_diagram_style(diagram.diagram_style)
        if style_block:
            lines.append(style_block)

    # Scale
    if diagram.scale:
        scale_str = render_scale(diagram.scale)
        if scale_str:
            lines.append(scale_str)

    # Title
    if diagram.title:
        lines.append(f"title {diagram.title}")

    # Header and footer
    if diagram.header:
        lines.extend(render_header(diagram.header))
    if diagram.footer:
        lines.extend(render_footer(diagram.footer))

    # Caption
    if diagram.caption:
        lines.append(render_caption(diagram.caption))

    # Legend
    if diagram.legend:
        lines.extend(render_legend(diagram.legend))

    # nwdiag block
    lines.append("nwdiag {")

    for elem in diagram.elements:
        lines.extend(_render_element(elem))

    lines.append("}")
    lines.append("@enduml")
    return "\n".join(lines)


def _render_network_diagram_style(style: NetworkDiagramStyle) -> str:
    """Render a network diagram style to a PlantUML <style> block."""
    lines = render_diagram_style(
        diagram_type="nwdiagDiagram",
        root_background=style.background,
        root_font_name=style.font_name,
        root_font_size=style.font_size,
        root_font_color=style.font_color,
        element_styles=[
            ("network", style.network),
            ("server", style.server),
            ("group", style.group),
        ],
        arrow_style=style.arrow,
        title_style=None,
    )
    return "\n".join(lines) if lines else ""


def _render_element(elem: NetworkElement) -> list[str]:
    """Render a single diagram element."""
    if isinstance(elem, Network):
        return _render_network(elem)
    if isinstance(elem, NetworkGroup):
        return _render_group(elem)
    if isinstance(elem, PeerLink):
        return [f"  {elem.source} -- {elem.target};"]
    if isinstance(elem, StandaloneNode):
        return [f"  {_render_standalone_node(elem)}"]
    raise TypeError(f"Unknown element type: {type(elem).__name__}")


def _render_network(network: Network) -> list[str]:
    """Render a network with its nodes."""
    lines: list[str] = []

    # Network declaration (color goes inside block, not on declaration)
    lines.append(f"  network {network.name} {{")

    # Color (inside block with quotes)
    if network.color:
        lines.append(f'    color = "{render_color(network.color)}";')

    # Network address
    if network.address:
        lines.append(f'    address = "{network.address}";')

    # Description
    if network.description:
        lines.append(f'    description = "{network.description}";')

    # Width
    if network.width:
        lines.append(f'    width = "{network.width}";')

    # Nodes
    for node in network.nodes:
        lines.append(f"    {_render_network_node(node)}")

    lines.append("  }")
    return lines


def _render_network_node(node: NetworkNode) -> str:
    """Render a node within a network."""
    parts: list[str] = []

    if node.address:
        parts.append(f'address = "{node.address}"')
    if node.shape:
        parts.append(f"shape = {node.shape}")
    if node.description:
        parts.append(f'description = "{node.description}"')
    if node.color:
        parts.append(f'color = "{render_color(node.color)}"')

    if parts:
        return f"{node.name} [{', '.join(parts)}];"
    return f"{node.name};"


def _render_standalone_node(node: StandaloneNode) -> str:
    """Render a standalone node (outside any network)."""
    parts: list[str] = []

    if node.shape:
        parts.append(f"shape = {node.shape}")
    if node.description:
        parts.append(f'description = "{node.description}"')
    if node.color:
        parts.append(f'color = "{render_color(node.color)}"')

    if parts:
        return f"{node.name} [{', '.join(parts)}];"
    return f"{node.name};"


def _render_group(group: NetworkGroup) -> list[str]:
    """Render a group of nodes."""
    lines: list[str] = ["  group {"]

    if group.color:
        lines.append(f'    color = "{render_color(group.color)}";')
    if group.description:
        lines.append(f'    description = "{group.description}";')

    for node_name in group.nodes:
        lines.append(f"    {node_name};")

    lines.append("  }")
    return lines
