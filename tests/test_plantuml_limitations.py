"""Tests that verify known PlantUML limitations still exist.

These tests generate raw PlantUML syntax with features that PlantUML accepts
but does not render. By parsing the SVG output, we detect if the styling
actually appears.

If any of these tests FAIL, it means PlantUML has added support for the
feature, and we should consider exposing it in our builder API.

See CLAUDE.md "Only Expose What PlantUML Actually Renders" for context.
"""

import re
import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def render_and_parse_svg(tmp_path: Path):
    """Fixture that renders PlantUML to SVG and returns the SVG content."""

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


def svg_contains_color(svg_content: str, color: str) -> bool:
    """Check if SVG contains a specific color in fill or stroke attributes.

    Args:
        svg_content: The SVG file content
        color: Color to search for (e.g., "red", "#FF0000", "rgb(255,0,0)")

    Returns:
        True if the color appears in styling attributes
    """
    # Normalize color name to check various formats
    color_lower = color.lower()

    # Check for named colors and hex colors in common SVG attributes
    patterns = [
        rf'fill\s*[=:]\s*["\']?{color_lower}',
        rf'stroke\s*[=:]\s*["\']?{color_lower}',
        rf'style\s*=\s*["\'][^"\']*fill\s*:\s*{color_lower}',
        rf'style\s*=\s*["\'][^"\']*stroke\s*:\s*{color_lower}',
    ]

    # For hex colors, also check without the hash
    if color.startswith("#"):
        hex_color = color[1:].lower()
        patterns.extend(
            [
                rf'fill\s*[=:]\s*["\']?#{hex_color}',
                rf'stroke\s*[=:]\s*["\']?#{hex_color}',
            ]
        )

    for pattern in patterns:
        if re.search(pattern, svg_content, re.IGNORECASE):
            return True

    return False


class TestForkJoinStylingLimitation:
    """Verify that fork/join bars cannot be styled in PlantUML.

    PlantUML accepts `state fork1 <<fork>> #red` syntax but renders
    the bar in default gray. If these tests fail, PlantUML has added
    support and we should expose the `style` parameter on fork()/join().
    """

    def test_fork_color_not_rendered(self, render_and_parse_svg):
        """Fork bars with #red should NOT show red in the SVG."""
        puml = """
@startuml
state fork1 <<fork>> #FF0000
S1 --> fork1
fork1 --> S2
@enduml
"""
        svg = render_and_parse_svg(puml)

        # The fork bar should NOT be red - PlantUML ignores the color
        assert not svg_contains_color(svg, "#FF0000"), (
            "PlantUML now renders fork bar colors! "
            "Consider adding `style` parameter to fork() builder method."
        )

    def test_join_color_not_rendered(self, render_and_parse_svg):
        """Join bars with #green should NOT show green in the SVG."""
        puml = """
@startuml
state join1 <<join>> #00FF00
S1 --> join1
join1 --> S2
@enduml
"""
        svg = render_and_parse_svg(puml)

        # The join bar should NOT be green - PlantUML ignores the color
        assert not svg_contains_color(svg, "#00FF00"), (
            "PlantUML now renders join bar colors! "
            "Consider adding `style` parameter to join() builder method."
        )

    def test_fork_with_line_color_not_rendered(self, render_and_parse_svg):
        """Fork bars with ##blue line color should NOT show blue."""
        puml = """
@startuml
state fork1 <<fork>> ##0000FF
S1 --> fork1
fork1 --> S2
@enduml
"""
        svg = render_and_parse_svg(puml)

        # The fork bar border should NOT be blue
        assert not svg_contains_color(svg, "#0000FF"), (
            "PlantUML now renders fork bar line colors! "
            "Consider adding `style` parameter to fork() builder method."
        )


class TestChoiceStylingLimitation:
    """Verify that choice diamonds cannot be styled in PlantUML.

    PlantUML accepts `state choice1 <<choice>> #yellow` syntax but renders
    the diamond in default gray. If these tests fail, PlantUML has added
    support and we should expose the `style` parameter on choice().
    """

    def test_choice_color_not_rendered(self, render_and_parse_svg):
        """Choice diamonds with #yellow should NOT show yellow in the SVG."""
        puml = """
@startuml
state choice1 <<choice>> #FFFF00
S1 --> choice1
choice1 --> S2
@enduml
"""
        svg = render_and_parse_svg(puml)

        # The choice diamond should NOT be yellow - PlantUML ignores the color
        assert not svg_contains_color(svg, "#FFFF00"), (
            "PlantUML now renders choice diamond colors! "
            "Consider adding `style` parameter to choice() builder method."
        )


class TestStateStylingWorks:
    """Verify that regular states CAN be styled (positive control)."""

    def test_state_background_is_rendered(self, render_and_parse_svg):
        """States with #pink background SHOULD show pink in the SVG."""
        puml = """
@startuml
state S1 #FFC0CB
@enduml
"""
        svg = render_and_parse_svg(puml)

        # The state SHOULD have pink background
        assert svg_contains_color(svg, "#FFC0CB"), (
            "State background color not found in SVG. "
            "Either PlantUML changed behavior or SVG parsing is broken."
        )
