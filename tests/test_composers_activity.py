"""Tests for the activity diagram composer (namespace pattern)."""

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
        el = d.elements
        d.add(
            el.start(),
            el.action("Do something"),
            el.stop(),
        )
        result = d.build()
        assert len(result.elements) == 3
        assert isinstance(result.elements[0], Start)
        assert isinstance(result.elements[1], Action)
        assert isinstance(result.elements[2], Stop)

    def test_action_label(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.action("Process data"))
        result = d.build()
        action = result.elements[0]
        assert isinstance(action, Action)
        assert action.label.text == "Process data"

    def test_action_empty_label_raises(self):
        d = activity_diagram()
        el = d.elements
        with pytest.raises(ValueError, match="empty"):
            el.action("")

    def test_end_node(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.end())
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

    def test_elements_namespace_property(self):
        d = activity_diagram()
        el = d.elements
        from plantuml_compose.composers.activity import ActivityElementNamespace
        assert isinstance(el, ActivityElementNamespace)

    def test_add_returns_single(self):
        d = activity_diagram()
        el = d.elements
        item = d.add(el.start())
        assert isinstance(item, type(el.start()))

    def test_add_returns_tuple(self):
        d = activity_diagram()
        el = d.elements
        items = d.add(el.start(), el.stop())
        assert isinstance(items, tuple)
        assert len(items) == 2


class TestActivityActionShapes:

    @pytest.mark.parametrize("shape", [
        "default", "start_end", "receive", "send", "slant", "document", "database",
    ])
    def test_action_shape(self, shape):
        d = activity_diagram()
        el = d.elements
        d.add(el.action("Shaped action", shape=shape))
        result = d.build()
        assert result.elements[0].shape == shape

    def test_action_style_background(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.action("Colored", style={"background": "#FF0000"}))
        result = d.build()
        action = result.elements[0]
        assert action.style is not None
        assert action.style.background.value == "#FF0000"


class TestActivityArrows:

    def test_arrow_no_label(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.action("A"),
            el.arrow(),
            el.action("B"),
        )
        result = d.build()
        assert isinstance(result.elements[1], Arrow)
        assert result.elements[1].label is None

    def test_arrow_with_label(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.arrow("next"))
        result = d.build()
        assert result.elements[0].label.text == "next"

    def test_arrow_dashed(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.arrow(pattern="dashed"))
        result = d.build()
        assert result.elements[0].pattern == "dashed"

    def test_arrow_dotted(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.arrow(pattern="dotted"))
        result = d.build()
        assert result.elements[0].pattern == "dotted"

    def test_arrow_hidden(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.arrow(pattern="hidden"))
        result = d.build()
        assert result.elements[0].pattern == "hidden"

    def test_arrow_style_color(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.arrow(style={"color": "red"}))
        result = d.build()
        assert result.elements[0].line_style is not None
        assert result.elements[0].line_style.color is not None


class TestActivityIfElse:

    def test_if_then(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.if_("Valid?", [
                el.action("Process"),
            ], then_label="yes"),
        )
        result = d.build()
        if_stmt = result.elements[0]
        assert isinstance(if_stmt, If)
        assert if_stmt.condition == "Valid?"
        assert if_stmt.then_label == "yes"
        assert len(if_stmt.then_elements) == 1

    def test_if_else(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.if_("Valid?", [
                el.action("Process"),
            ], "no", [
                el.action("Reject"),
            ], then_label="yes"),
        )
        result = d.build()
        if_stmt = result.elements[0]
        assert if_stmt.else_label == "no"
        assert len(if_stmt.else_elements) == 1

    def test_if_elseif_else(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.if_("Score >= 90?", [
                el.action("Excellent"),
            ], "Score >= 80?", [
                el.action("Good"),
            ], None, [
                el.action("Average"),
            ], then_label="A"),
        )
        result = d.build()
        if_stmt = result.elements[0]
        assert len(if_stmt.elseif_branches) == 1
        assert if_stmt.elseif_branches[0].condition == "Score >= 80?"
        assert len(if_stmt.else_elements) == 1

    def test_nested_if(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.if_("Outer?", [
                el.if_("Inner?", [
                    el.action("Deep action"),
                ]),
            ]),
        )
        result = d.build()
        outer_if = result.elements[0]
        assert isinstance(outer_if, If)
        inner_if = outer_if.then_elements[0]
        assert isinstance(inner_if, If)
        assert inner_if.condition == "Inner?"

    def test_end_in_if(self):
        """end() is valid inside if branches."""
        d = activity_diagram()
        el = d.elements
        d.add(
            el.if_("Fatal?", [
                el.end(),
            ], None, [
                el.action("Continue"),
            ]),
        )
        result = d.build()
        if_stmt = result.elements[0]
        assert isinstance(if_stmt.then_elements[0], End)


class TestActivitySwitch:

    def test_switch_case(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.switch("Type?",
                ("A", [el.action("Handle A")]),
                ("B", [el.action("Handle B")]),
            ),
        )
        result = d.build()
        switch = result.elements[0]
        assert isinstance(switch, Switch)
        assert switch.condition == "Type?"
        assert len(switch.cases) == 2
        assert switch.cases[0].label == "A"
        assert switch.cases[1].label == "B"

    def test_switch_no_cases_raises(self):
        d = activity_diagram()
        el = d.elements
        with pytest.raises(ValueError, match="at least one case"):
            el.switch("Type?")


class TestActivityWhile:

    def test_while_loop(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.while_("More items?", [
                el.action("Process item"),
            ], is_label="yes", endwhile_label="no"),
        )
        result = d.build()
        while_stmt = result.elements[0]
        assert isinstance(while_stmt, While)
        assert while_stmt.condition == "More items?"
        assert while_stmt.is_label == "yes"
        assert while_stmt.endwhile_label == "no"
        assert len(while_stmt.elements) == 1

    def test_while_break(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.while_("Running?", [
                el.action("Work"),
                el.if_("Error?", [
                    el.break_(),
                ]),
            ]),
        )
        result = d.build()
        while_stmt = result.elements[0]
        if_stmt = while_stmt.elements[1]
        assert isinstance(if_stmt, If)
        assert isinstance(if_stmt.then_elements[0], Break)

    def test_while_kill(self):
        """kill() is valid inside while loops."""
        d = activity_diagram()
        el = d.elements
        d.add(
            el.while_("Running?", [
                el.action("Work"),
                el.kill(),
            ]),
        )
        result = d.build()
        while_stmt = result.elements[0]
        assert isinstance(while_stmt.elements[1], Kill)

    def test_while_detach(self):
        """detach() is valid inside while loops."""
        d = activity_diagram()
        el = d.elements
        d.add(
            el.while_("Running?", [
                el.detach(),
            ]),
        )
        result = d.build()
        while_stmt = result.elements[0]
        assert isinstance(while_stmt.elements[0], Detach)


class TestActivityRepeat:

    def test_repeat_while(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.repeat([
                el.action("Process"),
            ], condition="More?", is_label="yes", not_label="no"),
        )
        result = d.build()
        repeat = result.elements[0]
        assert isinstance(repeat, Repeat)
        assert repeat.condition == "More?"
        assert repeat.is_label == "yes"
        assert repeat.not_label == "no"
        assert len(repeat.elements) == 1

    def test_repeat_with_backward_action(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.repeat([
                el.action("Try operation"),
            ], condition="Done?", backward_action="Log attempt"),
        )
        result = d.build()
        repeat = result.elements[0]
        assert repeat.backward_action == "Log attempt"

    def test_repeat_with_start_label(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.repeat([
                el.action("Work"),
            ], start_label="Begin loop", condition="Continue?"),
        )
        result = d.build()
        repeat = result.elements[0]
        assert repeat.start_label == "Begin loop"

    def test_repeat_infinite(self):
        """repeat with no condition is infinite."""
        d = activity_diagram()
        el = d.elements
        d.add(
            el.repeat([
                el.action("Forever"),
            ]),
        )
        result = d.build()
        repeat = result.elements[0]
        assert repeat.condition is None


class TestActivityFork:

    def test_fork_join(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.fork(
                [el.action("Task 1")],
                [el.action("Task 2")],
            ),
        )
        result = d.build()
        fork = result.elements[0]
        assert isinstance(fork, Fork)
        assert len(fork.branches) == 2
        assert fork.end_style == "fork"

    def test_fork_merge(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.fork(
                [el.action("Path 1")],
                [el.action("Path 2")],
                end_style="merge",
            ),
        )
        result = d.build()
        assert result.elements[0].end_style == "merge"

    def test_fork_or(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.fork(
                [el.action("Path")],
                end_style="or",
            ),
        )
        result = d.build()
        assert result.elements[0].end_style == "or"

    def test_fork_and(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.fork(
                [el.action("Path")],
                end_style="and",
            ),
        )
        result = d.build()
        assert result.elements[0].end_style == "and"

    def test_fork_invalid_end_style_raises(self):
        d = activity_diagram()
        el = d.elements
        with pytest.raises(ValueError):
            el.fork([el.action("x")], end_style="invalid")

    def test_fork_no_branches_raises(self):
        d = activity_diagram()
        el = d.elements
        with pytest.raises(ValueError, match="at least one branch"):
            el.fork()

    def test_fork_branch_kill(self):
        """kill() is valid inside fork branches."""
        d = activity_diagram()
        el = d.elements
        d.add(
            el.fork(
                [el.action("Error path"), el.kill()],
                [el.action("Normal path")],
            ),
        )
        result = d.build()
        fork = result.elements[0]
        assert isinstance(fork.branches[0][-1], Kill)

    def test_fork_branch_detach(self):
        """detach() is valid inside fork branches."""
        d = activity_diagram()
        el = d.elements
        d.add(
            el.fork(
                [el.action("Background"), el.detach()],
            ),
        )
        result = d.build()
        fork = result.elements[0]
        assert isinstance(fork.branches[0][-1], Detach)


class TestActivitySplit:

    def test_split(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.split(
                [el.action("Path 1")],
                [el.action("Path 2")],
            ),
        )
        result = d.build()
        split = result.elements[0]
        assert isinstance(split, Split)
        assert len(split.branches) == 2

    def test_split_no_branches_raises(self):
        d = activity_diagram()
        el = d.elements
        with pytest.raises(ValueError, match="at least one branch"):
            el.split()


class TestActivitySwimlanes:

    def test_swimlane(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.swimlane("Client"),
            el.action("Submit order"),
            el.swimlane("Server"),
            el.action("Validate order"),
        )
        result = d.build()
        assert isinstance(result.elements[0], Swimlane)
        assert result.elements[0].name == "Client"
        assert isinstance(result.elements[2], Swimlane)
        assert result.elements[2].name == "Server"

    def test_swimlane_with_color(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.swimlane("Client", color="#LightBlue"))
        result = d.build()
        lane = result.elements[0]
        assert lane.color is not None

    def test_swimlane_empty_name_raises(self):
        d = activity_diagram()
        el = d.elements
        with pytest.raises(ValueError, match="empty"):
            el.swimlane("")


class TestActivityPartitions:

    def test_partition(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.partition("Validation", [
                el.action("Validate input"),
            ]),
        )
        result = d.build()
        part = result.elements[0]
        assert isinstance(part, Partition)
        assert part.name == "Validation"
        assert len(part.elements) == 1

    def test_partition_with_color(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.partition("Section", [
                el.action("Task"),
            ], color="LightBlue"),
        )
        result = d.build()
        assert result.elements[0].color is not None

    def test_partition_empty_name_raises(self):
        d = activity_diagram()
        el = d.elements
        with pytest.raises(ValueError, match="empty"):
            el.partition("", [])

    def test_partition_kill(self):
        """kill() is valid inside partitions."""
        d = activity_diagram()
        el = d.elements
        d.add(
            el.partition("Error handling", [
                el.action("Handle error"),
                el.kill(),
            ]),
        )
        result = d.build()
        part = result.elements[0]
        assert isinstance(part.elements[-1], Kill)


class TestActivityGroups:

    def test_group(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.group("Processing", [
                el.action("Process"),
            ]),
        )
        result = d.build()
        grp = result.elements[0]
        assert isinstance(grp, Group)
        assert grp.name == "Processing"
        assert len(grp.elements) == 1

    def test_group_empty_name_raises(self):
        d = activity_diagram()
        el = d.elements
        with pytest.raises(ValueError, match="empty"):
            el.group("", [])

    def test_group_detach(self):
        """detach() is valid inside groups."""
        d = activity_diagram()
        el = d.elements
        d.add(
            el.group("Async", [
                el.action("Fire and forget"),
                el.detach(),
            ]),
        )
        result = d.build()
        grp = result.elements[0]
        assert isinstance(grp.elements[-1], Detach)


class TestActivityNotes:

    def test_note_right(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.action("Process"),
            el.note("Check all fields"),
        )
        result = d.build()
        note = result.elements[1]
        assert isinstance(note, ActivityNote)
        assert note.position == "right"
        assert note.floating is False

    def test_note_left(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.note("Left note", "left"))
        result = d.build()
        assert result.elements[0].position == "left"

    def test_note_floating(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.note("Important!", floating=True))
        result = d.build()
        assert result.elements[0].floating is True

    def test_note_empty_raises(self):
        d = activity_diagram()
        el = d.elements
        with pytest.raises(ValueError, match="empty"):
            el.note("")


class TestActivityKillDetach:

    def test_kill_top_level(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.start(),
            el.action("Error"),
            el.kill(),
        )
        result = d.build()
        assert isinstance(result.elements[2], Kill)

    def test_detach_top_level(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.start(),
            el.action("Background"),
            el.detach(),
        )
        result = d.build()
        assert isinstance(result.elements[2], Detach)


class TestActivityConnectorsGoto:

    def test_connector(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.connector("A"))
        result = d.build()
        assert isinstance(result.elements[0], Connector)
        assert result.elements[0].name == "A"

    def test_goto(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.goto("retry"))
        result = d.build()
        assert isinstance(result.elements[0], Goto)
        assert result.elements[0].label == "retry"

    def test_label(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.label("retry_point"))
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
        el = d.elements
        d.add(
            el.start(),
            el.action("Process"),
            el.stop(),
        )
        result = render(d)
        assert "@startuml" in result
        assert "@enduml" in result
        assert "start" in result
        assert ":Process;" in result
        assert "stop" in result
        assert "title Basic" in result

    def test_render_if_else(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.if_("Valid?", [
                el.action("Accept"),
            ], "no", [
                el.action("Reject"),
            ], then_label="yes"),
        )
        result = render(d)
        assert "if (Valid?) then (yes)" in result
        assert "else (no)" in result
        assert "endif" in result

    def test_render_while(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.while_("More?", [
                el.action("Work"),
            ], is_label="yes", endwhile_label="no"),
        )
        result = render(d)
        assert "while (More?) is (yes)" in result
        assert "endwhile (no)" in result

    def test_render_repeat(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.repeat([
                el.action("Try"),
            ], condition="Again?", is_label="yes", not_label="no", backward_action="Log"),
        )
        result = render(d)
        assert "repeat" in result
        assert "backward :Log;" in result
        assert "repeat while (Again?) is (yes) not (no)" in result

    def test_render_fork(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.fork(
                [el.action("Task 1")],
                [el.action("Task 2")],
            ),
        )
        result = render(d)
        assert "fork" in result
        assert "fork again" in result
        assert "end fork" in result

    def test_render_split(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.split(
                [el.action("Path 1")],
                [el.action("Path 2")],
            ),
        )
        result = render(d)
        assert "split" in result
        assert "split again" in result
        assert "end split" in result

    def test_render_switch(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.switch("Type?",
                ("A", [el.action("Handle A")]),
                ("B", [el.action("Handle B")]),
            ),
        )
        result = render(d)
        assert "switch (Type?)" in result
        assert "case (A)" in result
        assert "case (B)" in result
        assert "endswitch" in result

    def test_render_swimlane(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.swimlane("Client"),
            el.action("Order"),
        )
        result = render(d)
        assert "|Client|" in result

    def test_render_partition(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.partition("Validation", [
                el.action("Validate"),
            ]),
        )
        result = render(d)
        assert 'partition "Validation"' in result

    def test_render_group(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.group("Batch", [
                el.action("Process"),
            ]),
        )
        result = render(d)
        assert "group Batch {" in result

    def test_render_note(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.action("Step"),
            el.note("Check this"),
        )
        result = render(d)
        assert "note right: Check this" in result

    def test_render_floating_note(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.note("Important!", floating=True))
        result = render(d)
        assert "floating note right: Important!" in result

    def test_render_arrow_styled(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.action("A"),
            el.arrow("next", pattern="dashed", style={"color": "#FF0000"}),
            el.action("B"),
        )
        result = render(d)
        assert "dashed" in result
        assert "#FF0000" in result

    def test_render_action_shapes(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.action("Default"),
            el.action("Send", shape="send"),
            el.action("Receive", shape="receive"),
            el.action("DB", shape="database"),
        )
        result = render(d)
        assert ":Default;" in result
        # SDL shapes use modern stereotype syntax, not deprecated suffixes
        assert ":Send;<<output>>" in result
        assert ":Receive;<<input>>" in result
        assert ":DB;<<continuous>>" in result

    def test_render_action_colored(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.action("Important", style={"background": "#FF0000"}))
        result = render(d)
        assert "#FF0000" in result

    def test_render_kill(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.start(),
            el.kill(),
        )
        result = render(d)
        assert "kill" in result

    def test_render_detach(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.start(),
            el.detach(),
        )
        result = render(d)
        assert "detach" in result

    def test_render_connector(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.connector("A"))
        result = render(d)
        assert "(A)" in result

    def test_render_goto(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.label("retry"),
            el.action("Try"),
            el.goto("retry"),
        )
        result = render(d)
        assert "label retry" in result
        assert "goto retry" in result

    def test_render_break(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.while_("Running?", [
                el.break_(),
            ]),
        )
        result = render(d)
        assert "break" in result

    def test_render_via_composer_method(self):
        """d.render() should produce the same output as render(d)."""
        d = activity_diagram(title="Test")
        el = d.elements
        d.add(
            el.start(),
            el.action("Go"),
            el.stop(),
        )
        assert d.render() == render(d)

    def test_render_vertical_if(self):
        d = activity_diagram(vertical_if=True)
        el = d.elements
        d.add(
            el.if_("x?", [
                el.action("A"),
            ]),
        )
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
        el = d.elements
        d.add(
            el.start(),
            el.action("Receive Order"),
            el.if_("Valid?", [
                el.action("Process Payment"),
                el.if_("Payment OK?", [
                    el.action("Ship Order"),
                ], None, [
                    el.action("Notify Customer"),
                ]),
            ], "no", [
                el.action("Reject Order"),
            ], then_label="yes"),
            el.stop(),
        )
        result = render(d)
        assert "@startuml" in result
        assert "@enduml" in result
        assert "title Order Processing" in result

    def test_parallel_with_conditions(self):
        """Fork with conditional logic inside branches."""
        d = activity_diagram()
        el = d.elements
        d.add(
            el.start(),
            el.fork(
                [
                    el.action("Validate A"),
                    el.if_("A OK?", [
                        el.action("Accept A"),
                    ], None, [
                        el.action("Reject A"),
                    ]),
                ],
                [el.action("Validate B")],
            ),
            el.stop(),
        )
        result = render(d)
        assert "fork" in result
        assert "fork again" in result
        assert "end fork" in result

    def test_nested_partition_with_loop(self):
        """Partition containing a while loop."""
        d = activity_diagram()
        el = d.elements
        d.add(
            el.partition("Retry Logic", [
                el.while_("Retries < 3", [
                    el.action("Attempt connection"),
                ]),
            ]),
        )
        result = render(d)
        assert 'partition "Retry Logic"' in result
        assert "while (Retries < 3)" in result

    def test_complex_pipeline(self):
        """Complex pipeline with swimlanes, forks, and loops."""
        d = activity_diagram(title="Pipeline")
        el = d.elements
        d.add(
            el.start(),
            el.swimlane("Client"),
            el.action("Submit Order"),
            el.swimlane("Server"),
            el.action("Validate"),
            el.if_("Valid?", [
                el.action("Process Payment"),
                el.arrow("next", pattern="dashed"),
                el.action("Ship"),
            ], "no", [
                el.action("Reject"),
                el.kill(),
            ], then_label="yes"),
            el.while_("More items?", [
                el.action("Process item"),
            ], is_label="yes", endwhile_label="no"),
            el.fork(
                [el.action("Send Email")],
                [el.action("Update DB")],
            ),
            el.stop(),
        )
        result = render(d)
        assert "|Client|" in result
        assert "|Server|" in result
        assert "fork" in result


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
        el = d.elements
        d.add(
            el.start(),
            el.action("Step 1"),
            el.action("Step 2", shape="send"),
            el.arrow("continue", pattern="dashed"),
            el.action("Step 3", shape="receive"),
            el.stop(),
        )

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
        el = d.elements
        d.add(
            el.start(),
            el.if_("Condition A?", [
                el.action("Do A"),
            ], "Condition B?", [
                el.action("Do B"),
            ], "no", [
                el.action("Do default"),
            ], then_label="yes"),
            el.switch("Type",
                ("X", [el.action("Handle X")]),
                ("Y", [el.action("Handle Y")]),
            ),
            el.stop(),
        )

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
        el = d.elements
        d.add(
            el.start(),
            el.while_("More items?", [
                el.action("Process item"),
            ], is_label="yes", endwhile_label="no"),
            el.repeat([
                el.action("Attempt"),
            ], condition="Done?", is_label="yes", not_label="no", backward_action="Retry"),
            el.stop(),
        )

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
        el = d.elements
        d.add(
            el.start(),
            el.fork(
                [el.action("Task A")],
                [el.action("Task B")],
                [el.action("Task C")],
            ),
            el.split(
                [el.action("Path 1"), el.kill()],
                [el.action("Path 2"), el.detach()],
            ),
            el.stop(),
        )

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
        el = d.elements
        d.add(
            el.swimlane("Client"),
            el.start(),
            el.action("Place Order"),
            el.swimlane("Server"),
            el.action("Validate"),
            el.swimlane("Client"),
            el.action("Receive Confirmation"),
            el.stop(),
        )

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
        el = d.elements
        d.add(
            el.start(),
            el.partition("Input Phase", [
                el.action("Read data"),
                el.action("Parse data"),
            ], color="LightBlue"),
            el.group("Processing", [
                el.action("Transform"),
                el.action("Validate"),
            ]),
            el.stop(),
        )

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
        el = d.elements
        d.add(
            el.start(),
            el.action("Process"),
            el.note("Check all fields", "right"),
            el.note("Important!", "left", floating=True),
            el.action("Continue"),
            el.stop(),
        )

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
        el = d.elements
        d.add(
            el.start(),
            el.action("Step 1"),
            el.connector("A"),
            el.action("Step 2"),
            el.connector("A"),
            el.stop(),
        )

        puml_file = tmp_path / "activity_connectors.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"


class TestActivitySwimlaneDisplayName:

    def test_swimlane_display_name_primitive(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.swimlane("svc", display_name="Service Layer"))
        result = d.build()
        lane = result.elements[0]
        assert isinstance(lane, Swimlane)
        assert lane.name == "svc"
        assert lane.display_name == "Service Layer"

    def test_swimlane_display_name_renders_alias_syntax(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.swimlane("svc", display_name="Service Layer"),
            el.action("Do work"),
        )
        result = render(d)
        assert "|svc| Service Layer" in result

    def test_swimlane_display_name_with_color(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.swimlane("svc", color="#LightBlue", display_name="Service Layer"),
            el.action("Do work"),
        )
        result = render(d)
        assert "|#LightBlue|svc| Service Layer" in result

    def test_swimlane_no_display_name_unchanged(self):
        """Without display_name, swimlane renders as before."""
        d = activity_diagram()
        el = d.elements
        d.add(el.swimlane("Client"))
        result = render(d)
        assert "|Client|" in result

    def test_swimlane_switch_back_with_alias(self):
        """After defining with display_name, switch back using just name."""
        d = activity_diagram()
        el = d.elements
        d.add(
            el.swimlane("svc", display_name="Service Layer"),
            el.action("First task"),
            el.swimlane("cli", display_name="Client App"),
            el.action("Client task"),
            el.swimlane("svc"),
            el.action("Back to service"),
        )
        result = render(d)
        assert "|svc| Service Layer" in result
        assert "|cli| Client App" in result
        # Second use of svc has no display_name, renders as plain alias
        lines = result.split("\n")
        svc_lines = [l for l in lines if l.strip().startswith("|svc")]
        assert len(svc_lines) == 2
        assert svc_lines[1].strip() == "|svc|"


class TestActivityStereotype:

    def test_action_stereotype_primitive(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.action("Read input", stereotype="input"))
        result = d.build()
        action = result.elements[0]
        assert isinstance(action, Action)
        assert action.stereotype == "input"

    def test_action_stereotype_renders(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.action("Read input", stereotype="input"))
        result = render(d)
        assert ":Read input;<<input>>" in result

    def test_action_no_stereotype_unchanged(self):
        """Without stereotype, action renders as before."""
        d = activity_diagram()
        el = d.elements
        d.add(el.action("Normal"))
        result = render(d)
        assert ":Normal;" in result
        assert "<<" not in result

    def test_action_stereotype_with_shape(self):
        """Stereotype works alongside SDL shapes."""
        d = activity_diagram()
        el = d.elements
        d.add(el.action("Data", shape="database", stereotype="output"))
        result = render(d)
        # shape="database" -> <<continuous>>, stereotype="output" -> <<output>>
        assert ":Data;<<continuous>><<output>>" in result

    def test_action_stereotype_with_style(self):
        """Stereotype works alongside colored actions."""
        d = activity_diagram()
        el = d.elements
        d.add(el.action("Alert", style={"background": "#FF0000"}, stereotype="sendSignal"))
        result = render(d)
        assert "<<sendSignal>>" in result
        assert "#FF0000" in result

    @pytest.mark.parametrize("stereotype", [
        "acceptEvent",
        "timeEvent",
        "sendSignal",
        "object",
        "trigger",
    ])
    def test_uml_stereotypes(self, stereotype):
        """UML-specific stereotypes render correctly."""
        d = activity_diagram()
        el = d.elements
        d.add(el.action("Test action", stereotype=stereotype))
        result = render(d)
        assert f"<<{stereotype}>>" in result

    def test_sdl_stereotypes(self):
        """SDL stereotypes (input, output, start, end) render correctly."""
        d = activity_diagram()
        el = d.elements
        d.add(
            el.action("Read data", stereotype="input"),
            el.action("Write data", stereotype="output"),
        )
        result = render(d)
        assert ":Read data;<<input>>" in result
        assert ":Write data;<<output>>" in result


class TestActivityWhileBackwardAction:

    def test_while_backward_action_primitive(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.while_("More?", [
                el.action("Process"),
            ], backward_action="Log iteration"),
        )
        result = d.build()
        while_stmt = result.elements[0]
        assert isinstance(while_stmt, While)
        assert while_stmt.backward_action == "Log iteration"

    def test_while_backward_action_renders(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.while_("More?", [
                el.action("Process"),
            ], is_label="yes", endwhile_label="no", backward_action="Log iteration"),
        )
        result = render(d)
        assert "backward :Log iteration;" in result
        assert "while (More?) is (yes)" in result
        assert "endwhile (no)" in result

    def test_while_no_backward_action_unchanged(self):
        d = activity_diagram()
        el = d.elements
        d.add(
            el.while_("More?", [
                el.action("Process"),
            ]),
        )
        result = render(d)
        assert "backward" not in result


class TestActivityConnectorColor:

    def test_connector_color_primitive(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.connector("B", color="blue"))
        result = d.build()
        conn = result.elements[0]
        assert isinstance(conn, Connector)
        assert conn.name == "B"
        assert conn.color == "blue"

    def test_connector_color_renders(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.connector("B", color="blue"))
        result = render(d)
        assert "#blue:(B)" in result

    def test_connector_no_color_unchanged(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.connector("A"))
        result = render(d)
        assert "(A)" in result
        assert "#" not in result

    def test_connector_hex_color(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.connector("C", color="#FF0000"))
        result = render(d)
        assert "#FF0000:(C)" in result


class TestActivityPackageRectangleCard:

    def test_package_primitive(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.package("My Package", [el.action("Work")]))
        result = d.build()
        part = result.elements[0]
        assert isinstance(part, Partition)
        assert part.keyword == "package"
        assert part.name == "My Package"

    def test_rectangle_primitive(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.rectangle("My Rectangle", [el.action("Work")]))
        result = d.build()
        part = result.elements[0]
        assert isinstance(part, Partition)
        assert part.keyword == "rectangle"

    def test_card_primitive(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.card("My Card", [el.action("Work")]))
        result = d.build()
        part = result.elements[0]
        assert isinstance(part, Partition)
        assert part.keyword == "card"

    def test_package_renders(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.package("My Package", [el.action("Work")]))
        result = render(d)
        assert 'package "My Package" {' in result

    def test_rectangle_renders(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.rectangle("My Rectangle", [el.action("Work")]))
        result = render(d)
        assert 'rectangle "My Rectangle" {' in result

    def test_card_renders(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.card("My Card", [el.action("Work")]))
        result = render(d)
        assert 'card "My Card" {' in result

    def test_package_with_color(self):
        d = activity_diagram()
        el = d.elements
        d.add(el.package("Pkg", [el.action("Work")], color="LightBlue"))
        result = render(d)
        assert 'package "Pkg"' in result
        assert "LightBlue" in result

    def test_partition_keyword_default(self):
        """Regular partition still renders as partition."""
        d = activity_diagram()
        el = d.elements
        d.add(el.partition("Section", [el.action("Work")]))
        result = render(d)
        assert 'partition "Section" {' in result

    def test_package_empty_name_raises(self):
        d = activity_diagram()
        el = d.elements
        with pytest.raises(ValueError, match="empty"):
            el.package("", [])

    def test_rectangle_empty_name_raises(self):
        d = activity_diagram()
        el = d.elements
        with pytest.raises(ValueError, match="empty"):
            el.rectangle("", [])

    def test_card_empty_name_raises(self):
        d = activity_diagram()
        el = d.elements
        with pytest.raises(ValueError, match="empty"):
            el.card("", [])


class TestActivityNewFeaturesPlantUMLValidation:

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

    def test_plantuml_swimlane_display_name(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = activity_diagram()
        el = d.elements
        d.add(
            el.swimlane("svc", color="#LightBlue", display_name="Service Layer"),
            el.start(),
            el.action("Process request"),
            el.swimlane("db", display_name="Database"),
            el.action("Query data"),
            el.swimlane("svc"),
            el.action("Return response"),
            el.stop(),
        )

        puml_file = tmp_path / "activity_swimlane_alias.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_plantuml_action_stereotype(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = activity_diagram()
        el = d.elements
        d.add(
            el.start(),
            el.action("Read input", stereotype="input"),
            el.action("Process", stereotype="object"),
            el.action("Write output", stereotype="output"),
            el.stop(),
        )

        puml_file = tmp_path / "activity_stereotype.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_plantuml_while_backward_action(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = activity_diagram()
        el = d.elements
        d.add(
            el.start(),
            el.while_("More items?", [
                el.action("Process item"),
            ], is_label="yes", endwhile_label="no", backward_action="Log iteration"),
            el.stop(),
        )

        puml_file = tmp_path / "activity_while_backward.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_plantuml_connector_color(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = activity_diagram()
        el = d.elements
        d.add(
            el.start(),
            el.action("Step 1"),
            el.connector("B", color="blue"),
            el.action("Step 2"),
            el.connector("B", color="blue"),
            el.stop(),
        )

        puml_file = tmp_path / "activity_connector_color.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_plantuml_package_rectangle_card(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = activity_diagram()
        el = d.elements
        d.add(
            el.start(),
            el.package("Package Name", [
                el.action("Action in package"),
            ]),
            el.rectangle("Rectangle Name", [
                el.action("Action in rectangle"),
            ]),
            el.card("Card Name", [
                el.action("Action in card"),
            ]),
            el.stop(),
        )

        puml_file = tmp_path / "activity_package_rect_card.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_plantuml_uml_stereotypes(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = activity_diagram()
        el = d.elements
        d.add(
            el.start(),
            el.action("Wait for timeout", stereotype="timeEvent"),
            el.action("Send notification", stereotype="sendSignal"),
            el.action("Wait for response", stereotype="acceptEvent"),
            el.action("Process object", stereotype="object"),
            el.action("Handle trigger", stereotype="trigger"),
            el.stop(),
        )

        puml_file = tmp_path / "activity_uml_stereotypes.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"
