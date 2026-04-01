"""Tests for sequence diagram boundary messages (incoming/outgoing)."""

import subprocess

import pytest

from plantuml_compose.composers.sequence import sequence_diagram
from plantuml_compose.primitives.sequence import GroupBlock, Message
from plantuml_compose.renderers import render


class TestSequenceBoundaryMessages:

    def test_incoming_message(self):
        d = sequence_diagram()
        p = d.participants
        e = d.events
        alice = p.participant("Alice")
        d.add(alice)
        d.phase("Flow", [
            e.incoming(alice, "request"),
        ])
        output = render(d)
        assert "[-> Alice : request" in output

    def test_outgoing_message(self):
        d = sequence_diagram()
        p = d.participants
        e = d.events
        alice = p.participant("Alice")
        d.add(alice)
        d.phase("Flow", [
            e.outgoing(alice, "response"),
        ])
        output = render(d)
        assert "Alice ->] : response" in output

    def test_incoming_dotted(self):
        d = sequence_diagram()
        p = d.participants
        e = d.events
        alice = p.participant("Alice")
        d.add(alice)
        d.phase("Flow", [
            e.incoming(alice, "async", line_style="dotted"),
        ])
        output = render(d)
        assert "[--> Alice : async" in output

    def test_outgoing_thin_head(self):
        d = sequence_diagram()
        p = d.participants
        e = d.events
        alice = p.participant("Alice")
        d.add(alice)
        d.phase("Flow", [
            e.outgoing(alice, "fast", arrow_head="thin"),
        ])
        output = render(d)
        assert "Alice ->>] : fast" in output

    def test_raw_bracket_source(self):
        """Using '[' directly in e.message() should work the same as e.incoming()."""
        d = sequence_diagram()
        p = d.participants
        e = d.events
        alice = p.participant("Alice")
        d.add(alice)
        d.phase("Flow", [
            e.message("[", alice, "direct bracket syntax"),
        ])
        output = render(d)
        assert "[-> Alice : direct bracket syntax" in output

    def test_raw_bracket_target(self):
        """Using ']' directly in e.message() should work the same as e.outgoing()."""
        d = sequence_diagram()
        p = d.participants
        e = d.events
        alice = p.participant("Alice")
        d.add(alice)
        d.phase("Flow", [
            e.message(alice, "]", "direct bracket syntax"),
        ])
        output = render(d)
        assert "Alice ->] : direct bracket syntax" in output

    def test_incoming_in_phase(self):
        """Boundary messages work inside d.phase() event lists."""
        d = sequence_diagram()
        p = d.participants
        e = d.events
        alice = p.participant("Alice")
        bob = p.participant("Bob")
        d.add(alice, bob)
        d.phase("External Call", [
            e.incoming(alice, "request"),
            e.message(alice, bob, "forward"),
            e.outgoing(bob, "response"),
        ])
        result = d.build()
        group = [el for el in result.elements if isinstance(el, GroupBlock)][0]
        assert len(group.elements) == 3
        assert isinstance(group.elements[0], Message)
        assert group.elements[0].source == "["
        assert isinstance(group.elements[2], Message)
        assert group.elements[2].target == "]"

    def test_incoming_with_activation(self):
        d = sequence_diagram()
        p = d.participants
        e = d.events
        alice = p.participant("Alice")
        d.add(alice)
        d.phase("Flow", [
            e.incoming(alice, "start", activation="activate"),
        ])
        output = render(d)
        assert "[-> Alice++ : start" in output

    def test_outgoing_with_style(self):
        d = sequence_diagram()
        p = d.participants
        e = d.events
        alice = p.participant("Alice")
        d.add(alice)
        d.phase("Flow", [
            e.outgoing(alice, "alert", style={"color": "red"}),
        ])
        output = render(d)
        assert "Alice -[#red]->] : alert" in output

    def test_incoming_no_label(self):
        d = sequence_diagram()
        p = d.participants
        e = d.events
        alice = p.participant("Alice")
        d.add(alice)
        d.phase("Flow", [
            e.incoming(alice),
        ])
        output = render(d)
        # Should have "[-> Alice" without a label part
        assert "[-> Alice" in output
        # No colon since no label
        lines = output.split("\n")
        boundary_lines = [l for l in lines if "[-> Alice" in l]
        assert len(boundary_lines) == 1
        assert " : " not in boundary_lines[0]

    def test_outgoing_no_label(self):
        d = sequence_diagram()
        p = d.participants
        e = d.events
        alice = p.participant("Alice")
        d.add(alice)
        d.phase("Flow", [
            e.outgoing(alice),
        ])
        output = render(d)
        lines = output.split("\n")
        boundary_lines = [l for l in lines if "Alice ->]" in l]
        assert len(boundary_lines) == 1
        assert " : " not in boundary_lines[0]


class TestSequenceBoundaryPlantUML:

    @pytest.fixture
    def plantuml_check(self):
        try:
            result = subprocess.run(
                ["plantuml", "-version"],
                capture_output=True, timeout=10,
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def test_boundary_messages_valid(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = sequence_diagram(title="Boundary Messages")
        p = d.participants
        e = d.events

        alice, bob = d.add(p.participant("Alice"), p.participant("Bob"))

        d.phase("Incoming", [
            e.incoming(alice, "request"),
            e.message(alice, bob, "forward"),
        ])

        d.phase("Outgoing", [
            e.message(bob, alice, "result"),
            e.outgoing(alice, "response"),
        ])

        d.phase("Variations", [
            e.incoming(alice, "dotted", line_style="dotted"),
            e.outgoing(bob, "thin", arrow_head="thin"),
            e.incoming(bob, "styled", style={"color": "red"}),
        ])

        puml_file = tmp_path / "boundary.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"
