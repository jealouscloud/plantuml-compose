"""State diagram renderer.

Pure functions that transform state diagram primitives to PlantUML text.
"""

from __future__ import annotations

from ..primitives.common import Note
from ..primitives.state import (
    CompositeState,
    ConcurrentState,
    PseudoState,
    PseudoStateKind,
    Region,
    StateDiagram,
    StateNode,
    Transition,
)
from .common import render_label, render_line_style_bracket, render_state_style, render_stereotype


def render_state_diagram(diagram: StateDiagram) -> str:
    """Render a complete state diagram to PlantUML text."""
    lines: list[str] = ["@startuml"]

    if diagram.title:
        lines.append(f"title {diagram.title}")

    if diagram.hide_empty_description:
        lines.append("hide empty description")

    for elem in diagram.elements:
        lines.extend(_render_element(elem))

    lines.append("@enduml")
    return "\n".join(lines)


def _render_element(
    elem: StateNode | PseudoState | Transition | CompositeState | ConcurrentState | Note,
) -> list[str]:
    """Render a single diagram element."""
    if isinstance(elem, StateNode):
        return _render_state_node(elem)
    if isinstance(elem, PseudoState):
        return _render_pseudo_state(elem)
    if isinstance(elem, Transition):
        return _render_transition(elem)
    if isinstance(elem, CompositeState):
        return _render_composite_state(elem)
    if isinstance(elem, ConcurrentState):
        return _render_concurrent_state(elem)
    if isinstance(elem, Note):
        return [f"note: {render_label(elem.content)}"]
    return []


def _render_state_node(state: StateNode) -> list[str]:
    """Render a state node declaration."""
    lines: list[str] = []
    ref = state.ref

    # Build declaration
    if state.alias or " " in state.name:
        decl = f'state "{state.name}" as {ref}'
    else:
        decl = f"state {state.name}"

    # Add stereotype if present
    if state.style and state.style.stereotype:
        decl += f" {render_stereotype(state.style.stereotype)}"

    # Add inline style if present
    if state.style:
        style_str = render_state_style(state.style)
        if style_str:
            decl += f" {style_str}"

    lines.append(decl)

    # Description (if any)
    if state.description:
        lines.append(f"{ref} : {render_label(state.description)}")

    # Note (if any)
    if state.note:
        pos = state.note.position.value
        lines.append(f"note {pos} of {ref}: {render_label(state.note.content)}")

    return lines


def _render_pseudo_state(pseudo: PseudoState) -> list[str]:
    """Render a pseudo-state declaration."""
    # Initial and final are rendered in transitions, not as declarations
    if pseudo.kind in (PseudoStateKind.INITIAL, PseudoStateKind.FINAL):
        return []

    # History states are also rendered in transitions
    if pseudo.kind in (PseudoStateKind.HISTORY, PseudoStateKind.DEEP_HISTORY):
        return []

    # Other pseudo-states need explicit declarations with stereotypes
    if pseudo.name:
        decl = f"state {pseudo.name} <<{pseudo.kind.value}>>"
        if pseudo.style:
            style_str = render_state_style(pseudo.style)
            if style_str:
                decl += f" {style_str}"
        return [decl]

    return []


def _render_transition(trans: Transition) -> list[str]:
    """Render a transition between states."""
    # Convert source/target to PlantUML syntax
    src = _state_ref_to_plantuml(trans.source)
    tgt = _state_ref_to_plantuml(trans.target)

    # Build arrow
    arrow = _build_arrow(trans)

    # Build label
    label = _build_transition_label(trans)
    label_str = f" : {label}" if label else ""

    return [f"{src} {arrow} {tgt}{label_str}"]


def _state_ref_to_plantuml(ref: str) -> str:
    """Convert a state reference to PlantUML syntax."""
    if ref in ("initial", "final", "[*]"):
        return "[*]"
    if ref == "history":
        return "[H]"
    if ref == "deep_history":
        return "[H*]"
    return ref


def _build_arrow(trans: Transition) -> str:
    """Build the arrow string for a transition."""
    # Direction modifier
    dir_mod = ""
    if trans.direction:
        dir_mod = trans.direction.value[0]  # First letter: u, d, l, r

    # Style modifier
    style_mod = ""
    if trans.style:
        style_mod = render_line_style_bracket(trans.style)

    # Construct arrow
    if style_mod:
        return f"-{style_mod}{dir_mod}->"
    if dir_mod:
        return f"-{dir_mod}->"
    return "-->"


def _build_transition_label(trans: Transition) -> str:
    """Build the label string for a transition."""
    parts: list[str] = []

    # Main label first
    if trans.label:
        parts.append(render_label(trans.label))

    # Trigger (event name)
    if trans.trigger:
        parts.append(trans.trigger)

    # Guard condition
    if trans.guard:
        parts.append(f"[{trans.guard}]")

    # Effect (action)
    if trans.effect:
        parts.append(f"/ {trans.effect}")

    return " ".join(parts)


def _render_composite_state(comp: CompositeState) -> list[str]:
    """Render a composite state with nested elements."""
    lines: list[str] = []
    ref = comp.ref

    # Build opening line
    if comp.alias or " " in comp.name:
        opening = f'state "{comp.name}" as {ref}'
    else:
        opening = f"state {ref}"

    # Add stereotype
    if comp.style and comp.style.stereotype:
        opening += f" {render_stereotype(comp.style.stereotype)}"

    # Add inline style
    if comp.style:
        style_str = render_state_style(comp.style)
        if style_str:
            opening += f" {style_str}"

    lines.append(f"{opening} {{")

    # Nested elements (indented)
    for elem in comp.elements:
        for line in _render_element(elem):
            lines.append(f"  {line}")

    # Closing
    lines.append("}")

    # Note (if any)
    if comp.note:
        pos = comp.note.position.value
        lines.append(f"note {pos} of {ref}: {render_label(comp.note.content)}")

    return lines


def _render_concurrent_state(conc: ConcurrentState) -> list[str]:
    """Render a concurrent state with parallel regions."""
    lines: list[str] = []
    ref = conc.ref

    # Build opening line
    if conc.alias or " " in conc.name:
        opening = f'state "{conc.name}" as {ref}'
    else:
        opening = f"state {ref}"

    # Add stereotype
    if conc.style and conc.style.stereotype:
        opening += f" {render_stereotype(conc.style.stereotype)}"

    # Add inline style
    if conc.style:
        style_str = render_state_style(conc.style)
        if style_str:
            opening += f" {style_str}"

    lines.append(f"{opening} {{")

    # Regions (separated by --)
    for i, region in enumerate(conc.regions):
        if i > 0:
            lines.append("  --")
        lines.extend(_render_region(region))

    # Closing
    lines.append("}")

    # Note (if any)
    if conc.note:
        pos = conc.note.position.value
        lines.append(f"note {pos} of {ref}: {render_label(conc.note.content)}")

    return lines


def _render_region(region: Region) -> list[str]:
    """Render a single region within a concurrent state."""
    lines: list[str] = []
    for elem in region.elements:
        for line in _render_element(elem):
            lines.append(f"  {line}")
    return lines
