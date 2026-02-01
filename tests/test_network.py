"""Tests for network diagram (nwdiag) support."""

from plantuml_compose import network_diagram, NodeRef
from plantuml_compose.primitives.network import (
    Network,
    NetworkDiagram,
    NetworkGroup,
    NetworkNode,
    PeerLink,
    StandaloneNode,
)
from plantuml_compose.renderers.network import render_network_diagram


class TestPrimitives:
    """Test network diagram primitives."""

    def test_network_node_minimal(self):
        node = NetworkNode(name="server1")
        assert node.name == "server1"
        assert node.address is None
        assert node.shape is None

    def test_network_node_full(self):
        node = NetworkNode(
            name="db01",
            address="192.168.1.100",
            shape="database",
            description="Primary Database",
            color="#CCFFCC",
        )
        assert node.name == "db01"
        assert node.address == "192.168.1.100"
        assert node.shape == "database"
        assert node.description == "Primary Database"
        assert node.color == "#CCFFCC"

    def test_network_minimal(self):
        network = Network(name="dmz")
        assert network.name == "dmz"
        assert network.nodes == ()

    def test_network_with_nodes(self):
        network = Network(
            name="internal",
            address="172.16.0.0/24",
            color="#FFFFCC",
            nodes=(
                NetworkNode(name="web01", address="172.16.0.10"),
                NetworkNode(name="web02", address="172.16.0.11"),
            ),
        )
        assert network.name == "internal"
        assert network.address == "172.16.0.0/24"
        assert len(network.nodes) == 2

    def test_standalone_node(self):
        node = StandaloneNode(
            name="internet",
            shape="cloud",
            description="Public Internet",
            color="#CCCCFF",
        )
        assert node.name == "internet"
        assert node.shape == "cloud"

    def test_peer_link(self):
        link = PeerLink(source="internet", target="router")
        assert link.source == "internet"
        assert link.target == "router"

    def test_network_group(self):
        group = NetworkGroup(
            color="#CCFFCC",
            description="Web Tier",
            nodes=("web01", "web02", "web03"),
        )
        assert group.description == "Web Tier"
        assert len(group.nodes) == 3

    def test_network_diagram(self):
        diagram = NetworkDiagram(
            title="Office Network",
            elements=(
                Network(name="dmz", nodes=(NetworkNode(name="fw01"),)),
                StandaloneNode(name="internet", shape="cloud"),
            ),
        )
        assert diagram.title == "Office Network"
        assert len(diagram.elements) == 2


class TestRenderer:
    """Test network diagram rendering."""

    def test_render_empty_diagram(self):
        diagram = NetworkDiagram()
        result = render_network_diagram(diagram)
        assert "@startuml" in result
        assert "nwdiag {" in result
        assert "}" in result
        assert "@enduml" in result

    def test_render_with_title(self):
        diagram = NetworkDiagram(title="Test Network")
        result = render_network_diagram(diagram)
        assert "title Test Network" in result

    def test_render_network_with_nodes(self):
        diagram = NetworkDiagram(
            elements=(
                Network(
                    name="dmz",
                    address="10.0.1.0/24",
                    nodes=(
                        NetworkNode(name="web01", address="10.0.1.10"),
                        NetworkNode(name="web02", address="10.0.1.11"),
                    ),
                ),
            )
        )
        result = render_network_diagram(diagram)
        assert 'network dmz {' in result
        assert 'address = "10.0.1.0/24"' in result
        assert 'web01 [address = "10.0.1.10"]' in result
        assert 'web02 [address = "10.0.1.11"]' in result

    def test_render_node_with_shape(self):
        diagram = NetworkDiagram(
            elements=(
                Network(
                    name="internal",
                    nodes=(NetworkNode(name="db01", shape="database"),),
                ),
            )
        )
        result = render_network_diagram(diagram)
        assert "db01 [shape = database]" in result

    def test_render_node_with_description(self):
        diagram = NetworkDiagram(
            elements=(
                Network(
                    name="dmz",
                    nodes=(
                        NetworkNode(name="web01", description="Primary Web Server"),
                    ),
                ),
            )
        )
        result = render_network_diagram(diagram)
        assert 'web01 [description = "Primary Web Server"]' in result

    def test_render_node_with_color(self):
        diagram = NetworkDiagram(
            elements=(
                Network(
                    name="internal",
                    nodes=(NetworkNode(name="db01", color="#CCFFCC"),),
                ),
            )
        )
        result = render_network_diagram(diagram)
        assert 'db01 [color = "#CCFFCC"]' in result

    def test_render_node_multiple_attributes(self):
        diagram = NetworkDiagram(
            elements=(
                Network(
                    name="internal",
                    nodes=(
                        NetworkNode(
                            name="db01",
                            address="172.16.0.100",
                            shape="database",
                            description="Main DB",
                        ),
                    ),
                ),
            )
        )
        result = render_network_diagram(diagram)
        # Should have multiple attributes
        assert "db01 [" in result
        assert 'address = "172.16.0.100"' in result
        assert "shape = database" in result
        assert 'description = "Main DB"' in result

    def test_render_network_with_color(self):
        diagram = NetworkDiagram(
            elements=(
                Network(name="dmz", color="#FFFFCC", nodes=()),
            )
        )
        result = render_network_diagram(diagram)
        # Color is inside the block with quotes
        assert 'color = "#FFFFCC"' in result

    def test_render_standalone_node(self):
        diagram = NetworkDiagram(
            elements=(StandaloneNode(name="internet", shape="cloud"),)
        )
        result = render_network_diagram(diagram)
        assert "internet [shape = cloud]" in result

    def test_render_peer_link(self):
        diagram = NetworkDiagram(
            elements=(
                StandaloneNode(name="internet", shape="cloud"),
                PeerLink(source="internet", target="router"),
            )
        )
        result = render_network_diagram(diagram)
        assert "internet -- router" in result

    def test_render_network_group(self):
        diagram = NetworkDiagram(
            elements=(
                NetworkGroup(
                    color="#CCFFCC",
                    description="Web Servers",
                    nodes=("web01", "web02"),
                ),
            )
        )
        result = render_network_diagram(diagram)
        assert "group {" in result
        assert 'color = "#CCFFCC"' in result
        assert 'description = "Web Servers"' in result
        assert "web01" in result
        assert "web02" in result

    def test_render_full_width_network(self):
        diagram = NetworkDiagram(
            elements=(Network(name="backbone", width="full", nodes=()),)
        )
        result = render_network_diagram(diagram)
        # Width is quoted inside the block
        assert 'width = "full";' in result


class TestBuilder:
    """Test network diagram builder."""

    def test_empty_diagram(self):
        with network_diagram() as d:
            pass
        result = d.render()
        assert "nwdiag {" in result

    def test_diagram_with_title(self):
        with network_diagram(title="My Network") as d:
            pass
        result = d.render()
        assert "title My Network" in result

    def test_network_with_nodes(self):
        with network_diagram() as d:
            with d.network("dmz", address="10.0.1.0/24") as dmz:
                dmz.node("web01", address="10.0.1.10")
                dmz.node("web02", address="10.0.1.11")

        result = d.render()
        assert "network dmz {" in result
        assert 'address = "10.0.1.0/24"' in result
        assert "web01" in result
        assert "web02" in result

    def test_node_returns_ref(self):
        with network_diagram() as d:
            with d.network("dmz") as dmz:
                ref = dmz.node("web01")
                assert isinstance(ref, NodeRef)
                assert ref.name == "web01"

    def test_standalone_node(self):
        with network_diagram() as d:
            inet = d.node("internet", shape="cloud")
            assert isinstance(inet, NodeRef)
            assert inet.name == "internet"

        result = d.render()
        assert "internet [shape = cloud]" in result

    def test_peer_link_with_refs(self):
        with network_diagram() as d:
            inet = d.node("internet", shape="cloud")
            with d.network("dmz") as dmz:
                router = dmz.node("router")
            d.link(inet, router)

        result = d.render()
        assert "internet -- router" in result

    def test_peer_link_with_strings(self):
        with network_diagram() as d:
            d.node("internet", shape="cloud")
            d.link("internet", "router")

        result = d.render()
        assert "internet -- router" in result

    def test_group(self):
        with network_diagram() as d:
            with d.network("internal") as internal:
                internal.node("web01")
                internal.node("web02")
            d.group("web01", "web02", color="#CCFFCC", description="Web Tier")

        result = d.render()
        assert "group {" in result
        assert 'color = "#CCFFCC"' in result

    def test_group_with_refs(self):
        with network_diagram() as d:
            with d.network("internal") as internal:
                w1 = internal.node("web01")
                w2 = internal.node("web02")
            d.group(w1, w2, color="#CCFFCC")

        result = d.render()
        assert "group {" in result
        assert "web01" in result
        assert "web02" in result

    def test_multi_network_shared_node(self):
        """Test node appearing on multiple networks (PlantUML feature)."""
        with network_diagram() as d:
            with d.network("dmz", address="10.0.1.0/24") as dmz:
                dmz.node("web01", address="10.0.1.10")

            with d.network("internal", address="172.16.0.0/24") as internal:
                # Same node, different address on internal network
                internal.node("web01", address="172.16.0.10")
                internal.node("db01", address="172.16.0.100", shape="database")

        result = d.render()
        # web01 should appear in both networks
        assert result.count("web01") >= 2

    def test_build_returns_diagram(self):
        with network_diagram(title="Test") as d:
            with d.network("dmz") as dmz:
                dmz.node("server1")

        diagram = d.build()
        assert isinstance(diagram, NetworkDiagram)
        assert diagram.title == "Test"
        assert len(diagram.elements) == 1


class TestValidation:
    """Test input validation."""

    def test_empty_network_name_raises(self):
        import pytest

        with pytest.raises(ValueError, match="Network name cannot be empty"):
            with network_diagram() as d:
                with d.network("") as net:
                    pass

    def test_empty_node_name_raises(self):
        import pytest

        with pytest.raises(ValueError, match="Node name cannot be empty"):
            with network_diagram() as d:
                with d.network("test") as net:
                    net.node("")

    def test_whitespace_name_raises(self):
        import pytest

        with pytest.raises(ValueError, match="Network name cannot be empty"):
            with network_diagram() as d:
                with d.network("   ") as net:
                    pass

    def test_empty_standalone_node_name_raises(self):
        import pytest

        with pytest.raises(ValueError, match="Node name cannot be empty"):
            with network_diagram() as d:
                d.node("")

    def test_empty_link_source_raises(self):
        import pytest

        with pytest.raises(ValueError, match="Source node cannot be empty"):
            with network_diagram() as d:
                d.link("", "target")

    def test_whitespace_link_source_raises(self):
        import pytest

        with pytest.raises(ValueError, match="Source node cannot be empty"):
            with network_diagram() as d:
                d.link("   ", "target")

    def test_empty_link_target_raises(self):
        import pytest

        with pytest.raises(ValueError, match="Target node cannot be empty"):
            with network_diagram() as d:
                d.link("source", "")

    def test_empty_group_raises(self):
        import pytest

        with pytest.raises(ValueError, match="Group must contain at least one node"):
            with network_diagram() as d:
                d.group()


class TestNetworkDescription:
    """Test network description feature."""

    def test_network_with_description(self):
        with network_diagram() as d:
            with d.network("dmz", description="DMZ Network") as dmz:
                dmz.node("web01")

        result = d.render()
        assert 'description = "DMZ Network"' in result

    def test_network_with_address_and_description(self):
        with network_diagram() as d:
            with d.network(
                "internal",
                address="172.16.0.0/24",
                description="Internal LAN",
            ) as internal:
                internal.node("db01", shape="database")

        result = d.render()
        assert 'address = "172.16.0.0/24"' in result
        assert 'description = "Internal LAN"' in result


class TestDiagramStyle:
    """Test CSS-style diagram styling."""

    def test_diagram_style_with_class(self):
        from plantuml_compose import NetworkDiagramStyle
        from plantuml_compose.primitives.common import ElementStyle

        with network_diagram(
            diagram_style=NetworkDiagramStyle(
                background="white",
                network=ElementStyle(background="LightYellow"),
                server=ElementStyle(background="LightGreen"),
            )
        ) as d:
            with d.network("dmz") as dmz:
                dmz.node("web01")

        result = d.render()
        assert "<style>" in result
        assert "nwdiagDiagram" in result
        assert "BackgroundColor white" in result or "background" in result.lower()

    def test_diagram_style_with_dict(self):
        with network_diagram(
            diagram_style={
                "background": "white",
                "network": {"background": "LightYellow"},
                "server": {"background": "LightGreen"},
            }
        ) as d:
            with d.network("internal") as internal:
                internal.node("db01")

        result = d.render()
        assert "<style>" in result

    def test_diagram_style_group_styling(self):
        from plantuml_compose import NetworkDiagramStyle
        from plantuml_compose.primitives.common import ElementStyle

        with network_diagram(
            diagram_style=NetworkDiagramStyle(
                group=ElementStyle(background="PaleGreen", line_color="Green"),
            )
        ) as d:
            with d.network("internal") as internal:
                internal.node("web01")
                internal.node("web02")
            d.group("web01", "web02")

        result = d.render()
        assert "<style>" in result
        assert "group" in result


class TestPlantUMLIntegration:
    """Integration tests verifying PlantUML accepts output."""

    def test_basic_network(self, tmp_path):
        """Verify PlantUML accepts basic network diagram."""
        import subprocess

        with network_diagram(title="Basic Network") as d:
            with d.network("dmz", address="10.0.1.0/24") as dmz:
                dmz.node("web01", address="10.0.1.10")
                dmz.node("web02", address="10.0.1.11")

        puml_file = tmp_path / "network.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_complex_network(self, tmp_path):
        """Verify PlantUML accepts complex network diagram."""
        import subprocess

        with network_diagram(title="Data Center") as d:
            inet = d.node("internet", shape="cloud")

            with d.network("dmz", address="10.0.1.0/24", color="#FFFFCC") as dmz:
                dmz.node("fw01", address="10.0.1.1", description="Firewall")
                dmz.node("web01", address="10.0.1.10")
                dmz.node("web02", address="10.0.1.11")

            with d.network("internal", address="172.16.0.0/24") as internal:
                internal.node("web01", address="172.16.0.10")
                internal.node("web02", address="172.16.0.11")
                internal.node("db01", address="172.16.0.100", shape="database")

            d.link(inet, "fw01")
            d.group("web01", "web02", color="#CCFFCC", description="Web Servers")

        puml_file = tmp_path / "complex_network.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_standalone_nodes_and_links(self, tmp_path):
        """Verify PlantUML accepts standalone nodes with peer links."""
        import subprocess

        with network_diagram() as d:
            inet = d.node("internet", shape="cloud")
            router = d.node("router")
            d.link(inet, router)

        puml_file = tmp_path / "standalone.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_network_description(self, tmp_path):
        """Verify PlantUML accepts network descriptions."""
        import subprocess

        with network_diagram() as d:
            with d.network(
                "dmz",
                address="10.0.1.0/24",
                description="DMZ Network",
            ) as dmz:
                dmz.node("web01", address="10.0.1.10")

        puml_file = tmp_path / "description.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_diagram_style(self, tmp_path):
        """Verify PlantUML accepts diagram styling."""
        import subprocess

        with network_diagram(
            diagram_style={
                "background": "white",
                "network": {"background": "LightYellow"},
                "server": {"background": "LightGreen"},
                "group": {"background": "PaleGreen"},
            }
        ) as d:
            with d.network("dmz", address="10.0.1.0/24") as dmz:
                dmz.node("web01", address="10.0.1.10")
                dmz.node("web02", address="10.0.1.11")
            d.group("web01", "web02", description="Web Servers")

        puml_file = tmp_path / "styled.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"
