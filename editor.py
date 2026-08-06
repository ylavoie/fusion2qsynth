#!/usr/bin/env python3

import mido
import time

from fusion_lib import (
    find_fluidsynth_output,
    note_name
)

from fusion_project import FusionProject
from sf2_library import list_presets

MIDI_OUT_NAME = "FLUID Synth"

TEST_DURATION = 2

def get_test_note(part):

    note_min = part.get("note_min")
    note_max = part.get("note_max")

    if note_min is not None and note_max is not None:
        return (note_min + note_max) // 2
    elif note_min is not None:
        return note_min
    elif note_max is not None:
        return note_max

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

def choose_sf2_preset():

    presets = list_presets()

    if not presets:

        print(
            "Aucun preset SoundFont disponible."
        )

        return None

    while True:

        print()

        search = input(
            "Recherche (Entrée = tous, q = annuler) : "
        ).strip().lower()

        if search == "q":

            return None

        filtered = [
            preset
            for preset in presets
            if search in preset["name"].lower()
        ]

        if not filtered:

            print(
                "Aucun preset trouvé."
            )

            continue

        print()

        print(
            "Presets SoundFont disponibles :"
        )

        print()

        for index, preset in enumerate(
            filtered,
            start=1
        ):

            print(
                f"{index} - "
                f"{preset['name']} "
                f"(Bank {preset['sf2_bank']} "
                f"Program {preset['sf2_program']})"
            )

        print()

        choice = input(
            "Choix : "
        )

        try:

            index = int(choice) - 1

            return filtered[index]

        except (ValueError, IndexError):

            print(
                "Choix invalide."
            )

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

        if not project.save_safe():

            print(
                "⚠ Sauvegarde non effectuée."
            )
            repaired = False

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

    def rename_mix_menu(
        mix_id,
        mix
    ):

        print()

        print(
            "Nom actuel :",
            mix.get(
                "name",
                mix_id
            )
        )

        name = input(
            "Nouveau nom (Entrée = conserver) : "
        )

        if not name:

            return

        ok, errors = project.rename_mix(
            mix_id,
            name
        )

        if ok:

            if project.save_safe():

                print(
                    "Mix renommé."
                )

        else:

            print(
                "Modification refusée :"
            )

            for error in errors:

                print(
                    "-",
                    error
                )

    def duplicate_mix_menu(
        mix_id
    ):

        print()

        print(
            "Dupliquer le Mix :",
            mix_id
        )

        new_mix_id = input(
            "Nouvel ID Mix (ex: 0:2) : "
        )

        if not new_mix_id:

            return

        ok, errors = project.duplicate_mix(
            mix_id,
            new_mix_id
        )

        if ok:

            if project.save_safe():

                print(
                    "Mix dupliqué :",
                    new_mix_id
                )

            else:

                print(
                    "⚠ Sauvegarde non effectuée."
                )

        else:

            print(
                "Duplication refusée :"
            )

            for error in errors:

                print(
                    "-",
                    error
                )

    mix = project.get_mix(
        mix_id
    )

    if mix is None:

        print(
            "Mix inconnu"
        )

        return

    while True:

        project.print_mix(
            mix_id
        )

        print()
        print("====================")
        print("Edition Mix")
        print("====================")

        print(
            "1 - Renommer le Mix"
        )

        print(
            "2 - Dupliquer le Mix"
        )

        print(
            "3 - Tester le Mix"
        )

        print(
            "4 - Modifier les PARTS"
        )

        print(
            "q - Retour"
        )

        choix = input("> ")

        if choix == "1":

            rename_mix_menu(
                mix_id,
                mix
            )

        elif choix == "2":

            duplicate_mix_menu(
                mix_id
            )

        elif choix == "3":

            test_mix_menu(
                mix
            )

        elif choix == "4":

            edit_parts(
                project,
                mix_id,
                mix
            )

        elif choix.lower() == "q":

            return

def edit_parts(
    project,
    mix_id,
    mix
):
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

        project.print_part(part_id,part)

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

                print()

                print(
                    "1 - Modifier instrument"
                )

                print(
                    "2 - Modifier paramètres PART"
                )

                print(
                    "q - Annuler"
                )

                choix = input("> ")

                if choix == "1":

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

                                if not project.save_safe():

                                    print(
                                        "⚠ Sauvegarde non effectuée."
                                    )

                                    input(
                                        "Entrée pour continuer..."
                                    )

                                    break

                                break

                            elif choix.lower()=="q":

                                break

                    break

                if choix == "2":

                    edit_part_parameters(
                        project,
                        mix_id,
                        part_id,
                        part
                    )

                    break

def read_int(
    prompt,
    minimum=None,
    maximum=None
):

    while True:

        value = input(
            prompt
        )

        if not value:

            return None

        try:

            value = int(value)

        except ValueError:

            print(
                "Valeur numérique requise."
            )

            continue


        if (
            minimum is not None
            and
            value < minimum
        ):

            print(
                f"Valeur minimale : {minimum}"
            )

            continue


        if (
            maximum is not None
            and
            value > maximum
        ):

            print(
                f"Valeur maximale : {maximum}"
            )

            continue


        return value

def validate_part_updates(
    part,
    updates
):

    test = dict(part)

    test.update(
        updates
    )

    if not (
        0 <= test.get(
            "note_min",
            0
        )
        <=
        test.get(
            "note_max",
            127
        )
        <= 127
    ):

        print()

        print(
            "Plage de notes invalide (0-127)."
        )

        return False


    if not (
        0 <= test.get(
            "velocity_min",
            0
        )
        <=
        test.get(
            "velocity_max",
            127
        )
        <= 127
    ):

        print()

        print(
            "Plage de vélocité invalide (0-127)."
        )

        return False


    return True

def edit_part_parameters(
    project,
    mix_id,
    part_id,
    part
):

    updates = {}

    print()

    print(
        "Canal MIDI actuel :",
        part.get(
            "midi_channel",
            "?"
        )
    )

    value = read_int(
        "Nouveau canal MIDI (Entrée = conserver) : ",
        1,
        16
    )

    if value:

        updates["midi_channel"] = int(value)


    print()

    print(
        "Note min actuelle :",
        part.get(
            "note_min",
            "?"
        )
    )

    value = read_int(
        "Nouvelle note min (Entrée = conserver) : ",
        0,
        127
    )

    if value:

        updates["note_min"] = int(value)


    print()

    print(
        "Note max actuelle :",
        part.get(
            "note_max",
            "?"
        )
    )

    value = read_int(
        "Nouvelle note max (Entrée = conserver) : ",
        0,
        127
    )

    if value:

        updates["note_max"] = int(value)

    print()

    print(
        "Velocity min :",
        part.get(
            "velocity_min",
            0
        )
    )
    value = read_int(
        "Nouvelle velocity min (Entrée = conserver) : ",
        0,
        127
    )

    if value:

        updates["velocity_min"] = int(value)

    print()

    print(
        "Velocity max :",
        part.get(
            "velocity_max",
            127
        )
    )
    value = read_int(
        "Nouvelle velocity max (Entrée = conserver) : ",
        0,
        127
    )

    if value:

        updates["velocity_max"] = int(value)

    if not updates:

        print(
            "Aucune modification."
        )

        return

    if not validate_part_updates(
        part,
        updates
    ):

        print(
            "PART non modifiée."
        )

        return


    success, messages = project.update_part(
        mix_id,
        part_id,
        updates
    )

    if success:

        mix = project.get_mix(
            mix_id
        )

        part = mix["parts"][part_id]

        if project.save_safe():

            print(
                "PART modifiée."
            )

        else:

            print(
                "⚠ Sauvegarde non effectuée."
            )

    else:

        print()

        print(
            "Modification refusée :"
        )

        for message in messages:

            print(
                "-",
                message["message"]
            )

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

            bank = instrument.get(
                "sf2_bank",
                0
            )

            if not 0 <= bank <= 127:

                print(
                    "PART",
                    part_id,
                    "bank SF2",
                    bank,
                    "non testable directement en MIDI"
                )

                continue

            out.send(
                mido.Message(
                    "control_change",
                    channel=ch,
                    control=0,
                    value=bank
                )
            )

            program = instrument.get(
                "sf2_bank",
                0
            )

            if not 0 <= program <= 127:

                print(
                    "PART",
                    part_id,
                    "program SF2",
                    program,
                    "non testable directement en MIDI"
                )

                continue

            out.send(
                mido.Message(
                    "program_change",
                    channel=ch,
                    program=program
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

    print(
        f"{'ID':<10}{'Nom':<30}{'PARTS':>5}"
    )

    print(
        "-" * 45
    )

    for mix_id, mix in project.iter_mixes():

        print(
            f"{mix_id:<10}"
            f"{mix.get('name', ''):<30}"
            f"{len(mix.get('parts', {})):>5}"
        )

def get_mix_summary(
    self
):

    result = []

    for mix_id, mix in self.iter_mixes():

        result.append(
            {
                "id": mix_id,
                "name": mix.get(
                    "name",
                    mix_id
                ),
                "parts": len(
                    mix.get(
                        "parts",
                        {}
                    )
                )
            }
        )

    return result

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

    print()

    print(
        "Source instrument :"
    )

    print(
        "1 - Bibliothèque SoundFont"
    )

    print(
        "2 - Saisie manuelle"
    )

    source = input(
        "Choix : "
    )

    if source == "1":

        preset = choose_sf2_preset()

        if preset is None:

            return

        instrument_id = preset["id"]

        name = preset["name"]

        bank = preset["sf2_bank"]

        program = preset["sf2_program"]

    elif source == "2":

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

    else:

        print(
            "Choix invalide."
        )

        return

    if not project.add_instrument(
        instrument_id,
        {
            "name": name,
            "sf2_bank": bank,
            "sf2_program": program
        }
    ):

        print(
            "Identifiant déjà utilisé."
        )

        return

    if not project.save_safe():

        print(
            "⚠ Sauvegarde non effectuée."
        )

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

        if project.save_safe():

            print(
                "Instrument supprimé."
            )

        else:

            print(
                "Suppression non sauvegardée."
            )

    else:

        print(
            "Suppression impossible."
        )

def edit_instrument(project):

    instruments = project.list_instruments()

    if not instruments:
        print("Aucun instrument.")
        return

    # choisir instrument

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
        "Instrument à éditer : "
    )

    instrument = project.get_instrument(
        instrument_id
    )

    name = input(
        f"Nom [{instrument['name']}] : "
    )

    bank = input(
        f"Bank [{instrument['sf2_bank']}] : "
    )

    program = input(
        f"Program [{instrument['sf2_program']}] : "
    )

    updated = {
        "name": name or instrument["name"],
        "sf2_bank": int(bank) if bank else instrument["sf2_bank"],
        "sf2_program": int(program) if program else instrument["sf2_program"],
    }

    project.update_instrument(
        instrument_id,
        updated
    )

    project.save_safe()

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

        if project.save_safe():

            print(
                "Instrument affecté."
            )

        else:

            print(
                "Instrument non-affecté."
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

    def delete_empty_mixes_menu():

        empty_mixes = []

        for mix_id, mix in project.iter_mixes():

            if not mix.get(
                "parts",
                {}
            ):

                empty_mixes.append(
                    mix_id
                )

        if not empty_mixes:

            print()
            print(
                "Aucun MIX vide."
            )

            return

        print()

        print(
            "MIX vides détectés :"
        )

        for mix_id in empty_mixes:

            print(
                "-",
                mix_id
            )

        rep = input(
            "Supprimer ? (o/n) : "
        )

        if rep.lower() != "o":

            return

        ok, removed = project.delete_empty_mixes()

        if ok:

            if not removed:

                print()

                print(
                    "Aucun MIX vide."
                )

                return

            if project.save_safe():

                print()

                print(
                    "MIX supprimés :"
                )

                for mix_id in removed:

                    print(
                        "-",
                        mix_id
                    )

                print()

                print(
                    len(removed),
                    "MIX supprimé(s)."
                )

                print(
                    "Sauvegarde effectuée."
                )

        else:

            print(
                "⚠ Sauvegarde non effectuée."
            )

    def delete_mix_menu():

        mix_id = input(
            "Mix à supprimer : "
        )

        mix = project.get_mix(
            mix_id
        )

        if mix is None:

            print(
                "Mix inconnu."
            )

            return

        print()

        print(
            "Suppression du MIX :"
        )

        print(
            "ID :",
            mix_id
        )

        print(
            "Nom :",
            mix.get(
                "name",
                ""
            )
        )

        print(
            "PARTS :",
            len(
                mix.get(
                    "parts",
                    {}
                )
            )
        )

        rep = input(
            "Confirmer suppression ? (o/n) : "
        )

        if rep.lower() != "o":

            return

        ok, errors = project.delete_mix(
            mix_id
        )

        if not ok:

            print(
                "Suppression refusée."
            )

            return

        if project.save_safe():

            print(
                "MIX supprimé."
            )

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
        print("3 - Supprimer un MIX")
        print("4 - Supprimer les MIX vides")
        print("5 - Gestion Instruments")
        print("q - Quitter")

        choix = input("> ")

        if choix == "1":

            list_mixes(project)

        elif choix == "2":

            mix_id = input(
                "Numéro du Mix (ex: 2:4) : "
            )

            edit_mix(project,mix_id)

        elif choix == "3":

            delete_mix_menu()

        elif choix == "4":

            delete_empty_mixes_menu()

        elif choix == "5":

            instruments_menu(project)

        elif choix.lower() == "q":

            break

if __name__ == "__main__":

    main()
