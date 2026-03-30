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
from ..primitives.timing import (
    IntricatedState,
    StateChange,
    TimeAnchor,
    TimingConstraint,
    TimingDiagram,
    TimingElement,
    TimingHighlight,
    TimingInitialState,
    TimingMessage,
    TimingParticipant,
    TimingParticipantType,
    TimingScale,
    TimingStateOrder,
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


@dataclass(frozen=True)
class _MessageEventData:
    """Pure data from e.message()."""
    source: EntityRef | str
    target: EntityRef | str
    label: str | None = None


@dataclass(frozen=True)
class _IntricatedEventData:
    """Pure data from e.intricated()."""
    participant: EntityRef | str
    state1: str
    state2: str
    color: ColorLike | None = None


# Union of things that go inside a d.at() call
_AtEvent = _StateEventData | _MessageEventData | _IntricatedEventData


# ---------------------------------------------------------------------------
# Namespaces
# ---------------------------------------------------------------------------


class TimingParticipantNamespace:
    """Factory namespace for timing diagram participants."""

    def robust(
        self,
        name: str,
        *,
        states: tuple[str, ...] = (),
        initial: str | None = None,
        ref: str | None = None,
    ) -> EntityRef:
        return EntityRef(
            name, ref=ref,
            data={
                "_type": "robust",
                "states": states,
                "initial": initial,
            },
        )

    def concise(
        self,
        name: str,
        *,
        states: tuple[str, ...] = (),
        initial: str | None = None,
        ref: str | None = None,
    ) -> EntityRef:
        return EntityRef(
            name, ref=ref,
            data={
                "_type": "concise",
                "states": states,
                "initial": initial,
            },
        )

    def binary(
        self,
        name: str,
        *,
        ref: str | None = None,
    ) -> EntityRef:
        return EntityRef(
            name, ref=ref,
            data={"_type": "binary"},
        )

    def clock(
        self,
        name: str,
        *,
        period: int,
        pulse: int | None = None,
        offset: int | None = None,
        ref: str | None = None,
    ) -> EntityRef:
        return EntityRef(
            name, ref=ref,
            data={
                "_type": "clock",
                "period": period,
                "pulse": pulse,
                "offset": offset,
            },
        )

    def analog(
        self,
        name: str,
        *,
        ref: str | None = None,
    ) -> EntityRef:
        return EntityRef(
            name, ref=ref,
            data={"_type": "analog"},
        )


class TimingEventNamespace:
    """Factory namespace for timing diagram events."""

    def state(
        self,
        participant: EntityRef | str,
        state: str,
        *,
        color: ColorLike | None = None,
    ) -> _StateEventData:
        return _StateEventData(
            participant=participant,
            state=state,
            color=color,
        )

    def message(
        self,
        source: EntityRef | str,
        target: EntityRef | str,
        label: str | None = None,
    ) -> _MessageEventData:
        return _MessageEventData(
            source=source,
            target=target,
            label=label,
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
    ) -> None:
        super().__init__(
            title=title, mainframe=mainframe, caption=caption,
            header=header, footer=footer, legend=legend,
        )
        self._theme = theme
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
                    period=data.get("period"),
                    pulse=data.get("pulse"),
                    offset=data.get("offset"),
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

        # Process d.at() groups
        for group in self._at_groups:
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
                    ))
                elif isinstance(event, _MessageEventData):
                    elements.append(TimingMessage(
                        source=self._resolve_participant(event.source),
                        target=self._resolve_participant(event.target),
                        label=event.label,
                        source_time=time,
                    ))
                elif isinstance(event, _IntricatedEventData):
                    elements.append(IntricatedState(
                        participant=self._resolve_participant(event.participant),
                        time=time,
                        states=(event.state1, event.state2),
                        color=event.color,
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
        theme=theme,
    )
