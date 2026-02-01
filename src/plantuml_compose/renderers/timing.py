"""Timing diagram renderers.

Pure functions that transform timing diagram primitives to PlantUML text.
"""

from __future__ import annotations

from ..primitives.common import TimingDiagramStyle
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
    TimingScale,
    TimingStateOrder,
    TimingTicks,
    TimeValue,
)
from .common import (
    render_caption,
    render_color_hash,
    render_diagram_style,
    render_footer,
    render_header,
    render_legend,
    render_theme,
)


def render_timing_diagram(diagram: TimingDiagram) -> str:
    """Render a complete timing diagram to PlantUML text."""
    lines: list[str] = ["@startuml"]

    # Theme (must come first)
    if diagram.theme:
        theme_line = render_theme(diagram.theme)
        if theme_line:
            lines.append(theme_line)

    # Diagram style
    if diagram.diagram_style:
        lines.extend(_render_timing_diagram_style(diagram.diagram_style))

    # Global compact mode
    if diagram.compact_mode:
        lines.append("mode compact")

    # Time axis control
    if diagram.hide_time_axis:
        lines.append("hide time-axis")
    if diagram.manual_time_axis:
        lines.append("manual time-axis")

    # Date format
    if diagram.date_format:
        lines.append(f'use date format "{diagram.date_format}"')

    # Title
    if diagram.title:
        lines.append(f"title {diagram.title}")

    # Header
    if diagram.header:
        lines.extend(render_header(diagram.header))

    # Footer
    if diagram.footer:
        lines.extend(render_footer(diagram.footer))

    # Caption
    if diagram.caption:
        lines.append(render_caption(diagram.caption))

    # Legend
    if diagram.legend:
        lines.extend(render_legend(diagram.legend))

    # Elements
    for elem in diagram.elements:
        lines.extend(_render_element(elem))

    lines.append("@enduml")
    return "\n".join(lines)


def _render_element(elem: TimingElement) -> list[str]:
    """Dispatch to specific renderer based on element type."""
    if isinstance(elem, TimingParticipant):
        return _render_participant(elem)
    if isinstance(elem, TimingStateOrder):
        return [_render_state_order(elem)]
    if isinstance(elem, TimingTicks):
        return [_render_ticks(elem)]
    if isinstance(elem, TimeAnchor):
        return [_render_anchor(elem)]
    if isinstance(elem, TimingInitialState):
        return [_render_initial_state(elem)]
    if isinstance(elem, StateChange):
        return [_render_state_change(elem)]
    if isinstance(elem, IntricatedState):
        return [_render_intricated_state(elem)]
    if isinstance(elem, HiddenState):
        return [_render_hidden_state(elem)]
    if isinstance(elem, TimingMessage):
        return [_render_message(elem)]
    if isinstance(elem, TimingConstraint):
        return [_render_constraint(elem)]
    if isinstance(elem, TimingHighlight):
        return [_render_highlight(elem)]
    if isinstance(elem, TimingScale):
        return [_render_scale(elem)]
    if isinstance(elem, TimingNote):
        return _render_note(elem)
    raise TypeError(f"Unknown timing element type: {type(elem)}")


def _format_time(time: TimeValue) -> str:
    """Format a time value for PlantUML.

    Integers and strings (dates/times like "2020/07/04") are both
    converted to their string representation.
    """
    return str(time)


def _format_time_ref(time: TimeValue) -> str:
    """Format a time value as a time reference (@time or @:anchor)."""
    return f"@{time}"


def _render_participant(p: TimingParticipant) -> list[str]:
    """Render participant declaration.

    PlantUML syntax variants:
        robust "Name" as R
        clock "CLK" <<hw>> as C with period 50
        compact concise "Status" as S
        analog "Voltage" between 0 and 5 as V
    """
    lines: list[str] = []
    parts: list[str] = []

    # Compact keyword comes first
    if p.compact:
        parts.append("compact")

    # Type and name
    parts.append(p.type)
    parts.append(f'"{p.name}"')

    # Analog range (between min and max)
    if p.type == "analog" and p.min_value is not None and p.max_value is not None:
        parts.append(f"between {p.min_value} and {p.max_value}")

    # Stereotype comes after name, before alias
    if p.stereotype:
        parts.append(p.stereotype)

    # Alias
    if p.alias:
        parts.append(f"as {p.alias}")

    # Clock parameters
    if p.type == "clock":
        if p.period is not None:
            parts.append(f"with period {p.period}")
        if p.pulse is not None:
            parts.append(f"pulse {p.pulse}")
        if p.offset is not None:
            parts.append(f"offset {p.offset}")

    lines.append(" ".join(parts))

    # Analog height (separate line)
    if p.type == "analog" and p.height_pixels is not None:
        ref = p.alias if p.alias else p.name
        lines.append(f"{ref} is {p.height_pixels} pixels height")

    return lines


def _render_state_order(order: TimingStateOrder) -> str:
    """Render state ordering directive.

    PlantUML syntax:
        R has Idle,Active,Done
        R has "Ready" as ready, "Running" as running
    """
    if order.labels:
        # With labels: "Label" as state
        state_parts = []
        for state in order.states:
            if state in order.labels:
                state_parts.append(f'"{order.labels[state]}" as {state}')
            else:
                state_parts.append(state)
        return f"{order.participant} has {', '.join(state_parts)}"
    else:
        # Simple: state1,state2,state3
        return f"{order.participant} has {','.join(order.states)}"


def _render_ticks(ticks: TimingTicks) -> str:
    """Render tick marks for analog signal."""
    return f"{ticks.participant} ticks num on multiple {ticks.multiple}"


def _render_anchor(anchor: TimeAnchor) -> str:
    """Render time anchor definition."""
    return f"{_format_time_ref(anchor.time)} as :{anchor.name}"


def _render_initial_state(state: TimingInitialState) -> str:
    """Render initial state before timeline."""
    return f"{state.participant} is {state.state}"


def _render_state_change(state: StateChange) -> str:
    """Render state change.

    PlantUML timing diagram syntax:
        @0
        R is Idle

    With color:
        @0
        R is Idle #Blue

    With comment:
        @0
        R is Idle: starts here
    """
    state_str = f"{state.participant} is {state.state}"
    if state.color:
        state_str += f" {render_color_hash(state.color)}"
    if state.comment:
        state_str += f": {state.comment}"
    return f"{_format_time_ref(state.time)}\n{state_str}"


def _render_intricated_state(state: IntricatedState) -> str:
    """Render intricated (undefined) state."""
    state_str = f"{{{state.states[0]},{state.states[1]}}}"
    if state.color:
        state_str += f" {render_color_hash(state.color)}"
    return f"{_format_time_ref(state.time)}\n{state.participant} is {state_str}"


def _render_hidden_state(state: HiddenState) -> str:
    """Render hidden state placeholder."""
    state_str = f"{{{state.style}}}"
    return f"{_format_time_ref(state.time)}\n{state.participant} is {state_str}"


def _render_message(msg: TimingMessage) -> str:
    """Render message between participants."""
    parts = [msg.source, "->"]

    if msg.target_time_offset is not None:
        # Target with time offset: target@+50 or target@-10
        sign = "+" if msg.target_time_offset >= 0 else ""
        parts.append(f"{msg.target}@{sign}{msg.target_time_offset}")
    else:
        parts.append(msg.target)

    if msg.label:
        parts.append(f": {msg.label}")

    result = " ".join(parts)
    if msg.source_time is not None:
        result = f"{_format_time_ref(msg.source_time)}\n{result}"
    return result


def _render_constraint(constraint: TimingConstraint) -> str:
    """Render timing constraint annotation."""
    # Format: participant@start <-> @end : {label}
    return (
        f"{constraint.participant}{_format_time_ref(constraint.start_time)} <-> "
        f"{_format_time_ref(constraint.end_time)} : {constraint.label}"
    )


def _render_highlight(highlight: TimingHighlight) -> str:
    """Render highlighted time region."""
    parts = [f"highlight {_format_time(highlight.start)} to {_format_time(highlight.end)}"]
    if highlight.color:
        parts.append(render_color_hash(highlight.color))
    if highlight.caption:
        parts.append(f": {highlight.caption}")
    return " ".join(parts)


def _render_scale(scale: TimingScale) -> str:
    """Render scale directive."""
    return f"scale {scale.time_units} as {scale.pixels} pixels"


def _render_note(note: TimingNote) -> list[str]:
    """Render note attached to a participant at a specific time."""
    # Set the time context first, then render the note
    lines = [
        _format_time_ref(note.time),
        f"note {note.position} of {note.participant}",
    ]
    lines.extend(note.text.split("\n"))
    lines.append("end note")
    return lines


def _render_timing_diagram_style(style: TimingDiagramStyle) -> list[str]:
    """Render TimingDiagramStyle as PlantUML <style> block."""
    element_styles: list[tuple[str, object]] = [
        ("robust", style.robust),
        ("concise", style.concise),
        ("clock", style.clock),
        ("binary", style.binary),
        ("analog", style.analog),
        ("highlight", style.highlight),
        ("note", style.note),
    ]

    return render_diagram_style(
        diagram_type="timingDiagram",
        root_background=style.background,
        root_font_name=style.font_name,
        root_font_size=style.font_size,
        root_font_color=style.font_color,
        element_styles=element_styles,  # type: ignore[arg-type]
        arrow_style=style.arrow,
        title_style=style.title,
    )
