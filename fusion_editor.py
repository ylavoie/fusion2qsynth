#!/usr/bin/env python3

import mido
import time

from fusion_lib import (
    find_fluidsynth_output,
    note_name,
    note_number,
    note_range
)

from fusion_diagnostic import (
    print_validation_errors,
    print_error_messages
)

from fusion_performance import (
    print_mix
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
    preset,
    allowed_errors=None
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

    original_data = project.snapshot()

    ok, errors = project.add_instrument(
        instrument_id,
        instrument
    )

    if not ok:

        print(
            "Instrument non ajouté."
        )

        print_error_messages(
            errors
        )

        return None

    if not project.save_safe(
        allowed_errors=allowed_errors
    ):

        project.restore_snapshot(
            original_data
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
    fusion_name=None,
    fusion_program=None,
    allowed_errors=None
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

            program = fusion_program

            if (
                program is None
                and
                part is not None
            ):

                program = part.get(
                    "program"
                )

            suggestions = get_sf2_suggestions(
                fusion_name,
                program
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
                    "Q - Annuler"
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
                    preset,
                    allowed_errors=allowed_errors
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
        print("Q - Annuler")

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

    if old_instrument["name"] != "Non configuré":

        input(
            "Entrée pour écouter A..."
        )

        play_preview(
            part,
            old_instrument
        )

    else:

        print(
            "Aucun instrument à écouter."
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

        bank = instrument["sf2_bank"]

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

def edit_mix(project,mix_id):

    def test_mix_menu(
        mix
    ):

        while True:

            print()
            print("====================")
            print("Test Mix")
            print("====================")

            print(
                "1 - Tester un canal"
            )

            print(
                "2 - Tous les canaux configurés"
            )

            print(
                "Q - Retour"
            )

            choix = input(
                "> "
            )

            if choix == "1":

                test_mix_channel(
                    project,
                    mix
                )

            elif choix == "2":

                test_mix_channels_all(
                    project,
                    mix
                )

            elif choix.lower() == "q":

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

        allowed_errors = project.get_blocking_errors(
            project.validate()
        )

        ok, errors = project.rename_mix(
            mix_id,
            name
        )

        if ok:

            if project.save_safe(
                allowed_errors=allowed_errors
            ):
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

        allowed_errors = project.get_blocking_errors(
            project.validate()
        )

        ok, errors = project.duplicate_mix(
            mix_id,
            new_mix_id
        )

        if ok:

            if project.save_safe(
                allowed_errors=allowed_errors
            ):
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

        print_mix(
            project,
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
            "4 - Modifier les Canaux"
        )

        print(
            "Q - Retour"
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

            edit_mix_channels(
                project,
                mix_id,
                mix
            )

        elif choix.lower() == "q":

            return

def edit_mix_channels(
    project,
    mix_id,
    mix
):

    channels = mix.get(
        "channels",
        {}
    )

    while True:

        print()
        print("====================")
        print("Canaux du MIX")
        print("====================")

        if not channels:

            print(
                "Aucun canal."
            )

            return

        for channel_id, channel in sorted(
            channels.items(),
            key=lambda item: int(
                item[0]
            )
        ):

            program_id = channel.get(
                "program"
            )

            program_name = None

            if program_id:

                program = project.get_program(
                    program_id
                )

                if program:

                    program_name = program.get(
                        "name"
                    )

            instrument = (
                project.resolve_mix_channel_instrument(
                    channel
                )
            )

            instrument_name = (
                instrument.get(
                    "name",
                    "?"
                )
                if instrument
                else "Non configuré"
            )

            print(
                f"CH {channel_id:>2} | "
                f"PROGRAM {program_id or '?':<7} | "
                f"{program_name or '?':<25} | "
                f"SoundFont : {instrument_name}"
            )

        print()

        channel_id = input(
            "Canal à modifier (q pour quitter) : "
        ).strip()

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

        edit_mix_channel(
            project,
            mix_id,
            channel_id,
            channel
        )

def edit_mix_channel(
    project,
    mix_id,
    channel_id,
    channel
):

    def edit_mix_channel_instrument(
        project,
        mix_id,
        channel_id,
        channel
    ):

        program_id = channel.get(
            "program"
        )

        global_program = None

        if program_id:

            global_program = project.get_program(
                program_id
            )

        fusion_name = None
        fusion_program = None

        if global_program:

            fusion_name = global_program.get(
                "name"
            )

        if program_id:

            try:

                fusion_program = int(
                    program_id.split(
                        ":",
                        1
                    )[1]
                )

            except (
                ValueError,
                IndexError
            ):

                fusion_program = None

        allowed_errors = (
            project.get_blocking_errors(
                project.validate()
            )
        )

        instrument = choose_instrument(
            project,
            channel,
            fusion_name=fusion_name,
            fusion_program=fusion_program,
            allowed_errors=allowed_errors
        )

        if instrument is None:

            return

        allowed_errors = (
            project.get_blocking_errors(
                project.validate()
            )
        )

        original_data = project.snapshot()

        ok, errors = project.update_mix_channel(
            mix_id,
            channel_id,
            {
                "instrument":
                    instrument["id"]
            }
        )

        if not ok:

            print(
                "Instrument local non affecté."
            )

            print_error_messages(
                errors
            )

            return

        if project.save_safe(
            allowed_errors=allowed_errors
        ):

            print(
                "Instrument local affecté."
            )

        else:

            project.restore_snapshot(
                original_data
            )

            print(
                "⚠ Sauvegarde non effectuée."
            )

    def edit_mix_channel_program(
        project,
        mix_id,
        channel_id,
        channel
    ):

        print()
        print(
            "PROGRAM actuel :",
            channel.get(
                "program",
                "Aucun"
            )
        )

        print()
        print(
            "1 - Sélectionner un PROGRAM"
        )
        print(
            "2 - Aucun PROGRAM"
        )
        print(
            "Q - Annuler"
        )

        while True:

            choice = input(
                "> "
            ).strip()

            if choice == "1":

                program_id = choose_program_id(
                    project
                )

                if program_id is None:

                    return

                updates = {
                    "program": program_id
                }

                remove_fields = None

                break

            elif choice == "2":

                updates = None

                remove_fields = [
                    "program"
                ]

                break

            elif choice.lower() == "q":

                return

            print(
                "Choix invalide."
            )

        allowed_errors = (
            project.get_blocking_errors(
                project.validate()
            )
        )

        original_data = project.snapshot()

        ok, errors = project.update_mix_channel(
            mix_id,
            channel_id,
            updates=updates,
            remove_fields=remove_fields
        )

        if not ok:

            print(
                "PROGRAM non modifié."
            )

            print_error_messages(
                errors
            )

            return

        if project.save_safe(
            allowed_errors=allowed_errors
        ):

            print(
                "PROGRAM modifié."
            )

        else:

            project.restore_snapshot(
                original_data
            )

            print(
                "⚠ Sauvegarde non effectuée."
            )

    def edit_mix_channel_ranges(
        project,
        mix_id,
        channel_id,
        channel
    ):

        updates = {}

        print()

        note_min = channel.get(
            "note_min"
        )

        print(
            "Note min actuelle :",
            (
                note_name(note_min)
                if note_min is not None
                else "non spécifiée"
            )
        )

        value = read_note(
            "Nouvelle note min (Entrée = conserver) : "
        )

        if value is not None:

            updates["note_min"] = value

        effective_note_min = updates.get(
            "note_min",
            channel.get(
                "note_min",
                0
            )
        )

        print()

        note_max = channel.get(
            "note_max"
        )

        print(
            "Note max actuelle :",
            (
                note_name(note_max)
                if note_max is not None
                else "non spécifiée"
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
            channel.get(
                "velocity_min",
                "non spécifiée"
            )
        )

        value = read_int(
            "Nouvelle velocity min (Entrée = conserver) : ",
            0,
            127
        )

        if value is not None:

            updates["velocity_min"] = value

        print()

        print(
            "Velocity max :",
            channel.get(
                "velocity_max",
                "non spécifiée"
            )
        )

        value = read_int(
            "Nouvelle velocity max (Entrée = conserver) : ",
            0,
            127
        )

        if value is not None:

            updates["velocity_max"] = value

        if not updates:

            print(
                "Aucune modification."
            )

            return

        allowed_errors = (
            project.get_blocking_errors(
                project.validate()
            )
        )

        original_data = project.snapshot()

        ok, errors = project.update_mix_channel(
            mix_id,
            channel_id,
            updates=updates
        )

        if not ok:

            print(
                "Plages non modifiées."
            )

            print_error_messages(
                errors
            )

            return

        if project.save_safe(
            allowed_errors=allowed_errors
        ):

            print(
                "Plages modifiées."
            )

        else:

            project.restore_snapshot(
                original_data
            )

            print(
                "⚠ Sauvegarde non effectuée."
            )

    def remove_mix_channel_instrument(
        project,
        mix_id,
        channel_id,
        channel
    ):

        if "instrument" not in channel:

            print(
                "Aucun instrument local à supprimer."
            )

            return

        allowed_errors = (
            project.get_blocking_errors(
                project.validate()
            )
        )

        original_data = project.snapshot()

        ok, errors = project.update_mix_channel(
            mix_id,
            channel_id,
            remove_fields=[
                "instrument"
            ]
        )

        if not ok:

            print(
                "Instrument local non supprimé."
            )

            print_error_messages(
                errors
            )

            return

        if project.save_safe(
            allowed_errors=allowed_errors
        ):

            print(
                "Instrument local supprimé."
            )

            instrument = (
                project.resolve_mix_channel_instrument(
                    channel
                )
            )

            print(
                "Instrument effectif :",
                (
                    instrument.get(
                        "name",
                        "?"
                    )
                    if instrument
                    else "Non configuré"
                )
            )

        else:

            project.restore_snapshot(
                original_data
            )

            print(
                "⚠ Sauvegarde non effectuée."
            )

    while True:

        program_id = channel.get(
            "program"
        )

        global_program = None

        if program_id:

            global_program = project.get_program(
                program_id
            )

        fusion_name = None

        if global_program:

            fusion_name = global_program.get(
                "name"
            )

        local_instrument_id = channel.get(
            "instrument"
        )

        local_instrument = None

        if local_instrument_id:

            local_instrument = project.get_instrument(
                local_instrument_id
            )

        effective_instrument = (
            project.resolve_mix_channel_instrument(
                channel
            )
        )

        print()
        print("====================")
        print(
            "Edition canal MIX",
            channel_id
        )
        print("====================")

        print(
            "PROGRAM Fusion :",
            program_id or "?"
        )

        print(
            "Nom Fusion     :",
            fusion_name or "?"
        )

        note_min = channel.get(
            "note_min"
        )

        note_max = channel.get(
            "note_max"
        )

        velocity_min = channel.get(
            "velocity_min"
        )

        velocity_max = channel.get(
            "velocity_max"
        )

        print(
            "Zone de notes  :",
            (
                f"{note_name(note_min)} - "
                f"{note_name(note_max)}"
                if (
                    note_min is not None
                    and
                    note_max is not None
                )
                else "?"
            )
        )

        print(
            "Vélocité       :",
            (
                f"{velocity_min} - "
                f"{velocity_max}"
                if (
                    velocity_min is not None
                    and
                    velocity_max is not None
                )
                else "?"
            )
        )

        print(
            "Instrument local :",
            (
                local_instrument.get(
                    "name",
                    local_instrument_id
                )
                if local_instrument
                else "Aucun"
            )
        )

        print(
            "Instrument effectif :",
            (
                effective_instrument.get(
                    "name",
                    "?"
                )
                if effective_instrument
                else "Non configuré"
            )
        )

        print()
        print(
            "1 - Modifier le PROGRAM"
        )

        print(
            "2 - Modifier l'instrument local"
        )

        print(
            "3 - Supprimer l'instrument local"
        )

        print(
            "4 - Modifier les plages"
        )

        print(
            "Q - Retour"
        )

        choice = input(
            "> "
        ).strip()

        if choice == "1":

            edit_mix_channel_program(
                project,
                mix_id,
                channel_id,
                channel
            )

        elif choice == "2":

            edit_mix_channel_instrument(
                project,
                mix_id,
                channel_id,
                channel
            )

        elif choice == "3":

            remove_mix_channel_instrument(
                project,
                mix_id,
                channel_id,
                channel
            )

        elif choice == "4":

            edit_mix_channel_ranges(
                project,
                mix_id,
                channel_id,
                channel
            )

        elif choice.lower() == "q":

            return

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

def choose_fusion_program_bank(
    project,
    current_bank=None
):

    print()

    print(
        "Banque Fusion actuelle :",
        (
            f"{project.get_program_bank_name(current_bank)} "
            f"({current_bank})"
            if current_bank is not None
            else "?"
        )
    )

    print()

    for bank in project.get_program_banks():

        print(
            f"{bank:2} - "
            f"{project.get_program_bank_name(bank)}"
        )

    print()
    print(
        "Entrée - Conserver"
    )

    while True:

        value = input(
            "> "
        ).strip()

        if not value:

            return None

        try:

            bank = int(
                value
            )

        except ValueError:

            print(
                "Choix invalide."
            )

            continue

        if 0 <= bank <= 127:

            return bank

        print(
            "Banque Fusion invalide."
        )

def choose_mix_id(
    project,
    allowed_ids=None
):

    if allowed_ids is None:

        mix_ids = {
            mix_id
            for mix_id, mix
            in project.iter_mixes()
        }

    else:

        mix_ids = set(
            allowed_ids
        )

    if not mix_ids:

        print()
        print(
            "Aucun MIX disponible."
        )

        return None

    while True:

        print()
        print(
            "MIX bank:program"
        )
        print(
            "? - Sélection assistée"
        )
        print(
            "Entrée - Annuler"
        )

        value = input(
            "> "
        ).strip()

        if not value:

            return None

        if value != "?":

            if value in mix_ids:

                return value

            print(
                "MIX inconnu ou non disponible :",
                value
            )

            continue

        #
        # Sélection assistée
        #

        while True:

            banks = sorted({
                int(
                    mix_id.split(
                        ":",
                        1
                    )[0]
                )
                for mix_id in mix_ids
            })

            print()
            print(
                "Banques MIX disponibles"
            )
            print(
                "-----------------------"
            )

            for bank in banks:

                print(
                    f"{bank:3} - "
                    f"{project.get_mix_bank_name(bank)}"
                )

            print()
            print(
                "Entrée - Retour"
            )

            bank_value = input(
                "> "
            ).strip()

            if not bank_value:

                break

            try:

                bank = int(
                    bank_value
                )

            except ValueError:

                print(
                    "Choix invalide."
                )

                continue

            if bank not in banks:

                print(
                    "Banque MIX non disponible."
                )

                continue

            while True:

                available = []

                for mix_id in mix_ids:

                    bank_text, program_text = (
                        mix_id.split(
                            ":",
                            1
                        )
                    )

                    if int(bank_text) != bank:

                        continue

                    available.append(
                        (
                            int(program_text),
                            mix_id
                        )
                    )

                available.sort()

                print()

                print(
                    f"{project.get_mix_bank_name(bank)} "
                    f"({bank})"
                )

                print(
                    "----------------------------"
                )

                for program, mix_id in available:

                    mix = project.get_mix(
                        mix_id
                    )

                    name = (
                        mix.get(
                            "name",
                            mix_id
                        )
                        if mix
                        else mix_id
                    )

                    print(
                        f"{program:3} - {name}"
                    )

                print()
                print(
                    "Entrée - Retour"
                )

                program_value = input(
                    "> "
                ).strip()

                if not program_value:

                    break

                try:

                    program = int(
                        program_value
                    )

                except ValueError:

                    print(
                        "Choix invalide."
                    )

                    continue

                mix_id = (
                    f"{bank}:{program}"
                )

                if mix_id not in mix_ids:

                    print(
                        "MIX inconnu ou non disponible :",
                        mix_id
                    )

                    continue

                return mix_id

def choose_program_id(
    project,
    allowed_ids=None
):

    if allowed_ids is None:

        program_ids = {
            program_id
            for program_id, program
            in project.iter_programs()
        }

    else:

        program_ids = {
            str(program_id)
            for program_id in allowed_ids
        }

    if not program_ids:

        print(
            "Aucun PROGRAM disponible."
        )

        return None

    while True:

        print()
        print(
            "PROGRAM bank:program"
        )
        print(
            "? - Sélection assistée"
        )
        print(
            "Entrée - Annuler"
        )

        value = input(
            "> "
        ).strip()

        if not value:

            return None

        #
        # Saisie directe
        #
        if value != "?":

            if value not in program_ids:

                print(
                    "PROGRAM inconnu ou non disponible :",
                    value
                )

                continue

            return value

        #
        # Sélection assistée
        #
        banks = {}

        for program_id in program_ids:

            try:

                bank_str, program_str = (
                    program_id.split(
                        ":",
                        1
                    )
                )

                bank = int(
                    bank_str
                )

                program = int(
                    program_str
                )

            except (
                ValueError,
                AttributeError
            ):

                continue

            banks.setdefault(
                bank,
                []
            ).append(
                (
                    program,
                    program_id
                )
            )

        if not banks:

            print(
                "Aucun PROGRAM disponible."
            )

            continue

        print()
        print(
            "Banques PROGRAM disponibles"
        )
        print(
            "----------------------------"
        )

        for bank in sorted(
            banks
        ):

            print(
                f"{bank:3} - "
                f"{project.get_program_bank_name(bank)}"
            )

        print()
        print(
            "Entrée - Retour"
        )

        bank = read_int(
            "> ",
            0,
            127
        )

        if bank is None:

            continue

        if bank not in banks:

            print(
                "Aucun PROGRAM disponible dans cette banque."
            )

            continue

        programs = sorted(
            banks[bank]
        )

        while True:

            print()
            print(
                project.get_program_bank_name(bank),
                f"({bank})"
            )
            print(
                "----------------------------"
            )

            for program, program_id in programs:

                program_data = project.get_program(
                    program_id
                )

                name = "?"

                if program_data:

                    name = program_data.get(
                        "name",
                        "?"
                    )

                print(
                    f"{program:3} - {name}"
                )

            print()
            print(
                "Entrée - Retour"
            )

            program = read_int(
                "> ",
                0,
                127
            )

            if program is None:

                break

            program_id = (
                f"{bank}:{program}"
            )

            if program_id not in program_ids:

                print(
                    "PROGRAM inconnu ou non disponible :",
                    program_id
                )

                continue

            return program_id

def choose_song_id(
    project,
    allowed_ids=None
):

    if allowed_ids is None:

        song_ids = {
            song_id
            for song_id, song
            in project.iter_songs()
        }

    else:

        song_ids = set(
            allowed_ids
        )

    if not song_ids:

        print()
        print(
            "Aucune SONG disponible."
        )

        return None

    while True:

        print()
        print(
            "SONG"
        )
        print(
            "? - Sélection assistée"
        )
        print(
            "Entrée - Annuler"
        )

        value = input(
            "> "
        ).strip()

        if not value:

            return None

        if value != "?":

            if value in song_ids:

                return value

            print(
                "SONG inconnue ou non disponible :",
                value
            )

            continue

        #
        # Sélection assistée
        #
        while True:

            available = sorted(
                song_ids,
                key=str.casefold
            )

            print()
            print(
                "SONGs disponibles"
            )
            print(
                "-----------------"
            )

            for index, song_id in enumerate(
                available,
                start=1
            ):

                song = project.get_song(
                    song_id
                )

                name = (
                    song.get(
                        "name",
                        song_id
                    )
                    if song
                    else song_id
                )

                if (
                    name
                    and
                    name != song_id
                ):

                    label = (
                        f"{song_id} - {name}"
                    )

                else:

                    label = song_id

                print(
                    f"{index:2} - {label}"
                )

            print()
            print(
                "Entrée - Retour"
            )

            choice = input(
                "> "
            ).strip()

            if not choice:

                break

            try:

                index = int(
                    choice
                )

            except ValueError:

                print(
                    "Choix invalide."
                )

                continue

            if not (
                1 <= index <= len(available)
            ):

                print(
                    "Choix invalide."
                )

                continue

            return available[
                index - 1
            ]

def edit_part_values(
    project,
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

    bank = part.get(
        "bank"
    )

    print(
        "Fusion Bank :",
        (
            f"{project.get_program_bank_name(bank)} ({bank})"
            if bank is not None
            else "?"
        )
    )

    print(
        "Fusion Prog :",
        part.get(
            "program",
            "?"
        )
    )

    print(
        "Plage      :",
        note_range(
            part.get(
                "note_min",
                None
            ),
            part.get(
                "note_max",
                None
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

    if value is not None:

        updates["midi_channel"] = value

    print()

    bank = part.get("bank")

    print(
        "Fusion Bank actuelle :",
        (
            f"{project.get_program_bank_name(bank)} ({bank})"
            if bank is not None
            else "?"
        )
    )

    value = choose_fusion_program_bank(
        project,
        bank
    )

    if value is not None:

        updates["bank"] = value

    print()

    print(
        "Fusion Program actuel :",
        part.get(
            "program",
            "?"
        )
    )

    value = read_int(
        "Nouveau Fusion Program (Entrée = conserver) : ",
        0,
        127
    )

    if value is not None:

        updates["program"] = value

    print()

    note_min = part.get("note_min")

    print(
        "Note min actuelle :",
        (
            note_name(note_min)
            if note_min is not None
            else "non spécifiée (défaut C-1)"
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

    note_max = part.get("note_max")

    print(
        "Note max actuelle :",
        (
            note_name(note_max)
            if note_max is not None
            else "non spécifiée (défaut G9)"
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

    if value is not None:

        updates["velocity_min"] = value

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

    if value is not None:

        updates["velocity_max"] = value

    if not updates:

        print(
            "Aucune modification."
        )

        return None

    return updates

def send_midi_message(
    out,
    message
):

    try:

        out.send(
            message
        )

        return True

    except Exception as error:

        print()

        print(
            "Erreur MIDI :",
            error
        )

        return False

def stop_midi_test(
    out,
    channels,
    active_notes
):

    #
    # NOTE_OFF explicites
    #
    for midi_channel, note in list(
        active_notes
    ):

        send_midi_message(
            out,
            mido.Message(
                "note_off",
                channel=midi_channel,
                note=note,
                velocity=0
            )
        )

    active_notes.clear()

    #
    # Nettoyage des contrôleurs
    #
    for midi_channel in channels:

        send_midi_message(
            out,
            mido.Message(
                "control_change",
                channel=midi_channel,
                control=64,
                value=0
            )
        )

        send_midi_message(
            out,
            mido.Message(
                "control_change",
                channel=midi_channel,
                control=123,
                value=0
            )
        )

        send_midi_message(
            out,
            mido.Message(
                "control_change",
                channel=midi_channel,
                control=120,
                value=0
            )
        )

def test_mix_channel(
    project,
    mix
):

    channels = mix.get(
        "channels",
        {}
    )

    if not channels:

        print(
            "Aucun canal."
        )

        return

    print()

    print(
        "Canaux disponibles :"
    )

    for channel_id, channel in sorted(
        channels.items(),
        key=lambda item: int(
            item[0]
        )
    ):

        instrument = (
            project.resolve_mix_channel_instrument(
                channel
            )
        )

        print(
            "CH",
            channel_id,
            "-",
            (
                instrument.get(
                    "name",
                    "?"
                )
                if instrument
                else "Non configuré"
            )
        )

    print()

    channel_id = input(
        "Canal à tester : "
    ).strip()

    channel = channels.get(
        channel_id
    )

    if channel is None:

        print(
            "Canal inconnu."
        )

        return

    instrument = (
        project.resolve_mix_channel_instrument(
            channel
        )
    )

    if not instrument:

        print(
            "Canal non configuré."
        )

        return

    port_name = (
        find_fluidsynth_output()
    )

    if not port_name:

        print(
            "FluidSynth introuvable"
        )

        return

    midi_channel = (
        int(channel_id) - 1
    )

    bank = instrument.get(
        "sf2_bank",
        0
    )

    program = instrument.get(
        "sf2_program",
        0
    )

    if not 0 <= bank <= 16383:

        print(
            "Bank SF2 invalide :",
            bank
        )

        return

    if not 0 <= program <= 127:

        print(
            "Program SF2 invalide :",
            program
        )

        return

    bank_msb = bank // 128
    bank_lsb = bank % 128

    print()

    print(
        "CH",
        channel_id,
        "-",
        instrument["name"]
    )

    input(
        "Entrée pour jouer..."
    )

    notes = [
        60,
        64,
        67,
        72
    ]

    active_notes = set()

    try:

        with mido.open_output(
            port_name
        ) as out:

            try:

                if not send_midi_message(
                    out,
                    mido.Message(
                        "control_change",
                        channel=midi_channel,
                        control=0,
                        value=bank_msb
                    )
                ):

                    return

                if not send_midi_message(
                    out,
                    mido.Message(
                        "control_change",
                        channel=midi_channel,
                        control=32,
                        value=bank_lsb
                    )
                ):

                    return

                if not send_midi_message(
                    out,
                    mido.Message(
                        "program_change",
                        channel=midi_channel,
                        program=program
                    )
                ):

                    return

                for note in notes:

                    if not send_midi_message(
                        out,
                        mido.Message(
                            "note_on",
                            channel=midi_channel,
                            note=note,
                            velocity=70
                        )
                    ):

                        break

                    active_notes.add(
                        (
                            midi_channel,
                            note
                        )
                    )

                    time.sleep(
                        0.5
                    )

                    if not send_midi_message(
                        out,
                        mido.Message(
                            "note_off",
                            channel=midi_channel,
                            note=note,
                            velocity=0
                        )
                    ):

                        break

                    active_notes.discard(
                        (
                            midi_channel,
                            note
                        )
                    )

            except KeyboardInterrupt:

                print()
                print(
                    "Test interrompu."
                )

            finally:

                stop_midi_test(
                    out,
                    {
                        midi_channel
                    },
                    active_notes
                )

    except Exception as error:

        print()

        print(
            "Erreur lors de l'accès au port MIDI :",
            error
        )

def test_mix_channels_all(
    project,
    mix
):

    port_name = (
        find_fluidsynth_output()
    )

    if not port_name:

        print(
            "FluidSynth introuvable"
        )

        return

    channels = mix.get(
        "channels",
        {}
    )

    if not channels:

        print(
            "Aucun canal."
        )

        return

    notes = [
        60,
        64,
        67,
        72
    ]

    active_channels = []
    active_notes = set()

    try:

        with mido.open_output(
            port_name
        ) as out:

            active_channels = []

            try:

                #
                # Préparation des instruments
                #
                for channel_id, channel in sorted(
                    channels.items(),
                    key=lambda item: int(
                        item[0]
                    )
                ):

                    instrument = (
                        project.resolve_mix_channel_instrument(
                            channel
                        )
                    )

                    if not instrument:

                        print(
                            "CH",
                            channel_id,
                            "- Non configuré"
                        )

                        continue

                    midi_channel = (
                        int(channel_id) - 1
                    )

                    bank = instrument.get(
                        "sf2_bank",
                        0
                    )

                    program = instrument.get(
                        "sf2_program",
                        0
                    )

                    if not 0 <= bank <= 16383:

                        continue

                    if not 0 <= program <= 127:

                        continue

                    bank_msb = (
                        bank // 128
                    )

                    bank_lsb = (
                        bank % 128
                    )

                    if not send_midi_message(
                        out,
                        mido.Message(
                            "control_change",
                            channel=midi_channel,
                            control=0,
                            value=bank_msb
                        )
                    ):

                        break

                    if not send_midi_message(
                        out,
                        mido.Message(
                            "control_change",
                            channel=midi_channel,
                            control=32,
                            value=bank_lsb
                        )
                    ):

                        break

                    if not send_midi_message(
                        out,
                        mido.Message(
                            "program_change",
                            channel=midi_channel,
                            program=program
                        )
                    ):

                        break

                    active_channels.append(
                        (
                            channel_id,
                            midi_channel,
                            instrument
                        )
                    )

                if active_channels:

                    input(
                        "Entrée pour jouer..."
                    )

                    for note in notes:

                        send_failed = False

                        for (
                            channel_id,
                            midi_channel,
                            instrument
                        ) in active_channels:

                            if not send_midi_message(
                                out,
                                mido.Message(
                                    "note_on",
                                    channel=midi_channel,
                                    note=note,
                                    velocity=70
                                )
                            ):

                                send_failed = True

                                break

                            active_notes.add(
                                (
                                    midi_channel,
                                    note
                                )
                            )

                        if send_failed:

                            break

                        time.sleep(
                            0.5
                        )

                        for (
                            channel_id,
                            midi_channel,
                            instrument
                        ) in active_channels:

                            if not send_midi_message(
                                out,
                                mido.Message(
                                    "note_off",
                                    channel=midi_channel,
                                    note=note,
                                    velocity=0
                                )
                            ):

                                send_failed = True

                                break

                            active_notes.discard(
                                (
                                    midi_channel,
                                    note
                                )
                            )

                        if send_failed:

                            break

            except KeyboardInterrupt:

                print()
                print(
                    "Test interrompu."
                )

            finally:

                stop_midi_test(
                    out,
                    {
                        midi_channel
                        for (
                            channel_id,
                            midi_channel,
                            instrument
                        ) in active_channels
                    },
                    active_notes
                )

    except Exception as error:

        print()

        print(
            "Erreur lors de l'accès au port MIDI :",
            error
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
        f"{'Canaux':>7}"
        f"{'Configurés':>14}"
        f"{'État':>24}"
    )

    print(
        "-" * 85
    )

    displayed = []

    for mix_id, mix in project.iter_mixes():

        mix_diag = diagnostic.get(
            mix_id,
            {}
        )

        units = mix_diag.get(
            "channels",
            []
        )

        total = len(
            units
        )

        valid = sum(
            1
            for unit in units
            if unit.get(
                "fusion_valid",
                False
            )
        )

        configured = sum(
            1
            for unit in units
            if unit.get(
                "soundfont_configured",
                False
            )
        )

        #
        # État de configuration
        #
        if valid < total:

            state_code = "error"

        elif total == 0:

            state_code = "unconfigured"

        elif configured == 0:

            state_code = "unconfigured"

        elif configured < total:

            state_code = "partial"

        else:

            state_code = "configured"

        if status_filter == "unconfigured":

            if state_code not in (
                "unconfigured",
                "partial"
            ):

                continue

        elif (
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

        elif state_code == "partial":

            state = "Partiellement configuré"

        else:

            state = "OK"

        print(
            f"{mix_id:<10}"
            f"{mix.get('name', ''):<30}"
            f"{total:>7}"
            f"{f'{configured}/{total}':>14}"
            f"{state:>24}"
        )

    if len(
        displayed
    ) == 0:

        if status_filter == "error":

            print(
                "Aucun MIX en erreur."
            )

        elif status_filter == "unconfigured":

            print(
                "Aucun MIX à configurer."
            )

        elif status_filter == "partial":

            print(
                "Aucun MIX partiellement configuré."
            )

        elif status_filter == "configured":

            print(
                "Aucun MIX configuré."
            )

        else:

            print(
                "Aucun MIX."
            )

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
        print("Q - Retour")

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

    allowed_errors = project.get_blocking_errors(
        project.validate()
    )

    original_data = project.snapshot()

    ok, errors = project.add_instrument(
        instrument_id,
        {
            "name": name,
            "sf2_bank": bank,
            "sf2_program": program
        }
    )

    if not ok:

        print(
            "Instrument non ajouté."
        )

        print_error_messages(
            errors
        )

        return

    if project.save_safe(
        allowed_errors=allowed_errors
    ):

        print(
            "Instrument ajouté."
        )

    else:

        project.restore_snapshot(
            original_data
        )

        print(
            "⚠ Sauvegarde non effectuée."
        )

def delete_instrument(
    project
):

    allowed_errors = (
        project.get_blocking_errors(
            project.validate()
        )
    )

    selected = choose_instrument(
        project,
        allowed_errors=allowed_errors
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

            usage_type = usage.get(
                "type"
            )

            if usage_type == "program":

                print(
                    "- PROGRAM",
                    usage["program_id"],
                    "PART",
                    usage["part_id"]
                )

            elif usage_type == "mix":

                print(
                    "- MIX",
                    usage["mix_id"],
                    "CH",
                    usage["channel_id"]
                )

            elif usage_type == "song":

                print(
                    "- SONG",
                    usage["song_id"],
                    "CH",
                    usage["channel_id"],
                    "PROGRAM",
                    usage["program_id"]
                )

            else:

                print(
                    "-",
                    usage
                )

        return

    allowed_errors = (
        project.get_blocking_errors(
            project.validate()
        )
    )

    original_data = project.snapshot()

    ok, errors = project.remove_instrument(
        instrument_id
    )

    if not ok:

        print(
            "Instrument non supprimé."
        )

        print_error_messages(
            errors
        )

        return

    if project.save_safe(
        allowed_errors=allowed_errors
    ):

        print(
            "Instrument supprimé."
        )

    else:

        project.restore_snapshot(
            original_data
        )

def edit_instrument(project):

    # choisir instrument

    allowed_errors = (
        project.get_blocking_errors(
            project.validate()
        )
    )

    selected = choose_instrument(
        project,
        allowed_errors=allowed_errors
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

    allowed_errors = project.get_blocking_errors(
        project.validate()
    )

    original_data = project.snapshot()

    ok, errors = project.update_instrument(
        instrument_id,
        updated
    )

    if not ok:

        print(
            "Instrument non modifié."
        )

        print_error_messages(
            errors
        )

        return

    if project.save_safe(
        allowed_errors=allowed_errors
    ):

        print(
            "Instrument modifié."
        )

    else:

        project.restore_snapshot(
            original_data
        )

        print(
            "⚠ Sauvegarde non effectuée."
        )

def validate_and_repair(
    project
):

    errors = project.validate()

    if not errors:

        return

    print_validation_errors(
        project,
        errors
    )

    print()

    print(
        "Aucune réparation automatique disponible."
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
            "soundfont_configured",
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
        f"  {'Banque Fusion':<22}"
        f"{'Prog':>5}"
        f"  {'Instrument':<22}"
        f"État"
    )

    print(
        "-" * 115
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

        bank = part.get(
            "bank"
        )

        bank_name = (
            project.get_program_bank_name(bank)
            if bank is not None
            else "?"
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
            f"  {bank_name:<22}"
            f"{part.get('program', '?'):>5}"
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

    def edit_program_name(
        program
    ):

        current_name = program.get(
            "name",
            ""
        )

        print()
        print(
            "Nom Fusion actuel :",
            current_name or "Non défini"
        )

        name = input(
            "Nom Fusion "
            "(Entrée = conserver) : "
        ).strip()

        if not name:

            return None

        return name

    def print_part(
        part_id,
        part,
        fusion_name=None
    ):

        print()

        print(
            "PART",
            part_id
        )

        print("----------------")

        print(
            "Nom Fusion     :",
            (
                fusion_name
                if fusion_name is not None
                else part.get(
                    "fusion_name",
                    "Non défini"
                )
            )
        )

        bank = part.get("bank")

        print(
            "Fusion Bank    :",
            (
                f"{project.get_program_bank_name(bank)} ({bank})"
                if bank is not None
                else "?"
            )
        )

        print(
            "Fusion Program :",
            part.get(
                "program",
                "?"
            )
        )

        instrument = project.resolve_part_instrument(
            part
        )

        if instrument:

            print(
                "Instrument     :",
                instrument.get(
                    "name",
                    "?"
                )
            )

            print(
                "SF2 Bank       :",
                instrument.get(
                    "sf2_bank",
                    0
                )
            )

            print(
                "SF2 Program    :",
                instrument.get(
                    "sf2_program",
                    0
                )
            )

        else:

            print(
                "Instrument     : Non configuré"
            )


        print(
            "Canal MIDI     :",
            part.get(
                "midi_channel",
                "?"
            )
        )

        print(
            "Plage          :",
            note_range(
                part.get(
                    "note_min",
                    None
                ),
                part.get(
                    "note_max",
                    None
                )
            )
        )

        print(
            "Velocity       :",
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

    print_part(
        "1",
        part,
        fusion_name=program.get(
            "name"
        )
    )

    while True:

        print()
        print("====================")
        print("Edition PROGRAM")
        print("====================")
        print("1 - Modifier l'instrument")
        print("2 - Modifier les paramètres")
        print("3 - Modifier le nom Fusion")
        print("Q - Retour")

        choice = input(
            "> "
        )

        if choice == "1":

            allowed_errors = (
                project.get_blocking_errors(
                    project.validate()
                )
            )

            instrument = choose_instrument(
                project,
                part,
                fusion_name=program.get(
                    "name"
                ),
                allowed_errors=allowed_errors
            )

            if instrument is None:

                continue

            allowed_errors = project.get_blocking_errors(
                project.validate()
            )

            original_data = project.snapshot()

            ok, errors = project.update_program_part(
                program_id,
                "1",
                {
                    "instrument":
                        instrument["id"]
                }
            )

            if not ok:

                print(
                    "Instrument non affecté."
                )

                print_error_messages(
                    errors
                )

                continue

            if project.save_safe(
                allowed_errors=allowed_errors
            ):

                print(
                    "Instrument affecté."
                )

            else:

                project.restore_snapshot(
                    original_data
                )

                print(
                    "⚠ Sauvegarde non effectuée."
                )

        elif choice == "2":

            updates = edit_part_values(
                project,
                part,
                "1"
            )

            if not updates:

                continue

            allowed_errors = project.get_blocking_errors(
                project.validate()
            )

            original_data = project.snapshot()

            ok, errors = project.update_program_part(
                program_id,
                "1",
                updates
            )

            if not ok:

                print(
                    "PROGRAM non modifié."
                )

                print_error_messages(
                    errors
                )

                continue

            if project.save_safe(
                allowed_errors=allowed_errors
            ):

                print(
                    "PROGRAM modifié."
                )

            else:

                project.restore_snapshot(
                    original_data
                )

                print(
                    "⚠ Sauvegarde non effectuée."
                )

        elif choice == "3":

            name = edit_program_name(
                program
            )

            if name is None:

                continue

            allowed_errors = project.get_blocking_errors(
                project.validate()
            )

            original_data = project.snapshot()

            ok, errors = project.rename_program(
                program_id,
                name
            )

            if not ok:

                print(
                    "Nom Fusion non modifié."
                )

                print_error_messages(
                    errors
                )

                continue

            if project.save_safe(
                allowed_errors=allowed_errors
            ):

                print(
                    "Nom Fusion modifié."
                )

            else:

                project.restore_snapshot(
                    original_data
                )

                print(
                    "⚠ Sauvegarde non effectuée."
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

        configured = 0

        song_channels = song.get(
            "channels",
            {}
        )

        total = len(
            song_channels
        )

        for channel in song_channels.values():

            programs = channel.get(
                "programs"
            )

            if not programs:

                continue

            channel_configured = True

            for program_id, program_data in programs.items():

                instrument = project.resolve_song_program_instrument(
                    program_id,
                    program_data
                )

                if not instrument:

                    channel_configured = False

                    break

            if channel_configured:

                configured += 1

            continue

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

        # boucle des canaux...

        for channel_id, channel in sorted(
            song.get(
                "channels",
                {}
            ).items(),
            key=lambda item: int(
                item[0]
            )
        ):
            programs = channel.get(
                "programs"
            )

            if not programs:

                print(
                    f" CH {str(channel_id):<2}"
                    " → Aucun PROGRAM"
                )

                continue

            first = True

            for program_id, program_data in programs.items():

                try:

                    bank_str, _ = (
                        program_id.split(
                            ":",
                            1
                        )
                    )

                    bank = int(
                        bank_str
                    )

                except (
                    ValueError,
                    AttributeError
                ):

                    bank = None

                instrument = project.resolve_song_program_instrument(
                    program_id,
                    program_data
                )

                instrument_name = (
                    instrument.get(
                        "name",
                        "Non configuré"
                    )
                    if instrument
                    else "Non configuré"
                )

                bank_name = (
                    project.get_program_bank_name(
                        bank
                    )
                    if bank is not None
                    else "?"
                )

                channel_label = (
                    f"CH {channel_id}"
                    if first
                    else ""
                )

                print(
                    f" {channel_label:<5}"
                    f" → {instrument_name:<20}"
                    f" | {bank_name:<20}"
                    f" | {program_id:>6}"
                )

                first = False

            continue

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
            "Nouveau Volume (Entrée = conserver) : ",
            0,
            127
        )

        if value is not None:

            updates[
                "volume"
            ] = value

        value = read_int(
            "Nouveau Pan (Entrée = conserver) : ",
            0,
            127
        )

        if value is not None:

            updates[
                "pan"
            ] = value

        value = read_int(
            "Nouvelle Expression (Entrée = conserver) : ",
            0,
            127
        )

        if value is not None:

            updates[
                "expression"
            ] = value

        value = read_int(
            "Nouvelle Reverb (Entrée = conserver) : ",
            0,
            127
        )

        if value is not None:

            updates[
                "reverb"
            ] = value

        value = read_int(
            "Nouveau Chorus (Entrée = conserver) : ",
            0,
            127
        )

        if value is not None:

            updates[
                "chorus"
            ] = value

        if not updates:

            print(
                "Aucune modification."
            )

            return

        allowed_errors = project.get_blocking_errors(
            project.validate()
        )

        original_data = project.snapshot()

        ok, errors = project.update_song_channel(
            song_id,
            channel_id,
            updates=updates
        )

        if not ok:

            print(
                "Canal SONG non modifié."
            )

            print_error_messages(
                errors
            )

            return

        if project.save_safe(
            allowed_errors=allowed_errors
        ):

            print(
                "Paramètres du canal modifiés."
            )

        else:

            project.restore_snapshot(
                original_data
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

        for channel_id, channel in sorted(
            channels.items(),
            key=lambda item: int(
                item[0]
            )
        ):

            programs = channel.get(
                "programs",
                {}
            )

            if not programs:

                print(
                    f"CH {channel_id} - Aucun PROGRAM"
                )

                continue

            first = True

            for program_id, program_data in programs.items():

                instrument = project.resolve_song_program_instrument(
                    program_id,
                    program_data
                )

                instrument_name = (
                    instrument.get(
                        "name",
                        "Non configuré"
                    )
                    if instrument
                    else "Non configuré"
                )

                channel_label = (
                    f"CH {channel_id}"
                    if first
                    else ""
                )

                print(
                    f"{channel_label:<5}"
                    f" - {instrument_name:<20}"
                    f" ({program_id})"
                )

                first = False

            continue

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

        programs = channel.get(
            "programs",
            {}
        )

        while True:

            selected_program_id = None
            program_data = None

            if not programs:

                selected_program_id = None
                program_data = None

            else:

                program_ids = list(
                    programs.keys()
                )

                if len(program_ids) == 1:

                    selected_program_id = (
                        program_ids[0]
                    )

                else:

                    print()
                    print(
                        "PROGRAMs disponibles :"
                    )

                    for index, program_id in enumerate(
                        program_ids,
                        start=1
                    ):

                        current_program_data = programs[
                            program_id
                        ]

                        instrument = project.resolve_song_program_instrument(
                            program_id,
                            current_program_data
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
                            f"{index} - "
                            f"{program_id}"
                            f" - {instrument_name}"
                        )

                    print(
                        "Q - Retour"
                    )

                    while True:

                        choice = input(
                            "> "
                        ).strip()

                        if choice.lower() == "q":

                            selected_program_id = None

                            break

                        try:

                            index = int(
                                choice
                            )

                        except ValueError:

                            print(
                                "Choix invalide."
                            )

                            continue

                        if not (
                            1
                            <= index
                            <= len(program_ids)
                        ):

                            print(
                                "Choix invalide."
                            )

                            continue

                        selected_program_id = (
                            program_ids[
                                index - 1
                            ]
                        )

                        break

                    if selected_program_id is None:

                        break

                program_data = programs[
                    selected_program_id
                ]

            return_to_channel = False

            while True:

                print()

                #
                # Nouveau format avec PROGRAM
                #
                if selected_program_id is not None:

                    bank_str, program_str = (
                        selected_program_id.split(
                            ":",
                            1
                        )
                    )

                    bank = int(
                        bank_str
                    )

                    print(
                        "Fusion Bank    :",
                        f"{project.get_program_bank_name(bank)} ({bank})"
                    )

                    print(
                        "Fusion Program :",
                        program_str
                    )

                    global_program = project.get_program(
                        selected_program_id
                    )

                    global_fusion_name = (
                        global_program.get(
                            "name"
                        )
                        if global_program
                        else None
                    )

                    print(
                        "Nom Fusion global :",
                        global_fusion_name
                        or "PROGRAM inconnu"
                    )

                    local_instrument = project.resolve_part_instrument(
                        program_data
                    )

                    inherited_instrument = project.resolve_program_instrument(
                        selected_program_id
                    )

                    print()

                    print(
                        "Instrument hérité :",
                        (
                            inherited_instrument.get(
                                "name",
                                "Non configuré"
                            )
                            if inherited_instrument
                            else "Non configuré"
                        )
                    )

                    print(
                        "Instrument local  :",
                        (
                            local_instrument.get(
                                "name",
                                "Aucun"
                            )
                            if local_instrument
                            else "Aucun"
                        )
                    )
                #
                # Nouveau format sans PROGRAM
                #
                else:

                    print(
                        "Aucun PROGRAM capturé "
                        "sur ce canal."
                    )

                print()
                print("====================")
                print("Edition canal SONG")
                print("====================")

                if program_data is not None:

                    print(
                        "1 - Modifier l'instrument local du PROGRAM"
                    )

                print(
                    "2 - Modifier les paramètres du canal"
                )

                print(
                    "3 - Modifier le canal MIDI"
                )

                if program_data is not None:

                    if "instrument" in program_data:

                        print(
                            "4 - Supprimer l'instrument local"
                        )

                print(
                    "Q - Retour"
                )

                choice = input(
                    "> "
                )

                if choice == "1":

                    if program_data is None:

                        print(
                            "Aucun PROGRAM à modifier."
                        )

                        continue

                    global_program = project.get_program(
                        selected_program_id
                    )

                    fusion_name = None

                    if global_program:

                        fusion_name = global_program.get(
                            "name"
                        )

                    allowed_errors = project.get_blocking_errors(
                        project.validate()
                    )

                    instrument = choose_instrument(
                        project,
                        program_data,
                        fusion_name=fusion_name,
                        fusion_program=int(
                            program_str
                        ),
                        allowed_errors=allowed_errors
                    )

                    if instrument is None:

                        continue

                    allowed_errors = project.get_blocking_errors(
                        project.validate()
                    )

                    original_data = project.snapshot()

                    ok, errors = project.update_song_program(
                        song_id,
                        channel_id,
                        selected_program_id,
                        updates={
                            "instrument":
                                instrument["id"]
                        }
                    )

                    if not ok:

                        print(
                            "Instrument non affecté."
                        )

                        print_error_messages(
                            errors
                        )

                        continue

                    if project.save_safe(
                        allowed_errors=allowed_errors
                    ):

                        print(
                            "Instrument affecté."
                        )

                    else:

                        project.restore_snapshot(
                            original_data
                        )

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

                    allowed_errors = project.get_blocking_errors(
                        project.validate()
                    )

                    original_data = project.snapshot()

                    ok, errors = project.move_song_channel(
                        song_id,
                        channel_id,
                        new_channel_id
                    )

                    if not ok:

                        print(
                            "Canal MIDI non modifié."
                        )

                        print_error_messages(
                            errors
                        )

                        continue

                    if project.save_safe(
                        allowed_errors=allowed_errors
                    ):

                        print(
                            "Canal MIDI modifié :",
                            channel_id,
                            "→",
                            new_channel_id
                        )

                        channel_id = new_channel_id

                        channel = channels[
                            new_channel_id
                        ]

                    else:

                        project.restore_snapshot(
                            original_data
                        )

                        print(
                            "⚠ Sauvegarde non effectuée."
                        )

                elif choice == "4":

                    if (
                        program_data is None
                        or
                        "instrument" not in program_data
                    ):

                        print(
                            "Aucun instrument local à supprimer."
                        )

                        continue

                    allowed_errors = project.get_blocking_errors(
                        project.validate()
                    )

                    original_data = project.snapshot()

                    ok, errors = project.update_song_program(
                        song_id,
                        channel_id,
                        selected_program_id,
                        remove_fields=[
                            "instrument"
                        ]
                    )

                    if not ok:

                        print(
                            "Instrument local non supprimé."
                        )

                        print_error_messages(
                            errors
                        )

                        continue

                    if project.save_safe(
                        allowed_errors=allowed_errors
                    ):

                        print(
                            "Instrument local supprimé."
                        )

                        inherited_instrument = (
                            project.resolve_program_instrument(
                                selected_program_id
                            )
                        )

                        if inherited_instrument:

                            print(
                                "Instrument hérité :",
                                inherited_instrument.get(
                                    "name",
                                    "Non configuré"
                                )
                            )

                        else:

                            print(
                                "Instrument hérité : Non configuré"
                            )

                    else:

                        project.restore_snapshot(
                            original_data
                        )

                        print(
                            "⚠ Sauvegarde non effectuée."
                        )

                elif choice.lower() == "q":

                    if len(programs) <= 1:

                        return_to_channel = True

                    break

            if return_to_channel:

                break

def manage_banks(
    project
):

    def manage_bank_type(
        performance_type
    ):

        label = performance_type.upper()

        while True:

            print()
            print("====================")
            print(
                f"Banques {label}"
            )
            print("====================")

            banks = project.get_banks(
                performance_type
            )

            if not banks:

                print(
                    "Aucune banque."
                )

                return

            for bank in banks:

                name = project.get_bank_name(
                    performance_type,
                    bank
                )

                print(
                    f"{bank:2} - {name}"
                )

            print()
            print(
                "Q - Retour"
            )

            choix = input(
                "Banque > "
            )

            if choix.lower() == "q":

                return

            try:

                bank = int(
                    choix
                )

            except ValueError:

                print(
                    "Banque invalide."
                )

                continue

            if not 0 <= bank <= 127:

                print(
                    "Banque invalide (0-127)."
                )

                continue

            effective_name = project.get_bank_name(
                performance_type,
                bank
            )

            custom_name = project.get_custom_bank_name(
                performance_type,
                bank
            )

            print()
            print(
                "Nom effectif     :",
                effective_name
            )

            print(
                "Nom personnalisé :",
                (
                    custom_name
                    if custom_name is not None
                    else "-"
                )
            )

            print()
            print(
                "Nouveau nom"
            )

            print(
                "Entrée = conserver"
            )

            print(
                "- = supprimer le nom personnalisé"
            )

            name = input(
                "> "
            ).strip()

            if not name:

                continue

            if name == "-":

                name = None

            allowed_errors = project.get_blocking_errors(
                project.validate()
            )

            success, messages = project.set_bank_name(
                performance_type,
                bank,
                name
            )

            if success:

                if project.save_safe(
                    allowed_errors=allowed_errors
                ):

                    print(
                        "Nom de banque enregistré."
                    )

            else:

                print(
                    "Modification refusée :"
                )

                print_error_messages(
                    messages
                )


    while True:

        print()
        print("====================")
        print("Gestion des banques")
        print("====================")

        print(
            "1 - PROGRAM"
        )

        print(
            "2 - MIX"
        )

        print(
            "Q - Retour"
        )

        choix = input(
            "> "
        )

        if choix == "1":

            manage_bank_type(
                "program"
            )

        elif choix == "2":

            manage_bank_type(
                "mix"
            )

        elif choix.lower() == "q":

            return

def print_project_summary(
    project
):

    summary = project.get_project_diagnostic_summary()

    print()
    print("État du projet")
    print("--------------")

    for label, key in (
        ("INSTRUMENT", "instruments"),
        ("MIX", "mixes"),
        ("PROGRAM", "programs"),
        ("SONG", "songs")
    ):

        data = summary[
            key
        ]

        line = (
            f"{label:<11}: "
            f"{data['total']:>4} | "
            f"OK {data['ok']:>3} | "
            f"À configurer {data['unconfigured']:>3} | "
            f"Erreurs {data['error']:>3}"
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
                    "channels",
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

            allowed_errors = project.get_blocking_errors(
                project.validate()
            )

            ok, removed = project.delete_empty_mixes()

            if ok:

                if not removed:

                    print()

                    print(
                        "Aucun MIX vide."
                    )

                    return

                if project.save_safe(
                    allowed_errors=allowed_errors
                ):
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

            mix_id = choose_mix_id(
                project
            )

            if mix_id is None:

                return

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
                "Canaux :",
                len(
                    mix.get(
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

            allowed_errors = project.get_blocking_errors(
                project.validate()
            )

            ok, errors = project.delete_mix(
                mix_id
            )

            if not ok:

                print(
                    "Suppression refusée."
                )

                print_error_messages(
                    errors
                )

                return

            if project.save_safe(
                allowed_errors=allowed_errors
            ):

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
            print("Q - Retour")

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

                    mix_id = choose_mix_id(
                        project,
                        allowed_ids=mix_ids
                    )

                    if mix_id is None:

                        break

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

                    mix_id = choose_mix_id(
                        project,
                        allowed_ids=mix_ids
                    )

                    if mix_id is None:

                        break

                    edit_mix(
                        project,
                        mix_id
                    )


            elif choice == "4":

                mix_id = choose_mix_id(
                    project
                )

                if mix_id is None:

                    continue

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

            program_id = choose_program_id(
                project
            )

            if program_id is None:

                return

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

            allowed_errors = project.get_blocking_errors(
                project.validate()
            )

            original_data = project.snapshot()

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

            if project.save_safe(
                allowed_errors=allowed_errors
            ):

                print(
                    "PROGRAM renommé."
                )

            else:

                project.restore_snapshot(
                    original_data
                )

                print(
                    "⚠ Sauvegarde non effectuée."
                )

        def delete_program_menu():

            program_id = choose_program_id(
                project
            )

            if program_id is None:

                return

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

            allowed_errors = project.get_blocking_errors(
                project.validate()
            )

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

            if project.save_safe(
                allowed_errors=allowed_errors
            ):
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
            print("Q - Retour")

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

                    program_id = choose_program_id(
                        project,
                        allowed_ids=program_ids
                    )

                    if program_id is None:

                        break

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

                    program_id = choose_program_id(
                        project,
                        allowed_ids=program_ids
                    )

                    if program_id is None:

                        break

                    edit_program(
                        project,
                        program_id
                    )

            elif choice == "4":

                program_id = choose_program_id(
                    project
                )

                if program_id is None:

                    continue

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

            song_id = choose_song_id(
                project
            )

            if song_id is None:

                return

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

            allowed_errors = project.get_blocking_errors(
                project.validate()
            )

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

            if project.save_safe(
                allowed_errors=allowed_errors
            ):
                print(
                    "SONG renommée."
                )

        def delete_song_menu():

            song_id = choose_song_id(
                project
            )

            if song_id is None:

                return

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

            allowed_errors = project.get_blocking_errors(
                project.validate()
            )

            ok, errors = project.delete_song(
                song_id
            )

            if not ok:

                print(
                    "Suppression refusée."
                )

                print_error_messages(
                    errors
                )

                return

            if project.save_safe(
                allowed_errors=allowed_errors
            ):
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
            print("Q - Retour")

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

                    song_id = choose_song_id(
                        project,
                        allowed_ids=song_ids
                    )

                    if song_id is None:

                        break

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

                    song_id = choose_song_id(
                        project,
                        allowed_ids=song_ids
                    )

                    if song_id is None:

                        break

                    edit_song(
                        project,
                        song_id
                    )

            elif choice == "4":

                song_id = choose_song_id(
                    project
                )

                if song_id is None:

                    continue

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
        print("5 - Gestion des banques")
        print("Q - Quitter")
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

        elif choix == "5":

            manage_banks(
                project
            )

        elif choix.lower() == "q":

            break
