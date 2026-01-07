"""Deployment diagram primitives.

Deployment diagrams show the physical deployment of software onto hardware.
They map software artifacts (components, executables, files) to the hardware
nodes (servers, devices, cloud instances) where they run. Useful for:

- Documenting server architecture and infrastructure
- Planning cloud deployments and scaling
- Showing network topology
- Mapping services to physical/virtual machines

Key concepts:
    Node:      A computational resource (server, VM, container, device)
    Artifact:  A deployable unit (JAR, Docker image, executable)
    Nested:    Elements can be nested to show containment

All types are frozen dataclasses - immutable data with no behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, Union

from .common import ColorLike, Direction, Footer, Header, Label, LabelLike, Legend, LineStyle, sanitize_ref, Scale, Stereotype, Style

if TYPE_CHECKING:
    pass


# All deployment element types
ElementType = Literal[
    "actor",
    "agent",
    "artifact",
    "boundary",
    "card",
    "circle",
    "cloud",
    "collections",
    "component",
    "control",
    "database",
    "entity",
    "file",
    "folder",
    "frame",
    "hexagon",
    "interface",
    "label",
    "node",
    "package",
    "person",
    "process",
    "queue",
    "rectangle",
    "stack",
    "storage",
    "usecase",
]

RelationType = Literal[
    "association",  # --
    "dependency",  # ..>
    "arrow",  # -->
    "dotted_arrow",  # ..>
    "line",  # --
    "dotted",  # ..
]


@dataclass(frozen=True)
class DeploymentElement:
    """An element in the deployment diagram."""

    name: str
    type: ElementType = "node"
    alias: str | None = None
    stereotype: Stereotype | None = None
    style: Style | None = None
    # For nested elements
    elements: tuple["DeploymentDiagramElement", ...] = field(default_factory=tuple)

    @property
    def _ref(self) -> str:
        """Internal identifier used when rendering relationships.

        Returns the alias if set, otherwise the name with spaces converted
        to underscores. You don't need this directly - just pass objects to
        arrow(), connect(), etc. Exposed for debugging the PlantUML output.
        """
        if self.alias:
            return self.alias
        return sanitize_ref(self.name)


@dataclass(frozen=True)
class Relationship:
    """A relationship between deployment elements."""

    source: str
    target: str
    type: RelationType = "association"
    label: Label | None = None
    style: LineStyle | None = None
    direction: Direction | None = None
    note: Label | None = None


@dataclass(frozen=True)
class DeploymentNote:
    """A note attached to a deployment diagram element."""

    content: Label
    position: Literal["left", "right", "top", "bottom"] = "right"
    target: str | None = None
    floating: bool = False
    color: ColorLike | None = None


# Union type for all deployment diagram elements
DeploymentDiagramElement = Union[
    DeploymentElement,
    Relationship,
    DeploymentNote,
]


@dataclass(frozen=True)
class DeploymentDiagram:
    """A complete deployment diagram."""

    elements: tuple[DeploymentDiagramElement, ...] = field(default_factory=tuple)
    title: str | None = None
    caption: str | None = None
    header: Header | None = None
    footer: Footer | None = None
    legend: Legend | None = None
    scale: Scale | None = None
