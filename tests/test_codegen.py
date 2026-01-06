#!/usr/bin/env python3
"""
Code generation tests that verify type definitions match PlantUML's actual behavior.

These tests extract data from PlantUML output and compare against our Literal types.
If PlantUML adds/removes colors, these tests fail, signaling we need to update types.
"""

import re
import subprocess
import tempfile
from pathlib import Path


def extract_plantuml_colors() -> set[str]:
    """
    Extract all color names from PlantUML by rendering the 'colors' diagram.

    PlantUML's `@startuml\\ncolors\\n@enduml` generates an SVG with all
    supported color names as text labels in rectangles.
    """
    puml_content = "@startuml\ncolors\n@enduml"

    with tempfile.TemporaryDirectory() as tmpdir:
        puml_file = Path(tmpdir) / "colors.puml"
        svg_file = Path(tmpdir) / "colors.svg"

        puml_file.write_text(puml_content)

        result = subprocess.run(
            ["plantuml", "-tsvg", str(puml_file)],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f"PlantUML failed: {result.stderr}")

        if not svg_file.exists():
            raise RuntimeError("PlantUML did not generate SVG")

        svg_content = svg_file.read_text()

    # Extract color names from <text> elements
    # Pattern: <text ... font-weight="bold" ...>ColorName</text>
    # The colors appear as bold text labels in the color chart
    pattern = r'<text[^>]*font-weight="bold"[^>]*>([A-Za-z]+)</text>'
    matches = re.findall(pattern, svg_content)

    # Filter out non-color entries (like "APPLICATION", "BUSINESS", etc.)
    # These are category headers in all caps
    colors = {name for name in matches if not name.isupper()}

    return colors


def test_extract_plantuml_colors():
    """Test that we can extract colors from PlantUML."""
    colors = extract_plantuml_colors()

    # Sanity checks - these colors definitely exist
    assert "Red" in colors or "red" in colors, "Expected 'Red' or 'red' in colors"
    assert "Blue" in colors or "blue" in colors, "Expected 'Blue' or 'blue' in colors"
    assert "AliceBlue" in colors, "Expected 'AliceBlue' in colors"

    # Should have many colors (PlantUML has 100+)
    assert len(colors) > 100, f"Expected 100+ colors, got {len(colors)}"

    print(f"\nExtracted {len(colors)} colors from PlantUML:")
    for color in sorted(colors):
        print(f"  {color}")


def test_color_literal_matches_plantuml():
    """
    Verify that our PlantUMLColor Literal type matches PlantUML's actual colors.

    This test will fail if:
    - PlantUML adds new colors we don't have
    - PlantUML removes colors we still list
    - Our Literal type has typos
    """
    from typing import get_args

    try:
        from plantuml_compose.primitives.styling import PlantUMLColor
    except ImportError:
        # Type doesn't exist yet - skip test but show what colors we found
        colors = extract_plantuml_colors()
        print(f"\nPlantUMLColor type not yet defined.")
        print(f"Found {len(colors)} colors in PlantUML.")
        print("\nTo create the Literal type, use:")
        print("PlantUMLColor = Literal[")
        for color in sorted(colors):
            print(f'    "{color}",')
        print("]")
        return

    # Get colors from our Literal type
    literal_colors = set(get_args(PlantUMLColor))

    # Get colors from PlantUML
    plantuml_colors = extract_plantuml_colors()

    # Normalize case for comparison (PlantUML uses PascalCase)
    literal_lower = {c.lower() for c in literal_colors}
    plantuml_lower = {c.lower() for c in plantuml_colors}

    # Find differences
    missing_from_literal = plantuml_lower - literal_lower
    extra_in_literal = literal_lower - plantuml_lower

    errors = []

    if missing_from_literal:
        # Find the original case from PlantUML
        missing = [c for c in plantuml_colors if c.lower() in missing_from_literal]
        errors.append(f"Colors in PlantUML but missing from Literal: {sorted(missing)}")

    if extra_in_literal:
        # Find the original case from our Literal
        extra = [c for c in literal_colors if c.lower() in extra_in_literal]
        errors.append(f"Colors in Literal but not in PlantUML: {sorted(extra)}")

    if errors:
        raise AssertionError("\n".join(errors))

    print(f"\nPlantUMLColor Literal matches PlantUML ({len(literal_colors)} colors)")


def generate_color_literal() -> str:
    """
    Generate Python code for the PlantUMLColor Literal type.

    Run this function to get the code to paste into primitives/styling.py
    """
    colors = extract_plantuml_colors()

    lines = ["PlantUMLColor = Literal["]
    for color in sorted(colors):
        lines.append(f'    "{color}",')
    lines.append("]")

    return "\n".join(lines)


def test_all_builders_importable():
    """Smoke test: verify all diagram builders are importable from package root."""
    from plantuml_compose import (
        activity_diagram,
        class_diagram,
        component_diagram,
        deployment_diagram,
        object_diagram,
        sequence_diagram,
        state_diagram,
        usecase_diagram,
        render,
    )

    # Verify each is callable (they are context managers)
    assert callable(activity_diagram)
    assert callable(class_diagram)
    assert callable(component_diagram)
    assert callable(deployment_diagram)
    assert callable(object_diagram)
    assert callable(sequence_diagram)
    assert callable(state_diagram)
    assert callable(usecase_diagram)
    assert callable(render)


def test_subpackage_imports():
    """Verify builders can also be imported from subpackages."""
    from plantuml_compose.builders import (
        activity_diagram,
        class_diagram,
        component_diagram,
        deployment_diagram,
        object_diagram,
        sequence_diagram,
        state_diagram,
        usecase_diagram,
    )

    assert callable(activity_diagram)
    assert callable(class_diagram)
    assert callable(component_diagram)
    assert callable(deployment_diagram)
    assert callable(object_diagram)
    assert callable(sequence_diagram)
    assert callable(state_diagram)
    assert callable(usecase_diagram)


if __name__ == "__main__":
    # When run directly, output the Literal type definition
    print(generate_color_literal())
