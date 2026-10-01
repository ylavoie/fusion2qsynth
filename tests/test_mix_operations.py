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
