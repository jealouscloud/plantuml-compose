"""Tests for the network diagram composer."""

import subprocess

import pytest

from plantuml_compose.composers.network import network_diagram
from plantuml_compose.primitives.network import (
    Network,
    NetworkDiagram,
    NetworkGroup,
    NetworkNode,
    StandaloneNode,
)
from plantuml_compose.renderers import render


class TestNetworkComposer:

    def test_empty_diagram(self):
        d = network_diagram()
        result = d.build()
        assert isinstance(result, NetworkDiagram)
        assert result.elements == ()

    def test_standalone_node(self):
        d = network_diagram()
        n = d.networks
        d.add(n.node("Internet", shape="cloud"))
        result = d.build()
        assert len(result.elements) == 1
        node = result.elements[0]
        assert isinstance(node, StandaloneNode)
        assert node.name == "Internet"
        assert node.shape == "cloud"

    def test_network_with_nodes(self):
        d = network_diagram()
        n = d.networks
        d.add(
            n.network("DMZ",
                n.node("web01", address="10.0.1.10"),
                n.node("web02", address="10.0.1.11"),
                address="10.0.1.0/24", color="#E3F2FD",
            ),
        )
        result = d.build()
        assert len(result.elements) == 1
        net = result.elements[0]
        assert isinstance(net, Network)
        assert net.name == "DMZ"
        assert net.address == "10.0.1.0/24"
        assert net.color == "#E3F2FD"
        assert len(net.nodes) == 2
        assert net.nodes[0].name == "web01"
        assert net.nodes[0].address == "10.0.1.10"

    def test_multi_membership(self):
        """Same node name in multiple networks creates multi-membership."""
        d = network_diagram()
        n = d.networks
        d.add(n.node("firewall", shape="node"))
        d.add(
            n.network("DMZ",
                n.node("firewall", address="10.0.1.1"),
                n.node("web01", address="10.0.1.10"),
                address="10.0.1.0/24",
            ),
            n.network("Internal",
                n.node("firewall", address="10.0.2.1"),
                n.node("db01", address="10.0.2.10"),
                address="10.0.2.0/24",
            ),
        )
        result = d.build()
        # One standalone + two networks
        assert len(result.elements) == 3
        assert isinstance(result.elements[0], StandaloneNode)
        assert isinstance(result.elements[1], Network)
        assert isinstance(result.elements[2], Network)
        # firewall appears in both networks
        dmz = result.elements[1]
        internal = result.elements[2]
        dmz_names = [node.name for node in dmz.nodes]
        internal_names = [node.name for node in internal.nodes]
        assert "firewall" in dmz_names
        assert "firewall" in internal_names

    def test_group(self):
        d = network_diagram()
        n = d.networks
        d.add(n.group("web01", "web02", color="#CCFFCC", description="Web Servers"))
        result = d.build()
        groups = [e for e in result.elements if isinstance(e, NetworkGroup)]
        assert len(groups) == 1
        assert groups[0].nodes == ("web01", "web02")
        assert groups[0].color == "#CCFFCC"
        assert groups[0].description == "Web Servers"

    def test_node_with_description(self):
        d = network_diagram()
        n = d.networks
        d.add(
            n.network("SL1",
                n.node("shared", address="203.0.113.0/26", description="Shared Hosting"),
                address="Public IP",
            ),
        )
        result = d.build()
        net = result.elements[0]
        assert isinstance(net, Network)
        assert net.nodes[0].description == "Shared Hosting"

    def test_title(self):
        d = network_diagram(title="Security Levels")
        result = d.build()
        assert result.title == "Security Levels"

    def test_render_produces_plantuml(self):
        d = network_diagram(title="Test")
        n = d.networks
        d.add(n.node("Internet", shape="cloud"))
        d.add(
            n.network("DMZ",
                n.node("Internet"),
                n.node("web01", address="10.0.1.10"),
                address="10.0.1.0/24",
            ),
        )
        result = render(d)
        assert "@startnwdiag" in result
        assert "Internet" in result
        assert "@endnwdiag" in result

class TestNetworkComposerExtended:

    def test_standalone_node_address(self):
        d = network_diagram()
        n = d.networks
        d.add(n.node("srv", address="10.0.0.1"))
        result = d.build()
        node = result.elements[0]
        assert isinstance(node, StandaloneNode)
        assert node.address == "10.0.0.1"
        output = render(d)
        assert "10.0.0.1" in output

    def test_anonymous_network(self):
        d = network_diagram()
        n = d.networks
        d.add(n.network(None, n.node("srv")))
        result = d.build()
        net = result.elements[0]
        assert isinstance(net, Network)
        assert net.name == ""
        output = render(d)
        assert "network {" in output

    def test_diagram_style(self):
        d = network_diagram(diagram_style={"network": {"background": "lightblue"}})
        n = d.networks
        d.add(n.node("srv"))
        output = render(d)
        assert "<style>" in output


class TestNetworkPlantUMLValidation:

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

    def test_plantuml_validation(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = network_diagram(title="Security Levels")
        n = d.networks

        d.add(n.node("Internet", shape="cloud"))

        d.add(
            n.network("SL1",
                n.node("Internet"),
                n.node("shared", address="203.0.113.0/26", description="Shared Hosting"),
                n.node("havps", address="203.0.113.64/26", description="HAVPS"),
                address="Public IP", color="#E3F2FD",
            ),
            n.network("SL2",
                n.node("Internet"),
                n.node("firewall", address="Public NAT", description="HW Firewall"),
                address="Public IP", color="#E8F5E9",
            ),
        )

        puml_file = tmp_path / "network_composer.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"


class TestNetworkNewlineEscaping:
    """Verify that newlines in nwdiag descriptions are escaped properly.

    Raw newlines inside quoted nwdiag attributes produce syntax errors.
    The renderer must escape them. Both \\n and %n() are valid in PlantUML;
    we use \\n to match the convention used by other renderers.
    """

    def test_raw_newline_in_node_description_is_invalid(self, tmp_path):
        """Prove that a raw newline inside a description breaks nwdiag."""
        puml = (
            '@startnwdiag\n'
            'nwdiag {\n'
            '  network lan {\n'
            '    srv [description = "line1\nline2"];\n'
            '  }\n'
            '}\n'
            '@endnwdiag'
        )
        puml_file = tmp_path / "raw_newline.puml"
        puml_file.write_text(puml)
        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode != 0

    def test_escaped_newline_in_node_description_is_valid(self, tmp_path):
        """Prove that \\n in a description is accepted by nwdiag."""
        puml = (
            '@startnwdiag\n'
            'nwdiag {\n'
            '  network lan {\n'
            '    srv [description = "line1\\nline2"];\n'
            '  }\n'
            '}\n'
            '@endnwdiag'
        )
        puml_file = tmp_path / "escaped_newline.puml"
        puml_file.write_text(puml)
        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_node_description_newline_escaped_in_render(self):
        """The renderer must escape newlines in network node descriptions."""
        d = network_diagram()
        n = d.networks
        d.add(n.network("lan", n.node("srv", description="line1\nline2")))
        output = render(d)
        assert r"line1\nline2" in output
        assert "line1\nline2" not in output.replace(r"\n", "")

    def test_standalone_node_description_newline_escaped(self):
        """The renderer must escape newlines in standalone node descriptions."""
        d = network_diagram()
        n = d.networks
        d.add(n.node("srv", description="line1\nline2"))
        output = render(d)
        assert r"line1\nline2" in output

    def test_network_description_newline_escaped(self):
        """The renderer must escape newlines in network descriptions."""
        d = network_diagram()
        n = d.networks
        d.add(n.network("lan", n.node("srv"), description="net line1\nnet line2"))
        output = render(d)
        assert r"net line1\nnet line2" in output

    def test_group_description_newline_escaped(self):
        """The renderer must escape newlines in group descriptions."""
        d = network_diagram()
        n = d.networks
        d.add(
            n.network("lan", n.node("a"), n.node("b")),
            n.group("a", "b", description="grp1\ngrp2"),
        )
        output = render(d)
        assert r"grp1\ngrp2" in output

    def test_rendered_multiline_description_valid_plantuml(self, tmp_path):
        """End-to-end: rendered diagram with newlines passes plantuml check."""
        d = network_diagram()
        n = d.networks
        d.add(
            n.network("lan",
                n.node("srv", description="dnsmasq\nFastAPI"),
            ),
        )
        puml_file = tmp_path / "multiline_desc.puml"
        puml_file.write_text(render(d))
        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"


class TestNetworkNameValidation:
    """nwdiag identifiers don't support spaces or special characters.

    The composer must reject invalid names at build time rather than
    producing broken PlantUML output.
    """

    def test_network_name_with_space_rejected(self):
        d = network_diagram()
        n = d.networks
        d.add(n.network("Datacenter L2", n.node("srv")))
        with pytest.raises(ValueError, match="nwdiag network name"):
            render(d)

    def test_node_name_with_space_rejected(self):
        d = network_diagram()
        n = d.networks
        d.add(n.network("lan", n.node("my server")))
        with pytest.raises(ValueError, match="nwdiag node name"):
            render(d)

    def test_standalone_node_name_with_space_rejected(self):
        d = network_diagram()
        n = d.networks
        d.add(n.node("my server"))
        with pytest.raises(ValueError, match="nwdiag node name"):
            render(d)

    def test_valid_names_accepted(self):
        """Underscores, hyphens, dots are fine in nwdiag identifiers."""
        d = network_diagram()
        n = d.networks
        d.add(n.network("dc_l2", n.node("srv-01"), n.node("web.prod")))
        output = render(d)
        assert "dc_l2" in output
        assert "srv-01" in output
        assert "web.prod" in output

    def test_anonymous_network_accepted(self):
        """name=None networks should not be validated."""
        d = network_diagram()
        n = d.networks
        d.add(n.network(None, n.node("srv")))
        output = render(d)
        assert "srv" in output
