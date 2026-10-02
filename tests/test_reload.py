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


