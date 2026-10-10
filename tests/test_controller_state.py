import json

import fusion_controller_state


def test_controller_state_initial_values():

    state = fusion_controller_state.ControllerState()

    assert state.current_mode is None
    assert state.current_performance is None
    assert state.current_parts == {}
    assert state.current_song_programs == {}
    assert state.active_notes == set()
    assert state.pending_reload is False
    assert state.reload_wait_announced is False
