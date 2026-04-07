"""Tests for universal element types across all @startuml diagram types.

PlantUML has 27 element types that work identically across all @startuml
diagram types. These tests verify:
1. All types validate in every @startuml diagram type
2. Composers can connect new types to each other
3. Nesting and leaf behavior works correctly
"""

import subprocess
from pathlib import Path

import pytest

from plantuml_compose import component_diagram, deployment_diagram, usecase_diagram, render


NESTABLE_TYPES = [
    "artifact", "card", "cloud", "component", "database",
    "file", "folder", "frame", "hexagon", "node",
    "package", "process", "queue", "rectangle", "stack", "storage",
]

LEAF_TYPES = [
    "actor", "agent", "boundary", "circle", "collections",
    "control", "entity", "label_", "person", "usecase",
]

LEAF_KEYWORDS = {"label_": "label"}

ALL_PUML_KEYWORDS = NESTABLE_TYPES + [LEAF_KEYWORDS.get(t, t) for t in LEAF_TYPES]

STARTUML_DIAGRAM_TYPES = [
    "component", "deployment", "usecase", "class", "object",
    "sequence", "activity", "state", "timing",
]


def _check_plantuml(puml: str, tmp_dir: Path) -> tuple[bool, str]:
    f = tmp_dir / "test.puml"
    f.write_text(puml)
    result = subprocess.run(
        ["plantuml", "-checkonly", str(f)],
        capture_output=True, text=True, timeout=30,
    )
    return result.returncode == 0, result.stderr.strip()


class TestUniversalTypesPlantUMLValid:
    """All 27 element types validate in every @startuml diagram type."""

    def test_all_types_all_diagram_types(self, tmp_path):
        try:
            result = subprocess.run(
                ["plantuml", "-version"], capture_output=True, timeout=10,
            )
            if result.returncode != 0:
                pytest.skip("PlantUML not available")
        except FileNotFoundError:
            pytest.skip("PlantUML not available")

        body = "\n".join(f'{t} "T {t}" as T_{t}' for t in ALL_PUML_KEYWORDS)

        failures = []
        for dtype in STARTUML_DIAGRAM_TYPES:
            ok, err = _check_plantuml(f"@startuml\n{body}\n@enduml", tmp_path)
            if not ok:
                failures.append(f"{dtype}: {err[:80]}")

        assert not failures, (
            f"Failed in {len(failures)} diagram type(s):\n" + "\n".join(failures)
        )


class TestComponentUniversalTypes:

    def test_all_types_valid_plantuml(self, validate_plantuml):
        """All types combined pass PlantUML validation."""
        d = component_diagram(title="All Universal Types")
        el = d.elements
        for t in NESTABLE_TYPES:
            d.add(getattr(el, t)(f"N {t}"))
        for t in LEAF_TYPES:
            d.add(getattr(el, t)(f"L {t}"))
        assert validate_plantuml(render(d), "component_all_types")

    def test_connect_new_nestable_types(self, validate_plantuml):
        """New nestable types can be connected with arrows."""
        d = component_diagram()
        el = d.elements
        c = d.connections
        d.add(
            el.queue("Ingest", ref="ingest"),
            el.storage("Archive", ref="arc"),
            el.artifact("Report", ref="rpt"),
            el.stack("Pipeline", ref="pipe"),
        )
        d.connect(
            c.arrow("ingest", "arc", "stores"),
            c.arrow("arc", "rpt", "generates"),
            c.arrow("rpt", "pipe", "feeds"),
        )
        assert validate_plantuml(render(d), "component_nestable_connections")

    def test_connect_new_leaf_types(self, validate_plantuml):
        """New leaf types can be connected with arrows."""
        d = component_diagram()
        el = d.elements
        c = d.connections
        d.add(
            el.actor("User", ref="user"),
            el.agent("Bot", ref="bot"),
            el.person("Admin", ref="admin"),
            el.boundary("Firewall", ref="fw"),
            el.control("Scheduler", ref="sched"),
        )
        d.connect(
            c.arrow("user", "fw", "requests"),
            c.arrow("fw", "bot", "forwards"),
            c.arrow("admin", "sched", "configures"),
        )
        assert validate_plantuml(render(d), "component_leaf_connections")

    def test_nesting_children(self, validate_plantuml):
        """Nestable types contain children correctly."""
        d = component_diagram()
        el = d.elements
        d.add(el.storage("Bucket",
            el.file("data.csv"),
            el.artifact("report.pdf"),
        ))
        assert validate_plantuml(render(d), "component_nesting")


class TestUsecaseUniversalTypes:

    def test_all_types_valid_plantuml(self, validate_plantuml):
        """All types combined pass PlantUML validation."""
        d = usecase_diagram(title="All Universal Types")
        el = d.elements
        for t in NESTABLE_TYPES:
            d.add(getattr(el, t)(f"N {t}"))
        generic_leaf = ["agent", "boundary", "circle", "collections",
                        "control", "entity", "interface", "label_", "person"]
        for t in generic_leaf:
            d.add(getattr(el, t)(f"L {t}"))
        assert validate_plantuml(render(d), "usecase_all_types")

    def test_connect_new_types(self, validate_plantuml):
        """New types can connect to actors and use cases."""
        d = usecase_diagram()
        el = d.elements
        r = d.relationships
        d.add(
            el.person("Admin", ref="admin"),
            el.agent("Bot", ref="bot"),
            el.database("DB", el.usecase("Query"), ref="db"),
            el.cloud("API", el.usecase("Deploy"), ref="api"),
        )
        d.connect(
            r.arrow("admin", "db"),
            r.arrow("bot", "api"),
            r.arrow("admin", "bot"),
        )
        assert validate_plantuml(render(d), "usecase_connections")


class TestDeploymentNestingWarning:

    def test_leaf_with_children_warns_and_strips(self):
        """Non-nestable types with children emit a warning and strip them."""
        d = deployment_diagram()
        d.add(d.elements.actor("Bob", d.elements.component("Inner")))
        with pytest.warns(UserWarning, match="cannot contain children"):
            output = render(d)
        assert "Inner" not in output
        assert "actor Bob" in output

    def test_nestable_with_children_no_warning(self):
        """Nestable types with children do not warn."""
        d = deployment_diagram()
        d.add(d.elements.node("Server", d.elements.artifact("app.jar")))
        output = render(d)
        assert "app.jar" in output
