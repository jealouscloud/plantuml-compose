"""Test inherited method behavior on sub-builders.

These tests verify whether PlantUML accepts semantically questionable constructs
that are possible through inherited methods on sub-builders. The goal is to
document actual PlantUML behavior, not to test our library's API.

If PlantUML accepts these constructs, we may choose to keep them available.
If PlantUML rejects them, we should consider restricting the API.
"""

from plantuml_compose import render
from plantuml_compose.builders.activity import activity_diagram
from plantuml_compose.builders.component import component_diagram
from plantuml_compose.builders.sequence import sequence_diagram
from plantuml_compose.builders.state import state_diagram


class TestActivityInheritedMethods:
    """Test inherited methods on activity diagram sub-builders."""

    def test_swimlane_inside_partition_rejected(self, validate_plantuml):
        """Test whether PlantUML rejects swimlane() inside a partition.

        This documents that PlantUML does NOT accept swimlanes inside partitions.
        Our API allows this through inheritance, but PlantUML rejects it.
        """
        with activity_diagram() as d:
            d.start()
            with d.partition("Processing") as p:
                p.swimlane("Lane A")
                p.action("Task in Lane A")
            d.stop()

        puml = render(d.build())
        is_valid = validate_plantuml(puml, "swimlane_in_partition")
        # PlantUML rejects this - we document this behavior
        assert not is_valid, "PlantUML should reject swimlane inside partition"

    def test_nested_partition_in_partition(self, validate_plantuml):
        """Test whether PlantUML accepts nested partitions."""
        with activity_diagram() as d:
            d.start()
            with d.partition("Outer") as outer:
                outer.action("Outer task")
                with outer.partition("Inner") as inner:
                    inner.action("Inner task")
            d.stop()

        puml = render(d.build())
        is_valid = validate_plantuml(puml, "nested_partition")
        assert is_valid, "PlantUML should accept nested partitions"

    def test_group_inside_partition(self, validate_plantuml):
        """Test whether PlantUML accepts group() inside a partition."""
        with activity_diagram() as d:
            d.start()
            with d.partition("Main") as p:
                with p.group("Grouped") as g:
                    g.action("Grouped task")
            d.stop()

        puml = render(d.build())
        is_valid = validate_plantuml(puml, "group_in_partition")
        assert is_valid, "PlantUML should accept group inside partition"


class TestComponentInheritedMethods:
    """Test inherited methods on component diagram sub-builders."""

    def test_relationship_inside_package(self, validate_plantuml):
        """Test whether PlantUML accepts relationships inside package blocks."""
        with component_diagram() as d:
            with d.package("Backend") as pkg:
                api = pkg.component("API")
                db = pkg.component("DB")
                # Relationship defined inside the package
                pkg.arrow(api, db)

        puml = render(d.build())
        is_valid = validate_plantuml(puml, "relationship_in_package")
        assert is_valid, "PlantUML should accept relationships inside packages"

    def test_nested_containers(self, validate_plantuml):
        """Test deeply nested containers."""
        with component_diagram() as d:
            with d.package("System") as system:
                with system.node("Server") as server:
                    with server.folder("App") as app:
                        app.component("Core")

        puml = render(d.build())
        is_valid = validate_plantuml(puml, "nested_containers")
        assert is_valid, "PlantUML should accept nested containers"


class TestSequenceInheritedMethods:
    """Test inherited methods on sequence diagram sub-builders."""

    def test_nested_groups_in_else(self, validate_plantuml):
        """Test whether PlantUML accepts nested groups inside else blocks."""
        with sequence_diagram() as d:
            a = d.participant("Client")
            b = d.participant("Server")

            with d.alt("Success") as alt:
                alt.message(a, b, "Request")
                with alt.else_("Failure") as else_block:
                    # Nested group inside else
                    with else_block.opt("Retry?") as opt_block:
                        opt_block.message(a, b, "Retry")

        puml = render(d.build())
        is_valid = validate_plantuml(puml, "nested_groups_in_else")
        assert is_valid, "PlantUML should accept nested groups in else blocks"

    def test_nested_alt_in_loop(self, validate_plantuml):
        """Test nested alt inside loop."""
        with sequence_diagram() as d:
            client = d.participant("Client")
            server = d.participant("Server")

            with d.loop("Until done") as loop_block:
                loop_block.message(client, server, "Request")
                with loop_block.alt("Success") as alt:
                    alt.message(server, client, "Response")
                    with alt.else_("Error") as err:
                        err.message(server, client, "Error")

        puml = render(d.build())
        is_valid = validate_plantuml(puml, "nested_alt_in_loop")
        assert is_valid, "PlantUML should accept nested alt in loop"


class TestStateInheritedMethods:
    """Test inherited methods on state diagram sub-builders."""

    def test_arrow_defined_at_top_level_referencing_composite_states(
        self, validate_plantuml
    ):
        """Test arrows connecting to states inside composites."""
        with state_diagram() as d:
            idle = d.state("Idle")
            with d.composite("Processing") as proc:
                step1 = proc.state("Step1")
                step2 = proc.state("Step2")
                proc.arrow(step1, step2)

            # Arrow from top-level to inside composite
            d.arrow(idle, step1)

        puml = render(d.build())
        is_valid = validate_plantuml(puml, "arrow_to_composite_state")
        assert is_valid, "PlantUML should accept arrows to states inside composites"

    def test_nested_composites(self, validate_plantuml):
        """Test nested composite states."""
        with state_diagram() as d:
            with d.composite("Outer") as outer:
                outer.state("OuterState")
                with outer.composite("Inner") as inner:
                    inner.state("InnerState")

        puml = render(d.build())
        is_valid = validate_plantuml(puml, "nested_composites")
        assert is_valid, "PlantUML should accept nested composite states"

    def test_concurrent_inside_composite(self, validate_plantuml):
        """Test concurrent state inside composite state."""
        with state_diagram() as d:
            with d.composite("Main") as main:
                main.state("Setup")
                with main.concurrent("ConcurrentBlock") as conc:
                    with conc.region() as r1:
                        r1.state("Region1State")
                    with conc.region() as r2:
                        r2.state("Region2State")

        puml = render(d.build())
        is_valid = validate_plantuml(puml, "concurrent_in_composite")
        assert is_valid, "PlantUML should accept concurrent inside composite"
