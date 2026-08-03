#!/usr/bin/env python3

import subprocess
import json
import re

SF2DUMP = "sf2dump"

def dump_sf2(filename):

    result = subprocess.run(
        [
            SF2DUMP,
            filename
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:

        raise Exception(
            result.stderr
        )

    return result.stdout

def parse_presets(text):

    presets = []

    for line in text.splitlines():

        line = line.strip()

        match = re.search(
            r"^(.*?)\s*\(Preset:\s*(\d+),\s*Bank:\s*(\d+)",
            line
        )

        if match:

            name = match.group(1).strip()

            program = int(
                match.group(2)
            )

            bank = int(
                match.group(3)
            )

            preset_id = (
                re.sub(
                    r"[^a-z0-9]+",
                    "_",
                    name.lower()
                ).strip("_")
            )

            presets.append(
                {
                    "id": preset_id,
                    "name": name,
                    "sf2_bank": bank,
                    "sf2_program": program
                }
            )

    return presets

def build_library(sf2_file):

    dump = dump_sf2(
        sf2_file
    )

    presets = parse_presets(
        dump
    )

    return {

        "soundfont":
            sf2_file,

        "presets":
            presets

    }

def save_library(
    library,
    filename="sf2_library.json"
):

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            library,
            f,
            indent=2,
            ensure_ascii=False
        )

def show_presets(presets):

    print()

    print(
        len(presets),
        "presets trouvés"
    )

    print()

    for p in presets:

        print(
            f"{p['id']} : "
            f"Bank {p['sf2_bank']} "
            f"Program {p['sf2_program']} "
            f"- {p['name']}"
        )

if __name__ == "__main__":

    import sys

    if len(sys.argv) < 2:

        print(
            "Usage : sf2_library.py fichier.sf2"
        )

        exit(1)

    sf2_file = sys.argv[1]

    library = build_library(
        sf2_file
    )

    show_presets(
        library["presets"]
    )

    save_library(
        library
    )

    print()

    print(
        "Bibliothèque sauvegardée"
    )