"""Tests for the salt wireframe composer."""

import subprocess

import pytest

from plantuml_compose.composers.salt import salt_diagram
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
    Separator,
    TabBar,
    Text,
    TextField,
    Tree,
)
from plantuml_compose.renderers import render


class TestSaltComposer:

    def test_empty_diagram(self):
        d = salt_diagram()
        result = d.build()
        assert isinstance(result, SaltDiagram)
        assert result.content == ()

    def test_title(self):
        d = salt_diagram(title="My Form")
        result = d.build()
        assert result.title == "My Form"

    def test_text_widget(self):
        d = salt_diagram()
        w = d.widgets
        d.add(w.text("Hello"))
        result = d.build()
        assert len(result.content) == 1
        assert isinstance(result.content[0], Text)
        assert result.content[0].text == "Hello"

    def test_button_widget(self):
        d = salt_diagram()
        w = d.widgets
        d.add(w.button("Submit"))
        result = d.build()
        assert isinstance(result.content[0], Button)
        assert result.content[0].label == "Submit"

    def test_checkbox_widget(self):
        d = salt_diagram()
        w = d.widgets
        d.add(w.checkbox("Agree", checked=True))
        result = d.build()
        assert isinstance(result.content[0], Checkbox)
        assert result.content[0].checked is True

    def test_radio_widget(self):
        d = salt_diagram()
        w = d.widgets
        d.add(w.radio("Option A", selected=True))
        result = d.build()
        assert isinstance(result.content[0], Radio)
        assert result.content[0].selected is True

    def test_text_field_widget(self):
        d = salt_diagram()
        w = d.widgets
        d.add(w.text_field("default", width=20))
        result = d.build()
        assert isinstance(result.content[0], TextField)
        assert result.content[0].value == "default"
        assert result.content[0].width == 20

    def test_dropdown_variadic(self):
        d = salt_diagram()
        w = d.widgets
        d.add(w.dropdown("DC1", "DC2", "DC3"))
        result = d.build()
        dd = result.content[0]
        assert isinstance(dd, Dropdown)
        assert dd.items == ("DC1", "DC2", "DC3")

    def test_separator(self):
        d = salt_diagram()
        w = d.widgets
        d.add(w.separator("=="))
        result = d.build()
        assert isinstance(result.content[0], Separator)
        assert result.content[0].style == "=="

    def test_grid_with_rows(self):
        d = salt_diagram()
        w = d.widgets
        d.add(w.grid("#",
            w.row(w.text("Name"), w.text_field("John", width=15)),
            w.row(w.text("Age"), w.text_field("30", width=5)),
        ))
        result = d.build()
        grid = result.content[0]
        assert isinstance(grid, Grid)
        assert grid.style == "#"
        assert len(grid.rows) == 2
        assert isinstance(grid.rows[0], Row)
        assert isinstance(grid.rows[0].cells[0], Text)

    def test_menu(self):
        d = salt_diagram()
        w = d.widgets
        d.add(w.menu("File", "Edit", sub_items=(("File", "New"),)))
        result = d.build()
        menu = result.content[0]
        assert isinstance(menu, Menu)
        assert menu.items == ("File", "Edit")
        assert menu.sub_items == (("File", "New"),)

    def test_tab_bar(self):
        d = salt_diagram()
        w = d.widgets
        d.add(w.tab_bar("Tab1", "Tab2"))
        result = d.build()
        assert isinstance(result.content[0], TabBar)
        assert result.content[0].tabs == ("Tab1", "Tab2")

    def test_group_box(self):
        d = salt_diagram()
        w = d.widgets
        d.add(w.group_box("Login",
            w.text_field("username"),
            w.button("Submit"),
        ))
        result = d.build()
        gb = result.content[0]
        assert isinstance(gb, GroupBox)
        assert gb.title == "Login"
        assert len(gb.content) == 2

    def test_tree(self):
        d = salt_diagram()
        w = d.widgets
        d.add(w.tree((1, "Root"), (2, "Child")))
        result = d.build()
        assert isinstance(result.content[0], Tree)
        assert result.content[0].nodes == ((1, "Root"), (2, "Child"))

    def test_no_primitive_imports_needed(self):
        """All widgets constructable from d.widgets alone."""
        d = salt_diagram()
        w = d.widgets
        d.add(
            w.text("label"),
            w.button("btn"),
            w.checkbox("cb"),
            w.radio("rd"),
            w.text_field("val"),
            w.dropdown("a", "b"),
            w.separator(),
        )
        result = d.build()
        assert len(result.content) == 7

    def test_render_produces_plantuml(self):
        d = salt_diagram(title="Test")
        w = d.widgets
        d.add(w.button("OK"))
        result = render(d)
        assert "@startsalt" in result
        assert "[OK]" in result or "OK" in result
        assert "@endsalt" in result

class TestSaltPlantUMLValidation:

    @pytest.fixture
    def plantuml_check(self):
        try:
            result = subprocess.run(
                ["plantuml", "-version"],
                capture_output=True, timeout=10,
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def test_form_valid_plantuml(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = salt_diagram(title="Provisioning")
        w = d.widgets
        d.add(
            w.menu("File", "Servers"),
            w.tab_bar("New", "Bulk"),
            w.grid("#",
                w.row(w.text("MAC"), w.text_field("aa:bb:cc", width=20)),
                w.row(w.text("DC"), w.dropdown("DC1", "DC2")),
            ),
            w.separator("=="),
            w.radio("Provision", selected=True),
            w.radio("Decommission"),
            w.checkbox("Burn-in", checked=True),
            w.separator("=="),
            w.grid("+", w.row(w.button("Submit"), w.button("Cancel"))),
        )

        puml_file = tmp_path / "salt_composer.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"
