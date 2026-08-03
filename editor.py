#!/usr/bin/env python3

import json
import os
import mido
import time

from fusion_lib import (
    find_fluidsynth_output,
    note_name,
    print_mix,
    print_part
)

from fusion_project import FusionProject

SF2_FILE = "sf2_library.json"

MIDI_OUT_NAME = "FLUID Synth"

TEST_DURATION = 2

def get_test_note(part):

    if (
        "note_min" in part
        and
        "note_max" in part
    ):

        return (
            part["note_min"]
            +
            part["note_max"]
        ) // 2

    return 60

def get_test_velocity(part):

    if (
        "velocity_min" in part
        and
        "velocity_max" in part
    ):

        return (
            part["velocity_min"]
            +
            part["velocity_max"]
        ) // 2

    return 80

def test_instrument(part, instrument):

    port_name = find_fluidsynth_output()

    if not port_name:

        print(
            "FluidSynth introuvable"
        )

        return

    channel = (
        part["midi_channel"] - 1
    )

    note = get_test_note(
        part
    )

    velocity = get_test_velocity(
        part
    )

    with mido.open_output(port_name) as out:

        # Bank Select MSB
        out.send(
            mido.Message(
                "control_change",
                channel=channel,
                control=0,
                value=instrument["sf2_bank"]
            )
        )

        # Program Change
        out.send(
            mido.Message(
                "program_change",
                channel=channel,
                program=instrument["sf2_program"]
            )
        )

        print()

        print(
            "Test",
            instrument["name"]
        )

        print(
            "CH",
            part["midi_channel"],
            "Note",
            note_name(note),
            "Velocity",
            velocity
        )

        # Note test C4
        out.send(
            mido.Message(
                "note_on",
                channel=channel,
                note=note,
                velocity=velocity
            )
        )

        time.sleep(TEST_DURATION)

        out.send(
            mido.Message(
                "note_off",
                channel=channel,
                note=note,
                velocity=0
            )
        )

def load_instruments():

    if not os.path.exists(SF2_FILE):

        print(
            "Bibliothèque SF2 absente"
        )

        return []

    with open(
        SF2_FILE,
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    instruments = data.get(
        "presets",
        []
    )

    instruments.sort(
        key=lambda x:
            (
                x["sf2_bank"],
                x["sf2_program"]
            )
    )

    return instruments

def search_instruments():

    print()

    recherche = input(
        "Recherche instrument (vide = tous) : "
    ).strip().lower()

    if not recherche:

        return INSTRUMENTS

    results = []

    for inst in INSTRUMENTS:

        if (
            recherche in inst["name"].lower()
            or recherche in str(inst["sf2_program"]
            or recherche in str(inst["sf2_bank"]))
            ):

            results.append(inst)

    return results

INSTRUMENTS = load_instruments()

def choose_instrument(part):

    print()

    while True:

        results = search_instruments()

        if not results:

            print(
                "Aucun instrument trouvé"
            )

            continue

        break

    for i, inst in enumerate(
        results,
        start=1
    ):

        print(
            f"{i} - {inst['name']} "
            f"(Bank {inst['sf2_bank']} "
            f"Program {inst['sf2_program']})"
        )

    while True:

        choix = input(
            "Choix (q pour quitter) : "
        )

        if choix.lower() == "q":

            return None

        try:

            num = int(choix)

            if 1 <= num <= len(INSTRUMENTS):

                inst = results[num-1]

                preview = input(
                    "Tester ce son ? (o/n) : "
                )

                if preview.lower() == "o":

                    preview_instrument(
                        part,
                        inst
                    )

                confirm = input(
                    "Utiliser ce son ? (o/n) : "
                )

                if confirm.lower()=="o":

                    return {
                        "sf2_bank":
                            inst["sf2_bank"],

                        "sf2_program":
                            inst["sf2_program"],

                        "name":
                            inst["name"]
                    }

        except ValueError:

            pass

        print(
            "Choix invalide"
        )

def preview_instrument(part,instrument):

    print()

    print(
        "Test arpège :",
        instrument["name"]
    )

    root = get_test_note(part)

    notes = [
        root,
        root + 4,
        root + 7,
        root + 12
    ]

    print(
        "Notes :",
        [
            note_name(n)
            for n in notes
        ]
    )

    print(
        "Bank",
        instrument["sf2_bank"],
        "Program",
        instrument["sf2_program"]
    )

    test_instrument(
        part,
        instrument
    )

def compare_instrument(
    part,
    old_instrument,
    new_instrument
):

    print()

    print(
        "A :",
        old_instrument["name"]
    )

    input(
        "Entrée pour écouter A..."
    )

    play_preview(
        part,
        old_instrument
    )

    print()

    print(
        "B :",
        new_instrument["name"]
    )

    input(
        "Entrée pour écouter B..."
    )

    play_preview(
        part,
        new_instrument
    )

def play_preview(part, instrument, duration=5):

    port_name = find_fluidsynth_output()

    if not port_name:
        print("FluidSynth introuvable")
        return

    channel = part["midi_channel"] - 1

    root = get_test_note(part)

    velocity = get_test_velocity(part)

    notes = [
        root,
        root + 4,
        root + 7,
        root + 12
    ]

    with mido.open_output(port_name) as out:

        out.send(
            mido.Message(
                "control_change",
                channel=channel,
                control=0,
                value=instrument["sf2_bank"]
            )
        )

        out.send(
            mido.Message(
                "program_change",
                channel=channel,
                program=instrument["sf2_program"]
            )
        )

        delay = duration / len(notes)

        for note in notes:

            out.send(
                mido.Message(
                    "note_on",
                    channel=channel,
                    note=note,
                    velocity=velocity
                )
            )

            time.sleep(delay)

            out.send(
                mido.Message(
                    "note_off",
                    channel=channel,
                    note=note,
                    velocity=0
                )
            )

def play_part_preview(part):

    if "sf2_bank" not in part:

        print(
            "PART non configurée"
        )

        return

    instrument = {

        "name":
            part["name"],

        "sf2_bank":
            part["sf2_bank"],

        "sf2_program":
            part["sf2_program"]

    }

    play_preview(
        part,
        instrument
    )

def check_parts(mix):

    channels = []

    for part_id, part in mix["parts"].items():

        channels.append(
            part["midi_channel"]
        )

    duplicates = []

    for ch in channels:

        if channels.count(ch) > 1:

            if ch not in duplicates:

                duplicates.append(ch)

    if duplicates:

        print()
        print(
            "⚠ Attention :"
        )

        print(
            "Canaux MIDI utilisés plusieurs fois :",
            duplicates
        )

        print(
            "Une seule instance FluidSynth ne pourra pas reproduire"
        )

        print(
            "toutes les couches Fusion."
        )

        print()

    return not duplicates

def edit_mix(project,mix_id):

    def test_mix_menu(mix):

        while True:

            print()

            print("====================")
            print("Test Mix")
            print("====================")

            print(
                "1 - PARTS séparées"
            )

            print(
                "2 - Toutes les PARTS"
            )

            print(
                "q - Retour"
            )

            choix = input("> ")

            if choix == "1":

                test_mix_parts(
                    mix
                )

            elif choix == "2":

                test_mix_all(
                    mix
                )

            elif choix.lower()=="q":

                return

    project = FusionProject()

    mix = project.get_mix(
        mix_id
    )

    check_parts(mix)
    print_mix(
        mix_id,
        mix
    )

    if "parts" not in mix:

        print(
            "Aucune PART détectée"
        )

        return

    test_mix_menu(
        mix
    )

    while True:

        part_id = input(
            "PART à modifier (q pour quitter) : "
        )

        if part_id.lower() == "q":
            project.save()
            print()
            print(
                "Mix complet sauvegardé"
            )
            return

        if part_id not in mix["parts"]:
            print("PART inconnue")
            continue

        part = mix["parts"][part_id]

        print_part(part_id,part)

        while True:

            rep = input(
                "Configurer cette PART ? (o/n/q) : "
            )

            if rep.lower() == "q":

                project.save()

                print(
                    "Edition terminée"
                )

                return

            if rep.lower() == "n":

                break

            if rep.lower() == "o":

                old_instrument = {
                    "name":
                        part.get(
                            "name",
                            "Non configuré"
                        ),

                    "sf2_bank":
                        part.get(
                            "sf2_bank",
                            0
                        ),

                    "sf2_program":
                        part.get(
                            "sf2_program",
                            0
                        )
                }

                instrument = choose_instrument(part)

                if instrument:

                    while True:

                        print()

                        print(
                            "1 - Tester"
                        )

                        print(
                            "2 - Comparer A/B"
                        )

                        print(
                            "3 - Garder"
                        )

                        print(
                            "q - Annuler"
                        )

                        choix = input("> ")

                        if choix == "1":

                            play_preview(
                                part,
                                instrument
                            )

                        elif choix == "2":

                            compare_instrument(
                                part,
                                old_instrument,
                                instrument
                            )

                        elif choix == "3":

                            part.update(
                                instrument
                            )

                            project.save()

                            break

                        elif choix.lower()=="q":

                            break

                if instrument is None:

                    project.save()

                    print(
                        "Edition terminée"
                    )

                    return

                part["sf2_bank"] = instrument["sf2_bank"]
                part["sf2_program"] = instrument["sf2_program"]
                part["name"] = instrument["name"]

                project.save()

                print(
                    "Sauvegardé :",
                    part
                )

                break

def test_mix_parts(mix):

    print()

    print(
        "===================="
    )

    print(
        "Test du Mix"
    )

    print(
        "===================="
    )

    for part_id, part in mix["parts"].items():

        print()

        print(
            "PART",
            part_id
        )

        if "sf2_bank" not in part:

            print(
                "Non configurée"
            )

            continue

        print(
            part["name"]
        )

        input(
            "Entrée pour jouer..."
        )

        play_part_preview(
            part
        )

def test_mix_all(mix):

    port_name = find_fluidsynth_output()

    if not port_name:

        print(
            "FluidSynth introuvable"
        )

        return

    notes = [
        60,
        64,
        67,
        72
    ]

    with mido.open_output(port_name) as out:

        print()

        print(
            "Test toutes les PARTS"
        )

        #
        # Préparer tous les sons
        #

        for part_id, part in mix["parts"].items():

            if "sf2_bank" not in part:

                continue

            ch = (
                part["midi_channel"] - 1
            )

            out.send(
                mido.Message(
                    "control_change",
                    channel=ch,
                    control=0,
                    value=part["sf2_bank"]
                )
            )

            out.send(
                mido.Message(
                    "program_change",
                    channel=ch,
                    program=part["sf2_program"]
                )
            )

            print(
                "PART",
                part_id,
                "CH",
                part["midi_channel"],
                part["name"]
            )

        time.sleep(0.2)

        #
        # Jouer l'accord sur toutes les PARTS
        #

        for note in notes:

            for part_id, part in mix["parts"].items():

                if "sf2_bank" not in part:

                    continue

                ch = (
                    part["midi_channel"] - 1
                )

                out.send(
                    mido.Message(
                        "note_on",
                        channel=ch,
                        note=note,
                        velocity=70
                    )
                )

            time.sleep(0.5)

            for part_id, part in mix["parts"].items():

                if "sf2_bank" not in part:

                    continue

                ch = (
                    part["midi_channel"] - 1
                )

                out.send(
                    mido.Message(
                        "note_off",
                        channel=ch,
                        note=note,
                        velocity=0
                    )
                )

def list_mixes(project):

    print()

    print(
        "Mix disponibles :",
        project.count_mixes()
    )

    print()

    for mix_id, mix in project.iter_mixes():

        print(
            mix_id,
            "-",
            mix.get(
                "name",
                ""
            )
        )

def main():

    project = FusionProject()

    while True:

        print()
        print("===================")
        print("Fusion Editor")
        print("===================")
        print("1 - Liste des Mix")
        print("2 - Editer un Mix")
        print("q - Quitter")

        choix = input("> ")

        if choix == "1":

            list_mixes(project)

        elif choix == "2":

            mix = input(
                "Numéro du Mix (ex: 2:4) : "
            )

            edit_mix(project,mix)

        elif choix.lower() == "q":

            break

if __name__ == "__main__":

    main()
