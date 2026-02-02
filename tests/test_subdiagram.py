"""Tests for sub-diagram embedding functionality.

Tests the EmbeddedDiagram primitive and embed() method on diagram builders,
verifying that diagrams can be embedded inside notes, messages, legends, etc.
"""

import sys
from pathlib import Path

import pytest

# Add tools directory to path for shared utilities
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
from svg_utils import check_svg_for_subdiagram_errors

from plantuml_compose import render, EmbeddedDiagram, EmbeddableContent
from plantuml_compose.builders.sequence import sequence_diagram
from plantuml_compose.builders.component import component_diagram
from plantuml_compose.builders.class_ import class_diagram
from plantuml_compose.builders.state import state_diagram
from plantuml_compose.builders.activity import activity_diagram
from plantuml_compose.builders.deployment import deployment_diagram
from plantuml_compose.builders.usecase import usecase_diagram
from plantuml_compose.builders.object_ import object_diagram
from plantuml_compose.builders.timing import timing_diagram
from plantuml_compose.builders.network import network_diagram
from plantuml_compose.builders.gantt import gantt_diagram
from plantuml_compose.builders.mindmap import mindmap_diagram
from plantuml_compose.builders.wbs import wbs_diagram
from plantuml_compose.builders.json_ import json_diagram, yaml_diagram
from plantuml_compose.renderers.common import render_embeddable_content


class TestEmbeddedDiagram:
    """Tests for EmbeddedDiagram primitive."""

    def test_multiline_render(self):
        """Test multi-line render format (default)."""
        embedded = EmbeddedDiagram(content="component API\ncomponent DB")
        result = embedded.render(inline=False)

        assert result.startswith("{{")
        assert result.endswith("}}")
        # Style block has newlines for proper parsing
        assert "<style>" in result
        assert "root { BackgroundColor transparent }" in result
        assert "</style>" in result
        assert "component API" in result
        assert "component DB" in result

    def test_inline_render(self):
        """Test inline render format with %breakline()."""
        embedded = EmbeddedDiagram(content="component API\ncomponent DB")
        result = embedded.render(inline=True)

        # Inline mode uses double braces without spaces: {{content}}
        assert result.startswith("{{")
        assert result.endswith("}}")
        assert "%breakline()" in result
        # Content should be on single line for inline mode
        assert "\n" not in result

    def test_no_transparency(self):
        """Test that transparent=False omits background style."""
        embedded = EmbeddedDiagram(content="component API", transparent=False)
        result = embedded.render()

        assert "BackgroundColor transparent" not in result
        assert "component API" in result

    def test_empty_content(self):
        """Test with empty content."""
        embedded = EmbeddedDiagram(content="")
        result = embedded.render()

        assert "{{" in result
        assert "}}" in result


class TestRenderEmbeddableContent:
    """Tests for the render_embeddable_content helper function."""

    def test_with_string(self):
        """Test rendering plain string content."""
        result = render_embeddable_content("Hello World")
        assert result == "Hello World"

    def test_with_embedded_diagram(self):
        """Test rendering EmbeddedDiagram content."""
        embedded = EmbeddedDiagram(content="component API")
        result = render_embeddable_content(embedded)

        assert "{{" in result
        assert "component API" in result
        assert "}}" in result

    def test_with_none(self):
        """Test rendering None content."""
        result = render_embeddable_content(None)
        assert result == ""

    def test_inline_mode_with_string(self):
        """Test inline mode escapes newlines for regular text."""
        result = render_embeddable_content("line1\nline2", inline=True)
        assert "%n()" in result
        assert "\n" not in result

    def test_inline_mode_with_embedded_diagram(self):
        """Test inline mode uses %breakline() for embedded diagrams."""
        embedded = EmbeddedDiagram(content="component API\ncomponent DB")
        result = render_embeddable_content(embedded, inline=True)

        assert "%breakline()" in result


class TestBuilderEmbedMethod:
    """Tests for embed() method on diagram builders."""

    def test_sequence_diagram_embed(self):
        """Test embed() on sequence diagram builder."""
        with sequence_diagram() as d:
            alice = d.participant("Alice")
            bob = d.participant("Bob")
            d.message(alice, bob, "Hello")

        embedded = d.embed()
        assert isinstance(embedded, EmbeddedDiagram)
        assert "participant" in embedded.content
        assert "@startuml" not in embedded.content
        assert "@enduml" not in embedded.content

    def test_component_diagram_embed(self):
        """Test embed() on component diagram builder."""
        with component_diagram() as d:
            api = d.component("API")
            db = d.component("DB")
            d.link(api, db)

        embedded = d.embed()
        assert isinstance(embedded, EmbeddedDiagram)
        assert "component" in embedded.content.lower()
        assert "@startuml" not in embedded.content

    def test_class_diagram_embed(self):
        """Test embed() on class diagram builder."""
        with class_diagram() as d:
            user = d.class_("User")
            order = d.class_("Order")

        embedded = d.embed()
        assert isinstance(embedded, EmbeddedDiagram)
        assert "@startuml" not in embedded.content

    def test_state_diagram_embed(self):
        """Test embed() on state diagram builder."""
        with state_diagram() as d:
            idle = d.state("Idle")
            active = d.state("Active")
            d.arrow(idle, active)

        embedded = d.embed()
        assert isinstance(embedded, EmbeddedDiagram)
        assert "@startuml" not in embedded.content

    def test_activity_diagram_embed(self):
        """Test embed() on activity diagram builder."""
        with activity_diagram() as d:
            d.start()
            d.action("Do something")
            d.stop()

        embedded = d.embed()
        assert isinstance(embedded, EmbeddedDiagram)
        assert "@startuml" not in embedded.content

    def test_deployment_diagram_embed(self):
        """Test embed() on deployment diagram builder."""
        with deployment_diagram() as d:
            with d.node_nested("Server"):
                pass
            d.database("MySQL")

        embedded = d.embed()
        assert isinstance(embedded, EmbeddedDiagram)
        assert "@startuml" not in embedded.content

    def test_usecase_diagram_embed(self):
        """Test embed() on use case diagram builder."""
        with usecase_diagram() as d:
            d.actor("User")
            d.usecase("Login")

        embedded = d.embed()
        assert isinstance(embedded, EmbeddedDiagram)
        assert "@startuml" not in embedded.content

    def test_object_diagram_embed(self):
        """Test embed() on object diagram builder."""
        with object_diagram() as d:
            d.object("user1")

        embedded = d.embed()
        assert isinstance(embedded, EmbeddedDiagram)
        assert "@startuml" not in embedded.content

    def test_timing_diagram_embed(self):
        """Test embed() on timing diagram builder."""
        with timing_diagram() as d:
            d.robust("Clock", alias="C")

        embedded = d.embed()
        assert isinstance(embedded, EmbeddedDiagram)
        assert "@startuml" not in embedded.content

    def test_network_diagram_embed(self):
        """Test embed() on network diagram builder."""
        with network_diagram() as d:
            with d.network("dmz") as net:
                net.node("web01")

        embedded = d.embed()
        assert isinstance(embedded, EmbeddedDiagram)
        assert "@startuml" not in embedded.content

    def test_gantt_diagram_embed(self):
        """Test embed() on gantt diagram builder."""
        with gantt_diagram() as d:
            d.task("Task 1", days=10)

        embedded = d.embed()
        assert isinstance(embedded, EmbeddedDiagram)
        # Specialized diagrams keep their markers for PlantUML to identify the type
        assert "@startgantt" in embedded.content
        assert "@endgantt" in embedded.content

    def test_mindmap_diagram_embed(self):
        """Test embed() on mindmap diagram builder."""
        with mindmap_diagram() as d:
            with d.node("Root") as root:
                root.leaf("Leaf 1")

        embedded = d.embed()
        assert isinstance(embedded, EmbeddedDiagram)
        # Specialized diagrams keep their markers for PlantUML to identify the type
        assert "@startmindmap" in embedded.content
        assert "@endmindmap" in embedded.content

    def test_wbs_diagram_embed(self):
        """Test embed() on WBS diagram builder."""
        with wbs_diagram() as d:
            with d.node("Project") as proj:
                proj.leaf("Task 1")

        embedded = d.embed()
        assert isinstance(embedded, EmbeddedDiagram)
        # Specialized diagrams keep their markers for PlantUML to identify the type
        assert "@startwbs" in embedded.content
        assert "@endwbs" in embedded.content

    def test_json_diagram_embed(self):
        """Test embed() on JSON diagram builder."""
        with json_diagram({"name": "John"}) as d:
            pass

        embedded = d.embed()
        assert isinstance(embedded, EmbeddedDiagram)
        # Specialized diagrams keep their markers for PlantUML to identify the type
        assert "@startjson" in embedded.content
        assert "@endjson" in embedded.content

    def test_yaml_diagram_embed(self):
        """Test embed() on YAML diagram builder."""
        with yaml_diagram({"name": "John"}) as d:
            pass

        embedded = d.embed()
        assert isinstance(embedded, EmbeddedDiagram)
        # Specialized diagrams keep their markers for PlantUML to identify the type
        assert "@startyaml" in embedded.content
        assert "@endyaml" in embedded.content

    def test_embed_with_transparent_false(self):
        """Test embed() with transparent=False."""
        with component_diagram() as d:
            d.component("API")

        embedded = d.embed(transparent=False)
        assert embedded.transparent is False


class TestEmbeddingInNotes:
    """Tests for embedding diagrams in notes."""

    def test_sequence_note_with_embedded_diagram(self):
        """Test embedding a diagram in a sequence note."""
        # Create the sub-diagram
        with component_diagram() as arch:
            api = arch.component("API")
            db = arch.component("DB")
            arch.link(api, db)

        # Embed in a sequence diagram note
        with sequence_diagram() as d:
            alice = d.participant("Alice")
            bob = d.participant("Bob")
            d.note(arch.embed(), position="right", of=alice)

        output = render(d.build())
        assert "{{" in output
        assert "}}" in output
        assert "BackgroundColor transparent" in output

    def test_activity_note_with_embedded_diagram(self):
        """Test embedding a diagram in an activity note."""
        with component_diagram() as arch:
            arch.component("Service")

        with activity_diagram() as d:
            d.start()
            d.action("Process")
            d.note(arch.embed(), position="right")
            d.stop()

        output = render(d.build())
        assert "{{" in output
        assert "note right" in output

    def test_component_note_with_embedded_diagram(self):
        """Test embedding a diagram in a component note."""
        with activity_diagram() as flow:
            flow.start()
            flow.action("Process")
            flow.stop()

        with component_diagram() as d:
            api = d.component("API")
            d.note(flow.embed(), target=api, position="right")

        output = render(d.build())
        assert "{{" in output
        assert "note right of" in output


class TestEmbeddingInMessages:
    """Tests for embedding diagrams in sequence messages (inline mode)."""

    def test_sequence_message_with_embedded_diagram(self):
        """Test embedding a diagram in a sequence message label."""
        with component_diagram() as arch:
            arch.component("API")

        with sequence_diagram() as d:
            alice = d.participant("Alice")
            bob = d.participant("Bob")
            d.message(alice, bob, arch.embed())

        output = render(d.build())
        # Inline mode should use {{ }} with %breakline()
        assert "{{" in output
        assert "%breakline()" in output


class TestEmbeddingInLegends:
    """Tests for embedding diagrams in legends."""

    def test_legend_with_embedded_diagram(self):
        """Test embedding a diagram in a legend."""
        from plantuml_compose.primitives.common import Legend

        with component_diagram() as arch:
            arch.component("API")
            arch.component("DB")

        # Create a diagram with a legend containing embedded content
        with sequence_diagram() as d:
            alice = d.participant("Alice")

        # Build the diagram with embedded legend content
        diagram = d.build()
        # Replace legend with one containing embedded content
        from dataclasses import replace
        diagram_with_legend = replace(
            diagram,
            legend=Legend(content=arch.embed(), position="right")
        )

        output = render(diagram_with_legend)
        assert "legend" in output
        assert "{{" in output
        assert "endlegend" in output


class TestSubdiagramRendering:
    """Tests that verify subdiagrams render correctly using local PlantUML.

    These tests generate SVG using the local plantuml command and check for
    errors in the rendered output, including errors in base64-encoded
    subdiagram images.
    """

    def test_component_in_sequence_note_renders_without_error(self, render_and_parse_svg):
        """Test that a component diagram embedded in a sequence note renders correctly."""
        with component_diagram() as arch:
            api = arch.component("API")
            db = arch.component("DB")
            arch.link(api, db)

        with sequence_diagram() as d:
            client = d.participant("Client")
            server = d.participant("Server")
            d.message(client, server, "request")
            d.note(arch.embed(), of=server, position="right")

        output = render(d.build())
        svg = render_and_parse_svg(output)
        error = check_svg_for_subdiagram_errors(svg)
        assert error is None, f"Subdiagram render error: {error}"

    def test_state_in_activity_note_renders_without_error(self, render_and_parse_svg):
        """Test that a state diagram embedded in an activity note renders correctly."""
        with state_diagram() as states:
            idle = states.state("Idle")
            active = states.state("Active")
            states.arrow(idle, active)

        with activity_diagram() as d:
            d.start()
            d.action("Process")
            d.note(states.embed(), position="right")
            d.stop()

        output = render(d.build())
        svg = render_and_parse_svg(output)
        error = check_svg_for_subdiagram_errors(svg)
        assert error is None, f"Subdiagram render error: {error}"

    def test_class_in_sequence_note_renders_without_error(self, render_and_parse_svg):
        """Test that a class diagram embedded in a sequence note renders correctly."""
        with class_diagram() as model:
            model.class_("User")
            model.class_("Order")

        with sequence_diagram() as d:
            api = d.participant("API")
            d.note(model.embed(), of=api, position="left")

        output = render(d.build())
        svg = render_and_parse_svg(output)
        error = check_svg_for_subdiagram_errors(svg)
        assert error is None, f"Subdiagram render error: {error}"

    def test_inline_embed_in_message_renders_without_error(self, render_and_parse_svg):
        """Test that an inline embedded diagram in a message label renders correctly."""
        with component_diagram() as mini:
            mini.component("Data")

        with sequence_diagram() as d:
            a = d.participant("Sender")
            b = d.participant("Receiver")
            d.message(a, b, mini.embed())

        output = render(d.build())
        svg = render_and_parse_svg(output)
        error = check_svg_for_subdiagram_errors(svg)
        assert error is None, f"Subdiagram render error: {error}"


class TestIntegration:
    """Integration tests for sub-diagram embedding."""

    def test_complex_embedding_scenario(self):
        """Test a complex scenario with multiple embedded diagrams."""
        # Architecture diagram
        with component_diagram() as arch:
            api = arch.component("API Gateway")
            svc = arch.component("Service")
            db = arch.component("Database")
            arch.link(api, svc)
            arch.link(svc, db)

        # Embed in a sequence diagram
        with sequence_diagram(title="System Interaction") as d:
            client = d.participant("Client")
            server = d.participant("Server")

            d.message(client, server, "Request")
            d.note(arch.embed(), of=server, position="right")
            d.message(server, client, "Response")

        output = render(d.build())

        # Verify structure
        assert "@startuml" in output
        assert "@enduml" in output
        assert "title System Interaction" in output
        assert "{{" in output
        assert "}}" in output
        assert "BackgroundColor transparent" in output
        # The embedded content shouldn't have @startuml
        assert output.count("@startuml") == 1

    def test_rendered_output_is_valid_plantuml_syntax(self):
        """Test that the rendered output follows PlantUML syntax rules."""
        with component_diagram() as inner:
            inner.component("Inner")

        with sequence_diagram() as d:
            alice = d.participant("Alice")
            d.note(inner.embed(), of=alice, position="left")

        output = render(d.build())

        # Basic syntax checks
        lines = output.split("\n")
        assert lines[0] == "@startuml"
        assert lines[-1] == "@enduml"

        # Check for balanced {{ }}
        assert output.count("{{") == output.count("}}")
