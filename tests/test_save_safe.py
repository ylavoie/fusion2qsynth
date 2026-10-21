import os
import json
import copy
import pytest

def test_save_safe_new_file(
    project
):

    assert project.save_safe(
        allowed_errors=[]
    ) is True

    assert os.path.exists(
        project.filename
    )

    with open(
        project.filename,
        encoding="utf-8"
    ) as f:

        saved = json.load(
            f
        )

    assert saved == project.data

    assert project.file_time == (
        os.path.getmtime(
            project.filename
        )
    )

    assert not os.path.exists(
        project.filename + ".tmp"
    )

    assert not os.path.exists(
        project.filename + ".old"
    )


def test_save_safe_rejects_blocking_error(
    project
):

    project.data[
        "mixes"
    ][
        "invalid"
    ] = {
        "name": "Invalid",
        "channels": {}
    }

    assert project.save_safe(
        allowed_errors=[]
    ) is False

    assert not os.path.exists(
        project.filename
    )

    assert not os.path.exists(
        project.filename + ".tmp"
    )


def test_save_safe_allows_existing_error(
    project
):

    project.data[
        "mixes"
    ][
        "invalid"
    ] = {
        "name": "Invalid",
        "channels": {}
    }

    errors = project.get_blocking_errors(
        project.validate()
    )

    assert errors

    assert project.save_safe(
        allowed_errors=errors
    ) is True

    assert os.path.exists(
        project.filename
    )


def test_save_safe_existing_file_creates_backup(
    project
):

    assert project.save_safe(
        allowed_errors=[]
    ) is True

    with open(
        project.filename,
        encoding="utf-8"
    ) as f:

        original = json.load(
            f
        )

    project.data[
        "banks"
    ][
        "program"
    ][
        "1"
    ] = "Test"

    assert project.save_safe(
        allowed_errors=[]
    ) is True

    backup = (
        project.filename
        + ".bak"
    )

    assert os.path.exists(
        backup
    )

    with open(
        backup,
        encoding="utf-8"
    ) as f:

        assert json.load(
            f
        ) == original


def test_save_safe_rotates_backups(
    project
):

    versions = []

    for index in range(4):

        project.data[
            "banks"
        ][
            "program"
        ][
            "1"
        ] = f"Version {index}"

        versions.append(
            copy.deepcopy(
                project.data
            )
        )

        assert project.save_safe(
            allowed_errors=[]
        ) is True

    with open(
        project.filename + ".bak",
        encoding="utf-8"
    ) as f:

        assert json.load(f) == versions[2]

    with open(
        project.filename + ".bak1",
        encoding="utf-8"
    ) as f:

        assert json.load(f) == versions[1]

    with open(
        project.filename + ".bak2",
        encoding="utf-8"
    ) as f:

        assert json.load(f) == versions[0]


def test_save_safe_replace_failure_preserves_original(
    project,
    monkeypatch
):

    assert project.save_safe(
        allowed_errors=[]
    ) is True

    with open(
        project.filename,
        encoding="utf-8"
    ) as f:

        original = json.load(
            f
        )

    project.data[
        "banks"
    ][
        "program"
    ][
        "1"
    ] = "Changed"

    real_replace = os.replace

    def failing_replace(
        src,
        dst
    ):

        if (
            os.path.dirname(
                os.path.abspath(
                    src
                )
            )
            ==
            os.path.dirname(
                os.path.abspath(
                    project.filename
                )
            )
            and
            os.path.basename(
                os.fspath(
                    src
                )
            ).startswith(
                os.path.basename(
                    project.filename
                )
                + ".save-"
            )
            and
            os.fspath(
                src
            ).endswith(
                ".tmp"
            )
            and
            os.fspath(
                dst
            ) == project.filename
        ):

            raise OSError(
                "simulated failure"
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

    assert project.save_safe(
        allowed_errors=[]
    ) is False

    #
    # Simuler un rechargement
    # précédemment échoué.
    #
    failed_signature = (
        123456789,
        1024
    )

    project.failed_reload_signature = (
        failed_signature
    )

    with open(
        project.filename,
        encoding="utf-8"
    ) as f:

        assert json.load(f) == original

    assert not os.path.exists(
        project.filename + ".tmp"
    )

    assert not os.path.exists(
        project.filename + ".old"
    )

    #
    # Une sauvegarde échouée ne doit
    # pas effacer l'état d'échec.
    #
    assert (
        project.failed_reload_signature
        == failed_signature
    )


def test_save_safe_getmtime_failure_after_replace(
    project,
    monkeypatch
):

    assert project.save_safe(
        allowed_errors=[]
    ) is True

    project.data[
        "banks"
    ][
        "program"
    ][
        "1"
    ] = "Changed"

    def failing_getmtime(
        path
    ):

        if path == project.filename:

            raise OSError(
                "simulated getmtime failure"
            )

        return real_getmtime(
            path
        )

    real_getmtime = os.path.getmtime

    monkeypatch.setattr(
        os.path,
        "getmtime",
        failing_getmtime
    )

    assert project.save_safe(
        allowed_errors=[]
    ) is True

    with open(
        project.filename,
        encoding="utf-8"
    ) as f:

        saved = json.load(
            f
        )

    assert saved == project.data

    assert not os.path.exists(
        project.filename + ".tmp"
    )

    assert not os.path.exists(
        project.filename + ".old"
    )


def test_save_safe_backup_rotation_failure_is_nonfatal(
    project,
    monkeypatch
):

    assert project.save_safe(
        allowed_errors=[]
    ) is True

    project.data[
        "banks"
    ][
        "program"
    ][
        "1"
    ] = "Changed"

    def failing_rotate(
        old_file
    ):

        raise OSError(
            "simulated rotation failure"
        )

    monkeypatch.setattr(
        project,
        "_rotate_backups",
        failing_rotate
    )

    assert project.save_safe(
        allowed_errors=[]
    ) is True

    with open(
        project.filename,
        encoding="utf-8"
    ) as f:

        saved = json.load(
            f
        )

    assert saved == project.data

    assert not os.path.exists(
        project.filename + ".old"
    )


def test_save_safe_old_cleanup_failure_after_replace(
    project,
    monkeypatch
):

    assert project.save_safe(
        allowed_errors=[]
    ) is True

    project.data[
        "banks"
    ][
        "program"
    ][
        "1"
    ] = "Changed"

    old_file = None

    rotation_simulated = False
    remove_simulated = False

    real_remove = os.remove

    def failing_remove(
        path
    ):

        nonlocal old_file
        nonlocal remove_simulated

        #
        # Identifier le fichier
        # temporaire contenant
        # l'ancienne version.
        #
        if (
            os.path.basename(
                os.fspath(
                    path
                )
            ).startswith(
                os.path.basename(
                    project.filename
                )
                + ".old-"
            )
            and
            os.fspath(
                path
            ).endswith(
                ".tmp"
            )
        ):

            old_file = os.fspath(
                path
            )

            remove_simulated = True

            raise OSError(
                "simulated cleanup failure"
            )

        return real_remove(
            path
        )

    def failing_rotate(
        path
    ):

        nonlocal rotation_simulated

        #
        # Vérifier que la rotation
        # reçoit le fichier
        # temporaire attendu.
        #
        assert os.path.basename(
            os.fspath(
                path
            )
        ).startswith(
            os.path.basename(
                project.filename
            )
            + ".old-"
        )

        rotation_simulated = True

        raise OSError(
            "simulated rotation failure"
        )

    monkeypatch.setattr(
        os,
        "remove",
        failing_remove
    )

    monkeypatch.setattr(
        project,
        "_rotate_backups",
        failing_rotate
    )

    assert project.save_safe(
        allowed_errors=[]
    ) is True

    with open(
        project.filename,
        encoding="utf-8"
    ) as f:

        assert json.load(f) == project.data

    #
    # Les deux erreurs doivent
    # avoir été simulées.
    #
    assert rotation_simulated

    assert remove_simulated

    #
    # Le fichier temporaire
    # n'a pas pu être supprimé.
    #
    assert old_file is not None

    assert os.path.exists(
        old_file
    )


def test_save_safe_temp_cleanup_failure(
    project,
    monkeypatch
):

    assert project.save_safe(
        allowed_errors=[]
    ) is True

    with open(
        project.filename,
        encoding="utf-8"
    ) as f:

        original = json.load(f)

    project.data[
        "banks"
    ][
        "program"
    ][
        "1"
    ] = "Changed"

    temp_file = None

    replace_simulated = False
    remove_simulated = False

    real_remove = os.remove
    real_replace = os.replace

    def failing_replace(
        src,
        dst
    ):

        nonlocal temp_file
        nonlocal replace_simulated

        if (
            os.path.basename(
                os.fspath(
                    src
                )
            ).startswith(
                os.path.basename(
                    project.filename
                )
                + ".save-"
            )
            and
            os.fspath(
                src
            ).endswith(
                ".tmp"
            )
            and
            os.fspath(
                dst
            ) == project.filename
        ):

            temp_file = os.fspath(
                src
            )

            replace_simulated = True

            raise OSError(
                "simulated replace failure"
            )

        return real_replace(
            src,
            dst
        )

    def failing_remove(
        path
    ):

        nonlocal remove_simulated

        if (
            temp_file is not None
            and
            os.fspath(
                path
            ) == temp_file
        ):

            remove_simulated = True

            raise OSError(
                "simulated cleanup failure"
            )

        return real_remove(
            path
        )

    real_replace = os.replace

    monkeypatch.setattr(
        os,
        "replace",
        failing_replace
    )

    monkeypatch.setattr(
        os,
        "remove",
        failing_remove
    )

    assert project.save_safe(
        allowed_errors=[]
    ) is False

    with open(
        project.filename,
        encoding="utf-8"
    ) as f:

        assert json.load(f) == original

    assert replace_simulated
    assert remove_simulated

    assert temp_file is not None

    assert os.path.exists(
        temp_file
    )


def test_save_safe_old_cleanup_failure_before_replace(
    project,
    monkeypatch
):

    assert project.save_safe(
        allowed_errors=[]
    ) is True

    with open(
        project.filename,
        encoding="utf-8"
    ) as f:

        original = json.load(f)

    project.data[
        "banks"
    ][
        "program"
    ][
        "1"
    ] = "Changed"

    old_file = None

    real_replace = os.replace
    real_remove = os.remove

    replace_simulated = False
    remove_simulated = False

    def failing_replace(src, dst):

        nonlocal replace_simulated
        replace_simulated = True

        if (
            os.path.basename(
                os.fspath(
                    src
                )
            ).startswith(
                os.path.basename(
                    project.filename
                )
                + ".save-"
            )
            and
            os.fspath(
                src
            ).endswith(
                ".tmp"
            )
            and
            os.fspath(
                dst
            ) == project.filename
        ):

            raise OSError(
                "simulated replace failure"
            )

        return real_replace(src, dst)

    def failing_remove(
        path
    ):

        nonlocal old_file
        nonlocal remove_simulated

        #
        # Identifier le fichier
        # temporaire contenant
        # l'ancienne version.
        #
        if (
            os.path.basename(
                os.fspath(
                    path
                )
            ).startswith(
                os.path.basename(
                    project.filename
                )
                + ".old-"
            )
            and
            os.fspath(
                path
            ).endswith(
                ".tmp"
            )
        ):

            old_file = os.fspath(
                path
            )

            remove_simulated = True

            raise OSError(
                "simulated old cleanup failure"
            )

        return real_remove(
            path
        )

    monkeypatch.setattr(
        os,
        "replace",
        failing_replace
    )

    monkeypatch.setattr(
        os,
        "remove",
        failing_remove
    )

    assert project.save_safe(
        allowed_errors=[]
    ) is False

    with open(
        project.filename,
        encoding="utf-8"
    ) as f:

        assert json.load(f) == original

    assert replace_simulated

    assert remove_simulated

    assert old_file is not None

    assert os.path.exists(
        old_file
    )


def test_save_safe_preserves_existing_temp(
    project
):

    #
    # Simuler un fichier temporaire
    # laissé par une exécution précédente.
    #
    old_temp = (
        project.filename
        + ".tmp"
    )

    old_content = (
        "Fichier temporaire préexistant"
    )

    with open(
        old_temp,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            old_content
        )

    #
    # La sauvegarde doit réussir
    # sans modifier l'ancien fichier.
    #
    assert project.save_safe(
        allowed_errors=[]
    ) is True

    with open(
        project.filename,
        encoding="utf-8"
    ) as f:

        assert json.load(
            f
        ) == project.data

    #
    # Le fichier temporaire
    # préexistant doit être intact.
    #
    with open(
        old_temp,
        "r",
        encoding="utf-8"
    ) as f:

        assert f.read() == (
            old_content
        )


def test_save_safe_preserves_existing_old(
    project
):

    #
    # Créer une première version
    # du projet.
    #
    assert project.save_safe(
        allowed_errors=[]
    ) is True

    #
    # Simuler un ancien fichier
    # .old laissé par une
    # exécution précédente.
    #
    old_file = (
        project.filename
        + ".old"
    )

    old_content = (
        "Ancien fichier préexistant"
    )

    with open(
        old_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            old_content
        )

    #
    # Modifier le projet pour
    # provoquer une nouvelle
    # sauvegarde.
    #
    project.data[
        "banks"
    ][
        "program"
    ][
        "1"
    ] = "Changed"

    assert project.save_safe(
        allowed_errors=[]
    ) is True

    #
    # Vérifier la nouvelle
    # version du projet.
    #
    with open(
        project.filename,
        encoding="utf-8"
    ) as f:

        assert json.load(
            f
        ) == project.data

    #
    # L'ancien fichier .old
    # doit rester intact.
    #
    with open(
        old_file,
        "r",
        encoding="utf-8"
    ) as f:

        assert f.read() == (
            old_content
        )


def test_save_safe_respects_error_occurrences(
    project,
    monkeypatch
):

    #
    # Simuler deux erreurs identiques.
    #
    error = "Erreur de validation simulée"

    errors = [
        error,
        error
    ]

    monkeypatch.setattr(
        project,
        "validate",
        lambda: errors
    )

    monkeypatch.setattr(
        project,
        "get_blocking_errors",
        lambda validation_errors: (
            validation_errors
        )
    )

    #
    # Une seule occurrence autorisée :
    # sauvegarde refusée.
    #
    assert project.save_safe(
        allowed_errors=[
            error
        ]
    ) is False

    assert not os.path.exists(
        project.filename
    )

    #
    # Deux occurrences autorisées :
    # sauvegarde acceptée.
    #
    assert project.save_safe(
        allowed_errors=[
            error,
            error
        ]
    ) is True

    assert os.path.exists(
        project.filename
    )


def test_save_safe_rejects_replaced_error(
    project,
    monkeypatch
):

    #
    # Erreur initialement autorisée.
    #
    original_error = (
        "Erreur A"
    )

    #
    # Nouvelle erreur non autorisée.
    #
    new_error = (
        "Erreur B"
    )

    monkeypatch.setattr(
        project,
        "validate",
        lambda: [
            new_error
        ]
    )

    monkeypatch.setattr(
        project,
        "get_blocking_errors",
        lambda errors: errors
    )

    #
    # Même nombre d'erreurs,
    # mais erreur différente.
    #
    assert project.save_safe(
        allowed_errors=[
            original_error
        ]
    ) is False

    #
    # Aucun fichier ne doit
    # avoir été créé.
    #
    assert not os.path.exists(
        project.filename
    )


def test_save_safe_allows_resolved_error(
    project,
    monkeypatch
):

    #
    # Une erreur était autorisée,
    # mais elle a été corrigée.
    #
    original_error = "Erreur A"

    monkeypatch.setattr(
        project,
        "validate",
        lambda: []
    )

    monkeypatch.setattr(
        project,
        "get_blocking_errors",
        lambda errors: errors
    )

    #
    # L'ancienne erreur autorisée
    # n'existe plus.
    #
    assert project.save_safe(
        allowed_errors=[
            original_error
        ]
    ) is True

    #
    # Le fichier doit être créé.
    #
    assert os.path.exists(
        project.filename
    )


def test_save_safe_validation_exception(
    project,
    monkeypatch
):

    #
    # Créer un fichier valide.
    #
    assert project.save_safe(
        allowed_errors=[]
    ) is True

    #
    # Conserver son contenu exact.
    #
    with open(
        project.filename,
        "rb"
    ) as f:

        original_content = f.read()

    #
    # Modifier les données en mémoire.
    #
    project.data["banks"]["program"]["1"] = (
        "Unsaved modification"
    )

    #
    # Simuler une exception pendant
    # la validation.
    #
    def failing_validate():

        raise RuntimeError(
            "Erreur de validation simulée"
        )

    monkeypatch.setattr(
        project,
        "validate",
        failing_validate
    )

    #
    # Vérifier la propagation
    # de l'exception.
    #
    with pytest.raises(
        RuntimeError,
        match="Erreur de validation simulée"
    ):

        project.save_safe(
            allowed_errors=[]
        )

    #
    # Le fichier existant doit
    # demeurer inchangé.
    #
    with open(
        project.filename,
        "rb"
    ) as f:

        assert f.read() == original_content

    #
    # Les modifications en mémoire
    # ne doivent pas être perdues.
    #
    assert (
        project.data["banks"]["program"]["1"]
        == "Unsaved modification"
    )
