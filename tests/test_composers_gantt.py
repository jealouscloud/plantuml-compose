"""Tests for the gantt diagram composer."""

import subprocess
from datetime import date

import pytest

from plantuml_compose.composers.gantt import gantt_diagram
from plantuml_compose.primitives.gantt import (
    GanttDependency,
    GanttDiagram,
    GanttMilestone,
    GanttResourceOff,
    GanttSeparator,
    GanttTask,
)
from plantuml_compose.renderers import render


class TestGanttComposer:

    def test_empty_diagram(self):
        d = gantt_diagram()
        result = d.build()
        assert isinstance(result, GanttDiagram)
        assert result.elements == ()

    def test_task(self):
        d = gantt_diagram()
        tk = d.tasks
        audit = tk.task("Audit", days=3)
        d.add(audit)
        result = d.build()
        tasks = [e for e in result.elements if isinstance(e, GanttTask)]
        assert len(tasks) == 1
        assert tasks[0].name == "Audit"
        assert tasks[0].duration_days == 3

    def test_task_with_color(self):
        d = gantt_diagram()
        tk = d.tasks
        prep = tk.task("Prepare", days=5, color="#E3F2FD")
        d.add(prep)
        result = d.build()
        tasks = [e for e in result.elements if isinstance(e, GanttTask)]
        assert tasks[0].color == "#E3F2FD"

    def test_milestone(self):
        d = gantt_diagram()
        tk = d.tasks
        ms = tk.milestone("Release", color="#4CAF50")
        d.add(ms)
        result = d.build()
        milestones = [e for e in result.elements if isinstance(e, GanttMilestone)]
        assert len(milestones) == 1
        assert milestones[0].name == "Release"
        assert milestones[0].color == "#4CAF50"

    def test_after_dependency(self):
        d = gantt_diagram()
        tk = d.tasks
        dep = d.dependencies
        audit = tk.task("Audit", days=3)
        prep = tk.task("Prepare", days=5)
        d.add(audit, prep)
        d.connect(dep.after(prep, audit))
        result = d.build()
        tasks = [e for e in result.elements if isinstance(e, GanttTask)]
        # prep should have starts_after set to audit's alias
        prep_task = [t for t in tasks if t.name == "Prepare"][0]
        audit_task = [t for t in tasks if t.name == "Audit"][0]
        assert prep_task.starts_after == audit_task.alias

    def test_starts_with(self):
        d = gantt_diagram()
        tk = d.tasks
        dep = d.dependencies
        a = tk.task("A", days=3)
        b = tk.task("B", days=3)
        d.add(a, b)
        d.connect(dep.starts_with(b, a))
        result = d.build()
        tasks = [e for e in result.elements if isinstance(e, GanttTask)]
        b_task = [t for t in tasks if t.name == "B"][0]
        a_task = [t for t in tasks if t.name == "A"][0]
        assert b_task.starts_with == a_task.alias

    def test_separator_ordering(self):
        """Separators interleave with tasks in order."""
        d = gantt_diagram()
        tk = d.tasks
        audit = tk.task("Audit", days=3)
        d.add(audit)
        d.separator("Wave 1")
        drain = tk.task("Drain", days=3)
        d.add(drain)
        result = d.build()
        # Order: task, separator, task
        assert len(result.elements) == 3
        assert isinstance(result.elements[0], GanttTask)
        assert isinstance(result.elements[1], GanttSeparator)
        assert result.elements[1].label == "Wave 1"
        assert isinstance(result.elements[2], GanttTask)

    def test_close_days(self):
        d = gantt_diagram()
        d.close_days("saturday", "sunday")
        result = d.build()
        assert "saturday" in result.closed_days
        assert "sunday" in result.closed_days

    def test_milestone_after_dependency(self):
        d = gantt_diagram()
        tk = d.tasks
        dep = d.dependencies
        test = tk.task("Test", days=2)
        go_nogo = tk.milestone("Go / No-Go", color="#4CAF50")
        d.add(test, go_nogo)
        d.connect(dep.after(go_nogo, test))
        result = d.build()
        milestones = [e for e in result.elements if isinstance(e, GanttMilestone)]
        assert len(milestones) == 1
        test_task = [e for e in result.elements if isinstance(e, GanttTask)][0]
        assert milestones[0].happens_at == test_task.alias

    def test_multiple_after_dependencies(self):
        """Multiple predecessors: first goes to starts_after, rest become arrows."""
        d = gantt_diagram()
        tk = d.tasks
        dep = d.dependencies
        a = tk.task("A", days=2)
        b = tk.task("B", days=2)
        c = tk.task("C", days=1)
        d.add(a, b, c)
        d.connect(dep.after(c, [a, b]))
        result = d.build()
        tasks = [e for e in result.elements if isinstance(e, GanttTask)]
        c_task = [t for t in tasks if t.name == "C"][0]
        a_task = [t for t in tasks if t.name == "A"][0]
        b_task = [t for t in tasks if t.name == "B"][0]
        # First predecessor is starts_after
        assert c_task.starts_after == a_task.alias
        # Second predecessor becomes a GanttDependency
        deps = [e for e in result.elements if isinstance(e, GanttDependency)]
        assert len(deps) == 1
        assert deps[0].from_alias == b_task.alias
        assert deps[0].to_alias == c_task.alias

    def test_project_start(self):
        d = gantt_diagram(title="Migration", start=date(2026, 4, 6))
        result = d.build()
        assert result.project_start == date(2026, 4, 6)
        assert result.title == "Migration"

    def test_render_produces_plantuml(self):
        d = gantt_diagram(title="Test", start=date(2026, 1, 1))
        tk = d.tasks
        dep = d.dependencies
        audit = tk.task("Audit", days=3)
        prep = tk.task("Prepare", days=5)
        d.add(audit, prep)
        d.connect(dep.after(prep, audit))
        result = render(d)
        assert "@startgantt" in result
        assert "Audit" in result
        assert "@endgantt" in result


class TestGanttPlantUMLValidation:

    @pytest.fixture
    def plantuml_check(self):
        try:
            result = subprocess.run(
                ["plantuml", "-version"],
                capture_output=True, timeout=10,
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def test_plantuml_validation(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = gantt_diagram(title="Migration", start=date(2026, 4, 6))
        tk = d.tasks
        dep = d.dependencies

        d.close_days("saturday", "sunday")

        d.separator("Preparation")
        audit = tk.task("Audit", days=3)
        prep = tk.task("Prepare", days=5, color="#E3F2FD")
        test = tk.task("Test migration", days=2)
        go_nogo = tk.milestone("Go / No-Go", color="#4CAF50")
        d.add(audit, prep, test, go_nogo)

        d.separator("Wave 1")
        drain = tk.task("Drain node-01", days=3, color="#FFF3E0")
        reprov = tk.task("Re-provision", days=2, color="#E8F5E9")
        d.add(drain, reprov)

        d.connect(
            dep.after(prep, audit),
            dep.after(test, prep),
            dep.after(go_nogo, test),
            dep.after(drain, go_nogo),
            dep.after(reprov, drain),
        )

        puml_file = tmp_path / "gantt_composer.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"


class TestGanttHideAndRowFeatures:

    def test_hide_resource_names(self):
        d = gantt_diagram(hide_resource_names=True)
        result = d.build()
        assert result.hide_resource_names is True
        output = render(d)
        assert "hide resources names" in output

    def test_hide_resource_footbox(self):
        d = gantt_diagram(hide_resource_footbox=True)
        result = d.build()
        assert result.hide_resource_footbox is True
        output = render(d)
        assert "hide resources footbox" in output

    def test_on_same_row_as(self):
        d = gantt_diagram(start=date(2026, 4, 6))
        tk = d.tasks
        task_a = tk.task("A", days=3)
        task_b = tk.task("B", on_same_row_as=task_a, days=3)
        d.add(task_a, task_b)
        result = d.build()
        tasks = [e for e in result.elements if isinstance(e, GanttTask)]
        b_task = [t for t in tasks if t.name == "B"][0]
        assert b_task.on_same_row_as is not None
        output = render(d)
        assert "displays on same row" in output

    def test_start_with_days(self):
        d = gantt_diagram(start=date(2026, 4, 1))
        tk = d.tasks
        task = tk.task("A", start=date(2026, 4, 6), days=5)
        d.add(task)
        result = d.build()
        tasks = [e for e in result.elements if isinstance(e, GanttTask)]
        assert tasks[0].start_date == date(2026, 4, 6)
        assert tasks[0].duration_days == 5
        output = render(d)
        assert "2026-04-06" in output
        assert "5 days" in output


class TestGanttNewFeatures:

    def test_language(self):
        d = gantt_diagram(language="de")
        result = d.build()
        assert result.language == "de"

    def test_week_numbering(self):
        d = gantt_diagram(week_numbering=True)
        result = d.build()
        assert result.week_numbering is True

    def test_show_calendar_date(self):
        d = gantt_diagram(show_calendar_date=True)
        result = d.build()
        assert result.show_calendar_date is True

    def test_week_starts_on(self):
        d = gantt_diagram(week_starts_on="monday")
        result = d.build()
        assert result.week_starts_on == "monday"

    def test_min_days_in_first_week(self):
        d = gantt_diagram(min_days_in_first_week=4)
        result = d.build()
        assert result.min_days_in_first_week == 4

    def test_scale(self):
        d = gantt_diagram(scale="weekly")
        result = d.build()
        assert result.scale == "weekly"

    def test_scale_zoom(self):
        d = gantt_diagram(scale="weekly", scale_zoom=2)
        result = d.build()
        assert result.scale == "weekly"
        assert result.scale_zoom == 2

    def test_resource_off(self):
        d = gantt_diagram(start=date(2026, 1, 1))
        tk = d.tasks
        task = tk.task("Dev", days=5, resources=("Alice",))
        d.add(task)
        d.resource_off("Alice", date(2026, 1, 3), date(2026, 1, 4))
        result = d.build()
        resource_offs = [e for e in result.elements if isinstance(e, GanttResourceOff)]
        assert len(resource_offs) == 1
        assert resource_offs[0].resource == "Alice"
        assert resource_offs[0].dates == (date(2026, 1, 3), date(2026, 1, 4))

    def test_close_dates(self):
        d = gantt_diagram(start=date(2026, 1, 1))
        d.close_dates(date(2026, 1, 1), date(2026, 1, 2))
        result = d.build()
        assert date(2026, 1, 1) in result.closed_dates
        assert date(2026, 1, 2) in result.closed_dates

    def test_print_range(self):
        d = gantt_diagram(
            start=date(2026, 1, 1),
            print_range=(date(2026, 1, 1), date(2026, 3, 1)),
        )
        result = d.build()
        assert result.print_range == (date(2026, 1, 1), date(2026, 3, 1))

    def test_all_constructor_params(self):
        """Ensure all new constructor params pass through to GanttDiagram."""
        d = gantt_diagram(
            title="Full",
            start=date(2026, 1, 1),
            language="ja",
            week_numbering=3,
            show_calendar_date=True,
            week_starts_on="tuesday",
            min_days_in_first_week=2,
            scale="monthly",
            scale_zoom=3,
            print_range=(date(2026, 1, 1), date(2026, 6, 1)),
        )
        result = d.build()
        assert result.language == "ja"
        assert result.week_numbering == 3
        assert result.show_calendar_date is True
        assert result.week_starts_on == "tuesday"
        assert result.min_days_in_first_week == 2
        assert result.scale == "monthly"
        assert result.scale_zoom == 3
        assert result.print_range == (date(2026, 1, 1), date(2026, 6, 1))
