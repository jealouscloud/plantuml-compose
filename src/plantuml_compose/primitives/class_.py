"""Class diagram primitives.

Class diagrams show the static structure of a system: the classes, their
attributes and methods, and the relationships between them. They're the
most common UML diagram type, useful for:

- Modeling object-oriented designs
- Documenting APIs and data structures
- Showing inheritance and interface hierarchies
- Visualizing database schemas

Key concepts:
    Class:        A blueprint defining attributes and methods
    Interface:    A contract specifying required methods
    Relationship: Connection between classes (inheritance, composition, etc.)
    Package:      A namespace grouping related classes

All types are frozen dataclasses - immutable data with no behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, TypeAlias

from .common import (
    ColorLike,
    Direction,
    Footer,
    Header,
    LabelLike,
    Legend,
    Scale,
    LineStyleLike,
    Note,
    Stereotype,
    StyleLike,
)


# Class element types - determines the visual shape and semantics
ClassType = Literal[
    "class",  # Standard class box
    "abstract",  # Abstract class (italicized name)
    "interface",  # Interface (<<interface>> stereotype)
    "annotation",  # Java-style annotation (@interface)
    "enum",  # Enumeration with values
    "entity",  # JPA/database entity
    "exception",  # Exception class
    "metaclass",  # Python metaclass
    "protocol",  # Python protocol (typing.Protocol)
    "struct",  # C-style struct
    "circle",  # Shorthand circle notation
    "diamond",  # Shorthand diamond notation
]

# Member visibility - human-readable names
Visibility = Literal[
    "public",  # Visible to all classes
    "private",  # Visible only within the declaring class
    "protected",  # Visible to the class and its subclasses
    "package",  # Visible within the same package
]

# Visibility options for validation errors
VISIBILITY_OPTIONS: dict[str, str] = {
    "public": "Accessible from anywhere (UML: +)",
    "private": "Only accessible within this class (UML: -)",
    "protected": "Accessible from this class and subclasses (UML: #)",
    "package": "Accessible within the same package (UML: ~)",
}

# Internal mapping for rendering to PlantUML syntax
_VISIBILITY_TO_SYMBOL: dict[str, str] = {
    "public": "+",
    "private": "-",
    "protected": "#",
    "package": "~",
}

# Member modifiers affecting display
MemberModifier = Literal[
    "static",  # Underlined, class-level member
    "abstract",  # Italicized, must be implemented by subclasses
    "field",  # Explicit field marker
    "method",  # Explicit method marker
]

# Relationship types - each renders with a distinct arrow style
RelationType = Literal[
    "extension",  # <|-- Inheritance (solid line, closed arrow)
    "implementation",  # <|.. Interface implementation (dotted, closed arrow)
    "composition",  # *-- Strong ownership (solid line, filled diamond)
    "aggregation",  # o-- Weak ownership (solid line, hollow diamond)
    "association",  # --> Uses/references (solid line, open arrow)
    "dependency",  # ..> Depends on (dotted line, open arrow)
    "line",  # -- Plain connection (no arrowhead)
    "dotted",  # .. Dotted connection (no arrowhead)
]

# Package visual styles - container appearance
PackageStyle = Literal[
    "package",  # Standard UML package (tab folder)
    "node",  # 3D box (deployment diagram style)
    "rectangle",  # Plain rectangle
    "folder",  # Folder icon
    "frame",  # Frame with title bar
    "cloud",  # Cloud shape
    "database",  # Cylinder shape
]

# Separator line styles within class definitions
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
    """A field or method within a class.

    Members are shown inside the class box. By convention, fields appear
    above the separator line and methods below it.

        name:       Member name (e.g., "count" or "getName()")
        visibility: Access level (+, -, #, ~)
        type:       Data type or return type
        modifier:   "static", "abstract", etc.
        is_method:  True for methods, False for fields

    PlantUML renders visibility as symbols:
        + public, - private, # protected, ~ package
    """

    name: str
    visibility: Visibility | None = None
    type: str | None = None  # Return type for methods, field type for fields
    modifier: MemberModifier | None = None  # static, abstract, etc.
    is_method: bool = False  # True if method, False if field


@dataclass(frozen=True)
class Separator:
    """A visual divider line within a class definition.

    Separators group related members. They can have labels to identify
    the section (e.g., "-- Private methods --").

        style: Line style ("solid", "dotted", "double", "underline")
        label: Optional section label
    """

    style: SeparatorStyle = "solid"
    label: str | None = None


@dataclass(frozen=True)
class ClassNode:
    """A class, interface, enum, or other type in a class diagram.

    The main building block of class diagrams. Each ClassNode represents
    a type definition with optional members, generics, and styling.

        name:        Type name (e.g., "User", "List<T>")
        alias:       Short reference for relationships
        type:        Kind of type ("class", "interface", "enum", etc.)
        generics:    Generic parameters (e.g., "T extends Element")
        stereotype:  UML stereotype marker (e.g., <<service>>)
        members:     Fields and methods
        style:       Visual styling
        note:        Attached annotation
        enum_values: For enums, the list of values
    """

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

    def __post_init__(self) -> None:
        """Validate field combinations."""
        if self.enum_values and self.members:
            raise ValueError(
                f"ClassNode '{self.name}' cannot have both enum_values and members. "
                "Use enum_values for simple enums, or members for enums with methods/fields."
            )

    @property
    def _ref(self) -> str:
        """Internal: Reference name for use in relationships."""
        if self.alias:
            return self.alias
        return _sanitize_class_ref(self.name)


@dataclass(frozen=True)
class Relationship:
    """A relationship (arrow) between classes.

    Relationships show how classes are connected. The type determines
    both the semantics and the arrow style:

        extension:      Inheritance (A extends B)
        implementation: Interface implementation (A implements B)
        composition:    Strong ownership (B cannot exist without A)
        aggregation:    Weak ownership (B can exist independently)
        association:    General connection (A uses B)
        dependency:     A depends on B (e.g., parameter type)

    Labels at source/target ends can show cardinality, role names, or both.

        source/target:       Class references
        source/target_label: Text at each end (cardinality, role, or both)
        label:               Relationship name (on the line)
        label_direction:     Arrow in label ("<" or ">")
    """

    source: str  # Class reference
    target: str  # Class reference
    type: RelationType = "association"
    label: LabelLike | None = None
    source_label: str | None = None  # Label at source end (cardinality, role, etc.)
    target_label: str | None = None  # Label at target end
    style: LineStyleLike | None = None
    direction: Direction | None = None
    note: LabelLike | None = None
    # Arrow direction indicator in label
    label_direction: Literal["<", ">", None] = None


@dataclass(frozen=True)
class Package:
    """A namespace container for grouping related classes.

    Packages organize classes into logical groups and can be nested.
    The visual style can be customized to represent different concepts:

        name:     Package name (e.g., "com.example.models")
        alias:    Short reference name
        style:    Visual shape ("package", "folder", "cloud", etc.)
        color:    Background color
        elements: Classes and nested packages inside
    """

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
    """A layout hint to keep classes visually grouped.

    Classes in a "together" block are placed adjacent to each other,
    useful when you want related classes close together regardless of
    their relationships.
    """

    elements: tuple["ClassDiagramElement", ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ClassNote:
    """A note annotation in a class diagram.

    Notes can be attached to classes, specific members, or float freely.

        content:   Note text (can include Creole markup)
        position:  Where to place relative to target
        target:    Class to attach to (None for floating)
        member:    Specific member to annotate (e.g., "getId()")
    """

    content: LabelLike
    position: Literal["left", "right", "top", "bottom"] = "right"
    target: str | None = None  # Class reference to attach to
    # For notes on specific members
    member: str | None = None  # e.g., "method(int)" for method overloads


@dataclass(frozen=True)
class HideShow:
    """A directive to show, hide, or remove diagram elements.

    Used to customize which parts of classes are displayed:

        action: "hide", "show", "remove", or "restore"
        target: What to affect (e.g., "empty members", "ClassName methods")

    Common targets:
        "empty members"    - Hide classes with no members
        "methods"          - Hide all methods
        "ClassName fields" - Hide fields of specific class
    """

    action: Literal["hide", "show", "remove", "restore"]
    target: (
        str  # What to hide/show (e.g., "empty members", "ClassName methods", "$tag")
    )


@dataclass(frozen=True)
class ClassDiagram:
    """A complete class diagram ready for rendering.

    Contains all classes, relationships, and diagram-level settings.
    Usually created via the class_diagram() builder rather than directly.

        elements:            All diagram elements
        title:               Optional diagram title
        hide_empty_members:  If True, hide classes with no members
        hide_circle:         If True, hide the class type circle icon
        namespace_separator: Namespace separator (e.g., "::" or "none")
    """

    elements: tuple["ClassDiagramElement", ...] = field(default_factory=tuple)
    title: str | None = None
    caption: str | None = None
    header: Header | None = None
    footer: Footer | None = None
    legend: Legend | None = None
    scale: Scale | None = None
    # Diagram-level directives
    hide_empty_members: bool = False
    hide_circle: bool = False
    namespace_separator: str | None = None  # e.g., "::" or "none"


# Type alias for elements that can appear in a class diagram
ClassDiagramElement: TypeAlias = (
    ClassNode | Relationship | Package | Together | ClassNote | HideShow | Note
)
