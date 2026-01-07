"""Class diagram builder with context manager syntax.

Provides a fluent API for constructing class diagrams:

    with class_diagram(title="Domain Model") as d:
        user = d.class_("User")
        order = d.class_("Order")
        d.has(user, order, source_card="1", target_card="*")

    print(d.render())
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Literal

from ..primitives.class_ import (
    ClassDiagram,
    ClassDiagramElement,
    ClassNode,
    ClassNote,
    ClassType,
    HideShow,
    Member,
    MemberModifier,
    Package,
    PackageStyle,
    Relationship,
    RelationType,
    Separator,
    SeparatorStyle,
    Together,
    Visibility,
)
from ..primitives.common import (
    ColorLike,
    Direction,
    Footer,
    Header,
    Label,
    LabelLike,
    Legend,
    LineStyleLike,
    Note,
    NotePosition,
    Scale,
    Stereotype,
)


class _BaseClassBuilder:
    """Base class for class builders with shared methods."""

    def __init__(self) -> None:
        self._elements: list[ClassDiagramElement] = []

    def class_(
        self,
        name: str,
        *,
        alias: str | None = None,
        generics: str | None = None,
        stereotype: Stereotype | None = None,
    ) -> ClassNode:
        """Create and register a class.

        Args:
            name: Class name
            alias: Optional short reference name
            generics: Generic type parameters (e.g., "T extends Element")
            stereotype: Optional stereotype

        Returns:
            The created ClassNode
        """
        if not name:
            raise ValueError("Class name cannot be empty")
        node = ClassNode(
            name=name,
            alias=alias,
            type="class",
            generics=generics,
            stereotype=stereotype,
        )
        self._elements.append(node)
        return node

    def abstract(
        self,
        name: str,
        *,
        alias: str | None = None,
        generics: str | None = None,
        stereotype: Stereotype | None = None,
    ) -> ClassNode:
        """Create and register an abstract class."""
        if not name:
            raise ValueError("Abstract class name cannot be empty")
        node = ClassNode(
            name=name,
            alias=alias,
            type="abstract",
            generics=generics,
            stereotype=stereotype,
        )
        self._elements.append(node)
        return node

    def interface(
        self,
        name: str,
        *,
        alias: str | None = None,
        generics: str | None = None,
        stereotype: Stereotype | None = None,
    ) -> ClassNode:
        """Create and register an interface."""
        if not name:
            raise ValueError("Interface name cannot be empty")
        node = ClassNode(
            name=name,
            alias=alias,
            type="interface",
            generics=generics,
            stereotype=stereotype,
        )
        self._elements.append(node)
        return node

    def enum(
        self,
        name: str,
        *values: str,
        alias: str | None = None,
    ) -> ClassNode:
        """Create and register an enum.

        Args:
            name: Enum name
            *values: Enum values (e.g., "VALUE1", "VALUE2")
            alias: Optional short reference name

        Example:
            d.enum("Status", "PENDING", "ACTIVE", "CLOSED")
        """
        if not name:
            raise ValueError("Enum name cannot be empty")
        node = ClassNode(
            name=name,
            alias=alias,
            type="enum",
            enum_values=values if values else None,
        )
        self._elements.append(node)
        return node

    def annotation(self, name: str, *, alias: str | None = None) -> ClassNode:
        """Create and register an annotation."""
        if not name:
            raise ValueError("Annotation name cannot be empty")
        node = ClassNode(name=name, alias=alias, type="annotation")
        self._elements.append(node)
        return node

    def entity(self, name: str, *, alias: str | None = None) -> ClassNode:
        """Create and register an entity."""
        if not name:
            raise ValueError("Entity name cannot be empty")
        node = ClassNode(name=name, alias=alias, type="entity")
        self._elements.append(node)
        return node

    @contextmanager
    def class_with_members(
        self,
        name: str,
        *,
        alias: str | None = None,
        type: ClassType = "class",
        generics: str | None = None,
        stereotype: Stereotype | None = None,
    ) -> Iterator["_ClassMemberBuilder"]:
        """Create a class with a builder for adding members.

        Usage:
            with d.class_with_members("User") as user:
                user.field("-id", "int")
                user.field("-email", "str")
                user.method("+login()", "bool")

        Args:
            name: Class name
            alias: Optional short reference name
            type: Class type (class, abstract, interface, etc.)
            generics: Generic type parameters
            stereotype: Optional stereotype

        Yields:
            A builder for adding members to the class
        """
        builder = _ClassMemberBuilder(name, alias, type, generics, stereotype)
        yield builder
        self._elements.append(builder._build())

    # Relationship methods
    def extends(
        self,
        child: ClassNode | str,
        parent: ClassNode | str,
        *,
        label: str | Label | None = None,
        direction: Direction | None = None,
    ) -> Relationship:
        """Create an extension (inheritance) relationship.

        Rendered as: child <|-- parent (child extends parent)
        """
        return self._relationship(
            parent, child, "extension", label=label, direction=direction
        )

    def implements(
        self,
        implementer: ClassNode | str,
        interface: ClassNode | str,
        *,
        label: str | Label | None = None,
        direction: Direction | None = None,
    ) -> Relationship:
        """Create an implementation relationship.

        Rendered as: implementer <|.. interface
        """
        return self._relationship(
            interface, implementer, "implementation", label=label, direction=direction
        )

    def has(
        self,
        container: ClassNode | str,
        contained: ClassNode | str,
        *,
        composition: bool = False,
        source_card: str | None = None,
        target_card: str | None = None,
        source_label: str | None = None,
        target_label: str | None = None,
        label: str | Label | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
    ) -> Relationship:
        """Create a has-a relationship (aggregation or composition).

        Args:
            container: The containing class
            contained: The contained class
            composition: If True, uses composition (*--); if False, aggregation (o--)
            source_card: Cardinality at container end (e.g., "1")
            target_card: Cardinality at contained end (e.g., "*", "0..*")
            source_label: Role name at container end
            target_label: Role name at contained end
            label: Relationship label
            style: Line style (color, pattern, thickness)
            direction: Layout direction hint

        Example:
            d.has(user, order, source_card="1", target_card="*", label="places")
        """
        rel_type: RelationType = "composition" if composition else "aggregation"
        return self._relationship(
            container,
            contained,
            rel_type,
            source_card=source_card,
            target_card=target_card,
            source_label=source_label,
            target_label=target_label,
            label=label,
            style=style,
            direction=direction,
        )

    def uses(
        self,
        user: ClassNode | str,
        used: ClassNode | str,
        *,
        label: str | Label | None = None,
        direction: Direction | None = None,
    ) -> Relationship:
        """Create a uses (dependency) relationship.

        Rendered as: user ..> used
        """
        return self._relationship(
            user, used, "dependency", label=label, direction=direction
        )

    def associates(
        self,
        source: ClassNode | str,
        target: ClassNode | str,
        *,
        source_card: str | None = None,
        target_card: str | None = None,
        source_label: str | None = None,
        target_label: str | None = None,
        label: str | Label | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
    ) -> Relationship:
        """Create an association relationship.

        Rendered as: source --> target

        Args:
            source: Source class
            target: Target class
            source_card: Cardinality at source end
            target_card: Cardinality at target end
            source_label: Role name at source end
            target_label: Role name at target end
            label: Relationship label
            style: Line style (color, pattern, thickness)
            direction: Layout direction hint
        """
        return self._relationship(
            source,
            target,
            "association",
            source_card=source_card,
            target_card=target_card,
            source_label=source_label,
            target_label=target_label,
            label=label,
            style=style,
            direction=direction,
        )

    def relationship(
        self,
        source: ClassNode | str,
        target: ClassNode | str,
        type: RelationType = "association",
        *,
        source_card: str | None = None,
        target_card: str | None = None,
        source_label: str | None = None,
        target_label: str | None = None,
        label: str | Label | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
    ) -> Relationship:
        """Create a custom relationship.

        For when the convenience methods don't fit your needs.

        Args:
            source: Source class
            target: Target class
            type: Relationship type
            source_card: Cardinality at source end (e.g., "1")
            target_card: Cardinality at target end (e.g., "*")
            source_label: Role name at source end
            target_label: Role name at target end
            label: Relationship label
            style: Line style (color, pattern, thickness)
            direction: Layout direction hint
        """
        return self._relationship(
            source,
            target,
            type,
            source_card=source_card,
            target_card=target_card,
            source_label=source_label,
            target_label=target_label,
            label=label,
            style=style,
            direction=direction,
        )

    def _relationship(
        self,
        source: ClassNode | str,
        target: ClassNode | str,
        type: RelationType,
        *,
        source_card: str | None = None,
        target_card: str | None = None,
        source_label: str | None = None,
        target_label: str | None = None,
        label: str | Label | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
    ) -> Relationship:
        """Internal: Create and register a relationship."""
        label_obj = Label(label) if isinstance(label, str) else label
        rel = Relationship(
            source=self._to_ref(source),
            target=self._to_ref(target),
            type=type,
            source_cardinality=source_card,
            target_cardinality=target_card,
            source_label=source_label,
            target_label=target_label,
            label=label_obj,
            style=style,
            direction=direction,
        )
        self._elements.append(rel)
        return rel

    def note(
        self,
        content: str | Label,
        position: Literal["left", "right", "top", "bottom"] = "right",
        *,
        of: ClassNode | str | None = None,
        member: str | None = None,
    ) -> ClassNote:
        """Create and register a note.

        Args:
            content: Note text
            position: Note position (left, right, top, bottom)
            of: Class to attach the note to
            member: Specific member (e.g., "method(int)") for overloaded methods

        Returns:
            The created ClassNote
        """
        text = content.text if isinstance(content, Label) else content
        if not text:
            raise ValueError("Note content cannot be empty")
        content_label = Label(content) if isinstance(content, str) else content
        note = ClassNote(
            content=content_label,
            position=position,
            target=self._to_ref(of) if of else None,
            member=member,
        )
        self._elements.append(note)
        return note

    def hide(self, target: str) -> HideShow:
        """Hide elements (e.g., "empty members", "circle")."""
        hs = HideShow(action="hide", target=target)
        self._elements.append(hs)
        return hs

    def show(self, target: str) -> HideShow:
        """Show elements."""
        hs = HideShow(action="show", target=target)
        self._elements.append(hs)
        return hs

    @contextmanager
    def package(
        self,
        name: str,
        *,
        alias: str | None = None,
        style: PackageStyle = "package",
        color: ColorLike | None = None,
    ) -> Iterator["_PackageBuilder"]:
        """Create a package containing classes.

        Usage:
            with d.package("domain") as pkg:
                pkg.class_("User")
                pkg.class_("Order")
        """
        builder = _PackageBuilder(name, alias, style, color)
        yield builder
        self._elements.append(builder._build())

    @contextmanager
    def together(self) -> Iterator["_TogetherBuilder"]:
        """Group classes for layout.

        Classes in a together block are laid out close to each other.

        Usage:
            with d.together() as t:
                t.class_("A")
                t.class_("B")
        """
        builder = _TogetherBuilder()
        yield builder
        self._elements.append(builder._build())

    def _to_ref(self, node: ClassNode | str) -> str:
        """Convert a class node to its reference string."""
        if isinstance(node, str):
            return node
        return node._ref


class _ClassMemberBuilder:
    """Builder for adding members to a class."""

    def __init__(
        self,
        name: str,
        alias: str | None,
        type: ClassType,
        generics: str | None,
        stereotype: Stereotype | None,
    ) -> None:
        self._name = name
        self._alias = alias
        self._type = type
        self._generics = generics
        self._stereotype = stereotype
        self._members: list[Member | Separator] = []

    @property
    def _ref(self) -> str:
        """Reference name for use in relationships."""
        if self._alias:
            return self._alias
        return self._name if self._name.isidentifier() else self._name.replace(" ", "_")

    def field(
        self,
        name: str,
        type: str | None = None,
        *,
        visibility: Visibility | None = None,
        modifier: MemberModifier | None = None,
    ) -> Member:
        """Add a field to the class.

        Args:
            name: Field name (can include visibility prefix like "-id")
            type: Field type
            visibility: Explicit visibility (+, -, #, ~)
            modifier: Modifier (static, abstract)

        Returns:
            The created Member
        """
        # Parse visibility from name if not explicit
        actual_visibility = visibility
        actual_name = name
        if name and name[0] in "+-#~" and visibility is None:
            actual_visibility = name[0]  # type: ignore[assignment]
            actual_name = name[1:]

        member = Member(
            name=actual_name,
            type=type,
            visibility=actual_visibility,
            modifier=modifier,
            is_method=False,
        )
        self._members.append(member)
        return member

    def method(
        self,
        name: str,
        return_type: str | None = None,
        *,
        visibility: Visibility | None = None,
        modifier: MemberModifier | None = None,
    ) -> Member:
        """Add a method to the class.

        Args:
            name: Method signature (e.g., "login()", "calculate(x: int)")
            return_type: Return type
            visibility: Explicit visibility (+, -, #, ~)
            modifier: Modifier (static, abstract)

        Returns:
            The created Member
        """
        # Parse visibility from name if not explicit
        actual_visibility = visibility
        actual_name = name
        if name and name[0] in "+-#~" and visibility is None:
            actual_visibility = name[0]  # type: ignore[assignment]
            actual_name = name[1:]

        member = Member(
            name=actual_name,
            type=return_type,
            visibility=actual_visibility,
            modifier=modifier,
            is_method=True,
        )
        self._members.append(member)
        return member

    def separator(
        self,
        style: SeparatorStyle = "solid",
        label: str | None = None,
    ) -> Separator:
        """Add a separator line within the class.

        Args:
            style: Separator style (solid, dotted, double, underline)
            label: Optional label text

        Returns:
            The created Separator
        """
        sep = Separator(style=style, label=label)
        self._members.append(sep)
        return sep

    def static(
        self,
        name: str,
        type: str | None = None,
        *,
        visibility: Visibility | None = None,
        is_method: bool = True,
    ) -> Member:
        """Add a static member (field or method).

        Args:
            name: Member name
            type: Type (return type for methods, field type for fields)
            visibility: Visibility (+, -, #, ~)
            is_method: If True, creates a method; if False, creates a field

        Returns:
            The created Member
        """
        if is_method:
            return self.method(name, type, visibility=visibility, modifier="static")
        return self.field(name, type, visibility=visibility, modifier="static")

    def abstract_method(
        self,
        name: str,
        return_type: str | None = None,
        *,
        visibility: Visibility | None = None,
    ) -> Member:
        """Add an abstract method."""
        return self.method(name, return_type, visibility=visibility, modifier="abstract")

    def _build(self) -> ClassNode:
        """Build the class node with members."""
        return ClassNode(
            name=self._name,
            alias=self._alias,
            type=self._type,
            generics=self._generics,
            stereotype=self._stereotype,
            members=tuple(self._members),
        )


class _PackageBuilder(_BaseClassBuilder):
    """Builder for packages containing classes."""

    def __init__(
        self,
        name: str,
        alias: str | None,
        style: PackageStyle,
        color: ColorLike | None,
    ) -> None:
        if not name:
            raise ValueError("Package name cannot be empty")
        super().__init__()
        self._name = name
        self._alias = alias
        self._style = style
        self._color = color

    def _build(self) -> Package:
        """Build the package primitive."""
        return Package(
            name=self._name,
            alias=self._alias,
            style=self._style,
            color=self._color,
            elements=tuple(self._elements),
        )


class _TogetherBuilder(_BaseClassBuilder):
    """Builder for together layout grouping."""

    def _build(self) -> Together:
        """Build the together block."""
        return Together(elements=tuple(self._elements))


class ClassDiagramBuilder(_BaseClassBuilder):
    """Builder for complete class diagrams.

    Usage:
        with class_diagram(title="Domain Model") as d:
            user = d.class_("User")
            order = d.class_("Order")
            d.has(user, order, source_card="1", target_card="*")

        diagram = d.build()
        print(render(diagram))
    """

    def __init__(
        self,
        *,
        title: str | None = None,
        hide_empty_members: bool = False,
        hide_circle: bool = False,
        namespace_separator: str | None = None,
        caption: str | None = None,
        header: str | Header | None = None,
        footer: str | Footer | None = None,
        legend: str | Legend | None = None,
        scale: float | Scale | None = None,
    ) -> None:
        super().__init__()
        self._title = title
        self._hide_empty_members = hide_empty_members
        self._hide_circle = hide_circle
        self._namespace_separator = namespace_separator
        self._caption = caption
        self._header = Header(header) if isinstance(header, str) else header
        self._footer = Footer(footer) if isinstance(footer, str) else footer
        self._legend = Legend(legend) if isinstance(legend, str) else legend
        self._scale = Scale(factor=scale) if isinstance(scale, (int, float)) else scale

    def build(self) -> ClassDiagram:
        """Build the complete class diagram."""
        return ClassDiagram(
            elements=tuple(self._elements),
            title=self._title,
            hide_empty_members=self._hide_empty_members,
            hide_circle=self._hide_circle,
            namespace_separator=self._namespace_separator,
            caption=self._caption,
            header=self._header,
            footer=self._footer,
            legend=self._legend,
            scale=self._scale,
        )

    def render(self) -> str:
        """Build and render the diagram to PlantUML text.

        Convenience method combining build() and render() in one call.
        """
        from ..renderers import render
        return render(self.build())


@contextmanager
def class_diagram(
    *,
    title: str | None = None,
    hide_empty_members: bool = False,
    hide_circle: bool = False,
    namespace_separator: str | None = None,
    caption: str | None = None,
    header: str | Header | None = None,
    footer: str | Footer | None = None,
    legend: str | Legend | None = None,
    scale: float | Scale | None = None,
) -> Iterator[ClassDiagramBuilder]:
    """Create a class diagram with context manager syntax.

    Usage:
        with class_diagram(title="Domain Model") as d:
            user = d.class_("User")
            order = d.class_("Order")

            with d.class_with_members("Product") as product:
                product.field("-id", "int")
                product.field("-name", "str")
                product.method("+save()", "bool")

            d.has(user, order, source_card="1", target_card="*")
            d.extends(admin, user)

        print(d.render())

    Args:
        title: Optional diagram title
        hide_empty_members: Hide classes with no members
        hide_circle: Hide the circle icons
        namespace_separator: Namespace separator (e.g., "::" or "none")
        caption: Optional diagram caption
        header: Optional header text or Header object
        footer: Optional footer text or Footer object
        legend: Optional legend text or Legend object
        scale: Optional scale factor or Scale object

    Yields:
        A ClassDiagramBuilder for adding diagram elements
    """
    builder = ClassDiagramBuilder(
        title=title,
        hide_empty_members=hide_empty_members,
        hide_circle=hide_circle,
        namespace_separator=namespace_separator,
        caption=caption,
        header=header,
        footer=footer,
        legend=legend,
        scale=scale,
    )
    yield builder
