import json
import math
from pathlib import Path

from generate_suggestions_reference import (
    REFERENCE_FILE,
    build_reference,
)


SCORE_TOLERANCE = 1e-12


def compare_references(expected, actual):

    errors = []

    #
    # Format et paramètres
    #
    for field in (
        "format_version",
        "limit",
        "soundfont",
        "sf2_library_sha256",
        "fusion_catalog_sha256",
    ):

        if expected.get(field) != actual.get(field):

            errors.append(
                f"Métadonnée différente : {field}"
            )

    #
    # Arrêter si les données sources diffèrent
    #
    if errors:

        return errors

    expected_programs = expected["programs"]
    actual_programs = actual["programs"]

    for program_id in sorted(
        set(expected_programs)
        | set(actual_programs)
    ):

        if program_id not in expected_programs:

            errors.append(
                f"{program_id} : PROGRAM ajouté"
            )

            continue

        if program_id not in actual_programs:

            errors.append(
                f"{program_id} : PROGRAM supprimé"
            )

            continue

        expected_entry = expected_programs[program_id]
        actual_entry = actual_programs[program_id]

        if expected_entry["name"] != actual_entry["name"]:

            errors.append(
                f"{program_id} : nom modifié"
            )

        expected_suggestions = expected_entry[
            "suggestions"
        ]

        actual_suggestions = actual_entry[
            "suggestions"
        ]

        for family in sorted(
            set(expected_suggestions)
            | set(actual_suggestions)
        ):

            if family not in expected_suggestions:

                errors.append(
                    f"{program_id} : famille ajoutée : {family}"
                )

                continue

            if family not in actual_suggestions:

                errors.append(
                    f"{program_id} : famille supprimée : {family}"
                )

                continue

            expected_matches = expected_suggestions[
                family
            ]

            actual_matches = actual_suggestions[
                family
            ]

            if len(expected_matches) != len(actual_matches):

                errors.append(
                    f"{program_id}/{family} : "
                    "nombre de suggestions différent "
                    f"({len(expected_matches)} → "
                    f"{len(actual_matches)})"
                )

            for index, (old, new) in enumerate(
                zip(
                    expected_matches,
                    actual_matches,
                ),
                start=1,
            ):

                old_id = (
                    old["bank"],
                    old["program"],
                )

                new_id = (
                    new["bank"],
                    new["program"],
                )

                if old_id != new_id:

                    errors.append(
                        f"{program_id}/{family} "
                        f"rang {index} : "
                        f"preset {old_id} → {new_id}"
                    )

                if not math.isclose(
                    old["score"],
                    new["score"],
                    rel_tol=0.0,
                    abs_tol=SCORE_TOLERANCE,
                ):

                    errors.append(
                        f"{program_id}/{family} "
                        f"rang {index} : "
                        f"score {old['score']} → "
                        f"{new['score']}"
                    )

    return errors


def main():

    if not Path(REFERENCE_FILE).is_file():

        raise SystemExit(
            f"Référence absente : {REFERENCE_FILE}"
        )

    with open(
        REFERENCE_FILE,
        encoding="utf-8",
    ) as f:

        expected = json.load(f)

    actual = build_reference()

    errors = compare_references(
        expected,
        actual,
    )

    print()
    print("==============================")
    print(" Comparaison des suggestions")
    print("==============================")

    print(
        "PROGRAMs de référence :",
        len(expected["programs"])
    )

    print(
        "PROGRAMs actuels :",
        len(actual["programs"])
    )

    print(
        "Écarts :",
        len(errors)
    )

    if errors:

        print()

        for error in errors:

            print(
                "ERREUR :",
                error
            )

        raise SystemExit(1)

    print(
        "Référence respectée."
    )


if __name__ == "__main__":

    main()