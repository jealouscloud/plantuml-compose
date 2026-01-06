"""Tests for object diagram builder, primitives, and renderer."""

import pytest

from plantuml_compose.builders.object_ import object_diagram
from plantuml_compose.primitives.object_ import (
    Field,
    Map,
    MapEntry,
    Object,
    ObjectDiagram,
    ObjectNote,
    Relationship,
)
from plantuml_compose.renderers.object_ import render_object_diagram


class TestObjects:
    """Tests for objects."""

    def test_simple_object(self):
        with object_diagram() as d:
            d.object("Customer")

        output = d.render()
        assert "object Customer" in output

    def test_object_with_alias(self):
        with object_diagram() as d:
            c = d.object("Customer", alias="cust")

        output = d.render()
        assert c == "cust"
        assert "object Customer as cust" in output

    def test_object_with_spaces(self):
        with object_diagram() as d:
            d.object("My Customer")

        output = d.render()
        assert 'object "My Customer"' in output

    def test_object_with_stereotype(self):
        with object_diagram() as d:
            d.object("Customer", stereotype="entity")

        output = d.render()
        assert "<<entity>>" in output

    def test_object_with_color(self):
        with object_diagram() as d:
            d.object("VIP", color="gold")

        output = d.render()
        assert "#gold" in output

    def test_object_with_fields(self):
        with object_diagram() as d:
            d.object_with_fields(
                "Order",
                alias="ord",
                fields={"id": "12345", "status": "pending"}
            )

        output = d.render()
        assert "object Order as ord {" in output
        assert "id = 12345" in output
        assert "status = pending" in output
        assert "}" in output


class TestMaps:
    """Tests for maps."""

    def test_simple_map(self):
        with object_diagram() as d:
            d.map("Products", entries={"item1": "Widget", "item2": "Gadget"})

        output = d.render()
        assert "map Products {" in output
        assert "item1 => Widget" in output
        assert "item2 => Gadget" in output

    def test_map_with_alias(self):
        with object_diagram() as d:
            p = d.map("Products", alias="prod", entries={"x": "y"})

        output = d.render()
        assert p == "prod"
        assert "map Products as prod" in output

    def test_map_with_links(self):
        with object_diagram() as d:
            d.object("Widget", alias="widget")
            d.map("Products", links={"item1": "widget"})

        output = d.render()
        assert "item1 *-> widget" in output

    def test_map_with_color(self):
        with object_diagram() as d:
            d.map("Config", color="LightBlue", entries={"key": "value"})

        output = d.render()
        assert "#LightBlue" in output


class TestRelationships:
    """Tests for relationships."""

    def test_arrow(self):
        with object_diagram() as d:
            a = d.object("A", alias="a")
            b = d.object("B", alias="b")
            d.arrow(a, b)

        output = d.render()
        assert "a --> b" in output

    def test_arrow_with_label(self):
        with object_diagram() as d:
            a = d.object("A", alias="a")
            b = d.object("B", alias="b")
            d.arrow(a, b, label="creates")

        output = d.render()
        assert "a --> b : creates" in output

    def test_link(self):
        with object_diagram() as d:
            a = d.object("A", alias="a")
            b = d.object("B", alias="b")
            d.link(a, b)

        output = d.render()
        assert "a -- b" in output

    def test_composition(self):
        with object_diagram() as d:
            a = d.object("A", alias="a")
            b = d.object("B", alias="b")
            d.composition(a, b)

        output = d.render()
        assert "a *-- b" in output

    def test_aggregation(self):
        with object_diagram() as d:
            a = d.object("A", alias="a")
            b = d.object("B", alias="b")
            d.aggregation(a, b)

        output = d.render()
        assert "a o-- b" in output

    def test_extension(self):
        with object_diagram() as d:
            a = d.object("A", alias="a")
            b = d.object("B", alias="b")
            d.extension(a, b)

        output = d.render()
        assert "a <|-- b" in output

    def test_implementation(self):
        with object_diagram() as d:
            a = d.object("A", alias="a")
            b = d.object("B", alias="b")
            d.implementation(a, b)

        output = d.render()
        assert "a <|.. b" in output

    def test_extension_with_label(self):
        with object_diagram() as d:
            a = d.object("A", alias="a")
            b = d.object("B", alias="b")
            d.extension(a, b, label="extends")

        output = d.render()
        assert "a <|-- b : extends" in output

    def test_relationship_with_color(self):
        with object_diagram() as d:
            a = d.object("A", alias="a")
            b = d.object("B", alias="b")
            d.arrow(a, b, color="blue")

        output = d.render()
        assert "[#blue]" in output


class TestNotes:
    """Tests for notes."""

    def test_note_right(self):
        with object_diagram() as d:
            d.object("Order", alias="ord")
            d.note("Important", target="ord", position="right")

        output = d.render()
        assert "note right of ord" in output
        assert "Important" in output

    def test_floating_note(self):
        with object_diagram() as d:
            d.note("System overview", floating=True)

        output = d.render()
        assert "floating note" in output

    def test_note_with_color(self):
        with object_diagram() as d:
            d.object("Order", alias="ord")
            d.note("Warning", target="ord", color="yellow")

        output = d.render()
        assert "#yellow" in output


class TestDiagramOptions:
    """Tests for diagram-level options."""

    def test_title(self):
        with object_diagram(title="Order Example") as d:
            d.object("Order")

        output = d.render()
        assert "title Order Example" in output


class TestRenderMethod:
    """Tests for the render() convenience method."""

    def test_render_returns_plantuml_text(self):
        with object_diagram() as d:
            d.object("Order")

        output = d.render()
        assert output.startswith("@startuml")
        assert output.endswith("@enduml")

    def test_render_equivalent_to_render_build(self):
        with object_diagram() as d:
            d.object("Order")
            d.object("Customer")

        from plantuml_compose.renderers import render
        assert d.render() == render(d.build())


class TestComplexDiagram:
    """Integration tests with complex diagrams."""

    def test_order_system(self):
        with object_diagram(title="Order System") as d:
            # Customer object
            customer = d.object_with_fields(
                "Customer",
                alias="cust",
                fields={"name": "John Doe", "email": "john@example.com"}
            )

            # Order object
            order = d.object_with_fields(
                "Order",
                alias="ord",
                fields={"id": "ORD-123", "status": "processing", "total": "$99.99"}
            )

            # Items map
            items = d.map(
                "Order Items",
                alias="items",
                entries={"SKU001": "Widget x2", "SKU002": "Gadget x1"}
            )

            # Relationships
            d.arrow(customer, order, label="places")
            d.composition(order, items)

            # Note
            d.note("Pending payment verification", target=order, position="right")

        output = d.render()
        assert "title Order System" in output
        assert "object Customer as cust {" in output
        assert 'name = John Doe' in output
        assert "object Order as ord {" in output
        assert 'id = ORD-123' in output
        assert 'map "Order Items" as items {' in output
        assert "cust --> ord : places" in output
        assert "ord *-- items" in output
        assert "note right of ord" in output


class TestValidation:
    """Tests for input validation."""

    def test_empty_object_name_rejected(self):
        with object_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                d.object("")

    def test_empty_object_with_fields_name_rejected(self):
        with object_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                d.object_with_fields("", fields={"x": "y"})

    def test_empty_map_name_rejected(self):
        with object_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                d.map("", entries={"x": "y"})

    def test_empty_note_content_rejected(self):
        with object_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                d.note("")
