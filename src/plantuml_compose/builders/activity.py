"""Activity diagram builder with context manager syntax.

Provides a fluent API for constructing activity diagrams:

    with activity_diagram(title="Order Process") as d:
        d.start()
        d.action("Receive Order")

        with d.if_("Valid?", then_label="yes") as branch:
            branch.action("Process")
            with branch.else_("no"):
                branch.action("Reject")

        d.stop()

    print(d.render())
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Literal

from ..primitives.activity import (
    Action,
    ActionShape,
    ActivityDiagram,
    ActivityElement,
    ActivityNote,
    Arrow,
    ArrowStyle,
    Break,
    Case,
    Connector,
    Detach,
    ElseIfBranch,
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
from ..primitives.activity import GotoLabel as ActivityLabel
from ..primitives.common import (
    ColorLike,
    Label,
    LabelLike,
)


class _BaseActivityBuilder:
    """Base class for activity builders with shared methods."""

    def __init__(self) -> None:
        self._elements: list[ActivityElement] = []

    def start(self) -> Start:
        """Add a start node."""
        s = Start()
        self._elements.append(s)
        return s

    def stop(self) -> Stop:
        """Add a stop node (filled circle)."""
        s = Stop()
        self._elements.append(s)
        return s

    def end(self) -> End:
        """Add an end node (circle with X)."""
        e = End()
        self._elements.append(e)
        return e

    def action(
        self,
        label: str | Label,
        *,
        shape: ActionShape = "default",
        color: ColorLike | None = None,
    ) -> Action:
        """Add an action.

        Args:
            label: Action text
            shape: SDL shape type
            color: Background color

        Returns:
            The created Action
        """
        text = label.text if isinstance(label, Label) else label
        if not text:
            raise ValueError("Action label cannot be empty")
        label_obj = Label(label) if isinstance(label, str) else label
        a = Action(label=label_obj, shape=shape, color=color)
        self._elements.append(a)
        return a

    def arrow(
        self,
        label: str | Label | None = None,
        *,
        color: ColorLike | None = None,
        style: ArrowStyle = "solid",
        bold: bool = False,
    ) -> Arrow:
        """Add an arrow with optional label.

        Args:
            label: Arrow label
            color: Arrow color
            style: Arrow style (solid, dashed, dotted, hidden)
            bold: If True, use bold arrow

        Returns:
            The created Arrow
        """
        label_obj = Label(label) if isinstance(label, str) else label
        a = Arrow(
            label=label_obj,
            color=color,
            style=style,
            bold=bold,
        )
        self._elements.append(a)
        return a

    def break_(self) -> Break:
        """Add a break statement (exit loop)."""
        b = Break()
        self._elements.append(b)
        return b

    def kill(self) -> Kill:
        """Add a kill terminator (X symbol)."""
        k = Kill()
        self._elements.append(k)
        return k

    def detach(self) -> Detach:
        """Detach from flow."""
        d = Detach()
        self._elements.append(d)
        return d

    def connector(self, name: str) -> Connector:
        """Add a connector for goto-like jumps."""
        c = Connector(name=name)
        self._elements.append(c)
        return c

    def goto(self, label: str) -> Goto:
        """Add a goto statement (experimental)."""
        g = Goto(label=label)
        self._elements.append(g)
        return g

    def label(self, name: str) -> ActivityLabel:
        """Add a label for goto (experimental)."""
        l = ActivityLabel(name=name)
        self._elements.append(l)
        return l

    def swimlane(self, name: str, color: ColorLike | None = None) -> Swimlane:
        """Switch to a swimlane.

        Args:
            name: Lane name
            color: Lane background color

        Returns:
            The created Swimlane
        """
        if not name:
            raise ValueError("Swimlane name cannot be empty")
        s = Swimlane(name=name, color=color)
        self._elements.append(s)
        return s

    def note(
        self,
        content: str | Label,
        position: Literal["left", "right"] = "right",
        *,
        floating: bool = False,
    ) -> ActivityNote:
        """Add a note.

        Args:
            content: Note text
            position: "left" or "right"
            floating: If True, creates a floating note

        Returns:
            The created ActivityNote
        """
        text = content.text if isinstance(content, Label) else content
        if not text:
            raise ValueError("Note content cannot be empty")
        content_label = Label(content) if isinstance(content, str) else content
        n = ActivityNote(
            content=content_label,
            position=position,
            floating=floating,
        )
        self._elements.append(n)
        return n

    # Control flow context managers
    @contextmanager
    def if_(
        self,
        condition: str,
        *,
        then_label: str | None = None,
    ) -> Iterator["_IfBuilder"]:
        """Create an if statement.

        Usage:
            with d.if_("Valid?", then_label="yes") as branch:
                branch.action("Process")
                with branch.else_("no") as else_block:
                    else_block.action("Reject")
        """
        builder = _IfBuilder(condition, then_label)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def switch(self, condition: str) -> Iterator["_SwitchBuilder"]:
        """Create a switch statement.

        Usage:
            with d.switch("Type?") as sw:
                with sw.case("A"):
                    sw.action("Handle A")
                with sw.case("B"):
                    sw.action("Handle B")
        """
        builder = _SwitchBuilder(condition)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def while_(
        self,
        condition: str,
        *,
        is_label: str | None = None,
        endwhile_label: str | None = None,
    ) -> Iterator["_WhileBuilder"]:
        """Create a while loop.

        Usage:
            with d.while_("More items?", is_label="yes", endwhile_label="no") as loop:
                loop.action("Process item")
        """
        builder = _WhileBuilder(condition, is_label, endwhile_label)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def repeat(
        self,
        *,
        start_label: str | None = None,
        condition: str | None = None,
        is_label: str | None = None,
        not_label: str | None = None,
        backward_action: str | None = None,
    ) -> Iterator["_RepeatBuilder"]:
        """Create a repeat-while loop.

        Usage:
            with d.repeat(condition="More?", is_label="yes", not_label="no") as loop:
                loop.action("Process")
        """
        builder = _RepeatBuilder(
            start_label=start_label,
            condition=condition,
            is_label=is_label,
            not_label=not_label,
            backward_action=backward_action,
        )
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def fork(
        self,
        end_style: str = "fork",
    ) -> Iterator["_ForkBuilder"]:
        """Create a fork/join for parallel execution.

        Usage:
            with d.fork() as f:
                with f.branch():
                    f.action("Task 1")
                with f.branch():
                    f.action("Task 2")
        """
        builder = _ForkBuilder(end_style)  # type: ignore[arg-type]
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def split(self) -> Iterator["_SplitBuilder"]:
        """Create a split for parallel paths (no sync bar).

        Usage:
            with d.split() as s:
                with s.branch():
                    s.action("Path 1")
                with s.branch():
                    s.action("Path 2")
        """
        builder = _SplitBuilder()
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def partition(
        self,
        name: str,
        color: ColorLike | None = None,
    ) -> Iterator["_PartitionBuilder"]:
        """Create a partition (grouping with border).

        Usage:
            with d.partition("Validation") as p:
                p.action("Validate input")
        """
        builder = _PartitionBuilder(name, color)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def group(self, name: str) -> Iterator["_GroupBuilder"]:
        """Create a group (lighter grouping).

        Usage:
            with d.group("Processing") as g:
                g.action("Process")
        """
        builder = _GroupBuilder(name)
        yield builder
        self._elements.append(builder._build())


class _IfBuilder(_BaseActivityBuilder):
    """Builder for if statements."""

    def __init__(self, condition: str, then_label: str | None) -> None:
        super().__init__()
        self._condition = condition
        self._then_label = then_label
        self._elseif_branches: list[ElseIfBranch] = []
        self._else_label: str | None = None
        self._else_elements: list[ActivityElement] = []

    @contextmanager
    def elseif(
        self,
        condition: str,
        *,
        then_label: str | None = None,
    ) -> Iterator["_ElseIfBuilder"]:
        """Add an elseif branch."""
        builder = _ElseIfBuilder(condition, then_label)
        yield builder
        self._elseif_branches.append(builder._build())

    @contextmanager
    def else_(self, label: str | None = None) -> Iterator["_ElseBuilder"]:
        """Add an else branch."""
        self._else_label = label
        builder = _ElseBuilder()
        yield builder
        self._else_elements = list(builder._elements)

    def _build(self) -> If:
        """Build the if statement."""
        return If(
            condition=self._condition,
            then_label=self._then_label,
            then_elements=tuple(self._elements),
            elseif_branches=tuple(self._elseif_branches),
            else_label=self._else_label,
            else_elements=tuple(self._else_elements),
        )


class _ElseIfBuilder(_BaseActivityBuilder):
    """Builder for elseif branches."""

    def __init__(self, condition: str, then_label: str | None) -> None:
        super().__init__()
        self._condition = condition
        self._then_label = then_label

    def _build(self) -> ElseIfBranch:
        """Build the elseif branch."""
        return ElseIfBranch(
            condition=self._condition,
            then_label=self._then_label,
            elements=tuple(self._elements),
        )


class _ElseBuilder(_BaseActivityBuilder):
    """Builder for else branches."""

    pass


class _SwitchBuilder(_BaseActivityBuilder):
    """Builder for switch statements."""

    def __init__(self, condition: str) -> None:
        super().__init__()
        self._condition = condition
        self._cases: list[Case] = []

    @contextmanager
    def case(self, label: str) -> Iterator["_CaseBuilder"]:
        """Add a case."""
        builder = _CaseBuilder(label)
        yield builder
        self._cases.append(builder._build())

    def _build(self) -> Switch:
        """Build the switch statement."""
        return Switch(
            condition=self._condition,
            cases=tuple(self._cases),
        )


class _CaseBuilder(_BaseActivityBuilder):
    """Builder for case blocks."""

    def __init__(self, label: str) -> None:
        super().__init__()
        self._label = label

    def _build(self) -> Case:
        """Build the case."""
        return Case(
            label=self._label,
            elements=tuple(self._elements),
        )


class _WhileBuilder(_BaseActivityBuilder):
    """Builder for while loops."""

    def __init__(
        self,
        condition: str,
        is_label: str | None,
        endwhile_label: str | None,
    ) -> None:
        super().__init__()
        self._condition = condition
        self._is_label = is_label
        self._endwhile_label = endwhile_label

    def _build(self) -> While:
        """Build the while loop."""
        return While(
            condition=self._condition,
            is_label=self._is_label,
            elements=tuple(self._elements),
            endwhile_label=self._endwhile_label,
        )


class _RepeatBuilder(_BaseActivityBuilder):
    """Builder for repeat loops."""

    def __init__(
        self,
        start_label: str | None,
        condition: str | None,
        is_label: str | None,
        not_label: str | None,
        backward_action: str | None,
    ) -> None:
        super().__init__()
        self._start_label = start_label
        self._condition = condition
        self._is_label = is_label
        self._not_label = not_label
        self._backward_action = backward_action

    def _build(self) -> Repeat:
        """Build the repeat loop."""
        return Repeat(
            elements=tuple(self._elements),
            start_label=self._start_label,
            condition=self._condition,
            is_label=self._is_label,
            not_label=self._not_label,
            backward_action=self._backward_action,
        )


class _ForkBuilder(_BaseActivityBuilder):
    """Builder for fork/join."""

    def __init__(self, end_style: str) -> None:
        super().__init__()
        self._end_style = end_style
        self._branches: list[list[ActivityElement]] = []

    @contextmanager
    def branch(self) -> Iterator["_BranchBuilder"]:
        """Add a branch to the fork."""
        builder = _BranchBuilder()
        yield builder
        self._branches.append(list(builder._elements))

    def _build(self) -> Fork:
        """Build the fork."""
        return Fork(
            branches=tuple(tuple(b) for b in self._branches),
            end_style=self._end_style,  # type: ignore[arg-type]
        )


class _SplitBuilder(_BaseActivityBuilder):
    """Builder for split."""

    def __init__(self) -> None:
        super().__init__()
        self._branches: list[list[ActivityElement]] = []

    @contextmanager
    def branch(self) -> Iterator["_BranchBuilder"]:
        """Add a branch to the split."""
        builder = _BranchBuilder()
        yield builder
        self._branches.append(list(builder._elements))

    def _build(self) -> Split:
        """Build the split."""
        return Split(
            branches=tuple(tuple(b) for b in self._branches),
        )


class _BranchBuilder(_BaseActivityBuilder):
    """Builder for fork/split branches."""

    pass


class _PartitionBuilder(_BaseActivityBuilder):
    """Builder for partitions."""

    def __init__(self, name: str, color: ColorLike | None) -> None:
        if not name:
            raise ValueError("Partition name cannot be empty")
        super().__init__()
        self._name = name
        self._color = color

    def _build(self) -> Partition:
        """Build the partition."""
        return Partition(
            name=self._name,
            color=self._color,
            elements=tuple(self._elements),
        )


class _GroupBuilder(_BaseActivityBuilder):
    """Builder for groups."""

    def __init__(self, name: str) -> None:
        if not name:
            raise ValueError("Group name cannot be empty")
        super().__init__()
        self._name = name

    def _build(self) -> Group:
        """Build the group."""
        return Group(
            name=self._name,
            elements=tuple(self._elements),
        )


class ActivityDiagramBuilder(_BaseActivityBuilder):
    """Builder for complete activity diagrams.

    Usage:
        with activity_diagram(title="Order Process") as d:
            d.start()
            d.action("Receive Order")
            d.stop()

        diagram = d.build()
        print(render(diagram))
    """

    def __init__(self, *, title: str | None = None) -> None:
        super().__init__()
        self._title = title

    def build(self) -> ActivityDiagram:
        """Build the complete activity diagram."""
        return ActivityDiagram(
            elements=tuple(self._elements),
            title=self._title,
        )

    def render(self) -> str:
        """Build and render the diagram to PlantUML text.

        Convenience method combining build() and render() in one call.
        """
        from ..renderers import render
        return render(self.build())


@contextmanager
def activity_diagram(
    *,
    title: str | None = None,
) -> Iterator[ActivityDiagramBuilder]:
    """Create an activity diagram with context manager syntax.

    Usage:
        with activity_diagram(title="Order Process") as d:
            d.start()
            d.action("Receive Order")

            with d.if_("Valid?", then_label="yes") as branch:
                branch.action("Process")
                with branch.else_("no") as else_block:
                    else_block.action("Reject")

            d.stop()

        print(d.render())

    Args:
        title: Optional diagram title

    Yields:
        An ActivityDiagramBuilder for adding diagram elements
    """
    builder = ActivityDiagramBuilder(title=title)
    yield builder
