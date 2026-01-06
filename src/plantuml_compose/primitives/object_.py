"""Object diagram primitives.

Frozen dataclasses representing all object diagram elements.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, Union

from .common import ColorLike, Label, LabelLike, Stereotype

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
    color: ColorLike | None = None
    fields: tuple[Field, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Map:
    """A map (associative array) in the diagram."""

    name: str
    alias: str | None = None
    color: ColorLike | None = None
    entries: tuple[MapEntry, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Relationship:
    """A relationship between objects."""

    source: str
    target: str
    type: RelationType = "association"
    label: Label | None = None
    color: ColorLike | None = None


@dataclass(frozen=True)
class ObjectNote:
    """A note attached to an object diagram element."""

    content: Label
    position: Literal["left", "right", "top", "bottom"] = "right"
    target: str | None = None
    floating: bool = False
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
