"""Tests for JSON and YAML diagram support."""

import pytest

from plantuml_compose import json_diagram, yaml_diagram, render
from plantuml_compose.primitives import JsonDiagram, YamlDiagram


class TestJsonDiagramPrimitive:
    """Tests for JsonDiagram primitive."""

    def test_minimal(self):
        diagram = JsonDiagram(data='{"name": "John"}')
        assert diagram.data == '{"name": "John"}'
        assert diagram.title is None
        assert diagram.highlights == ()
        assert diagram.diagram_style is None

    def test_with_title(self):
        diagram = JsonDiagram(data='{"key": "value"}', title="My Data")
        assert diagram.title == "My Data"

    def test_with_highlights(self):
        diagram = JsonDiagram(
            data='{"name": "John", "age": 30}',
            highlights=(("name",), ("user", "email")),
        )
        assert diagram.highlights == (("name",), ("user", "email"))

    def test_frozen(self):
        diagram = JsonDiagram(data='{}')
        with pytest.raises(AttributeError):
            diagram.data = '{"changed": true}'


class TestYamlDiagramPrimitive:
    """Tests for YamlDiagram primitive."""

    def test_minimal(self):
        diagram = YamlDiagram(data="name: John")
        assert diagram.data == "name: John"
        assert diagram.title is None
        assert diagram.highlights == ()
        assert diagram.diagram_style is None

    def test_with_title(self):
        diagram = YamlDiagram(data="key: value", title="Config")
        assert diagram.title == "Config"

    def test_with_highlights(self):
        diagram = YamlDiagram(
            data="server:\n  port: 8080",
            highlights=(("server", "port"),),
        )
        assert diagram.highlights == (("server", "port"),)


class TestJsonDiagramBuilder:
    """Tests for json_diagram builder."""

    def test_render_returns_plantuml_text(self):
        with json_diagram('{"name": "John"}') as d:
            pass
        result = d.render()
        assert "@startjson" in result
        assert "@endjson" in result
        assert '{"name": "John"}' in result

    def test_from_string(self):
        with json_diagram('{"name": "John"}') as d:
            pass
        diagram = d.build()
        assert diagram.data == '{"name": "John"}'

    def test_from_dict(self):
        with json_diagram({"name": "John", "age": 30}) as d:
            pass
        diagram = d.build()
        # Dict gets serialized to JSON
        assert '"name": "John"' in diagram.data
        assert '"age": 30' in diagram.data

    def test_from_list(self):
        with json_diagram(["a", "b", "c"]) as d:
            pass
        diagram = d.build()
        assert '"a"' in diagram.data
        assert '"b"' in diagram.data
        assert '"c"' in diagram.data

    def test_with_title(self):
        with json_diagram('{}', title="Empty Object") as d:
            pass
        diagram = d.build()
        assert diagram.title == "Empty Object"

    def test_highlight_single_key(self):
        with json_diagram('{"name": "John"}') as d:
            d.highlight("name")
        diagram = d.build()
        assert diagram.highlights == (("name",),)

    def test_highlight_nested_path(self):
        with json_diagram('{"user": {"email": "test@example.com"}}') as d:
            d.highlight("user", "email")
        diagram = d.build()
        assert diagram.highlights == (("user", "email"),)

    def test_highlight_multiple(self):
        with json_diagram('{"a": 1, "b": 2}') as d:
            d.highlight("a")
            d.highlight("b")
        diagram = d.build()
        assert diagram.highlights == (("a",), ("b",))

    def test_highlight_empty_path_raises(self):
        with json_diagram('{}') as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                d.highlight()

    def test_with_diagram_style_dict(self):
        with json_diagram('{}', diagram_style={"node": {"background": "#E3F2FD"}}) as d:
            pass
        diagram = d.build()
        assert diagram.diagram_style is not None
        assert diagram.diagram_style.node.background.value == "#E3F2FD"


class TestYamlDiagramBuilder:
    """Tests for yaml_diagram builder."""

    def test_render_returns_plantuml_text(self):
        with yaml_diagram("name: John") as d:
            pass
        result = d.render()
        assert "@startyaml" in result
        assert "@endyaml" in result
        assert "name: John" in result

    def test_from_string(self):
        with yaml_diagram("name: John") as d:
            pass
        diagram = d.build()
        assert diagram.data == "name: John"

    def test_from_dict(self):
        with yaml_diagram({"server": {"port": 8080}}) as d:
            pass
        diagram = d.build()
        # Dict gets serialized to YAML
        assert "server:" in diagram.data
        assert "port: 8080" in diagram.data

    def test_from_list(self):
        with yaml_diagram(["a", "b", "c"]) as d:
            pass
        diagram = d.build()
        assert "- a" in diagram.data
        assert "- b" in diagram.data
        assert "- c" in diagram.data

    def test_with_title(self):
        with yaml_diagram("key: value", title="Config") as d:
            pass
        diagram = d.build()
        assert diagram.title == "Config"

    def test_highlight_single_key(self):
        with yaml_diagram("name: John") as d:
            d.highlight("name")
        diagram = d.build()
        assert diagram.highlights == (("name",),)

    def test_highlight_nested_path(self):
        with yaml_diagram("server:\n  port: 8080") as d:
            d.highlight("server", "port")
        diagram = d.build()
        assert diagram.highlights == (("server", "port"),)


class TestJsonDiagramRenderer:
    """Tests for JSON diagram rendering."""

    def test_minimal(self):
        diagram = JsonDiagram(data='{"name": "John"}')
        result = render(diagram)
        assert result == '@startjson\n{"name": "John"}\n@endjson'

    def test_with_title(self):
        diagram = JsonDiagram(data='{}', title="My Data")
        result = render(diagram)
        assert "@startjson" in result
        assert "title My Data" in result
        assert "@endjson" in result

    def test_with_single_highlight(self):
        diagram = JsonDiagram(data='{"name": "John"}', highlights=(("name",),))
        result = render(diagram)
        assert '#highlight "name"' in result

    def test_with_nested_highlight(self):
        diagram = JsonDiagram(
            data='{"user": {"email": "test"}}',
            highlights=(("user", "email"),),
        )
        result = render(diagram)
        assert '#highlight "user" / "email"' in result

    def test_with_multiple_highlights(self):
        diagram = JsonDiagram(
            data='{"a": 1, "b": 2}',
            highlights=(("a",), ("b",)),
        )
        result = render(diagram)
        assert '#highlight "a"' in result
        assert '#highlight "b"' in result

    def test_highlights_before_data(self):
        diagram = JsonDiagram(
            data='{"name": "John"}',
            highlights=(("name",),),
        )
        result = render(diagram)
        lines = result.split("\n")
        highlight_idx = next(i for i, l in enumerate(lines) if "#highlight" in l)
        data_idx = next(i for i, l in enumerate(lines) if '{"name"' in l)
        assert highlight_idx < data_idx


class TestYamlDiagramRenderer:
    """Tests for YAML diagram rendering."""

    def test_minimal(self):
        diagram = YamlDiagram(data="name: John")
        result = render(diagram)
        assert result == "@startyaml\nname: John\n@endyaml"

    def test_with_title(self):
        diagram = YamlDiagram(data="key: value", title="Config")
        result = render(diagram)
        assert "@startyaml" in result
        assert "title Config" in result
        assert "@endyaml" in result

    def test_with_highlight(self):
        diagram = YamlDiagram(data="name: John", highlights=(("name",),))
        result = render(diagram)
        assert '#highlight "name"' in result

    def test_with_nested_highlight(self):
        diagram = YamlDiagram(
            data="server:\n  port: 8080",
            highlights=(("server", "port"),),
        )
        result = render(diagram)
        assert '#highlight "server" / "port"' in result


class TestJsonDiagramStyle:
    """Tests for JSON diagram styling."""

    def test_with_node_style(self):
        with json_diagram(
            '{"name": "John"}',
            diagram_style={"node": {"background": "#E3F2FD"}},
        ) as d:
            pass
        result = render(d.build())
        assert "<style>" in result
        assert "jsonDiagram" in result
        assert "node" in result
        assert "BackgroundColor #E3F2FD" in result
        assert "</style>" in result

    def test_with_highlight_style(self):
        with json_diagram(
            '{"name": "John"}',
            diagram_style={"highlight": {"background": "#FFEB3B"}},
        ) as d:
            d.highlight("name")
        result = render(d.build())
        assert "highlight" in result
        assert "BackgroundColor #FFEB3B" in result

    def test_with_root_background(self):
        with json_diagram('{}', diagram_style={"background": "#FAFAFA"}) as d:
            pass
        result = render(d.build())
        assert "BackgroundColor #FAFAFA" in result


class TestYamlDiagramStyle:
    """Tests for YAML diagram styling."""

    def test_with_node_style(self):
        with yaml_diagram(
            "name: John",
            diagram_style={"node": {"background": "#E8F5E9"}},
        ) as d:
            pass
        result = render(d.build())
        assert "<style>" in result
        assert "yamlDiagram" in result
        assert "node" in result
        assert "BackgroundColor #E8F5E9" in result


class TestJsonYamlPlantUMLValidation:
    """Integration tests that verify PlantUML accepts the generated output."""

    def test_json_minimal(self, validate_plantuml):
        with json_diagram('{"name": "John"}') as d:
            pass
        assert validate_plantuml(render(d.build()))

    def test_json_with_title(self, validate_plantuml):
        with json_diagram('{"key": "value"}', title="Test Data") as d:
            pass
        assert validate_plantuml(render(d.build()))

    def test_json_with_highlights(self, validate_plantuml):
        with json_diagram('{"user": {"name": "John"}}') as d:
            d.highlight("user", "name")
        assert validate_plantuml(render(d.build()))

    def test_json_with_style(self, validate_plantuml):
        with json_diagram(
            '{"name": "John"}',
            diagram_style={"node": {"background": "#E3F2FD"}},
        ) as d:
            pass
        assert validate_plantuml(render(d.build()))

    def test_json_from_dict(self, validate_plantuml):
        with json_diagram({"users": [{"id": 1}, {"id": 2}]}) as d:
            pass
        assert validate_plantuml(render(d.build()))

    def test_yaml_minimal(self, validate_plantuml):
        with yaml_diagram("name: John") as d:
            pass
        assert validate_plantuml(render(d.build()))

    def test_yaml_with_title(self, validate_plantuml):
        with yaml_diagram("key: value", title="Config") as d:
            pass
        assert validate_plantuml(render(d.build()))

    def test_yaml_with_highlights(self, validate_plantuml):
        with yaml_diagram("server:\n  port: 8080") as d:
            d.highlight("server", "port")
        assert validate_plantuml(render(d.build()))

    def test_yaml_with_style(self, validate_plantuml):
        with yaml_diagram(
            "name: John",
            diagram_style={"node": {"background": "#E8F5E9"}},
        ) as d:
            pass
        assert validate_plantuml(render(d.build()))

    def test_yaml_from_dict(self, validate_plantuml):
        with yaml_diagram({"database": {"host": "localhost", "port": 5432}}) as d:
            pass
        assert validate_plantuml(render(d.build()))


class TestJsonYamlEndToEnd:
    """End-to-end tests for JSON/YAML diagrams."""

    def test_json_complete_example(self):
        with json_diagram(
            {"user": {"name": "John", "email": "john@example.com"}, "active": True},
            title="User Data",
            diagram_style={"node": {"background": "#E3F2FD"}},
        ) as d:
            d.highlight("user", "name")
            d.highlight("active")

        result = render(d.build())

        assert "@startjson" in result
        assert "title User Data" in result
        assert "<style>" in result
        assert '#highlight "user" / "name"' in result
        assert '#highlight "active"' in result
        assert "@endjson" in result

    def test_yaml_complete_example(self):
        with yaml_diagram(
            {"server": {"host": "localhost", "port": 8080}},
            title="Server Config",
            diagram_style={"highlight": {"background": "#FFEB3B"}},
        ) as d:
            d.highlight("server", "port")

        result = render(d.build())

        assert "@startyaml" in result
        assert "title Server Config" in result
        assert '<style>' in result
        assert '#highlight "server" / "port"' in result
        assert "@endyaml" in result
