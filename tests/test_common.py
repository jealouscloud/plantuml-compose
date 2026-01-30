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
