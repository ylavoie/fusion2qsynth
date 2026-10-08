import os
import pytest

from pathlib import Path
from datetime import (
    date,
    datetime
)

from fusion_project import FusionProject

import fusion_project


def create_archive(
    archive_dir,
    filename,
    content="{}"
):

    path = (
        archive_dir
        / filename
    )

    path.write_text(
        content,
        encoding="utf-8"
    )

    return path


def archive_names(
    archive_dir
):

    return {
        path.name
        for path in archive_dir.iterdir()
    }


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
        lambda archive_type="manual":
            archive_type == "auto"
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

    def fake_archive(
        archive_type="manual"
    ):

        called.append(
            archive_type
        )

        return True

    monkeypatch.setattr(
        project,
        "archive",
        fake_archive
    )

    assert project.archive_if_changed() is True

    assert called == [
        "auto"
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

    monkeypatch.setattr(
        project,
        "_rotate_archives",
        lambda: None
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

    names = (
        "fusion-auto-2026-09-01_080000.json",
        "fusion-auto-2026-09-01_200000.json"
    )

    for name in names:

        create_archive(
            archive_dir,
            name
        )

    removed = []

    def failing_remove(
        filename
    ):

        removed.append(
            os.path.basename(
                filename
            )
        )

        raise OSError(
            "simulated failure"
        )

    monkeypatch.setattr(
        fusion_project.os,
        "remove",
        failing_remove
    )

    #
    # Le 1er septembre est dans la
    # classe quotidienne.
    #
    # L'archive de 08:00 doit donc
    # être candidate à la suppression.
    #
    # L'exception OSError doit être
    # absorbée.
    #
    project._rotate_archives(
        today=date(
            2026,
            10,
            7
        )
    )

    assert removed == [
        "fusion-auto-2026-09-01_080000.json"
    ]

    #
    # os.remove() ayant échoué,
    # les deux fichiers existent
    # toujours physiquement.
    #
    assert archive_names(
        archive_dir
    ) == set(
        names
    )


def test_parse_archive_filename_auto(
    project
):

    result = project._parse_archive_filename(
        "fusion-auto-2026-10-07_142530.json"
    )

    assert result == {
        "type": "auto",
        "timestamp": datetime(
            2026,
            10,
            7,
            14,
            25,
            30
        ),
        "suffix": None
    }


def test_parse_archive_filename_manual(
    project
):

    result = project._parse_archive_filename(
        "fusion-manual-2026-10-07_142530.json"
    )

    assert result == {
        "type": "manual",
        "timestamp": datetime(
            2026,
            10,
            7,
            14,
            25,
            30
        ),
        "suffix": None
    }


def test_parse_archive_filename_legacy(
    project
):

    result = project._parse_archive_filename(
        "fusion-2026-10-07_142530.json"
    )

    assert result == {
        "type": "legacy",
        "timestamp": datetime(
            2026,
            10,
            7,
            14,
            25,
            30
        ),
        "suffix": None
    }


def test_parse_archive_filename_auto_suffix(
    project
):

    result = project._parse_archive_filename(
        "fusion-auto-2026-10-07_142530-2.json"
    )

    assert result["type"] == "auto"
    assert result["suffix"] == 2


def test_parse_archive_filename_manual_suffix(
    project
):

    result = project._parse_archive_filename(
        "fusion-manual-2026-10-07_142530-3.json"
    )

    assert result["type"] == "manual"
    assert result["suffix"] == 3

def test_parse_archive_filename_rejects_invalid_date(
    project
):

    assert project._parse_archive_filename(
        "fusion-auto-2026-02-30_120000.json"
    ) is None


def test_parse_archive_filename_rejects_invalid_time(
    project
):

    assert project._parse_archive_filename(
        "fusion-auto-2026-10-07_250000.json"
    ) is None


def test_parse_archive_filename_rejects_zero_suffix(
    project
):

    assert project._parse_archive_filename(
        "fusion-auto-2026-10-07_120000-0.json"
    ) is None


def test_parse_archive_filename_rejects_malformed_name(
    project
):

    assert project._parse_archive_filename(
        "fusion-auto-2026-10-07_120000-copy.json"
    ) is None


def test_parse_archive_filename_rejects_unknown_file(
    project
):

    assert project._parse_archive_filename(
        "fusion-test.json"
    ) is None


def test_parse_archive_filename_uses_project_basename(
    tmp_path
):

    project_file = (
        tmp_path
        / "test-project.json"
    )

    project = FusionProject(
        filename=str(
            project_file
        )
    )

    result = project._parse_archive_filename(
        "test-project-auto-2026-10-07_120000.json"
    )

    assert result is not None
    assert result["type"] == "auto"

    assert project._parse_archive_filename(
        "fusion-auto-2026-10-07_120000.json"
    ) is None


def test_rotate_archives_age_14_keeps_all(
    project,
    monkeypatch,
    tmp_path
):

    archive_dir = tmp_path / "archives"
    archive_dir.mkdir()

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    create_archive(
        archive_dir,
        "fusion-auto-2026-09-23_080000.json"
    )
    create_archive(
        archive_dir,
        "fusion-auto-2026-09-23_200000.json"
    )

    project._rotate_archives(
        today=date(
            2026,
            10,
            7
        )
    )

    assert archive_names(
        archive_dir
    ) == {
        "fusion-auto-2026-09-23_080000.json",
        "fusion-auto-2026-09-23_200000.json"
    }


def test_rotate_archives_age_15_keeps_last_daily(
    project,
    monkeypatch,
    tmp_path
):

    archive_dir = tmp_path / "archives"
    archive_dir.mkdir()

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    create_archive(
        archive_dir,
        "fusion-auto-2026-09-22_080000.json"
    )
    create_archive(
        archive_dir,
        "fusion-auto-2026-09-22_200000.json"
    )

    project._rotate_archives(
        today=date(
            2026,
            10,
            7
        )
    )

    assert archive_names(
        archive_dir
    ) == {
        "fusion-auto-2026-09-22_200000.json"
    }


def test_rotate_archives_age_60_keeps_last_daily(
    project,
    monkeypatch,
    tmp_path
):

    archive_dir = tmp_path / "archives"
    archive_dir.mkdir()

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    create_archive(
        archive_dir,
        "fusion-auto-2026-08-08_080000.json"
    )
    create_archive(
        archive_dir,
        "fusion-auto-2026-08-08_200000.json"
    )

    project._rotate_archives(
        today=date(
            2026,
            10,
            7
        )
    )

    assert archive_names(
        archive_dir
    ) == {
        "fusion-auto-2026-08-08_200000.json"
    }


def test_rotate_archives_age_61_keeps_last_weekly(
    project,
    monkeypatch,
    tmp_path
):

    archive_dir = tmp_path / "archives"
    archive_dir.mkdir()

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    create_archive(
        archive_dir,
        "fusion-auto-2026-08-03_080000.json"
    )
    create_archive(
        archive_dir,
        "fusion-auto-2026-08-07_200000.json"
    )

    project._rotate_archives(
        today=date(
            2026,
            10,
            7
        )
    )

    assert archive_names(
        archive_dir
    ) == {
        "fusion-auto-2026-08-07_200000.json"
    }


def test_rotate_archives_age_180_keeps_last_weekly(
    project,
    monkeypatch,
    tmp_path
):

    archive_dir = tmp_path / "archives"
    archive_dir.mkdir()

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    create_archive(
        archive_dir,
        "fusion-auto-2026-04-10_080000.json"
    )
    create_archive(
        archive_dir,
        "fusion-auto-2026-04-11_200000.json"
    )

    project._rotate_archives(
        today=date(
            2026,
            10,
            7
        )
    )

    assert archive_names(
        archive_dir
    ) == {
        "fusion-auto-2026-04-11_200000.json"
    }


def test_rotate_archives_age_181_keeps_last_monthly(
    project,
    monkeypatch,
    tmp_path
):

    archive_dir = tmp_path / "archives"
    archive_dir.mkdir()

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    create_archive(
        archive_dir,
        "fusion-auto-2026-04-01_080000.json"
    )
    create_archive(
        archive_dir,
        "fusion-auto-2026-04-09_200000.json"
    )

    project._rotate_archives(
        today=date(
            2026,
            10,
            7
        )
    )

    assert archive_names(
        archive_dir
    ) == {
        "fusion-auto-2026-04-09_200000.json"
    }


def test_rotate_archives_week_cut_by_60_61(
    project,
    monkeypatch,
    tmp_path
):

    archive_dir = tmp_path / "archives"
    archive_dir.mkdir()

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    #
    # Même semaine ISO.
    #
    # 7 août : J-61 → hebdomadaire
    # 8 août : J-60 → quotidienne
    #
    create_archive(
        archive_dir,
        "fusion-auto-2026-08-07_080000.json"
    )
    create_archive(
        archive_dir,
        "fusion-auto-2026-08-08_080000.json"
    )
    create_archive(
        archive_dir,
        "fusion-auto-2026-08-08_200000.json"
    )

    project._rotate_archives(
        today=date(
            2026,
            10,
            7
        )
    )

    assert archive_names(
        archive_dir
    ) == {
        "fusion-auto-2026-08-07_080000.json",
        "fusion-auto-2026-08-08_200000.json"
    }


def test_rotate_archives_month_cut_by_180_181(
    project,
    monkeypatch,
    tmp_path
):

    archive_dir = tmp_path / "archives"
    archive_dir.mkdir()

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    #
    # Même mois.
    #
    # 9 avril  : J-181 → mensuelle
    # 10 avril : J-180 → hebdomadaire
    #
    create_archive(
        archive_dir,
        "fusion-auto-2026-04-09_080000.json"
    )
    create_archive(
        archive_dir,
        "fusion-auto-2026-04-10_080000.json"
    )
    create_archive(
        archive_dir,
        "fusion-auto-2026-04-10_200000.json"
    )

    project._rotate_archives(
        today=date(
            2026,
            10,
            7
        )
    )

    assert archive_names(
        archive_dir
    ) == {
        "fusion-auto-2026-04-09_080000.json",
        "fusion-auto-2026-04-10_200000.json"
    }


def test_rotate_archives_iso_week_crosses_new_year(
    project,
    monkeypatch,
    tmp_path
):

    archive_dir = tmp_path / "archives"
    archive_dir.mkdir()

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    #
    # Ces quatre dates appartiennent
    # toutes à la semaine ISO
    # 2004-W01.
    #
    create_archive(
        archive_dir,
        "fusion-auto-2003-12-29_080000.json"
    )
    create_archive(
        archive_dir,
        "fusion-auto-2003-12-31_120000.json"
    )
    create_archive(
        archive_dir,
        "fusion-auto-2004-01-01_160000.json"
    )
    create_archive(
        archive_dir,
        "fusion-auto-2004-01-04_200000.json"
    )

    project._rotate_archives(
        today=date(
            2004,
            3,
            15
        )
    )

    assert archive_names(
        archive_dir
    ) == {
        "fusion-auto-2004-01-04_200000.json"
    }


def test_rotate_archives_distinguishes_iso_weeks(
    project,
    monkeypatch,
    tmp_path
):

    archive_dir = tmp_path / "archives"
    archive_dir.mkdir()

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    #
    # 28 décembre 2003 :
    # 2003-W52
    #
    # 29 décembre 2003 et
    # 4 janvier 2004 :
    # 2004-W01
    #
    create_archive(
        archive_dir,
        "fusion-auto-2003-12-28_200000.json"
    )
    create_archive(
        archive_dir,
        "fusion-auto-2003-12-29_080000.json"
    )
    create_archive(
        archive_dir,
        "fusion-auto-2004-01-04_200000.json"
    )

    project._rotate_archives(
        today=date(
            2004,
            3,
            15
        )
    )

    assert archive_names(
        archive_dir
    ) == {
        "fusion-auto-2003-12-28_200000.json",
        "fusion-auto-2004-01-04_200000.json"
    }


def test_rotate_archives_keeps_last_monthly(
    project,
    monkeypatch,
    tmp_path
):

    archive_dir = tmp_path / "archives"
    archive_dir.mkdir()

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    create_archive(
        archive_dir,
        "fusion-auto-2026-01-05_080000.json"
    )
    create_archive(
        archive_dir,
        "fusion-auto-2026-01-20_120000.json"
    )
    create_archive(
        archive_dir,
        "fusion-auto-2026-01-31_200000.json"
    )

    create_archive(
        archive_dir,
        "fusion-auto-2026-02-01_080000.json"
    )
    create_archive(
        archive_dir,
        "fusion-auto-2026-02-28_200000.json"
    )

    project._rotate_archives(
        today=date(
            2026,
            10,
            7
        )
    )

    assert archive_names(
        archive_dir
    ) == {
        "fusion-auto-2026-01-31_200000.json",
        "fusion-auto-2026-02-28_200000.json"
    }


def test_rotate_archives_only_deletes_valid_auto(
    project,
    monkeypatch,
    tmp_path
):

    archive_dir = tmp_path / "archives"
    archive_dir.mkdir()

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    #
    # Deux AUTO valides du même jour
    # dans la classe quotidienne.
    #
    # 08:00 doit être supprimée.
    # 20:00 doit être conservée.
    #
    auto_old = (
        "fusion-auto-2026-09-01_080000.json"
    )
    auto_last = (
        "fusion-auto-2026-09-01_200000.json"
    )

    #
    # Tous ces fichiers doivent être
    # absolument intouchables.
    #
    protected = {
        #
        # LEGACY
        #
        "fusion-2026-09-01_080000.json",

        #
        # MANUAL
        #
        "fusion-manual-2026-09-01_080000.json",

        #
        # Ressemble à AUTO,
        # mais nom mal formé.
        #
        "fusion-auto-2026-09-01_080000-copy.json",

        #
        # Date impossible.
        #
        "fusion-auto-2026-02-30_080000.json",

        #
        # Heure impossible.
        #
        "fusion-auto-2026-09-01_250000.json",

        #
        # Mauvais projet.
        #
        "other-auto-2026-09-01_080000.json",

        #
        # Fichier quelconque.
        #
        "notes.json"
    }

    for filename in (
        auto_old,
        auto_last,
        *protected
    ):

        create_archive(
            archive_dir,
            filename
        )

    project._rotate_archives(
        today=date(
            2026,
            10,
            7
        )
    )

    assert archive_names(
        archive_dir
    ) == (
        protected
        | {
            auto_last
        }
    )


def test_rotate_archives_without_valid_auto_deletes_nothing(
    project,
    monkeypatch,
    tmp_path
):

    archive_dir = tmp_path / "archives"
    archive_dir.mkdir()

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    names = {
        "fusion-2026-01-01_120000.json",
        "fusion-manual-2026-01-01_120000.json",
        "fusion-auto-invalid.json",
        "fusion-auto-2026-02-30_120000.json",
        "notes.json"
    }

    for filename in names:

        create_archive(
            archive_dir,
            filename
        )

    project._rotate_archives(
        today=date(
            2026,
            10,
            7
        )
    )

    assert archive_names(
        archive_dir
    ) == names


def test_rotate_archives_is_deterministic(
    project,
    monkeypatch,
    tmp_path
):

    today = date(
        2026,
        10,
        7
    )

    names = [
        #
        # Classe quotidienne
        #
        "fusion-auto-2026-09-01_080000.json",
        "fusion-auto-2026-09-01_200000.json",

        #
        # Classe hebdomadaire
        #
        "fusion-auto-2026-07-06_080000.json",
        "fusion-auto-2026-07-10_200000.json",

        #
        # Classe mensuelle
        #
        "fusion-auto-2026-01-05_080000.json",
        "fusion-auto-2026-01-31_200000.json",

        #
        # Protégées
        #
        "fusion-2026-01-01_120000.json",
        "fusion-manual-2026-01-01_120000.json"
    ]

    orders = (
        names,
        list(
            reversed(
                names
            )
        ),
        [
            names[4],
            names[0],
            names[7],
            names[2],
            names[5],
            names[1],
            names[6],
            names[3]
        ]
    )

    expected = {
        "fusion-auto-2026-09-01_200000.json",
        "fusion-auto-2026-07-10_200000.json",
        "fusion-auto-2026-01-31_200000.json",
        "fusion-2026-01-01_120000.json",
        "fusion-manual-2026-01-01_120000.json"
    }

    results = []

    for index, order in enumerate(
        orders
    ):

        archive_dir = (
            tmp_path
            / f"archives-{index}"
        )

        archive_dir.mkdir()

        for filename in names:

            create_archive(
                archive_dir,
                filename
            )

        monkeypatch.setattr(
            fusion_project,
            "ARCHIVE_DIR",
            str(archive_dir)
        )

        original_listdir = os.listdir

        def ordered_listdir(
            path,
            order=order
        ):

            if str(path) == str(
                archive_dir
            ):

                return list(
                    order
                )

            return original_listdir(
                path
            )

        monkeypatch.setattr(
            fusion_project.os,
            "listdir",
            ordered_listdir
        )

        project._rotate_archives(
            today=today
        )

        result = archive_names(
            archive_dir
        )

        results.append(
            result
        )

        assert result == expected

    assert (
        results[0]
        == results[1]
        == results[2]
    )


def test_rotate_archives_is_idempotent(
    project,
    monkeypatch,
    tmp_path
):

    archive_dir = tmp_path / "archives"
    archive_dir.mkdir()

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    names = {
        #
        # Quotidienne
        #
        "fusion-auto-2026-09-01_080000.json",
        "fusion-auto-2026-09-01_200000.json",

        #
        # Hebdomadaire
        #
        "fusion-auto-2026-07-06_080000.json",
        "fusion-auto-2026-07-10_200000.json",

        #
        # Mensuelle
        #
        "fusion-auto-2026-01-05_080000.json",
        "fusion-auto-2026-01-31_200000.json",

        #
        # Protégées
        #
        "fusion-2026-01-01_120000.json",
        "fusion-manual-2026-01-01_120000.json"
    }

    for filename in names:

        create_archive(
            archive_dir,
            filename
        )

    today = date(
        2026,
        10,
        7
    )

    project._rotate_archives(
        today=today
    )

    after_first = archive_names(
        archive_dir
    )

    project._rotate_archives(
        today=today
    )

    after_second = archive_names(
        archive_dir
    )

    assert after_second == after_first


def test_archive_creates_manual_archive(
    project,
    tmp_path,
    monkeypatch
):

    archive_dir = tmp_path / "archives"

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    monkeypatch.setattr(
        fusion_project.time,
        "strftime",
        lambda format:
            "2026-10-07_143000"
    )

    assert project.save_safe(
        allowed_errors=[]
    )

    assert project.archive() is True

    assert (
        archive_dir
        / "fusion-manual-2026-10-07_143000.json"
    ).exists()


def test_archive_creates_auto_archive(
    project,
    tmp_path,
    monkeypatch
):

    archive_dir = tmp_path / "archives"

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    monkeypatch.setattr(
        fusion_project.time,
        "strftime",
        lambda format:
            "2026-10-07_143000"
    )

    assert project.save_safe(
        allowed_errors=[]
    )

    assert project.archive(
        archive_type="auto"
    ) is True

    assert (
        archive_dir
        / "fusion-auto-2026-10-07_143000.json"
    ).exists()


def test_archive_manual_collision_does_not_overwrite(
    project,
    tmp_path,
    monkeypatch
):

    archive_dir = tmp_path / "archives"

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    monkeypatch.setattr(
        fusion_project.time,
        "strftime",
        lambda format:
            "2026-10-07_143000"
    )

    assert project.save_safe(
        allowed_errors=[]
    )

    project_file = Path(
        project.filename
    )

    project_file.write_text(
        "first",
        encoding="utf-8"
    )

    assert project.archive() is True

    original = (
        archive_dir
        / "fusion-manual-2026-10-07_143000.json"
    )

    assert original.read_text(
        encoding="utf-8"
    ) == "first"

    project_file.write_text(
        "second",
        encoding="utf-8"
    )

    assert project.archive() is True

    collision = (
        archive_dir
        / "fusion-manual-2026-10-07_143000-1.json"
    )

    assert original.read_text(
        encoding="utf-8"
    ) == "first"

    assert collision.read_text(
        encoding="utf-8"
    ) == "second"


def test_archive_collision_increments_suffix(
    project,
    tmp_path,
    monkeypatch
):

    archive_dir = tmp_path / "archives"

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    monkeypatch.setattr(
        fusion_project.time,
        "strftime",
        lambda format:
            "2026-10-07_143000"
    )

    assert project.save_safe(
        allowed_errors=[]
    )

    assert project.archive() is True
    assert project.archive() is True
    assert project.archive() is True

    assert archive_names(
        archive_dir
    ) == {
        "fusion-manual-2026-10-07_143000.json",
        "fusion-manual-2026-10-07_143000-1.json",
        "fusion-manual-2026-10-07_143000-2.json"
    }


def test_archive_rejects_invalid_type(
    project,
    tmp_path,
    monkeypatch
):

    archive_dir = tmp_path / "archives"

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    assert project.save_safe(
        allowed_errors=[]
    )

    assert project.archive(
        archive_type="legacy"
    ) is False

    assert not archive_dir.exists()


@pytest.mark.parametrize(
    "archive_name",
    [
        "fusion-2026-01-01_120000.json",
        "fusion-manual-2026-01-01_120000.json",
        "fusion-auto-2026-01-01_120000.json"
    ]
)
def test_archive_if_changed_deduplicates_against_recognized_archives(
    project,
    monkeypatch,
    tmp_path,
    archive_name
):

    archive_dir = tmp_path / "archives"
    archive_dir.mkdir()

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    project.filename = str(
        tmp_path / "fusion.json"
    )

    Path(
        project.filename
    ).write_text(
        "same content",
        encoding="utf-8"
    )

    create_archive(
        archive_dir,
        archive_name,
        content="same content"
    )

    called = []

    def fake_archive(
        archive_type="manual"
    ):

        called.append(
            archive_type
        )

        return True

    monkeypatch.setattr(
        project,
        "archive",
        fake_archive
    )

    assert (
        project.archive_if_changed()
        is False
    )

    assert called == []


def test_archive_if_changed_ignores_unrecognized_duplicate(
    project,
    monkeypatch,
    tmp_path
):

    archive_dir = tmp_path / "archives"
    archive_dir.mkdir()

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    project.filename = str(
        tmp_path / "fusion.json"
    )

    Path(
        project.filename
    ).write_text(
        "same content",
        encoding="utf-8"
    )

    create_archive(
        archive_dir,
        "fusion-auto-invalid.json",
        content="same content"
    )

    called = []

    def fake_archive(
        archive_type="manual"
    ):

        called.append(
            archive_type
        )

        return True

    monkeypatch.setattr(
        project,
        "archive",
        fake_archive
    )

    assert (
        project.archive_if_changed()
        is True
    )

    assert called == [
        "auto"
    ]


def test_rotate_archives_protects_future_auto(
    project,
    monkeypatch,
    tmp_path
):

    archive_dir = tmp_path / "archives"
    archive_dir.mkdir()

    monkeypatch.setattr(
        fusion_project,
        "ARCHIVE_DIR",
        str(archive_dir)
    )

    names = {
        "fusion-auto-2026-10-08_080000.json",
        "fusion-auto-2026-10-08_200000.json"
    }

    for filename in names:

        create_archive(
            archive_dir,
            filename
        )

    project._rotate_archives(
        today=date(
            2026,
            10,
            7
        )
    )

    assert archive_names(
        archive_dir
    ) == names
