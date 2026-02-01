"""Diagram builders with context manager syntax."""

from .activity import activity_diagram
from .class_ import class_diagram
from .component import component_diagram
from .deployment import deployment_diagram
from .json_ import json_diagram, yaml_diagram
from .mindmap import mindmap_diagram
from .network import network_diagram, NodeRef
from .wbs import wbs_diagram
from .gantt import gantt_diagram, TaskRef, MilestoneRef
from .object_ import object_diagram
from .sequence import sequence_diagram
from .state import state_diagram
from .timing import timing_diagram, ParticipantRef, AnchorRef
from .usecase import usecase_diagram

__all__ = [
    "activity_diagram",
    "class_diagram",
    "component_diagram",
    "deployment_diagram",
    "gantt_diagram",
    "json_diagram",
    "mindmap_diagram",
    "network_diagram",
    "object_diagram",
    "sequence_diagram",
    "state_diagram",
    "timing_diagram",
    "usecase_diagram",
    "wbs_diagram",
    "yaml_diagram",
    # Gantt references
    "MilestoneRef",
    "TaskRef",
    # Network references
    "NodeRef",
    # Timing references
    "AnchorRef",
    "ParticipantRef",
]
