"""Shared test fixtures for PlantUML validation."""

import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def validate_plantuml(tmp_path: Path):
    """Validate PlantUML syntax by rendering to SVG.

    Returns a function that takes PlantUML text and an optional name,
    writes it to a temp file, runs PlantUML, and returns True if successful.
    """

    def _validate(puml_text: str, name: str = "test") -> bool:
        puml_file = tmp_path / f"{name}.puml"
        svg_file = tmp_path / f"{name}.svg"

        puml_file.write_text(puml_text)

        result = subprocess.run(
            ["plantuml", "-tsvg", str(puml_file)],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"PlantUML error: {result.stderr}")
            return False

        return svg_file.exists()

    return _validate


@pytest.fixture
def render_and_parse_svg(tmp_path: Path):
    """Render PlantUML to SVG and return the SVG content.

    Used for inspecting SVG output to verify styling is applied.
    Fails the test if PlantUML returns an error.
    """

    def _render(puml_text: str) -> str:
        puml_file = tmp_path / "test.puml"
        svg_file = tmp_path / "test.svg"

        puml_file.write_text(puml_text)

        result = subprocess.run(
            ["plantuml", "-tsvg", str(puml_file)],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            pytest.fail(f"PlantUML failed: {result.stderr}")

        return svg_file.read_text()

    return _render
