import copy


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


def add_instrument_direct(
    project,
    instrument_id="test_instrument"
):

    project.data[
        "instruments"
    ][
        instrument_id
    ] = make_instrument()


#
# add_instrument()
#

def test_add_instrument_valid(
    project
):

    instrument = make_instrument()

    success, errors = project.add_instrument(
        "test_instrument",
        instrument
    )

    assert success is True
    assert errors == []

    assert (
        project.get_instrument(
            "test_instrument"
        )
        ==
        instrument
    )


def test_add_instrument_existing(
    project
):

    add_instrument_direct(
        project
    )

    before = copy.deepcopy(
        project.data
    )

    success, errors = project.add_instrument(
        "test_instrument",
        make_instrument(
            name="Autre"
        )
    )

    assert success is False
    assert errors

    assert project.data == before


def test_add_instrument_invalid_id_rolls_back(
    project
):

    before = copy.deepcopy(
        project.data
    )

    success, errors = project.add_instrument(
        "Instrument invalide",
        make_instrument()
    )

    assert success is False
    assert errors

    assert project.data == before


def test_add_instrument_invalid_definition_rolls_back(
    project
):

    before = copy.deepcopy(
        project.data
    )

    success, errors = project.add_instrument(
        "test_instrument",
        "abc"
    )

    assert success is False
    assert errors

    assert project.data == before


def test_add_instrument_bool_sf2_bank_rejected(
    project
):

    before = copy.deepcopy(
        project.data
    )

    success, errors = project.add_instrument(
        "test_instrument",
        make_instrument(
            sf2_bank=True
        )
    )

    assert success is False
    assert errors

    assert project.data == before


def test_add_instrument_bool_sf2_program_rejected(
    project
):

    before = copy.deepcopy(
        project.data
    )

    success, errors = project.add_instrument(
        "test_instrument",
        make_instrument(
            sf2_program=True
        )
    )

    assert success is False
    assert errors

    assert project.data == before


def test_add_instrument_with_preexisting_error(
    project
):

    project.data[
        "mixes"
    ][
        "1:1"
    ] = "abc"

    success, errors = project.add_instrument(
        "test_instrument",
        make_instrument()
    )

    assert success is True
    assert errors == []

    assert (
        project.get_instrument(
            "test_instrument"
        )
        ==
        make_instrument()
    )

    assert project.get_mix(
        "1:1"
    ) == "abc"


#
# update_instrument()
#

def test_update_instrument_valid(
    project
):

    add_instrument_direct(
        project
    )

    replacement = make_instrument(
        name="Instrument modifié",
        sf2_bank=10,
        sf2_program=20
    )

    success, errors = project.update_instrument(
        "test_instrument",
        replacement
    )

    assert success is True
    assert errors == []

    assert (
        project.get_instrument(
            "test_instrument"
        )
        ==
        replacement
    )


def test_update_instrument_unknown(
    project
):

    before = copy.deepcopy(
        project.data
    )

    success, errors = project.update_instrument(
        "test_instrument",
        make_instrument()
    )

    assert success is False
    assert errors

    assert project.data == before


def test_update_instrument_invalid_rolls_back(
    project
):

    add_instrument_direct(
        project
    )

    before = copy.deepcopy(
        project.data
    )

    success, errors = project.update_instrument(
        "test_instrument",
        {
            "name": "",
            "sf2_bank": 0,
            "sf2_program": 0
        }
    )

    assert success is False
    assert errors

    assert project.data == before


def test_update_instrument_repairs_invalid_instrument(
    project
):

    project.data[
        "instruments"
    ][
        "test_instrument"
    ] = "abc"

    success, errors = project.update_instrument(
        "test_instrument",
        make_instrument()
    )

    assert success is True
    assert errors == []

    assert (
        project.get_instrument(
            "test_instrument"
        )
        ==
        make_instrument()
    )


def test_update_instrument_with_preexisting_error(
    project
):

    add_instrument_direct(
        project
    )

    project.data[
        "mixes"
    ][
        "1:1"
    ] = "abc"

    replacement = make_instrument(
        name="Instrument modifié",
        sf2_bank=5,
        sf2_program=10
    )

    success, errors = project.update_instrument(
        "test_instrument",
        replacement
    )

    assert success is True
    assert errors == []

    assert (
        project.get_instrument(
            "test_instrument"
        )
        ==
        replacement
    )

    assert project.get_mix(
        "1:1"
    ) == "abc"


#
# find_instrument_usage()
#

def test_find_instrument_usage_none(
    project
):

    add_instrument_direct(
        project
    )

    assert project.find_instrument_usage(
        "test_instrument"
    ) == []


def test_find_instrument_usage_program(
    project
):

    add_instrument_direct(
        project
    )

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
                "midi_channel": 1,
                "instrument":
                    "test_instrument"
            }
        }
    }

    usages = project.find_instrument_usage(
        "test_instrument"
    )

    assert usages == [
        {
            "type": "program",
            "program_id": "0:0",
            "part_id": "1"
        }
    ]


def test_find_instrument_usage_mix(
    project
):

    add_instrument_direct(
        project
    )

    project.data[
        "mixes"
    ][
        "0:0"
    ] = {
        "name": "MIX test",
        "channels": {
            "1": {
                "instrument":
                    "test_instrument"
            }
        }
    }

    usages = project.find_instrument_usage(
        "test_instrument"
    )

    assert usages == [
        {
            "type": "mix",
            "mix_id": "0:0",
            "channel_id": "1"
        }
    ]


def test_find_instrument_usage_song(
    project
):

    add_instrument_direct(
        project
    )

    project.data[
        "songs"
    ][
        "Song test"
    ] = {
        "name": "Song test",
        "channels": {
            "1": {
                "programs": {
                    "0:0": {
                        "instrument":
                            "test_instrument"
                    }
                }
            }
        }
    }

    usages = project.find_instrument_usage(
        "test_instrument"
    )

    assert usages == [
        {
            "type": "song",
            "song_id": "Song test",
            "channel_id": "1",
            "program_id": "0:0"
        }
    ]


def test_find_instrument_usage_multiple(
    project
):

    add_instrument_direct(
        project
    )

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
                "midi_channel": 1,
                "instrument":
                    "test_instrument"
            }
        }
    }

    project.data[
        "mixes"
    ][
        "0:0"
    ] = {
        "name": "MIX test",
        "channels": {
            "1": {
                "instrument":
                    "test_instrument"
            }
        }
    }

    project.data[
        "songs"
    ][
        "Song test"
    ] = {
        "name": "Song test",
        "channels": {
            "1": {
                "programs": {
                    "0:0": {
                        "instrument":
                            "test_instrument"
                    }
                }
            }
        }
    }

    usages = project.find_instrument_usage(
        "test_instrument"
    )

    assert len(
        usages
    ) == 3

    assert {
        usage["type"]
        for usage in usages
    } == {
        "program",
        "mix",
        "song"
    }


def test_find_instrument_usage_corrupt_program(
    project
):

    project.data[
        "programs"
    ][
        "0:0"
    ] = "abc"

    assert project.find_instrument_usage(
        "test_instrument"
    ) == []


def test_find_instrument_usage_corrupt_mix(
    project
):

    project.data[
        "mixes"
    ][
        "0:0"
    ] = "abc"

    assert project.find_instrument_usage(
        "test_instrument"
    ) == []


def test_find_instrument_usage_corrupt_song(
    project
):

    project.data[
        "songs"
    ][
        "Song test"
    ] = "abc"

    assert project.find_instrument_usage(
        "test_instrument"
    ) == []


def test_find_instrument_usage_corrupt_nested_structures(
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

    project.data[
        "mixes"
    ][
        "0:0"
    ] = {
        "name": "MIX test",
        "channels": {
            "1": "abc"
        }
    }

    project.data[
        "songs"
    ][
        "Song test"
    ] = {
        "name": "Song test",
        "channels": {
            "1": {
                "programs": {
                    "0:0": "abc"
                }
            }
        }
    }

    assert project.find_instrument_usage(
        "test_instrument"
    ) == []


#
# remove_instrument()
#

def test_remove_instrument_valid(
    project
):

    add_instrument_direct(
        project
    )

    success, errors = project.remove_instrument(
        "test_instrument"
    )

    assert success is True
    assert errors == []

    assert project.get_instrument(
        "test_instrument"
    ) is None


def test_remove_instrument_unknown(
    project
):

    before = copy.deepcopy(
        project.data
    )

    success, errors = project.remove_instrument(
        "test_instrument"
    )

    assert success is False
    assert errors

    assert project.data == before


def test_remove_instrument_used_by_program(
    project
):

    add_instrument_direct(
        project
    )

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
                "midi_channel": 1,
                "instrument":
                    "test_instrument"
            }
        }
    }

    success, errors = project.remove_instrument(
        "test_instrument"
    )

    assert success is False
    assert errors

    assert project.get_instrument(
        "test_instrument"
    ) is not None


def test_remove_instrument_used_by_mix(
    project
):

    add_instrument_direct(
        project
    )

    project.data[
        "mixes"
    ][
        "0:0"
    ] = {
        "name": "MIX test",
        "channels": {
            "1": {
                "instrument":
                    "test_instrument"
            }
        }
    }

    success, errors = project.remove_instrument(
        "test_instrument"
    )

    assert success is False
    assert errors

    assert project.get_instrument(
        "test_instrument"
    ) is not None


def test_remove_instrument_used_by_song(
    project
):

    add_instrument_direct(
        project
    )

    project.data[
        "songs"
    ][
        "Song test"
    ] = {
        "name": "Song test",
        "channels": {
            "1": {
                "programs": {
                    "0:0": {
                        "instrument":
                            "test_instrument"
                    }
                }
            }
        }
    }

    success, errors = project.remove_instrument(
        "test_instrument"
    )

    assert success is False
    assert errors

    assert project.get_instrument(
        "test_instrument"
    ) is not None


def test_remove_instrument_with_preexisting_error(
    project
):

    add_instrument_direct(
        project
    )

    project.data[
        "mixes"
    ][
        "1:1"
    ] = "abc"

    success, errors = project.remove_instrument(
        "test_instrument"
    )

    assert success is True
    assert errors == []

    assert project.get_instrument(
        "test_instrument"
    ) is None

    assert project.get_mix(
        "1:1"
    ) == "abc"


def test_remove_instrument_with_corrupt_structures(
    project
):

    add_instrument_direct(
        project
    )

    project.data[
        "programs"
    ][
        "0:0"
    ] = "abc"

    project.data[
        "mixes"
    ][
        "0:0"
    ] = {
        "name": "MIX invalide",
        "channels": "abc"
    }

    project.data[
        "songs"
    ][
        "Song test"
    ] = {
        "name": "Song invalide",
        "channels": {
            "1": "abc"
        }
    }

    success, errors = project.remove_instrument(
        "test_instrument"
    )

    assert success is True
    assert errors == []

    assert project.get_instrument(
        "test_instrument"
    ) is None

#
# get_instruments()
#

def test_get_instruments(
    project
):

    add_instrument_direct(
        project,
        "instrument_1"
    )

    instruments = project.get_instruments()

    assert instruments is project.data[
        "instruments"
    ]

    assert "instrument_1" in instruments


#
# get_instrument()
#

def test_get_instrument_existing(
    project
):

    add_instrument_direct(
        project,
        "instrument_1"
    )

    assert (
        project.get_instrument(
            "instrument_1"
        )
        ==
        make_instrument()
    )


def test_get_instrument_unknown(
    project
):

    assert project.get_instrument(
        "unknown"
    ) is None


#
# resolve_part_instrument()
#

def test_resolve_part_instrument_global(
    project
):

    add_instrument_direct(
        project,
        "instrument_1"
    )

    part = {
        "instrument": "instrument_1"
    }

    assert (
        project.resolve_part_instrument(
            part
        )
        ==
        make_instrument()
    )


def test_resolve_part_instrument_global_has_priority(
    project
):

    add_instrument_direct(
        project,
        "instrument_1"
    )

    part = {
        "instrument": "instrument_1",
        "name": "Legacy",
        "sf2_bank": 10,
        "sf2_program": 20
    }

    assert (
        project.resolve_part_instrument(
            part
        )
        ==
        make_instrument()
    )


def test_resolve_part_instrument_unknown_global_falls_back(
    project
):

    part = {
        "instrument": "unknown",
        "name": "Legacy",
        "sf2_bank": 10,
        "sf2_program": 20
    }

    assert project.resolve_part_instrument(
        part
    ) == {
        "name": "Legacy",
        "sf2_bank": 10,
        "sf2_program": 20
    }


def test_resolve_part_instrument_legacy(
    project
):

    part = {
        "name": "Legacy",
        "sf2_bank": 10,
        "sf2_program": 20
    }

    assert project.resolve_part_instrument(
        part
    ) == {
        "name": "Legacy",
        "sf2_bank": 10,
        "sf2_program": 20
    }


def test_resolve_part_instrument_legacy_default_name(
    project
):

    part = {
        "sf2_bank": 10,
        "sf2_program": 20
    }

    assert project.resolve_part_instrument(
        part
    ) == {
        "name": "Non configuré",
        "sf2_bank": 10,
        "sf2_program": 20
    }


def test_resolve_part_instrument_incomplete_legacy(
    project
):

    assert project.resolve_part_instrument(
        {
            "sf2_bank": 10
        }
    ) is None

    assert project.resolve_part_instrument(
        {
            "sf2_program": 20
        }
    ) is None


def test_resolve_part_instrument_invalid_part(
    project
):

    for part in (
        None,
        "abc",
        [],
        123
    ):

        assert project.resolve_part_instrument(
            part
        ) is None


def test_resolve_part_instrument_unknown_global_without_fallback(
    project
):

    assert project.resolve_part_instrument(
        {
            "instrument": "unknown"
        }
    ) is None


#
# list_instruments()
#

def test_list_instruments_sorted(
    project
):

    add_instrument_direct(
        project,
        "z_instrument"
    )

    add_instrument_direct(
        project,
        "a_instrument"
    )

    instruments = project.list_instruments()

    assert [
        instrument_id
        for instrument_id, instrument
        in instruments
    ] == [
        "a_instrument",
        "z_instrument"
    ]


def test_list_instruments_empty(
    project
):

    assert project.list_instruments() == []


#
# count_instruments()
#

def test_count_instruments_empty(
    project
):

    assert project.count_instruments() == 0


def test_count_instruments(
    project
):

    add_instrument_direct(
        project,
        "instrument_1"
    )

    add_instrument_direct(
        project,
        "instrument_2"
    )

    assert project.count_instruments() == 2
