import copy


def add_program(
    project,
    program_id="0:0",
    name="Program test"
):

    bank_text, program_text = (
        program_id.split(
            ":",
            1
        )
    )

    project.data[
        "programs"
    ][
        program_id
    ] = {
        "name": name,
        "parts": {
            "1": {
                "bank": int(
                    bank_text
                ),
                "program": int(
                    program_text
                ),
                "midi_channel": 1
            }
        }
    }


def add_mix_reference(
    project,
    program_id="0:0"
):

    project.data[
        "mixes"
    ][
        "1:1"
    ] = {
        "name": "Mix test",
        "channels": {
            "1": {
                "program": program_id
            }
        }
    }


#
# rename_program()
#

def test_rename_program_valid(
    project
):

    add_program(
        project
    )

    success, errors = project.rename_program(
        "0:0",
        "Nouveau nom"
    )

    assert success is True
    assert errors == []

    assert project.get_program(
        "0:0"
    )["name"] == "Nouveau nom"


def test_rename_program_unknown(
    project
):

    success, errors = project.rename_program(
        "0:0",
        "Nouveau nom"
    )

    assert success is False
    assert errors


def test_rename_program_invalid_structure(
    project
):

    project.data[
        "programs"
    ][
        "0:0"
    ] = "abc"

    success, errors = project.rename_program(
        "0:0",
        "Nouveau nom"
    )

    assert success is False
    assert errors

    assert project.get_program(
        "0:0"
    ) == "abc"


def test_rename_program_invalid_name_rolls_back(
    project
):

    add_program(
        project,
        name="Original"
    )

    success, errors = project.rename_program(
        "0:0",
        ""
    )

    assert success is False
    assert errors

    assert project.get_program(
        "0:0"
    )["name"] == "Original"


def test_rename_program_with_preexisting_error(
    project
):

    add_program(
        project
    )

    project.data[
        "mixes"
    ][
        "1:1"
    ] = "abc"

    success, errors = project.rename_program(
        "0:0",
        "Nouveau nom"
    )

    assert success is True
    assert errors == []

    assert project.get_program(
        "0:0"
    )["name"] == "Nouveau nom"

    assert project.get_mix(
        "1:1"
    ) == "abc"


def test_rename_program_without_name_new_error_rolls_back(
    project,
    monkeypatch
):

    project.data[
        "programs"
    ][
        "0:0"
    ] = {
        "parts": {}
    }

    program = project.data[
        "programs"
    ][
        "0:0"
    ]

    assert "name" not in program

    monkeypatch.setattr(
        project,
        "get_new_blocking_errors",
        lambda before_errors: [
            "Erreur simulée"
        ]
    )

    success, errors = project.rename_program(
        "0:0",
        "Nouveau nom"
    )

    assert success is False
    assert errors == [
        "Erreur simulée"
    ]

    assert "name" not in program


#
# delete_program()
#

def test_delete_program_valid(
    project
):

    add_program(
        project
    )

    success, errors = project.delete_program(
        "0:0"
    )

    assert success is True
    assert errors == []

    assert project.get_program(
        "0:0"
    ) is None


def test_delete_program_unknown(
    project
):

    success, errors = project.delete_program(
        "0:0"
    )

    assert success is False
    assert errors


def test_delete_invalid_program(
    project
):

    project.data[
        "programs"
    ][
        "0:0"
    ] = "abc"

    success, errors = project.delete_program(
        "0:0"
    )

    assert success is True
    assert errors == []

    assert project.get_program(
        "0:0"
    ) is None


def test_delete_referenced_program_rolls_back(
    project
):

    add_program(
        project
    )

    add_mix_reference(
        project
    )

    success, errors = project.delete_program(
        "0:0"
    )

    assert success is False
    assert errors

    assert project.get_program(
        "0:0"
    ) is not None

    assert (
        project.get_mix(
            "1:1"
        )["channels"]["1"]["program"]
        ==
        "0:0"
    )


def test_delete_program_with_preexisting_error(
    project
):

    add_program(
        project
    )

    project.data[
        "mixes"
    ][
        "1:1"
    ] = "abc"

    success, errors = project.delete_program(
        "0:0"
    )

    assert success is True
    assert errors == []

    assert project.get_program(
        "0:0"
    ) is None

    assert project.get_mix(
        "1:1"
    ) == "abc"


#
# update_program_part()
#

def test_update_program_part_valid(
    project
):

    add_program(
        project
    )

    success, errors = project.update_program_part(
        "0:0",
        "1",
        {
            "midi_channel": 2
        }
    )

    assert success is True
    assert errors == []

    assert (
        project.get_program(
            "0:0"
        )["parts"]["1"]["midi_channel"]
        ==
        2
    )


def test_update_program_part_creates_program(
    project
):

    success, errors = project.update_program_part(
        "0:0",
        "1",
        {
            "bank": 0,
            "program": 0,
            "midi_channel": 1
        }
    )

    assert success is True
    assert errors == []

    program = project.get_program(
        "0:0"
    )

    assert program is not None

    assert program[
        "parts"
    ][
        "1"
    ] == {
        "bank": 0,
        "program": 0,
        "midi_channel": 1
    }


def test_update_program_part_invalid_updates(
    project
):

    add_program(
        project
    )

    before = copy.deepcopy(
        project.data
    )

    success, errors = project.update_program_part(
        "0:0",
        "1",
        "abc"
    )

    assert success is False
    assert errors

    assert project.data == before


def test_update_program_part_invalid_program_structure(
    project
):

    project.data[
        "programs"
    ][
        "0:0"
    ] = "abc"

    success, errors = project.update_program_part(
        "0:0",
        "1",
        {
            "midi_channel": 2
        }
    )

    assert success is False
    assert errors

    assert project.get_program(
        "0:0"
    ) == "abc"


def test_update_program_part_invalid_part_structure(
    project
):

    add_program(
        project
    )

    project.get_program(
        "0:0"
    )["parts"]["1"] = "abc"

    success, errors = project.update_program_part(
        "0:0",
        "1",
        {
            "midi_channel": 2
        }
    )

    assert success is False
    assert errors

    assert (
        project.get_program(
            "0:0"
        )["parts"]["1"]
        ==
        "abc"
    )


def test_update_program_part_invalid_value_rolls_back(
    project
):

    add_program(
        project
    )

    before = copy.deepcopy(
        project.data
    )

    success, errors = project.update_program_part(
        "0:0",
        "1",
        {
            "midi_channel": 99
        }
    )

    assert success is False
    assert errors

    assert project.data == before


def test_update_program_part_incoherent_program_rolls_back(
    project
):

    add_program(
        project
    )

    before = copy.deepcopy(
        project.data
    )

    success, errors = project.update_program_part(
        "0:0",
        "1",
        {
            "program": 1
        }
    )

    assert success is False
    assert errors

    assert project.data == before


def test_update_program_part_invalid_parts_structure(
    project
):

    project.data[
        "programs"
    ][
        "0:0"
    ] = {
        "name": "Test",
        "parts": "abc"
    }

    before = copy.deepcopy(
        project.data
    )

    success, errors = project.update_program_part(
        "0:0",
        1,
        {
            "instrument": "piano"
        }
    )

    assert success is False

    assert errors == [
        "0:0 : définition PART invalide."
    ]

    assert project.data == before


def test_update_program_part_with_preexisting_error(
    project
):

    add_program(
        project
    )

    project.data[
        "mixes"
    ][
        "1:1"
    ] = "abc"

    success, errors = project.update_program_part(
        "0:0",
        "1",
        {
            "midi_channel": 2
        }
    )

    assert success is True
    assert errors == []

    assert (
        project.get_program(
            "0:0"
        )["parts"]["1"]["midi_channel"]
        ==
        2
    )

    assert project.get_mix(
        "1:1"
    ) == "abc"


def test_validate_part_invalid_definition(
    project
):

    errors = project._validate_part_data(
        "0:0",
        "1",
        "abc"
    )

    assert any(
        "définition invalide" in error
        for error in errors
    )


def test_validate_part_unknown_field(
    project
):

    part = {
        "midi_channel": 1,
        "bank": 0,
        "program": 0,
        "unknown": 1
    }

    errors = project._validate_part_data(
        "0:0",
        "1",
        part
    )

    assert any(
        "champ inconnu" in error
        for error in errors
    )


def test_validate_part_missing_midi_channel(
    project
):

    part = {
        "bank": 0,
        "program": 0
    }

    errors = project._validate_part_data(
        "0:0",
        "1",
        part
    )

    assert any(
        "midi_channel absent" in error
        for error in errors
    )


def test_validate_part_invalid_midi_channel(
    project
):

    part = {
        "midi_channel": 17,
        "bank": 0,
        "program": 0
    }

    errors = project._validate_part_data(
        "0:0",
        "1",
        part
    )

    assert any(
        "canal MIDI invalide" in error
        for error in errors
    )


def test_validate_part_missing_bank(
    project
):

    part = {
        "midi_channel": 1,
        "program": 0
    }

    errors = project._validate_part_data(
        "0:0",
        "1",
        part
    )

    assert any(
        "bank Fusion absente" in error
        for error in errors
    )


def test_validate_part_invalid_bank(
    project
):

    part = {
        "midi_channel": 1,
        "bank": 128,
        "program": 0
    }

    errors = project._validate_part_data(
        "0:0",
        "1",
        part
    )

    assert any(
        "bank Fusion invalide" in error
        for error in errors
    )


def test_validate_part_missing_program(
    project
):

    part = {
        "midi_channel": 1,
        "bank": 0
    }

    errors = project._validate_part_data(
        "0:0",
        "1",
        part
    )

    assert any(
        "program Fusion absent" in error
        for error in errors
    )


def test_validate_part_invalid_program(
    project
):

    part = {
        "midi_channel": 1,
        "bank": 0,
        "program": 128
    }

    errors = project._validate_part_data(
        "0:0",
        "1",
        part
    )

    assert any(
        "program Fusion invalide" in error
        for error in errors
    )


def test_validate_part_invalid_instrument(
    project
):

    part = {
        "midi_channel": 1,
        "bank": 0,
        "program": 0,
        "instrument": ""
    }

    errors = project._validate_part_data(
        "0:0",
        "1",
        part
    )

    assert any(
        "instrument invalide" in error
        for error in errors
    )


def test_validate_part_unknown_instrument(
    project
):

    part = {
        "midi_channel": 1,
        "bank": 0,
        "program": 0,
        "instrument": "unknown"
    }

    errors = project._validate_part_data(
        "0:0",
        "1",
        part
    )

    assert any(
        "instrument unknown inexistant" in error
        for error in errors
    )


def test_validate_part_incomplete_note_range(
    project
):

    part = {
        "midi_channel": 1,
        "bank": 0,
        "program": 0,
        "note_min": 20
    }

    errors = project._validate_part_data(
        "0:0",
        "1",
        part
    )

    assert any(
        "zone de notes incomplète" in error
        for error in errors
    )


def test_validate_part_invalid_note_range(
    project
):

    part = {
        "midi_channel": 1,
        "bank": 0,
        "program": 0,
        "note_min": 100,
        "note_max": 20
    }

    errors = project._validate_part_data(
        "0:0",
        "1",
        part
    )

    assert any(
        "zone de notes invalide" in error
        for error in errors
    )


def test_validate_part_incomplete_velocity_range(
    project
):

    part = {
        "midi_channel": 1,
        "bank": 0,
        "program": 0,
        "velocity_min": 20
    }

    errors = project._validate_part_data(
        "0:0",
        "1",
        part
    )

    assert any(
        "plage de vélocité incomplète" in error
        for error in errors
    )


def test_validate_part_invalid_velocity_range(
    project
):

    part = {
        "midi_channel": 1,
        "bank": 0,
        "program": 0,
        "velocity_min": 100,
        "velocity_max": 20
    }

    errors = project._validate_part_data(
        "0:0",
        "1",
        part
    )

    assert any(
        "plage de vélocité invalide" in error
        for error in errors
    )


def test_validate_part_valid_with_ranges(
    project
):

    part = {
        "midi_channel": 1,
        "bank": 0,
        "program": 0,
        "note_min": 20,
        "note_max": 100,
        "velocity_min": 10,
        "velocity_max": 120
    }

    errors = project._validate_part_data(
        "0:0",
        "1",
        part
    )

    assert errors == []


def test_program_rejects_malformed_id(
    project
):

    program = {
        "name": "Test",
        "parts": {}
    }

    errors = project._validate_program_data(
        "abc",
        program
    )

    assert (
        "PROGRAM abc : identifiant invalide."
        in errors
    )

def test_program_rejects_noncanonical_id(
    project
):

    program = {
        "name": "Test",
        "parts": {}
    }

    errors = project._validate_program_data(
        "01:2",
        program
    )

    assert (
        "PROGRAM 01:2 : identifiant invalide."
        in errors
    )


def test_program_missing_parts(
    project
):

    add_program(
        project
    )

    del project.data[
        "programs"
    ][
        "0:0"
    ][
        "parts"
    ]

    errors = project.validate_program(
        "0:0"
    )

    assert (
        "0:0 : parts absent."
        in errors
    )


def test_program_extra_part(
    project
):

    add_program(
        project
    )

    project.data[
        "programs"
    ][
        "0:0"
    ][
        "parts"
    ][
        "2"
    ] = {
        "bank": 0,
        "program": 0,
        "midi_channel": 2
    }

    errors = project.validate_program(
        "0:0"
    )

    assert (
        "0:0 : PART 2 invalide."
        in errors
    )


def test_program_incoherent_bank(
    project
):

    add_program(
        project,
        program_id="5:10"
    )

    project.data[
        "programs"
    ][
        "5:10"
    ][
        "parts"
    ][
        "1"
    ][
        "bank"
    ] = 6

    errors = project.validate_program(
        "5:10"
    )

    assert (
        "5:10 PART 1 : "
        "bank Fusion incohérente avec l'identifiant."
        in errors
    )


def test_validate_program_invalid_id_with_valid_part_program(
    project
):

    project.data[
        "programs"
    ][
        "invalid"
    ] = {
        "name": "Invalid",
        "parts": {
            "1": {
                "midi_channel": 1,
                "bank": 0,
                "program": 0
            }
        }
    }

    errors = project._validate_program_data(
        "invalid",
        project.data[
            "programs"
        ][
            "invalid"
        ]
    )

    assert (
        "PROGRAM invalid : identifiant invalide."
        in errors
    )
