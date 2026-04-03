"""Tests for the activity diagram composer."""

import subprocess

import pytest

from plantuml_compose.composers.activity import activity_diagram, ActivityComposer
from plantuml_compose.primitives.activity import (
    Action,
    ActivityDiagram,
    ActivityNote,
    Arrow,
    Break,
    Connector,
    Detach,
    End,
    Fork,
    Goto,
    Group,
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
from plantuml_compose.primitives.activity import GotoLabel as ActivityLabel
from plantuml_compose.primitives.common import Label
from plantuml_compose.renderers import render


class TestActivityComposerBasic:

    def test_factory_returns_composer(self):
        d = activity_diagram()
        assert isinstance(d, ActivityComposer)

    def test_empty_diagram(self):
        d = activity_diagram()
        result = d.build()
        assert isinstance(result, ActivityDiagram)
        assert result.elements == ()

    def test_start_stop_flow(self):
        d = activity_diagram()
        d.start()
        d.action("Do something")
        d.stop()
        result = d.build()
        assert len(result.elements) == 3
        assert isinstance(result.elements[0], Start)
        assert isinstance(result.elements[1], Action)
        assert isinstance(result.elements[2], Stop)

    def test_action_label(self):
        d = activity_diagram()
        d.action("Process data")
        result = d.build()
        action = result.elements[0]
        assert isinstance(action, Action)
        assert action.label.text == "Process data"

    def test_action_empty_label_raises(self):
        d = activity_diagram()
        with pytest.raises(ValueError, match="empty"):
            d.action("")

    def test_end_node(self):
        d = activity_diagram()
        d.end()
        result = d.build()
        assert isinstance(result.elements[0], End)

    def test_title(self):
        d = activity_diagram(title="My Workflow")
        result = d.build()
        assert result.title == "My Workflow"

    def test_mainframe(self):
        d = activity_diagram(mainframe="Workflow Frame")
        result = d.build()
        assert result.mainframe == "Workflow Frame"

    def test_caption(self):
        d = activity_diagram(caption="Figure 1")
        result = d.build()
        assert result.caption == "Figure 1"

    def test_header_string(self):
        d = activity_diagram(header="Page Header")
        result = d.build()
        assert result.header.content == "Page Header"

    def test_footer_string(self):
        d = activity_diagram(footer="Page Footer")
        result = d.build()
        assert result.footer.content == "Page Footer"

    def test_legend_string(self):
        d = activity_diagram(legend="A legend")
        result = d.build()
        assert result.legend.content == "A legend"

    def test_scale_float(self):
        d = activity_diagram(scale=1.5)
        result = d.build()
        assert result.scale.factor == 1.5

    def test_theme(self):
        d = activity_diagram(theme="cerulean")
        result = d.build()
        assert result.theme == "cerulean"

    def test_vertical_if(self):
        d = activity_diagram(vertical_if=True)
        result = d.build()
        assert result.vertical_if is True


class TestActivityActionShapes:

    @pytest.mark.parametrize("shape", [
        "default", "start_end", "receive", "send", "slant", "document", "database",
    ])
    def test_action_shape(self, shape):
        d = activity_diagram()
        d.action("Shaped action", shape=shape)
        result = d.build()
        assert result.elements[0].shape == shape

    def test_action_style_background(self):
        d = activity_diagram()
        d.action("Colored", style={"background": "#FF0000"})
        result = d.build()
        action = result.elements[0]
        assert action.style is not None
        assert action.style.background.value == "#FF0000"


class TestActivityArrows:

    def test_arrow_no_label(self):
        d = activity_diagram()
        d.action("A")
        d.arrow()
        d.action("B")
        result = d.build()
        assert isinstance(result.elements[1], Arrow)
        assert result.elements[1].label is None

    def test_arrow_with_label(self):
        d = activity_diagram()
        d.arrow("next")
        result = d.build()
        assert result.elements[0].label.text == "next"

    def test_arrow_dashed(self):
        d = activity_diagram()
        d.arrow(pattern="dashed")
        result = d.build()
        assert result.elements[0].pattern == "dashed"

    def test_arrow_dotted(self):
        d = activity_diagram()
        d.arrow(pattern="dotted")
        result = d.build()
        assert result.elements[0].pattern == "dotted"

    def test_arrow_hidden(self):
        d = activity_diagram()
        d.arrow(pattern="hidden")
        result = d.build()
        assert result.elements[0].pattern == "hidden"

    def test_arrow_style_color(self):
        d = activity_diagram()
        d.arrow(style={"color": "red"})
        result = d.build()
        assert result.elements[0].line_style is not None
        assert result.elements[0].line_style.color is not None


class TestActivityIfElse:

    def test_if_then(self):
        d = activity_diagram()
        with d.if_("Valid?", then_label="yes") as branch:
            branch.action("Process")
        result = d.build()
        if_stmt = result.elements[0]
        assert isinstance(if_stmt, If)
        assert if_stmt.condition == "Valid?"
        assert if_stmt.then_label == "yes"
        assert len(if_stmt.then_elements) == 1

    def test_if_else(self):
        d = activity_diagram()
        with d.if_("Valid?", then_label="yes") as branch:
            branch.action("Process")
            with branch.else_("no") as else_block:
                else_block.action("Reject")
        result = d.build()
        if_stmt = result.elements[0]
        assert if_stmt.else_label == "no"
        assert len(if_stmt.else_elements) == 1

    def test_if_elseif_else(self):
        d = activity_diagram()
        with d.if_("Score >= 90?", then_label="A") as branch:
            branch.action("Excellent")
            with branch.elseif("Score >= 80?", then_label="B") as elif_branch:
                elif_branch.action("Good")
            with branch.else_("C") as else_block:
                else_block.action("Average")
        result = d.build()
        if_stmt = result.elements[0]
        assert len(if_stmt.elseif_branches) == 1
        assert if_stmt.elseif_branches[0].condition == "Score >= 80?"
        assert if_stmt.elseif_branches[0].then_label == "B"
        assert len(if_stmt.else_elements) == 1

    def test_elseif_after_else_raises(self):
        d = activity_diagram()
        with d.if_("x?") as branch:
            with branch.else_():
                pass
            with pytest.raises(ValueError, match="elseif.*cannot.*after.*else"):
                with branch.elseif("y?"):
                    pass

    def test_nested_if(self):
        d = activity_diagram()
        with d.if_("Outer?") as outer:
            with outer.if_("Inner?") as inner:
                inner.action("Deep action")
        result = d.build()
        outer_if = result.elements[0]
        assert isinstance(outer_if, If)
        inner_if = outer_if.then_elements[0]
        assert isinstance(inner_if, If)
        assert inner_if.condition == "Inner?"

    def test_end_in_if(self):
        """end() is valid inside if branches."""
        d = activity_diagram()
        with d.if_("Fatal?") as branch:
            branch.end()
            with branch.else_() as else_block:
                else_block.action("Continue")
        result = d.build()
        if_stmt = result.elements[0]
        assert isinstance(if_stmt.then_elements[0], End)


class TestActivitySwitch:

    def test_switch_case(self):
        d = activity_diagram()
        with d.switch("Type?") as sw:
            with sw.case("A") as case_a:
                case_a.action("Handle A")
            with sw.case("B") as case_b:
                case_b.action("Handle B")
        result = d.build()
        switch = result.elements[0]
        assert isinstance(switch, Switch)
        assert switch.condition == "Type?"
        assert len(switch.cases) == 2
        assert switch.cases[0].label == "A"
        assert switch.cases[1].label == "B"

    def test_switch_no_cases_raises(self):
        d = activity_diagram()
        with pytest.raises(ValueError, match="at least one case"):
            with d.switch("Type?") as sw:
                pass  # No cases added


class TestActivityWhile:

    def test_while_loop(self):
        d = activity_diagram()
        with d.while_("More items?", is_label="yes", endwhile_label="no") as loop:
            loop.action("Process item")
        result = d.build()
        while_stmt = result.elements[0]
        assert isinstance(while_stmt, While)
        assert while_stmt.condition == "More items?"
        assert while_stmt.is_label == "yes"
        assert while_stmt.endwhile_label == "no"
        assert len(while_stmt.elements) == 1

    def test_while_break(self):
        d = activity_diagram()
        with d.while_("Running?") as loop:
            loop.action("Work")
            with loop.if_("Error?") as check:
                check.break_()
        result = d.build()
        while_stmt = result.elements[0]
        if_stmt = while_stmt.elements[1]
        assert isinstance(if_stmt, If)
        assert isinstance(if_stmt.then_elements[0], Break)

    def test_while_kill(self):
        """kill() is valid inside while loops."""
        d = activity_diagram()
        with d.while_("Running?") as loop:
            loop.action("Work")
            loop.kill()
        result = d.build()
        while_stmt = result.elements[0]
        assert isinstance(while_stmt.elements[1], Kill)

    def test_while_detach(self):
        """detach() is valid inside while loops."""
        d = activity_diagram()
        with d.while_("Running?") as loop:
            loop.detach()
        result = d.build()
        while_stmt = result.elements[0]
        assert isinstance(while_stmt.elements[0], Detach)


class TestActivityRepeat:

    def test_repeat_while(self):
        d = activity_diagram()
        with d.repeat(condition="More?", is_label="yes", not_label="no") as loop:
            loop.action("Process")
        result = d.build()
        repeat = result.elements[0]
        assert isinstance(repeat, Repeat)
        assert repeat.condition == "More?"
        assert repeat.is_label == "yes"
        assert repeat.not_label == "no"
        assert len(repeat.elements) == 1

    def test_repeat_with_backward_action(self):
        d = activity_diagram()
        with d.repeat(condition="Done?", backward_action="Log attempt") as loop:
            loop.action("Try operation")
        result = d.build()
        repeat = result.elements[0]
        assert repeat.backward_action == "Log attempt"

    def test_repeat_with_start_label(self):
        d = activity_diagram()
        with d.repeat(start_label="Begin loop", condition="Continue?") as loop:
            loop.action("Work")
        result = d.build()
        repeat = result.elements[0]
        assert repeat.start_label == "Begin loop"

    def test_repeat_infinite(self):
        """repeat with no condition is infinite."""
        d = activity_diagram()
        with d.repeat() as loop:
            loop.action("Forever")
        result = d.build()
        repeat = result.elements[0]
        assert repeat.condition is None


class TestActivityFork:

    def test_fork_join(self):
        d = activity_diagram()
        with d.fork() as f:
            with f.branch() as b1:
                b1.action("Task 1")
            with f.branch() as b2:
                b2.action("Task 2")
        result = d.build()
        fork = result.elements[0]
        assert isinstance(fork, Fork)
        assert len(fork.branches) == 2
        assert fork.end_style == "fork"

    def test_fork_merge(self):
        d = activity_diagram()
        with d.fork(end_style="merge") as f:
            with f.branch() as b1:
                b1.action("Path 1")
            with f.branch() as b2:
                b2.action("Path 2")
        result = d.build()
        assert result.elements[0].end_style == "merge"

    def test_fork_or(self):
        d = activity_diagram()
        with d.fork(end_style="or") as f:
            with f.branch() as b:
                b.action("Path")
        result = d.build()
        assert result.elements[0].end_style == "or"

    def test_fork_and(self):
        d = activity_diagram()
        with d.fork(end_style="and") as f:
            with f.branch() as b:
                b.action("Path")
        result = d.build()
        assert result.elements[0].end_style == "and"

    def test_fork_invalid_end_style_raises(self):
        d = activity_diagram()
        with pytest.raises(ValueError):
            with d.fork(end_style="invalid") as f:
                pass

    def test_fork_no_branches_raises(self):
        d = activity_diagram()
        with pytest.raises(ValueError, match="at least one branch"):
            with d.fork() as f:
                pass  # No branches

    def test_fork_branch_kill(self):
        """kill() is valid inside fork branches."""
        d = activity_diagram()
        with d.fork() as f:
            with f.branch() as b1:
                b1.action("Error path")
                b1.kill()
            with f.branch() as b2:
                b2.action("Normal path")
        result = d.build()
        fork = result.elements[0]
        assert isinstance(fork.branches[0][-1], Kill)

    def test_fork_branch_detach(self):
        """detach() is valid inside fork branches."""
        d = activity_diagram()
        with d.fork() as f:
            with f.branch() as b:
                b.action("Background")
                b.detach()
        result = d.build()
        fork = result.elements[0]
        assert isinstance(fork.branches[0][-1], Detach)


class TestActivitySplit:

    def test_split(self):
        d = activity_diagram()
        with d.split() as s:
            with s.branch() as b1:
                b1.action("Path 1")
            with s.branch() as b2:
                b2.action("Path 2")
        result = d.build()
        split = result.elements[0]
        assert isinstance(split, Split)
        assert len(split.branches) == 2

    def test_split_no_branches_raises(self):
        d = activity_diagram()
        with pytest.raises(ValueError, match="at least one branch"):
            with d.split() as s:
                pass


class TestActivitySwimlanes:

    def test_swimlane(self):
        d = activity_diagram()
        d.swimlane("Client")
        d.action("Submit order")
        d.swimlane("Server")
        d.action("Validate order")
        result = d.build()
        assert isinstance(result.elements[0], Swimlane)
        assert result.elements[0].name == "Client"
        assert isinstance(result.elements[2], Swimlane)
        assert result.elements[2].name == "Server"

    def test_swimlane_with_color(self):
        d = activity_diagram()
        d.swimlane("Client", color="#LightBlue")
        result = d.build()
        lane = result.elements[0]
        assert lane.color is not None

    def test_swimlane_empty_name_raises(self):
        d = activity_diagram()
        with pytest.raises(ValueError, match="empty"):
            d.swimlane("")


class TestActivityPartitions:

    def test_partition(self):
        d = activity_diagram()
        with d.partition("Validation") as p:
            p.action("Validate input")
        result = d.build()
        part = result.elements[0]
        assert isinstance(part, Partition)
        assert part.name == "Validation"
        assert len(part.elements) == 1

    def test_partition_with_color(self):
        d = activity_diagram()
        with d.partition("Section", color="LightBlue") as p:
            p.action("Task")
        result = d.build()
        assert result.elements[0].color is not None

    def test_partition_empty_name_raises(self):
        d = activity_diagram()
        with pytest.raises(ValueError, match="empty"):
            with d.partition("") as p:
                pass

    def test_partition_kill(self):
        """kill() is valid inside partitions."""
        d = activity_diagram()
        with d.partition("Error handling") as p:
            p.action("Handle error")
            p.kill()
        result = d.build()
        part = result.elements[0]
        assert isinstance(part.elements[-1], Kill)


class TestActivityGroups:

    def test_group(self):
        d = activity_diagram()
        with d.group("Processing") as g:
            g.action("Process")
        result = d.build()
        grp = result.elements[0]
        assert isinstance(grp, Group)
        assert grp.name == "Processing"
        assert len(grp.elements) == 1

    def test_group_empty_name_raises(self):
        d = activity_diagram()
        with pytest.raises(ValueError, match="empty"):
            with d.group("") as g:
                pass

    def test_group_detach(self):
        """detach() is valid inside groups."""
        d = activity_diagram()
        with d.group("Async") as g:
            g.action("Fire and forget")
            g.detach()
        result = d.build()
        grp = result.elements[0]
        assert isinstance(grp.elements[-1], Detach)


class TestActivityNotes:

    def test_note_right(self):
        d = activity_diagram()
        d.action("Process")
        d.note("Check all fields")
        result = d.build()
        note = result.elements[1]
        assert isinstance(note, ActivityNote)
        assert note.position == "right"
        assert note.floating is False

    def test_note_left(self):
        d = activity_diagram()
        d.note("Left note", "left")
        result = d.build()
        assert result.elements[0].position == "left"

    def test_note_floating(self):
        d = activity_diagram()
        d.note("Important!", floating=True)
        result = d.build()
        assert result.elements[0].floating is True

    def test_note_empty_raises(self):
        d = activity_diagram()
        with pytest.raises(ValueError, match="empty"):
            d.note("")


class TestActivityKillDetach:

    def test_kill_top_level(self):
        d = activity_diagram()
        d.start()
        d.action("Error")
        d.kill()
        result = d.build()
        assert isinstance(result.elements[2], Kill)

    def test_detach_top_level(self):
        d = activity_diagram()
        d.start()
        d.action("Background")
        d.detach()
        result = d.build()
        assert isinstance(result.elements[2], Detach)


class TestActivityConnectorsGoto:

    def test_connector(self):
        d = activity_diagram()
        d.connector("A")
        result = d.build()
        assert isinstance(result.elements[0], Connector)
        assert result.elements[0].name == "A"

    def test_goto(self):
        d = activity_diagram()
        d.goto("retry")
        result = d.build()
        assert isinstance(result.elements[0], Goto)
        assert result.elements[0].label == "retry"

    def test_label(self):
        d = activity_diagram()
        d.label("retry_point")
        result = d.build()
        assert isinstance(result.elements[0], ActivityLabel)
        assert result.elements[0].name == "retry_point"


class TestActivityDiagramStyle:

    def test_diagram_style_dict(self):
        d = activity_diagram(
            diagram_style={"background": "#FAFAFA", "font_size": 14}
        )
        result = d.build()
        assert result.diagram_style is not None
        assert result.diagram_style.font_size == 14


class TestActivityRendering:

    def test_render_basic_flow(self):
        d = activity_diagram(title="Basic")
        d.start()
        d.action("Process")
        d.stop()
        result = render(d)
        assert "@startuml" in result
        assert "@enduml" in result
        assert "start" in result
        assert ":Process;" in result
        assert "stop" in result
        assert "title Basic" in result

    def test_render_if_else(self):
        d = activity_diagram()
        with d.if_("Valid?", then_label="yes") as branch:
            branch.action("Accept")
            with branch.else_("no") as else_block:
                else_block.action("Reject")
        result = render(d)
        assert "if (Valid?) then (yes)" in result
        assert "else (no)" in result
        assert "endif" in result

    def test_render_while(self):
        d = activity_diagram()
        with d.while_("More?", is_label="yes", endwhile_label="no") as loop:
            loop.action("Work")
        result = render(d)
        assert "while (More?) is (yes)" in result
        assert "endwhile (no)" in result

    def test_render_repeat(self):
        d = activity_diagram()
        with d.repeat(condition="Again?", is_label="yes", not_label="no", backward_action="Log") as loop:
            loop.action("Try")
        result = render(d)
        assert "repeat" in result
        assert "backward :Log;" in result
        assert "repeat while (Again?) is (yes) not (no)" in result

    def test_render_fork(self):
        d = activity_diagram()
        with d.fork() as f:
            with f.branch() as b1:
                b1.action("Task 1")
            with f.branch() as b2:
                b2.action("Task 2")
        result = render(d)
        assert "fork" in result
        assert "fork again" in result
        assert "end fork" in result

    def test_render_split(self):
        d = activity_diagram()
        with d.split() as s:
            with s.branch() as b1:
                b1.action("Path 1")
            with s.branch() as b2:
                b2.action("Path 2")
        result = render(d)
        assert "split" in result
        assert "split again" in result
        assert "end split" in result

    def test_render_switch(self):
        d = activity_diagram()
        with d.switch("Type?") as sw:
            with sw.case("A") as c:
                c.action("Handle A")
            with sw.case("B") as c:
                c.action("Handle B")
        result = render(d)
        assert "switch (Type?)" in result
        assert "case (A)" in result
        assert "case (B)" in result
        assert "endswitch" in result

    def test_render_swimlane(self):
        d = activity_diagram()
        d.swimlane("Client")
        d.action("Order")
        result = render(d)
        assert "|Client|" in result

    def test_render_partition(self):
        d = activity_diagram()
        with d.partition("Validation") as p:
            p.action("Validate")
        result = render(d)
        assert 'partition "Validation"' in result

    def test_render_group(self):
        d = activity_diagram()
        with d.group("Batch") as g:
            g.action("Process")
        result = render(d)
        assert "group Batch {" in result

    def test_render_note(self):
        d = activity_diagram()
        d.action("Step")
        d.note("Check this")
        result = render(d)
        assert "note right: Check this" in result

    def test_render_floating_note(self):
        d = activity_diagram()
        d.note("Important!", floating=True)
        result = render(d)
        assert "floating note right: Important!" in result

    def test_render_arrow_styled(self):
        d = activity_diagram()
        d.action("A")
        d.arrow("next", pattern="dashed", style={"color": "#FF0000"})
        d.action("B")
        result = render(d)
        # Should contain dashed arrow with color
        assert "dashed" in result
        assert "#FF0000" in result

    def test_render_action_shapes(self):
        d = activity_diagram()
        d.action("Default")
        d.action("Send", shape="send")
        d.action("Receive", shape="receive")
        d.action("DB", shape="database")
        result = render(d)
        assert ":Default;" in result
        assert ":Send>" in result
        assert ":Receive<" in result
        assert ":DB}" in result

    def test_render_action_colored(self):
        d = activity_diagram()
        d.action("Important", style={"background": "#FF0000"})
        result = render(d)
        assert "#FF0000" in result

    def test_render_kill(self):
        d = activity_diagram()
        d.start()
        d.kill()
        result = render(d)
        assert "kill" in result

    def test_render_detach(self):
        d = activity_diagram()
        d.start()
        d.detach()
        result = render(d)
        assert "detach" in result

    def test_render_connector(self):
        d = activity_diagram()
        d.connector("A")
        result = render(d)
        assert "(A)" in result

    def test_render_goto(self):
        d = activity_diagram()
        d.label("retry")
        d.action("Try")
        d.goto("retry")
        result = render(d)
        assert "label retry" in result
        assert "goto retry" in result

    def test_render_break(self):
        d = activity_diagram()
        with d.while_("Running?") as loop:
            loop.break_()
        result = render(d)
        assert "break" in result

    def test_render_via_composer_method(self):
        """d.render() should produce the same output as render(d)."""
        d = activity_diagram(title="Test")
        d.start()
        d.action("Go")
        d.stop()
        assert d.render() == render(d)

    def test_render_vertical_if(self):
        d = activity_diagram(vertical_if=True)
        with d.if_("x?") as branch:
            branch.action("A")
        result = render(d)
        assert "!pragma useVerticalIf on" in result

    def test_render_theme(self):
        d = activity_diagram(theme="cerulean")
        result = render(d)
        assert "!theme cerulean" in result

    def test_render_mainframe(self):
        d = activity_diagram(mainframe="My Frame")
        result = render(d)
        assert "mainframe My Frame" in result


class TestActivityComplex:

    def test_full_workflow(self):
        """End-to-end test: a realistic order processing workflow."""
        d = activity_diagram(title="Order Processing")
        d.start()
        d.action("Receive Order")

        with d.if_("Valid?", then_label="yes") as branch:
            branch.action("Process Payment")
            with branch.if_("Payment OK?") as inner:
                inner.action("Ship Order")
                with inner.else_() as fail:
                    fail.action("Notify Customer")
            with branch.else_("no") as invalid:
                invalid.action("Reject Order")

        d.stop()

        result = render(d)
        assert "@startuml" in result
        assert "@enduml" in result
        assert "title Order Processing" in result

    def test_parallel_with_conditions(self):
        """Fork with conditional logic inside branches."""
        d = activity_diagram()
        d.start()
        with d.fork() as f:
            with f.branch() as b1:
                b1.action("Validate A")
                with b1.if_("A OK?") as check:
                    check.action("Accept A")
                    with check.else_() as fail:
                        fail.action("Reject A")
            with f.branch() as b2:
                b2.action("Validate B")
        d.stop()

        result = render(d)
        assert "fork" in result
        assert "fork again" in result
        assert "end fork" in result

    def test_nested_partition_with_loop(self):
        """Partition containing a while loop."""
        d = activity_diagram()
        with d.partition("Retry Logic") as p:
            with p.while_("Retries < 3") as loop:
                loop.action("Attempt connection")
        result = render(d)
        assert 'partition "Retry Logic"' in result
        assert "while (Retries < 3)" in result


class TestActivityPlantUMLValidation:

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

    def test_plantuml_basic_flow(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = activity_diagram(title="Syntax Check")
        d.start()
        d.action("Step 1")
        d.action("Step 2", shape="send")
        d.arrow("continue", pattern="dashed")
        d.action("Step 3", shape="receive")
        d.stop()

        puml_file = tmp_path / "activity_basic.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_plantuml_branching(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = activity_diagram()
        d.start()

        with d.if_("Condition A?", then_label="yes") as branch:
            branch.action("Do A")
            with branch.elseif("Condition B?", then_label="also yes") as elif_b:
                elif_b.action("Do B")
            with branch.else_("no") as else_block:
                else_block.action("Do default")

        with d.switch("Type") as sw:
            with sw.case("X") as c:
                c.action("Handle X")
            with sw.case("Y") as c:
                c.action("Handle Y")

        d.stop()

        puml_file = tmp_path / "activity_branching.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_plantuml_loops(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = activity_diagram()
        d.start()

        with d.while_("More items?", is_label="yes", endwhile_label="no") as loop:
            loop.action("Process item")

        with d.repeat(condition="Done?", is_label="yes", not_label="no", backward_action="Retry") as loop:
            loop.action("Attempt")

        d.stop()

        puml_file = tmp_path / "activity_loops.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_plantuml_fork_split(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = activity_diagram()
        d.start()

        with d.fork() as f:
            with f.branch() as b1:
                b1.action("Task A")
            with f.branch() as b2:
                b2.action("Task B")
            with f.branch() as b3:
                b3.action("Task C")

        with d.split() as s:
            with s.branch() as b1:
                b1.action("Path 1")
                b1.kill()
            with s.branch() as b2:
                b2.action("Path 2")
                b2.detach()

        d.stop()

        puml_file = tmp_path / "activity_fork_split.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_plantuml_swimlanes(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = activity_diagram()
        d.swimlane("Client")
        d.start()
        d.action("Place Order")
        d.swimlane("Server")
        d.action("Validate")
        d.swimlane("Client")
        d.action("Receive Confirmation")
        d.stop()

        puml_file = tmp_path / "activity_swimlanes.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_plantuml_partition_group(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = activity_diagram()
        d.start()

        with d.partition("Input Phase", color="LightBlue") as p:
            p.action("Read data")
            p.action("Parse data")

        with d.group("Processing") as g:
            g.action("Transform")
            g.action("Validate")

        d.stop()

        puml_file = tmp_path / "activity_partition_group.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_plantuml_notes(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = activity_diagram()
        d.start()
        d.action("Process")
        d.note("Check all fields", "right")
        d.note("Important!", "left", floating=True)
        d.action("Continue")
        d.stop()

        puml_file = tmp_path / "activity_notes.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_plantuml_connectors(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = activity_diagram()
        d.start()
        d.action("Step 1")
        d.connector("A")
        d.action("Step 2")
        d.connector("A")
        d.stop()

        puml_file = tmp_path / "activity_connectors.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"
