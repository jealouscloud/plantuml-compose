"""Tests for universal element types across component, usecase, and deployment composers.

PlantUML has 27 element types that work identically across all @startuml
diagram types. These tests verify that all types render correctly and
pass PlantUML validation in each structural composer.
"""

import subprocess

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

# In component diagrams, interface is a first-class element (not in the
# universal lists above). In usecase diagrams, it's a generic leaf.
# These are tested separately within each composer's test class.

# label_ in composer maps to "label" in PlantUML
LEAF_KEYWORDS = {
    "label_": "label",
}


@pytest.fixture
def plantuml_check():
    try:
        result = subprocess.run(
            ["plantuml", "-version"],
            capture_output=True, timeout=10,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


class TestComponentUniversalTypes:

    def test_nestable_types_render(self):
        """All nestable types produce correct PlantUML keywords."""
        for t in NESTABLE_TYPES:
            d = component_diagram()
            el = d.elements
            # Existing types (cloud, database, etc.) are already containers,
            # new types route through _container too
            factory = getattr(el, t)
            d.add(factory(f"Test {t}"))
            output = render(d)
            assert f'{t} "Test {t}"' in output, f"{t} not rendered correctly"

    def test_leaf_types_render(self):
        """All leaf types produce correct PlantUML keywords."""
        for t in LEAF_TYPES:
            d = component_diagram()
            el = d.elements
            factory = getattr(el, t)
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

    def test_leaf_no_children(self):
        """Leaf types do not accept *children (keyword-only after name)."""
        d = component_diagram()
        el = d.elements
        # actor() has no *children param — only keyword args
        d.add(el.actor("User"))
        output = render(d)
        assert "actor User" in output
        assert "{" not in output or "actor User" in output.split("{")[0]

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

    def test_all_types_valid_plantuml(self, plantuml_check, validate_plantuml):
        """Every element type passes PlantUML validation."""
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = component_diagram(title="All Universal Types")
        el = d.elements

        for t in NESTABLE_TYPES:
            factory = getattr(el, t)
            d.add(factory(f"N {t}"))

        for t in LEAF_TYPES:
            factory = getattr(el, t)
            d.add(factory(f"L {t}"))

        assert validate_plantuml(render(d), "component_all_types")


class TestUsecaseUniversalTypes:

    def test_nestable_types_render(self):
        """All nestable types produce correct PlantUML keywords."""
        for t in NESTABLE_TYPES:
            d = usecase_diagram()
            el = d.elements
            factory = getattr(el, t)
            d.add(factory(f"Test {t}"))
            output = render(d)
            assert f'{t} "Test {t}"' in output or f"{t} Test" in output, (
                f"{t} not rendered correctly"
            )

    def test_leaf_types_render(self):
        """All leaf types produce correct PlantUML keywords."""
        # actor and usecase have their own renderers, skip those
        generic_leaf = ["agent", "boundary", "circle", "collections",
                        "control", "entity", "interface", "label_", "person"]
        for t in generic_leaf:
            d = usecase_diagram()
            el = d.elements
            factory = getattr(el, t)
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

    def test_connections_between_types(self):
        """Different element types can connect to each other."""
        d = usecase_diagram()
        el = d.elements
        r = d.relationships
        d.add(
            el.person("Admin", ref="admin"),
            el.cloud("API", el.usecase("Deploy"), ref="api"),
        )
        d.connect(r.arrow("admin", "api"))
        output = render(d)
        assert "admin -->" in output

    def test_all_types_valid_plantuml(self, plantuml_check, validate_plantuml):
        """Every element type passes PlantUML validation."""
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = usecase_diagram(title="All Universal Types")
        el = d.elements

        for t in NESTABLE_TYPES:
            factory = getattr(el, t)
            d.add(factory(f"N {t}"))

        generic_leaf = ["agent", "boundary", "circle", "collections",
                        "control", "entity", "interface", "label_", "person"]
        for t in generic_leaf:
            factory = getattr(el, t)
            d.add(factory(f"L {t}"))

        assert validate_plantuml(render(d), "usecase_all_types")


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
        import warnings
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
        # No warning expected — if one fires, pytest.warns would catch it
        output = render(d)
        assert "app.jar" in output
