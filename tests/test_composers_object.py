"""Tests for the object diagram composer."""

import subprocess

import pytest

from plantuml_compose.composers.object_ import object_diagram
from plantuml_compose.primitives.object_ import (
    Field,
    Map,
    MapEntry,
    Object,
    ObjectDiagram,
    ObjectNote,
    Relationship,
)
from plantuml_compose.renderers import render


class TestObjectComposer:

    def test_empty_diagram(self):
        d = object_diagram()
        result = d.build()
        assert isinstance(result, ObjectDiagram)
        assert result.elements == ()

    def test_object_with_fields(self):
        d = object_diagram()
        el = d.elements
        d.add(el.object("vz-node-01 : Node", ref="n1", fields={
            "totalRAM": "64 GB",
            "usedMem": "58 GB",
        }))
        result = d.build()
        assert len(result.elements) == 1
        obj = result.elements[0]
        assert isinstance(obj, Object)
        assert obj.name == "vz-node-01 : Node"
        assert obj.alias == "n1"
        assert len(obj.fields) == 2
        assert obj.fields[0] == Field(name="totalRAM", value="64 GB")

    def test_object_without_fields(self):
        d = object_diagram()
        el = d.elements
        d.add(el.object("Customer"))
        result = d.build()
        obj = result.elements[0]
        assert isinstance(obj, Object)
        assert obj.fields == ()

    def test_map_with_entries(self):
        d = object_diagram()
        el = d.elements
        d.add(el.map("config", entries={"env": "prod", "debug": "false"}))
        result = d.build()
        m = result.elements[0]
        assert isinstance(m, Map)
        assert len(m.entries) == 2

    def test_composition(self):
        d = object_diagram()
        el = d.elements
        r = d.relationships
        node = el.object("Node", ref="n1")
        ct = el.object("Container", ref="ct1")
        d.add(node, ct)
        d.connect(r.composition(node, ct))
        result = d.build()
        rels = [e for e in result.elements if isinstance(e, Relationship)]
        assert len(rels) == 1
        assert rels[0].type == "composition"
        assert rels[0].source == "n1"
        assert rels[0].target == "ct1"

    def test_arrow_with_style(self):
        d = object_diagram()
        el = d.elements
        r = d.relationships
        a = el.object("A")
        b = el.object("B")
        d.add(a, b)
        d.connect(r.arrow(a, b, "link", style={"color": "#D32F2F", "pattern": "bold"}))
        result = d.build()
        rels = [e for e in result.elements if isinstance(e, Relationship)]
        assert len(rels) == 1
        assert rels[0].type == "arrow"
        assert rels[0].label.text == "link"
        assert rels[0].style is not None
        assert rels[0].style.color.value == "#D32F2F"

    def test_association(self):
        d = object_diagram()
        el = d.elements
        r = d.relationships
        a = el.object("A")
        b = el.object("B")
        d.add(a, b)
        d.connect(r.association(a, b))
        result = d.build()
        rels = [e for e in result.elements if isinstance(e, Relationship)]
        assert rels[0].type == "association"

    def test_note(self):
        d = object_diagram()
        el = d.elements
        obj = el.object("Foo")
        d.add(obj)
        d.note("Important", target=obj, position="bottom")
        result = d.build()
        notes = [e for e in result.elements if isinstance(e, ObjectNote)]
        assert len(notes) == 1
        assert notes[0].content == "Important"
        assert notes[0].position == "bottom"
        assert notes[0].target == obj._ref

    def test_title_and_theme(self):
        d = object_diagram(title="Snapshot", theme="plain")
        el = d.elements
        d.add(el.object("A"))
        result = d.build()
        assert result.title == "Snapshot"
        assert result.theme == "plain"

    def test_render_produces_plantuml(self):
        d = object_diagram(title="Test")
        el = d.elements
        r = d.relationships
        a = el.object("Node", ref="n1", fields={"ram": "64GB"})
        b = el.object("Container", ref="ct1")
        d.add(a, b)
        d.connect(r.arrow(a, b, "hosts"))
        result = render(d)
        assert "@startuml" in result
        assert "Node" in result
        assert "@enduml" in result

    def test_render_matches_builder(self):
        """Simple objects + arrow matches old builder."""
        from plantuml_compose.builders.object_ import (
            object_diagram as builder_object,
        )

        # Old builder
        with builder_object(title="Test") as old:
            a = old.object_with_fields(
                "Node", alias="n1",
                fields={"ram": "64GB"},
            )
            b = old.object("Container", alias="ct1")
            old.arrow(a, b, label="hosts")
        old_output = render(old.build())

        # New composer
        d = object_diagram(title="Test")
        el = d.elements
        r = d.relationships
        a = el.object("Node", ref="n1", fields={"ram": "64GB"})
        b = el.object("Container", ref="ct1")
        d.add(a, b)
        d.connect(r.arrow(a, b, "hosts"))
        new_output = render(d)

        assert old_output == new_output

    def test_render_matches_builder_composition(self):
        """Composition relationship matches old builder."""
        from plantuml_compose.builders.object_ import (
            object_diagram as builder_object,
        )

        # Old builder
        with builder_object() as old:
            node = old.object("Node", alias="n1")
            ct = old.object("Container", alias="ct1")
            old.composition(node, ct)
        old_output = render(old.build())

        # New composer
        d = object_diagram()
        el = d.elements
        r = d.relationships
        node = el.object("Node", ref="n1")
        ct = el.object("Container", ref="ct1")
        d.add(node, ct)
        d.connect(r.composition(node, ct))
        new_output = render(d)

        assert old_output == new_output

    def test_style_applied(self):
        d = object_diagram()
        el = d.elements
        d.add(el.object("Node", style={"background": "#FFCDD2"}))
        result = d.build()
        obj = result.elements[0]
        assert obj.style is not None
        assert obj.style.background.value == "#FFCDD2"

    def test_map_with_links(self):
        d = object_diagram()
        el = d.elements
        user = el.object("User", ref="u1")
        refs = el.map("refs", links={"owner": user})
        d.add(user, refs)
        result = d.build()
        maps = [e for e in result.elements if isinstance(e, Map)]
        assert len(maps) == 1
        assert len(maps[0].entries) == 1
        assert maps[0].entries[0].key == "owner"
        assert maps[0].entries[0].link == "u1"

    def test_map_with_entries_and_links(self):
        d = object_diagram()
        el = d.elements
        target = el.object("Target", ref="t1")
        m = el.map("config", entries={"env": "prod"}, links={"ref": target})
        d.add(target, m)
        result = d.build()
        maps = [e for e in result.elements if isinstance(e, Map)]
        assert len(maps[0].entries) == 2

    def test_hub_and_spokes(self):
        d = object_diagram()
        el = d.elements
        server = el.object("Server", ref="srv")
        c1 = el.object("Client1", ref="c1")
        c2 = el.object("Client2", ref="c2")
        d.add(server, c1, c2)
        d.hub(server, [c1, c2])
        result = d.build()
        rels = [e for e in result.elements if isinstance(e, Relationship)]
        assert len(rels) == 2
        assert all(r.type == "arrow" for r in rels)
        assert all(r.source == "srv" for r in rels)
        targets = {r.target for r in rels}
        assert targets == {"c1", "c2"}

    def test_relationship_note(self):
        d = object_diagram()
        el = d.elements
        r = d.relationships
        a = el.object("A")
        b = el.object("B")
        d.add(a, b)
        d.connect(r.arrow(a, b, note="important link"))
        result = d.build()
        rels = [e for e in result.elements if isinstance(e, Relationship)]
        assert rels[0].note is not None
        assert rels[0].note.text == "important link"

    def test_composition_note(self):
        d = object_diagram()
        el = d.elements
        r = d.relationships
        a = el.object("A")
        b = el.object("B")
        d.add(a, b)
        d.connect(r.composition(a, b, note="owns"))
        result = d.build()
        rels = [e for e in result.elements if isinstance(e, Relationship)]
        assert rels[0].note.text == "owns"


class TestObjectPlantUMLValidation:

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

    def test_plantuml_validation(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = object_diagram(title="Validation Test")
        el = d.elements
        r = d.relationships

        node = el.object("vz-node-01 : Node", ref="n1", fields={
            "totalRAM": "64 GB",
            "usedMem": "58 GB",
        })
        ct = el.object("CT-101 : Container", ref="ct101", fields={
            "physpages.l": "8 GB",
        })

        d.add(node, ct)
        d.connect(
            r.composition(node, ct),
            r.arrow(ct, node, "reports"),
        )

        puml_file = tmp_path / "object_composer.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"
