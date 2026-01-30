"""Sequence diagram renderer.

Pure functions that transform sequence diagram primitives to PlantUML text.
"""

from __future__ import annotations

from ..primitives.common import coerce_line_style
from ..primitives.sequence import (
    Activation,
    Autonumber,
    Box,
    Delay,
    Divider,
    GroupBlock,
    Message,
    Participant,
    Reference,
    Return,
    SequenceDiagram,
    SequenceDiagramElement,
    SequenceNote,
    Space,
)
from .common import (
    escape_quotes,
    render_caption,
    render_color,
    render_footer,
    render_header,
    render_label,
    render_legend,
    render_scale,
    render_theme,
)


def render_sequence_diagram(diagram: SequenceDiagram) -> str:
    """Render a complete sequence diagram to PlantUML text."""
    lines: list[str] = ["@startuml"]

    # Theme comes first
    theme_line = render_theme(diagram.theme)
    if theme_line:
        lines.append(theme_line)

    # Scale (affects output size)
    if diagram.scale:
        scale_str = render_scale(diagram.scale)
        if scale_str:
            lines.append(scale_str)

    if diagram.title:
        if "\n" in diagram.title:
            lines.append("title")
            for title_line in diagram.title.split("\n"):
                lines.append(f"  {escape_quotes(title_line)}")
            lines.append("end title")
        else:
            lines.append(f"title {escape_quotes(diagram.title)}")

    # Header and footer
    if diagram.header:
        lines.extend(render_header(diagram.header))
    if diagram.footer:
        lines.extend(render_footer(diagram.footer))

    # Caption (appears below diagram)
    if diagram.caption:
        lines.append(render_caption(diagram.caption))

    # Legend
    if diagram.legend:
        lines.extend(render_legend(diagram.legend))

    if diagram.hide_unlinked:
        lines.append("hide unlinked")

    # Autonumber at start
    if diagram.autonumber:
        lines.append(_render_autonumber(diagram.autonumber))

    # Boxes with their participants
    for box in diagram.boxes:
        lines.extend(_render_box(box))

    # Standalone participants (not in boxes)
    for participant in diagram.participants:
        lines.append(_render_participant(participant))

    # Main elements
    for elem in diagram.elements:
        lines.extend(_render_element(elem))

    lines.append("@enduml")
    return "\n".join(lines)


def _render_participant(p: Participant) -> str:
    """Render a participant declaration."""
    # Type keyword
    parts: list[str] = [p.type]

    # Name with optional alias
    if p.alias or not p.name.isidentifier():
        escaped = escape_quotes(p.name)
        parts.append(f'"{escaped}" as {p._ref}')
    else:
        parts.append(p.name)

    # Order
    if p.order is not None:
        parts.append(f"order {p.order}")

    # Style background as element color
    if p.style and p.style.background:
        color = render_color(p.style.background)
        if not color.startswith("#"):
            color = f"#{color}"
        parts.append(color)

    # Multiline description - appended after all other parts
    if p.description:
        desc = render_label(p.description)
        if "\n" in desc:
            # Multiline participant - use all parts, then add description block
            base = " ".join(parts)
            lines = [f"{base} ["]
            for line in desc.split("\n"):
                lines.append(f"  {line}")
            lines.append("]")
            return "\n".join(lines)

    return " ".join(parts)


def _render_box(box: Box) -> list[str]:
    """Render a box with participants."""
    lines: list[str] = []

    # Opening
    parts = ["box"]
    if box.name:
        parts.append(f'"{escape_quotes(box.name)}"')
    if box.color:
        color = render_color(box.color)
        if not color.startswith("#"):
            color = f"#{color}"
        parts.append(color)
    lines.append(" ".join(parts))

    # Participants
    for p in box.participants:
        lines.append(f"  {_render_participant(p)}")

    lines.append("end box")
    return lines


def _render_element(elem: SequenceDiagramElement) -> list[str]:
    """Render a single diagram element."""
    if isinstance(elem, Message):
        return [_render_message(elem)]
    if isinstance(elem, Return):
        return [_render_return(elem)]
    if isinstance(elem, Activation):
        return [_render_activation(elem)]
    if isinstance(elem, GroupBlock):
        return _render_group_block(elem)
    if isinstance(elem, SequenceNote):
        return _render_note(elem)
    if isinstance(elem, Reference):
        return _render_reference(elem)
    if isinstance(elem, Divider):
        return [f"== {elem.title} =="]
    if isinstance(elem, Delay):
        if elem.message:
            return [f"...{elem.message}..."]
        return ["..."]
    if isinstance(elem, Space):
        if elem.pixels:
            return [f"||{elem.pixels}||"]
        return ["|||"]
    if isinstance(elem, Autonumber):
        return [_render_autonumber(elem)]
    raise TypeError(f"Unknown element type: {type(elem).__name__}")


def _render_message(msg: Message) -> str:
    """Render a message between participants."""
    # Build arrow
    arrow = _build_message_arrow(msg)

    # Activation shorthand
    activation = ""
    if msg.activation:
        activation_map = {
            "activate": "++",
            "deactivate": "--",
            "create": "**",
            "destroy": "!!",
        }
        activation = activation_map[msg.activation]
        if msg.activation_color and msg.activation == "activate":
            color = render_color(msg.activation_color)
            if not color.startswith("#"):
                color = f"#{color}"
            activation += color

    # Label
    label = ""
    if msg.label:
        label = f" : {render_label(msg.label, inline=True)}"

    return f"{msg.source} {arrow} {msg.target}{activation}{label}"


def _build_message_arrow(msg: Message) -> str:
    """Build the arrow string for a message."""
    # Build bracket styling if any style options are set
    # Note: thickness is in the primitive but not rendered - PlantUML doesn't support it
    bracket_parts: list[str] = []

    # Extract styling from style object
    if msg.style:
        style = coerce_line_style(msg.style)
        if style.color:
            color = render_color(style.color)
            if not color.startswith("#"):
                color = f"#{color}"
            bracket_parts.append(color)
        if style.bold:
            bracket_parts.append("bold")

    # Bracket syntax: -[style]-> (brackets go between dashes)
    bracket = f"[{','.join(bracket_parts)}]" if bracket_parts else ""

    # Line style: solid uses single dash, dotted uses double dash
    line_left = "-" if msg.line_style == "solid" else "--"
    # With bracket syntax, need closing dash before head: -[style]-> or --[style]->
    line_right = "-" if bracket else ""

    # Arrow head
    head_map = {
        "normal": ">",
        "thin": ">>",
        "lost": ">x",
        "open": "\\",  # Upper half arrow
        "circle": ">o",
        "none": "",
    }
    head = head_map[msg.arrow_head]

    # Handle bidirectional - always add < on left side
    if msg.bidirectional:
        return f"<{line_left}{bracket}{line_right}{head}"

    return f"{line_left}{bracket}{line_right}{head}"


def _render_return(ret: Return) -> str:
    """Render a return message."""
    if ret.label:
        return f"return {render_label(ret.label, inline=True)}"
    return "return"


def _render_activation(act: Activation) -> str:
    """Render an explicit activation/deactivation/create."""
    if act.action == "activate":
        if act.color:
            color = render_color(act.color)
            if not color.startswith("#"):
                color = f"#{color}"
            return f"activate {act.participant} {color}"
        return f"activate {act.participant}"
    if act.action == "deactivate":
        return f"deactivate {act.participant}"
    if act.action == "destroy":
        return f"destroy {act.participant}"
    if act.action == "create":
        return f"create {act.participant}"
    raise ValueError(f"Unknown activation action: {act.action}")


def _render_group_block(group: GroupBlock) -> list[str]:
    """Render a grouping block (alt, opt, loop, etc.)."""
    lines: list[str] = []

    # Opening line
    if group.type == "group":
        # Custom group with optional secondary label
        opening = (
            f"group {render_label(group.label, inline=True)}" if group.label else "group"
        )
        if group.secondary_label:
            opening += f" [{render_label(group.secondary_label, inline=True)}]"
        lines.append(opening)
    else:
        # Semantic keyword (alt, opt, loop, etc.)
        opening = group.type
        if group.label:
            opening += f" {render_label(group.label, inline=True)}"
        lines.append(opening)

    # Elements (indented)
    for elem in group.elements:
        for line in _render_element(elem):
            lines.append(f"  {line}")

    # Else blocks (only valid for alt and par)
    for else_block in group.else_blocks:
        else_line = "else"
        if else_block.label:
            else_line += f" {render_label(else_block.label, inline=True)}"
        lines.append(else_line)
        for elem in else_block.elements:
            for line in _render_element(elem):
                lines.append(f"  {line}")

    lines.append("end")
    return lines


def _render_note(note: SequenceNote) -> list[str]:
    """Render a note."""
    lines: list[str] = []
    content = render_label(note.content)

    # Build position prefix
    if note.across:
        prefix = "note across"
    elif note.position == "over":
        participants = ", ".join(note.participants)
        shape = note.shape if note.shape != "note" else "note"
        prefix = f"{shape} over {participants}"
    elif note.position in ("left", "right"):
        if note.participants:
            prefix = f"note {note.position} of {note.participants[0]}"
        else:
            prefix = f"note {note.position}"
    else:
        prefix = f"note {note.position}"

    # Aligned prefix
    if note.aligned:
        prefix = f"/ {prefix}"

    # Single or multiline
    if "\n" in content:
        lines.append(prefix)
        for line in content.split("\n"):
            lines.append(f"  {line}")
        lines.append("end note")
    else:
        lines.append(f"{prefix}: {content}")

    return lines


def _render_reference(ref: Reference) -> list[str]:
    """Render a reference to another diagram."""
    participants = ", ".join(ref.participants)
    content = render_label(ref.label)

    if "\n" in content:
        lines = [f"ref over {participants}"]
        for line in content.split("\n"):
            lines.append(f"  {line}")
        lines.append("end ref")
        return lines

    return [f"ref over {participants} : {content}"]


def _render_autonumber(auto: Autonumber) -> str:
    """Render autonumber control."""
    if auto.action == "stop":
        return "autonumber stop"
    if auto.action == "resume":
        return "autonumber resume"

    # Start
    parts = ["autonumber"]
    if auto.start is not None:
        parts.append(str(auto.start))
        if auto.increment is not None:
            parts.append(str(auto.increment))
    if auto.format:
        parts.append(f'"{auto.format}"')

    return " ".join(parts)
