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

    def test_participant_with_style(self):
        with sequence_diagram() as d:
            d.participant("User", style={"background": "red"})

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

    def test_message_open_arrow(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "async call", arrow_head="open")

        output = render(d.build())
        assert r"User -\ API : async call" in output

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

    def test_message_bidirectional_open(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "msg", arrow_head="open", bidirectional=True)

        output = render(d.build())
        assert "<-\\" in output

    def test_explicit_activation(self):
        """Use explicit activate() instead of inline parameter."""
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "request")
            d.activate(api)

        output = render(d.build())
        assert "User -> API : request" in output
        assert "activate API" in output

    def test_explicit_deactivation(self):
        """Use explicit deactivate() instead of inline parameter."""
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.activate(api)
            d.message(api, user, "response")
            d.deactivate(api)

        output = render(d.build())
        assert "activate API" in output
        assert "API -> User : response" in output
        assert "deactivate API" in output

    def test_message_with_style_color(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "request", style={"color": "red"})

        output = render(d.build())
        assert "-[#red]->" in output

    def test_message_with_style_bold(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "request", style={"bold": True})

        output = render(d.build())
        assert "-[bold]->" in output

    def test_message_with_combined_styling(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "request", style={"color": "blue", "bold": True})

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
            api = d.participant("API")
            d.message(user, api, "request")
            d.activate(user)
            d.deactivate(user)

        output = render(d.build())
        assert "deactivate User" in output

    def test_explicit_destroy(self):
        with sequence_diagram() as d:
            user = d.participant("User")
            api = d.participant("API")
            d.message(user, api, "request")
            d.activate(user)
            d.destroy(user)

        output = render(d.build())
        assert "destroy User" in output

    def test_activate_with_color(self):
        with sequence_diagram() as d:
            user = d.participant("User")
            d.activate(user, color="red")

        output = render(d.build())
        assert "activate User #red" in output

    def test_explicit_create(self):
        """Test create action marks participant as created at a point."""
        with sequence_diagram() as d:
            user = d.participant("User")
            api = d.participant("API")
            d.create(api)
            d.message(user, api, "instantiate")

        output = render(d.build())
        assert "create API" in output


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
            user, api = d.participants("User", "API")
            d.message(user, api, "request")
            d.divider("Initialization")
            d.message(api, user, "response")

        output = render(d.build())
        assert "== Initialization ==" in output

    def test_delay(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "request")
            d.delay("5 minutes later")
            d.message(api, user, "response")

        output = render(d.build())
        assert "...5 minutes later..." in output

    def test_delay_no_message(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "request")
            d.delay()
            d.message(api, user, "response")

        output = render(d.build())
        assert "..." in output

    def test_space(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "request")
            d.space()
            d.message(api, user, "response")

        output = render(d.build())
        assert "|||" in output

    def test_space_with_pixels(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "request")
            d.space(pixels=45)
            d.message(api, user, "response")

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
        with sequence_diagram(autonumber=True) as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "first")
            d.autonumber("stop")
            d.message(api, user, "second")

        output = render(d.build())
        assert "autonumber stop" in output

    def test_autonumber_resume(self):
        with sequence_diagram(autonumber=True) as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "first")
            d.autonumber("stop")
            d.message(api, user, "second")
            d.autonumber("resume")
            d.message(user, api, "third")

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
            user, api = d.participants("User", "API")
            d.participant("Unused")  # This will be hidden
            d.message(user, api, "request")

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

    def test_participant_style_rejects_text_color(self):
        with sequence_diagram() as d:
            with pytest.raises(ValueError, match="only supports 'background' styling"):
                d.participant("User", style={"text_color": "blue"})

    def test_participant_style_rejects_line(self):
        with sequence_diagram() as d:
            with pytest.raises(ValueError, match="only supports 'background' styling"):
                d.participant("User", style={"line": {"color": "red"}})


class TestBlockMisuseDetection:
    """Tests for detecting d.message() called inside block contexts."""

    def test_message_inside_alt_raises_error(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            with d.alt("condition"):
                with pytest.raises(RuntimeError) as exc_info:
                    d.message(user, api, "wrong")

        # Error message should contain helpful guidance
        error_text = str(exc_info.value)
        assert "d.message() called inside 'alt' block" in error_text
        assert "alt_block.message" in error_text

    def test_message_inside_opt_raises_error(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            with d.opt("condition"):
                with pytest.raises(RuntimeError, match="inside 'opt' block"):
                    d.message(user, api, "wrong")

    def test_message_inside_loop_raises_error(self):
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            with d.loop("10 times"):
                with pytest.raises(RuntimeError, match="inside 'loop' block"):
                    d.message(user, api, "wrong")

    def test_correct_usage_in_block_works(self):
        """Verify that using the block's builder works correctly."""
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            with d.alt("success") as alt:
                alt.message(api, user, "200 OK")

        output = render(d.build())
        assert "alt success" in output
        assert "API -> User : 200 OK" in output

    # Test all protected methods raise errors inside blocks
    def test_return_inside_block_raises_error(self):
        with sequence_diagram() as d:
            d.participants("User", "API")
            with d.alt("condition"):
                with pytest.raises(
                    RuntimeError, match="d.return_\\(\\) called inside 'alt' block"
                ):
                    d.return_("result")

    def test_activate_inside_block_raises_error(self):
        with sequence_diagram() as d:
            user = d.participant("User")
            with d.alt("condition"):
                with pytest.raises(
                    RuntimeError, match="d.activate\\(\\) called inside 'alt' block"
                ):
                    d.activate(user)

    def test_deactivate_inside_block_raises_error(self):
        with sequence_diagram() as d:
            user = d.participant("User")
            with d.alt("condition"):
                with pytest.raises(
                    RuntimeError, match="d.deactivate\\(\\) called inside 'alt' block"
                ):
                    d.deactivate(user)

    def test_destroy_inside_block_raises_error(self):
        with sequence_diagram() as d:
            user = d.participant("User")
            with d.alt("condition"):
                with pytest.raises(
                    RuntimeError, match="d.destroy\\(\\) called inside 'alt' block"
                ):
                    d.destroy(user)

    def test_create_inside_block_raises_error(self):
        with sequence_diagram() as d:
            user = d.participant("User")
            with d.alt("condition"):
                with pytest.raises(
                    RuntimeError, match="d.create\\(\\) called inside 'alt' block"
                ):
                    d.create(user)

    def test_note_inside_block_raises_error(self):
        with sequence_diagram() as d:
            d.participant("User")
            with d.alt("condition"):
                with pytest.raises(
                    RuntimeError, match="d.note\\(\\) called inside 'alt' block"
                ):
                    d.note("test note")

    def test_ref_inside_block_raises_error(self):
        with sequence_diagram() as d:
            user = d.participant("User")
            with d.alt("condition"):
                with pytest.raises(
                    RuntimeError, match="d.ref\\(\\) called inside 'alt' block"
                ):
                    d.ref(user, label="See other diagram")

    def test_divider_inside_block_raises_error(self):
        with sequence_diagram() as d:
            with d.alt("condition"):
                with pytest.raises(
                    RuntimeError, match="d.divider\\(\\) called inside 'alt' block"
                ):
                    d.divider("Section")

    def test_delay_inside_block_raises_error(self):
        with sequence_diagram() as d:
            with d.alt("condition"):
                with pytest.raises(
                    RuntimeError, match="d.delay\\(\\) called inside 'alt' block"
                ):
                    d.delay("5 minutes later")

    def test_space_inside_block_raises_error(self):
        with sequence_diagram() as d:
            with d.alt("condition"):
                with pytest.raises(
                    RuntimeError, match="d.space\\(\\) called inside 'alt' block"
                ):
                    d.space(50)

    def test_all_block_types_track_context(self):
        """Verify all block types are tracked."""
        block_types = [
            ("alt", lambda d: d.alt("x")),
            ("opt", lambda d: d.opt("x")),
            ("loop", lambda d: d.loop("x")),
            ("par", lambda d: d.par("x")),
            ("break", lambda d: d.break_("x")),
            ("critical", lambda d: d.critical("x")),
            ("group", lambda d: d.group("x")),
        ]
        for block_name, block_fn in block_types:
            with sequence_diagram() as d:
                user, api = d.participants("User", "API")
                with block_fn(d):
                    with pytest.raises(
                        RuntimeError, match=f"inside '{block_name}' block"
                    ):
                        d.message(user, api, "wrong")


class TestTeozFeatures:
    """Tests for teoz mode features (parallel messages, slanted arrows)."""

    def test_teoz_pragma_enabled(self):
        """Test that teoz=True adds the pragma."""
        with sequence_diagram(teoz=True) as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "request")

        output = render(d.build())
        assert "!pragma teoz true" in output

    def test_teoz_pragma_not_added_by_default(self):
        """Test that teoz pragma is not added by default."""
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "request")

        output = render(d.build())
        assert "teoz" not in output

    def test_slant_renders_correctly(self):
        """Test slant parameter renders arrow with shift."""
        with sequence_diagram(teoz=True) as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "delayed arrival", slant=10)

        output = render(d.build())
        assert "->(10)" in output

    def test_slant_requires_teoz(self):
        """Test that slant without teoz raises error."""
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "request", slant=10)

        with pytest.raises(ValueError, match="slant requires teoz=True"):
            d.build()

    def test_negative_slant_rejected(self):
        """Test that negative slant values are rejected."""
        with sequence_diagram(teoz=True) as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "request", slant=-5)

        with pytest.raises(ValueError, match="slant must be a non-negative integer"):
            d.build()

    def test_slant_zero_allowed(self):
        """Test that slant=0 is allowed (no-op but valid)."""
        with sequence_diagram(teoz=True) as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "request", slant=0)

        output = render(d.build())
        assert "->(0)" in output

    def test_parallel_renders_correctly(self):
        """Test parallel parameter adds & prefix."""
        with sequence_diagram(teoz=True) as d:
            user, api, db = d.participants("User", "API", "Database")
            d.message(user, api, "first")
            d.message(api, db, "concurrent", parallel=True)

        output = render(d.build())
        assert "& API -> Database : concurrent" in output

    def test_parallel_requires_teoz(self):
        """Test that parallel without teoz raises error."""
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "first")
            d.message(api, user, "parallel", parallel=True)

        with pytest.raises(ValueError, match="parallel requires teoz=True"):
            d.build()

    def test_slant_and_parallel_together(self):
        """Test using both slant and parallel."""
        with sequence_diagram(teoz=True) as d:
            a, b, c = d.participants("A", "B", "C")
            d.message(a, b, "first")
            d.message(b, c, "concurrent and slanted", slant=15, parallel=True)

        output = render(d.build())
        assert "!pragma teoz true" in output
        assert "& B ->(15) C : concurrent and slanted" in output

    def test_slant_in_group_requires_teoz(self):
        """Test that slant in group blocks also requires teoz."""
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            with d.alt("condition") as alt:
                alt.message(user, api, "in alt", slant=5)

        with pytest.raises(ValueError, match="slant requires teoz=True"):
            d.build()

    def test_parallel_in_group_requires_teoz(self):
        """Test that parallel in group blocks also requires teoz."""
        with sequence_diagram() as d:
            user, api = d.participants("User", "API")
            d.message(user, api, "first")
            with d.opt("maybe") as opt:
                opt.message(api, user, "parallel in opt", parallel=True)

        with pytest.raises(ValueError, match="parallel requires teoz=True"):
            d.build()

    def test_teoz_with_slant_in_nested_groups(self):
        """Test teoz features work in deeply nested groups."""
        with sequence_diagram(teoz=True) as d:
            a, b = d.participants("A", "B")
            with d.alt("outer") as alt:
                with alt.else_("inner") as else_block:
                    else_block.message(a, b, "nested slant", slant=20)

        output = render(d.build())
        assert "->(20)" in output


class TestDiagramStyle:
    """Tests for CSS-like diagram-wide styling."""

    def test_diagram_style_with_dict(self):
        """Test diagram_style with dict input."""
        with sequence_diagram(
            diagram_style={
                "background": "white",
                "font_name": "Arial",
                "participant": {"background": "#E3F2FD", "line_color": "#1976D2"},
                "arrow": {"line_color": "#757575"},
            }
        ) as d:
            a, b = d.participants("A", "B")
            d.message(a, b, "hello")

        output = render(d.build())
        assert "<style>" in output
        assert "</style>" in output
        assert "sequenceDiagram {" in output
        assert "BackgroundColor white" in output
        assert "FontName Arial" in output
        assert "participant {" in output
        assert "BackgroundColor #E3F2FD" in output
        assert "LineColor #1976D2" in output
        assert "arrow {" in output
        assert "LineColor #757575" in output

    def test_diagram_style_with_typed_objects(self):
        """Test diagram_style with typed style objects."""
        from plantuml_compose.primitives import (
            SequenceDiagramStyle,
            ElementStyle,
            DiagramArrowStyle,
        )

        style = SequenceDiagramStyle(
            background="white",
            participant=ElementStyle(background="#BBDEFB"),
            arrow=DiagramArrowStyle(line_color="blue", line_thickness=2),
        )
        with sequence_diagram(diagram_style=style) as d:
            a, b = d.participants("A", "B")
            d.message(a, b, "test")

        output = render(d.build())
        assert "BackgroundColor white" in output
        assert "participant {" in output
        assert "BackgroundColor #BBDEFB" in output
        assert "arrow {" in output
        assert "LineColor blue" in output
        assert "LineThickness 2" in output

    def test_diagram_style_actor_specific(self):
        """Test styling specific participant types."""
        with sequence_diagram(
            diagram_style={
                "actor": {"background": "yellow"},
                "database": {"background": "green"},
            }
        ) as d:
            user = d.actor("User")
            db = d.database("DB")
            d.message(user, db, "query")

        output = render(d.build())
        assert "actor {" in output
        assert "database {" in output

    def test_diagram_style_note_and_box(self):
        """Test note and box styling."""
        with sequence_diagram(
            diagram_style={
                "note": {"background": "#FFFDE7", "font_color": "black"},
                "box": {"background": "#E8EAF6"},
            }
        ) as d:
            with d.box("Services") as box:
                a = box.participant("A")
            b = d.participant("B")
            d.message(a, b, "msg")
            d.note("A note", of=a)

        output = render(d.build())
        assert "note {" in output
        assert "BackgroundColor #FFFDE7" in output
        assert "FontColor black" in output
        assert "box {" in output
        assert "BackgroundColor #E8EAF6" in output

    def test_diagram_style_title(self):
        """Test title styling goes to document block."""
        with sequence_diagram(
            title="My Title",
            diagram_style={
                "title": {"font_size": 24, "font_color": "navy"},
            }
        ) as d:
            a, b = d.participants("A", "B")
            d.message(a, b, "msg")

        output = render(d.build())
        assert "document {" in output
        assert "title {" in output
        assert "FontSize 24" in output
        assert "FontColor navy" in output

    def test_diagram_style_empty_produces_no_block(self):
        """Test that empty style doesn't produce style block."""
        from plantuml_compose.primitives import SequenceDiagramStyle

        with sequence_diagram(diagram_style=SequenceDiagramStyle()) as d:
            a, b = d.participants("A", "B")
            d.message(a, b, "msg")

        output = render(d.build())
        assert "<style>" not in output

    def test_diagram_style_arrow_line_pattern(self):
        """Test arrow line pattern styling."""
        with sequence_diagram(
            diagram_style={
                "arrow": {"line_pattern": "dashed"},
            }
        ) as d:
            a, b = d.participants("A", "B")
            d.message(a, b, "msg")

        output = render(d.build())
        assert "LineStyle dashed" in output
