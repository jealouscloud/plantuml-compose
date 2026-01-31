"""Tests for activity diagram builder, primitives, and renderer."""

import pytest

from plantuml_compose import render
from plantuml_compose.builders.activity import activity_diagram
from plantuml_compose.primitives.activity import (
    Action,
    ActivityDiagram,
    Arrow,
    Break,
    Connector,
    Detach,
    End,
    Fork,
    If,
    Kill,
    Partition,
    Repeat,
    Split,
    Start,
    Stop,
    Swimlane,
    Switch,
    While,
)
from plantuml_compose.renderers.activity import render_activity_diagram


class TestBasicElements:
    """Tests for basic activity elements."""

    def test_start(self):
        with activity_diagram() as d:
            d.start()

        output = render(d.build())
        assert "start" in output

    def test_stop(self):
        with activity_diagram() as d:
            d.stop()

        output = render(d.build())
        assert "stop" in output

    def test_end(self):
        with activity_diagram() as d:
            d.end()

        output = render(d.build())
        # "end" appears both as command and in @enduml
        assert output.count("end") >= 2

    def test_action(self):
        with activity_diagram() as d:
            d.action("Process Order")

        output = render(d.build())
        assert ":Process Order;" in output

    def test_action_with_style(self):
        with activity_diagram() as d:
            d.action("Important", style={"background": "red"})

        output = render(d.build())
        assert "#red:Important;" in output

    def test_action_with_shape_database(self):
        with activity_diagram() as d:
            d.action("Store Data", shape="database")

        output = render(d.build())
        assert ":Store Data}" in output

    def test_action_with_shape_document(self):
        with activity_diagram() as d:
            d.action("Generate Report", shape="document")

        output = render(d.build())
        assert ":Generate Report]" in output


class TestArrows:
    """Tests for arrows."""

    def test_basic_arrow(self):
        with activity_diagram() as d:
            d.action("A")
            d.arrow()
            d.action("B")

        output = render(d.build())
        assert "->" in output

    def test_arrow_with_label(self):
        with activity_diagram() as d:
            d.action("A")
            d.arrow("next")
            d.action("B")

        output = render(d.build())
        assert "-> next;" in output

    def test_arrow_with_style(self):
        with activity_diagram() as d:
            d.action("A")
            d.arrow(style={"color": "blue"})
            d.action("B")

        output = render(d.build())
        assert "-[#blue]->" in output

    def test_arrow_dashed(self):
        with activity_diagram() as d:
            d.action("A")
            d.arrow(pattern="dashed")
            d.action("B")

        output = render(d.build())
        assert "-[dashed]->" in output

    def test_arrow_bold(self):
        with activity_diagram() as d:
            d.action("A")
            d.arrow(style={"bold": True})
            d.action("B")

        output = render(d.build())
        assert "-[bold]->" in output

    def test_arrow_combined_styling(self):
        with activity_diagram() as d:
            d.action("A")
            d.arrow(style={"color": "red", "bold": True})
            d.action("B")

        output = render(d.build())
        assert "-[#red,bold]->" in output


class TestIf:
    """Tests for if statements."""

    def test_if_basic(self):
        with activity_diagram() as d:
            with d.if_("Condition?") as branch:
                branch.action("Then action")

        output = render(d.build())
        assert "if (Condition?) then" in output
        assert ":Then action;" in output
        assert "endif" in output

    def test_if_with_then_label(self):
        with activity_diagram() as d:
            with d.if_("Valid?", then_label="yes") as branch:
                branch.action("Process")

        output = render(d.build())
        assert "if (Valid?) then (yes)" in output

    def test_if_with_else(self):
        with activity_diagram() as d:
            with d.if_("Valid?", then_label="yes") as branch:
                branch.action("Process")
                with branch.else_("no") as else_block:
                    else_block.action("Reject")

        output = render(d.build())
        assert "if (Valid?) then (yes)" in output
        assert ":Process;" in output
        assert "else (no)" in output
        assert ":Reject;" in output
        assert "endif" in output

    def test_if_with_elseif(self):
        with activity_diagram() as d:
            with d.if_("A?") as branch:
                branch.action("A action")
                with branch.elseif("B?") as elseif:
                    elseif.action("B action")
                with branch.else_() as else_block:
                    else_block.action("Default")

        output = render(d.build())
        assert "if (A?) then" in output
        assert "elseif (B?) then" in output
        assert "else" in output


class TestSwitch:
    """Tests for switch statements."""

    def test_switch_basic(self):
        with activity_diagram() as d:
            with d.switch("Type?") as sw:
                with sw.case("A") as case:
                    case.action("Handle A")
                with sw.case("B") as case:
                    case.action("Handle B")

        output = render(d.build())
        assert "switch (Type?)" in output
        assert "case (A)" in output
        assert "case (B)" in output
        assert "endswitch" in output


class TestWhile:
    """Tests for while loops."""

    def test_while_basic(self):
        with activity_diagram() as d:
            with d.while_("More items?") as loop:
                loop.action("Process item")

        output = render(d.build())
        assert "while (More items?)" in output
        assert ":Process item;" in output
        assert "endwhile" in output

    def test_while_with_labels(self):
        with activity_diagram() as d:
            with d.while_("Continue?", is_label="yes", endwhile_label="no") as loop:
                loop.action("Process")

        output = render(d.build())
        assert "while (Continue?) is (yes)" in output
        assert "endwhile (no)" in output


class TestRepeat:
    """Tests for repeat loops."""

    def test_repeat_basic(self):
        with activity_diagram() as d:
            with d.repeat(condition="More?") as loop:
                loop.action("Process")

        output = render(d.build())
        assert "repeat" in output
        assert ":Process;" in output
        assert "repeat while (More?)" in output

    def test_repeat_with_labels(self):
        with activity_diagram() as d:
            with d.repeat(
                condition="Continue?",
                is_label="yes",
                not_label="no",
            ) as loop:
                loop.action("Process")

        output = render(d.build())
        assert "repeat while (Continue?) is (yes) not (no)" in output


class TestForkSplit:
    """Tests for fork/join and split."""

    def test_fork_basic(self):
        with activity_diagram() as d:
            with d.fork() as f:
                with f.branch() as b1:
                    b1.action("Task 1")
                with f.branch() as b2:
                    b2.action("Task 2")

        output = render(d.build())
        assert "fork" in output
        assert "fork again" in output
        assert ":Task 1;" in output
        assert ":Task 2;" in output
        assert "end fork" in output

    def test_fork_with_merge(self):
        with activity_diagram() as d:
            with d.fork(end_style="merge") as f:
                with f.branch() as b1:
                    b1.action("Task 1")
                with f.branch() as b2:
                    b2.action("Task 2")

        output = render(d.build())
        assert "end merge" in output

    def test_split_basic(self):
        with activity_diagram() as d:
            with d.split() as s:
                with s.branch() as b1:
                    b1.action("Path 1")
                with s.branch() as b2:
                    b2.action("Path 2")

        output = render(d.build())
        assert "split" in output
        assert "split again" in output
        assert "end split" in output


class TestSwimlanes:
    """Tests for swimlanes."""

    def test_swimlane_basic(self):
        with activity_diagram() as d:
            d.swimlane("Sales")
            d.action("Take Order")
            d.swimlane("Warehouse")
            d.action("Ship Order")

        output = render(d.build())
        assert "|Sales|" in output
        assert "|Warehouse|" in output

    def test_swimlane_with_color(self):
        with activity_diagram() as d:
            d.swimlane("Sales", color="LightBlue")
            d.action("Take Order")

        output = render(d.build())
        assert "|#LightBlue|Sales|" in output


class TestPartitionGroup:
    """Tests for partition and group."""

    def test_partition(self):
        with activity_diagram() as d:
            with d.partition("Validation") as p:
                p.action("Validate input")

        output = render(d.build())
        assert 'partition "Validation" {' in output
        assert ":Validate input;" in output
        assert "}" in output

    def test_partition_with_color(self):
        with activity_diagram() as d:
            with d.partition("Validation", color="LightGreen") as p:
                p.action("Validate")

        output = render(d.build())
        assert "#LightGreen" in output

    def test_group(self):
        with activity_diagram() as d:
            with d.group("Processing") as g:
                g.action("Process")

        output = render(d.build())
        assert "group Processing {" in output
        assert "}" in output


class TestControlFlow:
    """Tests for control flow elements."""

    def test_break(self):
        with activity_diagram() as d:
            with d.while_("Continue?") as loop:
                loop.action("Process")
                loop.break_()

        output = render(d.build())
        assert "break" in output

    def test_kill(self):
        with activity_diagram() as d:
            d.action("Error")
            d.kill()

        output = render(d.build())
        assert "kill" in output

    def test_detach(self):
        with activity_diagram() as d:
            d.action("Background task")
            d.detach()

        output = render(d.build())
        assert "detach" in output

    def test_connector(self):
        with activity_diagram() as d:
            d.action("Start")
            d.connector("A")
            d.detach()
            d.connector("A")
            d.action("Continue")

        output = render(d.build())
        assert "(A)" in output


class TestNotes:
    """Tests for notes."""

    def test_note_right(self):
        with activity_diagram() as d:
            d.action("Process")
            d.note("Important step", position="right")

        output = render(d.build())
        assert "note right: Important step" in output

    def test_floating_note(self):
        with activity_diagram() as d:
            d.note("Overview", floating=True)

        output = render(d.build())
        assert "floating note" in output


class TestDiagramOptions:
    """Tests for diagram-level options."""

    def test_title(self):
        with activity_diagram(title="Order Process") as d:
            d.start()
            d.stop()

        output = render(d.build())
        assert "title Order Process" in output

    def test_vertical_if_pragma(self):
        """Test that vertical_if=True adds the pragma."""
        with activity_diagram(vertical_if=True) as d:
            d.start()
            with d.if_("condition") as branch:
                branch.action("then")
                with branch.else_() as else_branch:
                    else_branch.action("else")
            d.stop()

        output = render(d.build())
        assert "!pragma useVerticalIf on" in output

    def test_vertical_if_not_added_by_default(self):
        """Test that vertical_if pragma is not added by default."""
        with activity_diagram() as d:
            d.start()
            with d.if_("condition") as branch:
                branch.action("then")
            d.stop()

        output = render(d.build())
        assert "useVerticalIf" not in output


class TestRenderMethod:
    """Tests for the render() convenience method."""

    def test_render_returns_plantuml_text(self):
        with activity_diagram() as d:
            d.start()
            d.action("Process")
            d.stop()

        output = render(d.build())
        assert output.startswith("@startuml")
        assert output.endswith("@enduml")

    def test_render_equivalent_to_render_build(self):
        with activity_diagram() as d:
            d.start()
            d.action("Process")
            d.stop()

        from plantuml_compose.renderers import render

        assert render(d.build()) == render(d.build())


class TestComplexDiagram:
    """Integration tests with complex diagrams."""

    def test_order_workflow(self):
        with activity_diagram(title="Order Workflow") as d:
            d.start()
            d.action("Receive Order")

            with d.if_("Valid?", then_label="yes") as valid:
                with d.fork() as f:
                    with f.branch() as b1:
                        b1.action("Check Stock")
                    with f.branch() as b2:
                        b2.action("Process Payment")

                valid.action("Ship Order")

                with valid.else_("no") as invalid:
                    invalid.action("Reject Order")

            d.stop()

        output = render(d.build())
        assert "title Order Workflow" in output
        assert "start" in output
        assert ":Receive Order;" in output
        assert "if (Valid?) then (yes)" in output
        assert "fork" in output
        assert ":Check Stock;" in output
        assert ":Process Payment;" in output
        assert ":Ship Order;" in output
        assert "else (no)" in output
        assert ":Reject Order;" in output
        assert "stop" in output


class TestValidation:
    """Tests for input validation."""

    def test_empty_action_label_rejected(self):
        with activity_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                d.action("")

    def test_empty_swimlane_name_rejected(self):
        with activity_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                d.swimlane("")

    def test_empty_note_content_rejected(self):
        with activity_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                d.note("")

    def test_empty_partition_name_rejected(self):
        with activity_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                with d.partition(""):
                    pass

    def test_empty_group_name_rejected(self):
        with activity_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                with d.group(""):
                    pass

    def test_action_style_rejects_text_color(self):
        with activity_diagram() as d:
            with pytest.raises(ValueError, match="only supports 'background' styling"):
                d.action("Test", style={"text_color": "blue"})

    def test_action_style_rejects_line(self):
        with activity_diagram() as d:
            with pytest.raises(ValueError, match="only supports 'background' styling"):
                d.action("Test", style={"line": {"color": "red"}})

    def test_elseif_after_else_rejected(self):
        """elseif() cannot be called after else_() - else must be final branch."""
        with activity_diagram() as d:
            with d.if_("condition") as branch:
                branch.action("then")
                with branch.else_() as else_block:
                    else_block.action("else")
                with pytest.raises(ValueError, match="elseif.*cannot be called after else_"):
                    with branch.elseif("another"):
                        pass


class TestBlockMisuseDetection:
    """Tests for detecting d.action() called inside block contexts."""

    def test_action_inside_if_raises_error(self):
        with activity_diagram() as d:
            d.start()
            with d.if_("condition"):
                with pytest.raises(RuntimeError) as exc_info:
                    d.action("wrong")

        error_text = str(exc_info.value)
        assert "d.action() called inside 'if_' block" in error_text
        assert "if_block.action" in error_text

    def test_action_inside_while_raises_error(self):
        with activity_diagram() as d:
            d.start()
            with d.while_("condition"):
                with pytest.raises(RuntimeError, match="inside 'while_' block"):
                    d.action("wrong")

    def test_action_inside_fork_raises_error(self):
        with activity_diagram() as d:
            d.start()
            with d.fork() as f:
                with f.branch() as b:
                    b.action("valid")
                with pytest.raises(RuntimeError, match="inside 'fork' block"):
                    d.action("wrong")

    def test_correct_usage_in_block_works(self):
        """Verify that using the block's builder works correctly."""
        with activity_diagram() as d:
            d.start()
            with d.if_("Valid?", then_label="yes") as branch:
                branch.action("Process")
            d.stop()

        output = render(d.build())
        assert "if (Valid?) then (yes)" in output
        assert ":Process;" in output

    # Test all protected methods raise errors inside blocks
    def test_start_inside_block_raises_error(self):
        with activity_diagram() as d:
            with d.if_("condition"):
                with pytest.raises(
                    RuntimeError, match="d.start\\(\\) called inside 'if_' block"
                ):
                    d.start()

    def test_stop_inside_block_raises_error(self):
        with activity_diagram() as d:
            with d.if_("condition"):
                with pytest.raises(
                    RuntimeError, match="d.stop\\(\\) called inside 'if_' block"
                ):
                    d.stop()

    def test_end_inside_block_raises_error(self):
        with activity_diagram() as d:
            with d.if_("condition"):
                with pytest.raises(
                    RuntimeError, match="d.end\\(\\) called inside 'if_' block"
                ):
                    d.end()

    def test_arrow_inside_block_raises_error(self):
        with activity_diagram() as d:
            with d.if_("condition"):
                with pytest.raises(
                    RuntimeError, match="d.arrow\\(\\) called inside 'if_' block"
                ):
                    d.arrow("test")

    def test_break_inside_block_raises_error(self):
        with activity_diagram() as d:
            with d.while_("condition"):
                with pytest.raises(
                    RuntimeError, match="d.break_\\(\\) called inside 'while_' block"
                ):
                    d.break_()

    def test_kill_inside_block_raises_error(self):
        with activity_diagram() as d:
            with d.if_("condition"):
                with pytest.raises(
                    RuntimeError, match="d.kill\\(\\) called inside 'if_' block"
                ):
                    d.kill()

    def test_detach_inside_block_raises_error(self):
        with activity_diagram() as d:
            with d.fork() as f:
                with f.branch() as b:
                    b.action("valid")
                with pytest.raises(
                    RuntimeError, match="d.detach\\(\\) called inside 'fork' block"
                ):
                    d.detach()

    def test_connector_inside_block_raises_error(self):
        with activity_diagram() as d:
            with d.if_("condition"):
                with pytest.raises(
                    RuntimeError, match="d.connector\\(\\) called inside 'if_' block"
                ):
                    d.connector("conn")

    def test_goto_inside_block_raises_error(self):
        with activity_diagram() as d:
            with d.if_("condition"):
                with pytest.raises(
                    RuntimeError, match="d.goto\\(\\) called inside 'if_' block"
                ):
                    d.goto("label")

    def test_label_inside_block_raises_error(self):
        with activity_diagram() as d:
            with d.if_("condition"):
                with pytest.raises(
                    RuntimeError, match="d.label\\(\\) called inside 'if_' block"
                ):
                    d.label("test")

    def test_swimlane_inside_block_raises_error(self):
        with activity_diagram() as d:
            with d.if_("condition"):
                with pytest.raises(
                    RuntimeError, match="d.swimlane\\(\\) called inside 'if_' block"
                ):
                    d.swimlane("Lane1")

    def test_note_inside_block_raises_error(self):
        with activity_diagram() as d:
            with d.if_("condition"):
                with pytest.raises(
                    RuntimeError, match="d.note\\(\\) called inside 'if_' block"
                ):
                    d.note("test note")

    def test_partition_block_tracks_context(self):
        """Verify partition is tracked as a block context."""
        with activity_diagram() as d:
            with d.partition("Section"):
                with pytest.raises(
                    RuntimeError, match="d.action\\(\\) called inside 'partition' block"
                ):
                    d.action("wrong")

    def test_group_block_tracks_context(self):
        """Verify group is tracked as a block context."""
        with activity_diagram() as d:
            with d.group("Section"):
                with pytest.raises(
                    RuntimeError, match="d.action\\(\\) called inside 'group' block"
                ):
                    d.action("wrong")

    def test_all_block_types_track_context(self):
        """Verify all block types are tracked."""
        # Block types that don't require children
        simple_block_types = [
            ("if_", lambda d: d.if_("x")),
            ("while_", lambda d: d.while_("x")),
            ("repeat", lambda d: d.repeat()),
            ("partition", lambda d: d.partition("x")),
            ("group", lambda d: d.group("x")),
        ]
        for block_name, block_fn in simple_block_types:
            with activity_diagram() as d:
                with block_fn(d):
                    with pytest.raises(
                        RuntimeError, match=f"inside '{block_name}' block"
                    ):
                        d.action("wrong")

        # fork/split require at least one branch
        for block_name in ["fork", "split"]:
            with activity_diagram() as d:
                block_fn = getattr(d, block_name)
                with block_fn() as f:
                    with f.branch() as b:
                        b.action("valid")
                    with pytest.raises(
                        RuntimeError, match=f"inside '{block_name}' block"
                    ):
                        d.action("wrong")

        # switch requires at least one case
        with activity_diagram() as d:
            with d.switch("x") as sw:
                with sw.case("a") as c:
                    c.action("valid")
                with pytest.raises(RuntimeError, match="inside 'switch' block"):
                    d.action("wrong")


class TestNestedBuilderRestrictions:
    """Test that nested builders don't expose diagram-only methods.

    Methods like swimlane(), start(), stop(), end(), label() are only valid
    at the diagram level, not inside nested blocks. The builder hierarchy
    ensures these methods aren't even available on nested builders.
    """

    def test_branch_builder_has_no_swimlane(self):
        """Branch builders (inside fork/split) shouldn't have swimlane()."""
        with activity_diagram() as d:
            with d.fork() as f:
                with f.branch() as b:
                    assert not hasattr(b, "swimlane") or not callable(
                        getattr(b, "swimlane", None)
                    )
                    b.action("valid")

    def test_if_builder_has_no_swimlane(self):
        """If builders shouldn't have swimlane()."""
        with activity_diagram() as d:
            with d.if_("condition") as branch:
                assert not hasattr(branch, "swimlane")
                branch.action("valid")

    def test_if_builder_has_no_start_stop(self):
        """If builders shouldn't have start(), stop()."""
        with activity_diagram() as d:
            with d.if_("condition") as branch:
                assert not hasattr(branch, "start")
                assert not hasattr(branch, "stop")
                # Note: end() IS allowed inside conditionals (PlantUML supports it)
                assert hasattr(branch, "end")
                branch.action("valid")

    def test_while_builder_has_no_diagram_methods(self):
        """While builders shouldn't have diagram-only methods."""
        with activity_diagram() as d:
            with d.while_("condition") as loop:
                assert not hasattr(loop, "swimlane")
                assert not hasattr(loop, "start")
                assert not hasattr(loop, "stop")
                loop.action("valid")

    def test_else_builder_has_no_diagram_methods(self):
        """Else builders shouldn't have diagram-only methods."""
        with activity_diagram() as d:
            with d.if_("condition") as branch:
                branch.action("yes path")
                with branch.else_() as else_block:
                    assert not hasattr(else_block, "swimlane")
                    assert not hasattr(else_block, "start")
                    else_block.action("no path")

    def test_nested_builders_still_have_valid_methods(self):
        """Nested builders should still have action(), note(), etc."""
        with activity_diagram() as d:
            with d.if_("condition") as branch:
                # These should all be available on nested builders
                assert hasattr(branch, "action")
                assert hasattr(branch, "arrow")
                assert hasattr(branch, "note")
                assert hasattr(branch, "break_")
                assert hasattr(branch, "if_")  # Nesting is valid
                branch.action("test")


class TestDiagramStyle:
    """Tests for CSS-like diagram-wide styling."""

    def test_diagram_style_with_dict(self):
        """Test diagram_style with dict input."""
        with activity_diagram(
            diagram_style={
                "background": "white",
                "font_name": "Arial",
                "activity": {"background": "#E3F2FD", "line_color": "#1976D2"},
                "arrow": {"line_color": "#757575"},
            }
        ) as d:
            d.start()
            d.action("Test Action")
            d.stop()

        output = render(d.build())
        assert "<style>" in output
        assert "</style>" in output
        assert "activityDiagram {" in output
        assert "BackgroundColor white" in output
        assert "FontName Arial" in output
        assert "activity {" in output
        assert "BackgroundColor #E3F2FD" in output
        assert "LineColor #1976D2" in output
        assert "arrow {" in output
        assert "LineColor #757575" in output

    def test_diagram_style_partition_and_diamond(self):
        """Test partition and diamond styling."""
        with activity_diagram(
            diagram_style={
                "partition": {"background": "#EEEEEE"},
                "diamond": {"background": "yellow"},
            }
        ) as d:
            d.start()
            with d.partition("Test") as p:
                with p.if_("Condition?") as branch:
                    branch.action("Yes")
            d.stop()

        output = render(d.build())
        assert "partition {" in output
        assert "diamond {" in output

    def test_diagram_style_empty_produces_no_block(self):
        """Test that empty style doesn't produce style block."""
        from plantuml_compose.primitives import ActivityDiagramStyle

        with activity_diagram(diagram_style=ActivityDiagramStyle()) as d:
            d.start()
            d.stop()

        output = render(d.build())
        assert "<style>" not in output
