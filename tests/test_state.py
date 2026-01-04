"""Tests for state diagram primitives, builders, and renderers."""

import subprocess

import pytest

from plantuml_compose import (
    Color,
    DiagramArrowStyle,
    Direction,
    ElementStyle,
    FontStyle,
    Label,
    LinePattern,
    LineStyle,
    Note,
    NotePosition,
    Spot,
    StateDiagramStyle,
    Stereotype,
    Style,
    render,
    state_diagram,
)


class TestStateNode:
    """Tests for StateNode primitive."""

    def test_state_ref_uses_alias_when_provided(self):
        with state_diagram() as d:
            s = d.state("My State", alias="ms")
        assert s.ref == "ms"

    def test_state_ref_replaces_spaces(self):
        with state_diagram() as d:
            s = d.state("My State")
        assert s.ref == "My_State"

    def test_state_with_description(self):
        with state_diagram() as d:
            d.state("Idle", description="Waiting for input")
        output = render(d.build())
        assert "Idle : Waiting for input" in output


class TestTransition:
    """Tests for transitions between states."""

    def test_basic_arrow(self):
        with state_diagram() as d:
            a = d.state("A")
            b = d.state("B")
            d.arrow(a, b, "go")
        output = render(d.build())
        assert "A --> B : go" in output

    def test_arrow_with_trigger_guard_effect(self):
        with state_diagram() as d:
            a = d.state("A")
            b = d.state("B")
            d.arrow(a, b, trigger="event", guard="x > 0", effect="doAction()")
        output = render(d.build())
        assert "A --> B : event [x > 0] / doAction()" in output

    def test_arrow_with_direction(self):
        with state_diagram() as d:
            a = d.state("A")
            b = d.state("B")
            d.arrow(a, b, direction=Direction.DOWN)
        output = render(d.build())
        assert "A -d-> B" in output

    def test_arrow_with_style(self):
        with state_diagram() as d:
            a = d.state("A")
            b = d.state("B")
            d.arrow(a, b, style=LineStyle(pattern=LinePattern.DASHED, color=Color.named("red")))
        output = render(d.build())
        assert "-[#red,dashed]->" in output

    def test_hidden_arrow(self):
        """Hidden arrows for layout control."""
        with state_diagram() as d:
            a = d.state("A")
            b = d.state("B")
            d.arrow(a, b, style=LineStyle(pattern=LinePattern.HIDDEN))
        output = render(d.build())
        assert "A -[hidden]-> B" in output

    def test_hidden_arrow_with_direction(self):
        """Hidden arrows can have direction hints."""
        with state_diagram() as d:
            a = d.state("A")
            b = d.state("B")
            d.arrow(a, b, style=LineStyle(pattern=LinePattern.HIDDEN), direction=Direction.DOWN)
        output = render(d.build())
        assert "A -[hidden]d-> B" in output

    def test_note_on_link(self):
        """Note attached to a transition."""
        with state_diagram() as d:
            a = d.state("A")
            b = d.state("B")
            d.arrow(a, b, "go", note="This is a note")
        output = render(d.build())
        assert "A --> B : go" in output
        assert "note on link: This is a note" in output

    def test_note_on_link_multiline(self):
        """Multi-line note on a transition."""
        with state_diagram() as d:
            a = d.state("A")
            b = d.state("B")
            d.arrow(a, b, note="Line 1\nLine 2")
        output = render(d.build())
        assert "note on link" in output
        assert "Line 1" in output
        assert "Line 2" in output
        assert "end note" in output

    def test_note_on_link_with_label_object(self):
        """Note can be passed as Label object."""
        with state_diagram() as d:
            a = d.state("A")
            b = d.state("B")
            d.arrow(a, b, note=Label("Custom note"))
        output = render(d.build())
        assert "note on link: Custom note" in output

    def test_initial_and_final(self):
        with state_diagram() as d:
            s = d.state("S")
            d.arrow(d.start(), s)
            d.arrow(s, d.end())
        output = render(d.build())
        assert "[*] --> S" in output
        assert "S --> [*]" in output


class TestCompositeState:
    """Tests for composite (nested) states."""

    def test_composite_basic(self):
        with state_diagram() as d:
            with d.composite("Outer") as outer:
                inner = outer.state("Inner")
                outer.arrow(outer.start(), inner)
        output = render(d.build())
        assert "state Outer {" in output
        assert "state Inner" in output
        assert "[*] --> Inner" in output
        assert "}" in output

    def test_composite_with_alias(self):
        with state_diagram() as d:
            with d.composite("My Composite", alias="mc") as comp:
                comp.state("Sub")
            d.arrow(d.start(), comp.ref)
        output = render(d.build())
        assert 'state "My Composite" as mc {' in output
        assert "[*] --> mc" in output

    def test_nested_composite(self):
        with state_diagram() as d:
            with d.composite("Level1") as l1:
                with l1.composite("Level2") as l2:
                    s = l2.state("Deep")
                    l2.arrow(l2.start(), s)
        output = render(d.build())
        assert "state Level1 {" in output
        assert "state Level2 {" in output
        assert "state Deep" in output


class TestConcurrentState:
    """Tests for concurrent (parallel) states."""

    def test_concurrent_basic(self):
        with state_diagram() as d:
            with d.concurrent("Parallel") as par:
                with par.region() as r1:
                    r1.state("A")
                with par.region() as r2:
                    r2.state("B")
        output = render(d.build())
        assert "state Parallel {" in output
        assert "state A" in output
        assert "--" in output
        assert "state B" in output

    def test_concurrent_with_transitions(self):
        with state_diagram() as d:
            with d.concurrent("Par", alias="p") as par:
                with par.region() as r1:
                    a = r1.state("A")
                    r1.arrow(r1.start(), a)
                with par.region() as r2:
                    x = r2.state("X")
                    r2.arrow(r2.start(), x)
            d.arrow(d.start(), par.ref)
        output = render(d.build())
        assert "[*] --> A" in output
        assert "[*] --> X" in output
        assert "[*] --> p" in output


class TestPseudoStates:
    """Tests for pseudo-states (choice, fork, join)."""

    def test_choice_state(self):
        with state_diagram() as d:
            s1 = d.state("S1")
            s2 = d.state("S2")
            s3 = d.state("S3")
            c = d.choice("check")
            d.arrow(s1, c)
            d.arrow(c, s2, guard="x > 0")
            d.arrow(c, s3, guard="x <= 0")
        output = render(d.build())
        assert "state check <<choice>>" in output
        assert "S1 --> check" in output
        assert "check --> S2 : [x > 0]" in output
        assert "check --> S3 : [x <= 0]" in output

    def test_fork_join(self):
        with state_diagram() as d:
            s = d.state("Start")
            a = d.state("A")
            b = d.state("B")
            e = d.state("End")
            f = d.fork("fork1")
            j = d.join("join1")
            d.arrow(s, f)
            d.arrow(f, a)
            d.arrow(f, b)
            d.arrow(a, j)
            d.arrow(b, j)
            d.arrow(j, e)
        output = render(d.build())
        assert "state fork1 <<fork>>" in output
        assert "state join1 <<join>>" in output


class TestDiagramOptions:
    """Tests for diagram-level options."""

    def test_title(self):
        with state_diagram(title="My State Machine") as d:
            d.state("S")
        output = render(d.build())
        assert "title My State Machine" in output

    def test_hide_empty_description(self):
        with state_diagram(hide_empty_description=True) as d:
            d.state("S")
        output = render(d.build())
        assert "hide empty description" in output


class TestStateStyles:
    """Tests for style rendering on state elements."""

    def test_state_with_background_color(self):
        with state_diagram() as d:
            d.state("Colored", style=Style(background=Color.named("pink")))
        output = render(d.build())
        assert "state Colored #pink" in output

    def test_state_with_gradient_background(self):
        from plantuml_compose import Gradient

        with state_diagram() as d:
            d.state(
                "Grad",
                style=Style(
                    background=Gradient(Color.named("red"), Color.named("blue"))
                ),
            )
        output = render(d.build())
        assert "state Grad #red|blue" in output

    def test_state_with_line_style(self):
        with state_diagram() as d:
            d.state(
                "Bordered",
                style=Style(
                    line=LineStyle(color=Color.named("blue"), pattern=LinePattern.DASHED)
                ),
            )
        output = render(d.build())
        # Uses ##[pattern]color format
        assert "##[dashed]blue" in output

    def test_state_with_text_color(self):
        with state_diagram() as d:
            d.state("TextColored", style=Style(text_color=Color.named("red")))
        output = render(d.build())
        assert "text:red" in output

    def test_state_with_stereotype(self):
        with state_diagram() as d:
            d.state("Service", style=Style(stereotype=Stereotype("service")))
        output = render(d.build())
        assert "<<service>>" in output

    def test_state_with_stereotype_and_spot(self):
        with state_diagram() as d:
            d.state(
                "Important",
                style=Style(stereotype=Stereotype("critical", spot=Spot("!", Color.named("red")))),
            )
        output = render(d.build())
        assert "<< (!,#red) critical >>" in output

    def test_fork_basic(self):
        with state_diagram() as d:
            d.fork("f1")
        output = render(d.build())
        assert "state f1 <<fork>>" in output

    def test_choice_basic(self):
        with state_diagram() as d:
            d.choice("c1")
        output = render(d.build())
        assert "state c1 <<choice>>" in output

    def test_composite_with_style(self):
        with state_diagram() as d:
            with d.composite(
                "Styled", style=Style(background=Color.named("lightblue"))
            ) as comp:
                comp.state("Inner")
        output = render(d.build())
        assert "state Styled #lightblue {" in output

    def test_concurrent_with_style(self):
        with state_diagram() as d:
            with d.concurrent(
                "Par", style=Style(background=Color.named("lightyellow"))
            ) as par:
                with par.region() as r:
                    r.state("X")
        output = render(d.build())
        assert "state Par #lightyellow {" in output

    def test_concurrent_note_rendered(self):
        with state_diagram() as d:
            with d.concurrent("Par", note="A note") as par:
                with par.region() as r:
                    r.state("X")
        output = render(d.build())
        assert "note right of Par: A note" in output

    def test_full_style_combination(self):
        with state_diagram() as d:
            d.state(
                "FullStyle",
                style=Style(
                    background=Color.named("pink"),
                    line=LineStyle(color=Color.named("red"), pattern=LinePattern.DASHED),
                    text_color=Color.named("blue"),
                    stereotype=Stereotype("important"),
                ),
            )
        output = render(d.build())
        assert "<<important>>" in output
        # Uses semicolon format when text color is present
        assert "#pink;line.dashed;line:red;text:blue" in output


class TestStateDiagramStyle:
    """Tests for typed CSS-like style block support."""

    def test_style_with_background(self):
        """Style with root-level background color."""
        with state_diagram(
            style=StateDiagramStyle(background=Color.named("white"))
        ) as d:
            d.state("S1")

        output = render(d.build())
        assert "<style>" in output
        assert "stateDiagram {" in output
        assert "BackgroundColor white" in output
        assert "</style>" in output

    def test_style_with_font_properties(self):
        """Style with font properties."""
        with state_diagram(
            style=StateDiagramStyle(
                font_name="Arial",
                font_size=14,
                font_color=Color.named("black"),
            )
        ) as d:
            d.state("S1")

        output = render(d.build())
        assert "FontName Arial" in output
        assert "FontSize 14" in output
        assert "FontColor black" in output

    def test_style_block_appears_before_title(self):
        """Style block should appear before title in the output."""
        with state_diagram(
            title="My Diagram",
            style=StateDiagramStyle(background=Color.named("white")),
        ) as d:
            d.state("S1")

        output = render(d.build())
        style_pos = output.find("<style>")
        title_pos = output.find("title My Diagram")
        assert style_pos < title_pos, "Style block should appear before title"

    def test_no_style_block_when_none(self):
        """No style block when not specified."""
        with state_diagram() as d:
            d.state("S1")

        output = render(d.build())
        assert "<style>" not in output

    def test_state_element_style(self):
        """Style for state elements."""
        with state_diagram(
            style=StateDiagramStyle(
                state=ElementStyle(
                    background=Color.hex("#E3F2FD"),
                    line_color=Color.hex("#1976D2"),
                    font_color=Color.hex("#0D47A1"),
                    round_corner=10,
                )
            )
        ) as d:
            d.state("S1")

        output = render(d.build())
        assert "state {" in output
        assert "BackgroundColor #E3F2FD" in output
        assert "LineColor #1976D2" in output
        assert "FontColor #0D47A1" in output
        assert "RoundCorner 10" in output

    def test_arrow_style(self):
        """Style for arrows."""
        with state_diagram(
            style=StateDiagramStyle(
                arrow=DiagramArrowStyle(
                    line_color=Color.hex("#757575"),
                    line_thickness=2,
                    line_pattern=LinePattern.DASHED,
                )
            )
        ) as d:
            s1 = d.state("S1")
            s2 = d.state("S2")
            d.arrow(s1, s2)

        output = render(d.build())
        assert "arrow {" in output
        assert "LineColor #757575" in output
        assert "LineThickness 2" in output
        assert "LineStyle dashed" in output

    def test_full_style_block(self):
        """Complete style block with all element types."""
        with state_diagram(
            style=StateDiagramStyle(
                background=Color.named("white"),
                font_name="Arial",
                state=ElementStyle(
                    background=Color.hex("#E3F2FD"),
                    line_color=Color.hex("#1976D2"),
                ),
                arrow=DiagramArrowStyle(
                    line_color=Color.hex("#757575"),
                ),
                note=ElementStyle(
                    background=Color.named("lightyellow"),
                ),
            )
        ) as d:
            s1 = d.state("S1")
            s2 = d.state("S2")
            d.arrow(s1, s2)

        output = render(d.build())
        assert "BackgroundColor white" in output
        assert "FontName Arial" in output
        assert "state {" in output
        assert "arrow {" in output
        assert "note {" in output
        assert "BackgroundColor lightyellow" in output

    def test_element_style_font_properties(self):
        """Element style with font properties."""
        with state_diagram(
            style=StateDiagramStyle(
                state=ElementStyle(
                    font_name="Courier",
                    font_size=12,
                    font_style=FontStyle.BOLD,
                )
            )
        ) as d:
            d.state("S1")

        output = render(d.build())
        assert "FontName Courier" in output
        assert "FontSize 12" in output
        assert "FontStyle bold" in output

    def test_empty_style_no_output(self):
        """Empty StateDiagramStyle should not emit style block."""
        with state_diagram(style=StateDiagramStyle()) as d:
            d.state("S1")

        output = render(d.build())
        assert "<style>" not in output
        assert "stateDiagram {" not in output

    def test_empty_element_style_no_nested_block(self):
        """Empty ElementStyle should not emit nested block."""
        with state_diagram(
            style=StateDiagramStyle(
                background=Color.named("white"),
                state=ElementStyle(),  # Empty - should not emit state {}
            )
        ) as d:
            d.state("S1")

        output = render(d.build())
        assert "BackgroundColor white" in output
        # Should not have empty state block
        assert "state {\n  }" not in output
        assert "state {}" not in output

    def test_title_uses_document_selector(self):
        """Title styling should use document selector, not stateDiagram."""
        with state_diagram(
            style=StateDiagramStyle(
                title=ElementStyle(font_color=Color.named("red"))
            )
        ) as d:
            d.state("S1")

        output = render(d.build())
        # Title must be under document, not stateDiagram
        assert "document {" in output
        assert "title {" in output
        assert "FontColor red" in output
        # Verify it's NOT under stateDiagram (which would style states, not title)
        lines = output.split("\n")
        in_document = False
        title_in_document = False
        for line in lines:
            if "document {" in line:
                in_document = True
            if in_document and "title {" in line:
                title_in_document = True
                break
            if in_document and "}" in line and "title" not in line:
                in_document = False
        assert title_in_document, "title block should be inside document block"

    def test_gradient_in_style_background(self):
        """Gradient should work in style block background."""
        from plantuml_compose import Gradient

        with state_diagram(
            style=StateDiagramStyle(
                background=Gradient(Color.named("red"), Color.named("green"))
            )
        ) as d:
            d.state("S1")

        output = render(d.build())
        assert "BackgroundColor red|green" in output


class TestPlantUMLValidation:
    """Integration tests that validate output with PlantUML and generate SVGs."""

    @pytest.fixture
    def render_svg(self, request):
        """Fixture that validates PlantUML and renders to SVG in tests/output/."""
        from pathlib import Path

        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)

        def _render(puml_text: str, name: str) -> bool:
            puml_file = output_dir / f"{name}.puml"
            svg_file = output_dir / f"{name}.svg"

            puml_file.write_text(puml_text)

            # Generate SVG
            result = subprocess.run(
                ["plantuml", "-tsvg", str(puml_file)],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print(f"PlantUML error: {result.stderr}")
                return False

            return svg_file.exists()

        return _render

    def test_basic_diagram(self, render_svg):
        with state_diagram(title="Basic State Diagram") as d:
            a = d.state("A")
            b = d.state("B")
            d.arrow(d.start(), a)
            d.arrow(a, b, "transition")
            d.arrow(b, d.end())
        assert render_svg(render(d.build()), "01_basic")

    def test_composite_diagram(self, render_svg):
        with state_diagram(title="Composite State") as d:
            idle = d.state("Idle")
            with d.composite("Active") as active:
                sub1 = active.state("Sub1")
                sub2 = active.state("Sub2")
                active.arrow(active.start(), sub1)
                active.arrow(sub1, sub2)
                active.arrow(sub2, active.end())
            d.arrow(d.start(), idle)
            d.arrow(idle, active.ref, "activate")
            d.arrow(active.ref, idle, "done")
        assert render_svg(render(d.build()), "02_composite")

    def test_concurrent_diagram(self, render_svg):
        with state_diagram(title="Concurrent State") as d:
            with d.concurrent("Parallel") as par:
                with par.region() as r1:
                    a = r1.state("A")
                    b = r1.state("B")
                    r1.arrow(r1.start(), a)
                    r1.arrow(a, b)
                with par.region() as r2:
                    x = r2.state("X")
                    y = r2.state("Y")
                    r2.arrow(r2.start(), x)
                    r2.arrow(x, y)
            d.arrow(d.start(), par.ref)
            d.arrow(par.ref, d.end())
        assert render_svg(render(d.build()), "03_concurrent")

    def test_styled_states(self, render_svg):
        from plantuml_compose import Gradient

        with state_diagram(title="Styled States") as d:
            # Background colors
            pink = d.state("Pink", style=Style(background=Color.named("pink")))
            gradient = d.state(
                "Gradient",
                style=Style(background=Gradient(Color.named("red"), Color.named("yellow"))),
            )

            # Line styles
            dashed = d.state(
                "DashedBorder",
                style=Style(line=LineStyle(pattern=LinePattern.DASHED, color=Color.named("blue"))),
            )

            # Text color
            colored_text = d.state("ColoredText", style=Style(text_color=Color.named("green")))

            # Stereotype
            service = d.state("Service", style=Style(stereotype=Stereotype("service")))

            # With spot
            critical = d.state(
                "Critical",
                style=Style(stereotype=Stereotype("important", spot=Spot("!", Color.named("red")))),
            )

            d.arrow(d.start(), pink)
            d.arrow(pink, gradient)
            d.arrow(gradient, dashed)
            d.arrow(dashed, colored_text)
            d.arrow(colored_text, service)
            d.arrow(service, critical)
            d.arrow(critical, d.end())

        assert render_svg(render(d.build()), "04_styled_states")

    def test_pseudo_states(self, render_svg):
        """Test pseudo-states (fork, join, choice).

        Note: PlantUML does not support styling any pseudo-states.
        Fork/join bars and choice diamonds always render in default gray.
        We don't expose style parameters on these methods.
        """
        with state_diagram(title="Pseudo-States") as d:
            s1 = d.state("S1")
            s2 = d.state("S2")
            s3 = d.state("S3")
            s4 = d.state("S4")

            # No style parameters - PlantUML doesn't render them
            fork = d.fork("fork1")
            join = d.join("join1")
            choice = d.choice("check")

            d.arrow(d.start(), s1)
            d.arrow(s1, fork)
            d.arrow(fork, s2)
            d.arrow(fork, s3)
            d.arrow(s2, join)
            d.arrow(s3, join)
            d.arrow(join, choice)
            d.arrow(choice, s4, guard="ok")
            d.arrow(choice, d.end(), guard="fail")
            d.arrow(s4, d.end())

        assert render_svg(render(d.build()), "05_styled_pseudo")

    def test_styled_composite(self, render_svg):
        with state_diagram(title="Styled Composite") as d:
            with d.composite(
                "StyledComposite",
                style=Style(
                    background=Color.named("lightyellow"),
                    stereotype=Stereotype("subsystem"),
                ),
            ) as comp:
                inner = comp.state("Inner", style=Style(background=Color.named("lightblue")))
                comp.arrow(comp.start(), inner)
                comp.arrow(inner, comp.end())

            d.arrow(d.start(), comp.ref)
            d.arrow(comp.ref, d.end())

        assert render_svg(render(d.build()), "06_styled_composite")

    def test_styled_arrows(self, render_svg):
        with state_diagram(title="Styled Arrows") as d:
            a = d.state("A")
            b = d.state("B")
            c = d.state("C")
            e = d.state("D")
            f = d.state("E")

            d.arrow(d.start(), a)
            d.arrow(a, b, "dashed red", style=LineStyle(pattern=LinePattern.DASHED, color=Color.named("red")))
            d.arrow(b, c, "dotted blue", style=LineStyle(pattern=LinePattern.DOTTED, color=Color.named("blue")))
            d.arrow(c, e, "thick", style=LineStyle(thickness=3))
            d.arrow(e, f, "bold green", style=LineStyle(bold=True, color=Color.named("green")))
            d.arrow(f, d.end())

        assert render_svg(render(d.build()), "07_styled_arrows")

    def test_full_featured(self, render_svg):
        """Comprehensive test with all features."""
        with state_diagram(title="Full Featured State Diagram", hide_empty_description=True) as d:
            idle = d.state("Idle", description="Waiting for input")

            with d.composite(
                "Processing",
                alias="proc",
                style=Style(background=Color.named("lightyellow")),
            ) as proc:
                init = proc.state("Init", style=Style(background=Color.named("lightgreen")))
                working = proc.state("Working")
                proc.arrow(proc.start(), init)
                proc.arrow(init, working, "start")
                proc.arrow(working, proc.end(), "done")

            with d.concurrent("Monitoring", alias="mon", note="Runs in parallel") as mon:
                with mon.region() as r1:
                    check = r1.state("HealthCheck")
                    r1.arrow(r1.start(), check)
                with mon.region() as r2:
                    log = r2.state("Logging")
                    r2.arrow(r2.start(), log)

            error = d.state("Error", style=Style(background=Color.named("salmon")))
            choice = d.choice("validate")  # No style - PlantUML doesn't render it

            d.arrow(d.start(), idle)
            d.arrow(idle, choice, "submit")
            d.arrow(choice, proc.ref, guard="valid")
            d.arrow(choice, error, guard="invalid", style=LineStyle(color=Color.named("red")))
            d.arrow(proc.ref, mon.ref, "monitor")
            d.arrow(mon.ref, d.end(), "complete")
            d.arrow(error, idle, "retry", direction=Direction.UP)

        assert render_svg(render(d.build()), "08_full_featured")
