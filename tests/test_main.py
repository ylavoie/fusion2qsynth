import builtins

import pytest

import fusion2qsynth


def test_show_status(
    monkeypatch,
    capsys
):

    monkeypatch.setattr(
        fusion2qsynth,
        "system_status",
        lambda project: {
            "fusion": True,
            "fluidsynth": False,
            "instrument_count": 10,
            "mix_count": 20,
            "program_count": 30,
            "song_count": 40,
        }
    )

    fusion2qsynth.show_status(
        object()
    )

    output = capsys.readouterr().out

    assert "Fusion MIDI     : OK" in output
    assert "FluidSynth MIDI : absent" in output
    assert "Instruments enregistrés : 10" in output
    assert "Mix enregistrés         : 20" in output
    assert "Programs enregistrés    : 30" in output
    assert "Songs enregistrées      : 40" in output


def test_choose_backup_restore_no_backups(
    monkeypatch,
    capsys
):

    monkeypatch.setattr(
        fusion2qsynth.FusionProject,
        "list_backups",
        lambda: []
    )

    result = (
        fusion2qsynth.choose_backup_restore()
    )

    assert result is None

    output = capsys.readouterr().out

    assert (
        "Aucune sauvegarde disponible."
        in output
    )


def test_choose_backup_restore_select(
    monkeypatch,
    capsys
):

    backups = [
        {
            "filename": "fusion.json.bak",
            "size": "8 Ko",
            "time": "01-10-2026 12:00:00",
        },
        {
            "filename": "fusion.json.bak1",
            "size": "4 Ko",
            "time": "30-09-2026 12:00:00",
        },
    ]

    monkeypatch.setattr(
        fusion2qsynth.FusionProject,
        "list_backups",
        lambda: backups
    )

    monkeypatch.setattr(
        builtins,
        "input",
        lambda prompt: "2"
    )

    result = (
        fusion2qsynth.choose_backup_restore()
    )

    assert result is backups[1]

    output = capsys.readouterr().out

    assert "fusion.json.bak" in output
    assert "fusion.json.bak1" in output
    assert "8 Ko" in output
    assert "01-10-2026 12:00:00" in output


@pytest.mark.parametrize(
    "choice",
    [
        "q",
        "Q",
        "invalid",
        "99",
    ]
)
def test_choose_backup_restore_cancel_or_invalid(
    monkeypatch,
    choice
):

    monkeypatch.setattr(
        fusion2qsynth.FusionProject,
        "list_backups",
        lambda: [
            {
                "filename": "fusion.json.bak",
                "size": "8 Ko",
                "time": "01-10-2026 12:00:00",
            }
        ]
    )

    monkeypatch.setattr(
        builtins,
        "input",
        lambda prompt: choice
    )

    assert (
        fusion2qsynth.choose_backup_restore()
        is None
    )


def test_choose_archive_restore_no_archives(
    monkeypatch,
    capsys
):

    monkeypatch.setattr(
        fusion2qsynth.FusionProject,
        "list_archives",
        lambda: []
    )

    result = (
        fusion2qsynth.choose_archive_restore()
    )

    assert result is None

    assert (
        "Aucune archive disponible."
        in capsys.readouterr().out
    )


def test_choose_archive_restore_select(
    monkeypatch
):

    archives = [
        {
            "name": "Archive 1",
            "filename": "archive-1.json",
        },
        {
            "name": "Archive 2",
            "filename": "archive-2.json",
        },
    ]

    monkeypatch.setattr(
        fusion2qsynth.FusionProject,
        "list_archives",
        lambda: archives
    )

    monkeypatch.setattr(
        builtins,
        "input",
        lambda prompt: "2"
    )

    result = (
        fusion2qsynth.choose_archive_restore()
    )

    assert result is archives[1]


@pytest.mark.parametrize(
    "choice",
    [
        "q",
        "Q",
        "invalid",
        "99",
    ]
)
def test_choose_archive_restore_cancel_or_invalid(
    monkeypatch,
    choice
):

    monkeypatch.setattr(
        fusion2qsynth.FusionProject,
        "list_archives",
        lambda: [
            {
                "name": "Archive",
                "filename": "archive.json",
            }
        ]
    )

    monkeypatch.setattr(
        builtins,
        "input",
        lambda prompt: choice
    )

    assert (
        fusion2qsynth.choose_archive_restore()
        is None
    )


def test_main_runtime_error(
    monkeypatch,
    capsys
):

    def raise_error():

        raise RuntimeError(
            "Projet invalide"
        )

    monkeypatch.setattr(
        fusion2qsynth,
        "FusionProject",
        raise_error
    )

    with pytest.raises(
        SystemExit
    ) as exc:

        fusion2qsynth.main()

    assert exc.value.code == 1

    output = capsys.readouterr().out

    assert "Erreur projet" in output
    assert "Projet invalide" in output
    assert "Le programme va se terminer." in output


def test_main_recovery_cancelled(
    monkeypatch,
    capsys
):

    class DummyFusionProject:

        def __init__(self):

            raise (
                fusion2qsynth.ProjectRecoveryError(
                    "fusion.json invalide"
                )
            )

    monkeypatch.setattr(
        fusion2qsynth,
        "FusionProject",
        DummyFusionProject
    )

    monkeypatch.setattr(
        fusion2qsynth,
        "choose_backup_restore",
        lambda: None
    )

    with pytest.raises(
        SystemExit
    ) as exc:

        fusion2qsynth.main()

    assert exc.value.code == 1

    output = capsys.readouterr().out

    assert "Projet récupérable" in output
    assert "fusion.json invalide" in output
    assert "Aucune restauration effectuée." in output


def test_main_recovery_restore_failed(
    monkeypatch,
    capsys
):

    class DummyFusionProject:

        def __init__(self):

            raise (
                fusion2qsynth.ProjectRecoveryError(
                    "fusion.json invalide"
                )
            )

        @staticmethod
        def restore_from_backup(
            filename
        ):

            assert (
                filename
                == "fusion.json.bak"
            )

            return None

    monkeypatch.setattr(
        fusion2qsynth,
        "FusionProject",
        DummyFusionProject
    )

    monkeypatch.setattr(
        fusion2qsynth,
        "choose_backup_restore",
        lambda: {
            "filename":
                "fusion.json.bak"
        }
    )

    with pytest.raises(
        SystemExit
    ) as exc:

        fusion2qsynth.main()

    assert exc.value.code == 1

    assert (
        "Restauration impossible."
        in capsys.readouterr().out
    )


def test_main_recovery_restore_success(
    monkeypatch,
    capsys
):

    restored_project = object()

    class DummyFusionProject:

        def __init__(self):

            raise (
                fusion2qsynth.ProjectRecoveryError(
                    "fusion.json invalide"
                )
            )

        @staticmethod
        def restore_from_backup(
            filename
        ):

            assert (
                filename
                == "fusion.json.bak"
            )

            return restored_project

    monkeypatch.setattr(
        fusion2qsynth,
        "FusionProject",
        DummyFusionProject
    )

    monkeypatch.setattr(
        fusion2qsynth,
        "choose_backup_restore",
        lambda: {
            "filename":
                "fusion.json.bak"
        }
    )

    monkeypatch.setattr(
        fusion2qsynth,
        "show_status",
        lambda project: None
    )

    monkeypatch.setattr(
        builtins,
        "input",
        lambda prompt: "q"
    )

    # Le projet restauré doit pouvoir traiter
    # la sortie normale du programme.
    class RestoredProject:

        def __init__(self):

            self.archived = False

        def archive_if_changed(self):

            self.archived = True

    restored = RestoredProject()

    DummyFusionProject.restore_from_backup = (
        staticmethod(
            lambda filename: restored
        )
    )

    fusion2qsynth.main()

    assert restored.archived is True

    assert (
        "Restauration réussie."
        in capsys.readouterr().out
    )


def test_main_recovery_restore_success(
    monkeypatch,
    capsys
):

    class RestoredProject:

        def __init__(self):

            self.archived = False

        def archive_if_changed(self):

            self.archived = True

    restored = RestoredProject()

    class DummyFusionProject:

        def __init__(self):

            raise (
                fusion2qsynth.ProjectRecoveryError(
                    "fusion.json invalide"
                )
            )

        @staticmethod
        def restore_from_backup(
            filename
        ):

            assert (
                filename
                == "fusion.json.bak"
            )

            return restored

    monkeypatch.setattr(
        fusion2qsynth,
        "FusionProject",
        DummyFusionProject
    )

    monkeypatch.setattr(
        fusion2qsynth,
        "choose_backup_restore",
        lambda: {
            "filename":
                "fusion.json.bak"
        }
    )

    monkeypatch.setattr(
        fusion2qsynth,
        "show_status",
        lambda project: None
    )

    monkeypatch.setattr(
        builtins,
        "input",
        lambda prompt: "q"
    )

    fusion2qsynth.main()

    assert restored.archived is True

    assert (
        "Restauration réussie."
        in capsys.readouterr().out
    )


@pytest.mark.parametrize(
    (
        "choice",
        "module"
    ),
    [
        (
            "1",
            fusion2qsynth.fusion_capture
        ),
        (
            "2",
            fusion2qsynth.fusion_editor
        ),
        (
            "3",
            fusion2qsynth.fusion_controller
        ),
        (
            "4",
            fusion2qsynth.fusion_monitor
        ),
    ]
)
def test_main_dispatches_modules(
    monkeypatch,
    choice,
    module
):

    calls = []

    class DummyProject:

        def archive_if_changed(self):

            pass

    monkeypatch.setattr(
        fusion2qsynth,
        "FusionProject",
        DummyProject
    )

    monkeypatch.setattr(
        fusion2qsynth,
        "show_status",
        lambda project: None
    )

    monkeypatch.setattr(
        module,
        "main",
        lambda: calls.append(
            choice
        )
    )

    choices = iter([
        choice,
        "q",
    ])

    monkeypatch.setattr(
        builtins,
        "input",
        lambda prompt: next(
            choices
        )
    )

    fusion2qsynth.main()

    assert calls == [
        choice
    ]


@pytest.mark.parametrize(
    (
        "archive_result",
        "expected"
    ),
    [
        (
            True,
            "Archive créée."
        ),
        (
            False,
            "Échec de l'archivage."
        ),
    ]
)
def test_main_archive(
    monkeypatch,
    capsys,
    archive_result,
    expected
):

    class DummyProject:

        def archive(self):

            return archive_result

        def archive_if_changed(self):

            pass

    monkeypatch.setattr(
        fusion2qsynth,
        "FusionProject",
        DummyProject
    )

    monkeypatch.setattr(
        fusion2qsynth,
        "show_status",
        lambda project: None
    )

    choices = iter([
        "5",
        "q",
    ])

    monkeypatch.setattr(
        builtins,
        "input",
        lambda prompt: next(
            choices
        )
    )

    fusion2qsynth.main()

    assert (
        expected
        in capsys.readouterr().out
    )


def test_main_archive_restore_cancelled(
    monkeypatch
):

    class DummyProject:

        def archive_if_changed(self):

            pass

    monkeypatch.setattr(
        fusion2qsynth,
        "FusionProject",
        DummyProject
    )

    monkeypatch.setattr(
        fusion2qsynth,
        "show_status",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion2qsynth,
        "choose_archive_restore",
        lambda: None
    )

    choices = iter([
        "6",
        "q",
    ])

    monkeypatch.setattr(
        builtins,
        "input",
        lambda prompt: next(
            choices
        )
    )

    fusion2qsynth.main()


def test_main_archive_restore_failed(
    monkeypatch,
    capsys
):

    class DummyProject:

        def archive_if_changed(self):

            pass

        @staticmethod
        def restore_from_archive(
            filename
        ):

            assert (
                filename
                == "archive.json"
            )

            return None

    monkeypatch.setattr(
        fusion2qsynth,
        "FusionProject",
        DummyProject
    )

    monkeypatch.setattr(
        fusion2qsynth,
        "show_status",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion2qsynth,
        "choose_archive_restore",
        lambda: {
            "filename":
                "archive.json"
        }
    )

    choices = iter([
        "6",
        "q",
    ])

    monkeypatch.setattr(
        builtins,
        "input",
        lambda prompt: next(
            choices
        )
    )

    fusion2qsynth.main()

    assert (
        "Restauration impossible."
        in capsys.readouterr().out
    )


def test_main_archive_restore_success(
    monkeypatch,
    capsys
):

    class InitialProject:

        pass

    class RestoredProject:

        def __init__(self):

            self.archived = False

        def archive_if_changed(self):

            self.archived = True

    restored = RestoredProject()

    class DummyFusionProject:

        def __new__(cls):

            return InitialProject()

        @staticmethod
        def restore_from_archive(
            filename
        ):

            assert (
                filename
                == "archive.json"
            )

            return restored

    monkeypatch.setattr(
        fusion2qsynth,
        "FusionProject",
        DummyFusionProject
    )

    monkeypatch.setattr(
        fusion2qsynth,
        "show_status",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion2qsynth,
        "choose_archive_restore",
        lambda: {
            "filename":
                "archive.json"
        }
    )

    choices = iter([
        "6",
        "q",
    ])

    monkeypatch.setattr(
        builtins,
        "input",
        lambda prompt: next(
            choices
        )
    )

    fusion2qsynth.main()

    assert restored.archived is True

    assert (
        "Archive restaurée."
        in capsys.readouterr().out
    )
