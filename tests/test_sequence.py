"""Tests for sequence diagram builder, primitives, and renderer."""

import pytest

from plantuml_compose import render
from plantuml_compose.builders.sequence import sequence_diagram
from plantuml_compose.primitives.sequence import (
    Activation,
    Autonumber,
    Box,
    Delay,
    Divider,
    ElseBlock,
    GroupBlock,
    Message,
    Participant,
    Reference,
    Return,
    SequenceDiagram,
    SequenceNote,
    Space,
)
from plantuml_compose.renderers.sequence import render_sequence_diagram


class TestParticipant:
    """Tests for participant creation and rendering."""

    def test_basic_participant(self):
        with sequence_diagram() as d:
            user = d.participant("User")

        output = render(d.build())
        assert "participant User" in output

    def test_participant_with_alias(self):
        with sequence_diagram() as d:
            d.participant("Long User Name", alias="user")

        output = render(d.build())
        assert 'participant "Long User Name" as user' in output

    def test_actor(self):
        with sequence_diagram() as d:
            d.actor("User")

        output = render(d.build())
        assert "actor User" in output

    def test_database(self):
        with sequence_diagram() as d:
            d.database("MySQL")

        output = render(d.build())
        assert "database MySQL" in output

    def test_boundary(self):
        with sequence_diagram() as d:
            d.boundary("API")

        output = render(d.build())
        assert "boundary API" in output

    def test_control(self):
        with sequence_diagram() as d:
            d.control("Controller")

        output = render(d.build())
        assert "control Controller" in output

    def test_entity(self):
        with sequence_diagram() as d:
            d.entity("Order")

        output = render(d.build())
        assert "entity Order" in output

    def test_queue(self):
        with sequence_diagram() as d:
            d.queue("MessageQueue")

        output = render(d.build())
        assert "queue MessageQueue" in output

    def test_collections(self):
        with sequence_diagram() as d:
            d.collections("Users")

        output = render(d.build())
        assert "collections Users" in output

    def test_participant_with_order(self):
        with sequence_diagram() as d:
            d.participant("User", order=10)

        output = render(d.build())
        assert "participant User order 10" in output

    def test_participant_with_color(self):
        with sequence_diagram() as d:
            d.participant("User", color="red")

        output = render(d.build())
        assert "participant User #red" in output

    def test_participants_bulk_creation(self):
        with sequence_diagram() as d:
            user, api, db = d.participants("User", "API", "Database")

        assert user.name == "User"
        assert api.name == "API"
        assert db.name == "Database"
        output = render(d.build())
        assert "participant User" in output
        assert "participant API" in output
        assert "participant Database" in output

    def test_participant_with_multiline_description(self):
        with sequence_diagram() as d:
            d.participant("User", description="Primary user\ninterface")

        output = render(d.build())
        # Multiline descriptions use bracket syntax
        assert "participant User [" in output
        assert "Primary user" in output
        assert "interface" in output
        assert "]" in output


class TestMessage:
    """Tests for message creation and rendering."""

    def test_basic_message(self):
        with sequence_diagram() as d:
            user = d.participant("User")
            api = d.participant("API")
            d.message(user, api, "request")

        output = render(d.build())
        assert "User -> API : request" in output

    def test_message_dotted(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "request", line_style="dotted")

        output = render(d.build())
        assert "User --> API : request" in output

    def test_message_thin_arrow(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "request", arrow_head="thin")

        output = render(d.build())
        assert "User ->> API : request" in output

    def test_message_bidirectional(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "sync", bidirectional=True)

        output = render(d.build())
        assert "User <-> API : sync" in output

    def test_message_bidirectional_lost(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "msg", arrow_head="lost", bidirectional=True)

        output = render(d.build())
        assert "<->x" in output

    def test_message_bidirectional_circle(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "msg", arrow_head="circle", bidirectional=True)

        output = render(d.build())
        assert "<->o" in output

    def test_message_bidirectional_thin(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "msg", arrow_head="thin", bidirectional=True)

        output = render(d.build())
        assert "<->>" in output

    def test_message_with_activation(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "request", activate="activate")

        output = render(d.build())
        assert "User -> API++ : request" in output

    def test_message_with_deactivation(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.message(api, user, "response", activate="deactivate")

        output = render(d.build())
        assert "API -> User-- : response" in output

    def test_message_with_color(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "request", color="red")

        output = render(d.build())
        assert "-[#red]->" in output

    def test_message_with_bold(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "request", bold=True)

        output = render(d.build())
        assert "-[bold]->" in output

    def test_message_with_combined_styling(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "request", color="blue", bold=True)

        output = render(d.build())
        assert "-[#blue,bold]->" in output

    def test_return_message(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "request")
            d.return_("response")

        output = render(d.build())
        assert "return response" in output


class TestActivation:
    """Tests for explicit activation/deactivation."""

    def test_explicit_activate(self):
        with sequence_diagram() as d:
            user = d.participant("User")
            d.activate(user)

        output = render(d.build())
        assert "activate User" in output

    def test_explicit_deactivate(self):
        with sequence_diagram() as d:
            user = d.participant("User")
            d.deactivate(user)

        output = render(d.build())
        assert "deactivate User" in output

    def test_explicit_destroy(self):
        with sequence_diagram() as d:
            user = d.participant("User")
            d.destroy(user)

        output = render(d.build())
        assert "destroy User" in output

    def test_activate_with_color(self):
        with sequence_diagram() as d:
            user = d.participant("User")
            d.activate(user, color="red")

        output = render(d.build())
        assert "activate User #red" in output


class TestGrouping:
    """Tests for grouping blocks (alt, opt, loop, etc.)."""

    def test_alt_basic(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            with d.alt("success") as alt:
                alt.message(api, user, "200 OK")

        output = render(d.build())
        assert "alt success" in output
        assert "  API -> User : 200 OK" in output
        assert "end" in output

    def test_alt_with_else(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            with d.alt("success") as alt:
                alt.message(api, user, "200 OK")
                with alt.else_("error") as else_block:
                    else_block.message(api, user, "500 Error")

        output = render(d.build())
        assert "alt success" in output
        assert "else error" in output
        assert "end" in output

    def test_opt(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            with d.opt("has_cache") as opt:
                opt.message(api, user, "cached result")

        output = render(d.build())
        assert "opt has_cache" in output
        assert "end" in output

    def test_loop(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            with d.loop("10 times") as loop:
                loop.message(user, api, "retry")

        output = render(d.build())
        assert "loop 10 times" in output
        assert "end" in output

    def test_par(self):
        with sequence_diagram() as d:
            user, api, db = d.participants("User", "API", "Database")
            with d.par("parallel") as par:
                par.message(api, db, "query 1")
                with par.else_() as else_block:
                    else_block.message(api, db, "query 2")

        output = render(d.build())
        assert "par parallel" in output
        assert "else" in output
        assert "end" in output

    def test_break(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            with d.break_("error condition") as brk:
                brk.message(api, user, "error")

        output = render(d.build())
        assert "break error condition" in output
        assert "end" in output

    def test_critical(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            with d.critical("transaction") as crit:
                crit.message(user, api, "commit")

        output = render(d.build())
        assert "critical transaction" in output
        assert "end" in output

    def test_group_custom(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            with d.group("Custom Label", secondary="Secondary") as grp:
                grp.message(user, api, "action")

        output = render(d.build())
        assert "group Custom Label [Secondary]" in output
        assert "end" in output


class TestBox:
    """Tests for participant boxes."""

    def test_box_basic(self):
        with sequence_diagram() as d:
            with d.box("Backend") as backend:
                api = backend.participant("API")
                db = backend.database("Database")

        output = render(d.build())
        assert 'box "Backend"' in output
        assert "end box" in output
        assert "participant API" in output
        assert "database Database" in output

    def test_box_with_color(self):
        with sequence_diagram() as d:
            with d.box("Backend", color="LightBlue") as backend:
                backend.participant("API")

        output = render(d.build())
        assert 'box "Backend" #LightBlue' in output


class TestNotes:
    """Tests for notes."""

    def test_note_right(self):
        with sequence_diagram() as d:
            user = d.participant("User")
            d.note("A note", position="right", of=user)

        output = render(d.build())
        assert "note right of User: A note" in output

    def test_note_left(self):
        with sequence_diagram() as d:
            user = d.participant("User")
            d.note("A note", position="left", of=user)

        output = render(d.build())
        assert "note left of User: A note" in output

    def test_note_over(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.note("Spanning note", over=(user, api))

        output = render(d.build())
        assert "note over User, API: Spanning note" in output

    def test_note_across(self):
        with sequence_diagram() as d:
            d.participants("User", "API", "Database")
            d.note("All participants", across=True)

        output = render(d.build())
        assert "note across: All participants" in output


class TestReference:
    """Tests for references to other diagrams."""

    def test_reference(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.ref(user, api, label="See authentication diagram")

        output = render(d.build())
        assert "ref over User, API : See authentication diagram" in output


class TestDividerDelaySpace:
    """Tests for dividers, delays, and spacing."""

    def test_divider(self):
        with sequence_diagram() as d:
            d.divider("Initialization")

        output = render(d.build())
        assert "== Initialization ==" in output

    def test_delay(self):
        with sequence_diagram() as d:
            d.delay("5 minutes later")

        output = render(d.build())
        assert "...5 minutes later..." in output

    def test_delay_no_message(self):
        with sequence_diagram() as d:
            d.delay()

        output = render(d.build())
        assert "..." in output

    def test_space(self):
        with sequence_diagram() as d:
            d.space()

        output = render(d.build())
        assert "|||" in output

    def test_space_with_pixels(self):
        with sequence_diagram() as d:
            d.space(pixels=45)

        output = render(d.build())
        assert "||45||" in output


class TestAutonumber:
    """Tests for autonumbering."""

    def test_autonumber_on(self):
        with sequence_diagram(autonumber=True) as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "first")

        output = render(d.build())
        assert "autonumber" in output

    def test_autonumber_stop(self):
        with sequence_diagram() as d:
            d.autonumber("stop")

        output = render(d.build())
        assert "autonumber stop" in output

    def test_autonumber_resume(self):
        with sequence_diagram() as d:
            d.autonumber("resume")

        output = render(d.build())
        assert "autonumber resume" in output


class TestDiagramOptions:
    """Tests for diagram-level options."""

    def test_title(self):
        with sequence_diagram(title="My Diagram") as d:
            d.participant("User")

        output = render(d.build())
        assert "title My Diagram" in output

    def test_hide_unlinked(self):
        with sequence_diagram(hide_unlinked=True) as d:
            d.participant("User")

        output = render(d.build())
        assert "hide unlinked" in output


class TestRenderMethod:
    """Tests for the render() convenience method."""

    def test_render_returns_plantuml_text(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "hello")

        output = render(d.build())
        assert output.startswith("@startuml")
        assert output.endswith("@enduml")

    def test_render_equivalent_to_render_build(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "hello")

        from plantuml_compose.renderers import render
        assert render(d.build()) == render(d.build())


class TestEdgeCases:
    """Tests for edge cases and special characters."""

    def test_participant_name_with_spaces(self):
        with sequence_diagram() as d:
            d.participant("My User")

        output = render(d.build())
        # Names with spaces need quoting
        assert 'participant "My User"' in output

    def test_message_label_with_special_chars(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "POST /api/v1/users?name=test")

        output = render(d.build())
        assert "POST /api/v1/users?name=test" in output

    def test_empty_diagram(self):
        with sequence_diagram() as d:
            pass

        output = render(d.build())
        assert "@startuml" in output
        assert "@enduml" in output

    def test_nested_groups(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            with d.alt("outer") as alt:
                alt.message(user, api, "outer message")
                with alt.else_("inner") as else_block:
                    with else_block.opt("nested") as opt:
                        opt.message(api, user, "nested message")

        output = render(d.build())
        assert "alt outer" in output
        assert "else inner" in output
        assert "opt nested" in output


class TestValidation:
    """Tests for input validation."""

    def test_empty_participant_name_rejected(self):
        with sequence_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                d.participant("")

    def test_empty_divider_title_rejected(self):
        with sequence_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                d.divider("")

    def test_empty_note_content_rejected(self):
        with sequence_diagram() as d:
            d.participant("User")
            with pytest.raises(ValueError, match="cannot be empty"):
                d.note("")

    def test_empty_actor_name_rejected(self):
        with sequence_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                d.actor("")

    def test_empty_database_name_rejected(self):
        with sequence_diagram() as d:
            with pytest.raises(ValueError, match="cannot be empty"):
                d.database("")
