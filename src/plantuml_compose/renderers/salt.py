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
from .common import render_mainframe


def render_salt_diagram(diagram: SaltDiagram) -> str:
    """Render a complete Salt wireframe diagram to PlantUML text."""
    lines: list[str] = ["@startsalt"]

    if diagram.mainframe:
        lines.append(render_mainframe(diagram.mainframe))

    if diagram.title:
        lines.append(f"title {diagram.title}")

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
        return [_render_row(widget, indent)]

    if isinstance(widget, Grid):
        return _render_grid(widget, indent)

    raise TypeError(f"Unknown widget type: {type(widget).__name__}")


def _render_row(row: Row, indent: int) -> str:
    """Render a row as pipe-separated cells on a single line."""
    prefix = "  " * indent
    cells: list[str] = []
    for cell in row.cells:
        cell_lines = _render_widget(cell, indent=0)
        if len(cell_lines) > 1:
            raise TypeError(
                f"Row cells must be single-line widgets, got multi-line "
                f"{type(cell).__name__}"
            )
        cells.append(cell_lines[0] if cell_lines else "")
    return f"{prefix}{' | '.join(cells)}"


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
    lines = [f"{prefix}{{T"]
    for depth, label in tree.nodes:
        plus = "+" * depth
        lines.append(f"{prefix}  {plus} {label}")
    lines.append(f"{prefix}}}")
    return lines


def _render_tab_bar(tab_bar: TabBar, indent: int) -> list[str]:
    """Render a tab bar container."""
    prefix = "  " * indent
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
