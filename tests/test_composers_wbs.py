"""Tests for the WBS diagram composer."""

import subprocess

import pytest

from plantuml_compose.composers.wbs import wbs_diagram
from plantuml_compose.primitives.wbs import WBSArrow, WBSDiagram, WBSNode
from plantuml_compose.renderers import render


class TestWBSComposer:

    def test_empty_diagram(self):
        d = wbs_diagram()
        result = d.build()
        assert isinstance(result, WBSDiagram)
        assert result.roots == ()
        assert result.arrows == ()

    def test_single_root(self):
        d = wbs_diagram()
        n = d.nodes
        d.add(n.node("Project"))
        result = d.build()
        assert len(result.roots) == 1
        assert result.roots[0].text == "Project"

    def test_nested_tree(self):
        d = wbs_diagram()
        n = d.nodes
        d.add(n.node("Root",
            n.node("Branch",
                n.leaf("Leaf"),
            ),
        ))
        result = d.build()
        root = result.roots[0]
        assert root.text == "Root"
        branch = root.children[0]
        assert branch.text == "Branch"
        leaf = branch.children[0]
        assert leaf.text == "Leaf"

    def test_nodes_without_arrows_have_no_alias(self):
        """Without arrows, nodes don't need aliases."""
        d = wbs_diagram()
        n = d.nodes
        d.add(n.node("Root", n.leaf("Child Node")))
        result = d.build()
        assert result.roots[0].alias is None

    def test_nodes_with_arrows_get_aliases(self):
        """When arrows exist, all nodes get alias= for resolution."""
        d = wbs_diagram()
        n = d.nodes
        c = d.connections
        a = n.leaf("Task A")
        b = n.leaf("Task B")
        d.add(n.node("Root", a, b))
        d.connect(c.arrow(a, b))
        result = d.build()
        root = result.roots[0]
        assert root.alias is not None
        assert root.children[0].alias == "Task_A"
        assert root.children[1].alias == "Task_B"

    def test_explicit_ref_becomes_alias(self):
        d = wbs_diagram()
        n = d.nodes
        d.add(n.leaf("Some Long Name", ref="sln"))
        result = d.build()
        assert result.roots[0].alias == "sln"

    def test_color_propagation(self):
        d = wbs_diagram()
        n = d.nodes
        d.add(n.node("Root",
            n.leaf("Colored"),
            color="#E3F2FD",
        ))
        result = d.build()
        assert result.roots[0].color is not None

    def test_side_propagation(self):
        d = wbs_diagram()
        n = d.nodes
        d.add(n.node("Root",
            n.leaf("Left", side="left"),
        ))
        result = d.build()
        assert result.roots[0].children[0].side == "left"

    def test_arrow_between_refs(self):
        """Capture at construction, wire via d.connect()."""
        d = wbs_diagram()
        n = d.nodes
        c = d.connections

        a = n.leaf("Task A")
        b = n.leaf("Task B")

        d.add(n.node("Project", a, b))
        d.connect(c.arrow(a, b))

        result = d.build()
        assert len(result.arrows) == 1
        arrow = result.arrows[0]
        assert arrow.from_alias == a._ref
        assert arrow.to_alias == b._ref

    def test_multiple_arrows(self):
        d = wbs_diagram()
        n = d.nodes
        c = d.connections

        a = n.leaf("A")
        b = n.leaf("B")
        x = n.leaf("X")

        d.add(n.node("Root", a, b, x))
        d.connect(c.arrow(a, b), c.arrow(b, x))

        result = d.build()
        assert len(result.arrows) == 2

    def test_bulk_arrows(self):
        d = wbs_diagram()
        n = d.nodes
        c = d.connections

        a = n.leaf("A")
        b = n.leaf("B")
        x = n.leaf("X")

        d.add(n.node("Root", a, b, x))
        d.connect(c.arrows((a, b), (b, x)))

        result = d.build()
        assert len(result.arrows) == 2

    def test_diagram_style(self):
        d = wbs_diagram(diagram_style={"arrow": {"line_color": "#999"}})
        n = d.nodes
        d.add(n.node("Root"))
        result = d.build()
        assert result.diagram_style is not None

    def test_render_produces_plantuml(self):
        d = wbs_diagram()
        n = d.nodes
        d.add(n.node("Root", n.leaf("A"), n.leaf("B")))
        result = render(d)
        assert "@startwbs" in result
        assert "Root" in result
        assert "@endwbs" in result

    def test_render_with_arrows(self):
        d = wbs_diagram()
        n = d.nodes
        c = d.connections
        a = n.leaf("Task A")
        b = n.leaf("Task B")
        d.add(n.node("Root", a, b))
        d.connect(c.arrow(a, b))
        result = render(d)
        assert "Task_A" in result or "Task A" in result
        assert "-->" in result or "->" in result

    def test_render_matches_builder(self):
        """Compare simple tree output with old builder."""
        from plantuml_compose.builders.wbs import wbs_diagram as builder_wbs

        # Old builder
        with builder_wbs() as old:
            with old.node("Root") as root:
                root.leaf("A")
                root.leaf("B")
        old_output = render(old.build())

        # New composer
        d = wbs_diagram()
        n = d.nodes
        d.add(n.node("Root",
            n.leaf("A"),
            n.leaf("B"),
        ))
        new_output = render(d)

        assert old_output == new_output


class TestWBSPlantUMLValidation:

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

    def test_tree_with_arrows_valid_plantuml(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = wbs_diagram()
        n = d.nodes
        c = d.connections

        cabling = n.leaf("Cabling")
        edge = n.leaf("Edge routers")
        tor = n.leaf("ToR switches")

        d.add(n.node("DC Buildout",
            n.node("Physical", cabling),
            n.node("Network", edge, tor),
        ))
        d.connect(c.arrow(cabling, edge), c.arrow(edge, tor))

        puml_file = tmp_path / "wbs_composer.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"
