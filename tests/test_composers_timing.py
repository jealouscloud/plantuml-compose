"""Tests for the timing diagram composer."""

import subprocess

import pytest

from plantuml_compose.composers.timing import timing_diagram
from plantuml_compose.primitives.timing import (
    IntricatedState,
    StateChange,
    TimeAnchor,
    TimingConstraint,
    TimingDiagram,
    TimingHighlight,
    TimingInitialState,
    TimingMessage,
    TimingParticipant,
    TimingScale,
    TimingStateOrder,
)
from plantuml_compose.renderers import render


class TestTimingComposer:

    def test_empty_diagram(self):
        d = timing_diagram()
        result = d.build()
        assert isinstance(result, TimingDiagram)
        assert result.elements == ()

    def test_participants_with_states(self):
        d = timing_diagram()
        p = d.participants
        source = p.robust("Source Node",
            states=("idle", "running", "dumping"),
            initial="running",
        )
        d.add(source)
        result = d.build()

        participants = [e for e in result.elements if isinstance(e, TimingParticipant)]
        assert len(participants) == 1
        assert participants[0].name == "Source Node"
        assert participants[0].type == "robust"

        state_orders = [e for e in result.elements if isinstance(e, TimingStateOrder)]
        assert len(state_orders) == 1
        assert state_orders[0].states == ("idle", "running", "dumping")

        initial_states = [e for e in result.elements if isinstance(e, TimingInitialState)]
        assert len(initial_states) == 1
        assert initial_states[0].state == "running"

    def test_at_grouping(self):
        d = timing_diagram()
        p = d.participants
        e = d.events
        source = p.robust("Source", states=("idle", "running"), initial="idle")
        d.add(source)
        d.at(10,
            e.state(source, "running"),
        )
        result = d.build()

        state_changes = [el for el in result.elements if isinstance(el, StateChange)]
        assert len(state_changes) == 1
        assert state_changes[0].state == "running"
        assert state_changes[0].time == 10

    def test_named_anchor(self):
        d = timing_diagram()
        p = d.participants
        e = d.events
        source = p.robust("Source", states=("idle", "running"), initial="idle")
        d.add(source)
        d.at(55,
            e.state(source, "running"),
            name="start_point",
        )
        result = d.build()

        anchors = [el for el in result.elements if isinstance(el, TimeAnchor)]
        assert len(anchors) == 1
        assert anchors[0].time == 55
        assert anchors[0].name == "start_point"

    def test_message_inside_at(self):
        d = timing_diagram()
        p = d.participants
        e = d.events
        source = p.robust("Source", states=("idle", "running"), initial="idle")
        dest = p.robust("Dest", states=("idle", "running"), initial="idle")
        d.add(source, dest)
        d.at(25,
            e.state(source, "running"),
            e.message(source, dest, "data transfer"),
        )
        result = d.build()

        messages = [el for el in result.elements if isinstance(el, TimingMessage)]
        assert len(messages) == 1
        assert messages[0].label == "data transfer"
        assert messages[0].source_time == 25

    def test_highlight(self):
        d = timing_diagram()
        d.highlight(start=55, end=80, color="#FFCDD2", caption="Downtime")
        result = d.build()

        highlights = [el for el in result.elements if isinstance(el, TimingHighlight)]
        assert len(highlights) == 1
        assert highlights[0].start == 55
        assert highlights[0].end == 80
        assert highlights[0].color == "#FFCDD2"
        assert highlights[0].caption == "Downtime"

    def test_constraint(self):
        d = timing_diagram()
        p = d.participants
        ct = p.robust("CT", states=("frozen", "running"), initial="running")
        d.add(ct)
        d.constraint(ct, start="start_point", end="end_point", label="{~25ms}")
        result = d.build()

        constraints = [el for el in result.elements if isinstance(el, TimingConstraint)]
        assert len(constraints) == 1
        assert constraints[0].label == "{~25ms}"

    def test_scale(self):
        d = timing_diagram()
        d.scale(time_units=10, pixels=120)
        result = d.build()

        scales = [el for el in result.elements if isinstance(el, TimingScale)]
        assert len(scales) == 1
        assert scales[0].time_units == 10
        assert scales[0].pixels == 120

    def test_intricated_inside_at(self):
        d = timing_diagram()
        p = d.participants
        e = d.events
        ct = p.robust("CT", states=("frozen", "running-src", "running-dest"), initial="running-src")
        d.add(ct)
        d.at(78,
            e.intricated(ct, "frozen", "running-dest"),
        )
        result = d.build()

        intricated = [el for el in result.elements if isinstance(el, IntricatedState)]
        assert len(intricated) == 1
        assert intricated[0].states == ("frozen", "running-dest")
        assert intricated[0].time == 78

    def test_render_produces_plantuml(self):
        d = timing_diagram(title="Migration")
        p = d.participants
        e = d.events
        source = p.robust("Source",
            states=("idle", "running"),
            initial="idle",
        )
        d.add(source)
        d.at(10, e.state(source, "running"))
        result = render(d)
        assert "@startuml" in result
        assert "Source" in result
        assert "@enduml" in result

    def test_title(self):
        d = timing_diagram(title="Test Timing")
        result = d.build()
        assert result.title == "Test Timing"

    def test_multiple_participants_multiple_at(self):
        d = timing_diagram()
        p = d.participants
        e = d.events
        a = p.robust("A", states=("off", "on"), initial="off")
        b = p.concise("B", states=("low", "high"), initial="low")
        d.add(a, b)
        d.at(10,
            e.state(a, "on"),
            e.state(b, "high"),
        )
        d.at(20,
            e.state(a, "off"),
        )
        result = d.build()
        state_changes = [el for el in result.elements if isinstance(el, StateChange)]
        assert len(state_changes) == 3


class TestTimingPlantUMLValidation:

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

        d = timing_diagram(title="Validation Test")
        p = d.participants
        e = d.events

        source = p.robust("Source Node",
            states=("idle", "running", "dumping"),
            initial="running",
        )
        dest = p.robust("Destination Node",
            states=("idle", "restoring", "running"),
            initial="idle",
        )
        d.add(source, dest)

        d.scale(time_units=10, pixels=120)

        d.at(10,
            e.state(source, "dumping"),
        )
        d.at(25,
            e.state(source, "running"),
            e.message(source, dest, "image"),
        )
        d.at(55,
            e.state(source, "dumping"),
            name="downtime_start",
        )
        d.at(80,
            e.state(source, "idle"),
            e.state(dest, "running"),
            name="downtime_end",
        )

        d.highlight(start=55, end=80, color="#FFCDD2", caption="Downtime")

        puml_file = tmp_path / "timing_composer.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"
