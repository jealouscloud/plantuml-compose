"""Tests for the use case diagram composer."""

import subprocess

import pytest

from plantuml_compose.composers.usecase import usecase_diagram
from plantuml_compose.primitives.usecase import (
    Actor,
    Container,
    Relationship,
    UseCase,
    UseCaseDiagram,
    UseCaseNote,
)
from plantuml_compose.renderers import render


class TestUseCaseComposer:

    def test_empty_diagram(self):
        d = usecase_diagram()
        result = d.build()
        assert isinstance(result, UseCaseDiagram)
        assert result.elements == ()

    def test_actor(self):
        d = usecase_diagram()
        el = d.elements
        d.add(el.actor("Engineer"))
        result = d.build()
        assert len(result.elements) == 1
        assert isinstance(result.elements[0], Actor)
        assert result.elements[0].name == "Engineer"

    def test_usecase_in_package(self):
        d = usecase_diagram()
        el = d.elements
        d.add(el.package("Lifecycle",
            el.usecase("View Alerts", ref="view_alerts"),
            el.usecase("Open Incident", ref="open_incident"),
        ))
        result = d.build()
        pkg = result.elements[0]
        assert isinstance(pkg, Container)
        assert pkg.type == "package"
        assert len(pkg.elements) == 2
        assert isinstance(pkg.elements[0], UseCase)
        assert pkg.elements[0].name == "View Alerts"

    def test_generalizes(self):
        """Generalizes maps child as source, parent as target, type extension."""
        d = usecase_diagram()
        el = d.elements
        r = d.relationships
        engineer = el.actor("Engineer")
        oncall = el.actor("OnCall Engineer", ref="oncall")
        d.add(engineer, oncall)
        d.connect(r.generalizes(oncall, engineer, direction="up"))
        result = d.build()
        rels = [e for e in result.elements if isinstance(e, Relationship)]
        assert len(rels) == 1
        assert rels[0].type == "extension"
        assert rels[0].source == "oncall"
        assert rels[0].target == "Engineer"
        assert rels[0].direction == "up"

    def test_include(self):
        d = usecase_diagram()
        el = d.elements
        r = d.relationships
        checkout = el.usecase("Checkout")
        validate = el.usecase("Validate Cart", ref="validate")
        d.add(checkout, validate)
        d.connect(r.include(checkout, validate))
        result = d.build()
        rels = [e for e in result.elements if isinstance(e, Relationship)]
        assert len(rels) == 1
        assert rels[0].type == "include"
        assert rels[0].source == "Checkout"
        assert rels[0].target == "validate"

    def test_extends(self):
        d = usecase_diagram()
        el = d.elements
        r = d.relationships
        checkout = el.usecase("Checkout")
        coupon = el.usecase("Apply Coupon", ref="coupon")
        d.add(checkout, coupon)
        d.connect(r.extends(coupon, checkout))
        result = d.build()
        rels = [e for e in result.elements if isinstance(e, Relationship)]
        assert rels[0].type == "extends"
        assert rels[0].source == "coupon"
        assert rels[0].target == "Checkout"

    def test_child_access(self):
        """Child access works for wiring connections."""
        d = usecase_diagram()
        el = d.elements
        r = d.relationships

        lifecycle = el.package("Lifecycle",
            el.usecase("View Alerts", ref="view_alerts"),
            el.usecase("Open Incident", ref="open_incident"),
        )

        d.add(lifecycle)

        # Access children by ref
        assert lifecycle.view_alerts._name == "View Alerts"
        assert lifecycle.view_alerts._ref == "view_alerts"

        # Access children by name
        assert lifecycle["View Alerts"]._name == "View Alerts"

    def test_child_access_in_connections(self):
        d = usecase_diagram()
        el = d.elements
        r = d.relationships

        engineer = el.actor("Engineer")
        lifecycle = el.package("Lifecycle",
            el.usecase("View Alerts", ref="view_alerts"),
        )

        d.add(engineer, lifecycle)
        d.connect(r.arrow(engineer, lifecycle.view_alerts))
        result = d.build()

        rels = [e for e in result.elements if isinstance(e, Relationship)]
        assert rels[0].source == "Engineer"
        assert rels[0].target == "view_alerts"

    def test_arrow_with_label(self):
        d = usecase_diagram()
        el = d.elements
        r = d.relationships
        monitoring = el.actor("Monitoring", ref="mon")
        incident = el.usecase("Open Incident", ref="open")
        d.add(monitoring, incident)
        d.connect(r.arrow(monitoring, incident, "triggers"))
        result = d.build()
        rels = [e for e in result.elements if isinstance(e, Relationship)]
        assert rels[0].label.text == "triggers"

    def test_note(self):
        d = usecase_diagram()
        el = d.elements
        uc = el.usecase("Browse")
        d.add(uc)
        d.note("Primary entry point", target=uc)
        result = d.build()
        notes = [e for e in result.elements if isinstance(e, UseCaseNote)]
        assert len(notes) == 1
        assert notes[0].content == "Primary entry point"

    def test_actor_style(self):
        d = usecase_diagram(actor_style="awesome")
        el = d.elements
        d.add(el.actor("User"))
        result = d.build()
        assert result.actor_style == "awesome"

    def test_title_and_theme(self):
        d = usecase_diagram(title="Shopping", theme="plain")
        result = d.build()
        assert result.title == "Shopping"
        assert result.theme == "plain"

    def test_render_produces_plantuml(self):
        d = usecase_diagram(title="Test")
        el = d.elements
        r = d.relationships
        user = el.actor("User")
        browse = el.usecase("Browse")
        d.add(user, browse)
        d.connect(r.arrow(user, browse))
        result = render(d)
        assert "@startuml" in result
        assert "User" in result
        assert "@enduml" in result

class TestUseCasePlantUMLValidation:

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

        d = usecase_diagram(title="Validation Test", actor_style="awesome")
        el = d.elements
        r = d.relationships

        engineer = el.actor("Engineer")
        oncall = el.actor("OnCall Engineer", ref="oncall")

        lifecycle = el.package("Incident Lifecycle",
            el.usecase("View Alerts", ref="view_alerts"),
            el.usecase("Open Incident", ref="open_incident"),
        )

        d.add(engineer, oncall, lifecycle)
        d.connect(
            r.generalizes(oncall, engineer, direction="up"),
            r.arrow(engineer, lifecycle.view_alerts),
            r.arrow(engineer, lifecycle.open_incident),
        )

        puml_file = tmp_path / "usecase_composer.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"
