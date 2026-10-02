def test_validate_mix_unknown(
    project
):

    assert project.validate_mix(
        "0:0"
    ) == [
        "Mix inconnu : 0:0"
    ]


def test_validate_program_unknown(
    project
):

    assert project.validate_program(
        "0:0"
    ) == [
        "PROGRAM inconnu : 0:0"
    ]


def test_validate_song_unknown(
    project
):

    assert project.validate_song(
        "1"
    ) == [
        "SONG inconnue : 1"
    ]


def test_validate_mix_valid(
    project
):

    project.data[
        "mixes"
    ][
        "0:0"
    ] = {
        "name": "Mix test",
        "channels": {}
    }

    assert project.validate_mix(
        "0:0"
    ) == []


def test_validate_program_valid(
    project
):

    project.data[
        "programs"
    ][
        "0:0"
    ] = {
        "name": "PROGRAM test",
        "parts": {
            "1": {
                "bank": 0,
                "program": 0,
                "midi_channel": 1
            }
        }
    }

    assert project.validate_program(
        "0:0"
    ) == []


def test_validate_song_valid(
    project
):

    project.data[
        "songs"
    ][
        "1"
    ] = {
        "name": "SONG test",
        "channels": {}
    }

    assert project.validate_song(
        "1"
    ) == []

def test_validate_empty_project(
    project
):

    assert project.validate() == []


def test_validate_aggregates_all_sections(
    project
):

    project.data[
        "banks"
    ][
        "program"
    ][
        "128"
    ] = "Invalid"

    project.data[
        "instruments"
    ][
        "invalid"
    ] = {
        "name": "Invalid",
        "sf2_bank": 0,
        "sf2_program": 128
    }

    project.data[
        "mixes"
    ][
        "0:0"
    ] = "abc"

    project.data[
        "programs"
    ][
        "0:1"
    ] = "abc"

    project.data[
        "songs"
    ][
        "1"
    ] = "abc"

    errors = project.validate()

    assert any(
        "Banque PROGRAM 128"
        in error
        for error in errors
    )

    assert any(
        "Instrument invalid"
        in error
        for error in errors
    )

    assert any(
        "0:0"
        in error
        for error in errors
    )

    assert any(
        "0:1"
        in error
        for error in errors
    )

    assert any(
        "1"
        in error
        for error in errors
    )