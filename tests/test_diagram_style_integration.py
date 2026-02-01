"""Integration tests that verify PlantUML actually renders diagram styles.

These tests run PlantUML and check the SVG output to verify styles are applied.
They require PlantUML to be installed and available in PATH.

IMPORTANT: Every test in this file MUST verify that the style has a visual effect
(color appears in SVG output), not just that the syntax is accepted.
"""
import subprocess
import tempfile
import pytest
from pathlib import Path

from plantuml_compose.builders.sequence import sequence_diagram
from plantuml_compose.builders.activity import activity_diagram
from plantuml_compose.builders.class_ import class_diagram
from plantuml_compose.builders.state import state_diagram
from plantuml_compose.builders.component import component_diagram
from plantuml_compose.builders.object_ import object_diagram
from plantuml_compose.builders.json_ import json_diagram, yaml_diagram
from plantuml_compose.builders.wbs import wbs_diagram
from plantuml_compose.renderers import render


def plantuml_available() -> bool:
    """Check if PlantUML is available."""
    try:
        result = subprocess.run(
            ["plantuml", "-version"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def run_plantuml_and_verify_color(puml: str, color: str) -> None:
    """Run PlantUML and verify the color appears in SVG output.

    Args:
        puml: PlantUML source code
        color: Hex color code (without #) to verify appears in SVG

    Raises:
        AssertionError: If PlantUML fails or color not found in output
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        puml_file = Path(tmpdir) / "test.puml"
        svg_file = Path(tmpdir) / "test.svg"
        puml_file.write_text(puml)

        result = subprocess.run(
            ["plantuml", "-tsvg", str(puml_file)],
            capture_output=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML failed: {result.stderr.decode()}"
        assert svg_file.exists(), "SVG file not created"

        svg_content = svg_file.read_text()

        # Check for color in SVG (case-insensitive)
        assert color.upper() in svg_content.upper(), (
            f"Color #{color} not found in SVG output. "
            f"PlantUML accepted syntax but did not render the style."
        )


def run_plantuml_and_verify_pattern(puml: str, pattern: str) -> None:
    """Run PlantUML and verify a pattern appears in SVG output.

    Args:
        puml: PlantUML source code
        pattern: Text pattern to verify appears in SVG

    Raises:
        AssertionError: If PlantUML fails or pattern not found in output
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        puml_file = Path(tmpdir) / "test.puml"
        svg_file = Path(tmpdir) / "test.svg"
        puml_file.write_text(puml)

        result = subprocess.run(
            ["plantuml", "-tsvg", str(puml_file)],
            capture_output=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML failed: {result.stderr.decode()}"
        assert svg_file.exists(), "SVG file not created"

        svg_content = svg_file.read_text()

        assert pattern in svg_content, (
            f"Pattern '{pattern}' not found in SVG output. "
            f"PlantUML accepted syntax but did not render the style."
        )


# =============================================================================
# Sequence Diagram Selectors - All verified to render
# =============================================================================


@pytest.mark.skipif(not plantuml_available(), reason="PlantUML not available")
class TestSequenceDiagramStyles:
    """Test sequence diagram CSS-style selectors that PlantUML renders."""

    def test_participant_background(self):
        """Verify participant background color renders."""
        with sequence_diagram(
            diagram_style={"participant": {"background": "#E3F2FD"}}
        ) as d:
            a, b = d.participants("Alice", "Bob")
            d.message(a, b, "Hello")
        run_plantuml_and_verify_color(render(d.build()), "E3F2FD")

    def test_actor_background(self):
        """Verify actor background color renders."""
        with sequence_diagram(
            diagram_style={"actor": {"background": "#C8E6C9"}}
        ) as d:
            d.actor("User")
            d.participant("System")
            d.message("User", "System", "Request")
        run_plantuml_and_verify_color(render(d.build()), "C8E6C9")

    def test_boundary_background(self):
        """Verify boundary background color renders."""
        with sequence_diagram(
            diagram_style={"boundary": {"background": "#FFCCBC"}}
        ) as d:
            d.boundary("WebUI")
            d.participant("Backend")
            d.message("WebUI", "Backend", "Request")
        run_plantuml_and_verify_color(render(d.build()), "FFCCBC")

    def test_control_background(self):
        """Verify control background color renders."""
        with sequence_diagram(
            diagram_style={"control": {"background": "#D1C4E9"}}
        ) as d:
            d.control("Controller")
            d.participant("Service")
            d.message("Controller", "Service", "Command")
        run_plantuml_and_verify_color(render(d.build()), "D1C4E9")

    def test_entity_background(self):
        """Verify entity background color renders."""
        with sequence_diagram(
            diagram_style={"entity": {"background": "#B2DFDB"}}
        ) as d:
            d.entity("User")
            d.participant("DB")
            d.message("User", "DB", "Save")
        run_plantuml_and_verify_color(render(d.build()), "B2DFDB")

    def test_database_background(self):
        """Verify database background color renders."""
        with sequence_diagram(
            diagram_style={"database": {"background": "#BBDEFB"}}
        ) as d:
            d.database("PostgreSQL")
            d.participant("App")
            d.message("App", "PostgreSQL", "Query")
        run_plantuml_and_verify_color(render(d.build()), "BBDEFB")

    def test_collections_background(self):
        """Verify collections background color renders."""
        with sequence_diagram(
            diagram_style={"collections": {"background": "#F0F4C3"}}
        ) as d:
            d.collections("Workers")
            d.participant("Queue")
            d.message("Queue", "Workers", "Job")
        run_plantuml_and_verify_color(render(d.build()), "F0F4C3")

    def test_queue_background(self):
        """Verify queue background color renders."""
        with sequence_diagram(
            diagram_style={"queue": {"background": "#FFE0B2"}}
        ) as d:
            d.queue("MessageQueue")
            d.participant("Consumer")
            d.message("MessageQueue", "Consumer", "Message")
        run_plantuml_and_verify_color(render(d.build()), "FFE0B2")

    def test_arrow_color(self):
        """Verify arrow line color renders."""
        with sequence_diagram(
            diagram_style={"arrow": {"line_color": "#FF5722"}}
        ) as d:
            a, b = d.participants("A", "B")
            d.message(a, b, "Test")
        run_plantuml_and_verify_color(render(d.build()), "FF5722")

    def test_note_background(self):
        """Verify note background color renders."""
        with sequence_diagram(
            diagram_style={"note": {"background": "#FFF9C4"}}
        ) as d:
            a, b = d.participants("A", "B")
            d.message(a, b, "Test")
            d.note("Important note", over=[a])
        run_plantuml_and_verify_color(render(d.build()), "FFF9C4")

    def test_box_background(self):
        """Verify box background color renders."""
        with sequence_diagram(
            diagram_style={"box": {"background": "#E8EAF6"}}
        ) as d:
            with d.box("MyBox") as box:
                box.participant("A")
            d.participant("B")
            d.message("A", "B", "Request")
        run_plantuml_and_verify_color(render(d.build()), "E8EAF6")

    def test_group_background(self):
        """Verify group background color renders."""
        with sequence_diagram(
            diagram_style={"group": {"background": "#FFF3E0"}}
        ) as d:
            a = d.participant("A")
            b = d.participant("B")
            with d.group("MyGroup") as grp:
                grp.message(a, b, "Hello")
        run_plantuml_and_verify_color(render(d.build()), "FFF3E0")

    def test_separator_background(self):
        """Verify separator (divider) background color renders."""
        with sequence_diagram(
            diagram_style={"divider": {"background": "#E1F5FE"}}
        ) as d:
            a = d.participant("A")
            b = d.participant("B")
            d.message(a, b, "Before")
            d.divider("Section Break")
            d.message(a, b, "After")
        run_plantuml_and_verify_color(render(d.build()), "E1F5FE")

    def test_reference_background(self):
        """Verify reference background color renders."""
        with sequence_diagram(
            diagram_style={"reference": {"background": "#F3E5F5"}}
        ) as d:
            a = d.participant("A")
            b = d.participant("B")
            d.ref(a, b, label="See other diagram")
        run_plantuml_and_verify_color(render(d.build()), "F3E5F5")


# =============================================================================
# Class Diagram Selectors - Only class_, arrow, note verified to render
# =============================================================================


@pytest.mark.skipif(not plantuml_available(), reason="PlantUML not available")
class TestClassDiagramStyles:
    """Test class diagram CSS-style selectors that PlantUML renders."""

    def test_class_background(self):
        """Verify class background color renders."""
        with class_diagram(
            diagram_style={"class_": {"background": "#E3F2FD"}}
        ) as d:
            d.class_("User")
        run_plantuml_and_verify_color(render(d.build()), "E3F2FD")

    def test_class_line_color(self):
        """Verify class border color renders."""
        with class_diagram(
            diagram_style={"class_": {"line_color": "#1976D2"}}
        ) as d:
            d.class_("User")
        run_plantuml_and_verify_color(render(d.build()), "1976D2")

    def test_arrow_color(self):
        """Verify arrow line color renders."""
        with class_diagram(
            diagram_style={"arrow": {"line_color": "#4CAF50"}}
        ) as d:
            a = d.class_("A")
            b = d.class_("B")
            d.associates(a, b)
        run_plantuml_and_verify_color(render(d.build()), "4CAF50")

    def test_note_background(self):
        """Verify note background color renders."""
        with class_diagram(
            diagram_style={"note": {"background": "#FFFDE7"}}
        ) as d:
            d.class_("User")
            d.note("A note", position="right")
        run_plantuml_and_verify_color(render(d.build()), "FFFDE7")


# =============================================================================
# State Diagram Selectors - All verified to render
# =============================================================================


@pytest.mark.skipif(not plantuml_available(), reason="PlantUML not available")
class TestStateDiagramStyles:
    """Test state diagram CSS-style selectors that PlantUML renders."""

    def test_state_background(self):
        """Verify state background color renders."""
        with state_diagram(
            diagram_style={"state": {"background": "#E3F2FD"}}
        ) as d:
            a = d.state("Active")
            b = d.state("Idle")
            d.arrow(a, b)
        run_plantuml_and_verify_color(render(d.build()), "E3F2FD")

    def test_state_line_color(self):
        """Verify state border color renders."""
        with state_diagram(
            diagram_style={"state": {"line_color": "#1565C0"}}
        ) as d:
            a = d.state("Active")
            b = d.state("Idle")
            d.arrow(a, b)
        run_plantuml_and_verify_color(render(d.build()), "1565C0")

    def test_arrow_color(self):
        """Verify arrow line color renders."""
        with state_diagram(
            diagram_style={"arrow": {"line_color": "#FF5722"}}
        ) as d:
            a = d.state("A")
            b = d.state("B")
            d.arrow(a, b)
        run_plantuml_and_verify_color(render(d.build()), "FF5722")

    def test_note_background(self):
        """Verify note background color renders."""
        with state_diagram(
            diagram_style={"note": {"background": "#FFF9C4"}}
        ) as d:
            d.state("Active", note="Important state")
        run_plantuml_and_verify_color(render(d.build()), "FFF9C4")


# =============================================================================
# Activity Diagram Selectors - All verified to render
# =============================================================================


@pytest.mark.skipif(not plantuml_available(), reason="PlantUML not available")
class TestActivityDiagramStyles:
    """Test activity diagram CSS-style selectors that PlantUML renders."""

    def test_activity_background(self):
        """Verify activity background color renders."""
        with activity_diagram(
            diagram_style={"activity": {"background": "#C8E6C9"}}
        ) as d:
            d.start()
            d.action("Process")
            d.stop()
        run_plantuml_and_verify_color(render(d.build()), "C8E6C9")

    def test_activity_line_color(self):
        """Verify activity border color renders."""
        with activity_diagram(
            diagram_style={"activity": {"line_color": "#388E3C"}}
        ) as d:
            d.start()
            d.action("Process")
            d.stop()
        run_plantuml_and_verify_color(render(d.build()), "388E3C")

    def test_diamond_background(self):
        """Verify diamond (decision) background color renders."""
        with activity_diagram(
            diagram_style={"diamond": {"background": "#FFF9C4"}}
        ) as d:
            d.start()
            with d.if_("condition") as branch:
                branch.action("Yes")
            d.stop()
        run_plantuml_and_verify_color(render(d.build()), "FFF9C4")

    def test_arrow_color(self):
        """Verify arrow line color renders."""
        with activity_diagram(
            diagram_style={"arrow": {"line_color": "#FF5722"}}
        ) as d:
            d.start()
            d.action("Step")
            d.stop()
        run_plantuml_and_verify_color(render(d.build()), "FF5722")

    def test_partition_background(self):
        """Verify partition background color renders."""
        with activity_diagram(
            diagram_style={"partition": {"background": "#E1BEE7"}}
        ) as d:
            d.start()
            with d.partition("MyPartition") as p:
                p.action("Inside")
            d.stop()
        run_plantuml_and_verify_color(render(d.build()), "E1BEE7")

    def test_note_background(self):
        """Verify note background color renders."""
        with activity_diagram(
            diagram_style={"note": {"background": "#FFFDE7"}}
        ) as d:
            d.start()
            d.action("Step")
            d.note("A note", position="right")
            d.stop()
        run_plantuml_and_verify_color(render(d.build()), "FFFDE7")


# =============================================================================
# Component Diagram Selectors - component, arrow, note verified to render
# =============================================================================


@pytest.mark.skipif(not plantuml_available(), reason="PlantUML not available")
class TestComponentDiagramStyles:
    """Test component diagram CSS-style selectors that PlantUML renders."""

    def test_component_background(self):
        """Verify component background color renders."""
        with component_diagram(
            diagram_style={"component": {"background": "#E1BEE7"}}
        ) as d:
            d.component("WebServer")
        run_plantuml_and_verify_color(render(d.build()), "E1BEE7")

    def test_component_line_color(self):
        """Verify component border color renders."""
        with component_diagram(
            diagram_style={"component": {"line_color": "#7B1FA2"}}
        ) as d:
            d.component("WebServer")
        run_plantuml_and_verify_color(render(d.build()), "7B1FA2")

    def test_arrow_color(self):
        """Verify arrow line color renders."""
        with component_diagram(
            diagram_style={"arrow": {"line_color": "#FF5722"}}
        ) as d:
            a = d.component("A")
            b = d.component("B")
            d.depends(a, b)
        run_plantuml_and_verify_color(render(d.build()), "FF5722")

    def test_note_background(self):
        """Verify note background color renders."""
        with component_diagram(
            diagram_style={"note": {"background": "#FFF9C4"}}
        ) as d:
            c = d.component("MyComponent")
            d.note("A note", target=c)
        run_plantuml_and_verify_color(render(d.build()), "FFF9C4")

    def test_package_background(self):
        """Verify package container background color renders."""
        with component_diagram(
            diagram_style={"package": {"background": "#C8E6C9"}}
        ) as d:
            with d.package("Services"):
                d.component("API")
        run_plantuml_and_verify_color(render(d.build()), "C8E6C9")

    def test_node_background(self):
        """Verify node container background color renders."""
        with component_diagram(
            diagram_style={"node": {"background": "#BBDEFB"}}
        ) as d:
            with d.node("Server"):
                d.component("App")
        run_plantuml_and_verify_color(render(d.build()), "BBDEFB")

    def test_folder_background(self):
        """Verify folder container background color renders."""
        with component_diagram(
            diagram_style={"folder": {"background": "#FFE0B2"}}
        ) as d:
            with d.folder("Config"):
                d.component("Settings")
        run_plantuml_and_verify_color(render(d.build()), "FFE0B2")

    def test_cloud_background(self):
        """Verify cloud container background color renders."""
        with component_diagram(
            diagram_style={"cloud": {"background": "#E1BEE7"}}
        ) as d:
            with d.cloud("AWS"):
                d.component("Lambda")
        run_plantuml_and_verify_color(render(d.build()), "E1BEE7")

    def test_database_background(self):
        """Verify database container background color renders."""
        with component_diagram(
            diagram_style={"database": {"background": "#FFCCBC"}}
        ) as d:
            with d.database("PostgreSQL"):
                d.component("Tables")
        run_plantuml_and_verify_color(render(d.build()), "FFCCBC")

    def test_frame_background(self):
        """Verify frame container background color renders."""
        with component_diagram(
            diagram_style={"frame": {"background": "#B2EBF2"}}
        ) as d:
            with d.frame("System"):
                d.component("Core")
        run_plantuml_and_verify_color(render(d.build()), "B2EBF2")


# =============================================================================
# Object Diagram Selectors - Only object verified to render
# =============================================================================


@pytest.mark.skipif(not plantuml_available(), reason="PlantUML not available")
class TestObjectDiagramStyles:
    """Test object diagram CSS-style selectors that PlantUML renders."""

    def test_object_background(self):
        """Verify object background color renders."""
        with object_diagram(
            diagram_style={"object": {"background": "#D1C4E9"}}
        ) as d:
            d.object("myObj")
        run_plantuml_and_verify_color(render(d.build()), "D1C4E9")

    def test_object_line_color(self):
        """Verify object border color renders."""
        with object_diagram(
            diagram_style={"object": {"line_color": "#512DA8"}}
        ) as d:
            d.object("myObj")
        run_plantuml_and_verify_color(render(d.build()), "512DA8")

    def test_map_background(self):
        """Verify map background color renders."""
        with object_diagram(
            diagram_style={"map": {"background": "#B3E5FC"}}
        ) as d:
            d.map("myMap", entries={"key": "value"})
        run_plantuml_and_verify_color(render(d.build()), "B3E5FC")


# =============================================================================
# ElementStyle CSS Properties - Test individual properties render
# =============================================================================


@pytest.mark.skipif(not plantuml_available(), reason="PlantUML not available")
class TestElementStyleProperties:
    """Test that individual ElementStyle CSS properties render correctly."""

    def test_background_color(self):
        """Verify BackgroundColor property renders."""
        with class_diagram(
            diagram_style={"class_": {"background": "#E3F2FD"}}
        ) as d:
            d.class_("Test")
        run_plantuml_and_verify_color(render(d.build()), "E3F2FD")

    def test_line_color(self):
        """Verify LineColor property renders."""
        with class_diagram(
            diagram_style={"class_": {"line_color": "#FF0000"}}
        ) as d:
            d.class_("Test")
        run_plantuml_and_verify_color(render(d.build()), "FF0000")

    def test_font_color(self):
        """Verify FontColor property renders."""
        with class_diagram(
            diagram_style={"class_": {"font_color": "#0000FF"}}
        ) as d:
            d.class_("Test")
        run_plantuml_and_verify_color(render(d.build()), "0000FF")

    def test_shadowing(self):
        """Verify Shadowing property renders (creates filter for shadow effect)."""
        with class_diagram(
            diagram_style={"class_": {"shadowing": True}}
        ) as d:
            d.class_("Test")
        # Shadowing creates a feGaussianBlur filter in SVG
        run_plantuml_and_verify_pattern(render(d.build()), "feGaussianBlur")

    def test_font_name(self):
        """Verify FontName property renders."""
        with class_diagram(
            diagram_style={"class_": {"font_name": "Courier"}}
        ) as d:
            d.class_("Test")
        # Font name appears in font-family attribute
        run_plantuml_and_verify_pattern(render(d.build()), 'font-family="Courier"')

    def test_font_size(self):
        """Verify FontSize property renders."""
        with class_diagram(
            diagram_style={"class_": {"font_size": 20}}
        ) as d:
            d.class_("Test")
        # Font size appears in font-size attribute
        run_plantuml_and_verify_pattern(render(d.build()), 'font-size="20"')


# =============================================================================
# DiagramArrowStyle Properties - Test arrow styling renders
# =============================================================================


@pytest.mark.skipif(not plantuml_available(), reason="PlantUML not available")
class TestArrowStyleProperties:
    """Test that DiagramArrowStyle CSS properties render correctly."""

    def test_arrow_line_color(self):
        """Verify arrow LineColor renders."""
        with sequence_diagram(
            diagram_style={"arrow": {"line_color": "#9C27B0"}}
        ) as d:
            a, b = d.participants("A", "B")
            d.message(a, b, "Test")
        run_plantuml_and_verify_color(render(d.build()), "9C27B0")

    def test_arrow_line_color_state(self):
        """Verify arrow LineColor renders in state diagrams."""
        with state_diagram(
            diagram_style={"arrow": {"line_color": "#FF5722"}}
        ) as d:
            a = d.state("A")
            b = d.state("B")
            d.arrow(a, b)
        run_plantuml_and_verify_color(render(d.build()), "FF5722")

    def test_arrow_line_color_activity(self):
        """Verify arrow LineColor renders in activity diagrams."""
        with activity_diagram(
            diagram_style={"arrow": {"line_color": "#4CAF50"}}
        ) as d:
            d.start()
            d.action("Step")
            d.stop()
        run_plantuml_and_verify_color(render(d.build()), "4CAF50")


# =============================================================================
# Comprehensive Multi-Property Tests
# =============================================================================


@pytest.mark.skipif(not plantuml_available(), reason="PlantUML not available")
class TestComprehensiveStyles:
    """Test multiple style properties together on working selectors."""

    def test_sequence_comprehensive(self):
        """Test multiple properties on sequence diagram."""
        with sequence_diagram(
            diagram_style={
                "participant": {
                    "background": "#E3F2FD",
                    "line_color": "#1976D2",
                },
                "arrow": {"line_color": "#757575"},
                "note": {"background": "#FFFDE7"},
            }
        ) as d:
            a, b = d.participants("Alice", "Bob")
            d.message(a, b, "Hello")
            d.note("A note", over=[a])
        puml = render(d.build())
        run_plantuml_and_verify_color(puml, "E3F2FD")
        run_plantuml_and_verify_color(puml, "1976D2")

    def test_class_comprehensive(self):
        """Test multiple properties on class diagram."""
        with class_diagram(
            diagram_style={
                "class_": {
                    "background": "#E3F2FD",
                    "line_color": "#1976D2",
                },
                "arrow": {"line_color": "#4CAF50"},
                "note": {"background": "#FFFDE7"},
            }
        ) as d:
            a = d.class_("User")
            b = d.class_("Order")
            d.associates(a, b)
            d.note("Entity", position="right")
        puml = render(d.build())
        run_plantuml_and_verify_color(puml, "E3F2FD")
        run_plantuml_and_verify_color(puml, "4CAF50")

    def test_state_comprehensive(self):
        """Test multiple properties on state diagram."""
        with state_diagram(
            diagram_style={
                "state": {
                    "background": "#BBDEFB",
                    "line_color": "#1565C0",
                },
                "arrow": {"line_color": "#424242"},
                "note": {"background": "#F5F5F5"},
            }
        ) as d:
            a = d.state("Active", note="Current")
            b = d.state("Inactive")
            d.arrow(a, b, label="deactivate")
        puml = render(d.build())
        run_plantuml_and_verify_color(puml, "BBDEFB")
        run_plantuml_and_verify_color(puml, "1565C0")

    def test_activity_comprehensive(self):
        """Test multiple properties on activity diagram."""
        with activity_diagram(
            diagram_style={
                "activity": {
                    "background": "#C8E6C9",
                    "line_color": "#388E3C",
                },
                "diamond": {"background": "#FFF9C4"},
                "arrow": {"line_color": "#616161"},
            }
        ) as d:
            d.start()
            d.action("Step 1")
            with d.if_("condition") as branch:
                branch.action("Yes")
            d.stop()
        puml = render(d.build())
        run_plantuml_and_verify_color(puml, "C8E6C9")
        run_plantuml_and_verify_color(puml, "FFF9C4")

    def test_component_comprehensive(self):
        """Test multiple properties on component diagram."""
        with component_diagram(
            diagram_style={
                "component": {
                    "background": "#E1BEE7",
                    "line_color": "#7B1FA2",
                },
                "arrow": {"line_color": "#9E9E9E"},
            }
        ) as d:
            web = d.component("WebServer")
            db = d.component("Database")
            d.depends(web, db)
        puml = render(d.build())
        run_plantuml_and_verify_color(puml, "E1BEE7")
        run_plantuml_and_verify_color(puml, "7B1FA2")


# =============================================================================
# JSON/YAML Diagram Selectors
# =============================================================================


@pytest.mark.skipif(not plantuml_available(), reason="PlantUML not available")
class TestJsonDiagramSelectors:
    """Test JSON diagram style selectors actually render."""

    def test_node_background(self):
        """Test node background color renders in JSON diagram."""
        with json_diagram(
            '{"name": "John", "age": 30}',
            diagram_style={"node": {"background": "#E3F2FD"}},
        ) as d:
            pass
        puml = render(d.build())
        run_plantuml_and_verify_color(puml, "E3F2FD")

    def test_highlight_background(self):
        """Test highlight background color renders in JSON diagram."""
        with json_diagram(
            '{"name": "John", "age": 30}',
            diagram_style={"highlight": {"background": "#FFEB3B"}},
        ) as d:
            d.highlight("name")
        puml = render(d.build())
        run_plantuml_and_verify_color(puml, "FFEB3B")

    def test_root_background(self):
        """Test diagram root background color renders."""
        with json_diagram(
            '{"key": "value"}',
            diagram_style={"background": "#FAFAFA"},
        ) as d:
            pass
        puml = render(d.build())
        run_plantuml_and_verify_color(puml, "FAFAFA")


@pytest.mark.skipif(not plantuml_available(), reason="PlantUML not available")
class TestYamlDiagramSelectors:
    """Test YAML diagram style selectors actually render."""

    def test_node_background(self):
        """Test node background color renders in YAML diagram."""
        with yaml_diagram(
            "name: John\nage: 30",
            diagram_style={"node": {"background": "#E8F5E9"}},
        ) as d:
            pass
        puml = render(d.build())
        run_plantuml_and_verify_color(puml, "E8F5E9")

    def test_highlight_background(self):
        """Test highlight background color renders in YAML diagram."""
        with yaml_diagram(
            "name: John\nage: 30",
            diagram_style={"highlight": {"background": "#FFF9C4"}},
        ) as d:
            d.highlight("name")
        puml = render(d.build())
        run_plantuml_and_verify_color(puml, "FFF9C4")


# =============================================================================
# WBS Diagram Selectors
# =============================================================================


@pytest.mark.skipif(not plantuml_available(), reason="PlantUML not available")
class TestWbsDiagramSelectors:
    """Test WBS diagram style selectors actually render."""

    def test_node_background(self):
        """Test node background color renders in WBS diagram."""
        with wbs_diagram(
            diagram_style={"node": {"background": "#E3F2FD"}},
        ) as d:
            with d.node("Project") as proj:
                proj.leaf("Task 1")
        puml = render(d.build())
        run_plantuml_and_verify_color(puml, "E3F2FD")

    def test_root_node_background(self):
        """Test root node background color renders in WBS diagram."""
        with wbs_diagram(
            diagram_style={"root_node": {"background": "#FFA500"}},
        ) as d:
            with d.node("Project") as proj:
                proj.leaf("Task 1")
        puml = render(d.build())
        run_plantuml_and_verify_color(puml, "FFA500")

    def test_leaf_node_background(self):
        """Test leaf node background color renders in WBS diagram."""
        with wbs_diagram(
            diagram_style={"leaf_node": {"background": "#90EE90"}},
        ) as d:
            with d.node("Project") as proj:
                proj.leaf("Task 1")
        puml = render(d.build())
        run_plantuml_and_verify_color(puml, "90EE90")

    def test_diagram_background(self):
        """Test diagram background color renders in WBS diagram."""
        with wbs_diagram(
            diagram_style={"background": "#FAFAFA"},
        ) as d:
            with d.node("Project") as proj:
                proj.leaf("Task 1")
        puml = render(d.build())
        run_plantuml_and_verify_color(puml, "FAFAFA")

    def test_inline_node_color(self):
        """Test inline node color renders in WBS diagram."""
        with wbs_diagram() as d:
            with d.node("Project", color="#FF5722") as proj:
                proj.leaf("Task 1")
        puml = render(d.build())
        run_plantuml_and_verify_color(puml, "FF5722")
