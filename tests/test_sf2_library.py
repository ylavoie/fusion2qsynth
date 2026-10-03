import json
import pytest
import runpy
import subprocess
import sys

import sf2_library


def test_dump_sf2(
    monkeypatch
):

    class Result:

        returncode = 0
        stdout = "SF2 output"
        stderr = ""

    calls = []

    def fake_run(
        command,
        capture_output,
        text
    ):

        calls.append(
            (
                command,
                capture_output,
                text,
            )
        )

        return Result()

    monkeypatch.setattr(
        sf2_library.subprocess,
        "run",
        fake_run
    )

    result = (
        sf2_library.dump_sf2(
            "test.sf2"
        )
    )

    assert result == "SF2 output"

    assert calls == [
        (
            [
                sf2_library.SF2DUMP,
                "test.sf2",
            ],
            True,
            True,
        )
    ]


def test_dump_sf2_error(
    monkeypatch
):

    class Result:

        returncode = 1
        stdout = ""
        stderr = "sf2dump failed"

    monkeypatch.setattr(
        sf2_library.subprocess,
        "run",
        lambda *args, **kwargs:
            Result()
    )

    with pytest.raises(
        Exception,
        match="sf2dump failed"
    ):

        sf2_library.dump_sf2(
            "test.sf2"
        )


def test_parse_presets():

    text = """
Ignored line
Grand Piano (Preset: 0, Bank: 0)
Stereo Strings (Preset: 48, Bank: 0)
My Special-Preset! (Preset: 12, Bank: 3)
"""

    assert (
        sf2_library.parse_presets(
            text
        )
        == [
            {
                "id":
                    "grand_piano",
                "name":
                    "Grand Piano",
                "sf2_bank":
                    0,
                "sf2_program":
                    0,
            },
            {
                "id":
                    "stereo_strings",
                "name":
                    "Stereo Strings",
                "sf2_bank":
                    0,
                "sf2_program":
                    48,
            },
            {
                "id":
                    "my_special_preset",
                "name":
                    "My Special-Preset!",
                "sf2_bank":
                    3,
                "sf2_program":
                    12,
            },
        ]
    )


def test_parse_presets_empty():

    assert (
        sf2_library.parse_presets(
            "No presets here"
        )
        == []
    )


def test_build_library(
    monkeypatch
):

    monkeypatch.setattr(
        sf2_library,
        "dump_sf2",
        lambda filename:
            "dump content"
    )

    presets = [
        {
            "id": "piano",
        }
    ]

    monkeypatch.setattr(
        sf2_library,
        "parse_presets",
        lambda text:
            presets
    )

    result = (
        sf2_library.build_library(
            "test.sf2"
        )
    )

    assert result == {
        "soundfont":
            "test.sf2",
        "presets":
            presets,
    }


def test_load_library_missing(
    monkeypatch,
    capsys
):

    monkeypatch.setattr(
        sf2_library.os.path,
        "exists",
        lambda filename:
            False
    )

    assert (
        sf2_library.load_library()
        == {}
    )

    assert (
        "Bibliothèque SF2 absente"
        in capsys.readouterr().out
    )


def test_load_library(
    monkeypatch,
    tmp_path
):

    filename = (
        tmp_path
        / "sf2_library.json"
    )

    data = {
        "soundfont":
            "test.sf2",
        "presets":
            [],
    }

    filename.write_text(
        json.dumps(
            data
        ),
        encoding="utf-8"
    )

    monkeypatch.setattr(
        sf2_library,
        "SF2_FILE",
        str(filename)
    )

    assert (
        sf2_library.load_library()
        == data
    )


def test_list_presets(
    monkeypatch
):

    monkeypatch.setattr(
        sf2_library,
        "load_library",
        lambda: {
            "presets": [
                {
                    "sf2_bank": 1,
                    "sf2_program": 0,
                },
                {
                    "sf2_bank": 0,
                    "sf2_program": 10,
                },
                {
                    "sf2_bank": 0,
                    "sf2_program": 2,
                },
            ]
        }
    )

    presets = (
        sf2_library.list_presets()
    )

    assert [
        (
            p["sf2_bank"],
            p["sf2_program"],
        )
        for p in presets
    ] == [
        (
            0,
            2,
        ),
        (
            0,
            10,
        ),
        (
            1,
            0,
        ),
    ]


def test_list_presets_missing_presets(
    monkeypatch
):

    monkeypatch.setattr(
        sf2_library,
        "load_library",
        lambda: {}
    )

    assert (
        sf2_library.list_presets()
        == []
    )


def test_save_library(
    tmp_path
):

    filename = (
        tmp_path
        / "library.json"
    )

    library = {
        "soundfont":
            "test.sf2",
        "presets": [
            {
                "name":
                    "Piano été",
            }
        ],
    }

    sf2_library.save_library(
        library,
        filename=str(filename)
    )

    assert (
        json.loads(
            filename.read_text(
                encoding="utf-8"
            )
        )
        == library
    )

    # ensure_ascii=False :
    # le caractère doit rester lisible.
    assert (
        "été"
        in filename.read_text(
            encoding="utf-8"
        )
    )


def test_show_presets(
    capsys
):

    presets = [
        {
            "id":
                "grand_piano",
            "name":
                "Grand Piano",
            "sf2_bank":
                0,
            "sf2_program":
                0,
        },
        {
            "id":
                "strings",
            "name":
                "Strings",
            "sf2_bank":
                1,
            "sf2_program":
                48,
        },
    ]

    sf2_library.show_presets(
        presets
    )

    output = (
        capsys.readouterr().out
    )

    assert (
        "2 presets trouvés"
        in output
    )

    assert (
        "grand_piano : "
        "Bank 0 Program 0 "
        "- Grand Piano"
        in output
    )

    assert (
        "strings : "
        "Bank 1 Program 48 "
        "- Strings"
        in output
    )


def test_cli_without_argument(
    monkeypatch,
    capsys
):

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "sf2_library.py"
        ]
    )

    with pytest.raises(
        SystemExit
    ) as exc:

        runpy.run_module(
            "sf2_library",
            run_name="__main__"
        )

    assert exc.value.code == 1

    assert (
        "Usage : sf2_library.py fichier.sf2"
        in capsys.readouterr().out
    )


def test_cli_builds_and_saves_library(
    monkeypatch,
    tmp_path,
    capsys
):

    class Result:

        returncode = 0
        stderr = ""

        stdout = (
            "Grand Piano "
            "(Preset: 0, Bank: 0)\n"
        )

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs:
            Result()
    )

    monkeypatch.chdir(
        tmp_path
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "sf2_library.py",
            "test.sf2",
        ]
    )

    runpy.run_module(
        "sf2_library",
        run_name="__main__"
    )

    output = (
        capsys.readouterr().out
    )

    assert (
        "1 presets trouvés"
        in output
    )

    assert (
        "Bibliothèque sauvegardée"
        in output
    )

    filename = (
        tmp_path
        / "sf2_library.json"
    )

    assert filename.exists()

    data = json.loads(
        filename.read_text(
            encoding="utf-8"
        )
    )

    assert (
        data["soundfont"]
        == "test.sf2"
    )

    assert data["presets"] == [
        {
            "id":
                "grand_piano",
            "name":
                "Grand Piano",
            "sf2_bank":
                0,
            "sf2_program":
                0,
        }
    ]
