#!/usr/bin/env python3

"""
Constantes globales Fusion2QSynth
"""

PROJECT = "Fusion2QSynth"

VERSION = "1.2.0"


# Fichiers

FUSION_FILE = "fusion.json"

LAST_MIX_FILE = "last_mix.json"

LOG_FILE = "fusion.log"


# MIDI

FUSION_INPUT_NAME = "CH345"

FLUIDSYNTH_OUTPUT_NAME = "FLUID Synth"


# MIDI limites

MIDI_CHANNEL_MIN = 1
MIDI_CHANNEL_MAX = 16

MIDI_NOTE_MIN = 0
MIDI_NOTE_MAX = 127

MIDI_VELOCITY_MIN = 0
MIDI_VELOCITY_MAX = 127


# SF2

SF2_BANK_MIN = 0
SF2_BANK_MAX = 127

SF2_PROGRAM_MIN = 0
SF2_PROGRAM_MAX = 127