#!/usr/bin/env python3

import os
import pytest
import shutil
import time

from fusion_project import (
    FusionProject
)


def test_list_backups_empty():

    assert FusionProject.list_backups() == []


def test_list_backups():

    files = (
        ("fusion.json.bak", 100),
        ("fusion.json.bak1", 2048),
        ("fusion.json.bak2", 2 * 1024 * 1024)
    )

    for filename, size in files:

        with open(
            filename,
            "wb"
        ) as f:

            f.write(
                b"x" * size
            )

    backups = FusionProject.list_backups()

    assert len(backups) == 3

    assert [
        backup["filename"]
        for backup in backups
    ] == [
        "fusion.json.bak",
        "fusion.json.bak1",
        "fusion.json.bak2"
    ]

    assert backups[0][
        "size"
    ] == "100 octets"

    assert backups[1][
        "size"
    ] == "2 Ko"

    assert backups[2][
        "size"
    ] == "2.0 Mo"

    for backup in backups:

        assert isinstance(
            backup["time"],
            str
        )

        assert backup["time"]


def test_list_backups_skips_missing_files():

    with open(
        "fusion.json.bak1",
        "wb"
    ) as f:

        f.write(
            b"x"
        )

    backups = FusionProject.list_backups()

    assert len(backups) == 1

    assert backups[0][
        "filename"
    ] == "fusion.json.bak1"


def test_format_size_boundaries():

    assert FusionProject._format_size(
        1023
    ) == "1023 octets"

    assert FusionProject._format_size(
        1024
    ) == "1 Ko"

    assert FusionProject._format_size(
        1024 * 1024 - 1
    ) == "1023 Ko"

    assert FusionProject._format_size(
        1024 * 1024
    ) == "1.0 Mo"


def test_format_time():

    timestamp = time.mktime(
        (
            2026,
            10,
            1,
            12,
            34,
            56,
            0,
            0,
            -1
        )
    )

    assert FusionProject._format_time(
        timestamp
    ) == "01-10-2026 12:34:56"


def test_rotate_backups_disabled(
    project,
    monkeypatch
):

    monkeypatch.setattr(
        "fusion_project._BACKUP_COUNT",
        0
    )

    project._rotate_backups(
        "unused.old"
    )


def test_list_backups_skips_file_disappearing_before_stat(
    monkeypatch
):

    real_exists = os.path.exists
    real_stat = os.stat

    filename = "fusion.json.bak"

    with open(
        filename,
        "wb"
    ) as f:

        f.write(
            b"x"
        )

    with open(
        "fusion.json.bak1",
        "wb"
    ) as f:

        f.write(
            b"y"
        )

    stat_calls = 0

    def failing_stat(
        path,
        *args,
        **kwargs
    ):

        nonlocal stat_calls

        if os.fspath(path) == filename:

            stat_calls += 1

            if stat_calls == 2:

                raise FileNotFoundError(
                    filename
                )

        return real_stat(
            path,
            *args,
            **kwargs
        )

    monkeypatch.setattr(
        "fusion_project.os.stat",
        failing_stat
    )

    backups = FusionProject.list_backups()

    assert [
        backup["filename"]
        for backup in backups
    ] == [
        "fusion.json.bak1"
    ]


def test_list_backups_skips_inaccessible_file(
    monkeypatch
):

    real_stat = os.stat

    filename = "fusion.json.bak"

    with open(
        filename,
        "wb"
    ) as f:

        f.write(
            b"x"
        )

    with open(
        "fusion.json.bak1",
        "wb"
    ) as f:

        f.write(
            b"y"
        )

    stat_calls = 0

    def failing_stat(
        path,
        *args,
        **kwargs
    ):

        nonlocal stat_calls

        if os.fspath(path) == filename:

            stat_calls += 1

            if stat_calls == 2:

                raise PermissionError(
                    filename
                )

        return real_stat(
            path,
            *args,
            **kwargs
        )

    monkeypatch.setattr(
        "fusion_project.os.stat",
        failing_stat
    )

    backups = FusionProject.list_backups()

    assert [
        backup["filename"]
        for backup in backups
    ] == [
        "fusion.json.bak1"
    ]


def test_rotate_backups_failure_preserves_history(
    project,
    monkeypatch
):

    #
    # Utiliser quatre générations
    # pour provoquer plusieurs
    # déplacements.
    #
    monkeypatch.setattr(
        "fusion_project._BACKUP_COUNT",
        4
    )

    backup = project.filename + ".bak"

    #
    # Créer un historique connu.
    #
    original = {
        backup: b"Backup A",
        backup + "1": b"Backup B",
        backup + "2": b"Backup C",
        backup + "3": b"Backup D"
    }

    for filename, content in original.items():

        with open(
            filename,
            "wb"
        ) as f:

            f.write(
                content
            )

    #
    # Créer la nouvelle sauvegarde
    # qui devrait devenir .bak.
    #
    old_file = project.filename + ".old-test"

    with open(
        old_file,
        "wb"
    ) as f:

        f.write(
            b"Nouvelle sauvegarde"
        )

    #
    # Simuler un échec après
    # le premier déplacement.
    #
    real_replace = os.replace

    failure_simulated = False

    def failing_replace(
        src,
        dst
    ):

        nonlocal failure_simulated

        if (
            os.fspath(src) == backup + "1"
            and
            os.fspath(dst) == backup + "2"
        ):

            failure_simulated = True

            raise OSError(
                "simulated rotation failure"
            )

        return real_replace(
            src,
            dst
        )

    monkeypatch.setattr(
        os,
        "replace",
        failing_replace
    )

    #
    # La rotation doit signaler
    # son échec.
    #
    with pytest.raises(
        OSError,
        match="simulated rotation failure"
    ):

        project._rotate_backups(
            old_file
        )

    assert failure_simulated

    #
    # Aucun backup préexistant
    # ne doit avoir changé.
    #
    for filename, content in original.items():

        with open(
            filename,
            "rb"
        ) as f:

            assert f.read() == content

    #
    # La nouvelle sauvegarde
    # doit également être intacte.
    #
    with open(
        old_file,
        "rb"
    ) as f:

        assert f.read() == (
            b"Nouvelle sauvegarde"
        )


def test_rotate_backups_final_replace_failure_preserves_history(
    project,
    monkeypatch
):

    monkeypatch.setattr(
        "fusion_project._BACKUP_COUNT",
        4
    )

    backup = project.filename + ".bak"

    #
    # Historique initial.
    #
    original = {
        backup: b"Backup A",
        backup + "1": b"Backup B",
        backup + "2": b"Backup C",
        backup + "3": b"Backup D"
    }

    for filename, content in original.items():

        with open(
            filename,
            "wb"
        ) as f:

            f.write(
                content
            )

    old_file = project.filename + ".old-test"

    old_content = b"Nouvelle sauvegarde"

    with open(
        old_file,
        "wb"
    ) as f:

        f.write(
            old_content
        )

    real_replace = os.replace
    failure_simulated = False

    def failing_replace(
        src,
        dst
    ):

        nonlocal failure_simulated

        if (
            os.fspath(src) == old_file
            and
            os.fspath(dst) == backup
        ):

            failure_simulated = True

            raise OSError(
                "simulated final replace failure"
            )

        return real_replace(
            src,
            dst
        )

    monkeypatch.setattr(
        os,
        "replace",
        failing_replace
    )

    #
    # L'installation du nouveau
    # backup doit échouer.
    #
    with pytest.raises(
        OSError,
        match="simulated final replace failure"
    ):

        project._rotate_backups(
            old_file
        )

    assert failure_simulated

    #
    # Tous les backups doivent
    # retrouver leur état initial.
    #
    for filename, content in original.items():

        with open(
            filename,
            "rb"
        ) as f:

            assert f.read() == content

    #
    # La nouvelle sauvegarde
    # doit rester disponible.
    #
    with open(
        old_file,
        "rb"
    ) as f:

        assert f.read() == old_content


def test_rotate_backups_failure_preserves_missing_generations(
    project,
    monkeypatch
):

    monkeypatch.setattr(
        "fusion_project._BACKUP_COUNT",
        4
    )

    backup = project.filename + ".bak"

    #
    # Historique comportant
    # des générations absentes.
    #
    original = {
        backup: b"Backup A",
        backup + "2": b"Backup C"
    }

    for filename, content in original.items():

        with open(
            filename,
            "wb"
        ) as f:

            f.write(
                content
            )

    old_file = project.filename + ".old-test"

    old_content = b"Nouvelle sauvegarde"

    with open(
        old_file,
        "wb"
    ) as f:

        f.write(
            old_content
        )

    real_replace = os.replace
    failure_simulated = False

    def failing_replace(
        src,
        dst
    ):

        nonlocal failure_simulated

        if (
            os.fspath(src) == backup
            and
            os.fspath(dst) == backup + "1"
        ):

            failure_simulated = True

            raise OSError(
                "simulated rotation failure"
            )

        return real_replace(
            src,
            dst
        )

    monkeypatch.setattr(
        os,
        "replace",
        failing_replace
    )

    #
    # Le déplacement .bak2
    # vers .bak3 réussit avant
    # l'échec simulé.
    #
    with pytest.raises(
        OSError,
        match="simulated rotation failure"
    ):

        project._rotate_backups(
            old_file
        )

    assert failure_simulated

    #
    # Vérifier les générations
    # présentes à l'origine.
    #
    for filename, content in original.items():

        with open(
            filename,
            "rb"
        ) as f:

            assert f.read() == content

    #
    # Vérifier que les générations
    # absentes le sont toujours.
    #
    assert not os.path.exists(
        backup + "1"
    )

    assert not os.path.exists(
        backup + "3"
    )

    #
    # Le fichier source doit
    # également être conservé.
    #
    with open(
        old_file,
        "rb"
    ) as f:

        assert f.read() == old_content


def test_rotate_backups_restore_failure_preserves_copies(
    project,
    monkeypatch
):

    monkeypatch.setattr(
        "fusion_project._BACKUP_COUNT",
        4
    )

    backup = project.filename + ".bak"

    #
    # Historique initial.
    #
    original = {
        backup: b"Backup A",
        backup + "1": b"Backup B",
        backup + "2": b"Backup C",
        backup + "3": b"Backup D"
    }

    for filename, content in original.items():

        with open(
            filename,
            "wb"
        ) as f:

            f.write(
                content
            )

    old_file = project.filename + ".old-test"

    with open(
        old_file,
        "wb"
    ) as f:

        f.write(
            b"Nouvelle sauvegarde"
        )

    real_replace = os.replace
    real_copy2 = shutil.copy2

    rotation_failed = False
    restore_failed = False
    recovery_directory = None

    #
    # Simuler un échec après
    # un premier déplacement.
    #
    def failing_replace(
        src,
        dst
    ):

        nonlocal rotation_failed

        if (
            os.fspath(src) == backup + "1"
            and
            os.fspath(dst) == backup + "2"
        ):

            rotation_failed = True

            raise OSError(
                "simulated rotation failure"
            )

        return real_replace(
            src,
            dst
        )

    #
    # Simuler ensuite un échec
    # pendant la restauration.
    #
    def failing_copy2(
        src,
        dst,
        *args,
        **kwargs
    ):

        nonlocal restore_failed
        nonlocal recovery_directory

        src_path = os.fspath(
            src
        )

        if (
            rotation_failed
            and
            os.path.basename(
                os.path.dirname(
                    src_path
                )
            ).startswith(
                os.path.basename(
                    project.filename
                )
                + ".rotation-"
            )
            and
            os.fspath(
                dst
            ) == backup
        ):

            restore_failed = True

            recovery_directory = (
                os.path.dirname(
                    src_path
                )
            )

            raise OSError(
                "simulated restore failure"
            )

        return real_copy2(
            src,
            dst,
            *args,
            **kwargs
        )

    monkeypatch.setattr(
        os,
        "replace",
        failing_replace
    )

    monkeypatch.setattr(
        shutil,
        "copy2",
        failing_copy2
    )

    #
    # La rotation doit signaler
    # une erreur.
    #
    with pytest.raises(
        OSError
    ):

        project._rotate_backups(
            old_file
        )

    #
    # Vérifier que les deux
    # erreurs ont été simulées.
    #
    assert rotation_failed

    assert restore_failed

    assert recovery_directory is not None

    #
    # Les copies originales
    # doivent rester disponibles.
    #
    assert os.path.isdir(
        recovery_directory
    )

    for index, content in enumerate(
        original.values()
    ):

        copy = os.path.join(
            recovery_directory,
            str(index)
        )

        with open(
            copy,
            "rb"
        ) as f:

            assert f.read() == content


def test_rotate_backups_success_cleans_temporary_directory(
    project,
    monkeypatch
):

    monkeypatch.setattr(
        "fusion_project._BACKUP_COUNT",
        4
    )

    backup = project.filename + ".bak"

    #
    # Créer un backup existant.
    #
    with open(
        backup,
        "wb"
    ) as f:

        f.write(
            b"Backup A"
        )

    #
    # Créer la nouvelle version
    # destinée aux backups.
    #
    old_file = project.filename + ".old-test"

    with open(
        old_file,
        "wb"
    ) as f:

        f.write(
            b"Nouvelle sauvegarde"
        )

    #
    # Effectuer la rotation.
    #
    project._rotate_backups(
        old_file
    )

    #
    # Vérifier le résultat.
    #
    with open(
        backup,
        "rb"
    ) as f:

        assert f.read() == (
            b"Nouvelle sauvegarde"
        )

    with open(
        backup + "1",
        "rb"
    ) as f:

        assert f.read() == (
            b"Backup A"
        )

    #
    # Le fichier source a été
    # déplacé vers .bak.
    #
    assert not os.path.exists(
        old_file
    )

    #
    # Aucun répertoire temporaire
    # de rotation ne doit subsister.
    #
    directory = os.path.dirname(
        os.path.abspath(
            project.filename
        )
    )

    prefix = (
        os.path.basename(
            project.filename
        )
        + ".rotation-"
    )

    assert not any(
        name.startswith(
            prefix
        )
        for name in os.listdir(
            directory
        )
    )
