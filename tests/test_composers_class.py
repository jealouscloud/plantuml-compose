"""Tests for the class diagram composer."""

import subprocess

import pytest

from plantuml_compose.composers.class_ import class_diagram
from plantuml_compose.primitives.class_ import (
    ClassDiagram,
    ClassNode,
    ClassNote,
    Member,
    Package,
    Relationship,
    Separator,
)
from plantuml_compose.renderers import render


class TestClassComposer:

    def test_empty_diagram(self):
        d = class_diagram()
        result = d.build()
        assert isinstance(result, ClassDiagram)
        assert result.elements == ()

    def test_simple_class(self):
        d = class_diagram()
        el = d.elements
        d.add(el.class_("User"))
        result = d.build()
        node = result.elements[0]
        assert isinstance(node, ClassNode)
        assert node.name == "User"
        assert node.type == "class"

    def test_abstract_class(self):
        d = class_diagram()
        el = d.elements
        d.add(el.abstract("Base"))
        result = d.build()
        assert result.elements[0].type == "abstract"

    def test_interface(self):
        d = class_diagram()
        el = d.elements
        d.add(el.interface("IService"))
        result = d.build()
        assert result.elements[0].type == "interface"

    def test_protocol(self):
        d = class_diagram()
        el = d.elements
        d.add(el.protocol("Renderable"))
        result = d.build()
        assert result.elements[0].type == "protocol"

    def test_enum(self):
        d = class_diagram()
        el = d.elements
        d.add(el.enum("Color", "RED", "GREEN", "BLUE"))
        result = d.build()
        node = result.elements[0]
        assert node.type == "enum"
        assert node.enum_values == ("RED", "GREEN", "BLUE")

    def test_class_with_members(self):
        d = class_diagram()
        el = d.elements
        d.add(el.class_("User", members=(
            el.field("name", "str"),
            el.field("age", "int"),
            el.separator(),
            el.method("greet()", "str"),
        )))
        result = d.build()
        node = result.elements[0]
        assert len(node.members) == 4
        assert isinstance(node.members[0], Member)
        assert node.members[0].name == "name"
        assert node.members[0].type == "str"
        assert node.members[0].is_method is False
        assert isinstance(node.members[2], Separator)
        assert isinstance(node.members[3], Member)
        assert node.members[3].is_method is True

    def test_field_with_visibility(self):
        d = class_diagram()
        el = d.elements
        d.add(el.class_("X", members=(
            el.field("pub", visibility="public"),
            el.field("priv", visibility="private"),
        )))
        result = d.build()
        members = result.elements[0].members
        assert members[0].visibility == "public"
        assert members[1].visibility == "private"

    def test_stereotype_string_coercion(self):
        d = class_diagram()
        el = d.elements
        d.add(el.class_("Meta", stereotype="metaclass"))
        result = d.build()
        node = result.elements[0]
        assert node.stereotype is not None
        assert node.stereotype.name == "metaclass"

    def test_generics(self):
        d = class_diagram()
        el = d.elements
        d.add(el.class_("List", generics="T"))
        result = d.build()
        assert result.elements[0].generics == "T"

    def test_package_with_children(self):
        d = class_diagram()
        el = d.elements
        d.add(el.package("models",
            el.class_("User"),
            el.class_("Role"),
        ))
        result = d.build()
        pkg = result.elements[0]
        assert isinstance(pkg, Package)
        assert pkg.name == "models"
        assert len(pkg.elements) == 2

    def test_extends_relationship(self):
        d = class_diagram()
        el = d.elements
        r = d.relationships
        base = el.class_("Base")
        child = el.class_("Child")
        d.add(base, child)
        d.connect(r.extends(child, base))
        result = d.build()
        rels = [e for e in result.elements if isinstance(e, Relationship)]
        assert len(rels) == 1
        assert rels[0].type == "extension"

    def test_implements_relationship(self):
        d = class_diagram()
        el = d.elements
        r = d.relationships
        iface = el.interface("IService")
        impl = el.class_("Service")
        d.add(iface, impl)
        d.connect(r.implements(impl, iface))
        result = d.build()
        rels = [e for e in result.elements if isinstance(e, Relationship)]
        assert rels[0].type == "implementation"

    def test_has_relationship_with_part_label(self):
        d = class_diagram()
        el = d.elements
        r = d.relationships
        whole = el.class_("Car")
        part = el.class_("Engine")
        d.add(whole, part)
        d.connect(r.has(whole, part, label="engine", part_label="1"))
        result = d.build()
        rels = [e for e in result.elements if isinstance(e, Relationship)]
        assert rels[0].type == "composition"
        assert rels[0].label.text == "engine"
        assert rels[0].target_label == "1"

    def test_uses_relationship(self):
        d = class_diagram()
        el = d.elements
        r = d.relationships
        a = el.class_("A")
        b = el.class_("B")
        d.add(a, b)
        d.connect(r.uses(a, b, label="depends"))
        result = d.build()
        rels = [e for e in result.elements if isinstance(e, Relationship)]
        assert rels[0].type == "dependency"

    def test_note(self):
        d = class_diagram()
        el = d.elements
        cls = el.class_("Node")
        d.add(cls)
        d.note("Type union", target=cls, position="right")
        result = d.build()
        notes = [e for e in result.elements if isinstance(e, ClassNote)]
        assert len(notes) == 1
        assert notes[0].content == "Type union"
        assert notes[0].target == cls._ref

    def test_title_and_theme(self):
        d = class_diagram(title="Model", theme="plain")
        el = d.elements
        d.add(el.class_("X"))
        result = d.build()
        assert result.title == "Model"
        assert result.theme == "plain"

    def test_render_produces_plantuml(self):
        d = class_diagram(title="Test")
        el = d.elements
        r = d.relationships
        a = el.class_("A")
        b = el.class_("B")
        d.add(a, b)
        d.connect(r.extends(b, a))
        result = render(d)
        assert "@startuml" in result
        assert "class A" in result or "A" in result

    def test_render_matches_builder_simple(self):
        """Simple class + extends matches old builder."""
        from plantuml_compose.builders.class_ import (
            class_diagram as builder_class,
        )

        # Old builder
        with builder_class(title="Test") as old:
            a = old.class_("Base")
            b = old.class_("Child")
            old.extends(b, a)
        old_output = render(old.build())

        # New composer
        d = class_diagram(title="Test")
        el = d.elements
        r = d.relationships
        a = el.class_("Base")
        b = el.class_("Child")
        d.add(a, b)
        d.connect(r.extends(b, a))
        new_output = render(d)

        assert old_output == new_output

    def test_render_matches_builder_with_members(self):
        """Class with members matches old builder."""
        from plantuml_compose.builders.class_ import (
            class_diagram as builder_class,
        )

        # Old builder
        with builder_class() as old:
            with old.class_with_members("User") as user:
                user.field("name", "str")
                user.method("greet()", "str")
        old_output = render(old.build())

        # New composer
        d = class_diagram()
        el = d.elements
        d.add(el.class_("User", members=(
            el.field("name", "str"),
            el.method("greet()", "str"),
        )))
        new_output = render(d)

        assert old_output == new_output


class TestClassPlantUMLValidation:

    @pytest.fixture
    def plantuml_check(self):
        try:
            result = subprocess.run(
                ["plantuml", "-version"],
                capture_output=True, timeout=10,
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def test_class_diagram_valid_plantuml(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = class_diagram(title="Model", theme="plain")
        el = d.elements
        r = d.relationships

        base = el.abstract("BaseElement", members=(
            el.field("tag", "str"),
            el.separator(),
            el.method("render()", "str"),
        ))
        div = el.class_("div")
        a = el.class_("a")

        d.add(base, div, a)
        d.connect(
            r.extends(div, base),
            r.extends(a, base),
        )

        puml_file = tmp_path / "class_composer.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"
