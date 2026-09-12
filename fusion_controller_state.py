import os
import json

from fusion_constants import (
    LAST_PERFORMANCE_FILE
)

class ControllerState:

    def __init__(self):

        self.current_mode = None
        self.current_performance = None
        self.current_parts = {}
        self.current_song_programs = {}
        self.active_notes = set()
        self.pending_reload = False
        self.reload_wait_announced = False

state = ControllerState()

def save_last_performance(
    mode,
    performance_id
):

    data = {}

    if os.path.exists(
        LAST_PERFORMANCE_FILE
    ):

        try:

            with open(
                LAST_PERFORMANCE_FILE
            ) as f:

                data = json.load(
                    f
                )

        except Exception:

            data = {}

    data[
        mode
    ] = performance_id

    with open(
        LAST_PERFORMANCE_FILE,
        "w"
    ) as f:

        json.dump(
            data,
            f,
            indent=2
        )

def load_last_performance(
    mode
):

    if not os.path.exists(
        LAST_PERFORMANCE_FILE
    ):

        return None

    try:

        with open(
            LAST_PERFORMANCE_FILE
        ) as f:

            data = json.load(
                f
            )

    except Exception:

        return None

    return data.get(
        mode
    )

