"""Tests for Salt wireframe diagrams."""

import pytest

from plantuml_compose import salt_diagram, render
from plantuml_compose.primitives.salt import (
    Button,
    Checkbox,
    Dropdown,
    Grid,
    GroupBox,
    Menu,
    Radio,
    Row,
    SaltDiagram,
    Scrollbar,
    Separator,
    TabBar,
    Text,
    TextField,
    Tree,
)


class TestSaltBasic:
    """Basic Salt wireframe tests."""

    def test_empty_salt_diagram(self):
        with salt_diagram() as d:
            pass
        result = d.render()
        assert "@startsalt" in result
        assert "@endsalt" in result

    def test_salt_with_title(self):
        with salt_diagram(title="Login Form") as d:
            d.text("Hello")
        result = d.render()
        assert "title Login Form" in result

    def test_salt_with_mainframe(self):
        with salt_diagram(mainframe="My Wireframe") as d:
            d.text("Content")
        result = d.render()
        assert "mainframe My Wireframe" in result

    def test_render_dispatch(self):
        """Verify render() dispatches SaltDiagram correctly."""
        with salt_diagram() as d:
            d.text("Hello")
        result = render(d.build())
        assert "@startsalt" in result
        assert "Hello" in result


class TestSaltWidgets:
    """Tests for individual Salt widgets."""

    def test_text(self):
        with salt_diagram() as d:
            d.text("Username")
        result = d.render()
        assert "Username" in result

    def test_button(self):
        with salt_diagram() as d:
            d.button("Submit")
        result = d.render()
        assert "[Submit]" in result

    def test_checkbox_unchecked(self):
        with salt_diagram() as d:
            d.checkbox("Remember me")
        result = d.render()
        assert "[ ] Remember me" in result

    def test_checkbox_checked(self):
        with salt_diagram() as d:
            d.checkbox("I agree", checked=True)
        result = d.render()
        assert "[X] I agree" in result

    def test_radio_unselected(self):
        with salt_diagram() as d:
            d.radio("Option A")
        result = d.render()
        assert "( ) Option A" in result

    def test_radio_selected(self):
        with salt_diagram() as d:
            d.radio("Option B", selected=True)
        result = d.render()
        assert "(X) Option B" in result

    def test_text_field_default(self):
        with salt_diagram() as d:
            d.text_field()
        result = d.render()
        # Default: empty value, width=10 → 10 spaces
        assert '"          "' in result

    def test_text_field_with_value(self):
        with salt_diagram() as d:
            d.text_field("John", width=10)
        result = d.render()
        # "John" + 6 trailing spaces to reach width 10
        assert '"John      "' in result

    def test_text_field_custom_width(self):
        with salt_diagram() as d:
            d.text_field("Hi", width=5)
        result = d.render()
        assert '"Hi   "' in result

    def test_text_field_value_exceeds_width(self):
        """When value is longer than width, no truncation — just no padding."""
        with salt_diagram() as d:
            d.text_field("Hello World", width=5)
        result = d.render()
        assert '"Hello World"' in result

    def test_dropdown(self):
        with salt_diagram() as d:
            d.dropdown("Option 1", "Option 2", "Option 3")
        result = d.render()
        assert "^Option 1^Option 2^Option 3^" in result

    def test_dropdown_requires_items(self):
        with salt_diagram() as d:
            with pytest.raises(ValueError, match="at least one item"):
                d.dropdown()

    def test_separator_default(self):
        with salt_diagram() as d:
            d.separator()
        result = d.render()
        assert ".." in result

    def test_separator_double(self):
        with salt_diagram() as d:
            d.separator("==")
        result = d.render()
        assert "==" in result

    def test_separator_wave(self):
        with salt_diagram() as d:
            d.separator("~~")
        result = d.render()
        assert "~~" in result

    def test_separator_dashed(self):
        with salt_diagram() as d:
            d.separator("--")
        result = d.render()
        assert "--" in result


class TestSaltGrid:
    """Tests for grid layout."""

    def test_grid_all_lines(self):
        with salt_diagram() as d:
            with d.grid("#") as g:
                g.row(Text("A"), Text("B"))
                g.row(Text("C"), Text("D"))
        result = d.render()
        assert "{#" in result
        assert "A | B" in result
        assert "C | D" in result

    def test_grid_vertical_only(self):
        with salt_diagram() as d:
            with d.grid("!") as g:
                g.row(Text("X"), Text("Y"))
        result = d.render()
        assert "{!" in result

    def test_grid_horizontal_only(self):
        with salt_diagram() as d:
            with d.grid("-") as g:
                g.row(Text("X"), Text("Y"))
        result = d.render()
        assert "{-" in result

    def test_grid_external_only(self):
        with salt_diagram() as d:
            with d.grid("+") as g:
                g.row(Text("X"), Text("Y"))
        result = d.render()
        assert "{+" in result

    def test_grid_with_widgets(self):
        with salt_diagram() as d:
            with d.grid() as g:
                g.row(Text("Name"), TextField("", width=15))
                g.row(Text("Email"), TextField("", width=15))
        result = d.render()
        assert "Name |" in result
        assert "Email |" in result

    def test_grid_with_separator(self):
        with salt_diagram() as d:
            with d.grid() as g:
                g.row(Text("Header 1"), Text("Header 2"))
                g.separator("..")
                g.row(Text("Data 1"), Text("Data 2"))
        result = d.render()
        lines = result.split("\n")
        # Separator should appear between rows
        assert any(".." in line for line in lines)

    def test_row_outside_grid(self):
        with salt_diagram() as d:
            d.row(Text("A"), Button("B"), Checkbox("C"))
        result = d.render()
        assert "A | [B] | [ ] C" in result


class TestSaltContainers:
    """Tests for container widgets."""

    def test_tree(self):
        with salt_diagram() as d:
            d.tree(
                (1, "Root"),
                (2, "Child 1"),
                (3, "Grandchild"),
                (2, "Child 2"),
            )
        result = d.render()
        assert "{T" in result
        assert "+ Root" in result
        assert "++ Child 1" in result
        assert "+++ Grandchild" in result
        assert "++ Child 2" in result

    def test_tree_requires_nodes(self):
        with salt_diagram() as d:
            with pytest.raises(ValueError, match="at least one node"):
                d.tree()

    def test_tab_bar(self):
        with salt_diagram() as d:
            d.tab_bar("General", "Advanced", "About")
        result = d.render()
        assert "{/ General | Advanced | About}" in result

    def test_tab_bar_with_content(self):
        with salt_diagram() as d:
            d.tab_bar(
                "Tab1", "Tab2",
                content=(Text("Tab 1 content"),),
            )
        result = d.render()
        assert "{/ Tab1 | Tab2" in result
        assert "Tab 1 content" in result

    def test_tab_bar_requires_tabs(self):
        with salt_diagram() as d:
            with pytest.raises(ValueError, match="at least one tab"):
                d.tab_bar()

    def test_menu(self):
        with salt_diagram() as d:
            d.menu("File", "Edit", "View")
        result = d.render()
        assert "{* File | Edit | View}" in result

    def test_menu_with_sub_items(self):
        with salt_diagram() as d:
            d.menu(
                "File", "Edit",
                sub_items=(("File", "New"), ("File", "Open")),
            )
        result = d.render()
        assert "{* File | Edit" in result
        assert "File | New" in result
        assert "File | Open" in result

    def test_menu_requires_items(self):
        with salt_diagram() as d:
            with pytest.raises(ValueError, match="at least one item"):
                d.menu()

    def test_scrollbar_both(self):
        with salt_diagram() as d:
            with d.scrollbar("S") as s:
                s.text("Scrollable content")
        result = d.render()
        assert "{S" in result
        assert "Scrollable content" in result

    def test_scrollbar_vertical(self):
        with salt_diagram() as d:
            with d.scrollbar("SI") as s:
                s.text("Vertical only")
        result = d.render()
        assert "{SI" in result

    def test_scrollbar_horizontal(self):
        with salt_diagram() as d:
            with d.scrollbar("S-") as s:
                s.text("Horizontal only")
        result = d.render()
        assert "{S-" in result

    def test_group_box(self):
        with salt_diagram() as d:
            with d.group_box("Login") as g:
                g.text_field("username")
                g.button("Submit")
        result = d.render()
        assert '{^"Login"' in result
        assert "[Submit]" in result


class TestSaltContainerBuilder:
    """Tests for the _ContainerBuilder widget methods."""

    def test_container_checkbox(self):
        with salt_diagram() as d:
            with d.group_box("Options") as g:
                g.checkbox("Option A", checked=True)
                g.checkbox("Option B")
        result = d.render()
        assert "[X] Option A" in result
        assert "[ ] Option B" in result

    def test_container_radio(self):
        with salt_diagram() as d:
            with d.group_box("Choice") as g:
                g.radio("Yes", selected=True)
                g.radio("No")
        result = d.render()
        assert "(X) Yes" in result
        assert "( ) No" in result

    def test_container_dropdown(self):
        with salt_diagram() as d:
            with d.group_box("Select") as g:
                g.dropdown("A", "B", "C")
        result = d.render()
        assert "^A^B^C^" in result

    def test_container_dropdown_requires_items(self):
        with salt_diagram() as d:
            with d.group_box("G") as g:
                with pytest.raises(ValueError, match="at least one item"):
                    g.dropdown()

    def test_container_separator(self):
        with salt_diagram() as d:
            with d.group_box("Group") as g:
                g.text("Above")
                g.separator("==")
                g.text("Below")
        result = d.render()
        assert "==" in result

    def test_container_row(self):
        with salt_diagram() as d:
            with d.group_box("Form") as g:
                g.row(Text("Name"), TextField("", width=10))
        result = d.render()
        assert "Name |" in result


class TestSaltComposite:
    """Tests combining multiple features."""

    def test_login_form(self):
        """A realistic login form wireframe."""
        with salt_diagram(title="Login") as d:
            with d.grid() as g:
                g.row(Text("Username"), TextField(width=20))
                g.row(Text("Password"), TextField(width=20))
            d.checkbox("Remember me")
            d.separator("..")
            d.button("Login")
        result = d.render()
        assert "@startsalt" in result
        assert "title Login" in result
        assert "{#" in result
        assert "Username |" in result
        assert "Password |" in result
        assert "[ ] Remember me" in result
        assert ".." in result
        assert "[Login]" in result
        assert "@endsalt" in result

    def test_form_with_group_boxes(self):
        """Form with multiple group boxes."""
        with salt_diagram() as d:
            with d.group_box("Personal Info") as g:
                g.text_field("First name", width=15)
                g.text_field("Last name", width=15)
            with d.group_box("Preferences") as g:
                g.checkbox("Newsletter", checked=True)
                g.radio("Light theme", selected=True)
                g.radio("Dark theme")
        result = d.render()
        assert '{^"Personal Info"' in result
        assert '{^"Preferences"' in result
        assert "[X] Newsletter" in result
        assert "(X) Light theme" in result
        assert "( ) Dark theme" in result

    def test_build_returns_salt_diagram(self):
        with salt_diagram() as d:
            d.text("Hello")
        diagram = d.build()
        assert isinstance(diagram, SaltDiagram)
        assert len(diagram.content) == 1
        assert isinstance(diagram.content[0], Text)

    def test_row_rejects_multiline_widget(self):
        """Row cells must be single-line — multi-line widgets raise TypeError."""
        with salt_diagram() as d:
            # Tree renders to multiple lines, so it can't go in a Row cell
            tree = Tree(nodes=((1, "Root"), (2, "Child")))
            d.row(tree, Text("B"))
        with pytest.raises(TypeError, match="single-line"):
            d.render()

    def test_primitives_are_frozen(self):
        widget = Button(label="Test")
        with pytest.raises(AttributeError):
            widget.label = "Changed"

        diagram = SaltDiagram(content=(widget,))
        with pytest.raises(AttributeError):
            diagram.title = "Changed"
