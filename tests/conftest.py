"""Shared test fixtures for PlantUML validation."""

import subprocess
from pathlib import Path

import pytest

# Directory for saving all .puml output files for visual verification
OUTPUT_DIR = Path(__file__).parent / "output"


@pytest.fixture(autouse=True)
def auto_save_puml(request, monkeypatch):
    """Automatically save all rendered PlantUML diagrams to tests/output/.

    Wraps the render() function to capture output and save it with the test name.
    Handles multiple renders per test by appending a counter suffix.
    """
    from plantuml_compose import render as original_render

    captured_outputs = []

    def patched_render(diagram):
        output = original_render(diagram)
        captured_outputs.append(output)
        return output

    # Patch render in the test module's namespace (where it's imported)
    test_module = request.node.module
    if hasattr(test_module, "render"):
        monkeypatch.setattr(test_module, "render", patched_render)

    # Also patch in plantuml_compose for any dynamic imports
    monkeypatch.setattr("plantuml_compose.render", patched_render)

    yield

    # After test completes, save all captured outputs
    if captured_outputs:
        test_name = request.node.name
        class_name = request.node.parent.name if request.node.parent else ""
        if class_name and class_name.startswith("Test"):
            base_name = f"{class_name}__{test_name}"
        else:
            base_name = test_name

        OUTPUT_DIR.mkdir(exist_ok=True)

        for i, output in enumerate(captured_outputs):
            if len(captured_outputs) == 1:
                output_name = base_name
            else:
                output_name = f"{base_name}__{i}"
            (OUTPUT_DIR / f"{output_name}.puml").write_text(output)


@pytest.fixture
def validate_plantuml(tmp_path: Path, request):
    """Validate PlantUML syntax by rendering to SVG.

    Returns a function that takes PlantUML text and an optional name,
    writes it to a temp file, runs PlantUML, and returns True if successful.
    Also saves the .puml file to tests/output/ with the test name for verification.
    """

    def _validate(puml_text: str, name: str = "test") -> bool:
        puml_file = tmp_path / f"{name}.puml"
        svg_file = tmp_path / f"{name}.svg"

        puml_file.write_text(puml_text)

        # Also save to tests/output/ for visual verification
        test_name = request.node.name
        class_name = request.node.parent.name if request.node.parent else ""
        if class_name and class_name.startswith("Test"):
            output_name = f"{class_name}__{test_name}__{name}"
        else:
            output_name = f"{test_name}__{name}"
        OUTPUT_DIR.mkdir(exist_ok=True)
        (OUTPUT_DIR / f"{output_name}.puml").write_text(puml_text)

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
def render_and_parse_svg(tmp_path: Path, request):
    """Render PlantUML to SVG and return the SVG content.

    Used for inspecting SVG output to verify styling is applied.
    Fails the test if PlantUML returns an error.
    Also saves the .puml file to tests/output/ with the test name for verification.
    """
    call_count = [0]  # Mutable counter to track multiple calls in same test

    def _render(puml_text: str) -> str:
        puml_file = tmp_path / "test.puml"
        svg_file = tmp_path / "test.svg"

        puml_file.write_text(puml_text)

        # Also save to tests/output/ for visual verification
        test_name = request.node.name
        class_name = request.node.parent.name if request.node.parent else ""
        if class_name and class_name.startswith("Test"):
            output_name = f"{class_name}__{test_name}"
        else:
            output_name = test_name
        # Append call count if multiple renders in same test
        if call_count[0] > 0:
            output_name = f"{output_name}__{call_count[0]}"
        call_count[0] += 1
        OUTPUT_DIR.mkdir(exist_ok=True)
        (OUTPUT_DIR / f"{output_name}.puml").write_text(puml_text)

        result = subprocess.run(
            ["plantuml", "-tsvg", str(puml_file)],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            pytest.fail(f"PlantUML failed: {result.stderr}")

        return svg_file.read_text()

    return _render
