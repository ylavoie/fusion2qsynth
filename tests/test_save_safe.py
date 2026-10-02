import os
import json
import copy

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

        if src == (
            project.filename
            + ".tmp"
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
