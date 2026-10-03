import pytest

import fusion_monitor


class DummyInput:

    def __init__(
        self,
        messages
    ):

        self.messages = messages

    def __enter__(self):

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback
    ):

        return False

    def __iter__(self):

        return iter(
            self.messages
        )


def make_message(
    message_type,
    **kwargs
):

    class Message:

        type = message_type

    message = Message()

    for name, value in kwargs.items():

        setattr(
            message,
            name,
            value
        )

    return message


def test_main_missing_fusion(
    monkeypatch
):

    monkeypatch.setattr(
        fusion_monitor,
        "find_fusion_input",
        lambda: None
    )

    with pytest.raises(
        Exception,
        match="Fusion MIDI introuvable"
    ):

        fusion_monitor.main()


@pytest.mark.parametrize(
    (
        "message",
        "expected"
    ),
    [
        (
            make_message(
                "note_on",
                channel=0,
                note=60,
                velocity=100
            ),
            "NOTE ON"
        ),
        (
            make_message(
                "note_off",
                channel=1,
                note=61,
                velocity=64
            ),
            "NOTE OFF"
        ),
        (
            make_message(
                "program_change",
                channel=2,
                program=42
            ),
            "PROGRAM"
        ),
        (
            make_message(
                "pitchwheel",
                channel=3,
                pitch=123
            ),
            "PITCHWHEEL"
        ),
        (
            make_message(
                "aftertouch",
                channel=4,
                value=75
            ),
            "AFTERTOUCH"
        ),
        (
            make_message(
                "polytouch",
                channel=5,
                note=62,
                value=80
            ),
            "POLYTOUCH"
        ),
        (
            make_message(
                "sysex",
                data=(
                    1,
                    2,
                    3
                )
            ),
            "SYSEX"
        ),
        (
            make_message(
                "quarter_frame",
                frame_type=2,
                frame_value=7
            ),
            "QUARTER FRAME"
        ),
        (
            make_message(
                "songpos",
                pos=1234
            ),
            "SONG POSITION"
        ),
        (
            make_message(
                "song_select",
                song=12
            ),
            "SONG SELECT"
        ),
        (
            make_message(
                "tune_request"
            ),
            "TUNE REQUEST"
        ),
        (
            make_message(
                "clock"
            ),
            "CLOCK"
        ),
        (
            make_message(
                "start"
            ),
            "START"
        ),
        (
            make_message(
                "continue"
            ),
            "CONTINUE"
        ),
        (
            make_message(
                "stop"
            ),
            "STOP"
        ),
        (
            make_message(
                "active_sensing"
            ),
            "ACTIVE SENSING"
        ),
        (
            make_message(
                "reset"
            ),
            "RESET"
        ),
    ]
)
def test_main_message_types(
    monkeypatch,
    capsys,
    message,
    expected
):

    monkeypatch.setattr(
        fusion_monitor,
        "find_fusion_input",
        lambda:
            "Fusion MIDI"
    )

    monkeypatch.setattr(
        fusion_monitor.mido,
        "open_input",
        lambda port:
            DummyInput(
                [
                    message
                ]
            )
    )

    monkeypatch.setattr(
        fusion_monitor.time,
        "monotonic",
        lambda: 10.0
    )

    fusion_monitor.main()

    output = (
        capsys.readouterr().out
    )

    assert (
        "Monitoring : Fusion MIDI"
        in output
    )

    assert expected in output


@pytest.mark.parametrize(
    (
        "control",
        "expected"
    ),
    [
        (
            64,
            "Sustain"
        ),
        (
            3,
            "Undefined"
        ),
    ]
)
def test_main_control_change(
    monkeypatch,
    capsys,
    control,
    expected
):

    message = make_message(
        "control_change",
        channel=0,
        control=control,
        value=100
    )

    monkeypatch.setattr(
        fusion_monitor,
        "find_fusion_input",
        lambda:
            "Fusion MIDI"
    )

    monkeypatch.setattr(
        fusion_monitor.mido,
        "open_input",
        lambda port:
            DummyInput(
                [
                    message
                ]
            )
    )

    monkeypatch.setattr(
        fusion_monitor.time,
        "monotonic",
        lambda: 10.0
    )

    fusion_monitor.main()

    output = (
        capsys.readouterr().out
    )

    assert "CONTROL" in output
    assert expected in output


def test_main_unknown_message(
    monkeypatch,
    capsys
):

    message = make_message(
        "unknown"
    )

    monkeypatch.setattr(
        fusion_monitor,
        "find_fusion_input",
        lambda:
            "Fusion MIDI"
    )

    monkeypatch.setattr(
        fusion_monitor.mido,
        "open_input",
        lambda port:
            DummyInput(
                [
                    message
                ]
            )
    )

    monkeypatch.setattr(
        fusion_monitor.time,
        "monotonic",
        lambda: 10.0
    )

    fusion_monitor.main()

    assert (
        "UNKNOWN"
        in capsys.readouterr().out
    )


def test_main_keyboard_interrupt(
    monkeypatch,
    capsys
):

    class InterruptInput:

        def __enter__(self):

            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback
        ):

            return False

        def __iter__(self):

            return self

        def __next__(self):

            raise KeyboardInterrupt

    monkeypatch.setattr(
        fusion_monitor,
        "find_fusion_input",
        lambda:
            "Fusion MIDI"
    )

    monkeypatch.setattr(
        fusion_monitor.mido,
        "open_input",
        lambda port:
            InterruptInput()
    )

    monkeypatch.setattr(
        fusion_monitor.time,
        "monotonic",
        lambda: 10.0
    )

    fusion_monitor.main()

    assert (
        "Retour au menu"
        in capsys.readouterr().out
    )
