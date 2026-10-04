import fusion_editor


def test_get_test_note():

    assert fusion_editor.get_test_note({
        "note_min": 40,
        "note_max": 60
    }) == 50

    assert fusion_editor.get_test_note({
        "note_min": 40
    }) == 40

    assert fusion_editor.get_test_note({
        "note_max": 60
    }) == 60

    assert fusion_editor.get_test_note(
        {}
    ) == 60


def test_get_test_velocity():

    assert fusion_editor.get_test_velocity({
        "velocity_min": 40,
        "velocity_max": 100
    }) == 70

    assert fusion_editor.get_test_velocity(
        {}
    ) == 80


def test_get_sf2_suggestions_invalid():

    assert fusion_editor.get_sf2_suggestions(
        "",
        10
    ) == {}

    assert fusion_editor.get_sf2_suggestions(
        "Piano",
        None
    ) == {}


def test_get_sf2_suggestions_no_presets(
    monkeypatch
):

    monkeypatch.setattr(
        fusion_editor,
        "list_presets",
        lambda: []
    )

    assert fusion_editor.get_sf2_suggestions(
        "Piano",
        10
    ) == {}


def test_get_sf2_suggestions(
    monkeypatch
):

    presets = [
        {
            "id": "grand_piano",
            "name": "Grand Piano",
            "sf2_bank": 2,
            "sf2_program": 10
        }
    ]

    monkeypatch.setattr(
        fusion_editor,
        "list_presets",
        lambda: presets
    )

    received = {}

    def fake_suggest(
        fusion_program,
        sf2_presets
    ):

        received["fusion_program"] = (
            fusion_program
        )

        received["sf2_presets"] = (
            sf2_presets
        )

        return [
            "result"
        ]

    monkeypatch.setattr(
        fusion_editor,
        "suggest_instruments",
        fake_suggest
    )

    result = fusion_editor.get_sf2_suggestions(
        "Fusion Piano",
        10
    )

    assert result == [
        "result"
    ]

    assert received["fusion_program"] == {
        "name": "Fusion Piano",
        "program": 10
    }

    assert received["sf2_presets"] == [
        {
            "id": "grand_piano",
            "name": "Grand Piano",
            "bank": 2,
            "program": 10,
            "sf2_bank": 2,
            "sf2_program": 10
        }
    ]


def test_choose_sf2_preset_no_presets(
    monkeypatch,
    capsys
):

    monkeypatch.setattr(
        fusion_editor,
        "list_presets",
        lambda: []
    )

    assert (
        fusion_editor.choose_sf2_preset()
        is None
    )

    assert (
        "Aucun preset SoundFont disponible."
        in capsys.readouterr().out
    )


def test_choose_sf2_preset_cancel_search(
    monkeypatch
):

    monkeypatch.setattr(
        fusion_editor,
        "list_presets",
        lambda: [
            {
                "name": "Piano"
            }
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "q"
    )

    assert (
        fusion_editor.choose_sf2_preset()
        is None
    )


def test_choose_sf2_preset_search_and_select(
    monkeypatch,
    capsys
):

    presets = [
        {
            "id": "strings",
            "name": "Strings",
            "sf2_bank": 0,
            "sf2_program": 48
        },
        {
            "id": "piano",
            "name": "Acoustic Piano",
            "sf2_bank": 0,
            "sf2_program": 0
        }
    ]

    monkeypatch.setattr(
        fusion_editor,
        "list_presets",
        lambda: presets
    )

    responses = iter([
        "xyz",
        "piano",
        "bad",
        "piano",
        "1"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    result = (
        fusion_editor.choose_sf2_preset()
    )

    assert result["id"] == "piano"

    output = capsys.readouterr().out

    assert "Aucun preset trouvé." in output
    assert "Choix invalide." in output


def test_ensure_project_instrument_existing():

    class Project:

        def get_instrument(
            self,
            instrument_id
        ):

            return {
                "name": "Existing",
                "sf2_bank": 1,
                "sf2_program": 2
            }

    result = (
        fusion_editor.ensure_project_instrument(
            Project(),
            {
                "id": "piano"
            }
        )
    )

    assert result == {
        "id": "piano",
        "name": "Existing",
        "sf2_bank": 1,
        "sf2_program": 2
    }


def test_ensure_project_instrument_add_failure(
    monkeypatch,
    capsys
):

    class Project:

        def get_instrument(
            self,
            instrument_id
        ):

            return None

        def snapshot(self):

            return {
                "original": True
            }

        def add_instrument(
            self,
            instrument_id,
            instrument
        ):

            return (
                False,
                [
                    "Erreur instrument"
                ]
            )

    monkeypatch.setattr(
        fusion_editor,
        "print_error_messages",
        lambda errors:
            print(*errors)
    )

    result = (
        fusion_editor.ensure_project_instrument(
            Project(),
            {
                "id": "piano",
                "name": "Piano",
                "sf2_bank": 0,
                "sf2_program": 1
            }
        )
    )

    assert result is None

    output = capsys.readouterr().out

    assert "Instrument non ajouté." in output
    assert "Erreur instrument" in output


def test_ensure_project_instrument_save_failure():

    class Project:

        def __init__(self):

            self.restored = None

        def get_instrument(
            self,
            instrument_id
        ):

            return None

        def snapshot(self):

            return {
                "original": True
            }

        def add_instrument(
            self,
            instrument_id,
            instrument
        ):

            return (
                True,
                []
            )

        def save_safe(
            self,
            allowed_errors=None
        ):

            assert allowed_errors == [
                "existing-error"
            ]

            return False

        def restore_snapshot(
            self,
            snapshot
        ):

            self.restored = snapshot

    project = Project()

    result = (
        fusion_editor.ensure_project_instrument(
            project,
            {
                "id": "piano",
                "name": "Piano",
                "sf2_bank": 0,
                "sf2_program": 1
            },
            allowed_errors=[
                "existing-error"
            ]
        )
    )

    assert result is None

    assert project.restored == {
        "original": True
    }


def test_ensure_project_instrument_success():

    class Project:

        def __init__(self):

            self.added = None

        def get_instrument(
            self,
            instrument_id
        ):

            return None

        def snapshot(self):

            return {}

        def add_instrument(
            self,
            instrument_id,
            instrument
        ):

            self.added = (
                instrument_id,
                instrument
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

    result = (
        fusion_editor.ensure_project_instrument(
            project,
            {
                "id": "piano",
                "name": "Piano",
                "sf2_bank": 2,
                "sf2_program": 10
            }
        )
    )

    assert project.added == (
        "piano",
        {
            "name": "Piano",
            "sf2_bank": 2,
            "sf2_program": 10
        }
    )

    assert result == {
        "id": "piano",
        "name": "Piano",
        "sf2_bank": 2,
        "sf2_program": 10
    }


def test_choose_sf2_preset_cancel_choice(
    monkeypatch
):

    monkeypatch.setattr(
        fusion_editor,
        "list_presets",
        lambda: [
            {
                "id": "piano",
                "name": "Piano",
                "sf2_bank": 0,
                "sf2_program": 0
            }
        ]
    )

    responses = iter([
        "",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    assert (
        fusion_editor.choose_sf2_preset()
        is None
    )


def test_choose_instrument_from_list(
    monkeypatch,
    capsys
):

    class Project:

        def resolve_part_instrument(
            self,
            part
        ):

            return {
                "name": "Current"
            }

        def list_instruments(self):

            return [
                (
                    "strings",
                    {
                        "name": "Strings",
                        "sf2_bank": 0,
                        "sf2_program": 48
                    }
                ),
                (
                    "piano",
                    {
                        "name": "Acoustic Piano",
                        "sf2_bank": 0,
                        "sf2_program": 0
                    }
                )
            ]

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "1"
    )

    result = fusion_editor.choose_instrument(
        Project(),
        part={
            "instrument": "piano"
        }
    )

    #
    # Tri alphabétique :
    # Acoustic Piano est premier.
    #
    assert result == {
        "id": "piano",
        "name": "Acoustic Piano",
        "sf2_bank": 0,
        "sf2_program": 0
    }

    output = capsys.readouterr().out

    assert "Instrument actuel : Current" in output
    assert "*  1 - Acoustic Piano" in output


def test_choose_instrument_invalid(
    monkeypatch,
    capsys
):

    class Project:

        def resolve_part_instrument(
            self,
            part
        ):

            return None

        def list_instruments(self):

            return []

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "bad"
    )

    result = fusion_editor.choose_instrument(
        Project(),
        part={}
    )

    assert result is None

    output = capsys.readouterr().out

    assert "Instrument non-configuré" in output
    assert "Choix invalide" in output


def test_choose_instrument_cancel(
    monkeypatch
):

    class Project:

        def list_instruments(self):

            return []

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "q"
    )

    assert (
        fusion_editor.choose_instrument(
            Project()
        )
        is None
    )


def test_choose_instrument_add_from_list(
    monkeypatch
):

    class Project:

        def list_instruments(self):

            return []

    calls = []

    monkeypatch.setattr(
        fusion_editor,
        "add_instrument",
        lambda project:
            calls.append(project)
    )

    responses = iter([
        "a",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    project = Project()

    assert (
        fusion_editor.choose_instrument(
            project
        )
        is None
    )

    assert calls == [
        project
    ]


def test_choose_instrument_suggestion(
    monkeypatch,
    capsys
):

    class Project:

        def resolve_part_instrument(
            self,
            part
        ):

            return None

    preset = {
        "id": "grand_piano",
        "name": "Grand Piano",
        "sf2_bank": 2,
        "sf2_program": 10
    }

    received = {}

    def fake_suggestions(
        name,
        program
    ):

        received["name"] = name
        received["program"] = program

        return {
            "piano": [
                (
                    100,
                    preset
                )
            ]
        }

    monkeypatch.setattr(
        fusion_editor,
        "get_sf2_suggestions",
        fake_suggestions
    )

    def fake_ensure(
        project,
        selected,
        allowed_errors=None
    ):

        received["preset"] = selected
        received["allowed_errors"] = (
            allowed_errors
        )

        return {
            "selected": True
        }

    monkeypatch.setattr(
        fusion_editor,
        "ensure_project_instrument",
        fake_ensure
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "1"
    )

    result = fusion_editor.choose_instrument(
        Project(),
        part={
            "program": 10
        },
        fusion_name="Fusion Piano",
        allowed_errors=[
            "existing-error"
        ]
    )

    assert result == {
        "selected": True
    }

    assert received["name"] == (
        "Fusion Piano"
    )

    assert received["program"] == 10
    assert received["preset"] is preset

    assert received["allowed_errors"] == [
        "existing-error"
    ]

    output = capsys.readouterr().out

    assert (
        "Suggestions pour : Fusion Piano"
        in output
    )

    assert "PIANO" in output


def test_choose_instrument_suggestion_actions(
    monkeypatch,
    capsys
):

    class Project:

        def resolve_part_instrument(
            self,
            part
        ):

            return None

    preset = {
        "id": "piano",
        "name": "Piano",
        "sf2_bank": 0,
        "sf2_program": 0
    }

    monkeypatch.setattr(
        fusion_editor,
        "get_sf2_suggestions",
        lambda name, program: {
            "piano": [
                (
                    100,
                    preset
                )
            ]
        }
    )

    calls = []

    monkeypatch.setattr(
        fusion_editor,
        "add_instrument",
        lambda project:
            calls.append(project)
    )

    responses = iter([
        "bad",
        "a",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    project = Project()

    result = fusion_editor.choose_instrument(
        project,
        part={},
        fusion_name="Piano",
        fusion_program=0
    )

    assert result is None

    assert calls == [
        project
    ]

    assert (
        "Choix invalide."
        in capsys.readouterr().out
    )


def test_choose_instrument_show_all(
    monkeypatch
):

    class Project:

        def resolve_part_instrument(
            self,
            part
        ):

            return None

        def list_instruments(self):

            return [
                (
                    "piano",
                    {
                        "name": "Piano",
                        "sf2_bank": 0,
                        "sf2_program": 0
                    }
                )
            ]

    calls = []

    def fake_suggestions(
        name,
        program
    ):

        calls.append(
            (
                name,
                program
            )
        )

        return {
            "piano": [
                (
                    100,
                    {
                        "id": "suggested",
                        "name": "Suggested",
                        "sf2_bank": 0,
                        "sf2_program": 1
                    }
                )
            ]
        }

    monkeypatch.setattr(
        fusion_editor,
        "get_sf2_suggestions",
        fake_suggestions
    )

    responses = iter([
        "t",
        "1"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    result = fusion_editor.choose_instrument(
        Project(),
        part={},
        fusion_name="Fusion Piano",
        fusion_program=0
    )

    assert result["id"] == "piano"

    #
    # get_sf2_suggestions() est recalculé au
    # début de la deuxième boucle, même si
    # show_suggestions est False.
    #
    assert len(calls) == 2


def test_compare_instrument(
    monkeypatch
):

    part = {
        "midi_channel": 1
    }

    old = {
        "name": "Old"
    }

    new = {
        "name": "New"
    }

    played = []

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: ""
    )

    monkeypatch.setattr(
        fusion_editor,
        "play_preview",
        lambda part, instrument:
            played.append(
                instrument["name"]
            )
    )

    fusion_editor.compare_instrument(
        part,
        old,
        new
    )

    assert played == [
        "Old",
        "New"
    ]


def test_compare_instrument_unconfigured(
    monkeypatch,
    capsys
):

    played = []

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: ""
    )

    monkeypatch.setattr(
        fusion_editor,
        "play_preview",
        lambda part, instrument:
            played.append(
                instrument["name"]
            )
    )

    fusion_editor.compare_instrument(
        {},
        {
            "name": "Non configuré"
        },
        {
            "name": "New"
        }
    )

    assert played == [
        "New"
    ]

    assert (
        "Aucun instrument à écouter."
        in capsys.readouterr().out
    )


def test_play_preview_without_fluidsynth(
    monkeypatch,
    capsys
):

    monkeypatch.setattr(
        fusion_editor,
        "find_fluidsynth_output",
        lambda: None
    )

    fusion_editor.play_preview(
        {
            "midi_channel": 1
        },
        {}
    )

    assert (
        "FluidSynth introuvable"
        in capsys.readouterr().out
    )


def test_play_preview(
    monkeypatch
):

    class Output:

        def __init__(self):

            self.messages = []

        def __enter__(self):

            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback
        ):

            return False

        def send(
            self,
            message
        ):

            self.messages.append(
                message
            )

    output = Output()

    monkeypatch.setattr(
        fusion_editor,
        "find_fluidsynth_output",
        lambda: "FluidSynth"
    )

    monkeypatch.setattr(
        fusion_editor.mido,
        "open_output",
        lambda port:
            output
    )

    sleeps = []

    monkeypatch.setattr(
        fusion_editor.time,
        "sleep",
        lambda duration:
            sleeps.append(
                duration
            )
    )

    fusion_editor.play_preview(
        {
            "midi_channel": 3,
            "note_min": 48,
            "note_max": 72,
            "velocity_min": 60,
            "velocity_max": 100
        },
        {
            "sf2_bank": 130,
            "sf2_program": 25
        },
        duration=4
    )

    assert len(output.messages) == 11

    #
    # MIDI channel 3 utilisateur
    # -> channel 2 pour mido.
    #
    assert all(
        message.channel == 2
        for message in output.messages
    )

    bank_msb = output.messages[0]

    assert bank_msb.type == (
        "control_change"
    )

    assert bank_msb.control == 0
    assert bank_msb.value == 1

    bank_lsb = output.messages[1]

    assert bank_lsb.type == (
        "control_change"
    )

    assert bank_lsb.control == 32
    assert bank_lsb.value == 2

    program = output.messages[2]

    assert program.type == (
        "program_change"
    )

    assert program.program == 25

    #
    # Centre de 48..72 = 60.
    #
    expected_notes = [
        60,
        64,
        67,
        72
    ]

    note_messages = (
        output.messages[3:]
    )

    assert [
        message.note
        for message in note_messages
        if message.type == "note_on"
    ] == expected_notes

    assert [
        message.velocity
        for message in note_messages
        if message.type == "note_on"
    ] == [
        80,
        80,
        80,
        80
    ]

    assert [
        message.note
        for message in note_messages
        if message.type == "note_off"
    ] == expected_notes

    assert [
        message.velocity
        for message in note_messages
        if message.type == "note_off"
    ] == [
        0,
        0,
        0,
        0
    ]

    assert sleeps == [
        1,
        1,
        1,
        1
    ]


def test_play_part_preview_without_instrument(
    monkeypatch,
    capsys
):

    class Project:

        def resolve_part_instrument(
            self,
            part
        ):

            return None

    def fail_preview(
        part,
        instrument
    ):

        raise AssertionError(
            "play_preview ne doit pas "
            "être appelé"
        )

    monkeypatch.setattr(
        fusion_editor,
        "play_preview",
        fail_preview
    )

    fusion_editor.play_part_preview(
        Project(),
        {}
    )

    assert (
        "Instrument non configuré."
        in capsys.readouterr().out
    )


def test_play_part_preview(
    monkeypatch
):

    instrument = {
        "name": "Piano"
    }

    class Project:

        def resolve_part_instrument(
            self,
            part
        ):

            return instrument

    calls = []

    monkeypatch.setattr(
        fusion_editor,
        "play_preview",
        lambda part, selected:
            calls.append(
                (
                    part,
                    selected
                )
            )
    )

    part = {
        "midi_channel": 3
    }

    fusion_editor.play_part_preview(
        Project(),
        part
    )

    assert calls == [
        (
            part,
            instrument
        )
    ]


def test_edit_mix_unknown(
    capsys
):

    class Project:

        def get_mix(
            self,
            mix_id
        ):

            return None

    fusion_editor.edit_mix(
        Project(),
        "0:1"
    )

    assert (
        "Mix inconnu"
        in capsys.readouterr().out
    )


def test_edit_mix_channels_menu(
    monkeypatch
):

    mix = {
        "name": "Test Mix"
    }

    class Project:

        def get_mix(
            self,
            mix_id
        ):

            return mix

        def validate_mix(
            self,
            mix_id
        ):

            return [
                "validation-error"
            ]

    project = Project()

    printed = []
    edited = []

    monkeypatch.setattr(
        fusion_editor,
        "print_mix",
        lambda project, mix_id:
            None
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_validation_errors",
        lambda project, errors:
            printed.append(errors)
    )

    monkeypatch.setattr(
        fusion_editor,
        "edit_mix_channels",
        lambda project, mix_id, selected:
            edited.append(
                (
                    mix_id,
                    selected
                )
            )
    )

    responses = iter([
        "4",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.edit_mix(
        project,
        "0:1"
    )

    assert printed == [
        [
            "validation-error"
        ],
        [
            "validation-error"
        ]
    ]

    assert edited == [
        (
            "0:1",
            mix
        )
    ]


def test_edit_mix_rename_cancel(
    monkeypatch
):

    mix = {
        "name": "Original"
    }

    class Project:

        def get_mix(
            self,
            mix_id
        ):

            return mix

        def validate_mix(
            self,
            mix_id
        ):

            return []

    project = Project()

    monkeypatch.setattr(
        fusion_editor,
        "print_mix",
        lambda project, mix_id:
            None
    )

    responses = iter([
        "1",
        "",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.edit_mix(
        project,
        "0:1"
    )


def test_edit_mix_rename_success(
    monkeypatch,
    capsys
):

    mix = {
        "name": "Original"
    }

    class Project:

        def __init__(self):

            self.renamed = None
            self.saved_errors = None

        def get_mix(
            self,
            mix_id
        ):

            return mix

        def validate_mix(
            self,
            mix_id
        ):

            return []

        def validate(self):

            return [
                "existing-error"
            ]

        def get_blocking_errors(
            self,
            errors
        ):

            assert errors == [
                "existing-error"
            ]

            return [
                "blocking-error"
            ]

        def rename_mix(
            self,
            mix_id,
            name
        ):

            self.renamed = (
                mix_id,
                name
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

    monkeypatch.setattr(
        fusion_editor,
        "print_mix",
        lambda project, mix_id:
            None
    )

    responses = iter([
        "1",
        "Nouveau Mix",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.edit_mix(
        project,
        "0:1"
    )

    assert project.renamed == (
        "0:1",
        "Nouveau Mix"
    )

    assert project.saved_errors == [
        "blocking-error"
    ]

    assert (
        "Mix renommé."
        in capsys.readouterr().out
    )


def test_edit_mix_rename_failure(
    monkeypatch,
    capsys
):

    mix = {}

    class Project:

        def get_mix(self, mix_id):

            return mix

        def validate_mix(self, mix_id):

            return []

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def rename_mix(
            self,
            mix_id,
            name
        ):

            return (
                False,
                [
                    "Erreur rename"
                ]
            )

    monkeypatch.setattr(
        fusion_editor,
        "print_mix",
        lambda *args:
            None
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_error_messages",
        lambda errors:
            print(*errors)
    )

    responses = iter([
        "1",
        "New",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.edit_mix(
        Project(),
        "0:1"
    )

    output = capsys.readouterr().out

    assert "Modification refusée :" in output
    assert "Erreur rename" in output


def test_edit_mix_duplicate_paths(
    monkeypatch,
    capsys
):

    mix = {}

    class Project:

        def __init__(self):

            self.duplicates = []
            self.save_results = iter([
                True,
                False
            ])

        def get_mix(self, mix_id):

            return mix

        def validate_mix(self, mix_id):

            return []

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def duplicate_mix(
            self,
            mix_id,
            new_mix_id
        ):

            self.duplicates.append(
                (
                    mix_id,
                    new_mix_id
                )
            )

            if new_mix_id == "0:4":

                return (
                    False,
                    [
                        "Erreur duplicate"
                    ]
                )

            return (
                True,
                []
            )

        def save_safe(
            self,
            allowed_errors=None
        ):

            return next(
                self.save_results
            )

    project = Project()

    monkeypatch.setattr(
        fusion_editor,
        "print_mix",
        lambda *args:
            None
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_error_messages",
        lambda errors:
            print(*errors)
    )

    responses = iter([
        "2",
        "0:2",

        "2",
        "0:3",

        "2",
        "0:4",

        "2",
        "",

        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.edit_mix(
        project,
        "0:1"
    )

    assert project.duplicates == [
        (
            "0:1",
            "0:2"
        ),
        (
            "0:1",
            "0:3"
        ),
        (
            "0:1",
            "0:4"
        )
    ]

    output = capsys.readouterr().out

    assert "Mix dupliqué : 0:2" in output

    assert (
        "⚠ Sauvegarde non effectuée."
        in output
    )

    assert "Duplication refusée :" in output
    assert "Erreur duplicate" in output


def test_edit_mix_test_menu(
    monkeypatch
):

    mix = {}

    class Project:

        def get_mix(self, mix_id):

            return mix

        def validate_mix(self, mix_id):

            return []

    project = Project()

    calls = []

    monkeypatch.setattr(
        fusion_editor,
        "print_mix",
        lambda *args:
            None
    )

    monkeypatch.setattr(
        fusion_editor,
        "test_mix_channel",
        lambda project, selected:
            calls.append(
                (
                    "one",
                    selected
                )
            )
    )

    monkeypatch.setattr(
        fusion_editor,
        "test_mix_channels_all",
        lambda project, selected:
            calls.append(
                (
                    "all",
                    selected
                )
            )
    )

    responses = iter([
        "3",
        "1",
        "2",
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.edit_mix(
        project,
        "0:1"
    )

    assert calls == [
        (
            "one",
            mix
        ),
        (
            "all",
            mix
        )
    ]


def test_edit_mix_channels_empty(
    capsys
):

    fusion_editor.edit_mix_channels(
        object(),
        "0:1",
        {}
    )

    assert (
        "Aucun canal."
        in capsys.readouterr().out
    )


def test_edit_mix_channels_selection(
    monkeypatch,
    capsys
):

    channels = {
        "10": {
            "program": "0:10"
        },
        "2": {
            "program": "0:2"
        },
        "1": {}
    }

    mix = {
        "channels": channels
    }

    class Project:

        def get_program(
            self,
            program_id
        ):

            if program_id == "0:10":

                return {
                    "name": "Piano"
                }

            return None

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            if channel is channels["10"]:

                return {
                    "name": "Grand Piano"
                }

            return None

    project = Project()

    edited = []

    monkeypatch.setattr(
        fusion_editor,
        "edit_mix_channel",
        lambda project,
               mix_id,
               channel_id,
               channel:
            edited.append(
                (
                    mix_id,
                    channel_id,
                    channel
                )
            )
    )

    responses = iter([
        "99",
        "10",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.edit_mix_channels(
        project,
        "0:1",
        mix
    )

    assert edited == [
        (
            "0:1",
            "10",
            channels["10"]
        )
    ]

    output = capsys.readouterr().out

    assert "Canal inconnu." in output

    assert (
        "PROGRAM 0:10"
        in output
    )

    assert "Piano" in output
    assert "Grand Piano" in output
    assert "Non configuré" in output

    #
    # Vérifie le tri numérique
    # des canaux.
    #
    first = output.find("CH  1")
    second = output.find("CH  2")
    tenth = output.find("CH 10")

    assert (
        first
        <
        second
        <
        tenth
    )


def test_edit_mix_channel_display_and_quit(
    monkeypatch,
    capsys
):

    channel = {
        "program": "2:10",
        "instrument": "local"
    }

    class Project:

        def get_program(
            self,
            program_id
        ):

            assert program_id == "2:10"

            return {
                "name": "Fusion Piano"
            }

        def get_instrument(
            self,
            instrument_id
        ):

            assert instrument_id == "local"

            return {
                "name": "Local Piano"
            }

        def resolve_mix_channel_instrument(
            self,
            selected
        ):

            assert selected is channel

            return {
                "name": "Effective Piano"
            }

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "q"
    )

    fusion_editor.edit_mix_channel(
        Project(),
        "0:1",
        "3",
        channel
    )

    output = capsys.readouterr().out

    assert "PROGRAM Fusion : 2:10" in output
    assert "Nom Fusion     : Fusion Piano" in output
    assert "Instrument local : Local Piano" in output
    assert "Instrument effectif : Effective Piano" in output


def test_edit_mix_channel_program_cancel(
    monkeypatch,
    capsys
):

    channel = {}

    class Project:

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return None

    responses = iter([
        "1",
        "bad",
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.edit_mix_channel(
        Project(),
        "0:1",
        "1",
        channel
    )

    assert (
        "Choix invalide."
        in capsys.readouterr().out
    )


def test_edit_mix_channel_ranges_success(
    monkeypatch,
    capsys
):

    channel = {
        "note_min": 36,
        "note_max": 84,
        "velocity_min": 10,
        "velocity_max": 120
    }

    class Project:

        def __init__(self):

            self.update = None
            self.saved_errors = None

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return None

        def validate(self):

            return [
                "existing-error"
            ]

        def get_blocking_errors(
            self,
            errors
        ):

            assert errors == [
                "existing-error"
            ]

            return [
                "blocking-error"
            ]

        def snapshot(self):

            return {
                "original": True
            }

        def update_mix_channel(
            self,
            mix_id,
            channel_id,
            updates=None,
            remove_fields=None
        ):

            self.update = (
                mix_id,
                channel_id,
                updates,
                remove_fields
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

    responses = iter([
        "4",
        "48",
        "72",
        "20",
        "100",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.edit_mix_channel(
        project,
        "0:1",
        "3",
        channel
    )

    assert project.update == (
        "0:1",
        "3",
        {
            "note_min": 48,
            "note_max": 72,
            "velocity_min": 20,
            "velocity_max": 100
        },
        None
    )

    assert project.saved_errors == [
        "blocking-error"
    ]

    assert (
        "Plages modifiées."
        in capsys.readouterr().out
    )


def test_edit_mix_channel_ranges_no_change(
    monkeypatch,
    capsys
):

    channel = {
        "note_min": 36,
        "note_max": 84,
        "velocity_min": 10,
        "velocity_max": 120
    }

    class Project:

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return None

        def validate(self):

            raise AssertionError(
                "validate ne doit pas être appelé"
            )

        def update_mix_channel(
            self,
            *args,
            **kwargs
        ):

            raise AssertionError(
                "update_mix_channel ne doit pas être appelé"
            )

        def save_safe(
            self,
            **kwargs
        ):

            raise AssertionError(
                "save_safe ne doit pas être appelé"
            )

    responses = iter([
        "4",
        "",
        "",
        "",
        "",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.edit_mix_channel(
        Project(),
        "0:1",
        "3",
        channel
    )

    assert (
        "Aucune modification."
        in capsys.readouterr().out
    )


def test_edit_mix_channel_ranges_update_failure(
    monkeypatch,
    capsys
):

    channel = {}

    class Project:

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return None

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def snapshot(self):

            return {}

        def update_mix_channel(
            self,
            *args,
            **kwargs
        ):

            return (
                False,
                [
                    "Erreur plages"
                ]
            )

        def save_safe(
            self,
            **kwargs
        ):

            raise AssertionError(
                "save_safe ne doit pas être appelé"
            )

    monkeypatch.setattr(
        fusion_editor,
        "print_error_messages",
        lambda errors:
            print(*errors)
    )

    responses = iter([
        "4",
        "48",
        "72",
        "20",
        "100",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.edit_mix_channel(
        Project(),
        "0:1",
        "3",
        channel
    )

    output = capsys.readouterr().out

    assert (
        "Plages non modifiées."
        in output
    )

    assert "Erreur plages" in output


def test_edit_mix_channel_program_selection_cancel(
    monkeypatch
):

    channel = {}

    class Project:

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return None

    monkeypatch.setattr(
        fusion_editor,
        "choose_program_id",
        lambda project:
            None
    )

    responses = iter([
        "1",
        "1",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.edit_mix_channel(
        Project(),
        "0:1",
        "1",
        channel
    )


def test_edit_mix_channel_ranges_save_failure(
    monkeypatch,
    capsys
):

    channel = {}

    snapshot = {
        "original": True
    }

    class Project:

        def __init__(self):

            self.restored = None

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return None

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def snapshot(self):

            return snapshot

        def update_mix_channel(
            self,
            *args,
            **kwargs
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
            data
        ):

            self.restored = data

    project = Project()

    responses = iter([
        "4",
        "48",
        "72",
        "20",
        "100",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.edit_mix_channel(
        project,
        "0:1",
        "3",
        channel
    )

    assert project.restored is snapshot

    assert (
        "⚠ Sauvegarde non effectuée."
        in capsys.readouterr().out
    )


def test_edit_mix_channel_program_success(
    monkeypatch,
    capsys
):

    channel = {}

    class Project:

        def __init__(self):

            self.update = None
            self.saved_errors = None

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return None

        def validate(self):

            return [
                "existing-error"
            ]

        def get_blocking_errors(
            self,
            errors
        ):

            return [
                "blocking-error"
            ]

        def snapshot(self):

            return {
                "snapshot": True
            }

        def update_mix_channel(
            self,
            mix_id,
            channel_id,
            updates=None,
            remove_fields=None
        ):

            self.update = (
                mix_id,
                channel_id,
                updates,
                remove_fields
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

    monkeypatch.setattr(
        fusion_editor,
        "choose_program_id",
        lambda project:
            "3:42"
    )

    responses = iter([
        "1",
        "1",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.edit_mix_channel(
        project,
        "0:1",
        "5",
        channel
    )

    assert project.update == (
        "0:1",
        "5",
        {
            "program": "3:42"
        },
        None
    )

    assert project.saved_errors == [
        "blocking-error"
    ]

    assert (
        "PROGRAM modifié."
        in capsys.readouterr().out
    )


def test_edit_mix_channel_program_remove(
    monkeypatch
):

    channel = {
        "program": "3:42"
    }

    class Project:

        def __init__(self):

            self.update = None

        def get_program(
            self,
            program_id
        ):

            return None

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return None

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def snapshot(self):

            return {}

        def update_mix_channel(
            self,
            mix_id,
            channel_id,
            updates=None,
            remove_fields=None
        ):

            self.update = (
                updates,
                remove_fields
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

    responses = iter([
        "1",
        "2",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.edit_mix_channel(
        project,
        "0:1",
        "5",
        channel
    )

    assert project.update == (
        None,
        [
            "program"
        ]
    )


def test_edit_mix_channel_program_update_failure(
    monkeypatch,
    capsys
):

    channel = {}

    class Project:

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return None

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def snapshot(self):

            return {}

        def update_mix_channel(
            self,
            *args,
            **kwargs
        ):

            return (
                False,
                [
                    "Erreur PROGRAM"
                ]
            )

        def save_safe(
            self,
            **kwargs
        ):

            raise AssertionError(
                "save_safe ne doit pas "
                "être appelé"
            )

    monkeypatch.setattr(
        fusion_editor,
        "choose_program_id",
        lambda project:
            "0:10"
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_error_messages",
        lambda errors:
            print(*errors)
    )

    responses = iter([
        "1",
        "1",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.edit_mix_channel(
        Project(),
        "0:1",
        "1",
        channel
    )

    output = capsys.readouterr().out

    assert "PROGRAM non modifié." in output
    assert "Erreur PROGRAM" in output


def test_edit_mix_channel_program_save_failure(
    monkeypatch,
    capsys
):

    channel = {}

    snapshot = {
        "original": True
    }

    class Project:

        def __init__(self):

            self.restored = None

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return None

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def snapshot(self):

            return snapshot

        def update_mix_channel(
            self,
            *args,
            **kwargs
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
            data
        ):

            self.restored = data

    project = Project()

    monkeypatch.setattr(
        fusion_editor,
        "choose_program_id",
        lambda project:
            "0:10"
    )

    responses = iter([
        "1",
        "1",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.edit_mix_channel(
        project,
        "0:1",
        "1",
        channel
    )

    assert project.restored is snapshot

    assert (
        "⚠ Sauvegarde non effectuée."
        in capsys.readouterr().out
    )


def test_edit_mix_channel_instrument_cancel(
    monkeypatch
):

    channel = {
        "program": "2:42"
    }

    received = {}

    class Project:

        def get_program(
            self,
            program_id
        ):

            return {
                "name": "Fusion Piano"
            }

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return None

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return [
                "blocking-error"
            ]

    def fake_choose(
        project,
        part,
        fusion_name=None,
        fusion_program=None,
        allowed_errors=None
    ):

        received["name"] = fusion_name
        received["program"] = fusion_program
        received["errors"] = allowed_errors

        return None

    monkeypatch.setattr(
        fusion_editor,
        "choose_instrument",
        fake_choose
    )

    responses = iter([
        "2",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.edit_mix_channel(
        Project(),
        "0:1",
        "3",
        channel
    )

    assert received == {
        "name": "Fusion Piano",
        "program": 42,
        "errors": [
            "blocking-error"
        ]
    }


def test_edit_mix_channel_instrument_success(
    monkeypatch,
    capsys
):

    channel = {
        "program": "invalid"
    }

    class Project:

        def __init__(self):

            self.update = None

        def get_program(
            self,
            program_id
        ):

            return None

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return None

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

        def update_mix_channel(
            self,
            mix_id,
            channel_id,
            updates
        ):

            self.update = (
                mix_id,
                channel_id,
                updates
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

    received = {}

    def fake_choose(
        project,
        part,
        fusion_name=None,
        fusion_program=None,
        allowed_errors=None
    ):

        received["fusion_program"] = (
            fusion_program
        )

        return {
            "id": "piano"
        }

    monkeypatch.setattr(
        fusion_editor,
        "choose_instrument",
        fake_choose
    )

    responses = iter([
        "2",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.edit_mix_channel(
        project,
        "0:1",
        "3",
        channel
    )

    assert (
        received["fusion_program"]
        is None
    )

    assert project.update == (
        "0:1",
        "3",
        {
            "instrument": "piano"
        }
    )

    assert (
        "Instrument local affecté."
        in capsys.readouterr().out
    )


def test_edit_mix_channel_instrument_update_failure(
    monkeypatch,
    capsys
):

    channel = {}

    class Project:

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return None

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def snapshot(self):

            return {}

        def update_mix_channel(
            self,
            *args,
            **kwargs
        ):

            return (
                False,
                [
                    "Erreur instrument"
                ]
            )

    monkeypatch.setattr(
        fusion_editor,
        "choose_instrument",
        lambda *args, **kwargs: {
            "id": "piano"
        }
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_error_messages",
        lambda errors:
            print(*errors)
    )

    responses = iter([
        "2",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.edit_mix_channel(
        Project(),
        "0:1",
        "1",
        channel
    )

    output = capsys.readouterr().out

    assert (
        "Instrument local non affecté."
        in output
    )

    assert "Erreur instrument" in output


def test_edit_mix_channel_instrument_save_failure(
    monkeypatch,
    capsys
):

    channel = {}

    snapshot = {
        "original": True
    }

    class Project:

        def __init__(self):

            self.restored = None

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return None

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def snapshot(self):

            return snapshot

        def update_mix_channel(
            self,
            *args,
            **kwargs
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
            data
        ):

            self.restored = data

    project = Project()

    monkeypatch.setattr(
        fusion_editor,
        "choose_instrument",
        lambda *args, **kwargs: {
            "id": "piano"
        }
    )

    responses = iter([
        "2",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.edit_mix_channel(
        project,
        "0:1",
        "1",
        channel
    )

    assert project.restored is snapshot

    assert (
        "⚠ Sauvegarde non effectuée."
        in capsys.readouterr().out
    )


def test_remove_mix_channel_instrument_none(
    monkeypatch,
    capsys
):

    channel = {}

    class Project:

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return None

    responses = iter([
        "3",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.edit_mix_channel(
        Project(),
        "0:1",
        "1",
        channel
    )

    assert (
        "Aucun instrument local à supprimer."
        in capsys.readouterr().out
    )


def test_remove_mix_channel_instrument_success(
    monkeypatch,
    capsys
):

    channel = {
        "instrument": "local"
    }

    class Project:

        def get_instrument(
            self,
            instrument_id
        ):

            return {
                "name": "Local"
            }

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return {
                "name": "Inherited"
            }

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def snapshot(self):

            return {}

        def update_mix_channel(
            self,
            mix_id,
            channel_id,
            remove_fields=None
        ):

            assert remove_fields == [
                "instrument"
            ]

            return (
                True,
                []
            )

        def save_safe(
            self,
            allowed_errors=None
        ):

            return True

    responses = iter([
        "3",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.edit_mix_channel(
        Project(),
        "0:1",
        "1",
        channel
    )

    output = capsys.readouterr().out

    assert (
        "Instrument local supprimé."
        in output
    )

    assert (
        "Instrument effectif : Inherited"
        in output
    )


def test_remove_mix_channel_instrument_failure(
    monkeypatch,
    capsys
):

    channel = {
        "instrument": "local"
    }

    class Project:

        def get_instrument(
            self,
            instrument_id
        ):

            return None

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return None

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def snapshot(self):

            return {}

        def update_mix_channel(
            self,
            *args,
            **kwargs
        ):

            return (
                False,
                [
                    "Erreur suppression"
                ]
            )

    monkeypatch.setattr(
        fusion_editor,
        "print_error_messages",
        lambda errors:
            print(*errors)
    )

    responses = iter([
        "3",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.edit_mix_channel(
        Project(),
        "0:1",
        "1",
        channel
    )

    output = capsys.readouterr().out

    assert (
        "Instrument local non supprimé."
        in output
    )

    assert "Erreur suppression" in output


def test_remove_mix_channel_instrument_save_failure(
    monkeypatch,
    capsys
):

    channel = {
        "instrument": "local"
    }

    snapshot = {
        "original": True
    }

    class Project:

        def __init__(self):

            self.restored = None

        def get_instrument(
            self,
            instrument_id
        ):

            return None

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return None

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def snapshot(self):

            return snapshot

        def update_mix_channel(
            self,
            *args,
            **kwargs
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
            data
        ):

            self.restored = data

    project = Project()

    responses = iter([
        "3",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.edit_mix_channel(
        project,
        "0:1",
        "1",
        channel
    )

    assert project.restored is snapshot

    assert (
        "⚠ Sauvegarde non effectuée."
        in capsys.readouterr().out
    )


def test_read_int(
    monkeypatch,
    capsys
):

    responses = iter([
        "abc",
        "4",
        "11",
        "7"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    value = fusion_editor.read_int(
        "Valeur : ",
        minimum=5,
        maximum=10
    )

    assert value == 7

    output = capsys.readouterr().out

    assert (
        "Valeur numérique requise."
        in output
    )

    assert (
        "Valeur minimale : 5"
        in output
    )

    assert (
        "Valeur maximale : 10"
        in output
    )


def test_read_int_empty(
    monkeypatch
):

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: ""
    )

    assert (
        fusion_editor.read_int(
            "Valeur : "
        )
        is None
    )


def test_read_note(
    monkeypatch,
    capsys
):

    notes = {
        "bad": None,
        "low": 39,
        "high": 81,
        "good": 60
    }

    monkeypatch.setattr(
        fusion_editor,
        "note_number",
        lambda value:
            notes[value]
    )

    monkeypatch.setattr(
        fusion_editor,
        "note_name",
        lambda note:
            f"NOTE-{note}"
    )

    responses = iter([
        "bad",
        "low",
        "high",
        "good"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    value = fusion_editor.read_note(
        "Note : ",
        minimum=40,
        maximum=80
    )

    assert value == 60

    output = capsys.readouterr().out

    assert "Note invalide." in output
    assert "Note minimale : NOTE-40" in output
    assert "Note maximale : NOTE-80" in output


def test_read_note_empty(
    monkeypatch
):

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "   "
    )

    assert (
        fusion_editor.read_note(
            "Note : "
        )
        is None
    )


def test_choose_fusion_program_bank(
    monkeypatch,
    capsys
):

    class Project:

        def get_program_banks(self):

            return [
                0,
                8
            ]

        def get_program_bank_name(
            self,
            bank
        ):

            return {
                0: "ROM",
                8: "HD User"
            }[bank]

    responses = iter([
        "abc",
        "128",
        "8"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    result = (
        fusion_editor
        .choose_fusion_program_bank(
            Project(),
            current_bank=0
        )
    )

    assert result == 8

    output = capsys.readouterr().out

    assert (
        "Banque Fusion actuelle : ROM (0)"
        in output
    )

    assert " 0 - ROM" in output
    assert " 8 - HD User" in output
    assert "Choix invalide." in output

    assert (
        "Banque Fusion invalide."
        in output
    )


def test_choose_fusion_program_bank_keep(
    monkeypatch,
    capsys
):

    class Project:

        def get_program_banks(self):

            return []

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: ""
    )

    result = (
        fusion_editor
        .choose_fusion_program_bank(
            Project()
        )
    )

    assert result is None

    assert (
        "Banque Fusion actuelle : ?"
        in capsys.readouterr().out
    )


def test_choose_mix_id_empty(
    capsys
):

    class Project:

        def iter_mixes(self):

            return iter([])

    result = fusion_editor.choose_mix_id(
        Project()
    )

    assert result is None

    assert (
        "Aucun MIX disponible."
        in capsys.readouterr().out
    )


def test_choose_mix_id_direct(
    monkeypatch,
    capsys
):

    class Project:

        def iter_mixes(self):

            return iter([
                (
                    "0:1",
                    {}
                ),
                (
                    "2:10",
                    {}
                )
            ])

    responses = iter([
        "9:9",
        "2:10"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    result = fusion_editor.choose_mix_id(
        Project()
    )

    assert result == "2:10"

    assert (
        "MIX inconnu ou non disponible : 9:9"
        in capsys.readouterr().out
    )


def test_choose_mix_id_cancel_allowed(
    monkeypatch
):

    class Project:

        def iter_mixes(self):

            raise AssertionError(
                "iter_mixes ne doit pas "
                "être appelé"
            )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: ""
    )

    result = fusion_editor.choose_mix_id(
        Project(),
        allowed_ids=[
            "0:1",
            "2:10"
        ]
    )

    assert result is None


def test_choose_mix_id_assisted(
    monkeypatch,
    capsys
):

    class Project:

        def get_mix_bank_name(
            self,
            bank
        ):

            return {
                0: "ROM",
                2: "USER"
            }[bank]

        def get_mix(
            self,
            mix_id
        ):

            if mix_id == "2:10":

                return {
                    "name": "My Mix"
                }

            return None

    responses = iter([
        "?",
        "abc",
        "9",
        "2",
        "abc",
        "99",
        "10"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    result = fusion_editor.choose_mix_id(
        Project(),
        allowed_ids=[
            "0:1",
            "2:20",
            "2:10"
        ]
    )

    assert result == "2:10"

    output = capsys.readouterr().out

    assert "Banques MIX disponibles" in output
    assert "  0 - ROM" in output
    assert "  2 - USER" in output

    assert "Choix invalide." in output

    assert (
        "Banque MIX non disponible."
        in output
    )

    assert " 10 - My Mix" in output
    assert " 20 - 2:20" in output

    assert (
        "MIX inconnu ou non disponible : 2:99"
        in output
    )


def test_choose_mix_id_assisted_back(
    monkeypatch
):

    class Project:

        def get_mix_bank_name(
            self,
            bank
        ):

            return "ROM"

        def get_mix(
            self,
            mix_id
        ):

            return {
                "name": "Mix"
            }

    responses = iter([
        "?",
        "0",
        "",
        "",
        ""
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    result = fusion_editor.choose_mix_id(
        Project(),
        allowed_ids=[
            "0:1"
        ]
    )

    assert result is None


def test_choose_program_id_empty(
    capsys
):

    class Project:

        def iter_programs(self):

            return iter([])

    result = (
        fusion_editor.choose_program_id(
            Project()
        )
    )

    assert result is None

    assert (
        "Aucun PROGRAM disponible."
        in capsys.readouterr().out
    )


def test_choose_program_id_direct(
    monkeypatch,
    capsys
):

    class Project:

        def iter_programs(self):

            return iter([
                (
                    "0:1",
                    {}
                ),
                (
                    "2:10",
                    {}
                )
            ])

    responses = iter([
        "9:9",
        "2:10"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    result = (
        fusion_editor.choose_program_id(
            Project()
        )
    )

    assert result == "2:10"

    assert (
        "PROGRAM inconnu ou non disponible : 9:9"
        in capsys.readouterr().out
    )


def test_choose_program_id_cancel_allowed(
    monkeypatch
):

    class Project:

        def iter_programs(self):

            raise AssertionError(
                "iter_programs ne doit pas "
                "être appelé"
            )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: ""
    )

    result = (
        fusion_editor.choose_program_id(
            Project(),
            allowed_ids=[
                "0:1",
                42
            ]
        )
    )

    assert result is None


def test_choose_program_id_assisted(
    monkeypatch,
    capsys
):

    class Project:

        def get_program_bank_name(
            self,
            bank
        ):

            return {
                0: "ROM",
                2: "USER"
            }[bank]

        def get_program(
            self,
            program_id
        ):

            if program_id == "2:10":

                return {
                    "name": "Piano"
                }

            return None

    values = iter([
        9,
        2,
        99,
        10
    ])

    monkeypatch.setattr(
        fusion_editor,
        "read_int",
        lambda prompt,
               minimum,
               maximum:
            next(values)
    )

    responses = iter([
        "?",
        "?"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    result = (
        fusion_editor.choose_program_id(
            Project(),
            allowed_ids=[
                "invalid",
                "0:1",
                "2:20",
                "2:10"
            ]
        )
    )

    assert result == "2:10"

    output = capsys.readouterr().out

    assert (
        "Banques PROGRAM disponibles"
        in output
    )

    assert "  0 - ROM" in output
    assert "  2 - USER" in output

    assert (
        "Aucun PROGRAM disponible dans cette banque."
        in output
    )

    assert " 10 - Piano" in output
    assert " 20 - ?" in output

    assert (
        "PROGRAM inconnu ou non disponible : 2:99"
        in output
    )


def test_choose_program_id_assisted_back(
    monkeypatch
):

    class Project:

        def get_program_bank_name(
            self,
            bank
        ):

            return "ROM"

        def get_program(
            self,
            program_id
        ):

            return {
                "name": "Piano"
            }

    values = iter([
        None,
        0,
        None
    ])

    monkeypatch.setattr(
        fusion_editor,
        "read_int",
        lambda prompt,
               minimum,
               maximum:
            next(values)
    )

    responses = iter([
        "?",
        "?",
        ""
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    result = (
        fusion_editor.choose_program_id(
            Project(),
            allowed_ids=[
                "0:1"
            ]
        )
    )

    assert result is None


def test_choose_program_id_assisted_no_valid_ids(
    monkeypatch,
    capsys
):

    responses = iter([
        "?",
        ""
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    result = (
        fusion_editor.choose_program_id(
            object(),
            allowed_ids=[
                "invalid"
            ]
        )
    )

    assert result is None

    assert (
        "Aucun PROGRAM disponible."
        in capsys.readouterr().out
    )


def test_choose_song_id_empty(
    capsys
):

    class Project:

        def iter_songs(self):

            return iter([])

    result = (
        fusion_editor.choose_song_id(
            Project()
        )
    )

    assert result is None

    assert (
        "Aucune SONG disponible."
        in capsys.readouterr().out
    )


def test_choose_song_id_direct(
    monkeypatch,
    capsys
):

    class Project:

        def iter_songs(self):

            return iter([
                (
                    "Song A",
                    {}
                ),
                (
                    "Song B",
                    {}
                )
            ])

    responses = iter([
        "Unknown",
        "Song B"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    result = (
        fusion_editor.choose_song_id(
            Project()
        )
    )

    assert result == "Song B"

    assert (
        "SONG inconnue ou non disponible : Unknown"
        in capsys.readouterr().out
    )


def test_choose_song_id_cancel_allowed(
    monkeypatch
):

    class Project:

        def iter_songs(self):

            raise AssertionError(
                "iter_songs ne doit pas "
                "être appelé"
            )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: ""
    )

    result = (
        fusion_editor.choose_song_id(
            Project(),
            allowed_ids=[
                "Song A",
                "Song B"
            ]
        )
    )

    assert result is None


def test_choose_song_id_assisted(
    monkeypatch,
    capsys
):

    class Project:

        def get_song(
            self,
            song_id
        ):

            if song_id == "alpha":

                return {
                    "name": "My Alpha"
                }

            if song_id == "Beta":

                return {}

            return None

    responses = iter([
        "?",
        "abc",
        "99",
        "1"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    result = (
        fusion_editor.choose_song_id(
            Project(),
            allowed_ids=[
                "zulu",
                "Beta",
                "alpha"
            ]
        )
    )

    assert result == "alpha"

    output = capsys.readouterr().out

    assert "SONGs disponibles" in output

    assert (
        " 1 - alpha - My Alpha"
        in output
    )

    assert " 2 - Beta" in output
    assert " 3 - zulu" in output

    assert output.count(
        "Choix invalide."
    ) >= 2


def test_choose_song_id_assisted_back(
    monkeypatch
):

    class Project:

        def get_song(
            self,
            song_id
        ):

            return {
                "name": "My Song"
            }

    responses = iter([
        "?",
        "",
        ""
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    result = (
        fusion_editor.choose_song_id(
            Project(),
            allowed_ids=[
                "Song A"
            ]
        )
    )

    assert result is None


def test_edit_part_values_no_change(
    monkeypatch,
    capsys
):

    class Project:

        def get_program_bank_name(
            self,
            bank
        ):

            raise AssertionError(
                "Aucune banque ne devrait "
                "être résolue"
            )

    part = {
        "midi_channel": 1,
        "program": 10
    }

    monkeypatch.setattr(
        fusion_editor,
        "read_int",
        lambda *args, **kwargs:
            None
    )

    monkeypatch.setattr(
        fusion_editor,
        "read_note",
        lambda *args, **kwargs:
            None
    )

    monkeypatch.setattr(
        fusion_editor,
        "choose_fusion_program_bank",
        lambda project, bank:
            None
    )

    result = (
        fusion_editor.edit_part_values(
            Project(),
            part,
            1
        )
    )

    assert result is None

    output = capsys.readouterr().out

    assert "Fusion Bank : ?" in output

    assert (
        "non spécifiée (défaut C-1)"
        in output
    )

    assert (
        "non spécifiée (défaut G9)"
        in output
    )

    assert "Aucune modification." in output


def test_edit_part_values_all_changes(
    monkeypatch,
    capsys
):

    class Project:

        def get_program_bank_name(
            self,
            bank
        ):

            assert bank == 2

            return "USER"

    part = {
        "midi_channel": 1,
        "bank": 2,
        "program": 10,
        "note_min": 20,
        "note_max": 100,
        "velocity_min": 10,
        "velocity_max": 120
    }

    int_values = iter([
        3,
        42,
        15,
        110
    ])

    monkeypatch.setattr(
        fusion_editor,
        "read_int",
        lambda *args, **kwargs:
            next(int_values)
    )

    monkeypatch.setattr(
        fusion_editor,
        "choose_fusion_program_bank",
        lambda project, bank:
            8
    )

    note_values = iter([
        30,
        90
    ])

    note_calls = []

    def fake_read_note(
        *args,
        **kwargs
    ):

        note_calls.append(
            (
                args,
                kwargs
            )
        )

        return next(note_values)

    monkeypatch.setattr(
        fusion_editor,
        "read_note",
        fake_read_note
    )

    result = (
        fusion_editor.edit_part_values(
            Project(),
            part,
            2
        )
    )

    assert result == {
        "midi_channel": 3,
        "bank": 8,
        "program": 42,
        "note_min": 30,
        "note_max": 90,
        "velocity_min": 15,
        "velocity_max": 110
    }

    assert note_calls[1][1] == {
        "minimum": 30
    }

    output = capsys.readouterr().out

    assert "USER (2)" in output


def test_send_midi_message_success():

    class Output:

        def __init__(self):

            self.messages = []

        def send(
            self,
            message
        ):

            self.messages.append(
                message
            )

    out = Output()

    message = object()

    result = (
        fusion_editor.send_midi_message(
            out,
            message
        )
    )

    assert result is True

    assert out.messages == [
        message
    ]


def test_send_midi_message_error(
    capsys
):

    class Output:

        def send(
            self,
            message
        ):

            raise RuntimeError(
                "MIDI failure"
            )

    result = (
        fusion_editor.send_midi_message(
            Output(),
            object()
        )
    )

    assert result is False

    output = capsys.readouterr().out

    assert (
        "Erreur MIDI : MIDI failure"
        in output
    )


def test_stop_midi_test(
    monkeypatch
):

    messages = []

    monkeypatch.setattr(
        fusion_editor,
        "send_midi_message",
        lambda out, message:
            messages.append(message)
            or True
    )

    out = object()

    channels = [
        0,
        2
    ]

    active_notes = {
        (0, 60),
        (2, 64)
    }

    fusion_editor.stop_midi_test(
        out,
        channels,
        active_notes
    )

    assert active_notes == set()

    note_offs = [
        message
        for message in messages
        if message.type == "note_off"
    ]

    assert {
        (
            message.channel,
            message.note,
            message.velocity
        )
        for message in note_offs
    } == {
        (0, 60, 0),
        (2, 64, 0)
    }

    controls = [
        message
        for message in messages
        if message.type == "control_change"
    ]

    assert [
        (
            message.channel,
            message.control,
            message.value
        )
        for message in controls
    ] == [
        (0, 64, 0),
        (0, 123, 0),
        (0, 120, 0),
        (2, 64, 0),
        (2, 123, 0),
        (2, 120, 0)
    ]


def test_test_mix_channel_no_channels(
    capsys
):

    fusion_editor.test_mix_channel(
        object(),
        {}
    )

    assert (
        "Aucun canal."
        in capsys.readouterr().out
    )


def test_test_mix_channel_unknown_channel(
    monkeypatch,
    capsys
):

    class Project:

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return {
                "name": "Piano"
            }

    mix = {
        "channels": {
            "1": {}
        }
    }

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "9"
    )

    fusion_editor.test_mix_channel(
        Project(),
        mix
    )

    assert (
        "Canal inconnu."
        in capsys.readouterr().out
    )


def test_test_mix_channel_unconfigured(
    monkeypatch,
    capsys
):

    class Project:

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return None

    mix = {
        "channels": {
            "1": {}
        }
    }

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "1"
    )

    fusion_editor.test_mix_channel(
        Project(),
        mix
    )

    output = capsys.readouterr().out

    assert "Non configuré" in output
    assert "Canal non configuré." in output


def test_test_mix_channel_no_fluidsynth(
    monkeypatch,
    capsys
):

    class Project:

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return {
                "name": "Piano",
                "sf2_bank": 0,
                "sf2_program": 1
            }

    mix = {
        "channels": {
            "1": {}
        }
    }

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "1"
    )

    monkeypatch.setattr(
        fusion_editor,
        "find_fluidsynth_output",
        lambda: None
    )

    fusion_editor.test_mix_channel(
        Project(),
        mix
    )

    assert (
        "FluidSynth introuvable"
        in capsys.readouterr().out
    )


def test_test_mix_channel_invalid_bank(
    monkeypatch,
    capsys
):

    class Project:

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return {
                "name": "Piano",
                "sf2_bank": 16384,
                "sf2_program": 1
            }

    mix = {
        "channels": {
            "1": {}
        }
    }

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "1"
    )

    monkeypatch.setattr(
        fusion_editor,
        "find_fluidsynth_output",
        lambda: "FluidSynth"
    )

    fusion_editor.test_mix_channel(
        Project(),
        mix
    )

    assert (
        "Bank SF2 invalide : 16384"
        in capsys.readouterr().out
    )


def test_test_mix_channel_invalid_program(
    monkeypatch,
    capsys
):

    class Project:

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return {
                "name": "Piano",
                "sf2_bank": 0,
                "sf2_program": 128
            }

    mix = {
        "channels": {
            "1": {}
        }
    }

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "1"
    )

    monkeypatch.setattr(
        fusion_editor,
        "find_fluidsynth_output",
        lambda: "FluidSynth"
    )

    fusion_editor.test_mix_channel(
        Project(),
        mix
    )

    assert (
        "Program SF2 invalide : 128"
        in capsys.readouterr().out
    )


def test_test_mix_channel_success(
    monkeypatch
):

    class Project:

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return {
                "name": "Piano",
                "sf2_bank": 257,
                "sf2_program": 10
            }

    class Output:

        def __enter__(self):

            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback
        ):

            return False

    mix = {
        "channels": {
            "2": {}
        }
    }

    responses = iter([
        "2",
        ""
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    monkeypatch.setattr(
        fusion_editor,
        "find_fluidsynth_output",
        lambda: "FluidSynth"
    )

    monkeypatch.setattr(
        fusion_editor.mido,
        "open_output",
        lambda port_name:
            Output()
    )

    messages = []

    monkeypatch.setattr(
        fusion_editor,
        "send_midi_message",
        lambda out, message:
            messages.append(message)
            or True
    )

    monkeypatch.setattr(
        fusion_editor.time,
        "sleep",
        lambda seconds: None
    )

    stopped = []

    monkeypatch.setattr(
        fusion_editor,
        "stop_midi_test",
        lambda out,
               channels,
               active_notes:
            stopped.append(
                (
                    set(channels),
                    set(active_notes)
                )
            )
    )

    fusion_editor.test_mix_channel(
        Project(),
        mix
    )

    assert (
        messages[0].type
        == "control_change"
    )
    assert messages[0].channel == 1
    assert messages[0].control == 0
    assert messages[0].value == 2

    assert (
        messages[1].type
        == "control_change"
    )
    assert messages[1].control == 32
    assert messages[1].value == 1

    assert (
        messages[2].type
        == "program_change"
    )
    assert messages[2].channel == 1
    assert messages[2].program == 10

    note_ons = [
        message
        for message in messages
        if message.type == "note_on"
    ]

    assert [
        message.note
        for message in note_ons
    ] == [
        60,
        64,
        67,
        72
    ]

    assert stopped == [
        (
            {1},
            set()
        )
    ]


import pytest


@pytest.mark.parametrize(
    "failure_call",
    [
        1,
        2,
        3,
        4,
        5
    ]
)
def test_test_mix_channel_midi_failure(
    monkeypatch,
    failure_call
):

    class Project:

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return {
                "name": "Piano",
                "sf2_bank": 0,
                "sf2_program": 10
            }

    class Output:

        def __enter__(self):

            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback
        ):

            return False

    mix = {
        "channels": {
            "1": {}
        }
    }

    responses = iter([
        "1",
        ""
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    monkeypatch.setattr(
        fusion_editor,
        "find_fluidsynth_output",
        lambda: "FluidSynth"
    )

    monkeypatch.setattr(
        fusion_editor.mido,
        "open_output",
        lambda port_name:
            Output()
    )

    calls = 0

    def fake_send(
        out,
        message
    ):

        nonlocal calls

        calls += 1

        return calls != failure_call

    monkeypatch.setattr(
        fusion_editor,
        "send_midi_message",
        fake_send
    )

    monkeypatch.setattr(
        fusion_editor.time,
        "sleep",
        lambda seconds: None
    )

    stopped = []

    monkeypatch.setattr(
        fusion_editor,
        "stop_midi_test",
        lambda out,
               channels,
               active_notes:
            stopped.append(
                (
                    set(channels),
                    set(active_notes)
                )
            )
    )

    fusion_editor.test_mix_channel(
        Project(),
        mix
    )

    assert len(stopped) == 1


def test_test_mix_channel_keyboard_interrupt(
    monkeypatch,
    capsys
):

    class Project:

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return {
                "name": "Piano",
                "sf2_bank": 0,
                "sf2_program": 10
            }

    class Output:

        def __enter__(self):

            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback
        ):

            return False

    mix = {
        "channels": {
            "1": {}
        }
    }

    responses = iter([
        "1",
        ""
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    monkeypatch.setattr(
        fusion_editor,
        "find_fluidsynth_output",
        lambda: "FluidSynth"
    )

    monkeypatch.setattr(
        fusion_editor.mido,
        "open_output",
        lambda port_name:
            Output()
    )

    monkeypatch.setattr(
        fusion_editor,
        "send_midi_message",
        lambda out, message:
            True
    )

    monkeypatch.setattr(
        fusion_editor.time,
        "sleep",
        lambda seconds:
            (_ for _ in ()).throw(
                KeyboardInterrupt()
            )
    )

    monkeypatch.setattr(
        fusion_editor,
        "stop_midi_test",
        lambda *args:
            None
    )

    fusion_editor.test_mix_channel(
        Project(),
        mix
    )

    assert (
        "Test interrompu."
        in capsys.readouterr().out
    )


def test_test_mix_channel_open_output_error(
    monkeypatch,
    capsys
):

    class Project:

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return {
                "name": "Piano",
                "sf2_bank": 0,
                "sf2_program": 10
            }

    mix = {
        "channels": {
            "1": {}
        }
    }

    responses = iter([
        "1",
        ""
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    monkeypatch.setattr(
        fusion_editor,
        "find_fluidsynth_output",
        lambda: "FluidSynth"
    )

    def fail_open(
        port_name
    ):

        raise RuntimeError(
            "port failure"
        )

    monkeypatch.setattr(
        fusion_editor.mido,
        "open_output",
        fail_open
    )

    fusion_editor.test_mix_channel(
        Project(),
        mix
    )

    assert (
        "Erreur lors de l'accès au port MIDI : port failure"
        in capsys.readouterr().out
    )


def test_test_mix_channels_all_no_fluidsynth(
    monkeypatch,
    capsys
):

    monkeypatch.setattr(
        fusion_editor,
        "find_fluidsynth_output",
        lambda: None
    )

    fusion_editor.test_mix_channels_all(
        object(),
        {}
    )

    assert (
        "FluidSynth introuvable"
        in capsys.readouterr().out
    )


def test_test_mix_channels_all_no_channels(
    monkeypatch,
    capsys
):

    monkeypatch.setattr(
        fusion_editor,
        "find_fluidsynth_output",
        lambda: "FluidSynth"
    )

    fusion_editor.test_mix_channels_all(
        object(),
        {}
    )

    assert (
        "Aucun canal."
        in capsys.readouterr().out
    )


def test_test_mix_channels_all_success(
    monkeypatch,
    capsys
):

    instruments = {
        "unconfigured": None,
        "bad_bank": {
            "name": "Bad Bank",
            "sf2_bank": 16384,
            "sf2_program": 1
        },
        "bad_program": {
            "name": "Bad Program",
            "sf2_bank": 0,
            "sf2_program": 128
        },
        "piano": {
            "name": "Piano",
            "sf2_bank": 257,
            "sf2_program": 10
        },
        "strings": {
            "name": "Strings",
            "sf2_bank": 0,
            "sf2_program": 48
        }
    }

    class Project:

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return instruments[
                channel["kind"]
            ]

    class Output:

        def __enter__(self):

            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback
        ):

            return False

    mix = {
        "channels": {
            "1": {
                "kind": "unconfigured"
            },
            "2": {
                "kind": "bad_bank"
            },
            "3": {
                "kind": "bad_program"
            },
            "4": {
                "kind": "piano"
            },
            "10": {
                "kind": "strings"
            }
        }
    }

    monkeypatch.setattr(
        fusion_editor,
        "find_fluidsynth_output",
        lambda: "FluidSynth"
    )

    monkeypatch.setattr(
        fusion_editor.mido,
        "open_output",
        lambda port_name:
            Output()
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: ""
    )

    monkeypatch.setattr(
        fusion_editor.time,
        "sleep",
        lambda seconds: None
    )

    messages = []

    monkeypatch.setattr(
        fusion_editor,
        "send_midi_message",
        lambda out, message:
            messages.append(message)
            or True
    )

    stopped = []

    monkeypatch.setattr(
        fusion_editor,
        "stop_midi_test",
        lambda out,
               channels,
               active_notes:
            stopped.append(
                (
                    set(channels),
                    set(active_notes)
                )
            )
    )

    fusion_editor.test_mix_channels_all(
        Project(),
        mix
    )

    output = capsys.readouterr().out

    assert (
        "CH 1 - Non configuré"
        in output
    )

    program_changes = [
        message
        for message in messages
        if message.type
        == "program_change"
    ]

    assert [
        (
            message.channel,
            message.program
        )
        for message in program_changes
    ] == [
        (3, 10),
        (9, 48)
    ]

    bank_msb = [
        message
        for message in messages
        if (
            message.type
            == "control_change"
            and
            message.control == 0
        )
    ]

    assert [
        (
            message.channel,
            message.value
        )
        for message in bank_msb
    ] == [
        (3, 2),
        (9, 0)
    ]

    bank_lsb = [
        message
        for message in messages
        if (
            message.type
            == "control_change"
            and
            message.control == 32
        )
    ]

    assert [
        (
            message.channel,
            message.value
        )
        for message in bank_lsb
    ] == [
        (3, 1),
        (9, 0)
    ]

    note_ons = [
        message
        for message in messages
        if message.type == "note_on"
    ]

    note_offs = [
        message
        for message in messages
        if message.type == "note_off"
    ]

    assert len(note_ons) == 8
    assert len(note_offs) == 8

    assert stopped == [
        (
            {3, 9},
            set()
        )
    ]


@pytest.mark.parametrize(
    "failure_call",
    [
        1,
        2,
        3
    ]
)
def test_test_mix_channels_all_setup_failure(
    monkeypatch,
    failure_call
):

    class Project:

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return {
                "name": "Piano",
                "sf2_bank": 0,
                "sf2_program": 10
            }

    class Output:

        def __enter__(self):

            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback
        ):

            return False

    mix = {
        "channels": {
            "1": {}
        }
    }

    monkeypatch.setattr(
        fusion_editor,
        "find_fluidsynth_output",
        lambda: "FluidSynth"
    )

    monkeypatch.setattr(
        fusion_editor.mido,
        "open_output",
        lambda port_name:
            Output()
    )

    calls = 0

    def fake_send(
        out,
        message
    ):

        nonlocal calls

        calls += 1

        return calls != failure_call

    monkeypatch.setattr(
        fusion_editor,
        "send_midi_message",
        fake_send
    )

    stopped = []

    monkeypatch.setattr(
        fusion_editor,
        "stop_midi_test",
        lambda out,
               channels,
               active_notes:
            stopped.append(
                (
                    set(channels),
                    set(active_notes)
                )
            )
    )

    fusion_editor.test_mix_channels_all(
        Project(),
        mix
    )

    assert stopped == [
        (
            set(),
            set()
        )
    ]


def test_test_mix_channels_all_note_on_failure(
    monkeypatch
):

    class Project:

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return {
                "name": "Piano",
                "sf2_bank": 0,
                "sf2_program": 10
            }

    class Output:

        def __enter__(self):

            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback
        ):

            return False

    mix = {
        "channels": {
            "1": {}
        }
    }

    monkeypatch.setattr(
        fusion_editor,
        "find_fluidsynth_output",
        lambda: "FluidSynth"
    )

    monkeypatch.setattr(
        fusion_editor.mido,
        "open_output",
        lambda port_name:
            Output()
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: ""
    )

    calls = 0

    def fake_send(
        out,
        message
    ):

        nonlocal calls

        calls += 1

        # 1-3 = préparation
        # 4   = premier note_on
        return calls != 4

    monkeypatch.setattr(
        fusion_editor,
        "send_midi_message",
        fake_send
    )

    stopped = []

    monkeypatch.setattr(
        fusion_editor,
        "stop_midi_test",
        lambda out,
               channels,
               active_notes:
            stopped.append(
                (
                    set(channels),
                    set(active_notes)
                )
            )
    )

    fusion_editor.test_mix_channels_all(
        Project(),
        mix
    )

    assert stopped == [
        (
            {0},
            set()
        )
    ]


def test_test_mix_channels_all_note_off_failure(
    monkeypatch
):

    class Project:

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return {
                "name": "Piano",
                "sf2_bank": 0,
                "sf2_program": 10
            }

    class Output:

        def __enter__(self):

            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback
        ):

            return False

    mix = {
        "channels": {
            "1": {}
        }
    }

    monkeypatch.setattr(
        fusion_editor,
        "find_fluidsynth_output",
        lambda: "FluidSynth"
    )

    monkeypatch.setattr(
        fusion_editor.mido,
        "open_output",
        lambda port_name:
            Output()
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: ""
    )

    monkeypatch.setattr(
        fusion_editor.time,
        "sleep",
        lambda seconds: None
    )

    calls = 0

    def fake_send(
        out,
        message
    ):

        nonlocal calls

        calls += 1

        # 1-3 = préparation
        # 4   = note_on
        # 5   = note_off
        return calls != 5

    monkeypatch.setattr(
        fusion_editor,
        "send_midi_message",
        fake_send
    )

    stopped = []

    monkeypatch.setattr(
        fusion_editor,
        "stop_midi_test",
        lambda out,
               channels,
               active_notes:
            stopped.append(
                (
                    set(channels),
                    set(active_notes)
                )
            )
    )

    fusion_editor.test_mix_channels_all(
        Project(),
        mix
    )

    assert stopped == [
        (
            {0},
            {
                (0, 60)
            }
        )
    ]


def test_test_mix_channels_all_keyboard_interrupt(
    monkeypatch,
    capsys
):

    class Project:

        def resolve_mix_channel_instrument(
            self,
            channel
        ):

            return {
                "name": "Piano",
                "sf2_bank": 0,
                "sf2_program": 10
            }

    class Output:

        def __enter__(self):

            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback
        ):

            return False

    mix = {
        "channels": {
            "1": {}
        }
    }

    monkeypatch.setattr(
        fusion_editor,
        "find_fluidsynth_output",
        lambda: "FluidSynth"
    )

    monkeypatch.setattr(
        fusion_editor.mido,
        "open_output",
        lambda port_name:
            Output()
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            (_ for _ in ()).throw(
                KeyboardInterrupt()
            )
    )

    monkeypatch.setattr(
        fusion_editor,
        "send_midi_message",
        lambda out, message:
            True
    )

    monkeypatch.setattr(
        fusion_editor,
        "stop_midi_test",
        lambda *args:
            None
    )

    fusion_editor.test_mix_channels_all(
        Project(),
        mix
    )

    assert (
        "Test interrompu."
        in capsys.readouterr().out
    )


def test_test_mix_channels_all_open_output_error(
    monkeypatch,
    capsys
):

    monkeypatch.setattr(
        fusion_editor,
        "find_fluidsynth_output",
        lambda: "FluidSynth"
    )

    def fail_open(
        port_name
    ):

        raise RuntimeError(
            "port failure"
        )

    monkeypatch.setattr(
        fusion_editor.mido,
        "open_output",
        fail_open
    )

    fusion_editor.test_mix_channels_all(
        object(),
        {
            "channels": {
                "1": {}
            }
        }
    )

    assert (
        "Erreur lors de l'accès au port MIDI : port failure"
        in capsys.readouterr().out
    )


def test_list_mixes_all_states(
    capsys
):

    class Project:

        def count_mixes(self):

            return 6

        def iter_mixes(self):

            return iter([
                (
                    "0:0",
                    {
                        "name": "Error"
                    }
                ),
                (
                    "0:1",
                    {
                        "name": "Empty"
                    }
                ),
                (
                    "0:2",
                    {
                        "name": "Unconfigured"
                    }
                ),
                (
                    "0:3",
                    {
                        "name": "Partial"
                    }
                ),
                (
                    "0:4",
                    {
                        "name": "Configured"
                    }
                ),
                (
                    "0:5",
                    {}
                )
            ])

        def get_mix_diagnostic(self):

            return [
                {
                    "mix": "0:0",
                    "channels": [
                        {
                            "fusion_valid": False,
                            "soundfont_configured": True
                        }
                    ]
                },
                {
                    "mix": "0:1",
                    "channels": []
                },
                {
                    "mix": "0:2",
                    "channels": [
                        {
                            "fusion_valid": True,
                            "soundfont_configured": False
                        }
                    ]
                },
                {
                    "mix": "0:3",
                    "channels": [
                        {
                            "fusion_valid": True,
                            "soundfont_configured": True
                        },
                        {
                            "fusion_valid": True,
                            "soundfont_configured": False
                        }
                    ]
                },
                {
                    "mix": "0:4",
                    "channels": [
                        {
                            "fusion_valid": True,
                            "soundfont_configured": True
                        }
                    ]
                }
            ]

    result = fusion_editor.list_mixes(
        Project()
    )

    assert result == [
        "0:0",
        "0:1",
        "0:2",
        "0:3",
        "0:4",
        "0:5"
    ]

    output = capsys.readouterr().out

    assert "Mix disponibles : 6" in output

    assert "Erreur Fusion" in output
    assert "À configurer" in output
    assert "Partiellement configuré" in output
    assert "OK" in output

    assert "0:5" in output


@pytest.mark.parametrize(
    "status_filter, expected",
    [
        (
            "error",
            ["0:0"]
        ),
        (
            "unconfigured",
            [
                "0:1",
                "0:2"
            ]
        ),
        (
            "partial",
            ["0:2"]
        ),
        (
            "configured",
            ["0:3"]
        )
    ]
)
def test_list_mixes_filters(
    capsys,
    status_filter,
    expected
):

    class Project:

        def count_mixes(self):

            return 4

        def iter_mixes(self):

            return iter([
                (
                    "0:0",
                    {
                        "name": "Error"
                    }
                ),
                (
                    "0:1",
                    {
                        "name": "Unconfigured"
                    }
                ),
                (
                    "0:2",
                    {
                        "name": "Partial"
                    }
                ),
                (
                    "0:3",
                    {
                        "name": "Configured"
                    }
                )
            ])

        def get_mix_diagnostic(self):

            return [
                {
                    "mix": "0:0",
                    "channels": [
                        {
                            "fusion_valid": False,
                            "soundfont_configured": False
                        }
                    ]
                },
                {
                    "mix": "0:1",
                    "channels": [
                        {
                            "fusion_valid": True,
                            "soundfont_configured": False
                        }
                    ]
                },
                {
                    "mix": "0:2",
                    "channels": [
                        {
                            "fusion_valid": True,
                            "soundfont_configured": True
                        },
                        {
                            "fusion_valid": True,
                            "soundfont_configured": False
                        }
                    ]
                },
                {
                    "mix": "0:3",
                    "channels": [
                        {
                            "fusion_valid": True,
                            "soundfont_configured": True
                        }
                    ]
                }
            ]

    result = fusion_editor.list_mixes(
        Project(),
        status_filter
    )

    assert result == expected

    capsys.readouterr()


@pytest.mark.parametrize(
    "status_filter, expected",
    [
        (
            "error",
            "Aucun MIX en erreur."
        ),
        (
            "unconfigured",
            "Aucun MIX à configurer."
        ),
        (
            "partial",
            "Aucun MIX partiellement configuré."
        ),
        (
            "configured",
            "Aucun MIX configuré."
        ),
        (
            None,
            "Aucun MIX."
        )
    ]
)
def test_list_mixes_empty(
    capsys,
    status_filter,
    expected
):

    class Project:

        def count_mixes(self):

            return 0

        def iter_mixes(self):

            return iter([])

        def get_mix_diagnostic(self):

            return []

    result = fusion_editor.list_mixes(
        Project(),
        status_filter
    )

    assert result is None

    assert (
        expected
        in capsys.readouterr().out
    )


def test_instruments_menu(
    monkeypatch
):

    calls = []

    monkeypatch.setattr(
        fusion_editor,
        "list_instruments",
        lambda project:
            calls.append("list")
    )

    monkeypatch.setattr(
        fusion_editor,
        "add_instrument",
        lambda project:
            calls.append("add")
    )

    monkeypatch.setattr(
        fusion_editor,
        "edit_instrument",
        lambda project:
            calls.append("edit")
    )

    monkeypatch.setattr(
        fusion_editor,
        "delete_instrument",
        lambda project:
            calls.append("delete")
    )

    responses = iter([
        "1",
        "2",
        "3",
        "4",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    project = object()

    fusion_editor.instruments_menu(
        project
    )

    assert calls == [
        "list",
        "add",
        "edit",
        "delete"
    ]


def test_list_instruments_empty(
    capsys
):

    class Project:

        def list_instruments(self):

            return []

    fusion_editor.list_instruments(
        Project()
    )

    assert (
        "Aucun instrument."
        in capsys.readouterr().out
    )


def test_list_instruments_sorted(
    capsys
):

    class Project:

        def list_instruments(self):

            return [
                (
                    "strings",
                    {
                        "name": "Strings",
                        "sf2_bank": 1,
                        "sf2_program": 48
                    }
                ),
                (
                    "unknown",
                    {}
                ),
                (
                    "piano",
                    {
                        "name": "Piano",
                        "sf2_bank": 0,
                        "sf2_program": 1
                    }
                )
            ]

    fusion_editor.list_instruments(
        Project()
    )

    output = capsys.readouterr().out

    assert "Instruments : 3" in output
    assert "?" in output

    assert (
        output.index("Piano")
        <
        output.index("Strings")
    )


def test_add_instrument_sf2_cancel(
    monkeypatch
):

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "1"
    )

    monkeypatch.setattr(
        fusion_editor,
        "choose_sf2_preset",
        lambda: None
    )

    fusion_editor.add_instrument(
        object()
    )


@pytest.mark.parametrize(
    "responses, existing, read_values, expected",
    [
        (
            ["2", ""],
            False,
            [],
            "Identifiant requis."
        ),
        (
            ["2", "piano"],
            True,
            [],
            "Identifiant déjà utilisé."
        ),
        (
            ["2", "piano", ""],
            False,
            [],
            "Nom requis."
        ),
        (
            ["2", "piano", "Piano"],
            False,
            [None],
            "Ajout annulé."
        ),
        (
            ["2", "piano", "Piano"],
            False,
            [0, None],
            "Ajout annulé."
        )
    ]
)
def test_add_instrument_manual_cancel(
    monkeypatch,
    capsys,
    responses,
    existing,
    read_values,
    expected
):

    responses = iter(responses)

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    class Project:

        def get_instrument(
            self,
            instrument_id
        ):

            return (
                {"name": "Existing"}
                if existing
                else None
            )

    values = iter(read_values)

    monkeypatch.setattr(
        fusion_editor,
        "read_int",
        lambda *args:
            next(values)
    )

    fusion_editor.add_instrument(
        Project()
    )

    assert (
        expected
        in capsys.readouterr().out
    )


def test_add_instrument_invalid_source(
    monkeypatch,
    capsys
):

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "x"
    )

    fusion_editor.add_instrument(
        object()
    )

    assert (
        "Choix invalide."
        in capsys.readouterr().out
    )


def test_add_instrument_success(
    monkeypatch,
    capsys
):

    added = []

    class Project:

        def validate(self):

            return ["existing"]

        def get_blocking_errors(
            self,
            errors
        ):

            assert errors == ["existing"]

            return ["blocking"]

        def snapshot(self):

            return {
                "before": True
            }

        def add_instrument(
            self,
            instrument_id,
            instrument
        ):

            added.append(
                (
                    instrument_id,
                    instrument
                )
            )

            return True, []

        def save_safe(
            self,
            allowed_errors=None
        ):

            assert allowed_errors == [
                "blocking"
            ]

            return True

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "1"
    )

    monkeypatch.setattr(
        fusion_editor,
        "choose_sf2_preset",
        lambda: {
            "id": "grand_piano",
            "name": "Grand Piano",
            "sf2_bank": 2,
            "sf2_program": 10
        }
    )

    fusion_editor.add_instrument(
        Project()
    )

    assert added == [
        (
            "grand_piano",
            {
                "name": "Grand Piano",
                "sf2_bank": 2,
                "sf2_program": 10
            }
        )
    ]

    assert (
        "Instrument ajouté."
        in capsys.readouterr().out
    )


def test_add_instrument_manual_success(
    monkeypatch,
    capsys
):

    class Project:

        def get_instrument(
            self,
            instrument_id
        ):

            return None

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def snapshot(self):

            return {}

        def add_instrument(
            self,
            instrument_id,
            instrument
        ):

            assert instrument_id == "piano"

            assert instrument == {
                "name": "Piano",
                "sf2_bank": 12,
                "sf2_program": 34
            }

            return True, []

        def save_safe(
            self,
            allowed_errors=None
        ):

            return True

    responses = iter([
        "2",
        "piano",
        "Piano"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    values = iter([
        12,
        34
    ])

    monkeypatch.setattr(
        fusion_editor,
        "read_int",
        lambda *args:
            next(values)
    )

    fusion_editor.add_instrument(
        Project()
    )

    assert (
        "Instrument ajouté."
        in capsys.readouterr().out
    )


def test_add_instrument_failure(
    monkeypatch,
    capsys
):

    printed_errors = []

    class Project:

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def snapshot(self):

            return {}

        def add_instrument(
            self,
            instrument_id,
            instrument
        ):

            return False, [
                "invalid"
            ]

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "1"
    )

    monkeypatch.setattr(
        fusion_editor,
        "choose_sf2_preset",
        lambda: {
            "id": "piano",
            "name": "Piano",
            "sf2_bank": 0,
            "sf2_program": 1
        }
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_error_messages",
        lambda errors:
            printed_errors.extend(errors)
    )

    fusion_editor.add_instrument(
        Project()
    )

    assert printed_errors == [
        "invalid"
    ]

    assert (
        "Instrument non ajouté."
        in capsys.readouterr().out
    )


def test_add_instrument_save_failure(
    monkeypatch,
    capsys
):

    restored = []

    class Project:

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

        def add_instrument(
            self,
            instrument_id,
            instrument
        ):

            return True, []

        def save_safe(
            self,
            allowed_errors=None
        ):

            return False

        def restore_snapshot(
            self,
            data
        ):

            restored.append(data)

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "1"
    )

    monkeypatch.setattr(
        fusion_editor,
        "choose_sf2_preset",
        lambda: {
            "id": "piano",
            "name": "Piano",
            "sf2_bank": 0,
            "sf2_program": 1
        }
    )

    fusion_editor.add_instrument(
        Project()
    )

    assert restored == [
        {
            "original": True
        }
    ]

    assert (
        "Sauvegarde non effectuée."
        in capsys.readouterr().out
    )


def test_delete_instrument_cancel_selection(
    monkeypatch
):

    class Project:

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

    monkeypatch.setattr(
        fusion_editor,
        "choose_instrument",
        lambda *args, **kwargs:
            None
    )

    fusion_editor.delete_instrument(
        Project()
    )


def test_delete_instrument_unknown(
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

        def get_instrument(
            self,
            instrument_id
        ):

            return None

    monkeypatch.setattr(
        fusion_editor,
        "choose_instrument",
        lambda *args, **kwargs: {
            "id": "unknown"
        }
    )

    fusion_editor.delete_instrument(
        Project()
    )

    assert (
        "Instrument inconnu."
        in capsys.readouterr().out
    )


def test_delete_instrument_confirmation_cancel(
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

        def get_instrument(
            self,
            instrument_id
        ):

            return {
                "name": "Piano"
            }

    monkeypatch.setattr(
        fusion_editor,
        "choose_instrument",
        lambda *args, **kwargs: {
            "id": "piano"
        }
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "n"
    )

    fusion_editor.delete_instrument(
        Project()
    )

    assert (
        "Annulé."
        in capsys.readouterr().out
    )


def test_delete_instrument_used(
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

        def get_instrument(
            self,
            instrument_id
        ):

            return {
                "name": "Piano"
            }

        def find_instrument_usage(
            self,
            instrument_id
        ):

            return [
                {
                    "type": "program",
                    "program_id": "0:1",
                    "part_id": "1"
                },
                {
                    "type": "mix",
                    "mix_id": "0:2",
                    "channel_id": "2"
                },
                {
                    "type": "song",
                    "song_id": "0:3",
                    "channel_id": "3",
                    "program_id": "0:4"
                },
                {
                    "type": "other",
                    "value": "unknown"
                }
            ]

    monkeypatch.setattr(
        fusion_editor,
        "choose_instrument",
        lambda *args, **kwargs: {
            "id": "piano"
        }
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "o"
    )

    fusion_editor.delete_instrument(
        Project()
    )

    output = capsys.readouterr().out

    assert "Instrument utilisé par :" in output
    assert "- PROGRAM 0:1 PART 1" in output
    assert "- MIX 0:2 CH 2" in output
    assert "- SONG 0:3 CH 3 PROGRAM 0:4" in output


def test_delete_instrument_success(
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

        def get_instrument(
            self,
            instrument_id
        ):

            return {
                "name": "Piano"
            }

        def find_instrument_usage(
            self,
            instrument_id
        ):

            return []

        def snapshot(self):

            return {}

        def remove_instrument(
            self,
            instrument_id
        ):

            return True, []

        def save_safe(
            self,
            allowed_errors=None
        ):

            return True

    monkeypatch.setattr(
        fusion_editor,
        "choose_instrument",
        lambda *args, **kwargs: {
            "id": "piano"
        }
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "o"
    )

    fusion_editor.delete_instrument(
        Project()
    )

    assert (
        "Instrument supprimé."
        in capsys.readouterr().out
    )


def test_delete_instrument_failure(
    monkeypatch,
    capsys
):

    printed_errors = []

    class Project:

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def get_instrument(
            self,
            instrument_id
        ):

            return {
                "name": "Piano"
            }

        def find_instrument_usage(
            self,
            instrument_id
        ):

            return []

        def snapshot(self):

            return {}

        def remove_instrument(
            self,
            instrument_id
        ):

            return False, [
                "cannot remove"
            ]

    monkeypatch.setattr(
        fusion_editor,
        "choose_instrument",
        lambda *args, **kwargs: {
            "id": "piano"
        }
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "o"
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_error_messages",
        lambda errors:
            printed_errors.extend(errors)
    )

    fusion_editor.delete_instrument(
        Project()
    )

    assert printed_errors == [
        "cannot remove"
    ]

    assert (
        "Instrument non supprimé."
        in capsys.readouterr().out
    )


def test_delete_instrument_save_failure(
    monkeypatch
):

    restored = []

    class Project:

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def get_instrument(
            self,
            instrument_id
        ):

            return {
                "name": "Piano"
            }

        def find_instrument_usage(
            self,
            instrument_id
        ):

            return []

        def snapshot(self):

            return {
                "original": True
            }

        def remove_instrument(
            self,
            instrument_id
        ):

            return True, []

        def save_safe(
            self,
            allowed_errors=None
        ):

            return False

        def restore_snapshot(
            self,
            data
        ):

            restored.append(data)

    monkeypatch.setattr(
        fusion_editor,
        "choose_instrument",
        lambda *args, **kwargs: {
            "id": "piano"
        }
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "o"
    )

    fusion_editor.delete_instrument(
        Project()
    )

    assert restored == [
        {
            "original": True
        }
    ]


def test_edit_instrument_cancel(
    monkeypatch
):

    class Project:

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

    monkeypatch.setattr(
        fusion_editor,
        "choose_instrument",
        lambda *args, **kwargs:
            None
    )

    fusion_editor.edit_instrument(
        Project()
    )


def test_edit_instrument_unknown(
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

        def get_instrument(
            self,
            instrument_id
        ):

            return None

    monkeypatch.setattr(
        fusion_editor,
        "choose_instrument",
        lambda *args, **kwargs: {
            "id": "unknown"
        }
    )

    fusion_editor.edit_instrument(
        Project()
    )

    assert (
        "Instrument inconnu."
        in capsys.readouterr().out
    )


def test_edit_instrument_success(
    monkeypatch,
    capsys
):

    updated_values = []

    class Project:

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def get_instrument(
            self,
            instrument_id
        ):

            return {
                "name": "Old Piano",
                "sf2_bank": 1,
                "sf2_program": 10
            }

        def snapshot(self):

            return {
                "original": True
            }

        def update_instrument(
            self,
            instrument_id,
            instrument
        ):

            updated_values.append(
                (
                    instrument_id,
                    instrument
                )
            )

            return True, []

        def save_safe(
            self,
            allowed_errors=None
        ):

            return True

    monkeypatch.setattr(
        fusion_editor,
        "choose_instrument",
        lambda *args, **kwargs: {
            "id": "piano"
        }
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            "New Piano"
    )

    values = iter([
        2,
        None
    ])

    monkeypatch.setattr(
        fusion_editor,
        "read_int",
        lambda *args:
            next(values)
    )

    fusion_editor.edit_instrument(
        Project()
    )

    assert updated_values == [
        (
            "piano",
            {
                "name": "New Piano",
                "sf2_bank": 2,
                "sf2_program": 10
            }
        )
    ]

    assert (
        "Instrument modifié."
        in capsys.readouterr().out
    )


def test_edit_instrument_keep_values(
    monkeypatch
):

    updated_values = []

    class Project:

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def get_instrument(
            self,
            instrument_id
        ):

            return {
                "name": "Piano",
                "sf2_bank": 1,
                "sf2_program": 10
            }

        def snapshot(self):

            return {}

        def update_instrument(
            self,
            instrument_id,
            instrument
        ):

            updated_values.append(
                instrument
            )

            return True, []

        def save_safe(
            self,
            allowed_errors=None
        ):

            return True

    monkeypatch.setattr(
        fusion_editor,
        "choose_instrument",
        lambda *args, **kwargs: {
            "id": "piano"
        }
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: ""
    )

    values = iter([
        None,
        20
    ])

    monkeypatch.setattr(
        fusion_editor,
        "read_int",
        lambda *args:
            next(values)
    )

    fusion_editor.edit_instrument(
        Project()
    )

    assert updated_values == [
        {
            "name": "Piano",
            "sf2_bank": 1,
            "sf2_program": 20
        }
    ]


def test_edit_instrument_update_failure(
    monkeypatch,
    capsys
):

    printed_errors = []

    class Project:

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def get_instrument(
            self,
            instrument_id
        ):

            return {
                "name": "Piano",
                "sf2_bank": 0,
                "sf2_program": 1
            }

        def snapshot(self):

            return {}

        def update_instrument(
            self,
            instrument_id,
            instrument
        ):

            return False, [
                "invalid"
            ]

    monkeypatch.setattr(
        fusion_editor,
        "choose_instrument",
        lambda *args, **kwargs: {
            "id": "piano"
        }
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: ""
    )

    monkeypatch.setattr(
        fusion_editor,
        "read_int",
        lambda *args: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_error_messages",
        lambda errors:
            printed_errors.extend(errors)
    )

    fusion_editor.edit_instrument(
        Project()
    )

    assert printed_errors == [
        "invalid"
    ]

    assert (
        "Instrument non modifié."
        in capsys.readouterr().out
    )


def test_edit_instrument_save_failure(
    monkeypatch,
    capsys
):

    restored = []

    class Project:

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def get_instrument(
            self,
            instrument_id
        ):

            return {
                "name": "Piano",
                "sf2_bank": 0,
                "sf2_program": 1
            }

        def snapshot(self):

            return {
                "original": True
            }

        def update_instrument(
            self,
            instrument_id,
            instrument
        ):

            return True, []

        def save_safe(
            self,
            allowed_errors=None
        ):

            return False

        def restore_snapshot(
            self,
            data
        ):

            restored.append(data)

    monkeypatch.setattr(
        fusion_editor,
        "choose_instrument",
        lambda *args, **kwargs: {
            "id": "piano"
        }
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: ""
    )

    monkeypatch.setattr(
        fusion_editor,
        "read_int",
        lambda *args: None
    )

    fusion_editor.edit_instrument(
        Project()
    )

    assert restored == [
        {
            "original": True
        }
    ]

    assert (
        "Sauvegarde non effectuée."
        in capsys.readouterr().out
    )


def test_validate_and_repair_no_errors(
    monkeypatch
):

    called = []

    class Project:

        def validate(self):

            return []

    monkeypatch.setattr(
        fusion_editor,
        "print_validation_errors",
        lambda *args:
            called.append(True)
    )

    fusion_editor.validate_and_repair(
        Project()
    )

    assert called == []


def test_validate_and_repair_errors(
    monkeypatch,
    capsys
):

    errors = [
        "error 1",
        "error 2"
    ]

    called = []

    class Project:

        def validate(self):

            return errors

    monkeypatch.setattr(
        fusion_editor,
        "print_validation_errors",
        lambda project, received:
            called.append(received)
    )

    project = Project()

    fusion_editor.validate_and_repair(
        project
    )

    assert called == [
        errors
    ]

    assert (
        "Aucune réparation automatique disponible."
        in capsys.readouterr().out
    )


def test_list_programs_empty(
    capsys
):

    class Project:

        def iter_programs(self):

            return iter([])

        def get_program_diagnostic(self):

            return []

    result = fusion_editor.list_programs(
        Project()
    )

    assert result is None

    assert (
        "Aucun PROGRAM."
        in capsys.readouterr().out
    )


def test_list_programs_all_states(
    capsys
):

    class Project:

        def iter_programs(self):

            return iter([
                (
                    "0:0",
                    {
                        "name": "Error",
                        "parts": {
                            "1": {
                                "midi_channel": 1,
                                "bank": 0,
                                "program": 10,
                                "instrument": "piano"
                            }
                        }
                    }
                ),
                (
                    "0:1",
                    {
                        "name": "Unconfigured",
                        "parts": {
                            "1": {
                                "midi_channel": 2,
                                "bank": 1,
                                "program": 20,
                                "instrument": "missing"
                            }
                        }
                    }
                ),
                (
                    "0:2",
                    {
                        "name": "Configured",
                        "parts": {
                            "1": {
                                "midi_channel": 3,
                                "bank": 2,
                                "program": 30,
                                "instrument": "strings"
                            }
                        }
                    }
                ),
                (
                    "0:3",
                    {}
                )
            ])

        def get_program_diagnostic(self):

            return [
                {
                    "program": "0:0",
                    "fusion_valid": False,
                    "soundfont_configured": True
                },
                {
                    "program": "0:1",
                    "fusion_valid": True,
                    "soundfont_configured": False
                },
                {
                    "program": "0:2",
                    "fusion_valid": True,
                    "soundfont_configured": True
                }
            ]

        def get_program_bank_name(
            self,
            bank
        ):

            return f"Bank {bank}"

        def get_instrument(
            self,
            instrument_id
        ):

            if instrument_id == "piano":

                return {
                    "name": "Grand Piano"
                }

            if instrument_id == "strings":

                # couvre le fallback sur instrument_id
                return {
                    "sf2_bank": 0
                }

            return None

    result = fusion_editor.list_programs(
        Project()
    )

    assert result == [
        "0:0",
        "0:1",
        "0:2",
        "0:3"
    ]

    output = capsys.readouterr().out

    assert "PROGRAMS : 4" in output

    assert "Erreur Fusion" in output
    assert "À configurer" in output
    assert "OK" in output

    assert "Grand Piano" in output
    assert "Non configuré" in output

    assert "Bank 0" in output
    assert "Bank 1" in output
    assert "Bank 2" in output

    assert "strings" in output


@pytest.mark.parametrize(
    "status_filter, expected",
    [
        (
            "error",
            ["0:0"]
        ),
        (
            "unconfigured",
            ["0:1"]
        ),
        (
            "ok",
            ["0:2"]
        )
    ]
)
def test_list_programs_filters(
    status_filter,
    expected
):

    class Project:

        def iter_programs(self):

            return iter([
                (
                    "0:0",
                    {
                        "name": "Error"
                    }
                ),
                (
                    "0:1",
                    {
                        "name": "Unconfigured"
                    }
                ),
                (
                    "0:2",
                    {
                        "name": "Configured"
                    }
                )
            ])

        def get_program_diagnostic(self):

            return [
                {
                    "program": "0:0",
                    "fusion_valid": False,
                    "soundfont_configured": False
                },
                {
                    "program": "0:1",
                    "fusion_valid": True,
                    "soundfont_configured": False
                },
                {
                    "program": "0:2",
                    "fusion_valid": True,
                    "soundfont_configured": True
                }
            ]

    result = fusion_editor.list_programs(
        Project(),
        status_filter
    )

    assert result == expected


@pytest.mark.parametrize(
    "status_filter, expected",
    [
        (
            "error",
            "Aucun PROGRAM en erreur."
        ),
        (
            "unconfigured",
            "Aucun PROGRAM à configurer."
        ),
        (
            "other",
            "Aucun PROGRAM."
        )
    ]
)


def test_list_programs_filter_empty(
    capsys,
    status_filter,
    expected
):

    class Project:

        def iter_programs(self):

            return iter([
                (
                    "0:0",
                    {
                        "name": "Program"
                    }
                )
            ])

        def get_program_diagnostic(self):

            return [
                {
                    "program": "0:0",
                    "fusion_valid": True,
                    "soundfont_configured": True
                }
            ]

    result = fusion_editor.list_programs(
        Project(),
        status_filter
    )

    assert result is None

    output = capsys.readouterr().out

    assert expected in output


def test_edit_program_unknown(
    capsys
):

    class Project:

        def get_program(
            self,
            program_id
        ):

            return None

    fusion_editor.edit_program(
        Project(),
        "0:1"
    )

    assert (
        "PROGRAM inconnu."
        in capsys.readouterr().out
    )


def test_edit_program_missing_part(
    monkeypatch,
    capsys
):

    validation = []

    class Project:

        def get_program(
            self,
            program_id
        ):

            return {
                "name": "Piano",
                "parts": {}
            }

        def validate_program(
            self,
            program_id
        ):

            return [
                "invalid"
            ]

    monkeypatch.setattr(
        fusion_editor,
        "print_validation_errors",
        lambda project, errors:
            validation.extend(errors)
    )

    fusion_editor.edit_program(
        Project(),
        "0:1"
    )

    assert validation == [
        "invalid"
    ]

    assert (
        "PART absente."
        in capsys.readouterr().out
    )


def test_edit_program_display_configured(
    monkeypatch,
    capsys
):

    class Project:

        def get_program(
            self,
            program_id
        ):

            return {
                "name": "Fusion Piano",
                "parts": {
                    "1": {
                        "bank": 2,
                        "program": 10,
                        "midi_channel": 1,
                        "note_min": 20,
                        "note_max": 100,
                        "velocity_min": 10,
                        "velocity_max": 120,
                        "instrument": "piano"
                    }
                }
            }

        def validate_program(
            self,
            program_id
        ):

            return []

        def get_program_bank_name(
            self,
            bank
        ):

            return "USER"

        def resolve_part_instrument(
            self,
            part
        ):

            return {
                "name": "Grand Piano",
                "sf2_bank": 3,
                "sf2_program": 4
            }

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "q"
    )

    fusion_editor.edit_program(
        Project(),
        "2:10"
    )

    output = capsys.readouterr().out

    assert "Fusion Piano" in output
    assert "USER (2)" in output
    assert "Grand Piano" in output
    assert "SF2 Bank" in output
    assert "SF2 Program" in output


def test_edit_program_display_unconfigured(
    monkeypatch,
    capsys
):

    class Project:

        def get_program(
            self,
            program_id
        ):

            return {
                "parts": {
                    "1": {
                        "fusion_name": "Fallback"
                    }
                }
            }

        def validate_program(
            self,
            program_id
        ):

            return []

        def resolve_part_instrument(
            self,
            part
        ):

            return None

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "q"
    )

    fusion_editor.edit_program(
        Project(),
        "0:1"
    )

    output = capsys.readouterr().out

    assert "Fusion Bank    : ?" in output
    assert "Instrument     : Non configuré" in output


def test_edit_program_instrument_cancel_and_update_failure(
    monkeypatch,
    capsys
):

    errors_seen = []

    class Project:

        def get_program(
            self,
            program_id
        ):

            return {
                "name": "Piano",
                "parts": {
                    "1": {
                        "bank": 0
                    }
                }
            }

        def validate_program(
            self,
            program_id
        ):

            return []

        def get_program_bank_name(
            self,
            bank
        ):

            return "GM"

        def resolve_part_instrument(
            self,
            part
        ):

            return None

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def snapshot(self):

            return {}

        def update_program_part(
            self,
            program_id,
            part_id,
            updates
        ):

            assert updates == {
                "instrument": "piano"
            }

            return False, [
                "invalid"
            ]

    choices = iter([
        "1",
        "1",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(choices)
    )

    instruments = iter([
        None,
        {
            "id": "piano"
        }
    ])

    monkeypatch.setattr(
        fusion_editor,
        "choose_instrument",
        lambda *args, **kwargs:
            next(instruments)
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_error_messages",
        lambda errors:
            errors_seen.extend(errors)
    )

    fusion_editor.edit_program(
        Project(),
        "0:1"
    )

    assert errors_seen == [
        "invalid"
    ]

    assert (
        "Instrument non affecté."
        in capsys.readouterr().out
    )


@pytest.mark.parametrize(
    "save_result, expected",
    [
        (
            True,
            "Instrument affecté."
        ),
        (
            False,
            "Sauvegarde non effectuée."
        )
    ]
)
def test_edit_program_instrument_save(
    monkeypatch,
    capsys,
    save_result,
    expected
):

    restored = []

    class Project:

        def get_program(self, program_id):

            return {
                "name": "Piano",
                "parts": {
                    "1": {
                        "bank": 0
                    }
                }
            }

        def validate_program(self, program_id):

            return []

        def get_program_bank_name(self, bank):

            return "GM"

        def resolve_part_instrument(self, part):

            return None

        def validate(self):

            return []

        def get_blocking_errors(self, errors):

            return [
                "existing"
            ]

        def snapshot(self):

            return {
                "before": True
            }

        def update_program_part(
            self,
            program_id,
            part_id,
            updates
        ):

            return True, []

        def save_safe(
            self,
            allowed_errors=None
        ):

            assert allowed_errors == [
                "existing"
            ]

            return save_result

        def restore_snapshot(self, data):

            restored.append(data)

    choices = iter([
        "1",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(choices)
    )

    monkeypatch.setattr(
        fusion_editor,
        "choose_instrument",
        lambda *args, **kwargs: {
            "id": "piano"
        }
    )

    fusion_editor.edit_program(
        Project(),
        "0:1"
    )

    output = capsys.readouterr().out

    assert expected in output

    if save_result:

        assert restored == []

    else:

        assert restored == [
            {
                "before": True
            }
        ]


def test_edit_program_parameters_cancel_and_update_failure(
    monkeypatch,
    capsys
):

    errors_seen = []

    class Project:

        def get_program(self, program_id):

            return {
                "name": "Piano",
                "parts": {
                    "1": {
                        "bank": 0
                    }
                }
            }

        def validate_program(self, program_id):

            return []

        def get_program_bank_name(self, bank):

            return "GM"

        def resolve_part_instrument(self, part):

            return None

        def validate(self):

            return []

        def get_blocking_errors(self, errors):

            return []

        def snapshot(self):

            return {}

        def update_program_part(
            self,
            program_id,
            part_id,
            updates
        ):

            assert updates == {
                "midi_channel": 2
            }

            return False, [
                "invalid"
            ]

    choices = iter([
        "2",
        "2",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(choices)
    )

    updates = iter([
        None,
        {
            "midi_channel": 2
        }
    ])

    monkeypatch.setattr(
        fusion_editor,
        "edit_part_values",
        lambda *args:
            next(updates)
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_error_messages",
        lambda errors:
            errors_seen.extend(errors)
    )

    fusion_editor.edit_program(
        Project(),
        "0:1"
    )

    assert errors_seen == [
        "invalid"
    ]

    assert (
        "PROGRAM non modifié."
        in capsys.readouterr().out
    )


@pytest.mark.parametrize(
    "save_result, expected",
    [
        (
            True,
            "PROGRAM modifié."
        ),
        (
            False,
            "Sauvegarde non effectuée."
        )
    ]
)
def test_edit_program_parameters_save(
    monkeypatch,
    capsys,
    save_result,
    expected
):

    restored = []

    class Project:

        def get_program(self, program_id):

            return {
                "name": "Piano",
                "parts": {
                    "1": {
                        "bank": 0
                    }
                }
            }

        def validate_program(self, program_id):

            return []

        def get_program_bank_name(self, bank):

            return "GM"

        def resolve_part_instrument(self, part):

            return None

        def validate(self):

            return []

        def get_blocking_errors(self, errors):

            return []

        def snapshot(self):

            return {
                "before": True
            }

        def update_program_part(
            self,
            program_id,
            part_id,
            updates
        ):

            return True, []

        def save_safe(
            self,
            allowed_errors=None
        ):

            return save_result

        def restore_snapshot(self, data):

            restored.append(data)

    choices = iter([
        "2",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(choices)
    )

    monkeypatch.setattr(
        fusion_editor,
        "edit_part_values",
        lambda *args: {
            "midi_channel": 2
        }
    )

    fusion_editor.edit_program(
        Project(),
        "0:1"
    )

    assert expected in capsys.readouterr().out

    if save_result:

        assert restored == []

    else:

        assert restored == [
            {
                "before": True
            }
        ]


def test_edit_program_rename_cancel_and_failure(
    monkeypatch,
    capsys
):

    errors_seen = []

    class Project:

        def get_program(self, program_id):

            return {
                "name": "",
                "parts": {
                    "1": {
                        "bank": 0
                    }
                }
            }

        def validate_program(self, program_id):

            return []

        def get_program_bank_name(self, bank):

            return "GM"

        def resolve_part_instrument(self, part):

            return None

        def validate(self):

            return []

        def get_blocking_errors(self, errors):

            return []

        def snapshot(self):

            return {}

        def rename_program(
            self,
            program_id,
            name
        ):

            assert name == "New Name"

            return False, [
                "invalid"
            ]

    responses = iter([
        "3",
        "",
        "3",
        "New Name",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_error_messages",
        lambda errors:
            errors_seen.extend(errors)
    )

    fusion_editor.edit_program(
        Project(),
        "0:1"
    )

    assert errors_seen == [
        "invalid"
    ]

    output = capsys.readouterr().out

    assert "Non défini" in output
    assert "Nom Fusion non modifié." in output


@pytest.mark.parametrize(
    "save_result, expected",
    [
        (
            True,
            "Nom Fusion modifié."
        ),
        (
            False,
            "Sauvegarde non effectuée."
        )
    ]
)
def test_edit_program_rename_save(
    monkeypatch,
    capsys,
    save_result,
    expected
):

    restored = []

    class Project:

        def get_program(self, program_id):

            return {
                "name": "Old Name",
                "parts": {
                    "1": {
                        "bank": 0
                    }
                }
            }

        def validate_program(self, program_id):

            return []

        def get_program_bank_name(self, bank):

            return "GM"

        def resolve_part_instrument(self, part):

            return None

        def validate(self):

            return []

        def get_blocking_errors(self, errors):

            return []

        def snapshot(self):

            return {
                "before": True
            }

        def rename_program(
            self,
            program_id,
            name
        ):

            assert name == "New Name"

            return True, []

        def save_safe(
            self,
            allowed_errors=None
        ):

            return save_result

        def restore_snapshot(self, data):

            restored.append(data)

    responses = iter([
        "3",
        "New Name",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.edit_program(
        Project(),
        "0:1"
    )

    assert expected in capsys.readouterr().out

    if save_result:

        assert restored == []

    else:

        assert restored == [
            {
                "before": True
            }
        ]


def test_list_songs_empty(
    capsys
):

    class Project:

        def iter_songs(self):

            return iter([])

        def get_song_diagnostic(self):

            return []

    result = fusion_editor.list_songs(
        Project()
    )

    assert result is None

    assert (
        "Aucune SONG."
        in capsys.readouterr().out
    )


def test_list_songs_all_states(
    capsys
):

    class Project:

        def iter_songs(self):

            return iter([
                (
                    "1",
                    {
                        "name": "Error Song",
                        "channels": {
                            "2": {
                                "programs": {}
                            }
                        }
                    }
                ),
                (
                    "2",
                    {
                        "name": "2",
                        "channels": {
                            "1": {
                                "programs": {
                                    "0:10": {}
                                }
                            }
                        }
                    }
                ),
                (
                    "3",
                    {
                        "name": "Configured Song",
                        "channels": {
                            "10": {
                                "programs": {
                                    "1:20": {},
                                    "bad": {}
                                }
                            },
                            "2": {
                                "programs": {
                                    "2:30": {}
                                }
                            }
                        }
                    }
                )
            ])

        def get_song_diagnostic(self):

            return [
                {
                    "song": "1",
                    "channels": [
                        {
                            "fusion_valid": False
                        }
                    ]
                },
                {
                    "song": "2",
                    "channels": [
                        {
                            "fusion_valid": True
                        }
                    ]
                },
                {
                    "song": "3",
                    "channels": [
                        {
                            "fusion_valid": True
                        }
                    ]
                }
            ]

        def resolve_song_program_instrument(
            self,
            program_id,
            program_data
        ):

            if program_id == "0:10":

                return None

            if program_id == "bad":

                return {
                    "sf2_bank": 0
                }

            return {
                "name": f"Instrument {program_id}"
            }

        def get_program_bank_name(
            self,
            bank
        ):

            return f"Bank {bank}"

    result = fusion_editor.list_songs(
        Project()
    )

    assert result == [
        "1",
        "2",
        "3"
    ]

    output = capsys.readouterr().out

    assert "Error Song" in output
    assert "Erreur Fusion" in output

    assert "À configurer" in output
    assert "Aucun PROGRAM" in output

    assert "Configured Song" in output
    assert "OK" in output

    assert "Instrument 1:20" in output
    assert "Instrument 2:30" in output

    # instrument présent mais sans nom
    assert "Non configuré" in output

    # program_id invalide → banque inconnue
    assert "?" in output


def test_list_songs_no_channels(
    capsys
):

    class Project:

        def iter_songs(self):

            return iter([
                (
                    "1",
                    {
                        "name": "Empty",
                        "channels": {}
                    }
                )
            ])

        def get_song_diagnostic(self):

            return [
                {
                    "song": "1",
                    "channels": [
                        {
                            "fusion_valid": True
                        }
                    ]
                }
            ]

    result = fusion_editor.list_songs(
        Project()
    )

    assert result == [
        "1"
    ]

    output = capsys.readouterr().out

    assert (
        "0/0 canaux configurés - À configurer"
        in output
    )


@pytest.mark.parametrize(
    "status_filter, expected",
    [
        (
            "error",
            ["error"]
        ),
        (
            "unconfigured",
            ["unconfigured"]
        ),
        (
            "ok",
            ["ok"]
        )
    ]
)
def test_list_songs_filters(
    status_filter,
    expected
):

    class Project:

        def iter_songs(self):

            return iter([
                (
                    "error",
                    {
                        "channels": {}
                    }
                ),
                (
                    "unconfigured",
                    {
                        "channels": {}
                    }
                ),
                (
                    "ok",
                    {
                        "channels": {
                            "1": {
                                "programs": {
                                    "0:1": {}
                                }
                            }
                        }
                    }
                )
            ])

        def get_song_diagnostic(self):

            return [
                {
                    "song": "error",
                    "channels": [
                        {
                            "fusion_valid": False
                        }
                    ]
                },
                {
                    "song": "unconfigured",
                    "channels": [
                        {
                            "fusion_valid": True
                        }
                    ]
                },
                {
                    "song": "ok",
                    "channels": [
                        {
                            "fusion_valid": True
                        }
                    ]
                }
            ]

        def resolve_song_program_instrument(
            self,
            program_id,
            program_data
        ):

            return {
                "name": "Piano"
            }

        def get_program_bank_name(
            self,
            bank
        ):

            return "GM"

    result = fusion_editor.list_songs(
        Project(),
        status_filter
    )

    assert result == expected


@pytest.mark.parametrize(
    "status_filter, expected",
    [
        (
            "error",
            "Aucune SONG en erreur."
        ),
        (
            "unconfigured",
            "Aucune SONG à configurer."
        ),
        (
            "other",
            "Aucune SONG."
        )
    ]
)
def test_list_songs_filter_empty(
    capsys,
    status_filter,
    expected
):

    class Project:

        def iter_songs(self):

            return iter([
                (
                    "1",
                    {
                        "channels": {
                            "1": {
                                "programs": {
                                    "0:1": {}
                                }
                            }
                        }
                    }
                )
            ])

        def get_song_diagnostic(self):

            return [
                {
                    "song": "1",
                    "channels": [
                        {
                            "fusion_valid": True
                        }
                    ]
                }
            ]

        def resolve_song_program_instrument(
            self,
            program_id,
            program_data
        ):

            return {
                "name": "Piano"
            }

    result = fusion_editor.list_songs(
        Project(),
        status_filter
    )

    assert result is None

    assert (
        expected
        in capsys.readouterr().out
    )


def test_edit_song_unknown(
    capsys
):

    class Project:

        def get_song(self, song_id):

            return None

    fusion_editor.edit_song(
        Project(),
        "song1"
    )

    assert "SONG inconnue." in capsys.readouterr().out


def test_edit_song_no_channels(
    monkeypatch,
    capsys
):

    validation = []

    class Project:

        def get_song(self, song_id):

            return {
                "name": "Empty",
                "channels": {}
            }

        def validate_song(self, song_id):

            return ["invalid"]

    monkeypatch.setattr(
        fusion_editor,
        "print_validation_errors",
        lambda project, errors:
            validation.extend(errors)
    )

    fusion_editor.edit_song(
        Project(),
        "song1"
    )

    assert validation == ["invalid"]
    assert "Aucun canal." in capsys.readouterr().out


def test_edit_song_display_and_unknown_channel(
    monkeypatch,
    capsys
):

    class Project:

        def get_song(self, song_id):

            return {
                "name": "My Song",
                "channels": {
                    "10": {
                        "programs": {}
                    },
                    "2": {
                        "programs": {
                            "0:1": {}
                        }
                    },
                    "3": {
                        "programs": {
                            "0:2": {},
                            "0:3": {}
                        }
                    }
                }
            }

        def validate_song(self, song_id):

            return []

        def resolve_song_program_instrument(
            self,
            program_id,
            program_data
        ):

            if program_id == "0:1":

                return None

            if program_id == "0:2":

                return {
                    "name": "Piano"
                }

            return {
                "sf2_bank": 0
            }

    responses = iter([
        "99",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(responses)
    )

    fusion_editor.edit_song(
        Project(),
        "song1"
    )

    output = capsys.readouterr().out

    assert "My Song" in output
    assert "CH 10 - Aucun PROGRAM" in output
    assert "Non configuré" in output
    assert "Piano" in output
    assert "Canal inconnu." in output


def test_edit_song_multiple_program_selection_cancel(
    monkeypatch,
    capsys
):

    class Project:

        def get_song(self, song_id):

            return {
                "channels": {
                    "1": {
                        "programs": {
                            "0:1": {},
                            "0:2": {}
                        }
                    }
                }
            }

        def validate_song(self, song_id):

            return []

        def resolve_song_program_instrument(
            self,
            program_id,
            program_data
        ):

            return None

    responses = iter([
        "1",       # canal
        "bad",     # choix PROGRAM non numérique
        "99",      # hors plage
        "q",       # retour sélection PROGRAM
        "q"        # sortie SONG
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(responses)
    )

    fusion_editor.edit_song(
        Project(),
        "song1"
    )

    output = capsys.readouterr().out

    assert output.count(
        "Choix invalide."
    ) == 2


def test_edit_song_channel_without_program(
    monkeypatch,
    capsys
):

    class Project:

        def get_song(self, song_id):

            return {
                "channels": {
                    "1": {
                        "volume": 100,
                        "programs": {}
                    }
                }
            }

        def validate_song(self, song_id):

            return []

        def resolve_song_program_instrument(
            self,
            program_id,
            program_data
        ):

            return None

    responses = iter([
        "1",   # canal
        "1",   # instrument impossible
        "2",   # paramètres
        "q",   # retour sous-menu
        "q"    # sortie SONG
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(responses)
    )

    # Pour isoler ici l'appel à la fonction interne,
    # read_int retourne toujours None : aucun update.
    monkeypatch.setattr(
        fusion_editor,
        "read_int",
        lambda *args, **kwargs: None
    )

    fusion_editor.edit_song(
        Project(),
        "song1"
    )

    output = capsys.readouterr().out

    assert "Aucun PROGRAM capturé" in output
    assert "Aucun PROGRAM à modifier." in output
    assert "Aucune modification." in output


def test_edit_song_channel_parameters_update_failure(
    monkeypatch,
    capsys
):

    errors_seen = []

    class Project:

        def get_song(self, song_id):

            return {
                "channels": {
                    "1": {
                        "volume": 1,
                        "pan": 2,
                        "expression": 3,
                        "reverb": 4,
                        "chorus": 5,
                        "programs": {}
                    }
                }
            }

        def validate_song(self, song_id):

            return []

        def validate(self):

            return []

        def get_blocking_errors(self, errors):

            return []

        def snapshot(self):

            return {}

        def update_song_channel(
            self,
            song_id,
            channel_id,
            updates
        ):

            assert updates == {
                "volume": 10,
                "pan": 20,
                "expression": 30,
                "reverb": 40,
                "chorus": 50
            }

            return False, ["invalid"]

    responses = iter([
        "1",   # canal
        "2",   # paramètres
        "q",   # retour
        "q"    # sortie
    ])

    values = iter([
        10,
        20,
        30,
        40,
        50
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(responses)
    )

    monkeypatch.setattr(
        fusion_editor,
        "read_int",
        lambda *args, **kwargs:
            next(values)
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_error_messages",
        lambda errors:
            errors_seen.extend(errors)
    )

    fusion_editor.edit_song(
        Project(),
        "song1"
    )

    assert errors_seen == ["invalid"]

    assert (
        "Canal SONG non modifié."
        in capsys.readouterr().out
    )


@pytest.mark.parametrize(
    "save_result, expected",
    [
        (
            True,
            "Paramètres du canal modifiés."
        ),
        (
            False,
            "Sauvegarde non effectuée."
        )
    ]
)
def test_edit_song_channel_parameters_save(
    monkeypatch,
    capsys,
    save_result,
    expected
):

    restored = []

    class Project:

        def get_song(self, song_id):

            return {
                "channels": {
                    "1": {
                        "programs": {}
                    }
                }
            }

        def validate_song(self, song_id):

            return []

        def validate(self):

            return []

        def get_blocking_errors(self, errors):

            return ["existing"]

        def snapshot(self):

            return {
                "before": True
            }

        def update_song_channel(
            self,
            song_id,
            channel_id,
            updates
        ):

            assert updates == {
                "volume": 10
            }

            return True, []

        def save_safe(
            self,
            allowed_errors=None
        ):

            assert allowed_errors == [
                "existing"
            ]

            return save_result

        def restore_snapshot(self, data):

            restored.append(data)

    responses = iter([
        "1",
        "2",
        "q",
        "q"
    ])

    values = iter([
        10,
        None,
        None,
        None,
        None
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(responses)
    )

    monkeypatch.setattr(
        fusion_editor,
        "read_int",
        lambda *args, **kwargs:
            next(values)
    )

    fusion_editor.edit_song(
        Project(),
        "song1"
    )

    assert expected in capsys.readouterr().out

    if save_result:

        assert restored == []

    else:

        assert restored == [
            {
                "before": True
            }
        ]


def test_edit_song_single_program_display(
    monkeypatch,
    capsys
):

    class Project:

        def get_song(self, song_id):

            return {
                "name": "Test Song",
                "channels": {
                    "1": {
                        "programs": {
                            "2:42": {
                                "instrument": "local"
                            }
                        }
                    }
                }
            }

        def validate_song(self, song_id):

            return []

        def resolve_song_program_instrument(
            self,
            program_id,
            program_data
        ):

            return {
                "name": "Effective"
            }

        def get_program_bank_name(self, bank):

            assert bank == 2

            return "GM2"

        def get_program(self, program_id):

            assert program_id == "2:42"

            return {
                "name": "Fusion Piano"
            }

        def resolve_part_instrument(self, part):

            return {
                "name": "Local Piano"
            }

        def resolve_program_instrument(
            self,
            program_id
        ):

            return {
                "name": "Inherited Piano"
            }

    responses = iter([
        "1",   # canal
        "q",   # sous-menu PROGRAM
        "q"    # SONG
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(responses)
    )

    fusion_editor.edit_song(
        Project(),
        "song1"
    )

    output = capsys.readouterr().out

    assert "GM2 (2)" in output
    assert "42" in output
    assert "Fusion Piano" in output
    assert "Local Piano" in output
    assert "Inherited Piano" in output

    # présence de l'option suppression
    assert "4 - Supprimer l'instrument local" in output


def test_edit_song_multiple_program_selection(
    monkeypatch
):

    class Project:

        def get_song(self, song_id):

            return {
                "channels": {
                    "1": {
                        "programs": {
                            "0:1": {},
                            "0:2": {}
                        }
                    }
                }
            }

        def validate_song(self, song_id):

            return []

        def resolve_song_program_instrument(
            self,
            program_id,
            program_data
        ):

            return None

        def get_program_bank_name(self, bank):

            return "GM"

        def get_program(self, program_id):

            return None

        def resolve_part_instrument(self, part):

            return None

        def resolve_program_instrument(
            self,
            program_id
        ):

            return None

    responses = iter([
        "1",   # canal
        "2",   # deuxième PROGRAM
        "q",   # retour au choix PROGRAM
        "q",   # retour au choix canal
        "q"    # sortie
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(responses)
    )

    fusion_editor.edit_song(
        Project(),
        "song1"
    )


def test_edit_song_instrument_cancel_and_update_failure(
    monkeypatch,
    capsys
):

    errors_seen = []

    class Project:

        def get_song(self, song_id):

            return {
                "channels": {
                    "1": {
                        "programs": {
                            "2:42": {}
                        }
                    }
                }
            }

        def validate_song(self, song_id):

            return []

        def resolve_song_program_instrument(
            self,
            program_id,
            program_data
        ):

            return None

        def get_program_bank_name(self, bank):

            return "Bank"

        def get_program(self, program_id):

            return {
                "name": "Fusion Name"
            }

        def resolve_part_instrument(self, part):

            return None

        def resolve_program_instrument(self, program_id):

            return None

        def validate(self):

            return []

        def get_blocking_errors(self, errors):

            return []

        def snapshot(self):

            return {"before": True}

        def update_song_program(
            self,
            song_id,
            channel_id,
            program_id,
            updates
        ):

            assert updates == {
                "instrument": "piano"
            }

            return False, ["update error"]

    instruments = iter([
        None,
        {
            "id": "piano"
        }
    ])

    responses = iter([
        "1",
        "1",   # cancel choose
        "1",   # update failure
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(responses)
    )

    monkeypatch.setattr(
        fusion_editor,
        "choose_instrument",
        lambda *args, **kwargs:
            next(instruments)
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_error_messages",
        lambda errors:
            errors_seen.extend(errors)
    )

    fusion_editor.edit_song(
        Project(),
        "song1"
    )

    assert errors_seen == [
        "update error"
    ]

    assert (
        "Instrument non affecté."
        in capsys.readouterr().out
    )


@pytest.mark.parametrize(
    "save_result",
    [
        True,
        False
    ]
)
def test_edit_song_instrument_save(
    monkeypatch,
    capsys,
    save_result
):

    restored = []

    class Project:

        def get_song(self, song_id):

            return {
                "channels": {
                    "1": {
                        "programs": {
                            "2:42": {}
                        }
                    }
                }
            }

        def validate_song(self, song_id):

            return []

        def resolve_song_program_instrument(
            self,
            program_id,
            program_data
        ):

            return None

        def get_program_bank_name(self, bank):

            return "Bank"

        def get_program(self, program_id):

            return None

        def resolve_part_instrument(self, part):

            return None

        def resolve_program_instrument(self, program_id):

            return None

        def validate(self):

            return []

        def get_blocking_errors(self, errors):

            return ["existing"]

        def snapshot(self):

            return {"before": True}

        def update_song_program(
            self,
            song_id,
            channel_id,
            program_id,
            updates
        ):

            return True, []

        def save_safe(
            self,
            allowed_errors=None
        ):

            assert allowed_errors == [
                "existing"
            ]

            return save_result

        def restore_snapshot(self, data):

            restored.append(data)

    responses = iter([
        "1",
        "1",
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(responses)
    )

    monkeypatch.setattr(
        fusion_editor,
        "choose_instrument",
        lambda *args, **kwargs: {
            "id": "piano"
        }
    )

    fusion_editor.edit_song(
        Project(),
        "song1"
    )

    output = capsys.readouterr().out

    if save_result:

        assert "Instrument affecté." in output
        assert restored == []

    else:

        assert "Sauvegarde non effectuée." in output
        assert restored == [
            {"before": True}
        ]


def test_edit_song_move_channel_rejections(
    monkeypatch,
    capsys
):

    errors_seen = []

    class Project:

        def get_song(self, song_id):

            return {
                "channels": {
                    "1": {
                        "programs": {}
                    },
                    "2": {
                        "programs": {}
                    }
                }
            }

        def validate_song(self, song_id):

            return []

        def validate(self):

            return []

        def get_blocking_errors(self, errors):

            return []

        def snapshot(self):

            return {}

        def move_song_channel(
            self,
            song_id,
            old_channel,
            new_channel
        ):

            assert old_channel == "1"
            assert new_channel == "3"

            return False, ["move error"]

    responses = iter([
        "1",
        "3",   # None
        "3",   # même canal
        "3",   # déjà utilisé
        "3",   # move failure
        "q",
        "q"
    ])

    values = iter([
        None,
        1,
        2,
        3
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(responses)
    )

    monkeypatch.setattr(
        fusion_editor,
        "read_int",
        lambda *args, **kwargs:
            next(values)
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_error_messages",
        lambda errors:
            errors_seen.extend(errors)
    )

    fusion_editor.edit_song(
        Project(),
        "song1"
    )

    output = capsys.readouterr().out

    assert "Canal inchangé." in output
    assert "Canal MIDI déjà utilisé." in output
    assert "Canal MIDI non modifié." in output

    assert errors_seen == ["move error"]


@pytest.mark.parametrize(
    "save_result",
    [
        True,
        False
    ]
)
def test_edit_song_move_channel_save(
    monkeypatch,
    capsys,
    save_result
):

    restored = []

    channels = {
        "1": {
            "programs": {}
        }
    }

    class Project:

        def get_song(self, song_id):

            return {
                "channels": channels
            }

        def validate_song(self, song_id):

            return []

        def validate(self):

            return []

        def get_blocking_errors(self, errors):

            return []

        def snapshot(self):

            return {"before": True}

        def move_song_channel(
            self,
            song_id,
            old_channel,
            new_channel
        ):

            channel = channels.pop(
                old_channel
            )

            channels[new_channel] = channel

            return True, []

        def save_safe(
            self,
            allowed_errors=None
        ):

            return save_result

        def restore_snapshot(self, data):

            restored.append(data)

    responses = iter([
        "1",
        "3",
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(responses)
    )

    monkeypatch.setattr(
        fusion_editor,
        "read_int",
        lambda *args, **kwargs: 3
    )

    fusion_editor.edit_song(
        Project(),
        "song1"
    )

    output = capsys.readouterr().out

    if save_result:

        assert "Canal MIDI modifié" in output
        assert "1 → 3" in output
        assert restored == []

    else:

        assert "Sauvegarde non effectuée." in output
        assert restored == [
            {"before": True}
        ]


def test_edit_song_remove_instrument_missing(
    monkeypatch,
    capsys
):

    class Project:

        def get_song(self, song_id):

            return {
                "channels": {
                    "1": {
                        "programs": {
                            "0:1": {}
                        }
                    }
                }
            }

        def validate_song(self, song_id):

            return []

        def resolve_song_program_instrument(self, *args):

            return None

        def get_program_bank_name(self, bank):

            return "GM"

        def get_program(self, program_id):

            return None

        def resolve_part_instrument(self, part):

            return None

        def resolve_program_instrument(self, program_id):

            return None

    responses = iter([
        "1",
        "4",
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(responses)
    )

    fusion_editor.edit_song(
        Project(),
        "song1"
    )

    assert (
        "Aucun instrument local à supprimer."
        in capsys.readouterr().out
    )


@pytest.mark.parametrize(
    "update_ok, save_result, inherited",
    [
        (
            False,
            True,
            None
        ),
        (
            True,
            True,
            {"name": "Inherited"}
        ),
        (
            True,
            True,
            None
        ),
        (
            True,
            False,
            None
        )
    ]
)
def test_edit_song_remove_instrument(
    monkeypatch,
    capsys,
    update_ok,
    save_result,
    inherited
):

    restored = []
    errors_seen = []

    program_data = {
        "instrument": "local"
    }

    class Project:

        def get_song(self, song_id):

            return {
                "channels": {
                    "1": {
                        "programs": {
                            "0:1": program_data
                        }
                    }
                }
            }

        def validate_song(self, song_id):

            return []

        def resolve_song_program_instrument(self, *args):

            return {
                "name": "Effective"
            }

        def get_program_bank_name(self, bank):

            return "GM"

        def get_program(self, program_id):

            return None

        def resolve_part_instrument(self, part):

            return {
                "name": "Local"
            }

        def resolve_program_instrument(
            self,
            program_id
        ):

            return inherited

        def validate(self):

            return []

        def get_blocking_errors(self, errors):

            return []

        def snapshot(self):

            return {"before": True}

        def update_song_program(
            self,
            song_id,
            channel_id,
            program_id,
            remove_fields=None
        ):

            assert remove_fields == [
                "instrument"
            ]

            if not update_ok:

                return False, [
                    "remove error"
                ]

            return True, []

        def save_safe(
            self,
            allowed_errors=None
        ):

            return save_result

        def restore_snapshot(self, data):

            restored.append(data)

    responses = iter([
        "1",
        "4",
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(responses)
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_error_messages",
        lambda errors:
            errors_seen.extend(errors)
    )

    fusion_editor.edit_song(
        Project(),
        "song1"
    )

    output = capsys.readouterr().out

    if not update_ok:

        assert "Instrument local non supprimé." in output
        assert errors_seen == ["remove error"]

    elif not save_result:

        assert "Sauvegarde non effectuée." in output
        assert restored == [
            {"before": True}
        ]

    else:

        assert "Instrument local supprimé." in output

        if inherited:

            assert "Inherited" in output

        else:

            assert (
                "Instrument hérité : Non configuré"
                in output
            )


def test_manage_banks_empty(
    monkeypatch,
    capsys
):

    calls = []

    class Project:

        def get_banks(
            self,
            performance_type
        ):

            calls.append(
                performance_type
            )

            return []

    responses = iter([
        "1",
        "2",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.manage_banks(
        Project()
    )

    assert calls == [
        "program",
        "mix"
    ]

    output = capsys.readouterr().out

    assert "Banques PROGRAM" in output
    assert "Banques MIX" in output
    assert output.count(
        "Aucune banque."
    ) == 2


def test_manage_banks_validation_and_keep(
    monkeypatch,
    capsys
):

    class Project:

        def get_banks(
            self,
            performance_type
        ):

            return [
                0,
                8
            ]

        def get_bank_name(
            self,
            performance_type,
            bank
        ):

            return {
                0: "PRESET",
                8: "USER"
            }.get(
                bank,
                f"Bank {bank}"
            )

        def get_custom_bank_name(
            self,
            performance_type,
            bank
        ):

            if bank == 8:

                return "Ma banque"

            return None

    responses = iter([
        "1",       # PROGRAM
        "bad",     # non numérique
        "-1",      # < 0
        "128",     # > 127
        "0",       # banque valide
        "",        # conserver
        "8",       # banque avec nom custom
        "",        # conserver
        "q",       # retour banques
        "q"        # retour menu principal
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.manage_banks(
        Project()
    )

    output = capsys.readouterr().out

    assert " 0 - PRESET" in output
    assert " 8 - USER" in output

    assert "Banque invalide." in output

    assert output.count(
        "Banque invalide (0-127)."
    ) == 2

    assert "Nom effectif     : PRESET" in output
    assert "Nom effectif     : USER" in output

    assert "Nom personnalisé : -" in output
    assert "Nom personnalisé : Ma banque" in output


def test_manage_banks_set_and_remove_name(
    monkeypatch,
    capsys
):

    set_calls = []
    save_calls = []

    class Project:

        def get_banks(
            self,
            performance_type
        ):

            return [8]

        def get_bank_name(
            self,
            performance_type,
            bank
        ):

            return "USER"

        def get_custom_bank_name(
            self,
            performance_type,
            bank
        ):

            return None

        def validate(self):

            return [
                "existing"
            ]

        def get_blocking_errors(
            self,
            errors
        ):

            assert errors == [
                "existing"
            ]

            return [
                "blocking"
            ]

        def set_bank_name(
            self,
            performance_type,
            bank,
            name
        ):

            set_calls.append(
                (
                    performance_type,
                    bank,
                    name
                )
            )

            return True, []

        def save_safe(
            self,
            allowed_errors=None
        ):

            save_calls.append(
                allowed_errors
            )

            return True

    responses = iter([
        "2",          # MIX
        "8",
        "Custom",
        "8",
        "-",
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.manage_banks(
        Project()
    )

    assert set_calls == [
        (
            "mix",
            8,
            "Custom"
        ),
        (
            "mix",
            8,
            None
        )
    ]

    assert save_calls == [
        ["blocking"],
        ["blocking"]
    ]

    output = capsys.readouterr().out

    assert output.count(
        "Nom de banque enregistré."
    ) == 2


def test_manage_banks_set_name_failure(
    monkeypatch,
    capsys
):

    errors_seen = []

    class Project:

        def get_banks(
            self,
            performance_type
        ):

            return [8]

        def get_bank_name(
            self,
            performance_type,
            bank
        ):

            return "USER"

        def get_custom_bank_name(
            self,
            performance_type,
            bank
        ):

            return None

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def set_bank_name(
            self,
            performance_type,
            bank,
            name
        ):

            return (
                False,
                ["invalid name"]
            )

    responses = iter([
        "1",
        "8",
        "Custom",
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_error_messages",
        lambda messages:
            errors_seen.extend(
                messages
            )
    )

    fusion_editor.manage_banks(
        Project()
    )

    assert errors_seen == [
        "invalid name"
    ]

    assert (
        "Modification refusée :"
        in capsys.readouterr().out
    )


def test_print_project_summary(
    capsys
):

    class Project:

        def get_project_diagnostic_summary(
            self
        ):

            return {
                "instruments": {
                    "total": 10,
                    "ok": 7,
                    "unconfigured": 2,
                    "error": 1
                },
                "mixes": {
                    "total": 20,
                    "ok": 15,
                    "unconfigured": 3,
                    "error": 2
                },
                "programs": {
                    "total": 30,
                    "ok": 25,
                    "unconfigured": 4,
                    "error": 1
                },
                "songs": {
                    "total": 40,
                    "ok": 32,
                    "unconfigured": 5,
                    "error": 3
                }
            }

    fusion_editor.print_project_summary(
        Project()
    )

    output = capsys.readouterr().out

    assert "État du projet" in output

    assert (
        "INSTRUMENT :   10 | "
        "OK   7 | "
        "À configurer   2 | "
        "Erreurs   1"
        in output
    )

    assert (
        "MIX        :   20 | "
        "OK  15 | "
        "À configurer   3 | "
        "Erreurs   2"
        in output
    )

    assert (
        "PROGRAM    :   30 | "
        "OK  25 | "
        "À configurer   4 | "
        "Erreurs   1"
        in output
    )

    assert (
        "SONG       :   40 | "
        "OK  32 | "
        "À configurer   5 | "
        "Erreurs   3"
        in output
    )


def test_main_menu_routes(
    monkeypatch
):

    instrument_calls = []
    bank_calls = []
    summary_calls = []
    validation_calls = []

    project = object()

    monkeypatch.setattr(
        fusion_editor,
        "FusionProject",
        lambda: project
    )

    monkeypatch.setattr(
        fusion_editor,
        "validate_and_repair",
        lambda p:
            validation_calls.append(p)
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_project_summary",
        lambda p:
            summary_calls.append(p)
    )

    monkeypatch.setattr(
        fusion_editor,
        "instruments_menu",
        lambda p:
            instrument_calls.append(p)
    )

    monkeypatch.setattr(
        fusion_editor,
        "manage_banks",
        lambda p:
            bank_calls.append(p)
    )

    responses = iter([
        "1", "q",
        "2", "q",
        "3", "q",
        "4",
        "5",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.main()

    assert validation_calls == [
        project
    ]

    assert instrument_calls == [
        project
    ]

    assert bank_calls == [
        project
    ]

    # affiché à chaque passage dans le
    # menu principal
    assert len(summary_calls) == 6


def test_main_mixes_lists_empty(
    monkeypatch
):

    calls = []

    class Project:

        pass

    monkeypatch.setattr(
        fusion_editor,
        "FusionProject",
        Project
    )

    monkeypatch.setattr(
        fusion_editor,
        "validate_and_repair",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_project_summary",
        lambda project: None
    )

    def fake_list_mixes(
        project,
        status_filter=None
    ):

        calls.append(
            status_filter
        )

        if status_filter is None:

            return ["mix"]

        return []

    monkeypatch.setattr(
        fusion_editor,
        "list_mixes",
        fake_list_mixes
    )

    responses = iter([
        "1",       # main → MIX
        "1",       # liste complète
        "2",       # à configurer → vide
        "3",       # erreur → vide
        "q",       # retour
        "q"        # quitter
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.main()

    assert calls == [
        None,
        "unconfigured",
        "error"
    ]


def test_main_mixes_filtered_edit(
    monkeypatch
):

    edits = []
    choose_calls = []

    class Project:

        pass

    monkeypatch.setattr(
        fusion_editor,
        "FusionProject",
        Project
    )

    monkeypatch.setattr(
        fusion_editor,
        "validate_and_repair",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_project_summary",
        lambda project: None
    )

    counts = {
        "unconfigured": 0,
        "error": 0
    }

    def fake_list_mixes(
        project,
        status_filter=None
    ):

        counts[status_filter] += 1

        # unconfigured :
        # premier passage sélectionnable,
        # puis liste vide après édition
        if status_filter == "unconfigured":

            if counts[status_filter] == 1:

                return ["0:1"]

            return []

        # error reste disponible;
        # choose_mix_id retournera None
        return ["0:2"]

    def fake_choose_mix_id(
        project,
        allowed_ids=None
    ):

        choose_calls.append(
            allowed_ids
        )

        if allowed_ids == ["0:1"]:

            return "0:1"

        return None

    monkeypatch.setattr(
        fusion_editor,
        "list_mixes",
        fake_list_mixes
    )

    monkeypatch.setattr(
        fusion_editor,
        "choose_mix_id",
        fake_choose_mix_id
    )

    monkeypatch.setattr(
        fusion_editor,
        "edit_mix",
        lambda project, mix_id:
            edits.append(mix_id)
    )

    responses = iter([
        "1",       # main
        "2",       # unconfigured
        "3",       # error
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.main()

    assert edits == [
        "0:1"
    ]

    assert choose_calls == [
        ["0:1"],
        ["0:2"]
    ]


def test_main_mixes_direct_edit(
    monkeypatch
):

    edits = []

    class Project:

        pass

    monkeypatch.setattr(
        fusion_editor,
        "FusionProject",
        Project
    )

    monkeypatch.setattr(
        fusion_editor,
        "validate_and_repair",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_project_summary",
        lambda project: None
    )

    selections = iter([
        None,
        "0:1"
    ])

    monkeypatch.setattr(
        fusion_editor,
        "choose_mix_id",
        lambda project:
            next(selections)
    )

    monkeypatch.setattr(
        fusion_editor,
        "edit_mix",
        lambda project, mix_id:
            edits.append(mix_id)
    )

    responses = iter([
        "1",
        "4",       # annulation
        "4",       # édition
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.main()

    assert edits == [
        "0:1"
    ]


def test_main_delete_mix_cancel_and_unknown(
    monkeypatch,
    capsys
):

    class Project:

        def get_mix(self, mix_id):

            return None

    monkeypatch.setattr(
        fusion_editor,
        "FusionProject",
        Project
    )

    monkeypatch.setattr(
        fusion_editor,
        "validate_and_repair",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_project_summary",
        lambda project: None
    )

    selections = iter([
        None,
        "0:99"
    ])

    monkeypatch.setattr(
        fusion_editor,
        "choose_mix_id",
        lambda project:
            next(selections)
    )

    responses = iter([
        "1",
        "5",
        "5",
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.main()

    assert (
        "Mix inconnu."
        in capsys.readouterr().out
    )


def test_main_delete_mix_confirmation_cancel(
    monkeypatch,
    capsys
):

    class Project:

        def get_mix(self, mix_id):

            return {
                "name": "My Mix",
                "channels": {
                    "1": {}
                }
            }

    monkeypatch.setattr(
        fusion_editor,
        "FusionProject",
        Project
    )

    monkeypatch.setattr(
        fusion_editor,
        "validate_and_repair",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_project_summary",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "choose_mix_id",
        lambda project: "0:1"
    )

    responses = iter([
        "1",
        "5",
        "n",
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.main()

    output = capsys.readouterr().out

    assert "My Mix" in output
    assert "Canaux : 1" in output


def test_main_delete_mix_confirmation_cancel(
    monkeypatch,
    capsys
):

    class Project:

        def get_mix(self, mix_id):

            return {
                "name": "My Mix",
                "channels": {
                    "1": {}
                }
            }

    monkeypatch.setattr(
        fusion_editor,
        "FusionProject",
        Project
    )

    monkeypatch.setattr(
        fusion_editor,
        "validate_and_repair",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_project_summary",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "choose_mix_id",
        lambda project: "0:1"
    )

    responses = iter([
        "1",
        "5",
        "n",
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.main()

    output = capsys.readouterr().out

    assert "My Mix" in output
    assert "Canaux : 1" in output


def test_main_delete_empty_mixes_none(
    monkeypatch,
    capsys
):

    class Project:

        def iter_mixes(self):

            return iter([
                (
                    "0:1",
                    {
                        "channels": {
                            "1": {}
                        }
                    }
                )
            ])

    monkeypatch.setattr(
        fusion_editor,
        "FusionProject",
        Project
    )

    monkeypatch.setattr(
        fusion_editor,
        "validate_and_repair",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_project_summary",
        lambda project: None
    )

    responses = iter([
        "1",
        "6",
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.main()

    assert (
        "Aucun MIX vide."
        in capsys.readouterr().out
    )


def test_main_delete_empty_mixes_cancel(
    monkeypatch,
    capsys
):

    class Project:

        def iter_mixes(self):

            return iter([
                (
                    "0:1",
                    {
                        "channels": {}
                    }
                ),
                (
                    "0:2",
                    {}
                )
            ])

    monkeypatch.setattr(
        fusion_editor,
        "FusionProject",
        Project
    )

    monkeypatch.setattr(
        fusion_editor,
        "validate_and_repair",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_project_summary",
        lambda project: None
    )

    responses = iter([
        "1",
        "6",
        "n",
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.main()

    output = capsys.readouterr().out

    assert "MIX vides détectés :" in output
    assert "- 0:1" in output
    assert "- 0:2" in output


@pytest.mark.parametrize(
    "delete_result, save_result, expected",
    [
        (
            (True, []),
            True,
            "Aucun MIX vide."
        ),
        (
            (True, ["0:1", "0:2"]),
            True,
            "2 MIX supprimé(s)."
        ),
        (
            (False, []),
            True,
            "Sauvegarde non effectuée."
        )
    ]
)
def test_main_delete_empty_mixes_result(
    monkeypatch,
    capsys,
    delete_result,
    save_result,
    expected
):

    class Project:

        def iter_mixes(self):

            return iter([
                (
                    "0:1",
                    {
                        "channels": {}
                    }
                )
            ])

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def delete_empty_mixes(self):

            return delete_result

        def save_safe(
            self,
            allowed_errors=None
        ):

            return save_result

    monkeypatch.setattr(
        fusion_editor,
        "FusionProject",
        Project
    )

    monkeypatch.setattr(
        fusion_editor,
        "validate_and_repair",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_project_summary",
        lambda project: None
    )

    responses = iter([
        "1",
        "6",
        "o",
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.main()

    output = capsys.readouterr().out

    assert expected in output

    if delete_result[1]:

        assert "Sauvegarde effectuée." in output


def test_main_programs_list_and_direct_edit(
    monkeypatch
):

    edits = []
    selections = iter([
        None,
        "2:42"
    ])

    class Project:
        pass

    monkeypatch.setattr(
        fusion_editor,
        "FusionProject",
        Project
    )

    monkeypatch.setattr(
        fusion_editor,
        "validate_and_repair",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_project_summary",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "list_programs",
        lambda project, status_filter=None: []
    )

    monkeypatch.setattr(
        fusion_editor,
        "choose_program_id",
        lambda project, allowed_ids=None:
            next(selections)
    )

    monkeypatch.setattr(
        fusion_editor,
        "edit_program",
        lambda project, program_id:
            edits.append(program_id)
    )

    responses = iter([
        "2",
        "1",
        "4",
        "4",
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(responses)
    )

    fusion_editor.main()

    assert edits == [
        "2:42"
    ]


def test_main_programs_filtered(
    monkeypatch
):

    edits = []
    calls = []

    class Project:
        pass

    monkeypatch.setattr(
        fusion_editor,
        "FusionProject",
        Project
    )

    monkeypatch.setattr(
        fusion_editor,
        "validate_and_repair",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_project_summary",
        lambda project: None
    )

    counts = {
        "unconfigured": 0,
        "error": 0
    }

    def fake_list_programs(
        project,
        status_filter=None
    ):

        counts[status_filter] += 1

        if status_filter == "unconfigured":

            return ["2:10"]

        if counts["error"] == 1:

            return ["2:20"]

        return []

    def fake_choose_program_id(
        project,
        allowed_ids=None
    ):

        calls.append(
            allowed_ids
        )

        if allowed_ids == ["2:10"]:

            return None

        return "2:20"

    monkeypatch.setattr(
        fusion_editor,
        "list_programs",
        fake_list_programs
    )

    monkeypatch.setattr(
        fusion_editor,
        "choose_program_id",
        fake_choose_program_id
    )

    monkeypatch.setattr(
        fusion_editor,
        "edit_program",
        lambda project, program_id:
            edits.append(program_id)
    )

    responses = iter([
        "2",
        "2",
        "3",
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(responses)
    )

    fusion_editor.main()

    assert calls == [
        ["2:10"],
        ["2:20"]
    ]

    assert edits == [
        "2:20"
    ]


def test_main_rename_program_early_returns(
    monkeypatch,
    capsys
):

    class Project:

        def get_program(
            self,
            program_id
        ):

            if program_id == "2:99":

                return None

            return {
                "name": "Old name"
            }

    selections = iter([
        None,
        "2:99",
        "2:42"
    ])

    monkeypatch.setattr(
        fusion_editor,
        "FusionProject",
        Project
    )

    monkeypatch.setattr(
        fusion_editor,
        "validate_and_repair",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_project_summary",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "choose_program_id",
        lambda project:
            next(selections)
    )

    responses = iter([
        "2",
        "5",
        "5",
        "5",
        "",       # nouveau nom vide
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(responses)
    )

    fusion_editor.main()

    output = capsys.readouterr().out

    assert "PROGRAM inconnu." in output
    assert "Nom actuel : Old name" in output


@pytest.mark.parametrize(
    "rename_ok, save_ok, expected",
    [
        (
            False,
            True,
            "Renommage refusé."
        ),
        (
            True,
            True,
            "PROGRAM renommé."
        ),
        (
            True,
            False,
            "Sauvegarde non effectuée."
        )
    ]
)
def test_main_rename_program_result(
    monkeypatch,
    capsys,
    rename_ok,
    save_ok,
    expected
):

    restored = []
    errors_seen = []

    class Project:

        def get_program(
            self,
            program_id
        ):

            return {
                "name": "Old"
            }

        def validate(self):

            return ["existing"]

        def get_blocking_errors(
            self,
            errors
        ):

            return ["allowed"]

        def snapshot(self):

            return {
                "snapshot": True
            }

        def rename_program(
            self,
            program_id,
            name
        ):

            if rename_ok:

                return True, []

            return False, [
                "rename error"
            ]

        def save_safe(
            self,
            allowed_errors=None
        ):

            assert allowed_errors == [
                "allowed"
            ]

            return save_ok

        def restore_snapshot(
            self,
            snapshot
        ):

            restored.append(
                snapshot
            )

    monkeypatch.setattr(
        fusion_editor,
        "FusionProject",
        Project
    )

    monkeypatch.setattr(
        fusion_editor,
        "validate_and_repair",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_project_summary",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "choose_program_id",
        lambda project: "2:42"
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_error_messages",
        lambda errors:
            errors_seen.extend(errors)
    )

    responses = iter([
        "2",
        "5",
        "New name",
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(responses)
    )

    fusion_editor.main()

    assert expected in capsys.readouterr().out

    if not rename_ok:

        assert errors_seen == [
            "rename error"
        ]

    elif not save_ok:

        assert restored == [
            {
                "snapshot": True
            }
        ]


def test_main_delete_program_early_returns(
    monkeypatch,
    capsys
):

    class Project:

        def get_program(
            self,
            program_id
        ):

            if program_id == "2:99":

                return None

            return {
                "name": "My Program",
                "parts": {
                    "1": {},
                    "2": {}
                }
            }

    selections = iter([
        None,
        "2:99",
        "2:42"
    ])

    monkeypatch.setattr(
        fusion_editor,
        "FusionProject",
        Project
    )

    monkeypatch.setattr(
        fusion_editor,
        "validate_and_repair",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_project_summary",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "choose_program_id",
        lambda project:
            next(selections)
    )

    responses = iter([
        "2",
        "6",
        "6",
        "6",
        "n",
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(responses)
    )

    fusion_editor.main()

    output = capsys.readouterr().out

    assert "PROGRAM inconnu." in output
    assert "My Program" in output
    assert "PARTS : 2" in output


@pytest.mark.parametrize(
    "delete_ok, save_ok, expected",
    [
        (
            False,
            True,
            "Suppression refusée."
        ),
        (
            True,
            True,
            "PROGRAM supprimé."
        ),
        (
            True,
            False,
            "Sauvegarde non effectuée."
        )
    ]
)
def test_main_delete_program_result(
    monkeypatch,
    capsys,
    delete_ok,
    save_ok,
    expected
):

    errors_seen = []

    class Project:

        def get_program(
            self,
            program_id
        ):

            return {
                "name": "My Program",
                "parts": {}
            }

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def delete_program(
            self,
            program_id
        ):

            if delete_ok:

                return True, []

            return False, [
                "delete error"
            ]

        def save_safe(
            self,
            allowed_errors=None
        ):

            return save_ok

    monkeypatch.setattr(
        fusion_editor,
        "FusionProject",
        Project
    )

    monkeypatch.setattr(
        fusion_editor,
        "validate_and_repair",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_project_summary",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "choose_program_id",
        lambda project: "2:42"
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_error_messages",
        lambda errors:
            errors_seen.extend(errors)
    )

    responses = iter([
        "2",
        "6",
        "o",
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(responses)
    )

    fusion_editor.main()

    assert expected in capsys.readouterr().out

    if not delete_ok:

        assert errors_seen == [
            "delete error"
        ]


def test_main_songs_list_and_direct_edit(
    monkeypatch
):

    edits = []
    selections = iter([
        None,
        "song1"
    ])

    class Project:
        pass

    monkeypatch.setattr(
        fusion_editor,
        "FusionProject",
        Project
    )

    monkeypatch.setattr(
        fusion_editor,
        "validate_and_repair",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_project_summary",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "list_songs",
        lambda project, status_filter=None: []
    )

    monkeypatch.setattr(
        fusion_editor,
        "choose_song_id",
        lambda project, allowed_ids=None:
            next(selections)
    )

    monkeypatch.setattr(
        fusion_editor,
        "edit_song",
        lambda project, song_id:
            edits.append(song_id)
    )

    responses = iter([
        "3",
        "1",
        "4",
        "4",
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.main()

    assert edits == [
        "song1"
    ]


def test_main_songs_filtered(
    monkeypatch
):

    edits = []
    choose_calls = []

    class Project:
        pass

    monkeypatch.setattr(
        fusion_editor,
        "FusionProject",
        Project
    )

    monkeypatch.setattr(
        fusion_editor,
        "validate_and_repair",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_project_summary",
        lambda project: None
    )

    counts = {
        "unconfigured": 0,
        "error": 0
    }

    def fake_list_songs(
        project,
        status_filter=None
    ):

        counts[status_filter] += 1

        if status_filter == "unconfigured":

            return ["song1"]

        if counts["error"] == 1:

            return ["song2"]

        return []

    def fake_choose_song_id(
        project,
        allowed_ids=None
    ):

        choose_calls.append(
            allowed_ids
        )

        if allowed_ids == ["song1"]:

            return None

        return "song2"

    monkeypatch.setattr(
        fusion_editor,
        "list_songs",
        fake_list_songs
    )

    monkeypatch.setattr(
        fusion_editor,
        "choose_song_id",
        fake_choose_song_id
    )

    monkeypatch.setattr(
        fusion_editor,
        "edit_song",
        lambda project, song_id:
            edits.append(song_id)
    )

    responses = iter([
        "3",
        "2",
        "3",
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.main()

    assert choose_calls == [
        ["song1"],
        ["song2"]
    ]

    assert edits == [
        "song2"
    ]


def test_main_rename_song_early_returns(
    monkeypatch,
    capsys
):

    class Project:

        def get_song(
            self,
            song_id
        ):

            if song_id == "unknown":

                return None

            return {
                "name": "Old Song"
            }

    selections = iter([
        None,
        "unknown",
        "song1"
    ])

    monkeypatch.setattr(
        fusion_editor,
        "FusionProject",
        Project
    )

    monkeypatch.setattr(
        fusion_editor,
        "validate_and_repair",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_project_summary",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "choose_song_id",
        lambda project:
            next(selections)
    )

    responses = iter([
        "3",
        "5",
        "5",
        "5",
        "",
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.main()

    output = capsys.readouterr().out

    assert "SONG inconnue." in output
    assert "Nom actuel : Old Song" in output


@pytest.mark.parametrize(
    "rename_ok, expected",
    [
        (
            False,
            "Renommage refusé."
        ),
        (
            True,
            "SONG renommée."
        )
    ]
)
def test_main_rename_song_result(
    monkeypatch,
    capsys,
    rename_ok,
    expected
):

    errors_seen = []

    class Project:

        def get_song(
            self,
            song_id
        ):

            return {
                "name": "Old Song"
            }

        def validate(self):

            return ["existing"]

        def get_blocking_errors(
            self,
            errors
        ):

            return ["allowed"]

        def rename_song(
            self,
            song_id,
            new_name
        ):

            if rename_ok:

                return True, []

            return False, [
                "rename error"
            ]

        def save_safe(
            self,
            allowed_errors=None
        ):

            assert allowed_errors == [
                "allowed"
            ]

            return True

    monkeypatch.setattr(
        fusion_editor,
        "FusionProject",
        Project
    )

    monkeypatch.setattr(
        fusion_editor,
        "validate_and_repair",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_project_summary",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "choose_song_id",
        lambda project: "song1"
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_error_messages",
        lambda errors:
            errors_seen.extend(errors)
    )

    responses = iter([
        "3",
        "5",
        "New Song",
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.main()

    assert expected in capsys.readouterr().out

    if not rename_ok:

        assert errors_seen == [
            "rename error"
        ]


def test_main_delete_song_early_returns(
    monkeypatch,
    capsys
):

    class Project:

        def get_song(
            self,
            song_id
        ):

            if song_id == "unknown":

                return None

            return {
                "name": "My Song",
                "channels": {
                    "1": {},
                    "2": {}
                }
            }

    selections = iter([
        None,
        "unknown",
        "song1"
    ])

    monkeypatch.setattr(
        fusion_editor,
        "FusionProject",
        Project
    )

    monkeypatch.setattr(
        fusion_editor,
        "validate_and_repair",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_project_summary",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "choose_song_id",
        lambda project:
            next(selections)
    )

    responses = iter([
        "3",
        "6",
        "6",
        "6",
        "n",
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.main()

    output = capsys.readouterr().out

    assert "SONG inconnue." in output
    assert "My Song" in output
    assert "Canaux : 2" in output


@pytest.mark.parametrize(
    "delete_ok, expected",
    [
        (
            False,
            "Suppression refusée."
        ),
        (
            True,
            "SONG supprimée."
        )
    ]
)
def test_main_delete_song_result(
    monkeypatch,
    capsys,
    delete_ok,
    expected
):

    errors_seen = []

    class Project:

        def get_song(
            self,
            song_id
        ):

            return {
                "name": "My Song",
                "channels": {}
            }

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def delete_song(
            self,
            song_id
        ):

            if delete_ok:

                return True, []

            return False, [
                "delete error"
            ]

        def save_safe(
            self,
            allowed_errors=None
        ):

            return True

    monkeypatch.setattr(
        fusion_editor,
        "FusionProject",
        Project
    )

    monkeypatch.setattr(
        fusion_editor,
        "validate_and_repair",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_project_summary",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "choose_song_id",
        lambda project: "song1"
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_error_messages",
        lambda errors:
            errors_seen.extend(errors)
    )

    responses = iter([
        "3",
        "6",
        "o",
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.main()

    assert expected in capsys.readouterr().out

    if not delete_ok:

        assert errors_seen == [
            "delete error"
        ]


def test_main_delete_mix_success(
    monkeypatch,
    capsys
):

    class Project:

        def get_mix(
            self,
            mix_id
        ):

            return {
                "name": "My Mix",
                "channels": {}
            }

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def delete_mix(
            self,
            mix_id
        ):

            assert mix_id == "0:1"

            return True, []

        def save_safe(
            self,
            allowed_errors=None
        ):

            assert allowed_errors == []

            return True

    monkeypatch.setattr(
        fusion_editor,
        "FusionProject",
        Project
    )

    monkeypatch.setattr(
        fusion_editor,
        "validate_and_repair",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_project_summary",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "choose_mix_id",
        lambda project: "0:1"
    )

    responses = iter([
        "1",
        "5",
        "o",
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.main()

    assert (
        "MIX supprimé."
        in capsys.readouterr().out
    )


def test_main_remaining_mix_program_branches(
    monkeypatch
):

    mix_edits = []
    program_edits = []

    class Project:
        pass

    monkeypatch.setattr(
        fusion_editor,
        "FusionProject",
        Project
    )

    monkeypatch.setattr(
        fusion_editor,
        "validate_and_repair",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_project_summary",
        lambda project: None
    )

    #
    # MIX
    #

    mix_counts = {
        "error": 0
    }

    def fake_list_mixes(
        project,
        status_filter=None
    ):

        if status_filter == "unconfigured":

            return ["0:1"]

        if status_filter == "error":

            mix_counts["error"] += 1

            if mix_counts["error"] == 1:

                return ["0:2"]

            return []

        return []

    def fake_choose_mix_id(
        project,
        allowed_ids=None
    ):

        if allowed_ids == ["0:1"]:

            return None

        return "0:2"

    monkeypatch.setattr(
        fusion_editor,
        "list_mixes",
        fake_list_mixes
    )

    monkeypatch.setattr(
        fusion_editor,
        "choose_mix_id",
        fake_choose_mix_id
    )

    monkeypatch.setattr(
        fusion_editor,
        "edit_mix",
        lambda project, mix_id:
            mix_edits.append(mix_id)
    )

    #
    # PROGRAM
    #

    program_counts = {
        "unconfigured": 0
    }

    def fake_list_programs(
        project,
        status_filter=None
    ):

        if status_filter == "unconfigured":

            program_counts["unconfigured"] += 1

            if (
                program_counts["unconfigured"]
                == 1
            ):

                return ["2:10"]

            return []

        if status_filter == "error":

            return ["2:20"]

        return []

    def fake_choose_program_id(
        project,
        allowed_ids=None
    ):

        if allowed_ids == ["2:20"]:

            return None

        return "2:10"

    monkeypatch.setattr(
        fusion_editor,
        "list_programs",
        fake_list_programs
    )

    monkeypatch.setattr(
        fusion_editor,
        "choose_program_id",
        fake_choose_program_id
    )

    monkeypatch.setattr(
        fusion_editor,
        "edit_program",
        lambda project, program_id:
            program_edits.append(
                program_id
            )
    )

    responses = iter([
        "1",       # main → MIX
        "2",       # unconfigured → None
        "3",       # error → edit 0:2
        "q",

        "2",       # main → PROGRAM
        "2",       # unconfigured → edit,
                   # puis liste vide
        "3",       # error → None
        "q",

        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.main()

    assert mix_edits == [
        "0:2"
    ]

    assert program_edits == [
        "2:10"
    ]


def test_main_remaining_song_branches(
    monkeypatch
):

    edits = []

    class Project:
        pass

    monkeypatch.setattr(
        fusion_editor,
        "FusionProject",
        Project
    )

    monkeypatch.setattr(
        fusion_editor,
        "validate_and_repair",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_project_summary",
        lambda project: None
    )

    counts = {
        "unconfigured": 0
    }

    def fake_list_songs(
        project,
        status_filter=None
    ):

        if status_filter == "unconfigured":

            counts["unconfigured"] += 1

            if counts["unconfigured"] == 1:

                return ["song1"]

            return []

        if status_filter == "error":

            return ["song2"]

        return []

    def fake_choose_song_id(
        project,
        allowed_ids=None
    ):

        if allowed_ids == ["song2"]:

            return None

        return "song1"

    monkeypatch.setattr(
        fusion_editor,
        "list_songs",
        fake_list_songs
    )

    monkeypatch.setattr(
        fusion_editor,
        "choose_song_id",
        fake_choose_song_id
    )

    monkeypatch.setattr(
        fusion_editor,
        "edit_song",
        lambda project, song_id:
            edits.append(song_id)
    )

    responses = iter([
        "3",
        "2",
        "3",
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.main()

    assert edits == [
        "song1"
    ]


def test_main_delete_mix_failure(
    monkeypatch,
    capsys
):

    errors_seen = []

    class Project:

        def get_mix(
            self,
            mix_id
        ):

            return {
                "name": "My Mix",
                "channels": {}
            }

        def validate(self):

            return []

        def get_blocking_errors(
            self,
            errors
        ):

            return []

        def delete_mix(
            self,
            mix_id
        ):

            assert mix_id == "0:1"

            return (
                False,
                ["delete error"]
            )

    monkeypatch.setattr(
        fusion_editor,
        "FusionProject",
        Project
    )

    monkeypatch.setattr(
        fusion_editor,
        "validate_and_repair",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_project_summary",
        lambda project: None
    )

    monkeypatch.setattr(
        fusion_editor,
        "choose_mix_id",
        lambda project: "0:1"
    )

    monkeypatch.setattr(
        fusion_editor,
        "print_error_messages",
        lambda errors:
            errors_seen.extend(errors)
    )

    responses = iter([
        "1",
        "5",
        "o",
        "q",
        "q"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt:
            next(responses)
    )

    fusion_editor.main()

    assert (
        "Suppression refusée."
        in capsys.readouterr().out
    )

    assert errors_seen == [
        "delete error"
    ]
