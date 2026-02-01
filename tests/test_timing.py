"""Tests for timing diagram support."""

import subprocess

import pytest

from plantuml_compose import (
    timing_diagram,
    AnchorRef,
    Color,
    ElementStyle,
    HiddenState,
    IntricatedState,
    ParticipantRef,
    render,
    TimeAnchor,
    TimingConstraint,
    TimingDiagram,
    TimingDiagramStyle,
    TimingHighlight,
    TimingInitialState,
    TimingMessage,
    TimingNote,
    TimingParticipant,
    TimingScale,
    TimingStateChange,
    TimingStateOrder,
    TimingTicks,
)
from plantuml_compose.primitives.common import coerce_timing_diagram_style
from plantuml_compose.renderers.timing import render_timing_diagram


class TestTimingPrimitives:
    """Tests for timing diagram primitive dataclasses."""

    def test_participant_robust(self):
        p = TimingParticipant(type="robust", name="DataPath", alias="D")
        assert p.type == "robust"
        assert p.name == "DataPath"
        assert p.alias == "D"

    def test_participant_clock(self):
        p = TimingParticipant(
            type="clock", name="Clock", alias="CLK", period=50, pulse=25, offset=10
        )
        assert p.type == "clock"
        assert p.period == 50
        assert p.pulse == 25
        assert p.offset == 10

    def test_participant_binary(self):
        p = TimingParticipant(type="binary", name="ResetN")
        assert p.type == "binary"
        assert p.alias is None

    def test_time_anchor(self):
        anchor = TimeAnchor(time=0, name="start")
        assert anchor.time == 0
        assert anchor.name == "start"

    def test_state_change(self):
        sc = TimingStateChange(participant="D", time=10, state="Active", color="Blue")
        assert sc.participant == "D"
        assert sc.time == 10
        assert sc.state == "Active"
        assert sc.color == "Blue"

    def test_intricated_state(self):
        ist = IntricatedState(
            participant="D", time=50, states=("0", "1"), color="Gray"
        )
        assert ist.participant == "D"
        assert ist.states == ("0", "1")
        assert ist.color == "Gray"

    def test_hidden_state(self):
        hs = HiddenState(participant="D", time=100, style="hidden")
        assert hs.style == "hidden"

    def test_timing_message(self):
        msg = TimingMessage(
            source="A", target="B", label="trigger", source_time=15, target_time_offset=50
        )
        assert msg.source == "A"
        assert msg.target == "B"
        assert msg.label == "trigger"
        assert msg.target_time_offset == 50

    def test_timing_constraint(self):
        tc = TimingConstraint(
            participant="CLK", start_time=0, end_time=50, label="{50ns}"
        )
        assert tc.participant == "CLK"
        assert tc.start_time == 0
        assert tc.end_time == 50
        assert tc.label == "{50ns}"

    def test_timing_highlight(self):
        hl = TimingHighlight(start=20, end=40, color="Yellow", caption="Active Phase")
        assert hl.start == 20
        assert hl.end == 40
        assert hl.color == "Yellow"
        assert hl.caption == "Active Phase"

    def test_timing_scale(self):
        sc = TimingScale(time_units=100, pixels=50)
        assert sc.time_units == 100
        assert sc.pixels == 50

    def test_timing_note(self):
        note = TimingNote(participant="D", time=10, text="Important", position="bottom")
        assert note.participant == "D"
        assert note.time == 10
        assert note.text == "Important"
        assert note.position == "bottom"

    def test_timing_diagram(self):
        p = TimingParticipant(type="robust", name="D")
        sc = TimingStateChange(participant="D", time=0, state="Idle")
        diagram = TimingDiagram(
            elements=(p, sc),
            title="Test Diagram",
            date_format="YY-MM-dd",
        )
        assert len(diagram.elements) == 2
        assert diagram.title == "Test Diagram"
        assert diagram.date_format == "YY-MM-dd"


class TestTimingDiagramStyle:
    """Tests for TimingDiagramStyle."""

    def test_style_creation(self):
        style = TimingDiagramStyle(
            background="white",
            font_name="Arial",
            robust=ElementStyle(background="LightBlue"),
        )
        assert style.background == "white"
        assert style.font_name == "Arial"
        assert style.robust is not None
        assert style.robust.background == "LightBlue"

    def test_style_coercion_from_dict(self):
        style = coerce_timing_diagram_style({
            "background": "white",
            "robust": {"background": "LightBlue"},
        })
        assert isinstance(style, TimingDiagramStyle)
        assert isinstance(style.background, Color)
        assert style.background.value == "white"
        assert style.robust is not None
        assert isinstance(style.robust.background, Color)

    def test_style_passthrough(self):
        original = TimingDiagramStyle(background="white")
        result = coerce_timing_diagram_style(original)
        assert result is original


class TestTimingRenderer:
    """Tests for timing diagram rendering."""

    def test_render_empty_diagram(self):
        diagram = TimingDiagram()
        result = render_timing_diagram(diagram)
        assert result == "@startuml\n@enduml"

    def test_render_participant_robust(self):
        p = TimingParticipant(type="robust", name="DataPath", alias="D")
        diagram = TimingDiagram(elements=(p,))
        result = render_timing_diagram(diagram)
        assert 'robust "DataPath" as D' in result

    def test_render_participant_clock(self):
        p = TimingParticipant(
            type="clock", name="Clock", alias="CLK", period=50, pulse=25, offset=10
        )
        diagram = TimingDiagram(elements=(p,))
        result = render_timing_diagram(diagram)
        assert 'clock "Clock" as CLK with period 50 pulse 25 offset 10' in result

    def test_render_participant_binary(self):
        p = TimingParticipant(type="binary", name="ResetN")
        diagram = TimingDiagram(elements=(p,))
        result = render_timing_diagram(diagram)
        assert 'binary "ResetN"' in result

    def test_render_time_anchor(self):
        anchor = TimeAnchor(time=0, name="start")
        diagram = TimingDiagram(elements=(anchor,))
        result = render_timing_diagram(diagram)
        assert "@0 as :start" in result

    def test_render_state_change(self):
        sc = TimingStateChange(participant="D", time=10, state="Active")
        diagram = TimingDiagram(elements=(sc,))
        result = render_timing_diagram(diagram)
        assert "@10" in result
        assert "D is Active" in result

    def test_render_state_change_with_color(self):
        sc = TimingStateChange(participant="D", time=10, state="Active", color="Blue")
        diagram = TimingDiagram(elements=(sc,))
        result = render_timing_diagram(diagram)
        assert "D is Active #Blue" in result

    def test_render_intricated_state(self):
        ist = IntricatedState(participant="D", time=50, states=("0", "1"))
        diagram = TimingDiagram(elements=(ist,))
        result = render_timing_diagram(diagram)
        assert "D is {0,1}" in result

    def test_render_intricated_state_with_color(self):
        ist = IntricatedState(
            participant="D", time=50, states=("0", "1"), color="Gray"
        )
        diagram = TimingDiagram(elements=(ist,))
        result = render_timing_diagram(diagram)
        assert "D is {0,1} #Gray" in result

    def test_render_hidden_state(self):
        hs = HiddenState(participant="D", time=100, style="-")
        diagram = TimingDiagram(elements=(hs,))
        result = render_timing_diagram(diagram)
        assert "D is {-}" in result

    def test_render_message(self):
        msg = TimingMessage(source="A", target="B", label="trigger")
        diagram = TimingDiagram(elements=(msg,))
        result = render_timing_diagram(diagram)
        assert "A -> B : trigger" in result

    def test_render_message_with_offset(self):
        msg = TimingMessage(
            source="A", target="B", label="trigger", target_time_offset=50
        )
        diagram = TimingDiagram(elements=(msg,))
        result = render_timing_diagram(diagram)
        assert "A -> B@+50 : trigger" in result

    def test_render_message_with_negative_offset(self):
        msg = TimingMessage(
            source="A", target="B", label="trigger", target_time_offset=-10
        )
        diagram = TimingDiagram(elements=(msg,))
        result = render_timing_diagram(diagram)
        assert "A -> B@-10 : trigger" in result

    def test_render_constraint(self):
        tc = TimingConstraint(
            participant="CLK", start_time=0, end_time=50, label="{50ns}"
        )
        diagram = TimingDiagram(elements=(tc,))
        result = render_timing_diagram(diagram)
        assert "CLK@0 <-> @50 : {50ns}" in result

    def test_render_highlight(self):
        hl = TimingHighlight(start=20, end=40, color="Yellow", caption="Active")
        diagram = TimingDiagram(elements=(hl,))
        result = render_timing_diagram(diagram)
        assert "highlight 20 to 40 #Yellow : Active" in result

    def test_render_scale(self):
        sc = TimingScale(time_units=100, pixels=50)
        diagram = TimingDiagram(elements=(sc,))
        result = render_timing_diagram(diagram)
        assert "scale 100 as 50 pixels" in result

    def test_render_note(self):
        note = TimingNote(participant="D", time=10, text="Note text", position="top")
        diagram = TimingDiagram(elements=(note,))
        result = render_timing_diagram(diagram)
        assert "@10" in result  # Time context is rendered
        assert "note top of D" in result
        assert "Note text" in result
        assert "end note" in result

    def test_render_title(self):
        diagram = TimingDiagram(title="My Timing Diagram")
        result = render_timing_diagram(diagram)
        assert "title My Timing Diagram" in result

    def test_render_date_format(self):
        diagram = TimingDiagram(date_format="YY-MM-dd")
        result = render_timing_diagram(diagram)
        assert 'use date format "YY-MM-dd"' in result

    def test_render_diagram_style(self):
        style = TimingDiagramStyle(
            background="white",
            robust=ElementStyle(background="LightBlue"),
        )
        diagram = TimingDiagram(diagram_style=style)
        result = render_timing_diagram(diagram)
        assert "<style>" in result
        assert "timingDiagram {" in result
        assert "BackgroundColor white" in result
        assert "robust {" in result
        assert "</style>" in result


class TestAnchorRef:
    """Tests for AnchorRef arithmetic."""

    def test_anchor_ref_add(self):
        ref = AnchorRef("start")
        result = ref + 50
        assert result.name == "start"
        assert result.offset == 50

    def test_anchor_ref_radd(self):
        ref = AnchorRef("start")
        result = 50 + ref
        assert result.name == "start"
        assert result.offset == 50

    def test_anchor_ref_sub(self):
        ref = AnchorRef("end", offset=100)
        result = ref - 30
        assert result.name == "end"
        assert result.offset == 70

    def test_anchor_ref_chain(self):
        ref = AnchorRef("start")
        result = ref + 50 + 25 - 10
        assert result.offset == 65

    def test_anchor_ref_repr(self):
        ref = AnchorRef("start")
        assert repr(ref) == "<AnchorRef :start>"

    def test_anchor_ref_repr_with_offset(self):
        ref = AnchorRef("start", offset=50)
        assert repr(ref) == "<AnchorRef :start+50>"

    def test_anchor_ref_repr_negative_offset(self):
        ref = AnchorRef("start", offset=-10)
        assert repr(ref) == "<AnchorRef :start-10>"


class TestTimingBuilder:
    """Tests for timing diagram builder API."""

    def test_robust_participant(self):
        with timing_diagram() as d:
            data = d.robust("DataPath", alias="D")

        assert isinstance(data, ParticipantRef)
        assert data.name == "D"
        diagram = d.build()
        assert len(diagram.elements) == 1
        p = diagram.elements[0]
        assert isinstance(p, TimingParticipant)
        assert p.type == "robust"
        assert p.alias == "D"

    def test_robust_participant_auto_alias(self):
        with timing_diagram() as d:
            data = d.robust("DataPath")

        # Auto-generated alias
        assert isinstance(data, ParticipantRef)
        assert data.name == "_p1"
        diagram = d.build()
        p = diagram.elements[0]
        assert isinstance(p, TimingParticipant)
        assert p.alias == "_p1"

    def test_clock_participant(self):
        with timing_diagram() as d:
            clk = d.clock("Clock", alias="CLK", period=50, pulse=25, offset=10)

        assert isinstance(clk, ParticipantRef)
        diagram = d.build()
        p = diagram.elements[0]
        assert isinstance(p, TimingParticipant)
        assert p.type == "clock"
        assert p.period == 50
        assert p.pulse == 25
        assert p.offset == 10

    def test_clock_invalid_period(self):
        with timing_diagram() as d:
            with pytest.raises(ValueError, match="Clock period must be positive"):
                d.clock("Clock", period=0)

        with timing_diagram() as d:
            with pytest.raises(ValueError, match="Clock period must be positive"):
                d.clock("Clock", period=-10)

    def test_binary_participant(self):
        with timing_diagram() as d:
            rst = d.binary("ResetN")

        diagram = d.build()
        p = diagram.elements[0]
        assert isinstance(p, TimingParticipant)
        assert p.type == "binary"

    def test_concise_participant(self):
        with timing_diagram() as d:
            sig = d.concise("Signal", alias="S")

        diagram = d.build()
        p = diagram.elements[0]
        assert isinstance(p, TimingParticipant)
        assert p.type == "concise"

    def test_analog_participant(self):
        with timing_diagram() as d:
            analog = d.analog("Voltage", alias="V")

        diagram = d.build()
        p = diagram.elements[0]
        assert isinstance(p, TimingParticipant)
        assert p.type == "analog"

    def test_anchor(self):
        with timing_diagram() as d:
            start = d.anchor("start", at=0)

        assert isinstance(start, AnchorRef)
        assert start.name == "start"
        diagram = d.build()
        anchor = diagram.elements[0]
        assert isinstance(anchor, TimeAnchor)
        assert anchor.time == 0
        assert anchor.name == "start"

    def test_state(self):
        with timing_diagram() as d:
            data = d.robust("Data")
            d.state(data, "Idle", at=0)
            d.state(data, "Active", at=10, color="Blue")

        diagram = d.build()
        sc = diagram.elements[1]
        assert isinstance(sc, TimingStateChange)
        assert sc.state == "Idle"
        sc2 = diagram.elements[2]
        assert sc2.color == "Blue"

    def test_state_with_anchor_ref(self):
        with timing_diagram() as d:
            data = d.robust("Data")
            start = d.anchor("start", at=0)
            d.state(data, "Active", at=start + 50)

        diagram = d.build()
        sc = diagram.elements[2]
        assert isinstance(sc, TimingStateChange)
        assert sc.time == ":start+50"

    def test_intricated(self):
        with timing_diagram() as d:
            data = d.robust("Data")
            d.intricated(data, "0", "1", at=50, color="Gray")

        diagram = d.build()
        ist = diagram.elements[1]
        assert isinstance(ist, IntricatedState)
        assert ist.states == ("0", "1")
        assert ist.color == "Gray"

    def test_hidden(self):
        with timing_diagram() as d:
            data = d.robust("Data")
            d.hidden(data, at=100, style="hidden")

        diagram = d.build()
        hs = diagram.elements[1]
        assert isinstance(hs, HiddenState)
        assert hs.style == "hidden"

    def test_message(self):
        with timing_diagram() as d:
            data = d.robust("Data")
            rst = d.binary("Reset")
            d.message(data, rst, "trigger", at=15, target_offset=50)

        diagram = d.build()
        msg = diagram.elements[2]
        assert isinstance(msg, TimingMessage)
        assert msg.label == "trigger"
        assert msg.source_time == 15
        assert msg.target_time_offset == 50

    def test_message_with_zero_offset(self):
        """Test message with zero offset renders correctly."""
        with timing_diagram() as d:
            data = d.robust("Data")
            rst = d.binary("Reset")
            d.message(data, rst, "sync", at=10, target_offset=0)

        diagram = d.build()
        msg = diagram.elements[2]
        assert msg.target_time_offset == 0

        # Verify rendered output has @+0 syntax
        output = d.render()
        assert "_p2@+0" in output

    def test_constraint(self):
        with timing_diagram() as d:
            clk = d.clock("Clock", period=50)
            d.constraint(clk, start=0, end=50, label="{50ns}")

        diagram = d.build()
        tc = diagram.elements[1]
        assert isinstance(tc, TimingConstraint)
        assert tc.label == "{50ns}"

    def test_highlight(self):
        with timing_diagram() as d:
            d.highlight(start=20, end=40, color="Yellow", caption="Active Phase")

        diagram = d.build()
        hl = diagram.elements[0]
        assert isinstance(hl, TimingHighlight)
        assert hl.start == 20
        assert hl.end == 40
        assert hl.color == "Yellow"
        assert hl.caption == "Active Phase"

    def test_scale(self):
        with timing_diagram() as d:
            d.scale(time_units=100, pixels=50)

        diagram = d.build()
        sc = diagram.elements[0]
        assert isinstance(sc, TimingScale)
        assert sc.time_units == 100
        assert sc.pixels == 50

    def test_scale_invalid_time_units(self):
        with timing_diagram() as d:
            with pytest.raises(ValueError, match="time_units must be positive"):
                d.scale(time_units=0, pixels=50)

        with timing_diagram() as d:
            with pytest.raises(ValueError, match="time_units must be positive"):
                d.scale(time_units=-10, pixels=50)

    def test_scale_invalid_pixels(self):
        with timing_diagram() as d:
            with pytest.raises(ValueError, match="pixels must be positive"):
                d.scale(time_units=100, pixels=0)

        with timing_diagram() as d:
            with pytest.raises(ValueError, match="pixels must be positive"):
                d.scale(time_units=100, pixels=-5)

    def test_note(self):
        with timing_diagram() as d:
            data = d.robust("Data")
            d.note(data, "Important note", at=10, position="bottom")

        diagram = d.build()
        note = diagram.elements[1]
        assert isinstance(note, TimingNote)
        assert note.text == "Important note"
        assert note.position == "bottom"

    def test_diagram_with_style_dict(self):
        with timing_diagram(
            diagram_style={"robust": {"background": "LightBlue"}}
        ) as d:
            pass

        diagram = d.build()
        assert diagram.diagram_style is not None
        assert diagram.diagram_style.robust is not None
        assert isinstance(diagram.diagram_style.robust.background, Color)

    def test_full_example(self):
        """Test the full example from the plan."""
        with timing_diagram(title="Clock Domain Crossing") as d:
            # Participants
            clk = d.clock("Clock", period=50, pulse=25)
            data = d.robust("DataPath")
            rst = d.binary("ResetN")

            # Scale
            d.scale(time_units=100, pixels=50)

            # Anchors with arithmetic support
            start = d.anchor("start", at=0)

            # State changes
            d.state(data, "Idle", at=0)
            d.state(rst, "high", at=0)
            d.state(rst, "low", at=10)
            d.state(data, "Transmitting", at=20)
            d.state(data, "Receiving", at=40)

            # Use anchor with Python arithmetic
            d.state(rst, "high", at=start + 30)

            # Intricated (undefined) state
            d.intricated(data, "0", "1", at=50, color="Gray")

            # Messages between participants
            d.message(data, rst, "trigger", at=15)

            # Highlight time region
            d.highlight(start=20, end=40, color="Yellow", caption="Active Phase")

            # Timing constraint
            d.constraint(clk, start=0, end=50, label="{50ns}")

        result = d.render()
        assert "@startuml" in result
        assert "title Clock Domain Crossing" in result
        assert "clock" in result
        assert "robust" in result
        assert "binary" in result
        assert "@enduml" in result


class TestTimingDispatch:
    """Tests for render() dispatch function with Timing."""

    def test_render_dispatch(self):
        p = TimingParticipant(type="robust", name="Data")
        diagram = TimingDiagram(elements=(p,))
        result = render(diagram)
        assert "@startuml" in result
        assert 'robust "Data"' in result


class TestTimingPlantUMLIntegration:
    """Integration tests verifying PlantUML accepts the output."""

    @pytest.fixture
    def plantuml_check(self):
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

    def test_basic_timing(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with timing_diagram() as d:
            data = d.robust("Data")
            d.state(data, "Idle", at=0)
            d.state(data, "Active", at=10)

        puml_file = tmp_path / "timing_basic.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_clock_signal(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with timing_diagram() as d:
            d.clock("Clock", period=50)

        puml_file = tmp_path / "timing_clock.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_binary_signal(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with timing_diagram() as d:
            rst = d.binary("ResetN")
            d.state(rst, "high", at=0)
            d.state(rst, "low", at=10)

        puml_file = tmp_path / "timing_binary.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_highlight_region(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with timing_diagram() as d:
            data = d.robust("Data")
            d.state(data, "Idle", at=0)
            d.highlight(start=0, end=50, color="Yellow", caption="Phase 1")

        puml_file = tmp_path / "timing_highlight.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_full_diagram(self, plantuml_check, tmp_path):
        """Full timing diagram with all features."""
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with timing_diagram(title="Complex Timing") as d:
            # Participants
            clk = d.clock("Clock", period=50, pulse=25)
            data = d.robust("DataPath")
            rst = d.binary("ResetN")
            concise_sig = d.concise("Status")

            # Scale
            d.scale(time_units=100, pixels=50)

            # State changes
            d.state(data, "Idle", at=0)
            d.state(rst, "high", at=0)
            d.state(concise_sig, "OK", at=0)
            d.state(rst, "low", at=10)
            d.state(data, "Transmitting", at=20)

            # Highlight
            d.highlight(start=20, end=50, color="LightYellow")

        puml_file = tmp_path / "timing_full.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_with_style(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with timing_diagram(
            diagram_style=TimingDiagramStyle(
                background="white",
                robust=ElementStyle(background="LightBlue"),
            )
        ) as d:
            data = d.robust("Data")
            d.state(data, "Idle", at=0)

        puml_file = tmp_path / "timing_style.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"


class TestTimingExtendedFeatures:
    """Tests for extended timing diagram features."""

    def test_rectangle_participant(self):
        """Test rectangle participant type."""
        with timing_diagram() as d:
            rect = d.rectangle("Status")
            d.state(rect, "Active", at=0)

        result = d.render()
        assert 'rectangle "Status"' in result

    def test_compact_mode_global(self):
        """Test global compact mode."""
        with timing_diagram(compact_mode=True) as d:
            d.robust("Signal")

        result = d.render()
        assert "mode compact" in result

    def test_compact_mode_per_participant(self):
        """Test per-participant compact mode."""
        with timing_diagram() as d:
            d.robust("Signal", compact=True)

        result = d.render()
        assert 'compact robust "Signal"' in result

    def test_hide_time_axis(self):
        """Test hiding time axis."""
        with timing_diagram(hide_time_axis=True) as d:
            d.robust("Signal")

        result = d.render()
        assert "hide time-axis" in result

    def test_manual_time_axis(self):
        """Test manual time axis."""
        with timing_diagram(manual_time_axis=True) as d:
            d.robust("Signal")

        result = d.render()
        assert "manual time-axis" in result

    def test_analog_with_range(self):
        """Test analog participant with min/max range."""
        with timing_diagram() as d:
            d.analog("Voltage", min_value=0, max_value=5)

        result = d.render()
        assert 'analog "Voltage" between 0 and 5' in result

    def test_analog_with_height(self):
        """Test analog participant with explicit height."""
        with timing_diagram() as d:
            v = d.analog("Voltage", alias="V", height=100)
            d.state(v, "2.5", at=0)

        result = d.render()
        assert "V is 100 pixels height" in result

    def test_analog_ticks(self):
        """Test analog tick marks."""
        with timing_diagram() as d:
            v = d.analog("Voltage", alias="V")
            d.ticks(v, multiple=1)

        result = d.render()
        assert "V ticks num on multiple 1" in result

    def test_define_states_simple(self):
        """Test simple state ordering."""
        with timing_diagram() as d:
            sig = d.robust("Signal", alias="S")
            d.define_states(sig, "Idle", "Active", "Done")

        result = d.render()
        assert "S has Idle,Active,Done" in result

    def test_define_states_with_labels(self):
        """Test state ordering with labels."""
        with timing_diagram() as d:
            sig = d.robust("Signal", alias="S")
            d.define_states(sig, "idle", "active", labels={"idle": "Idle State"})

        result = d.render()
        # Each labeled state now gets its own line
        assert 'S has "Idle State" as idle' in result
        assert "S has active" in result

    def test_initial_state(self):
        """Test initial state before timeline."""
        with timing_diagram() as d:
            sig = d.robust("Signal", alias="S")
            d.initial_state(sig, "Idle")
            d.state(sig, "Active", at=10)

        result = d.render()
        assert "S is Idle" in result
        # Initial state should come before @time references
        lines = result.split("\n")
        initial_idx = next(i for i, line in enumerate(lines) if "S is Idle" in line and "@" not in line)
        time_idx = next(i for i, line in enumerate(lines) if "@10" in line)
        assert initial_idx < time_idx

    def test_stereotype(self):
        """Test stereotype on participant."""
        with timing_diagram() as d:
            d.robust("Data", stereotype="<<hw>>")

        result = d.render()
        # Stereotype comes after name, before alias
        assert 'robust "Data" <<hw>> as' in result

    def test_state_with_comment(self):
        """Test state change with inline comment."""
        with timing_diagram() as d:
            sig = d.robust("Signal", alias="S")
            d.state(sig, "Active", at=0, comment="starts here")

        result = d.render()
        assert "S is Active: starts here" in result


class TestTimingExtendedPrimitives:
    """Tests for extended timing diagram primitives."""

    def test_timing_state_order(self):
        order = TimingStateOrder(
            participant="S",
            states=("Idle", "Active", "Done"),
            labels=None,
        )
        assert order.participant == "S"
        assert order.states == ("Idle", "Active", "Done")

    def test_timing_state_order_with_labels(self):
        order = TimingStateOrder(
            participant="S",
            states=("idle", "active"),
            labels={"idle": "Idle State"},
        )
        assert order.labels == {"idle": "Idle State"}

    def test_timing_ticks(self):
        ticks = TimingTicks(participant="V", multiple=0.5)
        assert ticks.participant == "V"
        assert ticks.multiple == 0.5

    def test_timing_initial_state(self):
        init = TimingInitialState(participant="S", state="Idle")
        assert init.participant == "S"
        assert init.state == "Idle"

    def test_participant_with_extended_fields(self):
        p = TimingParticipant(
            type="analog",
            name="Voltage",
            alias="V",
            stereotype="<<hw>>",
            compact=True,
            min_value=0,
            max_value=5,
            height_pixels=100,
        )
        assert p.stereotype == "<<hw>>"
        assert p.compact is True
        assert p.min_value == 0
        assert p.max_value == 5
        assert p.height_pixels == 100

    def test_state_change_with_comment(self):
        sc = TimingStateChange(
            participant="S",
            time=0,
            state="Active",
            comment="starts here",
        )
        assert sc.comment == "starts here"

    def test_timing_diagram_extended_options(self):
        diagram = TimingDiagram(
            compact_mode=True,
            hide_time_axis=True,
            manual_time_axis=True,
        )
        assert diagram.compact_mode is True
        assert diagram.hide_time_axis is True
        assert diagram.manual_time_axis is True


class TestTimingExtendedPlantUMLIntegration:
    """Integration tests for extended timing features."""

    @pytest.fixture
    def plantuml_check(self):
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

    def test_rectangle_and_compact(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with timing_diagram(compact_mode=True) as d:
            status = d.rectangle("Status")
            d.state(status, "OK", at=0)
            d.state(status, "Error", at=50)

        puml_file = tmp_path / "timing_rect.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_analog_with_range_and_ticks(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with timing_diagram() as d:
            v = d.analog("Voltage", alias="V", min_value=0, max_value=5, height=80)
            d.ticks(v, multiple=1)
            d.state(v, "0", at=0)
            d.state(v, "2.5", at=10)
            d.state(v, "5", at=20)

        puml_file = tmp_path / "timing_analog.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_state_ordering(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with timing_diagram() as d:
            sig = d.robust("Signal", alias="S")
            d.define_states(sig, "Idle", "Active", "Done")
            d.state(sig, "Idle", at=0)
            d.state(sig, "Active", at=10)
            d.state(sig, "Done", at=30)

        puml_file = tmp_path / "timing_state_order.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_initial_state_integration(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with timing_diagram() as d:
            sig = d.robust("Signal", alias="S")
            d.initial_state(sig, "Off")
            d.state(sig, "On", at=10)
            d.state(sig, "Off", at=50)

        puml_file = tmp_path / "timing_initial.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_stereotype_integration(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with timing_diagram() as d:
            data = d.robust("Data", stereotype="<<hw>>")
            d.state(data, "Idle", at=0)
            d.state(data, "Active", at=10)

        puml_file = tmp_path / "timing_stereotype.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"
