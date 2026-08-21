import time

from fusion_constants import (
    DEBUG
)

from fusion_constants import (
    FUSION_DEFAULT_CHANNEL
)

from fusion_controller_state import (
    state
)

from fusion_lib import (
    note_name,
    log_event
)

from fusion_performance import (
    reload_current_performance,
    load_mix,
    load_program,
    load_song
)

fusion_default_channel = FUSION_DEFAULT_CHANNEL - 1

def execute_pending_reload(
    out,
    project,
    deferred=False
):

    print()

    if deferred:

        print(
            "Notes relâchées : reload différé."
        )

    else:

        print(
            "Projet modifié : reload immédiat."
        )

    reload_current_performance(
        out,
        project
    )

    state.pending_reload = False
    state.reload_wait_announced = False

def run_controller_loop(
    inp,
    out,
    project,
    selected_mode,
    selected_song=None
):
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

            execute_pending_reload(
                out,
                project
            )

        #
        # MIDI
        #
        for msg in inp.iter_pending():

            if (
                selected_mode == "song"
                and
                msg.type == "song_select"
            ):

                if DEBUG:

                    print(
                        "SONG SELECT reçu :",
                        msg.song
                    )

                continue

            if msg.type in [
                "note_on",
                "note_off"
            ]:

                if msg.channel + 1 not in state.current_parts:

                    if DEBUG:

                        print(
                            "NOTE ignorée",
                            "CH",
                            msg.channel + 1,
                            note_name(msg.note)
                        )

                    continue

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
                        execute_pending_reload(
                            out,
                            project,
                            deferred=state.reload_wait_announced
                        )

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

                if (
                    msg.channel + 1
                    not in state.current_parts
                ):

                    continue

                out.send(
                    msg
                )

                continue

            if msg.type == "control_change":

                if selected_mode in (
                    "program",
                    "mix"
                ):
                    #
                    # Détection banque du MIX Fusion
                    #
                    if (
                        msg.channel == fusion_default_channel
                        and
                        msg.control == 0
                    ):

                        bank = msg.value

                        continue

                    #
                    # Bank Select des PARTs :
                    # ne pas écraser le mapping SoundFont
                    #
                    if msg.control in (
                        0,
                        32
                    ):

                        continue

                    #
                    # PART non active
                    #
                    if (
                        msg.channel + 1
                        not in state.current_parts
                    ):

                        if DEBUG:

                            print(
                                "CC ignoré",
                                "CH",
                                msg.channel + 1,
                                "CC",
                                msg.control,
                                "Value",
                                msg.value
                            )

                        continue

                #
                # Autres contrôleurs MIDI
                #
                out.send(
                    msg
                )

                continue

            elif msg.type == "program_change":

                if selected_mode == "song":

                    continue

                if msg.channel != fusion_default_channel:

                    continue

                performance_id = (
                    f"{bank}:{msg.program}"
                )

                log_event(
                    f"PERFORMANCE détectée {performance_id}"
                )

                print()
                print(
                    "===================="
                )

                print(
                    "Performance Fusion détecté"
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
                    performance_id
                )

                print(
                    "===================="
                )

                if (
                    state.current_mode == selected_mode
                    and
                    performance_id == state.current_performance
                ):

                    continue

                if state.current_mode == "program":

                    load_program(
                        performance_id,
                        out,
                        project
                    )

                elif state.current_mode == "mix":

                    load_mix(
                        performance_id,
                        out,
                        project
                    )

                log_event(
                    f"PERFORMANCE chargée {performance_id}"
                )

            if (
                selected_mode == "song"
                and
                msg.type == "start"
            ):

                load_song(
                    selected_song,
                    out,
                    project
                )

                continue

        time.sleep(
            0.01
    )

