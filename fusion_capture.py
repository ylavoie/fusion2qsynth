#!/usr/bin/env python3

import mido
import time

from fusion_lib import (
    find_fusion_input,
    note_name
)

from fusion_constants import (
    FUSION_DEFAULT_CHANNEL
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
                            bank
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
    programs = {}

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

                    print(
                        f"\rCapture : {remaining}s | PARTS : {len(parts_seen)}\r",
                        end="",
                        flush=True
                    )

                    if now - capture_start >= CAPTURE_TIME:

                        capture_active = False

                        print("\r" + " " * 45)
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
                                    "CH   BANK   PROGRAM"
                                )

                                print(
                                    "-------------------"
                                )

                                for ch, part in parts_seen.items():

                                    print(
                                        f"{part['midi_channel']:<5}"
                                        f"{part['bank']:<7}"
                                        f"{part['program']}"
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

                                parts = {}

                                for i, part in enumerate(
                                    parts_seen.values(),
                                    start=1
                                ):
                                    parts[str(i)] = part

                                    success, errors = project.replace_mix_parts(
                                        current_mix,
                                        parts
                                    )

                                    if not success:

                                        print()

                                        print(
                                            "Remplacement du Mix refusé :"
                                        )

                                        for error in errors:

                                            print(
                                                "-",
                                                error
                                            )

                                        continue

                                if project.save_safe():

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

                        programs[msg.channel] = msg.program

                        #
                        # Canal principal Fusion
                        #
                        if msg.channel == fusion_default_channel:

                            bank = banks.get(
                                msg.channel,
                                fusion_default_channel
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
                                current_mix
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

                                "midi_channel": ch + 1,

                                "bank":
                                    banks.get( ch, 0 ),

                                "program":
                                    programs.get( ch, 0 )

                            }

                            # print()

                            print(
                                "PART",
                                len(parts_seen),
                                "→ CH",
                                ch + 1,
                                "Bank",
                                parts_seen[ch]["bank"],
                                "Program",
                                parts_seen[ch]["program"]
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

    song_id = None
    capture_active = False

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

                    song_id = msg.song

                    print()
                    print(
                        "SONG détectée :",
                        song_id
                    )

                    continue

                #
                # Début transport
                #
                if msg.type == "start":

                    if song_id is None:

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

                    song["channels"] = channels

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

                    bank = (
                        banks_msb.get(
                            msg.channel,
                            0
                        )
                        * 128
                        +
                        banks_lsb.get(
                            msg.channel,
                            0
                        )
                    )

                    channels[
                        channel
                    ][
                        "bank"
                    ] = bank

                    channels[
                        channel
                    ][
                        "program"
                    ] = msg.program

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
        print("1 - PROGRAM")
        print("2 - MIX")
        print("3 - SONG")
        print("q - Retour")
        print()

        choice = input(
            "> "
        )

        if choice == "1":

            capture_program(
                project,
                port_name
            )

        elif choice == "2":

            capture_mix(
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
