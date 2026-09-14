#!/usr/bin/env python3

import mido

from fusion_diagnostic import (
    print_validation_errors
)

from fusion_project import FusionProject

from fusion_lib import (
    find_fusion_input,
    find_fluidsynth_output,
    panic
)

from fusion_controller_state import (
    state,
    load_last_performance
)

from fusion_performance import (
    load_mix,
    load_program
)

from fusion_controller_loop import (
    run_controller_loop
)

def choose_song(
    project
):

    songs = list(
        project.iter_songs()
    )

    if not songs:

        print()
        print(
            "Aucune SONG enregistrée."
        )

        return None

    while True:

        print()
        print(
            "SONGS disponibles :"
        )
        print()

        for index, (song_id, song) in enumerate(
            songs,
            start=1
        ):

            label = song_id

            name = song.get(
                "name"
            )

            if (
                name
                and
                name != song_id
            ):

                label += (
                    " - "
                    + name
                )

            print(
                f"{index:3} - {label}"
            )

        print()
        print(
            "  Q - Retour"
        )

        print()

        choice = input(
            "> "
        ).strip()

        if choice.lower() == "q":

            return None

        try:

            index = int(
                choice
            ) - 1

            return songs[index][0]

        except (
            ValueError,
            IndexError
        ):

            print(
                "Choix invalide."
            )

def choose_controller_mode():

    while True:

        print()
        print("====================")
        print("Contrôleur Live")
        print("====================")
        print()
        print("1 - PROGRAM")
        print("2 - MIX")
        print("3 - SONG")
        print("q - Retour")
        print()

        choice = input(
            "> "
        )

        if choice == "1":

            return "program"

        elif choice == "2":

            return "mix"

        elif choice == "3":

            return "song"

        elif choice.lower() == "q":

            return None

        print(
            "Choix invalide."
        )

def print_mode_diagnostic(
    project,
    selected_mode
):
    if selected_mode == "program":
        diagnostic = project.get_program_diagnostic()

        for program in diagnostic:

            print()
            print(
                "PROGRAM :",
                program["program"],
                "-",
                program["name"]
            )

            print(
                " Fusion:",
                "OK"
                if program["fusion_valid"]
                else "ERREUR",
                "QSynth:",
                "OK"
                if program["qsynth_configured"]
                else "Non configuré"
            )

        print()
        print(
            project.count_programs(),
            "PROGRAM enregistrés"
        )

    if selected_mode == "song":

        diagnostic = project.get_song_diagnostic()

        for song in diagnostic:

            print()
            song_id = song["song"]
            song_name = song["name"]

            if (
                song_name
                and
                song_name != song_id
            ):

                print(
                    "SONG :",
                    song_id,
                    "-",
                    song_name
                )

            else:

                print(
                    "SONG :",
                    song_id
                )

            for channel in sorted(
                song["channels"],
                key=lambda item: int(
                    item["channel"]
                )
            ):

                print(
                    " CH",
                    channel["channel"],
                    "Fusion:",
                    "OK"
                    if channel["fusion_valid"]
                    else "ERREUR",
                    "QSynth:",
                    "OK"
                    if channel["qsynth_configured"]
                    else "Non configuré"
                )

        print()
        print(
            project.count_songs(),
            "SONG enregistrées"
        )

    if selected_mode == "mix":

        diagnostic = (
            project.get_mix_diagnostic()
        )

        for mix in diagnostic:

            print()

            print(
                "Mix :",
                mix["mix"],
                "-",
                mix["name"]
            )

            #
            # Nouveau format v2.10
            #
            if "channels" in mix:

                for channel in mix[
                    "channels"
                ]:

                    print(
                        " CH",
                        channel["channel"],
                        "Fusion:",
                        (
                            "OK"
                            if channel[
                                "fusion_valid"
                            ]
                            else "ERREUR"
                        ),
                        "QSynth:",
                        (
                            "OK"
                            if channel[
                                "qsynth_configured"
                            ]
                            else "Non configuré"
                        )
                    )

                continue

            #
            # Ancien format <= v2.9
            #
            for part in mix.get(
                "parts",
                []
            ):

                print(
                    " PART",
                    part["part"],
                    "Fusion:",
                    (
                        "OK"
                        if part[
                            "fusion_valid"
                        ]
                        else "ERREUR"
                    ),
                    "QSynth:",
                    (
                        "OK"
                        if part[
                            "qsynth_configured"
                        ]
                        else "Non configuré"
                    )
                )

            if "shared_channels" in mix:

                print(
                    " ⚠ Canaux partagés :",
                    mix[
                        "shared_channels"
                    ]
                )

        print()

        print(
            project.count_mixes(),
            "Mix chargés"
        )

def main():

    project = FusionProject()

    errors = project.validate()

    if errors:

        print_validation_errors(
            project,
            errors,
            title="AVERTISSEMENTS CONFIGURATION"
        )

        print()

    fusion_port = find_fusion_input()

    if not fusion_port:

        raise Exception(
            "Fusion MIDI introuvable"
        )

    synth_port = find_fluidsynth_output()

    if not synth_port:

        raise Exception(
            "FluidSynth MIDI introuvable"
        )

    print(
        "Fusion :",
        fusion_port
    )

    print(
        "Synth :",
        synth_port
    )

    try:

        with mido.open_input(
            fusion_port
        ) as inp:

            with mido.open_output(
                synth_port
            ) as out:

                while True:

                    selected_mode = choose_controller_mode()

                    if selected_mode is None:

                        return

                    state.current_mode = selected_mode

                    print_mode_diagnostic(
                        project,
                        selected_mode
                    )

                    last_id = load_last_performance(
                        selected_mode
                    )

                    selected_song = None

                    if selected_mode == "mix":

                        if last_id:

                            print()
                            print(
                                "Reprise MIX :",
                                last_id
                            )

                            load_mix(
                                last_id,
                                out,
                                project
                            )

                        print()
                        print(
                            "Prêt à jouer - en attente d'un changement de MIX..."
                        )

                        try:

                            run_controller_loop(
                                inp,
                                out,
                                project,
                                "mix"
                            )

                        except KeyboardInterrupt:

                            print()
                            print(
                                "Retour au Contrôleur Live"
                            )

                            continue

                    elif selected_mode == "program":

                        if last_id:

                            print()
                            print(
                                "Reprise PROGRAM :",
                                last_id
                            )

                            load_program(
                                last_id,
                                out,
                                project
                            )

                        print()
                        print(
                            "Prêt à jouer - en attente d'un changement de PROGRAM..."
                        )

                        try:

                            run_controller_loop(
                                inp,
                                out,
                                project,
                                "program"
                            )

                        except KeyboardInterrupt:

                            print()
                            print(
                                "Retour au Contrôleur Live"
                            )

                            continue

                    elif selected_mode == "song":

                        while True:

                            selected_song = choose_song(
                                project
                            )

                            if selected_song is None:

                                break

                            print()
                            print(
                                "SONG sélectionnée :",
                                selected_song
                            )

                            print(
                                "Attente du START..."
                            )

                            result = run_controller_loop(
                                inp,
                                out,
                                project,
                                "song",
                                selected_song=selected_song
                            )

                            if result == "song_change":

                                #
                                # Nettoyer l'état de la SONG précédente
                                #
                                panic(
                                    out
                                )

                                state.active_notes.clear()
                                state.current_parts = {}
                                state.current_performance = None
                                state.current_song_programs = {}

                                print()
                                print(
                                    "Sélectionne la nouvelle SONG."
                                )

                                continue

    except KeyboardInterrupt:

        print()
        print(
            "Retour au menu"
        )

        return

if __name__ == "__main__":

    main()
