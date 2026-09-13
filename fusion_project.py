#!/usr/bin/env python3

import os
import json
import shutil
import time
import copy

from fusion_lib import (
    note_name, note_range
)

from fusion_gm_map import fusion_program_bank_name

# Fichiers
FUSION_FILE = "fusion.json"

# Sauvegarde
_BACKUP_COUNT = 3
ARCHIVE_DIR = "backups"
ARCHIVE_COUNT = 30

# Journal
_RECOVERY_LOG = "fusion_recovery.log"

class ProjectRecoveryError(RuntimeError):
    pass

class FusionProject:

    def __init__(
        self,
        filename=FUSION_FILE
    ):

        self.filename = filename
        self.data = {}
        self.file_time = 0

        self.load()

    #
    # Chargement / sauvegarde
    #
    def load(self):

        if not os.path.exists(
            self.filename
        ):

            self.data = {}

            return

        try:

            with open(
                self.filename,
                encoding="utf-8"
            ) as f:

                self.data = json.load(f)
                self.file_time = os.path.getmtime(
                    self.filename
                )

        except json.JSONDecodeError:

            backup = self.filename + ".bak"

            if os.path.exists(backup):

                raise ProjectRecoveryError(
                    f"Fichier {self.filename} invalide. "
                    f"Une sauvegarde {backup} est disponible."
                )

            raise RuntimeError(
                f"Fichier {self.filename} invalide."
            )

    def restore_backup(self):

        backup = self.filename + ".bak"

        if not os.path.exists(
            backup
        ):

            return False

        try:

            shutil.copy2(
                backup,
                self.filename
            )

            return True

        except Exception:

            return False

    @classmethod
    def restore_from_backup(
        cls,
        backup
    ):

        if not os.path.exists(
            backup
        ):

            return None

        project = cls.__new__(
            cls
        )

        project.filename = FUSION_FILE
        project.data = {}
        project.file_time = 0

        try:

            shutil.copy2(
                backup,
                project.filename
            )

            project.load()

            errors = project.validate()

            if errors:

                return None

            project.log_recovery(
                "RESTORE_VALIDATED " + backup
            )

            return project

        except Exception:

            project.log_recovery(
                "RESTORE_FAILED " + backup
            )

            return None

    @classmethod
    def restore(cls):

        project = cls.__new__(cls)

        project.filename = FUSION_FILE
        project.data = {}
        project.file_time = 0

        project.log_recovery(
            "RECOVERY_REQUEST"
        )

        if not project.restore_backup():

            project.log_recovery(
                "RESTORE_FAILED"
            )
            return None

        try:

            project.load()

        except ProjectRecoveryError:

            project.log_recovery(
                "RESTORE_FAILED"
            )
            return None

        project.log_recovery(
            "RESTORE_COPY_SUCCESS"
        )
        errors = project.validate()

        if errors:

            project.log_recovery(
                "RESTORE_FAILED"
            )
            return None

        project.log_recovery(
            "RESTORE_VALIDATED"
        )
        return project

    @classmethod
    def get_backup_info(cls,backup):

        if not os.path.exists(
            backup
        ):

            return None

        stat = os.stat(
            backup
        )

        return {
            "filename": backup,
            "size": cls.format_size(stat.st_size),
            "time": cls.format_time(stat.st_mtime)
        }

    @classmethod
    def list_backups(cls):

        backups = []

        backup_base = FUSION_FILE + ".bak"

        for index in range(_BACKUP_COUNT):

            filename = (
                backup_base
                if index == 0
                else backup_base + str(index)
            )

            if not os.path.exists(filename):

                continue

            stat = os.stat(filename)

            backups.append(
                {
                    "filename": filename,
                    "size": stat.st_size,
                    "time": stat.st_mtime
                }
            )

        return backups

    def archive(self):

        if not os.path.exists(
            self.filename
        ):

            return False

        os.makedirs(
            ARCHIVE_DIR,
            exist_ok=True
        )

        timestamp = time.strftime(
            "%Y-%m-%d_%H%M%S"
        )

        basename = os.path.splitext(
            os.path.basename(
                self.filename
            )
        )[0]

        archive_file = os.path.join(
            ARCHIVE_DIR,
            f"{basename}-{timestamp}.json"
        )

        try:

            shutil.copy(
                self.filename,
                archive_file
            )

            self._rotate_archives()

            return True

        except Exception as e:

            print(
                f"Archivage impossible : {e}"
            )

            return False

    def _rotate_archives(self):

        if ARCHIVE_COUNT < 1:

            return

        if not os.path.isdir(
            ARCHIVE_DIR
        ):

            return

        prefix = (
            os.path.splitext(
                os.path.basename(
                    self.filename
                )
            )[0]
            + "-"
        )

        archives = []

        for filename in os.listdir(
            ARCHIVE_DIR
        ):

            if (
                filename.startswith(prefix)
                and
                filename.endswith(".json")
            ):

                archives.append(
                    filename
                )

        archives.sort(
            reverse=True
        )

        for filename in archives[
            ARCHIVE_COUNT:
        ]:

            try:

                os.remove(
                    os.path.join(
                        ARCHIVE_DIR,
                        filename
                    )
                )

            except OSError:

                pass

    def _file_hash(
        self,
        filename
    ):

        import hashlib

        hasher = hashlib.sha256()

        with open(
            filename,
            "rb"
        ) as f:

            for chunk in iter(
                lambda: f.read(65536),
                b""
            ):

                hasher.update(
                    chunk
                )

        return hasher.hexdigest()

    def format_size(size):

        if size < 1024:

            return f"{size} octets"

        if size < 1024 * 1024:

            return f"{size // 1024} Ko"

        return f"{size / (1024 * 1024):.1f} Mo"

    def format_time(timestamp):

        return time.strftime(
            "%d-%m-%Y %H:%M:%S",
            time.localtime(timestamp)
        )

    def get_blocking_errors(
        self,
        errors
    ):

        return [
            error
            for error in errors
            if not (
                isinstance(
                    error,
                    dict
                )
                and
                error.get(
                    "type"
                ) == "midi_channel_conflict"
            )
        ]

    def save_safe(
        self,
        allowed_errors=None
    ):

        errors = self.validate()

        blocking_errors = self.get_blocking_errors(
            errors
        )

        if allowed_errors is not None:

            blocking_errors = [
                error
                for error in blocking_errors
                if error not in allowed_errors
            ]

        if blocking_errors:

            print(
                "Sauvegarde refusée : erreurs de validation."
            )

            for error in blocking_errors:

                print(
                    "-",
                    error
                )

            return False

        self._rotate_backups()

        temp_file = self.filename + ".tmp"

        try:

            with open(
                temp_file,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    self.data,
                    f,
                    indent=2,
                    ensure_ascii=False
                )

            os.replace(
                temp_file,
                self.filename
            )

            return True

        except Exception as e:

            print(
                f"Sauvegarde impossible : {e}"
            )

            return False

        finally:

            if os.path.exists(temp_file):

                os.remove(temp_file)

    def archive_if_changed(self):

        if not os.path.exists(
            self.filename
        ):

            return False

        if not os.path.isdir(
            ARCHIVE_DIR
        ):

            return self.archive()

        prefix = (
            os.path.splitext(
                os.path.basename(
                    self.filename
                )
            )[0]
            + "-"
        )

        archives = sorted(
            (
                filename
                for filename in os.listdir(
                    ARCHIVE_DIR
                )
                if (
                    filename.startswith(prefix)
                    and
                    filename.endswith(".json")
                )
            ),
            reverse=True
        )

        if not archives:

            return self.archive()

        try:

            current_hash = self._file_hash(
                self.filename
            )

            for filename in archives:

                archive_file = os.path.join(
                    ARCHIVE_DIR,
                    filename
                )

                try:

                    if (
                        current_hash
                        ==
                        self._file_hash(
                            archive_file
                        )
                    ):

                        return False

                except OSError:

                    continue

        except OSError:

            pass

        return self.archive()

    @classmethod
    def list_archives(cls):

        if not os.path.isdir(
            ARCHIVE_DIR
        ):

            return []

        archives = []

        for filename in os.listdir(
            ARCHIVE_DIR
        ):

            if (
                filename.startswith("fusion-")
                and
                filename.endswith(".json")
            ):

                full_path = os.path.join(
                    ARCHIVE_DIR,
                    filename
                )

                if not cls.archive_is_valid(
                    full_path
                ):

                    continue

                archives.append(
                    {
                        "filename": full_path,
                        "name": filename,
                        "mtime": os.path.getmtime(
                            full_path
                        ),
                    }
                )

        archives.sort(
            key=lambda item: item["mtime"],
            reverse=True
        )

        return archives

    @classmethod
    def archive_is_valid(
        cls,
        filename
    ):

        if not os.path.isfile(
            filename
        ):

            return False

        try:

            with open(
                filename,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(
                    f
                )

            project = cls.__new__(
                cls
            )

            project.filename = filename
            project.data = data
            project.file_time = 0

            errors = project.validate()

            blocking_errors = (
                project.get_blocking_errors(
                    errors
                )
            )

            return not blocking_errors

        except (
            OSError,
            json.JSONDecodeError,
            TypeError,
            ValueError
        ):

            return False

    @classmethod
    def restore_from_archive(
        cls,
        archive
    ):

        if not os.path.exists(
            archive
        ):

            return None

        project = cls.__new__(
            cls
        )

        project.filename = FUSION_FILE
        project.data = {}
        project.file_time = 0

        try:

            with open(
                archive,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(
                    f
                )

            project.data = data

            errors = project.validate()

            blocking_errors = project.get_blocking_errors(
                errors
            )

            if blocking_errors:

                return None

            #
            # Protéger le fichier actuel avant restauration
            #
            if os.path.exists(
                project.filename
            ):

                project.archive_if_changed()

            shutil.copy(
                archive,
                project.filename
            )

            project.load()

            return project

        except Exception:

            return None

    def _rotate_backups(self):

        if _BACKUP_COUNT < 1:

            return

        backup = self.filename + ".bak"

        for index in range(
            _BACKUP_COUNT - 1,
            0,
            -1
        ):

            src = (
                backup
                if index == 1
                else backup + str(index - 1)
            )

            dst = (
                backup + str(index)
            )

            if os.path.exists(src):

                os.replace(
                    src,
                    dst
                )

        if os.path.exists(
            self.filename
        ):

            os.replace(
                self.filename,
                backup
            )

    def reload(self):

        self.load()

    def reload_if_changed(self):

        if not os.path.exists(
            self.filename
        ):

            return False

        new_time = os.path.getmtime(
            self.filename
        )

        if new_time == self.file_time:

            return False

        try:

            self.load()

        except (
            ProjectRecoveryError,
            RuntimeError
        ):

            return False

        return True

    def backup(self):

        if os.path.exists(
            self.filename
        ):

            shutil.copy2(
                self.filename,
                self.filename + ".bak"
            )

    def log_recovery(self, message):

        try:

            with open(
                _RECOVERY_LOG,
                "a",
                encoding="utf-8"
            ) as f:

                f.write(
                    message + "\n"
                )

        except Exception:

            pass

    #
    # Accès Mix
    #
    def get_mixes(self):

        mixes = self.data.get(
            "mixes"
        )

        if not isinstance(
            mixes,
            dict
        ):

            mixes = {}

            self.data["mixes"] = mixes

        return mixes

    def get_mix(
        self,
        mix_id
    ):

        return self.get_mixes().get(
            mix_id
        )

    def get_mix_channels(
        self,
        mix
    ):

        #
        # Nouveau format v2.10
        #
        if "channels" in mix:

            channels = mix.get(
                "channels",
                {}
            )

            if isinstance(
                channels,
                dict
            ):

                return channels

            return {}

        #
        # Ancien format <= v2.9
        #
        channels = {}

        for part in mix.get(
            "parts",
            {}
        ).values():

            if not isinstance(
                part,
                dict
            ):

                continue

            midi_channel = part.get(
                "midi_channel"
            )

            if midi_channel is None:

                continue

            channel = {}

            bank = part.get(
                "bank"
            )

            program = part.get(
                "program"
            )

            if (
                bank is not None
                and
                program is not None
            ):

                channel["program"] = (
                    f"{bank}:{program}"
                )

            if "instrument" in part:

                channel["instrument"] = (
                    part["instrument"]
                )

            channels[
                str(midi_channel)
            ] = channel

        return channels

    def rename_mix(
        self,
        mix_id,
        name
    ):

        mix = self.get_mix(
            mix_id
        )

        if not mix:

            return (
                False,
                []
            )

        old_name = mix.get(
            "name"
        )

        mix["name"] = name

        errors = self.validate()

        blocking_errors = self.get_blocking_errors(
            errors
        )

        if blocking_errors:

            if old_name is None:

                mix.pop(
                    "name",
                    None
                )

            else:

                mix["name"] = old_name

            return (
                False,
                blocking_errors
            )

        return (
            True,
            []
        )

    def duplicate_mix(
        self,
        source_mix_id,
        new_mix_id
    ):

        source = self.get_mix(
            source_mix_id
        )

        if not source:

            return (
                False,
                [
                    f"Mix source inconnu : {source_mix_id}"
                ]
            )

        mixes = self.get_mixes()

        if new_mix_id in mixes:

            return (
                False,
                [
                    f"Mix déjà existant : {new_mix_id}"
                ]
            )

        import copy

        new_mix = copy.deepcopy(
            source
        )

        new_mix["name"] = self._make_copy_name(
            source.get('name', source_mix_id)
        )

        mixes[new_mix_id] = new_mix

        errors = self.validate()

        blocking_errors = self.get_blocking_errors(
            errors
        )

        if blocking_errors:

            mixes.pop(
                new_mix_id,
                None
            )

            return (
                False,
                blocking_errors
            )

        return (
            True,
            []
        )

    def _make_copy_name(
        self,
        name
    ):

        if "(copie)" not in name:

            candidate = (
                f"{name} (copie)"
            )

            if not any(
                mix.get("name") == candidate
                for mix in self.get_mixes().values()
            ):
                return candidate

        index = 2

        while True:

            candidate = (
                f"{name} (copie {index})"
            )

            if not any(
                mix.get("name") == candidate
                for mix in self.get_mixes().values()
            ):
                return candidate

            index += 1

    def delete_empty_mixes(
        self
    ):

        import copy

        mixes = self.get_mixes()

        backup = copy.deepcopy(
            self.data
        )

        removed = []

        for mix_id, mix in list(
            self.iter_mixes()
        ):

            if not mix.get(
                "parts",
                {}
            ):

                removed.append(
                    mix_id
                )

                del mixes[mix_id]

        errors = self.validate()

        blocking_errors = self.get_blocking_errors(
            errors
        )

        if blocking_errors:

            self.data = backup

            return (
                False,
                blocking_errors
            )

        return (
            True,
            removed
        )

    def delete_mix(
        self,
        mix_id
    ):

        mixes = self.get_mixes()

        if not mix_id in mixes:

            return (
                False,
                [
                    "Mix inconnu"
                ]
            )

        backup = copy.deepcopy(
            self.data
        )

        del mixes[mix_id]

        errors = self.validate()

        blocking_errors = self.get_blocking_errors(
            errors
        )

        if blocking_errors:

            self.data = backup

            return (
                False,
                blocking_errors
            )

        return (
            True,
            []
        )

    def get_parts(
        self,
        mix_id
    ):

        mix = self.get_mix(
            mix_id
        )

        if not mix:

            return {}


        return mix.get(
            "parts",
            {}
        )

    def iter_mixes(self):

        mixes = self.get_mixes()

        for mix_id in self.sort_mix_ids(
            mixes
        ):

            yield (
                mix_id,
                mixes[mix_id]
            )

    def count_mixes(self):

        return len(
            self.get_mixes()
        )

    def summary(self):

        result = {}

        result["mixes"] = len(
            self.get_mixes()
        )

        parts = 0
        configured = 0

        for mix in self.get_mixes().values():

            for part in mix.get(
                "parts",
                {}
            ).values():

                parts += 1

                if "sf2_program" in part:

                    configured += 1

        result["parts"] = parts

        result["configured"] = configured

        result["missing"] = (
            parts - configured
        )

        return result

    @staticmethod
    def sort_mix_ids(data):

        mix_ids = [
            key
            for key in data.keys()
            if ":" in key
        ]

        return sorted(
            mix_ids,
            key=lambda x: (
                int(x.split(":")[0]),
                int(x.split(":")[1])
            )
        )

    def validate_instruments(self):

        errors = []

        for instrument_id, instrument in self.get_instruments().items():

            prefix = f"Instrument {instrument_id}"

            if "name" not in instrument:

                errors.append(
                    f"{prefix} : nom absent"
                )

            if "sf2_bank" not in instrument:

                errors.append(
                    f"{prefix} : sf2_bank absent"
                )

            if "sf2_program" not in instrument:

                errors.append(
                    f"{prefix} : sf2_program absent"
                )

            if "sf2_bank" in instrument:

                # SF2 bank may include percussion banks (>=128)
                if not 0 <= instrument["sf2_bank"] <= 16383:

                    errors.append(
                        f"{prefix} : sf2_bank invalide"
                    )

            if "sf2_program" in instrument:

                if not 0 <= instrument["sf2_program"] <= 127:

                    errors.append(
                        f"{prefix} : sf2_program invalide"
                    )

        return errors

    def validate_part_instruments(self):

        errors = []

        instruments = self.get_instruments()

        for mix_id, mix in self.iter_mixes():

            for part_id, part in mix.get(
                "parts",
                {}
            ).items():

                instrument_id = part.get(
                    "instrument"
                )

                if not instrument_id:

                    continue

                if instrument_id not in instruments:

                    errors.append(
                        {
                            "type": "missing_instrument",
                            "mix_id": mix_id,
                            "part_id": part_id,
                            "channel": part.get(
                                "midi_channel",
                                "?"
                            ),
                            "instrument": instrument_id,
                            "message":
                                f"Mix {mix_id} PART {part_id} : "
                                f"instrument {instrument_id} absent"
                        }
                    )

        return errors

    def validate_midi_channels(self):

        errors = []

        for mix_id, mix in self.iter_mixes():

            channels = {}

            for part_id, part in mix.get("parts", {}).items():

                channel = part.get(
                    "midi_channel"
                )

                if channel is None:

                    continue

                channels.setdefault(
                    channel,
                    []
                ).append(
                    part_id
                )

            for channel, parts in channels.items():

                if len(parts) > 1:

                    errors.append(
                        {
                            "type":
                                "midi_channel_conflict",

                            "mix_id":
                                mix_id,

                            "channel":
                                channel,

                            "parts":
                                parts,

                            "message":
                                f"Mix {mix_id} : "
                                f"canal MIDI {channel} utilisé par "
                                f"PART {', '.join(parts)}"
                        }
                    )

        return errors

    def validate_mix(
        self,
        mix_id
    ):

        mix = self.get_mix(
            mix_id
        )

        if not mix:

            return [
                f"Mix inconnu : {mix_id}"
            ]

        return self.validate_mix_data(
            mix_id,
            mix
        )

    def validate_mix_data(
        self,
        mix_id,
        mix
    ):

        errors = []

        if not isinstance(
            mix,
            dict
        ):

            errors.append(
                f"{mix_id} : définition invalide."
            )

            return errors

        #
        # Nouveau modèle v2.10
        #
        if "channels" in mix:

            channels = mix.get(
                "channels"
            )

            if not isinstance(
                channels,
                dict
            ):

                errors.append(
                    f"{mix_id} : channels invalide."
                )

                return errors

            for channel_id, channel in (
                channels.items()
            ):

                errors.extend(
                    self.validate_mix_channel_data(
                        mix_id,
                        channel_id,
                        channel
                    )
                )

            return errors

        #
        # Ancien modèle <= v2.9
        #
        if "parts" not in mix:

            errors.append(
                f"{mix_id} : aucune PART."
            )

            return errors

        for part_id, part in (
            mix["parts"].items()
        ):

            errors.extend(
                self.validate_part_data(
                    mix_id,
                    part_id,
                    part
                )
            )

        return errors

    def validate_mix_channel_data(
        self,
        mix_id,
        channel_id,
        channel
    ):

        errors = []

        prefix = (
            f"{mix_id} CH {channel_id}"
        )

        #
        # Canal MIDI
        #
        try:

            midi_channel = int(
                channel_id
            )

        except (
            TypeError,
            ValueError
        ):

            errors.append(
                f"{prefix} : canal MIDI invalide."
            )

            return errors

        if not (
            1 <= midi_channel <= 16
        ):

            errors.append(
                f"{prefix} : canal MIDI hors limites."
            )

        #
        # Définition du canal
        #
        if not isinstance(
            channel,
            dict
        ):

            errors.append(
                f"{prefix} : définition invalide."
            )

            return errors

        #
        # Seulement les champs v2.10 autorisés
        #
        allowed_fields = {
            "program",
            "instrument"
        }

        for field in channel:

            if field not in allowed_fields:

                errors.append(
                    f"{prefix} : champ inconnu '{field}'."
                )

        #
        # PROGRAM Fusion optionnel
        #
        program_id = channel.get(
            "program"
        )

        if program_id is not None:

            if not isinstance(
                program_id,
                str
            ):

                errors.append(
                    f"{prefix} : PROGRAM Fusion invalide."
                )

            else:

                try:

                    bank_text, program_text = (
                        program_id.split(
                            ":",
                            1
                        )
                    )

                    bank = int(
                        bank_text
                    )

                    program = int(
                        program_text
                    )

                except (
                    ValueError,
                    AttributeError
                ):

                    errors.append(
                        f"{prefix} : PROGRAM Fusion invalide "
                        f"'{program_id}'."
                    )

                else:

                    if not (
                        0 <= bank <= 16383
                    ):

                        errors.append(
                            f"{prefix} : bank Fusion hors limites."
                        )

                    if not (
                        0 <= program <= 127
                    ):

                        errors.append(
                            f"{prefix} : program Fusion hors limites."
                        )

                    if (
                        0 <= bank <= 16383
                        and
                        0 <= program <= 127
                        and
                        self.get_program(
                            program_id
                        ) is None
                    ):

                        errors.append(
                            f"{prefix} : PROGRAM global "
                            f"{program_id} inexistant."
                        )

        #
        # Override instrument optionnel
        #
        instrument_id = channel.get(
            "instrument"
        )

        if instrument_id is not None:

            if (
                not isinstance(
                    instrument_id,
                    str
                )
                or
                not instrument_id
            ):

                errors.append(
                    f"{prefix} : instrument invalide."
                )

            elif self.get_instrument(
                instrument_id
            ) is None:

                errors.append(
                    f"{prefix} : instrument "
                    f"{instrument_id} inexistant."
                )

        return errors

    def validate_part_data(
        self,
        mix_id,
        part_id,
        part
    ):

        errors = []

        prefix = f"{mix_id} PART {part_id}"

        if "midi_channel" not in part:

            errors.append(
                f"{prefix} : midi_channel absent."
            )

        else:

            ch = part["midi_channel"]

            if not (1 <= ch <= 16):

                errors.append(
                    f"{prefix} : canal MIDI invalide ({ch})."
                )

        has_bank = (
            "bank" in part
        )

        has_program = (
            "program" in part
        )

        if (
            has_bank
            and
            not has_program
        ):

            errors.append(
                f"{prefix} : program Fusion absent."
            )

        if (
            has_program
            and
            not has_bank
        ):

            errors.append(
                f"{prefix} : bank Fusion absente."
            )

        if "name" in part:

            if "sf2_bank" not in part:

                errors.append(
                    f"{prefix} : sf2_bank absent."
                )

            if "sf2_program" not in part:

                errors.append(
                    f"{prefix} : sf2_program absent."
                )


        if (
            "note_min" in part
            and
            "note_max" in part
        ):

            if not (
                0 <= part["note_min"]
                <= part["note_max"]
                <= 127
            ):

                errors.append(
                    f"{prefix} : zone de notes invalide."
                )


        if (
            "velocity_min" in part
            and
            "velocity_max" in part
        ):

            if not (
                0 <= part["velocity_min"]
                <= part["velocity_max"]
                <= 127
            ):

                errors.append(
                    f"{prefix} : plage de vélocité invalide."
                )

        return errors

    def is_qsynth_ready(
        self,
        part
    ):

        if "midi_channel" not in part:

            return False

        instrument = self.resolve_part_instrument(
            part
        )

        if not instrument:

            return False

        return (
            "sf2_bank" in instrument
            and
            "sf2_program" in instrument
        )

    def update_part(
        self,
        mix_id,
        part_id,
        updates
    ):

        mix = self.get_mix(
            mix_id
        )

        if not mix:
            return (
                False,
                []
            )

        parts = mix.get(
            "parts",
            {}
        )

        part = parts.get(
            str(part_id)
        )

        if not part:
            return (
                False,
                []
            )

        old = dict(part)

        before_errors = self.get_blocking_errors(
            self.validate()
        )

        part.update(
            updates
        )

        after_errors = self.get_blocking_errors(
            self.validate()
        )

        new_errors = [
            error
            for error in after_errors
            if error not in before_errors
        ]

        if new_errors:

            part.clear()

            part.update(
                old
            )

            return (
                False,
                new_errors
            )

        return (
            True,
            before_errors
        )

    def resolve_mix_channel_instrument(
        self,
        channel
    ):

        #
        # Override local
        #
        instrument = (
            self.resolve_part_instrument(
                channel
            )
        )

        if instrument:

            return instrument

        #
        # Héritage du PROGRAM global
        #
        program_id = channel.get(
            "program"
        )

        if not program_id:

            return None

        return self.resolve_program_instrument(
            program_id
        )

    #
    # Accès Program
    #
    def get_programs(self):

        programs = self.data.get(
            "programs"
        )

        if not isinstance(
            programs,
            dict
        ):

            programs = {}

            self.data["programs"] = programs

        return programs

    def get_program(
        self,
        program_id
    ):

        return self.get_programs().get(
            program_id
        )

    def rename_program(
        self,
        program_id,
        name
    ):

        program = self.get_program(
            program_id
        )

        if not program:

            return (
                False,
                []
            )

        old_name = program.get(
            "name"
        )

        program["name"] = name

        errors = self.validate()

        blocking_errors = self.get_blocking_errors(
            errors
        )

        if blocking_errors:

            if old_name is None:

                program.pop(
                    "name",
                    None
                )

            else:

                program["name"] = old_name

            return (
                False,
                blocking_errors
            )

        return (
            True,
            []
        )

    def delete_program(
        self,
        program_id
    ):

        import copy

        programs = self.get_programs()

        if program_id not in programs:

            return (
                False,
                [
                    "PROGRAM inconnu"
                ]
            )

        backup = copy.deepcopy(
            self.data
        )

        del programs[
            program_id
        ]

        errors = self.validate()

        blocking_errors = self.get_blocking_errors(
            errors
        )

        if blocking_errors:

            self.data = backup

            return (
                False,
                blocking_errors
            )

        return (
            True,
            []
        )

    def ensure_program(
        self,
        program_id
    ):

        programs = self.get_programs()

        if program_id not in programs:

            programs[program_id] = {
                "name":
                    f"Fusion Program {program_id}",

                "parts": {}
            }

        return programs[program_id]

    def iter_programs(self):

        programs = self.get_programs()

        for program_id in self.sort_mix_ids(
            programs
        ):

            yield (
                program_id,
                programs[program_id]
            )

    def count_programs(self):

        return len(
            self.get_programs()
        )

    def validate_program(
        self,
        program_id
    ):

        program = self.get_program(
            program_id
        )

        if not program:

            return [
                f"PROGRAM inconnu : {program_id}"
            ]

        part = program.get(
            "parts",
            {}
        ).get(
            "1"
        )

        if not part:

            return [
                f"{program_id} : PART 1 absente."
            ]

        return self.validate_part_data(
            program_id,
            "1",
            part
        )

    #
    # Accès Song
    #
    def get_songs(self):

        songs = self.data.get(
            "songs"
        )

        if not isinstance(
            songs,
            dict
        ):

            songs = {}

            self.data["songs"] = songs

        return songs

    def get_song(
        self,
        song_id
    ):

        return self.get_songs().get(
            str(song_id)
        )

    def rename_song(
        self,
        song_id,
        name
    ):

        song = self.get_song(
            song_id
        )

        if not song:

            return (
                False,
                []
            )

        old_name = song.get(
            "name"
        )

        song["name"] = name

        errors = self.validate()

        blocking_errors = self.get_blocking_errors(
            errors
        )

        if blocking_errors:

            if old_name is None:

                song.pop(
                    "name",
                    None
                )

            else:

                song["name"] = old_name

            return (
                False,
                blocking_errors
            )

        return (
            True,
            []
        )

    def delete_song(
        self,
        song_id
    ):

        import copy

        song_id = str(
            song_id
        )

        songs = self.get_songs()

        if song_id not in songs:

            return (
                False,
                [
                    "SONG inconnue"
                ]
            )

        backup = copy.deepcopy(
            self.data
        )

        del songs[
            song_id
        ]

        errors = self.validate()

        blocking_errors = self.get_blocking_errors(
            errors
        )

        if blocking_errors:

            self.data = backup

            return (
                False,
                blocking_errors
            )

        return (
            True,
            []
        )

    def ensure_song(
        self,
        song_id
    ):

        song_id = str(song_id)

        songs = self.get_songs()

        if song_id not in songs:

            songs[song_id] = {
                "name":
                    f"Fusion Song {song_id}",

                "channels": {}
            }

        return songs[song_id]

    def iter_songs(self):

        songs = self.get_songs()

        for song_id in sorted(
            songs,
            key=lambda value: value.lower()
        ):

            yield (
                song_id,
                songs[song_id]
            )

    def count_songs(self):

        return len(
            self.get_songs()
        )

    def validate_song_channel_data(
        self,
        song_id,
        channel_id,
        channel
    ):

        errors = []

        try:

            midi_channel = int(
                channel_id
            )

        except ValueError:

            return [
                f"{song_id} CH {channel_id} : canal MIDI invalide."
            ]

        if not (
            1 <= midi_channel <= 16
        ):

            errors.append(
                f"{song_id} CH {channel_id} : canal MIDI invalide."
            )

        programs = channel.get(
            "programs"
        )

        #
        # Nouveau format SONG
        #
        if programs is not None:

            if not isinstance(
                programs,
                dict
            ):

                errors.append(
                    f"{song_id} CH {channel_id} : "
                    "programs invalide."
                )

            else:

                for program_id, program_data in programs.items():

                    try:

                        bank_str, program_str = (
                            program_id.split(
                                ":",
                                1
                            )
                        )

                        bank = int(
                            bank_str
                        )

                        program = int(
                            program_str
                        )

                    except (
                        ValueError,
                        AttributeError
                    ):

                        errors.append(
                            f"{song_id} CH {channel_id} : "
                            f"PROGRAM invalide ({program_id})."
                        )

                        continue

                    if not (
                        0 <= bank <= 16383
                    ):

                        errors.append(
                            f"{song_id} CH {channel_id} : "
                            f"Bank invalide ({bank})."
                        )

                    if not (
                        0 <= program <= 127
                    ):

                        errors.append(
                            f"{song_id} CH {channel_id} : "
                            f"Program invalide ({program})."
                        )

                    if not isinstance(
                        program_data,
                        dict
                    ):

                        errors.append(
                            f"{song_id} CH {channel_id} : "
                            f"PROGRAM {program_id} invalide."
                        )

        #
        # Ancien format SONG
        #
        else:

            has_bank = (
                "bank" in channel
            )

            has_program = (
                "program" in channel
            )

            if (
                has_bank
                and
                not has_program
            ):

                errors.append(
                    f"{song_id} CH {channel_id} : Program absent."
                )

            if (
                has_program
                and
                not has_bank
            ):

                errors.append(
                    f"{song_id} CH {channel_id} : Bank absente."
                )

            if has_bank:

                bank = channel["bank"]

                if not (
                    0 <= bank <= 16383
                ):

                    errors.append(
                        f"{song_id} CH {channel_id} : "
                        f"Bank invalide ({bank})."
                    )

            if has_program:

                program = channel["program"]

                if not (
                    0 <= program <= 127
                ):

                    errors.append(
                        f"{song_id} CH {channel_id} : "
                        f"Program invalide ({program})."
                    )

        for field in (
            "volume",
            "pan",
            "expression",
            "reverb",
            "chorus"
        ):

            if field not in channel:

                continue

            value = channel[
                field
            ]

            if not (
                0 <= value <= 127
            ):

                errors.append(
                    f"{song_id} CH {channel_id} : "
                    f"{field} invalide ({value})."
                )

        return errors

    def validate_song_channel(
        self,
        song_id,
        channel_id
    ):

        song = self.get_song(
            song_id
        )

        if not song:

            return [
                f"SONG inconnue : {song_id}"
            ]

        channels = song.get(
            "channels",
            {}
        )

        channel = channels.get(
            str(channel_id)
        )

        if channel is None:

            return [
                f"{song_id} CH {channel_id} : canal inconnu."
            ]

        return self.validate_song_channel_data(
            song_id,
            str(channel_id),
            channel
        )

    def validate_song(
        self,
        song_id
    ):

        song = self.get_song(
            song_id
        )

        if not song:

            return [
                f"SONG inconnue : {song_id}"
            ]

        errors = []

        for channel_id, channel in song.get(
            "channels",
            {}
        ).items():

            errors.extend(
                self.validate_song_channel_data(
                    song_id,
                    channel_id,
                    channel
                )
            )

        return errors

    def resolve_song_program_instrument(
        self,
        program_id,
        program_data
    ):

        #
        # Surcharge locale de la SONG
        #
        instrument = self.resolve_part_instrument(
            program_data
        )

        if instrument:

            return instrument

        #
        # Héritage du PROGRAM global
        #
        return self.resolve_program_instrument(
            program_id
        )

    def resolve_program_instrument(
        self,
        program_id
    ):

        program = self.get_program(
            program_id
        )

        if not program:

            return None

        parts = program.get(
            "parts",
            {}
        )

        if len(parts) != 1:

            return None

        part = next(
            iter(
                parts.values()
            )
        )

        return self.resolve_part_instrument(
            part
        )

    #
    # Diagnostic
    #
    def get_mix_diagnostic(
        self
    ):

        result = []

        for mix_id, mix in self.iter_mixes():

            mix_result = {
                "mix": mix_id,
                "name": mix.get(
                    "name",
                    mix_id
                )
            }

            #
            # Nouveau format v2.10
            #
            if "channels" in mix:

                mix_result[
                    "channels"
                ] = []

                for channel_id, channel in sorted(
                    mix.get(
                        "channels",
                        {}
                    ).items(),
                    key=lambda item: int(
                        item[0]
                    )
                ):

                    errors = (
                        self.validate_mix_channel_data(
                            mix_id,
                            channel_id,
                            channel
                        )
                    )

                    instrument = (
                        self.resolve_mix_channel_instrument(
                            channel
                        )
                    )

                    mix_result[
                        "channels"
                    ].append(
                        {
                            "channel":
                                int(channel_id),

                            "program":
                                channel.get(
                                    "program"
                                ),

                            "fusion_valid":
                                len(errors) == 0,

                            "qsynth_configured":
                                instrument is not None,

                            "instrument":
                                instrument
                        }
                    )

                result.append(
                    mix_result
                )

                continue

            #
            # Ancien format <= v2.9
            #
            mix_result[
                "parts"
            ] = []

            channels = []

            for part_id, part in mix.get(
                "parts",
                {}
            ).items():

                errors = self.validate_part_data(
                    mix_id,
                    part_id,
                    part
                )

                instrument = (
                    self.resolve_part_instrument(
                        part
                    )
                )

                midi_channel = part.get(
                    "midi_channel"
                )

                if midi_channel is not None:

                    channels.append(
                        midi_channel
                    )

                mix_result[
                    "parts"
                ].append(
                    {
                        "part":
                            part_id,

                        "midi_channel":
                            midi_channel,

                        "fusion_valid":
                            len(errors) == 0,

                        "qsynth_configured":
                            instrument is not None,

                        "instrument":
                            instrument
                    }
                )

            duplicates = sorted(
                {
                    channel
                    for channel in channels
                    if channels.count(
                        channel
                    ) > 1
                }
            )

            if duplicates:

                mix_result[
                    "shared_channels"
                ] = duplicates

            result.append(
                mix_result
            )

        return result

    def get_program_diagnostic(self):

        results = []

        for program_id, program in self.iter_programs():

            parts = program.get(
                "parts",
                {}
            )

            part = parts.get(
                "1"
            )

            result = {
                "program": program_id,
                "name": program.get(
                    "name",
                    ""
                ),
                "fusion_valid": False,
                "qsynth_configured": False,
                "errors": []
            }

            if not part:

                result["errors"].append(
                    "PART absente"
                )

            else:

                if "midi_channel" in part:

                    result["fusion_valid"] = True

                else:

                    result["fusion_valid"] = False
                    result["errors"].append(
                        "Canal MIDI absent"
                    )

                #
                # Validation Fusion
                #

                if "midi_channel" not in part:

                    result["fusion_valid"] = False
                    result["errors"].append(
                        "Canal MIDI absent"
                    )

                else:

                    midi_channel = part[
                        "midi_channel"
                    ]

                    if not (
                        1 <= midi_channel <= 16
                    ):

                        result["fusion_valid"] = False
                        result["errors"].append(
                            f"Canal MIDI invalide ({midi_channel})"
                        )

                #
                # Plage de notes
                #
                if (
                    "note_min" in part
                    and
                    "note_max" in part
                ):

                    if not (
                        0
                        <= part["note_min"]
                        <= part["note_max"]
                        <= 127
                    ):

                        result["fusion_valid"] = False
                        result[
                            "errors"
                        ].append(
                            "Zone de notes invalide"
                        )

                #
                # Plage de vélocité
                #
                if (
                    "velocity_min" in part
                    and
                    "velocity_max" in part
                ):

                    if not (
                        0
                        <= part["velocity_min"]
                        <= part["velocity_max"]
                        <= 127
                    ):

                        result["fusion_valid"] = False
                        result[
                            "errors"
                        ].append(
                            "Plage de vélocité invalide"
                        )

                result["qsynth_configured"] = (
                    self.is_qsynth_ready(
                        part
                    )
                )

            results.append(
                result
            )

        return results

    def get_song_diagnostic(
        self
    ):

        diagnostic = []

        for song_id, song in self.iter_songs():

            song_diagnostic = {
                "song": song_id,
                "name": song.get(
                    "name",
                    song_id
                ),
                "channels": []
            }

            channels = song.get(
                "channels",
                {}
            )

            for channel_id, channel in channels.items():

                errors = self.validate_song_channel_data(
                    song_id,
                    channel_id,
                    channel
                )

                fusion_valid = (
                    len(errors) == 0
                )

                programs = channel.get(
                    "programs"
                )

                #
                # Nouveau format SONG
                #
                if isinstance(
                    programs,
                    dict
                ):

                    if not programs:

                        qsynth_configured = False

                    else:

                        qsynth_configured = True

                        for (
                            program_id,
                            program_data
                        ) in programs.items():

                            instrument = (
                                self.resolve_song_program_instrument(
                                    program_id,
                                    program_data
                                )
                            )

                            if not instrument:

                                qsynth_configured = False
                                break

                #
                # Ancien format SONG
                #
                else:

                    instrument = (
                        self.resolve_part_instrument(
                            channel
                        )
                    )

                    qsynth_configured = (
                        instrument is not None
                    )

                song_diagnostic[
                    "channels"
                ].append(
                    {
                        "channel": channel_id,
                        "fusion_valid": fusion_valid,
                        "qsynth_configured":
                            qsynth_configured
                    }
                )

            diagnostic.append(
                song_diagnostic
            )

        return diagnostic

    def get_project_diagnostic_summary(self):

        summary = {
            "mixes": {
                "total": 0,
                "ok": 0,
                "unconfigured": 0,
                "error": 0,
                "info": 0
            },
            "programs": {
                "total": 0,
                "ok": 0,
                "unconfigured": 0,
                "error": 0,
                "info": 0
            },
            "songs": {
                "total": 0,
                "ok": 0,
                "unconfigured": 0,
                "error": 0,
                "info": 0
            }
        }


        # MIX

        for mix in self.get_mix_diagnostic():

            summary["mixes"]["total"] += 1

            parts = mix.get(
                "parts",
                []
            )

            fusion_valid = all(
                part.get(
                    "fusion_valid",
                    False
                )
                for part in parts
            )

            qsynth_configured = (
                bool(parts)
                and all(
                    part.get(
                        "qsynth_configured",
                        False
                    )
                    for part in parts
                )
            )

            if not fusion_valid:

                summary["mixes"]["error"] += 1

            elif not qsynth_configured:

                summary["mixes"]["unconfigured"] += 1

            else:

                summary["mixes"]["ok"] += 1

            if mix.get(
                "shared_channels"
            ):

                summary["mixes"]["info"] += 1


        # PROGRAM

        for program in self.get_program_diagnostic():

            summary["programs"]["total"] += 1

            if not program.get(
                "fusion_valid",
                False
            ):

                summary["programs"]["error"] += 1

            elif not program.get(
                "qsynth_configured",
                False
            ):

                summary["programs"]["unconfigured"] += 1

            else:

                summary["programs"]["ok"] += 1


        # SONG

        for song in self.get_song_diagnostic():

            summary["songs"]["total"] += 1

            channels = song.get(
                "channels",
                []
            )

            fusion_valid = all(
                channel.get(
                    "fusion_valid",
                    False
                )
                for channel in channels
            )

            qsynth_configured = (
                bool(channels)
                and all(
                    channel.get(
                        "qsynth_configured",
                        False
                    )
                    for channel in channels
                )
            )

            if not fusion_valid:

                summary["songs"]["error"] += 1

            elif not qsynth_configured:

                summary["songs"]["unconfigured"] += 1

            else:

                summary["songs"]["ok"] += 1


        return summary

    #
    # Affichage
    #
    def print_mix(
        self,
        mix_id
    ):

        mix = self.get_mix(
            mix_id
        )

        if not mix:

            print(
                "Mix inconnu :",
                mix_id
            )

            return

        print()

        print(
            "Mix :",
            mix_id,
            "-",
            mix.get(
                "name",
                mix_id
            )
        )

        #
        # Nouveau format v2.10
        #
        if "channels" in mix:

            channels = mix.get(
                "channels",
                {}
            )

            for channel_id, channel in sorted(
                channels.items(),
                key=lambda item: int(
                    item[0]
                )
            ):

                program_id = channel.get(
                    "program"
                )

                instrument = (
                    self.resolve_mix_channel_instrument(
                        channel
                    )
                )

                instrument_name = (
                    instrument.get(
                        "name",
                        "?"
                    )
                    if instrument
                    else "Non configuré"
                )

                print()

                print(
                    "CH",
                    channel_id
                )

                print(
                    " PROGRAM    :",
                    (
                        program_id
                        if program_id
                        else "?"
                    )
                )

                print(
                    " Instrument :",
                    instrument_name
                )

            return

        #
        # Ancien format <= v2.9
        #
        for part_id, part in self.iter_parts(
            mix
        ):

            self.print_part(
                part_id,
                part
            )

    def print_part(
        self,
        part_id,
        part,
        fusion_name=None
    ):

        print()

        print(
            "PART",
            part_id
        )

        print("----------------")

        print(
            "Nom Fusion     :",
            (
                fusion_name
                if fusion_name is not None
                else part.get(
                    "fusion_name",
                    "Non défini"
                )
            )
        )

        bank = part.get("bank")

        print(
            "Fusion Bank    :",
            (
                f"{fusion_program_bank_name(bank)} ({bank})"
                if bank is not None
                else "?"
            )
        )

        print(
            "Fusion Program :",
            part.get(
                "program",
                "?"
            )
        )


        instrument = self.resolve_part_instrument(
            part
        )


        if instrument:

            print(
                "Instrument     :",
                instrument.get(
                    "name",
                    "?"
                )
            )

            print(
                "SF2 Bank       :",
                instrument.get(
                    "sf2_bank",
                    0
                )
            )

            print(
                "SF2 Program    :",
                instrument.get(
                    "sf2_program",
                    0
                )
            )

        else:

            print(
                "Instrument     : Non configuré"
            )


        print(
            "Canal MIDI     :",
            part.get(
                "midi_channel",
                "?"
            )
        )

        print(
            "Plage          :",
            note_range(
                part.get(
                    "note_min",
                    None
                ),
                part.get(
                    "note_max",
                    None
                )
            )
        )

        print(
            "Velocity       :",
            part.get(
                "velocity_min",
                0
            ),
            "-",
            part.get(
                "velocity_max",
                127
            )
        )

    # Mix
    def iter_parts(
        self,
        mix
    ):

        for part_id in sorted(
            mix.get(
                "parts",
                {}
            ),
            key=int
        ):

            yield (
                part_id,
                mix["parts"][part_id]
            )

    #
    # Validation
    #
    def validate(self):

        errors = []

        errors.extend(
            self.validate_instruments()
        )

        errors.extend(
            self.validate_part_instruments()
        )

        errors.extend(
            self.validate_midi_channels()
        )

        for mix_id in self.sort_mix_ids(
            self.get_mixes()
        ):

            errors.extend(
                self.validate_mix(
                    mix_id
                )
            )

        for program_id, program in self.iter_programs():

            errors.extend(
                self.validate_program(
                    program_id
                )
            )

        for song_id, song in self.iter_songs():

            errors.extend(
                self.validate_song(
                    song_id
                )
            )

        return errors

    def mix_has_parts(
        self,
        mix_id
    ):

        mix = self.get_mix(
            mix_id
        )

        if not mix:

            return False

        return bool(
            mix.get(
                "parts"
            )
        )

    def mix_has_channels(
        self,
        mix_id
    ):

        mix = self.get_mix(
            mix_id
        )

        if not mix:

            return False

        #
        # Nouveau format v2.10
        #
        if "channels" in mix:

            return bool(
                mix.get(
                    "channels",
                    {}
                )
            )

        #
        # Ancien format <= v2.9
        #
        return bool(
            mix.get(
                "parts",
                {}
            )
        )

    def ensure_mix(
        self,
        mix_id
    ):

        mixes = self.get_mixes()

        if mix_id not in mixes:

            mixes[mix_id] = {
                "name": (
                    f"Fusion Mix {mix_id}"
                ),
                "channels": {}
            }

        return mixes[mix_id]

    def replace_mix_parts(
            self,
            mix_id,
            parts,
            allowed_errors=None
        ):

            mix = self.get_mix(
                mix_id
            )

            if not mix:

                return (
                    False,
                    []
                )

            old_parts = dict(
                mix.get(
                    "parts",
                    {}
                )
            )

            mix["parts"] = parts

            errors = self.validate()

            blocking_errors = self.get_blocking_errors(
                errors
            )

            if allowed_errors:

                blocking_errors = [
                    error
                    for error in blocking_errors
                    if error not in allowed_errors
                ]

            if blocking_errors:

                mix["parts"] = old_parts

                return (
                    False,
                    blocking_errors
                )

            return (
                True,
                []
            )

    def replace_mix_channels(
        self,
        mix_id,
        channels,
        allowed_errors=None
    ):

        mix = self.get_mix(
            mix_id
        )

        if not mix:

            return (
                False,
                [
                    f"Mix inconnu : {mix_id}"
                ]
            )

        #
        # Sauvegarde complète de l'ancien MIX
        # pour permettre un rollback exact.
        #
        old_mix = copy.deepcopy(
            mix
        )

        #
        # Nouveau modèle v2.10
        #
        mix["channels"] = channels

        #
        # Une recapture convertit définitivement
        # ce MIX vers le nouveau modèle.
        #
        mix.pop(
            "parts",
            None
        )

        errors = self.get_blocking_errors(
            self.validate()
        )

        if allowed_errors is not None:

            errors = [
                error
                for error in errors
                if error not in allowed_errors
            ]

        if errors:

            mix.clear()

            mix.update(
                old_mix
            )

            return (
                False,
                errors
            )

        return (
            True,
            []
        )

    def prepare_capture(
        self,
        mix_id
    ):

        mixes = self.get_mixes()

        if mix_id not in mixes:

            mixes[mix_id] = {

                "name":
                    f"Fusion Mix {mix_id}",

                "parts": {}

            }

            return True

        if (
            "parts" in mixes[mix_id]
            and
            mixes[mix_id]["parts"]
        ):

            return False

        return True

    def find_part_by_channel(
        self,
        mix_id,
        midi_channel
    ):

        parts = self.get_parts(
            mix_id
        )


        for part_id, part in parts.items():

            if part.get(
                "midi_channel"
            ) == midi_channel:

                return (
                    part_id,
                    part
                )


        return (
            None,
            None
        )

    def build_channel_map(self):

        channels = {}

        for mix_id, mix in self.iter_mixes():

            for part_id, part in mix.get(
                "parts",
                {}
            ).items():

                ch = part.get(
                    "midi_channel"
                )

                if ch is None:

                    continue

                channels[ch] = {
                    "mix_id": mix_id,
                    "part_id": part_id,
                    "part": part
                }

        return channels
    #
    # Instruments
    #
    def get_instruments(self):

        return self.data.get(
            "instruments",
            {}
        )

    def get_instrument(
        self,
        instrument_id
    ):

        instruments = self.get_instruments()

        return instruments.get(
            instrument_id
        )

    def resolve_part_instrument(
        self,
        part
    ):

        if "instrument" in part:

            instrument = self.get_instrument(
                part["instrument"]
            )

            if instrument:

                return instrument

        if (
            "sf2_bank" in part
            and
            "sf2_program" in part
        ):

            return {
                "name": part.get(
                    "name",
                    "Non configuré"
                ),
                "sf2_bank": part["sf2_bank"],
                "sf2_program": part["sf2_program"]
            }

        return None

    def set_part_instrument(
        self,
        mix_id,
        part_id,
        instrument_id
    ):

        mix = self.get_mix(mix_id)

        if not mix:
            return False

        part = mix.get("parts", {}).get(str(part_id))

        if not part:
            return False

        if not self.get_instrument(instrument_id):
            return False

        part["instrument"] = instrument_id

        for key in (
            "name",
            "sf2_bank",
            "sf2_program"
        ):
            part.pop(key, None)

        return True

    def list_instruments(self):

        return sorted(
            self.get_instruments().items()
        )

    def add_instrument(
        self,
        instrument_id,
        instrument
    ):

        if "instruments" not in self.data:

            self.data["instruments"] = {}

        if instrument_id in self.data["instruments"]:

            return False

        self.data["instruments"][instrument_id] = instrument

        return True

    def update_instrument(
        self,
        instrument_id,
        instrument
    ):

        if "instruments" not in self.data:

            self.data["instruments"] = {}

        self.data["instruments"][instrument_id] = instrument

        return True

    def remove_instrument(
        self,
        instrument_id
    ):

        instruments = self.get_instruments()

        if instrument_id not in instruments:

            return False

        if self.find_instrument_usage(
            instrument_id
        ):

            return False

        del instruments[instrument_id]

        return True

    def find_instrument_usage(
        self,
        instrument_id
    ):

        usages = []

        for mix_id, mix in self.iter_mixes():

            for part_id, part in mix.get(
                "parts",
                {}
            ).items():

                if part.get(
                    "instrument"
                ) == instrument_id:

                    usages.append(
                        {
                            "mix_id": mix_id,
                            "part_id": part_id
                        }
                    )

        return usages
