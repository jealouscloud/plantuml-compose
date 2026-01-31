"""Tests for MindMap diagram type."""

import subprocess

import pytest

from plantuml_compose.builders.mindmap import mindmap_diagram
from plantuml_compose.primitives.mindmap import MindMapDiagram, MindMapNode
from plantuml_compose.renderers import render
from plantuml_compose.renderers.mindmap import render_mindmap_diagram


class TestMindMapNode:
    """Tests for MindMapNode primitive."""

    def test_basic_node(self):
        node = MindMapNode(text="Hello", depth=1)
        assert node.text == "Hello"
        assert node.depth == 1
        assert node.side is None
        assert node.color is None
        assert node.boxless is False

    def test_node_with_all_options(self):
        node = MindMapNode(
            text="Branch",
            depth=2,
            side="left",
            color="#Orange",
            boxless=True,
        )
        assert node.text == "Branch"
        assert node.depth == 2
        assert node.side == "left"
        assert node.color == "#Orange"
        assert node.boxless is True


class TestMindMapDiagram:
    """Tests for MindMapDiagram primitive."""

    def test_empty_diagram(self):
        diagram = MindMapDiagram()
        assert diagram.nodes == ()
        assert diagram.direction is None
        assert diagram.diagram_style is None

    def test_diagram_with_nodes(self):
        nodes = (
            MindMapNode("Root", depth=1),
            MindMapNode("Branch", depth=2),
        )
        diagram = MindMapDiagram(nodes=nodes)
        assert len(diagram.nodes) == 2

    def test_diagram_with_direction(self):
        diagram = MindMapDiagram(direction="top_to_bottom")
        assert diagram.direction == "top_to_bottom"


class TestMindMapRenderer:
    """Tests for MindMap rendering."""

    def test_render_empty_diagram(self):
        diagram = MindMapDiagram()
        result = render_mindmap_diagram(diagram)
        assert result == "@startmindmap\n@endmindmap"

    def test_render_single_node(self):
        diagram = MindMapDiagram(
            nodes=(MindMapNode("Root", depth=1),)
        )
        result = render_mindmap_diagram(diagram)
        assert "@startmindmap" in result
        assert "* Root" in result
        assert "@endmindmap" in result

    def test_render_tree_structure(self):
        diagram = MindMapDiagram(
            nodes=(
                MindMapNode("Root", depth=1),
                MindMapNode("Branch 1", depth=2),
                MindMapNode("Leaf 1.1", depth=3),
                MindMapNode("Leaf 1.2", depth=3),
                MindMapNode("Branch 2", depth=2),
            )
        )
        result = render_mindmap_diagram(diagram)
        lines = result.split("\n")
        assert "* Root" in lines
        assert "** Branch 1" in lines
        assert "*** Leaf 1.1" in lines
        assert "*** Leaf 1.2" in lines
        assert "** Branch 2" in lines

    def test_render_arithmetic_notation_right(self):
        diagram = MindMapDiagram(
            nodes=(
                MindMapNode("Root", depth=1),
                MindMapNode("Right", depth=2, side="right"),
            )
        )
        result = render_mindmap_diagram(diagram)
        assert "++ Right" in result

    def test_render_arithmetic_notation_left(self):
        diagram = MindMapDiagram(
            nodes=(
                MindMapNode("Root", depth=1),
                MindMapNode("Left", depth=2, side="left"),
            )
        )
        result = render_mindmap_diagram(diagram)
        assert "-- Left" in result

    def test_render_colored_node(self):
        diagram = MindMapDiagram(
            nodes=(MindMapNode("Colored", depth=1, color="#Orange"),)
        )
        result = render_mindmap_diagram(diagram)
        assert "*[#Orange] Colored" in result

    def test_render_boxless_node(self):
        diagram = MindMapDiagram(
            nodes=(MindMapNode("Boxless", depth=1, boxless=True),)
        )
        result = render_mindmap_diagram(diagram)
        assert "*_ Boxless" in result

    def test_render_boxless_with_color(self):
        diagram = MindMapDiagram(
            nodes=(MindMapNode("Both", depth=1, color="#Blue", boxless=True),)
        )
        result = render_mindmap_diagram(diagram)
        # Color comes before boxless marker: *[#color]_
        assert "*[#Blue]_ Both" in result

    def test_render_multiline_node(self):
        diagram = MindMapDiagram(
            nodes=(MindMapNode("Line 1\nLine 2", depth=1),)
        )
        result = render_mindmap_diagram(diagram)
        assert "*:Line 1\nLine 2;" in result

    def test_render_direction(self):
        diagram = MindMapDiagram(direction="top_to_bottom")
        result = render_mindmap_diagram(diagram)
        assert "top to bottom direction" in result

    def test_render_left_to_right_direction(self):
        diagram = MindMapDiagram(direction="left_to_right")
        result = render_mindmap_diagram(diagram)
        assert "left to right direction" in result


class TestMindMapBuilder:
    """Tests for MindMap builder."""

    def test_builder_basic(self):
        with mindmap_diagram() as d:
            d.node("Root")
            d.node("Branch", depth=2)

        diagram = d.build()
        assert len(diagram.nodes) == 2
        assert diagram.nodes[0].text == "Root"
        assert diagram.nodes[0].depth == 1
        assert diagram.nodes[1].text == "Branch"
        assert diagram.nodes[1].depth == 2

    def test_builder_with_options(self):
        with mindmap_diagram() as d:
            d.node("Root", color="#Red")
            d.node("Left", depth=2, side="left", boxless=True)

        diagram = d.build()
        assert diagram.nodes[0].color == "#Red"
        assert diagram.nodes[1].side == "left"
        assert diagram.nodes[1].boxless is True

    def test_builder_invalid_depth(self):
        with mindmap_diagram() as d:
            with pytest.raises(ValueError, match="Depth must be >= 1"):
                d.node("Invalid", depth=0)

    def test_builder_with_direction(self):
        with mindmap_diagram(direction="top_to_bottom") as d:
            d.node("Root")

        diagram = d.build()
        assert diagram.direction == "top_to_bottom"

    def test_builder_render(self):
        with mindmap_diagram() as d:
            d.node("Test")

        result = d.render()
        assert "@startmindmap" in result
        assert "* Test" in result


class TestMindMapDispatch:
    """Tests for render() dispatch function with MindMap."""

    def test_render_dispatch(self):
        diagram = MindMapDiagram(
            nodes=(MindMapNode("Root", depth=1),)
        )
        result = render(diagram)
        assert "@startmindmap" in result
        assert "* Root" in result


class TestMindMapPlantUMLIntegration:
    """Integration tests verifying PlantUML accepts the output."""

    @pytest.fixture
    def plantuml_check(self):
        """Check if PlantUML is available."""
        try:
            result = subprocess.run(
                ["plantuml", "-version"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def test_basic_mindmap_syntax(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with mindmap_diagram() as d:
            d.node("Central Topic")
            d.node("Branch 1", depth=2)
            d.node("Leaf 1.1", depth=3)
            d.node("Leaf 1.2", depth=3)
            d.node("Branch 2", depth=2)
            d.node("Leaf 2.1", depth=3)

        puml_file = tmp_path / "mindmap.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_arithmetic_notation_syntax(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with mindmap_diagram() as d:
            d.node("Root")
            d.node("Right 1", depth=2, side="right")
            d.node("Right 1.1", depth=3, side="right")
            d.node("Left 1", depth=2, side="left")
            d.node("Left 1.1", depth=3, side="left")

        puml_file = tmp_path / "mindmap_arithmetic.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_colored_nodes_syntax(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with mindmap_diagram() as d:
            d.node("Root", color="#Orange")
            d.node("Green", depth=2, color="#lightgreen")
            d.node("Blue", depth=2, color="#ADD8E6")

        puml_file = tmp_path / "mindmap_colors.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_boxless_nodes_syntax(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with mindmap_diagram() as d:
            d.node("Boxless Root", boxless=True)
            d.node("Boxless Child", depth=2, boxless=True)
            d.node("Normal Child", depth=2)

        puml_file = tmp_path / "mindmap_boxless.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_multiline_node_syntax(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with mindmap_diagram() as d:
            d.node("Single line root")
            d.node("Multi-line\nnode content", depth=2)

        puml_file = tmp_path / "mindmap_multiline.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_direction_syntax(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with mindmap_diagram(direction="top_to_bottom") as d:
            d.node("Root")
            d.node("Child 1", depth=2)
            d.node("Child 2", depth=2)

        puml_file = tmp_path / "mindmap_direction.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_boxless_with_color_syntax(self, plantuml_check, tmp_path):
        """Test that boxless + color combination generates valid PlantUML."""
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with mindmap_diagram() as d:
            d.node("Root", color="#Blue", boxless=True)
            d.node("Child", depth=2, color="#Orange", boxless=True)

        puml_file = tmp_path / "mindmap_boxless_color.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"
