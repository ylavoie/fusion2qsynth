#!/usr/bin/env python3

import time
import os
import json
import mido

from fusion_constants import LAST_MIX_FILE, FUSION_DEFAULT_CHANNEL
from fusion_project import FusionProject

from fusion_lib import (
    find_fusion_input,
    find_fluidsynth_output,
    panic,
    note_name,
    log_event
)

fusion_default_channel = FUSION_DEFAULT_CHANNEL - 1

class ControllerState:

    def __init__(self):

        self.current_mix = None
        self.current_parts = {}
        self.active_notes = set()
        self.pending_reload = False

state = ControllerState()

LAST_MIX_FILE = "last_mix.json"

DEBUG = False

def save_last_mix(mix_id):

    with open(
        LAST_MIX_FILE,
        "w"
    ) as f:

        json.dump(
            {
                "mix": mix_id
            },
            f,
            indent=2
        )

def send_program(out, channel, instrument):

    bank = instrument.get(
        "sf2_bank",
        0
    )

    program = instrument.get(
        "sf2_program",
        0
    )

    out.send(
        mido.Message(
            "control_change",
            channel=channel,
            control=0,
            value=min(max(bank,0),127)
        )
    )

    out.send(
        mido.Message(
            "control_change",
            channel=channel,
            control=32,
            value=0
        )
    )

    out.send(
        mido.Message(
            "program_change",
            channel=channel,
            program=min(max(program,0),127)
        )
    )

def load_mix(mix_id, out, project):

    loaded_parts = 0

    mix = project.get_mix(
        mix_id
    )

    if not mix:

        print()
        print(
            "Mix inconnu:",
            mix_id
        )

        return

    errors = project.validate_mix(
        mix_id
    )

    if errors:

        print()
        print(
            "Attention configuration Mix :",
            mix_id
        )

        for err in errors:

            print(
                "-",
                err
            )

        print()

    state.current_mix = mix_id
    state.current_parts = {}
    state.active_notes.clear()
    state.pending_reload = False

    save_last_mix(
        mix_id
    )

    print()
    print("======================")
    print(
        "Performance:",
        mix.get(
            "name",
            mix_id
        )
    )
    print(
        "Fusion Mix:",
        mix_id
    )
    project.print_mix(
        mix_id
    )
    print("======================")

    panic(out)

    state.active_notes.clear()

    time.sleep(0.1)

    for part_id, part in project.get_parts(mix_id).items():

        if not project.is_qsynth_ready(part):

            print(
                "PART",
                part_id,
                "incomplète, ignorée"
            )

            continue

        midi_channel = (
            part["midi_channel"] - 1
        )

        instrument = project.resolve_part_instrument(part)

        send_program(
            out,
            midi_channel,
            instrument
        )

        state.current_parts[
            part["midi_channel"]
        ] = part

        loaded_parts += 1

        log_event(
            f"PART {part_id} CH {part['midi_channel']} "
            f"SF2 {instrument.get('name', 'Non configuré')}"
        )

    print()
    print(
        loaded_parts,
        "PARTS chargées dans FluidSynth"
    )
    print()

    print()

    print(
        "Canaux actifs :"
    )

    for ch, part in state.current_parts.items():

        instrument = project.resolve_part_instrument(
            part
        )

        print(
            " CH",
            ch,
            "→",
            instrument.get(
                "name",
                "Non configuré"
            )
            if instrument
            else "Non configuré"
        )

    print()

def forward_message(out, msg):

    if msg.type in [
        "note_on",
        "note_off",
        "control_change",
        "pitchwheel",
        "aftertouch",
        "polytouch"
    ]:

        out.send(msg)

def reload_current_mix(out, project):

    if state.current_mix:

        load_mix(
            state.current_mix,
            out,
            project
        )

def load_last_mix():

    if not os.path.exists(LAST_MIX_FILE):

        return None

    with open(LAST_MIX_FILE) as f:

        data = json.load(f)

        return data.get(
            "mix"
        )

def main():

    project = FusionProject()

    errors = project.validate()

    if errors:

        print()
        print(
            "===================="
        )
        print(
            "AVERTISSEMENTS CONFIGURATION"
        )
        print(
            "===================="
        )

        for err in errors:

            print(
                "-",
                err
            )

        print()

    last_mix = load_last_mix()

    diagnostic = project.get_diagnostic()
    for mix in diagnostic:

        print()
        print(
            "Mix :",
            mix["mix"],
            "-",
            mix["name"]
        )


        for part in mix["parts"]:

            print(
                " PART",
                part["part"],
                "Fusion:",
                "OK"
                if part["fusion_valid"]
                else "ERREUR",
                "QSynth:",
                "OK"
                if part["qsynth_configured"]
                else "Non configuré"
            )


        if "shared_channels" in mix:

            print(
                " ⚠ Canaux partagés :",
                mix["shared_channels"]
            )

    print()
    print(
        project.count_mixes(),
        "Mix chargés"
    )
    print()

    fusion_port = find_fusion_input()

    if not fusion_port:

        raise Exception(
            "Fusion MIDI introuvable"
        )

    synth_port = find_fluidsynth_output()

    if not synth_port:

        raise Exception(
            "FluidSynth MIDI introuvable"
        )

    print(
        "Fusion :",
        fusion_port
    )

    print(
        "Synth :",
        synth_port
    )

    bank = 0

    try:
        with mido.open_input(
            fusion_port
        ) as inp:

            with mido.open_output(
                synth_port
            ) as out:

                if last_mix:

                    load_mix(
                        last_mix,
                        out,
                        project
                    )

                print()
                print(
                    "Attente des changements de Mix..."
                )

                while True:

                    if project.reload_if_changed():

                        if not state.pending_reload:

                            state.pending_reload = True
                            state.reload_wait_announced = False

                    #
                    # Reload immédiat si repos
                    #
                    if (
                        state.pending_reload
                        and
                        not state.active_notes
                    ):

                        print()
                        print(
                            "Projet modifié : reload immédiat."
                        )

                        reload_current_mix(
                            out,
                            project
                        )

                        state.pending_reload = False
                        state.reload_wait_announced = False

                    #
                    # MIDI
                    #
                    for msg in inp.iter_pending():

                        if msg.type == "note_on":

                            key = (
                                msg.channel,
                                msg.note
                            )

                            if msg.velocity > 0:

                                state.active_notes.add(
                                    key
                                )

                            else:

                                state.active_notes.discard(
                                    key
                                )

                        elif msg.type == "note_off":

                            state.active_notes.discard(
                                (
                                    msg.channel,
                                    msg.note
                                )
                            )

                            if (
                                state.pending_reload
                                and
                                not state.active_notes
                            ):

                                if state.reload_wait_announced:

                                    print()
                                    print(
                                        "Notes relâchées : reload différé."
                                    )

                                else:

                                    print()
                                    print(
                                        "Projet modifié : reload immédiat."
                                    )

                                reload_current_mix(
                                    out,
                                    project
                                )

                                state.pending_reload = False
                                state.reload_wait_announced = False

                        if (
                            state.pending_reload
                            and
                            state.active_notes
                            and
                            not state.reload_wait_announced
                        ):

                            print(
                                "Projet modifié : reload en attente "
                                "(notes actives)."
                            )

                            state.reload_wait_announced = True

                        if DEBUG:

                            part = state.current_parts.get(
                                msg.channel + 1
                            )
                            name = "?"

                            if part:

                                instrument = project.resolve_part_instrument(
                                    part
                                )

                                if instrument:

                                    name = instrument.get(
                                        "name",
                                        "?"
                                    )

                            if msg.type == "note_on" and msg.velocity > 0:

                                print(
                                    "NOTE ON",
                                    "CH",
                                    msg.channel + 1, name,
                                    "Note",
                                    note_name(msg.note),
                                    "Vel",
                                    msg.velocity
                                )

                            elif (
                                msg.type == "note_off"
                                or
                                (
                                    msg.type == "note_on"
                                    and
                                    msg.velocity == 0
                                )
                            ):
                                print(
                                    "NOTE OFF",
                                    "CH",
                                    msg.channel + 1, name,
                                    "Note",
                                    note_name(msg.note)
                                )

                        if msg.type in [
                            "note_on",
                            "note_off"
                        ]:

                            if not DEBUG:

                                print(
                                    "NOTE",
                                    msg.channel + 1,
                                    msg.type,
                                    note_name(msg.note),
                                    msg.velocity
                                )

                            out.send(msg)

                            continue

                        if msg.type in [
                            "pitchwheel",
                            "aftertouch",
                            "polytouch"
                        ]:

                            forward_message(out, msg)

                            continue

                        if msg.type == "control_change":

                            if (
                                msg.channel == fusion_default_channel
                                and
                                msg.control == 0
                            ):

                                bank = msg.value

                        elif msg.type == "program_change":

                            if msg.channel != fusion_default_channel:

                                continue

                            mix_id = (
                                f"{bank}:{msg.program}"
                            )

                            log_event(
                                f"MIX détecté {mix_id}"
                            )

                            print()
                            print(
                                "===================="
                            )

                            print(
                                "Mix Fusion détecté"
                            )

                            print(
                                "Bank:",
                                bank
                            )

                            print(
                                "Program:",
                                msg.program
                            )

                            print(
                                "ID:",
                                mix_id
                            )

                            print(
                                "===================="
                            )

                            if mix_id == state.current_mix:

                                continue

                            load_mix(
                                mix_id,
                                out,
                                project
                            )
                            log_event(
                                f"MIX chargé {mix_id}"
                            )

                time_sleep(
                    0.01
                )

    except KeyboardInterrupt:
        print()
        print("Retour au menu")
        return

if __name__ == "__main__":

    main()
