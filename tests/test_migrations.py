import copy

import pytest

def test_migrate_legacy_mix(
    project
):

    project.data[
        "mixes"
    ][
        "0:0"
    ] = {
        "name": "Legacy",
        "parts": {
            "1": {
                "midi_channel": 2,
                "instrument": "piano"
            },
            "2": {
                "midi_channel": 5
            }
        }
    }

    result = (
        project._migrate_legacy_mixes()
    )

    assert result == {
        "mixes": 1,
        "channels": 2,
        "instruments": 1
    }

    mix = project.data[
        "mixes"
    ][
        "0:0"
    ]

    assert "parts" not in mix

    assert mix[
        "channels"
    ] == {
        "2": {
            "instrument": "piano"
        },
        "5": {}
    }


def test_migrate_legacy_mix_ignores_modern_mix(
    project
):

    project.data[
        "mixes"
    ][
        "0:0"
    ] = {
        "name": "Modern",
        "channels": {
            "1": {}
        }
    }

    before = copy.deepcopy(
        project.data
    )

    result = (
        project._migrate_legacy_mixes()
    )

    assert result == {
        "mixes": 0,
        "channels": 0,
        "instruments": 0
    }

    assert project.data == before


def test_migrate_legacy_mix_ignores_unknown_structure(
    project
):

    project.data[
        "mixes"
    ][
        "0:0"
    ] = {
        "name": "Unknown"
    }

    before = copy.deepcopy(
        project.data
    )

    result = (
        project._migrate_legacy_mixes()
    )

    assert result[
        "mixes"
    ] == 0

    assert project.data == before


def test_migrate_legacy_mix_missing_midi_channel(
    project
):

    project.data["mixes"]["0:0"] = {
        "name": "Legacy",
        "parts": {
            "1": {}
        }
    }

    with pytest.raises(
        ValueError,
        match="midi_channel absent"
    ):

        project._migrate_legacy_mixes()


def test_migrate_legacy_mix_invalid_midi_channel(
    project
):

    project.data["mixes"]["0:0"] = {
        "name": "Legacy",
        "parts": {
            "1": {
                "midi_channel": "abc"
            }
        }
    }

    with pytest.raises(
        ValueError,
        match="midi_channel invalide"
    ):

        project._migrate_legacy_mixes()


def test_migrate_legacy_mix_out_of_range_midi_channel(
    project
):

    project.data["mixes"]["0:0"] = {
        "name": "Legacy",
        "parts": {
            "1": {
                "midi_channel": 17
            }
        }
    }

    with pytest.raises(
        ValueError,
        match="canal MIDI 17 invalide"
    ):

        project._migrate_legacy_mixes()


def test_migrate_legacy_mix_duplicate_midi_channel(
    project
):

    project.data["mixes"]["0:0"] = {
        "name": "Legacy",
        "parts": {
            "1": {
                "midi_channel": 2
            },
            "2": {
                "midi_channel": 2
            }
        }
    }

    with pytest.raises(
        ValueError,
        match="plusieurs PARTs"
    ):

        project._migrate_legacy_mixes()


def test_migrate_legacy_mixes_is_atomic(
    project
):

    project.data["mixes"] = {
        "0:0": {
            "name": "Valid legacy",
            "parts": {
                "1": {
                    "midi_channel": 1
                }
            }
        },
        "0:1": {
            "name": "Broken legacy",
            "parts": {
                "1": {}
            }
        }
    }

    before = copy.deepcopy(
        project.data
    )

    with pytest.raises(
        ValueError
    ):

        project._migrate_legacy_mixes()

    assert project.data == before


def test_migrate_legacy_song(
    project
):

    project.data["songs"]["Legacy"] = {
        "name": "Legacy",
        "channels": {
            "2": {
                "bank": 0,
                "program": 35,
                "volume": 127,
                "pan": 64,
                "expression": 100,
                "reverb": 20,
                "chorus": 30,
                "instrument": "bass"
            }
        }
    }

    result = (
        project._migrate_legacy_songs()
    )

    assert result == {
        "songs": 1,
        "channels": 1,
        "programs": 1,
        "instruments": 1
    }

    assert project.data[
        "songs"
    ][
        "Legacy"
    ][
        "channels"
    ][
        "2"
    ] == {
        "volume": 127,
        "pan": 64,
        "expression": 100,
        "reverb": 20,
        "chorus": 30,
        "programs": {
            "0:35": {
                "instrument": "bass"
            }
        }
    }


def test_migrate_legacy_song_without_program(
    project
):

    project.data["songs"]["Legacy"] = {
        "name": "Legacy",
        "channels": {
            "1": {
                "volume": 100
            }
        }
    }

    result = (
        project._migrate_legacy_songs()
    )

    assert result == {
        "songs": 1,
        "channels": 1,
        "programs": 0,
        "instruments": 0
    }

    assert project.data[
        "songs"
    ][
        "Legacy"
    ][
        "channels"
    ][
        "1"
    ] == {
        "volume": 100,
        "programs": {}
    }


def test_migrate_legacy_song_ignores_modern_channel(
    project
):

    project.data["songs"]["Modern"] = {
        "name": "Modern",
        "channels": {
            "1": {
                "programs": {
                    "0:0": {}
                }
            }
        }
    }

    before = copy.deepcopy(
        project.data
    )

    result = (
        project._migrate_legacy_songs()
    )

    assert result["songs"] == 0
    assert project.data == before


def test_migrate_legacy_song_ignores_invalid_song(
    project
):

    project.data[
        "songs"
    ][
        "Broken"
    ] = "abc"

    before = copy.deepcopy(
        project.data
    )

    result = (
        project._migrate_legacy_songs()
    )

    assert result["songs"] == 0
    assert project.data == before


def test_migrate_legacy_song_ignores_invalid_channels(
    project
):

    project.data["songs"]["Broken"] = {
        "name": "Broken",
        "channels": "abc"
    }

    before = copy.deepcopy(
        project.data
    )

    result = (
        project._migrate_legacy_songs()
    )

    assert result["songs"] == 0
    assert project.data == before


def test_migrate_legacy_song_preserves_invalid_channel(
    project
):

    project.data["songs"]["Broken"] = {
        "name": "Broken",
        "channels": {
            "1": "abc"
        }
    }

    before = copy.deepcopy(
        project.data
    )

    result = (
        project._migrate_legacy_songs()
    )

    assert result["songs"] == 0
    assert project.data == before


def test_migrate_legacy_song_preserves_unknown_structure(
    project
):

    project.data["songs"]["Unknown"] = {
        "name": "Unknown",
        "channels": {
            "1": {
                "bank": 0,
                "program": 1,
                "unexpected": 42
            }
        }
    }

    before = copy.deepcopy(
        project.data
    )

    result = (
        project._migrate_legacy_songs()
    )

    assert result["songs"] == 0
    assert project.data == before


def test_migrate_legacy_song_rejects_bank_without_program(
    project
):

    project.data["songs"]["Broken"] = {
        "name": "Broken",
        "channels": {
            "1": {
                "bank": 0
            }
        }
    }

    with pytest.raises(
        ValueError,
        match="bank/program incomplets"
    ):

        project._migrate_legacy_songs()


def test_migrate_legacy_song_rejects_program_without_bank(
    project
):

    project.data["songs"]["Broken"] = {
        "name": "Broken",
        "channels": {
            "1": {
                "program": 10
            }
        }
    }

    with pytest.raises(
        ValueError,
        match="bank/program incomplets"
    ):

        project._migrate_legacy_songs()


def test_migrate_legacy_songs_is_atomic(
    project
):

    project.data["songs"] = {
        "Good": {
            "name": "Good",
            "channels": {
                "1": {
                    "bank": 0,
                    "program": 1
                }
            }
        },
        "Broken": {
            "name": "Broken",
            "channels": {
                "2": {
                    "bank": 0
                }
            }
        }
    }

    before = copy.deepcopy(
        project.data
    )

    with pytest.raises(
        ValueError
    ):

        project._migrate_legacy_songs()

    assert project.data == before


def test_migrate_legacy_mix_ignores_invalid_mix(
    project
):

    project.data[
        "mixes"
    ][
        "0:0"
    ] = None

    before = copy.deepcopy(
        project.data
    )

    result = (
        project._migrate_legacy_mixes()
    )

    assert result == {
        "mixes": 0,
        "channels": 0,
        "instruments": 0
    }

    assert project.data == before
