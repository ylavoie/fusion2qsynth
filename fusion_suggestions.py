#!/usr/bin/env python3

import re
from difflib import SequenceMatcher

FAMILIES = {
    "piano": [
        "piano",
        "grand"
    ],
    "electric_piano": [
        "electric piano",
        "ep",
        "wurly",
        "suitcase"
    ],
    "harpsichord": [
        "harpsi",
        "harpsichord"
    ],
    "organ": [
        "organ",
        "drawbar"
    ],
    "guitar": [
        "guitar",
        "gtr",
        "string guitar"
    ],
    "violin": [
        "violin"
    ],
    "cello": [
        "cello"
    ],
    "contrabass": [
        "upright bass",
        "double bass",
        "contrabass",
        "acoustic upright"
    ],
    "bass": [
        "bass",
        "fretless bass",
        "slap bass",
        "fingered bass",
        "picked bass"
    ],
    "strings": [
        "strings",
        "string ensemble"
    ],
    "harp": [
        "harp"
    ],
    "trumpet": [
        "trumpet"
    ],
    "trombone": [
        "trombone"
    ],
    "horn": [
        "horn"
    ],
    "clarinet": [
        "clarinet"
    ],
    "oboe": [
        "oboe"
    ],
    "bassoon": [
        "bassoon"
    ],
    "flute": [
        "flute"
    ],
    "recorder": [
        "recorder"
    ],
    "sax": [
        "sax"
    ],
    "pan_flute": [
        "pan",
        "pan flute"
    ],
    "marimba": [
        "marimba"
    ],
    "vibraphone": [
        "vibes",
        "vibraphone"
    ],
    "xylophone": [
        "xylophone"
    ],
    "bells": [
        "bell",
        "bells",
        "chime"
    ],
    "choir": [
        "choir",
        "aah",
        "ooh"
    ],
    "pad": [
        "pad"
    ],
    "lead": [
        "lead"
    ],
    "drums": [
        "kit",
        "drum",
        "percussion"
    ],
    "square_wave": [
        "square"
    ]
}

def normalize_name(name):

    name = name.lower()

    name = re.sub(
        r"[^a-z0-9]+",
        " ",
        name
    )

    return " ".join(
        name.split()
    )

def contains_term(
    normalized_name,
    term
):

    words = normalized_name.split()
    term_words = term.split()

    if len(term_words) == 1:

        return term in words

    size = len(term_words)

    for i in range(
        len(words) - size + 1
    ):

        if (
            words[i:i + size]
            ==
            term_words
        ):

            return True

    return False

def detect_families(name):

    normalized_name = normalize_name(
        name
    )

    families = set()

    for family, aliases in FAMILIES.items():

        for alias in aliases:

            if contains_term(
                normalized_name,
                alias
            ):

                families.add(
                    family
                )

                break

    #
    # Corrections sémantiques
    #

    if contains_term(
        normalized_name,
        "bass drum"
    ):

        families.discard(
            "bass"
        )

        families.add(
            "drums"
        )

    if (
        contains_term(
            normalized_name,
            "drum n bass"
        )
        or
        contains_term(
            normalized_name,
            "drum and bass"
        )
    ):

        families.discard(
            "drums"
        )

        families.add(
            "bass"
        )
    #
    # Spécialisations
    #
    if "contrabass" in families:

        families.discard(
            "bass"
        )

    if "electric_piano" in families:

        families.discard(
            "piano"
        )

    if "pan_flute" in families:

        families.discard(
            "flute"
        )
    #
    # Square
    #
    if "square_wave" in families:

        families.discard(
            "square_wave"
        )

        if "bass" not in families:

            families.add(
                "square_lead"
            )

    return families

def similarity(
    name1,
    name2
):

    return SequenceMatcher(
        None,
        normalize_name(name1),
        normalize_name(name2)
    ).ratio()

def matches_for_family(
    fusion_program,
    sf2_presets,
    family,
    limit=3
):

    candidates = []

    for preset in sf2_presets:

        preset_families = detect_families(
            preset["name"]
        )

        if family not in preset_families:

            continue

        score = similarity(
            fusion_program["name"],
            preset["name"]
        )

        if (
            fusion_program["program"]
            ==
            preset["program"]
        ):

            score += 0.10

        candidates.append(
            (
                score,
                preset
            )
        )

    candidates.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return candidates[:limit]

def suggest_instruments(
    fusion_program,
    sf2_presets,
    limit=3
):

    families = detect_families(
        fusion_program["name"]
    )

    suggestions = {}

    for family in sorted(families):

        suggestions[family] = matches_for_family(
            fusion_program,
            sf2_presets,
            family,
            limit=limit
        )

    return suggestions