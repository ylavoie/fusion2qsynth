from fusion_gm_map import (
    fusion_program_bank_name,
    fusion_mix_bank_name,
    fusion_song_bank_name,
)


def test_program_bank_name_known():

    assert (
        fusion_program_bank_name(0)
        == "ROM:PRESET 1"
    )


def test_program_bank_name_unknown():

    assert (
        fusion_program_bank_name(127)
        == "BANK 127"
    )


def test_mix_bank_name_known():

    assert (
        fusion_mix_bank_name(0)
        == "ROM:GROOVE MIX"
    )


def test_mix_bank_name_unknown():

    assert (
        fusion_mix_bank_name(127)
        == "BANK 127"
    )


def test_song_bank_name_none():

    assert (
        fusion_song_bank_name(None)
        == "?"
    )


def test_song_bank_name_without_lsb():

    assert (
        fusion_song_bank_name(0)
        == "ROM:PRESET 1"
    )


def test_song_bank_name_with_lsb():

    assert (
        fusion_song_bank_name(3)
        == "ROM:PRESET 1 (LSB 3)"
    )


def test_song_bank_name_with_msb_and_lsb():

    bank = (
        8 * 128
        + 5
    )

    assert (
        fusion_song_bank_name(bank)
        == "HD:USER (LSB 5)"
    )
