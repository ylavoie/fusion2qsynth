#!/usr/bin/env python3

import os
import json
import copy
import shutil
import tempfile

from fusion_project import (
    FusionProject
)

from fusion_constants import (
    ARCHIVE_DIR
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

    if os.path.isdir(
        ARCHIVE_DIR
    ):

        shutil.rmtree(
            ARCHIVE_DIR
        )

    assert not os.path.exists(
        "fusion.json.restore.tmp"
    ), (
        "Le fichier temporaire de "
        "restauration existe encore."
    )


def test_missing_archive():

    print()
    print(
        "TEST 1 - Archive inexistante"
    )

    original = make_valid_project()

    original["mixes"]["0:0"] = {
        "name": "Projet original",
        "channels": {}
    }

    write_json(
        "fusion.json",
        original
    )

    result = (
        FusionProject.restore_from_archive(
            "inexistante.json"
        )
    )

    assert result is None

    assert_fusion_unchanged(
        original
    )

    assert_no_restore_temp()

    print("OK")


def test_broken_json():

    print()
    print(
        "TEST 2 - Archive JSON cassée"
    )

    original = make_valid_project()

    original["mixes"]["0:0"] = {
        "name": "Projet original",
        "channels": {}
    }

    write_json(
        "fusion.json",
        original
    )

    with open(
        "broken.json",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            '{ "format_version": '
        )

    result = (
        FusionProject.restore_from_archive(
            "broken.json"
        )
    )

    assert result is None

    assert_fusion_unchanged(
        original
    )

    assert_no_restore_temp()

    print("OK")


def test_invalid_structure():

    print()
    print(
        "TEST 3 - Archive invalide"
    )

    original = make_valid_project()

    original["mixes"]["0:0"] = {
        "name": "Projet original",
        "channels": {}
    }

    write_json(
        "fusion.json",
        original
    )

    invalid = make_valid_project()

    invalid["mixes"]["def"] = {
        "name": "MIX invalide",
        "channels": {}
    }

    write_json(
        "invalid.json",
        invalid
    )

    result = (
        FusionProject.restore_from_archive(
            "invalid.json"
        )
    )

    assert result is None

    assert_fusion_unchanged(
        original
    )

    assert_no_restore_temp()

    print("OK")


def test_legacy_migration():

    print()
    print(
        "TEST 4 - Archive legacy avec migration"
    )

    original = make_valid_project()

    original["mixes"]["0:0"] = {
        "name": "Projet original",
        "channels": {}
    }

    write_json(
        "fusion.json",
        original
    )

    legacy = make_valid_project()

    legacy["songs"]["Legacy song"] = {
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
                "instrument":
                    "synth_bass_1"
            }
        }
    }

    legacy["instruments"][
        "synth_bass_1"
    ] = {
        "name": "Synth Bass 1",
        "sf2_bank": 0,
        "sf2_program": 38
    }

    write_json(
        "legacy.json",
        legacy
    )

    legacy_before = copy.deepcopy(
        read_json(
            "legacy.json"
        )
    )

    result = (
        FusionProject.restore_from_archive(
            "legacy.json"
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
    # L'archive source ne doit jamais
    # être modifiée.
    #
    legacy_after = read_json(
        "legacy.json"
    )

    assert legacy_after == legacy_before, (
        "L'archive legacy source "
        "a été modifiée."
    )

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

    assert channel["volume"] == 127
    assert channel["pan"] == 64
    assert channel["reverb"] == 0
    assert channel["chorus"] == 35

    assert channel["programs"] == {
        "0:35": {
            "instrument":
                "synth_bass_1"
        }
    }

    assert result.data == restored

    print("OK")


def test_successful_restore_archives_current():

    print()
    print(
        "TEST 5 - Restauration réussie "
        "archive le projet courant"
    )

    #
    # Projet actuellement actif.
    #
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

    #
    # Projet valide à restaurer.
    #
    restored_project = make_valid_project()

    restored_project[
        "mixes"
    ][
        "1:1"
    ] = {
        "name": "Projet restauré",
        "channels": {}
    }

    write_json(
        "restore.json",
        restored_project
    )

    #
    # Aucune archive avant la restauration.
    #
    assert not os.path.exists(
        ARCHIVE_DIR
    )

    result = (
        FusionProject.restore_from_archive(
            "restore.json"
        )
    )

    assert result is not None, (
        "La restauration valide a échoué."
    )

    #
    # Une seule archive doit avoir été créée.
    #
    assert os.path.isdir(
        ARCHIVE_DIR
    ), (
        "Le répertoire d'archives "
        "n'a pas été créé."
    )

    archives = [
        filename
        for filename in os.listdir(
            ARCHIVE_DIR
        )
        if filename.endswith(
            ".json"
        )
    ]

    assert len(archives) == 1, (
        "Une seule archive était attendue, "
        f"{len(archives)} trouvée(s)."
    )

    #
    # Cette archive doit être exactement
    # l'ancien fusion.json.
    #
    archived = read_json(
        os.path.join(
            ARCHIVE_DIR,
            archives[0]
        )
    )

    assert archived == original, (
        "L'archive créée ne correspond pas "
        "à l'ancien fusion.json."
    )

    #
    # Et fusion.json doit maintenant contenir
    # le projet restauré.
    #
    current = read_json(
        "fusion.json"
    )

    assert current == restored_project, (
        "fusion.json ne contient pas "
        "le projet restauré."
    )

    assert result.data == current

    assert_no_restore_temp()

    print(
        "OK"
    )


def test_failed_restore_creates_no_archive():

    print()
    print(
        "TEST 6 - Restauration refusée "
        "ne crée aucune archive"
    )

    #
    # Isoler complètement ce test des
    # archives créées précédemment.
    #
    if os.path.isdir(
        ARCHIVE_DIR
    ):

        shutil.rmtree(
            ARCHIVE_DIR
        )

    #
    # Projet actuellement actif.
    #
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

    #
    # Archive syntaxiquement valide,
    # mais invalide pour Fusion2QSynth.
    #
    invalid = make_valid_project()

    invalid[
        "mixes"
    ][
        "def"
    ] = {
        "name": "MIX invalide",
        "channels": {}
    }

    write_json(
        "invalid-restore.json",
        invalid
    )

    #
    # Aucun effet de bord avant le test.
    #
    assert not os.path.exists(
        ARCHIVE_DIR
    )

    result = (
        FusionProject.restore_from_archive(
            "invalid-restore.json"
        )
    )

    #
    # La restauration doit être refusée.
    #
    assert result is None, (
        "Une archive invalide a été restaurée."
    )

    #
    # Le projet actif doit être absolument
    # inchangé.
    #
    assert_fusion_unchanged(
        original
    )

    #
    # Puisque le candidat a été refusé avant
    # archive_if_changed(), aucune archive
    # du projet actif ne doit avoir été créée.
    #
    if os.path.isdir(
        ARCHIVE_DIR
    ):

        archives = [
            filename
            for filename in os.listdir(
                ARCHIVE_DIR
            )
            if filename.endswith(
                ".json"
            )
        ]

        assert not archives, (
            "Une archive a été créée malgré "
            "l'échec de la restauration."
        )

    #
    # Le temporaire doit également avoir
    # été nettoyé.
    #
    assert_no_restore_temp()

    print(
        "OK"
    )
