"""Tests for the state diagram composer."""

import subprocess

import pytest

from plantuml_compose.composers.state import state_diagram
from plantuml_compose.primitives.common import Label, Note
from plantuml_compose.primitives.state import (
    CompositeState,
    ConcurrentState,
    PseudoState,
    PseudoStateKind,
    Region,
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

    def test_initial_final_pseudostates_string(self):
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

    def test_initial_final_helpers(self):
        """el.initial() and el.final() return '[*]' for use in transitions."""
        d = state_diagram()
        el = d.elements
        t = d.transitions
        idle = el.state("Idle")
        d.add(idle)
        d.connect(
            t.transition(el.initial(), idle, label="start"),
            t.transition(idle, el.final(), label="done"),
        )
        result = d.build()
        trans = [e for e in result.elements if isinstance(e, Transition)]
        assert trans[0].source == "[*]"
        assert trans[1].target == "[*]"
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


class TestStatePseudoStatesAndConcurrency:

    def test_choice(self):
        d = state_diagram()
        el = d.elements
        t = d.transitions
        check = el.choice("check")
        a = el.state("A")
        b = el.state("B")
        d.add(check, a, b)
        d.connect(
            t.transition("[*]", check),
            t.transition(check, a, guard="x > 0"),
            t.transition(check, b, guard="x <= 0"),
        )
        result = d.build()
        pseudos = [e for e in result.elements if isinstance(e, PseudoState)]
        assert len(pseudos) == 1
        assert pseudos[0].kind == PseudoStateKind.CHOICE
        assert pseudos[0].name == "check"

    def test_fork_join(self):
        d = state_diagram()
        el = d.elements
        t = d.transitions
        f = el.fork("split")
        j = el.join("merge")
        a = el.state("A")
        b = el.state("B")
        d.add(f, j, a, b)
        d.connect(
            t.transition("[*]", f),
            t.transition(f, a),
            t.transition(f, b),
            t.transition(a, j),
            t.transition(b, j),
            t.transition(j, "[*]"),
        )
        result = d.build()
        pseudos = [e for e in result.elements if isinstance(e, PseudoState)]
        kinds = {p.kind for p in pseudos}
        assert PseudoStateKind.FORK in kinds
        assert PseudoStateKind.JOIN in kinds

    def test_transition_trigger_effect(self):
        d = state_diagram()
        el = d.elements
        t = d.transitions
        a = el.state("Idle")
        b = el.state("Active")
        d.add(a, b)
        d.connect(t.transition(a, b, trigger="click", guard="enabled", effect="log()"))
        result = d.build()
        trans = [e for e in result.elements if isinstance(e, Transition)]
        assert trans[0].trigger == "click"
        assert trans[0].guard == "enabled"
        assert trans[0].effect == "log()"

    def test_concurrent_state(self):
        d = state_diagram()
        el = d.elements
        audio_on = el.state("On")
        audio_off = el.state("Off")
        video_active = el.state("Active")
        video_idle = el.state("Idle")

        active = el.concurrent("Active",
            el.region(audio_on, audio_off),
            el.region(video_active, video_idle),
        )
        d.add(active)
        result = d.build()
        concurrent = [e for e in result.elements if isinstance(e, ConcurrentState)]
        assert len(concurrent) == 1
        assert concurrent[0].name == "Active"
        assert len(concurrent[0].regions) == 2
        assert len(concurrent[0].regions[0].elements) == 2
        assert len(concurrent[0].regions[1].elements) == 2

    def test_history(self):
        d = state_diagram()
        el = d.elements
        h = el.history()
        d.add(h)
        result = d.build()
        pseudos = [e for e in result.elements if isinstance(e, PseudoState)]
        assert pseudos[0].kind == PseudoStateKind.HISTORY

    def test_deep_history(self):
        d = state_diagram()
        el = d.elements
        dh = el.deep_history()
        d.add(dh)
        result = d.build()
        pseudos = [e for e in result.elements if isinstance(e, PseudoState)]
        assert pseudos[0].kind == PseudoStateKind.DEEP_HISTORY


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
