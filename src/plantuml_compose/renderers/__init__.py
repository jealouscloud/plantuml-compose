"""Diagram renderers - pure functions that transform primitives to PlantUML text."""

from ..primitives.state import StateDiagram
from .state import render_state_diagram


def render(diagram: StateDiagram) -> str:
    """Render a diagram to PlantUML text.

    This is a dispatch function that routes to the appropriate
    renderer based on the diagram type.

    Args:
        diagram: A diagram primitive (StateDiagram, etc.)

    Returns:
        PlantUML text representation

    Raises:
        TypeError: If the diagram type is not supported
    """
    if isinstance(diagram, StateDiagram):
        return render_state_diagram(diagram)
    raise TypeError(f"Unknown diagram type: {type(diagram)}")


__all__ = ["render", "render_state_diagram"]
