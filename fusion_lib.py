import mido
import logging
import time

from fusion_constants import (
    FUSION_INPUT_NAME,
    FLUIDSYNTH_OUTPUT_NAME,
    LOG_FILE
)

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

        if FUSION_INPUT_NAME.lower() in port.lower():

            return port

    return None

def find_fluidsynth_output():

    for port in mido.get_output_names():

        if FLUIDSYNTH_OUTPUT_NAME.lower() in port.lower():

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

    mix_ids = [
        key
        for key in data.keys()
        if ":" in key
    ]

    return sorted(
        mix_ids,
        key=lambda x: (
            int(x.split(":")[0]),
            int(x.split(":")[1])
        )
    )

# Affichage
def print_mix(project, mix_id, mix):

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
            project,
            part_id,
            part
        )

def print_part(
    project,
    part_id,
    part
):

    print()

    print(
        "PART",
        part_id
    )

    print(
        "----------------"
    )


    instrument = project.resolve_part_instrument(
        part
    )


    if instrument:

        print(
            "Instrument :",
            instrument.get(
                "name",
                "?"
            )
        )

        print(
            "Bank       :",
            instrument.get(
                "sf2_bank",
                0
            )
        )

        print(
            "Program    :",
            instrument.get(
                "sf2_program",
                0
            )
        )

    else:

        print(
            "Instrument : Non configuré"
        )


    print(
        "Canal MIDI :",
        part.get(
            "midi_channel",
            "?"
        )
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
