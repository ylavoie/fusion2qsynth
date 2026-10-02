import pytest

from fusion_gm_map import (
    fusion_program_bank_name,
    fusion_mix_bank_name
)

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

def test_get_program_bank_name_default(
    project
):

    assert project.get_program_bank_name(
        0
    ) == fusion_program_bank_name(
        0
    )


def test_get_program_bank_name_custom(
    project
):

    project.data["banks"]["program"]["0"] = (
        "Custom PROGRAM"
    )

    assert project.get_program_bank_name(
        0
    ) == "Custom PROGRAM"


def test_get_mix_bank_name_default(
    project
):

    assert project.get_mix_bank_name(
        0
    ) == fusion_mix_bank_name(
        0
    )


def test_get_mix_bank_name_custom(
    project
):

    project.data["banks"]["mix"]["0"] = (
        "Custom MIX"
    )

    assert project.get_mix_bank_name(
        0
    ) == "Custom MIX"


def test_get_program_banks_includes_custom_bank(
    project
):

    project.data[
        "banks"
    ][
        "program"
    ][
        "127"
    ] = "Custom"

    banks = project.get_program_banks()

    assert 127 in banks
    assert banks == sorted(
        set(banks)
    )


def test_get_mix_banks_includes_custom_bank(
    project
):

    project.data[
        "banks"
    ][
        "mix"
    ][
        "127"
    ] = "Custom"

    banks = project.get_mix_banks()

    assert 127 in banks
    assert banks == sorted(
        set(banks)
    )


def test_get_banks_dispatches_program(
    project
):

    assert project.get_banks(
        "program"
    ) == project.get_program_banks()


def test_get_banks_dispatches_mix(
    project
):

    assert project.get_banks(
        "mix"
    ) == project.get_mix_banks()


def test_get_banks_rejects_invalid_type(
    project
):

    with pytest.raises(
        ValueError,
        match="Type de banque invalide"
    ):

        project.get_banks(
            "invalid"
        )


def test_get_bank_name_dispatches_program(
    project
):

    assert project.get_bank_name(
        "program",
        0
    ) == project.get_program_bank_name(
        0
    )


def test_get_bank_name_dispatches_mix(
    project
):

    assert project.get_bank_name(
        "mix",
        0
    ) == project.get_mix_bank_name(
        0
    )


def test_get_bank_name_rejects_invalid_type(
    project
):

    with pytest.raises(
        ValueError,
        match="Type de banque invalide"
    ):

        project.get_bank_name(
            "invalid",
            0
        )


def test_set_bank_name_rejects_invalid_type(
    project
):

    success, errors = project.set_bank_name(
        "invalid",
        1,
        "Test"
    )

    assert success is False
    assert errors == [
        "Type de banque invalide : invalid"
    ]


def test_set_bank_name_rejects_invalid_bank(
    project
):

    success, errors = project.set_bank_name(
        "program",
        "abc",
        "Test"
    )

    assert success is False
    assert errors == [
        "Banque invalide."
    ]


@pytest.mark.parametrize(
    "bank",
    [
        -1,
        128
    ]
)
def test_set_bank_name_rejects_out_of_range_bank(
    project,
    bank
):

    success, errors = project.set_bank_name(
        "program",
        bank,
        "Test"
    )

    assert success is False
    assert errors == [
        "Banque invalide."
    ]


def test_set_bank_name_rejects_empty_name(
    project
):

    success, errors = project.set_bank_name(
        "program",
        1,
        "   "
    )

    assert success is False
    assert errors == [
        "Nom de banque invalide."
    ]


def test_set_bank_name_strips_name(
    project
):

    success, errors = project.set_bank_name(
        "program",
        1,
        "  Custom Bank  "
    )

    assert success is True
    assert errors == []

    assert project.get_custom_bank_name(
        "program",
        1
    ) == "Custom Bank"


def test_get_custom_bank_name_rejects_invalid_type(
    project
):

    with pytest.raises(
        ValueError,
        match="Type de banque invalide"
    ):

        project.get_custom_bank_name(
            "invalid",
            1
        )


def test_set_bank_name_new_error_rolls_back_new_name(
    project,
    monkeypatch
):

    banks = project.data[
        "banks"
    ][
        "program"
    ]

    assert "1" not in banks

    monkeypatch.setattr(
        project,
        "get_new_blocking_errors",
        lambda before_errors: [
            "Erreur simulée"
        ]
    )

    success, errors = project.set_bank_name(
        "program",
        1,
        "Test"
    )

    assert success is False
    assert errors == [
        "Erreur simulée"
    ]

    assert "1" not in banks


def test_set_bank_name_new_error_restores_old_name(
    project,
    monkeypatch
):

    banks = project.data[
        "banks"
    ][
        "program"
    ]

    banks[
        "1"
    ] = "Ancien nom"

    monkeypatch.setattr(
        project,
        "get_new_blocking_errors",
        lambda before_errors: [
            "Erreur simulée"
        ]
    )

    success, errors = project.set_bank_name(
        "program",
        1,
        "Nouveau nom"
    )

    assert success is False
    assert errors == [
        "Erreur simulée"
    ]

    assert banks[
        "1"
    ] == "Ancien nom"
