#!/usr/bin/env python3

from functools import lru_cache
import re
from difflib import SequenceMatcher

from fusion_gm_map import (
    FUSION_GM_HINTS,
    GM_PROGRAMS,
    GM_DRUM_KIT_PROGRAMS,
    FAMILIES,
    FUSION_FAMILY_OVERRIDES
)

def detect_gm_program(
    name
):

    normalized_name = normalize_name(
        name
    )

    entry = GM_PROGRAMS.get(
        normalized_name
    )

    if entry is None:

        return None

    return dict(
        entry
    )

def detect_gm_drum_kit(
    name
):

    hint = detect_gm_hint(
        name
    )

    if hint is None:
        return None

    if hint.get("family") != "drums":
        return None

    program = hint.get(
        "gm_program"
    )

    if program not in GM_DRUM_KIT_PROGRAMS:
        return None

    return {
        "sf2_bank": 128,
        "sf2_program": program,
    }

def normalize_name(name):

    name = re.sub(
        r"(?<=[a-z])(?=[A-Z])",
        " ",
        name
    )

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

@lru_cache(
    maxsize=None
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

@lru_cache(
    maxsize=None
)
def _detect_gm_hint_cached(
    name
):

    gm_program = detect_gm_program(
        name
    )

    if gm_program is not None:

        return tuple(
            gm_program.items()
        )

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

    return tuple(
        best_match[1].items()
    )


def detect_gm_hint(
    name
):

    result = _detect_gm_hint_cached(
        name
    )

    if result is None:

        return None

    return dict(
        result
    )
@lru_cache(
    maxsize=None
)
def _detect_families_cached(
    name
):

    normalized_name = normalize_name(
        name
    )

    override = FUSION_FAMILY_OVERRIDES.get(
        normalized_name
    )

    if override is not None:

        return frozenset(
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

    return frozenset(
        families
    )

def detect_families(
    name
):
    return set(
        _detect_families_cached(
            name
        )
    )

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
    gm_hint,
    limit=3
):
    normalized_fusion_name = normalize_name(
        fusion_program["name"]
    )

    candidates = []
    expected_bank = 0

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
            preset["bank"] == expected_bank
        )

        if (
            family not in preset_families
            and
            not gm_match
        ):

            continue

        score = SequenceMatcher(
            None,
            normalized_fusion_name,
            normalize_preset_name(
                preset["name"]
            )
        ).ratio()

        if gm_match:

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
                gm_match,
                score,
                preset
            )
        )

    candidates.sort(
        key=lambda item: (
            item[0],
            item[1],
        ),
        reverse=True
    )

    return [
        (
            score,
            preset,
        )
        for gm_match, score, preset
        in candidates[:limit]
    ]

def suggest_instruments(
    fusion_program,
    sf2_presets,
    limit=3
):

    drum_kit = detect_gm_drum_kit(
        fusion_program["name"]
    )

    if drum_kit is not None:

        matches = []

        for preset in sf2_presets:

            if (
                preset["bank"]
                == drum_kit["sf2_bank"]
                and
                preset["program"]
                == drum_kit["sf2_program"]
            ):

                matches.append(
                    (
                        1.0,
                        preset
                    )
                )

        if matches:

            return {
                "drums": matches[:limit]
            }

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
            gm_hint,
            limit=limit
        )

    return suggestions