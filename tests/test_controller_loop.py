import mido
import pytest

import fusion_controller_loop


class StopControllerLoop(Exception):
    pass


class DummyInput:

    def __init__(
        self,
        batches
    ):

        self.batches = iter(
            batches
        )

    def iter_pending(self):

        try:

            return next(
                self.batches
            )

        except StopIteration:

            raise StopControllerLoop


class DummyOutput:

    def __init__(self):

        self.messages = []

    def send(
        self,
        msg
    ):

        self.messages.append(
            msg
        )


def test_execute_pending_reload_immediate(
    project,
    monkeypatch,
    capsys
):

    out = object()

    calls = []

    monkeypatch.setattr(
        fusion_controller_loop,
        "reload_current_performance",
        lambda output, proj:
            calls.append(
                (
                    output,
                    proj
                )
            )
    )

    fusion_controller_loop.state.pending_reload = True
    fusion_controller_loop.state.reload_wait_announced = True

    fusion_controller_loop.execute_pending_reload(
        out,
        project
    )

    output = capsys.readouterr().out

    assert (
        "Projet modifié : reload immédiat."
        in output
    )

    assert calls == [
        (
            out,
            project
        )
    ]

    assert (
        fusion_controller_loop.state.pending_reload
        is False
    )

    assert (
        fusion_controller_loop.state.reload_wait_announced
        is False
    )


def test_execute_pending_reload_deferred(
    project,
    monkeypatch,
    capsys
):

    out = object()

    calls = []

    monkeypatch.setattr(
        fusion_controller_loop,
        "reload_current_performance",
        lambda output, proj:
            calls.append(
                (
                    output,
                    proj
                )
            )
    )

    fusion_controller_loop.state.pending_reload = True
    fusion_controller_loop.state.reload_wait_announced = True

    fusion_controller_loop.execute_pending_reload(
        out,
        project,
        deferred=True
    )

    output = capsys.readouterr().out

    assert (
        "Notes relâchées : reload différé."
        in output
    )

    assert calls == [
        (
            out,
            project
        )
    ]

    assert (
        fusion_controller_loop.state.pending_reload
        is False
    )

    assert (
        fusion_controller_loop.state.reload_wait_announced
        is False
    )


def test_controller_forwards_note_on_on_active_channel(
    project,
    monkeypatch
):

    out = DummyOutput()

    msg = mido.Message(
        "note_on",
        channel=0,
        note=60,
        velocity=100
    )

    inp = DummyInput(
        [
            [msg]
        ]
    )

    fusion_controller_loop.state.current_parts = {
        1: {}
    }

    fusion_controller_loop.state.active_notes.clear()
    fusion_controller_loop.state.pending_reload = False
    fusion_controller_loop.state.reload_wait_announced = False

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    with pytest.raises(
        StopControllerLoop
    ):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "program"
        )

    assert out.messages == [
        msg
    ]

    assert (
        0,
        60
    ) in fusion_controller_loop.state.active_notes


def test_controller_forwards_note_off_and_clears_active_note(
    project,
    monkeypatch
):

    out = DummyOutput()

    msg = mido.Message(
        "note_off",
        channel=0,
        note=60,
        velocity=0
    )

    inp = DummyInput(
        [
            [msg]
        ]
    )

    fusion_controller_loop.state.current_parts = {
        1: {}
    }

    fusion_controller_loop.state.active_notes = {
        (
            0,
            60
        )
    }

    fusion_controller_loop.state.pending_reload = False
    fusion_controller_loop.state.reload_wait_announced = False

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    with pytest.raises(
        StopControllerLoop
    ):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "program"
        )

    assert out.messages == [
        msg
    ]

    assert (
        0,
        60
    ) not in fusion_controller_loop.state.active_notes


def test_controller_ignores_note_on_on_inactive_channel(
    project,
    monkeypatch
):

    out = DummyOutput()

    msg = mido.Message(
        "note_on",
        channel=1,
        note=60,
        velocity=100
    )

    inp = DummyInput(
        [
            [msg]
        ]
    )

    fusion_controller_loop.state.current_parts = {
        1: {}
    }

    fusion_controller_loop.state.active_notes.clear()
    fusion_controller_loop.state.pending_reload = False
    fusion_controller_loop.state.reload_wait_announced = False

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    with pytest.raises(
        StopControllerLoop
    ):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "program"
        )

    assert out.messages == []

    assert (
        1,
        60
    ) not in fusion_controller_loop.state.active_notes


def test_controller_ignores_unknown_note_off_on_inactive_channel(
    project,
    monkeypatch
):

    out = DummyOutput()

    msg = mido.Message(
        "note_off",
        channel=1,
        note=60,
        velocity=0
    )

    inp = DummyInput(
        [
            [msg]
        ]
    )

    fusion_controller_loop.state.current_parts = {
        1: {}
    }

    fusion_controller_loop.state.active_notes.clear()
    fusion_controller_loop.state.pending_reload = False
    fusion_controller_loop.state.reload_wait_announced = False

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    with pytest.raises(
        StopControllerLoop
    ):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "program"
        )

    assert out.messages == []

    assert (
        1,
        60
    ) not in fusion_controller_loop.state.active_notes


def test_controller_forwards_note_off_for_previously_active_note(
    project,
    monkeypatch
):

    out = DummyOutput()

    msg = mido.Message(
        "note_off",
        channel=1,
        note=60,
        velocity=0
    )

    inp = DummyInput(
        [
            [msg]
        ]
    )

    fusion_controller_loop.state.current_parts = {}

    fusion_controller_loop.state.active_notes = {
        (
            1,
            60
        )
    }

    fusion_controller_loop.state.pending_reload = False
    fusion_controller_loop.state.reload_wait_announced = False

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    with pytest.raises(
        StopControllerLoop
    ):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "program"
        )

    assert out.messages == [
        msg
    ]

    assert (
        1,
        60
    ) not in fusion_controller_loop.state.active_notes


def test_controller_treats_zero_velocity_note_on_as_note_off(
    project,
    monkeypatch
):

    out = DummyOutput()

    msg = mido.Message(
        "note_on",
        channel=0,
        note=60,
        velocity=0
    )

    inp = DummyInput(
        [
            [msg]
        ]
    )

    fusion_controller_loop.state.current_parts = {
        1: {}
    }

    fusion_controller_loop.state.active_notes = {
        (
            0,
            60
        )
    }

    fusion_controller_loop.state.pending_reload = False
    fusion_controller_loop.state.reload_wait_announced = False

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    with pytest.raises(
        StopControllerLoop
    ):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "program"
        )

    assert out.messages == [
        msg
    ]

    assert (
        0,
        60
    ) not in fusion_controller_loop.state.active_notes


def test_controller_reloads_immediately_when_project_changes_at_rest(
    project,
    monkeypatch
):

    out = DummyOutput()
    inp = DummyInput([])

    fusion_controller_loop.state.current_parts = {}
    fusion_controller_loop.state.active_notes.clear()
    fusion_controller_loop.state.pending_reload = False
    fusion_controller_loop.state.reload_wait_announced = True

    reload_calls = []

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: True
    )

    monkeypatch.setattr(
        fusion_controller_loop,
        "execute_pending_reload",
        lambda output, proj, deferred=False:
            reload_calls.append(
                (
                    output,
                    proj,
                    deferred
                )
            )
    )

    with pytest.raises(
        StopControllerLoop
    ):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "program"
        )

    assert reload_calls == [
        (
            out,
            project,
            False
        )
    ]

    assert (
        fusion_controller_loop.state.pending_reload
        is True
    )

    assert (
        fusion_controller_loop.state.reload_wait_announced
        is False
    )


def test_controller_defers_reload_while_note_is_active(
    project,
    monkeypatch,
    capsys
):

    out = DummyOutput()
    inp = DummyInput([])

    fusion_controller_loop.state.current_parts = {
        1: {}
    }

    fusion_controller_loop.state.active_notes = {
        (
            0,
            60
        )
    }

    fusion_controller_loop.state.pending_reload = False
    fusion_controller_loop.state.reload_wait_announced = False

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: True
    )

    with pytest.raises(
        StopControllerLoop
    ):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "program"
        )

    output = capsys.readouterr().out

    assert (
        fusion_controller_loop.state.pending_reload
        is True
    )

    assert (
        fusion_controller_loop.state.reload_wait_announced
        is False
    )


def test_controller_announces_pending_reload_with_active_notes(
    project,
    monkeypatch,
    capsys
):

    out = DummyOutput()

    msg = mido.Message(
        "note_on",
        channel=0,
        note=61,
        velocity=100
    )

    inp = DummyInput(
        [
            [msg]
        ]
    )

    fusion_controller_loop.state.current_parts = {
        1: {}
    }

    #
    # Une note est déjà tenue au moment où
    # la modification du projet est détectée.
    #
    fusion_controller_loop.state.active_notes = {
        (
            0,
            60
        )
    }

    fusion_controller_loop.state.pending_reload = False
    fusion_controller_loop.state.reload_wait_announced = False

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: True
    )

    with pytest.raises(
        StopControllerLoop
    ):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "program"
        )

    output = capsys.readouterr().out

    assert (
        "Projet modifié : reload en attente "
        "(notes actives)."
        in output
    )

    assert (
        fusion_controller_loop.state.pending_reload
        is True
    )

    assert (
        fusion_controller_loop.state.reload_wait_announced
        is True
    )

    assert (
        (
            0,
            60
        )
        in fusion_controller_loop.state.active_notes
    )

    assert (
        (
            0,
            61
        )
        in fusion_controller_loop.state.active_notes
    )

    assert out.messages == [
        msg
    ]


def test_controller_executes_deferred_reload_after_last_note_off(
    project,
    monkeypatch
):

    events = []

    class OrderedOutput:

        def send(
            self,
            msg
        ):

            events.append(
                (
                    "send",
                    msg
                )
            )

    out = OrderedOutput()

    msg = mido.Message(
        "note_off",
        channel=0,
        note=60,
        velocity=0
    )

    inp = DummyInput(
        [
            [msg]
        ]
    )

    fusion_controller_loop.state.current_parts = {
        1: {}
    }

    fusion_controller_loop.state.active_notes = {
        (
            0,
            60
        )
    }

    fusion_controller_loop.state.pending_reload = True
    fusion_controller_loop.state.reload_wait_announced = True

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    def fake_execute(
        output,
        proj,
        deferred=False
    ):

        events.append(
            (
                "reload",
                deferred
            )
        )

        #
        # Effets de execute_pending_reload()
        #
        fusion_controller_loop.state.pending_reload = False
        fusion_controller_loop.state.reload_wait_announced = False

    monkeypatch.setattr(
        fusion_controller_loop,
        "execute_pending_reload",
        fake_execute
    )

    with pytest.raises(
        StopControllerLoop
    ):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "program"
        )

    assert events == [
        (
            "send",
            msg
        ),
        (
            "reload",
            True
        )
    ]

    assert not fusion_controller_loop.state.active_notes

    assert (
        fusion_controller_loop.state.pending_reload
        is False
    )

    assert (
        fusion_controller_loop.state.reload_wait_announced
        is False
    )


def test_controller_detects_song_change(
    project,
    monkeypatch,
    capsys
):

    msg = mido.Message(
        "song_select",
        song=0
    )

    inp = DummyInput(
        [
            [msg]
        ]
    )

    out = DummyOutput()

    fusion_controller_loop.state.current_performance = (
        "My Song"
    )

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    result = (
        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "song",
            selected_song="My Song"
        )
    )

    output = capsys.readouterr().out

    assert result == "song_change"

    assert (
        "Changement de SONG détecté."
        in output
    )

    assert out.messages == []


def test_controller_ignores_initial_song_select(
    project,
    monkeypatch
):

    msg = mido.Message(
        "song_select",
        song=0
    )

    inp = DummyInput(
        [
            [msg]
        ]
    )

    out = DummyOutput()

    fusion_controller_loop.state.current_performance = None

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    with pytest.raises(
        StopControllerLoop
    ):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "song",
            selected_song="My Song"
        )

    assert out.messages == []


def test_controller_debug_program_note_on(
    project,
    monkeypatch,
    capsys
):

    msg = mido.Message(
        "note_on",
        channel=0,
        note=60,
        velocity=100
    )

    inp = DummyInput(
        [
            [msg]
        ]
    )

    out = DummyOutput()

    part = {
        "midi_channel": 1
    }

    fusion_controller_loop.state.current_parts = {
        1: part
    }

    fusion_controller_loop.state.active_notes.clear()
    fusion_controller_loop.state.pending_reload = False
    fusion_controller_loop.state.reload_wait_announced = False

    monkeypatch.setattr(
        fusion_controller_loop,
        "DEBUG",
        True
    )

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    monkeypatch.setattr(
        project,
        "resolve_part_instrument",
        lambda value: {
            "name": "Test Piano"
        }
    )

    with pytest.raises(
        StopControllerLoop
    ):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "program"
        )

    output = capsys.readouterr().out

    assert (
        "NOTE ON CH 1 Test Piano Note C4 Vel 100"
        in output
    )

    assert out.messages == [
        msg
    ]


def test_controller_debug_mix_note_on(
    project,
    monkeypatch,
    capsys
):

    msg = mido.Message(
        "note_on",
        channel=0,
        note=60,
        velocity=100
    )

    inp = DummyInput(
        [
            [msg]
        ]
    )

    out = DummyOutput()

    channel = {
        "midi_channel": 1
    }

    fusion_controller_loop.state.current_parts = {
        1: channel
    }

    fusion_controller_loop.state.active_notes.clear()
    fusion_controller_loop.state.pending_reload = False
    fusion_controller_loop.state.reload_wait_announced = False

    monkeypatch.setattr(
        fusion_controller_loop,
        "DEBUG",
        True
    )

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    monkeypatch.setattr(
        project,
        "resolve_mix_channel_instrument",
        lambda value: {
            "name": "Test Strings"
        }
    )

    with pytest.raises(
        StopControllerLoop
    ):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "mix"
        )

    output = capsys.readouterr().out

    assert (
        "NOTE ON CH 1 Test Strings Note C4 Vel 100"
        in output
    )

    assert out.messages == [
        msg
    ]


def test_controller_debug_song_note_on(
    project,
    monkeypatch,
    capsys
):

    msg = mido.Message(
        "note_on",
        channel=0,
        note=60,
        velocity=100
    )

    inp = DummyInput(
        [
            [msg]
        ]
    )

    out = DummyOutput()

    fusion_controller_loop.state.current_parts = {
        1: {}
    }

    fusion_controller_loop.state.current_song_programs = {
        1: {
            "program_id": "0:1",
            "instrument": {
                "name": "Test Violin"
            }
        }
    }

    fusion_controller_loop.state.active_notes.clear()
    fusion_controller_loop.state.pending_reload = False
    fusion_controller_loop.state.reload_wait_announced = False

    monkeypatch.setattr(
        fusion_controller_loop,
        "DEBUG",
        True
    )

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    with pytest.raises(
        StopControllerLoop
    ):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "song"
        )

    output = capsys.readouterr().out

    assert (
        "NOTE ON CH 1 Test Violin Note C4 Vel 100"
        in output
    )

    assert out.messages == [
        msg
    ]


def test_controller_debug_note_off(
    project,
    monkeypatch,
    capsys
):

    msg = mido.Message(
        "note_off",
        channel=0,
        note=60,
        velocity=0
    )

    inp = DummyInput(
        [
            [msg]
        ]
    )

    out = DummyOutput()

    part = {
        "midi_channel": 1
    }

    fusion_controller_loop.state.current_parts = {
        1: part
    }

    fusion_controller_loop.state.active_notes = {
        (
            0,
            60
        )
    }

    fusion_controller_loop.state.pending_reload = False
    fusion_controller_loop.state.reload_wait_announced = False

    monkeypatch.setattr(
        fusion_controller_loop,
        "DEBUG",
        True
    )

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    monkeypatch.setattr(
        project,
        "resolve_part_instrument",
        lambda value: {
            "name": "Test Piano"
        }
    )

    with pytest.raises(
        StopControllerLoop
    ):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "program"
        )

    output = capsys.readouterr().out

    assert (
        "NOTE OFF CH 1 Test Piano Note C4"
        in output
    )

    assert out.messages == [
        msg
    ]

    assert not fusion_controller_loop.state.active_notes


@pytest.mark.parametrize(
    "msg",
    [
        mido.Message(
            "pitchwheel",
            channel=0,
            pitch=1000
        ),
        mido.Message(
            "aftertouch",
            channel=0,
            value=64
        ),
        mido.Message(
            "polytouch",
            channel=0,
            note=60,
            value=64
        ),
    ]
)
def test_controller_forwards_expression_messages_on_active_channel(
    project,
    monkeypatch,
    msg
):

    inp = DummyInput(
        [
            [msg]
        ]
    )

    out = DummyOutput()

    fusion_controller_loop.state.current_parts = {
        1: {}
    }

    fusion_controller_loop.state.active_notes.clear()
    fusion_controller_loop.state.pending_reload = False
    fusion_controller_loop.state.reload_wait_announced = False

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    with pytest.raises(
        StopControllerLoop
    ):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "program"
        )

    assert out.messages == [
        msg
    ]


@pytest.mark.parametrize(
    "msg",
    [
        mido.Message(
            "pitchwheel",
            channel=0,
            pitch=1000
        ),
        mido.Message(
            "aftertouch",
            channel=0,
            value=64
        ),
        mido.Message(
            "polytouch",
            channel=0,
            note=60,
            value=64
        ),
    ]
)
def test_controller_ignores_expression_messages_on_inactive_channel(
    project,
    monkeypatch,
    msg
):

    inp = DummyInput(
        [
            [msg]
        ]
    )

    out = DummyOutput()

    fusion_controller_loop.state.current_parts = {}

    fusion_controller_loop.state.active_notes.clear()
    fusion_controller_loop.state.pending_reload = False
    fusion_controller_loop.state.reload_wait_announced = False

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    with pytest.raises(
        StopControllerLoop
    ):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "program"
        )

    assert out.messages == []


def test_controller_program_cc0_sets_bank(
    project,
    monkeypatch
):

    messages = [
        mido.Message(
            "control_change",
            channel=fusion_controller_loop.fusion_default_channel,
            control=0,
            value=8
        ),
        mido.Message(
            "program_change",
            channel=fusion_controller_loop.fusion_default_channel,
            program=12
        ),
    ]

    inp = DummyInput(
        [
            messages
        ]
    )

    out = DummyOutput()

    fusion_controller_loop.state.current_performance = None
    fusion_controller_loop.state.current_parts = {}
    fusion_controller_loop.state.active_notes.clear()
    fusion_controller_loop.state.pending_reload = False
    fusion_controller_loop.state.reload_wait_announced = False

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    loaded = []

    monkeypatch.setattr(
        fusion_controller_loop,
        "load_program",
        lambda performance_id, output, proj:
            loaded.append(performance_id)
    )

    with pytest.raises(
        StopControllerLoop
    ):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "program"
        )

    assert loaded == [
        "8:12"
    ]

    assert out.messages == []


@pytest.mark.parametrize(
    "control",
    [
        0,
        32
    ]
)
def test_controller_filters_part_bank_select(
    project,
    monkeypatch,
    control
):

    msg = mido.Message(
        "control_change",
        channel=1,
        control=control,
        value=42
    )

    inp = DummyInput(
        [
            [msg]
        ]
    )

    out = DummyOutput()

    fusion_controller_loop.state.current_parts = {
        2: {}
    }

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    with pytest.raises(
        StopControllerLoop
    ):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "program"
        )

    assert out.messages == []


def test_controller_ignores_control_change_on_inactive_channel(
    project,
    monkeypatch
):

    msg = mido.Message(
        "control_change",
        channel=1,
        control=7,
        value=100
    )

    inp = DummyInput(
        [
            [msg]
        ]
    )

    out = DummyOutput()

    fusion_controller_loop.state.current_parts = {}

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    with pytest.raises(
        StopControllerLoop
    ):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "program"
        )

    assert out.messages == []


def test_controller_forwards_control_change_on_active_channel(
    project,
    monkeypatch
):

    msg = mido.Message(
        "control_change",
        channel=1,
        control=7,
        value=100
    )

    inp = DummyInput(
        [
            [msg]
        ]
    )

    out = DummyOutput()

    fusion_controller_loop.state.current_parts = {
        2: {}
    }

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    with pytest.raises(
        StopControllerLoop
    ):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "program"
        )

    assert out.messages == [
        msg
    ]


def test_controller_song_bank_and_program_change(
    project,
    monkeypatch
):

    messages = [
        mido.Message(
            "control_change",
            channel=2,
            control=0,
            value=8
        ),
        mido.Message(
            "program_change",
            channel=2,
            program=12
        ),
    ]

    inp = DummyInput(
        [
            messages
        ]
    )

    out = DummyOutput()

    fusion_controller_loop.state.current_parts = {}
    fusion_controller_loop.state.active_notes.clear()
    fusion_controller_loop.state.pending_reload = False
    fusion_controller_loop.state.reload_wait_announced = False

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    loaded = []

    monkeypatch.setattr(
        fusion_controller_loop,
        "load_song_program",
        lambda channel_id, program_id, output, proj:
            loaded.append(
                (
                    channel_id,
                    program_id
                )
            )
    )

    with pytest.raises(
        StopControllerLoop
    ):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "song",
            selected_song="Test Song"
        )

    assert loaded == [
        (
            3,
            "8:12"
        )
    ]

    assert out.messages == []


def test_controller_song_filters_cc32(
    project,
    monkeypatch
):

    msg = mido.Message(
        "control_change",
        channel=2,
        control=32,
        value=10
    )

    inp = DummyInput(
        [
            [msg]
        ]
    )

    out = DummyOutput()

    fusion_controller_loop.state.current_parts = {
        3: {}
    }

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    with pytest.raises(
        StopControllerLoop
    ):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "song"
        )

    assert out.messages == []


def test_controller_song_ignores_cc_without_resolved_program(
    project,
    monkeypatch
):

    msg = mido.Message(
        "control_change",
        channel=2,
        control=7,
        value=100
    )

    inp = DummyInput(
        [
            [msg]
        ]
    )

    out = DummyOutput()

    fusion_controller_loop.state.current_parts = {}

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    with pytest.raises(
        StopControllerLoop
    ):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "song"
        )

    assert out.messages == []


def test_controller_song_forwards_cc_with_resolved_program(
    project,
    monkeypatch
):

    msg = mido.Message(
        "control_change",
        channel=2,
        control=7,
        value=100
    )

    inp = DummyInput(
        [
            [msg]
        ]
    )

    out = DummyOutput()

    fusion_controller_loop.state.current_parts = {
        3: {}
    }

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    with pytest.raises(
        StopControllerLoop
    ):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "song"
        )

    assert out.messages == [
        msg
    ]


def test_controller_ignores_program_change_on_non_default_channel(
    project,
    monkeypatch
):

    msg = mido.Message(
        "program_change",
        channel=1,
        program=12
    )

    inp = DummyInput([[msg]])
    out = DummyOutput()

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    with pytest.raises(StopControllerLoop):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "program"
        )

    assert out.messages == []


def test_controller_ignores_program_change_without_bank(
    project,
    monkeypatch
):

    msg = mido.Message(
        "program_change",
        channel=fusion_controller_loop.fusion_default_channel,
        program=12
    )

    inp = DummyInput([[msg]])
    out = DummyOutput()

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    with pytest.raises(StopControllerLoop):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "program"
        )

    assert out.messages == []


def test_controller_loads_detected_mix(
    project,
    monkeypatch
):

    messages = [
        mido.Message(
            "control_change",
            channel=fusion_controller_loop.fusion_default_channel,
            control=0,
            value=2
        ),
        mido.Message(
            "program_change",
            channel=fusion_controller_loop.fusion_default_channel,
            program=4
        ),
    ]

    inp = DummyInput([messages])
    out = DummyOutput()

    fusion_controller_loop.state.current_performance = None

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    monkeypatch.setattr(
        project,
        "get_mix_bank_name",
        lambda bank: "Test MIX Bank"
    )

    loaded = []

    monkeypatch.setattr(
        fusion_controller_loop,
        "load_mix",
        lambda performance_id, output, proj:
            loaded.append(performance_id)
    )

    with pytest.raises(StopControllerLoop):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "mix"
        )

    assert loaded == [
        "2:4"
    ]


def test_controller_loads_detected_mix(
    project,
    monkeypatch
):

    messages = [
        mido.Message(
            "control_change",
            channel=fusion_controller_loop.fusion_default_channel,
            control=0,
            value=2
        ),
        mido.Message(
            "program_change",
            channel=fusion_controller_loop.fusion_default_channel,
            program=4
        ),
    ]

    inp = DummyInput([messages])
    out = DummyOutput()

    fusion_controller_loop.state.current_performance = None

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    monkeypatch.setattr(
        project,
        "get_mix_bank_name",
        lambda bank: "Test MIX Bank"
    )

    loaded = []

    monkeypatch.setattr(
        fusion_controller_loop,
        "load_mix",
        lambda performance_id, output, proj:
            loaded.append(performance_id)
    )

    with pytest.raises(StopControllerLoop):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "mix"
        )

    assert loaded == [
        "2:4"
    ]


def test_controller_start_loads_selected_song(
    project,
    monkeypatch
):

    msg = mido.Message(
        "start"
    )

    inp = DummyInput([[msg]])
    out = DummyOutput()

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    loaded = []

    monkeypatch.setattr(
        fusion_controller_loop,
        "load_song",
        lambda song_id, output, proj:
            loaded.append(song_id)
    )

    with pytest.raises(StopControllerLoop):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "song",
            selected_song="Test Song"
        )

    assert loaded == [
        "Test Song"
    ]


def test_controller_ignores_current_performance(
    project,
    monkeypatch
):

    messages = [
        mido.Message(
            "control_change",
            channel=fusion_controller_loop.fusion_default_channel,
            control=0,
            value=2
        ),
        mido.Message(
            "program_change",
            channel=fusion_controller_loop.fusion_default_channel,
            program=4
        ),
    ]

    inp = DummyInput(
        [
            messages,
            []
        ]
    )

    out = DummyOutput()

    fusion_controller_loop.state.current_performance = "2:4"
    fusion_controller_loop.state.current_parts = {}
    fusion_controller_loop.state.active_notes.clear()
    fusion_controller_loop.state.pending_reload = False
    fusion_controller_loop.state.reload_wait_announced = False

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    loaded = []

    monkeypatch.setattr(
        fusion_controller_loop,
        "load_program",
        lambda *args:
            loaded.append(args)
    )

    with pytest.raises(
        StopControllerLoop
    ):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "program"
        )

    assert loaded == []

    assert (
        fusion_controller_loop.state.current_performance
        == "2:4"
    )


def test_controller_debug_song_select(
    project,
    monkeypatch,
    capsys
):

    msg = mido.Message(
        "song_select",
        song=0
    )

    inp = DummyInput([[msg]])
    out = DummyOutput()

    fusion_controller_loop.state.current_performance = "Test Song"

    monkeypatch.setattr(
        fusion_controller_loop,
        "DEBUG",
        True
    )

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    result = fusion_controller_loop.run_controller_loop(
        inp,
        out,
        project,
        "song",
        selected_song="Test Song"
    )

    output = capsys.readouterr().out

    assert "SONG SELECT reçu : 0" in output
    assert result == "song_change"


def test_controller_debug_ignored_note_on(
    project,
    monkeypatch,
    capsys
):

    msg = mido.Message(
        "note_on",
        channel=0,
        note=60,
        velocity=100
    )

    inp = DummyInput([[msg]])
    out = DummyOutput()

    fusion_controller_loop.state.current_parts = {}
    fusion_controller_loop.state.active_notes.clear()

    monkeypatch.setattr(
        fusion_controller_loop,
        "DEBUG",
        True
    )

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    with pytest.raises(StopControllerLoop):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "program"
        )

    output = capsys.readouterr().out

    assert "NOTE ignorée CH 1 C4" in output
    assert out.messages == []


def test_controller_debug_ignored_note_off(
    project,
    monkeypatch,
    capsys
):

    msg = mido.Message(
        "note_off",
        channel=0,
        note=60,
        velocity=0
    )

    inp = DummyInput([[msg]])
    out = DummyOutput()

    fusion_controller_loop.state.current_parts = {}
    fusion_controller_loop.state.active_notes.clear()

    monkeypatch.setattr(
        fusion_controller_loop,
        "DEBUG",
        True
    )

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    with pytest.raises(StopControllerLoop):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "program"
        )

    output = capsys.readouterr().out

    assert "NOTE OFF ignorée CH 1 C4" in output
    assert out.messages == []


def test_controller_debug_ignored_control_change(
    project,
    monkeypatch,
    capsys
):

    msg = mido.Message(
        "control_change",
        channel=1,
        control=7,
        value=100
    )

    inp = DummyInput([[msg]])
    out = DummyOutput()

    fusion_controller_loop.state.current_parts = {}

    monkeypatch.setattr(
        fusion_controller_loop,
        "DEBUG",
        True
    )

    monkeypatch.setattr(
        project,
        "reload_if_changed",
        lambda: False
    )

    with pytest.raises(StopControllerLoop):

        fusion_controller_loop.run_controller_loop(
            inp,
            out,
            project,
            "program"
        )

    output = capsys.readouterr().out

    assert "CC ignoré CH 2 CC 7 Value 100" in output
    assert out.messages == []
