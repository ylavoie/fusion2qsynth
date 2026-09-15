import time
import mido

from fusion_constants import DEBUG

from fusion_controller_state import (
    state,
    save_last_performance
)

from fusion_lib import (
    panic,
    log_event
)

from fusion_diagnostic import (
    print_validation_errors
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

    bank_msb = bank // 128
    bank_lsb = bank % 128

    out.send(
        mido.Message(
            "control_change",
            channel=channel,
            control=0,
            value=bank_msb
        )
    )

    out.send(
        mido.Message(
            "control_change",
            channel=channel,
            control=32,
            value=bank_lsb
        )
    )

    out.send(
        mido.Message(
            "program_change",
            channel=channel,
            program=min(
                max(
                    program,
                    0
                ),
                127
            )
        )
    )

def print_performance_header(
    mode,
    performance_id,
    name
):

    labels = {
        "program": "PROGRAM",
        "mix": "MIX",
        "song": "SONG"
    }

    label = labels.get(
        mode,
        mode.upper()
    )

    print()
    print("======================")
    print(
        f"{label}:",
        name
    )
    print(
        "Fusion",
        f"{label}:",
        performance_id
    )
    print("======================")

def load_mix(
    mix_id,
    out,
    project
):

    loaded_channels = 0

    mix = project.get_mix(
        mix_id
    )

    if not mix:

        print()

        print(
            "MIX inconnu:",
            mix_id
        )

        return

    errors = project.validate_mix(
        mix_id
    )

    if errors:

        print_validation_errors(
            project,
            errors,
            title="Attention configuration"
        )

        print()

    channels = mix.get(
        "channels",
        {}
    )

    ready_channels = []

    for channel_id, channel in channels.items():

        instrument = (
            project.resolve_mix_channel_instrument(
                channel
            )
        )

        if instrument:

            ready_channels.append(
                (
                    channel_id,
                    channel,
                    instrument
                )
            )

    state.current_mode = "mix"

    state.current_performance = (
        mix_id
    )

    state.current_parts = {}

    state.pending_reload = False

    print_performance_header(
        "mix",
        mix_id,
        mix.get(
            "name",
            mix_id
        )
    )

    project.print_mix(
        mix_id
    )

    print(
        "======================"
    )

    panic(
        out
    )

    state.active_notes.clear()

    time.sleep(
        0.1
    )

    if not ready_channels:

        print()

        print(
            "MIX",
            mix_id,
            "sans canal configuré pour FluidSynth."
        )

        print()

        print(
            "Canaux actifs : aucun"
        )

        print()

        save_last_performance(
            "mix",
            mix_id
        )
        return

    for (
        channel_id,
        channel,
        instrument
    ) in ready_channels:

        midi_channel = (
            int(channel_id) - 1
        )

        send_program(
            out,
            midi_channel,
            instrument
        )

        state.current_parts[
            int(channel_id)
        ] = channel

        loaded_channels += 1

        log_event(
            f"CH {channel_id} "
            f"SF2 "
            f"{instrument.get('name', 'Non configuré')}"
        )

    print()

    print(
        loaded_channels,
        "canaux chargés dans FluidSynth"
    )

    print()

    print(
        "Canaux actifs :"
    )

    if loaded_channels > 0:

        save_last_performance(
            "mix",
            mix_id
        )

    for channel_id, channel in sorted(
        state.current_parts.items()
    ):

        instrument = (
            project.resolve_mix_channel_instrument(
                channel
            )
        )

        print(
            " CH",
            channel_id,
            "→",
            instrument.get(
                "name",
                "Non configuré"
            )
            if instrument
            else "Non configuré"
        )

    print()

def load_program(
    program_id,
    out,
    project
):

    program = project.get_program(
        program_id
    )

    if not program:

        print()
        print(
            "PROGRAM inconnu:",
            program_id
        )

        return

    parts = program.get(
        "parts",
        {}
    )

    if not parts:

        print()
        print(
            "PROGRAM sans PART:",
            program_id
        )

        return

    part_id, part = next(
        iter(
            parts.items()
        )
    )

    if not project.is_qsynth_ready(
        part
    ):

        print()
        print(
            "PROGRAM",
            program_id,
            "non configuré pour FluidSynth."
        )

        return

    instrument = project.resolve_part_instrument(
        part
    )

    if not instrument:

        print()
        print(
            "Instrument non configuré."
        )

        return

    state.current_mode = "program"
    state.current_performance = program_id
    state.current_parts = {}
    state.pending_reload = False

    print_performance_header(
        "program",
        program_id,
        program.get(
            "name",
            program_id
        )
    )

    panic(out)

    state.active_notes.clear()

    time.sleep(0.1)

    midi_channel = (
        part["midi_channel"] - 1
    )

    send_program(
        out,
        midi_channel,
        instrument
    )

    state.current_parts[
        part["midi_channel"]
    ] = part

    save_last_performance(
        "program",
        program_id
    )

    print()
    print(
        "Canal actif :"
    )

    print(
        " CH",
        part["midi_channel"],
        "→",
        instrument.get(
            "name",
            "Non configuré"
        )
    )

    print()

def load_song(
    song_id,
    out,
    project
):

    song = project.get_song(
        song_id
    )

    if not song:

        print()
        print(
            "SONG inconnue:",
            song_id
        )

        return

    channels = song.get(
        "channels",
        {}
    )

    if not channels:

        print()
        print(
            "SONG sans canaux:",
            song_id
        )

        return

    state.current_mode = "song"
    state.current_performance = song_id
    state.current_parts = {}
    state.current_song_programs = {}
    state.pending_reload = False

    print_performance_header(
        "song",
        song_id,
        song.get(
            "name",
            song_id
        )
    )

    panic(
        out
    )

    state.active_notes.clear()

    time.sleep(
        0.1
    )

    prepared_channels = 0

    controls = {
        7: "volume",
        10: "pan",
        11: "expression",
        91: "reverb",
        93: "chorus"
    }

    for channel_id, channel in sorted(
        channels.items(),
        key=lambda item: int(
            item[0]
        )
    ):

        midi_channel = (
            int(channel_id) - 1
        )

        #
        # Paramètres statiques SONG
        #
        for cc, field in controls.items():

            if field not in channel:

                continue

            out.send(
                mido.Message(
                    "control_change",
                    channel=midi_channel,
                    control=cc,
                    value=channel[field]
                )
            )

        prepared_channels += 1


    print()
    print(
        prepared_channels,
        "canaux SONG préparés"
    )

    save_last_performance(
        "song",
        song_id
    )

    print()
    print(
        "En attente des PROGRAM_CHANGE du Fusion..."
    )

    print()

def load_song_program(
    channel_id,
    program_id,
    out,
    project
):

    song_id = state.current_performance

    song = project.get_song(
        song_id
    )

    if not song:

        return False

    channel = song.get(
        "channels",
        {}
    ).get(
        str(channel_id)
    )

    if channel is None:

        return False

    programs = channel.get(
        "programs"
    )

    program_data = programs.get(
        program_id
    )

    if program_data is None:

        if DEBUG:

            print(
                "PROGRAM SONG ignoré",
                "CH",
                channel_id,
                program_id
            )

        state.current_parts.pop(
            channel_id,
            None
        )

        state.current_song_programs.pop(
            channel_id,
            None
        )

        return False

    instrument = (
        project.resolve_song_program_instrument(
            program_id,
            program_data
        )
    )

    if not instrument:

        print(
            "CH",
            channel_id,
            "PROGRAM",
            program_id,
            "non configuré"
        )

        state.current_parts.pop(
            channel_id,
            None
        )

        state.current_song_programs.pop(
            channel_id,
            None
        )

        return False

    send_program(
        out,
        channel_id - 1,
        instrument
    )

    state.current_parts[
        channel_id
    ] = channel

    state.current_song_programs[
        channel_id
    ] = {
        "program_id": program_id,
        "instrument": instrument
    }

    print(
        "CH",
        channel_id,
        "PROGRAM",
        program_id,
        "→",
        instrument.get(
            "name",
            "?"
        )
    )

    return True

def reload_current_performance(
    out,
    project
):

    if state.current_mode == "program":

        load_program(
            state.current_performance,
            out,
            project
        )

    elif state.current_mode == "mix":

        load_mix(
            state.current_performance,
            out,
            project
        )

    elif state.current_mode == "song":

        load_song(
            state.current_performance,
            out,
            project
        )
