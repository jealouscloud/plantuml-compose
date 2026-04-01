"""Pytest tests for arrow length= across all diagram types.

These verify both primitive round-trip and rendered PlantUML output.
Run from project root: uv run pytest one-offs/test_arrow_length_pytest.py -v
"""
import subprocess

import pytest

from plantuml_compose import (
    class_diagram,
    component_diagram,
    deployment_diagram,
    object_diagram,
    render,
    sequence_diagram,
    state_diagram,
    usecase_diagram,
)


class TestArrowLengthState:

    def test_length_default(self):
        d = state_diagram()
        el = d.elements
        t = d.transitions
        a, b = el.state("A"), el.state("B")
        d.add(a, b)
        d.connect(t.transition(a, b))
        output = render(d)
        assert "A --> B" in output

    def test_length_1(self):
        d = state_diagram()
        el = d.elements
        t = d.transitions
        a, b = el.state("A"), el.state("B")
        d.add(a, b)
        d.connect(t.transition(a, b, length=1))
        output = render(d)
        assert "A -> B" in output
        assert "A --> B" not in output

    def test_length_3(self):
        d = state_diagram()
        el = d.elements
        t = d.transitions
        a, b = el.state("A"), el.state("B")
        d.add(a, b)
        d.connect(t.transition(a, b, length=3))
        output = render(d)
        assert "A ---> B" in output

    def test_length_with_label(self):
        d = state_diagram()
        el = d.elements
        t = d.transitions
        a, b = el.state("A"), el.state("B")
        d.add(a, b)
        d.connect(t.transition(a, b, label="go", length=1))
        output = render(d)
        assert "A -> B : go" in output

    def test_length_primitive_roundtrip(self):
        d = state_diagram()
        el = d.elements
        t = d.transitions
        a, b = el.state("A"), el.state("B")
        d.add(a, b)
        d.connect(t.transition(a, b, length=3))
        result = d.build()
        transitions = [e for e in result.elements if hasattr(e, 'length')]
        assert len(transitions) == 1
        assert transitions[0].length == 3


class TestArrowLengthClass:

    def test_extends_length_1(self):
        d = class_diagram()
        el = d.elements
        r = d.relationships
        parent = el.class_("Parent")
        child = el.class_("Child")
        d.add(parent, child)
        d.connect(r.extends(child, parent, length=1))
        output = render(d)
        # Should have single dash extension arrow
        assert "<|-" in output
        # Should NOT have double dash
        lines = [l for l in output.split("\n") if "<|" in l]
        assert len(lines) == 1
        assert "<|--" not in lines[0]

    def test_association_length_3(self):
        d = class_diagram()
        el = d.elements
        r = d.relationships
        a = el.class_("A")
        b = el.class_("B")
        d.add(a, b)
        d.connect(r.association(a, b, length=3))
        output = render(d)
        assert "---" in output


class TestArrowLengthComponent:

    def test_arrow_length_1(self):
        d = component_diagram()
        el = d.elements
        c = d.connections
        a = el.component("API")
        b = el.component("DB")
        d.add(a, b)
        d.connect(c.arrow(a, b, length=1))
        output = render(d)
        assert "API -> DB" in output
        assert "API --> DB" not in output

    def test_arrow_length_3(self):
        d = component_diagram()
        el = d.elements
        c = d.connections
        a = el.component("API")
        b = el.component("DB")
        d.add(a, b)
        d.connect(c.arrow(a, b, length=3))
        output = render(d)
        assert "API ---> DB" in output

    def test_chain_with_length(self):
        d = component_diagram()
        el = d.elements
        c = d.connections
        a = el.component("A")
        b = el.component("B")
        cx = el.component("C")
        d.add(a, b, cx)
        d.connect(c.chain(a, b, cx, length=1))
        output = render(d)
        assert "A -> B" in output
        assert "B -> C" in output


class TestArrowLengthDeployment:

    def test_arrow_length_1(self):
        d = deployment_diagram()
        el = d.elements
        c = d.connections
        a = el.node("Web")
        b = el.node("DB")
        d.add(a, b)
        d.connect(c.arrow(a, b, length=1))
        output = render(d)
        assert "Web -> DB" in output
        assert "Web --> DB" not in output

    def test_line_length_3(self):
        d = deployment_diagram()
        el = d.elements
        c = d.connections
        a = el.node("A")
        b = el.node("B")
        d.add(a, b)
        d.connect(c.line(a, b, length=3))
        output = render(d)
        assert "---" in output


class TestArrowLengthUsecase:

    def test_arrow_length_1(self):
        d = usecase_diagram()
        el = d.elements
        r = d.relationships
        user = el.actor("User")
        uc = el.usecase("Login")
        d.add(user, uc)
        d.connect(r.arrow(user, uc, length=1))
        output = render(d)
        assert "User -> Login" in output or 'User -> (Login)' in output

    def test_include_length_3(self):
        d = usecase_diagram()
        el = d.elements
        r = d.relationships
        a = el.usecase("A")
        b = el.usecase("B")
        d.add(a, b)
        d.connect(r.include(a, b, length=3))
        output = render(d)
        # Include uses dotted arrows
        assert "..." in output


class TestArrowLengthObject:

    def test_arrow_length_1(self):
        d = object_diagram()
        el = d.elements
        r = d.relationships
        a = el.object("A")
        b = el.object("B")
        d.add(a, b)
        d.connect(r.arrow(a, b, length=1))
        output = render(d)
        assert "A -> B" in output
        assert "A --> B" not in output

    def test_composition_length_3(self):
        d = object_diagram()
        el = d.elements
        r = d.relationships
        a = el.object("A")
        b = el.object("B")
        d.add(a, b)
        d.connect(r.composition(a, b, length=3))
        output = render(d)
        assert "---" in output


class TestArrowLengthPlantUMLValidation:

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

    def test_state_length_valid(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")
        d = state_diagram()
        el = d.elements
        t = d.transitions
        a, b, c = el.state("A"), el.state("B"), el.state("C")
        d.add(a, b, c)
        d.connect(
            t.transition(a, b, length=1),
            t.transition(b, c, length=3),
        )
        puml = tmp_path / "length.puml"
        puml.write_text(render(d))
        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_class_length_valid(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")
        d = class_diagram()
        el = d.elements
        r = d.relationships
        a, b = el.class_("A"), el.class_("B")
        d.add(a, b)
        d.connect(r.extends(b, a, length=1))
        d.connect(r.association(a, b, length=3))
        puml = tmp_path / "length.puml"
        puml.write_text(render(d))
        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_component_length_valid(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")
        d = component_diagram()
        el = d.elements
        c = d.connections
        a, b = el.component("A"), el.component("B")
        d.add(a, b)
        d.connect(c.arrow(a, b, length=1))
        d.connect(c.arrow(b, a, length=3))
        puml = tmp_path / "length.puml"
        puml.write_text(render(d))
        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"
