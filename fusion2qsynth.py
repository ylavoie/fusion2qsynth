#!/usr/bin/env python3

import fusion_editor
import fusion_capture
import fusion_controller
import fusion_monitor
from fusion_project import FusionProject, ProjectRecoveryError

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
        "Mix enregistrés      :",
        status["mix_count"]
    )

    print(
        "Programs enregistrés :",
        status["program_count"]
    )

    print(
        "Songs enregistrées   :",
        status["song_count"]
    )

def choose_backup_restore():

    backups = FusionProject.list_backups()

    if not backups:

        print(
            "Aucune sauvegarde disponible."
        )

        return None

    print()

    print(
        "Sauvegardes disponibles :"
    )

    print()

    for index, backup in enumerate(
        backups,
        start=1
    ):

        info = FusionProject.get_backup_info(backup["filename"])

        print(
            index,
            "-",
            info["filename"]
        )

        print(
            "   Taille :",
            info["size"]
        )

        print(
            "   Date   :",
            info["time"]
        )

        print()

    print(
        "q - Annuler"
    )

    choix = input("> ")

    if choix.lower() == "q":

        return None

    try:

        index = int(choix) - 1

        return backups[index]

    except (ValueError, IndexError):

        print(
            "Choix invalide."
        )

        return None

def choose_archive_restore():

    archives = FusionProject.list_archives()

    if not archives:

        print(
            "Aucune archive disponible."
        )

        return None

    print()
    print(
        "Archives disponibles :"
    )
    print()

    for index, archive in enumerate(
        archives,
        start=1
    ):

        print(
            index,
            "-",
            archive["name"]
        )

    print()
    print(
        "q - Annuler"
    )

    choix = input("> ")

    if choix.lower() == "q":

        return None

    try:

        index = int(choix) - 1

        return archives[index]

    except (ValueError, IndexError):

        print(
            "Choix invalide."
        )

        return None

def main():

    try:

        project = FusionProject()

    except ProjectRecoveryError as e:

        print()
        print("==========================")
        print("Projet récupérable")
        print("==========================")
        print(e)
        print()

        backup = choose_backup_restore()

        if backup is None:

            print(
                "Aucune restauration effectuée."
            )

            exit(1)


        project = FusionProject.restore_from_backup(
            backup["filename"]
        )

        if project is None:

            print(
                "Restauration impossible."
            )

            exit(1)

        print(
            "Restauration réussie."
        )

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
        print("5 - Sauvegarder une archive")
        print("6 - Restaurer une archive")
        print("Q - Quitter")

        choix = input("> ")

        if choix == "1":

            fusion_capture.main()

        elif choix == "2":

            fusion_editor.main()

        elif choix == "3":

            fusion_controller.main()

        elif choix == "4":

            fusion_monitor.main()

        elif choix == "5":

            if project.archive():

                print(
                    "Archive créée."
                )

            else:

                print(
                    "Échec de l'archivage."
                )

        elif choix == "6":

            archive = choose_archive_restore()

            if archive is None:

                continue

            restored = FusionProject.restore_from_archive(
                archive["filename"]
            )

            if restored is None:

                print(
                    "Restauration impossible."
                )

                continue

            project = restored

            print(
                "Archive restaurée."
            )

        elif choix.lower() == "q":

            project.archive_if_changed()

            break

if __name__ == "__main__":

    main()