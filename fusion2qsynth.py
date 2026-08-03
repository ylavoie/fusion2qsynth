#!/usr/bin/env python3

import editor
import fusion_capture
import fusion_controller
import fusion_monitor

from fusion_lib import(
    load_json,
    find_fusion_input,
    find_fluidsynth_output,
    system_status
)

def show_status():

    status = system_status()

    print()

    print("=========================")
    print(" État du système")
    print("=========================")

    print(
        "Fusion MIDI     :",
        "OK" if status["fusion"] else "absent"
    )

    print(
        "FluidSynth MIDI :",
        "OK" if status["fluidsynth"] else "absent"
    )

    print(
        "Mix enregistrés :",
        status["mix_count"]
    )

def main():

    while True:

        print()
        print("==========================")
        print(" Fusion → QSynth")
        print("==========================")

        show_status()

        print()

        print("1 - Capture Fusion")
        print("2 - Éditeur")
        print("3 - Contrôleur Live")
        print("4 - Monitor MIDI")
        print("Q - Quitter")

        choix = input("> ")

        if choix == "1":

            fusion_capture.main()

        elif choix == "2":

            editor.main()

        elif choix == "3":

            fusion_controller.main()

        elif choix == "4":

            fusion_monitor.main()

        elif choix.lower() == "q":

            break

if __name__ == "__main__":

    main()