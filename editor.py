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

def choose_instrument(
        project,
        part
):

    instruments = project.list_instruments()

    if not instruments:

        print(
            "Aucun instrument disponible."
        )

        return None

    print()

    print(
        "===================="
    )

    print(
        "Choix Instrument"
    )

    print(
        "===================="
    )

    for index, (instrument_id, instrument) in enumerate(
        instruments,
        start=1
    ):

        print(
            f"{index} - "
            f"{instrument_id} : "
            f"{instrument.get('name', '?')} "
            f"(Bank {instrument.get('sf2_bank', 0)}, "
            f"Program {instrument.get('sf2_program', 0)})"
        )

    print(
        "q - Annuler"
    )

    choix = input(
        "> "
    )

    if choix.lower() == "q":

        return None

    try:

        index = int(choix) - 1

        instrument_id, instrument = instruments[index]

    except:

        print(
            "Choix invalide"
        )

        return None

    result = dict(instrument)

    result["id"] = instrument_id

    return result

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

def play_part_preview(project, part):

    instrument = project.resolve_part_instrument(part)

    if instrument is None:

        print("Instrument non configuré.")

        return

    play_preview(
        part,
        instrument
    )

def repair_instrument_errors(
    project,
    errors
):

    repaired = False

    for error in errors:

        if not isinstance(error, dict):

            continue

        if error.get("type") != "missing_instrument":

            continue

        print()

        print(
            "Instrument absent :"
        )

        print(
            "Mix",
            error["mix_id"],
            "PART",
            error["part_id"]
        )

        print(
            error["instrument"]
        )

        print()

        choix = input(
            "Remplacer cet instrument ? (o/n) : "
        )

        if choix.lower() != "o":

            continue

        mix = project.get_mix(
            error["mix_id"]
        )

        part = mix["parts"][
            error["part_id"]
        ]

        instrument = choose_instrument(
            project,
            part
        )

        if instrument is None:

            continue

        project.set_part_instrument(
            error["mix_id"],
            error["part_id"],
            instrument["id"]
        )

        repaired = True

        print(
            "Instrument remplacé."
        )

    if repaired:

        project.save()

    return repaired

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
                    project,
                    mix
                )

            elif choix == "2":

                test_mix_all(
                    project,
                    mix
                )

            elif choix.lower()=="q":

                return

    project = FusionProject()

    mix = project.get_mix(
        mix_id
    )

    if mix is None:

        print(
            "Mix inconnu"
        )

        return

    print_mix(
        project,
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

            break

        if part_id not in mix["parts"]:
            print("PART inconnue")
            continue

        part = mix["parts"][part_id]

        print_part(project, part_id,part)

        while True:

            rep = input(
                "Configurer cette PART ? (o/n/q) : "
            )

            if rep.lower() == "q":

                break

            if rep.lower() == "n":

                break

            if rep.lower() == "o":

                old_instrument = project.resolve_part_instrument(part)

                if old_instrument is None:

                    old_instrument = {
                        "name": "Non configuré",
                        "sf2_bank": 0,
                        "sf2_program": 0
                    }

                instrument = choose_instrument(project, part)

                if instrument is None:

                    # L'utilisateur a annulé.
                    # On ne modifie rien.
                    break

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

                            project.set_part_instrument(
                                mix_id,
                                part_id,
                                instrument["id"]
                            )

                            project.save()

                            break

                        elif choix.lower()=="q":

                            break

                break

def test_mix_parts(project, mix):

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

        instrument = project.resolve_part_instrument(
            part
        )

        if not instrument:

            print(
                "Non configurée"
            )

            continue

        print(
            instrument["name"]
        )

        input(
            "Entrée pour jouer..."
        )

        play_part_preview(
            project,
            part
        )

def test_mix_all(project, mix):

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

        active_parts = []

        for part_id, part in mix["parts"].items():

            instrument = project.resolve_part_instrument(
                part
            )

            if not instrument:

                continue

            ch = (
                part["midi_channel"] - 1
            )

            out.send(
                mido.Message(
                    "control_change",
                    channel=ch,
                    control=0,
                    value=instrument["sf2_bank"]
                )
            )

            out.send(
                mido.Message(
                    "program_change",
                    channel=ch,
                    program=instrument["sf2_program"]
                )
            )

            print(
                "PART",
                part_id,
                "CH",
                part["midi_channel"],
                instrument["name"]
            )

            active_parts.append(
                (
                    part_id,
                    part,
                    ch
                )
            )

        time.sleep(0.2)

        #
        # Jouer l'accord sur toutes les PARTS
        #

        for note in notes:

            for part_id, part, ch in active_parts:

                out.send(
                    mido.Message(
                        "note_on",
                        channel=ch,
                        note=note,
                        velocity=70
                    )
                )

            time.sleep(0.5)

            for part_id, part, ch in active_parts:

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

def instruments_menu(project):

    while True:

        print()
        print("===================")
        print(" Instruments ")
        print("===================")

        print("1 - Liste")
        print("2 - Ajouter")
        print("3 - Modifier")
        print("4 - Supprimer")
        print("q - Retour")

        choice = input("> ")

        if choice == "1":

            list_instruments(project)

        elif choice == "2":

            add_instrument(project)

        elif choice == "3":

            edit_instrument(project)

        elif choice == "4":

            delete_instrument(project)

        elif choice.lower() == "q":

            break

def list_instruments(project):

    instruments = project.list_instruments()

    print()

    if not instruments:

        print("Aucun instrument.")

        return


    for instrument_id, instrument in instruments:

        print(
            f"{instrument_id} : "
            f"{instrument.get('name','?')} "
            f"(Bank {instrument.get('sf2_bank')} "
            f"Program {instrument.get('sf2_program')})"
        )

def add_instrument(project):

    instrument_id = input(
        "Identifiant : "
    )

    name = input(
        "Nom : "
    )

    bank = int(
        input(
            "SF2 Bank : "
        )
    )

    program = int(
        input(
            "SF2 Program : "
        )
    )


    project.add_instrument(
        instrument_id,
        {
            "name": name,
            "sf2_bank": bank,
            "sf2_program": program
        }
    )

    project.save()

def delete_instrument(project):

    instruments = project.list_instruments()

    if not instruments:

        print(
            "Aucun instrument."
        )

        return


    print()

    for instrument_id, instrument in instruments:

        print(
            instrument_id,
            "-",
            instrument.get(
                "name",
                "?"
            )
        )


    instrument_id = input(
        "Instrument à supprimer : "
    )


    instrument = project.get_instrument(
        instrument_id
    )


    if not instrument:

        print(
            "Instrument inconnu."
        )

        return


    confirm = input(
        f"Supprimer {instrument.get('name', instrument_id)} ? (o/n) : "
    )


    if confirm.lower() != "o":

        print(
            "Annulé."
        )

        return

    usages = project.find_instrument_usage(
        instrument_id
    )

    if usages:

        print(
            "Instrument utilisé par :"
        )

        for usage in usages:

            print(
                "-",
                usage["mix_id"],
                "PART",
                usage["part_id"]
            )

        return

    if project.remove_instrument(
        instrument_id
    ):

        project.save()

        print(
            "Instrument supprimé."
        )

    else:

        print(
            "Suppression impossible."
        )

def edit_part_instrument(
    project,
    mix_id,
    part_id
):

    instruments = project.list_instruments()

    if not instruments:

        print(
            "Aucun instrument disponible."
        )

        return


    print()

    for index, (instrument_id, instrument) in enumerate(
        instruments,
        start=1
    ):

        print(
            index,
            "-",
            instrument_id,
            instrument.get(
                "name",
                "?"
            )
        )


    choice = input(
        "Choix instrument : "
    )


    try:

        index = int(choice) - 1

        instrument_id = instruments[index][0]

    except:

        print(
            "Choix invalide."
        )

        return


    if project.set_part_instrument(
        mix_id,
        part_id,
        instrument_id
    ):

        project.save()

        print(
            "Instrument affecté."
        )

def print_validation_errors(errors):

    print()

    print(
        "===================="
    )

    print(
        "Erreurs de validation"
    )

    print(
        "===================="
    )

    for error in errors:

        if isinstance(error, str):

            print(
                "-",
                error
            )

            continue

        if error.get("type") == "missing_instrument":

            print()

            print(
                "⚠ Instrument absent"
            )

            print(
                "Mix        :",
                error["mix_id"]
            )

            print(
                "PART       :",
                error["part_id"]
            )

            print(
                "Canal MIDI :",
                error.get(
                    "channel",
                    "?"
                )
            )

            print(
                "Instrument :",
                error["instrument"]
            )

        elif error.get("type") == "midi_channel_conflict":

            print()

            print(
                "⚠ Information : canal MIDI partagé"
            )

            print(
                "Mix        :",
                error["mix_id"]
            )

            print(
                "Canal MIDI :",
                error["channel"]
            )

            print(
                "PARTS      :",
                ", ".join(
                    error["parts"]
                )
            )
            print(
                "Note : ce partage peut être volontaire."
            )
        else:

            print(
                "-",
                error.get(
                    "message",
                    error
                )
            )

def validate_and_repair(project):

    while True:

        errors = project.validate()

        if not errors:

            return

        print_validation_errors(
            errors
        )

        repairable = any(
            isinstance(error, dict)
            and
            error.get("type") == "missing_instrument"
            for error in errors
        )

        if not repairable:

            print()

            print(
                "Aucune réparation automatique disponible."
            )

            return

        choix = input(
            "Réparer maintenant ? (o/n) : "
        )

        if choix.lower() != "o":

            return

        repair_instrument_errors(
            project,
            errors
        )

def main():

    project = FusionProject()

    validate_and_repair(
        project
    )

    while True:

        print()
        print("===================")
        print("Fusion Editor")
        print("===================")
        print("1 - Liste des Mix")
        print("2 - Editer un Mix")
        print("3 - Gestion Instruments")
        print("q - Quitter")

        choix = input("> ")

        if choix == "1":

            list_mixes(project)

        elif choix == "2":

            mix = input(
                "Numéro du Mix (ex: 2:4) : "
            )

            edit_mix(project,mix)

        elif choix == "3":

            instruments_menu(project)

        elif choix.lower() == "q":

            break

if __name__ == "__main__":

    main()
