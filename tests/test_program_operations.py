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
