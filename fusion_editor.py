#!/usr/bin/env python3

import mido
import time

from fusion_lib import (
    find_fluidsynth_output,
    note_name,
    note_number
)

from fusion_diagnostic import (
    print_validation_errors,
    print_error_messages
)

from fusion_suggestions import (
    suggest_instruments
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

def get_sf2_suggestions(
    name,
    program
):

    if not name or program is None:

        return {}

    presets = list_presets()

    if not presets:

        return {}

    sf2_presets = [
        {
            "id": preset["id"],
            "name": preset["name"],
            "bank": preset["sf2_bank"],
            "program": preset["sf2_program"],
            "sf2_bank": preset["sf2_bank"],
            "sf2_program": preset["sf2_program"]
        }
        for preset in presets
    ]

    return suggest_instruments(
        {
            "name": name,
            "program": program
        },
        sf2_presets
    )

def choose_sf2_preset():

    presets = list_presets()

    if not presets:

        print(
            "Aucun preset SoundFont disponible."
        )

        return None

    presets = sorted(
        presets,
        key=lambda preset:
            preset.get(
                "name",
                ""
            ).lower()
    )

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

        if choice.lower() == "q":

            return None

        try:

            index = int(choice) - 1

            return filtered[index]

        except (ValueError, IndexError):

            print(
                "Choix invalide."
            )

def ensure_project_instrument(
    project,
    preset
):

    instrument_id = preset["id"]

    existing = project.get_instrument(
        instrument_id
    )

    if existing:

        result = dict(
            existing
        )

        result["id"] = instrument_id

        return result

    instrument = {
        "name": preset["name"],
        "sf2_bank": preset["sf2_bank"],
        "sf2_program": preset["sf2_program"]
    }

    if not project.add_instrument(
        instrument_id,
        instrument
    ):

        return None

    if not project.save_safe():

        project.remove_instrument(
            instrument_id
        )

        return None

    result = dict(
        instrument
    )

    result["id"] = instrument_id

    return result

def choose_instrument(
    project,
    part=None,
    fusion_name=None
):
    print()

    print("====================")
    print("Choix Instrument")
    print("====================")

    show_suggestions = True

    while True:
        current_id = None

        suggestions = {}

        if part is not None:

            current = project.resolve_part_instrument(part)

            if current:

                print()

                print(
                    "Instrument actuel :",
                    current.get("name", "?")
                )
            else:

                print("Instrument non-configuré")

            current_id = part.get(
                "instrument"
            )

        if (
            part is not None
            and
            fusion_name
        ):

            suggestions = get_sf2_suggestions(
                fusion_name,
                part.get(
                    "program"
                )
            )
            if (
                show_suggestions
                and
                suggestions
            ):

                print()
                print(
                    "Suggestions pour :",
                    fusion_name
                )

                print()

                suggestion_list = []

                for family, matches in suggestions.items():

                    print(
                        family.upper()
                    )

                    for score, preset in matches:

                        suggestion_list.append(
                            preset
                        )

                        print(
                            f" {len(suggestion_list):2} - "
                            f"{preset['name']:<25}"
                            f"({preset['sf2_bank']}:"
                            f"{preset['sf2_program']})"
                        )

                    print()

                print(
                    "t - Tous les instruments"
                )

                print(
                    "a - Ajouter un instrument"
                )

                print(
                    "q - Annuler"
                )

                choix = input(
                    "> "
                )

                if choix.lower() == "q":

                    return None

                if choix.lower() == "a":

                    add_instrument(
                        project
                    )

                    continue

                if choix.lower() == "t":

                    suggestions = {}
                    show_suggestions = False

                    continue

                try:

                    index = int(
                        choix
                    ) - 1

                    preset = suggestion_list[
                        index
                    ]

                except (
                    ValueError,
                    IndexError
                ):

                    print(
                        "Choix invalide."
                    )

                    continue

                return ensure_project_instrument(
                    project,
                    preset
                )

        print()
        print("Choisir un instrument")
        print()

        instruments = sorted(
            project.list_instruments(),
            key=lambda item: item[1].get("name", "").lower()
        )

        for index, (instrument_id, instrument) in enumerate(
            instruments,
            start=1
        ):
            marker = "* " if instrument_id == current_id else "  "

            print(
                f"{marker}{index:2} - "
                f"{instrument.get('name', '?'):<25}"
                f"({instrument.get('sf2_bank', '?')}:"
                f"{instrument.get('sf2_program', '?')})"
            )

        print("a - Ajouter un instrument")
        print("q - Annuler")

        choix = input(
            "> "
        )

        if choix.lower() == "q":

            return None

        if choix.lower() == "a":

            add_instrument(
                project
            )

            continue

        try:

            index = int(choix) - 1

            instrument_id, instrument = instruments[index]

        except (ValueError, IndexError):

            print("Choix invalide")

            return None

        result = dict(instrument)

        result["id"] = instrument_id

        return result

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

        mix = project.get_mix(
            error["mix_id"]
        )

        part = mix["parts"][
            error["part_id"]
        ]

        instrument = choose_instrument(
            project,
            part,
            fusion_name=part.get(
                "fusion_name"
            )
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

def edit_fusion_name(
    data
):

    current_name = data.get(
        "fusion_name",
        ""
    )

    print()
    print(
        "Nom Fusion actuel :",
        current_name
        if current_name
        else "Non défini"
    )

    name = input(
        "Nom Fusion (Entrée = conserver, - = effacer) : "
    ).strip()

    if not name:

        return False

    if name == "-":

        data.pop(
            "fusion_name",
            None
        )

        return True

    data["fusion_name"] = name

    return True

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

            print_error_messages(
                errors
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

            print_error_messages(
                errors
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

        errors = project.validate_mix(
            mix_id
        )

        if errors:

            print_validation_errors(
                project,
                errors
            )

            print()

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

                print("1 - Modifier instrument")
                print("2 - Modifier paramètres PART")
                print("3 - Modifier nom Fusion")
                print("q - Annuler")

                choix = input("> ")

                if choix == "1":

                    instrument = choose_instrument(
                        project,
                        part,
                        fusion_name=part.get(
                            "fusion_name"
                        )
                    )

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

                elif choix == "3":

                    if edit_fusion_name(
                        part
                    ):

                        if project.save_safe():

                            print(
                                "Nom Fusion modifié."
                            )

                        else:

                            print(
                                "⚠ Sauvegarde non effectuée."
                            )

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

def read_note(
    prompt,
    minimum=0,
    maximum=127
):

    while True:

        value = input(
            prompt
        ).strip()

        if not value:

            return None

        note = note_number(
            value
        )

        if note is None:

            print(
                "Note invalide."
            )

            continue

        if note < minimum:

            print(
                "Note minimale :",
                note_name(minimum)
            )

            continue

        if note > maximum:

            print(
                "Note maximale :",
                note_name(maximum)
            )

            continue

        return note

def validate_part_updates(
    part,
    updates
):

    test = dict(part)

    test.update(
        updates
    )

    if not (
        1 <= test.get(
            "midi_channel",
            1
        )
        <= 16
    ):

        print()

        print(
            "Canal MIDI invalide (1-16)."
        )

        return False

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

def edit_part_values(
    part,
    part_id
):

    updates = {}

    print()
    print("====================")
    print("Paramètres PART", part_id)
    print("====================")

    print(
        "Canal MIDI :",
        part.get(
            "midi_channel",
            "?"
        )
    )

    print(
        "Plage      :",
        note_name(
            part.get(
                "note_min",
                0
            )
        ),
        "-",
        note_name(
            part.get(
                "note_max",
                127
            )
        )
    )

    print(
        "Velocity   :",
        part.get(
            "velocity_min",
            0
        ),
        "-",
        part.get(
            "velocity_max",
            127
        )
    )

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
        note_name(
            part.get(
                "note_min",
                0
            )
        )
    )

    value = read_note(
        "Nouvelle note min (Entrée = conserver) : "
    )

    if value is not None:

        updates["note_min"] = value

    effective_note_min = updates.get(
        "note_min",
        part.get(
            "note_min",
            0
        )
    )

    print()

    print(
        "Note max actuelle :",
        note_name(
            part.get(
                "note_max",
                0
            )
        )
    )

    value = read_note(
        "Nouvelle note max (Entrée = conserver) : ",
        minimum=effective_note_min
    )

    if value is not None:

        updates["note_max"] = value

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

        return None

    if not validate_part_updates(
        part,
        updates
    ):

        print(
            "PART non modifiée."
        )

        return None

    return updates

def edit_part_parameters(
    project,
    mix_id,
    part_id,
    part
):

    updates = edit_part_values(
        part,
        part_id
    )

    if not updates:

        return

    success, messages = project.update_part(
        mix_id,
        part_id,
        updates
    )

    if not success:

        print(
            "PART non modifiée."
        )

        for message in messages:

            print(
                "-",
                message
            )

        return

    if project.save_safe():

        print(
            "PART modifiée."
        )

    else:

        print(
            "⚠ Sauvegarde non effectuée."
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
                "sf2_program",
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

def list_mixes(
    project,
    status_filter=None
):

    print()

    print(
        "Mix disponibles :",
        project.count_mixes()
    )

    diagnostic = {
        item["mix"]: item
        for item in project.get_mix_diagnostic()
    }

    print()

    print(
        f"{'ID':<10}"
        f"{'Nom':<30}"
        f"{'PARTS':>7}"
        f"{'Configurées':>14}"
        f"{'État':>16}"
    )

    print(
        "-" * 77
    )

    displayed = []

    for mix_id, mix in project.iter_mixes():

        mix_diag = diagnostic.get(
            mix_id,
            {}
        )

        parts_diag = mix_diag.get(
            "parts",
            []
        )

        fusion_valid = all(
            part.get(
                "fusion_valid",
                False
            )
            for part in parts_diag
        )

        configured = sum(
            1
            for part in parts_diag
            if part.get(
                "qsynth_configured",
                False
            )
        )

        total = len(
            parts_diag
        )

        if not fusion_valid:

            state_code = "error"

        elif (
            total == 0
            or
            configured < total
        ):

            state_code = "unconfigured"

        else:

            state_code = "ok"

        if (
            status_filter is not None
            and
            state_code != status_filter
        ):

            continue

        displayed.append(
            mix_id
        )

        if state_code == "error":

            state = "Erreur Fusion"

        elif state_code == "unconfigured":

            state = "À configurer"

        elif mix_diag.get(
            "shared_channels"
        ):

            state = "Canaux partagés"

        else:

            state = "OK"

        print(
            f"{mix_id:<10}"
            f"{mix.get('name', ''):<30}"
            f"{total:>7}"
            f"{f'{configured}/{total}':>14}"
            f"{state:>16}"
        )
    if len(displayed) == 0:

        if status_filter == "error":

            print("Aucun MIX en erreur.")

        elif status_filter == "unconfigured":

            print("Aucun MIX à configurer.")

        else:

            print("Aucun MIX.")

        return

    return displayed

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

def list_instruments(
    project
):

    instruments = sorted(
        project.list_instruments(),
        key=lambda item:
            item[1].get(
                "name",
                ""
            ).lower()
    )

    print()

    if not instruments:

        print(
            "Aucun instrument."
        )

        return

    print(
        "Instruments :",
        len(instruments)
    )

    print()

    print(
        f"{'Nom':<25}"
        f"{'Identifiant':<20}"
        f"{'Bank':>6}"
        f"{'Program':>10}"
    )

    print(
        "-" * 61
    )

    for instrument_id, instrument in instruments:

        print(
            f"{instrument.get('name', '?'):<25}"
            f"{instrument_id:<20}"
            f"{instrument.get('sf2_bank', '?'):>6}"
            f"{instrument.get('sf2_program', '?'):>10}"
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
        ).strip()

        if not instrument_id:

            print(
                "Identifiant requis."
            )

            return

        if project.get_instrument(
            instrument_id
        ):

            print(
                "Identifiant déjà utilisé."
            )

            return

        name = input(
            "Nom : "
        ).strip()

        if not name:

            print(
                "Nom requis."
            )

            return

        bank = read_int(
            "SF2 Bank : ",
            0,
            128
        )

        if bank is None:

            print(
                "Ajout annulé."
            )

            return

        program = read_int(
            "SF2 Program : ",
            0,
            127
        )

        if program is None:

            print(
                "Ajout annulé."
            )

            return

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
            "Instrument déjà présent."
        )

        return

    if project.save_safe():

        print(
            "Instrument ajouté :",
            name
        )

    else:

        print(
            "⚠ Sauvegarde non effectuée."
        )

def delete_instrument(
    project
):

    selected = choose_instrument(
        project
    )

    if selected is None:

        return

    instrument_id = selected["id"]

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

    # choisir instrument

    selected = choose_instrument(
        project
    )

    if selected is None:

        return

    instrument_id = selected["id"]

    instrument = project.get_instrument(
        instrument_id
    )

    if instrument is None:

        print(
            "Instrument inconnu."
        )

        return

    name = input(
        f"Nom [{instrument['name']}] : "
    )

    bank = read_int(
        f"Bank [{instrument['sf2_bank']}] : ",
        0,
        128
    )

    program = read_int(
        f"Program [{instrument['sf2_program']}] : ",
        0,
        127
    )

    updated = {
        "name":
            name or instrument["name"],

        "sf2_bank":
            instrument["sf2_bank"]
            if bank is None
            else bank,

        "sf2_program":
            instrument["sf2_program"]
            if program is None
            else program
    }

    if not project.update_instrument(
        instrument_id,
        updated
    ):

        print(
            "Modification refusée."
        )

        return

    if project.save_safe():

        print(
            "Instrument modifié."
        )

    else:

        print(
            "⚠ Sauvegarde non effectuée."
        )

def validate_and_repair(project):

    while True:

        errors = project.validate()

        if not errors:

            return

        print_validation_errors(
            project,
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

def list_programs(
    project,
    status_filter=None
):

    programs = list(
        project.iter_programs()
    )

    diagnostic = {
        item["program"]: item
        for item in project.get_program_diagnostic()
    }

    print()

    if not programs:

        print("Aucun PROGRAM.")

        return

    filtered_programs = []

    for program_id, program in programs:

        status = diagnostic.get(
            program_id,
            {}
        )

        if not status.get(
            "fusion_valid",
            False
        ):

            state = "error"

        elif not status.get(
            "qsynth_configured",
            False
        ):

            state = "unconfigured"

        else:

            state = "ok"

        if (
            status_filter is None
            or
            state == status_filter
        ):

            filtered_programs.append(
                (
                    program_id,
                    program,
                    state
                )
            )

    print(
        "PROGRAMS :",
        len(filtered_programs)
    )

    print()

    print(
        f"{'ID':<10}"
        f"{'Nom':<28}"
        f"{'CH':>4}"
        f"{'Bank':>8}"
        f"{'Program':>10}"
        f"  {'Instrument':<22}"
        f"État"
    )

    print(
        "-" * 100
    )

    displayed = []

    for program_id, program, state_code in filtered_programs:

        part = program.get(
            "parts",
            {}
        ).get(
            "1",
            {}
        )

        instrument_name = (
            "Non configuré"
        )

        instrument_id = part.get(
            "instrument"
        )

        if instrument_id:

            instrument = project.get_instrument(
                instrument_id
            )

            if instrument:

                instrument_name = instrument.get(
                    "name",
                    instrument_id
                )

        status = diagnostic.get(
            program_id,
            {}
        )

        if state_code == "error":

            state = "Erreur Fusion"

        elif state_code == "unconfigured":

            state = "À configurer"

        else:

            state = "OK"

        print(
            f"{program_id:<10}"
            f"{program.get('name', ''):<28}"
            f"{part.get('midi_channel', '?'):>4}"
            f"{part.get('bank', '?'):>8}"
            f"{part.get('program', '?'):>10}"
            f"  {instrument_name:<22}"
            f"{state}"
        )

        displayed.append(
            program_id
        )

    if len(filtered_programs) == 0:

        if status_filter == "error":

            print("Aucun PROGRAM en erreur.")

        elif status_filter == "unconfigured":

            print("Aucun PROGRAM à configurer.")

        else:

            print("Aucun PROGRAM.")

        return

    return displayed

def edit_program(
    project,
    program_id
):

    program = project.get_program(
        program_id
    )

    if not program:

        print(
            "PROGRAM inconnu."
        )

        return

    errors = project.validate_program(
        program_id
    )

    if errors:

        print_validation_errors(
            project,
            errors
        )

        print()

    part = program.get(
        "parts",
        {}
    ).get(
        "1"
    )

    if not part:

        print(
            "PART absente."
        )

        return

    print()

    print(
        "PROGRAM :",
        program_id,
        "-",
        program.get(
            "name",
            ""
        )
    )

    project.print_part(
        "1",
        part
    )

    while True:

        print()
        print("====================")
        print("Edition PROGRAM")
        print("====================")
        print("1 - Modifier l'instrument")
        print("2 - Modifier les paramètres")
        print("q - Retour")

        choice = input(
            "> "
        )

        if choice == "1":

            instrument = choose_instrument(
                project,
                part,
                fusion_name=program.get(
                    "name"
                )
            )

            if instrument is None:

                continue

            part["instrument"] = instrument["id"]

            if project.save_safe():

                print(
                    "Instrument affecté."
                )

        elif choice == "2":

            updates = edit_part_values(
                part,
                "1"
            )

            if not updates:

                continue

            old_part = dict(
                part
            )

            part.update(
                updates
            )

            errors = project.validate_program(
                program_id
            )

            if errors:

                part.clear()
                part.update(
                    old_part
                )

                print(
                    "PROGRAM non modifié."
                )

                print_error_messages(
                    errors
                )

                continue

            if project.save_safe():

                print(
                    "PROGRAM modifié."
                )

        elif choice.lower() == "q":

            return

def list_songs(
    project,
    status_filter=None
):

    songs = list(
        project.iter_songs()
    )

    diagnostic = {
        item["song"]: item
        for item in project.get_song_diagnostic()
    }

    if not songs:

        print("Aucune SONG.")

        return

    print()

    displayed = []

    for song_id, song in songs:

        song_diag = diagnostic.get(
            song_id,
            {}
        )

        channels_diag = song_diag.get(
            "channels",
            []
        )

        configured = sum(
            1
            for channel in channels_diag
            if channel.get(
                "qsynth_configured",
                False
            )
        )

        total = len(
            channels_diag
        )

        fusion_valid = all(
            channel.get(
                "fusion_valid",
                False
            )
            for channel in channels_diag
        )

        if not fusion_valid:

            state_code = "error"

        elif (
            total == 0
            or
            configured < total
        ):

            state_code = "unconfigured"

        else:

            state_code = "ok"

        #
        # Filtre AVANT affichage
        #
        if (
            status_filter is not None
            and
            state_code != status_filter
        ):

            continue

        displayed.append(
            song_id
        )
        #
        # Seulement ici on affiche la SONG
        #
        song_name = song.get(
            "name",
            ""
        )

        if (
            song_name
            and
            song_name != song_id
        ):

            print(
                "SONG",
                song_id,
                "-",
                song_name
            )

        else:

            print(
                "SONG",
                song_id
            )

        if state_code == "error":

            state = "Erreur Fusion"

        elif state_code == "unconfigured":

            state = "À configurer"

        else:

            state = "OK"

        print(
            f" {configured}/{total} canaux configurés - {state}"
        )

        print()

        # boucle des canaux...

        print()

        for channel_id, channel in song.get(
            "channels",
            {}
        ).items():

            instrument = project.resolve_part_instrument(
                channel
            )

            instrument_name = (
                instrument.get(
                    "name",
                    "Non configuré"
                )
                if instrument
                else "Non configuré"
            )

            print(
                f" CH {str(channel_id):<2}"
                f" → {instrument_name:<20}"
                f" | Bank {channel.get('bank', '?'):>3}"
                f" | Program {channel.get('program', '?'):>3}"
            )

        print()

    if len(displayed) == 0:

        if status_filter == "error":

            print(
                "Aucune SONG en erreur."
            )

        elif status_filter == "unconfigured":

            print(
                "Aucune SONG à configurer."
            )

        else:

            print(
                "Aucune SONG."
            )

        return

    print()

    return displayed

def edit_song(
    project,
    song_id
):
    def edit_song_channel_parameters(
        project,
        song_id,
        channel_id,
        channel
    ):

        updates = {}

        print()
        print("====================")
        print(
            "Paramètres canal",
            channel_id
        )
        print("====================")

        print(
            "Bank       :",
            channel.get(
                "bank",
                "?"
            )
        )

        print(
            "Program    :",
            channel.get(
                "program",
                "?"
            )
        )

        print(
            "Volume     :",
            channel.get(
                "volume",
                "?"
            )
        )

        print(
            "Pan        :",
            channel.get(
                "pan",
                "?"
            )
        )

        print(
            "Expression :",
            channel.get(
                "expression",
                "?"
            )
        )

        print(
            "Reverb     :",
            channel.get(
                "reverb",
                "?"
            )
        )

        print(
            "Chorus     :",
            channel.get(
                "chorus",
                "?"
            )
        )

        print()

        value = read_int(
            "Nouveau Bank (Entrée = conserver) : ",
            0,
            16383
        )

        if value is not None:

            updates["bank"] = value

        value = read_int(
            "Nouveau Program (Entrée = conserver) : ",
            0,
            127
        )

        if value is not None:

            updates["program"] = value

        value = read_int(
            "Nouveau Volume (Entrée = conserver) : ",
            0,
            127
        )

        if value is not None:

            updates["volume"] = value

        value = read_int(
            "Nouveau Pan (Entrée = conserver) : ",
            0,
            127
        )

        if value is not None:

            updates["pan"] = value

        value = read_int(
            "Nouvelle Expression (Entrée = conserver) : ",
            0,
            127
        )

        if value is not None:

            updates["expression"] = value

        value = read_int(
            "Nouvelle Reverb (Entrée = conserver) : ",
            0,
            127
        )

        if value is not None:

            updates["reverb"] = value

        value = read_int(
            "Nouveau Chorus (Entrée = conserver) : ",
            0,
            127
        )

        if value is not None:

            updates["chorus"] = value

        if not updates:

            print(
                "Aucune modification."
            )

            return

        old_channel = dict(
            channel
        )

        channel.update(
            updates
        )

        errors = project.validate_song_channel(
            song_id,
            channel_id
        )

        if errors:

            channel.clear()

            channel.update(
                old_channel
            )

            print(
                "Canal SONG non modifié."
            )

            print_error_messages(
                errors
            )

            return

        if project.save_safe():

            print(
                "Canal SONG modifié."
            )

        else:

            channel.clear()

            channel.update(
                old_channel
            )

            print(
                "⚠ Sauvegarde non effectuée."
            )

    song = project.get_song(
        song_id
    )

    if not song:

        print(
            "SONG inconnue."
        )

        return

    errors = project.validate_song(
        song_id
    )

    if errors:

        print_validation_errors(
            project,
            errors
        )

        print()

    channels = song.get(
        "channels",
        {}
    )

    if not channels:

        print(
            "Aucun canal."
        )

        return

    while True:

        print()
        print(
            "SONG :",
            song_id,
            "-",
            song.get(
                "name",
                ""
            )
        )

        print()

        for channel_id, channel in channels.items():

            instrument = project.resolve_part_instrument(
                channel
            )

            print(
                "CH",
                channel_id,
                "-",
                instrument.get(
                    "name",
                    "Non configuré"
                )
                if instrument
                else "Non configuré",
                f"({channel.get('bank', '?')}:"
                f"{channel.get('program', '?')})"
            )

        print()

        channel_id = input(
            "Canal à modifier (q pour quitter) : "
        )

        if channel_id.lower() == "q":

            return

        channel = channels.get(
            channel_id
        )

        if channel is None:

            print(
                "Canal inconnu."
            )

            continue

        print()
        print(
            "Fusion Bank    :",
            channel.get(
                "bank",
                "?"
            )
        )

        print(
            "Fusion Program :",
            channel.get(
                "program",
                "?"
            )
        )

        print()
        print("====================")
        print("Edition canal SONG")
        print("====================")
        print("1 - Modifier l'instrument")
        print("2 - Modifier les paramètres")
        print("3 - Modifier le canal MIDI")
        print("4 - Modifier le nom Fusion")
        print("q - Retour")

        choice = input(
            "> "
        )

        if choice == "1":

            instrument = choose_instrument(
                project,
                channel,
                fusion_name=channel.get(
                    "fusion_name"
                )
            )

            if instrument is None:

                continue

            old_instrument = channel.get(
                "instrument"
            )

            channel[
                "instrument"
            ] = instrument[
                "id"
            ]

            if project.save_safe():

                print(
                    "Instrument affecté."
                )

            else:

                if old_instrument is None:

                    channel.pop(
                        "instrument",
                        None
                    )

                else:

                    channel[
                        "instrument"
                    ] = old_instrument

                print(
                    "⚠ Sauvegarde non effectuée."
                )

        elif choice == "2":

            edit_song_channel_parameters(
                project,
                song_id,
                channel_id,
                channel
            )

        elif choice == "3":

            new_channel = read_int(
                "Nouveau canal MIDI : ",
                1,
                16
            )

            if new_channel is None:

                continue

            new_channel_id = str(
                new_channel
            )

            if new_channel_id == channel_id:

                print(
                    "Canal inchangé."
                )

                continue

            if new_channel_id in channels:

                print(
                    "Canal MIDI déjà utilisé."
                )

                continue

            old_channels = dict(
                channels
            )

            channels[
                new_channel_id
            ] = channels.pop(
                channel_id
            )

            errors = project.validate_song(
                song_id
            )

            if errors:

                channels.clear()

                channels.update(
                    old_channels
                )

                print(
                    "Canal MIDI non modifié."
                )

                print_error_messages(
                    errors
                )

                continue

            if project.save_safe():

                print(
                    "Canal MIDI modifié :",
                    channel_id,
                    "→",
                    new_channel_id
                )

            else:

                channels.clear()

                channels.update(
                    old_channels
                )

                print(
                    "⚠ Sauvegarde non effectuée."
                )

        elif choice == "4":

            if edit_fusion_name(
                channel
            ):

                if project.save_safe():

                    print(
                        "Nom Fusion modifié."
                    )

                else:

                    print(
                        "⚠ Sauvegarde non effectuée."
                    )

        elif choice.lower() == "q":

            continue

def print_project_summary(
    project
):

    summary = project.get_project_diagnostic_summary()

    print()
    print("État du projet")
    print("--------------")

    for label, key in (
        ("MIX", "mixes"),
        ("PROGRAM", "programs"),
        ("SONG", "songs")
    ):

        data = summary[
            key
        ]

        line = (
            f"{label:<8}: "
            f"{data['total']:>3} | "
            f"OK {data['ok']:>2} | "
            f"À configurer {data['unconfigured']:>2} | "
            f"Erreurs {data['error']:>2}"
        )

        if data.get(
            "info",
            0
        ):

            line += (
                f" | Infos {data['info']:>2}"
            )

        print(
            line
        )

def main():

    def mixes_menu(
        project
    ):

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

        while True:

            print()
            print("===================")
            print(" MIX ")
            print("===================")
            print("1 - Liste complète")
            print("2 - À configurer")
            print("3 - En erreur")
            print("4 - Éditer")
            print("5 - Supprimer")
            print("6 - Supprimer les MIX vides")
            print("q - Retour")

            choice = input(
                "> "
            )

            if choice == "1":

                list_mixes(
                    project
                )

            elif choice == "2":

                while True:

                    mix_ids = list_mixes(
                        project,
                        status_filter="unconfigured"
                    )

                    if not mix_ids:

                        break

                    print()

                    mix_id = input(
                        "MIX à éditer (Entrée = retour) : "
                    ).strip()

                    if not mix_id:

                        break

                    if mix_id not in mix_ids:

                        print(
                            "MIX non présent dans cette liste."
                        )

                        continue

                    edit_mix(
                        project,
                        mix_id
                    )

            elif choice == "3":

                while True:

                    mix_ids = list_mixes(
                        project,
                        status_filter="error"
                    )

                    if not mix_ids:

                        break

                    print()

                    mix_id = input(
                        "MIX à éditer (Entrée = retour) : "
                    ).strip()

                    if not mix_id:

                        break

                    if mix_id not in mix_ids:

                        print(
                            "MIX non présent dans cette liste."
                        )

                        continue

                    edit_mix(
                        project,
                        mix_id
                    )

            elif choice == "4":

                mix_id = input(
                    "Numéro du Mix (ex: 2:4) : "
                )

                edit_mix(
                    project,
                    mix_id
                )

            elif choice == "5":

                delete_mix_menu()

            elif choice == "6":

                delete_empty_mixes_menu()

            elif choice.lower() == "q":

                return

    def programs_menu(project):

        def rename_program_menu():

            program_id = input(
                "PROGRAM à renommer : "
            )

            program = project.get_program(
                program_id
            )

            if not program:

                print(
                    "PROGRAM inconnu."
                )

                return

            print()

            print(
                "Nom actuel :",
                program.get(
                    "name",
                    program_id
                )
            )

            new_name = input(
                "Nouveau nom : "
            ).strip()

            if not new_name:

                return

            ok, errors = project.rename_program(
                program_id,
                new_name
            )

            if not ok:

                print(
                    "Renommage refusé."
                )

                print_error_messages(
                    errors
                )

                return

            if project.save_safe():

                print(
                    "PROGRAM renommé."
                )

            else:

                print(
                    "⚠ Sauvegarde non effectuée."
                )

        def delete_program_menu():

            program_id = input(
                "PROGRAM à supprimer : "
            )

            program = project.get_program(
                program_id
            )

            if not program:

                print(
                    "PROGRAM inconnu."
                )

                return

            print()
            print(
                "Suppression du PROGRAM :"
            )

            print(
                "ID :",
                program_id
            )

            print(
                "Nom :",
                program.get(
                    "name",
                    ""
                )
            )

            print(
                "PARTS :",
                len(
                    program.get(
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

            ok, errors = project.delete_program(
                program_id
            )

            if not ok:

                print(
                    "Suppression refusée."
                )

                print_error_messages(
                    errors
                )

                return

            if project.save_safe():

                print(
                    "PROGRAM supprimé."
                )

            else:

                print(
                    "⚠ Sauvegarde non effectuée."
                )

        while True:

            print()
            print("===================")
            print(" PROGRAMS ")
            print("===================")
            print("1 - Liste complète")
            print("2 - À configurer")
            print("3 - En erreur")
            print("4 - Éditer")
            print("5 - Renommer")
            print("6 - Supprimer")
            print("q - Retour")

            choice = input(
                "> "
            )

            if choice == "1":

                list_programs(
                    project
                )

            elif choice == "2":

                while True:

                    program_ids = list_programs(
                        project,
                        status_filter="unconfigured"
                    )

                    if not program_ids:

                        break

                    print()

                    program_id = input(
                        "PROGRAM à éditer (Entrée = retour) : "
                    ).strip()

                    if not program_id:

                        break

                    if program_id not in program_ids:

                        print(
                            "PROGRAM non présent dans cette liste."
                        )

                        continue

                    edit_program(
                        project,
                        program_id
                    )

            elif choice == "3":

                while True:

                    program_ids = list_programs(
                        project,
                        status_filter="error"
                    )

                    if not program_ids:

                        break

                    print()

                    program_id = input(
                        "PROGRAM à éditer (Entrée = retour) : "
                    ).strip()

                    if not program_id:

                        break

                    if program_id not in program_ids:

                        print(
                            "PROGRAM non présent dans cette liste."
                        )

                        continue

                    edit_program(
                        project,
                        program_id
                    )

            elif choice == "4":

                program_id = input(
                    "PROGRAM à éditer : "
                )

                edit_program(
                    project,
                    program_id
                )

            elif choice == "5":

                rename_program_menu()

            elif choice == "6":

                delete_program_menu()

            elif choice.lower() == "q":

                return

    def songs_menu(
        project
    ):

        def rename_song_menu():

            song_id = input(
                "SONG à renommer : "
            )

            song = project.get_song(
                song_id
            )

            if not song:

                print(
                    "SONG inconnue."
                )

                return

            print()

            print(
                "Nom actuel :",
                song.get(
                    "name",
                    song_id
                )
            )

            new_name = input(
                "Nouveau nom : "
            ).strip()

            if not new_name:

                return

            ok, errors = project.rename_song(
                song_id,
                new_name
            )

            if not ok:

                print(
                    "Renommage refusé."
                )

                print_error_messages(
                    errors
                )

                return

            if project.save_safe():

                print(
                    "SONG renommée."
                )

        def delete_song_menu():

            song_id = input(
                "SONG à supprimer : "
            )

            song = project.get_song(
                song_id
            )

            if not song:

                print(
                    "SONG inconnue."
                )

                return

            print()
            print(
                "Suppression de la SONG :"
            )

            print(
                "ID :",
                song_id
            )

            print(
                "Nom :",
                song.get(
                    "name",
                    ""
                )
            )

            print(
                "Canaux :",
                len(
                    song.get(
                        "channels",
                        {}
                    )
                )
            )

            rep = input(
                "Confirmer suppression ? (o/n) : "
            )

            if rep.lower() != "o":

                return

            ok, errors = project.delete_song(
                song_id
            )

            if not ok:

                print(
                    "Suppression refusée."
                )

                return

            if project.save_safe():

                print(
                    "SONG supprimée."
                )

        while True:

            print()
            print("===================")
            print(" SONG ")
            print("===================")
            print("1 - Liste complète")
            print("2 - À configurer")
            print("3 - En erreur")
            print("4 - Éditer")
            print("5 - Renommer")
            print("6 - Supprimer")
            print("q - Retour")

            choice = input(
                "> "
            )

            if choice == "1":

                list_songs(
                    project
                )

            elif choice == "2":

                while True:

                    song_ids = list_songs(
                        project,
                        status_filter="unconfigured"
                    )

                    if not song_ids:

                        break

                    print()

                    song_id = input(
                        "SONG à éditer (Entrée = retour) : "
                    ).strip()

                    if not song_id:

                        break

                    if song_id not in song_ids:

                        print(
                            "SONG non présente dans cette liste."
                        )

                        continue

                    edit_song(
                        project,
                        song_id
                    )

            elif choice == "3":

                while True:

                    song_ids = list_songs(
                        project,
                        status_filter="error"
                    )

                    if not song_ids:

                        break

                    print()

                    song_id = input(
                        "SONG à éditer (Entrée = retour) : "
                    ).strip()

                    if not song_id:

                        break

                    if song_id not in song_ids:

                        print(
                            "SONG non présente dans cette liste."
                        )

                        continue

                    edit_song(
                        project,
                        song_id
                    )

            elif choice == "4":

                song_id = input(
                    "SONG à éditer : "
                )

                edit_song(
                    project,
                    song_id
                )

            elif choice == "5":

                rename_song_menu()

            elif choice == "6":

                delete_song_menu()

            elif choice.lower() == "q":

                return

    project = FusionProject()

    validate_and_repair(
        project
    )

    while True:

        print()
        print("===================")
        print("Fusion Editor")
        print("===================")

        print_project_summary(
            project
        )
        print()

        print("1 - Gestion MIX")
        print("2 - Gestion PROGRAM")
        print("3 - Gestion SONG")
        print("4 - Gestion Instruments")
        print("q - Quitter")
        choix = input(
            "> "
        )

        if choix == "1":

            mixes_menu(
                project
            )

        elif choix == "2":

            programs_menu(
                project
            )

        elif choix == "3":

            songs_menu(
                project
            )

        elif choix == "4":

            instruments_menu(
                project
            )

        elif choix.lower() == "q":

            break

if __name__ == "__main__":

    main()
