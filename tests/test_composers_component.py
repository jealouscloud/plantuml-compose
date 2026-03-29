"""Tests for the component diagram composer."""

import subprocess

import pytest

from plantuml_compose.composers.component import component_diagram
from plantuml_compose.primitives.component import (
    Component,
    ComponentDiagram,
    ComponentNote,
    Container,
    Interface,
    Relationship,
)
from plantuml_compose.renderers import render


class TestComponentComposer:

    def test_empty_diagram(self):
        d = component_diagram()
        result = d.build()
        assert isinstance(result, ComponentDiagram)
        assert result.elements == ()

    def test_standalone_component(self):
        d = component_diagram()
        el = d.elements
        d.add(el.component("API"))
        result = d.build()
        assert len(result.elements) == 1
        assert isinstance(result.elements[0], Component)
        assert result.elements[0].name == "API"

    def test_standalone_interface(self):
        d = component_diagram()
        el = d.elements
        d.add(el.interface("IService"))
        result = d.build()
        assert isinstance(result.elements[0], Interface)

    def test_package_with_children(self):
        d = component_diagram()
        el = d.elements
        d.add(el.package("MyPkg",
            el.component("Foo"),
            el.component("Bar"),
        ))
        result = d.build()
        pkg = result.elements[0]
        assert isinstance(pkg, Container)
        assert pkg.type == "package"
        assert len(pkg.elements) == 2
        assert pkg.elements[0].name == "Foo"

    def test_database_container(self):
        d = component_diagram()
        el = d.elements
        d.add(el.database("Redis"))
        result = d.build()
        assert isinstance(result.elements[0], Container)
        assert result.elements[0].type == "database"

    def test_cloud_container(self):
        d = component_diagram()
        el = d.elements
        d.add(el.cloud("Internet"))
        result = d.build()
        assert isinstance(result.elements[0], Container)
        assert result.elements[0].type == "cloud"

    def test_ref_kwarg(self):
        d = component_diagram()
        el = d.elements
        comp = el.component("Long Name", ref="ln")
        d.add(comp)
        assert comp._ref == "ln"

    def test_child_access(self):
        d = component_diagram()
        el = d.elements
        pkg = el.package("Wazuh",
            el.component("Agents", ref="agents"),
            el.database("OpenSearch"),
        )
        assert pkg.agents._name == "Agents"
        assert pkg.agents._ref == "agents"
        assert pkg["OpenSearch"]._name == "OpenSearch"

    def test_arrow_connection(self):
        d = component_diagram()
        el = d.elements
        c = d.connections
        api = el.component("API")
        db = el.database("DB")
        d.add(api, db)
        d.connect(c.arrow(api, db, "queries"))
        result = d.build()
        rels = [e for e in result.elements if isinstance(e, Relationship)]
        assert len(rels) == 1
        assert rels[0].type == "arrow"
        assert rels[0].label.text == "queries"

    def test_dependency_connection(self):
        d = component_diagram()
        el = d.elements
        c = d.connections
        a = el.component("A")
        b = el.component("B")
        d.add(a, b)
        d.connect(c.dependency(a, b, "depends"))
        result = d.build()
        rels = [e for e in result.elements if isinstance(e, Relationship)]
        assert rels[0].type == "dependency"

    def test_bulk_arrows(self):
        d = component_diagram()
        el = d.elements
        c = d.connections
        a, b, x = el.component("A"), el.component("B"), el.component("X")
        d.add(a, b, x)
        d.connect(c.arrows((a, b, "ab"), (b, x, "bx")))
        result = d.build()
        rels = [e for e in result.elements if isinstance(e, Relationship)]
        assert len(rels) == 2

    def test_bulk_lines(self):
        d = component_diagram()
        el = d.elements
        c = d.connections
        a, b = el.component("A"), el.component("B")
        d.add(a, b)
        d.connect(c.lines((a, b)))
        result = d.build()
        rels = [e for e in result.elements if isinstance(e, Relationship)]
        assert rels[0].type == "association"

    def test_note(self):
        d = component_diagram()
        el = d.elements
        comp = el.component("API")
        d.add(comp)
        d.note("Main service", target=comp, position="right")
        result = d.build()
        notes = [e for e in result.elements if isinstance(e, ComponentNote)]
        assert len(notes) == 1
        assert notes[0].content == "Main service"
        assert notes[0].target == comp._ref

    def test_stereotype_string_coercion(self):
        d = component_diagram()
        el = d.elements
        d.add(el.component("Redis", stereotype="cache"))
        result = d.build()
        comp = result.elements[0]
        assert comp.stereotype is not None
        assert comp.stereotype.name == "cache"

    def test_style_dict_coercion(self):
        d = component_diagram()
        el = d.elements
        d.add(el.component("API", style={"background": "#E3F2FD"}))
        result = d.build()
        comp = result.elements[0]
        assert comp.style is not None
        assert comp.style.background is not None

    def test_title_and_theme(self):
        d = component_diagram(title="Arch", theme="vibrant")
        el = d.elements
        d.add(el.component("A"))
        result = d.build()
        assert result.title == "Arch"
        assert result.theme == "vibrant"

    def test_render_produces_plantuml(self):
        d = component_diagram(title="Test")
        el = d.elements
        c = d.connections
        a = el.component("API")
        db = el.database("DB")
        d.add(a, db)
        d.connect(c.arrow(a, db, "queries"))
        result = render(d)
        assert "@startuml" in result
        assert "API" in result
        assert "@enduml" in result

    def test_render_matches_builder_simple(self):
        """Simple components + arrow matches old builder."""
        from plantuml_compose.builders.component import (
            component_diagram as builder_component,
        )

        # Old builder
        with builder_component(title="Test") as old:
            api = old.component("API")
            db = old.component("DB")
            old.arrow(api, db, label="queries")
        old_output = render(old.build())

        # New composer
        d = component_diagram(title="Test")
        el = d.elements
        c = d.connections
        api = el.component("API")
        db = el.component("DB")
        d.add(api, db)
        d.connect(c.arrow(api, db, "queries"))
        new_output = render(d)

        assert old_output == new_output

    def test_render_matches_builder_package(self):
        """Package with children matches old builder."""
        from plantuml_compose.builders.component import (
            component_diagram as builder_component,
        )

        # Old builder
        with builder_component() as old:
            with old.package("Pkg") as pkg:
                pkg.component("Inner")
        old_output = render(old.build())

        # New composer
        d = component_diagram()
        el = d.elements
        d.add(el.package("Pkg",
            el.component("Inner"),
        ))
        new_output = render(d)

        assert old_output == new_output

    def test_nested_child_access_in_connections(self):
        """Child access works for wiring connections."""
        d = component_diagram()
        el = d.elements
        c = d.connections

        pkg = el.package("Service",
            el.component("API", ref="api"),
            el.database("DB", ref="db"),
        )
        d.add(pkg)
        d.connect(c.arrow(pkg.api, pkg.db, "queries"))

        result = d.build()
        rels = [e for e in result.elements if isinstance(e, Relationship)]
        assert rels[0].source == "api"
        assert rels[0].target == "db"


class TestComponentPlantUMLValidation:

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

    def test_architecture_valid_plantuml(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = component_diagram(title="Architecture")
        el = d.elements
        c = d.connections

        svc = el.package("Service",
            el.component("API", ref="api"),
            el.component("Worker", ref="worker"),
            el.database("Redis", ref="redis"),
        )

        ext = el.cloud("External",
            el.component("Client", ref="client"),
        )

        d.add(svc, ext)
        d.connect(
            c.arrow(ext.client, svc.api, "HTTP"),
            c.arrow(svc.api, svc.redis, "cache"),
            c.arrow(svc.api, svc.worker, "dispatch"),
        )

        puml_file = tmp_path / "component_composer.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"
