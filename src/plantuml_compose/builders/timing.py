"""Timing diagram builders.

Provides context-manager based builders for timing diagrams.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Literal

from ..primitives.common import (
    ColorLike,
    Footer,
    Header,
    Legend,
    ThemeLike,
    TimingDiagramStyle,
    TimingDiagramStyleLike,
    coerce_timing_diagram_style,
)
from ..primitives.timing import (
    HiddenState,
    IntricatedState,
    StateChange,
    TimeAnchor,
    TimeValue,
    TimingConstraint,
    TimingDiagram,
    TimingElement,
    TimingHighlight,
    TimingInitialState,
    TimingMessage,
    TimingNote,
    TimingParticipant,
    TimingParticipantType,
    TimingScale,
    TimingStateOrder,
    TimingTicks,
)
from ..renderers import render as render_diagram


@dataclass
class ParticipantRef:
    """Reference to a participant for linking.

    Users should treat this as an opaque reference. Pass it to state change
    methods to specify which participant's state to change.
    """

    name: str

    def __repr__(self) -> str:
        return f"<ParticipantRef {self.name!r}>"


@dataclass
class AnchorRef:
    """Reference to a time anchor with arithmetic support.

    Supports Python arithmetic for offsets:
        start = d.anchor("start", at=0)
        d.state(data, "Done", at=start + 50)

    Attributes:
        name: Anchor name (without colon prefix)
        offset: Additional offset from the anchor
    """

    name: str
    offset: int = 0

    def __add__(self, offset: int) -> AnchorRef:
        """Add offset to the anchor reference."""
        return AnchorRef(self.name, self.offset + offset)

    def __radd__(self, offset: int) -> AnchorRef:
        """Support offset + anchor."""
        return AnchorRef(self.name, self.offset + offset)

    def __sub__(self, offset: int) -> AnchorRef:
        """Subtract offset from the anchor reference."""
        return AnchorRef(self.name, self.offset - offset)

    def __repr__(self) -> str:
        if self.offset == 0:
            return f"<AnchorRef :{self.name}>"
        sign = "+" if self.offset > 0 else ""
        return f"<AnchorRef :{self.name}{sign}{self.offset}>"


# Type for time parameters - absolute, date string, or anchor reference
TimeSpec = int | str | AnchorRef


def _resolve_time(time: TimeSpec) -> TimeValue:
    """Resolve a TimeSpec to a TimeValue for primitives."""
    if isinstance(time, AnchorRef):
        if time.offset == 0:
            return f":{time.name}"
        sign = "+" if time.offset > 0 else ""
        return f":{time.name}{sign}{time.offset}"
    return time


def _resolve_participant(participant: str | ParticipantRef) -> str:
    """Resolve participant to string name."""
    if isinstance(participant, ParticipantRef):
        return participant.name
    return participant


class TimingDiagramBuilder:
    """Builder for timing diagrams.

    Follows the same parameter-based pattern as other diagram builders.
    All configuration is done via method parameters, not separate state-setting calls.
    """

    def __init__(
        self,
        title: str | None,
        caption: str | None,
        header: Header | None,
        footer: Footer | None,
        legend: Legend | None,
        date_format: str | None,
        theme: ThemeLike | None,
        diagram_style: TimingDiagramStyle | None,
        compact_mode: bool,
        hide_time_axis: bool,
        manual_time_axis: bool,
    ) -> None:
        self._title = title
        self._caption = caption
        self._header = header
        self._footer = footer
        self._legend = legend
        self._date_format = date_format
        self._theme = theme
        self._diagram_style = diagram_style
        self._compact_mode = compact_mode
        self._hide_time_axis = hide_time_axis
        self._manual_time_axis = manual_time_axis
        self._elements: list[TimingElement] = []
        self._alias_counter = 0

    def _generate_alias(self) -> str:
        """Generate a unique internal alias."""
        self._alias_counter += 1
        return f"_p{self._alias_counter}"

    def _add_participant(
        self,
        type_: TimingParticipantType,
        name: str,
        alias: str | None = None,
        stereotype: str | None = None,
        compact: bool = False,
        period: int | None = None,
        pulse: int | None = None,
        offset: int | None = None,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
        height_pixels: int | None = None,
    ) -> ParticipantRef:
        """Add a participant and return a reference.

        PlantUML timing diagrams require aliases for participants when
        referencing them in state changes. If no alias is provided,
        we generate one automatically.
        """
        # PlantUML requires an alias to reference participants in state changes
        actual_alias = alias if alias else self._generate_alias()
        participant = TimingParticipant(
            type=type_,
            name=name,
            alias=actual_alias,
            stereotype=stereotype,
            compact=compact,
            period=period,
            pulse=pulse,
            offset=offset,
            min_value=min_value,
            max_value=max_value,
            height_pixels=height_pixels,
        )
        self._elements.append(participant)
        return ParticipantRef(actual_alias)

    def robust(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | None = None,
        compact: bool = False,
    ) -> ParticipantRef:
        """Add robust (multi-state) participant.

        Robust participants can have multiple named states and show
        complex waveforms with labeled state transitions.

        Args:
            name: Display name for the participant
            alias: Optional short alias for referencing
            stereotype: Optional stereotype annotation (e.g., "<<hw>>")
            compact: Use compact display mode for this participant

        Returns:
            ParticipantRef for use in state changes
        """
        return self._add_participant(
            "robust", name, alias, stereotype=stereotype, compact=compact
        )

    def concise(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | None = None,
        compact: bool = False,
    ) -> ParticipantRef:
        """Add concise (simple-state) participant.

        Concise participants show a simplified, binary-like display
        with state names shown inline.

        Args:
            name: Display name for the participant
            alias: Optional short alias for referencing
            stereotype: Optional stereotype annotation (e.g., "<<hw>>")
            compact: Use compact display mode for this participant

        Returns:
            ParticipantRef for use in state changes
        """
        return self._add_participant(
            "concise", name, alias, stereotype=stereotype, compact=compact
        )

    def rectangle(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | None = None,
        compact: bool = False,
    ) -> ParticipantRef:
        """Add rectangle participant.

        Rectangle participants are a variant of concise displayed
        within a rectangular shape.

        Args:
            name: Display name for the participant
            alias: Optional short alias for referencing
            stereotype: Optional stereotype annotation (e.g., "<<hw>>")
            compact: Use compact display mode for this participant

        Returns:
            ParticipantRef for use in state changes
        """
        return self._add_participant(
            "rectangle", name, alias, stereotype=stereotype, compact=compact
        )

    def clock(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | None = None,
        compact: bool = False,
        period: int,
        pulse: int | None = None,
        offset: int | None = None,
    ) -> ParticipantRef:
        """Add clock signal.

        Clock signals automatically generate a periodic waveform.

        Args:
            name: Display name for the clock
            alias: Optional short alias for referencing
            stereotype: Optional stereotype annotation (e.g., "<<hw>>")
            compact: Use compact display mode for this participant
            period: Clock period in time units (must be positive)
            pulse: Optional pulse width (defaults to period/2)
            offset: Optional offset from time 0

        Returns:
            ParticipantRef for use in state changes

        Raises:
            ValueError: If period is not positive
        """
        if period <= 0:
            raise ValueError(f"Clock period must be positive, got {period}")
        return self._add_participant(
            "clock",
            name,
            alias,
            stereotype=stereotype,
            compact=compact,
            period=period,
            pulse=pulse,
            offset=offset,
        )

    def binary(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | None = None,
        compact: bool = False,
    ) -> ParticipantRef:
        """Add binary (high/low) participant.

        Binary participants have only two states: high and low.

        Args:
            name: Display name for the participant
            alias: Optional short alias for referencing
            stereotype: Optional stereotype annotation (e.g., "<<hw>>")
            compact: Use compact display mode for this participant

        Returns:
            ParticipantRef for use in state changes
        """
        return self._add_participant(
            "binary", name, alias, stereotype=stereotype, compact=compact
        )

    def analog(
        self,
        name: str,
        *,
        alias: str | None = None,
        stereotype: str | None = None,
        compact: bool = False,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
        height: int | None = None,
    ) -> ParticipantRef:
        """Add analog (continuous) participant.

        Analog participants show continuous value transitions
        rather than discrete state changes.

        Args:
            name: Display name for the participant
            alias: Optional short alias for referencing
            stereotype: Optional stereotype annotation (e.g., "<<hw>>")
            compact: Use compact display mode for this participant
            min_value: Minimum value for analog range
            max_value: Maximum value for analog range
            height: Explicit height in pixels

        Returns:
            ParticipantRef for use in state changes
        """
        return self._add_participant(
            "analog",
            name,
            alias,
            stereotype=stereotype,
            compact=compact,
            min_value=min_value,
            max_value=max_value,
            height_pixels=height,
        )

    def define_states(
        self,
        participant: str | ParticipantRef,
        *states: str,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Define the order and optional labels of states for a participant.

        This controls the vertical ordering of states on the diagram axis.

        Args:
            participant: Participant reference or name
            *states: State names in display order
            labels: Optional dict mapping state names to display labels

        Example:
            d.define_states(signal, "Idle", "Active", "Done")
            d.define_states(signal, "idle", "active", labels={"idle": "Idle State"})
        """
        self._elements.append(
            TimingStateOrder(
                participant=_resolve_participant(participant),
                states=states,
                labels=labels,
            )
        )

    def ticks(
        self,
        participant: str | ParticipantRef,
        *,
        multiple: int | float,
    ) -> None:
        """Set tick marks for analog signal.

        Args:
            participant: Participant reference or name (must be analog)
            multiple: Tick interval value
        """
        self._elements.append(
            TimingTicks(
                participant=_resolve_participant(participant),
                multiple=multiple,
            )
        )

    def initial_state(
        self,
        participant: str | ParticipantRef,
        state: str,
    ) -> None:
        """Set initial state before the timeline starts.

        This declares a state before any @time reference, setting the
        initial condition of the signal.

        Args:
            participant: Participant reference or name
            state: Initial state value
        """
        self._elements.append(
            TimingInitialState(
                participant=_resolve_participant(participant),
                state=state,
            )
        )

    def anchor(self, name: str, *, at: TimeSpec) -> AnchorRef:
        """Create named time anchor.

        Returns AnchorRef that supports Python arithmetic:
            start = d.anchor("start", at=0)
            d.state(data, "Done", at=start + 50)

        Args:
            name: Anchor name (without colon)
            at: Time value for the anchor

        Returns:
            AnchorRef with arithmetic support
        """
        self._elements.append(TimeAnchor(time=_resolve_time(at), name=name))
        return AnchorRef(name)

    def state(
        self,
        participant: str | ParticipantRef,
        state: str,
        *,
        at: TimeSpec,
        color: ColorLike | None = None,
        comment: str | None = None,
    ) -> None:
        """Set participant state at a specific time.

        Args:
            participant: Participant reference or name
            state: New state value
            at: Time for the state change
            color: Optional color for the state
            comment: Optional inline comment annotation
        """
        self._elements.append(
            StateChange(
                participant=_resolve_participant(participant),
                time=_resolve_time(at),
                state=state,
                color=color,
                comment=comment,
            )
        )

    def intricated(
        self,
        participant: str | ParticipantRef,
        state1: str,
        state2: str,
        *,
        at: TimeSpec,
        color: ColorLike | None = None,
    ) -> None:
        """Set undefined/transitioning state between two values.

        Shows the signal as being in an undefined state between
        two possible values.

        Args:
            participant: Participant reference or name
            state1: First state value
            state2: Second state value
            at: Time for the intricated state
            color: Optional color for the intricated region
        """
        self._elements.append(
            IntricatedState(
                participant=_resolve_participant(participant),
                time=_resolve_time(at),
                states=(state1, state2),
                color=color,
            )
        )

    def hidden(
        self,
        participant: str | ParticipantRef,
        *,
        at: TimeSpec,
        style: Literal["-", "hidden"] = "-",
    ) -> None:
        """Set hidden state placeholder.

        Hides the signal for a period, useful for showing
        time gaps or don't-care regions.

        Args:
            participant: Participant reference or name
            at: Time for the hidden state
            style: Visual style ("-" for dash, "hidden" for full hidden)
        """
        self._elements.append(
            HiddenState(
                participant=_resolve_participant(participant),
                time=_resolve_time(at),
                style=style,
            )
        )

    def message(
        self,
        source: str | ParticipantRef,
        target: str | ParticipantRef,
        label: str | None = None,
        *,
        at: TimeSpec | None = None,
        target_offset: int | None = None,
    ) -> None:
        """Add message between participants.

        Args:
            source: Source participant
            target: Target participant
            label: Optional message label
            at: Optional time for the message at source
            target_offset: Optional relative time offset at target
        """
        self._elements.append(
            TimingMessage(
                source=_resolve_participant(source),
                target=_resolve_participant(target),
                label=label,
                source_time=_resolve_time(at) if at is not None else None,
                target_time_offset=target_offset,
            )
        )

    def constraint(
        self,
        participant: str | ParticipantRef,
        *,
        start: TimeSpec,
        end: TimeSpec,
        label: str,
    ) -> None:
        """Add timing constraint annotation.

        Shows a measurement/constraint between two time points.

        Args:
            participant: Participant reference or name
            start: Start time of the constraint
            end: End time of the constraint
            label: Constraint label (e.g., "{50ms}")
        """
        self._elements.append(
            TimingConstraint(
                participant=_resolve_participant(participant),
                start_time=_resolve_time(start),
                end_time=_resolve_time(end),
                label=label,
            )
        )

    def highlight(
        self,
        *,
        start: TimeSpec,
        end: TimeSpec,
        color: ColorLike | None = None,
        caption: str | None = None,
    ) -> None:
        """Highlight time region.

        Args:
            start: Start time of highlight
            end: End time of highlight
            color: Optional highlight color
            caption: Optional caption text
        """
        self._elements.append(
            TimingHighlight(
                start=_resolve_time(start),
                end=_resolve_time(end),
                color=color,
                caption=caption,
            )
        )

    def scale(self, *, time_units: int, pixels: int) -> None:
        """Set time-to-pixel scale.

        Args:
            time_units: Number of time units (must be positive)
            pixels: Number of pixels to map to (must be positive)

        Raises:
            ValueError: If time_units or pixels is not positive
        """
        if time_units <= 0:
            raise ValueError(f"time_units must be positive, got {time_units}")
        if pixels <= 0:
            raise ValueError(f"pixels must be positive, got {pixels}")
        self._elements.append(TimingScale(time_units=time_units, pixels=pixels))

    def note(
        self,
        participant: str | ParticipantRef,
        text: str,
        *,
        at: TimeSpec,
        position: Literal["top", "bottom"] = "top",
    ) -> None:
        """Add a note to a participant at a specific time.

        Args:
            participant: Participant reference or name
            text: Note text content
            at: Time for the note
            position: Note position ("top" or "bottom")
        """
        self._elements.append(
            TimingNote(
                participant=_resolve_participant(participant),
                time=_resolve_time(at),
                text=text,
                position=position,
            )
        )

    def build(self) -> TimingDiagram:
        """Build the immutable timing diagram."""
        return TimingDiagram(
            elements=tuple(self._elements),
            title=self._title,
            caption=self._caption,
            header=self._header,
            footer=self._footer,
            legend=self._legend,
            date_format=self._date_format,
            theme=self._theme,
            diagram_style=self._diagram_style,
            compact_mode=self._compact_mode,
            hide_time_axis=self._hide_time_axis,
            manual_time_axis=self._manual_time_axis,
        )

    def render(self) -> str:
        """Build and render the diagram to PlantUML text."""
        return render_diagram(self.build())


@contextmanager
def timing_diagram(
    *,
    title: str | None = None,
    caption: str | None = None,
    header: Header | None = None,
    footer: Footer | None = None,
    legend: Legend | None = None,
    date_format: str | None = None,
    theme: ThemeLike | None = None,
    diagram_style: TimingDiagramStyleLike | None = None,
    compact_mode: bool = False,
    hide_time_axis: bool = False,
    manual_time_axis: bool = False,
) -> Iterator[TimingDiagramBuilder]:
    """Create a timing diagram.

    Args:
        title: Diagram title
        caption: Caption below the diagram
        header: Header text
        footer: Footer text
        legend: Legend content
        date_format: Date format string (e.g., "YY-MM-dd")
        theme: PlantUML theme
        diagram_style: Diagram-wide styling (TimingDiagramStyle or dict)
        compact_mode: Enable global compact mode for all participants
        hide_time_axis: Hide the time axis
        manual_time_axis: Use manual time axis control

    Yields:
        TimingDiagramBuilder for adding participants and states

    Example:
        from plantuml_compose import timing_diagram

        with timing_diagram(title="Clock Domain Crossing") as d:
            # Participants
            clk = d.clock("Clock", period=50, pulse=25)
            data = d.robust("DataPath")
            rst = d.binary("ResetN")

            # Scale
            d.scale(time_units=100, pixels=50)

            # Anchors with arithmetic support
            start = d.anchor("start", at=0)

            # State changes
            d.state(data, "Idle", at=0)
            d.state(rst, "high", at=0)
            d.state(rst, "low", at=10)
            d.state(data, "Transmitting", at=20)
            d.state(data, "Receiving", at=40)

            # Use anchor with Python arithmetic
            d.state(rst, "high", at=start + 30)

            # Intricated (undefined) state
            d.intricated(data, "0", "1", at=50, color="Gray")

            # Messages between participants
            d.message(data, rst, "trigger", at=15)

            # Highlight time region
            d.highlight(start=20, end=40, color="Yellow", caption="Active Phase")

            # Timing constraint
            d.constraint(clk, start=0, end=50, label="{50ns}")

        print(d.render())
    """
    # Coerce diagram style if provided as dict
    style: TimingDiagramStyle | None = None
    if diagram_style is not None:
        style = coerce_timing_diagram_style(diagram_style)

    builder = TimingDiagramBuilder(
        title=title,
        caption=caption,
        header=header,
        footer=footer,
        legend=legend,
        date_format=date_format,
        theme=theme,
        diagram_style=style,
        compact_mode=compact_mode,
        hide_time_axis=hide_time_axis,
        manual_time_axis=manual_time_axis,
    )
    yield builder
