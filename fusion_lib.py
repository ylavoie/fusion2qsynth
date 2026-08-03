VERSION = "1.0"
PROJECT = "Fusion2QSynth"

import mido
import json
import os
import shutil

FILE = "fusion.json"
FUSION_IN = "CH345"
SYNTH_OUT = "FLUID Synth"

# JSON

def load_json():

    if os.path.exists(FILE):

        with open(FILE, "r") as f:
            return json.load(f)

    return {}

def save_json(data):

    with open(FILE, "w") as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )
    backup_json()
    #json.dump(...)
    errors = validate_mix(data)

    if errors:

        print()
        print(
            "Attention : validation Fusion"
        )

        for e in errors:

            print(
                "-",
                e
            )

def backup_json():
    if os.path.exists(FILE):
        shutil.copy2(FILE, FILE + ".bak")

# MIDI

def find_fusion_input():

    for port in mido.get_input_names():

        if FUSION_IN.lower() in port.lower():

            return port

    return None

def find_fluidsynth_output():

    for port in mido.get_output_names():

        if SYNTH_OUT.lower() in port.lower():

            return port

    return None

def panic(out):

    for ch in range(16):

        out.send(
            mido.Message(
                "control_change",
                channel=ch,
                control=123,
                value=0
            )
        )

        out.send(
            mido.Message(
                "control_change",
                channel=ch,
                control=121,
                value=0
            )
        )

# NOTES

NOTE_NAMES = (
    "C","C#","D","D#","E","F",
    "F#","G","G#","A","A#","B"
)

def note_name(note):
    octave = note // 12 - 1

    return (
        NOTE_NAMES[note % 12]
        +
        str(octave)
    )

#def note_range()

# Mix
def get_mix(data, mix_id):

    return data.get(mix_id)

def get_part(mix, part_id):

    return mix.get(
        "parts",
        {}
    ).get(
        str(part_id)
    )

def iter_parts(mix):

    for part_id in sorted(
        mix.get(
            "parts",
            {}
        ),
        key=int
    ):

        yield (
            part_id,
            mix["parts"][part_id]
        )

def sort_mix_ids(data):

    return sorted(
        data.keys(),
        key=lambda x: (
            int(x.split(":")[0]),
            int(x.split(":")[1])
        )
    )

def is_part_configured(part):

    return (
        "sf2_bank" in part
        and
        "sf2_program" in part
    )

def build_channel_map(data):

    channels = {}

    for mix_id, mix in data.items():

        for part_id, part in mix.get(
            "parts",
            {}
        ).items():

            ch = part.get(
                "midi_channel"
            )

            if ch is None:

                continue

            channels[ch] = {

                "mix_id":
                    mix_id,

                "part_id":
                    part_id,

                "part":
                    part
            }

    return channels

# Validation
def validate_mix(data):

    errors = []

    if not isinstance(data, dict):

        return [
            "Le fichier fusion.json n'est pas un dictionnaire."
        ]

    for mix_id, mix in data.items():

        if not isinstance(mix, dict):

            errors.append(
                f"{mix_id} : définition invalide."
            )

            continue

        if "parts" not in mix:

            errors.append(
                f"{mix_id} : aucune PART."
            )

            continue

        channels = []

        for part_id, part in mix["parts"].items():

            prefix = f"{mix_id} PART {part_id}"

            #
            # Canal
            #

            ch = part.get("midi_channel")

            if ch is None:

                errors.append(
                    f"{prefix} : midi_channel absent."
                )

            elif not (1 <= ch <= 16):

                errors.append(
                    f"{prefix} : canal MIDI invalide ({ch})."
                )

            else:

                channels.append(ch)

            #
            # Fusion
            #

            if "bank" not in part:

                errors.append(
                    f"{prefix} : bank Fusion absente."
                )

            if "program" not in part:

                errors.append(
                    f"{prefix} : program Fusion absent."
                )

            #
            # SF2
            #

            if "name" in part:

                if "sf2_bank" not in part:

                    errors.append(
                        f"{prefix} : sf2_bank absent."
                    )

                if not is_part_configured(part):

                    errors.append(
                        f"{prefix} : sf2_program absent."
                    )

            #
            # Zone notes
            #

            if "note_min" in part and "note_max" in part:

                a = part["note_min"]
                b = part["note_max"]

                if not (0 <= a <= b <= 127):

                    errors.append(
                        f"{prefix} : zone de notes invalide."
                    )

            #
            # Velocity
            #

            if (
                "velocity_min" in part
                and
                "velocity_max" in part
            ):

                a = part["velocity_min"]
                b = part["velocity_max"]

                if not (0 <= a <= b <= 127):

                    errors.append(
                        f"{prefix} : plage de vélocité invalide."
                    )

        #
        # Doublons de canaux
        #

        duplicates = sorted({
            ch
            for ch in channels
            if channels.count(ch) > 1
        })

        if duplicates:

            errors.append(
                f"{mix_id} : canaux MIDI partagés {duplicates}."
            )

    return errors

# Affichage
def print_mix(mix_id, mix):

    print()

    print("=" * 40)

    print(
        mix.get(
            "name",
            mix_id
        )
    )

    print("=" * 40)

    for part_id, part in iter_parts(mix):

        print_part(
            part_id,
            part
        )

def print_part(part_id, part):

    print()
    print(f"PART {part_id}")

    print(
        "  Canal MIDI :",
        part.get("midi_channel", "?")
    )

    print(
        "  Fusion : Bank",
        part.get("bank", "?"),
        "Program",
        part.get("program", "?")
    )

    if "note_min" in part:

        print(
            "  Zone :",
            f"{note_name(part['note_min'])}"
            " - "
            f"{note_name(part['note_max'])}"
        )

    if "velocity_min" in part:

        print(
            "  Velocity :",
            part["velocity_min"],
            "-",
            part["velocity_max"]
        )

    if "sf2_program" in part:

        print(
            "  QSynth :",
            part.get(
                "name",
                "?"
            )
        )

        print(
            "    SF2 Bank",
            part["sf2_bank"],
            "Program",
            part["sf2_program"]
        )

    else:

        print(
            "  QSynth : Non configuré"
        )

#def summarize_mix(mix):

# System
def system_status():

    status = {}

    status["fusion"] = (
        find_fusion_input()
        is not None
    )

    status["fluidsynth"] = (
        find_fluidsynth_output()
        is not None
    )

    data = load_json()

    status["mix_count"] = len(data)

    return status