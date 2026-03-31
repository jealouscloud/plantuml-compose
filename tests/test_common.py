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


class TestColorRendering:
    """Tests for color rendering utilities."""

    def test_render_color_named(self):
        """Named colors are returned as-is."""
        from plantuml_compose.renderers.common import render_color

        assert render_color("red") == "red"
        assert render_color("LightBlue") == "LightBlue"

    def test_render_color_hex_keeps_hash(self):
        """Hex colors keep their # prefix."""
        from plantuml_compose.renderers.common import render_color

        assert render_color("#FF0000") == "#FF0000"
        assert render_color("#E3F2FD") == "#E3F2FD"
        assert render_color("#abc") == "#abc"  # Short hex
        assert render_color("#abcd") == "#abcd"  # 4-char ARGB
        assert render_color("#AABBCCDD") == "#AABBCCDD"  # 8-char AARRGGBB

    def test_render_color_strips_erroneous_hash_from_named(self):
        """Erroneous # on named colors is stripped."""
        from plantuml_compose.renderers.common import render_color

        assert render_color("#red") == "red"
        assert render_color("#LightBlue") == "LightBlue"

    def test_render_color_hash_adds_hash_to_named(self):
        """render_color_hash adds # to named colors."""
        from plantuml_compose.renderers.common import render_color_hash

        assert render_color_hash("red") == "#red"
        assert render_color_hash("LightBlue") == "#LightBlue"

    def test_render_color_hash_preserves_hex(self):
        """render_color_hash preserves # on hex colors."""
        from plantuml_compose.renderers.common import render_color_hash

        assert render_color_hash("#FF0000") == "#FF0000"
        assert render_color_hash("#E3F2FD") == "#E3F2FD"

    def test_render_color_hash_handles_erroneous_input(self):
        """render_color_hash normalizes erroneous # on named colors."""
        from plantuml_compose.renderers.common import render_color_hash

        # #red -> red -> #red
        assert render_color_hash("#red") == "#red"

    def test_render_color_bare_strips_hex(self):
        """render_color_bare strips # from hex colors."""
        from plantuml_compose.renderers.common import render_color_bare

        assert render_color_bare("#FF0000") == "FF0000"
        assert render_color_bare("#E3F2FD") == "E3F2FD"

    def test_render_color_bare_preserves_named(self):
        """render_color_bare preserves named colors without #."""
        from plantuml_compose.renderers.common import render_color_bare

        assert render_color_bare("red") == "red"
        assert render_color_bare("LightBlue") == "LightBlue"

    def test_render_color_bare_handles_erroneous_input(self):
        """render_color_bare normalizes erroneous # on named colors."""
        from plantuml_compose.renderers.common import render_color_bare

        # #red -> red (strip erroneous #) -> red
        assert render_color_bare("#red") == "red"

    def test_render_color_with_color_object(self):
        """render_color works with Color objects."""
        from plantuml_compose.primitives.common import Color
        from plantuml_compose.renderers.common import render_color

        assert render_color(Color.named("red")) == "red"
        assert render_color(Color.hex("#FF0000")) == "#FF0000"
        assert render_color(Color.hex("FF0000")) == "#FF0000"  # Color.hex normalizes
        assert render_color(Color.rgb(255, 0, 0)) == "#FF0000"

    def test_render_color_with_gradient(self):
        """render_color works with Gradient objects."""
        from plantuml_compose.primitives.common import Gradient
        from plantuml_compose.renderers.common import render_color

        grad = Gradient(start="red", end="blue", direction="horizontal")
        assert render_color(grad) == "red|blue"

        grad_hex = Gradient(start="#FF0000", end="#0000FF", direction="vertical")
        assert render_color(grad_hex) == "#FF0000-#0000FF"
