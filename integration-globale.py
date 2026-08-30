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
