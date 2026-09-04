import mido
import logging

from fusion_constants import (
    FUSION_INPUT_NAME,
    FLUIDSYNTH_OUTPUT_NAME,
    LOG_FILE
)

# Logging

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [ %(levelname)s ] %(message)s"
)

def log_info(message):

    logging.info(message)

def log_warning(message):

    logging.warning(message)

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

def note_number(
    value
):

    value = value.strip().upper()

    try:

        note = int(value)

        if 0 <= note <= 127:

            return note

        return None

    except ValueError:

        pass

    if len(value) < 2:

        return None

    if len(value) >= 3 and value[1] == "#":

        name = value[:2]
        octave_text = value[2:]

    else:

        name = value[:1]
        octave_text = value[1:]

    if name not in NOTE_NAMES:

        return None

    try:

        octave = int(
            octave_text
        )

    except ValueError:

        return None

    note = (
        (octave + 1) * 12
        +
        NOTE_NAMES.index(name)
    )

    if not 0 <= note <= 127:

        return None

    return note

def note_range(note_min=None, note_max=None):

    if note_min is None and note_max is None:
        return "défaut (C-1) → défaut (G9)"

    if note_min is None:
        return (
            f"défaut (C-1) → "
            f"{note_name(note_max)}"
        )

    if note_max is None:
        return (
            f"{note_name(note_min)} → "
            f"défaut (G9)"
        )

    if note_min > note_max:
        note_min, note_max = note_max, note_min

    return (
        f"{note_name(note_min)} → "
        f"{note_name(note_max)}"
    )

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
    status["program_count"] = project.count_programs()
    status["song_count"] = project.count_songs()

    return status
