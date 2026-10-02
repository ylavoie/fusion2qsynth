def test_bank_name_rejects_noncanonical_id(
    project
):

    success, errors = project.set_bank_name(
        "program",
        "01",
        "Test"
    )

    assert success is False
    assert errors


def test_bank_name_rejects_bool(
    project
):

    success, errors = project.set_bank_name(
        "program",
        True,
        "Test"
    )

    assert success is False
    assert errors


def test_bank_name_can_be_set(
    project
):

    success, errors = project.set_bank_name(
        "program",
        "1",
        "Test"
    )

    assert success is True
    assert errors == []

    assert project.get_custom_bank_name(
        "program",
        1
    ) == "Test"


def test_bank_name_can_be_removed(
    project
):

    project.set_bank_name(
        "program",
        1,
        "Test"
    )

    success, errors = project.set_bank_name(
        "program",
        1,
        None
    )

    assert success is True
    assert errors == []

    assert project.get_custom_bank_name(
        "program",
        1
    ) is None

#
# _validate_bank_names()
#

def test_validate_bank_names_valid(
    project
):

    project.data[
        "banks"
    ][
        "program"
    ] = {
        "0": "Preset",
        "127": "User"
    }

    assert project._validate_bank_names(
        "program"
    ) == []


def test_validate_bank_names_noncanonical_id(
    project
):

    project.data[
        "banks"
    ][
        "program"
    ] = {
        "01": "Test"
    }

    assert project._validate_bank_names(
        "program"
    ) == [
        "Banque PROGRAM 01 : identifiant invalide"
    ]


def test_validate_bank_names_out_of_range(
    project
):

    project.data[
        "banks"
    ][
        "program"
    ] = {
        "128": "Test"
    }

    assert project._validate_bank_names(
        "program"
    ) == [
        "Banque PROGRAM 128 : identifiant invalide"
    ]


def test_validate_bank_names_invalid_name(
    project
):

    project.data[
        "banks"
    ][
        "mix"
    ] = {
        "1": "   "
    }

    assert project._validate_bank_names(
        "mix"
    ) == [
        "Banque MIX 1 : nom invalide"
    ]

def test_validate_banks_valid(
    project
):

    project.data[
        "banks"
    ] = {
        "program": {},
        "mix": {}
    }

    assert project._validate_banks() == []


def test_validate_banks_invalid_definition(
    project
):

    project.data[
        "banks"
    ] = "abc"

    assert project._validate_banks() == [
        "Banques : définition invalide"
    ]


def test_validate_banks_missing_sections(
    project
):

    project.data[
        "banks"
    ] = {}

    assert project._validate_banks() == [
        "Banques : section mix absente",
        "Banques : section program absente"
    ]


def test_validate_banks_invalid_section(
    project
):

    project.data[
        "banks"
    ] = {
        "program": [],
        "mix": {}
    }

    assert project._validate_banks() == [
        "Banques : section program invalide"
    ]


def test_validate_banks_unknown_section(
    project
):

    project.data[
        "banks"
    ] = {
        "program": {},
        "mix": {},
        "song": {}
    }

    assert project._validate_banks() == [
        "Banques : section inconnue song"
    ]

