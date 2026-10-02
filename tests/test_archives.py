import os
from pathlib import Path
from fusion_project import FusionProject

import fusion_project

def test_file_hash_same_content(
    project,
    tmp_path
):

    file1 = tmp_path / "a.json"
    file2 = tmp_path / "b.json"

    file1.write_bytes(
        b"same content"
    )

    file2.write_bytes(
        b"same content"
    )

    assert project._file_hash(
        file1
    ) == project._file_hash(
        file2
    )


def test_file_hash_different_content(
    project,
    tmp_path
):

    file1 = tmp_path / "a.json"
    file2 = tmp_path / "b.json"

    file1.write_bytes(
        b"content A"
    )

    file2.write_bytes(
        b"content B"
    )

    assert project._file_hash(
        file1
    ) != project._file_hash(
        file2
    )


def test_archive_if_changed_ignores_unreadable_archive(
    project,
    monkeypatch,
    tmp_path
):

    archive_dir = tmp_path / "archives"

    archive_dir.mkdir()

    monkeypatch.setattr(
        "fusion_project.ARCHIVE_DIR",
        str(archive_dir)
    )

    project.filename = str(
        tmp_path / "fusion.json"
    )

    with open(
        project.filename,
        "w",
        encoding="utf-8"
    ) as f:

        f.write("{}")

    archive_file = (
        archive_dir
        / "fusion-2026-01-01_000000.json"
    )

    archive_file.write_text(
        "{}",
        encoding="utf-8"
    )

    def fake_hash(
        filename
    ):

        if filename == str(
            archive_file
        ):

            raise OSError(
                "lecture impossible"
            )

        return "current"

    monkeypatch.setattr(
        project,
        "_file_hash",
        fake_hash
    )

    monkeypatch.setattr(
        project,
        "archive",
        lambda: True
    )

    assert project.archive_if_changed() is True


def test_archive_if_changed_current_hash_error(
    project,
    monkeypatch,
    tmp_path
):

    archive_dir = tmp_path / "archives"

    archive_dir.mkdir()

    monkeypatch.setattr(
        "fusion_project.ARCHIVE_DIR",
        str(archive_dir)
    )

    project.filename = str(
        tmp_path / "fusion.json"
    )

    with open(
        project.filename,
        "w",
        encoding="utf-8"
    ) as f:

        f.write("{}")

    (
        archive_dir
        / "fusion-2026-01-01_000000.json"
    ).write_text(
        "{}",
        encoding="utf-8"
    )

    def fake_hash(
        filename
    ):

        raise OSError(
            "lecture impossible"
        )

    monkeypatch.setattr(
        project,
        "_file_hash",
        fake_hash
    )
    assert project.archive_if_changed() is True


def test_archive_if_changed_without_matching_archive(
    project,
    monkeypatch,
    tmp_path
):

    archive_dir = tmp_path / "archives"

    archive_dir.mkdir()

    monkeypatch.setattr(
        "fusion_project.ARCHIVE_DIR",
        str(archive_dir)
    )

    project.filename = str(
        tmp_path / "fusion.json"
    )

    with open(
        project.filename,
        "w",
        encoding="utf-8"
    ) as f:

        f.write("{}")

    called = []

    def fake_archive():

        called.append(
            True
        )

        return True

    monkeypatch.setattr(
        project,
        "archive",
        fake_archive
    )

    assert project.archive_if_changed() is True

    assert called == [
        True
    ]


def test_archive_is_valid_missing_file(
    tmp_path
):

    assert FusionProject._archive_is_valid(
        tmp_path / "missing.json"
    ) is False


def test_archive_is_valid_json_object(
    tmp_path
):

    filename = tmp_path / "archive.json"

    filename.write_text(
        '{"test": true}',
        encoding="utf-8"
    )

    assert FusionProject._archive_is_valid(
        filename
    ) is True


def test_archive_is_valid_rejects_non_object(
    tmp_path
):

    filename = tmp_path / "archive.json"

    filename.write_text(
        '["test"]',
        encoding="utf-8"
    )

    assert FusionProject._archive_is_valid(
        filename
    ) is False


def test_archive_is_valid_rejects_broken_json(
    tmp_path
):

    filename = tmp_path / "archive.json"

    filename.write_text(
        '{"test":',
        encoding="utf-8"
    )

    assert FusionProject._archive_is_valid(
        filename
    ) is False


def test_list_archives_missing_directory(
    tmp_path,
    monkeypatch
):

    archive_dir = (
        tmp_path
        / "archives"
    )

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    assert FusionProject.list_archives() == []


def test_list_archives_filters_and_sorts(
    tmp_path,
    monkeypatch
):

    archive_dir = (
        tmp_path
        / "archives"
    )

    archive_dir.mkdir()

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    old = (
        archive_dir
        / "fusion-2026-01-01_120000.json"
    )

    new = (
        archive_dir
        / "fusion-2026-01-02_120000.json"
    )

    invalid = (
        archive_dir
        / "fusion-2026-01-03_120000.json"
    )

    unrelated = (
        archive_dir
        / "other-2026-01-04_120000.json"
    )

    old.write_text(
        '{"version": 1}',
        encoding="utf-8"
    )

    new.write_text(
        '{"version": 2}',
        encoding="utf-8"
    )

    invalid.write_text(
        '{"broken":',
        encoding="utf-8"
    )

    unrelated.write_text(
        '{"version": 3}',
        encoding="utf-8"
    )

    os.utime(
        old,
        (1000, 1000)
    )

    os.utime(
        new,
        (2000, 2000)
    )

    archives = (
        FusionProject.list_archives()
    )

    assert [
        archive["name"]
        for archive in archives
    ] == [
        new.name,
        old.name
    ]


def test_archive_missing_project(
    project
):

    assert project.archive() is False


def test_archive_creates_archive(
    project,
    tmp_path,
    monkeypatch
):

    archive_dir = (
        tmp_path
        / "archives"
    )

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    assert project.save_safe(
        allowed_errors=[]
    )

    assert project.archive() is True

    archives = list(
        archive_dir.glob(
            "fusion-*.json"
        )
    )

    assert len(archives) == 1

    assert archives[
        0
    ].read_bytes() == (
        Path(
            project.filename
        ).read_bytes()
    )


def test_archive_copy_failure(
    project,
    tmp_path,
    monkeypatch
):

    archive_dir = (
        tmp_path
        / "archives"
    )

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    assert project.save_safe(
        allowed_errors=[]
    )

    def failing_copy(
        src,
        dst
    ):

        raise OSError(
            "simulated failure"
        )

    monkeypatch.setattr(
        fusion_project.shutil,
        "copy",
        failing_copy
    )

    assert project.archive() is False


def test_archive_if_changed_missing_project(
    project
):

    assert (
        project.archive_if_changed()
        is False
    )


def test_archive_if_changed_creates_first_archive(
    project,
    tmp_path,
    monkeypatch
):

    archive_dir = (
        tmp_path
        / "archives"
    )

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    assert project.save_safe(
        allowed_errors=[]
    )

    assert (
        project.archive_if_changed()
        is True
    )

    assert len(
        list(
            archive_dir.glob(
                "fusion-*.json"
            )
        )
    ) == 1


def test_archive_if_changed_skips_identical_content(
    project,
    tmp_path,
    monkeypatch
):

    archive_dir = (
        tmp_path
        / "archives"
    )

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    assert project.save_safe(
        allowed_errors=[]
    )

    assert (
        project.archive_if_changed()
        is True
    )

    assert (
        project.archive_if_changed()
        is False
    )


def test_archive_if_changed_archives_changed_content(
    project,
    tmp_path,
    monkeypatch
):

    archive_dir = (
        tmp_path
        / "archives"
    )

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    timestamps = iter(
        [
            "2026-01-01_120000",
            "2026-01-01_120001"
        ]
    )

    monkeypatch.setattr(
        fusion_project.time,
        "strftime",
        lambda format: next(
            timestamps
        )
    )

    assert project.save_safe(
        allowed_errors=[]
    )

    assert (
        project.archive_if_changed()
        is True
    )

    project.data[
        "banks"
    ][
        "program"
    ][
        "1"
    ] = "Changed"

    assert project.save_safe(
        allowed_errors=[]
    )

    assert (
        project.archive_if_changed()
        is True
    )

    assert len(
        list(
            archive_dir.glob(
                "fusion-*.json"
            )
        )
    ) == 2


def test_rotate_archives_keeps_newest(
    project,
    tmp_path,
    monkeypatch
):

    archive_dir = (
        tmp_path
        / "archives"
    )

    archive_dir.mkdir()

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_COUNT",
        2
    )

    names = [
        "fusion-2026-01-01_120000.json",
        "fusion-2026-01-02_120000.json",
        "fusion-2026-01-03_120000.json"
    ]

    for name in names:

        (
            archive_dir
            / name
        ).write_text(
            "{}",
            encoding="utf-8"
        )

    project._rotate_archives()

    remaining = sorted(
        path.name
        for path in archive_dir.glob(
            "fusion-*.json"
        )
    )

    assert remaining == [
        "fusion-2026-01-02_120000.json",
        "fusion-2026-01-03_120000.json"
    ]


def test_rotate_archives_disabled(
    project,
    tmp_path,
    monkeypatch
):

    archive_dir = (
        tmp_path
        / "archives"
    )

    archive_dir.mkdir()

    archive = (
        archive_dir
        / "fusion-2026-01-01_120000.json"
    )

    archive.write_text(
        "{}",
        encoding="utf-8"
    )

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_COUNT",
        0
    )

    project._rotate_archives()

    assert archive.exists()


def test_rotate_archives_missing_directory(
    project,
    tmp_path,
    monkeypatch
):

    archive_dir = (
        tmp_path
        / "missing"
    )

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    project._rotate_archives()

    assert not archive_dir.exists()


def test_rotate_archives_ignores_remove_failure(
    project,
    tmp_path,
    monkeypatch
):

    archive_dir = (
        tmp_path
        / "archives"
    )

    archive_dir.mkdir()

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_COUNT",
        1
    )

    for name in (
        "fusion-2026-01-01_120000.json",
        "fusion-2026-01-02_120000.json"
    ):

        (
            archive_dir
            / name
        ).write_text(
            "{}",
            encoding="utf-8"
        )

    def failing_remove(
        filename
    ):

        raise OSError(
            "simulated failure"
        )

    monkeypatch.setattr(
        fusion_project.os,
        "remove",
        failing_remove
    )

    #
    # L'exception doit être absorbée.
    #
    project._rotate_archives()

    assert len(
        list(
            archive_dir.glob(
                "fusion-*.json"
            )
        )
    ) == 2
