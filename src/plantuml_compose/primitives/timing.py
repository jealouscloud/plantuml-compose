"""Timing diagram primitives.

Frozen dataclasses representing timing diagram elements.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, TypeAlias

from .common import (
    ColorLike,
    Footer,
    Header,
    Legend,
    ThemeLike,
    TimingDiagramStyle,
)


# Participant types for timing diagrams
# rectangle is a variant of concise displayed in rectangular shape
TimingParticipantType = Literal[
    "robust", "concise", "clock", "binary", "analog", "rectangle"
]

# Time value can be an integer (time units) or string (dates/times like "2020/07/04" or "1:15:00")
# Also supports relative time strings like "+50"
TimeValue: TypeAlias = int | str


@dataclass(frozen=True)
class TimingParticipant:
    """A timing diagram participant (signal line).

    Attributes:
        type: Participant type ("robust", "concise", "clock", "binary", "analog", "rectangle")
        name: Display name for the participant
        alias: Optional short alias for referencing
        stereotype: Optional stereotype annotation (e.g., "<<hw>>")
        compact: If True, use compact display mode for this participant
        period: Clock period (only for clock type)
        pulse: Clock pulse width (only for clock type)
        offset: Clock offset (only for clock type)
        min_value: Minimum value for analog range (only for analog type)
        max_value: Maximum value for analog range (only for analog type)
        height_pixels: Explicit height in pixels (only for analog type)
    """

    type: TimingParticipantType
    name: str
    alias: str | None = None
    stereotype: str | None = None
    compact: bool = False
    # Clock-specific parameters
    period: int | None = None
    pulse: int | None = None
    offset: int | None = None
    # Analog-specific parameters
    min_value: int | float | None = None
    max_value: int | float | None = None
    height_pixels: int | None = None


@dataclass(frozen=True)
class TimingStateOrder:
    """Define the order and labels of states for a participant.

    PlantUML syntax:
        R has Idle,Active,Done
        R has "Ready" as ready, "Running" as running

    Attributes:
        participant: Participant alias or name
        states: Tuple of state names in display order
        labels: Optional dict mapping state names to display labels
    """

    participant: str
    states: tuple[str, ...]
    labels: dict[str, str] | None = None


@dataclass(frozen=True)
class TimingTicks:
    """Tick mark configuration for analog signals.

    PlantUML syntax:
        V ticks num on multiple 1

    Attributes:
        participant: Participant alias or name
        multiple: Tick interval value
    """

    participant: str
    multiple: int | float


@dataclass(frozen=True)
class TimeAnchor:
    """Named time point for reuse.

    Allows defining named time points that can be referenced later:
        @0 as :start
        @100 as :end

    Attributes:
        time: The time value (absolute or relative)
        name: Anchor name (without colon prefix)
    """

    time: TimeValue
    name: str


@dataclass(frozen=True)
class TimingInitialState:
    """Initial state declared before the timeline.

    PlantUML syntax (before any @time):
        R is Idle

    Attributes:
        participant: Participant alias or name
        state: Initial state value
    """

    participant: str
    state: str


@dataclass(frozen=True)
class StateChange:
    """State change at a specific time.

    Attributes:
        participant: Participant alias or name
        time: Time for the state change
        state: New state value
        color: Optional color for the state region
        comment: Optional inline comment (renders as ": comment")
    """

    participant: str
    time: TimeValue
    state: str
    color: ColorLike | None = None
    comment: str | None = None


@dataclass(frozen=True)
class IntricatedState:
    """Undefined/transitioning state between two values.

    Represents a state where the signal is in transition or undefined,
    shown as {state1,state2} in PlantUML.

    Attributes:
        participant: Participant alias or name
        time: Time for the intricated state
        states: Tuple of two state names
        color: Optional color for the intricated region
    """

    participant: str
    time: TimeValue
    states: tuple[str, str]
    color: ColorLike | None = None


@dataclass(frozen=True)
class HiddenState:
    """Hidden state placeholder.

    Represents a section where the signal is hidden or undefined,
    shown as {-} or {hidden} in PlantUML.

    Attributes:
        participant: Participant alias or name
        time: Time for the hidden state
        style: Visual style ("-" for dash, "hidden" for full hidden)
    """

    participant: str
    time: TimeValue
    style: Literal["-", "hidden"] = "-"


@dataclass(frozen=True)
class TimingMessage:
    """Message between participants.

    Attributes:
        source: Source participant alias or name
        target: Target participant alias or name
        label: Optional message label
        source_time: Time at source (optional)
        target_time_offset: Relative time offset at target (for @+50 syntax)
    """

    source: str
    target: str
    label: str | None = None
    source_time: TimeValue | None = None
    target_time_offset: int | None = None


@dataclass(frozen=True)
class TimingConstraint:
    """Timing constraint annotation.

    Shows a measurement/constraint between two time points.

    Attributes:
        participant: Participant alias or name
        start_time: Start time of the constraint
        end_time: End time of the constraint
        label: Constraint label (e.g., "{50ms}")
    """

    participant: str
    start_time: TimeValue
    end_time: TimeValue
    label: str


@dataclass(frozen=True)
class TimingHighlight:
    """Highlighted time region.

    Attributes:
        start: Start time of highlight
        end: End time of highlight
        color: Optional highlight color
        caption: Optional caption text
    """

    start: TimeValue
    end: TimeValue
    color: ColorLike | None = None
    caption: str | None = None


@dataclass(frozen=True)
class TimingScale:
    """Scale directive for time-to-pixel mapping.

    Attributes:
        time_units: Number of time units
        pixels: Number of pixels to map to
    """

    time_units: int
    pixels: int


@dataclass(frozen=True)
class TimingNote:
    """Note attached to a participant at a specific time.

    Attributes:
        participant: Participant alias or name
        time: Time for the note
        text: Note text content
        position: Note position relative to the signal
    """

    participant: str
    time: TimeValue
    text: str
    position: Literal["top", "bottom"] = "top"


# Union type for all timing diagram elements
TimingElement: TypeAlias = (
    TimingParticipant
    | TimingStateOrder
    | TimingTicks
    | TimeAnchor
    | TimingInitialState
    | StateChange
    | IntricatedState
    | HiddenState
    | TimingMessage
    | TimingConstraint
    | TimingHighlight
    | TimingScale
    | TimingNote
)


# Forward reference for style - imported at module level to avoid circular imports
# The actual TimingDiagramStyle is defined in common.py


@dataclass(frozen=True)
class TimingDiagram:
    """Complete timing diagram.

    Attributes:
        elements: Ordered sequence of timing diagram elements
        title: Diagram title
        caption: Caption below the diagram
        header: Header text
        footer: Footer text
        legend: Legend content
        date_format: Date format string (e.g., "YY-MM-dd")
        theme: PlantUML theme
        diagram_style: Diagram-wide styling
        compact_mode: Enable global compact mode
        hide_time_axis: Hide the time axis
        manual_time_axis: Use manual time axis control
    """

    elements: tuple[TimingElement, ...] = field(default_factory=tuple)
    title: str | None = None
    caption: str | None = None
    header: Header | None = None
    footer: Footer | None = None
    legend: Legend | None = None
    date_format: str | None = None
    theme: ThemeLike | None = None
    diagram_style: TimingDiagramStyle | None = None
    compact_mode: bool = False
    hide_time_axis: bool = False
    manual_time_axis: bool = False
