"""Tests for use case diagram builder, primitives, and renderer."""

import pytest

from plantuml_compose import render
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

        output = render(d.build())
        assert "actor User" in output

    def test_actor_with_alias(self):
        with usecase_diagram() as d:
            u = d.actor("User", alias="u")

        output = render(d.build())
        assert u.alias == "u"
        assert u._ref == "u"
        assert "actor User as u" in output

    def test_actor_with_stereotype(self):
        with usecase_diagram() as d:
            d.actor("Admin", stereotype="privileged")

        output = render(d.build())
        assert "<<privileged>>" in output

    def test_actor_with_style(self):
        with usecase_diagram() as d:
            d.actor("VIP", style={"background": "gold"})

        output = render(d.build())
        assert "#gold" in output

    def test_business_actor(self):
        with usecase_diagram() as d:
            d.actor("Employee", business=True)

        output = render(d.build())
        assert "actor/ Employee" in output


class TestUseCases:
    """Tests for use cases."""

    def test_usecase(self):
        with usecase_diagram() as d:
            d.usecase("Login")

        output = render(d.build())
        assert "usecase (Login)" in output

    def test_usecase_with_alias(self):
        with usecase_diagram() as d:
            uc = d.usecase("Login", alias="UC1")

        output = render(d.build())
        assert uc.alias == "UC1"
        assert uc._ref == "UC1"
        assert "usecase (Login) as UC1" in output

    def test_usecase_with_spaces(self):
        with usecase_diagram() as d:
            d.usecase("Browse Products")

        output = render(d.build())
        assert 'usecase ("Browse Products")' in output

    def test_usecase_with_stereotype(self):
        with usecase_diagram() as d:
            d.usecase("Payment", stereotype="critical")

        output = render(d.build())
        assert "<<critical>>" in output

    def test_usecase_with_style(self):
        with usecase_diagram() as d:
            d.usecase("Priority", style={"background": "red"})

        output = render(d.build())
        assert "#red" in output

    def test_business_usecase(self):
        with usecase_diagram() as d:
            d.usecase("Process Order", business=True)

        output = render(d.build())
        assert 'usecase/ ("Process Order")' in output


class TestContainers:
    """Tests for containers."""

    def test_rectangle(self):
        with usecase_diagram() as d:
            with d.rectangle("System") as r:
                r.usecase("Feature")

        output = render(d.build())
        assert "rectangle System" in output
        assert "{" in output
        assert "}" in output

    def test_package(self):
        with usecase_diagram() as d:
            with d.package("Module") as p:
                p.usecase("Feature")

        output = render(d.build())
        assert "package Module" in output

    def test_nested_containers(self):
        with usecase_diagram() as d:
            with d.rectangle("System") as r:
                with r.package("Subsystem") as p:
                    p.usecase("Feature")

        output = render(d.build())
        assert "rectangle System" in output
        assert "package Subsystem" in output

    def test_container_with_style(self):
        with usecase_diagram() as d:
            with d.rectangle("System", style={"background": "LightBlue"}) as r:
                r.usecase("Feature")

        output = render(d.build())
        assert "#LightBlue" in output

    def test_container_elements_without_explicit_alias(self):
        """Elements in containers should include implicit alias to prevent duplicates."""
        with usecase_diagram() as d:
            user = d.actor("System Admin")
            with d.rectangle("System") as r:
                manage = r.usecase("Manage Users")
            d.arrow(user, manage)

        output = render(d.build())
        # When name has spaces, _ref differs from name, so alias is rendered
        assert "as System_Admin" in output
        assert "as Manage_Users" in output


class TestRelationships:
    """Tests for relationships."""

    def test_arrow(self):
        with usecase_diagram() as d:
            user = d.actor("User", alias="u")
            uc = d.usecase("Login", alias="login")
            d.arrow(user, uc)

        output = render(d.build())
        assert "u --> login" in output

    def test_arrow_with_label(self):
        with usecase_diagram() as d:
            user = d.actor("User", alias="u")
            uc = d.usecase("Login", alias="login")
            d.arrow(user, uc, label="authenticates")

        output = render(d.build())
        assert "u --> login : authenticates" in output

    def test_link(self):
        with usecase_diagram() as d:
            user = d.actor("User", alias="u")
            uc = d.usecase("Browse", alias="browse")
            d.link(user, uc)

        output = render(d.build())
        assert "u -> browse" in output

    def test_requires(self):
        """requires() replaces includes() - base ALWAYS needs required."""
        with usecase_diagram() as d:
            checkout = d.usecase("Checkout", alias="checkout")
            validate = d.usecase("Validate Cart", alias="validate")
            d.requires(checkout, validate)

        output = render(d.build())
        assert "checkout .> validate : <<include>>" in output

    def test_optional_for(self):
        """optional_for() replaces extends() - extension MAY occur."""
        with usecase_diagram() as d:
            login = d.usecase("Login", alias="login")
            oauth = d.usecase("OAuth Login", alias="oauth")
            d.optional_for(oauth, login)

        output = render(d.build())
        assert "oauth .> login : <<extends>>" in output

    def test_generalizes(self):
        with usecase_diagram() as d:
            user = d.actor("User", alias="user")
            admin = d.actor("Admin", alias="admin")
            d.generalizes(admin, user)

        output = render(d.build())
        assert "admin <|-- user" in output

    def test_relationship_with_style(self):
        with usecase_diagram() as d:
            user = d.actor("User", alias="u")
            uc = d.usecase("Login", alias="login")
            d.arrow(user, uc, style={"color": "blue"})

        output = render(d.build())
        assert "[#blue]" in output

    def test_connect_hub_and_spoke(self):
        with usecase_diagram() as d:
            user = d.actor("Customer", alias="user")
            browse = d.usecase("Browse", alias="browse")
            cart = d.usecase("Add to Cart", alias="cart")
            checkout = d.usecase("Checkout", alias="checkout")
            d.connect(user, [browse, cart, checkout])

        output = render(d.build())
        assert "user --> browse" in output
        assert "user --> cart" in output
        assert "user --> checkout" in output

    def test_arrow_with_spaces_in_names(self):
        """Test that spaces in element names are sanitized in relationships."""
        with usecase_diagram() as d:
            user = d.actor("System Admin")
            uc = d.usecase("Manage Users")
            d.arrow(user, uc)

        output = render(d.build())
        # Spaces are converted to underscores in the _ref property
        assert "System_Admin --> Manage_Users" in output


class TestNotes:
    """Tests for notes."""

    def test_note_right(self):
        with usecase_diagram() as d:
            d.usecase("Login", alias="login")
            d.note("Important feature", target="login", position="right")

        output = render(d.build())
        assert "note right of login" in output
        assert "Important feature" in output

    def test_note_with_color(self):
        with usecase_diagram() as d:
            d.usecase("Login", alias="login")
            d.note("Warning", target="login", color="yellow")

        output = render(d.build())
        assert "#yellow" in output


class TestDiagramOptions:
    """Tests for diagram-level options."""

    def test_title(self):
        with usecase_diagram(title="Shopping System") as d:
            d.usecase("Browse")

        output = render(d.build())
        assert "title Shopping System" in output

    def test_left_to_right(self):
        with usecase_diagram(left_to_right=True) as d:
            d.usecase("Feature")

        output = render(d.build())
        assert "left to right direction" in output

    def test_actor_style_awesome(self):
        with usecase_diagram(actor_style="awesome") as d:
            d.actor("User")

        output = render(d.build())
        assert "skinparam actorStyle awesome" in output

    def test_actor_style_hollow(self):
        with usecase_diagram(actor_style="hollow") as d:
            d.actor("User")

        output = render(d.build())
        assert "skinparam actorStyle hollow" in output


class TestRenderMethod:
    """Tests for the render() convenience method."""

    def test_render_returns_plantuml_text(self):
        with usecase_diagram() as d:
            d.actor("User")
            d.usecase("Login")

        output = render(d.build())
        assert output.startswith("@startuml")
        assert output.endswith("@enduml")

    def test_render_equivalent_to_render_build(self):
        with usecase_diagram() as d:
            d.actor("User")
            d.usecase("Login")

        from plantuml_compose.renderers import render
        assert render(d.build()) == render(d.build())


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

            # Requires/optional_for
            d.requires(checkout, payment)
            d.optional_for(search, browse)

        output = render(d.build())
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

    def test_actor_style_rejects_text_color(self):
        with usecase_diagram() as d:
            with pytest.raises(ValueError, match="only supports 'background' styling"):
                d.actor("User", style={"text_color": "blue"})

    def test_usecase_style_rejects_line(self):
        with usecase_diagram() as d:
            with pytest.raises(ValueError, match="only supports 'background' styling"):
                d.usecase("Login", style={"line": {"color": "red"}})

    def test_container_style_rejects_text_color(self):
        with usecase_diagram() as d:
            with pytest.raises(ValueError, match="only supports 'background' styling"):
                with d.rectangle("System", style={"text_color": "blue"}):
                    pass
