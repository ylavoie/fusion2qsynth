import copy


def add_song(
    project,
    song_id="Song test",
    name="Song test",
    channels=None
):

    if channels is None:

        channels = {}

    project.data[
        "songs"
    ][
        str(song_id)
    ] = {
        "name": name,
        "channels": channels
    }


def make_channel(
    programs=None
):

    if programs is None:

        programs = {}

    return {
        "programs": programs
    }


#
# rename_song()
#

def test_rename_song_valid(
    project
):

    add_song(
        project
    )

    success, errors = project.rename_song(
        "Song test",
        "Nouveau nom"
    )

    assert success is True
    assert errors == []

    assert project.get_song(
        "Song test"
    )["name"] == "Nouveau nom"


def test_rename_song_unknown(
    project
):

    success, errors = project.rename_song(
        "Song test",
        "Nouveau nom"
    )

    assert success is False
    assert errors


def test_rename_song_invalid_structure(
    project
):

    project.data[
        "songs"
    ][
        "Song test"
    ] = "abc"

    success, errors = project.rename_song(
        "Song test",
        "Nouveau nom"
    )

    assert success is False
    assert errors

    assert project.get_song(
        "Song test"
    ) == "abc"


def test_rename_song_invalid_name_rolls_back(
    project
):

    add_song(
        project,
        name="Original"
    )

    success, errors = project.rename_song(
        "Song test",
        ""
    )

    assert success is False
    assert errors

    assert project.get_song(
        "Song test"
    )["name"] == "Original"


def test_rename_song_with_preexisting_error(
    project
):

    add_song(
        project
    )

    project.data[
        "mixes"
    ][
        "1:1"
    ] = "abc"

    success, errors = project.rename_song(
        "Song test",
        "Nouveau nom"
    )

    assert success is True
    assert errors == []

    assert project.get_song(
        "Song test"
    )["name"] == "Nouveau nom"

    assert project.get_mix(
        "1:1"
    ) == "abc"


#
# delete_song()
#

def test_delete_song_valid(
    project
):

    add_song(
        project
    )

    success, errors = project.delete_song(
        "Song test"
    )

    assert success is True
    assert errors == []

    assert project.get_song(
        "Song test"
    ) is None


def test_delete_song_unknown(
    project
):

    success, errors = project.delete_song(
        "Song test"
    )

    assert success is False
    assert errors


def test_delete_invalid_song(
    project
):

    project.data[
        "songs"
    ][
        "Song test"
    ] = "abc"

    success, errors = project.delete_song(
        "Song test"
    )

    assert success is True
    assert errors == []

    assert project.get_song(
        "Song test"
    ) is None


def test_delete_song_with_preexisting_error(
    project
):

    add_song(
        project
    )

    project.data[
        "mixes"
    ][
        "1:1"
    ] = "abc"

    success, errors = project.delete_song(
        "Song test"
    )

    assert success is True
    assert errors == []

    assert project.get_song(
        "Song test"
    ) is None

    assert project.get_mix(
        "1:1"
    ) == "abc"


#
# _ensure_song()
#

def test_ensure_song_creates_song(
    project
):

    song = project._ensure_song(
        "Song test"
    )

    assert song == {
        "name": "Song test",
        "channels": {}
    }

    assert project.get_song(
        "Song test"
    ) is song


def test_ensure_song_existing(
    project
):

    add_song(
        project,
        name="Nom existant"
    )

    original = project.get_song(
        "Song test"
    )

    song = project._ensure_song(
        "Song test"
    )

    assert song is original

    assert song == {
        "name": "Nom existant",
        "channels": {}
    }


def test_ensure_song_converts_id_to_string(
    project
):

    song = project._ensure_song(
        123
    )

    assert project.get_song(
        "123"
    ) is song

    assert song == {
        "name": "123",
        "channels": {}
    }


#
# replace_song_channels()
#

def test_replace_song_channels_valid(
    project
):

    add_song(
        project
    )

    channels = {
        "1": make_channel()
    }

    success, errors = project.replace_song_channels(
        "Song test",
        channels
    )

    assert success is True
    assert errors == []

    assert project.get_song(
        "Song test"
    )["channels"] == channels


def test_replace_song_channels_unknown_song(
    project
):

    success, errors = project.replace_song_channels(
        "Song test",
        {}
    )

    assert success is False
    assert errors


def test_replace_song_channels_invalid_song_structure(
    project
):

    project.data[
        "songs"
    ][
        "Song test"
    ] = "abc"

    success, errors = project.replace_song_channels(
        "Song test",
        {}
    )

    assert success is False
    assert errors

    assert project.get_song(
        "Song test"
    ) == "abc"


def test_replace_song_channels_invalid_channels_rolls_back(
    project
):

    add_song(
        project
    )

    before = copy.deepcopy(
        project.data
    )

    success, errors = project.replace_song_channels(
        "Song test",
        "abc"
    )

    assert success is False
    assert errors

    assert project.data == before


def test_replace_song_channels_invalid_channel_rolls_back(
    project
):

    add_song(
        project
    )

    before = copy.deepcopy(
        project.data
    )

    success, errors = project.replace_song_channels(
        "Song test",
        {
            "17": make_channel()
        }
    )

    assert success is False
    assert errors

    assert project.data == before


def test_replace_song_channels_invalid_program_rolls_back(
    project
):

    add_song(
        project
    )

    before = copy.deepcopy(
        project.data
    )

    success, errors = project.replace_song_channels(
        "Song test",
        {
            "1": make_channel(
                {
                    "abc": {}
                }
            )
        }
    )

    assert success is False
    assert errors

    assert project.data == before


def test_replace_song_channels_with_preexisting_error(
    project
):

    add_song(
        project
    )

    project.data[
        "mixes"
    ][
        "1:1"
    ] = "abc"

    channels = {
        "1": make_channel()
    }

    success, errors = project.replace_song_channels(
        "Song test",
        channels
    )

    assert success is True
    assert errors == []

    assert project.get_song(
        "Song test"
    )["channels"] == channels

    assert project.get_mix(
        "1:1"
    ) == "abc"


#
# update_song_channel()
#

def test_update_song_channel_valid(
    project
):

    add_song(
        project,
        channels={
            "1": make_channel()
        }
    )

    success, errors = project.update_song_channel(
        "Song test",
        "1",
        {
            "volume": 100,
            "pan": 64
        }
    )

    assert success is True
    assert errors == []

    channel = project.get_song(
        "Song test"
    )["channels"]["1"]

    assert channel["volume"] == 100
    assert channel["pan"] == 64


def test_update_song_channel_unknown_song(
    project
):

    success, errors = project.update_song_channel(
        "Song test",
        "1",
        {
            "volume": 100
        }
    )

    assert success is False
    assert errors


def test_update_song_channel_invalid_song_structure(
    project
):

    project.data[
        "songs"
    ][
        "Song test"
    ] = "abc"

    success, errors = project.update_song_channel(
        "Song test",
        "1",
        {
            "volume": 100
        }
    )

    assert success is False
    assert errors

    assert project.get_song(
        "Song test"
    ) == "abc"


def test_update_song_channel_invalid_channels_structure(
    project
):

    add_song(
        project
    )

    project.get_song(
        "Song test"
    )["channels"] = "abc"

    success, errors = project.update_song_channel(
        "Song test",
        "1",
        {
            "volume": 100
        }
    )

    assert success is False
    assert errors


def test_update_song_channel_unknown_channel(
    project
):

    add_song(
        project
    )

    success, errors = project.update_song_channel(
        "Song test",
        "1",
        {
            "volume": 100
        }
    )

    assert success is False
    assert errors


def test_update_song_channel_invalid_channel_structure(
    project
):

    add_song(
        project,
        channels={
            "1": "abc"
        }
    )

    success, errors = project.update_song_channel(
        "Song test",
        "1",
        {
            "volume": 100
        }
    )

    assert success is False
    assert errors

    assert project.get_song(
        "Song test"
    )["channels"]["1"] == "abc"


def test_update_song_channel_invalid_updates(
    project
):

    add_song(
        project,
        channels={
            "1": make_channel()
        }
    )

    before = copy.deepcopy(
        project.data
    )

    success, errors = project.update_song_channel(
        "Song test",
        "1",
        "abc"
    )

    assert success is False
    assert errors

    assert project.data == before


def test_update_song_channel_invalid_value_rolls_back(
    project
):

    add_song(
        project,
        channels={
            "1": make_channel()
        }
    )

    before = copy.deepcopy(
        project.data
    )

    success, errors = project.update_song_channel(
        "Song test",
        "1",
        {
            "volume": 128
        }
    )

    assert success is False
    assert errors

    assert project.data == before


def test_update_song_channel_unknown_field_rolls_back(
    project
):

    add_song(
        project,
        channels={
            "1": make_channel()
        }
    )

    before = copy.deepcopy(
        project.data
    )

    success, errors = project.update_song_channel(
        "Song test",
        "1",
        {
            "abc": 123
        }
    )

    assert success is False
    assert errors

    assert project.data == before


def test_update_song_channel_remove_field(
    project
):

    add_song(
        project,
        channels={
            "1": {
                "programs": {},
                "volume": 100
            }
        }
    )

    success, errors = project.update_song_channel(
        "Song test",
        "1",
        remove_fields=[
            "volume"
        ]
    )

    assert success is True
    assert errors == []

    assert "volume" not in (
        project.get_song(
            "Song test"
        )["channels"]["1"]
    )


def test_update_song_channel_with_preexisting_error(
    project
):

    add_song(
        project,
        channels={
            "1": make_channel()
        }
    )

    project.data[
        "mixes"
    ][
        "1:1"
    ] = "abc"

    success, errors = project.update_song_channel(
        "Song test",
        "1",
        {
            "volume": 100
        }
    )

    assert success is True
    assert errors == []

    assert (
        project.get_song(
            "Song test"
        )["channels"]["1"]["volume"]
        ==
        100
    )

    assert project.get_mix(
        "1:1"
    ) == "abc"


#
# move_song_channel()
#

def test_move_song_channel_valid(
    project
):

    add_song(
        project,
        channels={
            "1": make_channel()
        }
    )

    success, errors = project.move_song_channel(
        "Song test",
        "1",
        "2"
    )

    assert success is True
    assert errors == []

    channels = project.get_song(
        "Song test"
    )["channels"]

    assert "1" not in channels
    assert "2" in channels


def test_move_song_channel_unknown_song(
    project
):

    success, errors = project.move_song_channel(
        "Song test",
        "1",
        "2"
    )

    assert success is False
    assert errors


def test_move_song_channel_invalid_song_structure(
    project
):

    project.data[
        "songs"
    ][
        "Song test"
    ] = "abc"

    success, errors = project.move_song_channel(
        "Song test",
        "1",
        "2"
    )

    assert success is False
    assert errors


def test_move_song_channel_invalid_channels_structure(
    project
):

    add_song(
        project
    )

    project.get_song(
        "Song test"
    )["channels"] = "abc"

    success, errors = project.move_song_channel(
        "Song test",
        "1",
        "2"
    )

    assert success is False
    assert errors


def test_move_song_channel_unknown_source(
    project
):

    add_song(
        project,
        channels={
            "1": make_channel()
        }
    )

    success, errors = project.move_song_channel(
        "Song test",
        "2",
        "3"
    )

    assert success is False
    assert errors


def test_move_song_channel_destination_used(
    project
):

    add_song(
        project,
        channels={
            "1": make_channel(),
            "2": make_channel()
        }
    )

    before = copy.deepcopy(
        project.data
    )

    success, errors = project.move_song_channel(
        "Song test",
        "1",
        "2"
    )

    assert success is False
    assert errors

    assert project.data == before


def test_move_song_channel_invalid_destination_rolls_back(
    project
):

    add_song(
        project,
        channels={
            "1": make_channel()
        }
    )

    before = copy.deepcopy(
        project.data
    )

    success, errors = project.move_song_channel(
        "Song test",
        "1",
        "17"
    )

    assert success is False
    assert errors

    assert project.data == before


def test_move_song_channel_non_numeric_destination_rolls_back(
    project
):

    add_song(
        project,
        channels={
            "1": make_channel()
        }
    )

    before = copy.deepcopy(
        project.data
    )

    success, errors = project.move_song_channel(
        "Song test",
        "1",
        "abc"
    )

    assert success is False
    assert errors

    assert project.data == before


def test_move_song_channel_with_preexisting_error(
    project
):

    add_song(
        project,
        channels={
            "1": make_channel()
        }
    )

    project.data[
        "mixes"
    ][
        "1:1"
    ] = "abc"

    success, errors = project.move_song_channel(
        "Song test",
        "1",
        "2"
    )

    assert success is True
    assert errors == []

    channels = project.get_song(
        "Song test"
    )["channels"]

    assert "1" not in channels
    assert "2" in channels

    assert project.get_mix(
        "1:1"
    ) == "abc"

#
# update_song_program()
#

def make_song_program(
    fusion_name=None,
    instrument=None
):

    program = {}

    if fusion_name is not None:

        program[
            "fusion_name"
        ] = fusion_name

    if instrument is not None:

        program[
            "instrument"
        ] = instrument

    return program


def add_instrument(
    project,
    instrument_id="test_instrument"
):

    project.data[
        "instruments"
    ][
        instrument_id
    ] = {
        "name": "Instrument test",
        "sf2_bank": 0,
        "sf2_program": 0
    }


def test_update_song_program_fusion_name_valid(
    project
):

    add_song(
        project,
        channels={
            "1": make_channel(
                {
                    "0:0": {}
                }
            )
        }
    )

    success, errors = project.update_song_program(
        "Song test",
        "1",
        "0:0",
        {
            "fusion_name": "Grand Piano"
        }
    )

    assert success is True
    assert errors == []

    program = (
        project.get_song(
            "Song test"
        )["channels"]["1"]["programs"]["0:0"]
    )

    assert (
        program["fusion_name"]
        ==
        "Grand Piano"
    )


def test_update_song_program_instrument_valid(
    project
):

    add_instrument(
        project
    )

    add_song(
        project,
        channels={
            "1": make_channel(
                {
                    "0:0": {}
                }
            )
        }
    )

    success, errors = project.update_song_program(
        "Song test",
        "1",
        "0:0",
        {
            "instrument":
                "test_instrument"
        }
    )

    assert success is True
    assert errors == []

    program = (
        project.get_song(
            "Song test"
        )["channels"]["1"]["programs"]["0:0"]
    )

    assert (
        program["instrument"]
        ==
        "test_instrument"
    )


def test_update_song_program_remove_fusion_name(
    project
):

    add_song(
        project,
        channels={
            "1": make_channel(
                {
                    "0:0": {
                        "fusion_name":
                            "Grand Piano"
                    }
                }
            )
        }
    )

    success, errors = project.update_song_program(
        "Song test",
        "1",
        "0:0",
        remove_fields=[
            "fusion_name"
        ]
    )

    assert success is True
    assert errors == []

    program = (
        project.get_song(
            "Song test"
        )["channels"]["1"]["programs"]["0:0"]
    )

    assert "fusion_name" not in program


def test_update_song_program_remove_instrument(
    project
):

    add_instrument(
        project
    )

    add_song(
        project,
        channels={
            "1": make_channel(
                {
                    "0:0": {
                        "instrument":
                            "test_instrument"
                    }
                }
            )
        }
    )

    success, errors = project.update_song_program(
        "Song test",
        "1",
        "0:0",
        remove_fields=[
            "instrument"
        ]
    )

    assert success is True
    assert errors == []

    program = (
        project.get_song(
            "Song test"
        )["channels"]["1"]["programs"]["0:0"]
    )

    assert "instrument" not in program


def test_update_song_program_unknown_song(
    project
):

    success, errors = project.update_song_program(
        "Song test",
        "1",
        "0:0",
        {
            "fusion_name": "Test"
        }
    )

    assert success is False
    assert errors


def test_update_song_program_invalid_song_structure(
    project
):

    project.data[
        "songs"
    ][
        "Song test"
    ] = "abc"

    success, errors = project.update_song_program(
        "Song test",
        "1",
        "0:0",
        {
            "fusion_name": "Test"
        }
    )

    assert success is False
    assert errors

    assert project.get_song(
        "Song test"
    ) == "abc"


def test_update_song_program_invalid_channels_structure(
    project
):

    add_song(
        project
    )

    project.get_song(
        "Song test"
    )["channels"] = "abc"

    success, errors = project.update_song_program(
        "Song test",
        "1",
        "0:0",
        {
            "fusion_name": "Test"
        }
    )

    assert success is False
    assert errors


def test_update_song_program_unknown_channel(
    project
):

    add_song(
        project
    )

    success, errors = project.update_song_program(
        "Song test",
        "1",
        "0:0",
        {
            "fusion_name": "Test"
        }
    )

    assert success is False
    assert errors


def test_update_song_program_invalid_channel_structure(
    project
):

    add_song(
        project,
        channels={
            "1": "abc"
        }
    )

    success, errors = project.update_song_program(
        "Song test",
        "1",
        "0:0",
        {
            "fusion_name": "Test"
        }
    )

    assert success is False
    assert errors

    assert (
        project.get_song(
            "Song test"
        )["channels"]["1"]
        ==
        "abc"
    )


def test_update_song_program_invalid_programs_structure(
    project
):

    add_song(
        project,
        channels={
            "1": {
                "programs": "abc"
            }
        }
    )

    success, errors = project.update_song_program(
        "Song test",
        "1",
        "0:0",
        {
            "fusion_name": "Test"
        }
    )

    assert success is False
    assert errors


def test_update_song_program_unknown_program(
    project
):

    add_song(
        project,
        channels={
            "1": make_channel()
        }
    )

    success, errors = project.update_song_program(
        "Song test",
        "1",
        "0:0",
        {
            "fusion_name": "Test"
        }
    )

    assert success is False
    assert errors


def test_update_song_program_invalid_program_structure(
    project
):

    add_song(
        project,
        channels={
            "1": make_channel(
                {
                    "0:0": "abc"
                }
            )
        }
    )

    success, errors = project.update_song_program(
        "Song test",
        "1",
        "0:0",
        {
            "fusion_name": "Test"
        }
    )

    assert success is False
    assert errors

    assert (
        project.get_song(
            "Song test"
        )["channels"]["1"]["programs"]["0:0"]
        ==
        "abc"
    )


def test_update_song_program_invalid_updates(
    project
):

    add_song(
        project,
        channels={
            "1": make_channel(
                {
                    "0:0": {}
                }
            )
        }
    )

    before = copy.deepcopy(
        project.data
    )

    success, errors = project.update_song_program(
        "Song test",
        "1",
        "0:0",
        "abc"
    )

    assert success is False
    assert errors

    assert project.data == before


def test_update_song_program_invalid_fusion_name_rolls_back(
    project
):

    add_song(
        project,
        channels={
            "1": make_channel(
                {
                    "0:0": {}
                }
            )
        }
    )

    before = copy.deepcopy(
        project.data
    )

    success, errors = project.update_song_program(
        "Song test",
        "1",
        "0:0",
        {
            "fusion_name": ""
        }
    )

    assert success is False
    assert errors

    assert project.data == before


def test_update_song_program_unknown_instrument_rolls_back(
    project
):

    add_song(
        project,
        channels={
            "1": make_channel(
                {
                    "0:0": {}
                }
            )
        }
    )

    before = copy.deepcopy(
        project.data
    )

    success, errors = project.update_song_program(
        "Song test",
        "1",
        "0:0",
        {
            "instrument":
                "instrument_inexistant"
        }
    )

    assert success is False
    assert errors

    assert project.data == before


def test_update_song_program_unknown_field_rolls_back(
    project
):

    add_song(
        project,
        channels={
            "1": make_channel(
                {
                    "0:0": {}
                }
            )
        }
    )

    before = copy.deepcopy(
        project.data
    )

    success, errors = project.update_song_program(
        "Song test",
        "1",
        "0:0",
        {
            "abc": 123
        }
    )

    assert success is False
    assert errors

    assert project.data == before


def test_update_song_program_with_preexisting_error(
    project
):

    add_song(
        project,
        channels={
            "1": make_channel(
                {
                    "0:0": {}
                }
            )
        }
    )

    project.data[
        "mixes"
    ][
        "1:1"
    ] = "abc"

    success, errors = project.update_song_program(
        "Song test",
        "1",
        "0:0",
        {
            "fusion_name":
                "Grand Piano"
        }
    )

    assert success is True
    assert errors == []

    program = (
        project.get_song(
            "Song test"
        )["channels"]["1"]["programs"]["0:0"]
    )

    assert (
        program["fusion_name"]
        ==
        "Grand Piano"
    )

    assert project.get_mix(
        "1:1"
    ) == "abc"


#
# Validation SONG - branches complémentaires
#

def test_song_program_id_noncanonical(
    project
):

    add_song(
        project,
        channels={
            "1": make_channel(
                {
                    "01:2": {}
                }
            )
        }
    )

    errors = project.validate_song(
        "Song test"
    )

    assert any(
        "PROGRAM invalide (01:2)"
        in error
        for error in errors
    )


def test_song_program_bank_out_of_range(
    project
):

    add_song(
        project,
        channels={
            "1": make_channel(
                {
                    "128:0": {}
                }
            )
        }
    )

    errors = project.validate_song(
        "Song test"
    )

    assert any(
        "Bank invalide (128)"
        in error
        for error in errors
    )


def test_song_program_number_out_of_range(
    project
):

    add_song(
        project,
        channels={
            "1": make_channel(
                {
                    "0:128": {}
                }
            )
        }
    )

    errors = project.validate_song(
        "Song test"
    )

    assert any(
        "Program invalide (128)"
        in error
        for error in errors
    )


def test_song_program_invalid_instrument(
    project
):

    add_song(
        project,
        channels={
            "1": make_channel(
                {
                    "0:0": {
                        "instrument": ""
                    }
                }
            )
        }
    )

    errors = project.validate_song(
        "Song test"
    )

    assert any(
        "instrument invalide"
        in error
        for error in errors
    )


def test_song_unknown_field(
    project
):

    add_song(
        project
    )

    project.get_song(
        "Song test"
    )[
        "unknown"
    ] = 123

    errors = project.validate_song(
        "Song test"
    )

    assert any(
        "champ inconnu 'unknown'"
        in error
        for error in errors
    )


def test_song_channels_absent(
    project
):

    add_song(
        project
    )

    project.get_song(
        "Song test"
    ).pop(
        "channels"
    )

    errors = project.validate_song(
        "Song test"
    )

    assert any(
        "channels absent"
        in error
        for error in errors
    )
