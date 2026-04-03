"""Activity diagram composer.

Activity diagrams show workflows with decisions and parallel paths.
Unlike structural composers (component, class, etc.) that use d.add()
and d.connect(), activity diagrams are inherently sequential and nested,
so this composer uses context managers for control structures.

Example:
    d = activity_diagram(title="Order Process")
    d.start()
    d.action("Receive Order")

    with d.if_("Valid?", then_label="yes") as branch:
        branch.action("Process")
        with branch.else_("no") as else_block:
            else_block.action("Reject")

    d.stop()

    print(render(d))
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
    LayoutEngine,
    Legend,
    LineStyleLike,
    LineType,
    Scale,
    StyleLike,
    ThemeLike,
    coerce_line_style,
    validate_literal_type,
    validate_style_background_only,
)
from ..primitives.styles import (
    ActivityDiagramStyleLike,
    coerce_activity_diagram_style,
)

# Type alias for fork end styles
ForkEndStyle = Literal["fork", "merge", "or", "and"]


# ---------------------------------------------------------------------------
# Nested builder classes (used inside context managers)
# ---------------------------------------------------------------------------


class _NestedActivityBuilder:
    """Base for nested activity builders (inside if_, while_, fork, etc.).

    Exposes methods valid within nested contexts. Does NOT include
    diagram-level methods like swimlane(), start(), stop().
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
            style: Visual style (background only)
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
            style: Line style (color, bold)
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
        """Exit the enclosing loop (while or repeat)."""
        b = Break()
        self._elements.append(b)
        return b

    def end(self) -> End:
        """Add an end terminator (circle with X).

        Unlike kill(), end() can be used inside conditionals.
        """
        e = End()
        self._elements.append(e)
        return e

    def connector(self, name: str) -> Connector:
        """Add a named connector point for jumps."""
        c = Connector(name=name)
        self._elements.append(c)
        return c

    def goto(self, label: str) -> Goto:
        """Add a goto statement (experimental)."""
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
            position: Which side ("left" or "right")
            floating: If True, note floats independently
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
    ) -> Iterator[_IfBuilder]:
        """Create an if/else branch.

        Args:
            condition: Condition text shown in the decision diamond
            then_label: Label for the "then" branch arrow (e.g., "yes")
        """
        builder = _IfBuilder(condition, then_label)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def switch(self, condition: str) -> Iterator[_SwitchBuilder]:
        """Create a switch/case branch.

        Args:
            condition: Condition text shown in the decision diamond
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
    ) -> Iterator[_WhileBuilder]:
        """Create a while loop.

        Args:
            condition: Loop condition shown in the diamond
            is_label: Label for the "true" path (e.g., "yes")
            endwhile_label: Label for the "false" path (e.g., "no")
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
    ) -> Iterator[_RepeatBuilder]:
        """Create a repeat-while loop (do-while).

        Args:
            start_label: Label shown at loop entry point
            condition: Exit condition shown in the diamond
            is_label: Label for the "repeat" path (e.g., "yes")
            not_label: Label for the "exit" path (e.g., "no")
            backward_action: Action label on the backward arrow
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
    ) -> Iterator[_ForkBuilder]:
        """Create a fork/join for parallel execution.

        Args:
            end_style: How to end the fork ("fork", "merge", "or", "and")
        """
        validate_literal_type(end_style, ForkEndStyle, "end_style")
        builder = _ForkBuilder(end_style)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def split(self) -> Iterator[_SplitBuilder]:
        """Create a split for parallel paths (no sync bar)."""
        builder = _SplitBuilder()
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def partition(
        self,
        name: str,
        color: ColorLike | None = None,
    ) -> Iterator[_PartitionBuilder]:
        """Create a partition (grouping with visible border).

        Args:
            name: Partition label
            color: Background color
        """
        builder = _PartitionBuilder(name, color)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def group(self, name: str) -> Iterator[_GroupBuilder]:
        """Create a group (minimal visual grouping).

        Args:
            name: Group label
        """
        builder = _GroupBuilder(name)
        yield builder
        self._elements.append(builder._build())


class _TerminatorsMixin:
    """Mixin providing kill() and detach() for contexts where PlantUML supports them.

    PlantUML supports kill/detach in: top level, fork/split branches,
    while/repeat loops, partitions and groups.

    NOT supported in: if/else conditionals, switch/case.
    """

    _elements: list  # Provided by _NestedActivityBuilder

    def kill(self) -> Kill:
        """Add a kill terminator (X symbol)."""
        k = Kill()
        self._elements.append(k)
        return k

    def detach(self) -> Detach:
        """Detach from flow (async continuation)."""
        d = Detach()
        self._elements.append(d)
        return d


# ---------------------------------------------------------------------------
# Control structure builders
# ---------------------------------------------------------------------------


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
    ) -> Iterator[_ElseIfBuilder]:
        """Add an elseif branch.

        Raises:
            ValueError: If called after else_()
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
    def else_(self, label: str | None = None) -> Iterator[_ElseBuilder]:
        """Add an else branch."""
        self._else_called = True
        self._else_label = label
        builder = _ElseBuilder()
        yield builder
        self._else_elements = list(builder._elements)

    def _build(self) -> If:
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
        return ElseIfBranch(
            condition=self._condition,
            then_label=self._then_label,
            elements=tuple(self._elements),
        )


class _ElseBuilder(_NestedActivityBuilder):
    """Builder for else branches."""

    pass


class _SwitchBuilder:
    """Builder for switch statements. Only exposes case()."""

    def __init__(self, condition: str) -> None:
        self._condition = condition
        self._cases: list[Case] = []

    @contextmanager
    def case(self, label: str) -> Iterator[_CaseBuilder]:
        """Add a case."""
        builder = _CaseBuilder(label)
        yield builder
        self._cases.append(builder._build())

    def _build(self) -> Switch:
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
        return Case(
            label=self._label,
            elements=tuple(self._elements),
        )


class _WhileBuilder(_TerminatorsMixin, _NestedActivityBuilder):
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
        return While(
            condition=self._condition,
            is_label=self._is_label,
            elements=tuple(self._elements),
            endwhile_label=self._endwhile_label,
        )


class _RepeatBuilder(_TerminatorsMixin, _NestedActivityBuilder):
    """Builder for repeat-while loops."""

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
        return Repeat(
            elements=tuple(self._elements),
            start_label=self._start_label,
            condition=self._condition,
            is_label=self._is_label,
            not_label=self._not_label,
            backward_action=self._backward_action,
        )


class _ForkBuilder:
    """Builder for fork/join. Only exposes branch()."""

    def __init__(self, end_style: ForkEndStyle) -> None:
        self._end_style: ForkEndStyle = end_style
        self._branches: list[list[ActivityElement]] = []

    @contextmanager
    def branch(self) -> Iterator[_BranchBuilder]:
        """Add a branch to the fork."""
        builder = _BranchBuilder()
        yield builder
        self._branches.append(list(builder._elements))

    def _build(self) -> Fork:
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
    """Builder for split. Only exposes branch()."""

    def __init__(self) -> None:
        self._branches: list[list[ActivityElement]] = []

    @contextmanager
    def branch(self) -> Iterator[_BranchBuilder]:
        """Add a branch to the split."""
        builder = _BranchBuilder()
        yield builder
        self._branches.append(list(builder._elements))

    def _build(self) -> Split:
        if not self._branches:
            raise ValueError(
                "Split must have at least one branch. "
                "Use 'with s.branch() as b: b.action(...)'"
            )
        return Split(
            branches=tuple(tuple(b) for b in self._branches),
        )


class _BranchBuilder(_TerminatorsMixin, _NestedActivityBuilder):
    """Builder for fork/split branches."""

    pass


class _PartitionBuilder(_TerminatorsMixin, _NestedActivityBuilder):
    """Builder for partitions."""

    def __init__(self, name: str, color: ColorLike | None) -> None:
        if not name:
            raise ValueError("Partition name cannot be empty")
        super().__init__()
        self._name = name
        self._color = color

    def _build(self) -> Partition:
        return Partition(
            name=self._name,
            color=self._color,
            elements=tuple(self._elements),
        )


class _GroupBuilder(_TerminatorsMixin, _NestedActivityBuilder):
    """Builder for groups."""

    def __init__(self, name: str) -> None:
        if not name:
            raise ValueError("Group name cannot be empty")
        super().__init__()
        self._name = name

    def _build(self) -> Group:
        return Group(
            name=self._name,
            elements=tuple(self._elements),
        )


# ---------------------------------------------------------------------------
# Top-level composer
# ---------------------------------------------------------------------------


class ActivityComposer(_TerminatorsMixin, _NestedActivityBuilder):
    """Composer for complete activity diagrams.

    Usage:
        d = activity_diagram(title="Order Process")
        d.start()
        d.action("Receive Order")

        with d.if_("Valid?", then_label="yes") as branch:
            branch.action("Process")
            with branch.else_("no") as else_block:
                else_block.action("Reject")

        d.stop()

        print(render(d))
    """

    def __init__(
        self,
        *,
        title: str | None = None,
        mainframe: str | None = None,
        caption: str | None = None,
        header: str | Header | None = None,
        footer: str | Footer | None = None,
        legend: str | Legend | None = None,
        scale: float | Scale | None = None,
        theme: ThemeLike = None,
        layout_engine: LayoutEngine | None = None,
        linetype: LineType | None = None,
        diagram_style: ActivityDiagramStyleLike | None = None,
        vertical_if: bool = False,
    ) -> None:
        super().__init__()
        self._title = title
        self._mainframe = mainframe
        self._caption = caption
        self._header = Header(header) if isinstance(header, str) else header
        self._footer = Footer(footer) if isinstance(footer, str) else footer
        self._legend = Legend(legend) if isinstance(legend, str) else legend
        self._scale = (
            Scale(factor=scale) if isinstance(scale, (int, float)) else scale
        )
        self._theme: ThemeLike = theme
        self._layout_engine: LayoutEngine | None = layout_engine
        self._linetype: LineType | None = linetype
        self._diagram_style = (
            coerce_activity_diagram_style(diagram_style)
            if diagram_style
            else None
        )
        self._vertical_if = vertical_if

    def start(self) -> Start:
        """Add a start node (filled circle)."""
        s = Start()
        self._elements.append(s)
        return s

    def stop(self) -> Stop:
        """Add a stop node (filled circle with border)."""
        s = Stop()
        self._elements.append(s)
        return s

    def end(self) -> End:
        """Add an end node (circle with X)."""
        e = End()
        self._elements.append(e)
        return e

    def label(self, name: str) -> ActivityLabel:
        """Add a label for goto (experimental)."""
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
        """
        if not name:
            raise ValueError("Swimlane name cannot be empty")
        s = Swimlane(name=name, color=color)
        self._elements.append(s)
        return s

    def build(self) -> ActivityDiagram:
        """Build the frozen ActivityDiagram primitive."""
        return ActivityDiagram(
            elements=tuple(self._elements),
            title=self._title,
            mainframe=self._mainframe,
            caption=self._caption,
            header=self._header,
            footer=self._footer,
            legend=self._legend,
            scale=self._scale,
            theme=self._theme,
            layout_engine=self._layout_engine,
            linetype=self._linetype,
            diagram_style=self._diagram_style,
            vertical_if=self._vertical_if,
        )

    def render(self) -> str:
        """Build and render to PlantUML text."""
        from ..renderers import render

        return render(self.build())


# ---------------------------------------------------------------------------
# Public factory
# ---------------------------------------------------------------------------


def activity_diagram(
    *,
    title: str | None = None,
    mainframe: str | None = None,
    caption: str | None = None,
    header: str | Header | None = None,
    footer: str | Footer | None = None,
    legend: str | Legend | None = None,
    scale: float | Scale | None = None,
    theme: ThemeLike = None,
    layout_engine: LayoutEngine | None = None,
    linetype: LineType | None = None,
    diagram_style: ActivityDiagramStyleLike | None = None,
    vertical_if: bool = False,
) -> ActivityComposer:
    """Create an activity diagram composer.

    Args:
        title: Diagram title
        mainframe: Frame label drawn around the entire diagram
        caption: Diagram caption (appears below diagram)
        header: Header text or Header object
        footer: Footer text or Footer object
        legend: Legend text or Legend object
        scale: Scale factor or Scale object
        theme: PlantUML theme name (e.g., "cerulean", "amiga")
        layout_engine: Layout engine ("smetana" for pure-Java GraphViz)
        linetype: Line routing style ("ortho" for right angles)
        diagram_style: CSS-like diagram styling (ActivityDiagramStyle or dict)
        vertical_if: If True, if/else branches render vertically

    Returns:
        An ActivityComposer for adding diagram elements
    """
    return ActivityComposer(
        title=title,
        mainframe=mainframe,
        caption=caption,
        header=header,
        footer=footer,
        legend=legend,
        scale=scale,
        theme=theme,
        layout_engine=layout_engine,
        linetype=linetype,
        diagram_style=diagram_style,
        vertical_if=vertical_if,
    )
