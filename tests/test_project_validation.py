def test_new_blocking_errors_distinguishes_mix_and_program(
    project
):

    project.data["mixes"]["0:15"] = {
        "category": None,
        "channels": {}
    }

    project.data["programs"]["0:15"] = {
        "name": "Programme valide",
        "category": None,
        "parts": {
            "1": {
                "bank": 0,
                "program": 15
            }
        }
    }

    before_errors = project.get_blocking_errors(
        project.validate()
    )

    assert "0:15 : nom absent." in before_errors

    #
    # Introduire la même erreur dans le PROGRAM.
    #
    del project.data["programs"]["0:15"]["name"]

    new_errors = project.get_new_blocking_errors(
        before_errors
    )

    assert "0:15 : nom absent." in new_errors


def test_save_safe_rejects_new_duplicate_error(
    project,
    monkeypatch
):

    before_errors = [
        "Erreur A"
    ]

    after_errors = [
        "Erreur A",
        "Erreur A"
    ]

    monkeypatch.setattr(
        project,
        "validate",
        lambda: after_errors
    )

    success = project.save_safe(
        allowed_errors=before_errors
    )

    assert success is False
