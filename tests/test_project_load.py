import json
import os

import pytest

from fusion_constants import (
    PROJECT_FORMAT_VERSION
)

from fusion_project import (
    FusionProject,
    ProjectRecoveryError
)


def write_json(
    filename,
    data
):

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f
        )

def test_empty_project_data(
    project
):

    data = project._empty_project_data()

    assert data == {
        "format_version":
            PROJECT_FORMAT_VERSION,

        "banks": {
            "program": {},
            "mix": {}
        },

        "instruments": {},
        "mixes": {},
        "programs": {},
        "songs": {}
    }


def test_validate_format_version_valid(
    project
):

    project.data[
        "format_version"
    ] = PROJECT_FORMAT_VERSION

    project._validate_format_version()


def test_validate_format_version_invalid_root(
    project
):

    project.data = "abc"

    with pytest.raises(
        RuntimeError,
        match=(
            r"Structure racine de "
            r"fusion\.json invalide\."
        )
    ):

        project._validate_format_version()


def test_validate_format_version_missing(
    project
):

    project.data.pop(
        "format_version"
    )

    with pytest.raises(
        RuntimeError,
        match=(
            r"format_version absent "
            r"dans fusion\.json\."
        )
    ):

        project._validate_format_version()

def test_validate_format_version_too_new(
    project
):

    project.data[
        "format_version"
    ] = (
        PROJECT_FORMAT_VERSION + 1
    )

    with pytest.raises(
        RuntimeError,
        match="plus récent"
    ):

        project._validate_format_version()


def test_validate_format_version_too_old(
    project
):

    project.data[
        "format_version"
    ] = (
        PROJECT_FORMAT_VERSION - 1
    )

    with pytest.raises(
        RuntimeError,
        match="plus ancien"
    ):

        project._validate_format_version()


def test_validate_format_version_invalid_type(
    project
):

    project.data[
        "format_version"
    ] = str(
        PROJECT_FORMAT_VERSION
    )

    with pytest.raises(
        RuntimeError,
        match=(
            r"format_version invalide "
            r"dans fusion\.json\."
        )
    ):

        project._validate_format_version()


def test_validate_root_structure_valid(
    project
):

    project._validate_root_structure()


@pytest.mark.parametrize(
    "section",
    [
        "banks",
        "instruments",
        "mixes",
        "programs",
        "songs"
    ]
)
def test_validate_root_structure_missing_section(
    project,
    section
):

    project.data.pop(
        section
    )

    with pytest.raises(
        RuntimeError,
        match=(
            rf"Section {section} absente "
            rf"dans fusion\.json\."
        )
    ):

        project._validate_root_structure()


@pytest.mark.parametrize(
    "section",
    [
        "banks",
        "instruments",
        "mixes",
        "programs",
        "songs"
    ]
)
def test_validate_root_structure_invalid_section(
    project,
    section
):

    project.data[
        section
    ] = []

    with pytest.raises(
        RuntimeError,
        match=(
            rf"Section {section} invalide "
            rf"dans fusion\.json\."
        )
    ):

        project._validate_root_structure()


def test_validate_root_structure_unknown_section(
    project
):

    project.data[
        "unexpected"
    ] = {}

    with pytest.raises(
        RuntimeError,
        match=(
            r"Section unexpected inconnue "
            r"dans fusion\.json\."
        )
    ):

        project._validate_root_structure()


def test_load_missing_file_creates_empty_project(
    tmp_path
):

    filename = (
        tmp_path
        / "fusion.json"
    )

    project = FusionProject(
        filename=str(filename)
    )

    assert project.data == (
        project._empty_project_data()
    )

    assert project.file_time == 0

    assert not filename.exists()


def test_load_valid_project(
    tmp_path
):

    filename = (
        tmp_path
        / "fusion.json"
    )

    data = FusionProject.__new__(
        FusionProject
    )

    data.filename = str(filename)
    data.data = {}
    data.file_time = 0

    expected = (
        data._empty_project_data()
    )

    write_json(
        filename,
        expected
    )

    project = FusionProject(
        filename=str(filename)
    )

    assert project.data == expected

    assert project.file_time == (
        os.path.getmtime(
            filename
        )
    )


def test_load_invalid_json_without_backup(
    tmp_path
):

    filename = (
        tmp_path
        / "fusion.json"
    )

    filename.write_text(
        '{ "format_version": ',
        encoding="utf-8"
    )

    with pytest.raises(
        RuntimeError,
        match=r"Fichier .*fusion\.json invalide\."
    ):

        FusionProject(
            filename=str(filename)
        )


def test_load_invalid_json_with_backup(
    tmp_path
):

    filename = (
        tmp_path
        / "fusion.json"
    )

    backup = (
        tmp_path
        / "fusion.json.bak"
    )

    filename.write_text(
        '{ "format_version": ',
        encoding="utf-8"
    )

    backup.write_text(
        "{}",
        encoding="utf-8"
    )

    with pytest.raises(
        ProjectRecoveryError,
        match=r"Une sauvegarde .*fusion\.json\.bak est disponible"
    ):

        FusionProject(
            filename=str(filename)
        )


def test_load_rejects_invalid_format_version(
    tmp_path
):

    filename = (
        tmp_path
        / "fusion.json"
    )

    project = FusionProject.__new__(
        FusionProject
    )

    project.filename = str(filename)
    project.data = {}
    project.file_time = 0

    data = project._empty_project_data()

    data[
        "format_version"
    ] += 1

    write_json(
        filename,
        data
    )

    with pytest.raises(
        RuntimeError,
        match="plus récent"
    ):

        FusionProject(
            filename=str(filename)
        )


def test_load_rejects_invalid_root_structure(
    tmp_path
):

    filename = (
        tmp_path
        / "fusion.json"
    )

    project = FusionProject.__new__(
        FusionProject
    )

    project.filename = str(filename)
    project.data = {}
    project.file_time = 0

    data = project._empty_project_data()

    del data[
        "songs"
    ]

    write_json(
        filename,
        data
    )

    with pytest.raises(
        RuntimeError,
        match=(
            r"Section songs absente "
            r"dans fusion\.json\."
        )
    ):

        FusionProject(
            filename=str(filename)
        )
