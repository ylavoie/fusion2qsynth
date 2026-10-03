import logging

import mido

import fusion_lib


class DummyOutput:

    def __init__(self):

        self.messages = []

    def send(
        self,
        message
    ):

        self.messages.append(
            message
        )


def test_log_info(
    monkeypatch
):

    messages = []

    monkeypatch.setattr(
        logging,
        "info",
        messages.append
    )

    fusion_lib.log_info(
        "test info"
    )

    assert messages == [
        "test info"
    ]


def test_log_warning(
    monkeypatch
):

    messages = []

    monkeypatch.setattr(
        logging,
        "warning",
        messages.append
    )

    fusion_lib.log_warning(
        "test warning"
    )

    assert messages == [
        "test warning"
    ]


def test_log_event(
    monkeypatch
):

    messages = []

    monkeypatch.setattr(
        logging,
        "info",
        messages.append
    )

    fusion_lib.log_event(
        "test event"
    )

    assert messages == [
        "test event"
    ]


def test_log_error(
    monkeypatch
):

    messages = []

    monkeypatch.setattr(
        logging,
        "error",
        messages.append
    )

    fusion_lib.log_error(
        "test error"
    )

    assert messages == [
        "test error"
    ]


def test_find_fusion_input(
    monkeypatch
):

    monkeypatch.setattr(
        mido,
        "get_input_names",
        lambda: [
            "Midi Through",
            "CH345:CH345 MIDI 1 20:0",
        ]
    )

    assert (
        fusion_lib.find_fusion_input()
        == "CH345:CH345 MIDI 1 20:0"
    )


def test_find_fusion_input_case_insensitive(
    monkeypatch
):

    monkeypatch.setattr(
        mido,
        "get_input_names",
        lambda: [
            "ch345:midi"
        ]
    )

    assert (
        fusion_lib.find_fusion_input()
        == "ch345:midi"
    )


def test_find_fusion_input_not_found(
    monkeypatch
):

    monkeypatch.setattr(
        mido,
        "get_input_names",
        lambda: [
            "Midi Through"
        ]
    )

    assert (
        fusion_lib.find_fusion_input()
        is None
    )


def test_find_fluidsynth_output(
    monkeypatch
):

    monkeypatch.setattr(
        mido,
        "get_output_names",
        lambda: [
            "Midi Through",
            "FLUID Synth (131):0",
        ]
    )

    assert (
        fusion_lib.find_fluidsynth_output()
        == "FLUID Synth (131):0"
    )


def test_find_fluidsynth_output_case_insensitive(
    monkeypatch
):

    monkeypatch.setattr(
        mido,
        "get_output_names",
        lambda: [
            "fluid synth"
        ]
    )

    assert (
        fusion_lib.find_fluidsynth_output()
        == "fluid synth"
    )


def test_find_fluidsynth_output_not_found(
    monkeypatch
):

    monkeypatch.setattr(
        mido,
        "get_output_names",
        lambda: [
            "Midi Through"
        ]
    )

    assert (
        fusion_lib.find_fluidsynth_output()
        is None
    )


def test_panic():

    out = DummyOutput()

    fusion_lib.panic(
        out
    )

    assert len(
        out.messages
    ) == 32

    for channel in range(16):

        all_notes_off = (
            out.messages[
                channel * 2
            ]
        )

        reset_controllers = (
            out.messages[
                channel * 2 + 1
            ]
        )

        assert (
            all_notes_off.type
            == "control_change"
        )
        assert (
            all_notes_off.channel
            == channel
        )
        assert (
            all_notes_off.control
            == 123
        )
        assert (
            all_notes_off.value
            == 0
        )

        assert (
            reset_controllers.type
            == "control_change"
        )
        assert (
            reset_controllers.channel
            == channel
        )
        assert (
            reset_controllers.control
            == 121
        )
        assert (
            reset_controllers.value
            == 0
        )


def test_note_name():

    assert fusion_lib.note_name(0) == "C-1"
    assert fusion_lib.note_name(60) == "C4"
    assert fusion_lib.note_name(61) == "C#4"
    assert fusion_lib.note_name(127) == "G9"


def test_note_number_numeric():

    assert fusion_lib.note_number("0") == 0
    assert fusion_lib.note_number("60") == 60
    assert fusion_lib.note_number("127") == 127


def test_note_number_numeric_out_of_range():

    assert fusion_lib.note_number("-1") is None
    assert fusion_lib.note_number("128") is None


def test_note_number_names():

    assert fusion_lib.note_number("C-1") == 0
    assert fusion_lib.note_number("C4") == 60
    assert fusion_lib.note_number("C#4") == 61
    assert fusion_lib.note_number("G9") == 127


def test_note_number_strips_and_ignores_case():

    assert (
        fusion_lib.note_number(
            "  c#4  "
        )
        == 61
    )


def test_note_number_invalid_name():

    assert (
        fusion_lib.note_number(
            "H4"
        )
        is None
    )


def test_note_number_invalid_octave():

    assert (
        fusion_lib.note_number(
            "CA"
        )
        is None
    )


def test_note_number_too_short():

    assert (
        fusion_lib.note_number(
            "C"
        )
        is None
    )


def test_note_number_named_out_of_range():

    assert fusion_lib.note_number("C-2") is None
    assert fusion_lib.note_number("C10") is None


def test_note_range_defaults():

    assert (
        fusion_lib.note_range()
        == "défaut (C-1) → défaut (G9)"
    )


def test_note_range_min_default():

    assert (
        fusion_lib.note_range(
            note_max=60
        )
        == "défaut (C-1) → C4"
    )


def test_note_range_max_default():

    assert (
        fusion_lib.note_range(
            note_min=60
        )
        == "C4 → défaut (G9)"
    )


def test_note_range():

    assert (
        fusion_lib.note_range(
            48,
            60
        )
        == "C3 → C4"
    )


def test_note_range_reversed():

    assert (
        fusion_lib.note_range(
            60,
            48
        )
        == "C3 → C4"
    )


def test_system_status(
    monkeypatch
):

    class DummyProject:

        def count_instruments(self):

            return 10

        def count_mixes(self):

            return 20

        def count_programs(self):

            return 30

        def count_songs(self):

            return 40

    monkeypatch.setattr(
        fusion_lib,
        "find_fusion_input",
        lambda: "Fusion"
    )

    monkeypatch.setattr(
        fusion_lib,
        "find_fluidsynth_output",
        lambda: "FluidSynth"
    )

    status = fusion_lib.system_status(
        DummyProject()
    )

    assert status == {
        "fusion": True,
        "fluidsynth": True,
        "instrument_count": 10,
        "mix_count": 20,
        "program_count": 30,
        "song_count": 40,
    }


def test_system_status_missing_midi(
    monkeypatch
):

    class DummyProject:

        def count_instruments(self):

            return 1

        def count_mixes(self):

            return 2

        def count_programs(self):

            return 3

        def count_songs(self):

            return 4

    monkeypatch.setattr(
        fusion_lib,
        "find_fusion_input",
        lambda: None
    )

    monkeypatch.setattr(
        fusion_lib,
        "find_fluidsynth_output",
        lambda: None
    )

    status = fusion_lib.system_status(
        DummyProject()
    )

    assert status["fusion"] is False
    assert status["fluidsynth"] is False
