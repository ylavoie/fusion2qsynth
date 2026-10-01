import pytest

from fusion_project import FusionProject

@pytest.fixture(
    autouse=True
)
def workdir(
    tmp_path,
    monkeypatch
):

    monkeypatch.chdir(
        tmp_path
    )

    return tmp_path


@pytest.fixture(
    autouse=True
)
def project():

    project = FusionProject.__new__(
        FusionProject
    )

    project.filename = "fusion.json"
    project.data = (
        project._empty_project_data()
    )
    project.file_time = 0

    return project
