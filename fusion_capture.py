#!/usr/bin/env python3

import mido
import time

from fusion_lib import (
    find_fusion_input
)

from fusion_project import FusionProject

CAPTURE_TIME = 10

def main():

    port_name = find_fusion_input()

    if not port_name:

        raise Exception(
            "Fusion MIDI introuvable"
        )

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

    project = FusionProject()

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
                        "\rPARTS détectées :",
                        len(parts_seen),
                        " | Temps restant :",
                        remaining,
                        "s",
                        end="",
                        flush=True
                    )

                    if now - capture_start >= CAPTURE_TIME:

                        capture_active = False

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

                                for ch, part in parts_seen.items():

                                    print(
                                        "CH",
                                        part["midi_channel"],
                                        "Bank",
                                        part["bank"],
                                        "Program",
                                        part["program"]
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
                        if msg.channel == 0:

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

if __name__ == "__main__":

    main()
