"""Integration tests for the composer system.

Verifies that each composer type can render valid PlantUML,
that embedding works across composer types, and basic error cases.
"""

import subprocess
from datetime import date

import pytest

from plantuml_compose.composers import (
    class_diagram,
    component_diagram,
    deployment_diagram,
    gantt_diagram,
    mindmap_diagram,
    network_diagram,
    object_diagram,
    salt_diagram,
    sequence_diagram,
    state_diagram,
    timing_diagram,
    usecase_diagram,
    wbs_diagram,
)
from plantuml_compose.renderers import render


@pytest.fixture
def plantuml_available():
    try:
        result = subprocess.run(
            ["plantuml", "-version"],
            capture_output=True, timeout=10,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def _check_plantuml(puml_text: str, tmp_path, name: str, plantuml_available):
    """Write puml to file and validate with PlantUML."""
    if not plantuml_available:
        pytest.skip("PlantUML not available")
    puml_file = tmp_path / f"{name}.puml"
    puml_file.write_text(puml_text)
    result = subprocess.run(
        ["plantuml", "-checkonly", str(puml_file)],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"PlantUML error for {name}: {result.stderr}"


class TestAllTypesRender:
    """Every composer type produces valid PlantUML."""

    def test_component(self, plantuml_available, tmp_path):
        d = component_diagram(title="Test")
        el = d.elements
        c = d.connections
        pkg = el.package("Service",
            el.component("API", ref="api"),
            el.database("DB", ref="db"),
        )
        d.add(pkg)
        d.connect(c.arrow(pkg.api, pkg.db, "queries"))
        _check_plantuml(render(d), tmp_path, "component", plantuml_available)

    def test_sequence(self, plantuml_available, tmp_path):
        d = sequence_diagram(title="Test")
        p = d.participants
        e = d.events
        a, b = d.add(p.actor("User"), p.participant("API"))
        d.phase("Request", [
            e.message(a, b, "GET /data"),
            e.reply(b, a, "200 OK"),
        ])
        d.if_("cached", [
            e.message(b, b, "return cache"),
        ], "not cached", [
            e.message(b, b, "fetch"),
        ])
        _check_plantuml(render(d), tmp_path, "sequence", plantuml_available)

    def test_class(self, plantuml_available, tmp_path):
        d = class_diagram(title="Test")
        el = d.elements
        r = d.relationships
        base = el.abstract("Base", members=(
            el.field("id", "int"),
            el.separator(),
            el.method("save()"),
        ))
        child = el.class_("Child")
        d.add(base, child)
        d.connect(r.extends(child, base))
        _check_plantuml(render(d), tmp_path, "class", plantuml_available)

    def test_state(self, plantuml_available, tmp_path):
        d = state_diagram(title="Test")
        el = d.elements
        t = d.transitions
        idle = el.state("Idle")
        active = el.state("Active")
        check = el.choice("check")
        d.add(idle, active, check)
        d.connect(
            t.transition("[*]", idle),
            t.transition(idle, check),
            t.transition(check, active, guard="ready"),
            t.transition(active, "[*]"),
        )
        _check_plantuml(render(d), tmp_path, "state", plantuml_available)

    def test_deployment(self, plantuml_available, tmp_path):
        d = deployment_diagram(title="Test")
        el = d.elements
        c = d.connections
        rack = el.frame("Rack",
            el.node("Host",
                el.artifact("app"),
                ref="host",
            ),
            el.database("DB", ref="db"),
        )
        d.add(rack)
        d.connect(c.arrow(rack.host, rack.db))
        _check_plantuml(render(d), tmp_path, "deployment", plantuml_available)

    def test_usecase(self, plantuml_available, tmp_path):
        d = usecase_diagram(title="Test")
        el = d.elements
        r = d.relationships
        user = el.actor("User")
        pkg = el.package("System",
            el.usecase("Login", ref="login"),
            el.usecase("View Data", ref="view"),
        )
        d.add(user, pkg)
        d.connect(
            r.arrow(user, pkg.login),
            r.include(pkg.login, pkg.view),
        )
        _check_plantuml(render(d), tmp_path, "usecase", plantuml_available)

    def test_object(self, plantuml_available, tmp_path):
        d = object_diagram(title="Test")
        el = d.elements
        r = d.relationships
        n1 = el.object("server1 : Node", fields={"ram": "64GB"})
        ct = el.object("ct-1 : Container", fields={"mem": "8GB"})
        d.add(n1, ct)
        d.connect(r.composition(n1, ct))
        _check_plantuml(render(d), tmp_path, "object", plantuml_available)

    def test_mindmap(self, plantuml_available, tmp_path):
        d = mindmap_diagram()
        n = d.nodes
        d.add(n.node("Root",
            n.node("Branch",
                n.leaf("Leaf 1"),
                n.leaf("Leaf 2"),
            ),
            n.leaf("Other", side="left"),
        ))
        _check_plantuml(render(d), tmp_path, "mindmap", plantuml_available)

    def test_wbs(self, plantuml_available, tmp_path):
        d = wbs_diagram()
        n = d.nodes
        c = d.connections
        a = n.leaf("Task A")
        b = n.leaf("Task B")
        d.add(n.node("Project", a, b))
        d.connect(c.arrow(a, b))
        _check_plantuml(render(d), tmp_path, "wbs", plantuml_available)

    def test_salt(self, plantuml_available, tmp_path):
        d = salt_diagram(title="Test")
        w = d.widgets
        d.add(
            w.grid("#",
                w.row(w.text("Name"), w.text_field("val", width=15)),
            ),
            w.button("OK"),
        )
        _check_plantuml(render(d), tmp_path, "salt", plantuml_available)

    def test_network(self, plantuml_available, tmp_path):
        d = network_diagram(title="Test")
        n = d.networks
        d.add(n.node("Internet", shape="cloud"))
        d.add(n.network("DMZ",
            n.node("Internet"),
            n.node("Web", address="10.0.1.1"),
        ))
        _check_plantuml(render(d), tmp_path, "network", plantuml_available)

    def test_timing(self, plantuml_available, tmp_path):
        d = timing_diagram(title="Test")
        p = d.participants
        e = d.events
        sig = p.robust("Signal",
            states=("low", "high"),
            initial="low",
        )
        d.add(sig)
        d.at(10, e.state(sig, "high"))
        d.at(20, e.state(sig, "low"))
        _check_plantuml(render(d), tmp_path, "timing", plantuml_available)

    def test_gantt(self, plantuml_available, tmp_path):
        d = gantt_diagram(title="Test", start=date(2026, 4, 6))
        tk = d.tasks
        dep = d.dependencies
        d.close_days("saturday", "sunday")
        a = tk.task("Task A", days=3)
        b = tk.task("Task B", days=2)
        d.add(a, b)
        d.connect(dep.after(b, a))
        _check_plantuml(render(d), tmp_path, "gantt", plantuml_available)


class TestCrossTypeEmbedding:
    """Test embedding one composer's diagram in another's note."""

    def test_component_in_sequence_note(self, plantuml_available, tmp_path):
        # Build component diagram to embed
        arch = component_diagram()
        el = arch.elements
        c = arch.connections
        api = el.component("API")
        db = el.database("DB")
        arch.add(api, db)
        arch.connect(c.arrow(api, db))

        # Embed in sequence note via embed()
        d = sequence_diagram(title="With Architecture")
        p = d.participants
        e = d.events
        a, b = d.add(p.actor("User"), p.participant("Service"))
        d.phase("Flow", [
            e.message(a, b, "request"),
        ])
        d.note(arch.embed(), target=b)

        puml = render(d)
        assert "@startuml" in puml
        assert "API" in puml
        if plantuml_available:
            _check_plantuml(puml, tmp_path, "embed", plantuml_available)


class TestRenderIntegration:
    """Test that render() accepts composers directly."""

    def test_render_accepts_composer_directly(self):
        d = mindmap_diagram()
        n = d.nodes
        d.add(n.node("Root", n.leaf("Child")))
        result = render(d)
        assert "@startmindmap" in result
        assert "Root" in result

    def test_render_accepts_build_result(self):
        d = mindmap_diagram()
        n = d.nodes
        d.add(n.node("Root", n.leaf("Child")))
        result = render(d.build())
        assert "@startmindmap" in result
        assert "Root" in result

    def test_both_produce_same_output(self):
        d = component_diagram(title="Same")
        el = d.elements
        d.add(el.component("API"))
        direct = render(d)
        via_build = render(d.build())
        assert direct == via_build
