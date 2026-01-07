"""Tests for deployment diagram builder, primitives, and renderer."""

import pytest

from plantuml_compose import render
from plantuml_compose.builders.deployment import deployment_diagram
from plantuml_compose.primitives.deployment import (
    DeploymentDiagram,
    DeploymentElement,
    DeploymentNote,
    Relationship,
)
from plantuml_compose.renderers.deployment import render_deployment_diagram


class TestBasicElements:
    """Tests for basic deployment elements."""

    def test_node(self):
        with deployment_diagram() as d:
            with d.node_nested("Server") as server:
                server.component("App")

        output = render(d.build())
        assert "node Server" in output
        assert "component App" in output

    def test_actor(self):
        with deployment_diagram() as d:
            d.actor("User")

        output = render(d.build())
        assert "actor User" in output

    def test_artifact(self):
        with deployment_diagram() as d:
            d.artifact("app.jar")

        output = render(d.build())
        assert 'artifact "app.jar"' in output

    def test_component(self):
        with deployment_diagram() as d:
            d.component("WebApp")

        output = render(d.build())
        assert "component WebApp" in output

    def test_database(self):
        with deployment_diagram() as d:
            d.database("PostgreSQL")

        output = render(d.build())
        assert "database PostgreSQL" in output

    def test_cloud(self):
        with deployment_diagram() as d:
            d.cloud("AWS")

        output = render(d.build())
        assert "cloud AWS" in output

    def test_file(self):
        with deployment_diagram() as d:
            d.file("config.yml")

        output = render(d.build())
        assert 'file "config.yml"' in output

    def test_folder(self):
        with deployment_diagram() as d:
            d.folder("Documents")

        output = render(d.build())
        assert "folder Documents" in output

    def test_queue(self):
        with deployment_diagram() as d:
            d.queue("MessageQueue")

        output = render(d.build())
        assert "queue MessageQueue" in output

    def test_storage(self):
        with deployment_diagram() as d:
            d.storage("S3Bucket")

        output = render(d.build())
        assert "storage S3Bucket" in output

    def test_stack(self):
        with deployment_diagram() as d:
            d.stack("TechStack")

        output = render(d.build())
        assert "stack TechStack" in output

    def test_element_with_alias(self):
        with deployment_diagram() as d:
            srv = d.component("Web Server", alias="srv")

        output = render(d.build())
        assert srv == "srv"
        assert 'component "Web Server" as srv' in output

    def test_element_with_stereotype(self):
        with deployment_diagram() as d:
            d.component("API", stereotype="service")

        output = render(d.build())
        assert "<<service>>" in output

    def test_element_with_style(self):
        with deployment_diagram() as d:
            d.component("Critical", style={"background": "red"})

        output = render(d.build())
        assert "#red" in output


class TestNestedElements:
    """Tests for nested elements."""

    def test_node_with_components(self):
        with deployment_diagram() as d:
            with d.node_nested("AppServer") as node:
                node.component("Frontend")
                node.component("Backend")
                node.database("Cache")

        output = render(d.build())
        assert "node AppServer" in output
        assert "component Frontend" in output
        assert "component Backend" in output
        assert "database Cache" in output

    def test_cloud_with_services(self):
        with deployment_diagram() as d:
            with d.cloud_nested("AWS") as cloud:
                cloud.component("Lambda")
                cloud.database("DynamoDB")

        output = render(d.build())
        assert "cloud AWS" in output
        assert "component Lambda" in output
        assert "database DynamoDB" in output

    def test_database_nested(self):
        with deployment_diagram() as d:
            with d.database_nested("PostgreSQL") as db:
                db.artifact("users_table")

        output = render(d.build())
        assert "database PostgreSQL" in output
        assert "artifact users_table" in output

    def test_deeply_nested(self):
        with deployment_diagram() as d:
            with d.cloud_nested("AWS") as cloud:
                with cloud.node_nested("EC2") as node:
                    node.component("App")

        output = render(d.build())
        assert "cloud AWS" in output
        assert "node EC2" in output
        assert "component App" in output


class TestRelationships:
    """Tests for relationships between elements."""

    def test_arrow(self):
        with deployment_diagram() as d:
            a = d.component("A", alias="a")
            b = d.component("B", alias="b")
            d.arrow(a, b)

        output = render(d.build())
        assert "a --> b" in output

    def test_arrow_with_label(self):
        with deployment_diagram() as d:
            a = d.component("A", alias="a")
            b = d.component("B", alias="b")
            d.arrow(a, b, label="connects")

        output = render(d.build())
        assert "a --> b : connects" in output

    def test_dotted_arrow(self):
        with deployment_diagram() as d:
            a = d.component("A", alias="a")
            b = d.component("B", alias="b")
            d.arrow(a, b, dotted=True)

        output = render(d.build())
        assert "a ..> b" in output

    def test_link(self):
        with deployment_diagram() as d:
            a = d.component("A", alias="a")
            b = d.component("B", alias="b")
            d.link(a, b)

        output = render(d.build())
        assert "a -- b" in output

    def test_dotted_link(self):
        with deployment_diagram() as d:
            a = d.component("A", alias="a")
            b = d.component("B", alias="b")
            d.link(a, b, dotted=True)

        output = render(d.build())
        assert "a .. b" in output

    def test_relationship_with_style(self):
        with deployment_diagram() as d:
            a = d.component("A", alias="a")
            b = d.component("B", alias="b")
            d.arrow(a, b, style={"color": "blue"})

        output = render(d.build())
        assert "[#blue]" in output


class TestNotes:
    """Tests for notes."""

    def test_note_right(self):
        with deployment_diagram() as d:
            d.component("API", alias="api")
            d.note("Main entry point", target="api", position="right")

        output = render(d.build())
        assert "note right of api" in output
        assert "Main entry point" in output

    def test_floating_note(self):
        with deployment_diagram() as d:
            d.note("System overview", floating=True)

        output = render(d.build())
        assert "floating note" in output

    def test_note_with_color(self):
        with deployment_diagram() as d:
            d.component("API", alias="api")
            d.note("Important", target="api", color="yellow")

        output = render(d.build())
        assert "#yellow" in output


class TestDiagramOptions:
    """Tests for diagram-level options."""

    def test_title(self):
        with deployment_diagram(title="Infrastructure") as d:
            d.component("API")

        output = render(d.build())
        assert "title Infrastructure" in output


class TestRenderMethod:
    """Tests for the render() convenience method."""

    def test_render_returns_plantuml_text(self):
        with deployment_diagram() as d:
            d.component("API")

        output = render(d.build())
        assert output.startswith("@startuml")
        assert output.endswith("@enduml")

    def test_render_equivalent_to_render_build(self):
        with deployment_diagram() as d:
            d.component("API")
            d.database("DB")

        from plantuml_compose.renderers import render
        assert render(d.build()) == render(d.build())


class TestComplexDiagram:
    """Integration tests with complex diagrams."""

    def test_microservices_deployment(self):
        with deployment_diagram(title="Microservices Deployment") as d:
            # Load Balancer
            lb = d.component("Load Balancer", alias="lb")

            # Application servers
            with d.node_nested("App Server 1") as app1:
                api1 = app1.component("API", alias="api1")

            with d.node_nested("App Server 2") as app2:
                api2 = app2.component("API", alias="api2")

            # Database cluster
            with d.cloud_nested("Database Cluster") as dbcluster:
                primary = dbcluster.database("Primary", alias="primary")
                replica = dbcluster.database("Replica", alias="replica")

            # Message queue
            mq = d.queue("RabbitMQ", alias="mq")

            # Relationships
            d.arrow("lb", "api1")
            d.arrow("lb", "api2")
            d.arrow("api1", "primary", label="writes")
            d.arrow("api2", "primary", label="writes")
            d.arrow("api1", "mq")
            d.arrow("api2", "mq")
            d.link("primary", "replica", label="replicates")

        output = render(d.build())
        assert "title Microservices Deployment" in output
        assert 'component "Load Balancer" as lb' in output
        assert 'node "App Server 1"' in output
        assert "cloud \"Database Cluster\"" in output
        assert "lb --> api1" in output
        assert "primary -- replica : replicates" in output

    def test_all_element_types(self):
        """Test that all element types can be rendered."""
        with deployment_diagram() as d:
            d.actor("User")
            d.agent("Agent")
            d.artifact("Artifact")
            d.boundary("Boundary")
            d.card("Card")
            d.circle("Circle")
            d.cloud("Cloud")
            d.collections("Collections")
            d.component("Component")
            d.control("Control")
            d.database("Database")
            d.entity("Entity")
            d.file("File")
            d.folder("Folder")
            d.frame("Frame")
            d.hexagon("Hexagon")
            d.interface("Interface")
            d.label("Label")
            d.package("Package")
            d.person("Person")
            d.process("Process")
            d.queue("Queue")
            d.rectangle("Rectangle")
            d.stack("Stack")
            d.storage("Storage")
            d.usecase("Usecase")

        output = render(d.build())
        assert "actor User" in output
        assert "agent Agent" in output
        assert "database Database" in output
        assert "queue Queue" in output


class TestValidation:
    """Tests for input validation."""

    def test_empty_actor_name_rejected(self):
        with deployment_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                d.actor("")

    def test_empty_database_name_rejected(self):
        with deployment_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                d.database("")

    def test_empty_note_content_rejected(self):
        with deployment_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                d.note("")

    def test_empty_nested_node_name_rejected(self):
        with deployment_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                with d.node_nested(""):
                    pass

    def test_element_style_rejects_text_color(self):
        with deployment_diagram() as d:
            with pytest.raises(ValueError, match="only supports 'background' styling"):
                d.component("API", style={"text_color": "blue"})

    def test_element_style_rejects_line(self):
        with deployment_diagram() as d:
            with pytest.raises(ValueError, match="only supports 'background' styling"):
                d.database("DB", style={"line": {"color": "red"}})

    def test_nested_element_style_rejects_text_color(self):
        with deployment_diagram() as d:
            with pytest.raises(ValueError, match="only supports 'background' styling"):
                with d.node_nested("Server", style={"text_color": "blue"}):
                    pass
