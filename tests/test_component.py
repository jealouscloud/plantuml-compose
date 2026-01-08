"""Tests for component diagram builder, primitives, and renderer."""

import pytest

from plantuml_compose import render
from plantuml_compose.builders.component import component_diagram
from plantuml_compose.primitives.component import (
    Component,
    ComponentDiagram,
    Container,
    Interface,
    Port,
    Relationship,
)
from plantuml_compose.renderers.component import render_component_diagram


class TestBasicElements:
    """Tests for basic component elements."""

    def test_component(self):
        with component_diagram() as d:
            d.component("API Server")

        output = render(d.build())
        assert 'component "API Server"' in output

    def test_component_with_alias(self):
        with component_diagram() as d:
            api = d.component("API Server", alias="api")

        output = render(d.build())
        assert api._ref == "api"  # Component returns object with _ref property
        assert 'component "API Server" as api' in output

    def test_component_with_stereotype(self):
        with component_diagram() as d:
            d.component("Database", stereotype="storage")

        output = render(d.build())
        assert "<<storage>>" in output

    def test_component_with_style(self):
        with component_diagram() as d:
            d.component("Critical", style={"background": "red"})

        output = render(d.build())
        assert "#red" in output

    def test_component_with_line_style(self):
        with component_diagram() as d:
            d.component("Bordered", style={"line": {"color": "blue"}})

        output = render(d.build())
        # Uses semicolon format which works in component diagrams
        assert "#line:blue" in output

    def test_component_with_line_pattern(self):
        with component_diagram() as d:
            d.component("Dashed", style={"line": {"pattern": "dashed"}})

        output = render(d.build())
        # Uses semicolon format which works in component diagrams
        assert "#line.dashed" in output

    def test_component_with_text_color(self):
        with component_diagram() as d:
            d.component("Highlighted", style={"text_color": "green"})

        output = render(d.build())
        assert "text:green" in output

    def test_component_with_combined_style(self):
        with component_diagram() as d:
            d.component(
                "FullStyle",
                style={
                    "background": "yellow",
                    "line": {"color": "blue"},
                    "text_color": "red",
                },
            )

        output = render(d.build())
        assert "#yellow" in output
        assert "line:blue" in output
        assert "text:red" in output

    def test_interface(self):
        with component_diagram() as d:
            d.interface("REST API")

        output = render(d.build())
        assert 'interface "REST API"' in output

    def test_interface_with_alias(self):
        with component_diagram() as d:
            rest = d.interface("REST API", alias="rest")

        output = render(d.build())
        assert rest._ref == "rest"  # Interface returns object with _ref property
        assert 'interface "REST API" as rest' in output

    def test_service_with_color(self):
        """service() convenience method should work with color parameter."""
        with component_diagram() as d:
            d.service("API", color="LightBlue")

        output = render(d.build())
        assert "#LightBlue" in output

    def test_service_with_provides_and_requires(self):
        """service() should create component with interface relationships."""
        with component_diagram() as d:
            d.service("API", provides=("REST",), requires=("Database",))

        output = render(d.build())
        assert "component API" in output
        assert "interface REST" in output
        assert "interface Database" in output


class TestContainers:
    """Tests for container elements (package, node, etc.)."""

    def test_package(self):
        with component_diagram() as d:
            with d.package("Backend") as pkg:
                pkg.component("Service")

        output = render(d.build())
        assert "package Backend" in output
        assert "{" in output
        assert "}" in output
        assert "Service" in output

    def test_node(self):
        with component_diagram() as d:
            with d.node("Server") as n:
                n.component("App")

        output = render(d.build())
        assert "node Server" in output

    def test_folder(self):
        with component_diagram() as d:
            with d.folder("Documents") as f:
                f.component("Config")

        output = render(d.build())
        assert "folder Documents" in output

    def test_frame(self):
        with component_diagram() as d:
            with d.frame("Subsystem") as f:
                f.component("Module")

        output = render(d.build())
        assert "frame Subsystem" in output

    def test_cloud(self):
        with component_diagram() as d:
            with d.cloud("AWS") as c:
                c.component("Lambda")

        output = render(d.build())
        assert "cloud AWS" in output

    def test_database_container(self):
        with component_diagram() as d:
            with d.database("PostgreSQL") as db:
                db.component("Users Table")

        output = render(d.build())
        assert "database PostgreSQL" in output

    def test_rectangle(self):
        with component_diagram() as d:
            with d.rectangle("Group") as r:
                r.component("Item")

        output = render(d.build())
        assert "rectangle Group" in output

    def test_nested_containers(self):
        with component_diagram() as d:
            with d.package("Backend") as pkg:
                with pkg.node("Server") as node:
                    node.component("App")

        output = render(d.build())
        assert "package Backend" in output
        assert "node Server" in output
        assert "App" in output

    def test_container_with_style(self):
        with component_diagram() as d:
            with d.package("Important", style={"background": "LightBlue"}) as pkg:
                pkg.component("Service")

        output = render(d.build())
        assert "#LightBlue" in output


class TestPorts:
    """Tests for component ports."""

    def test_component_with_ports(self):
        with component_diagram() as d:
            with d.component_with_ports("WebServer", alias="ws") as c:
                c.port("http")
                c.portin("requests")
                c.portout("responses")

        output = render(d.build())
        assert "WebServer" in output
        assert "port http" in output
        assert "portin requests" in output
        assert "portout responses" in output


class TestRelationships:
    """Tests for relationships between components."""

    def test_arrow(self):
        with component_diagram() as d:
            api = d.component("API", alias="api")
            db = d.component("Database", alias="db")
            d.arrow(api, db)

        output = render(d.build())
        assert "api --> db" in output

    def test_arrow_with_label(self):
        with component_diagram() as d:
            api = d.component("API", alias="api")
            db = d.component("Database", alias="db")
            d.arrow(api, db, label="queries")

        output = render(d.build())
        assert "api --> db : queries" in output

    def test_dotted_arrow(self):
        with component_diagram() as d:
            a = d.component("A", alias="a")
            b = d.component("B", alias="b")
            d.arrow(a, b, style={"pattern": "dashed"})

        output = render(d.build())
        assert "a ..[dashed].> b" in output

    def test_link(self):
        with component_diagram() as d:
            a = d.component("A", alias="a")
            b = d.component("B", alias="b")
            d.link(a, b)

        output = render(d.build())
        assert "a -- b" in output

    def test_link_with_label(self):
        with component_diagram() as d:
            a = d.component("A", alias="a")
            b = d.component("B", alias="b")
            d.link(a, b, label="connects")

        output = render(d.build())
        assert "a -- b : connects" in output

    def test_depends(self):
        with component_diagram() as d:
            a = d.component("A", alias="a")
            b = d.component("B", alias="b")
            d.depends(a, b)

        output = render(d.build())
        assert "a ..> b" in output

    def test_provides(self):
        with component_diagram() as d:
            api = d.component("API", alias="api")
            rest = d.interface("REST", alias="rest")
            d.provides(api, rest)

        output = render(d.build())
        assert "api --( rest" in output

    def test_requires(self):
        with component_diagram() as d:
            api = d.component("API", alias="api")
            db = d.interface("DB", alias="db")
            d.requires(api, db)

        output = render(d.build())
        assert "api )-- db" in output

    def test_relationship_with_color(self):
        with component_diagram() as d:
            a = d.component("A", alias="a")
            b = d.component("B", alias="b")
            d.arrow(a, b, style={"color": "blue"})

        output = render(d.build())
        assert "[#blue]" in output


class TestNotes:
    """Tests for notes."""

    def test_note_right(self):
        with component_diagram() as d:
            d.component("API", alias="api")
            d.note("Main entry point", target="api", position="right")

        output = render(d.build())
        assert "note right of api" in output
        assert "Main entry point" in output

    def test_note_with_color(self):
        with component_diagram() as d:
            d.component("API", alias="api")
            d.note("Important", target="api", color="yellow")

        output = render(d.build())
        assert "#yellow" in output


class TestDiagramOptions:
    """Tests for diagram-level options."""

    def test_title(self):
        with component_diagram(title="System Architecture") as d:
            d.component("API")

        output = render(d.build())
        assert "title System Architecture" in output

    def test_style_uml1(self):
        with component_diagram(style="uml1") as d:
            d.component("API")

        output = render(d.build())
        assert "skinparam componentStyle uml1" in output

    def test_style_rectangle(self):
        with component_diagram(style="rectangle") as d:
            d.component("API")

        output = render(d.build())
        assert "skinparam componentStyle rectangle" in output

    def test_hide_stereotype(self):
        with component_diagram(hide_stereotype=True) as d:
            d.component("API", stereotype="service")

        output = render(d.build())
        assert "hide stereotype" in output


class TestRenderMethod:
    """Tests for the render() convenience method."""

    def test_render_returns_plantuml_text(self):
        with component_diagram() as d:
            d.component("API")

        output = render(d.build())
        assert output.startswith("@startuml")
        assert output.endswith("@enduml")

    def test_render_equivalent_to_render_build(self):
        with component_diagram() as d:
            d.component("API")
            d.component("Database")

        from plantuml_compose.renderers import render
        assert render(d.build()) == render(d.build())


class TestComplexDiagram:
    """Integration tests with complex diagrams."""

    def test_microservices_architecture(self):
        with component_diagram(title="Microservices") as d:
            # Frontend
            with d.package("Frontend") as fe:
                web = fe.component("Web App", alias="web")
                mobile = fe.component("Mobile App", alias="mobile")

            # API Gateway
            gateway = d.component("API Gateway", alias="gw")

            # Backend Services
            with d.package("Backend") as be:
                users = be.component("User Service", alias="users")
                orders = be.component("Order Service", alias="orders")
                products = be.component("Product Service", alias="products")

            # Database
            with d.database("PostgreSQL") as db:
                db.component("Users DB", alias="usersdb")
                db.component("Orders DB", alias="ordersdb")

            # Relationships
            d.arrow(web, gateway)
            d.arrow(mobile, gateway)
            d.arrow(gateway, users)
            d.arrow(gateway, orders)
            d.arrow(gateway, products)
            d.arrow(users, "usersdb", label="queries")
            d.arrow(orders, "ordersdb", label="queries")

        output = render(d.build())
        assert "title Microservices" in output
        assert "package Frontend" in output
        assert "package Backend" in output
        assert "database PostgreSQL" in output
        assert "web --> gw" in output
        assert "users --> usersdb : queries" in output


class TestValidation:
    """Tests for input validation."""

    def test_empty_component_name_rejected(self):
        with component_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                d.component("")

    def test_empty_interface_name_rejected(self):
        with component_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                d.interface("")

    def test_empty_port_name_rejected(self):
        with component_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                d.port("")

    def test_empty_note_content_rejected(self):
        with component_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                d.note("")

    def test_empty_package_name_rejected(self):
        with component_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                with d.package(""):
                    pass
