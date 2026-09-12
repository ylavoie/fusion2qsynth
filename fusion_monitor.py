#!/usr/bin/env python3

import mido
import time

from fusion_lib import (
    find_fusion_input,
    note_name
)

CC_NAMES = {
    0: "Bank Select",
    1: "Modulation",
    2: "Breath",
    4: "Foot Controller",
    5: "Portamento Time",
    6: "Data Entry MSB",
    7: "Volume",
    8: "Balance",
    10: "Pan",
    11: "Expression",
    12: "Effect Ctrl 1",
    13: "Effect Ctrl 2",
    64: "Sustain",
    65: "Portamento",
    66: "Sostenuto",
    67: "Soft Pedal",
    68: "Legato",
    69: "Hold 2",
    70: "Sound Variation",
    71: "Resonance",
    72: "Release",
    73: "Attack",
    74: "Brightness",
    75: "Sound Ctrl 6",
    76: "Sound Ctrl 7",
    77: "Sound Ctrl 8",
    78: "Sound Ctrl 9",
    79: "Sound Ctrl 10",
    80: "General Purpose 5",
    81: "General Purpose 6",
    82: "General Purpose 7",
    83: "General Purpose 8",
    84: "Portamento Control",
    91: "Reverb",
    92: "Tremolo",
    93: "Chorus",
    94: "Detune",
    95: "Phaser",
    96: "Data Increment",
    97: "Data Decrement",
    98: "NRPN LSB",
    99: "NRPN MSB",
    100: "RPN LSB",
    101: "RPN MSB",
    120: "All Sound Off",
    121: "Reset Controllers",
    122: "Local Control",
    123: "All Notes Off",
    124: "Omni Off",
    125: "Omni On",
    126: "Mono Mode",
    127: "Poly Mode",
}

def main():

    port_name = find_fusion_input()

    if not port_name:

        raise Exception(
            "Fusion MIDI introuvable"
        )

    print(
        "Monitoring :",
        port_name
    )

    start_time = time.monotonic()

    with mido.open_input(port_name) as inp:

        try:
            for msg in inp:

                elapsed = time.monotonic() - start_time

                if msg.type == "note_on":

                    print(
                        f"[{elapsed:12.4f}] "
                        f"NOTE ON        "
                        f"CH {msg.channel + 1:2}  "
                        f"{note_name(msg.note):3}  "
                        f"Vel {msg.velocity}"
                    )

                elif msg.type == "note_off":

                    print(
                        f"[{elapsed:12.4f}] "
                        f"NOTE OFF       "
                        f"CH {msg.channel + 1:2}  "
                        f"{note_name(msg.note):3}  "
                        f"Vel {msg.velocity}"
                    )

                elif msg.type == "control_change":

                    name = CC_NAMES.get(
                        msg.control,
                        "Undefined"
                    )

                    print(
                        f"[{elapsed:12.4f}] "
                        f"CONTROL        "
                        f"CH {msg.channel + 1:2}  "
                        f"CC {msg.control:3}  "
                        f"{name:<20}"
                        f"Value {msg.value}"
                    )

                elif msg.type == "program_change":

                    print(
                        f"[{elapsed:12.4f}] "
                        f"PROGRAM        "
                        f"CH {msg.channel + 1:2}  "
                        f"Program {msg.program}"
                    )

                elif msg.type == "pitchwheel":

                    print(
                        f"[{elapsed:12.4f}] "
                        f"PITCHWHEEL     "
                        f"CH {msg.channel + 1:2}  "
                        f"Pitch {msg.pitch}"
                    )

                elif msg.type == "aftertouch":

                    print(
                        f"[{elapsed:12.4f}] "
                        f"AFTERTOUCH     "
                        f"CH {msg.channel + 1:2}  "
                        f"Value {msg.value}"
                    )

                elif msg.type == "polytouch":

                    print(
                        f"[{elapsed:12.4f}] "
                        f"POLYTOUCH      "
                        f"CH {msg.channel + 1:2}  "
                        f"{note_name(msg.note):3}  "
                        f"Value {msg.value}"
                    )

                elif msg.type == "sysex":

                    print(
                        f"[{elapsed:12.4f}] "
                        "SYSEX          "
                        f"Data {list(msg.data)}"
                    )

                elif msg.type == "quarter_frame":

                    print(
                        f"[{elapsed:12.4f}] "
                        "QUARTER FRAME  "
                        f"Type {msg.frame_type}  "
                        f"Value {msg.frame_value}"
                    )

                elif msg.type == "songpos":

                    print(
                        f"[{elapsed:12.4f}] "
                        "SONG POSITION  "
                        f"Pos {msg.pos}"
                    )

                elif msg.type == "song_select":

                    print(
                        f"[{elapsed:12.4f}] "
                        "SONG SELECT    "
                        f"Song {msg.song}"
                    )

                elif msg.type == "tune_request":

                    print(
                        f"[{elapsed:12.4f}] "
                        "TUNE REQUEST"
                    )

                elif msg.type == "clock":

                    print(
                        f"[{elapsed:12.4f}] "
                        "CLOCK"
                    )

                elif msg.type == "start":

                    print(
                        f"[{elapsed:12.4f}] "
                        "START"
                    )

                elif msg.type == "continue":

                    print(
                        f"[{elapsed:12.4f}] "
                        "CONTINUE"
                    )

                elif msg.type == "stop":

                    print(
                        f"[{elapsed:12.4f}] "
                        "STOP"
                    )

                elif msg.type == "active_sensing":

                    print(
                        f"[{elapsed:12.4f}] "
                        "ACTIVE SENSING"
                    )

                elif msg.type == "reset":

                    print(
                        f"[{elapsed:12.4f}] "
                        "RESET"
                    )
                else:

                    print(
                        f"[{elapsed:12.4f}] "
                        "UNKNOWN        ",
                        msg
                    )
                    continue

        except KeyboardInterrupt:
            print()
            print("Retour au menu")
            return

if __name__ == "__main__":

    main()
