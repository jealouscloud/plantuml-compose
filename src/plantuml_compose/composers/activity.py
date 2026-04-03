"""Activity diagram composer.

Flow-based pattern with el.action(), el.if_(), el.while_(), etc.
All elements are pure factory functions returning frozen data objects,
registered via d.add().

Example:
    d = activity_diagram(title="Order Process")
    el = d.elements

    d.add(
        el.start(),
        el.action("Receive Order"),
        el.if_("Valid?", [
            el.action("Process"),
        ], "no", [
            el.action("Reject"),
        ], then_label="yes"),
        el.stop(),
    )

    print(render(d))
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

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
    validate_style_background_only,
)
from ..primitives.styles import (
    ActivityDiagramStyleLike,
    coerce_activity_diagram_style,
)

# Type alias for fork end styles
ForkEndStyle = Literal["fork", "merge", "or", "and"]


# ---------------------------------------------------------------------------
# Internal data types returned by namespace factories
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _StartData:
    pass


@dataclass(frozen=True)
class _StopData:
    pass


@dataclass(frozen=True)
class _EndData:
    pass


@dataclass(frozen=True)
class _ActionData:
    label: str | Label
    shape: ActionShape = "default"
    style: StyleLike | None = None


@dataclass(frozen=True)
class _ArrowData:
    label: str | Label | None = None
    pattern: ArrowStyle = "solid"
    style: LineStyleLike | None = None


@dataclass(frozen=True)
class _NoteData:
    content: str | Label
    position: Literal["left", "right"] = "right"
    floating: bool = False


@dataclass(frozen=True)
class _KillData:
    pass


@dataclass(frozen=True)
class _DetachData:
    pass


@dataclass(frozen=True)
class _BreakData:
    pass


@dataclass(frozen=True)
class _ConnectorData:
    name: str


@dataclass(frozen=True)
class _GotoData:
    label: str


@dataclass(frozen=True)
class _LabelData:
    name: str


@dataclass(frozen=True)
class _SwimlaneData:
    name: str
    color: ColorLike | None = None


@dataclass(frozen=True)
class _IfData:
    """The then branch events are in ``events``. Additional branches are
    alternating (label, events) pairs stored in ``extra_branches``.
    """
    condition: str
    then_label: str | None
    events: tuple[Any, ...]
    extra_branches: tuple[tuple[str | None, tuple[Any, ...]], ...] = ()


@dataclass(frozen=True)
class _WhileData:
    condition: str
    events: tuple[Any, ...]
    is_label: str | None = None
    endwhile_label: str | None = None


@dataclass(frozen=True)
class _RepeatData:
    events: tuple[Any, ...]
    condition: str | None = None
    is_label: str | None = None
    not_label: str | None = None
    backward_action: str | None = None
    start_label: str | None = None


@dataclass(frozen=True)
class _SwitchData:
    condition: str
    cases: tuple[tuple[str, tuple[Any, ...]], ...] = ()


@dataclass(frozen=True)
class _ForkData:
    branches: tuple[tuple[Any, ...], ...]
    end_style: ForkEndStyle = "fork"


@dataclass(frozen=True)
class _SplitData:
    branches: tuple[tuple[Any, ...], ...]


@dataclass(frozen=True)
class _PartitionData:
    name: str
    events: tuple[Any, ...]
    color: ColorLike | None = None


@dataclass(frozen=True)
class _GroupData:
    name: str
    events: tuple[Any, ...]


# Union of things that can appear in element lists
_FlowItem = (
    _StartData | _StopData | _EndData | _ActionData | _ArrowData
    | _NoteData | _KillData | _DetachData | _BreakData | _ConnectorData
    | _GotoData | _LabelData | _SwimlaneData | _IfData | _WhileData
    | _RepeatData | _SwitchData | _ForkData | _SplitData | _PartitionData
    | _GroupData
)


# ---------------------------------------------------------------------------
# Namespace
# ---------------------------------------------------------------------------


class ActivityElementNamespace:
    """Factory namespace for activity diagram flow elements."""

    # --- Simple elements ---

    def start(self) -> _StartData:
        """Start node (filled circle)."""
        return _StartData()

    def stop(self) -> _StopData:
        """Stop node (filled circle with border)."""
        return _StopData()

    def end(self) -> _EndData:
        """End node (circle with X)."""
        return _EndData()

    def action(
        self,
        label: str | Label,
        *,
        shape: ActionShape = "default",
        style: StyleLike | None = None,
    ) -> _ActionData:
        """An action step.

        Args:
            label: Action text
            shape: SDL shape type
            style: Visual style (background only)
        """
        text = label.text if isinstance(label, Label) else label
        if not text:
            raise ValueError("Action label cannot be empty")
        return _ActionData(label=label, shape=shape, style=style)

    def arrow(
        self,
        label: str | Label | None = None,
        *,
        pattern: ArrowStyle = "solid",
        style: LineStyleLike | None = None,
    ) -> _ArrowData:
        """Arrow with optional label.

        Args:
            label: Arrow label
            pattern: Line pattern (solid, dashed, dotted, hidden)
            style: Line style (color, bold)
        """
        return _ArrowData(label=label, pattern=pattern, style=style)

    def note(
        self,
        content: str | Label,
        position: Literal["left", "right"] = "right",
        *,
        floating: bool = False,
    ) -> _NoteData:
        """A note annotation.

        Args:
            content: Note text
            position: Which side ("left" or "right")
            floating: If True, note floats independently
        """
        text = content.text if isinstance(content, Label) else content
        if not text:
            raise ValueError("Note content cannot be empty")
        return _NoteData(content=content, position=position, floating=floating)

    def kill(self) -> _KillData:
        """Kill terminator (X symbol)."""
        return _KillData()

    def detach(self) -> _DetachData:
        """Detach from flow (async continuation)."""
        return _DetachData()

    def break_(self) -> _BreakData:
        """Break out of enclosing loop."""
        return _BreakData()

    def connector(self, name: str) -> _ConnectorData:
        """Named connector point for jumps."""
        return _ConnectorData(name=name)

    def goto(self, label: str) -> _GotoData:
        """Goto statement (experimental)."""
        return _GotoData(label=label)

    def label(self, name: str) -> _LabelData:
        """Label for goto (experimental)."""
        return _LabelData(name=name)

    def swimlane(self, name: str, color: ColorLike | None = None) -> _SwimlaneData:
        """Switch to a swimlane.

        Args:
            name: Lane name
            color: Lane background color
        """
        if not name:
            raise ValueError("Swimlane name cannot be empty")
        return _SwimlaneData(name=name, color=color)

    # --- Control structures ---

    def if_(
        self,
        condition: str,
        events: list[_FlowItem],
        *extra_branches: Any,
        then_label: str | None = None,
    ) -> _IfData:
        """Conditional branching (if/elseif/else).

        Extra branches are alternating (label, events) pairs.
        Use a condition string for elseif, or None for a plain else.

        Example (simple if/else):
            el.if_("Valid?", [
                el.action("Process"),
            ], "no", [
                el.action("Reject"),
            ], then_label="yes")

        Example (if/elseif/else):
            el.if_("Score >= 90?", [
                el.action("Excellent"),
            ], "Score >= 80?", [
                el.action("Good"),
            ], None, [
                el.action("Average"),
            ], then_label="A")
        """
        parsed: list[tuple[str | None, tuple[Any, ...]]] = []
        i = 0
        while i < len(extra_branches):
            branch_label = extra_branches[i]
            if i + 1 < len(extra_branches):
                branch_events = extra_branches[i + 1]
                parsed.append((branch_label, tuple(branch_events)))
                i += 2
            else:
                break

        return _IfData(
            condition=condition,
            then_label=then_label,
            events=tuple(events),
            extra_branches=tuple(parsed),
        )

    def while_(
        self,
        condition: str,
        events: list[_FlowItem],
        *,
        is_label: str | None = None,
        endwhile_label: str | None = None,
    ) -> _WhileData:
        """While loop.

        Args:
            condition: Loop condition
            events: Loop body
            is_label: Label for the "true" path
            endwhile_label: Label for the "false" path
        """
        return _WhileData(
            condition=condition,
            events=tuple(events),
            is_label=is_label,
            endwhile_label=endwhile_label,
        )

    def repeat(
        self,
        events: list[_FlowItem],
        *,
        condition: str | None = None,
        is_label: str | None = None,
        not_label: str | None = None,
        backward_action: str | None = None,
        start_label: str | None = None,
    ) -> _RepeatData:
        """Repeat-while loop (do-while).

        Args:
            events: Loop body
            condition: Exit condition
            is_label: Label for the "repeat" path
            not_label: Label for the "exit" path
            backward_action: Action label on the backward arrow
            start_label: Label at loop start
        """
        return _RepeatData(
            events=tuple(events),
            condition=condition,
            is_label=is_label,
            not_label=not_label,
            backward_action=backward_action,
            start_label=start_label,
        )

    def switch(
        self,
        condition: str,
        *cases: tuple[str, list[_FlowItem]],
    ) -> _SwitchData:
        """Switch/case branching.

        Cases are (label, events) tuples.

        Example:
            el.switch("Type?",
                ("A", [el.action("Handle A")]),
                ("B", [el.action("Handle B")]),
            )
        """
        if not cases:
            raise ValueError(
                "Switch must have at least one case. "
                "Pass (label, [events]) tuples as positional args."
            )
        parsed = tuple((label, tuple(evts)) for label, evts in cases)
        return _SwitchData(condition=condition, cases=parsed)

    def fork(
        self,
        *branches: list[_FlowItem],
        end_style: ForkEndStyle = "fork",
    ) -> _ForkData:
        """Fork/join for parallel execution.

        Each branch is a list of elements.

        Example:
            el.fork(
                [el.action("Task 1")],
                [el.action("Task 2")],
            )
        """
        if not branches:
            raise ValueError(
                "Fork must have at least one branch. "
                "Pass [events] lists as positional args."
            )
        _valid_end_styles = {"fork", "merge", "or", "and"}
        if end_style not in _valid_end_styles:
            raise ValueError(
                f"Invalid end_style {end_style!r}. "
                f"Must be one of: {', '.join(sorted(_valid_end_styles))}"
            )
        return _ForkData(
            branches=tuple(tuple(b) for b in branches),
            end_style=end_style,
        )

    def split(self, *branches: list[_FlowItem]) -> _SplitData:
        """Split for parallel paths (no sync bar).

        Each branch is a list of elements.

        Example:
            el.split(
                [el.action("Path 1")],
                [el.action("Path 2")],
            )
        """
        if not branches:
            raise ValueError(
                "Split must have at least one branch. "
                "Pass [events] lists as positional args."
            )
        return _SplitData(branches=tuple(tuple(b) for b in branches))

    def partition(
        self,
        name: str,
        events: list[_FlowItem],
        *,
        color: ColorLike | None = None,
    ) -> _PartitionData:
        """Partition (grouping with visible border).

        Args:
            name: Partition label
            events: Elements inside the partition
            color: Background color
        """
        if not name:
            raise ValueError("Partition name cannot be empty")
        return _PartitionData(name=name, events=tuple(events), color=color)

    def group(self, name: str, events: list[_FlowItem]) -> _GroupData:
        """Group (minimal visual grouping).

        Args:
            name: Group label
            events: Elements inside the group
        """
        if not name:
            raise ValueError("Group name cannot be empty")
        return _GroupData(name=name, events=tuple(events))


# ---------------------------------------------------------------------------
# Build helpers
# ---------------------------------------------------------------------------


def _build_item(item: _FlowItem) -> ActivityElement:
    """Convert a data object to a primitive, recursively."""
    if isinstance(item, _StartData):
        return Start()
    if isinstance(item, _StopData):
        return Stop()
    if isinstance(item, _EndData):
        return End()
    if isinstance(item, _ActionData):
        label_obj = Label(item.label) if isinstance(item.label, str) else item.label
        style_obj = validate_style_background_only(item.style, "Action")
        return Action(label=label_obj, shape=item.shape, style=style_obj)
    if isinstance(item, _ArrowData):
        label_obj = Label(item.label) if isinstance(item.label, str) else item.label
        style_obj = coerce_line_style(item.style) if item.style else None
        return Arrow(label=label_obj, pattern=item.pattern, line_style=style_obj)
    if isinstance(item, _NoteData):
        content_label = Label(item.content) if isinstance(item.content, str) else item.content
        return ActivityNote(
            content=content_label,
            position=item.position,
            floating=item.floating,
        )
    if isinstance(item, _KillData):
        return Kill()
    if isinstance(item, _DetachData):
        return Detach()
    if isinstance(item, _BreakData):
        return Break()
    if isinstance(item, _ConnectorData):
        return Connector(name=item.name)
    if isinstance(item, _GotoData):
        return Goto(label=item.label)
    if isinstance(item, _LabelData):
        return ActivityLabel(name=item.name)
    if isinstance(item, _SwimlaneData):
        return Swimlane(name=item.name, color=item.color)
    if isinstance(item, _IfData):
        return _build_if(item)
    if isinstance(item, _WhileData):
        return _build_while(item)
    if isinstance(item, _RepeatData):
        return _build_repeat(item)
    if isinstance(item, _SwitchData):
        return _build_switch(item)
    if isinstance(item, _ForkData):
        return _build_fork(item)
    if isinstance(item, _SplitData):
        return _build_split(item)
    if isinstance(item, _PartitionData):
        return _build_partition(item)
    if isinstance(item, _GroupData):
        return _build_group(item)
    raise TypeError(f"Unknown flow item type: {type(item)}")


def _build_items(items: tuple[Any, ...] | list[Any]) -> tuple[ActivityElement, ...]:
    """Convert a sequence of data objects to primitives."""
    return tuple(_build_item(i) for i in items)


def _build_if(data: _IfData) -> If:
    """Convert _IfData to If primitive.

    Non-last extra branches with string labels become elseif conditions.
    The last extra branch becomes the else (label string = arrow text, None = no label).
    """
    then_elements = _build_items(data.events)
    elseif_branches: list[ElseIfBranch] = []
    else_label: str | None = None
    else_elements: tuple[ActivityElement, ...] = ()

    if data.extra_branches:
        # Non-last branches are elseif
        for branch_label, branch_events in data.extra_branches[:-1]:
            if branch_label is not None:
                elseif_branches.append(ElseIfBranch(
                    condition=branch_label,
                    then_label=None,
                    elements=_build_items(branch_events),
                ))

        # Last branch is else
        last_label, last_events = data.extra_branches[-1]
        else_label = last_label
        else_elements = _build_items(last_events)

    return If(
        condition=data.condition,
        then_label=data.then_label,
        then_elements=then_elements,
        elseif_branches=tuple(elseif_branches),
        else_label=else_label,
        else_elements=else_elements,
    )


def _build_while(data: _WhileData) -> While:
    return While(
        condition=data.condition,
        is_label=data.is_label,
        elements=_build_items(data.events),
        endwhile_label=data.endwhile_label,
    )


def _build_repeat(data: _RepeatData) -> Repeat:
    return Repeat(
        elements=_build_items(data.events),
        condition=data.condition,
        is_label=data.is_label,
        not_label=data.not_label,
        backward_action=data.backward_action,
        start_label=data.start_label,
    )


def _build_switch(data: _SwitchData) -> Switch:
    cases = tuple(
        Case(label=label, elements=_build_items(events))
        for label, events in data.cases
    )
    return Switch(condition=data.condition, cases=cases)


def _build_fork(data: _ForkData) -> Fork:
    branches = tuple(
        _build_items(branch) for branch in data.branches
    )
    return Fork(branches=branches, end_style=data.end_style)


def _build_split(data: _SplitData) -> Split:
    branches = tuple(
        _build_items(branch) for branch in data.branches
    )
    return Split(branches=branches)


def _build_partition(data: _PartitionData) -> Partition:
    return Partition(
        name=data.name,
        elements=_build_items(data.events),
        color=data.color,
    )


def _build_group(data: _GroupData) -> Group:
    return Group(
        name=data.name,
        elements=_build_items(data.events),
    )


# ---------------------------------------------------------------------------
# Composer
# ---------------------------------------------------------------------------


class ActivityComposer:
    """Composer for activity diagrams.

    Usage:
        d = activity_diagram(title="Order Process")
        el = d.elements

        d.add(
            el.start(),
            el.action("Receive Order"),
            el.if_("Valid?", [
                el.action("Process"),
            ], "no", [
                el.action("Reject"),
            ], then_label="yes"),
            el.stop(),
        )

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
        self._elements_ns = ActivityElementNamespace()
        self._flow: list[_FlowItem] = []

    @property
    def elements(self) -> ActivityElementNamespace:
        return self._elements_ns

    def add(self, *items: _FlowItem) -> Any:
        """Register flow elements into the diagram.

        Returns what it receives: single item returns the item,
        multiple returns a tuple.
        """
        self._flow.extend(items)
        if len(items) == 1:
            return items[0]
        return items

    def build(self) -> ActivityDiagram:
        """Build the frozen ActivityDiagram primitive."""
        elements = _build_items(self._flow)
        return ActivityDiagram(
            elements=elements,
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

    Example:
        d = activity_diagram(title="Order Process")
        el = d.elements

        d.add(
            el.start(),
            el.action("Receive Order"),
            el.stop(),
        )

        print(render(d))
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
