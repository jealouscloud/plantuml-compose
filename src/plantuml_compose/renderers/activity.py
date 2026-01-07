"""Activity diagram renderer.

Pure functions that transform activity diagram primitives to PlantUML text.
"""

from __future__ import annotations

from ..primitives.activity import (
    Action,
    ActivityDiagram,
    ActivityElement,
    ActivityNote,
    Arrow,
    Break,
    Connector,
    Detach,
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
from ..primitives.common import Note
from .common import (
    escape_quotes,
    render_caption,
    render_color,
    render_footer,
    render_header,
    render_label,
    render_legend,
    render_scale,
)


def render_activity_diagram(diagram: ActivityDiagram) -> str:
    """Render a complete activity diagram to PlantUML text."""
    lines: list[str] = ["@startuml"]

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

    for elem in diagram.elements:
        lines.extend(_render_element(elem))

    lines.append("@enduml")
    return "\n".join(lines)


def _render_element(elem: ActivityElement, indent: int = 0) -> list[str]:
    """Render a single diagram element."""
    prefix = "  " * indent

    if isinstance(elem, Start):
        return [f"{prefix}start"]
    if isinstance(elem, Stop):
        return [f"{prefix}stop"]
    if isinstance(elem, End):
        return [f"{prefix}end"]
    if isinstance(elem, Action):
        return [f"{prefix}{_render_action(elem)}"]
    if isinstance(elem, Arrow):
        return [f"{prefix}{_render_arrow(elem)}"]
    if isinstance(elem, If):
        return _render_if(elem, indent)
    if isinstance(elem, Switch):
        return _render_switch(elem, indent)
    if isinstance(elem, While):
        return _render_while(elem, indent)
    if isinstance(elem, Repeat):
        return _render_repeat(elem, indent)
    if isinstance(elem, Break):
        return [f"{prefix}break"]
    if isinstance(elem, Fork):
        return _render_fork(elem, indent)
    if isinstance(elem, Split):
        return _render_split(elem, indent)
    if isinstance(elem, Kill):
        return [f"{prefix}kill"]
    if isinstance(elem, Detach):
        return [f"{prefix}detach"]
    if isinstance(elem, Connector):
        return [f"{prefix}({elem.name})"]
    if isinstance(elem, Goto):
        return [f"{prefix}goto {elem.label}"]
    if isinstance(elem, ActivityLabel):
        return [f"{prefix}label {elem.name}"]
    if isinstance(elem, Swimlane):
        return [_render_swimlane(elem)]
    if isinstance(elem, Partition):
        return _render_partition(elem, indent)
    if isinstance(elem, Group):
        return _render_group(elem, indent)
    if isinstance(elem, ActivityNote):
        return _render_note(elem, indent)
    if isinstance(elem, Note):
        return _render_floating_note(elem, indent)
    raise TypeError(f"Unknown element type: {type(elem).__name__}")


def _render_action(action: Action) -> str:
    """Render an action."""
    label = render_label(action.label)

    # Shape suffix
    shape_suffix = {
        "default": ";",
        "start_end": "|",
        "receive": "<",
        "send": ">",
        "slant": "/",
        "document": "]",
        "database": "}",
    }[action.shape]

    # Color prefix (from style.background)
    color_prefix = ""
    if action.style and action.style.background:
        color = render_color(action.style.background)
        if not color.startswith("#"):
            color = f"#{color}"
        color_prefix = color

    return f"{color_prefix}:{label}{shape_suffix}"


def _render_arrow(arrow: Arrow) -> str:
    """Render an arrow."""
    # Build bracket styling if any style options are set
    # Note: thickness and plain are in the primitive but not rendered -
    # PlantUML doesn't support them in bracket syntax
    parts: list[str] = []

    # Extract color and bold from line_style
    if arrow.line_style:
        if arrow.line_style.color:
            color = render_color(arrow.line_style.color)
            if not color.startswith("#"):
                color = f"#{color}"
            parts.append(color)
        if arrow.line_style.bold:
            parts.append("bold")

    # Line pattern (solid, dashed, dotted, hidden)
    if arrow.pattern != "solid":
        parts.append(arrow.pattern)

    style_part = f"[{','.join(parts)}]" if parts else ""
    arrow_str = f"-{style_part}->"

    if arrow.label:
        label = render_label(arrow.label)
        return f"{arrow_str} {label};"
    return arrow_str


def _render_if(if_stmt: If, indent: int) -> list[str]:
    """Render an if statement."""
    prefix = "  " * indent
    lines: list[str] = []

    # if line
    if_line = f"{prefix}if ({if_stmt.condition}) then"
    if if_stmt.then_label:
        if_line += f" ({if_stmt.then_label})"
    lines.append(if_line)

    # then elements
    for elem in if_stmt.then_elements:
        lines.extend(_render_element(elem, indent + 1))

    # elseif branches
    for elseif in if_stmt.elseif_branches:
        elseif_line = f"{prefix}elseif ({elseif.condition}) then"
        if elseif.then_label:
            elseif_line += f" ({elseif.then_label})"
        lines.append(elseif_line)
        for elem in elseif.elements:
            lines.extend(_render_element(elem, indent + 1))

    # else
    if if_stmt.else_elements:
        else_line = f"{prefix}else"
        if if_stmt.else_label:
            else_line += f" ({if_stmt.else_label})"
        lines.append(else_line)
        for elem in if_stmt.else_elements:
            lines.extend(_render_element(elem, indent + 1))

    lines.append(f"{prefix}endif")
    return lines


def _render_switch(switch: Switch, indent: int) -> list[str]:
    """Render a switch statement."""
    prefix = "  " * indent
    lines: list[str] = [f"{prefix}switch ({switch.condition})"]

    for case in switch.cases:
        lines.append(f"{prefix}case ({case.label})")
        for elem in case.elements:
            lines.extend(_render_element(elem, indent + 1))

    lines.append(f"{prefix}endswitch")
    return lines


def _render_while(while_stmt: While, indent: int) -> list[str]:
    """Render a while loop."""
    prefix = "  " * indent
    lines: list[str] = []

    # while line
    while_line = f"{prefix}while ({while_stmt.condition})"
    if while_stmt.is_label:
        while_line += f" is ({while_stmt.is_label})"
    lines.append(while_line)

    # body
    for elem in while_stmt.elements:
        lines.extend(_render_element(elem, indent + 1))

    # endwhile
    endwhile_line = f"{prefix}endwhile"
    if while_stmt.endwhile_label:
        endwhile_line += f" ({while_stmt.endwhile_label})"
    lines.append(endwhile_line)
    return lines


def _render_repeat(repeat: Repeat, indent: int) -> list[str]:
    """Render a repeat loop."""
    prefix = "  " * indent
    lines: list[str] = []

    # repeat line
    repeat_line = f"{prefix}repeat"
    if repeat.start_label:
        repeat_line += f" :{repeat.start_label};"
    lines.append(repeat_line)

    # body
    for elem in repeat.elements:
        lines.extend(_render_element(elem, indent + 1))

    # backward
    if repeat.backward_action:
        lines.append(f"{prefix}backward :{repeat.backward_action};")

    # repeat while
    if repeat.condition:
        repeat_while = f"{prefix}repeat while ({repeat.condition})"
        if repeat.is_label:
            repeat_while += f" is ({repeat.is_label})"
        if repeat.not_label:
            repeat_while += f" not ({repeat.not_label})"
        lines.append(repeat_while)
    else:
        lines.append(f"{prefix}repeat while (true)")

    return lines


def _render_fork(fork: Fork, indent: int) -> list[str]:
    """Render a fork/join."""
    prefix = "  " * indent
    lines: list[str] = []

    for i, branch in enumerate(fork.branches):
        if i == 0:
            lines.append(f"{prefix}fork")
        else:
            lines.append(f"{prefix}fork again")
        for elem in branch:
            lines.extend(_render_element(elem, indent + 1))

    # end fork
    if fork.end_style == "fork":
        lines.append(f"{prefix}end fork")
    elif fork.end_style == "merge":
        lines.append(f"{prefix}end merge")
    elif fork.end_style == "or":
        lines.append(f"{prefix}end fork {{or}}")
    elif fork.end_style == "and":
        lines.append(f"{prefix}end fork {{and}}")

    return lines


def _render_split(split: Split, indent: int) -> list[str]:
    """Render a split."""
    prefix = "  " * indent
    lines: list[str] = []

    for i, branch in enumerate(split.branches):
        if i == 0:
            lines.append(f"{prefix}split")
        else:
            lines.append(f"{prefix}split again")
        for elem in branch:
            lines.extend(_render_element(elem, indent + 1))

    lines.append(f"{prefix}end split")
    return lines


def _render_swimlane(lane: Swimlane) -> str:
    """Render a swimlane."""
    if lane.color:
        color = render_color(lane.color)
        if not color.startswith("#"):
            color = f"#{color}"
        return f"|{color}|{lane.name}|"
    return f"|{lane.name}|"


def _render_partition(partition: Partition, indent: int) -> list[str]:
    """Render a partition."""
    prefix = "  " * indent
    lines: list[str] = []

    # Opening
    opening = f'{prefix}partition "{partition.name}"'
    if partition.color:
        color = render_color(partition.color)
        if not color.startswith("#"):
            color = f"#{color}"
        opening += f" {color}"
    opening += " {"
    lines.append(opening)

    # Elements
    for elem in partition.elements:
        lines.extend(_render_element(elem, indent + 1))

    lines.append(f"{prefix}}}")
    return lines


def _render_group(group: Group, indent: int) -> list[str]:
    """Render a group."""
    prefix = "  " * indent
    lines: list[str] = [f"{prefix}group {group.name}"]

    for elem in group.elements:
        lines.extend(_render_element(elem, indent + 1))

    lines.append(f"{prefix}end group")
    return lines


def _render_note(note: ActivityNote, indent: int) -> list[str]:
    """Render a note."""
    prefix = "  " * indent
    content = render_label(note.content)

    pos = note.position
    if note.floating:
        pos = f"floating note {pos}"
    else:
        pos = f"note {pos}"

    if "\n" in content:
        lines = [f"{prefix}{pos}"]
        for line in content.split("\n"):
            lines.append(f"{prefix}  {line}")
        lines.append(f"{prefix}end note")
        return lines

    return [f"{prefix}{pos}: {content}"]


def _render_floating_note(note: Note, indent: int) -> list[str]:
    """Render a floating note from common."""
    prefix = "  " * indent
    content = render_label(note.content)

    if "\n" in content:
        lines = [f"{prefix}note {note.position}"]
        for line in content.split("\n"):
            lines.append(f"{prefix}  {line}")
        lines.append(f"{prefix}end note")
        return lines

    return [f"{prefix}note {note.position}: {content}"]
