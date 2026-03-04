"""Salt wireframe builder.

Provides a context-manager based builder for Salt UI wireframe diagrams.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from .base import EmbeddableDiagramMixin
from ..primitives.salt import (
    Button,
    Checkbox,
    Dropdown,
    Grid,
    GridStyle,
    GroupBox,
    Menu,
    Radio,
    Row,
    SaltDiagram,
    SaltWidget,
    Scrollbar,
    ScrollbarStyle,
    Separator,
    SeparatorStyle,
    TabBar,
    Text,
    TextField,
    Tree,
)
from ..renderers import render as render_diagram


class SaltDiagramBuilder(EmbeddableDiagramMixin):
    """Builder for Salt wireframe diagrams.

    Salt wireframes are UI mockup diagrams for sketching user interfaces.
    Use widget methods to add UI elements, and grid/container methods
    to organize layout.
    """

    _keep_diagram_markers = True

    def __init__(
        self,
        *,
        title: str | None = None,
        mainframe: str | None = None,
    ) -> None:
        self._title = title
        self._mainframe = mainframe
        self._content: list[SaltWidget] = []

    # -- Simple widgets --

    def text(self, text: str) -> Text:
        """Add a plain text label."""
        widget = Text(text=text)
        self._content.append(widget)
        return widget

    def button(self, label: str) -> Button:
        """Add a button widget. Rendered as [label]."""
        widget = Button(label=label)
        self._content.append(widget)
        return widget

    def checkbox(self, label: str, *, checked: bool = False) -> Checkbox:
        """Add a checkbox widget. Rendered as [X] or [ ] with label."""
        widget = Checkbox(label=label, checked=checked)
        self._content.append(widget)
        return widget

    def radio(self, label: str, *, selected: bool = False) -> Radio:
        """Add a radio button widget. Rendered as (X) or ( ) with label."""
        widget = Radio(label=label, selected=selected)
        self._content.append(widget)
        return widget

    def text_field(self, value: str = "", *, width: int = 10) -> TextField:
        """Add a text input field. Width controls visual size in characters."""
        widget = TextField(value=value, width=width)
        self._content.append(widget)
        return widget

    def dropdown(self, *items: str) -> Dropdown:
        """Add a dropdown/combobox. First item is displayed as selected.

        Example:
            d.dropdown("Option 1", "Option 2", "Option 3")
        """
        if not items:
            raise ValueError("Dropdown requires at least one item")
        widget = Dropdown(items=items)
        self._content.append(widget)
        return widget

    def separator(self, style: SeparatorStyle = "..") -> Separator:
        """Add a horizontal separator line.

        Styles: ".." (dotted), "==" (double), "~~" (wave), "--" (dashed)
        """
        widget = Separator(style=style)
        self._content.append(widget)
        return widget

    # -- Row --

    def row(self, *cells: SaltWidget) -> Row:
        """Add a row of pipe-separated cells.

        Cells should be simple widgets (Text, Button, etc.). For grid
        layout with borders, use the grid() context manager instead.

        Example:
            d.row(Text("Name"), TextField("John", width=15))
        """
        widget = Row(cells=cells)
        self._content.append(widget)
        return widget

    # -- Container context managers --

    @contextmanager
    def grid(self, style: GridStyle = "#") -> Iterator[_GridBuilder]:
        """Create a grid layout with configurable borders.

        Border styles:
            "#" — All lines (complete grid)
            "!" — Vertical lines only
            "-" — Horizontal lines only
            "+" — External lines only (outer border)

        Example:
            with d.grid("#") as g:
                g.row(Text("Name"), TextField("John"))
                g.row(Text("Age"), TextField("30"))
        """
        builder = _GridBuilder(style)
        yield builder
        self._content.append(builder._build())

    @contextmanager
    def group_box(self, title: str) -> Iterator[_ContainerBuilder]:
        """Create a titled group box container.

        Containers cannot be nested via the builder API. To nest a grid
        inside a group box, construct the Grid primitive directly and pass
        it via the container builder's row() method.

        Example:
            with d.group_box("Login") as g:
                g.text_field("username")
                g.button("Submit")
        """
        builder = _ContainerBuilder()
        yield builder
        widget = GroupBox(title=title, content=tuple(builder._widgets))
        self._content.append(widget)

    @contextmanager
    def scrollbar(
        self, style: ScrollbarStyle = "S"
    ) -> Iterator[_ContainerBuilder]:
        """Create a scrollbar container.

        Styles: "S" (both), "SI" (vertical only), "S-" (horizontal only)

        Containers cannot be nested via the builder API. To nest containers,
        construct the inner container primitive directly.

        Example:
            with d.scrollbar("SI") as s:
                s.text("Scrollable content")
        """
        builder = _ContainerBuilder()
        yield builder
        widget = Scrollbar(style=style, content=tuple(builder._widgets))
        self._content.append(widget)

    # -- Declarative containers --

    def tree(self, *nodes: tuple[int, str]) -> Tree:
        """Add a tree widget showing hierarchical data.

        Each node is a (depth, label) tuple. Depth starts at 1 for root.

        Example:
            d.tree(
                (1, "Root"),
                (2, "Child 1"),
                (3, "Grandchild"),
                (2, "Child 2"),
            )
        """
        if not nodes:
            raise ValueError("Tree requires at least one node")
        widget = Tree(nodes=nodes)
        self._content.append(widget)
        return widget

    def tab_bar(
        self,
        *tabs: str,
        content: tuple[SaltWidget, ...] = (),
    ) -> TabBar:
        """Add a tab bar with optional active tab content.

        Example:
            d.tab_bar("General", "Advanced", "About")

            # With content for active tab
            d.tab_bar("Tab1", "Tab2", content=(Text("Tab 1 content"),))
        """
        if not tabs:
            raise ValueError("Tab bar requires at least one tab")
        widget = TabBar(tabs=tabs, active_content=content)
        self._content.append(widget)
        return widget

    def menu(
        self,
        *items: str,
        sub_items: tuple[tuple[str, str], ...] = (),
    ) -> Menu:
        """Add a menu bar with optional nested sub-items.

        Example:
            d.menu("File", "Edit", "View")

            # With sub-menus
            d.menu(
                "File", "Edit",
                sub_items=(("File", "New"), ("File", "Open")),
            )
        """
        if not items:
            raise ValueError("Menu requires at least one item")
        widget = Menu(items=items, sub_items=sub_items)
        self._content.append(widget)
        return widget

    # -- Build/render --

    def build(self) -> SaltDiagram:
        """Build the Salt wireframe primitive."""
        return SaltDiagram(
            content=tuple(self._content),
            title=self._title,
            mainframe=self._mainframe,
        )

    def render(self) -> str:
        """Build and render the diagram to PlantUML text."""
        return render_diagram(self.build())


class _GridBuilder:
    """Builder for grid rows within a grid() context manager."""

    def __init__(self, style: GridStyle) -> None:
        self._style = style
        self._rows: list[SaltWidget] = []

    def row(self, *cells: SaltWidget) -> Row:
        """Add a row of pipe-separated cells to the grid."""
        widget = Row(cells=cells)
        self._rows.append(widget)
        return widget

    def separator(self, style: SeparatorStyle = "..") -> Separator:
        """Add a separator line within the grid."""
        widget = Separator(style=style)
        self._rows.append(widget)
        return widget

    def _build(self) -> Grid:
        return Grid(style=self._style, rows=tuple(self._rows))


class _ContainerBuilder:
    """Builder for widgets within container context managers (group_box, scrollbar)."""

    def __init__(self) -> None:
        self._widgets: list[SaltWidget] = []

    def text(self, text: str) -> Text:
        """Add a plain text label."""
        widget = Text(text=text)
        self._widgets.append(widget)
        return widget

    def button(self, label: str) -> Button:
        """Add a button widget."""
        widget = Button(label=label)
        self._widgets.append(widget)
        return widget

    def checkbox(self, label: str, *, checked: bool = False) -> Checkbox:
        """Add a checkbox widget."""
        widget = Checkbox(label=label, checked=checked)
        self._widgets.append(widget)
        return widget

    def radio(self, label: str, *, selected: bool = False) -> Radio:
        """Add a radio button widget."""
        widget = Radio(label=label, selected=selected)
        self._widgets.append(widget)
        return widget

    def text_field(self, value: str = "", *, width: int = 10) -> TextField:
        """Add a text input field."""
        widget = TextField(value=value, width=width)
        self._widgets.append(widget)
        return widget

    def dropdown(self, *items: str) -> Dropdown:
        """Add a dropdown widget."""
        if not items:
            raise ValueError("Dropdown requires at least one item")
        widget = Dropdown(items=items)
        self._widgets.append(widget)
        return widget

    def separator(self, style: SeparatorStyle = "..") -> Separator:
        """Add a separator line."""
        widget = Separator(style=style)
        self._widgets.append(widget)
        return widget

    def row(self, *cells: SaltWidget) -> Row:
        """Add a row of pipe-separated cells."""
        widget = Row(cells=cells)
        self._widgets.append(widget)
        return widget


@contextmanager
def salt_diagram(
    *,
    title: str | None = None,
    mainframe: str | None = None,
) -> Iterator[SaltDiagramBuilder]:
    """Create a Salt wireframe diagram.

    Salt wireframes are UI mockup diagrams for sketching user interfaces.
    Use the builder methods to add widgets and layout containers.

    Example:
        with salt_diagram(title="Login Form") as d:
            with d.grid() as g:
                g.row(Text("Username"), TextField(width=20))
                g.row(Text("Password"), TextField(width=20))
            d.button("Login")
        print(d.render())
    """
    builder = SaltDiagramBuilder(title=title, mainframe=mainframe)
    yield builder
