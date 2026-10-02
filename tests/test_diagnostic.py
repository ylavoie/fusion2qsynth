import fusion_diagnostic


class DummyProject:

    def iter_mixes(self):

        return iter([
            (
                "0:1",
                {}
            )
        ])

    def iter_programs(self):

        return iter([
            (
                "1:2",
                {}
            )
        ])

    def iter_songs(self):

        return iter([
            (
                "song-1",
                {}
            )
        ])

    def get_instruments(self):

        return {
            "piano": {}
        }


def test_print_validation_errors_all_categories(
    capsys
):

    project = DummyProject()

    errors = [
        "Banque PROGRAM 1 : erreur",
        "Banques : erreur",
        "MIX erreur directe",
        "PROGRAM erreur directe",
        "SONG erreur directe",
        "Instrument piano erreur",
        "song-1 erreur",
        "1:2 erreur",
        "0:1 erreur",
        "Erreur inconnue",
        {
            "message":
                "Erreur structurée"
        },
    ]

    fusion_diagnostic.print_validation_errors(
        project,
        errors,
        title="Diagnostic test"
    )

    output = capsys.readouterr().out

    assert "Diagnostic test" in output

    assert "BANK" in output
    assert "Banque PROGRAM 1 : erreur" in output
    assert "Banques : erreur" in output

    assert "INSTRUMENT" in output
    assert "Instrument piano erreur" in output

    assert "MIX" in output
    assert "MIX erreur directe" in output
    assert "0:1 erreur" in output

    assert "PROGRAM" in output
    assert "PROGRAM erreur directe" in output
    assert "1:2 erreur" in output

    assert "SONG" in output
    assert "SONG erreur directe" in output
    assert "song-1 erreur" in output

    assert "AUTRES" in output
    assert "Erreur inconnue" in output

    assert "Erreur structurée" in output


def test_print_validation_errors_structured_without_message(
    capsys
):

    project = DummyProject()

    error = {
        "code": "test"
    }

    fusion_diagnostic.print_validation_errors(
        project,
        [
            error
        ]
    )

    output = capsys.readouterr().out

    assert str(error) in output


def test_print_error_messages(
    capsys
):

    errors = [
        "Erreur texte",
        {
            "message":
                "Erreur structurée"
        },
        {
            "code":
                "test"
        },
    ]

    fusion_diagnostic.print_error_messages(
        errors
    )

    output = capsys.readouterr().out

    assert "- Erreur texte" in output
    assert "- Erreur structurée" in output
    assert "- {'code': 'test'}" in output
