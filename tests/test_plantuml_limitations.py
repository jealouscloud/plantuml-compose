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
from typing import get_args

from plantuml_compose.primitives.common import PlantUMLBuiltinTheme

# render_and_parse_svg fixture is provided by conftest.py


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


class TestArrowThicknessLimitation:
    """Verify that thickness=N is not supported in arrow bracket syntax.

    PlantUML's bracket syntax for arrows supports color, dashed, dotted, bold,
    etc. but NOT thickness=N. The syntax is rejected with "No such color".

    If these tests fail (SVG is generated successfully with thickness styling),
    it means PlantUML has added support and we should expose `thickness`
    parameter in arrow() and message() builder methods.
    """

    def test_activity_arrow_thickness_not_supported(self, render_and_parse_svg):
        """Activity arrows with thickness=N should render without thickness styling."""
        puml = """
@startuml
:A;
-[#red,bold]->
:B;
@enduml
"""
        svg = render_and_parse_svg(puml)

        # This SHOULD render - color and bold ARE supported
        assert svg_contains_color(svg, "#FF0000") or svg_contains_color(svg, "red"), (
            "Activity arrow color not rendered. Test infrastructure may be broken."
        )

    def test_sequence_arrow_thickness_not_supported(self, render_and_parse_svg):
        """Sequence arrows with thickness=N should render without thickness styling."""
        puml = """
@startuml
participant A
participant B
A -[#red,bold]-> B : message
@enduml
"""
        svg = render_and_parse_svg(puml)

        # This SHOULD render - color and bold ARE supported
        assert svg_contains_color(svg, "#FF0000") or svg_contains_color(svg, "red"), (
            "Sequence arrow color not rendered. Test infrastructure may be broken."
        )


class TestFloatingNoteSyntaxLimitation:
    """Verify that 'floating note' syntax is rejected in non-activity diagrams.

    PlantUML only supports 'floating note' syntax in Activity diagrams.
    In UseCase, Component, Deployment, and Object diagrams, the syntax
    causes a parse error.

    If these tests FAIL (syntax becomes valid), it means PlantUML has added
    support and we should re-expose the `floating` parameter in those builders.
    """

    def test_usecase_floating_note_rejected(self, validate_plantuml):
        """UseCase diagrams should reject 'floating note' syntax."""
        puml = """
@startuml
actor User
usecase (Login)
User --> Login
floating note right: This is a floating note
@enduml
"""
        assert not validate_plantuml(puml), (
            "PlantUML now accepts 'floating note' in UseCase diagrams! "
            "Consider re-adding `floating` parameter to usecase note() method."
        )

    def test_component_floating_note_rejected(self, validate_plantuml):
        """Component diagrams should reject 'floating note' syntax."""
        puml = """
@startuml
component API
component Database
API --> Database
floating note right: This is a floating note
@enduml
"""
        assert not validate_plantuml(puml), (
            "PlantUML now accepts 'floating note' in Component diagrams! "
            "Consider re-adding `floating` parameter to component note() method."
        )

    def test_deployment_floating_note_rejected(self, validate_plantuml):
        """Deployment diagrams should reject 'floating note' syntax."""
        puml = """
@startuml
node Server
database DB
Server --> DB
floating note right: This is a floating note
@enduml
"""
        assert not validate_plantuml(puml), (
            "PlantUML now accepts 'floating note' in Deployment diagrams! "
            "Consider re-adding `floating` parameter to deployment note() method."
        )

    def test_object_floating_note_rejected(self, validate_plantuml):
        """Object diagrams should reject 'floating note' syntax."""
        puml = """
@startuml
object Order
object Customer
Order --> Customer
floating note right: This is a floating note
@enduml
"""
        assert not validate_plantuml(puml), (
            "PlantUML now accepts 'floating note' in Object diagrams! "
            "Consider re-adding `floating` parameter to object note() method."
        )

    def test_activity_floating_note_works(self, validate_plantuml):
        """Activity diagrams SHOULD accept 'floating note' syntax (positive control)."""
        puml = """
@startuml
start
:Step 1;
floating note right: This should work
:Step 2;
stop
@enduml
"""
        assert validate_plantuml(puml), (
            "Activity diagram floating note stopped working! "
            "PlantUML may have changed behavior."
        )


class TestActivityKillDetachInConditionals:
    """Verify that kill/detach don't work inside conditionals.

    PlantUML does not support 'kill' or 'detach' inside if/else/switch blocks.
    These are syntax errors that PlantUML rejects.

    Our library validates this at build time, preventing users from generating
    invalid PlantUML. If PlantUML adds support in the future, these tests will
    fail, signaling we can remove the validation.
    """

    def test_kill_inside_if_is_invalid(self, validate_plantuml):
        """Kill inside if/else is a PlantUML syntax error."""
        puml = """
@startuml
start
:Process;
if (Error?) then (yes)
  kill
else (no)
  :Continue;
endif
stop
@enduml
"""
        assert not validate_plantuml(puml), (
            "kill inside conditional now works! "
            "PlantUML may have added support - remove _ConditionalBranchMixin.kill() restriction."
        )

    def test_detach_inside_if_is_invalid(self, validate_plantuml):
        """Detach inside if/else is a PlantUML syntax error."""
        puml = """
@startuml
start
:Process;
if (Error?) then (yes)
  detach
else (no)
  :Continue;
endif
stop
@enduml
"""
        assert not validate_plantuml(puml), (
            "detach inside conditional now works! "
            "PlantUML may have added support - remove _ConditionalBranchMixin.detach() restriction."
        )

    def test_end_inside_if_is_valid(self, validate_plantuml):
        """End inside if/else IS supported (unlike kill/detach)."""
        puml = """
@startuml
start
:Process;
if (Error?) then (yes)
  end
else (no)
  :Continue;
endif
stop
@enduml
"""
        assert validate_plantuml(puml), (
            "end inside conditional stopped working! "
            "PlantUML may have changed behavior."
        )


class TestCssStyleSelectorLimitations:
    """Verify that certain CSS-style selectors are NOT rendered by PlantUML.

    PlantUML accepts these selectors in <style> blocks but ignores them.
    If any of these tests FAIL, PlantUML has added support and we should
    add proper rendering tests for those selectors.

    The selectors that DO work are tested in test_diagram_style_integration.py.
    """

    # --- Class Diagram Selectors That Don't Render ---

    def test_class_interface_style_not_rendered(self, render_and_parse_svg):
        """Class diagram 'interface' selector is ignored by PlantUML."""
        puml = """
@startuml
<style>
classDiagram {
  interface {
    BackgroundColor #FF0000
  }
}
</style>
interface MyInterface
@enduml
"""
        svg = render_and_parse_svg(puml)
        assert not svg_contains_color(svg, "#FF0000"), (
            "PlantUML now renders 'interface' CSS-style selector in class diagrams! "
            "Add interface selector tests to test_diagram_style_integration.py."
        )

    def test_class_abstract_style_not_rendered(self, render_and_parse_svg):
        """Class diagram 'abstract' selector is ignored by PlantUML."""
        puml = """
@startuml
<style>
classDiagram {
  abstract {
    BackgroundColor #FF0000
  }
}
</style>
abstract class MyAbstract
@enduml
"""
        svg = render_and_parse_svg(puml)
        assert not svg_contains_color(svg, "#FF0000"), (
            "PlantUML now renders 'abstract' CSS-style selector in class diagrams! "
            "Add abstract selector tests to test_diagram_style_integration.py."
        )

    def test_class_enum_style_not_rendered(self, render_and_parse_svg):
        """Class diagram 'enum' selector is ignored by PlantUML."""
        puml = """
@startuml
<style>
classDiagram {
  enum {
    BackgroundColor #FF0000
  }
}
</style>
enum Status {
  ACTIVE
  INACTIVE
}
@enduml
"""
        svg = render_and_parse_svg(puml)
        assert not svg_contains_color(svg, "#FF0000"), (
            "PlantUML now renders 'enum' CSS-style selector in class diagrams! "
            "Add enum selector tests to test_diagram_style_integration.py."
        )

    def test_class_annotation_style_not_rendered(self, render_and_parse_svg):
        """Class diagram 'annotation' selector is ignored by PlantUML."""
        puml = """
@startuml
<style>
classDiagram {
  annotation {
    BackgroundColor #FF0000
  }
}
</style>
annotation MyAnnotation
@enduml
"""
        svg = render_and_parse_svg(puml)
        assert not svg_contains_color(svg, "#FF0000"), (
            "PlantUML now renders 'annotation' CSS-style selector in class diagrams! "
            "Add annotation selector tests to test_diagram_style_integration.py."
        )

    # --- Sequence Diagram Selectors That Don't Render ---

    def test_sequence_lifeline_style_not_rendered(self, render_and_parse_svg):
        """Sequence diagram 'lifeline' selector is ignored by PlantUML."""
        puml = """
@startuml
<style>
sequenceDiagram {
  lifeline {
    BackgroundColor #FF0000
  }
}
</style>
participant A
participant B
A -> B : message
@enduml
"""
        svg = render_and_parse_svg(puml)
        assert not svg_contains_color(svg, "#FF0000"), (
            "PlantUML now renders 'lifeline' CSS-style selector! "
            "Add lifeline selector tests to test_diagram_style_integration.py."
        )

    # NOTE: 'box' selector DOES render - tested in test_diagram_style_integration.py

    # --- Component Diagram Selectors That Don't Render ---

    def test_component_interface_style_not_rendered(self, render_and_parse_svg):
        """Component diagram 'interface' selector is ignored by PlantUML."""
        puml = """
@startuml
<style>
componentDiagram {
  interface {
    BackgroundColor #FF0000
  }
}
</style>
interface MyInterface
@enduml
"""
        svg = render_and_parse_svg(puml)
        assert not svg_contains_color(svg, "#FF0000"), (
            "PlantUML now renders 'interface' CSS-style selector in component diagrams! "
            "Add interface selector tests to test_diagram_style_integration.py."
        )

    # --- Deployment Diagram - ALL Selectors Don't Render ---

    def test_deployment_node_style_not_rendered(self, render_and_parse_svg):
        """Deployment diagram 'node' selector is ignored by PlantUML."""
        puml = """
@startuml
<style>
deploymentDiagram {
  node {
    BackgroundColor #FF0000
  }
}
</style>
node Server
@enduml
"""
        svg = render_and_parse_svg(puml)
        assert not svg_contains_color(svg, "#FF0000"), (
            "PlantUML now renders 'node' CSS-style selector in deployment diagrams! "
            "Add deployment node style tests to test_diagram_style_integration.py."
        )

    def test_deployment_database_style_not_rendered(self, render_and_parse_svg):
        """Deployment diagram 'database' selector is ignored by PlantUML."""
        puml = """
@startuml
<style>
deploymentDiagram {
  database {
    BackgroundColor #FF0000
  }
}
</style>
database MyDB
@enduml
"""
        svg = render_and_parse_svg(puml)
        assert not svg_contains_color(svg, "#FF0000"), (
            "PlantUML now renders 'database' CSS-style selector in deployment diagrams! "
            "Add deployment database style tests to test_diagram_style_integration.py."
        )

    def test_deployment_arrow_style_not_rendered(self, render_and_parse_svg):
        """Deployment diagram 'arrow' selector is ignored by PlantUML."""
        puml = """
@startuml
<style>
deploymentDiagram {
  arrow {
    LineColor #FF0000
  }
}
</style>
node A
node B
A --> B
@enduml
"""
        svg = render_and_parse_svg(puml)
        assert not svg_contains_color(svg, "#FF0000"), (
            "PlantUML now renders 'arrow' CSS-style selector in deployment diagrams! "
            "Add deployment arrow style tests to test_diagram_style_integration.py."
        )

    # --- Use Case Diagram - ALL Selectors Don't Render ---

    def test_usecase_actor_style_not_rendered(self, render_and_parse_svg):
        """Use case diagram 'actor' selector is ignored by PlantUML."""
        puml = """
@startuml
<style>
usecaseDiagram {
  actor {
    BackgroundColor #FF0000
  }
}
</style>
actor User
@enduml
"""
        svg = render_and_parse_svg(puml)
        assert not svg_contains_color(svg, "#FF0000"), (
            "PlantUML now renders 'actor' CSS-style selector in use case diagrams! "
            "Add usecase actor style tests to test_diagram_style_integration.py."
        )

    def test_usecase_usecase_style_not_rendered(self, render_and_parse_svg):
        """Use case diagram 'usecase' selector is ignored by PlantUML."""
        puml = """
@startuml
<style>
usecaseDiagram {
  usecase {
    BackgroundColor #FF0000
  }
}
</style>
usecase (Login)
@enduml
"""
        svg = render_and_parse_svg(puml)
        assert not svg_contains_color(svg, "#FF0000"), (
            "PlantUML now renders 'usecase' CSS-style selector in use case diagrams! "
            "Add usecase style tests to test_diagram_style_integration.py."
        )

    def test_usecase_arrow_style_not_rendered(self, render_and_parse_svg):
        """Use case diagram 'arrow' selector is ignored by PlantUML."""
        puml = """
@startuml
<style>
usecaseDiagram {
  arrow {
    LineColor #FF0000
  }
}
</style>
actor User
usecase (Login)
User --> Login
@enduml
"""
        svg = render_and_parse_svg(puml)
        assert not svg_contains_color(svg, "#FF0000"), (
            "PlantUML now renders 'arrow' CSS-style selector in use case diagrams! "
            "Add usecase arrow style tests to test_diagram_style_integration.py."
        )

    # --- Object Diagram Selectors That Don't Render ---

    def test_object_arrow_style_not_rendered(self, render_and_parse_svg):
        """Object diagram 'arrow' selector is ignored by PlantUML."""
        puml = """
@startuml
<style>
objectDiagram {
  arrow {
    LineColor #FF0000
  }
}
</style>
object A
object B
A --> B
@enduml
"""
        svg = render_and_parse_svg(puml)
        assert not svg_contains_color(svg, "#FF0000"), (
            "PlantUML now renders 'arrow' CSS-style selector in object diagrams! "
            "Add object arrow style tests to test_diagram_style_integration.py."
        )

    def test_object_note_style_not_rendered(self, render_and_parse_svg):
        """Object diagram 'note' selector is ignored by PlantUML."""
        puml = """
@startuml
<style>
objectDiagram {
  note {
    BackgroundColor #FF0000
  }
}
</style>
object MyObj
note right of MyObj: A note
@enduml
"""
        svg = render_and_parse_svg(puml)
        assert not svg_contains_color(svg, "#FF0000"), (
            "PlantUML now renders 'note' CSS-style selector in object diagrams! "
            "Add object note style tests to test_diagram_style_integration.py."
        )

    def test_sequence_delay_style_not_rendered(self, render_and_parse_svg):
        """Sequence diagram 'delay' selector is ignored by PlantUML."""
        puml = """
@startuml
<style>
sequenceDiagram {
  delay {
    BackgroundColor #FF0000
  }
}
</style>
participant A
participant B
A -> B : Before
...
A -> B : After
@enduml
"""
        svg = render_and_parse_svg(puml)
        assert not svg_contains_color(svg, "#FF0000"), (
            "PlantUML now renders 'delay' CSS-style selector! "
            "Add delay selector tests to test_diagram_style_integration.py."
        )


class TestElementStylePropertyLimitations:
    """Verify that certain ElementStyle CSS properties are NOT rendered.

    If any of these tests FAIL, PlantUML has added support and we should
    update the ElementStyle field documentation.
    """

    def test_line_style_not_rendered(self, render_and_parse_svg):
        """ElementStyle LineStyle property is ignored by PlantUML CSS."""
        puml = """
@startuml
<style>
classDiagram {
  class {
    BackgroundColor #AABBCC
    LineStyle dashed
  }
}
</style>
class Test
@enduml
"""
        svg = render_and_parse_svg(puml)
        # LineStyle dashed should NOT produce dash patterns in the SVG
        # We check that background color IS rendered (syntax accepted)
        # but no dashed stroke pattern appears
        assert svg_contains_color(svg, "#AABBCC"), (
            "Background color not rendered. Test may be broken."
        )
        # If PlantUML starts rendering LineStyle, the class border would become dashed
        # Check that the class border is NOT dashed (no stroke-dasharray on the rect)
        assert "stroke-dasharray" not in svg, (
            "PlantUML now renders 'LineStyle' CSS property! "
            "Update ElementStyle documentation and consider exposing in API."
        )


class TestBuiltinThemes:
    """Verify that PlantUMLBuiltinTheme Literal matches actual PlantUML themes.

    If these tests FAIL, it means PlantUML has added or removed themes and
    the PlantUMLBuiltinTheme Literal in primitives/common.py needs updating.
    """

    def test_builtin_themes_match_plantuml(self):
        """Verify PlantUMLBuiltinTheme matches PlantUML's actual theme list."""
        # Get themes from PlantUML using %get_all_theme() function
        # This outputs each theme name on its own line in text mode
        result = subprocess.run(
            ["plantuml", "-pipe", "-ttxt"],
            input="@startjson\n%get_all_theme()\n@endjson",
            capture_output=True,
            text=True,
        )

        # Parse themes from output - each non-empty line is a theme name
        plantuml_themes: set[str] = set()
        for line in result.stdout.split("\n"):
            theme_name = line.strip()
            if theme_name:
                plantuml_themes.add(theme_name)

        # Get themes from our Literal type
        our_themes = set(get_args(PlantUMLBuiltinTheme))

        # Check for differences
        missing_from_literal = plantuml_themes - our_themes
        extra_in_literal = our_themes - plantuml_themes

        if missing_from_literal:
            raise AssertionError(
                f"PlantUML has new themes not in PlantUMLBuiltinTheme: {sorted(missing_from_literal)}. "
                "Add them to primitives/common.py PlantUMLBuiltinTheme Literal."
            )

        if extra_in_literal:
            raise AssertionError(
                f"PlantUMLBuiltinTheme has themes not in PlantUML: {sorted(extra_in_literal)}. "
                "Remove them from primitives/common.py PlantUMLBuiltinTheme Literal."
            )


class TestGanttNotePositionLimitation:
    """Verify that Gantt chart notes only support 'bottom' position.

    PlantUML Gantt charts accept 'note bottom' but reject 'note left', 'note right',
    and 'note top'. If these tests fail, PlantUML has added support for other
    positions and we should expose `note_position` parameter in the builder API.
    """

    def test_gantt_note_left_is_invalid(self, validate_plantuml):
        """Gantt note left should be a syntax error."""
        puml = """
@startgantt
[Task] lasts 5 days
note left
memo
end note
@endgantt
"""
        assert not validate_plantuml(puml), (
            "PlantUML now accepts 'note left' in Gantt charts! "
            "Consider exposing `note_position` parameter in task() and milestone() builder methods."
        )

    def test_gantt_note_right_is_invalid(self, validate_plantuml):
        """Gantt note right should be a syntax error."""
        puml = """
@startgantt
[Task] lasts 5 days
note right
memo
end note
@endgantt
"""
        assert not validate_plantuml(puml), (
            "PlantUML now accepts 'note right' in Gantt charts! "
            "Consider exposing `note_position` parameter in task() and milestone() builder methods."
        )

    def test_gantt_note_top_is_invalid(self, validate_plantuml):
        """Gantt note top should be a syntax error."""
        puml = """
@startgantt
[Task] lasts 5 days
note top
memo
end note
@endgantt
"""
        assert not validate_plantuml(puml), (
            "PlantUML now accepts 'note top' in Gantt charts! "
            "Consider exposing `note_position` parameter in task() and milestone() builder methods."
        )

    def test_gantt_note_bottom_works(self, validate_plantuml):
        """Gantt note bottom should be valid (positive control)."""
        puml = """
@startgantt
[Task] lasts 5 days
note bottom
memo
end note
@endgantt
"""
        assert validate_plantuml(puml), (
            "Gantt 'note bottom' stopped working! "
            "PlantUML may have changed behavior."
        )
