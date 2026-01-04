"""
Comprehensive tests proving every PlantUML state diagram feature is representable.

Each test corresponds to a section in the PlantUML state diagram documentation.
These tests verify that our Python API can generate valid PlantUML syntax for
every documented feature.

"""

import subprocess
from pathlib import Path

import pytest

from plantuml_compose import (
    Color,
    Direction,
    Gradient,
    Label,
    LinePattern,
    LineStyle,
    Note,
    NotePosition,
    RegionSeparator,
    Stereotype,
    Style,
    render,
    state_diagram,
)


@pytest.fixture
def validate_plantuml(tmp_path: Path):
    """Fixture that validates PlantUML syntax and optionally renders to SVG."""

    def _validate(puml_text: str, name: str = "test") -> bool:
        puml_file = tmp_path / f"{name}.puml"
        svg_file = tmp_path / f"{name}.svg"

        puml_file.write_text(puml_text)

        result = subprocess.run(
            ["plantuml", "-tsvg", str(puml_file)],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"PlantUML error: {result.stderr}")
            return False

        return svg_file.exists()

    return _validate


class TestSimpleState:
    """Doc section: Simple State - basic states and arrows."""

    def test_simple_state_declaration(self, validate_plantuml):
        """States with names and arrows to initial/final."""
        with state_diagram() as d:
            s1 = d.state("State1")
            d.arrow(d.start(), s1)
            d.arrow(s1, d.end())

        output = render(d.build())
        assert "[*] --> State1" in output
        assert "State1 --> [*]" in output
        assert validate_plantuml(output, "simple_state")

    def test_state_with_description(self, validate_plantuml):
        """States can have descriptions (multiple lines)."""
        with state_diagram() as d:
            s1 = d.state("State1", description="this is a string")

        output = render(d.build())
        assert "State1 : this is a string" in output
        assert validate_plantuml(output, "state_description")


class TestChangeStateRendering:
    """Doc section: Change State Rendering - hide empty description."""

    def test_hide_empty_description(self, validate_plantuml):
        """hide empty description renders states as simple boxes."""
        with state_diagram(hide_empty_description=True) as d:
            s1 = d.state("State1")
            s2 = d.state("State2")
            d.arrow(d.start(), s1)
            d.arrow(s1, s2)
            d.arrow(s2, d.end())

        output = render(d.build())
        assert "hide empty description" in output
        assert validate_plantuml(output, "hide_empty")


class TestCompositeState:
    """Doc section: Composite State - nested states."""

    def test_internal_sub_state(self, validate_plantuml):
        """States can contain nested states."""
        with state_diagram() as d:
            with d.composite("NotShooting") as ns:
                idle = ns.state("Idle")
                configuring = ns.state("Configuring")
                ns.arrow(ns.start(), idle)
                ns.arrow(idle, configuring, "EvConfig")
                ns.arrow(configuring, idle, "EvConfig")

        output = render(d.build())
        assert "state NotShooting {" in output
        assert "state Idle" in output
        assert validate_plantuml(output, "composite_internal")

    def test_sub_state_to_sub_state(self, validate_plantuml):
        """Transitions between sub-states in different composites."""
        with state_diagram() as d:
            with d.composite("A") as a:
                with a.composite("X") as x:
                    x.state("Inner")
                with a.composite("Y") as y:
                    y.state("Other")
            with d.composite("B") as b:
                with b.composite("Z") as z:
                    z.state("Deep")
            d.arrow(x.ref, z.ref)
            d.arrow(z.ref, y.ref)

        output = render(d.build())
        assert "X --> Z" in output
        assert "Z --> Y" in output
        assert validate_plantuml(output, "sub_to_sub")


class TestLongName:
    """Doc section: Long Name - aliases for states with long names."""

    def test_state_with_alias(self, validate_plantuml):
        """Long state names can use aliases."""
        with state_diagram() as d:
            s = d.state("Accumulate Enough Data Long State Name", alias="long1")
            d.arrow(d.start(), s)

        output = render(d.build())
        assert (
            'state "Accumulate Enough Data Long State Name" as long1' in output
        )
        assert "[*] --> long1" in output
        assert validate_plantuml(output, "long_name")


class TestHistory:
    """Doc section: History - [H] and [H*] pseudo-states."""

    def test_history_state(self, validate_plantuml):
        """History pseudo-state [H] for returning to previous state."""
        with state_diagram() as d:
            s1 = d.state("State1")
            s2 = d.state("State2")
            with d.composite("State3") as s3:
                s3.state("ProcessData")
            d.arrow(d.start(), s1)
            d.arrow(s1, s2)
            d.arrow(s2, s3.ref)
            d.arrow(s2, d.history(), "Resume")

        output = render(d.build())
        assert "State2 --> [H]" in output
        assert validate_plantuml(output, "history")

    def test_deep_history_state(self, validate_plantuml):
        """Deep history pseudo-state [H*]."""
        with state_diagram() as d:
            s2 = d.state("State2")
            with d.composite("State3") as s3:
                s3.state("ProcessData")
            d.arrow(s2, d.deep_history(), "DeepResume")

        output = render(d.build())
        assert "State2 --> [H*]" in output
        assert validate_plantuml(output, "deep_history")


class TestForkJoin:
    """Doc section: Fork - <<fork>> and <<join>> stereotypes."""

    def test_fork_and_join(self, validate_plantuml):
        """Fork and join pseudo-states for parallel regions."""
        with state_diagram() as d:
            fork = d.fork("fork_state")
            s2 = d.state("State2")
            s3 = d.state("State3")
            join = d.join("join_state")
            s4 = d.state("State4")

            d.arrow(d.start(), fork)
            d.arrow(fork, s2)
            d.arrow(fork, s3)
            d.arrow(s2, join)
            d.arrow(s3, join)
            d.arrow(join, s4)
            d.arrow(s4, d.end())

        output = render(d.build())
        assert "state fork_state <<fork>>" in output
        assert "state join_state <<join>>" in output
        assert validate_plantuml(output, "fork_join")


class TestConcurrentState:
    """Doc section: Concurrent State - -- and || separators."""

    def test_horizontal_separator(self, validate_plantuml):
        """Concurrent regions with horizontal separator (--)."""
        with state_diagram() as d:
            with d.concurrent("Active") as active:
                with active.region() as r1:
                    num_off = r1.state("NumLockOff")
                    num_on = r1.state("NumLockOn")
                    r1.arrow(r1.start(), num_off)
                    r1.arrow(num_off, num_on, "EvNumLockPressed")
                with active.region() as r2:
                    caps_off = r2.state("CapsLockOff")
                    caps_on = r2.state("CapsLockOn")
                    r2.arrow(r2.start(), caps_off)
                    r2.arrow(caps_off, caps_on, "EvCapsLockPressed")
            d.arrow(d.start(), active.ref)

        output = render(d.build())
        assert "state Active {" in output
        assert "--" in output
        assert validate_plantuml(output, "concurrent_horizontal")

    def test_vertical_separator(self, validate_plantuml):
        """Concurrent regions with vertical separator (||)."""
        with state_diagram() as d:
            with d.concurrent(
                "Active", separator=RegionSeparator.VERTICAL
            ) as active:
                with active.region() as r1:
                    r1.state("NumLockOff")
                with active.region() as r2:
                    r2.state("CapsLockOff")
            d.arrow(d.start(), active.ref)

        output = render(d.build())
        assert "||" in output
        assert validate_plantuml(output, "concurrent_vertical")


class TestConditional:
    """Doc section: Conditional - <<choice>> stereotype."""

    def test_choice_state(self, validate_plantuml):
        """Choice pseudo-state for conditional branching."""
        with state_diagram() as d:
            req = d.state("ReqId")
            minor = d.state("MinorId")
            major = d.state("MajorId")
            c = d.choice("c")

            d.arrow("Idle", req)
            d.arrow(req, c)
            d.arrow(c, minor, guard="Id <= 10")
            d.arrow(c, major, guard="Id > 10")

        output = render(d.build())
        assert "state c <<choice>>" in output
        assert "c --> MinorId : [Id <= 10]" in output
        assert "c --> MajorId : [Id > 10]" in output
        assert validate_plantuml(output, "choice")


class TestStereotypes:
    """Doc section: Stereotypes - all available stereotypes."""

    def test_entry_exit_points(self, validate_plantuml):
        """Entry and exit point pseudo-states."""
        with state_diagram() as d:
            with d.composite("Somp") as somp:
                entry1 = somp.entry_point("entry1")
                entry2 = somp.entry_point("entry2")
                sin = somp.state("sin")
                sin2 = somp.state("sin2")
                exit_a = somp.exit_point("exitA")
                somp.arrow(entry1, sin)
                somp.arrow(entry2, sin)
                somp.arrow(sin, sin2)
                somp.arrow(sin2, exit_a)
            d.arrow(d.start(), "entry1")
            d.arrow("exitA", "Foo")

        output = render(d.build())
        assert "state entry1 <<entryPoint>>" in output
        assert "state exitA <<exitPoint>>" in output
        assert validate_plantuml(output, "entry_exit")

    def test_input_output_pins(self, validate_plantuml):
        """Input and output pin pseudo-states."""
        with state_diagram() as d:
            with d.composite("Somp") as somp:
                input1 = somp.input_pin("input1")
                output1 = somp.output_pin("output1")
                process = somp.state("process")
                somp.arrow(input1, process)
                somp.arrow(process, output1)
            d.arrow(d.start(), "input1")
            d.arrow("output1", "Foo")

        output = render(d.build())
        assert "state input1 <<inputPin>>" in output
        assert "state output1 <<outputPin>>" in output
        assert validate_plantuml(output, "input_output_pins")

    def test_sdl_receive(self, validate_plantuml):
        """SDL receive pseudo-state."""
        with state_diagram() as d:
            receive = d.sdl_receive("ReqId")
            d.arrow("Idle", receive)

        output = render(d.build())
        assert "state ReqId <<sdlreceive>>" in output
        assert validate_plantuml(output, "sdl_receive")

    def test_expansion_points(self, validate_plantuml):
        """Expansion input/output pseudo-states."""
        with state_diagram() as d:
            exp_in = d.expansion_input("expIn")
            exp_out = d.expansion_output("expOut")
            d.arrow(exp_in, exp_out)

        output = render(d.build())
        assert "state expIn <<expansionInput>>" in output
        assert "state expOut <<expansionOutput>>" in output
        assert validate_plantuml(output, "expansion")


class TestArrowDirection:
    """Doc section: Arrow Direction - up/down/left/right arrows."""

    def test_arrow_directions(self, validate_plantuml):
        """Arrow direction hints for layout control."""
        with state_diagram() as d:
            first = d.state("First")
            second = d.state("Second")
            third = d.state("Third")
            last = d.state("Last")

            d.arrow(d.start(), first, direction=Direction.UP)
            d.arrow(first, second, direction=Direction.RIGHT)
            d.arrow(second, third, direction=Direction.DOWN)
            d.arrow(third, last, direction=Direction.LEFT)

        output = render(d.build())
        assert "-u->" in output  # up
        assert "-r->" in output  # right
        assert "-d->" in output  # down
        assert "-l->" in output  # left
        assert validate_plantuml(output, "arrow_direction")


class TestLineColorAndStyle:
    """Doc section: Change Line Color and Style."""

    def test_arrow_color(self, validate_plantuml):
        """Colored arrows."""
        with state_diagram() as d:
            s1 = d.state("S1")
            s2 = d.state("S2")
            d.arrow(s1, s2, style=LineStyle(color=Color.hex("#DD00AA")))

        output = render(d.build())
        assert "#DD00AA" in output
        assert validate_plantuml(output, "arrow_color")

    def test_arrow_dashed(self, validate_plantuml):
        """Dashed arrows."""
        with state_diagram() as d:
            x1 = d.state("X1")
            x2 = d.state("X2")
            d.arrow(x1, x2, style=LineStyle(pattern=LinePattern.DASHED))

        output = render(d.build())
        assert "dashed" in output
        assert validate_plantuml(output, "arrow_dashed")

    def test_arrow_dotted(self, validate_plantuml):
        """Dotted arrows."""
        with state_diagram() as d:
            z1 = d.state("Z1")
            z2 = d.state("Z2")
            d.arrow(z1, z2, style=LineStyle(pattern=LinePattern.DOTTED))

        output = render(d.build())
        assert "dotted" in output
        assert validate_plantuml(output, "arrow_dotted")

    def test_arrow_bold(self, validate_plantuml):
        """Bold arrows."""
        with state_diagram() as d:
            y1 = d.state("Y1")
            y2 = d.state("Y2")
            d.arrow(
                y1, y2, style=LineStyle(bold=True, color=Color.named("blue"))
            )

        output = render(d.build())
        assert "bold" in output
        assert "#blue" in output
        assert validate_plantuml(output, "arrow_bold")

    def test_arrow_combined_style(self, validate_plantuml):
        """Combined color and pattern."""
        with state_diagram() as d:
            s1 = d.state("S1")
            s4 = d.state("S4")
            d.arrow(
                s1,
                s4,
                direction=Direction.UP,
                style=LineStyle(
                    color=Color.named("red"), pattern=LinePattern.DASHED
                ),
            )

        output = render(d.build())
        assert "#red" in output
        assert "dashed" in output
        assert validate_plantuml(output, "arrow_combined")


class TestNotes:
    """Doc section: Notes - various note placements."""

    def test_note_on_state(self, validate_plantuml):
        """Notes attached to states."""
        with state_diagram() as d:
            active = d.state("Active", note="this is a short note")
            inactive = d.state(
                "Inactive",
                note=Note(Label("A longer note"), NotePosition.LEFT),
            )
            d.arrow(d.start(), active)
            d.arrow(active, inactive)

        output = render(d.build())
        assert "note right of Active: this is a short note" in output
        assert "note left of Inactive: A longer note" in output
        assert validate_plantuml(output, "note_on_state")

    def test_floating_note(self, validate_plantuml):
        """Floating notes not attached to any element."""
        with state_diagram() as d:
            d.state("foo")
            d.note("This is a floating note")

        output = render(d.build())
        # Floating notes render differently
        assert "note" in output
        assert validate_plantuml(output, "floating_note")


class TestInlineColor:
    """Doc section: Inline Color - state background colors."""

    def test_state_colors(self, validate_plantuml):
        """States with inline colors."""
        with state_diagram() as d:
            current = d.state(
                "CurrentSite",
                style=Style(background=Color.named("pink")),
            )
            with d.composite(
                "HardwareSetup",
                style=Style(background=Color.named("lightblue")),
            ) as hw:
                hw.state("Site", style=Style(background=Color.named("brown")))
            d.state("Trends", style=Style(background=Color.hex("#FFFF77")))
            d.state("Schedule", style=Style(background=Color.named("magenta")))

        output = render(d.build())
        assert "#pink" in output
        assert "#lightblue" in output
        assert "#brown" in output
        assert "#FFFF77" in output
        assert "#magenta" in output
        assert validate_plantuml(output, "inline_color")


class TestChangeStateColorAndStyle:
    """Doc section: Change State Color and Style - advanced styling."""

    def test_gradient_background(self, validate_plantuml):
        """States with gradient backgrounds."""
        with state_diagram() as d:
            d.state(
                "FooGradient",
                style=Style(
                    background=Gradient(
                        Color.named("red"), Color.named("green")
                    )
                ),
            )

        output = render(d.build())
        assert "#red|green" in output  # horizontal gradient
        assert validate_plantuml(output, "gradient")

    def test_dashed_border(self, validate_plantuml):
        """States with dashed borders."""
        with state_diagram() as d:
            d.state(
                "FooDashed",
                style=Style(
                    line=LineStyle(
                        color=Color.named("blue"), pattern=LinePattern.DASHED
                    )
                ),
            )

        output = render(d.build())
        assert "##[dashed]blue" in output
        assert validate_plantuml(output, "dashed_border")

    def test_dotted_border(self, validate_plantuml):
        """States with dotted borders."""
        with state_diagram() as d:
            d.state(
                "FooDotted",
                style=Style(
                    line=LineStyle(
                        color=Color.named("blue"), pattern=LinePattern.DOTTED
                    )
                ),
            )

        output = render(d.build())
        assert "##[dotted]blue" in output
        assert validate_plantuml(output, "dotted_border")

    def test_combined_state_style(self, validate_plantuml):
        """Full style combination with background, line, and text color."""
        with state_diagram() as d:
            d.state(
                "s2",
                description="s2 description",
                style=Style(
                    background=Color.named("pink"),
                    line=LineStyle(color=Color.named("red"), bold=True),
                    text_color=Color.named("red"),
                ),
            )

        output = render(d.build())
        assert "s2 description" in output
        assert validate_plantuml(output, "combined_style")


class TestAlias:
    """Doc section: Alias - state aliases."""

    def test_various_alias_forms(self, validate_plantuml):
        """Different ways to create state aliases."""
        with state_diagram() as d:
            d.state("alias1")  # Simple name
            d.state("long name", alias="alias3")  # Long name with alias

        output = render(d.build())
        assert "state alias1" in output
        assert 'state "long name" as alias3' in output
        assert validate_plantuml(output, "aliases")


class TestTransitionLabels:
    """Tests for transition labels with trigger, guard, and effect."""

    def test_full_transition_label(self, validate_plantuml):
        """Transition with trigger, guard condition, and effect."""
        with state_diagram() as d:
            s1 = d.state("State1")
            s2 = d.state("State2")
            d.arrow(
                s1,
                s2,
                trigger="button_click",
                guard="x > 0",
                effect="doAction()",
            )

        output = render(d.build())
        assert "button_click [x > 0] / doAction()" in output
        assert validate_plantuml(output, "full_transition")


class TestComprehensiveExample:
    """A comprehensive test combining many features."""

    def test_all_features_combined(self, validate_plantuml):
        """Test combining most features in a single diagram."""
        with state_diagram(
            title="Comprehensive State Machine", hide_empty_description=True
        ) as d:
            # Simple states with styling
            idle = d.state(
                "Idle",
                description="Waiting",
                style=Style(background=Color.named("lightgreen")),
            )

            # Composite state with entry/exit points
            with d.composite(
                "Processing",
                alias="proc",
                style=Style(background=Color.named("lightyellow")),
            ) as proc:
                entry = proc.entry_point("enter")
                exit = proc.exit_point("exit")
                work = proc.state("Working")
                proc.arrow(entry, work)
                proc.arrow(work, exit)

            # Concurrent state with regions
            with d.concurrent(
                "Monitoring", separator=RegionSeparator.HORIZONTAL
            ) as mon:
                with mon.region() as r1:
                    r1.state("HealthCheck")
                    r1.arrow(r1.start(), "HealthCheck")
                with mon.region() as r2:
                    r2.state("Logging")
                    r2.arrow(r2.start(), "Logging")

            # Fork/join
            fork = d.fork("fork1")
            join = d.join("join1")

            # Choice
            check = d.choice("validate")

            # Error state with styling
            error = d.state(
                "Error", style=Style(background=Color.named("salmon"))
            )

            # Transitions with various styles
            d.arrow(d.start(), idle)
            d.arrow(idle, check, "submit")
            d.arrow(check, proc.ref, guard="valid")
            d.arrow(
                check,
                error,
                guard="invalid",
                style=LineStyle(color=Color.named("red")),
            )
            d.arrow("enter", "Working")
            d.arrow(proc.ref, fork)
            d.arrow(fork, mon.ref)
            d.arrow(fork, d.state("Background"))
            d.arrow(mon.ref, join)
            d.arrow("Background", join)
            d.arrow(join, d.end())
            d.arrow(error, idle, "retry", direction=Direction.UP)

        output = render(d.build())
        assert "title Comprehensive State Machine" in output
        assert "hide empty description" in output
        assert "state Idle #lightgreen" in output
        assert "state enter <<entryPoint>>" in output
        assert "state fork1 <<fork>>" in output
        assert "state validate <<choice>>" in output
        assert validate_plantuml(output, "comprehensive")
