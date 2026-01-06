"""Use case diagram primitives.

Frozen dataclasses representing all use case diagram elements.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, Union

from .common import ColorLike, Label, LabelLike, Stereotype

if TYPE_CHECKING:
    pass


# Type aliases for use case diagrams
ActorStyle = Literal["default", "awesome", "hollow"]
RelationType = Literal[
    "association",  # ->
    "arrow",  # -->
    "extension",  # <|--
    "include",  # .> with <<include>>
    "extends",  # .> with <<extends>>
    "dependency",  # ..>
    "line",  # --
]
ContainerType = Literal["rectangle", "package"]


@dataclass(frozen=True)
class Actor:
    """An actor in the diagram."""

    name: str
    alias: str | None = None
    stereotype: Stereotype | None = None
    color: ColorLike | None = None
    business: bool = False  # Business variant (actor/)


@dataclass(frozen=True)
class UseCase:
    """A use case in the diagram."""

    name: str
    alias: str | None = None
    stereotype: Stereotype | None = None
    color: ColorLike | None = None
    business: bool = False  # Business variant (usecase/)


@dataclass(frozen=True)
class Container:
    """A container (rectangle/package) grouping elements."""

    name: str
    type: ContainerType = "rectangle"
    elements: tuple["UseCaseDiagramElement", ...] = field(default_factory=tuple)
    stereotype: Stereotype | None = None
    color: ColorLike | None = None


@dataclass(frozen=True)
class Relationship:
    """A relationship in the diagram."""

    source: str
    target: str
    type: RelationType = "association"
    label: Label | None = None
    color: ColorLike | None = None


@dataclass(frozen=True)
class UseCaseNote:
    """A note attached to a use case diagram element."""

    content: Label
    position: Literal["left", "right", "top", "bottom"] = "right"
    target: str | None = None
    floating: bool = False
    color: ColorLike | None = None


# Union type for all use case diagram elements
UseCaseDiagramElement = Union[
    Actor,
    UseCase,
    Container,
    Relationship,
    UseCaseNote,
]


@dataclass(frozen=True)
class UseCaseDiagram:
    """A complete use case diagram."""

    elements: tuple[UseCaseDiagramElement, ...] = field(default_factory=tuple)
    title: str | None = None
    actor_style: ActorStyle | None = None
    left_to_right: bool = False
