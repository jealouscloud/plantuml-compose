"""Tests for MindMap diagram type."""

import subprocess

import pytest

from plantuml_compose.builders.mindmap import mindmap_diagram
from plantuml_compose.primitives.common import Color
from plantuml_compose.primitives.mindmap import MindMapDiagram, MindMapNode
from plantuml_compose.renderers import render
from plantuml_compose.renderers.mindmap import render_mindmap_diagram


class TestMindMapNode:
    """Tests for MindMapNode primitive."""

    def test_basic_node(self):
        node = MindMapNode(text="Hello")
        assert node.text == "Hello"
        assert node.children == ()
        assert node.side is None
        assert node.color is None
        assert node.boxless is False

    def test_node_with_children(self):
        child = MindMapNode(text="Child")
        parent = MindMapNode(text="Parent", children=(child,))
        assert len(parent.children) == 1
        assert parent.children[0].text == "Child"

    def test_node_with_all_options(self):
        node = MindMapNode(
            text="Branch",
            children=(),
            side="left",
            color="#Orange",
            boxless=True,
        )
        assert node.side == "left"
        assert node.color == "#Orange"
        assert node.boxless is True


class TestMindMapDiagram:
    """Tests for MindMapDiagram primitive."""

    def test_empty_diagram(self):
        diagram = MindMapDiagram()
        assert diagram.roots == ()
        assert diagram.direction is None
        assert diagram.diagram_style is None

    def test_diagram_with_roots(self):
        root = MindMapNode("Root")
        diagram = MindMapDiagram(roots=(root,))
        assert len(diagram.roots) == 1

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
        diagram = MindMapDiagram(roots=(MindMapNode("Root"),))
        result = render_mindmap_diagram(diagram)
        assert "@startmindmap" in result
        assert "* Root" in result
        assert "@endmindmap" in result

    def test_render_tree_structure(self):
        diagram = MindMapDiagram(
            roots=(
                MindMapNode(
                    "Root",
                    children=(
                        MindMapNode(
                            "Branch 1",
                            children=(
                                MindMapNode("Leaf 1.1"),
                                MindMapNode("Leaf 1.2"),
                            ),
                        ),
                        MindMapNode("Branch 2"),
                    ),
                ),
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
            roots=(
                MindMapNode(
                    "Root",
                    children=(MindMapNode("Right", side="right"),),
                ),
            )
        )
        result = render_mindmap_diagram(diagram)
        assert "++ Right" in result

    def test_render_arithmetic_notation_left(self):
        diagram = MindMapDiagram(
            roots=(
                MindMapNode(
                    "Root",
                    children=(MindMapNode("Left", side="left"),),
                ),
            )
        )
        result = render_mindmap_diagram(diagram)
        assert "-- Left" in result

    def test_render_colored_node(self):
        diagram = MindMapDiagram(
            roots=(MindMapNode("Colored", color="#Orange"),)
        )
        result = render_mindmap_diagram(diagram)
        assert "*[#Orange] Colored" in result

    def test_render_colored_node_with_color_object(self):
        diagram = MindMapDiagram(
            roots=(MindMapNode("Colored", color=Color.rgb(255, 165, 0)),)
        )
        result = render_mindmap_diagram(diagram)
        assert "*[#FFA500] Colored" in result

    def test_render_boxless_node(self):
        diagram = MindMapDiagram(roots=(MindMapNode("Boxless", boxless=True),))
        result = render_mindmap_diagram(diagram)
        assert "*_ Boxless" in result

    def test_render_boxless_with_color(self):
        diagram = MindMapDiagram(
            roots=(MindMapNode("Both", color="#Blue", boxless=True),)
        )
        result = render_mindmap_diagram(diagram)
        # Color comes before boxless marker: *[#color]_
        assert "*[#Blue]_ Both" in result

    def test_render_multiline_node(self):
        diagram = MindMapDiagram(roots=(MindMapNode("Line 1\nLine 2"),))
        result = render_mindmap_diagram(diagram)
        assert "*:Line 1\nLine 2;" in result

    def test_render_multiline_with_color_and_boxless(self):
        """Test that multiline + color + boxless all work together."""
        diagram = MindMapDiagram(
            roots=(MindMapNode("Line 1\nLine 2", color="#Red", boxless=True),)
        )
        result = render_mindmap_diagram(diagram)
        assert "*[#Red]_:Line 1\nLine 2;" in result

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

    def test_builder_single_root(self):
        with mindmap_diagram() as d:
            with d.node("Root"):
                pass

        diagram = d.build()
        assert len(diagram.roots) == 1
        assert diagram.roots[0].text == "Root"

    def test_builder_with_children(self):
        with mindmap_diagram() as d:
            with d.node("Root") as root:
                root.leaf("Leaf 1")
                root.leaf("Leaf 2")

        diagram = d.build()
        assert len(diagram.roots) == 1
        assert len(diagram.roots[0].children) == 2
        assert diagram.roots[0].children[0].text == "Leaf 1"
        assert diagram.roots[0].children[1].text == "Leaf 2"

    def test_builder_nested_children(self):
        with mindmap_diagram() as d:
            with d.node("Root") as root:
                with root.node("Branch") as branch:
                    branch.leaf("Leaf")

        diagram = d.build()
        root = diagram.roots[0]
        assert root.text == "Root"
        assert len(root.children) == 1
        branch = root.children[0]
        assert branch.text == "Branch"
        assert len(branch.children) == 1
        assert branch.children[0].text == "Leaf"

    def test_builder_with_options(self):
        with mindmap_diagram() as d:
            with d.node("Root", color="#Red") as root:
                root.leaf("Left", side="left", boxless=True)

        diagram = d.build()
        assert diagram.roots[0].color is not None
        child = diagram.roots[0].children[0]
        assert child.side == "left"
        assert child.boxless is True

    def test_builder_root_has_no_side(self):
        """Root nodes should not have side parameter."""
        with mindmap_diagram() as d:
            with d.node("Root") as root:
                pass

        diagram = d.build()
        # Root should always have side=None
        assert diagram.roots[0].side is None

    def test_builder_with_direction(self):
        with mindmap_diagram(direction="top_to_bottom") as d:
            with d.node("Root"):
                pass

        diagram = d.build()
        assert diagram.direction == "top_to_bottom"

    def test_builder_render(self):
        with mindmap_diagram() as d:
            with d.node("Test"):
                pass

        result = d.render()
        assert "@startmindmap" in result
        assert "* Test" in result

    def test_builder_complex_tree(self):
        with mindmap_diagram() as d:
            with d.node("Central Topic") as root:
                with root.node("Branch 1") as b1:
                    b1.leaf("Leaf 1.1")
                    b1.leaf("Leaf 1.2")
                with root.node("Branch 2", side="left") as b2:
                    b2.leaf("Leaf 2.1")

        result = d.render()
        lines = result.split("\n")
        assert "* Central Topic" in lines
        assert "** Branch 1" in lines
        assert "*** Leaf 1.1" in lines
        assert "*** Leaf 1.2" in lines
        assert "-- Branch 2" in lines  # Left side uses - notation
        # Children use OrgMode notation; PlantUML places them on parent's side
        assert "*** Leaf 2.1" in lines

    def test_builder_multiroot(self):
        """Test multiple root nodes (multi-root mindmap)."""
        with mindmap_diagram() as d:
            with d.node("Root 1") as r1:
                r1.leaf("Child 1")
            with d.node("Root 2") as r2:
                r2.leaf("Child 2")

        diagram = d.build()
        assert len(diagram.roots) == 2
        assert diagram.roots[0].text == "Root 1"
        assert diagram.roots[1].text == "Root 2"


class TestMindMapDispatch:
    """Tests for render() dispatch function with MindMap."""

    def test_render_dispatch(self):
        diagram = MindMapDiagram(roots=(MindMapNode("Root"),))
        result = render(diagram)
        assert "@startmindmap" in result
        assert "* Root" in result


class TestMindMapDiagramStyle:
    """Tests for diagram style rendering."""

    def test_render_with_node_style(self):
        from plantuml_compose.primitives.common import (
            ElementStyle,
            MindMapDiagramStyle,
        )

        style = MindMapDiagramStyle(
            node=ElementStyle(background="#E3F2FD"),
        )
        diagram = MindMapDiagram(
            roots=(MindMapNode("Root"),),
            diagram_style=style,
        )
        result = render_mindmap_diagram(diagram)
        assert "<style>" in result
        assert "mindmapDiagram" in result
        assert "node" in result
        assert "BackgroundColor #E3F2FD" in result

    def test_render_with_root_node_style(self):
        from plantuml_compose.primitives.common import (
            ElementStyle,
            MindMapDiagramStyle,
        )

        style = MindMapDiagramStyle(
            root_node=ElementStyle(background="#FFA500"),
        )
        diagram = MindMapDiagram(
            roots=(MindMapNode("Root"),),
            diagram_style=style,
        )
        result = render_mindmap_diagram(diagram)
        assert "rootNode" in result
        assert "BackgroundColor #FFA500" in result

    def test_render_with_leaf_node_style(self):
        from plantuml_compose.primitives.common import (
            ElementStyle,
            MindMapDiagramStyle,
        )

        style = MindMapDiagramStyle(
            leaf_node=ElementStyle(background="#90EE90"),
        )
        diagram = MindMapDiagram(
            roots=(MindMapNode("Root"),),
            diagram_style=style,
        )
        result = render_mindmap_diagram(diagram)
        assert "leafNode" in result
        assert "BackgroundColor #90EE90" in result


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
            with d.node("Central Topic") as root:
                with root.node("Branch 1") as b1:
                    b1.leaf("Leaf 1.1")
                    b1.leaf("Leaf 1.2")
                with root.node("Branch 2") as b2:
                    b2.leaf("Leaf 2.1")

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
            with d.node("Root") as root:
                with root.node("Right 1", side="right") as r1:
                    r1.leaf("Right 1.1", side="right")
                with root.node("Left 1", side="left") as l1:
                    l1.leaf("Left 1.1", side="left")

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
            with d.node("Root", color="#Orange") as root:
                root.leaf("Green", color="#lightgreen")
                root.leaf("Blue", color="#ADD8E6")

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
            with d.node("Boxless Root", boxless=True) as root:
                root.leaf("Boxless Child", boxless=True)
                root.leaf("Normal Child")

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
            with d.node("Single line root") as root:
                root.leaf("Multi-line\nnode content")

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
            with d.node("Root") as root:
                root.leaf("Child 1")
                root.leaf("Child 2")

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
            with d.node("Root", color="#Blue", boxless=True) as root:
                root.leaf("Child", color="#Orange", boxless=True)

        puml_file = tmp_path / "mindmap_boxless_color.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_multiline_with_color_and_boxless_syntax(
        self, plantuml_check, tmp_path
    ):
        """Test multiline + color + boxless all work together."""
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with mindmap_diagram() as d:
            with d.node("Root") as root:
                root.leaf("Multi\nLine", color="#Red", boxless=True)

        puml_file = tmp_path / "mindmap_multiline_combo.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_diagram_style_syntax(self, plantuml_check, tmp_path):
        """Test that diagram styles generate valid PlantUML."""
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        from plantuml_compose.primitives.common import (
            ElementStyle,
            MindMapDiagramStyle,
        )

        style = MindMapDiagramStyle(
            node=ElementStyle(background="#E3F2FD"),
            root_node=ElementStyle(background="#FFA500"),
            leaf_node=ElementStyle(background="#90EE90"),
        )

        with mindmap_diagram(diagram_style=style) as d:
            with d.node("Root") as root:
                with root.node("Branch") as branch:
                    branch.leaf("Leaf")

        puml_file = tmp_path / "mindmap_style.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"
