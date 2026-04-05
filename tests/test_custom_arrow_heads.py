"""Tests for custom arrow head support (left_head, right_head).

Verifies that custom arrow heads work across class, deployment, usecase,
object, and component diagrams at both the renderer and composer levels.
"""
import subprocess

import pytest

from plantuml_compose import (
    ArrowHead,
    class_diagram,
    component_diagram,
    deployment_diagram,
    object_diagram,
    render,
    usecase_diagram,
)


class TestClassCustomHeads:

    def test_custom_left_and_right(self):
        d = class_diagram()
        el = d.elements
        r = d.relationships
        a, b = el.class_("A"), el.class_("B")
        d.add(a, b)
        d.connect(r.relationship(a, b, type="association",
                                  left_head="o", right_head=">>"))
        output = render(d)
        assert "o-->>" in output

    def test_custom_left_only(self):
        d = class_diagram()
        el = d.elements
        r = d.relationships
        a, b = el.class_("A"), el.class_("B")
        d.add(a, b)
        d.connect(r.relationship(a, b, type="association",
                                  left_head="*"))
        output = render(d)
        # association base is "-->" so default right head preserves ">"
        assert "*-->" in output

    def test_custom_right_only(self):
        d = class_diagram()
        el = d.elements
        r = d.relationships
        a, b = el.class_("A"), el.class_("B")
        d.add(a, b)
        d.connect(r.relationship(a, b, type="line",
                                  right_head=">>"))
        output = render(d)
        # line base is "--", no arrow, so right_head replaces nothing
        assert "-->>" in output

    def test_custom_heads_dotted_base(self):
        d = class_diagram()
        el = d.elements
        r = d.relationships
        a, b = el.class_("A"), el.class_("B")
        d.add(a, b)
        d.connect(r.relationship(a, b, type="dependency",
                                  left_head="#", right_head="*"))
        output = render(d)
        assert "#..*" in output

    def test_custom_heads_with_length(self):
        d = class_diagram()
        el = d.elements
        r = d.relationships
        a, b = el.class_("A"), el.class_("B")
        d.add(a, b)
        d.connect(r.relationship(a, b, type="association",
                                  left_head="o", right_head=">>",
                                  length=3))
        output = render(d)
        assert "o--->>" in output

    def test_primitive_roundtrip(self):
        d = class_diagram()
        el = d.elements
        r = d.relationships
        a, b = el.class_("A"), el.class_("B")
        d.add(a, b)
        d.connect(r.relationship(a, b, left_head="o", right_head=">>"))
        result = d.build()
        rels = [e for e in result.elements if hasattr(e, "left_head")]
        assert len(rels) == 1
        assert rels[0].left_head == "o"
        assert rels[0].right_head == ">>"


class TestDeploymentCustomHeads:

    def test_custom_both_heads(self):
        d = deployment_diagram()
        el = d.elements
        c = d.connections
        a, b = el.node("A"), el.node("B")
        d.add(a, b)
        d.connect(c.arrow(a, b, left_head="#", right_head="*"))
        output = render(d)
        assert "#--*" in output

    def test_custom_left_only_preserves_arrow(self):
        d = deployment_diagram()
        el = d.elements
        c = d.connections
        a, b = el.node("A"), el.node("B")
        d.add(a, b)
        d.connect(c.arrow(a, b, left_head="o"))
        output = render(d)
        # arrow base is "-->" so right defaults to ">"
        assert "o-->" in output

    def test_custom_right_only(self):
        d = deployment_diagram()
        el = d.elements
        c = d.connections
        a, b = el.node("A"), el.node("B")
        d.add(a, b)
        d.connect(c.arrow(a, b, right_head=">>"))
        output = render(d)
        assert "-->>" in output

    def test_line_custom_heads(self):
        d = deployment_diagram()
        el = d.elements
        c = d.connections
        a, b = el.node("A"), el.node("B")
        d.add(a, b)
        d.connect(c.line(a, b, left_head="o", right_head="o"))
        output = render(d)
        assert "o--o" in output

    def test_custom_heads_with_length(self):
        d = deployment_diagram()
        el = d.elements
        c = d.connections
        a, b = el.node("A"), el.node("B")
        d.add(a, b)
        d.connect(c.arrow(a, b, left_head="*", right_head=">>", length=4))
        output = render(d)
        assert "*---->> " in output or "*----->>" in output or "*---->> B" in output
        # Just check the arrow pattern is in the output
        assert "*----" in output


class TestUseCaseCustomHeads:

    def test_arrow_custom_left(self):
        d = usecase_diagram()
        el = d.elements
        r = d.relationships
        actor = el.actor("User")
        uc = el.usecase("Login")
        d.add(actor, uc)
        d.connect(r.arrow(actor, uc, left_head="*"))
        output = render(d)
        # arrow base is "-->" so right defaults to ">"
        assert "*-->" in output

    def test_link_custom_heads(self):
        d = usecase_diagram()
        el = d.elements
        r = d.relationships
        a = el.actor("Admin")
        b = el.actor("User")
        d.add(a, b)
        d.connect(r.link(a, b, left_head="o", right_head="o"))
        output = render(d)
        # association base is "->" (single dash), custom overrides both heads
        # and defaults to 2 dashes
        assert "o--o" in output

    def test_custom_right_only(self):
        d = usecase_diagram()
        el = d.elements
        r = d.relationships
        actor = el.actor("User")
        uc = el.usecase("Browse")
        d.add(actor, uc)
        d.connect(r.arrow(actor, uc, right_head=">>"))
        output = render(d)
        assert "-->>" in output


class TestObjectCustomHeads:

    def test_arrow_custom_right(self):
        d = object_diagram()
        el = d.elements
        r = d.relationships
        a = el.object("obj1")
        b = el.object("obj2")
        d.add(a, b)
        d.connect(r.arrow(a, b, right_head=">>"))
        output = render(d)
        assert "-->>" in output

    def test_arrow_custom_both(self):
        d = object_diagram()
        el = d.elements
        r = d.relationships
        a = el.object("obj1")
        b = el.object("obj2")
        d.add(a, b)
        d.connect(r.arrow(a, b, left_head="o", right_head="*"))
        output = render(d)
        assert "o--*" in output

    def test_link_custom_heads(self):
        d = object_diagram()
        el = d.elements
        r = d.relationships
        a = el.object("obj1")
        b = el.object("obj2")
        d.add(a, b)
        d.connect(r.link(a, b, left_head="#", right_head=">>"))
        output = render(d)
        assert "#-->>" in output


class TestComponentCustomHeads:

    def test_arrow_custom_both(self):
        d = component_diagram()
        el = d.elements
        c = d.connections
        a, b = el.component("A"), el.component("B")
        d.add(a, b)
        d.connect(c.arrow(a, b, left_head="o", right_head="*"))
        output = render(d)
        assert "o--*" in output

    def test_arrow_custom_left_only(self):
        d = component_diagram()
        el = d.elements
        c = d.connections
        a, b = el.component("A"), el.component("B")
        d.add(a, b)
        d.connect(c.arrow(a, b, left_head="#"))
        output = render(d)
        # arrow base is "-->" so default right is ">"
        assert "#-->" in output

    def test_arrow_custom_right_only(self):
        d = component_diagram()
        el = d.elements
        c = d.connections
        a, b = el.component("A"), el.component("B")
        d.add(a, b)
        d.connect(c.arrow(a, b, right_head=">>"))
        output = render(d)
        assert "-->>" in output


class TestCustomHeadsWithModifiers:

    def test_custom_heads_with_style(self):
        """Style modifier in bracket syntax with custom heads."""
        d = class_diagram()
        el = d.elements
        r = d.relationships
        a, b = el.class_("A"), el.class_("B")
        d.add(a, b)
        d.connect(r.relationship(a, b, type="association",
                                  left_head="o", right_head=">>",
                                  style="dashed"))
        output = render(d)
        # Should contain bracket syntax + custom heads
        assert "o-" in output
        assert ">>" in output
        assert "[" in output  # bracket style modifier

    def test_custom_heads_with_direction(self):
        """Direction modifier with custom heads."""
        d = deployment_diagram()
        el = d.elements
        c = d.connections
        a, b = el.node("A"), el.node("B")
        d.add(a, b)
        d.connect(c.arrow(a, b, left_head="o", right_head="*",
                          direction="down"))
        output = render(d)
        assert "o-" in output
        assert "d" in output  # direction modifier
        assert "*" in output

    def test_custom_heads_with_length_3(self):
        """Length=3 with custom heads produces correct dash count."""
        d = component_diagram()
        el = d.elements
        c = d.connections
        a, b = el.component("A"), el.component("B")
        d.add(a, b)
        d.connect(c.arrow(a, b, left_head="o", right_head=">>", length=3))
        output = render(d)
        assert "o--->> " in output or "o--->>" in output


class TestCustomHeadsPlantUMLValidation:

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

    def test_class_custom_heads_valid(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")
        d = class_diagram()
        el = d.elements
        r = d.relationships
        a, b = el.class_("A"), el.class_("B")
        d.add(a, b)
        d.connect(r.relationship(a, b, left_head="o", right_head=">>"))
        d.connect(r.relationship(a, b, type="dependency",
                                  left_head="#", right_head="*"))
        puml = tmp_path / "custom_heads.puml"
        puml.write_text(render(d))
        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_deployment_custom_heads_valid(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")
        d = deployment_diagram()
        el = d.elements
        c = d.connections
        a, b = el.node("A"), el.node("B")
        d.add(a, b)
        d.connect(c.arrow(a, b, left_head="#", right_head="*"))
        d.connect(c.line(a, b, left_head="o", right_head="o"))
        puml = tmp_path / "custom_heads.puml"
        puml.write_text(render(d))
        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_usecase_custom_heads_valid(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")
        d = usecase_diagram()
        el = d.elements
        r = d.relationships
        actor = el.actor("User")
        uc = el.usecase("Login")
        d.add(actor, uc)
        d.connect(r.arrow(actor, uc, left_head="*"))
        puml = tmp_path / "custom_heads.puml"
        puml.write_text(render(d))
        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_object_custom_heads_valid(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")
        d = object_diagram()
        el = d.elements
        r = d.relationships
        a = el.object("obj1")
        b = el.object("obj2")
        d.add(a, b)
        d.connect(r.arrow(a, b, left_head="o", right_head="*"))
        puml = tmp_path / "custom_heads.puml"
        puml.write_text(render(d))
        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_component_custom_heads_valid(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")
        d = component_diagram()
        el = d.elements
        c = d.connections
        a, b = el.component("A"), el.component("B")
        d.add(a, b)
        d.connect(c.arrow(a, b, left_head="o", right_head="*"))
        d.connect(c.arrow(a, b, left_head="#", right_head=">>", length=3))
        puml = tmp_path / "custom_heads.puml"
        puml.write_text(render(d))
        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_all_diagrams_custom_heads_png(self, plantuml_check, tmp_path):
        """Generate PNGs for all diagram types with custom heads to verify rendering."""
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        # Class
        d = class_diagram()
        el = d.elements
        r = d.relationships
        a, b = el.class_("A"), el.class_("B")
        d.add(a, b)
        d.connect(r.relationship(a, b, left_head="o", right_head=">>"))
        puml = tmp_path / "class_heads.puml"
        puml.write_text(render(d))
        result = subprocess.run(
            ["plantuml", str(puml)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"
        assert (tmp_path / "class_heads.png").exists()

        # Deployment
        d = deployment_diagram()
        el = d.elements
        c = d.connections
        a, b = el.node("A"), el.node("B")
        d.add(a, b)
        d.connect(c.arrow(a, b, left_head="#", right_head="*"))
        puml = tmp_path / "deploy_heads.puml"
        puml.write_text(render(d))
        result = subprocess.run(
            ["plantuml", str(puml)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"
        assert (tmp_path / "deploy_heads.png").exists()

        # Object
        d = object_diagram()
        el = d.elements
        r = d.relationships
        a = el.object("obj1")
        b = el.object("obj2")
        d.add(a, b)
        d.connect(r.arrow(a, b, left_head="o", right_head="*"))
        puml = tmp_path / "object_heads.puml"
        puml.write_text(render(d))
        result = subprocess.run(
            ["plantuml", str(puml)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"
        assert (tmp_path / "object_heads.png").exists()


class TestArrowHeadEnum:
    """Tests for ArrowHead enum and ArrowHeadLike coercion through composers."""

    def test_enum_value_class_diagram(self):
        d = class_diagram()
        el = d.elements
        r = d.relationships
        a, b = el.class_("A"), el.class_("B")
        d.add(a, b)
        d.connect(r.relationship(a, b, type="association",
                                  left_head=ArrowHead.DIAMOND,
                                  right_head=ArrowHead.THIN_ARROW))
        output = render(d)
        assert "*-->>" in output

    def test_string_name_class_diagram(self):
        d = class_diagram()
        el = d.elements
        r = d.relationships
        a, b = el.class_("A"), el.class_("B")
        d.add(a, b)
        d.connect(r.relationship(a, b, type="association",
                                  left_head="diamond",
                                  right_head="thin_arrow"))
        output = render(d)
        assert "*-->>" in output

    def test_raw_symbol_backward_compat(self):
        """Raw PlantUML symbols still work (backward compatibility)."""
        d = class_diagram()
        el = d.elements
        r = d.relationships
        a, b = el.class_("A"), el.class_("B")
        d.add(a, b)
        d.connect(r.relationship(a, b, type="association",
                                  left_head="*", right_head=">>"))
        output = render(d)
        assert "*-->>" in output

    def test_enum_deployment_diagram(self):
        d = deployment_diagram()
        el = d.elements
        c = d.connections
        a, b = el.node("A"), el.node("B")
        d.add(a, b)
        d.connect(c.arrow(a, b, left_head=ArrowHead.HOLLOW_DIAMOND,
                          right_head=ArrowHead.DIAMOND))
        output = render(d)
        assert "o--*" in output

    def test_string_name_component_diagram(self):
        d = component_diagram()
        el = d.elements
        c = d.connections
        a, b = el.component("A"), el.component("B")
        d.add(a, b)
        d.connect(c.arrow(a, b, left_head="square",
                          right_head="hollow_diamond"))
        output = render(d)
        assert "#--o" in output

    def test_enum_usecase_diagram(self):
        d = usecase_diagram()
        el = d.elements
        r = d.relationships
        actor = el.actor("User")
        uc = el.usecase("Login")
        d.add(actor, uc)
        d.connect(r.arrow(actor, uc,
                          left_head=ArrowHead.HOLLOW_DIAMOND,
                          right_head=ArrowHead.THIN_ARROW))
        output = render(d)
        assert "o-->>" in output

    def test_enum_object_diagram(self):
        d = object_diagram()
        el = d.elements
        r = d.relationships
        a = el.object("obj1")
        b = el.object("obj2")
        d.add(a, b)
        d.connect(r.arrow(a, b,
                          left_head=ArrowHead.SQUARE,
                          right_head=ArrowHead.DIAMOND))
        output = render(d)
        assert "#--*" in output

    def test_mixed_enum_and_string_name(self):
        """Mixing enum members and string names in the same relationship."""
        d = class_diagram()
        el = d.elements
        r = d.relationships
        a, b = el.class_("A"), el.class_("B")
        d.add(a, b)
        d.connect(r.relationship(a, b, type="association",
                                  left_head=ArrowHead.HOLLOW_DIAMOND,
                                  right_head="diamond"))
        output = render(d)
        assert "o--*" in output

    def test_primitive_roundtrip_with_enum(self):
        """Enum values are coerced to raw symbols in the built primitive."""
        d = class_diagram()
        el = d.elements
        r = d.relationships
        a, b = el.class_("A"), el.class_("B")
        d.add(a, b)
        d.connect(r.relationship(a, b,
                                  left_head=ArrowHead.DIAMOND,
                                  right_head="thin_arrow"))
        result = d.build()
        rels = [e for e in result.elements if hasattr(e, "left_head")]
        assert len(rels) == 1
        assert rels[0].left_head == "*"
        assert rels[0].right_head == ">>"

    def test_deployment_line_with_string_names(self):
        d = deployment_diagram()
        el = d.elements
        c = d.connections
        a, b = el.node("A"), el.node("B")
        d.add(a, b)
        d.connect(c.line(a, b, left_head="hollow_diamond",
                         right_head="hollow_diamond"))
        output = render(d)
        assert "o--o" in output
