"""Use case diagram primitives.

Use case diagrams show what a system does from the users' perspective.
They capture functional requirements by showing who (actors) does what
(use cases) with the system. Useful for:

- Gathering and documenting requirements
- Defining system scope and boundaries
- Identifying user roles and their goals
- Planning feature development

Key concepts:
    Actor:    Someone or something that interacts with the system
    Use Case: A goal or function the system provides (shown as oval)
    Include:  A use case that's always part of another
    Extends:  Optional behavior that may extend a use case

All types are frozen dataclasses - immutable data with no behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, Union

from .common import (
    ColorLike,
    Direction,
    EmbeddableContent,
    Footer,
    Header,
    Label,
    LayoutDirection,
    LayoutEngine,
    Legend,
    LineType,
    LineStyle,
    sanitize_ref,
    Scale,
    Stereotype,
    Style,
    ThemeLike,
)
from .styles import UseCaseDiagramStyle

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
ContainerType = Literal[
    "artifact", "card", "cloud", "component", "database",
    "file", "folder", "frame", "hexagon", "node",
    "package", "process", "queue", "rectangle", "stack", "storage",
]


@dataclass(frozen=True)
class Actor:
    """An actor in the diagram."""

    name: str
    alias: str | None = None
    stereotype: Stereotype | None = None
    style: Style | None = None
    business: bool = False  # Business variant (actor/)

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
class UseCase:
    """A use case in the diagram."""

    name: str
    alias: str | None = None
    stereotype: Stereotype | None = None
    style: Style | None = None
    business: bool = False  # Business variant (usecase/)

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


GenericElementType = Literal[
    "agent", "boundary", "circle", "collections",
    "control", "entity", "interface", "label", "person",
]


@dataclass(frozen=True)
class GenericElement:
    """A universal leaf element (agent, boundary, circle, etc.)."""

    name: str
    type: GenericElementType = "agent"
    alias: str | None = None
    stereotype: Stereotype | None = None
    style: Style | None = None

    @property
    def _ref(self) -> str:
        if self.alias:
            return self.alias
        return sanitize_ref(self.name)


@dataclass(frozen=True)
class Container:
    """A container grouping elements."""

    name: str
    type: ContainerType = "rectangle"
    elements: tuple["UseCaseDiagramElement", ...] = field(default_factory=tuple)
    alias: str | None = None
    stereotype: Stereotype | None = None
    style: Style | None = None

    @property
    def _ref(self) -> str:
        if self.alias:
            return self.alias
        return sanitize_ref(self.name)


@dataclass(frozen=True)
class Relationship:
    """A relationship in the diagram."""

    source: str
    target: str
    type: RelationType = "association"
    label: Label | None = None
    style: LineStyle | None = None
    direction: Direction | None = None
    length: int | None = None  # Arrow dash count (None = default 2)
    note: Label | None = None
    # Arrow head customization
    left_head: str | None = None  # e.g., "o", "*", "#", etc.
    right_head: str | None = None


@dataclass(frozen=True)
class UseCaseNote:
    """A note attached to a use case diagram element."""

    content: EmbeddableContent
    position: Literal["left", "right", "top", "bottom"] = "right"
    target: str | None = None
    color: ColorLike | None = None


# Union type for all use case diagram elements
UseCaseDiagramElement = Union[
    Actor,
    UseCase,
    GenericElement,
    Container,
    Relationship,
    UseCaseNote,
]


@dataclass(frozen=True)
class UseCaseDiagram:
    """A complete use case diagram."""

    elements: tuple[UseCaseDiagramElement, ...] = field(default_factory=tuple)
    title: str | None = None
    mainframe: str | None = None
    caption: str | None = None
    header: Header | None = None
    footer: Footer | None = None
    legend: Legend | None = None
    scale: Scale | None = None
    theme: ThemeLike = None
    diagram_style: UseCaseDiagramStyle | None = None
    actor_style: ActorStyle | None = None
    layout: LayoutDirection | None = None
    layout_engine: LayoutEngine | None = None
    linetype: LineType | None = None
