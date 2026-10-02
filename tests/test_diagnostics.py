#
# get_program_diagnostic()
#

def add_instrument(
    project,
    instrument_id="piano",
    sf2_bank=0,
    sf2_program=0
):

    project.data[
        "instruments"
    ][
        instrument_id
    ] = {
        "name": "Piano",
        "sf2_bank": sf2_bank,
        "sf2_program": sf2_program
    }


def add_program(
    project,
    program_id="0:0",
    name="PROGRAM test",
    instrument="piano"
):

    bank, program = (
        int(value)
        for value in program_id.split(
            ":"
        )
    )

    part = {
        "bank": bank,
        "program": program,
        "midi_channel": 1
    }

    if instrument is not None:

        part[
            "instrument"
        ] = instrument

    project.data[
        "programs"
    ][
        program_id
    ] = {
        "name": name,
        "parts": {
            "1": part
        }
    }


def test_program_diagnostic_valid_and_configured(
    project
):

    add_instrument(
        project
    )

    add_program(
        project
    )

    assert project.get_program_diagnostic() == [
        {
            "program": "0:0",
            "name": "PROGRAM test",
            "fusion_valid": True,
            "qsynth_configured": True,
            "errors": []
        }
    ]


def test_program_diagnostic_valid_but_not_configured(
    project
):

    add_program(
        project,
        instrument=None
    )

    result = project.get_program_diagnostic()

    assert result[0][
        "fusion_valid"
    ] is True

    assert result[0][
        "qsynth_configured"
    ] is False

    assert result[0][
        "errors"
    ] == []


def test_program_diagnostic_invalid_but_configured(
    project
):

    add_instrument(
        project
    )

    add_program(
        project
    )

    project.data[
        "programs"
    ][
        "0:0"
    ][
        "unexpected"
    ] = True

    result = project.get_program_diagnostic()

    assert result[0][
        "fusion_valid"
    ] is False

    assert result[0][
        "qsynth_configured"
    ] is True

    assert result[0][
        "errors"
    ]


def test_program_diagnostic_invalid_definition(
    project
):

    project.data[
        "programs"
    ][
        "0:0"
    ] = "abc"

    result = project.get_program_diagnostic()

    assert result[0][
        "program"
    ] == "0:0"

    assert result[0][
        "name"
    ] == "0:0"

    assert result[0][
        "fusion_valid"
    ] is False

    assert result[0][
        "qsynth_configured"
    ] is False

    assert result[0][
        "errors"
    ]


def test_program_diagnostic_invalid_parts(
    project
):

    project.data[
        "programs"
    ][
        "0:0"
    ] = {
        "name": "PROGRAM test",
        "parts": "abc"
    }

    result = project.get_program_diagnostic()

    assert result[0][
        "fusion_valid"
    ] is False

    assert result[0][
        "qsynth_configured"
    ] is False

    assert result[0][
        "errors"
    ]


def test_program_diagnostic_missing_part_1(
    project
):

    project.data[
        "programs"
    ][
        "0:0"
    ] = {
        "name": "PROGRAM test",
        "parts": {}
    }

    result = project.get_program_diagnostic()

    assert result[0][
        "fusion_valid"
    ] is False

    assert result[0][
        "qsynth_configured"
    ] is False


def test_program_diagnostic_invalid_sf2_not_configured(
    project
):

    add_instrument(
        project,
        sf2_bank=16384
    )

    add_program(
        project
    )

    result = project.get_program_diagnostic()

    assert result[0][
        "qsynth_configured"
    ] is False


def test_program_diagnostic_sorted(
    project
):

    for program_id in (
        "10:2",
        "0:127",
        "2:10",
        "0:2"
    ):

        bank, program = (
            int(value)
            for value in program_id.split(
                ":"
            )
        )

        project.data[
            "programs"
        ][
            program_id
        ] = {
            "name": program_id,
            "parts": {
                "1": {
                    "bank": bank,
                    "program": program,
                    "midi_channel": 1
                }
            }
        }

    assert [
        item[
            "program"
        ]
        for item
        in project.get_program_diagnostic()
    ] == [
        "0:2",
        "0:127",
        "2:10",
        "10:2"
    ]

#
# get_mix_diagnostic()
#

def add_mix(
    project,
    mix_id="0:0",
    name="Mix test",
    channels=None
):

    if channels is None:

        channels = {}

    project.data[
        "mixes"
    ][
        mix_id
    ] = {
        "name": name,
        "channels": channels
    }


def test_mix_diagnostic_valid_and_configured(
    project
):

    add_instrument(
        project
    )

    add_mix(
        project,
        channels={
            "1": {
                "instrument": "piano"
            }
        }
    )

    result = project.get_mix_diagnostic()

    assert result == [
        {
            "mix": "0:0",
            "name": "Mix test",
            "fusion_valid": True,
            "channels": [
                {
                    "channel": "1",
                    "program": None,
                    "fusion_valid": True,
                    "qsynth_configured": True,
                    "instrument": {
                        "name": "Piano",
                        "sf2_bank": 0,
                        "sf2_program": 0
                    }
                }
            ]
        }
    ]


def test_mix_diagnostic_valid_but_not_configured(
    project
):

    add_mix(
        project,
        channels={
            "1": {}
        }
    )

    result = project.get_mix_diagnostic()

    channel = result[0][
        "channels"
    ][0]

    assert result[0][
        "fusion_valid"
    ] is True

    assert channel[
        "fusion_valid"
    ] is True

    assert channel[
        "qsynth_configured"
    ] is False

    assert channel[
        "instrument"
    ] is None


def test_mix_diagnostic_invalid_but_configured(
    project
):

    add_instrument(
        project
    )

    add_mix(
        project,
        channels={
            "1": {
                "instrument": "piano",
                "unexpected": True
            }
        }
    )

    result = project.get_mix_diagnostic()

    channel = result[0][
        "channels"
    ][0]

    assert result[0][
        "fusion_valid"
    ] is False

    assert channel[
        "fusion_valid"
    ] is False

    assert channel[
        "qsynth_configured"
    ] is True


def test_mix_diagnostic_invalid_definition(
    project
):

    project.data[
        "mixes"
    ][
        "0:0"
    ] = "abc"

    assert project.get_mix_diagnostic() == [
        {
            "mix": "0:0",
            "name": "0:0",
            "fusion_valid": False,
            "channels": []
        }
    ]


def test_mix_diagnostic_invalid_channels(
    project
):

    project.data[
        "mixes"
    ][
        "0:0"
    ] = {
        "name": "Mix test",
        "channels": "abc"
    }

    result = project.get_mix_diagnostic()

    assert result[0][
        "fusion_valid"
    ] is False

    assert result[0][
        "channels"
    ] == []


def test_mix_diagnostic_invalid_channel_definition(
    project
):

    add_mix(
        project,
        channels={
            "1": "abc"
        }
    )

    result = project.get_mix_diagnostic()

    channel = result[0][
        "channels"
    ][0]

    assert channel == {
        "channel": "1",
        "program": None,
        "fusion_valid": False,
        "qsynth_configured": False,
        "instrument": None
    }


def test_mix_diagnostic_invalid_channel_id_not_configured(
    project
):

    add_instrument(
        project
    )

    add_mix(
        project,
        channels={
            "17": {
                "instrument": "piano"
            }
        }
    )

    result = project.get_mix_diagnostic()

    channel = result[0][
        "channels"
    ][0]

    assert channel[
        "fusion_valid"
    ] is False

    assert channel[
        "qsynth_configured"
    ] is False


def test_mix_diagnostic_noncanonical_channel_id_not_configured(
    project
):

    add_instrument(
        project
    )

    add_mix(
        project,
        channels={
            "01": {
                "instrument": "piano"
            }
        }
    )

    result = project.get_mix_diagnostic()

    channel = result[0][
        "channels"
    ][0]

    assert channel[
        "fusion_valid"
    ] is False

    assert channel[
        "qsynth_configured"
    ] is False


def test_mix_diagnostic_invalid_sf2_not_configured(
    project
):

    add_instrument(
        project,
        sf2_program=128
    )

    add_mix(
        project,
        channels={
            "1": {
                "instrument": "piano"
            }
        }
    )

    result = project.get_mix_diagnostic()

    channel = result[0][
        "channels"
    ][0]

    assert channel[
        "qsynth_configured"
    ] is False


def test_mix_diagnostic_channel_sorting(
    project
):

    add_mix(
        project,
        channels={
            "10": {},
            "abc": {},
            "2": {},
            "1": {}
        }
    )

    result = project.get_mix_diagnostic()

    assert [
        channel[
            "channel"
        ]
        for channel
        in result[0][
            "channels"
        ]
    ] == [
        "1",
        "2",
        "10",
        "abc"
    ]


def test_mix_diagnostic_mix_sorting(
    project
):

    for mix_id in (
        "10:2",
        "0:127",
        "2:10",
        "0:2"
    ):

        add_mix(
            project,
            mix_id=mix_id,
            name=mix_id
        )

    assert [
        item[
            "mix"
        ]
        for item
        in project.get_mix_diagnostic()
    ] == [
        "0:2",
        "0:127",
        "2:10",
        "10:2"
    ]

#
# get_song_diagnostic()
#

def add_song(
    project,
    song_id="1",
    name="SONG test",
    channels=None
):

    if channels is None:

        channels = {}

    project.data[
        "songs"
    ][
        song_id
    ] = {
        "name": name,
        "channels": channels
    }


def test_song_diagnostic_valid_and_configured(
    project
):

    add_instrument(
        project
    )

    add_song(
        project,
        channels={
            "1": {
                "programs": {
                    "0:0": {
                        "instrument": "piano"
                    }
                }
            }
        }
    )

    result = project.get_song_diagnostic()

    assert result == [
        {
            "song": "1",
            "name": "SONG test",
            "fusion_valid": True,
            "channels": [
                {
                    "channel": "1",
                    "fusion_valid": True,
                    "qsynth_configured": True
                }
            ]
        }
    ]


def test_song_diagnostic_valid_but_not_configured(
    project
):

    add_song(
        project,
        channels={
            "1": {
                "programs": {}
            }
        }
    )

    result = project.get_song_diagnostic()

    channel = result[0][
        "channels"
    ][0]

    assert result[0][
        "fusion_valid"
    ] is True

    assert channel[
        "fusion_valid"
    ] is True

    assert channel[
        "qsynth_configured"
    ] is False


def test_song_diagnostic_invalid_but_configured(
    project
):

    add_instrument(
        project
    )

    add_song(
        project,
        channels={
            "1": {
                "programs": {
                    "0:0": {
                        "instrument": "piano"
                    }
                },
                "unexpected": True
            }
        }
    )

    result = project.get_song_diagnostic()

    channel = result[0][
        "channels"
    ][0]

    assert result[0][
        "fusion_valid"
    ] is False

    assert channel[
        "fusion_valid"
    ] is False

    assert channel[
        "qsynth_configured"
    ] is True


def test_song_diagnostic_invalid_definition(
    project
):

    project.data[
        "songs"
    ][
        "1"
    ] = "abc"

    assert project.get_song_diagnostic() == [
        {
            "song": "1",
            "name": "1",
            "fusion_valid": False,
            "channels": []
        }
    ]


def test_song_diagnostic_invalid_channels(
    project
):

    project.data[
        "songs"
    ][
        "1"
    ] = {
        "name": "SONG test",
        "channels": "abc"
    }

    result = project.get_song_diagnostic()

    assert result[0][
        "fusion_valid"
    ] is False

    assert result[0][
        "channels"
    ] == []


def test_song_diagnostic_invalid_channel_definition(
    project
):

    add_song(
        project,
        channels={
            "1": "abc"
        }
    )

    result = project.get_song_diagnostic()

    channel = result[0][
        "channels"
    ][0]

    assert channel[
        "channel"
    ] == "1"

    assert channel[
        "fusion_valid"
    ] is False

    assert channel[
        "qsynth_configured"
    ] is False


def test_song_diagnostic_invalid_channel_id_not_configured(
    project
):

    add_instrument(
        project
    )

    add_song(
        project,
        channels={
            "17": {
                "programs": {
                    "0:0": {
                        "instrument": "piano"
                    }
                }
            }
        }
    )

    result = project.get_song_diagnostic()

    channel = result[0][
        "channels"
    ][0]

    assert channel[
        "fusion_valid"
    ] is False

    assert channel[
        "qsynth_configured"
    ] is False


def test_song_diagnostic_invalid_non_numeric_channel(
    project
):

    project.data[
        "songs"
    ][
        "Song test"
    ] = {
        "name": "Song test",
        "channels": {
            "abc": {
                "programs": {}
            }
        }
    }

    diagnostic = project.get_song_diagnostic()

    assert len(
        diagnostic
    ) == 1

    song = diagnostic[
        0
    ]

    assert song[
        "song"
    ] == "Song test"

    assert song[
        "fusion_valid"
    ] is False

    assert len(
        song["channels"]
    ) == 1

    channel = song[
        "channels"
    ][
        0
    ]

    assert channel[
        "channel"
    ] == "abc"

    assert channel[
        "fusion_valid"
    ] is False

    assert channel[
        "qsynth_configured"
    ] is False


def test_song_diagnostic_noncanonical_channel_id_not_configured(
    project
):

    add_instrument(
        project
    )

    add_song(
        project,
        channels={
            "01": {
                "programs": {
                    "0:0": {
                        "instrument": "piano"
                    }
                }
            }
        }
    )

    result = project.get_song_diagnostic()

    channel = result[0][
        "channels"
    ][0]

    assert channel[
        "fusion_valid"
    ] is False

    assert channel[
        "qsynth_configured"
    ] is False


def test_song_diagnostic_invalid_program_definition(
    project
):

    add_song(
        project,
        channels={
            "1": {
                "programs": {
                    "0:0": "abc"
                }
            }
        }
    )

    result = project.get_song_diagnostic()

    channel = result[0][
        "channels"
    ][0]

    assert channel[
        "fusion_valid"
    ] is False

    assert channel[
        "qsynth_configured"
    ] is False


def test_song_diagnostic_invalid_sf2_not_configured(
    project
):

    add_instrument(
        project,
        sf2_bank=16384
    )

    add_song(
        project,
        channels={
            "1": {
                "programs": {
                    "0:0": {
                        "instrument": "piano"
                    }
                }
            }
        }
    )

    result = project.get_song_diagnostic()

    assert result[0][
        "channels"
    ][0][
        "qsynth_configured"
    ] is False


def test_song_diagnostic_all_programs_must_be_configured(
    project
):

    add_instrument(
        project
    )

    add_song(
        project,
        channels={
            "1": {
                "programs": {
                    "0:0": {
                        "instrument": "piano"
                    },
                    "0:1": {}
                }
            }
        }
    )

    result = project.get_song_diagnostic()

    assert result[0][
        "channels"
    ][0][
        "qsynth_configured"
    ] is False


def test_song_diagnostic_inherits_global_program(
    project
):

    add_instrument(
        project
    )

    add_program(
        project
    )

    add_song(
        project,
        channels={
            "1": {
                "programs": {
                    "0:0": {}
                }
            }
        }
    )

    result = project.get_song_diagnostic()

    assert result[0][
        "channels"
    ][0][
        "qsynth_configured"
    ] is True

#
# get_project_diagnostic_summary()
#

def test_project_diagnostic_summary_empty(
    project
):

    assert project.get_project_diagnostic_summary() == {
        "instruments": {
            "total": 0,
            "ok": 0,
            "unconfigured": 0,
            "error": 0
        },
        "mixes": {
            "total": 0,
            "ok": 0,
            "unconfigured": 0,
            "error": 0
        },
        "programs": {
            "total": 0,
            "ok": 0,
            "unconfigured": 0,
            "error": 0
        },
        "songs": {
            "total": 0,
            "ok": 0,
            "unconfigured": 0,
            "error": 0
        }
    }


def test_project_diagnostic_summary_instruments(
    project
):

    add_instrument(
        project,
        instrument_id="valid"
    )

    project.data[
        "instruments"
    ][
        "invalid"
    ] = {
        "name": "Invalid",
        "sf2_bank": 0,
        "sf2_program": 128
    }

    summary = (
        project.get_project_diagnostic_summary()
    )[
        "instruments"
    ]

    assert summary == {
        "total": 2,
        "ok": 1,
        "unconfigured": 0,
        "error": 1
    }


def test_project_diagnostic_summary_mixes(
    project
):

    add_instrument(
        project
    )

    add_mix(
        project,
        mix_id="0:0",
        name="OK",
        channels={
            "1": {
                "instrument": "piano"
            }
        }
    )

    add_mix(
        project,
        mix_id="0:1",
        name="Non configuré",
        channels={
            "1": {}
        }
    )

    add_mix(
        project,
        mix_id="0:2",
        name="Erreur",
        channels={
            "17": {
                "instrument": "piano"
            }
        }
    )

    summary = (
        project.get_project_diagnostic_summary()
    )[
        "mixes"
    ]

    assert summary == {
        "total": 3,
        "ok": 1,
        "unconfigured": 1,
        "error": 1
    }


def test_project_diagnostic_summary_empty_mix_unconfigured(
    project
):

    add_mix(
        project
    )

    summary = (
        project.get_project_diagnostic_summary()
    )[
        "mixes"
    ]

    assert summary == {
        "total": 1,
        "ok": 0,
        "unconfigured": 1,
        "error": 0
    }


def test_project_diagnostic_summary_partially_configured_mix(
    project
):

    add_instrument(
        project
    )

    add_mix(
        project,
        channels={
            "1": {
                "instrument": "piano"
            },
            "2": {}
        }
    )

    summary = (
        project.get_project_diagnostic_summary()
    )[
        "mixes"
    ]

    assert summary[
        "ok"
    ] == 0

    assert summary[
        "unconfigured"
    ] == 1

    assert summary[
        "error"
    ] == 0


def test_project_diagnostic_summary_programs(
    project
):

    add_instrument(
        project
    )

    add_program(
        project,
        program_id="0:0",
        name="OK"
    )

    add_program(
        project,
        program_id="0:1",
        name="Non configuré",
        instrument=None
    )

    project.data[
        "programs"
    ][
        "0:2"
    ] = "abc"

    summary = (
        project.get_project_diagnostic_summary()
    )[
        "programs"
    ]

    assert summary == {
        "total": 3,
        "ok": 1,
        "unconfigured": 1,
        "error": 1
    }


def test_project_diagnostic_summary_songs(
    project
):

    add_instrument(
        project
    )

    add_song(
        project,
        song_id="1",
        name="OK",
        channels={
            "1": {
                "programs": {
                    "0:0": {
                        "instrument": "piano"
                    }
                }
            }
        }
    )

    add_song(
        project,
        song_id="2",
        name="Non configurée",
        channels={
            "1": {
                "programs": {}
            }
        }
    )

    add_song(
        project,
        song_id="3",
        name="Erreur",
        channels={
            "17": {
                "programs": {
                    "0:0": {
                        "instrument": "piano"
                    }
                }
            }
        }
    )

    summary = (
        project.get_project_diagnostic_summary()
    )[
        "songs"
    ]

    assert summary == {
        "total": 3,
        "ok": 1,
        "unconfigured": 1,
        "error": 1
    }


def test_project_diagnostic_summary_empty_song_unconfigured(
    project
):

    add_song(
        project
    )

    summary = (
        project.get_project_diagnostic_summary()
    )[
        "songs"
    ]

    assert summary == {
        "total": 1,
        "ok": 0,
        "unconfigured": 1,
        "error": 0
    }


def test_project_diagnostic_summary_partially_configured_song(
    project
):

    add_instrument(
        project
    )

    add_song(
        project,
        channels={
            "1": {
                "programs": {
                    "0:0": {
                        "instrument": "piano"
                    }
                }
            },
            "2": {
                "programs": {}
            }
        }
    )

    summary = (
        project.get_project_diagnostic_summary()
    )[
        "songs"
    ]

    assert summary[
        "ok"
    ] == 0

    assert summary[
        "unconfigured"
    ] == 1

    assert summary[
        "error"
    ] == 0
