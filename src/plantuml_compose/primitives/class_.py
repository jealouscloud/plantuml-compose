"""Class diagram primitives.

All types are frozen dataclasses - immutable data with no behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, TypeAlias

from .common import (
    ColorLike,
    Direction,
    Label,
    LabelLike,
    LineStyleLike,
    Note,
    Stereotype,
    StyleLike,
)


# Class element types
ClassType = Literal[
    "class",
    "abstract",
    "interface",
    "annotation",
    "enum",
    "entity",
    "exception",
    "metaclass",
    "protocol",
    "struct",
    "circle",
    "diamond",
]

# Member visibility
Visibility = Literal["+", "-", "#", "~"]

# Member modifiers
MemberModifier = Literal["static", "abstract", "field", "method"]

# Relationship types
RelationType = Literal[
    "extension",  # <|--
    "implementation",  # <|..
    "composition",  # *--
    "aggregation",  # o--
    "association",  # -->
    "dependency",  # ..>
    "line",  # --
    "dotted",  # ..
]

# Package styles
PackageStyle = Literal[
    "package",
    "node",
    "rectangle",
    "folder",
    "frame",
    "cloud",
    "database",
]

# Separator types within classes
SeparatorStyle = Literal["solid", "dotted", "double", "underline"]


def _sanitize_class_ref(name: str) -> str:
    """Create a PlantUML-friendly identifier from a class name."""
    if name.isidentifier():
        return name
    sanitized = name.replace(" ", "_")
    for char in "\"'`()[]{}:;,.<>!@#$%^&*+=|\\/?~-":
        sanitized = sanitized.replace(char, "")
    return sanitized or "_"


@dataclass(frozen=True)
class Member:
    """A class member (field or method)."""

    name: str
    visibility: Visibility | None = None
    type: str | None = None  # Return type for methods, field type for fields
    modifier: MemberModifier | None = None  # static, abstract, etc.
    is_method: bool = False  # True if method, False if field


@dataclass(frozen=True)
class Separator:
    """A separator line within a class definition."""

    style: SeparatorStyle = "solid"
    label: str | None = None


@dataclass(frozen=True)
class ClassNode:
    """A class in a class diagram."""

    name: str
    alias: str | None = None
    type: ClassType = "class"
    generics: str | None = None  # e.g., "T extends Element"
    stereotype: Stereotype | None = None
    members: tuple[Member | Separator, ...] = field(default_factory=tuple)
    style: StyleLike | None = None
    note: Note | None = None
    # For enums
    enum_values: tuple[str, ...] | None = None

    @property
    def _ref(self) -> str:
        """Internal: Reference name for use in relationships."""
        if self.alias:
            return self.alias
        return _sanitize_class_ref(self.name)


@dataclass(frozen=True)
class Relationship:
    """A relationship between classes."""

    source: str  # Class reference
    target: str  # Class reference
    type: RelationType = "association"
    label: LabelLike | None = None
    source_cardinality: str | None = None  # e.g., "1", "0..*"
    target_cardinality: str | None = None
    source_label: str | None = None  # Label at source end
    target_label: str | None = None  # Label at target end
    style: LineStyleLike | None = None
    direction: Direction | None = None
    note: LabelLike | None = None
    # Arrow direction indicator in label
    label_direction: Literal["<", ">", None] = None


@dataclass(frozen=True)
class Package:
    """A package containing classes."""

    name: str
    alias: str | None = None
    style: PackageStyle = "package"
    color: ColorLike | None = None
    elements: tuple["ClassDiagramElement", ...] = field(default_factory=tuple)

    @property
    def _ref(self) -> str:
        """Internal: Reference name for use in relationships."""
        if self.alias:
            return self.alias
        return _sanitize_class_ref(self.name)


@dataclass(frozen=True)
class Together:
    """A together block for layout grouping.

    Classes in a together block are laid out close to each other.
    """

    elements: tuple["ClassDiagramElement", ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ClassNote:
    """A note in a class diagram."""

    content: LabelLike
    position: Literal["left", "right", "top", "bottom"] = "right"
    target: str | None = None  # Class reference to attach to
    # For notes on specific members
    member: str | None = None  # e.g., "method(int)" for method overloads


@dataclass(frozen=True)
class HideShow:
    """A hide/show/remove directive.

    Used to control visibility of elements.
    """

    action: Literal["hide", "show", "remove", "restore"]
    target: str  # What to hide/show (e.g., "empty members", "ClassName methods", "$tag")


@dataclass(frozen=True)
class ClassDiagram:
    """Complete class diagram."""

    elements: tuple["ClassDiagramElement", ...] = field(default_factory=tuple)
    title: str | None = None
    # Diagram-level directives
    hide_empty_members: bool = False
    hide_circle: bool = False
    namespace_separator: str | None = None  # e.g., "::" or "none"


# Type alias for elements that can appear in a class diagram
ClassDiagramElement: TypeAlias = (
    ClassNode
    | Relationship
    | Package
    | Together
    | ClassNote
    | HideShow
    | Note
)
