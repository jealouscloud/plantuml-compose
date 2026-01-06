"""Deployment diagram primitives.

Frozen dataclasses representing all deployment diagram elements.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, Union

from .common import ColorLike, Label, LabelLike, Stereotype

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
    color: ColorLike | None = None
    # For nested elements
    elements: tuple["DeploymentDiagramElement", ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Relationship:
    """A relationship between deployment elements."""

    source: str
    target: str
    type: RelationType = "association"
    label: Label | None = None
    color: ColorLike | None = None


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
