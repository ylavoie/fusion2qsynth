import copy
import pytest

def add_mix(
    project,
    mix_id,
    name="Test Mix",
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


def add_program(
    project,
    program_id="0:0"
):

    project.data[
        "programs"
    ][
        program_id
    ] = {
        "name": "Test Program",
        "parts": {
            "1": {
                "midi_channel": 1,
                "bank": 0,
                "program": 0
            }
        }
    }


def test_rename_mix_valid(
    project
):

    add_mix(
        project,
        "0:0"
    )

    success, errors = project.rename_mix(
        "0:0",
        "Nouveau nom"
    )

    assert success is True
    assert errors == []

    assert project.get_mix(
        "0:0"
    )["name"] == "Nouveau nom"


def test_rename_mix_unknown(
    project
):

    success, errors = project.rename_mix(
        "0:0",
        "Nouveau nom"
    )

    assert success is False
    assert errors


def test_rename_mix_invalid_name_rolls_back(
    project
):

    add_mix(
        project,
        "0:0",
        "Nom original"
    )

    success, errors = project.rename_mix(
        "0:0",
        ""
    )

    assert success is False
    assert errors

    assert project.get_mix(
        "0:0"
    )["name"] == "Nom original"


def test_rename_mix_with_preexisting_error(
    project
):

    add_mix(
        project,
        "0:0",
        "Original"
    )

    project.data[
        "mixes"
    ][
        "1:1"
    ] = "abc"

    success, errors = project.rename_mix(
        "0:0",
        "Renommé"
    )

    assert success is True
    assert errors == []

    assert project.get_mix(
        "0:0"
    )["name"] == "Renommé"

    assert project.get_mix(
        "1:1"
    ) == "abc"


def test_rename_mix_without_name_new_error_rolls_back(
    project,
    monkeypatch
):

    project.data[
        "mixes"
    ][
        "0:0"
    ] = {
        "channels": {}
    }

    mix = project.data[
        "mixes"
    ][
        "0:0"
    ]

    assert "name" not in mix

    monkeypatch.setattr(
        project,
        "get_new_blocking_errors",
        lambda before_errors: [
            "Erreur simulée"
        ]
    )

    success, errors = project.rename_mix(
        "0:0",
        "Nouveau nom"
    )

    assert success is False
    assert errors == [
        "Erreur simulée"
    ]

    assert "name" not in mix


def test_duplicate_mix_valid(
    project
):

    add_program(
        project
    )

    add_mix(
        project,
        "0:0",
        "Original",
        {
            "1": {}
        }
    )

    success, errors = project.duplicate_mix(
        "0:0",
        "0:1"
    )

    assert success is True
    assert errors == []

    duplicate = project.get_mix(
        "0:1"
    )

    assert duplicate is not None
    assert duplicate["name"] == "Original (copie)"


def test_duplicate_mix_is_deep_copy(
    project
):

    add_program(
        project
    )

    add_mix(
        project,
        "0:0",
        "Original",
        {
            "1": {
                "program": "0:0"
            }
        }
    )

    success, errors = project.duplicate_mix(
        "0:0",
        "0:1"
    )

    assert success is True
    assert errors == []

    project.get_mix(
        "0:1"
    )["channels"]["1"]["program"] = "0:1"

    assert (
        project.get_mix(
            "0:0"
        )["channels"]["1"]["program"]
        ==
        "0:0"
    )


def test_duplicate_mix_existing_destination(
    project
):

    add_mix(
        project,
        "0:0",
        "Source"
    )

    add_mix(
        project,
        "0:1",
        "Destination"
    )

    success, errors = project.duplicate_mix(
        "0:0",
        "0:1"
    )

    assert success is False
    assert errors

    assert project.get_mix(
        "0:1"
    )["name"] == "Destination"


def test_duplicate_mix_invalid_destination_rolls_back(
    project
):

    add_mix(
        project,
        "0:0",
        "Source"
    )

    success, errors = project.duplicate_mix(
        "0:0",
        "abc"
    )

    assert success is False
    assert errors

    assert "abc" not in project.get_mixes()


def test_duplicate_mix_unknown_source(
    project
):

    success, errors = project.duplicate_mix(
        "99:99",
        "0:1"
    )

    assert success is False

    assert errors == [
        "Mix source inconnu : 99:99"
    ]

    assert "0:1" not in project.get_mixes()


def test_duplicate_invalid_source_does_not_crash(
    project
):

    project.data[
        "mixes"
    ][
        "0:0"
    ] = {
        "name": None,
        "channels": {}
    }

    success, errors = project.duplicate_mix(
        "0:0",
        "0:1"
    )

    assert success is False
    assert errors

    assert "0:1" not in project.get_mixes()


def test_duplicate_mix_with_preexisting_invalid_mix(
    project
):

    add_mix(
        project,
        "0:0",
        "Original"
    )

    project.data[
        "mixes"
    ][
        "1:1"
    ] = "abc"

    success, errors = project.duplicate_mix(
        "0:0",
        "0:1"
    )

    assert success is True
    assert errors == []

    assert project.get_mix(
        "0:1"
    )["name"] == "Original (copie)"

    assert project.get_mix(
        "1:1"
    ) == "abc"


def test_duplicate_mix_rejects_source_without_valid_name(
    project
):

    project.data[
        "mixes"
    ][
        "0:0"
    ] = {
        "channels": {}
    }

    success, errors = project.duplicate_mix(
        "0:0",
        "0:1"
    )

    assert success is False

    assert errors == [
        "Mix source invalide : 0:0"
    ]

    assert "0:1" not in project.get_mixes()


@pytest.mark.parametrize(
    "name",
    [
        None,
        "",
        "   "
    ]
)
def test_duplicate_mix_rejects_invalid_source_name(
    project,
    name
):

    mix = {
        "channels": {}
    }

    if name is not None:

        mix["name"] = name

    project.data[
        "mixes"
    ][
        "0:0"
    ] = mix

    success, errors = project.duplicate_mix(
        "0:0",
        "0:1"
    )

    assert success is False
    assert errors == [
        "Mix source invalide : 0:0"
    ]

    assert "0:1" not in project.get_mixes()


def test_make_copy_name_first_copy(
    project
):

    assert project._make_copy_name(
        "Test"
    ) == "Test (copie)"


def test_make_copy_name_numbered_copy(
    project
):

    project.data[
        "mixes"
    ] = {
        "0:0": {
            "name": "Test (copie)",
            "channels": {}
        }
    }

    assert project._make_copy_name(
        "Test"
    ) == "Test (copie 2)"


def test_make_copy_name_skips_existing_numbers(
    project
):

    project.data[
        "mixes"
    ] = {
        "0:0": {
            "name": "Test (copie)",
            "channels": {}
        },
        "0:1": {
            "name": "Test (copie 2)",
            "channels": {}
        },
        "0:2": {
            "name": "Test (copie 3)",
            "channels": {}
        }
    }

    assert project._make_copy_name(
        "Test"
    ) == "Test (copie 4)"


def test_delete_empty_mixes(
    project
):

    add_mix(
        project,
        "0:0",
        "Vide"
    )

    add_mix(
        project,
        "0:1",
        "Non vide",
        {
            "1": {}
        }
    )

    success, removed = (
        project.delete_empty_mixes()
    )

    assert success is True
    assert removed == ["0:0"]

    assert "0:0" not in project.get_mixes()
    assert "0:1" in project.get_mixes()


def test_delete_empty_mixes_new_error_rolls_back(
    project,
    monkeypatch
):

    project.data[
        "mixes"
    ][
        "0:0"
    ] = {
        "name": "Mix vide",
        "channels": {}
    }

    before = copy.deepcopy(
        project.data
    )

    monkeypatch.setattr(
        project,
        "get_new_blocking_errors",
        lambda before_errors: [
            "Erreur simulée"
        ]
    )

    success, errors = (
        project.delete_empty_mixes()
    )

    assert success is False

    assert errors == [
        "Erreur simulée"
    ]

    assert project.data == before


def test_delete_empty_mixes_preserves_invalid_structures(
    project
):

    project.data["mixes"]["0:0"] = {
        "name": "Sans channels"
    }

    project.data["mixes"]["0:1"] = {
        "name": "Channels invalide",
        "channels": None
    }

    project.data["mixes"]["0:2"] = "abc"

    success, removed = (
        project.delete_empty_mixes()
    )

    assert success is True
    assert removed == []

    assert "0:0" in project.get_mixes()
    assert "0:1" in project.get_mixes()
    assert "0:2" in project.get_mixes()


def test_delete_mix_valid(
    project
):

    add_mix(
        project,
        "0:0"
    )

    success, errors = project.delete_mix(
        "0:0"
    )

    assert success is True
    assert errors == []
    assert "0:0" not in project.get_mixes()


def test_delete_mix_new_error_rolls_back(
    project,
    monkeypatch
):

    project.data[
        "mixes"
    ][
        "0:0"
    ] = {
        "name": "Mix",
        "channels": {}
    }

    before = copy.deepcopy(
        project.data
    )

    monkeypatch.setattr(
        project,
        "get_new_blocking_errors",
        lambda before_errors: [
            "Erreur simulée"
        ]
    )

    success, errors = project.delete_mix(
        "0:0"
    )

    assert success is False

    assert errors == [
        "Erreur simulée"
    ]

    assert project.data == before


def test_delete_mix_unknown(
    project
):

    success, errors = project.delete_mix(
        "0:0"
    )

    assert success is False
    assert errors


def test_delete_invalid_mix(
    project
):

    project.data[
        "mixes"
    ][
        "0:0"
    ] = "abc"

    success, errors = project.delete_mix(
        "0:0"
    )

    assert success is True
    assert errors == []
    assert "0:0" not in project.get_mixes()


def test_mix_rejects_noncanonical_id(
    project
):

    mix = {
        "name": "Test",
        "channels": {}
    }

    errors = project._validate_mix_data(
        "01:2",
        mix
    )

    assert (
        "MIX 01:2 : identifiant invalide."
        in errors
    )


def test_mix_rejects_out_of_range_id(
    project
):

    mix = {
        "name": "Test",
        "channels": {}
    }

    errors = project._validate_mix_data(
        "128:0",
        mix
    )

    assert (
        "MIX 128:0 : identifiant hors limites."
        in errors
    )


def test_mix_rejects_unknown_field(
    project
):

    mix = {
        "name": "Test",
        "channels": {},
        "unknown": 123
    }

    errors = project._validate_mix_data(
        "0:0",
        mix
    )

    assert (
        "0:0 : champ inconnu 'unknown'."
        in errors
    )


#
# mix_has_channels()
#

def test_mix_has_channels_unknown(
    project
):

    assert project.mix_has_channels(
        "1:1"
    ) is False


def test_mix_has_channels_empty(
    project
):

    project.data[
        "mixes"
    ][
        "1:1"
    ] = {
        "name": "Mix test",
        "channels": {}
    }

    assert project.mix_has_channels(
        "1:1"
    ) is False


def test_mix_has_channels_configured(
    project
):

    project.data[
        "mixes"
    ][
        "1:1"
    ] = {
        "name": "Mix test",
        "channels": {
            "1": {}
        }
    }

    assert project.mix_has_channels(
        "1:1"
    ) is True


def test_update_mix_channel_valid(
    project
):

    add_program(
        project
    )

    add_mix(
        project,
        "0:0",
        "Original",
        {
            "1": {}
        }
    )

    success, errors = project.update_mix_channel(
        "0:0",
        "1",
        updates={
            "program": "0:0"
        }
    )

    assert success is True
    assert errors == []

    assert project.get_mix(
        "0:0"
    )["channels"]["1"]["program"] == "0:0"


def test_update_mix_channel_remove_field(
    project
):

    add_mix(
        project,
        "0:0",
        "Original",
        {
            "1": {
                "volume": 100
            }
        }
    )

    success, errors = project.update_mix_channel(
        "0:0",
        "1",
        remove_fields=[
            "volume"
        ]
    )

    assert success is True
    assert errors == []

    assert (
        "volume"
        not in project.get_mix(
            "0:0"
        )["channels"]["1"]
    )


def test_update_mix_channel_invalid_channels(
    project
):

    project.data[
        "mixes"
    ][
        "1:1"
    ] = {
        "name": "Mix test",
        "channels": "abc"
    }

    success, errors = project.update_mix_channel(
        "1:1",
        "1",
        {
            "volume": 100
        }
    )

    assert success is False
    assert errors

    assert project.get_mix(
        "1:1"
    )["channels"] == "abc"


def test_update_mix_channel_invalid_rolls_back(
    project
):

    add_program(
        project
    )

    add_mix(
        project,
        "0:0",
        "Original",
        {
            "1": {
                "program": "0:0"
            }
        }
    )

    success, errors = project.update_mix_channel(
        "0:0",
        "1",
        updates={
            "program": "0:999"
        }
    )

    assert success is False
    assert errors

    assert project.get_mix(
        "0:0"
    )["channels"]["1"]["program"] == "0:0"


def test_update_mix_channel_unknown_mix(
    project
):

    success, errors = project.update_mix_channel(
        "0:0",
        "1",
        updates={
            "program": "0:0"
        }
    )

    assert success is False
    assert errors


def test_update_mix_channel_unknown_channel(
    project
):

    add_mix(
        project,
        "0:0"
    )

    success, errors = project.update_mix_channel(
        "0:0",
        "1",
        updates={
            "program": "0:0"
        }
    )

    assert success is False
    assert errors


def test_update_mix_channel_with_preexisting_error(
    project
):

    add_program(
        project
    )

    add_mix(
        project,
        "0:0",
        "Original",
        {
            "1": {}
        }
    )

    project.data[
        "mixes"
    ][
        "1:1"
    ] = "abc"

    success, errors = project.update_mix_channel(
        "0:0",
        "1",
        updates={
            "program": "0:0"
        }
    )

    assert success is True
    assert errors == []

    assert project.get_mix(
        "0:0"
    )["channels"]["1"]["program"] == "0:0"

    assert project.get_mix(
        "1:1"
    ) == "abc"


def test_replace_mix_channels_existing_mix(
    project
):

    add_program(
        project
    )

    add_mix(
        project,
        "0:0",
        "Original"
    )

    channels = {
        "1": {
            "program": "0:0"
        }
    }

    success, errors = project.replace_mix_channels(
        "0:0",
        channels
    )

    assert success is True
    assert errors == []

    assert project.get_mix(
        "0:0"
    )["channels"] == channels


def test_replace_mix_channels_creates_mix(
    project
):

    add_program(
        project
    )

    channels = {
        "1": {
            "program": "0:0"
        }
    }

    success, errors = project.replace_mix_channels(
        "0:0",
        channels
    )

    assert success is True
    assert errors == []

    mix = project.get_mix(
        "0:0"
    )

    assert mix is not None
    assert mix["name"] == "Fusion Mix 0:0"
    assert mix["channels"] == channels


def test_replace_mix_channels_invalid_channels_rolls_back(
    project
):

    add_program(
        project
    )

    add_mix(
        project,
        "0:0",
        "Original",
        {
            "1": {
                "program": "0:0"
            }
        }
    )

    success, errors = project.replace_mix_channels(
        "0:0",
        "abc"
    )

    assert success is False
    assert errors

    assert project.get_mix(
        "0:0"
    )["channels"] == {
        "1": {
            "program": "0:0"
        }
    }


def test_replace_mix_channels_invalid_mix_id_rolls_back(
    project
):

    success, errors = project.replace_mix_channels(
        "abc",
        {}
    )

    assert success is False
    assert errors

    assert "abc" not in project.get_mixes()


def test_replace_mix_channels_invalid_existing_mix_does_not_crash(
    project
):

    project.data[
        "mixes"
    ][
        "0:0"
    ] = "abc"

    success, errors = project.replace_mix_channels(
        "0:0",
        {}
    )

    assert success is False
    assert errors

    assert project.get_mix(
        "0:0"
    ) == "abc"


def test_replace_mix_channels_with_preexisting_error(
    project
):

    add_program(
        project
    )

    add_mix(
        project,
        "0:0",
        "Original"
    )

    project.data[
        "mixes"
    ][
        "1:1"
    ] = "abc"

    channels = {
        "1": {
            "program": "0:0"
        }
    }

    success, errors = project.replace_mix_channels(
        "0:0",
        channels
    )

    assert success is True
    assert errors == []

    assert project.get_mix(
        "0:0"
    )["channels"] == channels

    assert project.get_mix(
        "1:1"
    ) == "abc"


def test_validate_mix_unknown(
    project
):

    errors = project.validate_mix(
        "0:0"
    )

    assert errors
    assert any(
        "Mix inconnu" in error
        for error in errors
    )


def test_validate_mix_invalid_definition(
    project
):

    project.data[
        "mixes"
    ][
        "0:0"
    ] = "abc"

    errors = project.validate_mix(
        "0:0"
    )

    assert errors
    assert any(
        "définition invalide" in error
        for error in errors
    )


def test_validate_mix_missing_channels(
    project
):

    project.data[
        "mixes"
    ][
        "0:0"
    ] = {
        "name": "Test"
    }

    errors = project.validate_mix(
        "0:0"
    )

    assert any(
        "channels absent" in error
        for error in errors
    )


def test_validate_mix_invalid_channels(
    project
):

    project.data[
        "mixes"
    ][
        "0:0"
    ] = {
        "name": "Test",
        "channels": "abc"
    }

    errors = project.validate_mix(
        "0:0"
    )

    assert any(
        "channels invalide" in error
        for error in errors
    )


def test_validate_mix_channel_invalid_channel_id(
    project
):

    errors = project._validate_mix_channel_data(
        "0:0",
        "abc",
        {}
    )

    assert any(
        "canal MIDI invalide" in error
        for error in errors
    )


def test_validate_mix_channel_noncanonical_channel_id(
    project
):

    errors = project._validate_mix_channel_data(
        "0:0",
        "01",
        {}
    )

    assert any(
        "canal MIDI invalide" in error
        for error in errors
    )


def test_validate_mix_channel_out_of_range(
    project
):

    errors = project._validate_mix_channel_data(
        "0:0",
        "17",
        {}
    )

    assert any(
        "canal MIDI hors limites" in error
        for error in errors
    )


def test_validate_mix_channel_invalid_definition(
    project
):

    errors = project._validate_mix_channel_data(
        "0:0",
        "1",
        "abc"
    )

    assert any(
        "définition invalide" in error
        for error in errors
    )


def test_validate_mix_channel_unknown_field(
    project
):

    errors = project._validate_mix_channel_data(
        "0:0",
        "1",
        {
            "unknown": 1
        }
    )

    assert any(
        "champ inconnu" in error
        for error in errors
    )


def test_validate_mix_channel_program_not_string(
    project
):

    errors = project._validate_mix_channel_data(
        "0:0",
        "1",
        {
            "program": 123
        }
    )

    assert any(
        "PROGRAM Fusion invalide" in error
        for error in errors
    )


def test_validate_mix_channel_program_malformed(
    project
):

    errors = project._validate_mix_channel_data(
        "0:0",
        "1",
        {
            "program": "abc"
        }
    )

    assert any(
        "PROGRAM Fusion invalide" in error
        for error in errors
    )


def test_validate_mix_channel_program_noncanonical(
    project
):

    errors = project._validate_mix_channel_data(
        "0:0",
        "1",
        {
            "program": "01:2"
        }
    )

    assert any(
        "PROGRAM invalide" in error
        for error in errors
    )


def test_validate_mix_channel_bank_out_of_range(
    project
):

    errors = project._validate_mix_channel_data(
        "0:0",
        "1",
        {
            "program": "128:0"
        }
    )

    assert any(
        "bank Fusion hors limites" in error
        for error in errors
    )


def test_validate_mix_channel_program_out_of_range(
    project
):

    errors = project._validate_mix_channel_data(
        "0:0",
        "1",
        {
            "program": "0:128"
        }
    )

    assert any(
        "program Fusion hors limites" in error
        for error in errors
    )


def test_validate_mix_channel_unknown_program(
    project
):

    errors = project._validate_mix_channel_data(
        "0:0",
        "1",
        {
            "program": "0:0"
        }
    )

    assert any(
        "PROGRAM global 0:0 inexistant" in error
        for error in errors
    )


def test_validate_mix_channel_invalid_instrument(
    project
):

    errors = project._validate_mix_channel_data(
        "0:0",
        "1",
        {
            "instrument": ""
        }
    )

    assert any(
        "instrument invalide" in error
        for error in errors
    )


def test_validate_mix_channel_unknown_instrument(
    project
):

    errors = project._validate_mix_channel_data(
        "0:0",
        "1",
        {
            "instrument": "unknown"
        }
    )

    assert any(
        "instrument unknown inexistant" in error
        for error in errors
    )


def test_validate_mix_channel_valid_ranges(
    project
):

    errors = project._validate_mix_channel_data(
        "0:0",
        "1",
        {
            "note_min": 36,
            "note_max": 84,
            "velocity_min": 1,
            "velocity_max": 127
        }
    )

    assert errors == []


def test_validate_mix_channel_incomplete_note_range(
    project
):

    errors = project._validate_mix_channel_data(
        "0:0",
        "1",
        {
            "note_min": 36
        }
    )

    assert any(
        "zone de notes incomplète" in error
        for error in errors
    )


def test_validate_mix_channel_invalid_note_range(
    project
):

    errors = project._validate_mix_channel_data(
        "0:0",
        "1",
        {
            "note_min": 84,
            "note_max": 36
        }
    )

    assert any(
        "zone de notes invalide" in error
        for error in errors
    )


def test_validate_mix_channel_invalid_note_type(
    project
):

    errors = project._validate_mix_channel_data(
        "0:0",
        "1",
        {
            "note_min": True,
            "note_max": 84
        }
    )

    assert any(
        "zone de notes invalide" in error
        for error in errors
    )


def test_validate_mix_channel_incomplete_velocity_range(
    project
):

    errors = project._validate_mix_channel_data(
        "0:0",
        "1",
        {
            "velocity_min": 1
        }
    )

    assert any(
        "plage de vélocité incomplète" in error
        for error in errors
    )


def test_validate_mix_channel_invalid_velocity_range(
    project
):

    errors = project._validate_mix_channel_data(
        "0:0",
        "1",
        {
            "velocity_min": 100,
            "velocity_max": 50
        }
    )

    assert any(
        "plage de vélocité invalide" in error
        for error in errors
    )


def test_validate_mix_channel_invalid_velocity_type(
    project
):

    errors = project._validate_mix_channel_data(
        "0:0",
        "1",
        {
            "velocity_min": True,
            "velocity_max": 127
        }
    )

    assert any(
        "plage de vélocité invalide" in error
        for error in errors
    )
