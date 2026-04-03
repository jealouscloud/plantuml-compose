"""Tests for JSON and YAML diagram composers."""

import subprocess

import pytest

from plantuml_compose.composers.json_ import json_diagram, yaml_diagram
from plantuml_compose.primitives.json_ import JsonDiagram, YamlDiagram
from plantuml_compose.renderers import render


# ---------------------------------------------------------------------------
# JSON composer
# ---------------------------------------------------------------------------

class TestJsonComposer:

    def test_basic_build(self):
        d = json_diagram('{"key": "value"}')
        result = d.build()
        assert isinstance(result, JsonDiagram)
        assert result.data == '{"key": "value"}'

    def test_renders_startjson_endjson(self):
        d = json_diagram('{"a": 1}')
        output = render(d)
        assert output.startswith("@startjson")
        assert output.endswith("@endjson")
        assert '{"a": 1}' in output

    def test_title(self):
        d = json_diagram('{"a": 1}', title="My JSON")
        result = d.build()
        assert result.title == "My JSON"
        output = render(d)
        assert "title My JSON" in output

    def test_mainframe(self):
        d = json_diagram('{"a": 1}', mainframe="Data Frame")
        output = render(d)
        assert "mainframe Data Frame" in output

    def test_highlights(self):
        d = json_diagram(
            '{"name": "Alice", "hobbies": ["reading"]}',
            highlights=[("name",), ("hobbies", "0")],
        )
        result = d.build()
        assert result.highlights == (("name",), ("hobbies", "0"))
        output = render(d)
        assert '#highlight "name"' in output
        assert '#highlight "hobbies" / "0"' in output

    def test_diagram_style_dict(self):
        d = json_diagram(
            '{"a": 1}',
            diagram_style={"background": "white", "font_size": 14},
        )
        result = d.build()
        assert result.diagram_style is not None
        assert result.diagram_style.font_size == 14
        output = render(d)
        assert "<style>" in output

    def test_render_method(self):
        """Composer .render() produces the same output as render(composer)."""
        d = json_diagram('{"x": 1}', title="Test")
        assert d.render() == render(d)

    def test_no_optional_fields(self):
        d = json_diagram('{}')
        result = d.build()
        assert result.title is None
        assert result.mainframe is None
        assert result.highlights == ()
        assert result.diagram_style is None


# ---------------------------------------------------------------------------
# YAML composer
# ---------------------------------------------------------------------------

class TestYamlComposer:

    def test_basic_build(self):
        d = yaml_diagram("name: Alice\nage: 30")
        result = d.build()
        assert isinstance(result, YamlDiagram)
        assert "name: Alice" in result.data

    def test_renders_startyaml_endyaml(self):
        d = yaml_diagram("key: value")
        output = render(d)
        assert output.startswith("@startyaml")
        assert output.endswith("@endyaml")
        assert "key: value" in output

    def test_title(self):
        d = yaml_diagram("a: 1", title="My YAML")
        result = d.build()
        assert result.title == "My YAML"
        output = render(d)
        assert "title My YAML" in output

    def test_mainframe(self):
        d = yaml_diagram("a: 1", mainframe="Config")
        output = render(d)
        assert "mainframe Config" in output

    def test_highlights(self):
        d = yaml_diagram(
            "name: Alice\nhobbies:\n  - reading",
            highlights=[("name",), ("hobbies", "0")],
        )
        result = d.build()
        assert result.highlights == (("name",), ("hobbies", "0"))
        output = render(d)
        assert '#highlight "name"' in output
        assert '#highlight "hobbies" / "0"' in output

    def test_diagram_style_dict(self):
        d = yaml_diagram(
            "a: 1",
            diagram_style={"background": "white", "font_size": 14},
        )
        result = d.build()
        assert result.diagram_style is not None
        assert result.diagram_style.font_size == 14
        output = render(d)
        assert "<style>" in output

    def test_render_method(self):
        d = yaml_diagram("x: 1", title="Test")
        assert d.render() == render(d)

    def test_no_optional_fields(self):
        d = yaml_diagram("a: 1")
        result = d.build()
        assert result.title is None
        assert result.mainframe is None
        assert result.highlights == ()
        assert result.diagram_style is None


# ---------------------------------------------------------------------------
# Top-level import
# ---------------------------------------------------------------------------

class TestTopLevelImports:

    def test_json_diagram_importable(self):
        from plantuml_compose import json_diagram as jd
        assert callable(jd)

    def test_yaml_diagram_importable(self):
        from plantuml_compose import yaml_diagram as yd
        assert callable(yd)


# ---------------------------------------------------------------------------
# PlantUML syntax validation
# ---------------------------------------------------------------------------

class TestPlantUMLValidation:

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

    def test_json_basic_valid(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = json_diagram(
            '{"name": "Alice", "age": 30, "hobbies": ["reading", "hiking"]}',
            title="User Data",
        )
        puml_file = tmp_path / "json_basic.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_json_highlights_valid(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = json_diagram(
            '{"name": "Alice", "hobbies": ["reading", "hiking"]}',
            highlights=[("name",), ("hobbies", "0")],
        )
        puml_file = tmp_path / "json_highlights.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_json_styled_valid(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = json_diagram(
            '{"a": 1}',
            title="Styled",
            diagram_style={"background": "white", "font_size": 14},
        )
        puml_file = tmp_path / "json_styled.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_yaml_basic_valid(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = yaml_diagram(
            "name: Alice\nage: 30\nhobbies:\n  - reading\n  - hiking",
            title="User Data",
        )
        puml_file = tmp_path / "yaml_basic.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_yaml_highlights_valid(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = yaml_diagram(
            "name: Alice\nhobbies:\n  - reading",
            highlights=[("name",)],
        )
        puml_file = tmp_path / "yaml_highlights.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_yaml_styled_valid(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = yaml_diagram(
            "a: 1",
            title="Styled",
            diagram_style={"background": "white", "font_size": 14},
        )
        puml_file = tmp_path / "yaml_styled.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"
