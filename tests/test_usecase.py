"""Tests for use case diagram builder, primitives, and renderer."""

import pytest

from plantuml_compose.builders.usecase import usecase_diagram
from plantuml_compose.primitives.usecase import (
    Actor,
    UseCase,
    UseCaseDiagram,
    UseCaseNote,
    Relationship,
)
from plantuml_compose.renderers.usecase import render_usecase_diagram


class TestActors:
    """Tests for actors."""

    def test_actor(self):
        with usecase_diagram() as d:
            d.actor("User")

        output = d.render()
        assert "actor User" in output

    def test_actor_with_alias(self):
        with usecase_diagram() as d:
            u = d.actor("User", alias="u")

        output = d.render()
        assert u == "u"
        assert "actor User as u" in output

    def test_actor_with_stereotype(self):
        with usecase_diagram() as d:
            d.actor("Admin", stereotype="privileged")

        output = d.render()
        assert "<<privileged>>" in output

    def test_actor_with_color(self):
        with usecase_diagram() as d:
            d.actor("VIP", color="gold")

        output = d.render()
        assert "#gold" in output

    def test_business_actor(self):
        with usecase_diagram() as d:
            d.actor("Employee", business=True)

        output = d.render()
        assert "actor/ Employee" in output


class TestUseCases:
    """Tests for use cases."""

    def test_usecase(self):
        with usecase_diagram() as d:
            d.usecase("Login")

        output = d.render()
        assert "usecase (Login)" in output

    def test_usecase_with_alias(self):
        with usecase_diagram() as d:
            uc = d.usecase("Login", alias="UC1")

        output = d.render()
        assert uc == "UC1"
        assert "usecase (Login) as UC1" in output

    def test_usecase_with_spaces(self):
        with usecase_diagram() as d:
            d.usecase("Browse Products")

        output = d.render()
        assert 'usecase ("Browse Products")' in output

    def test_usecase_with_stereotype(self):
        with usecase_diagram() as d:
            d.usecase("Payment", stereotype="critical")

        output = d.render()
        assert "<<critical>>" in output

    def test_usecase_with_color(self):
        with usecase_diagram() as d:
            d.usecase("Priority", color="red")

        output = d.render()
        assert "#red" in output

    def test_business_usecase(self):
        with usecase_diagram() as d:
            d.usecase("Process Order", business=True)

        output = d.render()
        assert 'usecase/ ("Process Order")' in output


class TestContainers:
    """Tests for containers."""

    def test_rectangle(self):
        with usecase_diagram() as d:
            with d.rectangle("System") as r:
                r.usecase("Feature")

        output = d.render()
        assert "rectangle System" in output
        assert "{" in output
        assert "}" in output

    def test_package(self):
        with usecase_diagram() as d:
            with d.package("Module") as p:
                p.usecase("Feature")

        output = d.render()
        assert "package Module" in output

    def test_nested_containers(self):
        with usecase_diagram() as d:
            with d.rectangle("System") as r:
                with r.package("Subsystem") as p:
                    p.usecase("Feature")

        output = d.render()
        assert "rectangle System" in output
        assert "package Subsystem" in output

    def test_container_with_color(self):
        with usecase_diagram() as d:
            with d.rectangle("System", color="LightBlue") as r:
                r.usecase("Feature")

        output = d.render()
        assert "#LightBlue" in output


class TestRelationships:
    """Tests for relationships."""

    def test_arrow(self):
        with usecase_diagram() as d:
            user = d.actor("User", alias="u")
            uc = d.usecase("Login", alias="login")
            d.arrow(user, uc)

        output = d.render()
        assert "u --> login" in output

    def test_arrow_with_label(self):
        with usecase_diagram() as d:
            user = d.actor("User", alias="u")
            uc = d.usecase("Login", alias="login")
            d.arrow(user, uc, label="authenticates")

        output = d.render()
        assert "u --> login : authenticates" in output

    def test_link(self):
        with usecase_diagram() as d:
            user = d.actor("User", alias="u")
            uc = d.usecase("Browse", alias="browse")
            d.link(user, uc)

        output = d.render()
        assert "u -> browse" in output

    def test_includes(self):
        with usecase_diagram() as d:
            checkout = d.usecase("Checkout", alias="checkout")
            validate = d.usecase("Validate Cart", alias="validate")
            d.includes(checkout, validate)

        output = d.render()
        assert "checkout .> validate : <<include>>" in output

    def test_extends(self):
        with usecase_diagram() as d:
            login = d.usecase("Login", alias="login")
            oauth = d.usecase("OAuth Login", alias="oauth")
            d.extends(oauth, login)

        output = d.render()
        assert "oauth .> login : <<extends>>" in output

    def test_generalizes(self):
        with usecase_diagram() as d:
            user = d.actor("User", alias="user")
            admin = d.actor("Admin", alias="admin")
            d.generalizes(admin, user)

        output = d.render()
        assert "admin <|-- user" in output

    def test_relationship_with_color(self):
        with usecase_diagram() as d:
            user = d.actor("User", alias="u")
            uc = d.usecase("Login", alias="login")
            d.arrow(user, uc, color="blue")

        output = d.render()
        assert "[#blue]" in output


class TestNotes:
    """Tests for notes."""

    def test_note_right(self):
        with usecase_diagram() as d:
            d.usecase("Login", alias="login")
            d.note("Important feature", target="login", position="right")

        output = d.render()
        assert "note right of login" in output
        assert "Important feature" in output

    def test_floating_note(self):
        with usecase_diagram() as d:
            d.note("System overview", floating=True)

        output = d.render()
        assert "floating note" in output

    def test_note_with_color(self):
        with usecase_diagram() as d:
            d.usecase("Login", alias="login")
            d.note("Warning", target="login", color="yellow")

        output = d.render()
        assert "#yellow" in output


class TestDiagramOptions:
    """Tests for diagram-level options."""

    def test_title(self):
        with usecase_diagram(title="Shopping System") as d:
            d.usecase("Browse")

        output = d.render()
        assert "title Shopping System" in output

    def test_left_to_right(self):
        with usecase_diagram(left_to_right=True) as d:
            d.usecase("Feature")

        output = d.render()
        assert "left to right direction" in output

    def test_actor_style_awesome(self):
        with usecase_diagram(actor_style="awesome") as d:
            d.actor("User")

        output = d.render()
        assert "skinparam actorStyle awesome" in output

    def test_actor_style_hollow(self):
        with usecase_diagram(actor_style="hollow") as d:
            d.actor("User")

        output = d.render()
        assert "skinparam actorStyle hollow" in output


class TestRenderMethod:
    """Tests for the render() convenience method."""

    def test_render_returns_plantuml_text(self):
        with usecase_diagram() as d:
            d.actor("User")
            d.usecase("Login")

        output = d.render()
        assert output.startswith("@startuml")
        assert output.endswith("@enduml")

    def test_render_equivalent_to_render_build(self):
        with usecase_diagram() as d:
            d.actor("User")
            d.usecase("Login")

        from plantuml_compose.renderers import render
        assert d.render() == render(d.build())


class TestComplexDiagram:
    """Integration tests with complex diagrams."""

    def test_ecommerce_system(self):
        with usecase_diagram(title="E-Commerce System", left_to_right=True) as d:
            # Actors
            customer = d.actor("Customer", alias="customer")
            admin = d.actor("Admin", alias="admin")

            # System boundary
            with d.rectangle("E-Commerce Platform") as system:
                browse = system.usecase("Browse Products", alias="browse")
                search = system.usecase("Search", alias="search")
                cart = system.usecase("Manage Cart", alias="cart")
                checkout = system.usecase("Checkout", alias="checkout")
                payment = system.usecase("Process Payment", alias="payment")
                manage = system.usecase("Manage Products", alias="manage")

            # Customer relationships
            d.arrow(customer, browse)
            d.arrow(customer, search)
            d.arrow(customer, cart)
            d.arrow(customer, checkout)

            # Admin relationships
            d.arrow(admin, manage)

            # Include/extends
            d.includes(checkout, payment)
            d.extends(search, browse)

        output = d.render()
        assert "title E-Commerce System" in output
        assert "left to right direction" in output
        assert 'rectangle "E-Commerce Platform"' in output
        assert "customer --> browse" in output
        assert "admin --> manage" in output
        assert "checkout .> payment : <<include>>" in output
        assert "search .> browse : <<extends>>" in output


class TestValidation:
    """Tests for input validation."""

    def test_empty_actor_name_rejected(self):
        with usecase_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                d.actor("")

    def test_empty_usecase_name_rejected(self):
        with usecase_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                d.usecase("")

    def test_empty_note_content_rejected(self):
        with usecase_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                d.note("")

    def test_empty_rectangle_name_rejected(self):
        with usecase_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                with d.rectangle(""):
                    pass
