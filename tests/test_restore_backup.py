#!/usr/bin/env python3

import os
import json
import copy
import tempfile

from fusion_project import (
    FusionProject
)


def write_json(
    filename,
    data
):

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )


def read_json(
    filename
):

    with open(
        filename,
        encoding="utf-8"
    ) as f:

        return json.load(
            f
        )


def make_valid_project():

    project = FusionProject.__new__(
        FusionProject
    )

    project.filename = "fusion.json"
    project.data = {}
    project.file_time = 0

    return project._empty_project_data()


def assert_fusion_unchanged(
    expected
):

    current = read_json(
        "fusion.json"
    )

    assert current == expected, (
        "fusion.json a été modifié "
        "malgré l'échec de restauration."
    )


def assert_no_restore_temp():

    assert not os.path.exists(
        "fusion.json.restore.tmp"
    ), (
        "Le fichier temporaire de "
        "restauration existe encore."
    )


def test_missing_backup():

    print()
    print(
        "TEST 1 - Backup inexistant"
    )

    original = make_valid_project()

    original[
        "mixes"
    ][
        "0:0"
    ] = {
        "name": "Projet original",
        "channels": {}
    }

    write_json(
        "fusion.json",
        original
    )

    result = (
        FusionProject.restore_from_backup(
            "inexistant.json"
        )
    )

    assert result is None

    assert_fusion_unchanged(
        original
    )

    assert_no_restore_temp()

    print(
        "OK"
    )


def test_broken_json():

    print()
    print(
        "TEST 2 - JSON cassé"
    )

    original = make_valid_project()

    original[
        "mixes"
    ][
        "0:0"
    ] = {
        "name": "Projet original",
        "channels": {}
    }

    write_json(
        "fusion.json",
        original
    )

    with open(
        "broken.bak",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            '{ "format_version": '
        )

    result = (
        FusionProject.restore_from_backup(
            "broken.bak"
        )
    )

    assert result is None

    assert_fusion_unchanged(
        original
    )

    assert_no_restore_temp()

    print(
        "OK"
    )


def test_invalid_structure():

    print()
    print(
        "TEST 3 - Structure invalide"
    )

    original = make_valid_project()

    original[
        "mixes"
    ][
        "0:0"
    ] = {
        "name": "Projet original",
        "channels": {}
    }

    write_json(
        "fusion.json",
        original
    )

    invalid = make_valid_project()

    #
    # JSON valide syntaxiquement et structure
    # racine valide, mais erreur de validation
    # métier.
    #
    invalid[
        "mixes"
    ][
        "def"
    ] = {
        "name": "MIX invalide",
        "channels": {}
    }

    write_json(
        "invalid.bak",
        invalid
    )

    result = (
        FusionProject.restore_from_backup(
            "invalid.bak"
        )
    )

    assert result is None

    assert_fusion_unchanged(
        original
    )

    assert_no_restore_temp()

    print(
        "OK"
    )


def test_legacy_migration():

    print()
    print(
        "TEST 4 - Backup legacy avec migration"
    )

    original = make_valid_project()

    original[
        "mixes"
    ][
        "0:0"
    ] = {
        "name": "Projet original",
        "channels": {}
    }

    write_json(
        "fusion.json",
        original
    )

    legacy = make_valid_project()

    #
    # SONG pré-2.9 :
    # bank/program/instrument directement
    # dans le canal.
    #
    legacy[
        "songs"
    ][
        "Legacy song"
    ] = {
        "name": "Legacy song",
        "channels": {
            "2": {
                "volume": 127,
                "pan": 64,
                "bank": 0,
                "program": 35,
                "expression": 127,
                "chorus": 35,
                "reverb": 0,
                "instrument": "synth_bass_1"
            }
        }
    }

    #
    # L'instrument référencé doit exister pour
    # que le projet restauré soit valide.
    #
    legacy[
        "instruments"
    ][
        "synth_bass_1"
    ] = {
      "name": "Synth Bass 1",
      "sf2_bank": 0,
      "sf2_program": 38
    }

    write_json(
        "legacy.bak",
        legacy
    )

    #
    # Vérifier ensuite que la restauration
    # n'a pas modifié le backup original.
    #
    legacy_before = copy.deepcopy(
        read_json(
            "legacy.bak"
        )
    )

    result = (
        FusionProject.restore_from_backup(
            "legacy.bak"
        )
    )

    assert result is not None, (
        "La restauration legacy a échoué."
    )

    assert result.filename == (
        "fusion.json"
    )

    assert_no_restore_temp()

    #
    # Le backup source doit rester intact.
    #
    legacy_after = read_json(
        "legacy.bak"
    )

    assert legacy_after == legacy_before, (
        "Le backup legacy original "
        "a été modifié."
    )

    #
    # Vérifier la migration sur fusion.json.
    #
    restored = read_json(
        "fusion.json"
    )

    channel = (
        restored[
            "songs"
        ][
            "Legacy song"
        ][
            "channels"
        ][
            "2"
        ]
    )

    assert "bank" not in channel
    assert "program" not in channel
    assert "instrument" not in channel

    assert channel[
        "volume"
    ] == 127

    assert channel[
        "pan"
    ] == 64

    assert channel[
        "reverb"
    ] == 0

    assert channel[
        "chorus"
    ] == 35

    assert channel[
        "programs"
    ] == {
        "0:35": {
            "instrument":
                "synth_bass_1"
        }
    }

    #
    # Le projet retourné doit correspondre
    # au fichier installé.
    #
    assert result.data == restored

    print(
        "OK"
    )
