#!/usr/bin/env python3

"""
Constantes globales Fusion2QSynth
"""

PROJECT = "Fusion2QSynth"

VERSION = "2.1.0"


# Fichiers

LOG_FILE = "fusion.log"

LAST_MIX_FILE = "last_mix.json"


# MIDI

FUSION_INPUT_NAME = "CH345"

FLUIDSYNTH_OUTPUT_NAME = "FLUID Synth"

# Global Fusion 8HD MIDI Channel
FUSION_DEFAULT_CHANNEL = 1


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

# Debug

DEBUG = False