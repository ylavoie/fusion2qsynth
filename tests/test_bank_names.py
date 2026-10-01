def test_bank_name_rejects_noncanonical_id(
    project
):

    success, errors = project.set_bank_name(
        "program",
        "01",
        "Test"
    )

    assert success is False
    assert errors


def test_bank_name_rejects_bool(
    project
):

    success, errors = project.set_bank_name(
        "program",
        True,
        "Test"
    )

    assert success is False
    assert errors


def test_bank_name_can_be_set(
    project
):

    success, errors = project.set_bank_name(
        "program",
        "1",
        "Test"
    )

    assert success is True
    assert errors == []

    assert project.get_custom_bank_name(
        "program",
        1
    ) == "Test"


def test_bank_name_can_be_removed(
    project
):

    project.set_bank_name(
        "program",
        1,
        "Test"
    )

    success, errors = project.set_bank_name(
        "program",
        1,
        None
    )

    assert success is True
    assert errors == []

    assert project.get_custom_bank_name(
        "program",
        1
    ) is None