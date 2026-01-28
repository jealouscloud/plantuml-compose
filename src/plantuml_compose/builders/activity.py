"""Activity diagram builder with context manager syntax.

When to Use
-----------
Activity diagrams show workflows with decisions and parallel paths.
Use when:

- Modeling business processes (order fulfillment, approvals)
- Documenting algorithms with branching
- Showing user workflows with decision points
- Visualizing parallel operations

NOT for:
- Object lifecycles (use state diagram)
- Message exchanges between systems (use sequence diagram)
- Static structure (use class diagram)

Key Concepts
------------
Action:     A step in the workflow (rounded rectangle)
Decision:   Branch based on condition (if/else, switch)
Fork/Join:  Parallel execution paths

Control flow (arrows implied between actions):

    (●)──►[Action A]──►◆──►[Action B]──►(◉)
           start     decision          stop

Branching:

    with d.if_("Valid?") as branch:
        branch.action("Process")       # "yes" branch
        with branch.else_():
            branch.action("Reject")    # "no" branch

Parallel execution:

              │
          ════╪════   <- fork
          │   │   │
          ▼   ▼   ▼
         [A] [B] [C]  (all run concurrently)
          │   │   │
          ════╪════   <- join (waits for all)
              │

Swimlanes (partition by actor/department):

    |Customer|          |Warehouse|
        │                   │
     [Browse]               │
        │                   │
     [Order]───────────►[Pick Items]
        │                   │
     [Pay]              [Ship]
        │                   │

Example
-------
    with activity_diagram(title="Order Process") as d:
        d.start()
        d.action("Receive Order")

        with d.if_("Valid?", then_label="yes") as branch:
            branch.action("Process")
            with branch.else_("no"):
                branch.action("Reject")

        d.stop()

    print(render(d.build()))
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
    Footer,
    Header,
    Label,
    Legend,
    LineStyleLike,
    Scale,
    StyleLike,
    coerce_line_style,
    validate_literal_type,
    validate_style_background_only,
)

# Type alias for fork end styles - defines valid values once
ForkEndStyle = Literal["fork", "merge", "or", "and"]


class _NestedActivityBuilder:
    """Base class for nested activity builders (inside if_, while_, fork, etc.).

    Only exposes methods that are valid within nested contexts.
    Does NOT include diagram-level methods like swimlane(), start(), stop(), end().
    """

    def __init__(self) -> None:
        self._elements: list[ActivityElement] = []

    def action(
        self,
        label: str | Label,
        *,
        shape: ActionShape = "default",
        style: StyleLike | None = None,
    ) -> Action:
        """Add an action.

        Args:
            label: Action text
            shape: SDL shape type
            style: Visual style (background, line, text_color)

        Returns:
            The created Action

        Example:
            d.action("Validate input")
            d.action("Send", shape="input")
            d.action("Important", style={"background": "yellow"})
        """
        text = label.text if isinstance(label, Label) else label
        if not text:
            raise ValueError("Action label cannot be empty")
        label_obj = Label(label) if isinstance(label, str) else label
        style_obj = validate_style_background_only(style, "Action")
        a = Action(label=label_obj, shape=shape, style=style_obj)
        self._elements.append(a)
        return a

    def arrow(
        self,
        label: str | Label | None = None,
        *,
        pattern: ArrowStyle = "solid",
        style: LineStyleLike | None = None,
    ) -> Arrow:
        """Add an arrow with optional label.

        Args:
            label: Arrow label
            pattern: Line pattern (solid, dashed, dotted, hidden)
            style: Line style (color, thickness, bold)

        Returns:
            The created Arrow

        Example:
            d.action("Step 1")
            d.arrow("next")
            d.action("Step 2")
            d.arrow(pattern="dashed", style={"color": "gray"})
        """
        label_obj = Label(label) if isinstance(label, str) else label
        style_obj = coerce_line_style(style) if style else None
        a = Arrow(
            label=label_obj,
            pattern=pattern,
            line_style=style_obj,
        )
        self._elements.append(a)
        return a

    def break_(self) -> Break:
        """Add a break statement (exit loop).

        Example:
            with d.while_("condition") as loop:
                loop.action("Process")
                with loop.if_("error") as check:
                    check.break_()  # exits the while loop
        """
        b = Break()
        self._elements.append(b)
        return b

    def kill(self) -> Kill:
        """Add a kill terminator (X symbol).

        Example:
            with d.if_("Fatal error?") as check:
                check.kill()  # terminates with X
        """
        k = Kill()
        self._elements.append(k)
        return k

    def detach(self) -> Detach:
        """Detach from flow.

        Example:
            with d.fork() as f:
                with f.branch() as b:
                    b.action("Background task")
                    b.detach()  # branch continues independently
        """
        d = Detach()
        self._elements.append(d)
        return d

    def connector(self, name: str) -> Connector:
        """Add a connector for goto-like jumps.

        Example:
            d.connector("A")  # defines connection point A
            d.action("Process")
            d.connector("A")  # jumps back to point A
        """
        c = Connector(name=name)
        self._elements.append(c)
        return c

    def goto(self, label: str) -> Goto:
        """Add a goto statement (experimental).

        Example:
            d.label("retry")
            d.action("Attempt operation")
            d.goto("retry")  # jumps to label
        """
        g = Goto(label=label)
        self._elements.append(g)
        return g

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
            position: Which side of the activity flow ("left" or "right")
            floating: If True, note floats independently rather than attaching
                to the previous action

        Returns:
            The created ActivityNote

        Example:
            d.action("Validate")
            d.note("Check all fields", position="right")
            d.note("Important!", floating=True)
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

        Args:
            condition: The condition text shown in the decision diamond
            then_label: Label for the "then" branch arrow (e.g., "yes")

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

        Args:
            condition: The condition text shown in the decision diamond

        Usage:
            with d.switch("Type?") as sw:
                with sw.case("A") as case_a:
                    case_a.action("Handle A")
                with sw.case("B") as case_b:
                    case_b.action("Handle B")
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

        Args:
            condition: The loop condition shown in the diamond
            is_label: Label for the "true" path (loop continues), e.g. "yes"
            endwhile_label: Label for the "false" path (loop exits), e.g. "no"

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
        """Create a repeat-while loop (do-while).

        Args:
            start_label: Label shown at loop entry point
            condition: The loop condition shown in the diamond
            is_label: Label for the "true" path (loop repeats), e.g. "yes"
            not_label: Label for the "false" path (loop exits), e.g. "no"
            backward_action: Action label shown on the backward arrow

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
        end_style: ForkEndStyle = "fork",
    ) -> Iterator["_ForkBuilder"]:
        """Create a fork/join for parallel execution.

        Args:
            end_style: How to end the fork - "fork" (sync bar), "merge" (single arrow),
                "or" (diamond), or "and" (bar). Defaults to "fork".

        Usage:
            with d.fork() as f:
                with f.branch() as b1:
                    b1.action("Task 1")
                with f.branch() as b2:
                    b2.action("Task 2")
        """
        validate_literal_type(end_style, ForkEndStyle, "end_style")
        builder = _ForkBuilder(end_style)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def split(self) -> Iterator["_SplitBuilder"]:
        """Create a split for parallel paths (no sync bar).

        Usage:
            with d.split() as s:
                with s.branch() as b1:
                    b1.action("Path 1")
                with s.branch() as b2:
                    b2.action("Path 2")
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
        """Create a partition (grouping with visible border).

        Args:
            name: Partition label
            color: Background color for the partition

        Usage:
            with d.partition("Validation", color="LightBlue") as p:
                p.action("Validate input")
        """
        builder = _PartitionBuilder(name, color)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def group(self, name: str) -> Iterator["_GroupBuilder"]:
        """Create a group (minimal visual grouping, no border).

        Unlike partition(), groups have a subtle header without a box border.

        Usage:
            with d.group("Processing") as g:
                g.action("Process")
        """
        builder = _GroupBuilder(name)
        yield builder
        self._elements.append(builder._build())


class _BaseActivityBuilder(_NestedActivityBuilder):
    """Extends nested builder with diagram-level methods.

    Only ActivityDiagramBuilder should inherit from this directly.
    Nested builders (if_, while_, fork branches, etc.) should inherit
    from _NestedActivityBuilder to avoid exposing invalid methods.
    """

    def start(self) -> Start:
        """Add a start node.

        Example:
            d.start()
            d.action("First action")
        """
        s = Start()
        self._elements.append(s)
        return s

    def stop(self) -> Stop:
        """Add a stop node (filled circle).

        Example:
            d.action("Final action")
            d.stop()
        """
        s = Stop()
        self._elements.append(s)
        return s

    def end(self) -> End:
        """Add an end node (circle with X).

        Example:
            d.action("Abnormal termination")
            d.end()  # different visual than stop()
        """
        e = End()
        self._elements.append(e)
        return e

    def label(self, name: str) -> ActivityLabel:
        """Add a label for goto (experimental).

        Example:
            d.label("retry_point")
            d.action("Try operation")
            d.goto("retry_point")
        """
        _label = ActivityLabel(name=name)
        self._elements.append(_label)
        return _label

    def swimlane(self, name: str, color: ColorLike | None = None) -> Swimlane:
        """Switch to a swimlane.

        Swimlanes organize actions into vertical columns. All subsequent
        actions belong to the current swimlane until you switch to another.

        Args:
            name: Lane name (creates lane if new, switches if existing)
            color: Lane background color

        Returns:
            The created Swimlane

        Example:
            with activity_diagram() as d:
                d.swimlane("Client")
                d.action("Submit order")
                d.swimlane("Server")
                d.action("Validate order")
                d.swimlane("Client")  # switch back
                d.action("Receive confirmation")
        """
        if not name:
            raise ValueError("Swimlane name cannot be empty")
        s = Swimlane(name=name, color=color)
        self._elements.append(s)
        return s


class _IfBuilder(_NestedActivityBuilder):
    """Builder for if statements."""

    def __init__(self, condition: str, then_label: str | None) -> None:
        super().__init__()
        self._condition = condition
        self._then_label = then_label
        self._elseif_branches: list[ElseIfBranch] = []
        self._else_label: str | None = None
        self._else_elements: list[ActivityElement] = []
        self._else_called: bool = False

    @contextmanager
    def elseif(
        self,
        condition: str,
        *,
        then_label: str | None = None,
    ) -> Iterator["_ElseIfBuilder"]:
        """Add an elseif branch.

        Usage:
            with d.if_("Score >= 90?", then_label="A") as branch:
                branch.action("Excellent")
                with branch.elseif("Score >= 80?", then_label="B") as elif_branch:
                    elif_branch.action("Good")

        Raises:
            ValueError: If called after else_() has been called
        """
        if self._else_called:
            raise ValueError(
                "elseif() cannot be called after else_(). "
                "The else branch must be the final branch in an if statement."
            )
        builder = _ElseIfBuilder(condition, then_label)
        yield builder
        self._elseif_branches.append(builder._build())

    @contextmanager
    def else_(self, label: str | None = None) -> Iterator["_ElseBuilder"]:
        """Add an else branch.

        Usage:
            with d.if_("Valid?", then_label="yes") as branch:
                branch.action("Process")
                with branch.else_("no") as else_branch:
                    else_branch.action("Reject")
        """
        self._else_called = True
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


class _ElseIfBuilder(_NestedActivityBuilder):
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


class _ElseBuilder(_NestedActivityBuilder):
    """Builder for else branches."""

    pass


class _SwitchBuilder:
    """Builder for switch statements.

    Only exposes case() - actions must be added inside cases.
    """

    def __init__(self, condition: str) -> None:
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
        if not self._cases:
            raise ValueError(
                "Switch must have at least one case. "
                "Use 'with sw.case(\"label\") as c: c.action(...)'"
            )
        return Switch(
            condition=self._condition,
            cases=tuple(self._cases),
        )


class _CaseBuilder(_NestedActivityBuilder):
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


class _WhileBuilder(_NestedActivityBuilder):
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


class _RepeatBuilder(_NestedActivityBuilder):
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


class _ForkBuilder:
    """Builder for fork/join.

    Only exposes branch() - actions must be added inside branches.
    """

    def __init__(self, end_style: ForkEndStyle) -> None:
        self._end_style: ForkEndStyle = end_style
        self._branches: list[list[ActivityElement]] = []

    @contextmanager
    def branch(self) -> Iterator["_BranchBuilder"]:
        """Add a branch to the fork."""
        builder = _BranchBuilder()
        yield builder
        self._branches.append(list(builder._elements))

    def _build(self) -> Fork:
        """Build the fork."""
        if not self._branches:
            raise ValueError(
                "Fork must have at least one branch. "
                "Use 'with f.branch() as b: b.action(...)'"
            )
        return Fork(
            branches=tuple(tuple(b) for b in self._branches),
            end_style=self._end_style,
        )


class _SplitBuilder:
    """Builder for split.

    Only exposes branch() - actions must be added inside branches.
    """

    def __init__(self) -> None:
        self._branches: list[list[ActivityElement]] = []

    @contextmanager
    def branch(self) -> Iterator["_BranchBuilder"]:
        """Add a branch to the split."""
        builder = _BranchBuilder()
        yield builder
        self._branches.append(list(builder._elements))

    def _build(self) -> Split:
        """Build the split."""
        if not self._branches:
            raise ValueError(
                "Split must have at least one branch. "
                "Use 'with s.branch() as b: b.action(...)'"
            )
        return Split(
            branches=tuple(tuple(b) for b in self._branches),
        )


class _BranchBuilder(_NestedActivityBuilder):
    """Builder for fork/split branches."""

    pass


class _PartitionBuilder(_NestedActivityBuilder):
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


class _GroupBuilder(_NestedActivityBuilder):
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

    def __init__(
        self,
        *,
        title: str | None = None,
        caption: str | None = None,
        header: str | Header | None = None,
        footer: str | Footer | None = None,
        legend: str | Legend | None = None,
        scale: float | Scale | None = None,
    ) -> None:
        super().__init__()
        self._title = title
        self._caption = caption
        self._header = Header(header) if isinstance(header, str) else header
        self._footer = Footer(footer) if isinstance(footer, str) else footer
        self._legend = Legend(legend) if isinstance(legend, str) else legend
        self._scale = (
            Scale(factor=scale) if isinstance(scale, (int, float)) else scale
        )
        # Track block context for detecting d.action() inside blocks
        self._block_stack: list[str] = []

    def _check_not_in_block(self, method_name: str) -> None:
        """Raise error if called inside a block context."""
        if self._block_stack:
            block_type = self._block_stack[-1]
            # Clean variable name: if_ -> if_block (not if__block)
            var_name = block_type.rstrip("_") + "_block"
            raise RuntimeError(
                f"d.{method_name}() called inside '{block_type}' block.\n"
                f"\n"
                f"Inside blocks, use the block's builder:\n"
                f"\n"
                f"    # Correct:\n"
                f"    with d.{block_type}(...) as {var_name}:\n"
                f"        {var_name}.{method_name}(...)\n"
                f"\n"
                f"    # Wrong - this is what raised this error:\n"
                f"    with d.{block_type}(...):\n"
                f"        d.{method_name}(...)\n"
                f"\n"
                f"If you want the {method_name} outside the block, "
                f"move it before or after the 'with' statement."
            )

    # Override methods to detect misuse inside blocks
    def start(self) -> Start:
        """Add a start node.

        Raises:
            RuntimeError: If called inside a block context
        """
        self._check_not_in_block("start")
        return super().start()

    def stop(self) -> Stop:
        """Add a stop node (filled circle).

        Raises:
            RuntimeError: If called inside a block context
        """
        self._check_not_in_block("stop")
        return super().stop()

    def end(self) -> End:
        """Add an end node (circle with X).

        Raises:
            RuntimeError: If called inside a block context
        """
        self._check_not_in_block("end")
        return super().end()

    def action(
        self,
        label: str | Label,
        *,
        shape: ActionShape = "default",
        style: StyleLike | None = None,
    ) -> Action:
        """Add an action.

        Raises:
            RuntimeError: If called inside a block context (if_, while_, etc.)
        """
        self._check_not_in_block("action")
        return super().action(label, shape=shape, style=style)

    def arrow(
        self,
        label: str | Label | None = None,
        *,
        pattern: ArrowStyle = "solid",
        style: LineStyleLike | None = None,
    ) -> Arrow:
        """Add an arrow with optional label.

        Raises:
            RuntimeError: If called inside a block context
        """
        self._check_not_in_block("arrow")
        return super().arrow(label, pattern=pattern, style=style)

    def break_(self) -> Break:
        """Add a break statement (exit loop).

        Raises:
            RuntimeError: If called inside a block context
        """
        self._check_not_in_block("break_")
        return super().break_()

    def kill(self) -> Kill:
        """Add a kill terminator (X symbol).

        Raises:
            RuntimeError: If called inside a block context
        """
        self._check_not_in_block("kill")
        return super().kill()

    def detach(self) -> Detach:
        """Detach from flow.

        Raises:
            RuntimeError: If called inside a block context
        """
        self._check_not_in_block("detach")
        return super().detach()

    def connector(self, name: str) -> Connector:
        """Add a connector for goto-like jumps.

        Raises:
            RuntimeError: If called inside a block context
        """
        self._check_not_in_block("connector")
        return super().connector(name)

    def goto(self, label: str) -> Goto:
        """Add a goto statement (experimental).

        Raises:
            RuntimeError: If called inside a block context
        """
        self._check_not_in_block("goto")
        return super().goto(label)

    def label(self, name: str) -> ActivityLabel:
        """Add a label for goto (experimental).

        Raises:
            RuntimeError: If called inside a block context
        """
        self._check_not_in_block("label")
        return super().label(name)

    def swimlane(self, name: str, color: ColorLike | None = None) -> Swimlane:
        """Switch to a swimlane.

        Raises:
            RuntimeError: If called inside a block context
        """
        self._check_not_in_block("swimlane")
        return super().swimlane(name, color)

    def note(
        self,
        content: str | Label,
        position: Literal["left", "right"] = "right",
        *,
        floating: bool = False,
    ) -> ActivityNote:
        """Add a note.

        Raises:
            RuntimeError: If called inside a block context
        """
        self._check_not_in_block("note")
        return super().note(content, position, floating=floating)

    # Override block context managers to track block stack
    @contextmanager
    def if_(
        self,
        condition: str,
        *,
        then_label: str | None = None,
    ) -> Iterator["_IfBuilder"]:
        """Create an if statement."""
        self._block_stack.append("if_")
        try:
            builder = _IfBuilder(condition, then_label)
            yield builder
            self._elements.append(builder._build())
        finally:
            self._block_stack.pop()

    @contextmanager
    def switch(self, condition: str) -> Iterator["_SwitchBuilder"]:
        """Create a switch statement."""
        self._block_stack.append("switch")
        try:
            builder = _SwitchBuilder(condition)
            yield builder
            self._elements.append(builder._build())
        finally:
            self._block_stack.pop()

    @contextmanager
    def while_(
        self,
        condition: str,
        *,
        is_label: str | None = None,
        endwhile_label: str | None = None,
    ) -> Iterator["_WhileBuilder"]:
        """Create a while loop.

        Args:
            condition: The loop condition shown in the diamond
            is_label: Label for the "true" path (loop continues), e.g. "yes"
            endwhile_label: Label for the "false" path (loop exits), e.g. "no"
        """
        self._block_stack.append("while_")
        try:
            builder = _WhileBuilder(condition, is_label, endwhile_label)
            yield builder
            self._elements.append(builder._build())
        finally:
            self._block_stack.pop()

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
        """Create a repeat-while loop (do-while).

        Args:
            start_label: Label shown at loop entry point
            condition: The loop condition shown in the diamond
            is_label: Label for the "true" path (loop repeats), e.g. "yes"
            not_label: Label for the "false" path (loop exits), e.g. "no"
            backward_action: Action label shown on the backward arrow
        """
        self._block_stack.append("repeat")
        try:
            builder = _RepeatBuilder(
                start_label=start_label,
                condition=condition,
                is_label=is_label,
                not_label=not_label,
                backward_action=backward_action,
            )
            yield builder
            self._elements.append(builder._build())
        finally:
            self._block_stack.pop()

    @contextmanager
    def fork(
        self,
        end_style: ForkEndStyle = "fork",
    ) -> Iterator["_ForkBuilder"]:
        """Create a fork/join for parallel execution.

        Args:
            end_style: How to end the fork - "fork" (sync bar), "merge" (single arrow),
                "or" (diamond), or "and" (bar). Defaults to "fork".
        """
        validate_literal_type(end_style, ForkEndStyle, "end_style")
        self._block_stack.append("fork")
        try:
            builder = _ForkBuilder(end_style)
            yield builder
            self._elements.append(builder._build())
        finally:
            self._block_stack.pop()

    @contextmanager
    def split(self) -> Iterator["_SplitBuilder"]:
        """Create a split for parallel paths (no sync bar)."""
        self._block_stack.append("split")
        try:
            builder = _SplitBuilder()
            yield builder
            self._elements.append(builder._build())
        finally:
            self._block_stack.pop()

    @contextmanager
    def partition(
        self,
        name: str,
        color: ColorLike | None = None,
    ) -> Iterator["_PartitionBuilder"]:
        """Create a partition (grouping with border)."""
        self._block_stack.append("partition")
        try:
            builder = _PartitionBuilder(name, color)
            yield builder
            self._elements.append(builder._build())
        finally:
            self._block_stack.pop()

    @contextmanager
    def group(self, name: str) -> Iterator["_GroupBuilder"]:
        """Create a group (lighter grouping)."""
        self._block_stack.append("group")
        try:
            builder = _GroupBuilder(name)
            yield builder
            self._elements.append(builder._build())
        finally:
            self._block_stack.pop()

    def build(self) -> ActivityDiagram:
        """Build the complete activity diagram."""
        return ActivityDiagram(
            elements=tuple(self._elements),
            title=self._title,
            caption=self._caption,
            header=self._header,
            footer=self._footer,
            legend=self._legend,
            scale=self._scale,
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
    caption: str | None = None,
    header: str | Header | None = None,
    footer: str | Footer | None = None,
    legend: str | Legend | None = None,
    scale: float | Scale | None = None,
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
        caption: Optional diagram caption
        header: Optional header text or Header object
        footer: Optional footer text or Footer object
        legend: Optional legend text or Legend object
        scale: Optional scale factor or Scale object

    Yields:
        An ActivityDiagramBuilder for adding diagram elements
    """
    builder = ActivityDiagramBuilder(
        title=title,
        caption=caption,
        header=header,
        footer=footer,
        legend=legend,
        scale=scale,
    )
    yield builder
