import pytest

import fusion_performance
from fusion_constants import DEBUG

from fusion_performance import (
    send_program
)


class FakeMidiOutput:

    def __init__(self):

        self.messages = []

    def send(
        self,
        message
    ):

        self.messages.append(
            message
        )


class DummyOutput:

    def __init__(
        self
    ):

        self.messages = []

    def send(
        self,
        message
    ):

        self.messages.append(
            message
        )


def test_send_program():

    out = FakeMidiOutput()

    send_program(
        out,
        4,
        {
            "sf2_bank": 258,
            "sf2_program": 42
        }
    )

    assert len(
        out.messages
    ) == 3

    bank_msb = out.messages[0]

    assert bank_msb.type == (
        "control_change"
    )

    assert bank_msb.channel == 4
    assert bank_msb.control == 0
    assert bank_msb.value == 2

    bank_lsb = out.messages[1]

    assert bank_lsb.type == (
        "control_change"
    )

    assert bank_lsb.channel == 4
    assert bank_lsb.control == 32
    assert bank_lsb.value == 2

    program = out.messages[2]

    assert program.type == (
        "program_change"
    )

    assert program.channel == 4
    assert program.program == 42


def test_send_program_clamps_program_below_zero():

    out = FakeMidiOutput()

    send_program(
        out,
        0,
        {
            "sf2_bank": 0,
            "sf2_program": -1
        }
    )

    assert out.messages[
        2
    ].program == 0


def test_send_program_clamps_program_above_127():

    out = FakeMidiOutput()

    send_program(
        out,
        0,
        {
            "sf2_bank": 0,
            "sf2_program": 128
        }
    )

    assert out.messages[
        2
    ].program == 127

def test_send_program_uses_default_values():

    out = FakeMidiOutput()

    send_program(
        out,
        0,
        {}
    )

    assert out.messages[
        0
    ].value == 0

    assert out.messages[
        1
    ].value == 0

    assert out.messages[
        2
    ].program == 0


@pytest.mark.parametrize(
    (
        "mode",
        "label"
    ),
    [
        ("program", "PROGRAM"),
        ("mix", "MIX"),
        ("song", "SONG"),
        ("other", "OTHER")
    ]
)
def test_print_performance_header(
    capsys,
    mode,
    label
):

    fusion_performance.print_performance_header(
        mode,
        "2:4",
        "Test"
    )

    output = capsys.readouterr().out

    assert f"{label}: Test" in output
    assert f"Fusion {label}: 2:4" in output


def test_print_mix_unknown(
    project,
    capsys
):

    fusion_performance.print_mix(
        project,
        "99:99"
    )

    output = capsys.readouterr().out

    assert (
        "Mix inconnu : 99:99"
        in output
    )


def test_print_mix_without_channels(
    project,
    capsys
):

    project.data[
        "mixes"
    ][
        "0:0"
    ] = {
        "name": "Test Mix"
    }

    fusion_performance.print_mix(
        project,
        "0:0"
    )

    output = capsys.readouterr().out

    assert (
        "Mix : 0:0 - Test Mix"
        in output
    )


def test_print_mix_channels(
    project,
    capsys,
    monkeypatch
):

    project.data[
        "mixes"
    ][
        "0:0"
    ] = {
        "name": "Test Mix",
        "channels": {
            "10": {
                "program": "1:20"
            },
            "2": {}
        }
    }

    def resolve(
        channel
    ):

        if channel.get(
            "program"
        ) == "1:20":

            return {
                "name": "Piano"
            }

        return None

    monkeypatch.setattr(
        project,
        "resolve_mix_channel_instrument",
        resolve
    )

    fusion_performance.print_mix(
        project,
        "0:0"
    )

    output = capsys.readouterr().out

    assert "Mix : 0:0 - Test Mix" in output
    assert "PROGRAM    : 1:20" in output
    assert "Instrument : Piano" in output
    assert "PROGRAM    : ?" in output
    assert "Instrument : Non configuré" in output

    assert output.index(
        "CH 2"
    ) < output.index(
        "CH 10"
    )


def test_print_mix_instrument_without_name(
    project,
    capsys,
    monkeypatch
):

    project.data[
        "mixes"
    ][
        "0:0"
    ] = {
        "channels": {
            "1": {}
        }
    }

    monkeypatch.setattr(
        project,
        "resolve_mix_channel_instrument",
        lambda channel: {
            "sf2_bank": 0,
            "sf2_program": 0
        }
    )

    fusion_performance.print_mix(
        project,
        "0:0"
    )

    output = capsys.readouterr().out

    assert "Instrument : ?" in output

def test_load_mix_unknown(
    project,
    capsys
):

    out = DummyOutput()

    fusion_performance.load_mix(
        "0:99",
        out,
        project
    )

    output = capsys.readouterr().out

    assert "MIX inconnu: 0:99" in output

    assert out.messages == []


def test_load_mix_without_ready_channel(
    project,
    monkeypatch,
    capsys
):

    project.data["mixes"]["0:0"] = {
        "name": "Empty Mix",
        "channels": {
            "1": {}
        }
    }

    out = DummyOutput()

    saved = []

    monkeypatch.setattr(
        fusion_performance.time,
        "sleep",
        lambda delay: None
    )

    monkeypatch.setattr(
        fusion_performance,
        "panic",
        lambda output: None
    )

    monkeypatch.setattr(
        fusion_performance,
        "save_last_performance",
        lambda mode, performance_id:
            saved.append(
                (
                    mode,
                    performance_id
                )
            )
    )

    fusion_performance.state.active_notes.add(
        (0, 60)
    )

    fusion_performance.load_mix(
        "0:0",
        out,
        project
    )

    output = capsys.readouterr().out

    assert (
        "sans canal configuré pour FluidSynth"
        in output
    )

    assert (
        "Canaux actifs : aucun"
        in output
    )

    assert (
        fusion_performance.state.current_mode
        == "mix"
    )

    assert (
        fusion_performance.state.current_performance
        == "0:0"
    )

    assert (
        fusion_performance.state.current_parts
        == {}
    )

    assert not (
        fusion_performance.state.active_notes
    )

    assert saved == [
        (
            "mix",
            "0:0"
        )
    ]


def test_load_mix_ready_channel(
    project,
    monkeypatch,
    capsys
):

    project.data["instruments"]["piano"] = {
        "name": "Piano",
        "sf2_bank": 0,
        "sf2_program": 1
    }

    project.data["mixes"]["0:0"] = {
        "name": "Test Mix",
        "channels": {
            "2": {
                "instrument": "piano"
            }
        }
    }

    out = DummyOutput()

    sent = []
    saved = []

    monkeypatch.setattr(
        fusion_performance.time,
        "sleep",
        lambda delay: None
    )

    monkeypatch.setattr(
        fusion_performance,
        "panic",
        lambda output: None
    )

    monkeypatch.setattr(
        fusion_performance,
        "send_program",
        lambda output, channel, instrument:
            sent.append(
                (
                    channel,
                    instrument
                )
            )
    )

    monkeypatch.setattr(
        fusion_performance,
        "save_last_performance",
        lambda mode, performance_id:
            saved.append(
                (
                    mode,
                    performance_id
                )
            )
    )

    fusion_performance.load_mix(
        "0:0",
        out,
        project
    )

    output = capsys.readouterr().out

    assert len(sent) == 1

    assert sent[0][0] == 1

    assert sent[0][1][
        "name"
    ] == "Piano"

    assert (
        fusion_performance.state.current_parts
        == {
            2: {
                "instrument": "piano"
            }
        }
    )

    assert (
        "1 canaux chargés dans FluidSynth"
        in output
    )

    assert "CH 2 → Piano" in output

    assert saved == [
        (
            "mix",
            "0:0"
        )
    ]


def test_load_mix_ignores_unconfigured_channel(
    project,
    monkeypatch
):

    project.data["instruments"]["piano"] = {
        "name": "Piano",
        "sf2_bank": 0,
        "sf2_program": 1
    }

    project.data["mixes"]["0:0"] = {
        "name": "Partial Mix",
        "channels": {
            "1": {},
            "3": {
                "instrument": "piano"
            }
        }
    }

    out = DummyOutput()

    sent = []

    monkeypatch.setattr(
        fusion_performance.time,
        "sleep",
        lambda delay: None
    )

    monkeypatch.setattr(
        fusion_performance,
        "panic",
        lambda output: None
    )

    monkeypatch.setattr(
        fusion_performance,
        "send_program",
        lambda output, channel, instrument:
            sent.append(channel)
    )

    monkeypatch.setattr(
        fusion_performance,
        "save_last_performance",
        lambda *args: None
    )

    fusion_performance.load_mix(
        "0:0",
        out,
        project
    )

    assert sent == [
        2
    ]

    assert (
        fusion_performance.state.current_parts
        == {
            3: {
                "instrument": "piano"
            }
        }
    )


def test_load_mix_with_validation_errors(
    project,
    monkeypatch
):

    project.data["mixes"]["0:0"] = {
        "name": "Invalid Mix",
        "channels": {}
    }

    reported = []

    monkeypatch.setattr(
        project,
        "validate_mix",
        lambda mix_id: [
            "Erreur test"
        ]
    )

    monkeypatch.setattr(
        fusion_performance,
        "print_validation_errors",
        lambda project, errors, title=None:
            reported.append(
                (
                    errors,
                    title
                )
            )
    )

    monkeypatch.setattr(
        fusion_performance,
        "panic",
        lambda out: None
    )

    monkeypatch.setattr(
        fusion_performance.time,
        "sleep",
        lambda delay: None
    )

    monkeypatch.setattr(
        fusion_performance,
        "save_last_performance",
        lambda *args: None
    )

    out = DummyOutput()

    fusion_performance.load_mix(
        "0:0",
        out,
        project
    )

    assert reported == [
        (
            [
                "Erreur test"
            ],
            "Attention configuration"
        )
    ]


def test_load_program_unknown(
    project,
    capsys
):

    out = DummyOutput()

    fusion_performance.load_program(
        "0:99",
        out,
        project
    )

    output = capsys.readouterr().out

    assert "PROGRAM inconnu: 0:99" in output

    assert out.messages == []


def test_load_program_without_part(
    project,
    capsys
):

    project.data["programs"]["0:0"] = {
        "name": "Empty",
        "parts": {}
    }

    out = DummyOutput()

    fusion_performance.load_program(
        "0:0",
        out,
        project
    )

    output = capsys.readouterr().out

    assert "PROGRAM sans PART: 0:0" in output

    assert out.messages == []


def test_load_program_not_soundfont_ready(
    project,
    monkeypatch,
    capsys
):

    project.data["programs"]["0:0"] = {
        "name": "Test",
        "parts": {
            "1": {
                "midi_channel": 1
            }
        }
    }

    monkeypatch.setattr(
        project,
        "is_soundfont_ready",
        lambda part: False
    )

    out = DummyOutput()

    fusion_performance.load_program(
        "0:0",
        out,
        project
    )

    output = capsys.readouterr().out

    assert (
        "PROGRAM 0:0 non configuré pour FluidSynth."
        in output
    )

    assert out.messages == []


def test_load_program_without_resolved_instrument(
    project,
    monkeypatch,
    capsys
):

    project.data["programs"]["0:0"] = {
        "name": "Test",
        "parts": {
            "1": {
                "midi_channel": 1
            }
        }
    }

    monkeypatch.setattr(
        project,
        "is_soundfont_ready",
        lambda part: True
    )

    monkeypatch.setattr(
        project,
        "resolve_part_instrument",
        lambda part: None
    )

    out = DummyOutput()

    fusion_performance.load_program(
        "0:0",
        out,
        project
    )

    output = capsys.readouterr().out

    assert "Instrument non configuré." in output

    assert out.messages == []


def test_load_program(
    project,
    monkeypatch,
    capsys
):

    part = {
        "midi_channel": 3
    }

    instrument = {
        "name": "Piano",
        "sf2_bank": 0,
        "sf2_program": 1
    }

    project.data["programs"]["0:0"] = {
        "name": "Test Program",
        "parts": {
            "1": part
        }
    }

    monkeypatch.setattr(
        project,
        "is_soundfont_ready",
        lambda value: True
    )

    monkeypatch.setattr(
        project,
        "resolve_part_instrument",
        lambda value: instrument
    )

    monkeypatch.setattr(
        fusion_performance,
        "panic",
        lambda out: None
    )

    monkeypatch.setattr(
        fusion_performance.time,
        "sleep",
        lambda delay: None
    )

    sent = []
    saved = []

    monkeypatch.setattr(
        fusion_performance,
        "send_program",
        lambda out, channel, instrument:
            sent.append(
                (
                    channel,
                    instrument
                )
            )
    )

    monkeypatch.setattr(
        fusion_performance,
        "save_last_performance",
        lambda mode, performance_id:
            saved.append(
                (
                    mode,
                    performance_id
                )
            )
    )

    fusion_performance.state.active_notes.add(
        (
            0,
            60
        )
    )

    out = DummyOutput()

    fusion_performance.load_program(
        "0:0",
        out,
        project
    )

    output = capsys.readouterr().out

    assert (
        fusion_performance.state.current_mode
        == "program"
    )

    assert (
        fusion_performance.state.current_performance
        == "0:0"
    )

    assert (
        fusion_performance.state.current_parts
        == {
            3: part
        }
    )

    assert not (
        fusion_performance.state.pending_reload
    )

    assert not (
        fusion_performance.state.active_notes
    )

    assert sent == [
        (
            2,
            instrument
        )
    ]

    assert saved == [
        (
            "program",
            "0:0"
        )
    ]

    assert "PROGRAM: Test Program" in output
    assert "Fusion PROGRAM: 0:0" in output
    assert "Canal actif :" in output
    assert "CH 3 → Piano" in output


def test_load_song_unknown(
    project,
    capsys
):

    out = DummyOutput()

    fusion_performance.load_song(
        "Unknown",
        out,
        project
    )

    output = capsys.readouterr().out

    assert "SONG inconnue: Unknown" in output

    assert out.messages == []


def test_load_song_without_channels(
    project,
    capsys
):

    project.data["songs"]["Test"] = {
        "name": "Test Song",
        "channels": {}
    }

    out = DummyOutput()

    fusion_performance.load_song(
        "Test",
        out,
        project
    )

    output = capsys.readouterr().out

    assert "SONG sans canaux: Test" in output

    assert out.messages == []


def test_load_song(
    project,
    monkeypatch,
    capsys
):

    project.data["songs"]["Test"] = {
        "name": "Test Song",
        "channels": {
            "3": {
                "volume": 100,
                "pan": 64,
                "expression": 90,
                "reverb": 20,
                "chorus": 30
            },
            "1": {
                "volume": 80
            }
        }
    }

    out = DummyOutput()

    saved = []

    monkeypatch.setattr(
        fusion_performance,
        "panic",
        lambda out: None
    )

    monkeypatch.setattr(
        fusion_performance.time,
        "sleep",
        lambda delay: None
    )

    monkeypatch.setattr(
        fusion_performance,
        "save_last_performance",
        lambda mode, performance_id:
            saved.append(
                (
                    mode,
                    performance_id
                )
            )
    )

    fusion_performance.state.active_notes.add(
        (
            0,
            60
        )
    )

    fusion_performance.state.current_parts = {
        9: {
            "old": True
        }
    }

    fusion_performance.state.current_song_programs = {
        9: "old"
    }

    fusion_performance.state.pending_reload = True

    fusion_performance.load_song(
        "Test",
        out,
        project
    )

    output = capsys.readouterr().out

    assert (
        fusion_performance.state.current_mode
        == "song"
    )

    assert (
        fusion_performance.state.current_performance
        == "Test"
    )

    assert (
        fusion_performance.state.current_parts
        == {}
    )

    assert (
        fusion_performance.state.current_song_programs
        == {}
    )

    assert not (
        fusion_performance.state.pending_reload
    )

    assert not (
        fusion_performance.state.active_notes
    )

    assert saved == [
        (
            "song",
            "Test"
        )
    ]

    assert len(
        out.messages
    ) == 6

    assert [
        (
            message.channel,
            message.control,
            message.value
        )
        for message in out.messages
    ] == [
        (
            0,
            7,
            80
        ),
        (
            2,
            7,
            100
        ),
        (
            2,
            10,
            64
        ),
        (
            2,
            11,
            90
        ),
        (
            2,
            91,
            20
        ),
        (
            2,
            93,
            30
        )
    ]

    assert "SONG: Test Song" in output

    assert (
        "Fusion SONG: Test"
        in output
    )

    assert (
        "2 canaux SONG préparés"
        in output
    )

    assert (
        "En attente des PROGRAM_CHANGE du Fusion..."
        in output
    )


def test_load_song_program_unknown_song(
    project
):

    fusion_performance.state.current_performance = (
        "Unknown"
    )

    out = DummyOutput()

    result = (
        fusion_performance.load_song_program(
            1,
            "0:0",
            out,
            project
        )
    )

    assert result is False

    assert out.messages == []


def test_load_song_program_unknown_channel(
    project
):

    project.data["songs"]["Test"] = {
        "name": "Test",
        "channels": {}
    }

    fusion_performance.state.current_performance = (
        "Test"
    )

    out = DummyOutput()

    result = (
        fusion_performance.load_song_program(
            3,
            "0:0",
            out,
            project
        )
    )

    assert result is False

    assert out.messages == []


def test_load_song_program_unknown_program(
    project,
    monkeypatch,
    capsys
):

    monkeypatch.setattr(
        fusion_performance,
        "DEBUG",
        True
    )

    project.data["songs"]["Test"] = {
        "name": "Test",
        "channels": {
            "2": {
                "programs": {}
            }
        }
    }

    fusion_performance.state.current_performance = (
        "Test"
    )

    fusion_performance.state.current_parts = {
        2: {
            "old": True
        }
    }

    fusion_performance.state.current_song_programs = {
        2: {
            "old": True
        }
    }

    out = DummyOutput()

    result = (
        fusion_performance.load_song_program(
            2,
            "0:35",
            out,
            project
        )
    )

    assert result is False

    assert (
        2
        not in fusion_performance.state.current_parts
    )

    assert (
        2
        not in
        fusion_performance.state.current_song_programs
    )

    assert out.messages == []

    output = capsys.readouterr().out

    assert (
        "PROGRAM SONG ignoré CH 2 0:35"
        in output
    )

def test_load_song_program_instrument_not_ready(
    project,
    monkeypatch,
    capsys
):

    project.data["songs"]["Test"] = {
        "name": "Test",
        "channels": {
            "2": {
                "programs": {
                    "0:35": {}
                }
            }
        }
    }

    fusion_performance.state.current_performance = (
        "Test"
    )

    fusion_performance.state.current_parts = {
        2: {
            "old": True
        }
    }

    fusion_performance.state.current_song_programs = {
        2: {
            "old": True
        }
    }

    monkeypatch.setattr(
        project,
        "resolve_song_program_instrument",
        lambda program_id, program_data: None
    )

    monkeypatch.setattr(
        project,
        "is_instrument_soundfont_ready",
        lambda instrument: False
    )

    out = DummyOutput()

    result = (
        fusion_performance.load_song_program(
            2,
            "0:35",
            out,
            project
        )
    )

    output = capsys.readouterr().out

    assert result is False

    assert (
        "CH 2 PROGRAM 0:35 non configuré"
        in output
    )

    assert (
        2
        not in fusion_performance.state.current_parts
    )

    assert (
        2
        not in
        fusion_performance.state.current_song_programs
    )


def test_load_song_program(
    project,
    monkeypatch,
    capsys
):

    channel = {
        "programs": {
            "0:35": {}
        }
    }

    instrument = {
        "name": "Bass",
        "sf2_bank": 0,
        "sf2_program": 32
    }

    project.data["songs"]["Test"] = {
        "name": "Test",
        "channels": {
            "2": channel
        }
    }

    fusion_performance.state.current_performance = (
        "Test"
    )

    fusion_performance.state.current_parts = {}
    fusion_performance.state.current_song_programs = {}

    monkeypatch.setattr(
        project,
        "resolve_song_program_instrument",
        lambda program_id, program_data:
            instrument
    )

    monkeypatch.setattr(
        project,
        "is_instrument_soundfont_ready",
        lambda value: True
    )

    sent = []

    monkeypatch.setattr(
        fusion_performance,
        "send_program",
        lambda out, midi_channel, value:
            sent.append(
                (
                    midi_channel,
                    value
                )
            )
    )

    out = DummyOutput()

    result = (
        fusion_performance.load_song_program(
            2,
            "0:35",
            out,
            project
        )
    )

    output = capsys.readouterr().out

    assert result is True

    assert sent == [
        (
            1,
            instrument
        )
    ]

    assert (
        fusion_performance.state.current_parts
        == {
            2: channel
        }
    )

    assert (
        fusion_performance.state.current_song_programs
        == {
            2: {
                "program_id": "0:35",
                "instrument": instrument
            }
        }
    )

    assert (
        "CH 2 PROGRAM 0:35 → Bass"
        in output
    )


def test_reload_current_program(
    project,
    monkeypatch
):

    out = DummyOutput()

    fusion_performance.state.current_mode = (
        "program"
    )

    fusion_performance.state.current_performance = (
        "0:12"
    )

    calls = []

    monkeypatch.setattr(
        fusion_performance,
        "load_program",
        lambda performance_id, output, proj:
            calls.append(
                (
                    performance_id,
                    output,
                    proj
                )
            )
    )

    fusion_performance.reload_current_performance(
        out,
        project
    )

    assert calls == [
        (
            "0:12",
            out,
            project
        )
    ]


def test_reload_current_mix(
    project,
    monkeypatch
):

    out = DummyOutput()

    fusion_performance.state.current_mode = (
        "mix"
    )

    fusion_performance.state.current_performance = (
        "2:4"
    )

    calls = []

    monkeypatch.setattr(
        fusion_performance,
        "load_mix",
        lambda performance_id, output, proj:
            calls.append(
                (
                    performance_id,
                    output,
                    proj
                )
            )
    )

    fusion_performance.reload_current_performance(
        out,
        project
    )

    assert calls == [
        (
            "2:4",
            out,
            project
        )
    ]


def test_reload_current_song(
    project,
    monkeypatch
):

    out = DummyOutput()

    fusion_performance.state.current_mode = (
        "song"
    )

    fusion_performance.state.current_performance = (
        "My Song"
    )

    calls = []

    monkeypatch.setattr(
        fusion_performance,
        "load_song",
        lambda performance_id, output, proj:
            calls.append(
                (
                    performance_id,
                    output,
                    proj
                )
            )
    )

    fusion_performance.reload_current_performance(
        out,
        project
    )

    assert calls == [
        (
            "My Song",
            out,
            project
        )
    ]


