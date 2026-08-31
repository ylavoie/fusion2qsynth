from fusion_project import FusionProject
from fusion_suggestions import (
    detect_families,
    detect_gm_hint,
    suggest_instruments,
)
from sf2_library import list_presets

project = FusionProject()
hint_program_mismatch = []

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


names = set()

#
# MIX
#
for mix in project.data.get(
    "mixes",
    {}
).values():

    for part in mix.get(
        "parts",
        {}
    ).values():

        name = part.get(
            "fusion_name"
        )

        if name:
            names.add(name)

#
# PROGRAM
#
for program in project.data.get(
    "programs",
    {}
).values():

    for part in program.get(
        "parts",
        {}
    ).values():

        name = part.get(
            "fusion_name"
        )

        if name:
            names.add(name)

#
# SONG
#
for song in project.data.get(
    "songs",
    {}
).values():

    for channel in song.get(
        "channels",
        {}
    ).values():

        name = channel.get(
            "fusion_name"
        )

        if name:
            names.add(name)


FAMILY_COMPATIBILITY = {
    "brass": {
        "brass",
        "trumpet",
        "trombone",
        "french_horn",
    },

    "strings": {
        "strings",
        "violin",
        "viola",
        "cello",
        "contrabass",
    },

    "cello": {
        "cello",
        "strings",
    },

    "violin": {
        "violin",
        "strings",
    },

    "viola": {
        "viola",
        "strings",
    },

    "contrabass": {
        "contrabass",
        "strings",
        "bass",
    },

    "woodwind": {
        "woodwind",
        "flute",
        "clarinet",
        "oboe",
        "english_horn",
        "bassoon",
        "sax",
    },

    "choir": {
        "choir",
        "voice",
    },

    "voice": {
        "voice",
        "choir",
    },
}

def families_are_compatible(
    hint_family,
    detected_families
):

    if hint_family in detected_families:

        return True

    compatible = FAMILY_COMPATIBILITY.get(
        hint_family,
        set()
    )

    return bool(
        compatible
        & detected_families
    )

with_hint = []
family_only = []
unknown = []
empty_suggestions = []
conflicts = []
hint_program_mismatches = []
hint_top_mismatches = []
family_only_mismatches = []
invalid_suggestions = []
duplicate_suggestions = []
missing_fields = []
unsorted_suggestions = []
abnormal_scores = []

for name in sorted(names):

    hint = detect_gm_hint(
        name
    )

    families = detect_families(
        name
    )

    suggestions = suggest_instruments(
        {
            "name": name,
            "program": 0,
        },
        presets
    )

    for family, matches in suggestions.items():

        for score, preset in matches:

            if (
                score < -0.05
                or score > 1.50
            ):

                abnormal_scores.append(
                    (
                        name,
                        family,
                        score,
                        preset.get("name"),
                    )
                )

    for family, matches in suggestions.items():

        scores = [
            score
            for score, preset in matches
        ]

        if scores != sorted(
            scores,
            reverse=True
        ):

            unsorted_suggestions.append(
                (
                    name,
                    family,
                    scores,
                )
            )

    required_fields = {
        "name",
        "bank",
        "program",
    }

    for family, matches in suggestions.items():

        for score, preset in matches:

            missing = (
                required_fields
                - preset.keys()
            )

            if missing:

                missing_fields.append(
                    (
                        name,
                        family,
                        sorted(missing),
                        preset,
                    )
                )

    for family, matches in suggestions.items():

        seen = set()

        for score, preset in matches:

            key = (
                preset.get("bank"),
                preset.get("program"),
            )

            if key in seen:

                duplicate_suggestions.append(
                    (
                        name,
                        family,
                        key,
                        preset.get("name"),
                    )
                )

            seen.add(
                key
            )

    for family, matches in suggestions.items():

        for score, preset in matches:

            bank = preset.get(
                "bank"
            )

            program = preset.get(
                "program"
            )

            if (
                not isinstance(bank, int)
                or bank < 0
                or bank > 16383
                or not isinstance(program, int)
                or program < 0
                or program > 127
            ):

                invalid_suggestions.append(
                    (
                        name,
                        family,
                        bank,
                        program,
                        preset.get("name"),
                    )
                )

    if (
        not hint
        and families
    ):

        for family in families:

            matches = suggestions.get(
                family,
                []
            )

            if not matches:

                family_only_mismatches.append(
                    (
                        name,
                        family,
                        "aucune suggestion",
                    )
                )

                continue

            score, preset = matches[0]

            preset_families = detect_families(
                preset["name"]
            )

            if family not in preset_families:

                family_only_mismatches.append(
                    (
                        name,
                        family,
                        (
                            preset["bank"],
                            preset["program"],
                            preset["name"],
                            preset_families,
                        ),
                    )
                )

    if hint and suggestions:

        expected_program = hint.get(
            "gm_program"
        )

        found_program = False

        for matches in suggestions.values():

            for score, preset in matches:

                if (
                    preset["program"]
                    == expected_program
                ):
                    found_program = True
                    break

            if found_program:
                break

        if not found_program:

            hint_program_mismatches.append(
                (
                    name,
                    hint,
                    suggestions,
                )
            )

    if hint and suggestions:

        hint_family = hint.get(
            "family"
        )

        expected_program = hint.get(
            "gm_program"
        )

        matches = suggestions.get(
            hint_family,
            []
        )

        if matches:

            score, preset = matches[0]

            if (
                preset["program"]
                != expected_program
            ):

                hint_top_mismatches.append(
                    (
                        name,
                        hint,
                        score,
                        preset,
                    )
                )

    #
    # Classification
    #
    if hint:

        with_hint.append(
            (
                name,
                hint,
                families
            )
        )

    elif families:

        family_only.append(
            (
                name,
                families
            )
        )

    else:

        unknown.append(
            name
        )

    #
    # Suggestions réellement produites
    #
    total_matches = sum(
        len(matches)
        for matches
        in suggestions.values()
    )

    if total_matches == 0:

        empty_suggestions.append(
            name
        )

    #
    # Hint/famille potentiellement contradictoires
    #
    if (
        hint
        and
        families
        and
        not families_are_compatible(
            hint["family"],
            families
        )
    ):
        conflicts.append(
            (
                name,
                hint,
                families
            )
        )

print()
print("====================")
print("HINT GM")
print("====================")

for name, hint, families in with_hint:

    print(
        f"{name:<32}",
        hint,
        families
    )

print()
print("====================")
print("FAMILLE SEULEMENT")
print("====================")

for name, families in family_only:

    print(
        f"{name:<32}",
        families
    )

print()
print("====================")
print("INCONNUS")
print("====================")

for name in unknown:

    print(name)

print()
print("====================")
print("AUCUNE SUGGESTION")
print("====================")

for name in empty_suggestions:

    print(name)

print()
print("====================")
print("HINT / FAMILLE À VÉRIFIER")
print("====================")

for name, hint, families in conflicts:

    print(
        f"{name:<32}",
        hint,
        families
    )

print()
print("====================")
print("HINT GM NON RESPECTÉ")
print("====================")

for (
    name,
    gm_hint,
    suggestions,
) in hint_program_mismatches:

    print(
        name,
        gm_hint,
    )

    for family, matches in suggestions.items():

        print(
            "   ",
            family,
            [
                (
                    preset["bank"],
                    preset["program"],
                    preset["name"],
                )
                for score, preset in matches
            ]
        )

print()
print("====================")
print("MEILLEUR HINT GM INCORRECT")
print("====================")

for (
    name,
    gm_hint,
    score,
    preset,
) in hint_top_mismatches:

    print(
        name,
        gm_hint,
        "→",
        (
            preset["bank"],
            preset["program"],
            preset["name"],
        ),
        "score:",
        round(score, 3),
    )

print()
print("====================")
print("FAMILLE SEULEMENT À VÉRIFIER")
print("====================")

for (
    name,
    family,
    detail,
) in family_only_mismatches:

    print(
        name,
        family,
        "→",
        detail,
    )

print()
print("====================")
print("SUGGESTIONS INVALIDES")
print("====================")

for (
    name,
    family,
    bank,
    program,
    preset_name,
) in invalid_suggestions:

    print(
        name,
        family,
        "→",
        (
            bank,
            program,
            preset_name,
        )
    )

print()
print("====================")
print("SUGGESTIONS EN DOUBLON")
print("====================")

for (
    name,
    family,
    key,
    preset_name,
) in duplicate_suggestions:

    print(
        name,
        family,
        "→",
        key,
        preset_name,
    )

print()
print("====================")
print("CHAMPS MANQUANTS")
print("====================")

for (
    name,
    family,
    missing,
    preset,
) in missing_fields:

    print(
        name,
        family,
        "→",
        missing,
        preset,
    )

print()
print("====================")
print("SCORES MAL ORDONNÉS")
print("====================")

for (
    name,
    family,
    scores,
) in unsorted_suggestions:

    print(
        name,
        family,
        "→",
        scores,
    )

print()
print("====================")
print("SCORES ABERRANTS")
print("====================")

for (
    name,
    family,
    score,
    preset_name,
) in abnormal_scores:

    print(
        name,
        family,
        "→",
        score,
        preset_name,
    )

print()
print("====================")
print("RÉSUMÉ")
print("====================")

print(
    "Noms Fusion       :",
    len(names)
)

print(
    "Hint GM           :",
    len(with_hint)
)

print(
    "Famille seulement :",
    len(family_only)
)

print(
    "Inconnus          :",
    len(unknown)
)

print(
    "Sans suggestion   :",
    len(empty_suggestions)
)

print(
    "Conflits apparents:",
    len(conflicts)
)

print(
    "Hints non respectés:",
    len(hint_program_mismatches)
)

print(
    "Meilleurs hints incorrects:",
    len(hint_top_mismatches)
)

print(
    "Familles seules incorrectes:",
    len(family_only_mismatches)
)

print(
    "Suggestions invalides:",
    len(invalid_suggestions)
)

print(
    "Suggestions en doublon:",
    len(duplicate_suggestions)
)

print(
    "Presets avec champs manquants:",
    len(missing_fields)
)

print(
    "Scores mal ordonnés:",
    len(unsorted_suggestions)
)

print(
    "Scores aberrants:",
    len(abnormal_scores)
)
