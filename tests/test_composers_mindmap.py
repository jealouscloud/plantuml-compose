"""Tests for the mindmap composer."""

import subprocess

import pytest

from plantuml_compose.composers.mindmap import mindmap_diagram
from plantuml_compose.primitives.mindmap import MindMapDiagram, MindMapNode
from plantuml_compose.renderers import render


class TestMindMapComposer:

    def test_empty_diagram(self):
        d = mindmap_diagram()
        result = d.build()
        assert isinstance(result, MindMapDiagram)
        assert result.roots == ()

    def test_single_root(self):
        d = mindmap_diagram()
        n = d.nodes
        d.add(n.node("Root"))
        result = d.build()
        assert len(result.roots) == 1
        assert result.roots[0].text == "Root"

    def test_nested_tree(self):
        d = mindmap_diagram()
        n = d.nodes
        d.add(n.node("Root",
            n.node("Branch",
                n.leaf("Leaf"),
            ),
        ))
        result = d.build()
        root = result.roots[0]
        assert root.text == "Root"
        assert len(root.children) == 1
        branch = root.children[0]
        assert branch.text == "Branch"
        assert len(branch.children) == 1
        assert branch.children[0].text == "Leaf"

    def test_leaf_has_no_children(self):
        d = mindmap_diagram()
        n = d.nodes
        d.add(n.node("Root", n.leaf("Leaf")))
        result = d.build()
        leaf = result.roots[0].children[0]
        assert leaf.children == ()

    def test_color_propagation(self):
        d = mindmap_diagram()
        n = d.nodes
        d.add(n.node("Root", color="#E3F2FD"))
        result = d.build()
        assert result.roots[0].color is not None

    def test_side_propagation(self):
        d = mindmap_diagram()
        n = d.nodes
        d.add(n.node("Root",
            n.node("Right"),
            n.node("Left", side="left"),
        ))
        result = d.build()
        children = result.roots[0].children
        assert children[0].side is None
        assert children[1].side == "left"

    def test_boxless_propagation(self):
        d = mindmap_diagram()
        n = d.nodes
        d.add(n.node("Root", n.leaf("Leaf", boxless=True)))
        result = d.build()
        assert result.roots[0].children[0].boxless is True

    def test_direction(self):
        d = mindmap_diagram(direction="top_to_bottom")
        n = d.nodes
        d.add(n.node("Root"))
        result = d.build()
        assert result.direction == "top_to_bottom"

    def test_mainframe(self):
        d = mindmap_diagram(mainframe="My Map")
        n = d.nodes
        d.add(n.node("Root"))
        result = d.build()
        assert result.mainframe == "My Map"

    def test_diagram_style(self):
        d = mindmap_diagram(diagram_style={"node": {"background": "#E3F2FD"}})
        n = d.nodes
        d.add(n.node("Root"))
        result = d.build()
        assert result.diagram_style is not None

    def test_add_returns_ref(self):
        d = mindmap_diagram()
        n = d.nodes
        root = d.add(n.node("Root"))
        assert root._name == "Root"

    def test_render_produces_plantuml(self):
        d = mindmap_diagram()
        n = d.nodes
        d.add(n.node("Root", n.leaf("Child")))
        result = render(d)
        assert "@startmindmap" in result
        assert "Root" in result
        assert "Child" in result
        assert "@endmindmap" in result

    def test_render_matches_builder(self):
        """Build same diagram with old builder and new composer, compare output."""
        from plantuml_compose.builders.mindmap import (
            mindmap_diagram as builder_mindmap,
        )

        # Old builder
        with builder_mindmap() as old:
            with old.node("Root") as root:
                root.leaf("A")
                root.leaf("B")
        old_output = render(old.build())

        # New composer
        d = mindmap_diagram()
        n = d.nodes
        d.add(n.node("Root",
            n.leaf("A"),
            n.leaf("B"),
        ))
        new_output = render(d)

        assert old_output == new_output

    def test_render_nested_matches_builder(self):
        """Nested tree renders identically between builder and composer."""
        from plantuml_compose.builders.mindmap import (
            mindmap_diagram as builder_mindmap,
        )

        # Old builder
        with builder_mindmap() as old:
            with old.node("Root") as root:
                with root.node("Branch", color="#E3F2FD") as branch:
                    branch.leaf("Leaf 1")
                    branch.leaf("Leaf 2")
                root.leaf("Sibling", side="left", boxless=True)
        old_output = render(old.build())

        # New composer
        d = mindmap_diagram()
        n = d.nodes
        d.add(n.node("Root",
            n.node("Branch",
                n.leaf("Leaf 1"),
                n.leaf("Leaf 2"),
                color="#E3F2FD",
            ),
            n.leaf("Sibling", side="left", boxless=True),
        ))
        new_output = render(d)

        assert old_output == new_output


class TestMindMapPlantUMLValidation:

    @pytest.fixture
    def plantuml_check(self):
        """Check if PlantUML is available."""
        try:
            result = subprocess.run(
                ["plantuml", "-version"],
                capture_output=True, timeout=10,
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def test_simple_diagram_valid_plantuml(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = mindmap_diagram()
        n = d.nodes
        d.add(n.node("Root",
            n.node("Branch 1",
                n.leaf("Leaf A"),
                n.leaf("Leaf B"),
            ),
            n.node("Branch 2",
                n.leaf("Leaf C"),
                side="left",
            ),
        ))

        puml_file = tmp_path / "mindmap_composer.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_styled_diagram_valid_plantuml(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = mindmap_diagram(direction="top_to_bottom")
        n = d.nodes
        d.add(n.node("Infrastructure",
            n.node("Platforms",
                n.leaf("Shared Hosting"),
                n.leaf("HAVPS"),
                n.leaf("Dedicated"),
                color="#E3F2FD",
            ),
            n.node("Tools",
                n.leaf("Netbox", boxless=True),
                n.leaf("GitLab", boxless=True),
                side="left", color="#FFF3E0",
            ),
        ))

        puml_file = tmp_path / "mindmap_styled.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"
