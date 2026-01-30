"""Tests for common rendering utilities."""

import pytest

from plantuml_compose import link


class TestLink:
    """Tests for the link() helper function."""

    def test_url_only(self):
        assert link("http://example.com") == "[[http://example.com]]"

    def test_url_with_label(self):
        assert link("http://example.com", label="Click here") == "[[http://example.com Click here]]"

    def test_url_with_tooltip(self):
        assert link("http://example.com", tooltip="More info") == "[[http://example.com{More info}]]"

    def test_url_with_label_and_tooltip(self):
        result = link("http://example.com", label="Click here", tooltip="More info")
        assert result == "[[http://example.com{More info} Click here]]"

    def test_empty_url_raises(self):
        with pytest.raises(ValueError, match="url must not be empty"):
            link("")

    def test_url_with_braces_quoted(self):
        # URLs containing { or } get quoted per PlantUML spec
        result = link("http://example.com/path?foo={bar}")
        assert result == '[["http://example.com/path?foo={bar}"{}]]'

    def test_url_with_braces_and_label(self):
        result = link("http://example.com/{id}", label="Click")
        assert result == '[["http://example.com/{id}"{} Click]]'

    def test_url_with_braces_and_tooltip(self):
        result = link("http://example.com/{id}", tooltip="Info")
        assert result == '[["http://example.com/{id}"{Info}]]'

    def test_url_with_braces_label_and_tooltip(self):
        result = link("http://example.com/{id}", label="Click", tooltip="Info")
        assert result == '[["http://example.com/{id}"{Info} Click]]'

    def test_keyword_only_arguments(self):
        # label and tooltip must be keyword arguments
        with pytest.raises(TypeError):
            link("http://example.com", "label")  # type: ignore


class TestThemeSupport:
    """Tests for theme support across all diagram types."""

    def test_state_diagram_with_theme(self):
        from plantuml_compose import render, state_diagram

        with state_diagram(theme="cerulean") as d:
            d.state("Active")

        output = render(d.build())
        assert "!theme cerulean" in output
        # Theme should come right after @startuml
        lines = output.split("\n")
        assert lines[0] == "@startuml"
        assert lines[1] == "!theme cerulean"

    def test_state_diagram_without_theme(self):
        from plantuml_compose import render, state_diagram

        with state_diagram() as d:
            d.state("Idle")

        output = render(d.build())
        assert "!theme" not in output

    def test_sequence_diagram_with_theme(self):
        from plantuml_compose import render, sequence_diagram

        with sequence_diagram(theme="blueprint") as d:
            user = d.participant("User")

        output = render(d.build())
        assert "!theme blueprint" in output

    def test_activity_diagram_with_theme(self):
        from plantuml_compose import render, activity_diagram

        with activity_diagram(theme="plain") as d:
            d.start()
            d.action("Do something")
            d.stop()

        output = render(d.build())
        assert "!theme plain" in output

    def test_class_diagram_with_theme(self):
        from plantuml_compose import render, class_diagram

        with class_diagram(theme="sketchy-outline") as d:
            d.class_("User")

        output = render(d.build())
        assert "!theme sketchy-outline" in output

    def test_usecase_diagram_with_theme(self):
        from plantuml_compose import render
        from plantuml_compose.builders.usecase import usecase_diagram

        with usecase_diagram(theme="amiga") as d:
            d.actor("User")

        output = render(d.build())
        assert "!theme amiga" in output

    def test_object_diagram_with_theme(self):
        from plantuml_compose import render, object_diagram

        with object_diagram(theme="cerulean") as d:
            d.object("user:User")

        output = render(d.build())
        assert "!theme cerulean" in output

    def test_component_diagram_with_theme(self):
        from plantuml_compose import render, component_diagram

        with component_diagram(theme="blueprint") as d:
            d.component("API")

        output = render(d.build())
        assert "!theme blueprint" in output

    def test_deployment_diagram_with_theme(self):
        from plantuml_compose import render, deployment_diagram

        with deployment_diagram(theme="plain") as d:
            d.component("Server")

        output = render(d.build())
        assert "!theme plain" in output

    def test_empty_theme_ignored(self):
        """Empty or whitespace-only theme should not produce !theme directive."""
        from plantuml_compose import render, state_diagram

        with state_diagram(theme="") as d:
            d.state("A")
        output = render(d.build())
        assert "!theme" not in output

        with state_diagram(theme="   ") as d:
            d.state("B")
        output = render(d.build())
        assert "!theme" not in output

    def test_theme_in_primitive_directly(self):
        """Theme can be set via primitive directly for advanced users."""
        from plantuml_compose import render
        from plantuml_compose.primitives.state import StateDiagram, StateNode

        diagram = StateDiagram(
            elements=(StateNode(name="Test"),),
            theme="cerulean",
        )
        output = render(diagram)
        assert "!theme cerulean" in output

    def test_external_theme_from_local_path(self):
        """External theme with local path renders correctly."""
        from plantuml_compose import render, state_diagram
        from plantuml_compose.primitives.common import ExternalTheme

        with state_diagram(theme=ExternalTheme("mytheme", source="/path/to/themes")) as d:
            d.state("Test")

        output = render(d.build())
        assert "!theme mytheme from /path/to/themes" in output

    def test_external_theme_from_remote_url(self):
        """External theme with remote URL renders correctly."""
        from plantuml_compose import render, sequence_diagram
        from plantuml_compose.primitives.common import ExternalTheme

        url = "https://raw.githubusercontent.com/plantuml/plantuml/master/themes"
        with sequence_diagram(theme=ExternalTheme("amiga", source=url)) as d:
            d.participant("User")

        output = render(d.build())
        assert f"!theme amiga from {url}" in output

    def test_external_theme_empty_name_ignored(self):
        """External theme with empty name should not produce directive."""
        from plantuml_compose import render, state_diagram
        from plantuml_compose.primitives.common import ExternalTheme

        with state_diagram(theme=ExternalTheme("", source="/path")) as d:
            d.state("Test")

        output = render(d.build())
        assert "!theme" not in output
