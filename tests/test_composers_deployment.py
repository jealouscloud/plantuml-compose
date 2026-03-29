"""Tests for the deployment diagram composer."""

import subprocess

import pytest

from plantuml_compose.composers.deployment import deployment_diagram
from plantuml_compose.primitives.deployment import (
    DeploymentDiagram,
    DeploymentElement,
    Relationship,
)
from plantuml_compose.renderers import render


class TestDeploymentComposer:

    def test_empty_diagram(self):
        d = deployment_diagram()
        result = d.build()
        assert isinstance(result, DeploymentDiagram)
        assert result.elements == ()

    def test_standalone_node(self):
        d = deployment_diagram()
        el = d.elements
        d.add(el.node("Server"))
        result = d.build()
        assert len(result.elements) == 1
        elem = result.elements[0]
        assert isinstance(elem, DeploymentElement)
        assert elem.name == "Server"
        assert elem.type == "node"

    def test_nested_elements(self):
        d = deployment_diagram()
        el = d.elements
        d.add(el.node("Host",
            el.artifact("app"),
            el.database("data"),
        ))
        result = d.build()
        host = result.elements[0]
        assert len(host.elements) == 2
        assert host.elements[0].name == "app"
        assert host.elements[0].type == "artifact"
        assert host.elements[1].name == "data"
        assert host.elements[1].type == "database"

    def test_three_level_nesting(self):
        """Recursive nesting — the builder's biggest gap."""
        d = deployment_diagram()
        el = d.elements
        d.add(el.frame("Rack",
            el.node("Host",
                el.artifact("container runtime"),
                el.artifact("storage client"),
            ),
            el.storage("SAN"),
        ))
        result = d.build()
        rack = result.elements[0]
        assert rack.type == "frame"
        host = rack.elements[0]
        assert host.type == "node"
        assert len(host.elements) == 2
        assert rack.elements[1].type == "storage"

    def test_all_element_types(self):
        d = deployment_diagram()
        el = d.elements
        d.add(
            el.node("n"), el.artifact("a"), el.component("c"),
            el.database("db"), el.storage("s"), el.cloud("cl"),
            el.frame("fr"), el.folder("fo"), el.package("pk"),
            el.rectangle("r"), el.queue("q"), el.stack("st"),
            el.file("fi"), el.actor("ac"), el.interface("if"),
        )
        result = d.build()
        types = [e.type for e in result.elements]
        assert "node" in types
        assert "artifact" in types
        assert "database" in types
        assert "storage" in types
        assert "cloud" in types

    def test_child_access(self):
        d = deployment_diagram()
        el = d.elements
        rack = el.frame("Rack",
            el.node("ToR", ref="tor"),
            el.node("Host", ref="host"),
        )
        assert rack.tor._name == "ToR"
        assert rack.host._name == "Host"

    def test_connection_with_refs(self):
        d = deployment_diagram()
        el = d.elements
        c = d.connections
        rack = el.frame("Rack",
            el.node("ToR", ref="tor"),
            el.node("Host", ref="host"),
        )
        d.add(rack)
        d.connect(c.arrow(rack.tor, rack.host))
        result = d.build()
        rels = [e for e in result.elements if isinstance(e, Relationship)]
        assert len(rels) == 1
        assert rels[0].source == "tor"
        assert rels[0].target == "host"
        assert rels[0].type == "arrow"

    def test_bulk_lines(self):
        d = deployment_diagram()
        el = d.elements
        c = d.connections
        a = el.node("A", ref="a")
        b = el.node("B", ref="b")
        x = el.node("X", ref="x")
        d.add(a, b, x)
        d.connect(c.lines((a, b), (b, x)))
        result = d.build()
        rels = [e for e in result.elements if isinstance(e, Relationship)]
        assert len(rels) == 2
        assert all(r.type == "line" for r in rels)

    def test_render_produces_plantuml(self):
        d = deployment_diagram(title="Test")
        el = d.elements
        d.add(el.node("Server"))
        result = render(d)
        assert "@startuml" in result
        assert "Server" in result
        assert "@enduml" in result

    def test_render_nested_valid(self):
        """Three-level nesting renders valid PlantUML."""
        d = deployment_diagram(title="DC")
        el = d.elements
        c = d.connections
        rack = el.frame("Rack",
            el.node("ToR", ref="tor"),
            el.node("Host",
                el.artifact("app"),
                ref="host",
            ),
        )
        d.add(rack)
        d.connect(c.arrow(rack.tor, rack.host))
        result = render(d)
        assert "frame" in result
        assert "node" in result
        assert "artifact" in result


class TestDeploymentPlantUMLValidation:

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

    def test_datacenter_topology_valid(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = deployment_diagram(title="DC Topology")
        el = d.elements
        c = d.connections

        edge = el.node("Edge Router", ref="edge")
        dist = el.node("Dist Switch", ref="dist")

        rack = el.frame("HAVPS Rack",
            el.node("ToR Switch", ref="tor"),
            el.node("HAVPS Host",
                el.artifact("container runtime"),
                el.artifact("storage client"),
                ref="host",
            ),
            el.storage("Storage Node", ref="storage"),
        )

        d.add(edge, dist, rack)
        d.connect(
            c.line(edge, dist),
            c.line(dist, rack.tor),
            c.arrow(rack.tor, rack.host),
            c.arrow(rack.tor, rack.storage),
        )

        puml_file = tmp_path / "deployment_composer.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"
