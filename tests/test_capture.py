import builtins

import pytest

import fusion_capture


def test_main_missing_fusion(
    monkeypatch
):

    monkeypatch.setattr(
        fusion_capture,
        "find_fusion_input",
        lambda: None
    )

    with pytest.raises(
        Exception,
        match="Fusion MIDI introuvable"
    ):

        fusion_capture.main()


@pytest.mark.parametrize(
    (
        "choice",
        "function_name"
    ),
    [
        (
            "1",
            "capture_mix"
        ),
        (
            "2",
            "capture_program"
        ),
        (
            "3",
            "capture_song"
        ),
    ]
)
def test_main_dispatch(
    monkeypatch,
    choice,
    function_name
):

    port_name = "Fusion MIDI"
    project = object()

    calls = []

    monkeypatch.setattr(
        fusion_capture,
        "find_fusion_input",
        lambda:
            port_name
    )

    monkeypatch.setattr(
        fusion_capture,
        "FusionProject",
        lambda:
            project
    )

    monkeypatch.setattr(
        fusion_capture,
        function_name,
        lambda project_arg, port_arg:
            calls.append(
                (
                    project_arg,
                    port_arg
                )
            )
    )

    choices = iter([
        choice,
        "q",
    ])

    monkeypatch.setattr(
        builtins,
        "input",
        lambda prompt:
            next(choices)
    )

    fusion_capture.main()

    assert calls == [
        (
            project,
            port_name
        )
    ]


class Message:

    def __init__(
        self,
        message_type,
        **kwargs
    ):

        self.type = message_type

        for name, value in kwargs.items():

            setattr(
                self,
                name,
                value
            )


class PendingInput:

    def __init__(
        self,
        batches
    ):

        self.batches = iter(
            batches
        )

    def __enter__(self):

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback
    ):

        return False

    def iter_pending(self):

        try:

            return next(
                self.batches
            )

        except StopIteration:

            raise KeyboardInterrupt


def test_capture_program_success(
    monkeypatch,
    capsys
):

    class Project:

        def __init__(self):

            self.updated = None
            self.saved_errors = None

        def validate(self):

            return [
                "existing error"
            ]

        def get_blocking_errors(
            self,
            errors
        ):

            assert errors == [
                "existing error"
            ]

            return [
                "blocking error"
            ]

        def get_program_bank_name(
            self,
            bank
        ):

            return (
                f"Bank {bank}"
            )

        def snapshot(self):

            return {
                "before": True
            }

        def update_program_part(
            self,
            program_id,
            part_id,
            data
        ):

            self.updated = (
                program_id,
                part_id,
                data
            )

            return (
                True,
                []
            )

        def save_safe(
            self,
            allowed_errors=None
        ):

            self.saved_errors = (
                allowed_errors
            )

            return True

    project = Project()

    batches = [
        [
            Message(
                "control_change",
                channel=
                    fusion_capture.fusion_default_channel,
                control=0,
                value=8
            ),
            Message(
                "program_change",
                channel=
                    fusion_capture.fusion_default_channel,
                program=12
            ),
            Message(
                "note_on",
                channel=
                    fusion_capture.fusion_default_channel,
                note=60,
                velocity=80
            ),
            Message(
                "note_on",
                channel=
                    fusion_capture.fusion_default_channel,
                note=48,
                velocity=40
            ),
            Message(
                "note_on",
                channel=
                    fusion_capture.fusion_default_channel,
                note=72,
                velocity=110
            ),
        ],
        [],
    ]

    monkeypatch.setattr(
        fusion_capture.mido,
        "open_input",
        lambda port:
            PendingInput(
                batches
            )
    )

    times = iter([
        0,
        0,
        fusion_capture.CAPTURE_TIME + 1,
    ])

    monkeypatch.setattr(
        fusion_capture.time,
        "time",
        lambda:
            next(
                times,
                fusion_capture.CAPTURE_TIME + 1
            )
    )

    monkeypatch.setattr(
        fusion_capture.time,
        "sleep",
        lambda value:
            None
    )

    fusion_capture.capture_program(
        project,
        "Fusion MIDI"
    )

    program_id, part_id, data = (
        project.updated
    )

    assert program_id == "8:12"
    assert part_id == "1"

    assert data == {
        "midi_channel":
            fusion_capture.fusion_default_channel
            + 1,
        "bank":
            8,
        "program":
            12,
        "note_min":
            48,
        "note_max":
            72,
        "velocity_min":
            40,
        "velocity_max":
            110,
    }

    assert project.saved_errors == [
        "blocking error"
    ]

    output = (
        capsys.readouterr().out
    )

    assert (
        "Program Fusion détecté"
        in output
    )

    assert (
        "Program sauvegardé."
        in output
    )

    assert (
        "Plage détectée"
        in output
    )

    assert (
        "Velocity observée"
        in output
    )


def test_capture_program_update_failure(
    monkeypatch,
    capsys
):

    class Project:

        def __init__(self):

            self.restored = None

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def get_program_bank_name(
            self,
            bank
        ):

            return f"Bank {bank}"

        def snapshot(self):

            return {
                "original": True
            }

        def update_program_part(
            self,
            program_id,
            part_id,
            data
        ):

            return (
                False,
                [
                    "Erreur test"
                ]
            )

        def restore_snapshot(
            self,
            snapshot
        ):

            self.restored = snapshot

    project = Project()

    batches = [
        [
            Message(
                "program_change",
                channel=
                    fusion_capture.fusion_default_channel,
                program=12
            ),
            Message(
                "note_on",
                channel=
                    fusion_capture.fusion_default_channel,
                note=60,
                velocity=80
            ),
        ],
        [],
    ]

    monkeypatch.setattr(
        fusion_capture.mido,
        "open_input",
        lambda port:
            PendingInput(
                batches
            )
    )

    times = iter([
        0,
        0,
        fusion_capture.CAPTURE_TIME + 1,
    ])

    monkeypatch.setattr(
        fusion_capture.time,
        "time",
        lambda:
            next(
                times,
                fusion_capture.CAPTURE_TIME + 1
            )
    )

    monkeypatch.setattr(
        fusion_capture.time,
        "sleep",
        lambda value:
            None
    )

    fusion_capture.capture_program(
        project,
        "Fusion MIDI"
    )

    assert project.restored == {
        "original": True
    }

    output = capsys.readouterr().out

    assert "PROGRAM non modifié." in output
    assert "Erreur test" in output


def test_capture_program_save_failure(
    monkeypatch,
    capsys
):

    class Project:

        def __init__(self):

            self.restored = None

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def get_program_bank_name(
            self,
            bank
        ):

            return f"Bank {bank}"

        def snapshot(self):

            return {
                "original": True
            }

        def update_program_part(
            self,
            program_id,
            part_id,
            data
        ):

            return (
                True,
                []
            )

        def save_safe(
            self,
            allowed_errors=None
        ):

            return False

        def restore_snapshot(
            self,
            snapshot
        ):

            self.restored = snapshot

    project = Project()

    batches = [
        [
            Message(
                "program_change",
                channel=
                    fusion_capture.fusion_default_channel,
                program=12
            ),
            Message(
                "note_on",
                channel=
                    fusion_capture.fusion_default_channel,
                note=60,
                velocity=80
            ),
        ],
        [],
    ]

    monkeypatch.setattr(
        fusion_capture.mido,
        "open_input",
        lambda port:
            PendingInput(
                batches
            )
    )

    times = iter([
        0,
        0,
        fusion_capture.CAPTURE_TIME + 1,
    ])

    monkeypatch.setattr(
        fusion_capture.time,
        "time",
        lambda:
            next(
                times,
                fusion_capture.CAPTURE_TIME + 1
            )
    )

    monkeypatch.setattr(
        fusion_capture.time,
        "sleep",
        lambda value:
            None
    )

    fusion_capture.capture_program(
        project,
        "Fusion MIDI"
    )

    assert project.restored == {
        "original": True
    }

    output = capsys.readouterr().out

    assert "Sauvegarde non effectuée." in output
    assert (
        "État du projet restauré en mémoire."
        in output
    )


def test_capture_program_without_notes(
    monkeypatch,
    capsys
):

    class Project:

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def get_program_bank_name(
            self,
            bank
        ):

            return f"Bank {bank}"

    project = Project()

    batches = [
        [
            Message(
                "program_change",
                channel=
                    fusion_capture.fusion_default_channel,
                program=12
            ),
        ],
        [],
    ]

    monkeypatch.setattr(
        fusion_capture.mido,
        "open_input",
        lambda port:
            PendingInput(
                batches
            )
    )

    times = iter([
        0,
        0,
        fusion_capture.CAPTURE_TIME + 1,
    ])

    monkeypatch.setattr(
        fusion_capture.time,
        "time",
        lambda:
            next(
                times,
                fusion_capture.CAPTURE_TIME + 1
            )
    )

    monkeypatch.setattr(
        fusion_capture.time,
        "sleep",
        lambda value:
            None
    )

    fusion_capture.capture_program(
        project,
        "Fusion MIDI"
    )

    assert (
        "Aucune note détectée."
        in capsys.readouterr().out
    )


def test_capture_mix_success(
    monkeypatch,
    capsys
):

    class Project:

        def __init__(self):

            self.replaced = None
            self.saved_errors = None

        def get_mix_bank_name(
            self,
            bank
        ):

            return f"Bank {bank}"

        def mix_has_channels(
            self,
            mix_id
        ):

            return False

        def validate(self):

            return [
                "existing error"
            ]

        def get_blocking_errors(
            self,
            errors
        ):

            assert errors == [
                "existing error"
            ]

            return [
                "blocking error"
            ]

        def snapshot(self):

            return {
                "original": True
            }

        def replace_mix_channels(
            self,
            mix_id,
            channels
        ):

            self.replaced = (
                mix_id,
                channels
            )

            return (
                True,
                []
            )

        def save_safe(
            self,
            allowed_errors=None
        ):

            self.saved_errors = (
                allowed_errors
            )

            return True

    project = Project()

    batches = [
        [
            #
            # Note avant activation :
            # doit être ignorée
            #
            Message(
                "note_on",
                channel=5,
                note=40,
                velocity=100
            ),

            #
            # Détection du MIX
            #
            Message(
                "control_change",
                channel=
                    fusion_capture.fusion_default_channel,
                control=0,
                value=8
            ),
            Message(
                "program_change",
                channel=
                    fusion_capture.fusion_default_channel,
                program=12
            ),

            #
            # Note velocity 0 :
            # doit être ignorée
            #
            Message(
                "note_on",
                channel=4,
                note=50,
                velocity=0
            ),

            #
            # Deux PARTS réelles
            #
            Message(
                "note_on",
                channel=0,
                note=48,
                velocity=40
            ),
            Message(
                "note_on",
                channel=2,
                note=60,
                velocity=80
            ),

            #
            # Deuxième note sur CH 1 :
            # ne doit pas créer une nouvelle PART
            #
            Message(
                "note_on",
                channel=0,
                note=72,
                velocity=110
            ),
        ],
        [],
    ]

    monkeypatch.setattr(
        fusion_capture.mido,
        "open_input",
        lambda port:
            PendingInput(
                batches
            )
    )

    times = iter([
        0,
        0,
        fusion_capture.CAPTURE_TIME + 1,
    ])

    monkeypatch.setattr(
        fusion_capture.time,
        "time",
        lambda:
            next(
                times,
                fusion_capture.CAPTURE_TIME + 1
            )
    )

    monkeypatch.setattr(
        fusion_capture.time,
        "sleep",
        lambda value:
            None
    )

    fusion_capture.capture_mix(
        project,
        "Fusion MIDI"
    )

    assert project.replaced == (
        "8:12",
        {
            "1": {
                "note_min": 48,
                "note_max": 72,
                "velocity_min": 40,
                "velocity_max": 110
            },
            "3": {
                "note_min": 60,
                "note_max": 60,
                "velocity_min": 80,
                "velocity_max": 80
            },
        }
    )

    assert project.saved_errors == [
        "blocking error"
    ]

    output = (
        capsys.readouterr().out
    )

    assert "Nouveau Mix détecté" in output
    assert "PART 1" in output
    assert "PART 2" in output
    assert "PARTS détectées : 2" in output
    assert "Mix sauvegardé." in output


def run_capture_mix(
    monkeypatch,
    project,
    messages
):

    batches = [
        messages,
        [],
    ]

    monkeypatch.setattr(
        fusion_capture.mido,
        "open_input",
        lambda port:
            PendingInput(
                batches
            )
    )

    times = iter([
        0,
        0,
        fusion_capture.CAPTURE_TIME + 1,
    ])

    monkeypatch.setattr(
        fusion_capture.time,
        "time",
        lambda:
            next(
                times,
                fusion_capture.CAPTURE_TIME + 1
            )
    )

    monkeypatch.setattr(
        fusion_capture.time,
        "sleep",
        lambda value:
            None
    )

    fusion_capture.capture_mix(
        project,
        "Fusion MIDI"
    )


def mix_messages():

    return [
        Message(
            "program_change",
            channel=
                fusion_capture.fusion_default_channel,
            program=12
        ),
        Message(
            "note_on",
            channel=0,
            note=60,
            velocity=80
        ),
    ]


def test_capture_mix_existing_declined(
    monkeypatch,
    capsys
):

    class Project:

        def get_mix_bank_name(
            self,
            bank
        ):

            return f"Bank {bank}"

        def mix_has_channels(
            self,
            mix_id
        ):

            return True

    project = Project()

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            "n"
    )

    run_capture_mix(
        monkeypatch,
        project,
        mix_messages()
    )

    assert (
        "Mix déjà existant."
        in capsys.readouterr().out
    )


def test_capture_mix_replace_failure(
    monkeypatch,
    capsys
):

    class Project:

        def get_mix_bank_name(
            self,
            bank
        ):

            return f"Bank {bank}"

        def mix_has_channels(
            self,
            mix_id
        ):

            return False

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def snapshot(self):

            return {
                "original": True
            }

        def replace_mix_channels(
            self,
            mix_id,
            channels
        ):

            return (
                False,
                [
                    "Erreur Mix"
                ]
            )

    project = Project()

    run_capture_mix(
        monkeypatch,
        project,
        mix_messages()
    )

    output = capsys.readouterr().out

    assert (
        "Remplacement du Mix refusé :"
        in output
    )

    assert "Erreur Mix" in output


def test_capture_mix_save_failure(
    monkeypatch,
    capsys
):

    class Project:

        def __init__(self):

            self.restored = None

        def get_mix_bank_name(
            self,
            bank
        ):

            return f"Bank {bank}"

        def mix_has_channels(
            self,
            mix_id
        ):

            return False

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def snapshot(self):

            return {
                "original": True
            }

        def replace_mix_channels(
            self,
            mix_id,
            channels
        ):

            return (
                True,
                []
            )

        def save_safe(
            self,
            allowed_errors=None
        ):

            return False

        def restore_snapshot(
            self,
            snapshot
        ):

            self.restored = snapshot

    project = Project()

    run_capture_mix(
        monkeypatch,
        project,
        mix_messages()
    )

    assert project.restored == {
        "original": True
    }

    output = capsys.readouterr().out

    assert (
        "Le Mix n'a pas été sauvegardé."
        in output
    )

    assert (
        "État du projet restauré en mémoire."
        in output
    )


class SongInput:

    def __init__(
        self,
        messages
    ):

        self.messages = messages

    def __enter__(self):

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback
    ):

        return False

    def __iter__(self):

        yield from self.messages

        raise KeyboardInterrupt


def test_capture_song_success(
    monkeypatch,
    capsys
):

    class Project:

        def __init__(self):

            self.updated_programs = []
            self.replaced = None
            self.saved_errors = None

        def validate(self):

            return [
                "existing error"
            ]

        def get_blocking_errors(
            self,
            errors
        ):

            assert errors == [
                "existing error"
            ]

            return [
                "blocking error"
            ]

        def get_song(
            self,
            song_id
        ):

            return None

        def snapshot(self):

            return {
                "original": True
            }

        def ensure_song(
            self,
            song_id
        ):

            assert song_id == "song-test"

            return {
                "channels": {}
            }

        def get_program(
            self,
            program_id
        ):

            return None

        def update_program_part(
            self,
            program_id,
            part_id,
            data
        ):

            self.updated_programs.append(
                (
                    program_id,
                    part_id,
                    data
                )
            )

            return (
                True,
                []
            )

        def replace_song_channels(
            self,
            song_id,
            channels
        ):

            self.replaced = (
                song_id,
                channels
            )

            return (
                True,
                []
            )

        def save_safe(
            self,
            allowed_errors=None
        ):

            self.saved_errors = (
                allowed_errors
            )

            return True

    project = Project()

    messages = [
        #
        # Ignoré avant capture
        #
        Message(
            "control_change",
            channel=0,
            control=7,
            value=1
        ),

        #
        # Sélection SONG
        #
        Message(
            "song_select",
            song=5
        ),

        #
        # Début capture
        #
        Message(
            "start"
        ),

        #
        # Banque Fusion
        #
        Message(
            "control_change",
            channel=2,
            control=0,
            value=8
        ),

        #
        # LSB observé mais non utilisé
        # dans program_id
        #
        Message(
            "control_change",
            channel=2,
            control=32,
            value=4
        ),

        #
        # PROGRAM sur MIDI CH 3
        #
        Message(
            "program_change",
            channel=2,
            program=12
        ),

        #
        # Contrôleurs statiques
        #
        Message(
            "control_change",
            channel=2,
            control=7,
            value=100
        ),
        Message(
            "control_change",
            channel=2,
            control=10,
            value=64
        ),

        #
        # Fin capture
        #
        Message(
            "stop"
        ),
    ]

    monkeypatch.setattr(
        fusion_capture.mido,
        "open_input",
        lambda port:
            SongInput(
                messages
            )
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            "song-test"
    )

    fusion_capture.capture_song(
        project,
        "Fusion MIDI"
    )

    assert project.updated_programs == [
        (
            "8:12",
            "1",
            {
                "midi_channel":
                    fusion_capture.fusion_default_channel + 1,
                "bank": 8,
                "program": 12
            }
        )
    ]

    assert project.replaced == (
        "song-test",
        {
            "3": {
                "programs": {
                    "8:12": {}
                },
                "volume": 100,
                "pan": 64
            }
        }
    )

    assert project.saved_errors == [
        "blocking error"
    ]

    output = capsys.readouterr().out

    assert "SONG SELECT reçu : 5" in output
    assert "Capture SONG song-test" in output
    assert "PROGRAM inconnu : 8:12 - canal 3" in output
    assert "SONG sauvegardée : song-test" in output
    assert "Canaux détectés : 1" in output
    assert "Retour au menu Capture" in output


def test_capture_song_merge_existing(
    monkeypatch
):

    class Project:

        def __init__(self):

            self.replaced = None

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def get_song(
            self,
            song_id
        ):

            return {
                "channels": {
                    "1": {
                        "programs": {
                            "8:9":
                                "legacy-invalid",

                            #
                            # Instrument identique au global :
                            # doit disparaître.
                            #
                            "8:10": {
                                "fusion_name":
                                    "Old name",
                                "instrument":
                                    "piano",
                                "custom":
                                    123
                            },

                            #
                            # Véritable surcharge locale :
                            # doit rester.
                            #
                            "8:11": {
                                "instrument":
                                    "local-piano"
                            }
                        },
                        "volume": 90,
                        "pan": 40,
                        "chorus": 20
                    },

                    #
                    # Canal non observé :
                    # doit être conservé.
                    #
                    "4": {
                        "volume": 70
                    }
                }
            }

        def snapshot(self):

            return {
                "original": True
            }

        def ensure_song(
            self,
            song_id
        ):

            return self.get_song(
                song_id
            )

        def get_program(
            self,
            program_id
        ):

            if program_id in (
                "8:10",
                "8:11"
            ):

                return {
                    "parts": {
                        "1": {
                            "instrument":
                                "piano"
                        }
                    }
                }

            return None

        def update_program_part(
            self,
            program_id,
            part_id,
            data
        ):

            raise AssertionError(
                "Aucun PROGRAM inconnu attendu"
            )

        def replace_song_channels(
            self,
            song_id,
            channels
        ):

            self.replaced = (
                song_id,
                channels
            )

            return (
                True,
                []
            )

        def save_safe(
            self,
            allowed_errors=None
        ):

            return True

    project = Project()

    messages = [
        Message(
            "song_select",
            song=5
        ),
        Message(
            "start"
        ),

        #
        # PROGRAM déjà connu 8:10
        # sur le canal 1.
        #
        Message(
            "control_change",
            channel=0,
            control=0,
            value=8
        ),
        Message(
            "program_change",
            channel=0,
            program=10
        ),
        Message(
            "program_change",
            channel=0,
            program=11
        ),
        #
        # On observe seulement expression.
        # volume/pan/chorus devront être
        # récupérés de l'ancien canal.
        #
        Message(
            "control_change",
            channel=0,
            control=11,
            value=100
        ),

        Message(
            "stop"
        ),
    ]

    monkeypatch.setattr(
        fusion_capture.mido,
        "open_input",
        lambda port:
            SongInput(
                messages
            )
    )

    responses = iter([
        "song-test",
        "o",
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_capture.capture_song(
        project,
        "Fusion MIDI"
    )

    assert project.replaced == (
        "song-test",
        {
            "1": {
                "programs": {
                    "8:10": {},
                    "8:11": {
                        "instrument":
                            "local-piano"
                    }
                },
                "expression": 100,
                "volume": 90,
                "pan": 40,
                "chorus": 20
            },
            "4": {
                "volume": 70
            }
        }
    )


def test_capture_song_invalid_and_existing_id(
    monkeypatch,
    capsys
):

    class Project:

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def get_song(
            self,
            song_id
        ):

            if song_id == "existing":
                return {
                    "channels": {}
                }

            return None

    project = Project()

    messages = [
        Message(
            "song_select",
            song=5
        ),
    ]

    monkeypatch.setattr(
        fusion_capture.mido,
        "open_input",
        lambda port:
            SongInput(
                messages
            )
    )

    responses = iter([
        "",
        "existing",
        "n",
        "new-song",
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_capture.capture_song(
        project,
        "Fusion MIDI"
    )

    output = capsys.readouterr().out

    assert "Identifiant invalide." in output

    assert (
        "SONG déjà enregistrée : existing"
        in output
    )

    assert (
        "Choisis un autre identifiant."
        in output
    )


def test_capture_song_start_without_id(
    monkeypatch,
    capsys
):

    class Project:

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

    project = Project()

    monkeypatch.setattr(
        fusion_capture.mido,
        "open_input",
        lambda port:
            SongInput([
                Message(
                    "start"
                )
            ])
    )

    fusion_capture.capture_song(
        project,
        "Fusion MIDI"
    )

    output = capsys.readouterr().out

    assert (
        "START reçu sans identifiant de SONG."
        in output
    )


def test_capture_song_stop_without_channels(
    monkeypatch,
    capsys
):

    class Project:

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def get_song(
            self,
            song_id
        ):

            return None

    project = Project()

    messages = [
        Message(
            "song_select",
            song=5
        ),
        Message(
            "start"
        ),
        Message(
            "stop"
        ),
    ]

    monkeypatch.setattr(
        fusion_capture.mido,
        "open_input",
        lambda port:
            SongInput(
                messages
            )
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            "song-test"
    )

    fusion_capture.capture_song(
        project,
        "Fusion MIDI"
    )

    output = capsys.readouterr().out

    assert (
        "Aucun canal détecté : "
        "SONG non sauvegardée."
        in output
    )


def song_messages():

    return [
        Message(
            "song_select",
            song=5
        ),
        Message(
            "start"
        ),
        Message(
            "control_change",
            channel=0,
            control=0,
            value=8
        ),
        Message(
            "program_change",
            channel=0,
            program=12
        ),
        Message(
            "stop"
        ),
    ]


def test_capture_song_program_creation_failure(
    monkeypatch,
    capsys
):

    class Project:

        def __init__(self):

            self.restored = None

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def get_song(
            self,
            song_id
        ):

            return None

        def snapshot(self):

            return {
                "original": True
            }

        def ensure_song(
            self,
            song_id
        ):

            return {
                "channels": {}
            }

        def get_program(
            self,
            program_id
        ):

            return None

        def update_program_part(
            self,
            program_id,
            part_id,
            data
        ):

            return (
                False,
                [
                    "Erreur PROGRAM"
                ]
            )

        def restore_snapshot(
            self,
            snapshot
        ):

            self.restored = snapshot

    project = Project()

    monkeypatch.setattr(
        fusion_capture.mido,
        "open_input",
        lambda port:
            SongInput(
                song_messages()
            )
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            "song-test"
    )

    fusion_capture.capture_song(
        project,
        "Fusion MIDI"
    )

    assert project.restored == {
        "original": True
    }

    output = capsys.readouterr().out

    assert "PROGRAM non créé : 8:12" in output
    assert "Erreur PROGRAM" in output
    assert "SONG non sauvegardée." in output

    assert (
        "État du projet restauré en mémoire."
        in output
    )


def test_capture_song_replace_failure(
    monkeypatch,
    capsys
):

    class Project:

        def __init__(self):

            self.restored = None

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def get_song(
            self,
            song_id
        ):

            return None

        def snapshot(self):

            return {
                "original": True
            }

        def ensure_song(
            self,
            song_id
        ):

            return {
                "channels": {}
            }

        def get_program(
            self,
            program_id
        ):

            return {
                "parts": {}
            }

        def replace_song_channels(
            self,
            song_id,
            channels
        ):

            return (
                False,
                [
                    "Erreur SONG"
                ]
            )

        def restore_snapshot(
            self,
            snapshot
        ):

            self.restored = snapshot

    project = Project()

    monkeypatch.setattr(
        fusion_capture.mido,
        "open_input",
        lambda port:
            SongInput(
                song_messages()
            )
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            "song-test"
    )

    fusion_capture.capture_song(
        project,
        "Fusion MIDI"
    )

    assert project.restored == {
        "original": True
    }

    output = capsys.readouterr().out

    assert (
        "SONG non modifiée : song-test"
        in output
    )

    assert "Erreur SONG" in output


def test_capture_song_save_failure(
    monkeypatch,
    capsys
):

    class Project:

        def __init__(self):

            self.restored = None

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def get_song(
            self,
            song_id
        ):

            return None

        def snapshot(self):

            return {
                "original": True
            }

        def ensure_song(
            self,
            song_id
        ):

            return {
                "channels": {}
            }

        def get_program(
            self,
            program_id
        ):

            return {
                "parts": {}
            }

        def replace_song_channels(
            self,
            song_id,
            channels
        ):

            return (
                True,
                []
            )

        def save_safe(
            self,
            allowed_errors=None
        ):

            return False

        def restore_snapshot(
            self,
            snapshot
        ):

            self.restored = snapshot

    project = Project()

    monkeypatch.setattr(
        fusion_capture.mido,
        "open_input",
        lambda port:
            SongInput(
                song_messages()
            )
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            "song-test"
    )

    fusion_capture.capture_song(
        project,
        "Fusion MIDI"
    )

    assert project.restored == {
        "original": True
    }

    output = capsys.readouterr().out

    assert "Sauvegarde non effectuée." in output

    assert (
        "État du projet restauré en mémoire."
        in output
    )
