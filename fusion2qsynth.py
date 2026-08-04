#!/usr/bin/env python3

import editor
import fusion_capture
import fusion_controller
import fusion_monitor
from fusion_project import FusionProject

from fusion_lib import(
    system_status
)

def show_status(project):

    status = system_status(project)

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

    try:

        project = FusionProject()

    except RuntimeError as e:

        print()
        print("==========================")
        print("Erreur projet")
        print("==========================")
        print(e)
        print()
        print("Le programme va se terminer.")

        exit(1)

    while True:

        print()
        print("==========================")
        print(" Fusion → QSynth")
        print("==========================")

        show_status(project)

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