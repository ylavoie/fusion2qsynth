import re

from fusion_suggestions import (
    detect_families,
    matches_for_family
)

FUSION_ITEM_RE = re.compile(
    r"(\d+)\s+([A-P]-\s*\d+)\s+"
)

def parse_fusion_line(
    line,
    bank_name
):

    matches = list(
        FUSION_ITEM_RE.finditer(
            line
        )
    )

    items = []

    for index, match in enumerate(matches):

        start = match.end()

        if index + 1 < len(matches):

            end = matches[
                index + 1
            ].start()

        else:

            end = len(line)

        program = int(
            match.group(1)
        )

        location = (
            match.group(2)
            .replace(" ", "")
        )

        name = line[
            start:end
        ].strip()

        items.append(
            {
                "bank": bank_name,
                "program": program,
                "location": location,
                "name": name
            }
        )

    return items

def load_fusion_programs(
    filename
):

    programs = []

    bank_name = None

    with open(
        filename,
        encoding="utf-8",
        errors="replace"
    ) as f:

        for line in f:

            line = line.rstrip()

            if line.startswith(
                "ROM: PRESET "
            ):

                bank_name = (
                    line.split(
                        "(",
                        1
                    )[0]
                    .replace(
                        "ROM:",
                        ""
                    )
                    .strip()
                )

                continue

            if not bank_name:

                continue

            programs.extend(
                parse_fusion_line(
                    line,
                    bank_name
                )
            )

    return programs

'''
print(
    "Programmes Fusion :",
    len(fusion)
)

for program in fusion[:20]:

    print(
        program["bank"],
        program["program"],
        program["name"]
    )
'''

SF2_PRESET_RE = re.compile(
    r"^\s*(.*?)\s+"
    r"\(Preset:\s*(\d+),\s*"
    r"Bank:\s*(\d+),\s*"
    r"Preset bag:\s*\d+\)"
)

def load_sf2_presets(filename):

    presets = []

    with open(
        filename,
        encoding="utf-8",
        errors="replace"
    ) as f:

        for line in f:

            match = SF2_PRESET_RE.match(
                line
            )

            if not match:

                continue

            name = match.group(1).strip()
            program = int(match.group(2))
            bank = int(match.group(3))

            presets.append(
                {
                    "bank": bank,
                    "program": program,
                    "name": name
                }
            )

    return presets

sf2 = load_sf2_presets(
    "sf2_program_list.txt"
)

def best_name_match(
    fusion_program,
    sf2_presets
):

    fusion_families = detect_families(
        fusion_program["name"]
    )

    candidates = []

    #
    # Chercher d'abord les presets
    # appartenant à une famille commune.
    #
    if fusion_families:

        for preset in sf2_presets:

            preset_families = detect_families(
                preset["name"]
            )

            if fusion_families & preset_families:

                candidates.append(
                    preset
                )

    #
    # Aucune famille exploitable :
    # revenir à tous les presets.
    #
    if not candidates:

        candidates = sf2_presets

    best = None
    best_score = 0.0

    for preset in candidates:

        score = similarity(
            fusion_program["name"],
            preset["name"]
        )

        #
        # Le même numéro de programme
        # constitue seulement un indice.
        #
        if (
            fusion_program["program"]
            ==
            preset["program"]
        ):

            score += 0.15

        if score > best_score:

            best_score = score
            best = preset

    return best, best_score

def best_matches(
    fusion_program,
    sf2_presets,
    limit=3
):

    fusion_families = detect_families(
        fusion_program["name"]
    )

    candidates = []

    for preset in sf2_presets:

        preset_families = detect_families(
            preset["name"]
        )

        common_families = (
            fusion_families
            &
            preset_families
        )

        if (
            fusion_families
            and
            not common_families
        ):

            continue

        family_coverage = (
            len(common_families)
            /
            len(fusion_families)
        )

        score = similarity(
            fusion_program["name"],
            preset["name"]
        )

        score += (
            family_coverage
            * 0.25
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

fusion = load_fusion_programs(
    "fusion_program_list.txt"
)

for program in fusion:

    families = detect_families(
        program["name"]
    )

    if not families:

        continue

    print()
    print(
        program["bank"],
        program["program"],
        program["name"],
        "[" + ",".join(sorted(families)) + "]"
    )

    for family in sorted(families):

        print()
        print(
            " ",
            family.upper()
        )

        matches = matches_for_family(
            program,
            sf2,
            family
        )

        if not matches:

            print(
                "    Aucun candidat"
            )

            continue

        for rank, (score, preset) in enumerate(
            matches,
            start=1
        ):

            print(
                f"    {rank}. "
                f"{preset['bank']}:{preset['program']} "
                f"{preset['name']:<28} "
                f"{score:.2f}"
            )