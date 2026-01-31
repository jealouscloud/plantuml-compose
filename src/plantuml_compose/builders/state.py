"""State diagram builder with context manager syntax.

When to Use
-----------
State diagrams show how ONE entity changes over time. Use when:

- Modeling object lifecycles (Order: pending -> paid -> shipped)
- Showing workflow stages (Document: draft -> review -> published)
- Visualizing UI states (Button: idle -> hover -> pressed -> disabled)
- Protocol states (Connection: disconnected -> connecting -> connected)

NOT for:
- Multiple entities interacting (use sequence diagram)
- System architecture (use component/deployment diagram)
- Code structure (use class diagram)
- User workflows with decisions (use activity diagram)

Key Concepts
------------
State:      A condition during an entity's life ("Logged In", "Processing")
Transition: Movement between states, triggered by events
Guard:      Condition that must be true for transition [if authorized]
Effect:     Action performed during transition / doSomething()

Composite:  A state containing sub-states (nested state machine):

            ┌─────────────────────────────┐
            │ Active                      │
            │  ┌─────┐      ┌─────────┐   │
            │  │Idle │ ───► │ Working │   │
            │  └─────┘      └─────────┘   │
            └─────────────────────────────┘

Fork/Join:  Split into parallel paths, then synchronize:

                     │
                 ────┴────   <- fork
                 │   │   │
                 ▼   ▼   ▼
                [A] [B] [C]   (all execute concurrently)
                 │   │   │
                 ────┬────   <- join (waits for all)
                     │

Example
-------
    with state_diagram(title="Order Lifecycle") as d:
        pending = d.state("Pending")
        paid = d.state("Paid")
        shipped = d.state("Shipped")

        d.arrow(d.start(), pending)
        d.arrow(pending, paid, label="payment received")
        d.arrow(paid, shipped, label="dispatched")
        d.arrow(shipped, d.end())

    print(render(d.build()))
"""

from __future__ import annotations

import uuid
from contextlib import contextmanager
from typing import Iterator

from ..primitives.common import (
    Direction,
    Footer,
    Header,
    Label,
    LayoutDirection,
    LayoutEngine,
    Legend,
    LineStyleLike,
    LineType,
    Note,
    NotePosition,
    RegionSeparator,
    Scale,
    StateDiagramStyleLike,
    Style,
    StyleLike,
    coerce_direction,
    coerce_line_style,
    coerce_state_diagram_style,
    coerce_style,
)
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
from ..primitives.common import sanitize_ref


class _BaseStateBuilder:
    """Base class for state builders with shared methods."""

    def __init__(self) -> None:
        self._elements: list[StateDiagramElement] = []
        self._refs: set[str] = set()  # Track valid element references

    def _register_ref(
        self, element: StateNode | CompositeState | ConcurrentState
    ) -> None:
        """Register an element's reference for validation.

        Raises:
            ValueError: If the ref already exists (collision from different names)
        """
        ref = element._ref
        if ref in self._refs:
            raise ValueError(
                f'Reference "{ref}" already exists. '
                f'State "{element.name}" produces the same ref as another state. '
                f"Use an alias to disambiguate."
            )
        self._refs.add(ref)
        if hasattr(element, "alias") and element.alias:
            self._refs.add(element.alias)

    def _validate_ref(self, ref: str, param_name: str) -> None:
        """Validate that a string reference exists in the diagram.

        Args:
            ref: The reference string to validate
            param_name: Parameter name for error message

        Raises:
            ValueError: If ref is not found in registered elements
        """
        # Special pseudo-state refs are always valid
        if ref in ("[*]", "[H]", "[H*]"):
            return
        if ref not in self._refs:
            available = sorted(self._refs) if self._refs else ["(none)"]
            raise ValueError(
                f'{param_name} "{ref}" not found. Available: {", ".join(available)}'
            )

    def state(
        self,
        name: str,
        *,
        alias: str | None = None,
        description: str | Label | None = None,
        style: StyleLike | None = None,
        note: str | Note | None = None,
        note_position: NotePosition = "right",
    ) -> StateNode:
        """Create and register a state node.

        Args:
            name: Display name of the state
            alias: Optional short name for referencing in transitions
            description: Optional description text
            style: Optional visual styling (Style object or dict)
            note: Optional note content (string or Note)
            note_position: Position of note if note is a string (e.g., "left", "right")

        Returns:
            The created StateNode for use in transitions

        Raises:
            ValueError: If name is empty (PlantUML rejects empty state names)

        Example:
            idle = d.state("Idle")
            active = d.state("Active", style={"background": "#E3F2FD"})
            d.arrow(idle, active, label="start")
        """
        if not name:
            raise ValueError("State name cannot be empty")

        # Convert string description to Label
        desc_label = (
            Label(description) if isinstance(description, str) else description
        )

        # Convert string note to Note
        note_obj = (
            Note(Label(note), note_position) if isinstance(note, str) else note
        )

        # Coerce style dict to Style object
        style_obj = coerce_style(style)

        node = StateNode(
            name=name,
            alias=alias,
            description=desc_label,
            style=style_obj,
            note=note_obj,
        )
        self._elements.append(node)
        self._register_ref(node)
        return node

    def states(
        self,
        *names: str,
        style: StyleLike | None = None,
    ) -> tuple[StateNode, ...]:
        """Create and register multiple state nodes at once.

        Args:
            *names: Display names of the states
            style: Optional visual styling applied to all states

        Returns:
            Tuple of created StateNodes in order

        Example:
            fraud, balance, credit = d.states("FraudCheck", "BalanceCheck", "CreditCheck")
        """
        return tuple(self.state(name, style=style) for name in names)

    def arrow(
        self,
        *states: StateNode
        | PseudoState
        | CompositeState
        | "_CompositeBuilder"
        | "_ConcurrentBuilder"
        | str,
        label: str | Label | None = None,
        trigger: str | None = None,
        guard: str | None = None,
        effect: str | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | Label | None = None,
    ) -> list[Transition]:
        """Create and register transitions between consecutive states.

        Args:
            *states: Two or more states to connect (StateNode, PseudoState, builder, or ref string).
                     Creates transitions: states[0]->states[1], states[1]->states[2], etc.
            label: Optional transition label (applied to all transitions)
            trigger: Optional event/trigger name (applied to all transitions)
            guard: Optional guard condition without brackets (applied to all transitions)
            effect: Optional effect/action without leading / (applied to all transitions)
            style: Optional line styling (LineStyle object or dict)
            direction: Optional layout direction hint ("up", "down", "left", "right")
            note: Optional note attached to transitions (applied to all transitions)

        Returns:
            List of created Transitions

        Examples:
            d.arrow(a, b)           # Single transition: a -> b
            d.arrow(a, b, c)        # Chain: a -> b -> c (2 transitions)
            d.arrow(a, b, c, d)     # Chain: a -> b -> c -> d (3 transitions)
            d.arrow(a, b, label="go")  # All transitions labeled "go"
        """
        if len(states) < 2:
            raise ValueError("arrow() requires at least 2 states")

        # Detect common mistake: bare string intended as label
        # First two args can be strings (state references), but 3rd+ should be state objects
        for i, state in enumerate(states):
            if (
                i >= 2
                and isinstance(state, str)
                and state not in self._STATE_REF_STRINGS
            ):
                raise ValueError(
                    f"Unexpected string '{state}' at position {i + 1} in arrow().\n\n"
                    f"If this is a label, use the label parameter:\n"
                    f'    d.arrow(a, b, label="{state}")\n\n'
                    f"If this is a state to chain through, create a state object first:\n"
                    f'    c = d.state("{state}")\n'
                    f"    d.arrow(a, b, c)"
                )

        # Validate string refs (only first two positions allow string refs)
        for i, state in enumerate(states[:2]):
            if isinstance(state, str) and state not in self._STATE_REF_STRINGS:
                self._validate_ref(state, f"state[{i}]")

        # Convert string label to Label
        label_obj = Label(label) if isinstance(label, str) else label

        # Convert string note to Label
        note_obj = Label(note) if isinstance(note, str) else note

        # Coerce style dict to LineStyle object
        style_obj = coerce_line_style(style) if style is not None else None

        # Coerce direction (supports shortcuts: u/d/l/r)
        direction_val = coerce_direction(direction)

        transitions: list[Transition] = []
        for source, target in zip(states[:-1], states[1:]):
            trans = Transition(
                source=self._to_ref(source),
                target=self._to_ref(target),
                label=label_obj,
                trigger=trigger,
                guard=guard,
                effect=effect,
                style=style_obj,
                direction=direction_val,
                note=note_obj,
            )
            self._elements.append(trans)
            transitions.append(trans)

        return transitions

    # Special string values that are state references, not labels
    _STATE_REF_STRINGS = frozenset(
        {"initial", "final", "history", "deep_history", "[*]", "[H]", "[H*]"}
    )

    def _is_state_ref(self, item: object) -> bool:
        """Check if item is a state reference (not a label)."""
        if isinstance(item, (StateNode, PseudoState, CompositeState)):
            return True
        if hasattr(item, "_ref"):  # Builders
            return True
        if isinstance(item, str) and item in self._STATE_REF_STRINGS:
            return True
        return False

    def flow(
        self,
        *items: StateNode
        | PseudoState
        | CompositeState
        | "_CompositeBuilder"
        | "_ConcurrentBuilder"
        | str,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
    ) -> list[Transition]:
        """Create transitions with interleaved labels.

        A more ergonomic way to define a sequence of states with labels.
        States are objects (StateNode, PseudoState, builders), labels are strings.
        Special strings like "initial", "final", "history", "deep_history" are treated as states.

        Args:
            *items: Alternating states and labels. States are required between labels.
                    Labels between states become transition labels.
            style: Optional line styling applied to all transitions
            direction: Optional layout direction hint ("up", "down", "left", "right")

        Returns:
            List of created Transitions

        Examples:
            # Simple chain with labels
            d.flow(idle, "start", running, "stop", stopped)
            # Creates: idle --start--> running --stop--> stopped

            # Can omit labels for unlabeled transitions
            d.flow(a, b, c)  # Same as d.arrow(a, b, c)

            # Mix labeled and unlabeled
            d.flow(a, "go", b, c, "end", d)
            # Creates: a --go--> b --> c --end--> d

            # Works with start/end
            d.flow(d.start(), a, "go", b, d.end())

        Raises:
            ValueError: If items doesn't start with a state or has consecutive labels
        """
        if not items:
            raise ValueError("flow() requires at least 2 states")

        # Coerce style dict to LineStyle object
        style_obj = coerce_line_style(style) if style is not None else None

        # Coerce direction (supports shortcuts: u/d/l/r)
        direction_val = coerce_direction(direction)

        # Parse items into (source, label, target) tuples
        transitions: list[Transition] = []
        i = 0
        current_state = None

        while i < len(items):
            item = items[i]

            if self._is_state_ref(item):
                # This is a state
                if current_state is not None:
                    # Create unlabeled transition from previous state
                    trans = Transition(
                        source=self._to_ref(current_state),
                        target=self._to_ref(item),
                        style=style_obj,
                        direction=direction_val,
                    )
                    self._elements.append(trans)
                    transitions.append(trans)
                current_state = item
                i += 1
            elif isinstance(item, str):
                # This is a label - must have a current state and next item must be a state
                if current_state is None:
                    raise ValueError(
                        "flow() must start with a state, not a label"
                    )
                if i + 1 >= len(items):
                    raise ValueError("flow() cannot end with a label")
                next_item = items[i + 1]
                if isinstance(next_item, str) and not self._is_state_ref(
                    next_item
                ):
                    raise ValueError("flow() cannot have consecutive labels")

                # Create transition with label
                trans = Transition(
                    source=self._to_ref(current_state),
                    target=self._to_ref(next_item),
                    label=Label(item),
                    style=style_obj,
                    direction=direction_val,
                )
                self._elements.append(trans)
                transitions.append(trans)
                current_state = next_item
                i += 2  # Skip both label and next state
            else:
                raise ValueError(
                    f"flow() received unexpected item type: {type(item)}"
                )

        if len(transitions) == 0:
            raise ValueError("flow() requires at least 2 states")

        return transitions

    def choice(self, name: str) -> PseudoState:
        """Create and register a choice pseudo-state (diamond).

        Args:
            name: Identifier for the choice point (used in arrow references)

        Note: PlantUML does not support styling choice diamonds - they always render gray.

        Example:
            check = d.choice("valid?")
            d.arrow(processing, check)
            d.arrow(check, success, label="yes")
            d.arrow(check, failure, label="no")
        """
        pseudo = PseudoState(kind=PseudoStateKind.CHOICE, name=name)
        self._elements.append(pseudo)
        return pseudo

    def fork(self, name: str) -> PseudoState:
        """Create and register a fork pseudo-state (horizontal bar).

        Args:
            name: Identifier for the fork bar (used in arrow references)

        Note: PlantUML does not support styling fork bars - they always render gray.

        Example:
            f = d.fork("split")
            d.arrow(start_state, f)
            d.arrow(f, branch_a)
            d.arrow(f, branch_b)
        """
        pseudo = PseudoState(kind=PseudoStateKind.FORK, name=name)
        self._elements.append(pseudo)
        return pseudo

    def join(self, name: str) -> PseudoState:
        """Create and register a join pseudo-state (horizontal bar).

        Args:
            name: Identifier for the join bar (used in arrow references)

        Note: PlantUML does not support styling join bars - they always render gray.

        Example:
            j = d.join("sync")
            d.arrow(branch_a, j)
            d.arrow(branch_b, j)
            d.arrow(j, next_state)
        """
        pseudo = PseudoState(kind=PseudoStateKind.JOIN, name=name)
        self._elements.append(pseudo)
        return pseudo

    def sdl_receive(self, name: str) -> PseudoState:
        """Create and register an SDL receive pseudo-state (concave polygon).

        Args:
            name: Identifier for the receive state (used in arrow references)

        Example:
            recv = d.sdl_receive("WaitingForMessage")
        """
        pseudo = PseudoState(kind=PseudoStateKind.SDL_RECEIVE, name=name)
        self._elements.append(pseudo)
        self._refs.add(sanitize_ref(name))
        return pseudo

    def note(
        self,
        content: str | Label,
        position: NotePosition = "right",
    ) -> Note:
        """Create and register a floating note.

        Raises:
            ValueError: If content is empty (PlantUML rejects empty notes)

        Example:
            d.note("Waiting for user input", position="left")
        """
        text = content.text if isinstance(content, Label) else content
        if not text:
            raise ValueError("Note content cannot be empty")

        content_label = Label(content) if isinstance(content, str) else content
        note_obj = Note(content=content_label, position=position)
        self._elements.append(note_obj)
        return note_obj

    def start(self) -> str:
        """Return the initial pseudo-state reference for use as arrow source.

        Example:
            d.arrow(d.start(), idle)
        """
        return "initial"

    def end(self) -> str:
        """Return the final pseudo-state reference for use as arrow target.

        Example:
            d.arrow(completed, d.end())
        """
        return "final"

    def history(self) -> str:
        """Return the history pseudo-state reference.

        Example:
            d.arrow(d.history(), last_state)
        """
        return "history"

    def deep_history(self) -> str:
        """Return the deep history pseudo-state reference.

        Example:
            d.arrow(d.deep_history(), nested_state)
        """
        return "deep_history"

    @contextmanager
    def composite(
        self,
        name: str,
        *,
        alias: str | None = None,
        style: StyleLike | None = None,
        note: str | Note | None = None,
        note_position: NotePosition = "right",
    ) -> Iterator[_CompositeBuilder]:
        """Create a composite state with nested elements.

        Usage:
            with d.composite("Active") as active:
                sub = active.state("SubState")
                active.arrow(active.start(), sub)

        Args:
            name: Display name of the composite state
            alias: Optional short name for referencing
            style: Optional visual styling (Style object or dict)
            note: Optional note content
            note_position: Position of note if note is a string (e.g., "left", "right")

        Yields:
            A CompositeBuilder for adding nested elements
        """
        # Coerce style dict to Style object
        style_obj = coerce_style(style)
        builder = _CompositeBuilder(name, alias, style_obj, note, note_position)
        yield builder
        comp = builder._build()
        self._elements.append(comp)
        self._register_ref(comp)
        self._refs.update(builder._refs)

    @contextmanager
    def concurrent(
        self,
        name: str,
        *,
        alias: str | None = None,
        style: StyleLike | None = None,
        note: str | Note | None = None,
        note_position: NotePosition = "right",
        separator: RegionSeparator = "horizontal",
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
            style: Optional visual styling (Style object or dict)
            note: Optional note content
            note_position: Position of note if note is a string (e.g., "left", "right")
            separator: Region separator style ("--" for horizontal, "||" for vertical)

        Yields:
            A ConcurrentBuilder for adding parallel regions
        """
        # Coerce style dict to Style object
        style_obj = coerce_style(style)
        builder = _ConcurrentBuilder(
            name, alias, style_obj, note, note_position, separator
        )
        yield builder
        conc = builder._build()
        self._elements.append(conc)
        self._register_ref(conc)
        self._refs.update(builder._refs)

    @contextmanager
    def parallel(
        self,
        name: str | None = None,
    ) -> Iterator["_ParallelBuilder"]:
        """Create a fork/join parallel structure with branches.

        Automatically creates a fork pseudo-state, connects each branch's entry
        state from the fork, connects each branch's exit state to the join, and
        creates the join pseudo-state.

        Usage:
            with d.parallel("Payment") as p:
                with p.branch() as b1:
                    fraud = b1.state("FraudCheck")
                with p.branch() as b2:
                    balance = b2.state("BalanceCheck")
                    hold = b2.state("Hold")
                    b2.arrow(balance, hold)

            d.arrow(validate, p.fork)
            d.arrow(p.join, next_state)

        Args:
            name: Optional name prefix for fork/join (creates "{name}_fork" and "{name}_join")

        Yields:
            A ParallelBuilder for adding branches
        """
        builder = _ParallelBuilder(name)
        yield builder
        elements = builder._build()
        self._elements.extend(elements)

    def _to_ref(
        self,
        state: StateNode
        | PseudoState
        | CompositeState
        | "_CompositeBuilder"
        | "_ConcurrentBuilder"
        | str,
    ) -> str:
        """Convert a state to its reference string.

        Automatically resolves references, so users can pass builders directly:
            d.arrow(composite_builder, other_state)
        """
        if isinstance(state, str):
            return state
        if isinstance(state, StateNode):
            return state._ref
        if isinstance(state, CompositeState):
            return state._ref
        if isinstance(state, PseudoState):
            if state.name:
                return sanitize_ref(state.name)
            return state.kind.value
        # Handle builder types with ._ref property (e.g., _CompositeBuilder, _ConcurrentBuilder)
        if hasattr(state, "_ref"):
            ref = getattr(state, "_ref")
            if isinstance(ref, str):
                return ref
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
    def _ref(self) -> str:
        """Internal: Reference name for use in transitions."""
        if self._alias:
            return self._alias
        return sanitize_ref(self._name)

    # Boundary pseudo-states: these stereotypes only work inside composite states.
    # PlantUML crashes with IndexOutOfBoundsException if used at top level.

    def entry_point(self, name: str) -> PseudoState:
        """Create an entry point pseudo-state (small circle on boundary).

        Example:
            entry = active.entry_point("in")
        """
        pseudo = PseudoState(kind=PseudoStateKind.ENTRY_POINT, name=name)
        self._elements.append(pseudo)
        self._refs.add(sanitize_ref(name))
        return pseudo

    def exit_point(self, name: str) -> PseudoState:
        """Create an exit point pseudo-state (circle with X on boundary).

        Example:
            exit = active.exit_point("out")
        """
        pseudo = PseudoState(kind=PseudoStateKind.EXIT_POINT, name=name)
        self._elements.append(pseudo)
        self._refs.add(sanitize_ref(name))
        return pseudo

    def input_pin(self, name: str) -> PseudoState:
        """Create an input pin pseudo-state (small square on boundary).

        Example:
            pin = active.input_pin("data_in")
        """
        pseudo = PseudoState(kind=PseudoStateKind.INPUT_PIN, name=name)
        self._elements.append(pseudo)
        self._refs.add(sanitize_ref(name))
        return pseudo

    def output_pin(self, name: str) -> PseudoState:
        """Create an output pin pseudo-state (small square on boundary).

        Example:
            pin = active.output_pin("result_out")
        """
        pseudo = PseudoState(kind=PseudoStateKind.OUTPUT_PIN, name=name)
        self._elements.append(pseudo)
        self._refs.add(sanitize_ref(name))
        return pseudo

    def expansion_input(self, name: str) -> PseudoState:
        """Create an expansion input pseudo-state.

        Example:
            exp_in = active.expansion_input("batch_in")
        """
        pseudo = PseudoState(kind=PseudoStateKind.EXPANSION_INPUT, name=name)
        self._elements.append(pseudo)
        self._refs.add(sanitize_ref(name))
        return pseudo

    def expansion_output(self, name: str) -> PseudoState:
        """Create an expansion output pseudo-state.

        Example:
            exp_out = active.expansion_output("batch_out")
        """
        pseudo = PseudoState(kind=PseudoStateKind.EXPANSION_OUTPUT, name=name)
        self._elements.append(pseudo)
        self._refs.add(sanitize_ref(name))
        return pseudo

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
        separator: RegionSeparator,
    ) -> None:
        self._name = name
        self._alias = alias
        self._style = style
        self._note = note
        self._note_position = note_position
        self._separator = separator
        self._regions: list[Region] = []
        self._refs: set[str] = set()  # Track valid element references

    @property
    def _ref(self) -> str:
        """Internal: Reference name for use in transitions."""
        if self._alias:
            return self._alias
        return sanitize_ref(self._name)

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
        self._refs.update(builder._refs)

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
            separator=self._separator,
        )


class _RegionBuilder(_BaseStateBuilder):
    """Builder for a single region within a concurrent state."""

    def _build(self) -> Region:
        """Build the region primitive."""
        return Region(elements=tuple(self._elements))


class _BranchBuilder(_BaseStateBuilder):
    """Builder for a single branch within a parallel structure.

    Inherits from _BaseStateBuilder for full capabilities (state creation,
    transitions, etc.) within each branch.
    """

    def _analyze(self) -> tuple[str, str, list[StateDiagramElement]]:
        """Analyze branch to find entry and exit points.

        Returns:
            Tuple of (entry_ref, exit_ref, elements)

        The entry point is the first state-like element created.
        The exit point is the state with no outgoing transitions within this branch.
        """
        # Find all state-like elements (StateNode, CompositeState, ConcurrentState)
        # These are elements that can serve as entry/exit points for the branch
        state_likes = [
            e
            for e in self._elements
            if isinstance(e, (StateNode, CompositeState, ConcurrentState))
        ]
        if not state_likes:
            raise ValueError("Branch must have at least one state")

        # Entry: first state-like element created
        entry = state_likes[0]._ref

        # Exit: state with no outgoing transition within this branch
        transitions = [e for e in self._elements if isinstance(e, Transition)]
        sources = {t.source for t in transitions}
        exits = [s for s in state_likes if s._ref not in sources]

        if not exits:
            # All states have outgoing transitions - use last state as exit
            exit_ref = state_likes[-1]._ref
        elif len(exits) == 1:
            exit_ref = exits[0]._ref
        else:
            # Multiple exits - error for now
            exit_names = [s._ref for s in exits]
            raise ValueError(
                f"Branch has {len(exits)} exit states (states with no outgoing transition). "
                f"Expected exactly one. Exits: {exit_names}"
            )

        return entry, exit_ref, list(self._elements)


class _ParallelBuilder:
    """Builder for fork/join parallel execution.

    Composition-based like _ConcurrentBuilder - does not inherit from _BaseStateBuilder
    because it manages branches rather than accumulating elements directly.

    Usage:
        with d.parallel("Payment") as p:
            with p.branch() as b1:
                fraud = b1.state("FraudCheck")
            with p.branch() as b2:
                balance = b2.state("BalanceCheck")

        d.arrow(validate, p.fork)
        d.arrow(p.join, next_state)
    """

    def __init__(self, name: str | None = None) -> None:
        self._name = name
        # Use UUID for unnamed parallel blocks to ensure uniqueness and thread-safety
        self._generated_id = uuid.uuid4().hex[:8] if name is None else None
        self._branches: list[_BranchBuilder] = []
        self._fork: PseudoState | None = None
        self._join: PseudoState | None = None
        self._built = False
        self._refs: set[str] = set()  # Track valid element references

    def _fork_name(self) -> str:
        """Get the fork pseudo-state name."""
        if self._name:
            return f"{self._name}_fork"
        return f"parallel_{self._generated_id}_fork"

    def _join_name(self) -> str:
        """Get the join pseudo-state name."""
        if self._name:
            return f"{self._name}_join"
        return f"parallel_{self._generated_id}_join"

    @property
    def _ref(self) -> str:
        """Internal: Reference name for use in transitions (uses fork name)."""
        return self._fork_name()

    @property
    def fork(self) -> PseudoState:
        """The fork pseudo-state. Only accessible after parallel block exits."""
        if not self._built:
            raise RuntimeError(
                "Cannot access .fork before parallel block exits"
            )
        if self._fork is None:
            raise RuntimeError("Fork was not created")
        return self._fork

    @property
    def join(self) -> PseudoState:
        """The join pseudo-state. Only accessible after parallel block exits."""
        if not self._built:
            raise RuntimeError(
                "Cannot access .join before parallel block exits"
            )
        if self._join is None:
            raise RuntimeError("Join was not created")
        return self._join

    @contextmanager
    def branch(self) -> Iterator[_BranchBuilder]:
        """Create a branch within this parallel structure.

        Each branch can contain states and transitions. The first state
        becomes the entry point (connected from fork), and the state with
        no outgoing transitions becomes the exit point (connected to join).

        Usage:
            with p.branch() as b:
                a = b.state("A")
                b_state = b.state("B")
                b.arrow(a, b_state)  # B has no outgoing, becomes exit
        """
        b = _BranchBuilder()
        yield b
        if not b._elements:
            raise ValueError("Branch must have at least one element")
        self._branches.append(b)
        self._refs.update(b._refs)

    def _build(self) -> list[StateDiagramElement]:
        """Build all elements: fork, transitions to branches, branch contents, transitions to join, join.

        Returns:
            List of all elements to add to the parent builder
        """
        if not self._branches:
            raise ValueError("parallel() must have at least one branch")

        fork_name = self._fork_name()
        join_name = self._join_name()

        self._fork = PseudoState(kind=PseudoStateKind.FORK, name=fork_name)
        self._join = PseudoState(kind=PseudoStateKind.JOIN, name=join_name)
        self._built = True
        # Register fork/join refs for validation
        self._refs.add(fork_name)
        self._refs.add(join_name)

        elements: list[StateDiagramElement] = [self._fork]

        for branch in self._branches:
            entry, exit_ref, branch_elements = branch._analyze()

            # Fork → entry
            elements.append(
                Transition(
                    source=fork_name,
                    target=entry,
                )
            )

            # Branch contents
            elements.extend(branch_elements)

            # Exit → join
            elements.append(
                Transition(
                    source=exit_ref,
                    target=join_name,
                )
            )

        elements.append(self._join)
        return elements


class StateDiagramBuilder(_BaseStateBuilder):
    """Builder for complete state diagrams.

    Usage:
        with state_diagram(title="My State Machine") as d:
            idle = d.state("Idle")
            active = d.state("Active")
            d.arrow(d.start(), idle)
            d.arrow(idle, active, label="activate")
            d.arrow(active, d.end(), label="done")

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
        theme: str | None = None,
        layout: LayoutDirection | None = None,
        layout_engine: LayoutEngine | None = None,
        linetype: LineType | None = None,
        hide_empty_description: bool = False,
        diagram_style: StateDiagramStyleLike | None = None,
    ) -> None:
        super().__init__()
        self._title = title
        self._caption = caption
        # Coerce string to Header/Footer/Legend objects
        self._header = Header(header) if isinstance(header, str) else header
        self._footer = Footer(footer) if isinstance(footer, str) else footer
        self._legend = Legend(legend) if isinstance(legend, str) else legend
        self._scale = (
            Scale(factor=scale) if isinstance(scale, (int, float)) else scale
        )
        self._theme = theme
        self._layout = layout
        self._layout_engine = layout_engine
        self._linetype = linetype
        self._hide_empty_description = hide_empty_description
        # Coerce diagram_style dict to StateDiagramStyle object
        self._diagram_style = (
            coerce_state_diagram_style(diagram_style) if diagram_style is not None else None
        )
        # Track block context for detecting d.state() inside blocks
        self._block_stack: list[str] = []

    def _check_not_in_block(self, method_name: str) -> None:
        """Raise error if called inside a block context."""
        if self._block_stack:
            block_type = self._block_stack[-1]
            # Clean variable name for consistency (no trailing underscore issues in state,
            # but matches pattern in activity and sequence builders)
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
    def state(
        self,
        name: str,
        *,
        alias: str | None = None,
        description: str | Label | None = None,
        style: StyleLike | None = None,
        note: str | Note | None = None,
        note_position: NotePosition = "right",
    ) -> StateNode:
        """Create and register a state node.

        Raises:
            RuntimeError: If called inside a block context (composite, concurrent, etc.)
        """
        self._check_not_in_block("state")
        return super().state(
            name,
            alias=alias,
            description=description,
            style=style,
            note=note,
            note_position=note_position,
        )

    def states(
        self,
        *names: str,
        style: StyleLike | None = None,
    ) -> tuple[StateNode, ...]:
        """Create and register multiple state nodes at once.

        Raises:
            RuntimeError: If called inside a block context
        """
        self._check_not_in_block("states")
        return super().states(*names, style=style)

    def choice(self, name: str) -> PseudoState:
        """Create and register a choice pseudo-state (diamond).

        Raises:
            RuntimeError: If called inside a block context
        """
        self._check_not_in_block("choice")
        return super().choice(name)

    def fork(self, name: str) -> PseudoState:
        """Create and register a fork pseudo-state (horizontal bar).

        Raises:
            RuntimeError: If called inside a block context
        """
        self._check_not_in_block("fork")
        return super().fork(name)

    def join(self, name: str) -> PseudoState:
        """Create and register a join pseudo-state (horizontal bar).

        Raises:
            RuntimeError: If called inside a block context
        """
        self._check_not_in_block("join")
        return super().join(name)

    def sdl_receive(self, name: str) -> PseudoState:
        """Create and register an SDL receive pseudo-state (concave polygon).

        Raises:
            RuntimeError: If called inside a block context
        """
        self._check_not_in_block("sdl_receive")
        return super().sdl_receive(name)

    def note(
        self,
        content: str | Label,
        position: NotePosition = "right",
    ) -> Note:
        """Create and register a floating note.

        Raises:
            RuntimeError: If called inside a block context
        """
        self._check_not_in_block("note")
        return super().note(content, position)

    # Override block context managers to track block stack
    @contextmanager
    def composite(
        self,
        name: str,
        *,
        alias: str | None = None,
        style: StyleLike | None = None,
        note: str | Note | None = None,
        note_position: NotePosition = "right",
    ) -> Iterator[_CompositeBuilder]:
        """Create a composite state with nested elements."""
        self._block_stack.append("composite")
        try:
            style_obj = coerce_style(style)
            builder = _CompositeBuilder(
                name, alias, style_obj, note, note_position
            )
            yield builder
            comp = builder._build()
            self._elements.append(comp)
            self._register_ref(comp)
            self._refs.update(builder._refs)
        finally:
            self._block_stack.pop()

    @contextmanager
    def concurrent(
        self,
        name: str,
        *,
        alias: str | None = None,
        style: StyleLike | None = None,
        note: str | Note | None = None,
        note_position: NotePosition = "right",
        separator: RegionSeparator = "horizontal",
    ) -> Iterator[_ConcurrentBuilder]:
        """Create a concurrent state with parallel regions."""
        self._block_stack.append("concurrent")
        try:
            style_obj = coerce_style(style)
            builder = _ConcurrentBuilder(
                name, alias, style_obj, note, note_position, separator
            )
            yield builder
            conc = builder._build()
            self._elements.append(conc)
            self._register_ref(conc)
            self._refs.update(builder._refs)
        finally:
            self._block_stack.pop()

    @contextmanager
    def parallel(
        self,
        name: str | None = None,
    ) -> Iterator["_ParallelBuilder"]:
        """Create a fork/join parallel structure with branches."""
        self._block_stack.append("parallel")
        try:
            builder = _ParallelBuilder(name)
            yield builder
            self._elements.extend(builder._build())
            self._refs.update(builder._refs)
        finally:
            self._block_stack.pop()

    def build(self) -> StateDiagram:
        """Build the complete state diagram."""
        return StateDiagram(
            elements=tuple(self._elements),
            title=self._title,
            caption=self._caption,
            header=self._header,
            footer=self._footer,
            legend=self._legend,
            scale=self._scale,
            theme=self._theme,
            layout=self._layout,
            layout_engine=self._layout_engine,
            linetype=self._linetype,
            hide_empty_description=self._hide_empty_description,
            diagram_style=self._diagram_style,
        )

    def render(self) -> str:
        """Build and render the diagram to PlantUML text.

        Convenience method combining build() and render() in one call.

        Returns:
            PlantUML text representation of the diagram
        """
        from ..renderers import render

        return render(self.build())


@contextmanager
def state_diagram(
    *,
    title: str | None = None,
    caption: str | None = None,
    header: str | Header | None = None,
    footer: str | Footer | None = None,
    legend: str | Legend | None = None,
    scale: float | Scale | None = None,
    theme: str | None = None,
    layout: LayoutDirection | None = None,
    layout_engine: LayoutEngine | None = None,
    linetype: LineType | None = None,
    hide_empty_description: bool = False,
    diagram_style: StateDiagramStyleLike | None = None,
) -> Iterator[StateDiagramBuilder]:
    """Create a state diagram with context manager syntax.

    Usage:
        with state_diagram(title="Traffic Light") as d:
            red = d.state("Red")
            yellow = d.state("Yellow")
            green = d.state("Green")

            d.arrow(d.start(), red)
            d.arrow(red, green, label="timer")
            d.arrow(green, yellow, label="timer")
            d.arrow(yellow, red, label="timer")

        print(d.render())

    With dict-based styling (no extra imports needed):
        with state_diagram(
            diagram_style={
                "background": "white",
                "font_name": "Arial",
                "state": {"background": "#E3F2FD", "line_color": "#1976D2"},
                "arrow": {"line_color": "#757575"},
            }
        ) as d:
            d.state("Styled")

    Args:
        title: Optional diagram title
        caption: Optional caption below the diagram
        header: Optional header text (string or Header object for positioning)
        footer: Optional footer text (string or Footer object for positioning)
        legend: Optional legend content (string or Legend object for positioning)
        scale: Optional scale factor (float) or Scale object for sizing
        theme: Optional PlantUML theme name (e.g., "cerulean", "amiga")
        layout: Diagram layout direction; None uses PlantUML default (top-to-bottom)
        layout_engine: Layout engine; "smetana" uses pure-Java GraphViz alternative
        linetype: Line routing style; "ortho" for right angles, "polyline" for direct
        hide_empty_description: Whether to hide empty state descriptions
        diagram_style: CSS-style styling for the diagram (colors, fonts, etc.)

    Yields:
        A StateDiagramBuilder for adding diagram elements
    """
    builder = StateDiagramBuilder(
        title=title,
        caption=caption,
        header=header,
        footer=footer,
        legend=legend,
        scale=scale,
        theme=theme,
        layout=layout,
        layout_engine=layout_engine,
        linetype=linetype,
        hide_empty_description=hide_empty_description,
        diagram_style=diagram_style,
    )
    yield builder
