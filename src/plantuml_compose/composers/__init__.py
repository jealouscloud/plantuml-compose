"""Declarative composition API for PlantUML diagrams.

New user-facing API that replaces the builder pattern with pure
factory functions and explicit registration.

Example:
    from plantuml_compose.composers import component_diagram
    from plantuml_compose import render

    d = component_diagram(title="Architecture")
    el = d.elements
    c = d.connections

    api = el.component("API")
    db = el.database("PostgreSQL")
    d.add(api, db)
    d.connect(c.arrow(api, db, "queries"))

    print(render(d))
"""

from .activity import activity_diagram
from .class_ import class_diagram
from .component import component_diagram
from .deployment import deployment_diagram
from .gantt import gantt_diagram
from .json_ import json_diagram, yaml_diagram
from .mindmap import mindmap_diagram
from .network import network_diagram
from .object_ import object_diagram
from .salt import salt_diagram
from .sequence import sequence_diagram
from .state import state_diagram
from .timing import timing_diagram
from .usecase import usecase_diagram
from .wbs import wbs_diagram

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
    "salt_diagram",
    "sequence_diagram",
    "state_diagram",
    "timing_diagram",
    "usecase_diagram",
    "wbs_diagram",
    "yaml_diagram",
]
