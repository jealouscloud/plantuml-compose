"""Tests for the composer base classes."""

import pytest

from plantuml_compose.composers.base import BaseComposer, EntityRef


class TestEntityRef:

    def test_name_and_ref(self):
        ref = EntityRef("Hello World")
        assert ref._name == "Hello World"
        assert ref._ref == "Hello_World"

    def test_explicit_ref(self):
        ref = EntityRef("Some Name", ref="custom")
        assert ref._ref == "custom"

    def test_child_access_by_ref(self):
        child = EntityRef("Inner Node", ref="inner")
        parent = EntityRef("Outer", children=(child,))
        assert parent.inner is child

    def test_child_access_by_bracket(self):
        child = EntityRef("Inner Node", ref="inner")
        parent = EntityRef("Outer", children=(child,))
        assert parent["Inner Node"] is child

    def test_bracket_also_works_by_ref(self):
        child = EntityRef("Inner Node", ref="inner")
        parent = EntityRef("Outer", children=(child,))
        assert parent["inner"] is child

    def test_missing_child_attr_raises(self):
        parent = EntityRef("Outer")
        with pytest.raises(AttributeError, match="no child"):
            parent.nonexistent

    def test_missing_child_bracket_raises(self):
        parent = EntityRef("Outer")
        with pytest.raises(KeyError, match="no child"):
            parent["nonexistent"]

    def test_nested_children(self):
        grandchild = EntityRef("Leaf", ref="leaf")
        child = EntityRef("Branch", ref="branch", children=(grandchild,))
        root = EntityRef("Root", children=(child,))
        assert root.branch.leaf is grandchild

    def test_hashable(self):
        ref = EntityRef("Test")
        d = {ref: "value"}
        assert d[ref] == "value"

    def test_identity_equality(self):
        a = EntityRef("Same Name")
        b = EntityRef("Same Name")
        assert a != b  # different instances
        assert a == a  # same instance

    def test_repr(self):
        ref = EntityRef("My Node", ref="my_node")
        assert "My Node" in repr(ref)
        assert "my_node" in repr(ref)

    def test_data_storage(self):
        ref = EntityRef("Test", data={"color": "red", "boxless": True})
        assert ref._data["color"] == "red"
        assert ref._data["boxless"] is True


class TestBaseComposer:

    class _DummyComposer(BaseComposer):
        def build(self):
            return {"elements": self._elements, "connections": self._connections}

    def test_add_single_returns_item(self):
        d = self._DummyComposer()
        item = EntityRef("Foo")
        result = d.add(item)
        assert result is item

    def test_add_multiple_returns_tuple(self):
        d = self._DummyComposer()
        a = EntityRef("A")
        b = EntityRef("B")
        result = d.add(a, b)
        assert result == (a, b)

    def test_add_accumulates(self):
        d = self._DummyComposer()
        d.add(EntityRef("A"))
        d.add(EntityRef("B"))
        assert len(d._elements) == 2

    def test_connect_variadic(self):
        d = self._DummyComposer()
        d.connect("arrow1", "arrow2")
        assert d._connections == ["arrow1", "arrow2"]

    def test_connect_list(self):
        d = self._DummyComposer()
        d.connect(["arrow1", "arrow2"])
        assert d._connections == ["arrow1", "arrow2"]

    def test_connect_mixed(self):
        d = self._DummyComposer()
        d.connect("single", ["list1", "list2"], "another")
        assert d._connections == ["single", "list1", "list2", "another"]

    def test_note(self):
        d = self._DummyComposer()
        ref = EntityRef("Target")
        d.note("some text", target=ref, position="left")
        assert len(d._notes) == 1
        assert d._notes[0]["content"] == "some text"
        assert d._notes[0]["target"] is ref
        assert d._notes[0]["position"] == "left"

    def test_separator(self):
        d = self._DummyComposer()
        d.separator("Section 1")
        assert ("__separator__", "Section 1") in d._elements
