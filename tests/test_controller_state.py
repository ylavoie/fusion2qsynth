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


def test_save_last_performance_creates_file(
    tmp_path,
    monkeypatch
):

    filename = (
        tmp_path
        / "last_performance.json"
    )

    monkeypatch.setattr(
        fusion_controller_state,
        "LAST_PERFORMANCE_FILE",
        filename
    )

    fusion_controller_state.save_last_performance(
        "program",
        "0:15"
    )

    with open(filename) as f:

        data = json.load(f)

    assert data == {
        "program": "0:15"
    }


def test_save_last_performance_preserves_other_modes(
    tmp_path,
    monkeypatch
):

    filename = (
        tmp_path
        / "last_performance.json"
    )

    filename.write_text(
        json.dumps({
            "program": "0:15"
        })
    )

    monkeypatch.setattr(
        fusion_controller_state,
        "LAST_PERFORMANCE_FILE",
        filename
    )

    fusion_controller_state.save_last_performance(
        "mix",
        "2:4"
    )

    with open(filename) as f:

        data = json.load(f)

    assert data == {
        "program": "0:15",
        "mix": "2:4"
    }


def test_save_last_performance_replaces_invalid_file(
    tmp_path,
    monkeypatch
):

    filename = (
        tmp_path
        / "last_performance.json"
    )

    filename.write_text(
        "invalid json"
    )

    monkeypatch.setattr(
        fusion_controller_state,
        "LAST_PERFORMANCE_FILE",
        filename
    )

    fusion_controller_state.save_last_performance(
        "program",
        "0:16"
    )

    with open(filename) as f:

        data = json.load(f)

    assert data == {
        "program": "0:16"
    }


def test_load_last_performance_missing_file(
    tmp_path,
    monkeypatch
):

    filename = (
        tmp_path
        / "last_performance.json"
    )

    monkeypatch.setattr(
        fusion_controller_state,
        "LAST_PERFORMANCE_FILE",
        filename
    )

    result = (
        fusion_controller_state.load_last_performance(
            "program"
        )
    )

    assert result is None


def test_load_last_performance(
    tmp_path,
    monkeypatch
):

    filename = (
        tmp_path
        / "last_performance.json"
    )

    filename.write_text(
        json.dumps({
            "program": "0:17",
            "mix": "2:4"
        })
    )

    monkeypatch.setattr(
        fusion_controller_state,
        "LAST_PERFORMANCE_FILE",
        filename
    )

    assert (
        fusion_controller_state.load_last_performance(
            "program"
        )
        == "0:17"
    )

    assert (
        fusion_controller_state.load_last_performance(
            "mix"
        )
        == "2:4"
    )


def test_load_last_performance_invalid_file(
    tmp_path,
    monkeypatch
):

    filename = (
        tmp_path
        / "last_performance.json"
    )

    filename.write_text(
        "invalid json"
    )

    monkeypatch.setattr(
        fusion_controller_state,
        "LAST_PERFORMANCE_FILE",
        filename
    )

    result = (
        fusion_controller_state.load_last_performance(
            "program"
        )
    )

    assert result is None
