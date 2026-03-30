"""Salt wireframe diagram composer.

One namespace, one API — all widgets come from d.widgets.
No primitive imports needed.

Example:
    d = salt_diagram(title="Server Provisioning")
    w = d.widgets

    d.add(
        w.grid("#",
            w.row(w.text("Name"), w.text_field("value", width=20)),
        ),
        w.button("Submit"),
    )

    puml = render(d)
"""

from __future__ import annotations

from plantuml_compose.primitives.salt import (
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
from .base import BaseComposer


class SaltWidgetNamespace:
    """Factory namespace for salt widgets.

    All widget factories return salt primitives directly — no EntityRef
    wrapping needed since salt widgets don't have refs or connections.
    """

    def text(self, text: str) -> Text:
        return Text(text=text)

    def button(self, label: str) -> Button:
        return Button(label=label)

    def checkbox(self, label: str, *, checked: bool = False) -> Checkbox:
        return Checkbox(label=label, checked=checked)

    def radio(self, label: str, *, selected: bool = False) -> Radio:
        return Radio(label=label, selected=selected)

    def text_field(self, value: str = "", *, width: int = 10) -> TextField:
        return TextField(value=value, width=width)

    def dropdown(self, *items: str) -> Dropdown:
        return Dropdown(items=items)

    def separator(self, style: SeparatorStyle = "..") -> Separator:
        return Separator(style=style)

    def grid(self, style: GridStyle = "#", *children: SaltWidget) -> Grid:
        return Grid(style=style, rows=children)

    def row(self, *cells: SaltWidget) -> Row:
        return Row(cells=cells)

    def menu(
        self,
        *items: str,
        sub_items: tuple[tuple[str, str], ...] = (),
    ) -> Menu:
        return Menu(items=items, sub_items=sub_items)

    def tab_bar(
        self,
        *tabs: str,
        content: tuple[SaltWidget, ...] = (),
    ) -> TabBar:
        return TabBar(tabs=tabs, active_content=content)

    def group_box(self, title: str, *children: SaltWidget) -> GroupBox:
        return GroupBox(title=title, content=children)

    def scrollbar(
        self, style: ScrollbarStyle = "S", *children: SaltWidget,
    ) -> Scrollbar:
        return Scrollbar(style=style, content=children)

    def tree(self, *nodes: tuple[int, str]) -> Tree:
        return Tree(nodes=nodes)


class SaltComposer(BaseComposer):
    """Composer for salt wireframe diagrams."""

    def __init__(
        self,
        *,
        title: str | None = None,
        mainframe: str | None = None,
    ) -> None:
        super().__init__(title=title, mainframe=mainframe)
        self._widgets_ns = SaltWidgetNamespace()

    @property
    def widgets(self) -> SaltWidgetNamespace:
        return self._widgets_ns

    def build(self) -> SaltDiagram:
        content = tuple(
            el for el in self._elements
            if not isinstance(el, tuple)  # skip separators
        )
        return SaltDiagram(
            content=content,
            title=self._title,
            mainframe=self._mainframe,
        )


def salt_diagram(
    *,
    title: str | None = None,
    mainframe: str | None = None,
) -> SaltComposer:
    """Create a salt wireframe diagram composer.

    Example:
        d = salt_diagram(title="Login Form")
        w = d.widgets
        d.add(w.text_field("username"), w.button("Login"))
        print(render(d))
    """
    return SaltComposer(title=title, mainframe=mainframe)
