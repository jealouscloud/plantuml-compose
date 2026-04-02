"""Tests for depth selectors, stereotype selectors, and new style properties."""
import subprocess

import pytest

from plantuml_compose import (
    class_diagram,
    component_diagram,
    deployment_diagram,
    mindmap_diagram,
    render,
    state_diagram,
    usecase_diagram,
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


class TestUseCaseDiagramStyle:

    def test_usecase_diagram_style(self):
        d = usecase_diagram(diagram_style={
            "actor": {"background": "lightblue"},
            "usecase": {"background": "lightyellow"},
            "arrow": {"line_color": "gray"},
        })
        output = render(d)
        assert "usecaseDiagram" in output
        assert "actor {" in output
        assert "usecase {" in output

    def test_usecase_stereotype_style(self):
        d = usecase_diagram(diagram_style={
            "stereotypes": {"critical": {"background": "pink"}},
        })
        output = render(d)
        assert ".critical" in output

    def test_usecase_style_with_elements(self):
        d = usecase_diagram(diagram_style={
            "background": "white",
            "actor": {"background": "#E3F2FD"},
            "usecase": {"background": "#FFF9C4"},
            "package": {"background": "#F5F5F5"},
        })
        el = d.elements
        r = d.relationships
        user = el.actor("User")
        login = el.usecase("Login")
        d.add(user, login)
        d.connect(r.arrow(user, login))
        output = render(d)
        assert "usecaseDiagram" in output
        assert "actor {" in output
        assert "usecase {" in output
        assert "package {" in output

    def test_usecase_style_plantuml_valid(self, tmp_path):
        try:
            result = subprocess.run(
                ["plantuml", "-version"],
                capture_output=True, timeout=10,
            )
            if result.returncode != 0:
                pytest.skip("PlantUML not available")
        except FileNotFoundError:
            pytest.skip("PlantUML not available")

        d = usecase_diagram(diagram_style={
            "actor": {"background": "lightblue"},
            "usecase": {"background": "lightyellow"},
            "arrow": {"line_color": "gray"},
            "stereotypes": {"critical": {"background": "pink"}},
        })
        el = d.elements
        r = d.relationships
        user = el.actor("User")
        login = el.usecase("Login", stereotype="critical")
        d.add(user, login)
        d.connect(r.arrow(user, login))
        puml = tmp_path / "test.puml"
        puml.write_text(render(d))
        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"


class TestDeploymentDiagramStyle:

    def test_deployment_diagram_style(self):
        d = deployment_diagram(diagram_style={
            "node": {"background": "lightblue"},
            "artifact": {"background": "lightyellow"},
            "arrow": {"line_color": "gray"},
        })
        output = render(d)
        assert "deploymentDiagram" in output
        assert "node {" in output

    def test_deployment_stereotype_style(self):
        d = deployment_diagram(diagram_style={
            "stereotypes": {"production": {"background": "#E8F5E9"}},
        })
        output = render(d)
        assert ".production" in output

    def test_deployment_style_with_elements(self):
        d = deployment_diagram(diagram_style={
            "background": "white",
            "node": {"background": "#E3F2FD"},
            "database": {"background": "#FFF9C4"},
            "cloud": {"background": "#F5F5F5"},
        })
        el = d.elements
        c = d.connections
        server = el.node("Server")
        db = el.database("PostgreSQL")
        d.add(server, db)
        d.connect(c.arrow(server, db))
        output = render(d)
        assert "deploymentDiagram" in output
        assert "node {" in output
        assert "database {" in output
        assert "cloud {" in output

    def test_deployment_many_selectors(self):
        d = deployment_diagram(diagram_style={
            "node": {"background": "#E3F2FD"},
            "artifact": {"background": "#FFF9C4"},
            "database": {"background": "#C8E6C9"},
            "cloud": {"background": "#F5F5F5"},
            "component": {"background": "#FFCDD2"},
            "frame": {"background": "#E1BEE7"},
            "storage": {"background": "#FFE0B2"},
            "folder": {"background": "#B2EBF2"},
            "package": {"background": "#DCEDC8"},
            "rectangle": {"background": "#F0F4C3"},
            "queue": {"background": "#D7CCC8"},
            "stack": {"background": "#CFD8DC"},
        })
        output = render(d)
        assert "deploymentDiagram" in output
        assert "node {" in output
        assert "artifact {" in output
        assert "storage {" in output
        assert "queue {" in output
        assert "stack {" in output

    def test_deployment_style_plantuml_valid(self, tmp_path):
        try:
            result = subprocess.run(
                ["plantuml", "-version"],
                capture_output=True, timeout=10,
            )
            if result.returncode != 0:
                pytest.skip("PlantUML not available")
        except FileNotFoundError:
            pytest.skip("PlantUML not available")

        d = deployment_diagram(diagram_style={
            "node": {"background": "lightblue"},
            "artifact": {"background": "lightyellow"},
            "arrow": {"line_color": "gray"},
            "stereotypes": {"production": {"background": "#E8F5E9"}},
        })
        el = d.elements
        c = d.connections
        server = el.node("WebServer")
        app = el.artifact("App")
        d.add(server, app)
        d.connect(c.arrow(server, app))
        puml = tmp_path / "test.puml"
        puml.write_text(render(d))
        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"
