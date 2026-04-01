"""Tests for the sequence diagram composer."""

import subprocess

import pytest

from plantuml_compose.composers.sequence import sequence_diagram
from plantuml_compose.primitives.common import Label, Newpage
from plantuml_compose.primitives.sequence import (
    Activation,
    Autonumber,
    Box,
    GroupBlock,
    Message,
    Participant,
    Reference,
    Return,
    SequenceDiagram,
    SequenceNote,
    Space,
)
from plantuml_compose.renderers import render


class TestSequenceComposer:

    def test_empty_diagram(self):
        d = sequence_diagram()
        result = d.build()
        assert isinstance(result, SequenceDiagram)
        assert result.elements == ()
        assert result.participants == ()

    def test_participants(self):
        d = sequence_diagram()
        p = d.participants
        admin = p.actor("Admin")
        api = p.participant("API")
        db = p.database("DB")
        d.add(admin, api, db)
        result = d.build()
        assert len(result.participants) == 3
        assert result.participants[0].name == "Admin"
        assert result.participants[0].type == "actor"
        assert result.participants[1].name == "API"
        assert result.participants[1].type == "participant"
        assert result.participants[2].name == "DB"
        assert result.participants[2].type == "database"

    def test_phase_with_messages(self):
        d = sequence_diagram()
        p = d.participants
        e = d.events
        a = p.actor("Alice")
        b = p.participant("Bob")
        d.add(a, b)
        d.phase("Greeting", [
            e.message(a, b, "Hello"),
            e.message(b, a, "Hi"),
        ])
        result = d.build()
        # Phase becomes a GroupBlock
        groups = [el for el in result.elements if isinstance(el, GroupBlock)]
        assert len(groups) == 1
        group = groups[0]
        assert group.type == "group"
        assert group.label.text == "Greeting"
        assert len(group.elements) == 2
        msg1 = group.elements[0]
        assert isinstance(msg1, Message)
        assert msg1.label.text == "Hello"
        assert msg1.line_style == "solid"

    def test_reply_is_dotted(self):
        d = sequence_diagram()
        p = d.participants
        e = d.events
        a = p.participant("A")
        b = p.participant("B")
        d.add(a, b)
        d.phase("Flow", [
            e.message(a, b, "request"),
            e.reply(b, a, "response"),
        ])
        result = d.build()
        group = [el for el in result.elements if isinstance(el, GroupBlock)][0]
        reply = group.elements[1]
        assert isinstance(reply, Message)
        assert reply.line_style == "dotted"
        assert reply.label.text == "response"

    def test_event_note_inside_phase(self):
        d = sequence_diagram()
        p = d.participants
        e = d.events
        a = p.participant("A")
        d.add(a)
        d.phase("Flow", [
            e.note("Important", over=a),
        ])
        result = d.build()
        group = [el for el in result.elements if isinstance(el, GroupBlock)][0]
        note = group.elements[0]
        assert isinstance(note, SequenceNote)
        assert note.content.text == "Important"
        assert note.position == "over"
        assert a._ref in note.participants

    def test_diagram_note_outside_phase(self):
        d = sequence_diagram()
        p = d.participants
        a = p.participant("A")
        d.add(a)
        d.note("Diagram-level note", target=a)
        result = d.build()
        notes = [el for el in result.elements if isinstance(el, SequenceNote)]
        assert len(notes) == 1
        assert notes[0].content.text == "Diagram-level note"
        # Default position from BaseComposer is "right", preserved for targeted notes
        assert notes[0].position == "right"

    def test_render_produces_plantuml(self):
        d = sequence_diagram(title="Boot")
        p = d.participants
        e = d.events
        admin = p.actor("Admin")
        api = p.participant("API")
        d.add(admin, api)
        d.phase("Request", [
            e.message(admin, api, "POST /add"),
            e.reply(api, admin, "OK"),
        ])
        result = render(d)
        assert "@startuml" in result
        assert "Admin" in result
        assert "POST /add" in result
        assert "@enduml" in result

    def test_title_and_theme(self):
        d = sequence_diagram(title="Flow", theme="vibrant")
        result = d.build()
        assert result.title == "Flow"
        assert result.theme == "vibrant"

    def test_all_participant_types(self):
        d = sequence_diagram()
        p = d.participants
        refs = [
            p.actor("A"),
            p.participant("B"),
            p.boundary("C"),
            p.control("D"),
            p.entity("E"),
            p.database("F"),
            p.collections("G"),
            p.queue("H"),
        ]
        d.add(*refs)
        result = d.build()
        types = [part.type for part in result.participants]
        assert types == [
            "actor", "participant", "boundary", "control",
            "entity", "database", "collections", "queue",
        ]


class TestSequenceInteractionFrames:

    def test_if_simple(self):
        d = sequence_diagram()
        p = d.participants
        e = d.events
        a, b = d.add(p.participant("A"), p.participant("B"))
        d.if_("valid", [
            e.message(a, b, "ok"),
        ], "invalid", [
            e.message(a, b, "error"),
        ])
        result = d.build()
        blocks = [el for el in result.elements if isinstance(el, GroupBlock)]
        assert len(blocks) == 1
        block = blocks[0]
        assert block.type == "alt"
        assert block.label.text == "valid"
        assert len(block.elements) == 1
        assert len(block.else_blocks) == 1
        assert block.else_blocks[0].label.text == "invalid"

    def test_if_three_branches(self):
        d = sequence_diagram()
        p = d.participants
        e = d.events
        a, b = d.add(p.participant("A"), p.participant("B"))
        d.if_("case 1", [
            e.message(a, b, "path 1"),
        ], "case 2", [
            e.message(a, b, "path 2"),
        ], "case 3", [
            e.message(a, b, "path 3"),
        ])
        result = d.build()
        block = [el for el in result.elements if isinstance(el, GroupBlock)][0]
        assert block.type == "alt"
        assert len(block.else_blocks) == 2

    def test_optional(self):
        d = sequence_diagram()
        p = d.participants
        e = d.events
        a, b = d.add(p.participant("A"), p.participant("B"))
        d.optional("has cache", [
            e.message(a, b, "check"),
        ])
        result = d.build()
        block = [el for el in result.elements if isinstance(el, GroupBlock)][0]
        assert block.type == "opt"
        assert block.label.text == "has cache"
        assert block.else_blocks == ()

    def test_loop(self):
        d = sequence_diagram()
        p = d.participants
        e = d.events
        a, b = d.add(p.participant("A"), p.participant("B"))
        d.loop("3 times", [
            e.message(a, b, "retry"),
        ])
        result = d.build()
        block = [el for el in result.elements if isinstance(el, GroupBlock)][0]
        assert block.type == "loop"

    def test_parallel(self):
        d = sequence_diagram()
        p = d.participants
        e = d.events
        a, b, c = d.add(p.participant("A"), p.participant("B"), p.participant("C"))
        d.parallel([
            e.message(a, b, "notify"),
        ], None, [
            e.message(a, c, "log"),
        ])
        result = d.build()
        block = [el for el in result.elements if isinstance(el, GroupBlock)][0]
        assert block.type == "par"
        assert len(block.else_blocks) == 1

    def test_break(self):
        d = sequence_diagram()
        p = d.participants
        e = d.events
        a, b = d.add(p.participant("A"), p.participant("B"))
        d.break_("service recovered", [
            e.message(a, b, "resolve"),
        ])
        result = d.build()
        block = [el for el in result.elements if isinstance(el, GroupBlock)][0]
        assert block.type == "break"

    def test_critical(self):
        d = sequence_diagram()
        p = d.participants
        e = d.events
        a, b = d.add(p.participant("A"), p.participant("B"))
        d.critical("mutex on config", [
            e.message(a, b, "update"),
        ])
        result = d.build()
        block = [el for el in result.elements if isinstance(el, GroupBlock)][0]
        assert block.type == "critical"

    def test_nested_blocks(self):
        """Loop containing an optional — blocks nest via event-level factories."""
        d = sequence_diagram()
        p = d.participants
        e = d.events
        a, b = d.add(p.participant("A"), p.participant("B"))
        d.loop("until done", [
            e.message(a, b, "check"),
            e.optional("improving", [
                e.message(a, b, "ack"),
            ]),
        ])
        result = d.build()
        loop_block = [el for el in result.elements if isinstance(el, GroupBlock)][0]
        assert loop_block.type == "loop"
        assert len(loop_block.elements) == 2
        inner = loop_block.elements[1]
        assert isinstance(inner, GroupBlock)
        assert inner.type == "opt"

    def test_extracted_block_variable(self):
        """Blocks as named variables for readability."""
        d = sequence_diagram()
        p = d.participants
        e = d.events
        a, b = d.add(p.participant("A"), p.participant("B"))

        auth_check = e.if_("authorized", [
            e.message(a, b, "proceed"),
        ], "forbidden", [
            e.message(a, b, "403"),
        ])

        d.if_("authenticated", [
            auth_check,
        ], "not authenticated", [
            e.message(a, b, "401"),
        ])

        result = d.build()
        outer = [el for el in result.elements if isinstance(el, GroupBlock)][0]
        assert outer.type == "alt"
        inner = outer.elements[0]
        assert isinstance(inner, GroupBlock)
        assert inner.type == "alt"

    def test_phase_and_blocks_interleave(self):
        """Phases and blocks can be used together on the timeline."""
        d = sequence_diagram()
        p = d.participants
        e = d.events
        a, b = d.add(p.participant("A"), p.participant("B"))

        d.phase("Setup", [
            e.message(a, b, "init"),
        ])
        d.if_("ready", [
            e.message(a, b, "go"),
        ], "not ready", [
            e.message(a, b, "wait"),
        ])
        d.phase("Cleanup", [
            e.message(a, b, "done"),
        ])

        result = d.build()
        blocks = [el for el in result.elements if isinstance(el, GroupBlock)]
        assert len(blocks) == 3
        assert blocks[0].type == "group"
        assert blocks[1].type == "alt"
        assert blocks[2].type == "group"


class TestSequencePlantUMLValidation:

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

        d = sequence_diagram(title="PXE Boot")
        p = d.participants
        e = d.events

        admin = p.actor("Admin")
        api = p.participant("FastAPI")
        client = p.participant("Client")
        d.add(admin, api, client)

        d.phase("1. Request", [
            e.message(admin, api, "POST /add"),
            e.reply(api, admin, "OK"),
        ])

        d.phase("2. Boot", [
            e.message(client, api, "GET /boot"),
            e.reply(api, client, "iPXE script"),
            e.note("Client boots", over=client),
        ])

        puml_file = tmp_path / "sequence_composer.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"

    def test_interaction_frames_valid_plantuml(self, plantuml_check, tmp_path):
        if not plantuml_check:
            pytest.skip("PlantUML not available")

        d = sequence_diagram(title="Incident Response")
        p = d.participants
        e = d.events

        engineer, monitoring, paging = d.add(
            p.actor("Engineer"),
            p.participant("Monitoring"),
            p.participant("Paging"),
        )

        d.phase("Alert", [
            e.message(monitoring, paging, "threshold breached"),
            e.message(paging, engineer, "page"),
        ])

        d.if_("critical", [
            e.message(engineer, monitoring, "lookup playbook"),
            e.loop("until resolved", [
                e.message(engineer, monitoring, "check metrics"),
                e.optional("improving", [
                    e.message(engineer, monitoring, "ack"),
                ]),
            ]),
        ], "warning", [
            e.message(engineer, monitoring, "acknowledge"),
        ], "info", [
            e.message(engineer, monitoring, "silence"),
        ])

        d.parallel([
            e.message(engineer, monitoring, "update status"),
        ], None, [
            e.message(engineer, paging, "notify team"),
        ])

        d.phase("Resolution", [
            e.message(engineer, paging, "resolve"),
        ])

        puml_file = tmp_path / "sequence_frames.puml"
        puml_file.write_text(render(d))

        result = subprocess.run(
            ["plantuml", "-checkonly", str(puml_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PlantUML error: {result.stderr}"


class TestSequenceActivationLifecycle:

    def test_activate_deactivate_on_timeline(self):
        d = sequence_diagram()
        p = d.participants
        e = d.events
        a, b = d.add(p.participant("A"), p.participant("B"))
        d.phase("Flow", [
            e.message(a, b, "request"),
        ])
        d.activate(b, color="#LightBlue")
        d.phase("Processing", [
            e.message(b, a, "response"),
        ])
        d.deactivate(b)
        result = d.build()
        activations = [el for el in result.elements if isinstance(el, Activation)]
        assert len(activations) == 2
        assert activations[0].action == "activate"
        assert activations[0].color == "#LightBlue"
        assert activations[1].action == "deactivate"

    def test_activate_deactivate_in_events(self):
        d = sequence_diagram()
        p = d.participants
        e = d.events
        a, b = d.add(p.participant("A"), p.participant("B"))
        d.phase("Flow", [
            e.message(a, b, "request"),
            e.activate(b),
            e.message(b, a, "response"),
            e.deactivate(b),
        ])
        result = d.build()
        group = [el for el in result.elements if isinstance(el, GroupBlock)][0]
        activations = [el for el in group.elements if isinstance(el, Activation)]
        assert len(activations) == 2
        assert activations[0].action == "activate"
        assert activations[1].action == "deactivate"

    def test_create_destroy(self):
        d = sequence_diagram()
        p = d.participants
        e = d.events
        factory = p.participant("Factory")
        worker = p.participant("Worker")
        d.add(factory, worker)
        d.create(worker)
        d.phase("Work", [
            e.message(factory, worker, "new()"),
        ])
        d.destroy(worker)
        result = d.build()
        activations = [el for el in result.elements if isinstance(el, Activation)]
        assert len(activations) == 2
        assert activations[0].action == "create"
        assert activations[1].action == "destroy"

    def test_create_destroy_in_events(self):
        d = sequence_diagram()
        p = d.participants
        e = d.events
        factory, worker = d.add(p.participant("Factory"), p.participant("Worker"))
        d.phase("Lifecycle", [
            e.create(worker),
            e.message(factory, worker, "new()"),
            e.destroy(worker),
        ])
        result = d.build()
        group = [el for el in result.elements if isinstance(el, GroupBlock)][0]
        activations = [el for el in group.elements if isinstance(el, Activation)]
        assert len(activations) == 2
        assert activations[0].action == "create"
        assert activations[1].action == "destroy"

    def test_return_in_events(self):
        d = sequence_diagram()
        p = d.participants
        e = d.events
        a, b = d.add(p.participant("Client"), p.participant("Server"))
        d.phase("Flow", [
            e.message(a, b, "getData()"),
            e.return_("data"),
        ])
        result = d.build()
        group = [el for el in result.elements if isinstance(el, GroupBlock)][0]
        returns = [el for el in group.elements if isinstance(el, Return)]
        assert len(returns) == 1
        assert returns[0].label.text == "data"


class TestSequenceBox:

    def test_box_groups_participants(self):
        d = sequence_diagram()
        p = d.participants
        api = p.participant("API")
        db = p.database("DB")
        client = p.actor("Client")
        d.add(client)
        d.box("Backend", api, db, color="#LightBlue")
        result = d.build()
        assert len(result.boxes) == 1
        box = result.boxes[0]
        assert box.name == "Backend"
        assert box.color == "#LightBlue"
        assert len(box.participants) == 2
        assert box.participants[0].name == "API"
        assert box.participants[1].name == "DB"
        # Client should be in standalone participants, not in boxes
        assert len(result.participants) == 1
        assert result.participants[0].name == "Client"


class TestSequenceRef:

    def test_ref(self):
        d = sequence_diagram()
        p = d.participants
        a, b = d.add(p.participant("A"), p.participant("B"))
        d.ref(a, b, label="See Authentication Flow")
        result = d.build()
        refs = [el for el in result.elements if isinstance(el, Reference)]
        assert len(refs) == 1
        assert refs[0].label.text == "See Authentication Flow"
        assert len(refs[0].participants) == 2


class TestSequenceAutonumber:

    def test_autonumber_constructor(self):
        d = sequence_diagram(autonumber=True)
        result = d.build()
        assert result.autonumber is not None
        assert result.autonumber.action == "start"

    def test_autonumber_method(self):
        d = sequence_diagram()
        p = d.participants
        e = d.events
        a, b = d.add(p.participant("A"), p.participant("B"))
        d.autonumber(start=10, increment=5)
        d.phase("Flow", [
            e.message(a, b, "one"),
            e.message(a, b, "two"),
        ])
        result = d.build()
        autonums = [el for el in result.elements if isinstance(el, Autonumber)]
        assert len(autonums) == 1
        assert autonums[0].start == 10
        assert autonums[0].increment == 5


class TestSequenceNewpage:

    def test_newpage(self):
        d = sequence_diagram()
        p = d.participants
        e = d.events
        a, b = d.add(p.participant("A"), p.participant("B"))
        d.phase("Page 1", [
            e.message(a, b, "hello"),
        ])
        d.newpage("Second page")
        d.phase("Page 2", [
            e.message(b, a, "world"),
        ])
        result = d.build()
        newpages = [el for el in result.elements if isinstance(el, Newpage)]
        assert len(newpages) == 1
        assert newpages[0].title == "Second page"


class TestSequenceParticipantStyle:

    def test_participant_with_style(self):
        from plantuml_compose.primitives.common import Style
        d = sequence_diagram()
        p = d.participants
        styled = p.participant("API", style=Style(background="#LightBlue"))
        d.add(styled)
        result = d.build()
        assert result.participants[0].style is not None
        assert result.participants[0].style.background == "#LightBlue"

    def test_participant_order(self):
        d = sequence_diagram()
        p = d.participants
        a = p.actor("A", order=10)
        d.add(a)
        result = d.build()
        assert result.participants[0].order == 10
        output = render(d)
        assert "order 10" in output

    def test_message_style(self):
        d = sequence_diagram()
        p = d.participants
        e = d.events
        a, b = d.add(p.participant("A"), p.participant("B"))
        d.phase("Flow", [
            e.message(a, b, "hello", style={"color": "red"}),
        ])
        output = render(d)
        assert "[#red]" in output

    def test_message_bidirectional(self):
        d = sequence_diagram()
        p = d.participants
        e = d.events
        a, b = d.add(p.participant("A"), p.participant("B"))
        d.phase("Flow", [
            e.message(a, b, "sync", bidirectional=True),
        ])
        result = d.build()
        group = [el for el in result.elements if isinstance(el, GroupBlock)][0]
        msg = group.elements[0]
        assert isinstance(msg, Message)
        assert msg.bidirectional is True
        output = render(d)
        assert "<->" in output

    def test_message_activation(self):
        d = sequence_diagram()
        p = d.participants
        e = d.events
        a, b = d.add(p.participant("A"), p.participant("B"))
        d.phase("Flow", [
            e.message(a, b, "call", activation="activate"),
        ])
        result = d.build()
        group = [el for el in result.elements if isinstance(el, GroupBlock)][0]
        msg = group.elements[0]
        assert isinstance(msg, Message)
        assert msg.activation == "activate"
        output = render(d)
        assert "++" in output

    def test_space(self):
        d = sequence_diagram()
        p = d.participants
        a = p.participant("A")
        d.add(a)
        d.space()
        result = d.build()
        spaces = [el for el in result.elements if isinstance(el, Space)]
        assert len(spaces) == 1
        assert spaces[0].pixels is None
        output = render(d)
        assert "|||" in output

        d2 = sequence_diagram()
        p2 = d2.participants
        a2 = p2.participant("A")
        d2.add(a2)
        d2.space(pixels=45)
        result2 = d2.build()
        spaces2 = [el for el in result2.elements if isinstance(el, Space)]
        assert spaces2[0].pixels == 45
        output2 = render(d2)
        assert "||45||" in output2

    def test_note_multi_participant(self):
        d = sequence_diagram()
        p = d.participants
        e = d.events
        a, b = d.add(p.participant("A"), p.participant("B"))
        d.phase("Flow", [
            e.note("shared note", over=[a, b]),
        ])
        result = d.build()
        group = [el for el in result.elements if isinstance(el, GroupBlock)][0]
        note = group.elements[0]
        assert isinstance(note, SequenceNote)
        assert note.position == "over"
        assert len(note.participants) == 2
        output = render(d)
        assert "note over" in output
        assert "A" in output
        assert "B" in output

    def test_hide_unlinked(self):
        d = sequence_diagram(hide_unlinked=True)
        p = d.participants
        d.add(p.participant("A"))
        result = d.build()
        assert result.hide_unlinked is True
        output = render(d)
        assert "hide unlinked" in output

    def test_autonumber_stop_resume(self):
        d = sequence_diagram(autonumber=True)
        p = d.participants
        e = d.events
        a, b = d.add(p.participant("A"), p.participant("B"))
        d.phase("Flow", [
            e.message(a, b, "one"),
        ])
        d.autonumber_stop()
        d.phase("Untracked", [
            e.message(a, b, "two"),
        ])
        d.autonumber_resume()
        d.phase("Tracked", [
            e.message(a, b, "three"),
        ])
        result = d.build()
        autonums = [el for el in result.elements if isinstance(el, Autonumber)]
        actions = [a.action for a in autonums]
        assert "stop" in actions
        assert "resume" in actions
        output = render(d)
        assert "autonumber stop" in output
        assert "autonumber resume" in output

    def test_note_across(self):
        d = sequence_diagram()
        p = d.participants
        a, b = d.add(p.participant("A"), p.participant("B"))
        d.note("broadcast", across=True)
        result = d.build()
        notes = [el for el in result.elements if isinstance(el, SequenceNote)]
        assert len(notes) == 1
        assert notes[0].across is True
        output = render(d)
        assert "note across" in output

    def test_note_aligned(self):
        d = sequence_diagram()
        p = d.participants
        e = d.events
        a, b = d.add(p.participant("A"), p.participant("B"))
        d.phase("Flow", [
            e.note("first", over=a),
            e.note("aligned note", over=b, aligned=True),
        ])
        result = d.build()
        group = [el for el in result.elements if isinstance(el, GroupBlock)][0]
        aligned_notes = [el for el in group.elements
                        if isinstance(el, SequenceNote) and el.aligned]
        assert len(aligned_notes) == 1
        output = render(d)
        assert "/ note" in output
