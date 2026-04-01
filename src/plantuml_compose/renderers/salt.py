"""Salt wireframe renderer.

Pure functions that transform Salt wireframe primitives to PlantUML text.
"""

from __future__ import annotations

from ..primitives.salt import (
    Button,
    Checkbox,
    Dropdown,
    Grid,
    GroupBox,
    Menu,
    Radio,
    Row,
    Scrollbar,
    SaltDiagram,
    SaltWidget,
    Separator,
    TabBar,
    Text,
    TextField,
    Tree,
)
from .common import (
    render_caption,
    render_footer,
    render_header,
    render_legend,
    render_mainframe,
)


def render_salt_diagram(diagram: SaltDiagram) -> str:
    """Render a complete Salt wireframe diagram to PlantUML text."""
    lines: list[str] = ["@startsalt"]

    if diagram.mainframe:
        lines.append(render_mainframe(diagram.mainframe))

    if diagram.title:
        lines.append(f"title {diagram.title}")

    if diagram.header:
        lines.extend(render_header(diagram.header))
    if diagram.footer:
        lines.extend(render_footer(diagram.footer))

    if diagram.caption:
        lines.append(render_caption(diagram.caption))

    if diagram.legend:
        lines.extend(render_legend(diagram.legend))

    # Salt content is wrapped in { }
    lines.append("{")
    for widget in diagram.content:
        lines.extend(_render_widget(widget, indent=1))
    lines.append("}")

    lines.append("@endsalt")
    return "\n".join(lines)


def _render_widget(widget: SaltWidget, indent: int = 0) -> list[str]:
    """Render a single widget to PlantUML lines."""
    prefix = "  " * indent

    if isinstance(widget, Text):
        return [f"{prefix}{widget.text}"]

    if isinstance(widget, Button):
        return [f"{prefix}[{widget.label}]"]

    if isinstance(widget, Checkbox):
        mark = "X" if widget.checked else " "
        return [f"{prefix}[{mark}] {widget.label}"]

    if isinstance(widget, Radio):
        mark = "X" if widget.selected else " "
        return [f"{prefix}({mark}) {widget.label}"]

    if isinstance(widget, TextField):
        # Trailing spaces set the visual width
        padding = max(0, widget.width - len(widget.value))
        return [f'{prefix}"{widget.value}{" " * padding}"']

    if isinstance(widget, Dropdown):
        if widget.open:
            items = "^^".join(widget.items)
            return [f"{prefix}^^{items}^^"]
        else:
            items = "^".join(widget.items)
            return [f"{prefix}^{items}^"]

    if isinstance(widget, Separator):
        return [f"{prefix}{widget.style}"]

    if isinstance(widget, Tree):
        return _render_tree(widget, indent)

    if isinstance(widget, TabBar):
        return _render_tab_bar(widget, indent)

    if isinstance(widget, Menu):
        return _render_menu(widget, indent)

    if isinstance(widget, Scrollbar):
        return _render_scrollbar(widget, indent)

    if isinstance(widget, GroupBox):
        return _render_group_box(widget, indent)

    if isinstance(widget, Row):
        return _render_row(widget, indent)

    if isinstance(widget, Grid):
        return _render_grid(widget, indent)

    raise TypeError(f"Unknown widget type: {type(widget).__name__}")


def _render_row(row: Row, indent: int) -> list[str]:
    """Render a row as pipe-separated cells.

    When all cells are single-line, renders on one line with | separators.
    When any cell is multi-line (e.g. a nested Grid), each cell's lines
    are emitted between | separators on their own lines.
    """
    prefix = "  " * indent
    rendered_cells = [_render_widget(cell, indent=0) for cell in row.cells]
    all_single = all(len(c) == 1 for c in rendered_cells)

    if all_single:
        return [f"{prefix}{' | '.join(c[0] for c in rendered_cells)}"]

    # Multi-line cells: render each cell, separate with | on its own line
    lines: list[str] = []
    for i, cell_lines in enumerate(rendered_cells):
        for line in cell_lines:
            lines.append(f"{prefix}{line}")
        if i < len(rendered_cells) - 1:
            lines.append(f"{prefix}|")
    return lines


def _render_grid(grid: Grid, indent: int) -> list[str]:
    """Render a grid container."""
    prefix = "  " * indent
    lines = [f"{prefix}{{{grid.style}"]
    for row in grid.rows:
        lines.extend(_render_widget(row, indent=indent + 1))
    lines.append(f"{prefix}}}")
    return lines


def _render_tree(tree: Tree, indent: int) -> list[str]:
    """Render a tree widget."""
    prefix = "  " * indent
    lines = [f"{prefix}{{{tree.style}"]
    for depth, label in tree.nodes:
        plus = "+" * depth
        lines.append(f"{prefix}  {plus} {label}")
    lines.append(f"{prefix}}}")
    return lines


def _render_tab_bar(tab_bar: TabBar, indent: int) -> list[str]:
    """Render a tab bar container.

    Horizontal tabs use pipe separators on one line: {/ Tab1 | Tab2 }
    Vertical tabs place each tab on its own line with | between them.
    """
    prefix = "  " * indent
    if tab_bar.vertical:
        # Vertical: each tab on its own line, separated by |
        lines = [f"{prefix}{{/"]
        for i, tab in enumerate(tab_bar.tabs):
            lines.append(f"{prefix}  {tab}")
            if i < len(tab_bar.tabs) - 1:
                lines.append(f"{prefix}  |")
        for widget in tab_bar.active_content:
            lines.extend(_render_widget(widget, indent=indent + 1))
        lines.append(f"{prefix}}}")
        return lines
    else:
        # Horizontal: all tabs on one line
        tabs_str = " | ".join(tab_bar.tabs)
        if not tab_bar.active_content:
            return [f"{prefix}{{/ {tabs_str}}}"]
        lines = [f"{prefix}{{/ {tabs_str}"]
        for widget in tab_bar.active_content:
            lines.extend(_render_widget(widget, indent=indent + 1))
        lines.append(f"{prefix}}}")
        return lines


def _render_menu(menu: Menu, indent: int) -> list[str]:
    """Render a menu bar."""
    prefix = "  " * indent
    items_str = " | ".join(menu.items)
    if not menu.sub_items:
        return [f"{prefix}{{* {items_str}}}"]
    lines = [f"{prefix}{{* {items_str}"]
    for parent, child in menu.sub_items:
        lines.append(f"{prefix}  {parent} | {child}")
    lines.append(f"{prefix}}}")
    return lines


def _render_scrollbar(scrollbar: Scrollbar, indent: int) -> list[str]:
    """Render a scrollbar container."""
    prefix = "  " * indent
    lines = [f"{prefix}{{{scrollbar.style}"]
    for widget in scrollbar.content:
        lines.extend(_render_widget(widget, indent=indent + 1))
    lines.append(f"{prefix}}}")
    return lines


def _render_group_box(group_box: GroupBox, indent: int) -> list[str]:
    """Render a titled group box container."""
    prefix = "  " * indent
    lines = [f'{prefix}{{^"{group_box.title}"']
    for widget in group_box.content:
        lines.extend(_render_widget(widget, indent=indent + 1))
    lines.append(f"{prefix}}}")
    return lines
