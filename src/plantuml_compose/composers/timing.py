"""Timing diagram composer.

Temporal pattern with d.at() grouping.

Example:
    d = timing_diagram(title="Container Live Migration")
    p = d.participants
    e = d.events

    source = p.robust("Source Node",
        states=("idle", "running", "dumping"),
        initial="running",
    )
    d.add(source)

    d.at(10,
        e.state(source, "dumping"),
    )

    puml = render(d)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from ..primitives.common import (
    ColorLike,
    Footer,
    Header,
    Legend,
    ThemeLike,
)
from ..primitives.styles import (
    TimingDiagramStyle,
    TimingDiagramStyleLike,
    coerce_timing_diagram_style,
)
from ..primitives.timing import (
    HiddenState,
    IntricatedState,
    StateChange,
    TimeAnchor,
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
    TimeValue,
)
from .base import BaseComposer, EntityRef


def _resolve_ref(item: EntityRef | str) -> str:
    """Resolve an EntityRef or raw string to a participant alias."""
    if isinstance(item, EntityRef):
        return item._ref
    return item


# ---------------------------------------------------------------------------
# Internal data types returned by namespace factories
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _StateEventData:
    """Pure data from e.state()."""
    participant: EntityRef | str
    state: str
    color: ColorLike | None = None
    comment: str | None = None


@dataclass(frozen=True)
class _MessageEventData:
    """Pure data from e.message()."""
    source: EntityRef | str
    target: EntityRef | str
    label: str | None = None
    target_time_offset: int | None = None


@dataclass(frozen=True)
class _IntricatedEventData:
    """Pure data from e.intricated()."""
    participant: EntityRef | str
    state1: str
    state2: str
    color: ColorLike | None = None


@dataclass(frozen=True)
class _HiddenEventData:
    """Pure data from e.hidden()."""
    participant: EntityRef | str
    style: Literal["-", "hidden"] = "-"


# Union of things that go inside a d.at() call
_AtEvent = _StateEventData | _MessageEventData | _IntricatedEventData | _HiddenEventData


# ---------------------------------------------------------------------------
# Namespaces
# ---------------------------------------------------------------------------


class TimingParticipantNamespace:
    """Factory namespace for timing diagram participants."""

    def _normalize_states(
        self, states: tuple[str, ...] | dict[str, str],
    ) -> tuple[tuple[str, ...], dict[str, str] | None]:
        """Normalize states input to (state_names, labels_or_none).

        Accepts either a tuple of state names or a dict mapping state
        names to display labels.
        """
        if isinstance(states, dict):
            return tuple(states.keys()), states
        return states, None

    def robust(
        self,
        name: str,
        *,
        states: tuple[str, ...] | dict[str, str] = (),
        initial: str | None = None,
        ref: str | None = None,
        stereotype: str | None = None,
        compact: bool = False,
    ) -> EntityRef:
        state_names, labels = self._normalize_states(states)
        return EntityRef(
            name, ref=ref,
            data={
                "_type": "robust",
                "states": state_names,
                "labels": labels,
                "initial": initial,
                "stereotype": stereotype,
                "compact": compact,
            },
        )

    def concise(
        self,
        name: str,
        *,
        states: tuple[str, ...] | dict[str, str] = (),
        initial: str | None = None,
        ref: str | None = None,
        stereotype: str | None = None,
        compact: bool = False,
    ) -> EntityRef:
        state_names, labels = self._normalize_states(states)
        return EntityRef(
            name, ref=ref,
            data={
                "_type": "concise",
                "states": state_names,
                "labels": labels,
                "initial": initial,
                "stereotype": stereotype,
                "compact": compact,
            },
        )

    def rectangle(
        self,
        name: str,
        *,
        states: tuple[str, ...] | dict[str, str] = (),
        initial: str | None = None,
        ref: str | None = None,
        stereotype: str | None = None,
        compact: bool = False,
    ) -> EntityRef:
        state_names, labels = self._normalize_states(states)
        return EntityRef(
            name, ref=ref,
            data={
                "_type": "rectangle",
                "states": state_names,
                "labels": labels,
                "initial": initial,
                "stereotype": stereotype,
                "compact": compact,
            },
        )

    def binary(
        self,
        name: str,
        *,
        ref: str | None = None,
        stereotype: str | None = None,
        compact: bool = False,
    ) -> EntityRef:
        return EntityRef(
            name, ref=ref,
            data={
                "_type": "binary",
                "stereotype": stereotype,
                "compact": compact,
            },
        )

    def clock(
        self,
        name: str,
        *,
        period: int,
        pulse: int | None = None,
        offset: int | None = None,
        ref: str | None = None,
        stereotype: str | None = None,
        compact: bool = False,
    ) -> EntityRef:
        return EntityRef(
            name, ref=ref,
            data={
                "_type": "clock",
                "period": period,
                "pulse": pulse,
                "offset": offset,
                "stereotype": stereotype,
                "compact": compact,
            },
        )

    def analog(
        self,
        name: str,
        *,
        ref: str | None = None,
        stereotype: str | None = None,
        compact: bool = False,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
        height: int | None = None,
    ) -> EntityRef:
        return EntityRef(
            name, ref=ref,
            data={
                "_type": "analog",
                "stereotype": stereotype,
                "compact": compact,
                "min_value": min_value,
                "max_value": max_value,
                "height_pixels": height,
            },
        )


class TimingEventNamespace:
    """Factory namespace for timing diagram events."""

    def state(
        self,
        participant: EntityRef | str,
        state: str,
        *,
        color: ColorLike | None = None,
        comment: str | None = None,
    ) -> _StateEventData:
        return _StateEventData(
            participant=participant,
            state=state,
            color=color,
            comment=comment,
        )

    def message(
        self,
        source: EntityRef | str,
        target: EntityRef | str,
        label: str | None = None,
        *,
        target_time_offset: int | None = None,
    ) -> _MessageEventData:
        return _MessageEventData(
            source=source,
            target=target,
            label=label,
            target_time_offset=target_time_offset,
        )

    def intricated(
        self,
        participant: EntityRef | str,
        state1: str,
        state2: str,
        *,
        color: ColorLike | None = None,
    ) -> _IntricatedEventData:
        return _IntricatedEventData(
            participant=participant,
            state1=state1,
            state2=state2,
            color=color,
        )

    def hidden(
        self,
        participant: EntityRef | str,
        *,
        style: Literal["-", "hidden"] = "-",
    ) -> _HiddenEventData:
        return _HiddenEventData(
            participant=participant,
            style=style,
        )


# ---------------------------------------------------------------------------
# Composer
# ---------------------------------------------------------------------------


class TimingComposer(BaseComposer):
    """Composer for timing diagrams."""

    def __init__(
        self,
        *,
        title: str | None = None,
        mainframe: str | None = None,
        caption: str | None = None,
        header: str | Header | None = None,
        footer: str | Footer | None = None,
        legend: str | Legend | None = None,
        theme: ThemeLike = None,
        date_format: str | None = None,
        diagram_style: TimingDiagramStyleLike | None = None,
        compact_mode: bool = False,
        hide_time_axis: bool = False,
        manual_time_axis: bool = False,
    ) -> None:
        super().__init__(
            title=title, mainframe=mainframe, caption=caption,
            header=header, footer=footer, legend=legend,
        )
        self._theme = theme
        self._date_format = date_format
        self._diagram_style: TimingDiagramStyle | None = (
            coerce_timing_diagram_style(diagram_style) if diagram_style else None
        )
        self._compact_mode = compact_mode
        self._hide_time_axis = hide_time_axis
        self._manual_time_axis = manual_time_axis
        self._participants_ns = TimingParticipantNamespace()
        self._events_ns = TimingEventNamespace()
        self._at_groups: list[Any] = []
        self._highlights: list[dict[str, Any]] = []
        self._constraints: list[dict[str, Any]] = []
        self._scale_data: dict[str, int] | None = None
        self._alias_counter = 0

    def _generate_alias(self) -> str:
        """Generate a unique internal alias."""
        self._alias_counter += 1
        return f"_p{self._alias_counter}"

    @property
    def participants(self) -> TimingParticipantNamespace:
        return self._participants_ns

    @property
    def events(self) -> TimingEventNamespace:
        return self._events_ns

    def at(
        self,
        time: TimeValue,
        *events: _AtEvent,
        name: str | None = None,
    ) -> None:
        """Register state changes at a time point."""
        self._at_groups.append({
            "time": time,
            "events": events,
            "name": name,
        })

    def highlight(
        self,
        *,
        start: TimeValue,
        end: TimeValue,
        color: ColorLike | None = None,
        caption: str | None = None,
    ) -> None:
        """Add a highlighted time region."""
        self._highlights.append({
            "start": start,
            "end": end,
            "color": color,
            "caption": caption,
        })

    def constraint(
        self,
        participant: EntityRef | str,
        *,
        start: TimeValue | str,
        end: TimeValue | str,
        label: str,
    ) -> None:
        """Add a timing constraint annotation."""
        self._constraints.append({
            "participant": participant,
            "start": start,
            "end": end,
            "label": label,
        })

    def scale(self, *, time_units: int, pixels: int) -> None:
        """Set time-to-pixel scale."""
        self._scale_data = {"time_units": time_units, "pixels": pixels}

    def ticks(
        self,
        participant: EntityRef | str,
        *,
        multiple: int | float,
    ) -> None:
        """Set tick marks for an analog participant.

        Args:
            participant: Participant reference or name
            multiple: Tick interval value
        """
        self._at_groups.append({
            "_type": "ticks",
            "participant": participant,
            "multiple": multiple,
        })

    def note(
        self,
        content: str,
        participant: EntityRef | str,
        *,
        position: Literal["top", "bottom"] = "top",
        time: TimeValue | None = None,
    ) -> None:
        """Add a note to a participant at a specific time.

        Args:
            content: Note text
            participant: Participant reference or name
            position: "top" or "bottom" relative to the signal
            time: Time point for the note (required for rendering)
        """
        self._at_groups.append({
            "_type": "note",
            "content": content,
            "participant": participant,
            "position": position,
            "time": time,
        })

    def build(self) -> TimingDiagram:
        elements: list[TimingElement] = []

        # Build participants from d.add() entities
        for item in self._elements:
            if isinstance(item, EntityRef):
                data = item._data
                ptype: TimingParticipantType = data.get("_type", "robust")
                alias = self._generate_alias()

                participant = TimingParticipant(
                    type=ptype,
                    name=item._name,
                    alias=alias,
                    stereotype=data.get("stereotype"),
                    compact=data.get("compact", False),
                    period=data.get("period"),
                    pulse=data.get("pulse"),
                    offset=data.get("offset"),
                    min_value=data.get("min_value"),
                    max_value=data.get("max_value"),
                    height_pixels=data.get("height_pixels"),
                )
                elements.append(participant)

                # Store the alias on the EntityRef for resolution
                # We need a mapping from EntityRef -> alias
                item._data["_alias"] = alias

                # states= produces TimingStateOrder
                states = data.get("states", ())
                if states:
                    elements.append(TimingStateOrder(
                        participant=alias,
                        states=states,
                        labels=data.get("labels"),
                    ))

                # initial= produces TimingInitialState
                initial = data.get("initial")
                if initial:
                    elements.append(TimingInitialState(
                        participant=alias,
                        state=initial,
                    ))

        # Scale
        if self._scale_data:
            elements.append(TimingScale(
                time_units=self._scale_data["time_units"],
                pixels=self._scale_data["pixels"],
            ))

        # Process d.at() groups and ticks
        for group in self._at_groups:
            # Handle ticks entries
            if group.get("_type") == "ticks":
                elements.append(TimingTicks(
                    participant=self._resolve_participant(group["participant"]),
                    multiple=group["multiple"],
                ))
                continue

            # Handle note entries
            if group.get("_type") == "note":
                note_time = group["time"]
                if note_time is None:
                    raise ValueError("TimingNote requires a time value")
                elements.append(TimingNote(
                    participant=self._resolve_participant(group["participant"]),
                    time=note_time,
                    text=group["content"],
                    position=group["position"],
                ))
                continue

            time = group["time"]
            name = group["name"]

            # Named anchor
            if name is not None:
                elements.append(TimeAnchor(time=time, name=name))

            # Process events
            for event in group["events"]:
                if isinstance(event, _StateEventData):
                    elements.append(StateChange(
                        participant=self._resolve_participant(event.participant),
                        time=time,
                        state=event.state,
                        color=event.color,
                        comment=event.comment,
                    ))
                elif isinstance(event, _MessageEventData):
                    elements.append(TimingMessage(
                        source=self._resolve_participant(event.source),
                        target=self._resolve_participant(event.target),
                        label=event.label,
                        source_time=time,
                        target_time_offset=event.target_time_offset,
                    ))
                elif isinstance(event, _IntricatedEventData):
                    elements.append(IntricatedState(
                        participant=self._resolve_participant(event.participant),
                        time=time,
                        states=(event.state1, event.state2),
                        color=event.color,
                    ))
                elif isinstance(event, _HiddenEventData):
                    elements.append(HiddenState(
                        participant=self._resolve_participant(event.participant),
                        time=time,
                        style=event.style,
                    ))

        # Highlights
        for h in self._highlights:
            elements.append(TimingHighlight(
                start=h["start"],
                end=h["end"],
                color=h["color"],
                caption=h["caption"],
            ))

        # Constraints
        for c in self._constraints:
            elements.append(TimingConstraint(
                participant=self._resolve_participant(c["participant"]),
                start_time=c["start"],
                end_time=c["end"],
                label=c["label"],
            ))

        return TimingDiagram(
            elements=tuple(elements),
            title=self._title,
            mainframe=self._mainframe,
            caption=self._caption,
            header=self._header,
            footer=self._footer,
            legend=self._legend,
            theme=self._theme,
            date_format=self._date_format,
            diagram_style=self._diagram_style,
            compact_mode=self._compact_mode,
            hide_time_axis=self._hide_time_axis,
            manual_time_axis=self._manual_time_axis,
        )

    def _resolve_participant(self, item: EntityRef | str) -> str:
        """Resolve participant to its alias string."""
        if isinstance(item, EntityRef):
            alias = item._data.get("_alias")
            if alias:
                return alias
            return item._ref
        return item


def timing_diagram(
    *,
    title: str | None = None,
    mainframe: str | None = None,
    caption: str | None = None,
    header: str | Header | None = None,
    footer: str | Footer | None = None,
    legend: str | Legend | None = None,
    theme: ThemeLike = None,
    date_format: str | None = None,
    diagram_style: TimingDiagramStyleLike | None = None,
    compact_mode: bool = False,
    hide_time_axis: bool = False,
    manual_time_axis: bool = False,
) -> TimingComposer:
    """Create a timing diagram composer.

    Example:
        d = timing_diagram(title="Migration")
        p = d.participants
        e = d.events
        source = p.robust("Source", states=("idle", "running"), initial="idle")
        d.add(source)
        d.at(10, e.state(source, "running"))
        print(render(d))
    """
    return TimingComposer(
        title=title, mainframe=mainframe, caption=caption,
        header=header, footer=footer, legend=legend,
        theme=theme, date_format=date_format,
        diagram_style=diagram_style,
        compact_mode=compact_mode,
        hide_time_axis=hide_time_axis,
        manual_time_axis=manual_time_axis,
    )
