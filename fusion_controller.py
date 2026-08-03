#!/usr/bin/env python3

import time
import os
import json
import mido

from fusion_project import FusionProject

FILE = "fusion.json"

from fusion_lib import (
    load_json,
    find_fusion_input,
    find_fluidsynth_output,
    panic,
    note_name,
    validate_mix,
    print_mix,
    log_event
)

FILE_TIME = 0
LAST_FILE = "last_mix.json"

DEBUG = False

CURRENT_MIX = None
CURRENT_PARTS = {}

ACTIVE_NOTES = set()
PENDING_RELOAD = False

def save_last_mix(mix_id):

    with open(
        LAST_FILE,
        "w"
    ) as f:

        json.dump(
            {
                "mix": mix_id
            },
            f,
            indent=2
        )

def send_program(out, channel, part):

    bank = part.get(
        "sf2_bank",
        0
    )

    program = part.get(
        "sf2_program",
        0
    )

    out.send(
        mido.Message(
            "control_change",
            channel=channel,
            control=0,
            value=min(max(bank,0),127)
        )
    )

    out.send(
        mido.Message(
            "control_change",
            channel=channel,
            control=32,
            value=0
        )
    )

    out.send(
        mido.Message(
            "program_change",
            channel=channel,
            program=min(max(program,0),127)
        )
    )

def reload_if_changed():

    global FILE_TIME

    if not os.path.exists(FILE):

        return None

    new_time = os.path.getmtime(FILE)

    if new_time != FILE_TIME:

        FILE_TIME = new_time

        print()

        print(
            "fusion.json modifié"
        )

        print(
            "Rechargement..."
        )

        return load_json()

    return None

def validate_part(part):

    return (
        "midi_channel" in part
        and
        "sf2_bank" in part
        and
        "sf2_program" in part
    )

def load_mix(mix_id, out, performances):

    loaded_parts = 0

    if mix_id not in performances:

        print()
        print(
            "Mix inconnu:",
            mix_id
        )

        return

    mix = performances[mix_id]

    errors = validate_mix(
        {
            mix_id: mix
        }
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

    global CURRENT_MIX
    global CURRENT_PARTS

    CURRENT_MIX = mix_id
    CURRENT_PARTS = {}

    save_last_mix(
        mix_id
    )

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
    print_mix(
        mix_id,
        mix
    )
    print("======================")

    panic(out)

    time.sleep(0.1)

    for part_id, part in mix["parts"].items():

        if not validate_part(part):

            print(
                "PART",
                part_id,
                "incomplète, ignorée"
            )

            continue

        midi_channel = (
            part["midi_channel"] - 1
        )

        send_program(
            out,
            midi_channel,
            part
        )

        CURRENT_PARTS[
            part["midi_channel"]
        ] = part

        loaded_parts += 1

        log_event(
            f"PART {part_id} CH {part['midi_channel']} "
            f"SF2 {part.get('name','Non configuré')}"
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

    for ch, part in CURRENT_PARTS.items():

        print(
            " CH",
            ch,
            "→",
            part.get(
                "name",
                "Non configuré"
            )
        )

    print()

def forward_message(out, msg):

    if msg.type in [
        "note_on",
        "note_off",
        "control_change",
        "pitchwheel",
        "aftertouch",
        "polytouch"
    ]:

        out.send(msg)

def reload_current_mix(out, performances):

    if CURRENT_MIX:

        load_mix(
            CURRENT_MIX,
            out,
            performances
        )

def load_last_mix():

    if not os.path.exists(LAST_FILE):

        return None

    with open(LAST_FILE) as f:

        data = json.load(f)

        return data.get(
            "mix"
        )

def check_performances(performances):

    print()
    print("====================")
    print("Diagnostic Fusion")
    print("====================")

    errors = 0

    for mix_id, mix in performances.items():

        print()
        print(
            "Mix :",
            mix_id,
            "-",
            mix.get("name", "")
        )

        #
        # Étape 3
        # Détection canaux MIDI partagés
        #

        channels = []

        for part in mix.get("parts", {}).values():

            if "midi_channel" in part:

                channels.append(
                    part["midi_channel"]
                )

        duplicates = [
            ch
            for ch in set(channels)
            if channels.count(ch) > 1
        ]

        if duplicates:

            print()

            print(
                "⚠ Attention :"
            )

            print(
                "Canaux MIDI partagés :",
                duplicates
            )

            print(
                "Certaines PARTS Fusion peuvent être indissociables."
            )

        #
        # Vérification PARTS
        #

        for part_id, part in mix.get("parts", {}).items():

            problems = []

            if "midi_channel" not in part:

                problems.append(
                    "Canal MIDI absent"
                )

            if "sf2_bank" not in part:

                problems.append(
                    "SF2 Bank absent"
                )

            if "sf2_program" not in part:

                problems.append(
                    "SF2 Program absent"
                )

            print()

            print(
                "PART",
                part_id
            )

            print(
                " CH MIDI :",
                part.get(
                    "midi_channel",
                    "?"
                )
            )

            print(
                " Fusion : Bank",
                part.get(
                    "bank",
                    0
                ),
                "Program",
                part.get(
                    "program",
                    0
                )
            )

            print(
                " SF2 :",
                part.get(
                    "name",
                    "Non configuré"
                ),
                "Bank",
                part.get(
                    "sf2_bank",
                    "-"
                ),
                "Program",
                part.get(
                    "sf2_program",
                    "-"
                )
            )

            #
            # Étape 4
            # Zone MIDI apprise
            #

            if "note_min" in part and "note_max" in part:

                print(
                    " Zone :",
                    part["note_min"],
                    "-",
                    part["note_max"]
                )

            else:

                print(
                    " Zone : inconnue"
                )

            if "velocity_min" in part and "velocity_max" in part:

                print(
                    " Velocity :",
                    part["velocity_min"],
                    "-",
                    part["velocity_max"]
                )

            if problems:

                errors += 1

                print(
                    " ⚠",
                    ", ".join(problems)
                )

            else:

                print(
                    " ✓ PART valide"
                )

    print()

    if errors:

        print(
            "Diagnostic terminé :",
            errors,
            "problème(s)"
        )

    else:

        print(
            "Tous les Mix sont prêts"
        )

    print()

def main():

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

    performances = project.data

    last_mix = load_last_mix()
    check_performances(
        performances
    )

    global FILE_TIME

    FILE_TIME = os.path.getmtime(FILE)

    print()
    print(
        len(performances),
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

    if last_mix:

        print(
            "Dernier Mix :",
            last_mix
        )

    bank = 0

    try:
        with mido.open_input(
            fusion_port
        ) as inp:

            with mido.open_output(
                synth_port
            ) as out:

                print()
                print(
                    "Attente des changements de Mix..."
                )

                last_reload = time.time()

                for msg in inp:

                    new_data = reload_if_changed()

                    if new_data:

                        performances = new_data

                        PENDING_RELOAD = True

                        if PENDING_RELOAD and len(ACTIVE_NOTES) == 0:

                            reload_current_mix(
                                out,
                                performances
                            )
                            PENDING_RELOAD = False

                        else:

                            print(
                                "Reload en attente : notes actives"
                            )

                    if DEBUG:

                        part = CURRENT_PARTS.get(
                            msg.channel + 1
                        )
                        name = "?"

                        if part:

                            name = part.get(
                                "name",
                                "?"
                            )

                        if msg.type == "note_on" and msg.velocity > 0:

                            ACTIVE_NOTES.add(
                                (
                                    msg.channel,
                                    msg.note
                                )
                            )

                            print(
                                "NOTE ON",
                                "CH",
                                msg.channel + 1, name,
                                "Note",
                                note_name(msg.note),
                                "Vel",
                                msg.velocity
                            )

                        elif msg.type == "note_off":

                            ACTIVE_NOTES.discard(
                                (
                                    msg.channel,
                                    msg.note
                                )
                            )

                            print(
                                "NOTE OFF",
                                "CH",
                                msg.channel + 1, name,
                                "Note",
                                note_name(msg.note)
                            )

                    if time.time() - last_reload > 5:

                        performances = load_json()
                        last_reload = time.time()

                    if msg.type in [
                        "note_on",
                        "note_off"
                    ]:

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
                        "note_on",
                        "note_off",
                        "pitchwheel",
                        "aftertouch",
                        "polytouch"
                    ]:

                        forward_message(out, msg)

                        continue

                    if msg.type == "control_change":

                        if msg.control == 0:

                            bank = msg.value

                    elif msg.type == "program_change":

                        mix_id = (
                            f"{bank}:{msg.program}"
                        )

                        log_event(
                            f"MIX détecté {mix_id}"
                        )

                        print()
                        print(
                            "===================="
                        )

                        print(
                            "Mix Fusion détecté"
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
                            mix_id
                        )

                        print(
                            "===================="
                        )

                        if mix_id == CURRENT_MIX:

                            continue

                        load_mix(
                            mix_id,
                            out,
                            performances
                        )
                        log_event(
                            f"MIX chargé {mix_id}"
                        )

    except KeyboardInterrupt:
        print()
        print("Retour au menu")
        return

if __name__ == "__main__":

    main()
