"""State diagram renderer.

Pure functions that transform state diagram primitives to PlantUML text.
"""

from __future__ import annotations

from ..primitives.common import (
    DiagramArrowStyle,
    ElementStyle,
    Note,
    StateDiagramStyle,
    Style,
)
from ..primitives.state import (
    CompositeState,
    ConcurrentState,
    PseudoState,
    PseudoStateKind,
    Region,
    StateDiagram,
    StateNode,
    Transition,
    _sanitize_ref,
)
from .common import (
    escape_quotes,
    render_color,
    render_label,
    render_line_style_bracket,
    render_element_style,
    render_stereotype,
)


def _state_declaration(name: str, ref: str, alias: str | None) -> str:
    """Create a state declaration, quoting when needed."""
    escaped = escape_quotes(name)
    needs_alias = alias is not None or ref != name
    if needs_alias:
        return f'state "{escaped}" as {ref}'
    return f"state {escaped}"


def _note_prefix(position: str, anchor: str | None = None) -> str:
    """Map Note.position to the correct PlantUML prefix."""
    if anchor:
        # Only these positions support anchoring in state diagrams
        if position in ("left", "right", "top", "bottom"):
            return f"note {position} of {anchor}"
        raise ValueError(
            f"Note position '{position}' cannot be anchored to a state. "
            f"Use 'left', 'right', 'top', or 'bottom'."
        )
    # Unanchored notes
    if position == "floating":
        return "floating note"
    if position == "on link":
        return "note on link"
    return f"note {position}"


def _render_note_lines(prefix: str, text: str) -> list[str]:
    """Render either single-line or block note syntax."""
    if "\n" in text:
        lines = [prefix]
        lines.extend(f"  {line}" for line in text.split("\n"))
        lines.append("end note")
        return lines
    return [f"{prefix}: {text}"]


def _render_floating_note(note: Note, note_id: int = 0) -> list[str]:
    """Render a top-level note element.

    For position="floating", uses PlantUML's `note "content" as N1` syntax.
    For other positions (left, right, etc.), uses `note position: content`.
    """
    text = render_label(note.content)

    if note.position == "floating":
        # PlantUML floating note syntax: note "content" as alias
        # or for multiline: note as alias\n...\nend note
        alias = f"N{note_id}"
        if "\n" in text:
            lines = [f"note as {alias}"]
            lines.extend(f"  {line}" for line in text.split("\n"))
            lines.append("end note")
            return lines
        return [f'note "{escape_quotes(text)}" as {alias}']

    prefix = _note_prefix(note.position)
    return _render_note_lines(prefix, text)


def render_state_diagram(diagram: StateDiagram) -> str:
    """Render a complete state diagram to PlantUML text."""
    lines: list[str] = ["@startuml"]

    # Style block comes first (after @startuml)
    if diagram.style:
        lines.extend(_render_diagram_style(diagram.style))

    if diagram.title:
        if "\n" in diagram.title:
            lines.append("title")
            for title_line in diagram.title.split("\n"):
                lines.append(f"  {escape_quotes(title_line)}")
            lines.append("end title")
        else:
            lines.append(f"title {escape_quotes(diagram.title)}")

    if diagram.hide_empty_description:
        lines.append("hide empty description")

    floating_note_id = 0
    for elem in diagram.elements:
        if isinstance(elem, Note):
            lines.extend(_render_floating_note(elem, floating_note_id))
            if elem.position == "floating":
                floating_note_id += 1
        else:
            lines.extend(_render_element(elem))

    lines.append("@enduml")
    return "\n".join(lines)


def _render_diagram_style(style: StateDiagramStyle) -> list[str]:
    """Render a typed StateDiagramStyle to PlantUML <style> block."""
    # Collect stateDiagram block content
    diagram_props: list[str] = []

    # Root-level properties
    if style.background:
        diagram_props.append(
            f"  BackgroundColor {render_color(style.background)}"
        )
    if style.font_name:
        diagram_props.append(f"  FontName {style.font_name}")
    if style.font_size:
        diagram_props.append(f"  FontSize {style.font_size}")
    if style.font_color:
        diagram_props.append(f"  FontColor {render_color(style.font_color)}")

    # State element styles
    if style.state:
        diagram_props.extend(
            _render_element_style("state", style.state, indent=2)
        )

    # Arrow styles
    if style.arrow:
        diagram_props.extend(_render_arrow_style(style.arrow))

    # Note element styles
    if style.note:
        diagram_props.extend(
            _render_element_style("note", style.note, indent=2)
        )

    # Collect document block content (for title)
    document_props: list[str] = []
    if style.title:
        document_props.extend(
            _render_element_style("title", style.title, indent=2)
        )

    # Only emit style block if there's content
    if not diagram_props and not document_props:
        return []

    lines: list[str] = ["<style>"]

    # Emit stateDiagram block if it has content
    if diagram_props:
        lines.append("stateDiagram {")
        lines.extend(diagram_props)
        lines.append("}")

    # Emit document block for title styling (separate from stateDiagram)
    if document_props:
        lines.append("document {")
        lines.extend(document_props)
        lines.append("}")

    lines.append("</style>")
    return lines


def _render_element_style(
    selector: str, style: ElementStyle, indent: int = 2
) -> list[str]:
    """Render an ElementStyle as a nested block. Returns empty list if no properties."""
    props: list[str] = []
    prefix = " " * indent
    inner_prefix = " " * (indent + 2)

    if style.background:
        props.append(
            f"{inner_prefix}BackgroundColor {render_color(style.background)}"
        )
    if style.line_color:
        props.append(
            f"{inner_prefix}LineColor {render_color(style.line_color)}"
        )
    if style.font_color:
        props.append(
            f"{inner_prefix}FontColor {render_color(style.font_color)}"
        )
    if style.font_name:
        props.append(f"{inner_prefix}FontName {style.font_name}")
    if style.font_size:
        props.append(f"{inner_prefix}FontSize {style.font_size}")
    if style.font_style:
        props.append(f"{inner_prefix}FontStyle {style.font_style}")
    if style.round_corner is not None:
        props.append(f"{inner_prefix}RoundCorner {style.round_corner}")
    if style.line_thickness is not None:
        props.append(f"{inner_prefix}LineThickness {style.line_thickness}")

    # Only return block if there are properties
    if not props:
        return []

    return [f"{prefix}{selector} {{"] + props + [f"{prefix}}}"]


def _render_arrow_style(style: DiagramArrowStyle) -> list[str]:
    """Render a DiagramArrowStyle as a nested block. Returns empty list if no properties."""
    props: list[str] = []

    if style.line_color:
        props.append(f"    LineColor {render_color(style.line_color)}")
    if style.line_thickness is not None:
        props.append(f"    LineThickness {style.line_thickness}")
    if style.line_pattern:
        props.append(f"    LineStyle {style.line_pattern}")

    # Only return block if there are properties
    if not props:
        return []

    return ["  arrow {"] + props + ["  }"]


def _render_element(
    elem: StateNode | PseudoState | Transition | CompositeState | ConcurrentState,
) -> list[str]:
    """Render a single diagram element (except Note, handled separately)."""
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
    raise TypeError(f"Unknown element type: {type(elem).__name__}")


def _render_state_node(state: StateNode) -> list[str]:
    """Render a state node declaration."""
    lines: list[str] = []
    ref = state._ref
    style_obj = state.style if isinstance(state.style, Style) else None

    # Build declaration
    decl = _state_declaration(state.name, ref, state.alias)

    # Add stereotype if present
    if style_obj and style_obj.stereotype:
        decl += f" {render_stereotype(style_obj.stereotype)}"

    # Add inline style if present
    if state.style:
        style_str = render_element_style(state.style)
        if style_str:
            decl += f" {style_str}"

    lines.append(decl)

    # Description (if any)
    if state.description:
        lines.append(f"{ref} : {render_label(state.description)}")

    # Note (if any)
    if state.note:
        lines.extend(
            _render_note_lines(
                _note_prefix(state.note.position, ref),
                render_label(state.note.content),
            )
        )

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
        escaped_name = escape_quotes(pseudo.name)
        sanitized = _sanitize_ref(pseudo.name)
        # Use alias syntax so transitions can reference the sanitized name
        decl = f'state "{escaped_name}" as {sanitized} <<{pseudo.kind.value}>>'
        if pseudo.style:
            style_str = render_element_style(pseudo.style)
            if style_str:
                decl += f" {style_str}"
        return [decl]

    return []


def _render_transition(trans: Transition) -> list[str]:
    """Render a transition between states."""
    lines: list[str] = []

    # Convert source/target to PlantUML syntax
    src = _state_ref_to_plantuml(trans.source)
    tgt = _state_ref_to_plantuml(trans.target)

    # Build arrow
    arrow = _build_arrow(trans)

    # Build label
    label = _build_transition_label(trans)
    label_str = f" : {label}" if label else ""

    lines.append(f"{src} {arrow} {tgt}{label_str}")

    # Note on link (if any)
    if trans.note:
        note_text = render_label(trans.note)
        if "\n" in note_text:
            # Multi-line note
            lines.append("note on link")
            for note_line in note_text.split("\n"):
                lines.append(f"  {note_line}")
            lines.append("end note")
        else:
            # Single-line note
            lines.append(f"note on link: {note_text}")

    return lines


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
        dir_mod = trans.direction[0]  # First letter: u, d, l, r

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
    ref = comp._ref
    style_obj = comp.style if isinstance(comp.style, Style) else None

    # Build opening line
    opening = _state_declaration(comp.name, ref, comp.alias)

    # Add stereotype
    if style_obj and style_obj.stereotype:
        opening += f" {render_stereotype(style_obj.stereotype)}"

    # Add inline style
    if comp.style:
        style_str = render_element_style(comp.style)
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
        lines.extend(
            _render_note_lines(
                _note_prefix(comp.note.position, ref),
                render_label(comp.note.content),
            )
        )

    return lines


def _render_concurrent_state(conc: ConcurrentState) -> list[str]:
    """Render a concurrent state with parallel regions."""
    lines: list[str] = []
    ref = conc._ref
    style_obj = conc.style if isinstance(conc.style, Style) else None

    # Build opening line
    opening = _state_declaration(conc.name, ref, conc.alias)

    # Add stereotype
    if style_obj and style_obj.stereotype:
        opening += f" {render_stereotype(style_obj.stereotype)}"

    # Add inline style
    if conc.style:
        style_str = render_element_style(conc.style)
        if style_str:
            opening += f" {style_str}"

    lines.append(f"{opening} {{")

    # Regions (separated by -- or ||)
    # Convert user-friendly names to PlantUML syntax
    separator = "--" if conc.separator == "horizontal" else "||"
    for i, region in enumerate(conc.regions):
        if i > 0:
            lines.append(f"  {separator}")
        lines.extend(_render_region(region))

    # Closing
    lines.append("}")

    # Note (if any)
    if conc.note:
        lines.extend(
            _render_note_lines(
                _note_prefix(conc.note.position, ref),
                render_label(conc.note.content),
            )
        )

    return lines


def _render_region(region: Region) -> list[str]:
    """Render a single region within a concurrent state."""
    lines: list[str] = []
    for elem in region.elements:
        for line in _render_element(elem):
            lines.append(f"  {line}")
    return lines
