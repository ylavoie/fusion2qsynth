import copy
import json
import os

from fusion_constants import (
    PROJECT_FORMAT_VERSION
)

def test_reload_missing_file(
    project
):

    assert (
        project.reload_if_changed()
        is False
    )


def test_reload_unchanged_file(
    project
):

    assert project.save_safe(
        allowed_errors=[]
    )

    assert (
        project.reload_if_changed()
        is False
    )


def test_reload_changed_file(
    project
):

    assert project.save_safe(
        allowed_errors=[]
    )

    data = copy.deepcopy(
        project.data
    )

    data[
        "banks"
    ][
        "program"
    ][
        "1"
    ] = "Reloaded"

    with open(
        project.filename,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f
        )

    project.file_time = 0

    assert (
        project.reload_if_changed()
        is True
    )

    assert project.data[
        "banks"
    ][
        "program"
    ][
        "1"
    ] == "Reloaded"

    assert project.file_time == (
        os.path.getmtime(
            project.filename
        )
    )


def test_reload_invalid_json_preserves_state(
    project
):

    assert project.save_safe(
        allowed_errors=[]
    )

    before = project.snapshot()
    old_file_time = project.file_time

    with open(
        project.filename,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            '{"broken":'
        )

    project.file_time = old_file_time

    #
    # Garantir que reload_if_changed()
    # détecte une modification même sur un
    # système de fichiers à résolution faible.
    #
    os.utime(
        project.filename,
        (
            old_file_time + 10,
            old_file_time + 10
        )
    )

    assert (
        project.reload_if_changed()
        is False
    )

    assert project.data == before

    assert (
        project.file_time
        == old_file_time
    )


def test_reload_invalid_project_preserves_state(
    project
):

    assert project.save_safe(
        allowed_errors=[]
    )

    before = project.snapshot()
    old_file_time = project.file_time

    with open(
        project.filename,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            {
                "format_version":
                    PROJECT_FORMAT_VERSION
            },
            f
        )

    os.utime(
        project.filename,
        (
            old_file_time + 10,
            old_file_time + 10
        )
    )

    assert (
        project.reload_if_changed()
        is False
    )

    assert project.data == before

    assert (
        project.file_time
        == old_file_time
    )


def test_reload_getmtime_failure_then_retry(
    project,
    monkeypatch,
    caplog
):

    assert project.save_safe(
        allowed_errors=[]
    )

    before = project.snapshot()
    old_file_time = project.file_time

    data = copy.deepcopy(
        project.data
    )

    data["banks"]["program"]["1"] = (
        "Reloaded"
    )

    with open(
        project.filename,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f
        )

    os.utime(
        project.filename,
        (
            old_file_time + 10,
            old_file_time + 10
        )
    )

    real_getmtime = os.path.getmtime
    attempts = 0

    def temporary_getmtime(
        filename
    ):

        nonlocal attempts

        attempts += 1

        if attempts == 1:

            raise OSError(
                "Erreur temporaire simulée"
            )

        return real_getmtime(
            filename
        )

    monkeypatch.setattr(
        os.path,
        "getmtime",
        temporary_getmtime
    )

    assert (
        project.reload_if_changed()
        is False
    )

    assert attempts == 1
    assert project.data == before
    assert project.file_time == old_file_time

    assert (
        "Erreur temporaire simulée"
        in caplog.text
    )

    assert (
        project.reload_if_changed()
        is True
    )

    assert attempts >= 2

    assert (
        project.data["banks"]["program"]["1"]
        == "Reloaded"
    )

    assert project.file_time == (
        real_getmtime(
            project.filename
        )
    )


def test_reload_load_getmtime_failure_preserves_state(
    project,
    monkeypatch
):

    assert project.save_safe(
        allowed_errors=[]
    )

    before = project.snapshot()
    old_file_time = project.file_time

    data = copy.deepcopy(
        project.data
    )

    data["banks"]["program"]["1"] = (
        "Reloaded"
    )

    with open(
        project.filename,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f
        )

    os.utime(
        project.filename,
        (
            old_file_time + 10,
            old_file_time + 10
        )
    )

    real_getmtime = os.path.getmtime
    attempts = 0

    def temporary_getmtime(
        filename
    ):

        nonlocal attempts

        attempts += 1

        if attempts == 2:

            raise OSError(
                "Erreur getmtime pendant load"
            )

        return real_getmtime(
            filename
        )

    monkeypatch.setattr(
        os.path,
        "getmtime",
        temporary_getmtime
    )

    assert (
        project.reload_if_changed()
        is False
    )

    assert attempts == 2

    assert project.data == before

    assert (
        project.file_time
        == old_file_time
    )


def test_reload_after_save_getmtime_failure(
    project,
    monkeypatch
):

    #
    # Première sauvegarde normale.
    #
    assert project.save_safe(
        allowed_errors=[]
    )

    old_file_time = project.file_time

    #
    # Modifier les données.
    #
    project.data[
        "banks"
    ][
        "program"
    ][
        "1"
    ] = "Changed"

    real_getmtime = os.path.getmtime

    def failing_getmtime(
        filename
    ):

        if filename == project.filename:

            raise OSError(
                "Erreur getmtime simulée"
            )

        return real_getmtime(
            filename
        )

    #
    # Simuler l'échec de getmtime
    # après la sauvegarde.
    #
    monkeypatch.setattr(
        os.path,
        "getmtime",
        failing_getmtime
    )

    assert project.save_safe(
        allowed_errors=[]
    ) is True

    assert project.file_time == old_file_time

    #
    # Rétablir getmtime.
    #
    monkeypatch.setattr(
        os.path,
        "getmtime",
        real_getmtime
    )

    #
    # Forcer une date distincte
    # pour éviter toute ambiguïté
    # liée à la résolution du système
    # de fichiers.
    #
    os.utime(
        project.filename,
        (
            old_file_time + 10,
            old_file_time + 10
        )
    )

    #
    # Le rechargement doit rétablir
    # la synchronisation.
    #
    assert project.reload_if_changed() is True

    assert project.file_time == (
        real_getmtime(
            project.filename
        )
    )

    assert project.data[
        "banks"
    ][
        "program"
    ][
        "1"
    ] == "Changed"

    #
    # Aucun nouveau rechargement
    # ne doit être nécessaire.
    #
    assert project.reload_if_changed() is False
