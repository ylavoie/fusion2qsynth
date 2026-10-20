import pytest

from fusion_lock import ProjectLock


def test_project_lock_prevents_second_instance(
    tmp_path
):

    lock_file = (
        tmp_path
        / "fusion.json.lock"
    )

    first = ProjectLock(
        lock_file
    )

    second = ProjectLock(
        lock_file
    )

    try:

        first.acquire()

        with pytest.raises(
            BlockingIOError
        ):

            second.acquire()

    finally:

        second.release()

        first.release()


def test_project_lock_can_be_reacquired_after_release(
    tmp_path
):

    lock_file = (
        tmp_path
        / "fusion.json.lock"
    )

    first = ProjectLock(
        lock_file
    )

    second = ProjectLock(
        lock_file
    )

    try:

        first.acquire()

        first.release()

        #
        # Le verrou libéré doit
        # pouvoir être acquis
        # par une autre instance.
        #
        second.acquire()

    finally:

        second.release()

        first.release()


import subprocess
import sys


def test_project_lock_prevents_another_process(
    tmp_path
):

    lock_file = (
        tmp_path
        / "fusion.json.lock"
    )

    lock = ProjectLock(
        lock_file
    )

    try:

        lock.acquire()

        #
        # Un second processus tente
        # d'acquérir le même verrou.
        #
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "import fcntl, sys; "
                    "f = open(sys.argv[1], 'a+'); "
                    "fcntl.flock("
                    "f.fileno(), "
                    "fcntl.LOCK_EX | fcntl.LOCK_NB"
                    ")"
                ),
                str(lock_file)
            ],
            capture_output=True,
            text=True,
            timeout=5
        )

        #
        # Le second processus doit
        # échouer immédiatement.
        #
        assert result.returncode != 0

        assert (
            "BlockingIOError"
            in result.stderr
        )

    finally:

        lock.release()


def test_project_lock_released_after_exception(
    tmp_path
):

    lock_file = (
        tmp_path
        / "fusion.json.lock"
    )

    first = ProjectLock(
        lock_file
    )

    second = ProjectLock(
        lock_file
    )

    with pytest.raises(
        RuntimeError,
        match="Erreur simulée"
    ):

        with first:

            raise RuntimeError(
                "Erreur simulée"
            )

    #
    # La sortie du contexte doit
    # avoir libéré le verrou.
    #
    try:

        second.acquire()

    finally:

        second.release()
