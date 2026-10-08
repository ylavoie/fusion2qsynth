import pytest

import fusion_controller


class DummyPort:

    def __enter__(self):

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback
    ):

        return False


def test_choose_controller_mode_program(
    monkeypatch
):

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": "1"
    )

    assert (
        fusion_controller.choose_controller_mode()
        == "program"
    )


def test_choose_controller_mode_mix(
    monkeypatch
):

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": "2"
    )

    assert (
        fusion_controller.choose_controller_mode()
        == "mix"
    )


def test_choose_controller_mode_song(
    monkeypatch
):

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": "3"
    )

    assert (
        fusion_controller.choose_controller_mode()
        == "song"
    )


def test_choose_controller_mode_quit(
    monkeypatch
):

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": "Q"
    )

    assert (
        fusion_controller.choose_controller_mode()
        is None
    )


def test_choose_controller_mode_invalid_then_program(
    monkeypatch,
    capsys
):

    answers = iter(
        [
            "x",
            "1"
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": next(
            answers
        )
    )

    assert (
        fusion_controller.choose_controller_mode()
        == "program"
    )

    output = capsys.readouterr().out

    assert (
        "Choix invalide."
        in output
    )


def test_choose_song_without_songs(
    project,
    capsys
):

    result = fusion_controller.choose_song(
        project
    )

    assert result is None

    output = capsys.readouterr().out

    assert (
        "Aucune SONG enregistrée."
        in output
    )


def test_choose_song_selects_song(
    project,
    monkeypatch
):

    project.data["songs"] = {
        "Song A": {
            "name": "Première SONG",
            "channels": {}
        },
        "Song B": {
            "name": "Deuxième SONG",
            "channels": {}
        }
    }

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": "2"
    )

    result = fusion_controller.choose_song(
        project
    )

    assert result == "Song B"


def test_choose_song_quit(
    project,
    monkeypatch
):

    project.data["songs"] = {
        "Song A": {
            "name": "Première SONG",
            "channels": {}
        }
    }

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": "q"
    )

    assert (
        fusion_controller.choose_song(
            project
        )
        is None
    )


def test_choose_song_invalid_number_then_valid(
    project,
    monkeypatch,
    capsys
):

    project.data["songs"] = {
        "Song A": {
            "name": "Première SONG",
            "channels": {}
        }
    }

    answers = iter(
        [
            "99",
            "1"
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": next(
            answers
        )
    )

    result = fusion_controller.choose_song(
        project
    )

    assert result == "Song A"

    output = capsys.readouterr().out

    assert (
        "Choix invalide."
        in output
    )


def test_choose_song_invalid_text_then_valid(
    project,
    monkeypatch,
    capsys
):

    project.data["songs"] = {
        "Song A": {
            "name": "Première SONG",
            "channels": {}
        }
    }

    answers = iter(
        [
            "x",
            "1"
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": next(
            answers
        )
    )

    result = fusion_controller.choose_song(
        project
    )

    assert result == "Song A"

    output = capsys.readouterr().out

    assert (
        "Choix invalide."
        in output
    )


def test_print_mode_diagnostic_program(
    project,
    monkeypatch,
    capsys
):

    monkeypatch.setattr(
        project,
        "get_program_diagnostic",
        lambda: [
            {
                "program": "0:1",
                "name": "Piano",
                "fusion_valid": True,
                "soundfont_configured": True,
                "errors": []
            },
            {
                "program": "0:2",
                "name": "Strings",
                "fusion_valid": False,
                "soundfont_configured": False,
                "errors": ["erreur"]
            }
        ]
    )

    monkeypatch.setattr(
        project,
        "count_programs",
        lambda: 2
    )

    fusion_controller.print_mode_diagnostic(
        project,
        "program"
    )

    output = capsys.readouterr().out

    assert "PROGRAM : 0:1 - Piano" in output
    assert "PROGRAM : 0:2 - Strings" in output
    assert "Fusion: OK" in output
    assert "Fusion: ERREUR" in output
    assert "SoundFont: OK" in output
    assert "SoundFont: Non configuré" in output
    assert "2 PROGRAM enregistrés" in output


def test_print_mode_diagnostic_mix(
    project,
    monkeypatch,
    capsys
):

    monkeypatch.setattr(
        project,
        "get_mix_diagnostic",
        lambda: [
            {
                "mix": "0:10",
                "name": "Test Mix",
                "fusion_valid": True,
                "channels": [
                    {
                        "channel": "1",
                        "fusion_valid": True,
                        "soundfont_configured": True
                    },
                    {
                        "channel": "2",
                        "fusion_valid": False,
                        "soundfont_configured": False
                    }
                ]
            }
        ]
    )

    monkeypatch.setattr(
        project,
        "count_mixes",
        lambda: 1
    )

    fusion_controller.print_mode_diagnostic(
        project,
        "mix"
    )

    output = capsys.readouterr().out

    assert "Mix : 0:10 - Test Mix" in output
    assert "CH 1 Fusion: OK SoundFont: OK" in output
    assert (
        "CH 2 Fusion: ERREUR "
        "SoundFont: Non configuré"
        in output
    )
    assert "1 Mix chargés" in output


def test_print_mode_diagnostic_song_with_name(
    project,
    monkeypatch,
    capsys
):

    monkeypatch.setattr(
        project,
        "get_song_diagnostic",
        lambda: [
            {
                "song": "Song 1",
                "name": "Ma chanson",
                "fusion_valid": True,
                "channels": [
                    {
                        "channel": "2",
                        "fusion_valid": False,
                        "soundfont_configured": False
                    },
                    {
                        "channel": "1",
                        "fusion_valid": True,
                        "soundfont_configured": True
                    }
                ]
            }
        ]
    )

    monkeypatch.setattr(
        project,
        "count_songs",
        lambda: 1
    )

    fusion_controller.print_mode_diagnostic(
        project,
        "song"
    )

    output = capsys.readouterr().out

    assert "SONG : Song 1 - Ma chanson" in output
    assert "CH 1 Fusion: OK SoundFont: OK" in output
    assert (
        "CH 2 Fusion: ERREUR "
        "SoundFont: Non configuré"
        in output
    )
    assert (
        output.index("CH 1")
        < output.index("CH 2")
    )
    assert "1 SONG enregistrées" in output


def test_print_mode_diagnostic_song_without_distinct_name(
    project,
    monkeypatch,
    capsys
):

    monkeypatch.setattr(
        project,
        "get_song_diagnostic",
        lambda: [
            {
                "song": "Song 1",
                "name": "Song 1",
                "fusion_valid": True,
                "channels": []
            }
        ]
    )

    monkeypatch.setattr(
        project,
        "count_songs",
        lambda: 1
    )

    fusion_controller.print_mode_diagnostic(
        project,
        "song"
    )

    output = capsys.readouterr().out

    assert "SONG : Song 1" in output
    assert "SONG : Song 1 -" not in output


def test_main_rejects_missing_fusion_port(
    monkeypatch
):

    class DummyProject:

        def validate(self):
            return []

    monkeypatch.setattr(
        fusion_controller,
        "FusionProject",
        DummyProject
    )

    monkeypatch.setattr(
        fusion_controller,
        "find_fusion_input",
        lambda: None
    )

    with pytest.raises(
        Exception,
        match="Fusion MIDI introuvable"
    ):

        fusion_controller.main()


def test_main_rejects_missing_fluidsynth_port(
    monkeypatch
):

    class DummyProject:

        def validate(self):
            return []

    monkeypatch.setattr(
        fusion_controller,
        "FusionProject",
        DummyProject
    )

    monkeypatch.setattr(
        fusion_controller,
        "find_fusion_input",
        lambda: "Fusion MIDI"
    )

    monkeypatch.setattr(
        fusion_controller,
        "find_fluidsynth_output",
        lambda: None
    )

    with pytest.raises(
        Exception,
        match="FluidSynth MIDI introuvable"
    ):

        fusion_controller.main()


def test_main_displays_validation_errors_and_can_exit(
    monkeypatch
):

    project = object()

    class DummyProject:

        def validate(self):

            return [
                "Erreur test"
            ]

    validation_calls = []

    monkeypatch.setattr(
        fusion_controller,
        "FusionProject",
        DummyProject
    )

    monkeypatch.setattr(
        fusion_controller,
        "print_validation_errors",
        lambda project, errors, title=None:
            validation_calls.append(
                (
                    errors,
                    title
                )
            )
    )

    monkeypatch.setattr(
        fusion_controller,
        "find_fusion_input",
        lambda: "Fusion MIDI"
    )

    monkeypatch.setattr(
        fusion_controller,
        "find_fluidsynth_output",
        lambda: "FluidSynth MIDI"
    )

    monkeypatch.setattr(
        fusion_controller.mido,
        "open_input",
        lambda port: DummyPort()
    )

    monkeypatch.setattr(
        fusion_controller.mido,
        "open_output",
        lambda port: DummyPort()
    )

    monkeypatch.setattr(
        fusion_controller,
        "choose_controller_mode",
        lambda: None
    )

    fusion_controller.main()

    assert validation_calls == [
        (
            ["Erreur test"],
            "AVERTISSEMENTS CONFIGURATION"
        )
    ]


def test_main_opens_midi_ports_and_can_exit(
    monkeypatch,
    capsys
):

    class DummyProject:

        def validate(self):
            return []

    opened = []

    monkeypatch.setattr(
        fusion_controller,
        "FusionProject",
        DummyProject
    )

    monkeypatch.setattr(
        fusion_controller,
        "find_fusion_input",
        lambda: "Fusion Port"
    )

    monkeypatch.setattr(
        fusion_controller,
        "find_fluidsynth_output",
        lambda: "Synth Port"
    )

    def open_input(port):

        opened.append(
            (
                "input",
                port
            )
        )

        return DummyPort()

    def open_output(port):

        opened.append(
            (
                "output",
                port
            )
        )

        return DummyPort()

    monkeypatch.setattr(
        fusion_controller.mido,
        "open_input",
        open_input
    )

    monkeypatch.setattr(
        fusion_controller.mido,
        "open_output",
        open_output
    )

    monkeypatch.setattr(
        fusion_controller,
        "choose_controller_mode",
        lambda: None
    )

    fusion_controller.main()

    assert opened == [
        (
            "input",
            "Fusion Port"
        ),
        (
            "output",
            "Synth Port"
        )
    ]

    output = capsys.readouterr().out

    assert "Fusion : Fusion Port" in output
    assert "Synth : Synth Port" in output


def test_main_program_without_last_performance(
    monkeypatch
):

    class DummyProject:

        def validate(self):
            return []

    monkeypatch.setattr(
        fusion_controller,
        "FusionProject",
        DummyProject
    )

    monkeypatch.setattr(
        fusion_controller,
        "find_fusion_input",
        lambda: "Fusion MIDI"
    )

    monkeypatch.setattr(
        fusion_controller,
        "find_fluidsynth_output",
        lambda: "FluidSynth MIDI"
    )

    monkeypatch.setattr(
        fusion_controller.mido,
        "open_input",
        lambda port: DummyPort()
    )

    monkeypatch.setattr(
        fusion_controller.mido,
        "open_output",
        lambda port: DummyPort()
    )

    choices = iter(
        [
            "program",
            None
        ]
    )

    monkeypatch.setattr(
        fusion_controller,
        "choose_controller_mode",
        lambda: next(choices)
    )

    diagnostics = []

    monkeypatch.setattr(
        fusion_controller,
        "print_mode_diagnostic",
        lambda project, mode:
            diagnostics.append(mode)
    )

    monkeypatch.setattr(
        fusion_controller,
        "load_last_performance",
        lambda mode: None
    )

    loops = []

    monkeypatch.setattr(
        fusion_controller,
        "run_controller_loop",
        lambda inp, out, project, mode:
            loops.append(mode)
    )

    fusion_controller.main()

    assert diagnostics == [
        "program"
    ]

    assert loops == [
        "program"
    ]


def test_main_program_resumes_last_performance(
    monkeypatch
):

    class DummyProject:

        def validate(self):
            return []

    monkeypatch.setattr(
        fusion_controller,
        "FusionProject",
        DummyProject
    )

    monkeypatch.setattr(
        fusion_controller,
        "find_fusion_input",
        lambda: "Fusion MIDI"
    )

    monkeypatch.setattr(
        fusion_controller,
        "find_fluidsynth_output",
        lambda: "FluidSynth MIDI"
    )

    monkeypatch.setattr(
        fusion_controller.mido,
        "open_input",
        lambda port: DummyPort()
    )

    monkeypatch.setattr(
        fusion_controller.mido,
        "open_output",
        lambda port: DummyPort()
    )

    choices = iter(
        [
            "program",
            None
        ]
    )

    monkeypatch.setattr(
        fusion_controller,
        "choose_controller_mode",
        lambda: next(choices)
    )

    monkeypatch.setattr(
        fusion_controller,
        "print_mode_diagnostic",
        lambda project, mode: None
    )

    monkeypatch.setattr(
        fusion_controller,
        "load_last_performance",
        lambda mode: "0:12"
    )

    loaded = []

    monkeypatch.setattr(
        fusion_controller,
        "load_program",
        lambda program_id, out, project:
            loaded.append(program_id)
    )

    monkeypatch.setattr(
        fusion_controller,
        "run_controller_loop",
        lambda inp, out, project, mode: None
    )

    fusion_controller.main()

    assert loaded == [
        "0:12"
    ]


def test_main_program_keyboard_interrupt_returns_to_controller(
    monkeypatch,
    capsys
):

    class DummyProject:

        def validate(self):
            return []

    monkeypatch.setattr(
        fusion_controller,
        "FusionProject",
        DummyProject
    )

    monkeypatch.setattr(
        fusion_controller,
        "find_fusion_input",
        lambda: "Fusion MIDI"
    )

    monkeypatch.setattr(
        fusion_controller,
        "find_fluidsynth_output",
        lambda: "FluidSynth MIDI"
    )

    monkeypatch.setattr(
        fusion_controller.mido,
        "open_input",
        lambda port: DummyPort()
    )

    monkeypatch.setattr(
        fusion_controller.mido,
        "open_output",
        lambda port: DummyPort()
    )

    choices = iter(
        [
            "program",
            None
        ]
    )

    monkeypatch.setattr(
        fusion_controller,
        "choose_controller_mode",
        lambda: next(choices)
    )

    monkeypatch.setattr(
        fusion_controller,
        "print_mode_diagnostic",
        lambda project, mode: None
    )

    monkeypatch.setattr(
        fusion_controller,
        "load_last_performance",
        lambda mode: None
    )

    def interrupt(
        inp,
        out,
        project,
        mode
    ):

        raise KeyboardInterrupt

    monkeypatch.setattr(
        fusion_controller,
        "run_controller_loop",
        interrupt
    )

    fusion_controller.main()

    output = capsys.readouterr().out

    assert (
        "Retour au Contrôleur Live"
        in output
    )


def test_main_mix_without_last_performance(
    monkeypatch
):

    class DummyProject:

        def validate(self):
            return []

    monkeypatch.setattr(
        fusion_controller,
        "FusionProject",
        DummyProject
    )

    monkeypatch.setattr(
        fusion_controller,
        "find_fusion_input",
        lambda: "Fusion MIDI"
    )

    monkeypatch.setattr(
        fusion_controller,
        "find_fluidsynth_output",
        lambda: "FluidSynth MIDI"
    )

    monkeypatch.setattr(
        fusion_controller.mido,
        "open_input",
        lambda port: DummyPort()
    )

    monkeypatch.setattr(
        fusion_controller.mido,
        "open_output",
        lambda port: DummyPort()
    )

    choices = iter(
        [
            "mix",
            None
        ]
    )

    monkeypatch.setattr(
        fusion_controller,
        "choose_controller_mode",
        lambda: next(choices)
    )

    diagnostics = []

    monkeypatch.setattr(
        fusion_controller,
        "print_mode_diagnostic",
        lambda project, mode:
            diagnostics.append(mode)
    )

    monkeypatch.setattr(
        fusion_controller,
        "load_last_performance",
        lambda mode: None
    )

    loops = []

    monkeypatch.setattr(
        fusion_controller,
        "run_controller_loop",
        lambda inp, out, project, mode:
            loops.append(mode)
    )

    fusion_controller.main()

    assert diagnostics == [
        "mix"
    ]

    assert loops == [
        "mix"
    ]


def test_main_mix_resumes_last_performance(
    monkeypatch
):

    class DummyProject:

        def validate(self):
            return []

    monkeypatch.setattr(
        fusion_controller,
        "FusionProject",
        DummyProject
    )

    monkeypatch.setattr(
        fusion_controller,
        "find_fusion_input",
        lambda: "Fusion MIDI"
    )

    monkeypatch.setattr(
        fusion_controller,
        "find_fluidsynth_output",
        lambda: "FluidSynth MIDI"
    )

    monkeypatch.setattr(
        fusion_controller.mido,
        "open_input",
        lambda port: DummyPort()
    )

    monkeypatch.setattr(
        fusion_controller.mido,
        "open_output",
        lambda port: DummyPort()
    )

    choices = iter(
        [
            "mix",
            None
        ]
    )

    monkeypatch.setattr(
        fusion_controller,
        "choose_controller_mode",
        lambda: next(choices)
    )

    monkeypatch.setattr(
        fusion_controller,
        "print_mode_diagnostic",
        lambda project, mode: None
    )

    monkeypatch.setattr(
        fusion_controller,
        "load_last_performance",
        lambda mode: "2:4"
    )

    loaded = []

    monkeypatch.setattr(
        fusion_controller,
        "load_mix",
        lambda mix_id, out, project:
            loaded.append(mix_id)
    )

    monkeypatch.setattr(
        fusion_controller,
        "run_controller_loop",
        lambda inp, out, project, mode: None
    )

    fusion_controller.main()

    assert loaded == [
        "2:4"
    ]


def test_main_mix_keyboard_interrupt_returns_to_controller(
    monkeypatch,
    capsys
):

    class DummyProject:

        def validate(self):
            return []

    monkeypatch.setattr(
        fusion_controller,
        "FusionProject",
        DummyProject
    )

    monkeypatch.setattr(
        fusion_controller,
        "find_fusion_input",
        lambda: "Fusion MIDI"
    )

    monkeypatch.setattr(
        fusion_controller,
        "find_fluidsynth_output",
        lambda: "FluidSynth MIDI"
    )

    monkeypatch.setattr(
        fusion_controller.mido,
        "open_input",
        lambda port: DummyPort()
    )

    monkeypatch.setattr(
        fusion_controller.mido,
        "open_output",
        lambda port: DummyPort()
    )

    choices = iter(
        [
            "mix",
            None
        ]
    )

    monkeypatch.setattr(
        fusion_controller,
        "choose_controller_mode",
        lambda: next(choices)
    )

    monkeypatch.setattr(
        fusion_controller,
        "print_mode_diagnostic",
        lambda project, mode: None
    )

    monkeypatch.setattr(
        fusion_controller,
        "load_last_performance",
        lambda mode: None
    )

    def interrupt(
        inp,
        out,
        project,
        mode
    ):

        raise KeyboardInterrupt

    monkeypatch.setattr(
        fusion_controller,
        "run_controller_loop",
        interrupt
    )

    fusion_controller.main()

    output = capsys.readouterr().out

    assert (
        "Retour au Contrôleur Live"
        in output
    )


def test_main_song_can_return_without_selection(
    monkeypatch
):

    class DummyProject:

        def validate(self):
            return []

    monkeypatch.setattr(
        fusion_controller,
        "FusionProject",
        DummyProject
    )

    monkeypatch.setattr(
        fusion_controller,
        "find_fusion_input",
        lambda: "Fusion MIDI"
    )

    monkeypatch.setattr(
        fusion_controller,
        "find_fluidsynth_output",
        lambda: "FluidSynth MIDI"
    )

    monkeypatch.setattr(
        fusion_controller.mido,
        "open_input",
        lambda port: DummyPort()
    )

    monkeypatch.setattr(
        fusion_controller.mido,
        "open_output",
        lambda port: DummyPort()
    )

    choices = iter(
        [
            "song",
            None
        ]
    )

    monkeypatch.setattr(
        fusion_controller,
        "choose_controller_mode",
        lambda: next(choices)
    )

    monkeypatch.setattr(
        fusion_controller,
        "print_mode_diagnostic",
        lambda project, mode: None
    )

    monkeypatch.setattr(
        fusion_controller,
        "load_last_performance",
        lambda mode: None
    )

    monkeypatch.setattr(
        fusion_controller,
        "choose_song",
        lambda project: None
    )

    fusion_controller.main()


def test_main_song_runs_selected_song(
    monkeypatch
):

    class DummyProject:

        def validate(self):
            return []

    monkeypatch.setattr(
        fusion_controller,
        "FusionProject",
        DummyProject
    )

    monkeypatch.setattr(
        fusion_controller,
        "find_fusion_input",
        lambda: "Fusion MIDI"
    )

    monkeypatch.setattr(
        fusion_controller,
        "find_fluidsynth_output",
        lambda: "FluidSynth MIDI"
    )

    monkeypatch.setattr(
        fusion_controller.mido,
        "open_input",
        lambda port: DummyPort()
    )

    monkeypatch.setattr(
        fusion_controller.mido,
        "open_output",
        lambda port: DummyPort()
    )

    modes = iter(
        [
            "song",
            None
        ]
    )

    monkeypatch.setattr(
        fusion_controller,
        "choose_controller_mode",
        lambda: next(modes)
    )

    monkeypatch.setattr(
        fusion_controller,
        "print_mode_diagnostic",
        lambda project, mode: None
    )

    monkeypatch.setattr(
        fusion_controller,
        "load_last_performance",
        lambda mode: None
    )

    songs = iter(
        [
            "My Song",
            None
        ]
    )

    monkeypatch.setattr(
        fusion_controller,
        "choose_song",
        lambda project: next(songs)
    )

    calls = []

    def run_loop(
        inp,
        out,
        project,
        mode,
        selected_song=None
    ):

        calls.append(
            (
                mode,
                selected_song
            )
        )

        return None

    monkeypatch.setattr(
        fusion_controller,
        "run_controller_loop",
        run_loop
    )

    fusion_controller.main()

    assert calls == [
        (
            "song",
            "My Song"
        )
    ]


def test_main_song_change_clears_previous_song_state(
    monkeypatch
):

    class DummyProject:

        def validate(self):
            return []

    monkeypatch.setattr(
        fusion_controller,
        "FusionProject",
        DummyProject
    )

    monkeypatch.setattr(
        fusion_controller,
        "find_fusion_input",
        lambda: "Fusion MIDI"
    )

    monkeypatch.setattr(
        fusion_controller,
        "find_fluidsynth_output",
        lambda: "FluidSynth MIDI"
    )

    out = DummyPort()

    monkeypatch.setattr(
        fusion_controller.mido,
        "open_input",
        lambda port: DummyPort()
    )

    monkeypatch.setattr(
        fusion_controller.mido,
        "open_output",
        lambda port: out
    )

    modes = iter(
        [
            "song",
            None
        ]
    )

    monkeypatch.setattr(
        fusion_controller,
        "choose_controller_mode",
        lambda: next(modes)
    )

    monkeypatch.setattr(
        fusion_controller,
        "print_mode_diagnostic",
        lambda project, mode: None
    )

    monkeypatch.setattr(
        fusion_controller,
        "load_last_performance",
        lambda mode: None
    )

    songs = iter(
        [
            "Song 1",
            None
        ]
    )

    monkeypatch.setattr(
        fusion_controller,
        "choose_song",
        lambda project: next(songs)
    )

    fusion_controller.state.active_notes = {
        (
            0,
            60
        )
    }

    fusion_controller.state.current_parts = {
        1: {
            "test": True
        }
    }

    fusion_controller.state.current_performance = (
        "Song 1"
    )

    fusion_controller.state.current_song_programs = {
        1: {
            "program_id": "0:1"
        }
    }

    panic_calls = []

    monkeypatch.setattr(
        fusion_controller,
        "panic",
        lambda output:
            panic_calls.append(output)
    )

    monkeypatch.setattr(
        fusion_controller,
        "run_controller_loop",
        lambda *args, **kwargs: "song_change"
    )

    fusion_controller.main()

    assert panic_calls == [
        out
    ]

    assert (
        fusion_controller.state.active_notes
        == set()
    )

    assert (
        fusion_controller.state.current_parts
        == {}
    )

    assert (
        fusion_controller.state.current_performance
        is None
    )

    assert (
        fusion_controller.state.current_song_programs
        == {}
    )


def test_main_song_keyboard_interrupt_clears_song_state(
    monkeypatch
):

    class DummyProject:

        def validate(self):
            return []

    monkeypatch.setattr(
        fusion_controller,
        "FusionProject",
        DummyProject
    )

    monkeypatch.setattr(
        fusion_controller,
        "find_fusion_input",
        lambda: "Fusion MIDI"
    )

    monkeypatch.setattr(
        fusion_controller,
        "find_fluidsynth_output",
        lambda: "FluidSynth MIDI"
    )

    out = DummyPort()

    monkeypatch.setattr(
        fusion_controller.mido,
        "open_input",
        lambda port: DummyPort()
    )

    monkeypatch.setattr(
        fusion_controller.mido,
        "open_output",
        lambda port: out
    )

    modes = iter(
        [
            "song",
            None
        ]
    )

    monkeypatch.setattr(
        fusion_controller,
        "choose_controller_mode",
        lambda: next(modes)
    )

    monkeypatch.setattr(
        fusion_controller,
        "print_mode_diagnostic",
        lambda project, mode: None
    )

    monkeypatch.setattr(
        fusion_controller,
        "load_last_performance",
        lambda mode: None
    )

    songs = iter(
        [
            "Song 1",
            None
        ]
    )

    selected_songs = []

    def fake_choose_song(
        project
    ):

        song = next(
            songs
        )

        selected_songs.append(
            song
        )

        return song

    monkeypatch.setattr(
        fusion_controller,
        "choose_song",
        fake_choose_song
    )

    fusion_controller.state.active_notes = {
        (
            0,
            60
        )
    }

    fusion_controller.state.current_parts = {
        1: {
            "test": True
        }
    }

    fusion_controller.state.current_performance = (
        "Song 1"
    )

    fusion_controller.state.current_song_programs = {
        1: {
            "program_id": "0:1"
        }
    }

    panic_calls = []

    monkeypatch.setattr(
        fusion_controller,
        "panic",
        lambda output:
            panic_calls.append(output)
    )

    def interrupt_song(
        *args,
        **kwargs
    ):

        raise KeyboardInterrupt

    monkeypatch.setattr(
        fusion_controller,
        "run_controller_loop",
        interrupt_song
    )

    fusion_controller.main()

    assert panic_calls == [
        out
    ]

    assert (
        fusion_controller.state.active_notes
        == set()
    )

    assert (
        fusion_controller.state.current_parts
        == {}
    )

    assert (
        fusion_controller.state.current_performance
        is None
    )

    assert (
        fusion_controller.state.current_song_programs
        == {}
    )

    assert selected_songs == [
        "Song 1",
        None
    ]


def test_main_keyboard_interrupt_returns_to_menu(
    monkeypatch,
    capsys
):

    class DummyProject:

        def validate(self):
            return []

    monkeypatch.setattr(
        fusion_controller,
        "FusionProject",
        DummyProject
    )

    monkeypatch.setattr(
        fusion_controller,
        "find_fusion_input",
        lambda: "Fusion MIDI"
    )

    monkeypatch.setattr(
        fusion_controller,
        "find_fluidsynth_output",
        lambda: "FluidSynth MIDI"
    )

    monkeypatch.setattr(
        fusion_controller.mido,
        "open_input",
        lambda port: DummyPort()
    )

    monkeypatch.setattr(
        fusion_controller.mido,
        "open_output",
        lambda port: DummyPort()
    )

    def interrupt():

        raise KeyboardInterrupt

    monkeypatch.setattr(
        fusion_controller,
        "choose_controller_mode",
        interrupt
    )

    fusion_controller.main()

    output = capsys.readouterr().out

    assert "Retour au menu" in output
