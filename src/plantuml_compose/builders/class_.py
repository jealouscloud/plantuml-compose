"""Class diagram builder with context manager syntax.

When to Use
-----------
Class diagrams show static structure: types, their attributes, and relationships.
Use when:

- Modeling domain concepts (User, Order, Product)
- Documenting APIs or database schemas
- Planning inheritance hierarchies
- Showing associations between entities

NOT for:
- Runtime behavior (use sequence or activity diagram)
- Object instances at a point in time (use object diagram)
- Physical deployment (use deployment diagram)

Key Concepts
------------
Class:       A type with optional attributes and methods
Interface:   A contract (no implementation)
Enum:        Fixed set of values

Relationships:

    extends (inheritance):      Child ──▷ Parent
    implements (realization):   Class ··▷ Interface
    has (aggregation):          Whole ◇── Part   (part can exist alone)
    contains (composition):     Whole ◆── Part   (part dies with whole)
    uses (dependency):          A ···> B         (A depends on B)
    associates:                 A ──> B          (general relationship)

Labels: Cardinality, roles, or both at each end

    User "1" o-- "*" Order    (one User has many Orders)
         │        │
         │        └─ target_label
         └─ source_label

Visibility (for members):

    public:     Accessible from anywhere
    private:    Only within the class
    protected:  Class and subclasses
    package:    Same package only

Example
-------
    with class_diagram(title="Domain Model") as d:
        user = d.class_("User")
        order = d.class_("Order")
        d.has(user, order, source_label="1", target_label="*")

    print(render(d.build()))
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
    VISIBILITY_OPTIONS,
)
from ..primitives.common import (
    ClassDiagramStyleLike,
    ColorLike,
    Direction,
    Footer,
    Header,
    Label,
    LayoutDirection,
    LayoutEngine,
    Legend,
    LineStyleLike,
    LineType,
    Scale,
    Stereotype,
    StyleLike,
    coerce_class_diagram_style,
    coerce_direction,
    coerce_style,
    validate_literal,
)


class _BaseClassBuilder:
    """Base class for class builders with shared methods."""

    def __init__(self) -> None:
        self._elements: list[ClassDiagramElement] = []
        self._refs: set[str] = set()  # Track valid element references

    def _register_ref(self, node: ClassNode) -> None:
        """Register a class node's reference for validation."""
        self._refs.add(node._ref)
        if node.alias:
            self._refs.add(node.alias)

    def _validate_ref(self, ref: str, param_name: str) -> None:
        """Validate that a string reference exists in the diagram.

        Args:
            ref: The reference string to validate
            param_name: Parameter name for error message

        Raises:
            ValueError: If ref is not found in registered elements
        """
        if ref not in self._refs:
            available = sorted(self._refs) if self._refs else ["(none)"]
            raise ValueError(
                f'{param_name} "{ref}" not found. Available: {", ".join(available)}'
            )

    def class_(
        self,
        name: str,
        *,
        alias: str | None = None,
        generics: str | None = None,
        stereotype: Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> ClassNode:
        """Create and register a class.

        Args:
            name: Class name
            alias: Optional short name to use instead of the auto-generated
                reference (e.g., "svc" instead of "UserService")
            generics: Generic type parameters (e.g., "T" renders as Class<T>)
            stereotype: Label shown in «guillemets» above the name to
                categorize the class (e.g., "entity" renders as «entity»)
            style: Visual styling (background color, line color, text color)

        Returns:
            The created ClassNode

        Example:
            d.class_("Error", style={"background": "#FFCDD2"})
        """
        if not name:
            raise ValueError("Class name cannot be empty")
        node = ClassNode(
            name=name,
            alias=alias,
            type="class",
            generics=generics,
            stereotype=stereotype,
            style=coerce_style(style),
        )
        self._elements.append(node)
        self._register_ref(node)
        return node

    def abstract(
        self,
        name: str,
        *,
        alias: str | None = None,
        generics: str | None = None,
        stereotype: Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> ClassNode:
        """Create and register an abstract class.

        Example:
            shape = d.abstract("Shape")
            circle = d.class_("Circle")
            d.extends(circle, shape)
        """
        if not name:
            raise ValueError("Abstract class name cannot be empty")
        node = ClassNode(
            name=name,
            alias=alias,
            type="abstract",
            generics=generics,
            stereotype=stereotype,
            style=coerce_style(style),
        )
        self._elements.append(node)
        self._register_ref(node)
        return node

    def interface(
        self,
        name: str,
        *,
        alias: str | None = None,
        generics: str | None = None,
        stereotype: Stereotype | None = None,
        style: StyleLike | None = None,
    ) -> ClassNode:
        """Create and register an interface.

        Example:
            serializable = d.interface("Serializable")
            user = d.class_("User")
            d.implements(user, serializable)
        """
        if not name:
            raise ValueError("Interface name cannot be empty")
        node = ClassNode(
            name=name,
            alias=alias,
            type="interface",
            generics=generics,
            stereotype=stereotype,
            style=coerce_style(style),
        )
        self._elements.append(node)
        self._register_ref(node)
        return node

    def enum(
        self,
        name: str,
        *values: str,
        alias: str | None = None,
        style: StyleLike | None = None,
    ) -> ClassNode:
        """Create and register an enum.

        Args:
            name: Enum name
            *values: Enum values (e.g., "VALUE1", "VALUE2")
            alias: Optional short reference name
            style: Visual styling (background color, line color, text color)

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
            style=coerce_style(style),
        )
        self._elements.append(node)
        self._register_ref(node)
        return node

    def annotation(
        self,
        name: str,
        *,
        alias: str | None = None,
        style: StyleLike | None = None,
    ) -> ClassNode:
        """Create and register an annotation.

        Example:
            override = d.annotation("Override")
        """
        if not name:
            raise ValueError("Annotation name cannot be empty")
        node = ClassNode(
            name=name,
            alias=alias,
            type="annotation",
            style=coerce_style(style),
        )
        self._elements.append(node)
        self._register_ref(node)
        return node

    def entity(
        self,
        name: str,
        *,
        alias: str | None = None,
        style: StyleLike | None = None,
    ) -> ClassNode:
        """Create and register an entity.

        Example:
            user_entity = d.entity("User")
        """
        if not name:
            raise ValueError("Entity name cannot be empty")
        node = ClassNode(
            name=name,
            alias=alias,
            type="entity",
            style=coerce_style(style),
        )
        self._elements.append(node)
        self._register_ref(node)
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
        style: StyleLike | None = None,
    ) -> Iterator["_ClassMemberBuilder"]:
        """Create a class with a builder for adding members.

        Usage:
            with d.class_with_members("User") as user:
                user.field("-id", "int")
                user.field("-email", "str")
                user.method("+login()", "bool")

        Args:
            name: Class name
            alias: Optional short name to use instead of the auto-generated
                reference (e.g., "svc" instead of "UserService")
            type: Class type (class, abstract, interface, enum, annotation, entity)
            generics: Generic type parameters (e.g., "T" renders as Class<T>)
            stereotype: Label shown in «guillemets» above the name to
                categorize the class (e.g., "service" renders as «service»)
            style: Visual styling (background color, line color, text color)

        Yields:
            A builder for adding members to the class
        """
        builder = _ClassMemberBuilder(
            name, alias, type, generics, stereotype, style
        )
        yield builder
        node = builder._build()
        self._elements.append(node)
        self._register_ref(node)

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

        Example:
            animal = d.class_("Animal")
            dog = d.class_("Dog")
            d.extends(dog, animal)  # Dog extends Animal
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

        Example:
            comparable = d.interface("Comparable")
            user = d.class_("User")
            d.implements(user, comparable)
        """
        return self._relationship(
            interface,
            implementer,
            "implementation",
            label=label,
            direction=direction,
        )

    def has(
        self,
        whole: ClassNode | str,
        part: ClassNode | str,
        *,
        whole_label: str | None = None,
        part_label: str | None = None,
        label: str | Label | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | Label | None = None,
    ) -> Relationship:
        """Create an aggregation relationship (hollow diamond).

        Aggregation means the part can exist independently of the whole.
        When the whole is destroyed, the part continues to exist.

        For composition (lifecycle-bound ownership), use contains() instead.

        Args:
            whole: The containing class
            part: The contained class
            whole_label: Text at whole end - typically how many ("1" = one,
                "*" = many, "0..1" = optional) or a role name like "owner"
            part_label: Text at part end - same format as whole_label
            label: Text on the line itself (describes the relationship)
            style: Line style (color, pattern, thickness)
            direction: Layout hint ("up", "down", "left", "right") to
                influence arrow routing between elements
            note: Note to attach to this relationship

        Example:
            d.has(team, player)  # Player exists without Team

            # "One library has many books"
            d.has(library, book, whole_label="1", part_label="*")

        UML: Hollow diamond (o--)
        """
        return self._relationship(
            whole,
            part,
            "aggregation",
            source_label=whole_label,
            target_label=part_label,
            label=label,
            style=style,
            direction=direction,
            note=note,
        )

    def contains(
        self,
        whole: ClassNode | str,
        part: ClassNode | str,
        *,
        whole_label: str | None = None,
        part_label: str | None = None,
        label: str | Label | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | Label | None = None,
    ) -> Relationship:
        """Create a composition relationship (filled diamond).

        Composition means the part cannot exist independently of the whole.
        When the whole is destroyed, the part is also destroyed.

        For aggregation (independent lifecycle), use has() instead.

        Args:
            whole: The containing class
            part: The contained class
            whole_label: Text at whole end - typically how many ("1" = one,
                "*" = many, "0..1" = optional) or a role name like "owner"
            part_label: Text at part end - same format as whole_label
            label: Text on the line itself (describes the relationship)
            style: Line style (color, pattern, thickness)
            direction: Layout hint ("up", "down", "left", "right") to
                influence arrow routing between elements
            note: Note to attach to this relationship

        Example:
            d.contains(house, room)  # Room cannot exist without House

            # "One order contains one or more line items"
            d.contains(order, line_item, whole_label="1", part_label="1..*")

        UML: Filled diamond (*--)
        """
        return self._relationship(
            whole,
            part,
            "composition",
            source_label=whole_label,
            target_label=part_label,
            label=label,
            style=style,
            direction=direction,
            note=note,
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

        Example:
            service = d.class_("OrderService")
            logger = d.class_("Logger")
            d.uses(service, logger)  # OrderService depends on Logger
        """
        return self._relationship(
            user, used, "dependency", label=label, direction=direction
        )

    def lollipop(
        self,
        provider: ClassNode | str,
        consumer: ClassNode | str,
        *,
        label: str | Label | None = None,
        direction: Direction | None = None,
    ) -> Relationship:
        """Create a lollipop interface relationship.

        Rendered as: provider ()- consumer (provider provides interface)

        Use when a class provides an interface that another class uses.

        Example:
            service = d.class_("OrderService")
            repo = d.interface("Repository")
            d.lollipop(service, repo)  # OrderService provides Repository interface
        """
        return self._relationship(
            provider, consumer, "lollipop", label=label, direction=direction
        )

    def associates(
        self,
        source: ClassNode | str,
        target: ClassNode | str,
        *,
        source_label: str | None = None,
        target_label: str | None = None,
        label: str | Label | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | Label | None = None,
    ) -> Relationship:
        """Create an association relationship.

        Rendered as: source --> target

        Args:
            source: Source class
            target: Target class
            source_label: Text at source end - typically how many ("1" = one,
                "*" = many, "0..1" = optional) or a role name like "owner"
            target_label: Text at target end - same format as source_label
            label: Text on the line itself (describes the relationship)
            style: Line style (color, pattern, thickness)
            direction: Layout hint ("up", "down", "left", "right") to
                influence arrow routing between elements
            note: Note to attach to this relationship
        """
        return self._relationship(
            source,
            target,
            "association",
            source_label=source_label,
            target_label=target_label,
            label=label,
            style=style,
            direction=direction,
            note=note,
        )

    def relationship(
        self,
        source: ClassNode | str,
        target: ClassNode | str,
        type: RelationType = "association",
        *,
        source_label: str | None = None,
        target_label: str | None = None,
        label: str | Label | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | Label | None = None,
    ) -> Relationship:
        """Create a custom relationship.

        For when the convenience methods don't fit your needs.

        Args:
            source: Source class
            target: Target class
            type: Relationship type
            source_label: Text at source end - typically how many ("1" = one,
                "*" = many, "0..1" = optional) or a role name like "owner"
            target_label: Text at target end - same format as source_label
            label: Text on the line itself (describes the relationship)
            style: Line style (color, pattern, thickness)
            direction: Layout hint ("up", "down", "left", "right") to
                influence arrow routing between elements
            note: Note to attach to this relationship
        """
        return self._relationship(
            source,
            target,
            type,
            source_label=source_label,
            target_label=target_label,
            label=label,
            style=style,
            direction=direction,
            note=note,
        )

    def _relationship(
        self,
        source: ClassNode | str,
        target: ClassNode | str,
        type: RelationType,
        *,
        source_label: str | None = None,
        target_label: str | None = None,
        label: str | Label | None = None,
        style: LineStyleLike | None = None,
        direction: Direction | None = None,
        note: str | Label | None = None,
    ) -> Relationship:
        """Internal: Create and register a relationship."""
        # Validate string refs (object refs are already valid by construction)
        if isinstance(source, str):
            self._validate_ref(source, "source")
        if isinstance(target, str):
            self._validate_ref(target, "target")

        label_obj = Label(label) if isinstance(label, str) else label
        note_obj = Label(note) if isinstance(note, str) else note
        direction_val = coerce_direction(direction)
        rel = Relationship(
            source=self._to_ref(source),
            target=self._to_ref(target),
            type=type,
            source_label=source_label,
            target_label=target_label,
            label=label_obj,
            style=style,
            direction=direction_val,
            note=note_obj,
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

        Example:
            user = d.class_("User")
            d.note("Domain entity", of=user)
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
        """Hide elements (e.g., "empty members", "circle").

        Example:
            d.hide("empty members")
            d.hide("circle")
        """
        hs = HideShow(action="hide", target=target)
        self._elements.append(hs)
        return hs

    def show(self, target: str) -> HideShow:
        """Show elements.

        Example:
            d.show("methods")
        """
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

        Args:
            name: Package name
            alias: Optional short name to use instead of the auto-generated
                reference (e.g., "svc" instead of "UserService")
            style: Visual style ("package", "node", "folder", "frame",
                "cloud", "database", "rectangle")
            color: Background color

        Usage:
            with d.package("domain") as pkg:
                pkg.class_("User")
                pkg.class_("Order")
        """
        builder = _PackageBuilder(name, alias, style, color)
        # Register package ref before yield so it's available for relationships
        self._refs.add(builder._ref)
        if alias:
            self._refs.add(alias)
        yield builder
        pkg = builder._build()
        self._elements.append(pkg)
        # Merge refs from nested classes
        self._refs.update(builder._refs)

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
        # Merge refs from nested classes
        self._refs.update(builder._refs)

    def _to_ref(
        self, node: "ClassNode | _PackageBuilder | _ClassMemberBuilder | str"
    ) -> str:
        """Convert a node or builder to its reference string."""
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
        style: StyleLike | None,
    ) -> None:
        self._name = name
        self._alias = alias
        self._type: ClassType = type
        self._generics = generics
        self._stereotype = stereotype
        self._style = coerce_style(style)
        self._members: list[Member | Separator] = []

    @property
    def _ref(self) -> str:
        """Reference name for use in relationships."""
        if self._alias:
            return self._alias
        return (
            self._name
            if self._name.isidentifier()
            else self._name.replace(" ", "_")
        )

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
            name: Field name
            type: Field type
            visibility: 'public', 'private', 'protected', or 'package'
            modifier: Modifier (static, abstract)

        Returns:
            The created Member

        Example:
            with d.class_with_members("User") as user:
                user.field("id", "int", visibility="private")
                user.field("name", "str")
        """
        # Reject old visibility prefix pattern with helpful error
        if name and name[0] in "+-#~":
            symbol = name[0]
            word = {
                "+": "public",
                "-": "private",
                "#": "protected",
                "~": "package",
            }[symbol]
            raise ValueError(
                f"Visibility prefix '{symbol}' in field name is not supported.\n"
                f'Use: field("{name[1:]}", visibility="{word}")'
            )

        # Validate visibility if provided
        validated_visibility: Visibility | None = None
        if visibility is not None:
            validated_visibility = validate_literal(  # type: ignore[assignment]
                visibility, VISIBILITY_OPTIONS, "visibility"
            )

        member = Member(
            name=name,
            type=type,
            visibility=validated_visibility,
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
            visibility: 'public', 'private', 'protected', or 'package'
            modifier: Modifier (static, abstract)

        Returns:
            The created Member

        Example:
            with d.class_with_members("User") as user:
                user.method("login()", "bool", visibility="public")
                user.method("validate(input: str)", visibility="private")
        """
        # Reject old visibility prefix pattern with helpful error
        if name and name[0] in "+-#~":
            symbol = name[0]
            word = {
                "+": "public",
                "-": "private",
                "#": "protected",
                "~": "package",
            }[symbol]
            raise ValueError(
                f"Visibility prefix '{symbol}' in method name is not supported.\n"
                f'Use: method("{name[1:]}", visibility="{word}")'
            )

        # Validate visibility if provided
        validated_visibility: Visibility | None = None
        if visibility is not None:
            validated_visibility = validate_literal(  # type: ignore[assignment]
                visibility, VISIBILITY_OPTIONS, "visibility"
            )

        member = Member(
            name=name,
            type=return_type,
            visibility=validated_visibility,
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

        Example:
            with d.class_with_members("Service") as svc:
                svc.field("config", "Config")
                svc.separator(label="methods")
                svc.method("start()")
        """
        sep = Separator(style=style, label=label)
        self._members.append(sep)
        return sep

    def static_field(
        self,
        name: str,
        type: str | None = None,
        *,
        visibility: Visibility | None = None,
    ) -> Member:
        """Add a static field.

        Example:
            user.static_field("instance_count", "int")
        """
        return self.field(name, type, visibility=visibility, modifier="static")

    def static_method(
        self,
        name: str,
        return_type: str | None = None,
        *,
        visibility: Visibility | None = None,
    ) -> Member:
        """Add a static method.

        Example:
            user.static_method("getInstance()", "User")
        """
        return self.method(
            name, return_type, visibility=visibility, modifier="static"
        )

    def abstract_method(
        self,
        name: str,
        return_type: str | None = None,
        *,
        visibility: Visibility | None = None,
    ) -> Member:
        """Add an abstract method.

        Example:
            shape.abstract_method("draw()", "void")
        """
        return self.method(
            name, return_type, visibility=visibility, modifier="abstract"
        )

    def _build(self) -> ClassNode:
        """Build the class node with members."""
        return ClassNode(
            name=self._name,
            alias=self._alias,
            type=self._type,
            generics=self._generics,
            stereotype=self._stereotype,
            style=self._style,
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
        self._style: PackageStyle = style
        self._color = color

    @property
    def _ref(self) -> str:
        """Reference name for use in relationships.

        Returns alias if set, otherwise the raw name. The renderer's
        quote_ref() will handle quoting names with special characters.
        """
        if self._alias:
            return self._alias
        return self._name

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
            d.has(user, order, source_label="1", target_label="*")

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
        theme: str | None = None,
        layout: LayoutDirection | None = None,
        layout_engine: LayoutEngine | None = None,
        linetype: LineType | None = None,
        diagram_style: ClassDiagramStyleLike | None = None,
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
        self._scale = (
            Scale(factor=scale) if isinstance(scale, (int, float)) else scale
        )
        self._theme = theme
        self._layout = layout
        self._layout_engine = layout_engine
        self._linetype = linetype
        self._diagram_style = (
            coerce_class_diagram_style(diagram_style) if diagram_style else None
        )

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
            theme=self._theme,
            layout=self._layout,
            layout_engine=self._layout_engine,
            linetype=self._linetype,
            diagram_style=self._diagram_style,
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
    theme: str | None = None,
    layout: LayoutDirection | None = None,
    layout_engine: LayoutEngine | None = None,
    linetype: LineType | None = None,
    diagram_style: ClassDiagramStyleLike | None = None,
) -> Iterator[ClassDiagramBuilder]:
    """Create a class diagram with context manager syntax.

    Usage:
        with class_diagram(title="Domain Model") as d:
            user = d.class_("User")
            admin = d.class_("Admin")
            order = d.class_("Order")

            with d.class_with_members("Product") as product:
                product.field("id", "int", visibility="private")
                product.field("name", "str", visibility="private")
                product.method("save()", "bool", visibility="public")

            d.has(user, order, source_label="1", target_label="*")
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
        theme: Optional PlantUML theme name (e.g., "cerulean", "amiga")
        layout: Diagram layout direction; None uses PlantUML default (top-to-bottom)
        layout_engine: Layout engine; "smetana" uses pure-Java GraphViz alternative
        linetype: Line routing style; "ortho" for right angles, "polyline" for direct
        diagram_style: CSS-style styling for the diagram (colors, fonts, etc.)

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
        theme=theme,
        layout=layout,
        layout_engine=layout_engine,
        linetype=linetype,
        diagram_style=diagram_style,
    )
    yield builder
