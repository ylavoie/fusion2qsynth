import fusion_suggestions


def test_normalize_name():

    assert (
        fusion_suggestions.normalize_name(
            "Stereo12-Strings"
        )
        == "stereo12 strings"
    )

    assert (
        fusion_suggestions.normalize_name(
            "HolyGrail Grand_Piano"
        )
        == "holy grail grand piano"
    )


def test_normalize_preset_name():

    assert (
        fusion_suggestions.normalize_preset_name(
            "Grand Piano Expr"
        )
        == "grand piano"
    )

    assert (
        fusion_suggestions.normalize_preset_name(
            "Grand Piano"
        )
        == "grand piano"
    )


def test_contains_term():

    assert (
        fusion_suggestions.contains_term(
            "acoustic bass guitar",
            "bass"
        )
        is True
    )

    assert (
        fusion_suggestions.contains_term(
            "contrabass",
            "bass"
        )
        is False
    )


def test_detect_gm_program_known():

    result = (
        fusion_suggestions.detect_gm_program(
            "Acoustic Grand Piano"
        )
    )

    assert result is not None


def test_detect_gm_program_unknown():

    assert (
        fusion_suggestions.detect_gm_program(
            "Definitely Unknown Instrument"
        )
        is None
    )


def test_detect_gm_hint_known():

    result = (
        fusion_suggestions.detect_gm_hint(
            "Holy Grail Grand Piano"
        )
    )

    assert result is not None
    assert result["family"] == "piano"


def test_detect_gm_hint_unknown():

    assert (
        fusion_suggestions.detect_gm_hint(
            "Definitely Unknown Instrument"
        )
        is None
    )


def test_detect_gm_drum_kit_known():

    result = (
        fusion_suggestions.detect_gm_drum_kit(
            "Club Kit"
        )
    )

    assert result is not None
    assert result["sf2_bank"] == 128


def test_detect_gm_drum_kit_unknown():

    assert (
        fusion_suggestions.detect_gm_drum_kit(
            "Definitely Unknown Instrument"
        )
        is None
    )


def test_detect_gm_drum_kit_non_drum():

    assert (
        fusion_suggestions.detect_gm_drum_kit(
            "Holy Grail Grand Piano"
        )
        is None
    )


def test_detect_families():

    assert (
        "piano"
        in fusion_suggestions.detect_families(
            "Grand Piano"
        )
    )


def test_detect_families_bass_drum_semantics():

    families = (
        fusion_suggestions.detect_families(
            "Bass Drum"
        )
    )

    assert "drums" in families
    assert "bass" not in families


def test_detect_families_drum_and_bass_semantics():

    families = (
        fusion_suggestions.detect_families(
            "Drum and Bass"
        )
    )

    assert "bass" in families
    assert "drums" not in families


def test_detect_families_specializations():

    assert (
        "bass"
        not in fusion_suggestions.detect_families(
            "Contrabass"
        )
    )

    assert (
        "piano"
        not in fusion_suggestions.detect_families(
            "Electric Piano"
        )
    )

    assert (
        "flute"
        not in fusion_suggestions.detect_families(
            "Pan Flute"
        )
    )


def test_detect_families_square_lead():

    families = (
        fusion_suggestions.detect_families(
            "Square Wave"
        )
    )

    assert "square_wave" not in families
    assert "square_lead" in families


def test_similarity():

    assert (
        fusion_suggestions.similarity(
            "Grand Piano",
            "Grand Piano"
        )
        == 1.0
    )

    assert (
        fusion_suggestions.similarity(
            "Grand Piano",
            "Trumpet"
        )
        < 1.0
    )


def test_matches_for_family_filters_other_families():

    fusion_program = {
        "name": "Grand Piano",
        "program": 0,
    }

    presets = [
        {
            "name": "Grand Piano",
            "bank": 0,
            "program": 0,
        },
        {
            "name": "Trumpet",
            "bank": 0,
            "program": 56,
        },
    ]

    matches = (
        fusion_suggestions.matches_for_family(
            fusion_program,
            presets,
            "piano",
            None,
        )
    )

    assert len(matches) == 1

    score, preset = matches[0]

    assert preset["name"] == "Grand Piano"
    assert score > 0


def test_matches_for_family_respects_limit():

    fusion_program = {
        "name": "Piano",
        "program": 0,
    }

    presets = [
        {
            "name": "Grand Piano",
            "bank": 0,
            "program": 0,
        },
        {
            "name": "Bright Piano",
            "bank": 0,
            "program": 1,
        },
        {
            "name": "Electric Piano",
            "bank": 0,
            "program": 4,
        },
    ]

    matches = (
        fusion_suggestions.matches_for_family(
            fusion_program,
            presets,
            "piano",
            None,
            limit=2,
        )
    )

    assert len(matches) == 2


def test_matches_for_family_gm_match_has_priority():

    fusion_program = {
        "name": "Custom Piano",
        "program": 99,
    }

    gm_hint = {
        "family": "piano",
        "gm_program": 0,
    }

    presets = [
        {
            "name": "Custom Piano",
            "bank": 0,
            "program": 1,
        },
        {
            "name": "Acoustic Grand Piano",
            "bank": 0,
            "program": 0,
        },
    ]

    matches = (
        fusion_suggestions.matches_for_family(
            fusion_program,
            presets,
            "piano",
            gm_hint,
        )
    )

    assert (
        matches[0][1]["program"]
        == 0
    )


def test_matches_for_family_gm_match_requires_bank_zero():

    fusion_program = {
        "name": "Custom Instrument",
        "program": 99,
    }

    gm_hint = {
        "family": "piano",
        "gm_program": 0,
    }

    presets = [
        {
            "name": "Unknown Preset",
            "bank": 1,
            "program": 0,
        },
    ]

    matches = (
        fusion_suggestions.matches_for_family(
            fusion_program,
            presets,
            "piano",
            gm_hint,
        )
    )

    assert matches == []


def test_matches_for_family_same_program_bonus():

    fusion_program = {
        "name": "Piano",
        "program": 0,
    }

    presets = [
        {
            "name": "Piano",
            "bank": 0,
            "program": 0,
        },
        {
            "name": "Piano",
            "bank": 0,
            "program": 1,
        },
    ]

    matches = (
        fusion_suggestions.matches_for_family(
            fusion_program,
            presets,
            "piano",
            None,
        )
    )

    assert (
        matches[0][1]["program"]
        == 0
    )

    assert (
        matches[0][0]
        >
        matches[1][0]
    )


def test_matches_for_family_expr_penalty():

    fusion_program = {
        "name": "Grand Piano",
        "program": 99,
    }

    presets = [
        {
            "name": "Grand Piano",
            "bank": 0,
            "program": 1,
        },
        {
            "name": "Grand Piano Expr",
            "bank": 0,
            "program": 2,
        },
    ]

    matches = (
        fusion_suggestions.matches_for_family(
            fusion_program,
            presets,
            "piano",
            None,
        )
    )

    assert (
        matches[0][1]["name"]
        == "Grand Piano"
    )

    assert (
        matches[0][0]
        >
        matches[1][0]
    )


def test_suggest_instruments_drum_kit():

    fusion_program = {
        "name": "Club Kit",
        "program": 0,
    }

    drum_kit = (
        fusion_suggestions.detect_gm_drum_kit(
            "Club Kit"
        )
    )

    assert drum_kit is not None

    presets = [
        {
            "name": "Matching Drum Kit",
            "bank": drum_kit["sf2_bank"],
            "program": drum_kit["sf2_program"],
        },
        {
            "name": "Other Drum Kit",
            "bank": 128,
            "program": 99,
        },
    ]

    suggestions = (
        fusion_suggestions.suggest_instruments(
            fusion_program,
            presets,
        )
    )

    assert list(
        suggestions
    ) == [
        "drums"
    ]

    assert len(
        suggestions["drums"]
    ) == 1

    score, preset = (
        suggestions["drums"][0]
    )

    assert score == 1.0
    assert (
        preset["name"]
        == "Matching Drum Kit"
    )


def test_suggest_instruments_drum_kit_respects_limit():

    fusion_program = {
        "name": "Club Kit",
        "program": 0,
    }

    drum_kit = (
        fusion_suggestions.detect_gm_drum_kit(
            "Club Kit"
        )
    )

    presets = [
        {
            "name": "Kit A",
            "bank": drum_kit["sf2_bank"],
            "program": drum_kit["sf2_program"],
        },
        {
            "name": "Kit B",
            "bank": drum_kit["sf2_bank"],
            "program": drum_kit["sf2_program"],
        },
    ]

    suggestions = (
        fusion_suggestions.suggest_instruments(
            fusion_program,
            presets,
            limit=1,
        )
    )

    assert len(
        suggestions["drums"]
    ) == 1


def test_suggest_instruments_drum_kit_falls_back():

    fusion_program = {
        "name": "Club Kit",
        "program": 0,
    }

    presets = []

    suggestions = (
        fusion_suggestions.suggest_instruments(
            fusion_program,
            presets,
        )
    )

    assert isinstance(
        suggestions,
        dict
    )


def test_suggest_instruments_by_family(
    monkeypatch
):

    fusion_program = {
        "name": "Custom Instrument",
        "program": 10,
    }

    presets = [
        {
            "name": "Preset",
            "bank": 0,
            "program": 10,
        },
    ]

    monkeypatch.setattr(
        fusion_suggestions,
        "detect_families",
        lambda name: {
            "piano"
        }
    )

    monkeypatch.setattr(
        fusion_suggestions,
        "detect_gm_hint",
        lambda name: None
    )

    calls = []

    def fake_matches(
        fusion_program,
        sf2_presets,
        family,
        gm_hint,
        limit=3
    ):

        calls.append(
            (
                family,
                gm_hint,
                limit,
            )
        )

        return [
            (
                0.5,
                presets[0],
            )
        ]

    monkeypatch.setattr(
        fusion_suggestions,
        "matches_for_family",
        fake_matches
    )

    suggestions = (
        fusion_suggestions.suggest_instruments(
            fusion_program,
            presets,
            limit=2,
        )
    )

    assert suggestions == {
        "piano": [
            (
                0.5,
                presets[0],
            )
        ]
    }

    assert calls == [
        (
            "piano",
            None,
            2,
        )
    ]


def test_suggest_instruments_adds_gm_family(
    monkeypatch
):

    fusion_program = {
        "name": "Custom Instrument",
        "program": 10,
    }

    monkeypatch.setattr(
        fusion_suggestions,
        "detect_gm_drum_kit",
        lambda name: None
    )

    monkeypatch.setattr(
        fusion_suggestions,
        "detect_families",
        lambda name: set()
    )

    monkeypatch.setattr(
        fusion_suggestions,
        "detect_gm_hint",
        lambda name: {
            "family": "piano",
            "gm_program": 0,
        }
    )

    monkeypatch.setattr(
        fusion_suggestions,
        "matches_for_family",
        lambda *args, **kwargs: []
    )

    suggestions = (
        fusion_suggestions.suggest_instruments(
            fusion_program,
            [],
        )
    )

    assert "piano" in suggestions


def test_detect_gm_drum_kit_invalid_program(
    monkeypatch
):

    monkeypatch.setattr(
        fusion_suggestions,
        "detect_gm_hint",
        lambda name: {
            "family": "drums",
            "gm_program": 999,
        }
    )

    assert (
        fusion_suggestions.detect_gm_drum_kit(
            "Custom Kit"
        )
        is None
    )


def test_detect_gm_hint_direct_gm_program(
    monkeypatch
):

    fusion_suggestions._detect_gm_hint_cached.cache_clear()

    monkeypatch.setattr(
        fusion_suggestions,
        "detect_gm_program",
        lambda name: {
            "family": "piano",
            "gm_program": 0,
        }
    )

    result = (
        fusion_suggestions.detect_gm_hint(
            "Direct GM Program"
        )
    )

    assert result == {
        "family": "piano",
        "gm_program": 0,
    }

    fusion_suggestions._detect_gm_hint_cached.cache_clear()


def test_detect_families_override(
    monkeypatch
):

    fusion_suggestions._detect_families_cached.cache_clear()

    monkeypatch.setattr(
        fusion_suggestions,
        "FUSION_FAMILY_OVERRIDES",
        {
            "custom instrument": {
                "piano",
                "strings",
            }
        }
    )

    result = (
        fusion_suggestions.detect_families(
            "Custom Instrument"
        )
    )

    assert result == {
        "piano",
        "strings",
    }

    fusion_suggestions._detect_families_cached.cache_clear()
