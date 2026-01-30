"""Object diagram primitives.

Object diagrams show instances of classes at a specific moment in time.
While class diagrams show the structure (types), object diagrams show
actual objects with concrete values. Useful for:

- Illustrating example data scenarios
- Debugging by showing object state
- Documenting test cases
- Explaining complex relationships with concrete examples

Key concepts:
    Object: An instance of a class with name:Type format
    Field:  An attribute with a specific value
    Map:    A key-value collection (special PlantUML feature)
    Link:   A connection between object instances

All types are frozen dataclasses - immutable data with no behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, Union

from .common import (
    ColorLike,
    Direction,
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

if TYPE_CHECKING:
    pass


# Type aliases for object diagrams
RelationType = Literal[
    "association",  # --
    "arrow",  # -->
    "extension",  # <|--
    "implementation",  # <|..
    "composition",  # *--
    "aggregation",  # o--
    "dependency",  # ..>
    "line",  # --
    "dotted",  # ..
]


@dataclass(frozen=True)
class Field:
    """A field in an object."""

    name: str
    value: str


@dataclass(frozen=True)
class MapEntry:
    """An entry in a map."""

    key: str
    value: str
    link: str | None = None  # For *-> syntax linking to another object


@dataclass(frozen=True)
class Object:
    """An object in the diagram."""

    name: str
    alias: str | None = None
    stereotype: Stereotype | None = None
    style: Style | None = None
    fields: tuple[Field, ...] = field(default_factory=tuple)

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
class Map:
    """A map (associative array) in the diagram."""

    name: str
    alias: str | None = None
    style: Style | None = None
    entries: tuple[MapEntry, ...] = field(default_factory=tuple)

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
    """A relationship between objects."""

    source: str
    target: str
    type: RelationType = "association"
    label: Label | None = None
    style: LineStyle | None = None
    direction: Direction | None = None
    note: Label | None = None


@dataclass(frozen=True)
class ObjectNote:
    """A note attached to an object diagram element."""

    content: Label
    position: Literal["left", "right", "top", "bottom"] = "right"
    target: str | None = None
    color: ColorLike | None = None


# Union type for all object diagram elements
ObjectDiagramElement = Union[
    Object,
    Map,
    Relationship,
    ObjectNote,
]


@dataclass(frozen=True)
class ObjectDiagram:
    """A complete object diagram."""

    elements: tuple[ObjectDiagramElement, ...] = field(default_factory=tuple)
    title: str | None = None
    caption: str | None = None
    header: Header | None = None
    footer: Footer | None = None
    legend: Legend | None = None
    scale: Scale | None = None
    theme: ThemeLike = None
    layout: LayoutDirection | None = None
    layout_engine: LayoutEngine | None = None
    linetype: LineType | None = None
