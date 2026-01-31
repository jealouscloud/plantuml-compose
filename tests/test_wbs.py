"""Tests for Work Breakdown Structure (WBS) diagram type."""

import subprocess

import pytest

from plantuml_compose.builders.wbs import wbs_diagram
from plantuml_compose.primitives.common import Color
from plantuml_compose.primitives.wbs import WBSArrow, WBSDiagram, WBSNode
from plantuml_compose.renderers import render
from plantuml_compose.renderers.wbs import render_wbs_diagram


class TestWBSNode:
    """Tests for WBSNode primitive."""

    def test_basic_node(self):
        node = WBSNode(text="Task")
        assert node.text == "Task"
        assert node.children == ()
        assert node.side is None
        assert node.alias is None
        assert node.color is None
        assert node.boxless is False

    def test_node_with_children(self):
        child = WBSNode(text="Subtask")
        parent = WBSNode(text="Task", children=(child,))
        assert len(parent.children) == 1
        assert parent.children[0].text == "Subtask"

    def test_node_with_all_options(self):
        node = WBSNode(
            text="Task",
            children=(),
            side="left",
            alias="t1",
            color="#Orange",
            boxless=True,
        )
        assert node.side == "left"
        assert node.alias == "t1"
        assert node.color == "#Orange"
        assert node.boxless is True


class TestWBSDiagram:
    """Tests for WBSDiagram primitive."""

    def test_empty_diagram(self):
        diagram = WBSDiagram()
        assert diagram.roots == ()
        assert diagram.arrows == ()
        assert diagram.direction is None
        assert diagram.diagram_style is None

    def test_diagram_with_roots(self):
        root = WBSNode("Project")
        diagram = WBSDiagram(roots=(root,))
        assert len(diagram.roots) == 1

    def test_diagram_with_arrows(self):
        arrow = WBSArrow(from_alias="a", to_alias="b")
        diagram = WBSDiagram(arrows=(arrow,))
        assert len(diagram.arrows) == 1
        assert diagram.arrows[0].from_alias == "a"


class TestWBSRenderer:
    """Tests for WBS rendering."""

    def test_render_empty_diagram(self):
        diagram = WBSDiagram()
        result = render_wbs_diagram(diagram)
        assert result == "@startwbs\n@endwbs"

    def test_render_single_node(self):
        diagram = WBSDiagram(roots=(WBSNode("Project"),))
        result = render_wbs_diagram(diagram)
        assert "@startwbs" in result
        assert "* Project" in result
        assert "@endwbs" in result

    def test_render_tree_structure(self):
        diagram = WBSDiagram(
            roots=(
                WBSNode(
                    "Project",
                    children=(
                        WBSNode(
                            "Phase 1",
                            children=(
                                WBSNode("Task 1.1"),
                                WBSNode("Task 1.2"),
                            ),
                        ),
                        WBSNode("Phase 2"),
                    ),
                ),
            )
        )
        result = render_wbs_diagram(diagram)
        lines = result.split("\n")
        assert "* Project" in lines
        assert "** Phase 1" in lines
        assert "*** Task 1.1" in lines
        assert "*** Task 1.2" in lines
        assert "** Phase 2" in lines

    def test_render_left_direction(self):
        """WBS uses direction markers after depth: ***<"""
        diagram = WBSDiagram(
            roots=(
                WBSNode(
                    "Root",
                    children=(WBSNode("Left", side="left"),),
                ),
            )
        )
        result = render_wbs_diagram(diagram)
        assert "**< Left" in result

    def test_render_right_direction(self):
        """WBS uses direction markers after depth: ***>"""
        diagram = WBSDiagram(
            roots=(
                WBSNode(
                    "Root",
                    children=(WBSNode("Right", side="right"),),
                ),
            )
        )
        result = render_wbs_diagram(diagram)
        assert "**> Right" in result

    def test_render_inherited_side(self):
        """Children inherit parent's side notation."""
        diagram = WBSDiagram(
            roots=(
                WBSNode(
                    "Root",
                    children=(
                        WBSNode(
                            "Left Branch",
                            side="left",
                            children=(WBSNode("Leaf"),),
                        ),
                    ),
                ),
            )
        )
        result = render_wbs_diagram(diagram)
        assert "**< Left Branch" in result
        assert "***< Leaf" in result  # Inherits left side

    def test_render_colored_node(self):
        diagram = WBSDiagram(roots=(WBSNode("Colored", color="#Orange"),))
        result = render_wbs_diagram(diagram)
        assert "*[#Orange] Colored" in result

    def test_render_boxless_node(self):
        diagram = WBSDiagram(roots=(WBSNode("Boxless", boxless=True),))
        result = render_wbs_diagram(diagram)
        assert "*_ Boxless" in result

    def test_render_aliased_node(self):
        diagram = WBSDiagram(roots=(WBSNode("Task", alias="t1"),))
        result = render_wbs_diagram(diagram)
        assert '* "Task" as t1' in result

    def test_render_arrows(self):
        diagram = WBSDiagram(
            roots=(
                WBSNode(
                    "Root",
                    children=(
                        WBSNode("A", alias="a"),
                        WBSNode("B", alias="b"),
                    ),
                ),
            ),
            arrows=(WBSArrow(from_alias="a", to_alias="b"),),
        )
        result = render_wbs_diagram(diagram)
        assert "a -> b" in result

    def test_render_direction_ignored(self):
        """WBS does not support diagram-wide direction; field is ignored."""
        diagram = WBSDiagram(direction="top_to_bottom")
        result = render_wbs_diagram(diagram)
        # Direction should NOT appear - WBS doesn't support it
        assert "direction" not in result

    def test_render_combined_color_boxless_direction(self):
        """Test combined color, boxless, and direction markers."""
        diagram = WBSDiagram(
            roots=(
                WBSNode(
                    "Root",
                    children=(
                        WBSNode("Styled", side="left", color="#Orange", boxless=True),
                    ),
                ),
            )
        )
        result = render_wbs_diagram(diagram)
        # Format: **_<[#color] text (boxless before direction)
        assert "**_<[#Orange] Styled" in result

    def test_render_diagram_style(self):
        """Test CSS-style diagram styling."""
        from plantuml_compose.primitives.common import ElementStyle
        from plantuml_compose.primitives.wbs import WBSDiagramStyle

        style = WBSDiagramStyle(
            background="#EEEEEE",
            node=ElementStyle(background="#LightBlue"),  # Erroneous # on named color
        )
        diagram = WBSDiagram(
            roots=(WBSNode("Root"),),
            diagram_style=style,
        )
        result = render_wbs_diagram(diagram)
        assert "<style>" in result
        assert "wbsDiagram" in result
        assert "BackgroundColor #EEEEEE" in result  # Hex color keeps #
        assert "node {" in result
        assert "BackgroundColor LightBlue" in result  # Named color, # stripped
        assert "</style>" in result


class TestWBSBuilder:
    """Tests for WBS builder."""

    def test_builder_single_root(self):
        with wbs_diagram() as d:
            with d.node("Project"):
                pass

        diagram = d.build()
        assert len(diagram.roots) == 1
        assert diagram.roots[0].text == "Project"

    def test_builder_with_children(self):
        with wbs_diagram() as d:
            with d.node("Project") as proj:
                proj.leaf("Task 1")
                proj.leaf("Task 2")

        diagram = d.build()
        assert len(diagram.roots) == 1
        assert len(diagram.roots[0].children) == 2

    def test_builder_nested_children(self):
        with wbs_diagram() as d:
            with d.node("Project") as proj:
                with proj.node("Phase 1") as p1:
                    p1.leaf("Task 1.1")

        diagram = d.build()
        root = diagram.roots[0]
        assert root.text == "Project"
        phase = root.children[0]
        assert phase.text == "Phase 1"
        assert phase.children[0].text == "Task 1.1"

    def test_builder_with_arrows(self):
        with wbs_diagram() as d:
            with d.node("Root") as root:
                root.leaf("A", alias="a")
                root.leaf("B", alias="b")
            d.arrow("a", "b")

        diagram = d.build()
        assert len(diagram.arrows) == 1
        assert diagram.arrows[0].from_alias == "a"
        assert diagram.arrows[0].to_alias == "b"

    def test_builder_with_options(self):
        with wbs_diagram() as d:
            with d.node("Root", color="#Red") as root:
                root.leaf("Left", side="left", boxless=True, alias="l1")

        diagram = d.build()
        assert diagram.roots[0].color is not None
        child = diagram.roots[0].children[0]
        assert child.side == "left"
        assert child.boxless is True
        assert child.alias == "l1"

    def test_builder_render(self):
        with wbs_diagram() as d:
            with d.node("Test"):
                pass

        result = d.render()
        assert "@startwbs" in result
        assert "* Test" in result


class TestWBSDispatch:
    """Tests for render() dispatch function with WBS."""

    def test_render_dispatch(self):
        diagram = WBSDiagram(roots=(WBSNode("Root"),))
        result = render(diagram)
        assert "@startwbs" in result
        assert "* Root" in result


class TestWBSPlantUMLIntegration:
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

    def test_basic_wbs_syntax(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with wbs_diagram() as d:
            with d.node("Project") as proj:
                with proj.node("Phase 1") as p1:
                    p1.leaf("Task 1.1")
                    p1.leaf("Task 1.2")
                with proj.node("Phase 2") as p2:
                    p2.leaf("Task 2.1")

        puml_file = tmp_path / "wbs.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_direction_markers_syntax(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with wbs_diagram() as d:
            with d.node("Root") as root:
                with root.node("Left", side="left") as left:
                    left.leaf("Left Child")
                with root.node("Right", side="right") as right:
                    right.leaf("Right Child")

        puml_file = tmp_path / "wbs_direction.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_arrows_syntax(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with wbs_diagram() as d:
            with d.node("Root") as root:
                root.leaf("A", alias="a")
                root.leaf("B", alias="b")
            d.arrow("a", "b")

        puml_file = tmp_path / "wbs_arrows.puml"
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

        with wbs_diagram() as d:
            with d.node("Root", color="#Orange") as root:
                root.leaf("Green", color="#lightgreen")

        puml_file = tmp_path / "wbs_colors.puml"
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

        with wbs_diagram() as d:
            with d.node("Root", boxless=True) as root:
                root.leaf("Child", boxless=True)

        puml_file = tmp_path / "wbs_boxless.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_combined_color_boxless_direction_syntax(self, plantuml_check, tmp_path):
        """Test combined color, boxless, and direction in PlantUML."""
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with wbs_diagram() as d:
            with d.node("Root") as root:
                root.leaf("Styled", side="left", color="#Orange", boxless=True)

        puml_file = tmp_path / "wbs_combined.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_diagram_style_syntax(self, plantuml_check, tmp_path):
        """Test CSS-style diagram styling in PlantUML."""
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        from plantuml_compose.primitives.common import ElementStyle
        from plantuml_compose.primitives.wbs import WBSDiagramStyle

        style = WBSDiagramStyle(
            background="#EEEEEE",
            node=ElementStyle(background="#LightBlue", round_corner=10),
            root_node=ElementStyle(background="#Orange"),
        )
        with wbs_diagram(diagram_style=style) as d:
            with d.node("Project") as proj:
                proj.leaf("Task 1")
                proj.leaf("Task 2")

        puml_file = tmp_path / "wbs_style.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"
