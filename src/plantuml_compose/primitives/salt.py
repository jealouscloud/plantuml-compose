"""Salt wireframe primitives.

Salt wireframes are UI mockup diagrams for sketching user interfaces.
They use a widget-based syntax with grid layout for arranging elements
in rows and columns.

Key concepts:
    Widget:    A UI element (button, checkbox, text field, etc.)
    Grid:      A table-like layout with configurable borders
    Container: A grouping widget (tabs, tree, menu, scrollbar, group box)
    Separator: A horizontal divider line between rows

All types are frozen dataclasses - immutable data with no behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, TypeAlias


# Grid border styles control which lines are drawn
GridStyle = Literal[
    "#",   # All lines (complete grid)
    "!",   # Vertical lines only
    "-",   # Horizontal lines only
    "+",   # External lines only (outer border)
]

# Separator line styles
SeparatorStyle = Literal[
    "..",   # Dotted
    "==",   # Double line
    "~~",   # Wave
    "--",   # Dashed
]

# Scrollbar variants
ScrollbarStyle = Literal[
    "S",    # Both scrollbars
    "SI",   # Vertical scrollbar only
    "S-",   # Horizontal scrollbar only
]


@dataclass(frozen=True)
class Text:
    """A plain text label.

    Renders as literal text in the wireframe.
    """

    text: str


@dataclass(frozen=True)
class Button:
    """A button widget.

    Rendered as: [label]
    """

    label: str


@dataclass(frozen=True)
class Checkbox:
    """A checkbox widget.

    Rendered as: [X] label (checked) or [] label (unchecked)
    """

    label: str
    checked: bool = False


@dataclass(frozen=True)
class Radio:
    """A radio button widget.

    Rendered as: (X) label (selected) or () label (unselected)
    """

    label: str
    selected: bool = False


@dataclass(frozen=True)
class TextField:
    """A text input field.

    Rendered as: "text    " — trailing spaces control the visual width.

        value: Default text displayed in the field
        width: Approximate character width (adds trailing spaces)
    """

    value: str = ""
    width: int = 10


@dataclass(frozen=True)
class Dropdown:
    """A dropdown/combobox widget.

    Rendered as: ^item1^item2^item3^ — items separated by carets.
    The first item is displayed as the selected value.

        items: List of dropdown option strings
    """

    items: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Separator:
    """A horizontal separator line between rows.

    Rendered as: .., ==, ~~, or -- depending on style.
    """

    style: SeparatorStyle = ".."


TreeStyle = Literal["T", "T!", "T-", "T+", "T#"]


@dataclass(frozen=True)
class Tree:
    """A tree widget showing hierarchical data.

    Rendered as:
        {T
        + Root
        ++ Child 1
        +++ Grandchild
        ++ Child 2
        }

        nodes: Tuple of (depth, label) pairs. depth=1 is root level.
        style: Tree line style variant (T, T!, T-, T+, T#)
    """

    nodes: tuple[tuple[int, str], ...] = field(default_factory=tuple)
    style: TreeStyle = "T"


@dataclass(frozen=True)
class TabBar:
    """A tab bar container.

    Rendered as: {/ Tab1 | Tab2 | Tab3 }
    The content of the active tab appears after the tab bar definition.

        tabs:          Tab label strings
        active_content: Widgets displayed in the active tab's content area
    """

    tabs: tuple[str, ...]
    active_content: tuple["SaltWidget", ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Menu:
    """A menu bar.

    Rendered as: {* File | Edit | View }
    For nested menus, sub-items follow on additional lines.

        items: Top-level menu item labels
        sub_items: Tuple of (parent, child) pairs for nested menus
    """

    items: tuple[str, ...]
    sub_items: tuple[tuple[str, str], ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Scrollbar:
    """A scrollbar container wrapping content.

    Rendered as: {S content }, {SI content }, or {S- content }

        style:   Scrollbar variant (both, vertical only, horizontal only)
        content: Widgets displayed inside the scrollbar area
    """

    style: ScrollbarStyle = "S"
    content: tuple["SaltWidget", ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class GroupBox:
    """A titled group box container.

    Rendered as:
        {^"Title"
          content
        }

        title:   The group box title
        content: Widgets displayed inside the group box
    """

    title: str
    content: tuple["SaltWidget", ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Row:
    """A row of widgets separated by | in grid layout.

    Each cell can contain a widget or nested grid.
    """

    cells: tuple["SaltWidget", ...]


@dataclass(frozen=True)
class Grid:
    """A grid layout container with configurable borders.

    Rendered as:
        {#
          Cell 1 | Cell 2
          Cell 3 | Cell 4
        }

        style: Border style (#=all, !=vertical, -=horizontal, +=external)
        rows:  Grid content — rows separated by newlines, cells by |
    """

    style: GridStyle = "#"
    rows: tuple["SaltWidget", ...] = field(default_factory=tuple)


# Type alias for all widgets that can appear in a Salt wireframe
SaltWidget: TypeAlias = (
    Text
    | Button
    | Checkbox
    | Radio
    | TextField
    | Dropdown
    | Separator
    | Tree
    | TabBar
    | Menu
    | Scrollbar
    | GroupBox
    | Row
    | Grid
)


@dataclass(frozen=True)
class SaltDiagram:
    """A complete Salt wireframe diagram.

    Contains the top-level layout and diagram-level settings.

        content:   Top-level widgets (usually a single Grid)
        title:     Optional diagram title
        mainframe: Optional frame label around the entire diagram
    """

    content: tuple[SaltWidget, ...] = field(default_factory=tuple)
    title: str | None = None
    mainframe: str | None = None
