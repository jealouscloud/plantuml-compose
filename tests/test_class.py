"""Tests for class diagram builder, primitives, and renderer."""

import pytest

from plantuml_compose import render
from plantuml_compose.builders.class_ import class_diagram
from plantuml_compose.primitives.class_ import (
    ClassDiagram,
    ClassNode,
    Member,
    Package,
    Relationship,
    Separator,
    Together,
)
from plantuml_compose.renderers.class_ import render_class_diagram


class TestClassNode:
    """Tests for class creation and rendering."""

    def test_basic_class(self):
        with class_diagram() as d:
            d.class_("User")

        output = render(d.build())
        assert "class User" in output

    def test_abstract_class(self):
        with class_diagram() as d:
            d.abstract("AbstractEntity")

        output = render(d.build())
        assert "abstract class AbstractEntity" in output

    def test_interface(self):
        with class_diagram() as d:
            d.interface("Repository")

        output = render(d.build())
        assert "interface Repository" in output

    def test_enum_with_values(self):
        with class_diagram() as d:
            d.enum("Status", "PENDING", "ACTIVE", "CLOSED")

        output = render(d.build())
        assert "enum Status {" in output
        assert "PENDING" in output
        assert "ACTIVE" in output
        assert "CLOSED" in output

    def test_annotation(self):
        with class_diagram() as d:
            d.annotation("Deprecated")

        output = render(d.build())
        assert "annotation Deprecated" in output

    def test_entity(self):
        with class_diagram() as d:
            d.entity("Order")

        output = render(d.build())
        assert "entity Order" in output

    def test_class_with_generics(self):
        with class_diagram() as d:
            d.class_("Repository", generics="T extends Entity")

        output = render(d.build())
        assert "class Repository<T extends Entity>" in output

    def test_class_with_alias(self):
        with class_diagram() as d:
            d.class_("Long Class Name", alias="lcn")

        output = render(d.build())
        assert 'class "Long Class Name" as lcn' in output

    def test_class_with_style(self):
        """Test that class style renders inline color."""
        with class_diagram() as d:
            d.class_("Error", style={"background": "#FFCDD2"})

        output = render(d.build())
        assert "class Error #FFCDD2" in output

    def test_abstract_with_style(self):
        """Test that abstract class style renders inline color."""
        with class_diagram() as d:
            d.abstract("Base", style={"background": "#E3F2FD"})

        output = render(d.build())
        assert "abstract class Base #E3F2FD" in output

    def test_interface_with_style(self):
        """Test that interface style renders inline color."""
        with class_diagram() as d:
            d.interface("Serializable", style={"background": "#FFF3E0"})

        output = render(d.build())
        assert "interface Serializable #FFF3E0" in output

    def test_enum_with_style(self):
        """Test that enum style renders inline color."""
        with class_diagram() as d:
            d.enum("Status", "ACTIVE", "INACTIVE", style={"background": "#E8F5E9"})

        output = render(d.build())
        assert "#E8F5E9" in output

    def test_annotation_with_style(self):
        """Test that annotation style renders inline color."""
        with class_diagram() as d:
            d.annotation("Deprecated", style={"background": "#FFEBEE"})

        output = render(d.build())
        assert "annotation Deprecated #FFEBEE" in output

    def test_entity_with_style(self):
        """Test that entity style renders inline color."""
        with class_diagram() as d:
            d.entity("Order", style={"background": "#FCE4EC"})

        output = render(d.build())
        assert "entity Order #FCE4EC" in output

    def test_class_with_members_and_style(self):
        """Test that class_with_members style renders inline color."""
        with class_diagram() as d:
            with d.class_with_members("User", style={"background": "#E1F5FE"}) as user:
                user.field("name", "str")

        output = render(d.build())
        assert "#E1F5FE" in output
        assert "name : str" in output


class TestClassMembers:
    """Tests for class members (fields and methods)."""

    def test_field_with_type(self):
        with class_diagram() as d:
            with d.class_with_members("User") as user:
                user.field("id", "int")

        output = render(d.build())
        assert "id : int" in output

    def test_field_with_visibility(self):
        """Test visibility parameter with human-readable names."""
        with class_diagram() as d:
            with d.class_with_members("User") as user:
                user.field("private_field", "str", visibility="private")
                user.field("public_field", "str", visibility="public")
                user.field("protected_field", "str", visibility="protected")
                user.field("package_field", "str", visibility="package")

        output = render(d.build())
        assert "-private_field : str" in output
        assert "+public_field : str" in output
        assert "#protected_field : str" in output
        assert "~package_field : str" in output

    def test_field_visibility_prefix_rejected(self):
        """Visibility prefix in field name is rejected with helpful error."""
        with class_diagram() as d:
            with d.class_with_members("User") as user:
                with pytest.raises(ValueError, match="Visibility prefix"):
                    user.field("-private_field", "str")

    def test_method(self):
        with class_diagram() as d:
            with d.class_with_members("User") as user:
                user.method("login()", "bool", visibility="public")

        output = render(d.build())
        assert "+login() : bool" in output

    def test_method_visibility_prefix_rejected(self):
        """Visibility prefix in method name is rejected with helpful error."""
        with class_diagram() as d:
            with d.class_with_members("User") as user:
                with pytest.raises(ValueError, match="Visibility prefix"):
                    user.method("+login()", "bool")

    def test_static_method(self):
        with class_diagram() as d:
            with d.class_with_members("User") as user:
                user.static_method("create()", "User")

        output = render(d.build())
        assert "{static}" in output
        assert "create() : User" in output

    def test_static_field(self):
        with class_diagram() as d:
            with d.class_with_members("Counter") as counter:
                counter.static_field("count", "int")

        output = render(d.build())
        assert "{static}" in output
        assert "count : int" in output

    def test_abstract_method(self):
        with class_diagram() as d:
            with d.class_with_members("Entity") as entity:
                entity.abstract_method("save()", "bool", visibility="public")

        output = render(d.build())
        assert "{abstract}" in output
        assert "+ save() : bool" in output  # Space after modifier+visibility

    def test_separator(self):
        with class_diagram() as d:
            with d.class_with_members("User") as user:
                user.field("id", "int")
                user.separator()
                user.method("save()", "bool")

        output = render(d.build())
        assert "--" in output

    def test_separator_with_label(self):
        with class_diagram() as d:
            with d.class_with_members("User") as user:
                user.field("id", "int")
                user.separator(label="Methods")
                user.method("save()", "bool")

        output = render(d.build())
        assert "-- Methods --" in output


class TestRelationships:
    """Tests for class relationships."""

    def test_extends(self):
        with class_diagram() as d:
            parent = d.class_("Parent")
            child = d.class_("Child")
            d.extends(child, parent)

        output = render(d.build())
        assert "Parent <|-- Child" in output

    def test_relationship_with_member_builder_before_context_exit(self):
        """Using _ClassMemberBuilder in relationship before context exits works."""
        with class_diagram() as d:
            user = d.class_("User")
            with d.class_with_members("Admin") as admin:
                admin.field("level", "int")
                # Use admin in relationship BEFORE context exits
                d.extends(admin, user)

        output = render(d.build())
        assert "User <|-- Admin" in output
        assert "level : int" in output

    def test_implements(self):
        with class_diagram() as d:
            interface = d.interface("Repository")
            impl = d.class_("UserRepository")
            d.implements(impl, interface)

        output = render(d.build())
        assert "Repository <|.. UserRepository" in output

    def test_aggregation(self):
        with class_diagram() as d:
            container = d.class_("Container")
            item = d.class_("Item")
            d.has(container, item)

        output = render(d.build())
        assert "Container o-- Item" in output

    def test_composition(self):
        """Use contains() for composition (filled diamond)."""
        with class_diagram() as d:
            container = d.class_("Container")
            item = d.class_("Item")
            d.contains(container, item)

        output = render(d.build())
        assert "Container *-- Item" in output

    def test_uses_dependency(self):
        with class_diagram() as d:
            user = d.class_("User")
            service = d.class_("Service")
            d.uses(user, service)

        output = render(d.build())
        assert "User ..> Service" in output

    def test_lollipop_interface(self):
        """Test lollipop interface notation."""
        with class_diagram() as d:
            service = d.class_("OrderService")
            repo = d.interface("Repository")
            d.lollipop(service, repo)

        output = render(d.build())
        assert "OrderService ()- Repository" in output

    def test_lollipop_via_relationship(self):
        """Test lollipop using generic relationship method."""
        with class_diagram() as d:
            a = d.class_("A")
            b = d.class_("B")
            d.relationship(a, b, type="lollipop")

        output = render(d.build())
        assert "A ()- B" in output

    def test_association(self):
        with class_diagram() as d:
            a = d.class_("A")
            b = d.class_("B")
            d.associates(a, b)

        output = render(d.build())
        assert "A --> B" in output

    def test_relationship_with_labels(self):
        with class_diagram() as d:
            user = d.class_("User")
            order = d.class_("Order")
            d.has(user, order, whole_label="1", part_label="*")

        output = render(d.build())
        assert '"1"' in output
        assert '"*"' in output

    def test_relationship_with_label(self):
        with class_diagram() as d:
            user = d.class_("User")
            order = d.class_("Order")
            d.has(user, order, label="places")

        output = render(d.build())
        assert ": places" in output

    def test_relationship_with_role_labels(self):
        with class_diagram() as d:
            user = d.class_("User")
            order = d.class_("Order")
            d.has(
                user,
                order,
                whole_label="owner",
                part_label="orders",
            )

        output = render(d.build())
        assert '"owner"' in output
        assert '"orders"' in output

    def test_relationship_with_style_color(self):
        with class_diagram() as d:
            user = d.class_("User")
            order = d.class_("Order")
            d.associates(user, order, style={"color": "red"})

        output = render(d.build())
        assert "-[#red]->" in output

    def test_relationship_with_style_dashed(self):
        with class_diagram() as d:
            user = d.class_("User")
            order = d.class_("Order")
            d.associates(user, order, style={"pattern": "dashed"})

        output = render(d.build())
        assert "-[dashed]->" in output

    def test_relationship_with_combined_style(self):
        with class_diagram() as d:
            user = d.class_("User")
            order = d.class_("Order")
            d.associates(
                user,
                order,
                style={"color": "blue", "pattern": "dotted", "thickness": 2},
            )

        output = render(d.build())
        assert "-[#blue,dotted,thickness=2]->" in output

    def test_relationship_with_note(self):
        """Test that relationship note renders using 'note on link' syntax."""
        with class_diagram() as d:
            user = d.class_("User")
            order = d.class_("Order")
            d.has(user, order, note="Ownership relationship")

        output = render(d.build())
        assert "User o-- Order" in output
        assert "note on link : Ownership relationship" in output


class TestPackages:
    """Tests for packages."""

    def test_basic_package(self):
        with class_diagram() as d:
            with d.package("domain") as pkg:
                pkg.class_("User")
                pkg.class_("Order")

        output = render(d.build())
        assert "package domain {" in output
        assert "class User" in output
        assert "class Order" in output
        assert "}" in output

    def test_package_with_color(self):
        with class_diagram() as d:
            with d.package("domain", color="LightBlue") as pkg:
                pkg.class_("User")

        output = render(d.build())
        assert "#LightBlue" in output

    def test_package_with_style(self):
        with class_diagram() as d:
            with d.package("domain", style="folder") as pkg:
                pkg.class_("User")

        output = render(d.build())
        assert "<<Folder>>" in output

    def test_nested_packages(self):
        with class_diagram() as d:
            with d.package("com.example") as outer:
                with outer.package("domain") as inner:
                    inner.class_("User")

        output = render(d.build())
        # com.example gets quoted because it contains a dot
        assert 'package "com.example" {' in output
        assert "package domain {" in output

    def test_package_relationships(self):
        """Packages can participate in relationships."""
        with class_diagram() as d:
            with d.package("com.example") as pkg1:
                pkg1.class_("User")
            with d.package("com.other") as pkg2:
                pkg2.class_("Service")
            d.uses(pkg1, pkg2, label="depends")

        output = render(d.build())
        # Package refs with dots should be quoted
        assert '"com.example" ..> "com.other" : depends' in output


class TestTogether:
    """Tests for together layout grouping."""

    def test_together_basic(self):
        with class_diagram() as d:
            with d.together() as t:
                t.class_("A")
                t.class_("B")

        output = render(d.build())
        assert "together {" in output
        assert "class A" in output
        assert "class B" in output


class TestNotes:
    """Tests for notes."""

    def test_note_on_class(self):
        with class_diagram() as d:
            user = d.class_("User")
            d.note("Main entity", of=user)

        output = render(d.build())
        assert "note right of User: Main entity" in output


class TestDiagramOptions:
    """Tests for diagram-level options."""

    def test_title(self):
        with class_diagram(title="Domain Model") as d:
            d.class_("User")

        output = render(d.build())
        assert "title Domain Model" in output

    def test_hide_empty_members(self):
        with class_diagram(hide_empty_members=True) as d:
            d.class_("User")

        output = render(d.build())
        assert "hide empty members" in output

    def test_hide_circle(self):
        with class_diagram(hide_circle=True) as d:
            d.class_("User")

        output = render(d.build())
        assert "hide circle" in output

    def test_namespace_separator(self):
        with class_diagram(namespace_separator="::") as d:
            d.class_("User")

        output = render(d.build())
        assert "set separator ::" in output


class TestDiagramStyle:
    """Tests for CSS-style diagram styling."""

    def test_diagram_style_with_dict(self):
        with class_diagram(
            diagram_style={
                "background": "white",
                "class_": {"background": "#E3F2FD"},
                "arrow": {"line_color": "#757575"},
            }
        ) as d:
            a = d.class_("A")
            b = d.class_("B")
            d.associates(a, b)

        output = render(d.build())
        assert "<style>" in output
        assert "classDiagram {" in output
        assert "BackgroundColor #E3F2FD" in output
        assert "LineColor #757575" in output
        assert "</style>" in output

    def test_diagram_style_interface(self):
        with class_diagram(
            diagram_style={
                "interface": {"background": "#FFF3E0"},
            }
        ) as d:
            d.interface("IService")

        output = render(d.build())
        assert "interface {" in output
        assert "BackgroundColor #FFF3E0" in output

    def test_diagram_style_package(self):
        with class_diagram(
            diagram_style={
                "package": {"background": "#E8F5E9"},
            }
        ) as d:
            with d.package("domain"):
                pass

        output = render(d.build())
        assert "package {" in output
        assert "BackgroundColor #E8F5E9" in output


class TestRenderMethod:
    """Tests for the render() convenience method."""

    def test_render_returns_plantuml_text(self):
        with class_diagram() as d:
            d.class_("User")

        output = render(d.build())
        assert output.startswith("@startuml")
        assert output.endswith("@enduml")

    def test_render_equivalent_to_render_build(self):
        with class_diagram() as d:
            d.class_("User")

        from plantuml_compose.renderers import render

        assert render(d.build()) == render(d.build())


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_diagram(self):
        with class_diagram() as d:
            pass

        output = render(d.build())
        assert "@startuml" in output
        assert "@enduml" in output

    def test_class_name_with_spaces(self):
        with class_diagram() as d:
            d.class_("My Class")

        output = render(d.build())
        assert '"My Class"' in output

    def test_relationship_with_string_refs(self):
        """Test that string refs work when classes are declared first."""
        with class_diagram() as d:
            d.class_("User")
            d.class_("Order")
            d.relationship("User", "Order", "association")

        output = render(d.build())
        assert "User --> Order" in output

    def test_relationship_with_invalid_string_ref_fails(self):
        """Test that invalid string refs raise ValueError."""
        import pytest

        with class_diagram() as d:
            d.class_("User")
            with pytest.raises(ValueError, match='target "NonExistent" not found'):
                d.relationship("User", "NonExistent", "association")


class TestComplexDiagram:
    """Integration tests with complex diagrams."""

    def test_domain_model(self):
        with class_diagram(title="E-Commerce Domain") as d:
            # Entities
            user = d.class_("User")
            order = d.class_("Order")

            with d.class_with_members("Product") as product:
                product.field("id", "int", visibility="private")
                product.field("name", "str", visibility="private")
                product.field("price", "Decimal", visibility="private")
                product.separator()
                product.method("apply_discount(pct)", "Decimal", visibility="public")

            # Relationships
            d.has(user, order, whole_label="1", part_label="*", label="places")
            d.has(order, "Product", whole_label="1", part_label="*")

        output = render(d.build())
        assert "title E-Commerce Domain" in output
        assert "class User" in output
        assert "class Order" in output
        assert "class Product {" in output
        assert "-id : int" in output
        assert "+apply_discount(pct) : Decimal" in output
        assert 'User "1" o-- "*" Order : places' in output


class TestValidation:
    """Tests for input validation."""

    def test_empty_class_name_rejected(self):
        with class_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                d.class_("")

    def test_empty_abstract_name_rejected(self):
        with class_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                d.abstract("")

    def test_empty_interface_name_rejected(self):
        with class_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                d.interface("")

    def test_empty_enum_name_rejected(self):
        with class_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                d.enum("")

    def test_empty_annotation_name_rejected(self):
        with class_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                d.annotation("")

    def test_empty_entity_name_rejected(self):
        with class_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                d.entity("")

    def test_empty_note_content_rejected(self):
        with class_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                d.note("")

    def test_empty_package_name_rejected(self):
        with class_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                with d.package(""):
                    pass

    def test_enum_with_both_values_and_members_rejected(self):
        """ClassNode cannot have both enum_values and members set."""
        with pytest.raises(ValueError, match="cannot have both enum_values and members"):
            ClassNode(
                name="Status",
                type="enum",
                enum_values=("ACTIVE", "INACTIVE"),
                members=(Member(name="getValue()", is_method=True),),
            )
