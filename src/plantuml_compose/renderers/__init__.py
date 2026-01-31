"""Diagram renderers - pure functions that transform primitives to PlantUML text."""

from ..primitives.activity import ActivityDiagram
from ..primitives.class_ import ClassDiagram
from ..primitives.component import ComponentDiagram
from ..primitives.deployment import DeploymentDiagram
from ..primitives.json_ import JsonDiagram, YamlDiagram
from ..primitives.mindmap import MindMapDiagram
from ..primitives.wbs import WBSDiagram
from ..primitives.object_ import ObjectDiagram
from ..primitives.sequence import SequenceDiagram
from ..primitives.state import StateDiagram
from ..primitives.usecase import UseCaseDiagram
from .activity import render_activity_diagram
from .common import link
from .class_ import render_class_diagram
from .component import render_component_diagram
from .deployment import render_deployment_diagram
from .json_ import render_json_diagram, render_yaml_diagram
from .mindmap import render_mindmap_diagram
from .wbs import render_wbs_diagram
from .object_ import render_object_diagram
from .sequence import render_sequence_diagram
from .state import render_state_diagram
from .usecase import render_usecase_diagram


def render(
    diagram: StateDiagram
    | SequenceDiagram
    | ClassDiagram
    | ActivityDiagram
    | ComponentDiagram
    | DeploymentDiagram
    | UseCaseDiagram
    | ObjectDiagram
    | JsonDiagram
    | YamlDiagram
    | MindMapDiagram
    | WBSDiagram,
) -> str:
    """Render a diagram to PlantUML text.

    This is a dispatch function that routes to the appropriate
    renderer based on the diagram type.

    Args:
        diagram: A diagram primitive (StateDiagram, SequenceDiagram, ClassDiagram, etc.)

    Returns:
        PlantUML text representation

    Raises:
        TypeError: If the diagram type is not supported
    """
    if isinstance(diagram, StateDiagram):
        return render_state_diagram(diagram)
    if isinstance(diagram, SequenceDiagram):
        return render_sequence_diagram(diagram)
    if isinstance(diagram, ClassDiagram):
        return render_class_diagram(diagram)
    if isinstance(diagram, ActivityDiagram):
        return render_activity_diagram(diagram)
    if isinstance(diagram, ComponentDiagram):
        return render_component_diagram(diagram)
    if isinstance(diagram, DeploymentDiagram):
        return render_deployment_diagram(diagram)
    if isinstance(diagram, UseCaseDiagram):
        return render_usecase_diagram(diagram)
    if isinstance(diagram, ObjectDiagram):
        return render_object_diagram(diagram)
    if isinstance(diagram, JsonDiagram):
        return render_json_diagram(diagram)
    if isinstance(diagram, YamlDiagram):
        return render_yaml_diagram(diagram)
    if isinstance(diagram, MindMapDiagram):
        return render_mindmap_diagram(diagram)
    if isinstance(diagram, WBSDiagram):
        return render_wbs_diagram(diagram)
    raise TypeError(f"Unknown diagram type: {type(diagram)}")


__all__ = [
    "link",
    "render",
    "render_activity_diagram",
    "render_class_diagram",
    "render_component_diagram",
    "render_deployment_diagram",
    "render_json_diagram",
    "render_mindmap_diagram",
    "render_object_diagram",
    "render_sequence_diagram",
    "render_state_diagram",
    "render_usecase_diagram",
    "render_wbs_diagram",
    "render_yaml_diagram",
]
