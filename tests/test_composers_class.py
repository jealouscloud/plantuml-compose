"""Tests for the class diagram composer."""

import subprocess

import pytest

from plantuml_compose.composers.class_ import class_diagram
from plantuml_compose.primitives.class_ import (
    AssociationClass,
    ClassDiagram,
    ClassNode,
    ClassNote,
    HideShow,
    Member,
    Package,
    Relationship,
    Separator,
    Together,
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

    def test_together(self):
        d = class_diagram()
        el = d.elements
        a = el.class_("A")
        b = el.class_("B")
        d.together(a, b)
        result = d.build()
        together_elems = [e for e in result.elements if isinstance(e, Together)]
        assert len(together_elems) == 1
        assert len(together_elems[0].elements) == 2

    def test_association_class(self):
        d = class_diagram()
        el = d.elements
        r = d.relationships
        student = el.class_("Student")
        course = el.class_("Course")
        enrollment = el.class_("Enrollment")
        d.add(student, course, enrollment)
        d.connect(
            r.association(student, course),
            r.association_class(student, course, enrollment),
        )
        result = d.build()
        assocs = [e for e in result.elements if isinstance(e, AssociationClass)]
        assert len(assocs) == 1
        assert assocs[0].source == "Student"
        assert assocs[0].target == "Course"
        assert assocs[0].association_class == "Enrollment"

    def test_hide(self):
        d = class_diagram()
        el = d.elements
        d.add(el.class_("X"))
        d.hide("empty members")
        result = d.build()
        hs = [e for e in result.elements if isinstance(e, HideShow)]
        assert len(hs) == 1
        assert hs[0].action == "hide"
        assert hs[0].target == "empty members"

    def test_show(self):
        d = class_diagram()
        el = d.elements
        d.add(el.class_("X"))
        d.show("methods")
        result = d.build()
        hs = [e for e in result.elements if isinstance(e, HideShow)]
        assert len(hs) == 1
        assert hs[0].action == "show"
        assert hs[0].target == "methods"

    def test_remove(self):
        d = class_diagram()
        el = d.elements
        d.add(el.class_("X"))
        d.remove("empty members")
        result = d.build()
        hs = [e for e in result.elements if isinstance(e, HideShow)]
        assert len(hs) == 1
        assert hs[0].action == "remove"
        assert hs[0].target == "empty members"

    def test_restore(self):
        d = class_diagram()
        el = d.elements
        d.add(el.class_("X"))
        d.restore("methods")
        result = d.build()
        hs = [e for e in result.elements if isinstance(e, HideShow)]
        assert len(hs) == 1
        assert hs[0].action == "restore"
        assert hs[0].target == "methods"

    def test_note_with_member(self):
        d = class_diagram()
        el = d.elements
        cls = el.class_("User", members=(
            el.field("id", "int"),
            el.field("name", "str"),
        ))
        d.add(cls)
        d.note("important", target=cls, member="id")
        result = d.build()
        notes = [e for e in result.elements if isinstance(e, ClassNote)]
        assert len(notes) == 1
        assert notes[0].member == "id"
        assert notes[0].target == cls._ref
        output = render(d)
        assert "::id" in output

    def test_namespace_separator(self):
        d = class_diagram(namespace_separator="none")
        el = d.elements
        d.add(el.class_("com.example.User"))
        result = d.build()
        assert result.namespace_separator == "none"

    def test_generic_relationship(self):
        d = class_diagram()
        el = d.elements
        r = d.relationships
        a = el.class_("A")
        b = el.class_("B")
        d.add(a, b)
        d.connect(r.relationship(a, b, type="dependency", label="uses"))
        result = d.build()
        rels = [e for e in result.elements if isinstance(e, Relationship)]
        assert len(rels) == 1
        assert rels[0].type == "dependency"
        assert rels[0].label.text == "uses"

    def test_contains_relationship(self):
        d = class_diagram()
        el = d.elements
        r = d.relationships
        house = el.class_("House")
        room = el.class_("Room")
        d.add(house, room)
        d.connect(r.contains(house, room, whole_label="1", part_label="1..*"))
        result = d.build()
        rels = [e for e in result.elements if isinstance(e, Relationship)]
        assert len(rels) == 1
        assert rels[0].type == "composition"
        assert rels[0].source_label == "1"
        assert rels[0].target_label == "1..*"

    def test_relationship_note(self):
        d = class_diagram()
        el = d.elements
        r = d.relationships
        a = el.class_("A")
        b = el.class_("B")
        d.add(a, b)
        d.connect(r.extends(b, a, note="important"))
        result = d.build()
        rels = [e for e in result.elements if isinstance(e, Relationship)]
        assert rels[0].note is not None
        assert rels[0].note.text == "important"

    def test_relationship_qualifier(self):
        d = class_diagram()
        el = d.elements
        r = d.relationships
        bank = el.class_("Bank")
        acct = el.class_("Account")
        d.add(bank, acct)
        d.connect(r.association(bank, acct, qualifier="accountNum"))
        result = d.build()
        rels = [e for e in result.elements if isinstance(e, Relationship)]
        assert rels[0].qualifier == "accountNum"


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
