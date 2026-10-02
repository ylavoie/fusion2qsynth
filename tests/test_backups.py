#!/usr/bin/env python3

import os
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
