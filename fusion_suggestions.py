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
    "english_horn": [
        "english horn"
    ],

    "french_horn": [
        "french horn",
        "french horns"
    ],

    "trombone": [
        "trombone"
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

FUSION_GM_HINTS = {
    "holy grail": {
        "family": "piano",
        "gm_program": 0
    },
    "concert grand": {
        "family": "piano",
        "gm_program": 0
    },
    "pop piano": {
        "family": "piano",
        "gm_program": 0
    },
    "bright piano": {
        "family": "piano",
        "gm_program": 1
    },
    "rock piano": {
        "family": "piano",
        "gm_program": 1
    },
    "honky tonk": {
        "family": "piano",
        "gm_program": 3
    },
    "detuned piano": {
        "family": "piano",
        "gm_program": 3
    },
    "suitcase": {
        "family": "piano",
        "gm_program": 4
    },
    "mark i": {
        "family": "piano",
        "gm_program": 4
    },
    "wurlitzer": {
        "family": "piano",
        "gm_program": 5
    },
    "fm piano": {
        "family": "piano",
        "gm_program": 5
    },
    "big fat upright bass": {
        "family": "contrabass",
        "gm_program": 43
    },
    "upright bass": {
        "family": "contrabass",
        "gm_program": 32
    },
    "fingered bass": {
        "family": "bass",
        "gm_program": 33
    },
    "picked bass": {
        "family": "bass",
        "gm_program": 34
    },
    "square lead": {
        "family": "square_lead",
        "gm_program": 80
    },
    "sawtooth lead": {
        "family": "lead",
        "gm_program": 81
    },
    "waterchimes": {
        "family": "pad",
        "gm_program": 88
    }
}

FUSION_FAMILY_OVERRIDES = {
    "arco marcato strings": {
        "violin"
    },
    "lyrical english horn": {
        "english_horn"
    },
    "big classical brass": {
        "french_horn",
        "trombone"
    }
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

def normalize_preset_name(
    name
):

    normalized = normalize_name(
        name
    )

    words = [
        word
        for word in normalized.split()
        if word != "expr"
    ]

    return " ".join(
        words
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

def detect_gm_hint(
    name
):

    normalized_name = normalize_name(
        name
    )

    best_match = None

    for term, hint in FUSION_GM_HINTS.items():

        if not contains_term(
            normalized_name,
            term
        ):

            continue

        if (
            best_match is None
            or
            len(term) > len(best_match[0])
        ):

            best_match = (
                term,
                hint
            )

    if best_match is None:

        return None

    return dict(
        best_match[1]
    )

def detect_families(name):

    normalized_name = normalize_name(
        name
    )

    override = FUSION_FAMILY_OVERRIDES.get(
        normalized_name
    )

    if override is not None:

        return set(
            override
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

    gm_hint = detect_gm_hint(
        fusion_program["name"]
    )

    candidates = []

    for preset in sf2_presets:

        preset_families = detect_families(
            preset["name"]
        )

        gm_match = (
            gm_hint
            and
            gm_hint.get("family") == family
            and
            gm_hint.get("gm_program")
            == preset["program"]
            and
            preset["bank"] == 0
        )

        if (
            family not in preset_families
            and
            not gm_match
        ):

            continue

        score = SequenceMatcher(
            None,
            normalize_name(
                fusion_program["name"]
            ),
            normalize_preset_name(
                preset["name"]
            )
        ).ratio()

        if (
            gm_hint
            and
            gm_hint.get("gm_program")
            ==
            preset["program"]
        ):

            score += 0.40

        if (
            fusion_program["program"]
            ==
            preset["program"]
        ):

            score += 0.10

        normalized_preset = normalize_name(
            preset["name"]
        )

        if "expr" in normalized_preset.split():

            score -= 0.05

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

    gm_hint = detect_gm_hint(
        fusion_program["name"]
    )

    if (
        gm_hint
        and
        gm_hint.get("family")
    ):

        families.add(
            gm_hint["family"]
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