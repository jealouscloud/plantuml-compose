"""Tests for the state diagram composer."""

import subprocess

import pytest

from plantuml_compose.composers.state import state_diagram
from plantuml_compose.primitives.common import Label, Note
from plantuml_compose.primitives.state import (
    CompositeState,
    StateDiagram,
    StateNode,
    Transition,
)
from plantuml_compose.renderers import render


class TestStateComposer:

    def test_empty_diagram(self):
        d = state_diagram()
        result = d.build()
        assert isinstance(result, StateDiagram)
        assert result.elements == ()

    def test_simple_state(self):
        d = state_diagram()
        el = d.elements
        d.add(el.state("Idle"))
        result = d.build()
        assert len(result.elements) == 1
        node = result.elements[0]
        assert isinstance(node, StateNode)
        assert node.name == "Idle"

    def test_state_with_description(self):
        d = state_diagram()
        el = d.elements
        d.add(el.state("Firmware", description="lifecycle-lemur firmware module"))
        result = d.build()
        node = result.elements[0]
        assert isinstance(node, StateNode)
        assert node.description.text == "lifecycle-lemur firmware module"

    def test_state_with_style(self):
        d = state_diagram()
        el = d.elements
        d.add(el.state("Error", style={"background": "#FFCDD2"}))
        result = d.build()
        node = result.elements[0]
        assert node.style is not None
        assert node.style.background.value == "#FFCDD2"

    def test_state_with_note(self):
        d = state_diagram()
        el = d.elements
        d.add(el.state("Used", note="Routine polls"))
        result = d.build()
        node = result.elements[0]
        assert node.note is not None
        assert isinstance(node.note, Note)
        assert node.note.content.text == "Routine polls"

    def test_transition(self):
        d = state_diagram()
        el = d.elements
        t = d.transitions
        idle = el.state("Idle")
        active = el.state("Active")
        d.add(idle, active)
        d.connect(t.transition(idle, active, label="go"))
        result = d.build()
        trans = [e for e in result.elements if isinstance(e, Transition)]
        assert len(trans) == 1
        assert trans[0].source == "Idle"
        assert trans[0].target == "Active"
        assert trans[0].label.text == "go"

    def test_transition_with_guard(self):
        d = state_diagram()
        el = d.elements
        t = d.transitions
        idle = el.state("Idle")
        active = el.state("Active")
        d.add(idle, active)
        d.connect(t.transition(idle, active, label="start", guard="authorized"))
        result = d.build()
        trans = [e for e in result.elements if isinstance(e, Transition)]
        assert trans[0].guard == "authorized"

    def test_initial_final_pseudostates(self):
        """'[*]' string maps to initial/final pseudo-state references."""
        d = state_diagram()
        el = d.elements
        t = d.transitions
        idle = el.state("Idle")
        d.add(idle)
        d.connect(
            t.transition("[*]", idle, label="start"),
            t.transition(idle, "[*]", label="done"),
        )
        result = d.build()
        trans = [e for e in result.elements if isinstance(e, Transition)]
        assert len(trans) == 2
        assert trans[0].source == "[*]"
        assert trans[0].target == "Idle"
        assert trans[1].source == "Idle"
        assert trans[1].target == "[*]"

    def test_composite_state_with_children(self):
        """Passing children to state() creates a CompositeState."""
        d = state_diagram()
        el = d.elements
        t = d.transitions

        inner_a = el.state("SubA")
        inner_b = el.state("SubB")
        comp = el.state("Active", inner_a, inner_b)

        d.add(comp)
        result = d.build()

        assert len(result.elements) == 1
        cs = result.elements[0]
        assert isinstance(cs, CompositeState)
        assert cs.name == "Active"
        assert len(cs.elements) == 2
        assert cs.elements[0].name == "SubA"
        assert cs.elements[1].name == "SubB"

    def test_ref_kwarg(self):
        d = state_diagram()
        el = d.elements
        s = el.state("Long Name", ref="ln")
        d.add(s)
        assert s._ref == "ln"
        result = d.build()
        assert result.elements[0].alias == "ln"

    def test_title_and_theme(self):
        d = state_diagram(title="Lifecycle", theme="plain")
        result = d.build()
        assert result.title == "Lifecycle"
        assert result.theme == "plain"

    def test_hide_empty_description(self):
        d = state_diagram(hide_empty_description=True)
        result = d.build()
        assert result.hide_empty_description is True

    def test_render_produces_plantuml(self):
        d = state_diagram(title="Test")
        el = d.elements
        t = d.transitions
        idle = el.state("Idle")
        active = el.state("Active")
        d.add(idle, active)
        d.connect(t.transition("[*]", idle, label="start"))
        d.connect(t.transition(idle, active, label="go"))
        result = render(d)
        assert "@startuml" in result
        assert "Idle" in result
        assert "@enduml" in result

    def test_render_matches_builder(self):
        """Simple lifecycle matches old builder."""
        from plantuml_compose.builders.state import (
            state_diagram as builder_state,
        )

        # Old builder
        with builder_state(title="Lifecycle", theme="plain") as old:
            firmware = old.state("Firmware", description="firmware module")
            os_install = old.state("OS", description="Installing")
            ready = old.state("Ready", description="Available")
            old.arrow("[*]", firmware, label="Server racked")
            old.arrow(firmware, os_install, label="Firmware complete")
            old.arrow(os_install, ready, label="OS complete")
        old_output = render(old.build())

        # New composer
        d = state_diagram(title="Lifecycle", theme="plain")
        el = d.elements
        t = d.transitions
        firmware = el.state("Firmware", description="firmware module")
        os_install = el.state("OS", description="Installing")
        ready = el.state("Ready", description="Available")
        d.add(firmware, os_install, ready)
        d.connect(
            t.transition("[*]", firmware, label="Server racked"),
            t.transition(firmware, os_install, label="Firmware complete"),
            t.transition(os_install, ready, label="OS complete"),
        )
        new_output = render(d)

        assert old_output == new_output

    def test_render_matches_builder_with_style(self):
        """States with style match old builder."""
        from plantuml_compose.builders.state import (
            state_diagram as builder_state,
        )

        # Old builder
        with builder_state() as old:
            idle = old.state("Idle", style={"background": "#E8F5E9"})
            active = old.state("Active", style={"background": "#E3F2FD"})
            old.arrow("[*]", idle)
            old.arrow(idle, active, label="go")
        old_output = render(old.build())

        # New composer
        d = state_diagram()
        el = d.elements
        t = d.transitions
        idle = el.state("Idle", style={"background": "#E8F5E9"})
        active = el.state("Active", style={"background": "#E3F2FD"})
        d.add(idle, active)
        d.connect(
            t.transition("[*]", idle),
            t.transition(idle, active, label="go"),
        )
        new_output = render(d)

        assert old_output == new_output


class TestStatePlantUMLValidation:

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

    def test_plantuml_validation(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = state_diagram(title="Validation Test", theme="plain")
        el = d.elements
        t = d.transitions

        firmware = el.state("Firmware",
            description="lifecycle-lemur firmware module",
            style={"background": "#FFF3E0"},
        )
        os_install = el.state("OS",
            description="Installing Alma Linux 8",
            style={"background": "#E3F2FD"},
        )
        ready = el.state("Ready",
            description="Available for assignment",
            style={"background": "#E8F5E9"},
        )

        d.add(firmware, os_install, ready)
        d.connect(
            t.transition("[*]", firmware, label="Server racked"),
            t.transition(firmware, os_install, label="Firmware complete"),
            t.transition(os_install, ready, label="OS complete"),
            t.transition(ready, "[*]"),
        )

        puml_file = tmp_path / "state_composer.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"
