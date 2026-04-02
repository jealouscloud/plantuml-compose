"""Tests for depth selectors, stereotype selectors, and new style properties."""
import subprocess

import pytest

from plantuml_compose import (
    class_diagram,
    component_diagram,
    mindmap_diagram,
    render,
    state_diagram,
    wbs_diagram,
)


class TestElementStyleNewProperties:

    def test_diagonal_corner(self):
        d = class_diagram(diagram_style={
            "class_": {"diagonal_corner": 10},
        })
        output = render(d)
        assert "DiagonalCorner 10" in output

    def test_word_wrap(self):
        d = class_diagram(diagram_style={
            "class_": {"word_wrap": 200},
        })
        output = render(d)
        assert "WordWrap 200" in output

    def test_hyperlink_color(self):
        d = class_diagram(diagram_style={
            "class_": {"hyperlink_color": "blue"},
        })
        output = render(d)
        assert "HyperLinkColor" in output

    def test_all_new_properties_together(self):
        d = class_diagram(diagram_style={
            "class_": {
                "diagonal_corner": 5,
                "word_wrap": 150,
                "hyperlink_color": "#0000FF",
            },
        })
        output = render(d)
        assert "DiagonalCorner 5" in output
        assert "WordWrap 150" in output
        assert "HyperLinkColor" in output


class TestArrowStyleFontProperties:

    def test_arrow_font_color(self):
        d = class_diagram(diagram_style={
            "arrow": {"font_color": "blue"},
        })
        output = render(d)
        assert "FontColor" in output

    def test_arrow_font_size(self):
        d = class_diagram(diagram_style={
            "arrow": {"font_size": 14},
        })
        output = render(d)
        assert "FontSize 14" in output

    def test_arrow_font_name(self):
        d = class_diagram(diagram_style={
            "arrow": {"font_name": "Courier"},
        })
        output = render(d)
        assert "FontName Courier" in output

    def test_arrow_all_properties(self):
        d = class_diagram(diagram_style={
            "arrow": {
                "line_color": "red",
                "line_thickness": 2,
                "font_color": "blue",
                "font_size": 12,
                "font_name": "Arial",
            },
        })
        output = render(d)
        assert "LineColor" in output
        assert "LineThickness 2" in output
        assert "FontColor" in output
        assert "FontSize 12" in output
        assert "FontName Arial" in output


class TestDepthSelectors:

    def test_mindmap_depth(self):
        d = mindmap_diagram(diagram_style={
            "depths": {
                0: {"background": "pink"},
                1: {"background": "lightblue"},
            },
        })
        n = d.nodes
        d.add(n.node("Root", n.leaf("Child")))
        output = render(d)
        assert ":depth(0)" in output
        assert ":depth(1)" in output
        assert "pink" in output
        assert "lightblue" in output

    def test_wbs_depth(self):
        d = wbs_diagram(diagram_style={
            "depths": {
                0: {"background": "#E3F2FD"},
                1: {"background": "#BBDEFB"},
                2: {"background": "#90CAF9"},
            },
        })
        n = d.nodes
        d.add(n.node("Project", n.node("Phase", n.leaf("Task"))))
        output = render(d)
        assert ":depth(0)" in output
        assert ":depth(1)" in output
        assert ":depth(2)" in output

    def test_depth_with_element_styles(self):
        d = mindmap_diagram(diagram_style={
            "node": {"font_size": 14},
            "depths": {
                0: {"background": "pink", "font_style": "bold"},
            },
        })
        n = d.nodes
        d.add(n.node("Root", n.leaf("Child")))
        output = render(d)
        assert "node {" in output
        assert ":depth(0)" in output
        assert "FontStyle bold" in output


class TestStereotypeSelectors:

    def test_class_stereotype(self):
        d = class_diagram(diagram_style={
            "stereotypes": {
                "important": {"background": "pink", "font_style": "bold"},
            },
        })
        el = d.elements
        d.add(el.class_("Foo", stereotype="important"))
        output = render(d)
        assert ".important" in output
        assert "pink" in output
        assert "FontStyle bold" in output

    def test_component_stereotype_with_color(self):
        d = component_diagram(diagram_style={
            "stereotypes": {
                "error": {"background": "#FFCDD2"},
            },
        })
        output = render(d)
        assert ".error" in output

    def test_component_stereotype(self):
        d = component_diagram(diagram_style={
            "stereotypes": {
                "service": {"background": "lightgreen"},
            },
        })
        output = render(d)
        assert ".service" in output

    def test_multiple_stereotypes(self):
        d = class_diagram(diagram_style={
            "stereotypes": {
                "important": {"background": "pink"},
                "deprecated": {"font_color": "gray", "font_style": "italic"},
            },
        })
        output = render(d)
        assert ".important" in output
        assert ".deprecated" in output
        assert "gray" in output

    def test_stereotype_with_element_styles(self):
        d = class_diagram(diagram_style={
            "class_": {"background": "white"},
            "stereotypes": {
                "highlight": {"background": "yellow"},
            },
        })
        output = render(d)
        assert "class {" in output or "classDiagram" in output
        assert ".highlight" in output


class TestStylePlantUMLValidation:

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

    def test_new_element_properties_valid(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")
        d = class_diagram(diagram_style={
            "class_": {
                "diagonal_corner": 10,
                "word_wrap": 200,
            },
        })
        el = d.elements
        d.add(el.class_("Foo"))
        puml = tmp_path / "test.puml"
        puml.write_text(render(d))
        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_depth_selectors_valid(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")
        d = mindmap_diagram(diagram_style={
            "depths": {
                0: {"background": "pink"},
                1: {"background": "lightblue"},
            },
        })
        n = d.nodes
        d.add(n.node("Root", n.leaf("A"), n.leaf("B")))
        puml = tmp_path / "test.puml"
        puml.write_text(render(d))
        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_stereotype_selectors_valid(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")
        d = class_diagram(diagram_style={
            "stereotypes": {
                "important": {"background": "pink"},
            },
        })
        el = d.elements
        d.add(el.class_("Foo", stereotype="important"))
        puml = tmp_path / "test.puml"
        puml.write_text(render(d))
        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_arrow_font_properties_valid(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")
        d = class_diagram(diagram_style={
            "arrow": {
                "line_color": "red",
                "font_color": "blue",
                "font_size": 12,
            },
        })
        el = d.elements
        r = d.relationships
        a, b = el.class_("A"), el.class_("B")
        d.add(a, b)
        d.connect(r.arrow(a, b, label="go"))
        puml = tmp_path / "test.puml"
        puml.write_text(render(d))
        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"
