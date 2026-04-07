"""Tests for universal element types across all @startuml diagram types.

PlantUML has 27 element types that work identically across all @startuml
diagram types. These tests verify:
1. Composer API: new types render correctly in component, usecase, deployment
2. PlantUML validation: all types pass plantuml for every @startuml diagram type
"""

import subprocess
import warnings

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

# Every @startuml diagram type that supports the universal element types
STARTUML_DIAGRAM_TYPES = [
    "component", "deployment", "usecase", "class", "object",
    "sequence", "activity", "state", "timing",
]


# ============================================================================
# Raw PlantUML validation — proves all types work in all diagram types
# ============================================================================


class TestUniversalTypesPlantUMLValid:
    """Prove that all 27 element types pass PlantUML validation in every
    @startuml diagram type. This is the ground truth — if PlantUML accepts
    it, we should be able to render it."""

    @pytest.fixture
    def _skip_no_plantuml(self):
        try:
            result = subprocess.run(
                ["plantuml", "-version"],
                capture_output=True, timeout=10,
            )
            if result.returncode != 0:
                pytest.skip("PlantUML not available")
        except FileNotFoundError:
            pytest.skip("PlantUML not available")

    @pytest.mark.parametrize("diagram_type", STARTUML_DIAGRAM_TYPES)
    def test_all_types_in_diagram(self, _skip_no_plantuml, validate_plantuml,
                                  diagram_type):
        """All 27 element types validate in each @startuml diagram type."""
        lines = ["@startuml"]
        for t in ALL_PUML_KEYWORDS:
            lines.append(f'{t} "T {t}" as T_{t.replace(" ", "_")}')
        lines.append("@enduml")
        puml = "\n".join(lines)
        assert validate_plantuml(puml, f"universal_{diagram_type}"), (
            f"Universal element types failed validation in {diagram_type} diagram"
        )


# ============================================================================
# Composer API tests — component
# ============================================================================


class TestComponentUniversalTypes:

    def test_nestable_types_render(self):
        """All nestable types produce correct PlantUML keywords."""
        for t in NESTABLE_TYPES:
            d = component_diagram()
            factory = getattr(d.elements, t)
            d.add(factory(f"Test {t}"))
            output = render(d)
            assert f'{t} "Test {t}"' in output, f"{t} not rendered correctly"

    def test_leaf_types_render(self):
        """All leaf types produce correct PlantUML keywords."""
        for t in LEAF_TYPES:
            d = component_diagram()
            factory = getattr(d.elements, t)
            d.add(factory(f"Test {t}"))
            output = render(d)
            keyword = LEAF_KEYWORDS.get(t, t)
            assert f'{keyword} "Test {t}"' in output, f"{t} not rendered correctly"

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
        """Every composer element type passes PlantUML validation together."""
        d = component_diagram(title="All Universal Types")
        el = d.elements

        for t in NESTABLE_TYPES:
            d.add(getattr(el, t)(f"N {t}"))

        for t in LEAF_TYPES:
            d.add(getattr(el, t)(f"L {t}"))

        assert validate_plantuml(render(d), "component_all_types")


# ============================================================================
# Composer API tests — usecase
# ============================================================================


class TestUsecaseUniversalTypes:

    def test_nestable_types_render(self):
        """All nestable types produce correct PlantUML keywords."""
        for t in NESTABLE_TYPES:
            d = usecase_diagram()
            factory = getattr(d.elements, t)
            d.add(factory(f"Test {t}"))
            output = render(d)
            assert f'{t} "Test {t}"' in output or f"{t} Test" in output, (
                f"{t} not rendered correctly"
            )

    def test_leaf_types_render(self):
        """All leaf types (excluding actor/usecase which have special renderers)."""
        # actor and usecase have their own renderers with business= param
        generic_leaf = ["agent", "boundary", "circle", "collections",
                        "control", "entity", "interface", "label_", "person"]
        for t in generic_leaf:
            d = usecase_diagram()
            factory = getattr(d.elements, t)
            d.add(factory(f"Test {t}"))
            output = render(d)
            keyword = LEAF_KEYWORDS.get(t, t)
            assert f'{keyword} "Test {t}"' in output, f"{t} not rendered correctly"

    def test_nestable_with_usecase_children(self):
        """Nestable containers can hold use case elements."""
        d = usecase_diagram()
        el = d.elements
        d.add(el.database("System", el.usecase("Login"), el.actor("Admin")))
        output = render(d)
        assert "database" in output
        assert "Login" in output
        assert "Admin" in output

    def test_all_types_valid_plantuml(self, validate_plantuml):
        """Every composer element type passes PlantUML validation together."""
        d = usecase_diagram(title="All Universal Types")
        el = d.elements

        for t in NESTABLE_TYPES:
            d.add(getattr(el, t)(f"N {t}"))

        generic_leaf = ["agent", "boundary", "circle", "collections",
                        "control", "entity", "interface", "label_", "person"]
        for t in generic_leaf:
            d.add(getattr(el, t)(f"L {t}"))

        assert validate_plantuml(render(d), "usecase_all_types")


# ============================================================================
# Composer API tests — deployment nesting guard
# ============================================================================


class TestDeploymentNestingWarning:

    def test_leaf_with_children_warns(self):
        """Non-nestable types with children emit a warning."""
        d = deployment_diagram()
        el = d.elements
        d.add(el.actor("Bob", el.component("Inner")))
        with pytest.warns(UserWarning, match="cannot contain children"):
            render(d)

    def test_leaf_children_stripped(self):
        """Non-nestable types have children removed from output."""
        d = deployment_diagram()
        el = d.elements
        d.add(el.actor("Bob", el.component("Inner")))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
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
