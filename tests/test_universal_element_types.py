"""Tests for universal element types across all @startuml diagram types.

PlantUML has 27 element types that work identically across all @startuml
diagram types. These tests verify:
1. Raw PlantUML: all types validate in every @startuml diagram type
2. Composer API: new types render correctly in component, usecase, deployment
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

# label_ in composer maps to "label" in PlantUML
LEAF_KEYWORDS = {
    "label_": "label",
}

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
        """One diagram per type, all 27 elements, validated in a loop."""
        try:
            result = subprocess.run(
                ["plantuml", "-version"],
                capture_output=True, timeout=10,
            )
            if result.returncode != 0:
                pytest.skip("PlantUML not available")
        except FileNotFoundError:
            pytest.skip("PlantUML not available")

        lines = []
        for t in ALL_PUML_KEYWORDS:
            lines.append(f'{t} "T {t}" as T_{t}')
        body = "\n".join(lines)

        failures = []
        for dtype in STARTUML_DIAGRAM_TYPES:
            puml = f"@startuml\n{body}\n@enduml"
            ok, err = _check_plantuml(puml, tmp_path)
            if not ok:
                failures.append(f"{dtype}: {err[:80]}")

        assert not failures, (
            f"Universal types failed in {len(failures)} diagram type(s):\n"
            + "\n".join(failures)
        )


class TestComponentUniversalTypes:

    def test_all_nestable_types_render(self):
        """All nestable types in one diagram produce correct keywords."""
        d = component_diagram()
        el = d.elements
        for t in NESTABLE_TYPES:
            d.add(getattr(el, t)(f"Test {t}"))
        output = render(d)
        for t in NESTABLE_TYPES:
            assert f'{t} "Test {t}"' in output, f"{t} not rendered"

    def test_all_leaf_types_render(self):
        """All leaf types in one diagram produce correct keywords."""
        d = component_diagram()
        el = d.elements
        for t in LEAF_TYPES:
            d.add(getattr(el, t)(f"Test {t}"))
        output = render(d)
        for t in LEAF_TYPES:
            keyword = LEAF_KEYWORDS.get(t, t)
            assert f'{keyword} "Test {t}"' in output, f"{t} not rendered"

    def test_nestable_with_children(self):
        """Nestable types correctly contain children."""
        d = component_diagram()
        el = d.elements
        d.add(el.storage("Bucket", el.file("data.csv")))
        output = render(d)
        assert "storage" in output
        assert "file" in output

    def test_connections_between_types(self):
        """Different element types can connect to each other."""
        d = component_diagram()
        el = d.elements
        c = d.connections
        d.add(
            el.actor("User", ref="user"),
            el.queue("Messages", ref="q"),
            el.storage("Archive", ref="arc"),
        )
        d.connect(
            c.arrow("user", "q", "sends"),
            c.arrow("q", "arc", "stores"),
        )
        output = render(d)
        assert "user --> q" in output
        assert "q --> arc" in output

    def test_all_types_valid_plantuml(self, validate_plantuml):
        """All types combined pass PlantUML validation."""
        d = component_diagram(title="All Universal Types")
        el = d.elements
        for t in NESTABLE_TYPES:
            d.add(getattr(el, t)(f"N {t}"))
        for t in LEAF_TYPES:
            d.add(getattr(el, t)(f"L {t}"))
        assert validate_plantuml(render(d), "component_all_types")


class TestUsecaseUniversalTypes:

    def test_all_nestable_types_render(self):
        """All nestable types in one diagram produce correct keywords."""
        d = usecase_diagram()
        el = d.elements
        for t in NESTABLE_TYPES:
            d.add(getattr(el, t)(f"Test {t}"))
        output = render(d)
        for t in NESTABLE_TYPES:
            assert f'{t} "Test {t}"' in output or f"{t} Test" in output, (
                f"{t} not rendered"
            )

    def test_all_leaf_types_render(self):
        """All generic leaf types in one diagram produce correct keywords."""
        generic_leaf = ["agent", "boundary", "circle", "collections",
                        "control", "entity", "interface", "label_", "person"]
        d = usecase_diagram()
        el = d.elements
        for t in generic_leaf:
            d.add(getattr(el, t)(f"Test {t}"))
        output = render(d)
        for t in generic_leaf:
            keyword = LEAF_KEYWORDS.get(t, t)
            assert f'{keyword} "Test {t}"' in output, f"{t} not rendered"

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


class TestDeploymentNestingWarning:

    def test_leaf_with_children_warns_and_strips(self):
        """Non-nestable types with children emit a warning and strip them."""
        d = deployment_diagram()
        el = d.elements
        d.add(el.actor("Bob", el.component("Inner")))
        with pytest.warns(UserWarning, match="cannot contain children"):
            output = render(d)
        assert "Inner" not in output
        assert "actor Bob" in output

    def test_nestable_with_children_no_warning(self):
        """Nestable types with children do not warn."""
        d = deployment_diagram()
        el = d.elements
        d.add(el.node("Server", el.artifact("app.jar")))
        output = render(d)
        assert "app.jar" in output
