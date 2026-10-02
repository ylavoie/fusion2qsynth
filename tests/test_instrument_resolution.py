def make_instrument(
    name="Instrument test",
    sf2_bank=0,
    sf2_program=0
):

    return {
        "name": name,
        "sf2_bank": sf2_bank,
        "sf2_program": sf2_program
    }


def add_instrument(
    project,
    instrument_id,
    name="Instrument test",
    sf2_bank=0,
    sf2_program=0
):

    project.data[
        "instruments"
    ][
        instrument_id
    ] = make_instrument(
        name,
        sf2_bank,
        sf2_program
    )


def add_program(
    project,
    program_id="0:0",
    part=None
):

    if part is None:

        part = {
            "bank": 0,
            "program": 0,
            "midi_channel": 1
        }

    project.data[
        "programs"
    ][
        program_id
    ] = {
        "name": "PROGRAM test",
        "parts": {
            "1": part
        }
    }


#
# resolve_program_instrument()
#

def test_resolve_program_instrument_global(
    project
):

    add_instrument(
        project,
        "global_instrument",
        sf2_bank=10,
        sf2_program=20
    )

    add_program(
        project,
        part={
            "bank": 0,
            "program": 0,
            "midi_channel": 1,
            "instrument":
                "global_instrument"
        }
    )

    assert project.resolve_program_instrument(
        "0:0"
    ) == make_instrument(
        sf2_bank=10,
        sf2_program=20
    )


def test_resolve_program_instrument_legacy(
    project
):

    add_program(
        project,
        part={
            "bank": 0,
            "program": 0,
            "midi_channel": 1,
            "name": "Legacy",
            "sf2_bank": 10,
            "sf2_program": 20
        }
    )

    assert project.resolve_program_instrument(
        "0:0"
    ) == {
        "name": "Legacy",
        "sf2_bank": 10,
        "sf2_program": 20
    }


def test_resolve_program_instrument_unknown(
    project
):

    assert project.resolve_program_instrument(
        "0:0"
    ) is None


def test_resolve_program_instrument_invalid_program(
    project
):

    for invalid_program in (
        None,
        "abc",
        [],
        123
    ):

        project.data[
            "programs"
        ][
            "0:0"
        ] = invalid_program

        assert project.resolve_program_instrument(
            "0:0"
        ) is None


def test_resolve_program_instrument_invalid_parts(
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

    assert project.resolve_program_instrument(
        "0:0"
    ) is None


def test_resolve_program_instrument_missing_part_1(
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

    assert project.resolve_program_instrument(
        "0:0"
    ) is None


def test_resolve_program_instrument_invalid_part_1(
    project
):

    project.data[
        "programs"
    ][
        "0:0"
    ] = {
        "name": "PROGRAM test",
        "parts": {
            "1": "abc"
        }
    }

    assert project.resolve_program_instrument(
        "0:0"
    ) is None


#
# resolve_mix_channel_instrument()
#

def test_resolve_mix_channel_local_global_override(
    project
):

    add_instrument(
        project,
        "local_instrument",
        sf2_bank=10,
        sf2_program=20
    )

    add_instrument(
        project,
        "program_instrument",
        sf2_bank=30,
        sf2_program=40
    )

    add_program(
        project,
        part={
            "bank": 0,
            "program": 0,
            "midi_channel": 1,
            "instrument":
                "program_instrument"
        }
    )

    channel = {
        "program": "0:0",
        "instrument":
            "local_instrument"
    }

    assert project.resolve_mix_channel_instrument(
        channel
    ) == make_instrument(
        sf2_bank=10,
        sf2_program=20
    )


def test_resolve_mix_channel_local_legacy_has_priority(
    project
):

    add_instrument(
        project,
        "program_instrument",
        sf2_bank=30,
        sf2_program=40
    )

    add_program(
        project,
        part={
            "bank": 0,
            "program": 0,
            "midi_channel": 1,
            "instrument":
                "program_instrument"
        }
    )

    channel = {
        "program": "0:0",
        "name": "Legacy local",
        "sf2_bank": 10,
        "sf2_program": 20
    }

    assert project.resolve_mix_channel_instrument(
        channel
    ) == {
        "name": "Legacy local",
        "sf2_bank": 10,
        "sf2_program": 20
    }


def test_resolve_mix_channel_inherits_program(
    project
):

    add_instrument(
        project,
        "program_instrument",
        sf2_bank=30,
        sf2_program=40
    )

    add_program(
        project,
        part={
            "bank": 0,
            "program": 0,
            "midi_channel": 1,
            "instrument":
                "program_instrument"
        }
    )

    channel = {
        "program": "0:0"
    }

    assert project.resolve_mix_channel_instrument(
        channel
    ) == make_instrument(
        sf2_bank=30,
        sf2_program=40
    )


def test_resolve_mix_channel_unknown_local_falls_back(
    project
):

    add_instrument(
        project,
        "program_instrument",
        sf2_bank=30,
        sf2_program=40
    )

    add_program(
        project,
        part={
            "bank": 0,
            "program": 0,
            "midi_channel": 1,
            "instrument":
                "program_instrument"
        }
    )

    channel = {
        "program": "0:0",
        "instrument":
            "unknown_instrument"
    }

    assert project.resolve_mix_channel_instrument(
        channel
    ) == make_instrument(
        sf2_bank=30,
        sf2_program=40
    )


def test_resolve_mix_channel_without_resolution(
    project
):

    assert project.resolve_mix_channel_instrument(
        {}
    ) is None


def test_resolve_mix_channel_invalid_channel(
    project
):

    for channel in (
        None,
        "abc",
        [],
        123
    ):

        assert project.resolve_mix_channel_instrument(
            channel
        ) is None


#
# resolve_song_program_instrument()
#

def test_resolve_song_program_local_global_override(
    project
):

    add_instrument(
        project,
        "local_instrument",
        sf2_bank=10,
        sf2_program=20
    )

    add_instrument(
        project,
        "program_instrument",
        sf2_bank=30,
        sf2_program=40
    )

    add_program(
        project,
        part={
            "bank": 0,
            "program": 0,
            "midi_channel": 1,
            "instrument":
                "program_instrument"
        }
    )

    program_data = {
        "instrument":
            "local_instrument"
    }

    assert project.resolve_song_program_instrument(
        "0:0",
        program_data
    ) == make_instrument(
        sf2_bank=10,
        sf2_program=20
    )


def test_resolve_song_program_local_legacy_has_priority(
    project
):

    add_instrument(
        project,
        "program_instrument",
        sf2_bank=30,
        sf2_program=40
    )

    add_program(
        project,
        part={
            "bank": 0,
            "program": 0,
            "midi_channel": 1,
            "instrument":
                "program_instrument"
        }
    )

    program_data = {
        "name": "Legacy local",
        "sf2_bank": 10,
        "sf2_program": 20
    }

    assert project.resolve_song_program_instrument(
        "0:0",
        program_data
    ) == {
        "name": "Legacy local",
        "sf2_bank": 10,
        "sf2_program": 20
    }


def test_resolve_song_program_inherits_program(
    project
):

    add_instrument(
        project,
        "program_instrument",
        sf2_bank=30,
        sf2_program=40
    )

    add_program(
        project,
        part={
            "bank": 0,
            "program": 0,
            "midi_channel": 1,
            "instrument":
                "program_instrument"
        }
    )

    assert project.resolve_song_program_instrument(
        "0:0",
        {}
    ) == make_instrument(
        sf2_bank=30,
        sf2_program=40
    )


def test_resolve_song_program_unknown_local_falls_back(
    project
):

    add_instrument(
        project,
        "program_instrument",
        sf2_bank=30,
        sf2_program=40
    )

    add_program(
        project,
        part={
            "bank": 0,
            "program": 0,
            "midi_channel": 1,
            "instrument":
                "program_instrument"
        }
    )

    assert project.resolve_song_program_instrument(
        "0:0",
        {
            "instrument":
                "unknown_instrument"
        }
    ) == make_instrument(
        sf2_bank=30,
        sf2_program=40
    )


def test_resolve_song_program_invalid_local_falls_back(
    project
):

    add_instrument(
        project,
        "program_instrument",
        sf2_bank=30,
        sf2_program=40
    )

    add_program(
        project,
        part={
            "bank": 0,
            "program": 0,
            "midi_channel": 1,
            "instrument":
                "program_instrument"
        }
    )

    for program_data in (
        None,
        "abc",
        [],
        123
    ):

        assert project.resolve_song_program_instrument(
            "0:0",
            program_data
        ) == make_instrument(
            sf2_bank=30,
            sf2_program=40
        )


def test_resolve_song_program_without_resolution(
    project
):

    assert project.resolve_song_program_instrument(
        "0:0",
        {}
    ) is None

