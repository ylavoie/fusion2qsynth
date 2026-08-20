#!/usr/bin/env python3

import time
import os
import json
import mido

from fusion_constants import (
    LAST_MIX_FILE,
    FUSION_DEFAULT_CHANNEL,
    DEBUG
)

from fusion_project import FusionProject

from fusion_lib import (
    find_fusion_input,
    find_fluidsynth_output,
    panic,
    note_name,
    log_event
)

fusion_default_channel = FUSION_DEFAULT_CHANNEL - 1

class ControllerState:

    def __init__(self):

        self.current_mode = None
        self.current_performance = None
        self.current_parts = {}
        self.active_notes = set()
        self.pending_reload = False
        self.reload_wait_announced = False

state = ControllerState()

def save_last_mix(mix_id):

    with open(
        LAST_MIX_FILE,
        "w"
    ) as f:

        json.dump(
            {
                "mix": mix_id
            },
            f,
            indent=2
        )

def send_program(out, channel, instrument):

    bank = instrument.get(
        "sf2_bank",
        0
    )

    program = instrument.get(
        "sf2_program",
        0
    )

    bank_msb = bank // 128
    bank_lsb = bank % 128

    out.send(
        mido.Message(
            "control_change",
            channel=channel,
            control=0,
            value=bank_msb
        )
    )

    out.send(
        mido.Message(
            "control_change",
            channel=channel,
            control=32,
            value=bank_lsb
        )
    )

    out.send(
        mido.Message(
            "program_change",
            channel=channel,
            program=min(
                max(
                    program,
                    0
                ),
                127
            )
        )
    )

def load_mix(mix_id, out, project):

    loaded_parts = 0

    mix = project.get_mix(
        mix_id
    )

    if not mix:

        print()
        print(
            "Mix inconnu:",
            mix_id
        )

        return

    errors = project.validate_mix(
        mix_id
    )

    if errors:

        print()
        print(
            "Attention configuration Mix :",
            mix_id
        )

        for err in errors:

            print(
                "-",
                err
            )

        print()

    state.current_mode = "mix"
    state.current_performance = mix_id
    state.current_parts = {}
    state.pending_reload = False

    print()
    print("======================")
    print(
        "Performance:",
        mix.get(
            "name",
            mix_id
        )
    )
    print(
        "Fusion Mix:",
        mix_id
    )
    project.print_mix(
        mix_id
    )
    print("======================")

    panic(out)

    state.active_notes.clear()

    time.sleep(0.1)

    for part_id, part in project.get_parts(mix_id).items():

        if not project.is_qsynth_ready(part):

            print(
                "PART",
                part_id,
                "incomplète, ignorée"
            )

            continue

        midi_channel = (
            part["midi_channel"] - 1
        )

        instrument = project.resolve_part_instrument(part)

        send_program(
            out,
            midi_channel,
            instrument
        )

        state.current_parts[
            part["midi_channel"]
        ] = part

        loaded_parts += 1

        log_event(
            f"PART {part_id} CH {part['midi_channel']} "
            f"SF2 {instrument.get('name', 'Non configuré')}"
        )

    print()
    print(
        loaded_parts,
        "PARTS chargées dans FluidSynth"
    )
    print()

    print()

    print(
        "Canaux actifs :"
    )

    if loaded_parts > 0:

        save_last_mix(
            mix_id
        )

    for ch, part in state.current_parts.items():

        instrument = project.resolve_part_instrument(
            part
        )

        print(
            " CH",
            ch,
            "→",
            instrument.get(
                "name",
                "Non configuré"
            )
            if instrument
            else "Non configuré"
        )

    print()

def reload_current_performance(
    out,
    project
):

    if state.current_mode == "program":

        load_program(
            state.current_performance,
            out,
            project
        )

    elif state.current_mode == "mix":

        load_mix(
            state.current_performance,
            out,
            project
        )

    elif state.current_mode == "song":

        load_song(
            state.current_performance,
            out,
            project
        )

def execute_pending_reload(
    out,
    project,
    deferred=False
):

    print()

    if deferred:

        print(
            "Notes relâchées : reload différé."
        )

    else:

        print(
            "Projet modifié : reload immédiat."
        )

    reload_current_performance(
        out,
        project
    )

    state.pending_reload = False
    state.reload_wait_announced = False

def load_last_mix():

    if not os.path.exists(LAST_MIX_FILE):

        return None

    with open(LAST_MIX_FILE) as f:

        data = json.load(f)

        return data.get(
            "mix"
        )

def load_program(
    program_id,
    out,
    project
):

    program = project.get_program(
        program_id
    )

    if not program:

        print()
        print(
            "Program inconnu:",
            program_id
        )

        return

    parts = program.get(
        "parts",
        {}
    )

    if not parts:

        print()
        print(
            "Program sans PART:",
            program_id
        )

        return

    part_id, part = next(
        iter(
            parts.items()
        )
    )

    if not project.is_qsynth_ready(
        part
    ):

        print()
        print(
            "PROGRAM",
            program_id,
            "non configuré pour FluidSynth."
        )

        return

    instrument = project.resolve_part_instrument(
        part
    )

    if not instrument:

        print()
        print(
            "Instrument non configuré."
        )

        return

    state.current_mode = "program"
    state.current_performance = program_id
    state.current_parts = {}
    state.pending_reload = False

    print()
    print("======================")
    print(
        "PROGRAM:",
        program.get(
            "name",
            program_id
        )
    )
    print(
        "Fusion Program:",
        program_id
    )
    print("======================")

    panic(out)

    state.active_notes.clear()

    time.sleep(0.1)

    midi_channel = (
        part["midi_channel"] - 1
    )

    send_program(
        out,
        midi_channel,
        instrument
    )

    state.current_parts[
        part["midi_channel"]
    ] = part

    #save_last_performance(
    #    "program",
    #    program_id
    #)

    print()
    print(
        "Canal actif :"
    )

    print(
        " CH",
        part["midi_channel"],
        "→",
        instrument.get(
            "name",
            "Non configuré"
        )
    )

    print()

def load_song(
    song_id,
    out,
    project
):

    song = project.get_song(
        song_id
    )

    if not song:

        print()
        print(
            "SONG inconnue:",
            song_id
        )

        return

    channels = song.get(
        "channels",
        {}
    )

    if not channels:

        print()
        print(
            "SONG sans canaux:",
            song_id
        )

        return

    state.current_mode = "song"
    state.current_performance = song_id
    state.current_parts = {}
    state.pending_reload = False

    print()
    print("======================")
    print(
        "SONG:",
        song.get(
            "name",
            song_id
        )
    )
    print(
        "Fusion Song:",
        song_id
    )
    print("======================")

    panic(
        out
    )

    state.active_notes.clear()

    time.sleep(
        0.1
    )

    loaded_channels = 0

    for channel_id, channel in channels.items():

        instrument = project.resolve_part_instrument(
            channel
        )

        if not instrument:

            print(
                "CH",
                channel_id,
                "instrument non configuré"
            )

            continue

        midi_channel = (
            int(channel_id) - 1
        )

        #
        # Instrument SoundFont
        #
        send_program(
            out,
            midi_channel,
            instrument
        )

        #
        # Paramètres statiques SONG
        #
        controls = {
            7: "volume",
            10: "pan",
            11: "expression",
            91: "reverb",
            93: "chorus"
        }

        for cc, field in controls.items():

            if field not in channel:

                continue

            out.send(
                mido.Message(
                    "control_change",
                    channel=midi_channel,
                    control=cc,
                    value=channel[field]
                )
            )

        state.current_parts[
            int(channel_id)
        ] = channel

        loaded_channels += 1

    print()
    print(
        loaded_channels,
        "canaux chargés dans FluidSynth"
    )

    print()
    print(
        "Canaux actifs :"
    )

    for ch, channel in state.current_parts.items():

        instrument = project.resolve_part_instrument(
            channel
        )

        print(
            " CH",
            ch,
            "→",
            instrument.get(
                "name",
                "Non configuré"
            )
            if instrument
            else "Non configuré"
        )

    print()

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

            print(
                index,
                "-",
                song.get(
                    "name",
                    song_id
                )
            )

        print(
            "q - Retour"
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

def main():

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

    project = FusionProject()

    errors = project.validate()

    if errors:

        print()
        print(
            "===================="
        )
        print(
            "AVERTISSEMENTS CONFIGURATION"
        )
        print(
            "===================="
        )

        for err in errors:

            print(
                "-",
                err
            )

        print()

    selected_mode = choose_controller_mode()
    state.current_mode = selected_mode

    last_mix = None

    selected_song = None

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

            for channel in song["channels"]:

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

        selected_song = choose_song(
            project
        )

        if selected_song is None:

            return

    if selected_mode == "mix":

        last_mix = load_last_mix()

        diagnostic = project.get_mix_diagnostic()
        for mix in diagnostic:

            print()
            print(
                "Mix :",
                mix["mix"],
                "-",
                mix["name"]
            )


            for part in mix["parts"]:

                print(
                    " PART",
                    part["part"],
                    "Fusion:",
                    "OK"
                    if part["fusion_valid"]
                    else "ERREUR",
                    "QSynth:",
                    "OK"
                    if part["qsynth_configured"]
                    else "Non configuré"
                )


            if "shared_channels" in mix:

                print(
                    " ⚠ Canaux partagés :",
                    mix["shared_channels"]
                )

        print()
        print(
            project.count_mixes(),
            "Mix chargés"
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

    bank = 0

    try:
        with mido.open_input(
            fusion_port
        ) as inp:

            with mido.open_output(
                synth_port
            ) as out:

                if (
                    selected_mode == "mix"
                    and
                    last_mix
                ):

                    load_mix(
                        last_mix,
                        out,
                        project
                    )

                print()
                if selected_mode == "program":

                    print(
                        "Attente des changements de Program..."
                    )

                elif selected_mode == "song":

                    print(
                        "SONG sélectionnée :",
                        selected_song
                    )

                    print(
                        "Attente du START..."
                    )

                else:

                    print(
                        "Attente des changements de Mix..."
                    )

                while True:

                    if project.reload_if_changed():

                        if not state.pending_reload:

                            state.pending_reload = True
                            state.reload_wait_announced = False

                    #
                    # Reload immédiat si repos
                    #
                    if (
                        state.pending_reload
                        and
                        not state.active_notes
                    ):

                        execute_pending_reload(
                            out,
                            project
                        )

                    #
                    # MIDI
                    #
                    for msg in inp.iter_pending():

                        if (
                            selected_mode == "song"
                            and
                            msg.type == "song_select"
                        ):

                            if DEBUG:

                                print(
                                    "SONG SELECT reçu :",
                                    msg.song
                                )

                            continue

                        if msg.type in [
                            "note_on",
                            "note_off"
                        ]:

                            if msg.channel + 1 not in state.current_parts:

                                if DEBUG:

                                    print(
                                        "NOTE ignorée",
                                        "CH",
                                        msg.channel + 1,
                                        note_name(msg.note)
                                    )

                                continue

                        if msg.type == "note_on":

                            key = (
                                msg.channel,
                                msg.note
                            )

                            if msg.velocity > 0:

                                state.active_notes.add(
                                    key
                                )

                            else:

                                state.active_notes.discard(
                                    key
                                )

                        elif msg.type == "note_off":

                            state.active_notes.discard(
                                (
                                    msg.channel,
                                    msg.note
                                )
                            )

                            if (
                                state.pending_reload
                                and
                                not state.active_notes
                            ):
                                    execute_pending_reload(
                                        out,
                                        project,
                                        deferred=state.reload_wait_announced
                                    )

                        if (
                            state.pending_reload
                            and
                            state.active_notes
                            and
                            not state.reload_wait_announced
                        ):

                            print(
                                "Projet modifié : reload en attente "
                                "(notes actives)."
                            )

                            state.reload_wait_announced = True

                        if DEBUG:

                            part = state.current_parts.get(
                                msg.channel + 1
                            )
                            name = "?"

                            if part:

                                instrument = project.resolve_part_instrument(
                                    part
                                )

                                if instrument:

                                    name = instrument.get(
                                        "name",
                                        "?"
                                    )

                            if msg.type == "note_on" and msg.velocity > 0:

                                print(
                                    "NOTE ON",
                                    "CH",
                                    msg.channel + 1, name,
                                    "Note",
                                    note_name(msg.note),
                                    "Vel",
                                    msg.velocity
                                )

                            elif (
                                msg.type == "note_off"
                                or
                                (
                                    msg.type == "note_on"
                                    and
                                    msg.velocity == 0
                                )
                            ):
                                print(
                                    "NOTE OFF",
                                    "CH",
                                    msg.channel + 1, name,
                                    "Note",
                                    note_name(msg.note)
                                )

                        if msg.type in [
                            "note_on",
                            "note_off"
                        ]:

                            if not DEBUG:

                                print(
                                    "NOTE",
                                    msg.channel + 1,
                                    msg.type,
                                    note_name(msg.note),
                                    msg.velocity
                                )

                            out.send(msg)

                            continue

                        if msg.type in [
                            "pitchwheel",
                            "aftertouch",
                            "polytouch"
                        ]:

                            if (
                                msg.channel + 1
                                not in state.current_parts
                            ):

                                continue

                            out.send(
                                msg
                            )

                            continue

                        if msg.type == "control_change":

                            if selected_mode in (
                                "program",
                                "mix"
                            ):
                                #
                                # Détection banque du MIX Fusion
                                #
                                if (
                                    msg.channel == fusion_default_channel
                                    and
                                    msg.control == 0
                                ):

                                    bank = msg.value

                                    continue

                                #
                                # Bank Select des PARTs :
                                # ne pas écraser le mapping SoundFont
                                #
                                if msg.control in (
                                    0,
                                    32
                                ):

                                    continue

                                #
                                # PART non active
                                #
                                if (
                                    msg.channel + 1
                                    not in state.current_parts
                                ):

                                    if DEBUG:

                                        print(
                                            "CC ignoré",
                                            "CH",
                                            msg.channel + 1,
                                            "CC",
                                            msg.control,
                                            "Value",
                                            msg.value
                                        )

                                    continue

                            #
                            # Autres contrôleurs MIDI
                            #
                            out.send(
                                msg
                            )

                            continue

                        elif msg.type == "program_change":

                            if selected_mode == "song":

                                continue

                            if msg.channel != fusion_default_channel:

                                continue

                            performance_id = (
                                f"{bank}:{msg.program}"
                            )

                            log_event(
                                f"PERFORMANCE détectée {performance_id}"
                            )

                            print()
                            print(
                                "===================="
                            )

                            print(
                                "Performance Fusion détecté"
                            )

                            print(
                                "Bank:",
                                bank
                            )

                            print(
                                "Program:",
                                msg.program
                            )

                            print(
                                "ID:",
                                performance_id
                            )

                            print(
                                "===================="
                            )

                            if (
                                state.current_mode == selected_mode
                                and
                                performance_id == state.current_performance
                            ):

                                continue

                            if state.current_mode == "program":

                                load_program(
                                    performance_id,
                                    out,
                                    project
                                )

                            elif state.current_mode == "mix":

                                load_mix(
                                    performance_id,
                                    out,
                                    project
                                )

                            log_event(
                                f"PERFORMANCE chargée {performance_id}"
                            )

                        if (
                            selected_mode == "song"
                            and
                            msg.type == "start"
                        ):

                            load_song(
                                selected_song,
                                out,
                                project
                            )

                            continue

                time_sleep(
                    0.01
                )

    except KeyboardInterrupt:
        print()
        print("Retour au menu")
        return

if __name__ == "__main__":

    main()
