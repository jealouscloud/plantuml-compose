"""Test primitive fields that exist but may not be rendered.

These tests verify whether PlantUML actually supports certain primitive fields
that exist in our data model but aren't currently exposed through the builder API.

If PlantUML supports them, we should expose them in the builder.
If PlantUML ignores them, we should document this or add canary tests.
"""

from plantuml_compose.primitives.class_ import (
    ClassDiagram,
    ClassNode,
    Relationship,
)
from plantuml_compose.primitives.common import Label, Style
from plantuml_compose.renderers.class_ import render_class_diagram


class TestClassNodeStyle:
    """Test ClassNode.style field rendering."""

    def test_class_with_inline_style(self, validate_plantuml):
        """Test that ClassNode.style renders inline styling on class nodes.

        PlantUML supports inline color syntax: class ClassName #E3F2FD
        """
        # Create a class with style (directly using primitives)
        diagram = ClassDiagram(
            elements=(
                ClassNode(
                    name="StyledClass",
                    type="class",
                    style=Style(background="#E3F2FD"),
                ),
            )
        )

        puml = render_class_diagram(diagram)
        print(f"Generated PlantUML:\n{puml}")

        is_valid = validate_plantuml(puml, "class_with_style")
        assert is_valid, "PlantUML should accept the generated syntax"

        # Verify style is rendered
        assert "StyledClass" in puml
        assert "#E3F2FD" in puml, "Style should be rendered"


class TestRelationshipNote:
    """Test Relationship.note field for class diagrams."""

    def test_relationship_with_note(self, validate_plantuml):
        """Test that Relationship.note renders using 'note on link' syntax.

        PlantUML supports notes on relationships with the 'note on link' syntax.
        """
        diagram = ClassDiagram(
            elements=(
                ClassNode(name="ClassA", type="class"),
                ClassNode(name="ClassB", type="class"),
                Relationship(
                    source="ClassA",
                    target="ClassB",
                    type="association",
                    note=Label(text="This is a note on the relationship"),
                ),
            )
        )

        puml = render_class_diagram(diagram)
        print(f"Generated PlantUML:\n{puml}")

        is_valid = validate_plantuml(puml, "relationship_with_note")
        assert is_valid, "PlantUML should accept the generated syntax"

        # Verify note is rendered
        assert "note on link" in puml, "Relationship note should be rendered"
        assert "This is a note on the relationship" in puml


class TestPlantUMLSyntaxSupport:
    """Canary tests verifying PlantUML supports features we expose.

    These tests validate raw PlantUML syntax. If they fail, PlantUML has
    changed and we need to update our API accordingly.
    """

    def test_note_on_link_syntax(self, validate_plantuml):
        """Verify PlantUML accepts 'note on link' syntax in class diagrams."""
        puml = """@startuml
class ClassA
class ClassB
ClassA --> ClassB
note on link : This is a note
@enduml"""

        is_valid = validate_plantuml(puml, "note_on_link_raw")
        assert is_valid, "PlantUML should support 'note on link' syntax"

    def test_class_with_color_syntax(self, validate_plantuml):
        """Verify PlantUML accepts inline color styling on class declarations."""
        puml = """@startuml
class StyledClass #E3F2FD
class AnotherClass
@enduml"""

        is_valid = validate_plantuml(puml, "class_with_color_raw")
        assert is_valid, "PlantUML should support inline class colors"

    def test_class_with_line_color(self, validate_plantuml):
        """Verify PlantUML accepts extended inline style syntax."""
        puml = """@startuml
class StyledClass #back:E3F2FD;line:1976D2
@enduml"""

        is_valid = validate_plantuml(puml, "class_with_line_color_raw")
        assert is_valid, "PlantUML should support extended inline style syntax"
