import fcntl
import os


class ProjectLock:

    def __init__(
        self,
        filename
    ):

        self.filename = os.fspath(
            filename
        )

        self._file = None

    def acquire(
        self
    ):

        #
        # Une instance ne doit pas
        # acquérir deux fois le verrou.
        #
        if self._file is not None:

            raise RuntimeError(
                "Verrou déjà acquis."
            )

        #
        # Le fichier de verrouillage
        # reste présent sur disque.
        #
        lock_file = open(
            self.filename,
            "a+",
            encoding="utf-8"
        )

        try:

            #
            # Acquisition exclusive
            # et non bloquante.
            #
            fcntl.flock(
                lock_file.fileno(),
                fcntl.LOCK_EX
                | fcntl.LOCK_NB
            )

        except BaseException:

            #
            # Ne pas conserver un
            # descripteur ouvert si
            # l'acquisition échoue.
            #
            lock_file.close()

            raise

        self._file = lock_file

    def release(
        self
    ):

        #
        # Une libération répétée
        # ne doit pas provoquer
        # d'erreur.
        #
        if self._file is None:

            return

        lock_file = self._file

        self._file = None

        try:

            fcntl.flock(
                lock_file.fileno(),
                fcntl.LOCK_UN
            )

        finally:

            lock_file.close()

    def __enter__(
        self
    ):

        self.acquire()

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback
    ):

        self.release()

        #
        # Ne pas intercepter
        # les exceptions provenant
        # du bloc with.
        #
        return False
