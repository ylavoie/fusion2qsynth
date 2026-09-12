#!/usr/bin/env python3

import mido
import time

from fusion_lib import (
    find_fusion_input,
    note_name
)

from fusion_diagnostic import (
    print_error_messages
)

from fusion_constants import (
    FUSION_DEFAULT_CHANNEL,
    DEBUG
)

from fusion_gm_map import (
    fusion_mix_bank_name,
    fusion_program_bank_name,
)

fusion_default_channel = FUSION_DEFAULT_CHANNEL - 1

from fusion_project import FusionProject

CAPTURE_TIME = 10

def capture_program(
    project,
    port_name
):

    print()
    print(
        "Ecoute :",
        port_name
    )

    print()
    print(
        "Sélectionne un Program Fusion"
    )

    print(
        "Ctrl+C pour quitter"
    )

    bank = 0

    current_program = None
    current_program_bank = None
    current_program_number = None
    capture_active = False
    capture_start = 0

    note_min = None
    note_max = None
    velocity_min = None
    velocity_max = None

    try:

        with mido.open_input(
            port_name
        ) as inp:

            while True:

                now = time.time()

                #
                # Fin capture PROGRAM
                #
                if (
                    capture_active
                    and
                    now - capture_start >= CAPTURE_TIME
                ):

                    capture_active = False

                    print()
                    print("====================")
                    print("Fin de capture")
                    print("====================")
                    print()

                    if note_min is not None:

                        print(
                            "Plage détectée :",
                            note_name(note_min),
                            "-",
                            note_name(note_max)
                        )

                        print(
                            "Velocity observée :",
                            velocity_min,
                            "-",
                            velocity_max
                        )

                        program = project.ensure_program(
                            current_program
                        )

                        program["parts"] = {
                            "1": {
                                "midi_channel":
                                    fusion_default_channel + 1,

                                "bank":
                                    bank,

                                "program":
                                    current_program_number,

                                "note_min":
                                    note_min,

                                "note_max":
                                    note_max,

                                "velocity_min":
                                    velocity_min,

                                "velocity_max":
                                    velocity_max
                            }
                        }

                        if project.save_safe():

                            print(
                                "Program sauvegardé."
                            )

                        else:

                            print(
                                "⚠ Sauvegarde non effectuée."
                            )

                    else:

                        print(
                            "Aucune note détectée."
                        )

                    print()
                    print(
                        "Sélectionne un autre Program Fusion"
                    )

                for msg in inp.iter_pending():

                    #
                    # Bank Select
                    #
                    if (
                        msg.type == "control_change"
                        and
                        msg.channel == fusion_default_channel
                        and
                        msg.control == 0
                    ):

                        bank = msg.value

                        continue

                    #
                    # Nouveau PROGRAM
                    #
                    if (
                        msg.type == "program_change"
                        and
                        msg.channel == fusion_default_channel
                    ):

                        current_program_bank = bank
                        current_program_number = msg.program

                        current_program = (
                            f"{current_program_bank}:"
                            f"{current_program_number}"
                        )

                        note_min = None
                        note_max = None
                        velocity_min = None
                        velocity_max = None

                        capture_active = True
                        capture_start = time.time()

                        print()
                        print("====================")
                        print("Program Fusion détecté")
                        print("====================")
                        print()
                        print(
                            "Fusion Program :",
                            current_program
                        )
                        print(
                            "Canal MIDI     :",
                            msg.channel + 1
                        )
                        print(
                            "Bank           :",
                            fusion_program_bank_name(bank)
                        )
                        print(
                            "Program        :",
                            msg.program
                        )
                        print()
                        print(
                            "Balayez rapidement le clavier"
                        )
                        print(
                            "de la note la plus basse"
                        )
                        print(
                            "à la plus haute."
                        )
                        print()

                        continue

                    #
                    # Notes observées
                    #
                    if (
                        capture_active
                        and
                        msg.type == "note_on"
                        and
                        msg.velocity > 0
                        and
                        msg.channel == fusion_default_channel
                    ):

                        if (
                            note_min is None
                            or
                            msg.note < note_min
                        ):

                            note_min = msg.note

                        if (
                            note_max is None
                            or
                            msg.note > note_max
                        ):

                            note_max = msg.note

                        if (
                            velocity_min is None
                            or
                            msg.velocity < velocity_min
                        ):

                            velocity_min = msg.velocity

                        if (
                            velocity_max is None
                            or
                            msg.velocity > velocity_max
                        ):

                            velocity_max = msg.velocity

                time.sleep(
                    0.01
                )

    except KeyboardInterrupt:

        print()
        print(
            "Retour au menu"
        )

        return

def capture_mix(
        project,
        port_name
):
    print(
        "Ecoute :",
        port_name
    )

    print()
    print(
        "Sélectionne un Mix Fusion"
    )

    print(
        "La capture démarre automatiquement"
    )

    print(
        "Ctrl+C pour quitter"
    )

    # mémoire MIDI permanente
    banks = {}

    current_mix = None

    capture_active = False
    capture_start = 0

    parts_seen = {}
    notes_seen = {}

    try:
        with mido.open_input(port_name) as inp:

            while True:

                now = time.time()

                #
                # Fin de capture automatique
                #
                if capture_active:

                    remaining = int(
                        CAPTURE_TIME - (now - capture_start)
                    )

                    if DEBUG:

                        print(
                            f"\rCapture : {remaining}s | "
                            f"PARTS : {len(parts_seen)}",
                            end="",
                            flush=True
                        )

                    if now - capture_start >= CAPTURE_TIME:

                        capture_active = False

                        if DEBUG:
                            print()

                        print("====================")
                        print("Fin de capture")
                        print("====================")

                        if current_mix:

                            used_channels = []

                            for part in parts_seen.values():

                                used_channels.append(
                                    part["midi_channel"]
                                )

                            if len(used_channels) != len(set(used_channels)):

                                print()
                                print("ERREUR :")
                                print("Plusieurs PARTS utilisent le même canal MIDI.")
                                print("Réglage Fusion requis.")
                                print()

                            else:

                                print()

                                print(
                                    "PARTS détectées :",
                                    len(parts_seen)
                                )

                            print(
                                "CH"
                            )

                            print(
                                "--"
                            )

                            for part in sorted(
                                parts_seen.values(),
                                key=lambda p: p["midi_channel"]
                            ):

                                print(
                                    part["midi_channel"]
                                )

                            if project.mix_has_parts(
                                current_mix
                            ):

                                print(
                                    "Mix déjà existant."
                                )

                                rep = input(
                                    "Remplacer ? (o/n) : "
                                )

                                if rep.lower() != "o":

                                    continue

                            old_parts = {}

                            existing_mix = project.get_mix(
                                current_mix
                            )

                            if existing_mix:

                                old_parts = existing_mix.get(
                                    "parts",
                                    {}
                                )

                            parts = {}

                            for i, part in enumerate(
                                sorted(
                                    parts_seen.values(),
                                    key=lambda p: p["midi_channel"]
                                ),
                                start=1
                            ):

                                new_part = dict(
                                    part
                                )

                                for old_part in old_parts.values():

                                    if (
                                        old_part.get("midi_channel")
                                        !=
                                        new_part.get("midi_channel")
                                    ):

                                        continue

                                    #for key in (
                                    #    "bank",
                                    #    "program",
                                    #    "instrument",
                                    #    "fusion_name"
                                    #):

                                        #if key in old_part:

                                            #new_part[key] = (
                                            #    old_part[key]
                                            #)

                                    break

                                parts[str(i)] = new_part

                            #
                            # Erreurs préexistantes du projet
                            #
                            existing_errors = project.validate()

                            print("existing_errors:",existing_errors)

                            success, errors = project.replace_mix_parts(
                                current_mix,
                                parts,
                                allowed_errors=existing_errors
                            )

                            print("success:",success,"errors:",errors)

                            if not success:

                                print()

                                print(
                                    "Remplacement du Mix refusé :"
                                )

                                print_error_messages(
                                    errors
                                )

                                continue

                            if project.save_safe(
                                allowed_errors=existing_errors
                            ):
                                print()
                                print(
                                    "Capture terminée"
                                )

                                print(
                                    len(parts_seen),
                                    "PART(s) sauvegardée(s)"
                                )

                                print()

                            else:

                                print(
                                    "Le Mix n'a pas été sauvegardé."
                                )
                #
                # Poll MIDI
                #
                for msg in inp.iter_pending():

                    #
                    # Bank MSB
                    #
                    if msg.type == "control_change":

                        if msg.control == 0:

                            banks[msg.channel] = msg.value

                    #
                    # Program Change
                    #
                    elif msg.type == "program_change":

                        #
                        # Canal principal Fusion
                        #
                        if msg.channel == fusion_default_channel:

                            bank = banks.get(
                                msg.channel,
                                0
                            )

                            current_mix = (
                                f"{bank}:{msg.program}"
                            )

                            parts_seen = {}
                            notes_seen = {}

                            mix = project.ensure_mix(
                                current_mix
                            )

                            capture_active = True

                            capture_start = time.time()

                            print()
                            print("====================")
                            print("Nouveau Mix détecté")
                            print("====================")
                            print()
                            print(
                                "Fusion Mix :",
                                f"{fusion_mix_bank_name(bank)} "
                                f"({current_mix})"
                            )
                            print()
                            print(
                                "Capture automatique :",
                                CAPTURE_TIME,
                                "secondes"
                            )
                            print()
                            print(
                                "Jouez plusieurs notes :"
                            )
                            print(
                                "- graves"
                            )
                            print(
                                "- médiums"
                            )
                            print(
                                "- aigus"
                            )
                            print(
                                "- accords"
                            )
                            print()
                            print(
                                "Capture en cours..."
                            )

                    #
                    # Notes = découverte PART
                    #
                    elif msg.type == "note_on":

                        if not capture_active:

                            continue

                        if msg.velocity == 0:

                            continue

                        ch = msg.channel

                        if ch not in parts_seen:

                            parts_seen[ch] = {
                                "midi_channel": ch + 1
                            }

                            print(
                                "PART",
                                len(parts_seen),
                                "→ CH",
                                ch + 1
                            )

                        if ch not in notes_seen:

                            notes_seen[ch] = {
                                "notes": [],
                                "velocity": []
                            }

                        notes_seen[ch]["notes"].append(
                            msg.note
                        )

                        notes_seen[ch]["velocity"].append(
                            msg.velocity
                        )

                time.sleep(0.01)

    except KeyboardInterrupt:
        print()
        print("Retour au menu")
        return

def capture_song(
    project,
    port_name
):

    print(
        "Ecoute :",
        port_name
    )

    print()
    print(
        "Sélectionne une Song Fusion"
    )

    print(
        "Démarre la Song pour lancer la capture"
    )

    print(
        "Ctrl+C pour quitter"
    )

    capture_active = False

    song_id = None
    channels = {}
    banks_msb = {}
    banks_lsb = {}

    static_cc = {
        7: "volume",
        10: "pan",
        11: "expression",
        91: "reverb",
        93: "chorus"
    }

    try:

        with mido.open_input(
            port_name
        ) as inp:

            for msg in inp:

                #
                # Sélection SONG
                #
                if msg.type == "song_select":

                    print()
                    print(
                        "SONG SELECT reçu :",
                        msg.song
                    )

                    while True:

                        print()

                        song_id = input(
                            "Identifiant de la SONG : "
                        ).strip()

                        if not song_id:

                            print(
                                "Identifiant invalide."
                            )

                            continue

                        existing_song = project.get_song(
                            song_id
                        )

                        if existing_song:

                            print()
                            print(
                                "SONG déjà enregistrée :",
                                song_id
                            )

                            rep = input(
                                "Réenregistrer cette SONG ? (o/n) : "
                            ).strip().lower()

                            if rep != "o":

                                print(
                                    "Choisis un autre identifiant."
                                )

                                continue

                        break

                    channels = {}
                    capture_active = False

                    print(
                        "Démarre la Song pour lancer la capture"
                    )

                    continue

                #
                # Début transport
                #
                if msg.type == "start":

                    if song_id is None:

                        print(
                            "START reçu sans identifiant de SONG."
                        )

                        continue

                    capture_active = True

                    channels = {}
                    banks_msb = {}
                    banks_lsb = {}

                    print()
                    print("====================")
                    print(
                        "Capture SONG",
                        song_id
                    )
                    print("====================")

                    continue

                #
                # Fin transport
                #
                if (
                    msg.type == "stop"
                    and
                    capture_active
                ):

                    capture_active = False

                    song = project.ensure_song(
                        song_id
                    )

                    if not channels:

                        print()
                        print(
                            "Aucun canal détecté : "
                            "SONG non sauvegardée."
                        )

                        song_id = None

                        continue

                    old_channels = song.get(
                        "channels",
                        {}
                    )

                    unknown_programs = {}

                    for channel_id, channel in channels.items():

                        old_channel = old_channels.get(
                            channel_id
                        )

                        #
                        # PROGRAMs déjà enregistrés sur ce canal
                        #
                        old_programs = {}

                        if old_channel:

                            existing_programs = old_channel.get(
                                "programs"
                            )

                            #
                            # Nouveau format SONG
                            #
                            if isinstance(
                                existing_programs,
                                dict
                            ):

                                old_programs = existing_programs

                            #
                            # Ancien format SONG
                            #
                            else:

                                old_bank = old_channel.get(
                                    "bank"
                                )

                                old_program = old_channel.get(
                                    "program"
                                )

                                if (
                                    old_bank is not None
                                    and
                                    old_program is not None
                                ):

                                    old_program_id = (
                                        f"{old_bank}:"
                                        f"{old_program}"
                                    )

                                    old_program_data = {}

                                    if "fusion_name" in old_channel:

                                        old_program_data[
                                            "fusion_name"
                                        ] = old_channel[
                                            "fusion_name"
                                        ]

                                    if "instrument" in old_channel:

                                        old_program_data[
                                            "instrument"
                                        ] = old_channel[
                                            "instrument"
                                        ]

                                    old_programs[
                                        old_program_id
                                    ] = old_program_data

                        #
                        # Identifier les PROGRAMs inconnus
                        #
                        programs = channel.get(
                            "programs",
                            {}
                        )

                        for program_id in programs:

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

                            if project.get_program(
                                program_id
                            ):

                                continue

                            unknown_programs[
                                program_id
                            ] = {
                                "bank": bank,
                                "program": program
                            }

                            print()

                            print(
                                "PROGRAM inconnu :",
                                program_id,
                                "- canal",
                                channel_id
                            )

                        #
                        # Fusionner les PROGRAMs déjà enregistrés
                        # avec ceux observés pendant cette capture
                        #
                        captured_programs = channel.setdefault(
                            "programs",
                            {}
                        )

                        merged_programs = {}

                        #
                        # Normaliser les anciennes données.
                        #
                        # fusion_name appartient maintenant au PROGRAM global.
                        #
                        # Un instrument identique à l'instrument global est
                        # redondant et devient un simple héritage.
                        #
                        for (
                            program_id,
                            old_program_data
                        ) in old_programs.items():

                            if not isinstance(
                                old_program_data,
                                dict
                            ):

                                continue

                            clean_program_data = {
                                key: value
                                for key, value in old_program_data.items()
                                if key not in (
                                    "instrument",
                                    "fusion_name"
                                )
                            }

                            local_instrument = old_program_data.get(
                                "instrument"
                            )

                            if local_instrument:

                                global_instrument = None

                                global_program = project.get_program(
                                    program_id
                                )

                                if global_program:

                                    parts = global_program.get(
                                        "parts",
                                        {}
                                    )

                                    if len(parts) == 1:

                                        program_part = next(
                                            iter(
                                                parts.values()
                                            )
                                        )

                                        global_instrument = program_part.get(
                                            "instrument"
                                        )

                                #
                                # Conserver uniquement une vraie surcharge locale
                                #
                                if (
                                    local_instrument
                                    != global_instrument
                                ):

                                    clean_program_data[
                                        "instrument"
                                    ] = local_instrument

                            merged_programs[
                                program_id
                            ] = clean_program_data

                        #
                        # Ajouter les PROGRAMs observés pendant la capture
                        #
                        for (
                            program_id,
                            program_data
                        ) in captured_programs.items():

                            merged_program_data = dict(
                                program_data
                            )

                            old_program_data = merged_programs.get(
                                program_id
                            )

                            if isinstance(
                                old_program_data,
                                dict
                            ):

                                #
                                # Les vraies surcharges locales existantes
                                # ont priorité
                                #
                                if "instrument" in old_program_data:

                                    merged_program_data[
                                        "instrument"
                                    ] = old_program_data[
                                        "instrument"
                                    ]

                            merged_programs[
                                program_id
                            ] = merged_program_data

                        channel[
                            "programs"
                        ] = merged_programs

                        #
                        # Préserver les contrôleurs statiques
                        # non observés pendant cette capture
                        #
                        if old_channel:

                            for field in (
                                "volume",
                                "pan",
                                "expression",
                                "reverb",
                                "chorus"
                            ):

                                if (
                                    field not in channel
                                    and
                                    field in old_channel
                                ):

                                    channel[
                                        field
                                    ] = old_channel[
                                        field
                                    ]

                    #
                    # Créer les PROGRAMs inconnus détectés dans la SONG
                    #
                    for program_id, program_data in unknown_programs.items():

                        program = project.ensure_program(
                            program_id
                        )

                        program["parts"] = {
                            "1": {
                                "midi_channel":
                                    fusion_default_channel + 1,

                                "bank":
                                    program_data["bank"],

                                "program":
                                    program_data["program"]
                            }
                        }

                    #
                    # Conserver les canaux enregistrés
                    # non observés pendant cette capture
                    #
                    merged_channels = dict(
                        old_channels
                    )

                    merged_channels.update(
                        channels
                    )

                    song["channels"] = merged_channels

                    if project.save_safe():

                        print()
                        print(
                            "SONG sauvegardée :",
                            song_id
                        )

                        print(
                            "Canaux détectés :",
                            len(channels)
                        )

                        song_id = None
                        channels = {}

                        print()
                        print(
                            "Sélectionne une autre Song Fusion"
                        )

                        continue

                    else:

                        print(
                            "⚠ Sauvegarde non effectuée."
                        )

                    continue

                if not capture_active:

                    continue

                #
                # Bank Select MSB
                #
                if (
                    msg.type == "control_change"
                    and
                    msg.control == 0
                ):

                    banks_msb[
                        msg.channel
                    ] = msg.value

                    continue

                #
                # Bank Select LSB
                #
                if (
                    msg.type == "control_change"
                    and
                    msg.control == 32
                ):

                    banks_lsb[
                        msg.channel
                    ] = msg.value

                    continue

                #
                # Program Change
                #
                if msg.type == "program_change":

                    channel = str(
                        msg.channel + 1
                    )

                    channels.setdefault(
                        channel,
                        {}
                    )

                    bank = banks_msb.get(
                        msg.channel,
                        0
                    )

                    program_id = (
                        f"{bank}:"
                        f"{msg.program}"
                    )

                    channels[
                        channel
                    ].setdefault(
                        "programs",
                        {}
                    )

                    channels[
                        channel
                    ][
                        "programs"
                    ].setdefault(
                        program_id,
                        {}
                    )

                    continue

                #
                # Contrôleurs statiques
                #
                if (
                    msg.type == "control_change"
                    and
                    msg.control in static_cc
                ):

                    channel = str(
                        msg.channel + 1
                    )

                    channels.setdefault(
                        channel,
                        {}
                    )

                    channels[
                        channel
                    ][
                        static_cc[msg.control]
                    ] = msg.value

                    continue

    except KeyboardInterrupt:

        print()
        print(
            "Retour au menu Capture"
        )

        return

def main():

    port_name = find_fusion_input()

    if not port_name:

        raise Exception(
            "Fusion MIDI introuvable"
        )

    project = FusionProject()

    while True:

        print()
        print("====================")
        print("Capture Fusion")
        print("====================")
        print()
        print("1 - MIX")
        print("2 - PROGRAM")
        print("3 - SONG")
        print("q - Retour")
        print()

        choice = input(
            "> "
        )

        if choice == "1":

            capture_mix(
                project,
                port_name
            )

        elif choice == "2":

            capture_program(
                project,
                port_name
            )

        elif choice == "3":

            capture_song(
                project,
                port_name
            )

        elif choice.lower() == "q":

            return

if __name__ == "__main__":

    main()
