from fusion_project import FusionProject

#
# is_qsynth_ready()
#

def test_is_qsynth_ready_global_instrument(
    project
):

    project.data[
        "instruments"
    ][
        "piano"
    ] = {
        "name": "Piano",
        "sf2_bank": 0,
        "sf2_program": 0
    }

    part = {
        "midi_channel": 1,
        "instrument": "piano"
    }

    assert project.is_qsynth_ready(
        part
    ) is True


def test_is_qsynth_ready_legacy_instrument(
    project
):

    part = {
        "midi_channel": 1,
        "sf2_bank": 0,
        "sf2_program": 0
    }

    assert project.is_qsynth_ready(
        part
    ) is True


def test_is_qsynth_ready_invalid_part(
    project
):

    for part in (
        None,
        "abc",
        [],
        123
    ):

        assert project.is_qsynth_ready(
            part
        ) is False


def test_is_qsynth_ready_missing_midi_channel(
    project
):

    part = {
        "sf2_bank": 0,
        "sf2_program": 0
    }

    assert project.is_qsynth_ready(
        part
    ) is False


def test_is_qsynth_ready_invalid_midi_channel(
    project
):

    for midi_channel in (
        True,
        0,
        17,
        "1"
    ):

        part = {
            "midi_channel": midi_channel,
            "sf2_bank": 0,
            "sf2_program": 0
        }

        assert project.is_qsynth_ready(
            part
        ) is False


def test_is_qsynth_ready_midi_channel_boundaries(
    project
):

    for midi_channel in (
        1,
        16
    ):

        part = {
            "midi_channel": midi_channel,
            "sf2_bank": 0,
            "sf2_program": 0
        }

        assert project.is_qsynth_ready(
            part
        ) is True


def test_is_qsynth_ready_unknown_instrument(
    project
):

    part = {
        "midi_channel": 1,
        "instrument": "unknown"
    }

    assert project.is_qsynth_ready(
        part
    ) is False


def test_is_qsynth_ready_invalid_sf2_bank(
    project
):

    for sf2_bank in (
        True,
        -1,
        16384,
        "0"
    ):

        part = {
            "midi_channel": 1,
            "sf2_bank": sf2_bank,
            "sf2_program": 0
        }

        assert project.is_qsynth_ready(
            part
        ) is False


def test_is_qsynth_ready_sf2_bank_boundaries(
    project
):

    for sf2_bank in (
        0,
        16383
    ):

        part = {
            "midi_channel": 1,
            "sf2_bank": sf2_bank,
            "sf2_program": 0
        }

        assert project.is_qsynth_ready(
            part
        ) is True


def test_is_qsynth_ready_invalid_sf2_program(
    project
):

    for sf2_program in (
        True,
        -1,
        128,
        "0"
    ):

        part = {
            "midi_channel": 1,
            "sf2_bank": 0,
            "sf2_program": sf2_program
        }

        assert project.is_qsynth_ready(
            part
        ) is False


def test_is_qsynth_ready_sf2_program_boundaries(
    project
):

    for sf2_program in (
        0,
        127
    ):

        part = {
            "midi_channel": 1,
            "sf2_bank": 0,
            "sf2_program": sf2_program
        }

        assert project.is_qsynth_ready(
            part
        ) is True


def test_is_qsynth_ready_incomplete_sf2(
    project
):

    assert project.is_qsynth_ready(
        {
            "midi_channel": 1,
            "sf2_bank": 0
        }
    ) is False

    assert project.is_qsynth_ready(
        {
            "midi_channel": 1,
            "sf2_program": 0
        }
    ) is False

#
# MIX access
#

def test_get_mixes(
    project
):

    assert project.get_mixes() is project.data[
        "mixes"
    ]


def test_get_mix(
    project
):

    mix = {
        "name": "Mix test",
        "channels": {}
    }

    project.data[
        "mixes"
    ][
        "0:0"
    ] = mix

    assert project.get_mix(
        "0:0"
    ) is mix

    assert project.get_mix(
        "1:1"
    ) is None


def test_iter_mixes_sorted(
    project
):

    for mix_id in (
        "10:2",
        "0:127",
        "2:10",
        "0:2"
    ):

        project.data[
            "mixes"
        ][
            mix_id
        ] = {
            "name": mix_id,
            "channels": {}
        }

    assert [
        mix_id
        for mix_id, mix
        in project.iter_mixes()
    ] == [
        "0:2",
        "0:127",
        "2:10",
        "10:2"
    ]


def test_count_mixes(
    project
):

    assert project.count_mixes() == 0

    project.data[
        "mixes"
    ][
        "0:0"
    ] = {}

    project.data[
        "mixes"
    ][
        "0:1"
    ] = {}

    assert project.count_mixes() == 2


#
# PROGRAM access
#

def test_get_programs(
    project
):

    assert project.get_programs() is project.data[
        "programs"
    ]


def test_get_program(
    project
):

    program = {
        "name": "PROGRAM test",
        "parts": {}
    }

    project.data[
        "programs"
    ][
        "0:0"
    ] = program

    assert project.get_program(
        "0:0"
    ) is program

    assert project.get_program(
        "1:1"
    ) is None


def test_iter_programs_sorted(
    project
):

    for program_id in (
        "10:2",
        "0:127",
        "2:10",
        "0:2"
    ):

        project.data[
            "programs"
        ][
            program_id
        ] = {
            "name": program_id,
            "parts": {}
        }

    assert [
        program_id
        for program_id, program
        in project.iter_programs()
    ] == [
        "0:2",
        "0:127",
        "2:10",
        "10:2"
    ]


def test_count_programs(
    project
):

    assert project.count_programs() == 0

    project.data[
        "programs"
    ][
        "0:0"
    ] = {}

    project.data[
        "programs"
    ][
        "0:1"
    ] = {}

    assert project.count_programs() == 2


#
# SONG access
#

def test_get_songs(
    project
):

    assert project.get_songs() is project.data[
        "songs"
    ]


def test_get_song(
    project
):

    song = {
        "name": "SONG test",
        "channels": {}
    }

    project.data[
        "songs"
    ][
        "1"
    ] = song

    assert project.get_song(
        "1"
    ) is song

    assert project.get_song(
        1
    ) is song

    assert project.get_song(
        2
    ) is None


def test_iter_songs_sorted_case_insensitive(
    project
):

    for song_id in (
        "Zulu",
        "beta",
        "Alpha"
    ):

        project.data[
            "songs"
        ][
            song_id
        ] = {
            "name": song_id,
            "channels": {}
        }

    assert [
        song_id
        for song_id, song
        in project.iter_songs()
    ] == [
        "Alpha",
        "beta",
        "Zulu"
    ]


def test_count_songs(
    project
):

    assert project.count_songs() == 0

    project.data[
        "songs"
    ][
        "1"
    ] = {}

    project.data[
        "songs"
    ][
        "2"
    ] = {}

    assert project.count_songs() == 2


#
# sort_performance_ids()
#

def test_sort_performance_ids_numeric(
    project
):

    data = {
        "10:2": {},
        "2:10": {},
        "0:127": {},
        "0:2": {}
    }

    assert project.sort_performance_ids(
        data
    ) == [
        "0:2",
        "0:127",
        "2:10",
        "10:2"
    ]


def test_sort_performance_ids_invalid_after_numeric(
    project
):

    data = {
        "2:1": {},
        "xyz": {},
        "1:2": {},
        "abc": {}
    }

    assert project.sort_performance_ids(
        data
    ) == [
        "1:2",
        "2:1",
        "abc",
        "xyz"
    ]


def test_sort_performance_ids_malformed(
    project
):

    data = {
        "1:2:3": {},
        None: {},
        10: {},
        "2:1": {}
    }

    assert project.sort_performance_ids(
        data
    ) == [
        "2:1",
        10,
        "1:2:3",
        None
    ]


def test_sort_performance_ids_empty(
    project
):

    assert project.sort_performance_ids(
        {}
    ) == []


def test_sort_performance_ids_numeric_order():

    data = {
        "10:2": {},
        "2:10": {},
        "2:2": {},
        "0:127": {},
        "0:1": {}
    }

    assert FusionProject.sort_performance_ids(
        data
    ) == [
        "0:1",
        "0:127",
        "2:2",
        "2:10",
        "10:2"
    ]


def test_sort_performance_ids_invalid_after_valid():

    data = {
        "abc": {},
        "2:10": {},
        "invalid": {},
        "0:1": {}
    }

    assert FusionProject.sort_performance_ids(
        data
    ) == [
        "0:1",
        "2:10",
        "abc",
        "invalid"
    ]


def test_sort_performance_ids_accepts_non_string_ids():

    data = {
        12: {},
        "2:10": {},
        "0:1": {}
    }

    assert FusionProject.sort_performance_ids(
        data
    ) == [
        "0:1",
        "2:10",
        12
    ]
