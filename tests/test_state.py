"""Tests for state diagram primitives, builders, and renderers."""

import pytest

# validate_plantuml fixture is provided by conftest.py

from plantuml_compose import (
    Color,
    DiagramArrowStyle,
    ElementStyle,
    Gradient,
    Label,
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
        assert s._ref == "ms"

    def test_state_ref_replaces_spaces(self):
        with state_diagram() as d:
            s = d.state("My State")
        assert s._ref == "My_State"

    def test_state_with_description(self):
        with state_diagram() as d:
            d.state("Idle", description="Waiting for input")
        output = render(d.build())
        assert "Idle : Waiting for input" in output


class TestBulkStates:
    """Tests for states() bulk state creation."""

    def test_states_creates_multiple(self):
        """states() creates multiple StateNodes at once."""
        with state_diagram() as d:
            a, b, c = d.states("A", "B", "C")
        assert a._ref == "A"
        assert b._ref == "B"
        assert c._ref == "C"

    def test_states_with_style(self):
        """states() applies style to all created states."""
        with state_diagram() as d:
            a, b = d.states(
                "A", "B", style=Style(background=Color.named("lightblue"))
            )
        output = render(d.build())
        assert "A #lightblue" in output
        assert "B #lightblue" in output

    def test_states_returns_tuple(self):
        """states() returns a tuple for unpacking."""
        with state_diagram() as d:
            result = d.states("X", "Y")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_states_empty(self):
        """states() with no args returns empty tuple."""
        with state_diagram() as d:
            result = d.states()
        assert result == ()


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_state_name(self):
        """Empty state names are accepted (PlantUML handles gracefully)."""
        with state_diagram() as d:
            s = d.state("")
            d.arrow(d.start(), s)
        output = render(d.build())
        assert "@startuml" in output
        assert "@enduml" in output

    def test_state_name_with_special_characters(self):
        """State names with special characters use alias for safety."""
        with state_diagram() as d:
            s = d.state("State: Loading...", alias="loading")
            d.arrow(d.start(), s)
        output = render(d.build())
        assert 'state "State: Loading..." as loading' in output
        assert "[*] --> loading" in output

    def test_state_name_with_quotes(self):
        """State names containing quotes should be escaped and aliased."""
        with state_diagram() as d:
            quoted = d.state('He said "hi"')
            d.arrow(d.start(), quoted)

        output = render(d.build())
        assert 'state "He said \\"hi\\"" as He_said_hi' in output
        assert "[*] --> He_said_hi" in output

    def test_state_name_with_hyphen(self, validate_plantuml):
        """State names with hyphens must be sanitized - PlantUML treats - as arrow syntax."""
        with state_diagram() as d:
            api = d.state("pxe-api")
            client = d.state("pxe-client")
            d.arrow(client, api)

        output = render(d.build())
        # Hyphens removed from refs to avoid PlantUML arrow syntax conflicts
        assert 'state "pxe-api" as pxeapi' in output
        assert 'state "pxe-client" as pxeclient' in output
        assert "pxeclient --> pxeapi" in output
        assert validate_plantuml(output, "hyphen_state")

    def test_self_transition(self):
        """Self-transitions (state to itself) are valid."""
        with state_diagram() as d:
            s = d.state("Retry")
            d.arrow(s, s, label="retry")
        output = render(d.build())
        assert "Retry --> Retry : retry" in output

    def test_transition_label_with_quotes(self):
        """Transition labels containing quotes should be escaped."""
        with state_diagram() as d:
            a = d.state("A")
            b = d.state("B")
            d.arrow(a, b, label='say "hi"')

        output = render(d.build())
        assert 'A --> B : say \\"hi\\"' in output

    def test_unicode_state_name(self, validate_plantuml):
        """Unicode characters in state names render correctly."""
        with state_diagram() as d:
            s = d.state("待機中", alias="waiting")
            d.arrow(d.start(), s)
        output = render(d.build())
        assert "待機中" in output
        assert validate_plantuml(output, "unicode")

    def test_multiline_description(self):
        """Multi-line descriptions use \\n separator."""
        with state_diagram() as d:
            d.state("Complex", description="Line 1\\nLine 2")
        output = render(d.build())
        assert "Line 1\\nLine 2" in output

    def test_empty_diagram(self):
        """Empty diagram with no elements is valid."""
        with state_diagram() as d:
            pass
        output = render(d.build())
        assert "@startuml" in output
        assert "@enduml" in output

    def test_transition_to_undeclared_state(self, validate_plantuml):
        """Transitions can reference states by string name (auto-created by PlantUML)."""
        with state_diagram() as d:
            d.arrow("A", "B", label="go")
        output = render(d.build())
        assert "A --> B : go" in output
        assert validate_plantuml(output, "undeclared")

    def test_duplicate_state_names(self):
        """Duplicate state names create separate state declarations."""
        with state_diagram() as d:
            s1 = d.state("Same")
            s2 = d.state("Same")
            d.arrow(s1, s2)
        output = render(d.build())
        # Both declarations appear
        assert output.count("state Same") == 2


class TestTransition:
    """Tests for transitions between states."""

    def test_basic_arrow(self):
        with state_diagram() as d:
            a = d.state("A")
            b = d.state("B")
            d.arrow(a, b, label="go")
        output = render(d.build())
        assert "A --> B : go" in output

    def test_arrow_with_trigger_guard_effect(self):
        with state_diagram() as d:
            a = d.state("A")
            b = d.state("B")
            d.arrow(a, b, trigger="event", guard="x > 0", effect="doAction()")
        output = render(d.build())
        assert "A --> B : event [x > 0] / doAction()" in output

    def test_arrow_directions(self):
        """Arrow direction hints for layout control (up, down, left, right)."""
        with state_diagram() as d:
            s1 = d.state("S1")
            s2 = d.state("S2")
            s3 = d.state("S3")
            s4 = d.state("S4")
            d.arrow(d.start(), s1, direction="up")
            d.arrow(s1, s2, direction="right")
            d.arrow(s2, s3, direction="down")
            d.arrow(s3, s4, direction="left")
        output = render(d.build())
        assert "[*] -u-> S1" in output
        assert "S1 -r-> S2" in output
        assert "S2 -d-> S3" in output
        assert "S3 -l-> S4" in output

    def test_arrow_with_style(self):
        with state_diagram() as d:
            a = d.state("A")
            b = d.state("B")
            d.arrow(
                a,
                b,
                style=LineStyle(pattern="dashed", color=Color.named("red")),
            )
        output = render(d.build())
        assert "-[#red,dashed]->" in output

    def test_hidden_arrow(self):
        """Hidden arrows for layout control."""
        with state_diagram() as d:
            a = d.state("A")
            b = d.state("B")
            d.arrow(a, b, style=LineStyle(pattern="hidden"))
        output = render(d.build())
        assert "A -[hidden]-> B" in output

    def test_hidden_arrow_with_direction(self):
        """Hidden arrows can have direction hints."""
        with state_diagram() as d:
            a = d.state("A")
            b = d.state("B")
            d.arrow(a, b, style=LineStyle(pattern="hidden"), direction="down")
        output = render(d.build())
        assert "A -[hidden]d-> B" in output

    def test_note_on_link(self):
        """Note attached to a transition."""
        with state_diagram() as d:
            a = d.state("A")
            b = d.state("B")
            d.arrow(a, b, label="go", note="This is a note")
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


class TestVariadicArrow:
    """Tests for variadic arrow() method (chain transitions)."""

    def test_arrow_chain_three_states(self):
        """arrow(a, b, c) creates two transitions."""
        with state_diagram() as d:
            a, b, c = d.states("A", "B", "C")
            transitions = d.arrow(a, b, c)
        assert len(transitions) == 2
        output = render(d.build())
        assert "A --> B" in output
        assert "B --> C" in output

    def test_arrow_chain_with_label(self):
        """Label is applied to all transitions in chain."""
        with state_diagram() as d:
            a, b, c = d.states("A", "B", "C")
            d.arrow(a, b, c, label="next")
        output = render(d.build())
        assert "A --> B : next" in output
        assert "B --> C : next" in output

    def test_arrow_chain_four_states(self):
        """arrow(a, b, c, d) creates three transitions."""
        with state_diagram() as d:
            a, b, c, e = d.states("A", "B", "C", "D")
            transitions = d.arrow(a, b, c, e)
        assert len(transitions) == 3

    def test_arrow_returns_list(self):
        """arrow() now returns list[Transition]."""
        with state_diagram() as d:
            a, b = d.states("A", "B")
            result = d.arrow(a, b)
        assert isinstance(result, list)
        assert len(result) == 1

    def test_arrow_requires_two_states(self):
        """arrow() with less than 2 states raises ValueError."""
        import pytest

        with state_diagram() as d:
            a = d.state("A")
            with pytest.raises(ValueError, match="at least 2 states"):
                d.arrow(a)


class TestRenderMethod:
    """Tests for StateDiagramBuilder.render() convenience method."""

    def test_render_returns_plantuml_text(self):
        """render() returns PlantUML text without calling build() explicitly."""
        with state_diagram(title="Test") as d:
            d.state("Idle")
        output = d.render()
        assert "@startuml" in output
        assert "title Test" in output
        assert "state Idle" in output
        assert "@enduml" in output

    def test_render_equivalent_to_render_build(self):
        """render() produces same output as render(d.build())."""
        with state_diagram() as d:
            a, b = d.states("A", "B")
            d.arrow(a, b)
        assert d.render() == render(d.build())


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
            d.arrow(d.start(), comp)
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

    def test_composite_ref_sanitizes_spaces(self):
        """Builder _ref must match primitive _ref for names with spaces."""
        with state_diagram() as d:
            with d.composite("Review Process") as comp:
                comp.state("Inner")
            d.arrow(d.start(), comp)
        output = render(d.build())
        # Transition should use sanitized ref matching declaration alias
        assert "[*] --> Review_Process" in output
        assert 'state "Review Process" as Review_Process' in output


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
            d.arrow(d.start(), par)
        output = render(d.build())
        assert "[*] --> A" in output
        assert "[*] --> X" in output
        assert "[*] --> p" in output

    def test_concurrent_vertical_separator(self):
        """Concurrent regions with vertical separator (side-by-side)."""
        with state_diagram() as d:
            with d.concurrent("Active", separator="vertical") as active:
                with active.region() as r1:
                    r1.state("NumLockOff")
                with active.region() as r2:
                    r2.state("CapsLockOff")
            d.arrow(d.start(), active)
        output = render(d.build())
        assert "||" in output

    def test_concurrent_ref_sanitizes_spaces(self):
        """Builder _ref must match primitive _ref for names with spaces."""
        with state_diagram() as d:
            with d.concurrent("Parallel Region") as conc:
                with conc.region() as r:
                    r.state("Inner")
            d.arrow(d.start(), conc)
        output = render(d.build())
        # Transition should use sanitized ref matching declaration alias
        assert "[*] --> Parallel_Region" in output
        assert 'state "Parallel Region" as Parallel_Region' in output


class TestParallel:
    """Tests for parallel() fork/join builder."""

    def test_parallel_basic(self):
        """parallel() creates fork, branches, and join."""
        with state_diagram() as d:
            with d.parallel("P") as p:
                with p.branch() as b1:
                    b1.state("A")
                with p.branch() as b2:
                    b2.state("B")
        output = render(d.build())
        assert 'state "P_fork" as P_fork <<fork>>' in output
        assert 'state "P_join" as P_join <<join>>' in output
        assert "P_fork --> A" in output
        assert "P_fork --> B" in output
        assert "A --> P_join" in output
        assert "B --> P_join" in output

    def test_parallel_with_multi_step_branch(self):
        """Branch can have multiple states and transitions."""
        with state_diagram() as d:
            with d.parallel("Flow") as p:
                with p.branch() as b:
                    a = b.state("A")
                    middle = b.state("B")
                    c = b.state("C")
                    b.arrow(a, middle, c)
        output = render(d.build())
        # Entry is A, exit is C (no outgoing transitions)
        assert "Flow_fork --> A" in output
        assert "A --> B" in output
        assert "B --> C" in output
        assert "C --> Flow_join" in output

    def test_parallel_fork_join_accessible_after_block(self):
        """p.fork and p.join are accessible after parallel block exits."""
        with state_diagram() as d:
            start = d.state("Start")
            done = d.state("Done")

            with d.parallel("P") as p:
                with p.branch() as b:
                    b.state("Work")

            d.arrow(start, p.fork)
            d.arrow(p.join, done)
        output = render(d.build())
        assert "Start --> P_fork" in output
        assert "P_join --> Done" in output

    def test_parallel_unnamed(self):
        """parallel() without name generates unique fork/join names."""
        with state_diagram() as d:
            with d.parallel() as p:
                with p.branch() as b:
                    b.state("X")
        output = render(d.build())
        # Unnamed parallel blocks get unique names like "parallel_N_fork"
        assert output.count("parallel_") >= 2
        assert "<<fork>>" in output
        assert "<<join>>" in output
        assert 'state "parallel_' in output

    def test_parallel_requires_at_least_one_branch(self):
        """parallel() with no branches raises ValueError."""
        import pytest

        with state_diagram() as d:
            with pytest.raises(ValueError, match="at least one branch"):
                with d.parallel() as _parallel:
                    pass  # No branches

    def test_parallel_branch_requires_element(self):
        """Branch with no elements raises ValueError."""
        import pytest

        with state_diagram() as d:
            with pytest.raises(ValueError, match="at least one element"):
                with d.parallel() as p:
                    with p.branch() as _branch:
                        pass  # No elements

    def test_parallel_integration(self, validate_plantuml):
        """Full parallel example validates with PlantUML."""
        with state_diagram(title="Parallel Processing") as d:
            start = d.state("Start")
            done = d.state("Done")

            with d.parallel("Process") as p:
                with p.branch() as b1:
                    b1.state("TaskA")
                with p.branch() as b2:
                    b2.state("TaskB")
                with p.branch() as b3:
                    step1 = b3.state("Step1")
                    step2 = b3.state("Step2")
                    b3.arrow(step1, step2)

            d.arrow(d.start(), start)
            d.arrow(start, p.fork)
            d.arrow(p.join, done)
            d.arrow(done, d.end())

        assert validate_plantuml(d.render(), "parallel")

    def test_parallel_unnamed_ref_matches_actual_name(self):
        """Bug: _ref returns 'parallel_fork' but pseudo-state is named 'fork'.

        When using an unnamed parallel builder directly in arrow(), the
        generated transition should point to a valid pseudo-state name.
        """
        with state_diagram() as d:
            start = d.state("Start")
            with d.parallel() as p:
                with p.branch() as b:
                    b.state("Work")
            # Using the builder directly (not p.fork) should also work
            d.arrow(start, p._ref)

        output = render(d.build())
        # The transition target must match an actual declared pseudo-state
        # Currently _ref returns "parallel_fork" but the state is named "fork"
        lines = output.split("\n")

        # Find what fork name is actually declared
        fork_decl = [line for line in lines if "<<fork>>" in line]
        assert len(fork_decl) == 1, (
            f"Expected exactly one fork declaration, got: {fork_decl}"
        )
        declared_fork_name = (
            fork_decl[0].split()[1].strip('"')
        )  # "state NAME <<fork>>"

        # Find the transition from Start
        start_transition = [
            line for line in lines if line.startswith("Start -->")
        ]
        assert len(start_transition) == 1
        target = start_transition[0].split("-->")[1].strip()

        assert target == declared_fork_name, (
            f"Transition target '{target}' doesn't match declared fork '{declared_fork_name}'"
        )

    def test_parallel_multiple_unnamed_unique_names(self):
        """Bug: Multiple unnamed parallel() blocks create duplicate 'fork'/'join' names.

        Each parallel block should generate unique pseudo-state names to avoid
        PlantUML rendering duplicate nodes.
        """
        with state_diagram() as d:
            # Two unnamed parallel blocks
            with d.parallel() as p1:
                with p1.branch() as b:
                    b.state("A")
            with d.parallel() as p2:
                with p2.branch() as b:
                    b.state("B")

        output = render(d.build())
        lines = output.split("\n")

        # Count fork declarations - should be 2 unique ones
        fork_decls = [line for line in lines if "<<fork>>" in line]
        fork_names = [line.split()[1].strip('"') for line in fork_decls]

        assert len(fork_names) == 2, (
            f"Expected 2 fork declarations, got {len(fork_names)}"
        )
        assert len(set(fork_names)) == 2, (
            f"Fork names should be unique, got duplicates: {fork_names}"
        )

    def test_parallel_branch_with_composite_state(self):
        """Bug: Branch containing only CompositeState raises ValueError.

        _BranchBuilder._analyze() only looks at StateNode instances,
        so branches with composite states fail even though they're valid.
        """
        with state_diagram() as d:
            with d.parallel("P") as p:
                with p.branch() as b:
                    # Branch contains only a composite state
                    with b.composite("Inner") as inner:
                        inner.state("Nested")

        output = render(d.build())
        # Should successfully render with composite as the branch entry/exit
        assert "P_fork" in output
        assert "P_join" in output
        assert "Inner" in output

    def test_parallel_branch_with_concurrent_state(self):
        """Bug: Branch containing only ConcurrentState raises ValueError.

        Similar to composite - concurrent states should work as branch content.
        """
        with state_diagram() as d:
            with d.parallel("P") as p:
                with p.branch() as b:
                    # Branch contains only a concurrent state
                    with b.concurrent("Regions") as conc:
                        with conc.region() as r:
                            r.state("R1")

        output = render(d.build())
        assert "P_fork" in output
        assert "P_join" in output
        assert "Regions" in output


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
        assert 'state "check" as check <<choice>>' in output
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
        assert 'state "fork1" as fork1 <<fork>>' in output
        assert 'state "join1" as join1 <<join>>' in output

    def test_choice_with_spaces_in_name(self):
        """Pseudo-state names with spaces are sanitized for transitions."""
        with state_diagram() as d:
            s = d.state("Start")
            c = d.choice("Decision Point")
            d.arrow(s, c)
        output = render(d.build())
        # Alias must match what transitions use
        assert 'state "Decision Point" as Decision_Point <<choice>>' in output
        assert "Start --> Decision_Point" in output


class TestHistory:
    """Tests for history pseudo-states [H] and [H*]."""

    def test_history_state(self):
        """History pseudo-state [H] for returning to previous state."""
        with state_diagram() as d:
            s1 = d.state("State1")
            s2 = d.state("State2")
            with d.composite("State3") as s3:
                s3.state("ProcessData")
            d.arrow(d.start(), s1)
            d.arrow(s1, s2)
            d.arrow(s2, s3)
            d.arrow(s2, d.history(), label="Resume")
        output = render(d.build())
        assert "State2 --> [H]" in output

    def test_deep_history_state(self):
        """Deep history pseudo-state [H*]."""
        with state_diagram() as d:
            s2 = d.state("State2")
            with d.composite("State3") as s3:
                s3.state("ProcessData")
            d.arrow(s2, d.deep_history(), label="DeepResume")
        output = render(d.build())
        assert "State2 --> [H*]" in output


class TestStereotypes:
    """Tests for all available pseudo-state stereotypes."""

    def test_entry_exit_points(self):
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
        assert 'state "entry1" as entry1 <<entryPoint>>' in output
        assert 'state "exitA" as exitA <<exitPoint>>' in output

    def test_input_output_pins(self):
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
        assert 'state "input1" as input1 <<inputPin>>' in output
        assert 'state "output1" as output1 <<outputPin>>' in output

    def test_sdl_receive(self):
        """SDL receive pseudo-state."""
        with state_diagram() as d:
            receive = d.sdl_receive("ReqId")
            d.arrow("Idle", receive)
        output = render(d.build())
        assert 'state "ReqId" as ReqId <<sdlreceive>>' in output

    def test_expansion_points(self):
        """Expansion input/output pseudo-states."""
        with state_diagram() as d:
            exp_in = d.expansion_input("expIn")
            exp_out = d.expansion_output("expOut")
            d.arrow(exp_in, exp_out)
        output = render(d.build())
        assert 'state "expIn" as expIn <<expansionInput>>' in output
        assert 'state "expOut" as expOut <<expansionOutput>>' in output


class TestDiagramOptions:
    """Tests for diagram-level options."""

    def test_title(self):
        with state_diagram(title="My State Machine") as d:
            d.state("S")
        output = render(d.build())
        assert "title My State Machine" in output

    def test_multiline_title(self):
        """Multi-line titles use block syntax."""
        with state_diagram(title="Line 1\nLine 2") as d:
            d.state("S")
        output = render(d.build())
        assert "title\n" in output
        assert "  Line 1" in output
        assert "  Line 2" in output
        assert "end title" in output

    def test_hide_empty_description(self):
        with state_diagram(hide_empty_description=True) as d:
            d.state("S")
        output = render(d.build())
        assert "hide empty description" in output

    def test_floating_note(self):
        """Floating notes not attached to any element."""
        with state_diagram() as d:
            d.state("foo")
            d.note("This is a floating note")
        output = render(d.build())
        assert "note" in output
        assert "This is a floating note" in output

    def test_floating_note_position_respected(self):
        """Bug: Floating note position is ignored in rendering.

        The renderer outputs 'note: content' but ignores the position,
        so 'note left: content' or 'note right: content' never appears.
        """
        with state_diagram() as d:
            d.state("S1")
            d.note("Left note", position="left")

        output = render(d.build())
        # Position should be included in the output
        assert "note left" in output, (
            f"Expected 'note left' in output, got: {output}"
        )

    def test_floating_note_all_positions(self):
        """Test that various floating note positions render correctly."""
        positions: tuple[NotePosition, ...] = ("left", "right", "top", "bottom")
        for position in positions:
            with state_diagram() as d:
                d.state("S1")
                d.note(f"A {position} note", position=position)

            output = render(d.build())
            assert f"note {position}" in output, (
                f"Expected 'note {position}' for position={position}, got: {output}"
            )

    def test_note_on_state(self):
        """Notes attached to states with position control."""
        with state_diagram() as d:
            active = d.state("Active", note="this is a short note")
            inactive = d.state(
                "Inactive",
                note=Note(Label("A longer note"), "left"),
            )
            d.arrow(d.start(), active)
            d.arrow(active, inactive)
        output = render(d.build())
        assert "note right of Active: this is a short note" in output
        assert "note left of Inactive: A longer note" in output

    def test_explicit_floating_note_keyword(self):
        """Explicit floating notes should use the 'floating note' syntax."""
        with state_diagram() as d:
            d.state("S1")
            d.note("Detached", position="floating")

        output = render(d.build())
        assert "floating note" in output

    def test_floating_note_multiline_block(self):
        """Floating note with multi-line content should use block syntax."""
        with state_diagram() as d:
            d.note("Line 1\nLine 2", position="right")

        output = render(d.build())
        assert "note right" in output
        assert "Line 1" in output
        assert "Line 2" in output
        assert "end note" in output

    def test_state_note_multiline_block(self):
        """State-attached notes with newlines should render as blocks."""
        with state_diagram() as d:
            noted = d.state("HasNote", note="First\nSecond")
            d.arrow(d.start(), noted)

        output = render(d.build())
        assert "note right of HasNote" in output
        assert "First" in output
        assert "Second" in output
        assert "end note" in output


class TestStateStyles:
    """Tests for style rendering on state elements."""

    def test_state_with_background_color(self):
        with state_diagram() as d:
            d.state("Colored", style=Style(background=Color.named("pink")))
        output = render(d.build())
        assert "state Colored #pink" in output

    def test_state_with_gradient_background(self):
        with state_diagram() as d:
            d.state(
                "Grad",
                style=Style(
                    background=Gradient(Color.named("red"), Color.named("blue"))
                ),
            )
        output = render(d.build())
        assert "state Grad #red|blue" in output

    def test_state_with_style_dict_gradient(self):
        """Dict-based styles should accept Gradient instances."""
        with state_diagram() as d:
            d.state(
                "DictGrad",
                style={
                    "background": Gradient(
                        Color.named("black"),
                        Color.named("white"),
                    )
                },
            )

        output = render(d.build())
        assert "state DictGrad #black|white" in output

    def test_state_with_line_style(self):
        with state_diagram() as d:
            d.state(
                "Bordered",
                style=Style(
                    line=LineStyle(color=Color.named("blue"), pattern="dashed")
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
                style=Style(
                    stereotype=Stereotype(
                        "critical", spot=Spot("!", Color.named("red"))
                    )
                ),
            )
        output = render(d.build())
        assert "<< (!,#red) critical >>" in output

    def test_fork_basic(self):
        with state_diagram() as d:
            d.fork("f1")
        output = render(d.build())
        assert 'state "f1" as f1 <<fork>>' in output

    def test_choice_basic(self):
        with state_diagram() as d:
            d.choice("c1")
        output = render(d.build())
        assert 'state "c1" as c1 <<choice>>' in output

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
                    line=LineStyle(color=Color.named("red"), pattern="dashed"),
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
                    line_pattern="dashed",
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
                    font_style="bold",
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

        with state_diagram(
            style=StateDiagramStyle(
                background=Gradient(Color.named("red"), Color.named("green"))
            )
        ) as d:
            d.state("S1")

        output = render(d.build())
        assert "BackgroundColor red|green" in output

    def test_dict_based_style(self):
        """Dict-based styling for minimal imports."""
        # No need to import StateDiagramStyle, ElementStyle, DiagramArrowStyle
        with state_diagram(
            style={
                "background": "white",
                "font_name": "Arial",
                "state": {
                    "background": "#E3F2FD",
                    "line_color": "#1976D2",
                    "round_corner": 5,
                },
                "arrow": {"line_color": "#757575"},
                "note": {"background": "#FFF9C4"},
            }
        ) as d:
            s1 = d.state("S1")
            s2 = d.state("S2")
            d.arrow(s1, s2)

        output = render(d.build())
        assert "BackgroundColor white" in output
        assert "FontName Arial" in output
        assert "state {" in output
        assert "BackgroundColor #E3F2FD" in output
        assert "LineColor #1976D2" in output
        assert "RoundCorner 5" in output
        assert "arrow {" in output
        assert "LineColor #757575" in output
        assert "note {" in output
        assert "BackgroundColor #FFF9C4" in output

    def test_dict_based_style_gradient_background(self):
        """Dict-based root styles should accept Gradient values."""
        with state_diagram(
            style={
                "background": Gradient(Color.named("red"), Color.named("blue")),
            }
        ) as d:
            d.state("S1")

        output = render(d.build())
        assert "BackgroundColor red|blue" in output


class TestPlantUMLValidation:
    """Integration tests that validate output with PlantUML."""

    def test_basic_diagram(self, validate_plantuml):
        with state_diagram(title="Basic State Diagram") as d:
            a = d.state("A")
            b = d.state("B")
            d.arrow(d.start(), a)
            d.arrow(a, b, label="transition")
            d.arrow(b, d.end())
        assert validate_plantuml(render(d.build()), "basic")

    def test_composite_diagram(self, validate_plantuml):
        with state_diagram(title="Composite State") as d:
            idle = d.state("Idle")
            with d.composite("Active") as active:
                sub1 = active.state("Sub1")
                sub2 = active.state("Sub2")
                active.arrow(active.start(), sub1)
                active.arrow(sub1, sub2)
                active.arrow(sub2, active.end())
            d.arrow(d.start(), idle)
            d.arrow(idle, active, label="activate")
            d.arrow(active, idle, label="done")
        assert validate_plantuml(render(d.build()), "composite")

    def test_concurrent_diagram(self, validate_plantuml):
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
            d.arrow(d.start(), par)
            d.arrow(par, d.end())
        assert validate_plantuml(render(d.build()), "concurrent")

    def test_styled_states(self, validate_plantuml):
        with state_diagram(title="Styled States") as d:
            # Background colors
            pink = d.state("Pink", style=Style(background=Color.named("pink")))
            gradient = d.state(
                "Gradient",
                style=Style(
                    background=Gradient(
                        Color.named("red"), Color.named("yellow")
                    )
                ),
            )

            # Line styles
            dashed = d.state(
                "DashedBorder",
                style=Style(
                    line=LineStyle(pattern="dashed", color=Color.named("blue"))
                ),
            )

            # Text color
            colored_text = d.state(
                "ColoredText", style=Style(text_color=Color.named("green"))
            )

            # Stereotype
            service = d.state(
                "Service", style=Style(stereotype=Stereotype("service"))
            )

            # With spot
            critical = d.state(
                "Critical",
                style=Style(
                    stereotype=Stereotype(
                        "important", spot=Spot("!", Color.named("red"))
                    )
                ),
            )

            d.arrow(d.start(), pink)
            d.arrow(pink, gradient)
            d.arrow(gradient, dashed)
            d.arrow(dashed, colored_text)
            d.arrow(colored_text, service)
            d.arrow(service, critical)
            d.arrow(critical, d.end())

        assert validate_plantuml(render(d.build()), "styled_states")

    def test_pseudo_states(self, validate_plantuml):
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

        assert validate_plantuml(render(d.build()), "pseudo_states")

    def test_styled_composite(self, validate_plantuml):
        with state_diagram(title="Styled Composite") as d:
            with d.composite(
                "StyledComposite",
                style=Style(
                    background=Color.named("lightyellow"),
                    stereotype=Stereotype("subsystem"),
                ),
            ) as comp:
                inner = comp.state(
                    "Inner", style=Style(background=Color.named("lightblue"))
                )
                comp.arrow(comp.start(), inner)
                comp.arrow(inner, comp.end())

            d.arrow(d.start(), comp)
            d.arrow(comp, d.end())

        assert validate_plantuml(render(d.build()), "styled_composite")

    def test_styled_arrows(self, validate_plantuml):
        with state_diagram(title="Styled Arrows") as d:
            s1 = d.state("S1")
            s2 = d.state("S2")
            s3 = d.state("S3")
            s4 = d.state("S4")
            s5 = d.state("S5")

            d.arrow(d.start(), s1)
            d.arrow(
                s1,
                s2,
                label="dashed red",
                style=LineStyle(pattern="dashed", color=Color.named("red")),
            )
            d.arrow(
                s2,
                s3,
                label="dotted blue",
                style=LineStyle(pattern="dotted", color=Color.named("blue")),
            )
            d.arrow(s3, s4, label="thick", style=LineStyle(thickness=3))
            d.arrow(
                s4,
                s5,
                label="bold green",
                style=LineStyle(bold=True, color=Color.named("green")),
            )
            d.arrow(s5, d.end())

        assert validate_plantuml(render(d.build()), "styled_arrows")

    def test_full_featured(self, validate_plantuml):
        """Comprehensive test with all features."""
        with state_diagram(
            title="Full Featured State Diagram", hide_empty_description=True
        ) as d:
            idle = d.state("Idle", description="Waiting for input")

            with d.composite(
                "Processing",
                alias="proc",
                style=Style(background=Color.named("lightyellow")),
            ) as proc:
                init = proc.state(
                    "Init", style=Style(background=Color.named("lightgreen"))
                )
                working = proc.state("Working")
                proc.arrow(proc.start(), init)
                proc.arrow(init, working, label="start")
                proc.arrow(working, proc.end(), label="done")

            with d.concurrent(
                "Monitoring", alias="mon", note="Runs in parallel"
            ) as mon:
                with mon.region() as r1:
                    check = r1.state("HealthCheck")
                    r1.arrow(r1.start(), check)
                with mon.region() as r2:
                    log = r2.state("Logging")
                    r2.arrow(r2.start(), log)

            error = d.state(
                "Error", style=Style(background=Color.named("salmon"))
            )
            choice = d.choice(
                "validate"
            )  # No style - PlantUML doesn't render it

            d.arrow(d.start(), idle)
            d.arrow(idle, choice, label="submit")
            d.arrow(choice, proc, guard="valid")
            d.arrow(
                choice,
                error,
                guard="invalid",
                style=LineStyle(color=Color.named("red")),
            )
            d.arrow(proc, mon, label="monitor")
            d.arrow(mon, d.end(), label="complete")
            d.arrow(error, idle, label="retry", direction="up")

        assert validate_plantuml(render(d.build()), "full_featured")


class TestStyleLike:
    """Tests for dict-style styling with StyleLike and LineStyleLike."""

    def test_state_with_style_dict(self):
        """State accepts style as dict."""
        with state_diagram() as d:
            d.state("Error", style={"background": "salmon"})
        output = render(d.build())
        assert "Error #salmon" in output

    def test_state_with_style_dict_hex_color(self):
        """State accepts hex color in style dict."""
        with state_diagram() as d:
            d.state("Custom", style={"background": "#FF5500"})
        output = render(d.build())
        assert "Custom #FF5500" in output

    def test_state_with_style_dict_text_color(self):
        """State accepts text_color in style dict."""
        with state_diagram() as d:
            d.state("Colored", style={"text_color": "blue"})
        output = render(d.build())
        assert "#text:blue" in output

    def test_states_with_style_dict(self):
        """Bulk states() accepts style as dict."""
        with state_diagram() as d:
            a, b, c = d.states("A", "B", "C", style={"background": "lightblue"})
        output = render(d.build())
        assert "A #lightblue" in output
        assert "B #lightblue" in output
        assert "C #lightblue" in output

    def test_arrow_with_style_dict(self):
        """Arrow accepts style as dict."""
        with state_diagram() as d:
            a = d.state("A")
            b = d.state("B")
            d.arrow(a, b, style={"color": "red", "pattern": "dashed"})
        output = render(d.build())
        assert "[#red,dashed]" in output

    def test_arrow_with_style_dict_thickness(self):
        """Arrow accepts thickness in style dict."""
        with state_diagram() as d:
            a = d.state("A")
            b = d.state("B")
            d.arrow(a, b, style={"thickness": 3})
        output = render(d.build())
        assert "[thickness=3]" in output

    def test_arrow_with_style_dict_bold(self):
        """Arrow accepts bold in style dict."""
        with state_diagram() as d:
            a = d.state("A")
            b = d.state("B")
            d.arrow(a, b, style={"bold": True, "color": "green"})
        output = render(d.build())
        assert "[#green,bold]" in output

    def test_composite_with_style_dict(self):
        """Composite accepts style as dict."""
        with state_diagram() as d:
            with d.composite(
                "Container", style={"background": "lightyellow"}
            ) as c:
                c.state("Inner")
        output = render(d.build())
        assert "Container #lightyellow" in output

    def test_concurrent_with_style_dict(self):
        """Concurrent accepts style as dict."""
        with state_diagram() as d:
            with d.concurrent(
                "Parallel", style={"background": "lightgreen"}
            ) as p:
                with p.region() as r:
                    r.state("A")
        output = render(d.build())
        assert "Parallel #lightgreen" in output

    def test_style_dict_coexists_with_style_object(self):
        """Style objects and dicts can be used together in same diagram."""
        with state_diagram() as d:
            # Style object
            a = d.state("A", style=Style(background=Color.named("pink")))
            # Style dict
            b = d.state("B", style={"background": "lightblue"})
            d.arrow(a, b)
        output = render(d.build())
        assert "A #pink" in output
        assert "B #lightblue" in output

    def test_style_dict_validation(self, validate_plantuml):
        """Style dicts produce valid PlantUML."""
        with state_diagram(title="Dict Styles") as d:
            a = d.state(
                "Error", style={"background": "#FFCCCC", "text_color": "red"}
            )
            b = d.state("Success", style={"background": "#CCFFCC"})
            d.arrow(a, b, style={"color": "green", "pattern": "dashed"})

        assert validate_plantuml(render(d.build()), "dict_styles")


class TestFlow:
    """Tests for flow() method - interleaved states and labels."""

    def test_flow_basic_with_labels(self):
        """flow() creates transitions with interleaved labels."""
        with state_diagram() as d:
            a, b, c = d.states("A", "B", "C")
            d.flow(a, "go", b, "stop", c)
        output = render(d.build())
        assert "A --> B : go" in output
        assert "B --> C : stop" in output

    def test_flow_without_labels(self):
        """flow() works without labels (like arrow)."""
        with state_diagram() as d:
            a, b, c = d.states("A", "B", "C")
            d.flow(a, b, c)
        output = render(d.build())
        assert "A --> B" in output
        assert "B --> C" in output

    def test_flow_mixed_labeled_unlabeled(self):
        """flow() handles mix of labeled and unlabeled transitions."""
        with state_diagram() as d:
            a, b, c, e = d.states("A", "B", "C", "E")
            d.flow(a, "go", b, c, "end", e)
        output = render(d.build())
        assert "A --> B : go" in output
        assert "B --> C" in output
        assert "C --> E : end" in output

    def test_flow_with_style(self):
        """flow() accepts style dict."""
        with state_diagram() as d:
            a, b, c = d.states("A", "B", "C")
            d.flow(a, "go", b, "stop", c, style={"color": "red"})
        output = render(d.build())
        assert "[#red]" in output

    def test_flow_with_direction(self):
        """flow() accepts direction hint."""
        with state_diagram() as d:
            a, b = d.states("A", "B")
            d.flow(a, "up", b, direction="up")
        output = render(d.build())
        assert "-u->" in output

    def test_flow_returns_transitions(self):
        """flow() returns list of Transition objects."""
        with state_diagram() as d:
            a, b, c = d.states("A", "B", "C")
            result = d.flow(a, "x", b, "y", c)
        assert len(result) == 2
        assert isinstance(result[0].label, Label)
        assert isinstance(result[1].label, Label)
        assert result[0].label.text == "x"
        assert result[1].label.text == "y"

    def test_flow_with_pseudo_states(self):
        """flow() works with start/end pseudo-states."""
        with state_diagram() as d:
            a, b = d.states("A", "B")
            d.flow(d.start(), a, "go", b, d.end())
        output = render(d.build())
        assert "[*] --> A" in output
        assert "A --> B : go" in output
        assert "B --> [*]" in output

    def test_flow_with_composite(self):
        """flow() works with composite state builders."""
        with state_diagram() as d:
            before = d.state("Before")
            with d.composite("Active") as active:
                active.state("Inner")
            after = d.state("After")
            d.flow(before, "enter", active, "exit", after)
        output = render(d.build())
        assert "Before --> Active : enter" in output
        assert "Active --> After : exit" in output

    def test_flow_error_starts_with_label(self):
        """flow() raises error if starts with a label."""
        import pytest

        with state_diagram() as d:
            a = d.state("A")
            with pytest.raises(ValueError, match="must start with a state"):
                d.flow("label", a)

    def test_flow_error_ends_with_label(self):
        """flow() raises error if ends with a label."""
        import pytest

        with state_diagram() as d:
            a = d.state("A")
            with pytest.raises(ValueError, match="cannot end with a label"):
                d.flow(a, "label")

    def test_flow_error_consecutive_labels(self):
        """flow() raises error for consecutive labels."""
        import pytest

        with state_diagram() as d:
            a, b = d.states("A", "B")
            with pytest.raises(
                ValueError, match="cannot have consecutive labels"
            ):
                d.flow(a, "first", "second", b)

    def test_flow_error_single_state(self):
        """flow() raises error with only one state."""
        import pytest

        with state_diagram() as d:
            a = d.state("A")
            with pytest.raises(ValueError, match="requires at least 2 states"):
                d.flow(a)

    def test_flow_error_empty(self):
        """flow() raises error when empty."""
        import pytest

        with state_diagram() as d:
            with pytest.raises(ValueError, match="requires at least 2 states"):
                d.flow()

    def test_flow_validation(self, validate_plantuml):
        """flow() produces valid PlantUML."""
        with state_diagram(title="Flow Example") as d:
            idle, loading, ready, error = d.states(
                "Idle", "Loading", "Ready", "Error"
            )
            d.flow(d.start(), idle, "fetch", loading, "success", ready, d.end())
            d.arrow(loading, error, label="failure")
            d.arrow(error, idle, label="retry")
        assert validate_plantuml(render(d.build()), "flow_example")


class TestEnumLiteralSync:
    """Test to verify PseudoStateKindStr Literal matches PseudoStateKind enum.

    PseudoStateKind is the only remaining enum. We keep it for internal use
    since users don't construct PseudoState directly - they use builder methods.
    """

    def test_pseudo_state_kind_literal_matches_enum(self):
        """PseudoStateKindStr Literal matches PseudoStateKind enum values."""
        from typing import get_args

        from plantuml_compose.primitives.state import (
            PseudoStateKind,
            PseudoStateKindStr,
        )

        literal_values = set(get_args(PseudoStateKindStr))
        enum_values = {e.value for e in PseudoStateKind}
        assert literal_values == enum_values, (
            f"Mismatch: Literal={literal_values}, Enum={enum_values}"
        )


class TestDirectionLike:
    """Tests for string direction values."""

    def test_arrow_with_direction_string(self):
        """arrow() accepts direction as string."""
        with state_diagram() as d:
            a, b = d.states("A", "B")
            d.arrow(a, b, direction="up")
        output = render(d.build())
        assert "-u->" in output

    def test_flow_with_direction_string(self):
        """flow() accepts direction as string."""
        with state_diagram() as d:
            a, b = d.states("A", "B")
            d.flow(a, "go", b, direction="down")
        output = render(d.build())
        assert "-d->" in output


class TestLinePatternLike:
    """Tests for string line pattern values."""

    def test_arrow_style_dict_with_pattern_string(self):
        """Arrow style dict accepts pattern as string."""
        with state_diagram() as d:
            a, b = d.states("A", "B")
            d.arrow(a, b, style={"pattern": "dashed", "color": "red"})
        output = render(d.build())
        assert "[#red,dashed]" in output

    def test_arrow_style_dict_with_pattern_dotted(self):
        """Arrow style dict accepts 'dotted' pattern string."""
        with state_diagram() as d:
            a, b = d.states("A", "B")
            d.arrow(a, b, style={"pattern": "dotted"})
        output = render(d.build())
        assert "[dotted]" in output


class TestNotePositionLike:
    """Tests for string note position values."""

    def test_state_with_note_position_string(self):
        """state() accepts note_position as string."""
        with state_diagram() as d:
            d.state("A", note="My note", note_position="left")
        output = render(d.build())
        assert "note left of A" in output

    def test_note_with_position_string(self):
        """note() accepts position as string."""
        with state_diagram() as d:
            d.note("Floating note", position="top")
        # Note: floating notes render differently, just verify no crash
        output = render(d.build())
        assert "note" in output

    def test_composite_with_note_position_string(self):
        """composite() accepts note_position as string."""
        with state_diagram() as d:
            with d.composite(
                "Active", note="Composite note", note_position="left"
            ) as c:
                c.state("Inner")
        output = render(d.build())
        assert "note left of Active" in output

    def test_state_note_invalid_position_raises(self):
        """Anchored notes with invalid positions raise ValueError."""
        with state_diagram() as d:
            d.state("A", note="My note", note_position="over")
        with pytest.raises(ValueError, match="cannot be anchored"):
            render(d.build())

    def test_state_note_valid_positions(self):
        """Anchored notes work with left/right/top/bottom."""
        for position in ("left", "right", "top", "bottom"):
            with state_diagram() as d:
                d.state("A", note="My note", note_position=position)
            output = render(d.build())
            assert f"note {position} of A" in output


class TestRegionSeparator:
    """Tests for region separator values."""

    def test_concurrent_with_vertical_separator(self):
        """concurrent() accepts 'vertical' separator (side-by-side regions)."""
        with state_diagram() as d:
            with d.concurrent("Parallel", separator="vertical") as p:
                with p.region() as r1:
                    r1.state("A")
                with p.region() as r2:
                    r2.state("B")
        output = render(d.build())
        assert "||" in output  # vertical renders as ||

    def test_concurrent_with_horizontal_separator(self):
        """concurrent() accepts 'horizontal' separator (stacked regions)."""
        with state_diagram() as d:
            with d.concurrent("Parallel", separator="horizontal") as p:
                with p.region() as r1:
                    r1.state("A")
                with p.region() as r2:
                    r2.state("B")
        output = render(d.build())
        assert "--" in output  # horizontal renders as --


class TestEscapingInSVG:
    """Tests that verify special characters render correctly in SVG output.

    These tests generate actual SVG via PlantUML and verify the text content
    appears correctly, proving our escaping works end-to-end.
    """

    def test_state_name_with_spaces(self, render_and_parse_svg):
        """State names with spaces render correctly."""
        with state_diagram() as d:
            d.state("My State")
        svg = render_and_parse_svg(render(d.build()))
        assert "My State" in svg

    @pytest.mark.skip(reason="PlantUML limitation: escaped quotes in state names rejected")
    def test_state_name_with_quotes(self, render_and_parse_svg):
        """State names with quotes render correctly.

        KNOWN LIMITATION: PlantUML rejects state names containing escaped quotes.
        Input: state "Say \\"Hello\\"" as Say_Hello
        Error: PlantUML syntax error

        Workaround: Use an alias to avoid quotes in the display name, or
        use single quotes/apostrophes in the name (though these are also
        sanitized from the alias).
        """
        with state_diagram() as d:
            d.state('Say "Hello"')
        svg = render_and_parse_svg(render(d.build()))
        # SVG escapes quotes as &quot;
        assert "Say" in svg and "Hello" in svg

    def test_title_with_quotes(self, render_and_parse_svg):
        """Titles with quotes render correctly."""
        with state_diagram(title='The "Big" Test') as d:
            d.state("S")
        svg = render_and_parse_svg(render(d.build()))
        assert "Big" in svg and "Test" in svg

    def test_multiline_title_renders(self, render_and_parse_svg):
        """Multi-line titles render both lines."""
        with state_diagram(title="First Line\nSecond Line") as d:
            d.state("S")
        svg = render_and_parse_svg(render(d.build()))
        assert "First Line" in svg
        assert "Second Line" in svg

    def test_transition_label_with_special_chars(self, render_and_parse_svg):
        """Transition labels with special characters render correctly."""
        with state_diagram() as d:
            a = d.state("A")
            b = d.state("B")
            d.arrow(a, b, label="x > 0 && y < 10")
        svg = render_and_parse_svg(render(d.build()))
        # SVG escapes < and > as &lt; and &gt;
        assert "x" in svg and "0" in svg and "y" in svg

    def test_note_with_special_chars(self, render_and_parse_svg):
        """Notes with special characters render correctly."""
        with state_diagram() as d:
            d.state("S", note="Check: x > 0", note_position="right")
        svg = render_and_parse_svg(render(d.build()))
        assert "Check" in svg

    def test_unicode_state_names(self, render_and_parse_svg):
        """Unicode characters in state names render correctly."""
        with state_diagram() as d:
            d.state("État")  # French
            d.state("状态")  # Chinese
        svg = render_and_parse_svg(render(d.build()))
        # SVG may use HTML entities for unicode: É becomes &#201;
        # Check that the states are rendered (either as unicode or entities)
        assert "tat" in svg  # At minimum the ASCII part should appear
        # Both states should have elements in the SVG
        assert svg.count("<rect") >= 2  # Two state boxes rendered

    def test_composite_name_with_spaces(self, render_and_parse_svg):
        """Composite state names with spaces render correctly."""
        with state_diagram() as d:
            with d.composite("User Authentication") as comp:
                comp.state("Login")
            d.arrow(d.start(), comp)
        svg = render_and_parse_svg(render(d.build()))
        assert "User Authentication" in svg
        assert "Login" in svg

    def test_choice_name_with_spaces(self, render_and_parse_svg):
        """Choice pseudo-state names with spaces create valid SVG elements.

        Note: Choice diamonds don't display text labels in PlantUML - they're
        rendered as diamond shapes. We verify the element is created with the
        sanitized name as its identifier.
        """
        with state_diagram() as d:
            s = d.state("Start")
            c = d.choice("Is Valid")
            d.arrow(s, c)
        svg = render_and_parse_svg(render(d.build()))
        # Choice diamonds are polygons, not text - check the element exists
        assert "polygon" in svg  # Choice is rendered as diamond polygon
        assert "Is_Valid" in svg  # Sanitized name appears in element ID

    def test_description_with_special_chars(self, render_and_parse_svg):
        """State descriptions with special characters render correctly."""
        with state_diagram() as d:
            d.state("Waiting", description="Count < 10")
        svg = render_and_parse_svg(render(d.build()))
        assert "Waiting" in svg
        assert "Count" in svg

    def test_guard_condition_renders(self, render_and_parse_svg):
        """Guard conditions with brackets render correctly."""
        with state_diagram() as d:
            a = d.state("A")
            b = d.state("B")
            d.arrow(a, b, guard="x > 0")
        svg = render_and_parse_svg(render(d.build()))
        # Guard should appear in brackets in SVG
        assert "x" in svg

    def test_effect_renders(self, render_and_parse_svg):
        """Transition effects render correctly."""
        with state_diagram() as d:
            a = d.state("A")
            b = d.state("B")
            d.arrow(a, b, effect="doAction()")
        svg = render_and_parse_svg(render(d.build()))
        assert "doAction" in svg

    def test_concurrent_region_names(self, render_and_parse_svg):
        """Concurrent state with spaces in name renders correctly."""
        with state_diagram() as d:
            with d.concurrent("Parallel Tasks") as p:
                with p.region() as r:
                    r.state("Task A")
        svg = render_and_parse_svg(render(d.build()))
        assert "Parallel Tasks" in svg
        assert "Task A" in svg

    def test_multiline_note_renders(self, render_and_parse_svg):
        """Multi-line notes render all lines."""
        with state_diagram() as d:
            d.state("S", note="Line 1\nLine 2", note_position="right")
        svg = render_and_parse_svg(render(d.build()))
        assert "Line 1" in svg
        assert "Line 2" in svg

    def test_flow_labels_render(self, render_and_parse_svg):
        """Labels in flow() render correctly."""
        with state_diagram() as d:
            a, b, c = d.states("A", "B", "C")
            d.flow(a, "first step", b, "second step", c)
        svg = render_and_parse_svg(render(d.build()))
        assert "first step" in svg
        assert "second step" in svg

    def test_ampersand_in_label(self, render_and_parse_svg):
        """Ampersand in labels renders correctly."""
        with state_diagram() as d:
            a = d.state("A")
            b = d.state("B")
            d.arrow(a, b, label="Save & Exit")
        svg = render_and_parse_svg(render(d.build()))
        # SVG escapes & as &amp;
        assert "Save" in svg and "Exit" in svg

    def test_apostrophe_in_names(self, render_and_parse_svg):
        """Apostrophes in names are sanitized from alias and name renders."""
        with state_diagram() as d:
            d.state("It's Working")
        svg = render_and_parse_svg(render(d.build()))
        # The state should render - apostrophe is sanitized from the alias
        # Name displays as "It's Working", alias is "Its_Working"
        assert "Working" in svg
