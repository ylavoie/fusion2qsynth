import hashlib
import json
from pathlib import Path

from fusion_project import FusionProject
from fusion_suggestions import suggest_instruments
from sf2_library import (
    SF2_FILE,
    list_presets,
    load_library,
)


REFERENCE_FILE = Path(
    "suggestions_reference.json"
)

LIMIT = 3


def sha256_file(filename):

    digest = hashlib.sha256()

    with open(filename, "rb") as f:

        for chunk in iter(
            lambda: f.read(65536),
            b"",
        ):

            digest.update(chunk)

    return digest.hexdigest()


def main():

    if REFERENCE_FILE.exists():

        raise SystemExit(
            f"Référence déjà présente : {REFERENCE_FILE}"
        )

    project = FusionProject()

    library = load_library()

    if not library.get("presets"):

        raise SystemExit(
            "Bibliothèque SF2 absente ou vide."
        )

    presets = [
        {
            "id": p["id"],
            "name": p["name"],
            "bank": p["sf2_bank"],
            "program": p["sf2_program"],
            "sf2_bank": p["sf2_bank"],
            "sf2_program": p["sf2_program"],
        }
        for p in list_presets()
    ]

    programs = project.data.get(
        "programs",
        {}
    )

    if not programs:

        raise SystemExit(
            "Catalogue Fusion absent ou vide."
        )

    reference = {}

    for program_id in sorted(
        programs,
        key=lambda value: tuple(
            int(part)
            for part in value.split(":")
        ),
    ):

        bank, program_number = (
            int(part)
            for part in program_id.split(":")
        )

        if bank == 8:

            continue

        name = programs[program_id].get(
            "name"
        )

        if not name:

            raise SystemExit(
                f"Nom absent : {program_id}"
            )

        suggestions = suggest_instruments(
            {
                "name": name,
                "program": program_number,
            },
            presets,
            limit=LIMIT,
        )

        reference[program_id] = {
            "name": name,
            "suggestions": {
                family: [
                    {
                        "bank": preset["bank"],
                        "program": preset["program"],
                        "score": score,
                    }
                    for score, preset in matches
                ]
                for family, matches
                in suggestions.items()
            },
        }

    if not reference:

        raise SystemExit(
            "Aucun PROGRAM ROM trouvé."
        )

    # Empreinte canonique des données Fusion utilisées,
    # indépendante des autres champs de fusion.json.
    fusion_data = [
        {
            "id": program_id,
            "name": entry["name"],
        }
        for program_id, entry in reference.items()
    ]

    fusion_bytes = json.dumps(
        fusion_data,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    fusion_hash = hashlib.sha256(
        fusion_bytes
    ).hexdigest()

    output = {
        "format_version": 1,
        "limit": LIMIT,
        "soundfont": library.get(
            "soundfont"
        ),
        "sf2_library_sha256": sha256_file(
            SF2_FILE
        ),
        "fusion_catalog_sha256": fusion_hash,
        "programs": reference,
    }

    # Mode exclusif : aucune référence existante
    # ne peut être écrasée.
    try:

        with REFERENCE_FILE.open(
            "x",
            encoding="utf-8",
        ) as f:

            json.dump(
                output,
                f,
                ensure_ascii=False,
                indent=2,
                allow_nan=False,
            )

            f.write("\n")

    except FileExistsError:

        raise SystemExit(
            f"Référence déjà présente : {REFERENCE_FILE}"
        )

    print(
        "Référence générée :",
        REFERENCE_FILE
    )

    print(
        "PROGRAMs ROM :",
        len(reference)
    )

    print(
        "Presets SF2 :",
        len(presets)
    )

    print(
        "Limit :",
        LIMIT
    )


if __name__ == "__main__":

    main()