"""State diagram builder with context manager syntax.

Provides a fluent API for constructing state diagrams:

    with state_diagram(title="My Diagram") as d:
        idle = d.state("Idle")
        running = d.state("Running")
        d.arrow(d.start(), idle)
        d.arrow(idle, running, "begin")
        d.arrow(running, d.end(), "finish")

    print(render(d.build()))
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Iterator

from ..primitives.common import Direction, Label, LineStyle, Note, NotePosition, Style
from ..primitives.state import (
    CompositeState,
    ConcurrentState,
    PseudoState,
    PseudoStateKind,
    Region,
    StateDiagram,
    StateDiagramElement,
    StateNode,
    Transition,
)

if TYPE_CHECKING:
    pass


class _BaseStateBuilder:
    """Base class for state builders with shared methods."""

    def __init__(self) -> None:
        self._elements: list[StateDiagramElement] = []

    def state(
        self,
        name: str,
        *,
        alias: str | None = None,
        description: str | Label | None = None,
        style: Style | None = None,
        note: str | Note | None = None,
        note_position: NotePosition = NotePosition.RIGHT,
    ) -> StateNode:
        """Create and register a state node.

        Args:
            name: Display name of the state
            alias: Optional short name for referencing in transitions
            description: Optional description text
            style: Optional visual styling
            note: Optional note content (string or Note)
            note_position: Position of note if note is a string

        Returns:
            The created StateNode for use in transitions
        """
        # Convert string description to Label
        desc_label = Label(description) if isinstance(description, str) else description

        # Convert string note to Note
        note_obj = (
            Note(Label(note), note_position) if isinstance(note, str) else note
        )

        node = StateNode(
            name=name,
            alias=alias,
            description=desc_label,
            style=style,
            note=note_obj,
        )
        self._elements.append(node)
        return node

    def arrow(
        self,
        source: StateNode | PseudoState | str,
        target: StateNode | PseudoState | str,
        label: str | Label | None = None,
        *,
        trigger: str | None = None,
        guard: str | None = None,
        effect: str | None = None,
        style: LineStyle | None = None,
        direction: Direction | None = None,
    ) -> Transition:
        """Create and register a transition between states.

        Args:
            source: Source state (StateNode, PseudoState, or ref string)
            target: Target state (StateNode, PseudoState, or ref string)
            label: Optional transition label
            trigger: Optional event/trigger name
            guard: Optional guard condition (without brackets)
            effect: Optional effect/action (without leading /)
            style: Optional line styling
            direction: Optional layout direction hint

        Returns:
            The created Transition
        """
        # Convert sources/targets to reference strings
        src_ref = self._to_ref(source)
        tgt_ref = self._to_ref(target)

        # Convert string label to Label
        label_obj = Label(label) if isinstance(label, str) else label

        trans = Transition(
            source=src_ref,
            target=tgt_ref,
            label=label_obj,
            trigger=trigger,
            guard=guard,
            effect=effect,
            style=style,
            direction=direction,
        )
        self._elements.append(trans)
        return trans

    def choice(self, name: str, *, style: Style | None = None) -> PseudoState:
        """Create and register a choice pseudo-state (diamond)."""
        pseudo = PseudoState(kind=PseudoStateKind.CHOICE, name=name, style=style)
        self._elements.append(pseudo)
        return pseudo

    def fork(self, name: str, *, style: Style | None = None) -> PseudoState:
        """Create and register a fork pseudo-state (horizontal bar)."""
        pseudo = PseudoState(kind=PseudoStateKind.FORK, name=name, style=style)
        self._elements.append(pseudo)
        return pseudo

    def join(self, name: str, *, style: Style | None = None) -> PseudoState:
        """Create and register a join pseudo-state (horizontal bar)."""
        pseudo = PseudoState(kind=PseudoStateKind.JOIN, name=name, style=style)
        self._elements.append(pseudo)
        return pseudo

    def note(
        self,
        content: str | Label,
        position: NotePosition = NotePosition.RIGHT,
    ) -> Note:
        """Create and register a floating note."""
        content_label = Label(content) if isinstance(content, str) else content
        note_obj = Note(content=content_label, position=position)
        self._elements.append(note_obj)
        return note_obj

    def start(self) -> str:
        """Return the initial pseudo-state reference for use as arrow source."""
        return "initial"

    def end(self) -> str:
        """Return the final pseudo-state reference for use as arrow target."""
        return "final"

    def history(self) -> str:
        """Return the history pseudo-state reference."""
        return "history"

    def deep_history(self) -> str:
        """Return the deep history pseudo-state reference."""
        return "deep_history"

    @contextmanager
    def composite(
        self,
        name: str,
        *,
        alias: str | None = None,
        style: Style | None = None,
        note: str | Note | None = None,
        note_position: NotePosition = NotePosition.RIGHT,
    ) -> Iterator[_CompositeBuilder]:
        """Create a composite state with nested elements.

        Usage:
            with d.composite("Active") as active:
                sub = active.state("SubState")
                active.arrow(active.start(), sub)

        Args:
            name: Display name of the composite state
            alias: Optional short name for referencing
            style: Optional visual styling
            note: Optional note content
            note_position: Position of note if note is a string

        Yields:
            A CompositeBuilder for adding nested elements
        """
        builder = _CompositeBuilder(name, alias, style, note, note_position)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def concurrent(
        self,
        name: str,
        *,
        alias: str | None = None,
        style: Style | None = None,
        note: str | Note | None = None,
        note_position: NotePosition = NotePosition.RIGHT,
    ) -> Iterator[_ConcurrentBuilder]:
        """Create a concurrent state with parallel regions.

        Usage:
            with d.concurrent("Parallel") as par:
                with par.region() as r1:
                    r1.state("A")
                with par.region() as r2:
                    r2.state("B")

        Args:
            name: Display name of the concurrent state
            alias: Optional short name for referencing
            style: Optional visual styling
            note: Optional note content
            note_position: Position of note if note is a string

        Yields:
            A ConcurrentBuilder for adding parallel regions
        """
        builder = _ConcurrentBuilder(name, alias, style, note, note_position)
        yield builder
        self._elements.append(builder._build())

    def _to_ref(self, state: StateNode | PseudoState | CompositeState | str) -> str:
        """Convert a state to its reference string."""
        if isinstance(state, str):
            return state
        if isinstance(state, StateNode):
            return state.ref
        if isinstance(state, CompositeState):
            return state.ref
        if isinstance(state, PseudoState):
            if state.name:
                return state.name
            return state.kind.value
        return str(state)


class _CompositeBuilder(_BaseStateBuilder):
    """Builder for composite states with nested elements."""

    def __init__(
        self,
        name: str,
        alias: str | None,
        style: Style | None,
        note: str | Note | None,
        note_position: NotePosition,
    ) -> None:
        super().__init__()
        self._name = name
        self._alias = alias
        self._style = style
        self._note = note
        self._note_position = note_position

    @property
    def ref(self) -> str:
        """Reference name for use in transitions."""
        if self._alias:
            return self._alias
        return self._name.replace(" ", "_")

    def _build(self) -> CompositeState:
        """Build the composite state primitive."""
        note_obj = (
            Note(Label(self._note), self._note_position)
            if isinstance(self._note, str)
            else self._note
        )
        return CompositeState(
            name=self._name,
            alias=self._alias,
            elements=tuple(self._elements),
            style=self._style,
            note=note_obj,
        )


class _ConcurrentBuilder:
    """Builder for concurrent states with parallel regions."""

    def __init__(
        self,
        name: str,
        alias: str | None,
        style: Style | None,
        note: str | Note | None,
        note_position: NotePosition,
    ) -> None:
        self._name = name
        self._alias = alias
        self._style = style
        self._note = note
        self._note_position = note_position
        self._regions: list[Region] = []

    @property
    def ref(self) -> str:
        """Reference name for use in transitions."""
        if self._alias:
            return self._alias
        return self._name.replace(" ", "_")

    @contextmanager
    def region(self) -> Iterator[_RegionBuilder]:
        """Create a new parallel region.

        Usage:
            with par.region() as r:
                r.state("StateA")
                r.arrow(r.start(), "StateA")
        """
        builder = _RegionBuilder()
        yield builder
        self._regions.append(builder._build())

    def _build(self) -> ConcurrentState:
        """Build the concurrent state primitive."""
        note_obj = (
            Note(Label(self._note), self._note_position)
            if isinstance(self._note, str)
            else self._note
        )
        return ConcurrentState(
            name=self._name,
            alias=self._alias,
            regions=tuple(self._regions),
            style=self._style,
            note=note_obj,
        )


class _RegionBuilder(_BaseStateBuilder):
    """Builder for a single region within a concurrent state."""

    def _build(self) -> Region:
        """Build the region primitive."""
        return Region(elements=tuple(self._elements))


class StateDiagramBuilder(_BaseStateBuilder):
    """Builder for complete state diagrams.

    Usage:
        with state_diagram(title="My State Machine") as d:
            idle = d.state("Idle")
            active = d.state("Active")
            d.arrow(d.start(), idle)
            d.arrow(idle, active, "activate")
            d.arrow(active, d.end(), "done")

        diagram = d.build()
        print(render(diagram))
    """

    def __init__(
        self,
        *,
        title: str | None = None,
        hide_empty_description: bool = False,
    ) -> None:
        super().__init__()
        self._title = title
        self._hide_empty_description = hide_empty_description

    def build(self) -> StateDiagram:
        """Build the complete state diagram."""
        return StateDiagram(
            elements=tuple(self._elements),
            title=self._title,
            hide_empty_description=self._hide_empty_description,
        )


@contextmanager
def state_diagram(
    *,
    title: str | None = None,
    hide_empty_description: bool = False,
) -> Iterator[StateDiagramBuilder]:
    """Create a state diagram with context manager syntax.

    Usage:
        with state_diagram(title="Traffic Light") as d:
            red = d.state("Red")
            yellow = d.state("Yellow")
            green = d.state("Green")

            d.arrow(d.start(), red)
            d.arrow(red, green, "timer")
            d.arrow(green, yellow, "timer")
            d.arrow(yellow, red, "timer")

        print(render(d.build()))

    Args:
        title: Optional diagram title
        hide_empty_description: Whether to hide empty state descriptions

    Yields:
        A StateDiagramBuilder for adding diagram elements
    """
    builder = StateDiagramBuilder(
        title=title,
        hide_empty_description=hide_empty_description,
    )
    yield builder
