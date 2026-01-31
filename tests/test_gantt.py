"""Tests for Gantt chart diagram type."""

import subprocess
from datetime import date

import pytest

from plantuml_compose import (
    gantt_diagram,
    Color,
    GanttClosedDateRange,
    GanttColoredDate,
    GanttColoredDateRange,
    GanttDependency,
    GanttDiagram,
    GanttDiagramStyle,
    GanttMilestone,
    GanttOpenDate,
    GanttResource,
    GanttResourceOff,
    GanttSeparator,
    GanttTask,
    GanttVerticalSeparator,
    ElementStyle,
    MilestoneRef,
    TaskRef,
    render,
)
from plantuml_compose.renderers.gantt import render_gantt_diagram
from plantuml_compose.primitives.gantt import coerce_gantt_diagram_style


class TestGanttPrimitives:
    """Tests for Gantt primitive dataclasses."""

    def test_task_basic(self):
        task = GanttTask(name="Design")
        assert task.name == "Design"
        assert task.duration_days is None
        assert task.duration_weeks is None

    def test_task_with_days(self):
        task = GanttTask(name="Design", duration_days=5)
        assert task.duration_days == 5

    def test_task_with_weeks(self):
        task = GanttTask(name="Design", duration_weeks=2)
        assert task.duration_weeks == 2

    def test_task_with_resources(self):
        resources = (GanttResource(name="Alice"), GanttResource(name="Bob", allocation=50))
        task = GanttTask(name="Design", duration_days=5, resources=resources)
        assert len(task.resources) == 2
        assert task.resources[1].allocation == 50

    def test_milestone(self):
        ms = GanttMilestone(name="Release", happens_at="impl")
        assert ms.name == "Release"
        assert ms.happens_at == "impl"

    def test_diagram(self):
        task = GanttTask(name="Task", duration_days=5)
        diagram = GanttDiagram(
            elements=(task,),
            project_start=date(2024, 1, 1),
            closed_days=("saturday", "sunday"),
        )
        assert len(diagram.elements) == 1
        assert diagram.project_start == date(2024, 1, 1)
        assert "saturday" in diagram.closed_days


class TestGanttRenderer:
    """Tests for Gantt rendering."""

    def test_render_empty_diagram(self):
        diagram = GanttDiagram()
        result = render_gantt_diagram(diagram)
        assert result == "@startgantt\n@endgantt"

    def test_render_task_with_days(self):
        task = GanttTask(name="Design", duration_days=5, alias="_t1")
        diagram = GanttDiagram(elements=(task,))
        result = render_gantt_diagram(diagram)
        assert "[Design] as [_t1] lasts 5 days" in result

    def test_render_task_with_weeks(self):
        task = GanttTask(name="Design", duration_weeks=2, alias="_t1")
        diagram = GanttDiagram(elements=(task,))
        result = render_gantt_diagram(diagram)
        assert "[Design] as [_t1] lasts 2 weeks" in result

    def test_render_task_singular_units(self):
        task1 = GanttTask(name="Quick", duration_days=1, alias="_t1")
        task2 = GanttTask(name="OneWeek", duration_weeks=1, alias="_t2")
        diagram = GanttDiagram(elements=(task1, task2))
        result = render_gantt_diagram(diagram)
        assert "lasts 1 day" in result
        assert "lasts 1 week" in result

    def test_render_task_with_resources(self):
        resources = (GanttResource(name="Alice"), GanttResource(name="Bob"))
        task = GanttTask(name="Design", duration_days=5, resources=resources)
        diagram = GanttDiagram(elements=(task,))
        result = render_gantt_diagram(diagram)
        assert "on {Alice} {Bob}" in result

    def test_render_task_with_completion(self):
        task = GanttTask(name="Design", duration_days=5, alias="_t1", completion=75)
        diagram = GanttDiagram(elements=(task,))
        result = render_gantt_diagram(diagram)
        assert "[_t1] is 75% complete" in result

    def test_render_task_starts_after(self):
        task = GanttTask(name="Impl", duration_days=5, alias="_t2", starts_after="_t1")
        diagram = GanttDiagram(elements=(task,))
        result = render_gantt_diagram(diagram)
        assert "[_t2] starts at [_t1]'s end" in result

    def test_render_milestone(self):
        ms = GanttMilestone(name="Release", happens_at="_t1", alias="_m1")
        diagram = GanttDiagram(elements=(ms,))
        result = render_gantt_diagram(diagram)
        assert "[Release] as [_m1] happens at [_t1]'s end" in result

    def test_render_dependency(self):
        dep = GanttDependency(from_alias="_t1", to_alias="_t2")
        diagram = GanttDiagram(elements=(dep,))
        result = render_gantt_diagram(diagram)
        assert "[_t1] -> [_t2]" in result

    def test_render_separator(self):
        sep = GanttSeparator(label="Phase 2")
        diagram = GanttDiagram(elements=(sep,))
        result = render_gantt_diagram(diagram)
        assert "-- Phase 2 --" in result

    def test_render_project_start(self):
        diagram = GanttDiagram(project_start=date(2024, 1, 1))
        result = render_gantt_diagram(diagram)
        assert "Project starts 2024-01-01" in result

    def test_render_closed_days(self):
        diagram = GanttDiagram(closed_days=("saturday", "sunday"))
        result = render_gantt_diagram(diagram)
        assert "saturday are closed" in result
        assert "sunday are closed" in result

    def test_render_scale(self):
        diagram = GanttDiagram(scale="weekly", scale_zoom=2)
        result = render_gantt_diagram(diagram)
        assert "printscale weekly zoom 2" in result

    def test_render_task_with_note(self):
        task = GanttTask(name="Design", duration_days=5, note="Design notes\nLine 2")
        diagram = GanttDiagram(elements=(task,))
        result = render_gantt_diagram(diagram)
        assert "note bottom" in result
        assert "Design notes" in result
        assert "Line 2" in result
        assert "end note" in result

    def test_render_task_note_position_always_bottom(self):
        """Note position defaults to 'bottom' as it's the only supported position."""
        task = GanttTask(name="Design", duration_days=5, note="Bottom note")
        diagram = GanttDiagram(elements=(task,))
        result = render_gantt_diagram(diagram)
        assert "note bottom" in result

    def test_render_milestone_with_note(self):
        milestone = GanttMilestone(name="Release", happens_at="impl", note="Big release!")
        diagram = GanttDiagram(elements=(milestone,))
        result = render_gantt_diagram(diagram)
        assert "note bottom" in result
        assert "Big release!" in result
        assert "end note" in result


class TestGanttBuilder:
    """Tests for Gantt builder API."""

    def test_simple_task(self):
        with gantt_diagram(start=date(2024, 1, 1)) as d:
            task = d.task("Design", days=5)

        assert isinstance(task, TaskRef)
        diagram = d.build()
        assert len(diagram.elements) == 1
        elem = diagram.elements[0]
        assert isinstance(elem, GanttTask)
        assert elem.duration_days == 5

    def test_task_with_weeks(self):
        with gantt_diagram() as d:
            d.task("Design", weeks=2)

        diagram = d.build()
        elem = diagram.elements[0]
        assert isinstance(elem, GanttTask)
        assert elem.duration_weeks == 2

    def test_task_days_and_weeks_error(self):
        with gantt_diagram() as d:
            with pytest.raises(ValueError, match="Specify either days or weeks"):
                d.task("Design", days=5, weeks=2)

    def test_task_with_after(self):
        with gantt_diagram() as d:
            design = d.task("Design", weeks=2)
            d.task("Implementation", weeks=3, after=design)

        diagram = d.build()
        impl_task = diagram.elements[1]
        assert isinstance(impl_task, GanttTask)
        assert impl_task.starts_after == design._alias  # noqa: SLF001

    def test_task_with_multiple_after(self):
        """Task depending on multiple predecessors."""
        with gantt_diagram() as d:
            backend = d.task("Backend", weeks=3)
            frontend = d.task("Frontend", weeks=3)
            integration = d.task("Integration", weeks=1, after=[backend, frontend])

        diagram = d.build()
        # First dependency via starts_after
        integration_task = diagram.elements[2]
        assert isinstance(integration_task, GanttTask)
        assert integration_task.starts_after == backend._alias  # noqa: SLF001
        # Second dependency via arrow
        dep = diagram.elements[3]
        assert isinstance(dep, GanttDependency)
        assert dep.from_alias == frontend._alias  # noqa: SLF001
        assert dep.to_alias == integration._alias  # noqa: SLF001

    def test_task_with_resources(self):
        with gantt_diagram() as d:
            d.task("Design", days=5, resources=["Alice", "Bob"])

        diagram = d.build()
        task = diagram.elements[0]
        assert isinstance(task, GanttTask)
        assert len(task.resources) == 2
        assert task.resources[0].name == "Alice"
        assert task.resources[1].name == "Bob"

    def test_task_with_completed(self):
        with gantt_diagram() as d:
            d.task("Design", days=5, completed=50)

        diagram = d.build()
        elem = diagram.elements[0]
        assert isinstance(elem, GanttTask)
        assert elem.completion == 50

    def test_task_with_color(self):
        with gantt_diagram() as d:
            d.task("Design", days=5, color="LightBlue/Blue")

        diagram = d.build()
        elem = diagram.elements[0]
        assert isinstance(elem, GanttTask)
        assert elem.color == "LightBlue/Blue"

    def test_task_with_note(self):
        with gantt_diagram() as d:
            d.task("Design", days=5, note="This is the design phase")

        diagram = d.build()
        task = diagram.elements[0]
        assert isinstance(task, GanttTask)
        assert task.note == "This is the design phase"
        assert task.note_position == "bottom"  # Only "bottom" supported by PlantUML

    def test_milestone_with_note(self):
        with gantt_diagram() as d:
            d.task("Implementation", weeks=4)
            d.milestone("Release", after=None, note="Major release")

        diagram = d.build()
        milestone = diagram.elements[1]
        assert isinstance(milestone, GanttMilestone)
        assert milestone.note == "Major release"
        assert milestone.note_position == "bottom"  # Only "bottom" supported by PlantUML

    def test_milestone_after_task(self):
        with gantt_diagram() as d:
            impl = d.task("Implementation", weeks=4)
            ms = d.milestone("Release", after=impl)

        assert isinstance(ms, MilestoneRef)
        diagram = d.build()
        milestone = diagram.elements[1]
        assert isinstance(milestone, GanttMilestone)
        assert milestone.happens_at == impl._alias  # noqa: SLF001

    def test_milestone_on_date(self):
        with gantt_diagram() as d:
            d.milestone("Kickoff", on=date(2024, 1, 15))

        diagram = d.build()
        elem = diagram.elements[0]
        assert isinstance(elem, GanttMilestone)
        assert elem.date == date(2024, 1, 15)

    def test_separator(self):
        with gantt_diagram() as d:
            d.task("Task 1", days=5)
            d.separator("Phase 2")
            d.task("Task 2", days=3)

        diagram = d.build()
        assert isinstance(diagram.elements[1], GanttSeparator)
        assert diagram.elements[1].label == "Phase 2"

    def test_close_weekends(self):
        with gantt_diagram() as d:
            d.close_weekends()

        diagram = d.build()
        assert "saturday" in diagram.closed_days
        assert "sunday" in diagram.closed_days

    def test_close_weekends_deduplicates(self):
        """Calling close_weekends() multiple times should not duplicate entries."""
        with gantt_diagram() as d:
            d.close_weekends()
            d.close_weekends()
            d.close_days("saturday")  # Also deduplicated

        # Count occurrences in rendered output
        result = d.render()
        assert result.count("saturday are closed") == 1
        assert result.count("sunday are closed") == 1

    def test_close_dates(self):
        with gantt_diagram() as d:
            d.close_dates(date(2024, 1, 1), date(2024, 12, 25))

        diagram = d.build()
        assert date(2024, 1, 1) in diagram.closed_dates
        assert date(2024, 12, 25) in diagram.closed_dates

    def test_today(self):
        with gantt_diagram() as d:
            d.today(date(2024, 1, 15), color="#AAF")

        diagram = d.build()
        assert diagram.today == date(2024, 1, 15)
        assert diagram.today_color == "#AAF"

    def test_full_example(self):
        """Test the full example from the docstring."""
        with gantt_diagram(start=date(2024, 1, 1)) as d:
            d.close_weekends()

            design = d.task("Design", weeks=2, resources=["Alice"])
            backend = d.task("Backend", weeks=3, after=design, resources=["Bob"])
            frontend = d.task("Frontend", weeks=3, after=design)

            integration = d.task("Integration", weeks=1, after=[backend, frontend])
            testing = d.task("Testing", weeks=2, after=integration)

            d.milestone("Release", after=testing)

        result = d.render()
        assert "@startgantt" in result
        assert "saturday are closed" in result
        assert "lasts 2 weeks" in result
        assert "Release" in result
        assert "@endgantt" in result


class TestGanttDispatch:
    """Tests for render() dispatch function with Gantt."""

    def test_render_dispatch(self):
        task = GanttTask(name="Task", duration_days=5)
        diagram = GanttDiagram(elements=(task,))
        result = render(diagram)
        assert "@startgantt" in result
        assert "[Task] lasts 5 days" in result


class TestGanttPlantUMLIntegration:
    """Integration tests verifying PlantUML accepts the output."""

    @pytest.fixture
    def plantuml_check(self):
        """Check if PlantUML is available."""
        try:
            result = subprocess.run(
                ["plantuml", "-version"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def test_basic_project(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with gantt_diagram(start=date(2024, 1, 1)) as d:
            design = d.task("Design", weeks=2)
            d.task("Implementation", weeks=3, after=design)

        puml_file = tmp_path / "gantt.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_with_weekends_closed(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with gantt_diagram(start=date(2024, 1, 1)) as d:
            d.close_weekends()
            d.task("Task", weeks=2)

        puml_file = tmp_path / "gantt_weekends.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_with_resources(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with gantt_diagram(start=date(2024, 1, 1)) as d:
            d.task("Design", days=5, resources=["Alice", "Bob"])

        puml_file = tmp_path / "gantt_resources.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_with_milestones(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with gantt_diagram(start=date(2024, 1, 1)) as d:
            impl = d.task("Implementation", weeks=4)
            d.milestone("Release", after=impl)

        puml_file = tmp_path / "gantt_milestone.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_multiple_dependencies(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with gantt_diagram(start=date(2024, 1, 1)) as d:
            backend = d.task("Backend", weeks=3)
            frontend = d.task("Frontend", weeks=3)
            d.task("Integration", weeks=1, after=[backend, frontend])

        puml_file = tmp_path / "gantt_multi_dep.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_with_separators(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with gantt_diagram(start=date(2024, 1, 1)) as d:
            d.task("Planning", weeks=1)
            d.separator("Development")
            d.task("Coding", weeks=4)

        puml_file = tmp_path / "gantt_seps.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_colored_tasks(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with gantt_diagram(start=date(2024, 1, 1)) as d:
            d.task("Design", weeks=2, color="LightBlue/Blue", completed=50)

        puml_file = tmp_path / "gantt_colors.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_full_project(self, plantuml_check, tmp_path):
        """Full project example with all features."""
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with gantt_diagram(start=date(2024, 1, 1), title="Project Plan") as d:
            d.close_weekends()
            d.today(date(2024, 1, 15))

            d.separator("Phase 1: Design")
            design = d.task("Design", weeks=2, resources=["Alice"], color="LightBlue")

            d.separator("Phase 2: Build")
            backend = d.task("Backend", weeks=3, after=design, resources=["Bob"])
            frontend = d.task("Frontend", weeks=3, after=design, resources=["Charlie"])

            d.separator("Phase 3: Ship")
            integration = d.task("Integration", weeks=1, after=[backend, frontend])
            testing = d.task("Testing", weeks=2, after=integration, completed=25)

            d.milestone("Release", after=testing)

        puml_file = tmp_path / "gantt_full.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_with_notes(self, plantuml_check, tmp_path):
        """Test notes on tasks and milestones."""
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with gantt_diagram(start=date(2024, 1, 1)) as d:
            d.task(
                "Design",
                weeks=2,
                note="memo1 ...\nmemo2 ...\nexplanations",
            )
            impl = d.task("Implementation", weeks=3, note="Build it")
            d.milestone("Release", after=impl, note="Ship it!")

        puml_file = tmp_path / "gantt_notes.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"


class TestGanttNewPrimitives:
    """Tests for new Gantt primitive dataclasses."""

    def test_closed_date_range(self):
        closed = GanttClosedDateRange(start=date(2024, 12, 23), end=date(2024, 12, 27))
        assert closed.start == date(2024, 12, 23)
        assert closed.end == date(2024, 12, 27)

    def test_open_date(self):
        open_d = GanttOpenDate(date=date(2024, 12, 24))
        assert open_d.date == date(2024, 12, 24)

    def test_colored_date(self):
        colored = GanttColoredDate(date=date(2024, 1, 1), color="LightGreen")
        assert colored.date == date(2024, 1, 1)
        assert colored.color == "LightGreen"

    def test_colored_date_range(self):
        colored = GanttColoredDateRange(
            start=date(2024, 1, 1), end=date(2024, 1, 5), color="salmon"
        )
        assert colored.start == date(2024, 1, 1)
        assert colored.end == date(2024, 1, 5)
        assert colored.color == "salmon"

    def test_vertical_separator(self):
        sep = GanttVerticalSeparator(after="_t1")
        assert sep.after == "_t1"

    def test_resource_off(self):
        off = GanttResourceOff(resource="Alice", dates=(date(2024, 1, 15), date(2024, 1, 16)))
        assert off.resource == "Alice"
        assert len(off.dates) == 2

    def test_task_with_then(self):
        task = GanttTask(name="Build", then="_t1")
        assert task.then == "_t1"

    def test_task_with_pauses_on_days(self):
        task = GanttTask(name="Build", pauses_on_days=("monday",))
        assert task.pauses_on_days == ("monday",)

    def test_diagram_with_new_fields(self):
        diagram = GanttDiagram(
            week_numbering=1,
            show_calendar_date=True,
            week_starts_on="sunday",
            min_days_in_first_week=4,
            print_range=(date(2024, 1, 1), date(2024, 1, 31)),
            hide_resource_names=True,
            hide_resource_footbox=True,
        )
        assert diagram.week_numbering == 1
        assert diagram.show_calendar_date is True
        assert diagram.week_starts_on == "sunday"
        assert diagram.min_days_in_first_week == 4
        assert diagram.print_range == (date(2024, 1, 1), date(2024, 1, 31))
        assert diagram.hide_resource_names is True
        assert diagram.hide_resource_footbox is True


class TestGanttDiagramStyle:
    """Tests for GanttDiagramStyle."""

    def test_style_creation(self):
        style = GanttDiagramStyle(
            background="white",
            font_name="Arial",
            task=ElementStyle(background="LightBlue"),
        )
        assert style.background == "white"
        assert style.font_name == "Arial"
        assert style.task is not None
        assert style.task.background == "LightBlue"

    def test_style_coercion_from_dict(self):
        style = coerce_gantt_diagram_style({
            "background": "white",
            "task": {"background": "LightBlue"},
        })
        assert isinstance(style, GanttDiagramStyle)
        # background is coerced to a Color object
        assert isinstance(style.background, Color)
        assert style.background.value == "white"
        assert style.task is not None
        assert isinstance(style.task.background, Color)
        assert style.task.background.value == "LightBlue"

    def test_style_passthrough(self):
        original = GanttDiagramStyle(background="white")
        result = coerce_gantt_diagram_style(original)
        assert result is original


class TestGanttNewRendering:
    """Tests for rendering new Gantt features."""

    def test_render_week_numbering_true(self):
        # week_numbering=True without explicit scale defaults to weekly
        diagram = GanttDiagram(week_numbering=True)
        result = render_gantt_diagram(diagram)
        assert "printscale weekly" in result

    def test_render_week_numbering_from(self):
        diagram = GanttDiagram(week_numbering=1)
        result = render_gantt_diagram(diagram)
        assert "printscale weekly with week numbering from 1" in result

    def test_render_week_numbering_with_scale(self):
        diagram = GanttDiagram(scale="weekly", week_numbering=5)
        result = render_gantt_diagram(diagram)
        assert "printscale weekly with week numbering from 5" in result

    def test_render_calendar_date(self):
        diagram = GanttDiagram(show_calendar_date=True)
        result = render_gantt_diagram(diagram)
        assert "printscale weekly with calendar date" in result

    def test_render_calendar_date_with_scale(self):
        diagram = GanttDiagram(scale="weekly", show_calendar_date=True)
        result = render_gantt_diagram(diagram)
        assert "printscale weekly with calendar date" in result

    def test_render_week_starts_on(self):
        diagram = GanttDiagram(week_starts_on="sunday")
        result = render_gantt_diagram(diagram)
        assert "weeks starts on sunday" in result

    def test_render_min_days_in_first_week_requires_week_starts_on(self):
        # min_days alone (without week_starts_on) is not valid PlantUML syntax
        # so it should be ignored when week_starts_on is not set
        diagram = GanttDiagram(min_days_in_first_week=4)
        result = render_gantt_diagram(diagram)
        assert "must have at least" not in result

    def test_render_week_starts_on_with_min_days(self):
        diagram = GanttDiagram(week_starts_on="sunday", min_days_in_first_week=4)
        result = render_gantt_diagram(diagram)
        assert "weeks starts on sunday and must have at least 4 days" in result

    def test_render_print_range(self):
        diagram = GanttDiagram(
            print_range=(date(2024, 1, 1), date(2024, 1, 31))
        )
        result = render_gantt_diagram(diagram)
        assert "Print between 2024-01-01 and 2024-01-31" in result

    def test_render_hide_resource_names(self):
        diagram = GanttDiagram(hide_resource_names=True)
        result = render_gantt_diagram(diagram)
        assert "hide resources names" in result

    def test_render_hide_resource_footbox(self):
        diagram = GanttDiagram(hide_resource_footbox=True)
        result = render_gantt_diagram(diagram)
        assert "hide resources footbox" in result

    def test_render_closed_date_range(self):
        diagram = GanttDiagram(
            closed_date_ranges=(
                GanttClosedDateRange(start=date(2024, 12, 23), end=date(2024, 12, 27)),
            )
        )
        result = render_gantt_diagram(diagram)
        assert "2024-12-23 to 2024-12-27 is closed" in result

    def test_render_open_date(self):
        diagram = GanttDiagram(open_dates=(date(2024, 12, 24),))
        result = render_gantt_diagram(diagram)
        assert "2024-12-24 is open" in result

    def test_render_colored_date(self):
        diagram = GanttDiagram(
            colored_dates=(GanttColoredDate(date=date(2024, 1, 1), color="LightGreen"),)
        )
        result = render_gantt_diagram(diagram)
        assert "2024-01-01 is colored in LightGreen" in result

    def test_render_colored_date_range(self):
        diagram = GanttDiagram(
            colored_date_ranges=(
                GanttColoredDateRange(
                    start=date(2024, 1, 1), end=date(2024, 1, 5), color="salmon"
                ),
            )
        )
        result = render_gantt_diagram(diagram)
        assert "2024-01-01 to 2024-01-05 are colored in salmon" in result

    def test_render_vertical_separator(self):
        sep = GanttVerticalSeparator(after="_t1")
        diagram = GanttDiagram(elements=(sep,))
        result = render_gantt_diagram(diagram)
        assert "Separator just at [_t1]'s end" in result

    def test_render_resource_off(self):
        off = GanttResourceOff(resource="Alice", dates=(date(2024, 1, 15),))
        diagram = GanttDiagram(elements=(off,))
        result = render_gantt_diagram(diagram)
        assert "{Alice} is off on 2024-01-15" in result

    def test_render_task_with_then(self):
        task = GanttTask(name="Build", duration_days=5, alias="_t2", then="_t1")
        diagram = GanttDiagram(elements=(task,))
        result = render_gantt_diagram(diagram)
        assert "[_t2] starts at [_t1]'s end" in result

    def test_render_task_with_link(self):
        task = GanttTask(name="Build", duration_days=5, alias="_t1", link="https://example.com")
        diagram = GanttDiagram(elements=(task,))
        result = render_gantt_diagram(diagram)
        assert "[_t1] links to [[https://example.com]]" in result

    def test_render_task_pauses_on_day(self):
        task = GanttTask(name="Build", duration_days=5, alias="_t1", pauses_on_days=("monday",))
        diagram = GanttDiagram(elements=(task,))
        result = render_gantt_diagram(diagram)
        assert "[_t1] pauses on monday" in result

    def test_render_diagram_style(self):
        style = GanttDiagramStyle(
            background="white",
            task=ElementStyle(background="LightBlue"),
        )
        diagram = GanttDiagram(diagram_style=style)
        result = render_gantt_diagram(diagram)
        assert "<style>" in result
        assert "ganttDiagram {" in result
        assert "BackgroundColor white" in result
        assert "task {" in result
        assert "</style>" in result


class TestGanttNewBuilder:
    """Tests for new Gantt builder features."""

    def test_task_with_explicit_dates(self):
        with gantt_diagram() as d:
            d.task("Build", start=date(2024, 2, 1), end=date(2024, 2, 15))

        diagram = d.build()
        task = diagram.elements[0]
        assert isinstance(task, GanttTask)
        assert task.start_date == date(2024, 2, 1)
        assert task.end_date == date(2024, 2, 15)

    def test_task_with_then(self):
        with gantt_diagram() as d:
            design = d.task("Design", weeks=2)
            d.task("Build", weeks=3, then=design)

        diagram = d.build()
        build_task = diagram.elements[1]
        assert isinstance(build_task, GanttTask)
        assert build_task.then == design._alias  # noqa: SLF001

    def test_task_after_and_then_mutually_exclusive(self):
        with gantt_diagram() as d:
            design = d.task("Design", weeks=2)
            with pytest.raises(ValueError, match="Specify either after or then"):
                d.task("Build", weeks=3, after=design, then=design)

    def test_task_with_starts_with(self):
        with gantt_diagram() as d:
            backend = d.task("Backend", weeks=3)
            d.task("Docs", weeks=2, starts_with=backend)

        diagram = d.build()
        docs_task = diagram.elements[1]
        assert isinstance(docs_task, GanttTask)
        assert docs_task.starts_with == backend._alias  # noqa: SLF001

    def test_task_with_same_row_as(self):
        with gantt_diagram() as d:
            backend = d.task("Backend", weeks=3)
            d.task("Docs", weeks=2, same_row_as=backend)

        diagram = d.build()
        docs_task = diagram.elements[1]
        assert isinstance(docs_task, GanttTask)
        assert docs_task.on_same_row_as == backend._alias  # noqa: SLF001

    def test_task_with_link(self):
        with gantt_diagram() as d:
            d.task("Build", weeks=2, link="https://example.com")

        diagram = d.build()
        elem = diagram.elements[0]
        assert isinstance(elem, GanttTask)
        assert elem.link == "https://example.com"

    def test_task_with_pauses_on_dates(self):
        with gantt_diagram() as d:
            d.task("Build", weeks=2, pauses_on=[date(2024, 2, 14)])

        diagram = d.build()
        elem = diagram.elements[0]
        assert isinstance(elem, GanttTask)
        assert date(2024, 2, 14) in elem.pauses_on

    def test_task_with_pauses_on_days(self):
        with gantt_diagram() as d:
            d.task("Build", weeks=2, pauses_on=["monday"])

        diagram = d.build()
        elem = diagram.elements[0]
        assert isinstance(elem, GanttTask)
        assert "monday" in elem.pauses_on_days

    def test_task_with_mixed_pauses(self):
        with gantt_diagram() as d:
            d.task("Build", weeks=2, pauses_on=[date(2024, 2, 14), "monday"])

        diagram = d.build()
        task = diagram.elements[0]
        assert isinstance(task, GanttTask)
        assert date(2024, 2, 14) in task.pauses_on
        assert "monday" in task.pauses_on_days

    def test_task_deleted(self):
        with gantt_diagram() as d:
            d.task("Removed", weeks=1, deleted=True)

        diagram = d.build()
        elem = diagram.elements[0]
        assert isinstance(elem, GanttTask)
        assert elem.is_deleted is True

    def test_resource_allocation(self):
        with gantt_diagram() as d:
            d.task("Build", weeks=2, resources=[("Alice", 100), ("Bob", 50)])

        diagram = d.build()
        task = diagram.elements[0]
        assert isinstance(task, GanttTask)
        assert task.resources[0].name == "Alice"
        assert task.resources[0].allocation == 100
        assert task.resources[1].name == "Bob"
        assert task.resources[1].allocation == 50

    def test_resource_mixed_format(self):
        with gantt_diagram() as d:
            d.task("Build", weeks=2, resources=["Alice", ("Bob", 50)])

        diagram = d.build()
        task = diagram.elements[0]
        assert isinstance(task, GanttTask)
        assert task.resources[0].allocation is None
        assert task.resources[1].allocation == 50

    def test_milestone_with_link(self):
        with gantt_diagram() as d:
            d.milestone("Release", on=date(2024, 3, 1), link="https://releases.example.com")

        diagram = d.build()
        elem = diagram.elements[0]
        assert isinstance(elem, GanttMilestone)
        assert elem.link == "https://releases.example.com"

    def test_close_date_range(self):
        with gantt_diagram() as d:
            d.close_date_range(date(2024, 12, 23), date(2024, 12, 27))

        diagram = d.build()
        assert len(diagram.closed_date_ranges) == 1
        assert diagram.closed_date_ranges[0].start == date(2024, 12, 23)
        assert diagram.closed_date_ranges[0].end == date(2024, 12, 27)

    def test_open_date(self):
        with gantt_diagram() as d:
            d.open_date(date(2024, 12, 24))

        diagram = d.build()
        assert date(2024, 12, 24) in diagram.open_dates

    def test_open_dates(self):
        with gantt_diagram() as d:
            d.open_dates(date(2024, 12, 24), date(2024, 12, 25))

        diagram = d.build()
        assert date(2024, 12, 24) in diagram.open_dates
        assert date(2024, 12, 25) in diagram.open_dates

    def test_color_date(self):
        with gantt_diagram() as d:
            d.color_date(date(2024, 1, 1), "LightGreen")

        diagram = d.build()
        assert len(diagram.colored_dates) == 1
        assert diagram.colored_dates[0].date == date(2024, 1, 1)
        assert diagram.colored_dates[0].color == "LightGreen"

    def test_color_date_range(self):
        with gantt_diagram() as d:
            d.color_date_range(date(2024, 1, 1), date(2024, 1, 5), "salmon")

        diagram = d.build()
        assert len(diagram.colored_date_ranges) == 1
        assert diagram.colored_date_ranges[0].start == date(2024, 1, 1)
        assert diagram.colored_date_ranges[0].end == date(2024, 1, 5)
        assert diagram.colored_date_ranges[0].color == "salmon"

    def test_vertical_separator(self):
        with gantt_diagram() as d:
            design = d.task("Design", weeks=2)
            d.vertical_separator(after=design)

        diagram = d.build()
        sep = diagram.elements[1]
        assert isinstance(sep, GanttVerticalSeparator)
        assert sep.after == design._alias

    def test_resource_off(self):
        with gantt_diagram() as d:
            d.resource_off("Alice", date(2024, 1, 15), date(2024, 1, 16))

        diagram = d.build()
        off = diagram.elements[0]
        assert isinstance(off, GanttResourceOff)
        assert off.resource == "Alice"
        assert len(off.dates) == 2

    def test_week_numbering(self):
        with gantt_diagram(week_numbering=True) as d:
            pass

        diagram = d.build()
        assert diagram.week_numbering is True

    def test_week_numbering_from(self):
        with gantt_diagram(week_numbering=5) as d:
            pass

        diagram = d.build()
        assert diagram.week_numbering == 5

    def test_show_calendar_date(self):
        with gantt_diagram(show_calendar_date=True) as d:
            pass

        diagram = d.build()
        assert diagram.show_calendar_date is True

    def test_week_starts_on(self):
        with gantt_diagram(week_starts_on="sunday") as d:
            pass

        diagram = d.build()
        assert diagram.week_starts_on == "sunday"

    def test_min_days_in_first_week(self):
        with gantt_diagram(min_days_in_first_week=4) as d:
            pass

        diagram = d.build()
        assert diagram.min_days_in_first_week == 4

    def test_print_range(self):
        with gantt_diagram(print_range=(date(2024, 1, 1), date(2024, 1, 31))) as d:
            pass

        diagram = d.build()
        assert diagram.print_range == (date(2024, 1, 1), date(2024, 1, 31))

    def test_hide_resource_names(self):
        with gantt_diagram(hide_resource_names=True) as d:
            pass

        diagram = d.build()
        assert diagram.hide_resource_names is True

    def test_hide_resource_footbox(self):
        with gantt_diagram(hide_resource_footbox=True) as d:
            pass

        diagram = d.build()
        assert diagram.hide_resource_footbox is True

    def test_diagram_style_from_dict(self):
        with gantt_diagram(
            diagram_style={"task": {"background": "LightBlue"}}
        ) as d:
            pass

        diagram = d.build()
        assert diagram.diagram_style is not None
        assert diagram.diagram_style.task is not None
        assert isinstance(diagram.diagram_style.task.background, Color)
        assert diagram.diagram_style.task.background.value == "LightBlue"


class TestGanttNewPlantUMLIntegration:
    """Integration tests for new Gantt features with PlantUML."""

    @pytest.fixture
    def plantuml_check(self):
        """Check if PlantUML is available."""
        try:
            result = subprocess.run(
                ["plantuml", "-version"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def test_explicit_dates(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with gantt_diagram(start=date(2024, 1, 1)) as d:
            d.task("Build", start=date(2024, 2, 1), end=date(2024, 2, 15))

        puml_file = tmp_path / "gantt_explicit_dates.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_then_sequencing(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with gantt_diagram(start=date(2024, 1, 1)) as d:
            design = d.task("Design", weeks=2)
            d.task("Build", weeks=3, then=design)

        puml_file = tmp_path / "gantt_then.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_resource_allocation(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with gantt_diagram(start=date(2024, 1, 1)) as d:
            d.task("Build", weeks=2, resources=[("Alice", 100), ("Bob", 50)])

        puml_file = tmp_path / "gantt_alloc.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_closed_date_range(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with gantt_diagram(start=date(2024, 1, 1)) as d:
            d.close_date_range(date(2024, 12, 23), date(2024, 12, 27))
            d.task("Task", weeks=2)

        puml_file = tmp_path / "gantt_closed_range.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_colored_dates(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with gantt_diagram(start=date(2024, 1, 1)) as d:
            d.color_date(date(2024, 1, 1), "LightGreen")
            d.color_date_range(date(2024, 1, 10), date(2024, 1, 15), "salmon")
            d.task("Task", weeks=4)

        puml_file = tmp_path / "gantt_colored.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_week_numbering(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with gantt_diagram(start=date(2024, 1, 1), week_numbering=True) as d:
            d.task("Task", weeks=4)

        puml_file = tmp_path / "gantt_week_num.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_task_with_link(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with gantt_diagram(start=date(2024, 1, 1)) as d:
            d.task("Build", weeks=2, link="https://example.com")

        puml_file = tmp_path / "gantt_link.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_resource_off(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with gantt_diagram(start=date(2024, 1, 1)) as d:
            d.resource_off("Alice", date(2024, 1, 15), date(2024, 1, 16))
            d.task("Build", weeks=2, resources=["Alice"])

        puml_file = tmp_path / "gantt_res_off.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_full_new_features(self, plantuml_check, tmp_path):
        """Full project example using all new features."""
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        with gantt_diagram(
            start=date(2024, 1, 1),
            title="Project Plan",
            week_numbering=True,
            hide_resource_names=False,
            diagram_style=GanttDiagramStyle(
                task=ElementStyle(background="LightBlue"),
                milestone=ElementStyle(background="Gold"),
            ),
        ) as d:
            d.close_weekends()
            d.close_date_range(date(2024, 12, 23), date(2024, 12, 27))
            d.open_date(date(2024, 12, 24))
            d.color_date(date(2024, 1, 1), "LightGreen")

            d.resource_off("Alice", date(2024, 1, 15), date(2024, 1, 16))

            d.milestone("Kickoff", on=date(2024, 1, 1))

            d.separator("Phase 1: Design")
            design = d.task(
                "Design",
                weeks=2,
                resources=[("Alice", 100), ("Bob", 50)],
                note="Design phase",
            )

            d.separator("Phase 2: Build")
            backend = d.task("Backend", weeks=3, then=design, resources=["Bob"])
            frontend = d.task("Frontend", weeks=3, then=design, resources=["Charlie"])

            d.task("Documentation", weeks=2, then=design, same_row_as=backend)

            d.separator("Phase 3: Ship")
            integration = d.task(
                "Integration",
                weeks=1,
                after=[backend, frontend],
                pauses_on=[date(2024, 2, 14)],
            )

            d.vertical_separator(after=integration)

            testing = d.task("Testing", start=date(2024, 2, 20), end=date(2024, 3, 1))

            d.milestone("Release", after=testing, link="https://releases.example.com")

        puml_file = tmp_path / "gantt_full_new.puml"
        puml_file.write_text(d.render())

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"
