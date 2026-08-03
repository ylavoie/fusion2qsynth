VERSION = "1.0"
PROJECT = "Fusion2QSynth"

import mido
import logging
import time

FUSION_IN = "CH345"
SYNTH_OUT = "FLUID Synth"
LOG_FILE = "fusion.log"

# Logging

def _log(level, message):

    timestamp = time.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    line = (
        f"{timestamp} "
        f"[{level}] "
        f"{message}"
    )

    with open(
        LOG_FILE,
        "a",
        encoding="utf-8"
    ) as f:

        f.write(line + "\n")

def log_info(message):

    _log(
        "INFO",
        message
    )

def log_warning(message):

    _log(
        "WARN",
        message
    )

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def log_event(message):

    logging.info(message)

def log_error(message):

    logging.error(message)

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
def system_status(project):

    status = {}

    status["fusion"] = (
        find_fusion_input()
        is not None
    )

    status["fluidsynth"] = (
        find_fluidsynth_output()
        is not None
    )

    status["mix_count"] = project.count_mixes()

    return status
