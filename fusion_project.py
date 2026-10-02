#!/usr/bin/env python3

import os
import json
import shutil
import time
import copy
import re
import hashlib

from fusion_constants import (
    PROJECT_FORMAT_VERSION,
    ARCHIVE_DIR,
    ARCHIVE_COUNT
)

from fusion_gm_map import (
    FUSION_PROGRAM_BANK_NAMES,
    FUSION_MIX_BANK_NAMES,
    fusion_program_bank_name,
    fusion_mix_bank_name
)

# Fichiers
FUSION_FILE = "fusion.json"

# Sauvegarde
_BACKUP_COUNT = 3

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

    def _empty_project_data(
        self
    ):

        return {
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

    #
    # Chargement / sauvegarde
    #
    def load(self):

        if not os.path.exists(
            self.filename
        ):

            self.data = self._empty_project_data()

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

        self._validate_format_version()
        self._validate_root_structure()

        allowed_errors = self.get_blocking_errors(
            self.validate()
        )

        mix_migration = (
            self._migrate_legacy_mixes()
        )
        song_migration = (
            self._migrate_legacy_songs()
        )

        migration_needed = (
            mix_migration["mixes"] > 0
            or
            song_migration["songs"] > 0
        )

        if mix_migration["mixes"] > 0:

            print(
                "mix_migration MIX :",
                mix_migration["mixes"],
                "MIX migrés,",
                mix_migration["channels"],
                "canaux reconstruits,",
                mix_migration["instruments"],
                "instruments conservés."
            )

        if song_migration["songs"] > 0:

            print(
                "Migration SONG :",
                song_migration["songs"],
                "SONG migrées,",
                song_migration["channels"],
                "canaux migrés,",
                song_migration["programs"],
                "PROGRAM créés,",
                song_migration["instruments"],
                "instruments conservés."
            )

        if migration_needed:

            if not self.save_safe(
                allowed_errors=allowed_errors
            ):

                raise RuntimeError(
                    "Impossible de sauvegarder "
                    "la migration du projet."
                )

    def _validate_format_version(
        self
    ):

        if not isinstance(
            self.data,
            dict
        ):

            raise RuntimeError(
                "Structure racine de fusion.json invalide."
            )

        format_version = self.data.get(
            "format_version"
        )

        if format_version is None:

            raise RuntimeError(
                "format_version absent dans fusion.json."
            )

        if type(format_version) is not int:

            raise RuntimeError(
                "format_version invalide dans fusion.json."
            )

        if format_version > PROJECT_FORMAT_VERSION:

            raise RuntimeError(
                f"Format fusion.json {format_version} "
                f"plus récent que le format supporté "
                f"({PROJECT_FORMAT_VERSION})."
            )

        if format_version < PROJECT_FORMAT_VERSION:

            raise RuntimeError(
                f"Format fusion.json {format_version} "
                f"plus ancien que le format supporté "
                f"({PROJECT_FORMAT_VERSION})."
            )

    def _validate_root_structure(
        self
    ):

        required_sections = (
            "banks",
            "instruments",
            "mixes",
            "programs",
            "songs"
        )

        for section in required_sections:

            if section not in self.data:

                raise RuntimeError(
                    f"Section {section} absente "
                    "dans fusion.json."
                )

            if not isinstance(
                self.data[section],
                dict
            ):

                raise RuntimeError(
                    f"Section {section} invalide "
                    "dans fusion.json."
                )

        allowed_sections = {
            "format_version",
            "banks",
            "instruments",
            "mixes",
            "programs",
            "songs"
        }

        unknown_sections = (
            set(self.data)
            - allowed_sections
        )

        for section in sorted(
            unknown_sections
        ):

            raise RuntimeError(
                f"Section {section} inconnue "
                "dans fusion.json."
            )

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

        temp_file = (
            FUSION_FILE
            + ".restore.tmp"
        )

        try:

            #
            # Travailler sur une copie :
            # load() peut effectuer des migrations.
            #
            shutil.copy2(
                backup,
                temp_file
            )

            candidate = cls(
                filename=temp_file
            )

            errors = candidate.validate()

            if errors:

                project._log_recovery(
                    "RESTORE_FAILED "
                    + backup
                )

                return None

            #
            # Le candidat est complètement chargé,
            # migré et validé.
            #
            os.replace(
                temp_file,
                FUSION_FILE
            )

            candidate.filename = (
                FUSION_FILE
            )

            candidate.file_time = (
                os.path.getmtime(
                    FUSION_FILE
                )
            )

            candidate._log_recovery(
                "RESTORE_VALIDATED "
                + backup
            )

            return candidate

        except Exception:

            project._log_recovery(
                "RESTORE_FAILED "
                + backup
            )

            return None

        finally:

            if os.path.exists(
                temp_file
            ):

                os.remove(
                    temp_file
                )

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

            stat = os.stat(
                filename
            )

            backups.append(
                {
                    "filename": filename,
                    "size": cls._format_size(
                        stat.st_size
                    ),
                    "time": cls._format_time(
                        stat.st_mtime
                    )
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

    @staticmethod
    def _format_size(
        size
    ):

        if size < 1024:

            return f"{size} octets"

        if size < 1024 * 1024:

            return f"{size // 1024} Ko"

        return (
            f"{size / (1024 * 1024):.1f} Mo"
        )

    @staticmethod
    def _format_time(
        timestamp
    ):

        return time.strftime(
            "%d-%m-%Y %H:%M:%S",
            time.localtime(
                timestamp
            )
        )

    def get_blocking_errors(
        self,
        errors
    ):

        return list(
            errors
        )

    def get_new_blocking_errors(
        self,
        before_errors
    ):

        after_errors = self.get_blocking_errors(
            self.validate()
        )

        return [
            error
            for error in after_errors
            if error not in before_errors
        ]

    def save_safe(
        self,
        allowed_errors
    ):

        errors = self.validate()

        blocking_errors = self.get_blocking_errors(
            errors
        )

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

        temp_file = self.filename + ".tmp"
        old_file = self.filename + ".old"

        try:

            #
            # Préparer complètement le nouveau fichier
            #
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

            #
            # Conserver l'ancienne version
            #
            if os.path.exists(
                self.filename
            ):

                shutil.copy2(
                    self.filename,
                    old_file
                )

            #
            # Installer le nouveau fichier
            #
            os.replace(
                temp_file,
                self.filename
            )

            self.file_time = os.path.getmtime(
                self.filename
            )

        except Exception as e:

            print(
                f"Sauvegarde impossible : {e}"
            )

            if os.path.exists(
                temp_file
            ):

                os.remove(
                    temp_file
                )

            if os.path.exists(
                old_file
            ):

                os.remove(
                    old_file
                )

            return False

        #
        # À partir d'ici, fusion.json est sauvegardé.
        # Un problème de backup ne doit donc plus
        # faire retourner False.
        #
        try:

            if os.path.exists(
                old_file
            ):

                self._rotate_backups(
                    old_file
                )

        except Exception as e:

            print(
                "⚠ Sauvegarde effectuée, "
                "mais rotation des backups impossible :",
                e
            )

        finally:

            #
            # old_file peut encore exister si
            # la rotation a échoué.
            #
            if os.path.exists(
                old_file
            ):

                os.remove(
                    old_file
                )

        return True

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

                if not cls._archive_is_valid(
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
    def _archive_is_valid(
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

            if not isinstance(
                data,
                dict
            ):

                return False

            return True

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

        temp_file = (
            FUSION_FILE
            + ".restore.tmp"
        )

        try:

            #
            # Travailler sur une copie :
            # load() peut effectuer des migrations.
            #
            shutil.copy2(
                archive,
                temp_file
            )

            candidate = cls(
                filename=temp_file
            )

            errors = candidate.validate()

            if errors:

                return None

            #
            # Le candidat est maintenant chargé,
            # migré et valide.
            #
            # Protéger le projet actif avant
            # de le remplacer.
            #
            if os.path.exists(
                FUSION_FILE
            ):

                project.archive_if_changed()

            #
            # Installation atomique.
            #
            os.replace(
                temp_file,
                FUSION_FILE
            )

            candidate.filename = (
                FUSION_FILE
            )

            candidate.file_time = (
                os.path.getmtime(
                    FUSION_FILE
                )
            )

            return candidate

        except Exception:

            return None

        finally:

            if os.path.exists(
                temp_file
            ):

                os.remove(
                    temp_file
                )

    def _rotate_backups(
        self,
        old_file
    ):

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

        os.replace(
            old_file,
            backup
        )

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

        original_data = self.snapshot()
        original_file_time = self.file_time

        try:

            self.load()

        except (
            ProjectRecoveryError,
            RuntimeError
        ):

            self.restore_snapshot(
                original_data
            )

            self.file_time = original_file_time

            return False

        return True

    def _log_recovery(self, message):

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

    def snapshot(
        self
    ):

        return copy.deepcopy(
            self.data
        )

    def restore_snapshot(
        self,
        snapshot
    ):

        self.data = snapshot

    #
    # Accès BANK
    #
    def get_program_bank_name(
        self,
        bank
    ):

        name = (
            self.data.get(
                "banks",
                {}
            )
            .get(
                "program",
                {}
            )
            .get(
                str(bank)
            )
        )

        if name is not None:

            return name

        return fusion_program_bank_name(
            bank
        )

    def get_mix_bank_name(
        self,
        bank
    ):

        name = (
            self.data.get(
                "banks",
                {}
            )
            .get(
                "mix",
                {}
            )
            .get(
                str(bank)
            )
        )

        if name is not None:

            return name

        return fusion_mix_bank_name(
            bank
        )

    def get_program_banks(
        self
    ):

        banks = set(
            FUSION_PROGRAM_BANK_NAMES
        )

        banks.update(
            int(bank)
            for bank in self.data[
                "banks"
            ][
                "program"
            ]
        )

        return sorted(
            banks
        )

    def get_mix_banks(
        self
    ):

        banks = set(
            FUSION_MIX_BANK_NAMES
        )

        banks.update(
            int(bank)
            for bank in self.data[
                "banks"
            ][
                "mix"
            ]
        )

        return sorted(
            banks
        )

    def get_banks(
        self,
        bank_type
    ):

        if bank_type == "program":

            return self.get_program_banks()

        if bank_type == "mix":

            return self.get_mix_banks()

        raise ValueError(
            f"Type de banque invalide : {bank_type}"
        )

    def get_bank_name(
        self,
        bank_type,
        bank
    ):

        if bank_type == "program":

            return self.get_program_bank_name(
                bank
            )

        if bank_type == "mix":

            return self.get_mix_bank_name(
                bank
            )

        raise ValueError(
            f"Type de banque invalide : {bank_type}"
        )

    def set_bank_name(
        self,
        bank_type,
        bank,
        name
    ):

        if bank_type not in (
            "program",
            "mix"
        ):

            return (
                False,
                [
                    (
                        "Type de banque invalide : "
                        f"{bank_type}"
                    )
                ]
            )

        if isinstance(
            bank,
            bool
        ):

            return (
                False,
                [
                    "Banque invalide."
                ]
            )

        try:

            bank_number = int(
                bank
            )

        except (
            TypeError,
            ValueError
        ):

            return (
                False,
                [
                    "Banque invalide."
                ]
            )

        if (
            not 0 <= bank_number <= 127
            or
            (
                isinstance(
                    bank,
                    str
                )
                and
                str(bank_number) != bank
            )
        ):

            return (
                False,
                [
                    "Banque invalide."
                ]
            )

        bank = bank_number
        banks = self.data[
            "banks"
        ][
            bank_type
        ]

        bank_id = str(
            bank
        )

        old_name = banks.get(
            bank_id
        )

        if name is not None:

            name = name.strip()

            if not name:

                return (
                    False,
                    [
                        "Nom de banque invalide."
                    ]
                )

        before_errors = self.get_blocking_errors(
            self.validate()
        )

        if name is None:

            banks.pop(
                bank_id,
                None
            )

        else:

            banks[
                bank_id
            ] = name

        new_errors = self.get_new_blocking_errors(
            before_errors
        )

        if new_errors:

            if old_name is None:

                banks.pop(
                    bank_id,
                    None
                )

            else:

                banks[
                    bank_id
                ] = old_name

            return (
                False,
                new_errors
            )

        return (
            True,
            []
        )

    def get_custom_bank_name(
        self,
        bank_type,
        bank
    ):

        if bank_type not in (
            "program",
            "mix"
        ):

            raise ValueError(
                f"Type de banque invalide : {bank_type}"
            )

        return (
            self.data[
                "banks"
            ][
                bank_type
            ].get(
                str(bank)
            )
        )

    #
    # Accès Mix
    #
    def get_mixes(self):

        return self.data[
            "mixes"
        ]

    def get_mix(
        self,
        mix_id
    ):

        return self.get_mixes().get(
            mix_id
        )

    def _migrate_legacy_mixes(
        self
    ):

        mixes = self.get_mixes()

        replacements = {}

        migrated_count = 0
        channel_count = 0
        instrument_count = 0

        for mix_id, mix in mixes.items():

            #
            # Structure invalide :
            # laisser validate() la signaler.
            #
            if not isinstance(
                mix,
                dict
            ):

                continue

            #
            # Nouveau format :
            # rien à migrer.
            #
            if "channels" in mix:

                continue

            #
            # Ce n'est pas un ancien MIX connu.
            #
            if "parts" not in mix:

                continue

            parts = mix.get(
                "parts",
                {}
            )

            channels = {}

            for part_id, part in parts.items():

                midi_channel = part.get(
                    "midi_channel"
                )

                if midi_channel is None:

                    raise ValueError(
                        f"{mix_id} PART {part_id} : "
                        "midi_channel absent."
                    )

                try:

                    midi_channel = int(
                        midi_channel
                    )

                except (
                    TypeError,
                    ValueError
                ):

                    raise ValueError(
                        f"{mix_id} PART {part_id} : "
                        "midi_channel invalide."
                    )

                if not 1 <= midi_channel <= 16:

                    raise ValueError(
                        f"{mix_id} PART {part_id} : "
                        f"canal MIDI {midi_channel} invalide."
                    )

                channel_id = str(
                    midi_channel
                )

                if channel_id in channels:

                    raise ValueError(
                        f"{mix_id} : plusieurs PARTs "
                        f"utilisent le canal MIDI "
                        f"{midi_channel}."
                    )

                channel = {}

                instrument = part.get(
                    "instrument"
                )

                if instrument:

                    channel[
                        "instrument"
                    ] = instrument

                    instrument_count += 1

                channels[
                    channel_id
                ] = channel

                channel_count += 1

            replacements[
                mix_id
            ] = channels

            migrated_count += 1

        #
        # Appliquer seulement lorsque toute
        # la migration a pu être préparée.
        #
        for mix_id, channels in replacements.items():

            mix = mixes[
                mix_id
            ]

            mix[
                "channels"
            ] = channels

            mix.pop(
                "parts",
                None
            )

        return {
            "mixes": migrated_count,
            "channels": channel_count,
            "instruments": instrument_count
        }

    def rename_mix(
        self,
        mix_id,
        name
    ):

        mix = self.get_mix(
            mix_id
        )

        if mix is None:

            return (
                False,
                [
                    f"Mix inconnu : {mix_id}"
                ]
            )

        old_name = mix.get(
            "name"
        )

        before_errors = self.get_blocking_errors(
            self.validate()
        )

        mix["name"] = name

        new_errors = self.get_new_blocking_errors(
            before_errors
        )

        if new_errors:

            if old_name is None:

                mix.pop(
                    "name",
                    None
                )

            else:

                mix["name"] = old_name

            return (
                False,
                new_errors
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

        if source is None:

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

        source_name = source.get(
            "name"
        )

        if (
            not isinstance(
                source_name,
                str
            )
            or
            not source_name.strip()
        ):

            return (
                False,
                [
                    f"Mix source invalide : {source_mix_id}"
                ]
            )

        new_mix = copy.deepcopy(
            source
        )

        new_mix["name"] = self._make_copy_name(
            source_name
        )

        before_errors = self.get_blocking_errors(
            self.validate()
        )

        mixes[new_mix_id] = new_mix

        new_errors = self.get_new_blocking_errors(
            before_errors
        )

        if new_errors:

            mixes.pop(
                new_mix_id,
                None
            )

            return (
                False,
                new_errors
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
                isinstance(
                    mix,
                    dict
                )
                and
                mix.get(
                    "name"
                ) == candidate
                for mix in self.get_mixes().values()
            ):

                return candidate

        index = 2

        while True:

            candidate = (
                f"{name} (copie {index})"
            )

            if not any(
                isinstance(
                    mix,
                    dict
                )
                and
                mix.get(
                    "name"
                ) == candidate
                for mix in self.get_mixes().values()
            ):

                return candidate

            index += 1

    def delete_empty_mixes(
        self
    ):

        mixes = self.get_mixes()

        before_errors = self.get_blocking_errors(
            self.validate()
        )

        backup = copy.deepcopy(
            self.data
        )

        removed = []

        for mix_id, mix in list(
            self.iter_mixes()
        ):

            if not isinstance(
                mix,
                dict
            ):

                continue

            channels = mix.get(
                "channels"
            )

            if (
                isinstance(
                    channels,
                    dict
                )
                and
                not channels
            ):

                removed.append(
                    mix_id
                )

                del mixes[
                    mix_id
                ]

        new_errors = self.get_new_blocking_errors(
            before_errors
        )

        if new_errors:

            self.data = backup

            return (
                False,
                new_errors
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

        if mix_id not in mixes:

            return (
                False,
                [
                    "Mix inconnu"
                ]
            )

        before_errors = self.get_blocking_errors(
            self.validate()
        )

        backup = copy.deepcopy(
            self.data
        )

        del mixes[
            mix_id
        ]

        new_errors = self.get_new_blocking_errors(
            before_errors
        )

        if new_errors:

            self.data = backup

            return (
                False,
                new_errors
            )

        return (
            True,
            []
        )

    def iter_mixes(self):

        mixes = self.get_mixes()

        for mix_id in self.sort_performance_ids(
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

    @staticmethod
    def sort_performance_ids(
        data
    ):

        def sort_key(
            performance_id
        ):

            try:

                bank, program = (
                    performance_id.split(
                        ":"
                    )
                )

                return (
                    0,
                    int(bank),
                    int(program)
                )

            except (
                AttributeError,
                TypeError,
                ValueError
            ):

                return (
                    1,
                    str(performance_id)
                )

        return sorted(
            data.keys(),
            key=sort_key
        )

    def _validate_instrument(
        self,
        instrument_id
    ):

        errors = []

        instrument = self.get_instrument(
            instrument_id
        )

        prefix = f"Instrument {instrument_id}"

        if (
            not isinstance(
                instrument_id,
                str
            )
            or
            not re.fullmatch(
                r"[a-z0-9]+(?:_[a-z0-9]+)*",
                instrument_id
            )
        ):

            errors.append(
                f"{prefix} : identifiant invalide"
            )

        if not isinstance(
            instrument,
            dict
        ):

            errors.append(
                f"{prefix} : définition invalide"
            )

            return errors

        allowed_fields = {
            "name",
            "sf2_bank",
            "sf2_program"
        }

        unknown_fields = (
            set(instrument)
            - allowed_fields
        )

        for field in sorted(
            unknown_fields
        ):

            errors.append(
                f"{prefix} : champ inconnu {field}"
            )

        name = instrument.get(
            "name"
        )

        if name is None:

            errors.append(
                f"{prefix} : nom absent"
            )

        elif (
            not isinstance(
                name,
                str
            )
            or
            not name.strip()
        ):

            errors.append(
                f"{prefix} : nom invalide"
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

            sf2_bank = instrument[
                "sf2_bank"
            ]

            if (
                type(sf2_bank) is not int
                or
                not 0 <= sf2_bank <= 16383
            ):

                errors.append(
                    f"{prefix} : sf2_bank invalide"
                )

        if "sf2_program" in instrument:

            sf2_program = instrument[
                "sf2_program"
            ]

            if (
                type(sf2_program) is not int
                or
                not 0 <= sf2_program <= 127
            ):

                errors.append(
                    f"{prefix} : sf2_program invalide"
                )

        return errors

    def _validate_instruments(self):

        errors = []

        for instrument_id in self.get_instruments():

            errors.extend(
                self._validate_instrument(
                    instrument_id
                )
            )

        return errors

    def validate_mix(
        self,
        mix_id
    ):

        mix = self.get_mix(
            mix_id
        )

        if mix is None:

            return [
                f"Mix inconnu : {mix_id}"
            ]

        return self._validate_mix_data(
            mix_id,
            mix
        )

    def _validate_mix_data(
        self,
        mix_id,
        mix
    ):

        errors = []

        try:

            bank_text, program_text = (
                mix_id.split(
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

            if (
                str(bank) != bank_text
                or
                str(program) != program_text
            ):

                errors.append(
                    f"MIX {mix_id} : identifiant invalide."
                )

        except (
            ValueError,
            AttributeError
        ):

            errors.append(
                f"MIX {mix_id} : identifiant invalide."
            )

        else:

            if not (
                0 <= bank <= 127
                and
                0 <= program <= 127
            ):

                errors.append(
                    f"MIX {mix_id} : identifiant hors limites."
                )

        if not isinstance(
            mix,
            dict
        ):

            errors.append(
                f"{mix_id} : définition invalide."
            )

            return errors

        #
        # Champs autorisés
        #
        allowed_fields = {
            "name",
            "channels"
        }

        for field in mix:

            if field not in allowed_fields:

                errors.append(
                    f"{mix_id} : champ inconnu '{field}'."
                )

        name = mix.get(
            "name"
        )

        if name is None:

            errors.append(
                f"{mix_id} : nom absent."
            )

        elif (
            not isinstance(
                name,
                str
            )
            or
            not name.strip()
        ):

            errors.append(
                f"{mix_id} : nom invalide."
            )

        if "channels" not in mix:

            errors.append(
                f"{mix_id} : channels absent."
            )

            return errors

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
                self._validate_mix_channel_data(
                    mix_id,
                    channel_id,
                    channel
                )
            )

        return errors

    def _validate_mix_channel_data(
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

        else:

            if str(midi_channel) != channel_id:

                errors.append(
                    f"{prefix} : canal MIDI invalide."
                )

            elif not 1 <= midi_channel <= 16:

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
        # Champs autorisés
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

                    if (
                        str(bank) != bank_text
                        or
                        str(program) != program_text
                    ):

                        errors.append(
                            f"{prefix} : PROGRAM invalide ({program_id})."
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
                        0 <= bank <= 127
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
                        0 <= bank <= 127
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

    def _validate_part_data(
        self,
        program_id,
        part_id,
        part
    ):

        errors = []

        if not isinstance(
            part,
            dict
        ):

            errors.append(
                f"{program_id} : définition invalide."
            )

            return errors

        prefix = f"{program_id} PART {part_id}"

        #
        # Champs autorisés
        #
        allowed_fields = {
            "bank",
            "program",
            "midi_channel",
            "instrument",
            "note_min",
            "note_max",
            "velocity_min",
            "velocity_max"
        }

        for field in part:

            if field not in allowed_fields:

                errors.append(
                    f"{prefix} : champ inconnu '{field}'."
                )

        #
        # Canal MIDI
        #
        if "midi_channel" not in part:

            errors.append(
                f"{prefix} : midi_channel absent."
            )

        else:

            midi_channel = part[
                "midi_channel"
            ]

            if (
                type(midi_channel) is not int
                or
                not 1 <= midi_channel <= 16
            ):

                errors.append(
                    f"{prefix} : canal MIDI invalide."
                )

        #
        # Bank Fusion
        #
        if "bank" not in part:

            errors.append(
                f"{prefix} : bank Fusion absente."
            )

        else:

            bank = part[
                "bank"
            ]

            if (
                type(bank) is not int
                or
                not 0 <= bank <= 127
            ):

                errors.append(
                    f"{prefix} : bank Fusion invalide."
                )

        #
        # Program Fusion
        #
        if "program" not in part:

            errors.append(
                f"{prefix} : program Fusion absent."
            )

        else:

            program = part[
                "program"
            ]

            if (
                type(program) is not int
                or
                not 0 <= program <= 127
            ):

                errors.append(
                    f"{prefix} : program Fusion invalide."
                )

        #
        # Instrument global optionnel
        #
        instrument_id = part.get(
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

        #
        # Zone de notes
        #
        has_note_min = (
            "note_min" in part
        )

        has_note_max = (
            "note_max" in part
        )

        if (
            has_note_min
            != has_note_max
        ):

            errors.append(
                f"{prefix} : zone de notes incomplète."
            )

        elif has_note_min:

            note_min = part[
                "note_min"
            ]

            note_max = part[
                "note_max"
            ]

            if (
                type(note_min) is not int
                or
                type(note_max) is not int
                or
                not 0 <= note_min <= note_max <= 127
            ):

                errors.append(
                    f"{prefix} : zone de notes invalide."
                )

        #
        # Plage de vélocité
        #
        has_velocity_min = (
            "velocity_min" in part
        )

        has_velocity_max = (
            "velocity_max" in part
        )

        if (
            has_velocity_min
            != has_velocity_max
        ):

            errors.append(
                f"{prefix} : plage de vélocité incomplète."
            )

        elif has_velocity_min:

            velocity_min = part[
                "velocity_min"
            ]

            velocity_max = part[
                "velocity_max"
            ]

            if (
                type(velocity_min) is not int
                or
                type(velocity_max) is not int
                or
                not 0 <= velocity_min <= velocity_max <= 127
            ):

                errors.append(
                    f"{prefix} : plage de vélocité invalide."
                )

        return errors

    def is_instrument_soundfont_ready(
        self,
        instrument
    ):

        if not isinstance(
            instrument,
            dict
        ):

            return False

        sf2_bank = instrument.get(
            "sf2_bank"
        )

        sf2_program = instrument.get(
            "sf2_program"
        )

        if (
            type(sf2_bank) is not int
            or
            not 0 <= sf2_bank <= 16383
        ):

            return False

        if (
            type(sf2_program) is not int
            or
            not 0 <= sf2_program <= 127
        ):

            return False

        return True

    def is_soundfont_ready(
        self,
        part
    ):

        if not isinstance(
            part,
            dict
        ):

            return False

        midi_channel = part.get(
            "midi_channel"
        )

        if (
            type(midi_channel) is not int
            or
            not 1 <= midi_channel <= 16
        ):

            return False

        instrument = self.resolve_part_instrument(
            part
        )

        return self.is_instrument_soundfont_ready(
            instrument
        )

    def resolve_mix_channel_instrument(
        self,
        channel
    ):

        if not isinstance(
            channel,
            dict
        ):

            return None

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

        return self.data[
            "programs"
        ]

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

        if program is None:

            return (
                False,
                [
                    f"PROGRAM inconnu : {program_id}"
                ]
            )

        if not isinstance(
            program,
            dict
        ):

            return (
                False,
                [
                    f"PROGRAM invalide : {program_id}"
                ]
            )

        before_errors = self.get_blocking_errors(
            self.validate()
        )

        old_name = program.get(
            "name"
        )

        program["name"] = name

        new_errors = self.get_new_blocking_errors(
            before_errors
        )

        if new_errors:

            if old_name is None:

                program.pop(
                    "name",
                    None
                )

            else:

                program["name"] = old_name

            return (
                False,
                new_errors
            )

        return (
            True,
            []
        )

    def delete_program(
        self,
        program_id
    ):

        programs = self.get_programs()

        if program_id not in programs:

            return (
                False,
                [
                    "PROGRAM inconnu"
                ]
            )

        before_errors = self.get_blocking_errors(
            self.validate()
        )

        backup = copy.deepcopy(
            self.data
        )

        del programs[
            program_id
        ]

        new_errors = self.get_new_blocking_errors(
            before_errors
        )

        if new_errors:

            self.data = backup

            return (
                False,
                new_errors
            )

        return (
            True,
            []
        )

    def _ensure_program(
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

    def update_program_part(
        self,
        program_id,
        part_id,
        updates
    ):

        if not isinstance(
            updates,
            dict
        ):

            return (
                False,
                [
                    f"{program_id} PART {part_id} : modifications invalides."
                ]
            )

        before_errors = self.get_blocking_errors(
            self.validate()
        )

        backup = copy.deepcopy(
            self.data
        )

        program = self._ensure_program(
            program_id
        )

        if not isinstance(
            program,
            dict
        ):

            self.data = backup

            return (
                False,
                [
                    f"{program_id} : définition invalide."
                ]
            )

        parts = program.get(
            "parts"
        )

        if not isinstance(
            parts,
            dict
        ):

            self.data = backup

            return (
                False,
                [
                    f"{program_id} : définition PART invalide."
                ]
            )

        part_id = str(
            part_id
        )

        part = parts.setdefault(
            part_id,
            {}
        )

        if not isinstance(
            part,
            dict
        ):

            self.data = backup

            return (
                False,
                [
                    f"{program_id} PART {part_id} : définition invalide."
                ]
            )

        part.update(
            updates
        )

        new_errors = self.get_new_blocking_errors(
            before_errors
        )

        if new_errors:

            self.data = backup

            return (
                False,
                new_errors
            )

        return (
            True,
            []
        )

    def iter_programs(self):

        programs = self.get_programs()

        for program_id in self.sort_performance_ids(
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

        if program is None:

            return [
                f"PROGRAM inconnu : {program_id}"
            ]

        return self._validate_program_data(
            program_id,
            program
        )

    def _validate_program_data(
        self,
        program_id,
        program
    ):

        errors = []

        if not isinstance(
            program,
            dict
        ):

            errors.append(
                f"{program_id} : définition invalide."
            )

            return errors

        program_id_valid = True

        try:

            bank_text, program_text = (
                program_id.split(
                    ":",
                    1
                )
            )

            expected_bank = int(
                bank_text
            )

            expected_program = int(
                program_text
            )

        except (
            AttributeError,
            ValueError
        ):

            program_id_valid = False

        else:

            if (
                str(expected_bank) != bank_text
                or
                str(expected_program) != program_text
                or
                not 0 <= expected_bank <= 127
                or
                not 0 <= expected_program <= 127
            ):

                program_id_valid = False

        if not program_id_valid:

            errors.append(
                f"PROGRAM {program_id} : identifiant invalide."
            )

        #
        # Champs autorisés
        #
        allowed_fields = {
            "name",
            "parts"
        }

        for field in program:

            if field not in allowed_fields:

                errors.append(
                    f"{program_id} : champ inconnu '{field}'."
                )

        #
        # Nom
        #
        name = program.get(
            "name"
        )

        if name is None:

            errors.append(
                f"{program_id} : nom absent."
            )

        elif (
            not isinstance(
                name,
                str
            )
            or
            not name.strip()
        ):

            errors.append(
                f"{program_id} : nom invalide."
            )

        if "parts" not in program:

            errors.append(
                f"{program_id} : parts absent."
            )

            return errors

        parts = program.get(
            "parts"
        )

        if not isinstance(
            parts,
            dict
        ):

            errors.append(
                f"{program_id} : parts invalide."
            )

            return errors


        if "1" not in parts:

            errors.append(
                f"{program_id} : PART 1 absente."
            )

            return errors

        for part_id in parts:

            if part_id != "1":

                errors.append(
                    f"{program_id} : PART {part_id} invalide."
                )

        part = parts["1"]

        if not isinstance(
            part,
            dict
        ):

            errors.append(
                f"{program_id} PART 1 : définition invalide."
            )

            return errors

        errors.extend(
            self._validate_part_data(
                program_id,
                "1",
                part
            )
        )

        if program_id_valid:

            if (
                type(part.get("bank")) is int
                and
                0 <= part["bank"] <= 127
                and
                part["bank"] != expected_bank
            ):

                errors.append(
                    f"{program_id} PART 1 : "
                    f"bank Fusion incohérente avec l'identifiant."
                )

            if (
                type(part.get("program")) is int
                and
                0 <= part["program"] <= 127
                and
                part["program"] != expected_program
            ):

                errors.append(
                    f"{program_id} PART 1 : "
                    f"program Fusion incohérent avec l'identifiant."
                )

        return errors

    #
    # Accès Song
    #
    def get_songs(self):

        return self.data[
            "songs"
        ]

    def get_song(
        self,
        song_id
    ):

        return self.get_songs().get(
            str(song_id)
        )

    def _migrate_legacy_songs(
        self
    ):

        migrated_songs = 0
        migrated_channels = 0
        migrated_programs = 0
        preserved_instruments = 0

        songs = self.data.get(
            "songs",
            {}
        )

        #
        # Préparer toute la migration avant
        # de modifier self.data
        #
        migrated_data = {}

        for song_id, song in songs.items():

            if not isinstance(
                song,
                dict
            ):

                continue

            channels = song.get(
                "channels",
                {}
            )

            if not isinstance(
                channels,
                dict
            ):

                continue

            new_channels = {}
            song_changed = False

            for channel_id, channel in channels.items():

                #
                # Structure invalide :
                # laisser validate() la signaler.
                #
                if not isinstance(
                    channel,
                    dict
                ):

                    new_channels[
                        channel_id
                    ] = channel

                    continue

                #
                # Déjà au format v2.9+
                #
                if "programs" in channel:

                    new_channels[
                        channel_id
                    ] = channel

                    continue

                #
                # Champs reconnus dans l'ancien format
                #
                legacy_fields = {
                    "bank",
                    "program",
                    "volume",
                    "pan",
                    "expression",
                    "reverb",
                    "chorus",
                    "instrument"
                }

                unknown_fields = (
                    set(channel)
                    - legacy_fields
                )

                #
                # Structure inconnue :
                # ne pas la transformer silencieusement.
                #
                if unknown_fields:

                    new_channels[
                        channel_id
                    ] = channel

                    continue

                new_channel = {}

                #
                # Conserver les paramètres statiques
                #
                for field in (
                    "volume",
                    "pan",
                    "expression",
                    "reverb",
                    "chorus"
                ):

                    if field in channel:

                        new_channel[
                            field
                        ] = channel[
                            field
                        ]

                has_bank = (
                    "bank" in channel
                )

                has_program = (
                    "program" in channel
                )

                #
                # Format ancien incohérent :
                # ne rien inventer.
                #
                if has_bank != has_program:

                    raise ValueError(
                        f"{song_id} CH {channel_id} : "
                        "bank/program incomplets."
                    )

                programs = {}

                if has_bank:

                    bank = channel[
                        "bank"
                    ]

                    program = channel[
                        "program"
                    ]

                    program_id = (
                        f"{bank}:{program}"
                    )

                    program_data = {}

                    #
                    # Instrument local = override
                    #
                    if "instrument" in channel:

                        program_data[
                            "instrument"
                        ] = channel[
                            "instrument"
                        ]

                        preserved_instruments += 1

                    programs[
                        program_id
                    ] = program_data

                    migrated_programs += 1

                new_channel[
                    "programs"
                ] = programs

                new_channels[
                    channel_id
                ] = new_channel

                migrated_channels += 1
                song_changed = True

            if song_changed:

                new_song = dict(
                    song
                )

                new_song[
                    "channels"
                ] = new_channels

                migrated_data[
                    song_id
                ] = new_song

                migrated_songs += 1

        #
        # Appliquer seulement une fois toute
        # la migration préparée avec succès
        #
        for song_id, song in migrated_data.items():

            songs[
                song_id
            ] = song

        return {
            "songs": migrated_songs,
            "channels": migrated_channels,
            "programs": migrated_programs,
            "instruments": preserved_instruments
        }

    def rename_song(
        self,
        song_id,
        name
    ):

        song = self.get_song(
            song_id
        )

        if song is None:

            return (
                False,
                [
                    f"SONG inconnue : {song_id}"
                ]
            )

        if not isinstance(
            song,
            dict
        ):

            return (
                False,
                [
                    f"SONG invalide : {song_id}"
                ]
            )

        old_name = song.get(
            "name"
        )

        backup = copy.deepcopy(
            song
        )

        before_errors = self.get_blocking_errors(
            self.validate()
        )

        song["name"] = name

        new_errors = self.get_new_blocking_errors(
            before_errors
        )

        if new_errors:

            song.clear()
            song.update(
                backup
            )

            return (
                False,
                new_errors
            )

        return (
            True,
            []
        )

    def delete_song(
        self,
        song_id
    ):

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

        del songs[
            song_id
        ]

        return (
            True,
            []
        )

    def _ensure_song(
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

    def replace_song_channels(
        self,
        song_id,
        channels
    ):

        song = self.get_song(
            song_id
        )

        if song is None:

            return (
                False,
                [
                    f"SONG inconnue : {song_id}"
                ]
            )

        if not isinstance(
            song,
            dict
        ):

            return (
                False,
                [
                    f"SONG invalide : {song_id}"
                ]
            )

        before_errors = self.get_blocking_errors(
            self.validate()
        )

        backup = copy.deepcopy(
            self.data
        )

        song["channels"] = channels

        new_errors = self.get_new_blocking_errors(
            before_errors
        )

        if new_errors:

            self.data = backup

            return (
                False,
                new_errors
            )

        return (
            True,
            []
        )

    def update_song_channel(
        self,
        song_id,
        channel_id,
        updates=None,
        remove_fields=None
    ):

        song = self.get_song(
            song_id
        )

        if song is None:

            return (
                False,
                [
                    f"SONG inconnue : {song_id}"
                ]
            )

        if not isinstance(
            song,
            dict
        ):

            return (
                False,
                [
                    f"SONG invalide : {song_id}"
                ]
            )

        if (
            updates is not None
            and
            not isinstance(
                updates,
                dict
            )
        ):

            return (
                False,
                [
                    f"{song_id} CH {channel_id} : modifications invalides."
                ]
            )

        channels = song.get(
            "channels"
        )

        if not isinstance(
            channels,
            dict
        ):

            return (
                False,
                [
                    f"{song_id} : définition channels invalide."
                ]
            )

        channel_id = str(
            channel_id
        )

        channel = channels.get(
            channel_id
        )

        if not isinstance(
            channel,
            dict
        ):

            return (
                False,
                [
                    f"{song_id} CH {channel_id} : canal inconnu."
                ]
            )

        before_errors = self.get_blocking_errors(
            self.validate()
        )

        old_song = copy.deepcopy(
            song
        )

        if updates:

            channel.update(
                updates
            )

        if remove_fields:

            for field in remove_fields:

                channel.pop(
                    field,
                    None
                )

        new_errors = self.get_new_blocking_errors(
            before_errors
        )

        if new_errors:

            song.clear()

            song.update(
                old_song
            )

            return (
                False,
                new_errors
            )

        return (
            True,
            []
        )

    def update_song_program(
        self,
        song_id,
        channel_id,
        program_id,
        updates=None,
        remove_fields=None
    ):

        song = self.get_song(
            song_id
        )

        if song is None:

            return (
                False,
                [
                    f"SONG inconnue : {song_id}"
                ]
            )

        if not isinstance(
            song,
            dict
        ):

            return (
                False,
                [
                    f"SONG invalide : {song_id}"
                ]
            )

        if (
            updates is not None
            and
            not isinstance(
                updates,
                dict
            )
        ):

            return (
                False,
                [
                    f"{song_id} CH {channel_id} "
                    f"PROGRAM {program_id} : modifications invalides."
                ]
            )

        channels = song.get(
            "channels"
        )

        if not isinstance(
            channels,
            dict
        ):

            return (
                False,
                [
                    f"{song_id} : définition channels invalide."
                ]
            )

        channel_id = str(
            channel_id
        )

        channel = channels.get(
            channel_id
        )

        if not isinstance(
            channel,
            dict
        ):

            return (
                False,
                [
                    f"{song_id} CH {channel_id} : canal inconnu."
                ]
            )

        programs = channel.get(
            "programs"
        )

        if not isinstance(
            programs,
            dict
        ):

            return (
                False,
                [
                    f"{song_id} CH {channel_id} : "
                    "définition PROGRAMs invalide."
                ]
            )

        program = programs.get(
            program_id
        )

        if not isinstance(
            program,
            dict
        ):

            return (
                False,
                [
                    f"{song_id} CH {channel_id} : "
                    f"PROGRAM {program_id} inconnu."
                ]
            )

        before_errors = self.get_blocking_errors(
            self.validate()
        )

        old_song = copy.deepcopy(
            song
        )

        if updates:

            program.update(
                updates
            )

        if remove_fields:

            for field in remove_fields:

                program.pop(
                    field,
                    None
                )

        new_errors = self.get_new_blocking_errors(
            before_errors
        )

        if new_errors:

            song.clear()

            song.update(
                old_song
            )

            return (
                False,
                new_errors
            )

        return (
            True,
            []
        )

    def move_song_channel(
        self,
        song_id,
        old_channel_id,
        new_channel_id
    ):

        song = self.get_song(
            song_id
        )

        if song is None:

            return (
                False,
                [
                    f"SONG inconnue : {song_id}"
                ]
            )

        if not isinstance(
            song,
            dict
        ):

            return (
                False,
                [
                    f"SONG invalide : {song_id}"
                ]
            )


        channels = song.get(
            "channels"
        )

        if not isinstance(
            channels,
            dict
        ):

            return (
                False,
                [
                    f"{song_id} : définition channels invalide."
                ]
            )

        old_channel_id = str(
            old_channel_id
        )

        new_channel_id = str(
            new_channel_id
        )

        if old_channel_id not in channels:

            return (
                False,
                [
                    f"{song_id} CH {old_channel_id} : canal inconnu."
                ]
            )

        if new_channel_id in channels:

            return (
                False,
                [
                    f"{song_id} CH {new_channel_id} : canal déjà utilisé."
                ]
            )

        before_errors = self.get_blocking_errors(
            self.validate()
        )

        old_song = copy.deepcopy(
            song
        )

        channels[
            new_channel_id
        ] = channels.pop(
            old_channel_id
        )

        new_errors = self.get_new_blocking_errors(
            before_errors
        )

        if new_errors:

            song.clear()

            song.update(
                old_song
            )

            return (
                False,
                new_errors
            )

        return (
            True,
            []
        )

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

    def _validate_song_channel_data(
        self,
        song_id,
        channel_id,
        channel
    ):

        errors = []

        if not isinstance(
            channel,
            dict
        ):

            return [
                f"{song_id} CH {channel_id} : "
                "définition invalide."
            ]

        allowed_fields = {
            "programs",
            "volume",
            "pan",
            "expression",
            "reverb",
            "chorus"
        }

        for field in channel:

            if field not in allowed_fields:

                errors.append(
                    f"{song_id} CH {channel_id} : "
                    f"champ inconnu '{field}'."
                )

        try:

            midi_channel = int(
                channel_id
            )

        except (
            ValueError,
            TypeError
        ):

            return [
                f"{song_id} CH {channel_id} : "
                "canal MIDI invalide."
            ]

        if (
            str(midi_channel) != channel_id
            or
            not 1 <= midi_channel <= 16
        ):

            errors.append(
                f"{song_id} CH {channel_id} : "
                "canal MIDI invalide."
            )

        programs = channel.get(
            "programs"
        )

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

                    if (
                        str(bank) != bank_str
                        or
                        str(program) != program_str
                    ):

                        errors.append(
                            f"{song_id} CH {channel_id} : "
                            f"PROGRAM invalide ({program_id})."
                        )

                        continue

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
                    0 <= bank <= 127
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

                    continue

                allowed_program_fields = {
                    "fusion_name",
                    "instrument"
                }

                for field in program_data:

                    if field not in allowed_program_fields:

                        errors.append(
                            f"{song_id} CH {channel_id} : "
                            f"PROGRAM {program_id} : "
                            f"champ inconnu '{field}'."
                        )

                fusion_name = program_data.get(
                    "fusion_name"
                )

                if fusion_name is not None:

                    if (
                        not isinstance(
                            fusion_name,
                            str
                        )
                        or
                        not fusion_name.strip()
                    ):

                        errors.append(
                            f"{song_id} CH {channel_id} : "
                            f"PROGRAM {program_id} : "
                            "fusion_name invalide."
                        )

                #
                # Instrument global optionnel
                #
                instrument_id = program_data.get(
                    "instrument"
                )

                if instrument_id is not None:

                    if (
                        not isinstance(
                            instrument_id,
                            str
                        )
                        or
                        not instrument_id.strip()
                    ):

                        errors.append(
                            f"{song_id} CH {channel_id} : "
                            f"PROGRAM {program_id} : "
                            "instrument invalide."
                        )

                    elif self.get_instrument(
                        instrument_id
                    ) is None:

                        errors.append(
                            f"{song_id} CH {channel_id} : "
                            f"PROGRAM {program_id} : "
                            f"instrument {instrument_id} inexistant."
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

            if (
                type(value) is not int
                or
                not 0 <= value <= 127
            ):

                errors.append(
                    f"{song_id} CH {channel_id} : "
                    f"{field} invalide ({value})."
                )

        return errors

    def validate_song(
        self,
        song_id
    ):

        song = self.get_song(
            song_id
        )

        if song is None:

            return [
                f"SONG inconnue : {song_id}"
            ]

        return self._validate_song_data(
            song_id,
            song
        )

    def _validate_song_data(
        self,
        song_id,
        song
    ):

        errors = []

        if not isinstance(
            song,
            dict
        ):

            return [
                f"{song_id} : définition invalide."
            ]

        allowed_fields = {
            "name",
            "channels"
        }

        for field in song:

            if field not in allowed_fields:

                errors.append(
                    f"{song_id} : "
                    f"champ inconnu '{field}'."
                )

        name = song.get(
            "name"
        )

        if (
            not isinstance(
                name,
                str
            )
            or
            not name.strip()
        ):

            errors.append(
                f"{song_id} : nom invalide."
            )

        if "channels" not in song:

            errors.append(
                f"{song_id} : channels absent."
            )

            return errors

        channels = song[
            "channels"
        ]

        if not isinstance(
            channels,
            dict
        ):

            errors.append(
                f"{song_id} : channels invalide."
            )

            return errors

        for channel_id, channel in channels.items():

            errors.extend(
                self._validate_song_channel_data(
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

        if not isinstance(
            program,
            dict
        ):

            return None

        parts = program.get(
            "parts",
            {}
        )

        if not isinstance(
            parts,
            dict
        ):

            return None

        part = parts.get(
            "1"
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

        def channel_sort_key(
            item
        ):
            channel_id = item[0]

            try:

                return (
                    0,
                    int(channel_id)
                )

            except (
                TypeError,
                ValueError
            ):

                return (
                    1,
                    str(channel_id)
                )
        result = []

        for mix_id, mix in self.iter_mixes():

            mix_errors = self._validate_mix_data(
                mix_id,
                mix
            )

            if not isinstance(
                mix,
                dict
            ):

                result.append(
                    {
                        "mix": mix_id,
                        "name": mix_id,
                        "fusion_valid": False,
                        "channels": []
                    }
                )

                continue

            mix_result = {
                "mix": mix_id,
                "name": mix.get(
                    "name",
                    mix_id
                ),
                "fusion_valid":
                    len(mix_errors) == 0,
                "channels": []
            }

            channels = mix.get(
                "channels",
                {}
            )

            if not isinstance(
                channels,
                dict
            ):

                result.append(
                    mix_result
                )

                continue

            mix_result[
                "channels"
            ] = []

            for channel_id, channel in sorted(
                channels.items(),
                key=channel_sort_key
            ):
                errors = (
                    self._validate_mix_channel_data(
                        mix_id,
                        channel_id,
                        channel
                    )
                )

                if not isinstance(
                    channel,
                    dict
                ):

                    mix_result[
                        "channels"
                    ].append(
                        {
                            "channel":
                                channel_id,

                            "program":
                                None,

                            "fusion_valid":
                                False,

                            "soundfont_configured":
                                False,

                            "instrument":
                                None
                        }
                    )

                    continue

                try:

                    midi_channel = int(
                        channel_id
                    )

                except (
                    TypeError,
                    ValueError
                ):

                    midi_channel_valid = False

                else:

                    midi_channel_valid = (
                        str(midi_channel) == channel_id
                        and
                        1 <= midi_channel <= 16
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
                            channel_id,

                        "program":
                            channel.get(
                                "program"
                            ),

                        "fusion_valid":
                            len(errors) == 0,

                        "soundfont_configured": (
                            midi_channel_valid
                            and
                            self.is_instrument_soundfont_ready(
                                instrument
                            )
                        ),

                        "instrument":
                            instrument
                    }
                )

            result.append(
                mix_result
            )

            continue

        return result

    def get_program_diagnostic(
        self
    ):

        results = []

        for program_id, program in self.iter_programs():

            errors = self._validate_program_data(
                program_id,
                program
            )

            if not isinstance(
                program,
                dict
            ):

                results.append(
                    {
                        "program": program_id,
                        "name": program_id,
                        "fusion_valid": False,
                        "soundfont_configured": False,
                        "errors": errors
                    }
                )

                continue

            parts = program.get(
                "parts"
            )

            part = (
                parts.get(
                    "1"
                )
                if isinstance(
                    parts,
                    dict
                )
                else None
            )

            results.append(
                {
                    "program": program_id,

                    "name": program.get(
                        "name",
                        ""
                    ),

                    "fusion_valid":
                        len(errors) == 0,

                    "soundfont_configured":
                        (
                            isinstance(
                                part,
                                dict
                            )
                            and
                            self.is_soundfont_ready(
                                part
                            )
                        ),

                    "errors":
                        errors
                }
            )

        return results

    def get_song_diagnostic(
        self
    ):

        diagnostic = []

        for song_id, song in self.iter_songs():

            song_errors = self._validate_song_data(
                song_id,
                song
            )

            if not isinstance(
                song,
                dict
            ):

                diagnostic.append(
                    {
                        "song": song_id,
                        "name": song_id,
                        "fusion_valid": False,
                        "channels": []
                    }
                )

                continue

            song_diagnostic = {
                "song": song_id,
                "name": song.get(
                    "name",
                    song_id
                ),
                "fusion_valid": (
                    len(song_errors) == 0
                ),
                "channels": []
            }

            channels = song.get(
                "channels",
                {}
            )

            if not isinstance(
                channels,
                dict
            ):

                diagnostic.append(
                    song_diagnostic
                )

                continue

            for channel_id, channel in channels.items():

                errors = self._validate_song_channel_data(
                    song_id,
                    channel_id,
                    channel
                )

                fusion_valid = (
                    len(errors) == 0
                )

                programs = (
                    channel.get(
                        "programs"
                    )
                    if isinstance(
                        channel,
                        dict
                    )
                    else None
                )

                soundfont_configured = False

                try:

                    midi_channel = int(
                        channel_id
                    )

                except (
                    TypeError,
                    ValueError
                ):

                    midi_channel_valid = False

                else:

                    midi_channel_valid = (
                        str(midi_channel) == channel_id
                        and
                        1 <= midi_channel <= 16
                    )

                    if (
                        midi_channel_valid
                        and
                        isinstance(
                            programs,
                            dict
                        )
                        and
                        programs
                    ):

                        soundfont_configured = True

                        for (
                            program_id,
                            program_data
                        ) in programs.items():

                            if not isinstance(
                                program_data,
                                dict
                            ):

                                soundfont_configured = False
                                break

                            instrument = (
                                self.resolve_song_program_instrument(
                                    program_id,
                                    program_data
                                )
                            )

                            if not self.is_instrument_soundfont_ready(
                                instrument
                            ):

                                soundfont_configured = False
                                break

                song_diagnostic[
                    "channels"
                ].append(
                    {
                        "channel": channel_id,
                        "fusion_valid": fusion_valid,
                        "soundfont_configured":
                            soundfont_configured
                    }
                )

            diagnostic.append(
                song_diagnostic
            )

        return diagnostic

    def get_project_diagnostic_summary(self):

        summary = {
            "instruments": {
                "total": 0,
                "ok": 0,
                "unconfigured": 0,
                "error": 0
            },
            "mixes": {
                "total": 0,
                "ok": 0,
                "unconfigured": 0,
                "error": 0
            },
            "programs": {
                "total": 0,
                "ok": 0,
                "unconfigured": 0,
                "error": 0
            },
            "songs": {
                "total": 0,
                "ok": 0,
                "unconfigured": 0,
                "error": 0
            }
        }

        # INSTRUMENT

        for instrument_id in self.get_instruments():

            summary["instruments"]["total"] += 1

            errors = self._validate_instrument(
                instrument_id
            )

            if errors:

                summary["instruments"]["error"] += 1

            else:

                summary["instruments"]["ok"] += 1

        # MIX

        for mix in self.get_mix_diagnostic():

            summary["mixes"]["total"] += 1

            units = mix.get(
                "channels",
                []
            )

            total = len(
                units
            )

            fusion_valid = mix.get(
                "fusion_valid",
                False
            )

            configured = sum(
                1
                for unit in units
                if unit.get(
                    "soundfont_configured",
                    False
                )
            )

            #
            # État de configuration
            #
            if not fusion_valid:

                summary["mixes"]["error"] += 1

            elif (
                total == 0
                or
                configured < total
            ):

                summary["mixes"]["unconfigured"] += 1

            else:

                summary["mixes"]["ok"] += 1

        # PROGRAM

        for program in self.get_program_diagnostic():

            summary["programs"]["total"] += 1

            if not program.get(
                "fusion_valid",
                False
            ):

                summary["programs"]["error"] += 1

            elif not program.get(
                "soundfont_configured",
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

            fusion_valid = song.get(
                "fusion_valid",
                False
            )

            soundfont_configured = (
                bool(channels)
                and all(
                    channel.get(
                        "soundfont_configured",
                        False
                    )
                    for channel in channels
                )
            )

            if not fusion_valid:

                summary["songs"]["error"] += 1

            elif not soundfont_configured:

                summary["songs"]["unconfigured"] += 1

            else:

                summary["songs"]["ok"] += 1

        return summary

    #
    # Validation
    #
    def validate(self):

        errors = []

        errors.extend(
            self._validate_banks()
        )

        errors.extend(
            self._validate_instruments()
        )

        for mix_id in self.get_mixes():

            errors.extend(
                self.validate_mix(
                    mix_id
                )
            )

        for program_id in self.get_programs():

            errors.extend(
                self.validate_program(
                    program_id
                )
            )

        for song_id in self.get_songs():

            errors.extend(
                self.validate_song(
                    song_id
                )
            )

        return errors

    def _validate_bank_names(
        self,
        bank_type
    ):

        errors = []

        banks = self.data.get(
            "banks",
            {}
        ).get(
            bank_type,
            {}
        )

        for bank_id, name in banks.items():

            prefix = (
                f"Banque {bank_type.upper()} "
                f"{bank_id}"
            )

            if (
                not isinstance(
                    bank_id,
                    str
                )
                or
                not bank_id.isdigit()
                or
                str(int(bank_id)) != bank_id
                or
                not 0 <= int(bank_id) <= 127
            ):

                errors.append(
                    f"{prefix} : identifiant invalide"
                )

                continue

            if (
                not isinstance(
                    name,
                    str
                )
                or
                not name.strip()
            ):

                errors.append(
                    f"{prefix} : nom invalide"
                )

        return errors

    def _validate_banks(
        self
    ):

        errors = []

        banks = self.data.get(
            "banks"
        )

        if not isinstance(
            banks,
            dict
        ):

            return [
                "Banques : définition invalide"
            ]

        required_sections = {
            "program",
            "mix"
        }

        for section in sorted(
            required_sections
        ):

            if section not in banks:

                errors.append(
                    f"Banques : section {section} absente"
                )

            elif not isinstance(
                banks[section],
                dict
            ):

                errors.append(
                    f"Banques : section {section} invalide"
                )

        unknown_sections = (
            set(banks)
            - required_sections
        )

        for section in sorted(
            unknown_sections
        ):

            errors.append(
                f"Banques : section inconnue {section}"
            )

        if errors:

            return errors

        errors.extend(
            self._validate_bank_names(
                "program"
            )
        )

        errors.extend(
            self._validate_bank_names(
                "mix"
            )
        )

        return errors

    def mix_has_channels(
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
                "channels",
                {}
            )
        )

    def _ensure_mix(
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

    def update_mix_channel(
        self,
        mix_id,
        channel_id,
        updates=None,
        remove_fields=None
    ):

        mix = self.get_mix(
            mix_id
        )

        if mix is None:

            return (
                False,
                [
                    f"Mix inconnu : {mix_id}"
                ]
            )

        channels = mix.get(
            "channels"
        )

        if not isinstance(
            channels,
            dict
        ):

            return (
                False,
                [
                    f"{mix_id} : définition channels invalide."
                ]
            )

        channel_id = str(
            channel_id
        )

        channel = channels.get(
            channel_id
        )

        if not isinstance(
            channel,
            dict
        ):

            return (
                False,
                [
                    f"{mix_id} CH {channel_id} : canal inconnu."
                ]
            )

        before_errors = self.get_blocking_errors(
            self.validate()
        )

        old_mix = copy.deepcopy(
            mix
        )

        if updates:

            channel.update(
                updates
            )

        if remove_fields:

            for field in remove_fields:

                channel.pop(
                    field,
                    None
                )

        new_errors = self.get_new_blocking_errors(
            before_errors
        )

        if new_errors:

            mix.clear()

            mix.update(
                old_mix
            )

            return (
                False,
                new_errors
            )

        return (
            True,
            []
        )

    def replace_mix_channels(
        self,
        mix_id,
        channels
    ):

        before_errors = self.get_blocking_errors(
            self.validate()
        )

        backup = copy.deepcopy(
            self.data
        )

        mix = self._ensure_mix(
            mix_id
        )

        if not isinstance(
            mix,
            dict
        ):

            self.data = backup

            return (
                False,
                [
                    f"{mix_id} : définition invalide."
                ]
            )

        mix["channels"] = channels

        new_errors = self.get_new_blocking_errors(
            before_errors
        )

        if new_errors:

            self.data = backup

            return (
                False,
                new_errors
            )

        return (
            True,
            []
        )

    #
    # Instruments
    #
    def get_instruments(self):

        return self.data[
            "instruments"
        ]

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

        if not isinstance(
            part,
            dict
        ):

            return None

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

    def list_instruments(self):

        return sorted(
            self.get_instruments().items()
        )

    def add_instrument(
        self,
        instrument_id,
        instrument
    ):

        instruments = self.get_instruments()

        if instrument_id in instruments:

            return (
                False,
                [
                    f"Instrument existant : {instrument_id}"
                ]
            )

        before_errors = self.get_blocking_errors(
            self.validate()
        )

        instruments[
            instrument_id
        ] = instrument

        new_errors = self.get_new_blocking_errors(
            before_errors
        )

        if new_errors:

            instruments.pop(
                instrument_id,
                None
            )

            return (
                False,
                new_errors
            )

        return (
            True,
            []
        )

    def update_instrument(
        self,
        instrument_id,
        instrument
    ):

        instruments = self.get_instruments()

        if instrument_id not in instruments:

            return (
                False,
                [
                    f"Instrument inconnu : {instrument_id}"
                ]
            )

        before_errors = self.get_blocking_errors(
            self.validate()
        )

        old_instrument = copy.deepcopy(
            instruments[
                instrument_id
            ]
        )

        instruments[
            instrument_id
        ] = instrument

        new_errors = self.get_new_blocking_errors(
            before_errors
        )

        if new_errors:

            instruments[
                instrument_id
            ] = old_instrument

            return (
                False,
                new_errors
            )

        return (
            True,
            []
        )

    def remove_instrument(
        self,
        instrument_id
    ):

        instruments = self.get_instruments()

        if instrument_id not in instruments:

            return (
                False,
                [
                    f"Instrument inconnu : {instrument_id}"
                ]
            )

        if self.find_instrument_usage(
            instrument_id
        ):

            return (
                False,
                [
                    f"Instrument utilisé : {instrument_id}"
                ]
            )

        del instruments[
            instrument_id
        ]

        return (
            True,
            []
        )

    def find_instrument_usage(
        self,
        instrument_id
    ):

        usages = []

        #
        # PROGRAM
        #
        for program_id, program in self.iter_programs():

            if not isinstance(
                program,
                dict
            ):

                continue

            parts = program.get(
                "parts"
            )

            if not isinstance(
                parts,
                dict
            ):

                continue

            for part_id, part in parts.items():

                if not isinstance(
                    part,
                    dict
                ):

                    continue

                if part.get(
                    "instrument"
                ) == instrument_id:

                    usages.append(
                        {
                            "type": "program",
                            "program_id": program_id,
                            "part_id": part_id
                        }
                    )

        #
        # MIX
        #
        for mix_id, mix in self.iter_mixes():

            if not isinstance(
                mix,
                dict
            ):

                continue

            channels = mix.get(
                "channels"
            )

            if not isinstance(
                channels,
                dict
            ):

                continue

            for channel_id, channel in channels.items():

                if not isinstance(
                    channel,
                    dict
                ):

                    continue

                if channel.get(
                    "instrument"
                ) == instrument_id:

                    usages.append(
                        {
                            "type": "mix",
                            "mix_id": mix_id,
                            "channel_id": channel_id
                        }
                    )

        #
        # SONG
        #
        for song_id, song in self.iter_songs():

            if not isinstance(
                song,
                dict
            ):

                continue

            channels = song.get(
                "channels"
            )

            if not isinstance(
                channels,
                dict
            ):

                continue

            for channel_id, channel in channels.items():

                if not isinstance(
                    channel,
                    dict
                ):

                    continue

                programs = channel.get(
                    "programs"
                )

                if not isinstance(
                    programs,
                    dict
                ):

                    continue

                for program_id, program_data in programs.items():

                    if not isinstance(
                        program_data,
                        dict
                    ):

                        continue

                    if program_data.get(
                        "instrument"
                    ) == instrument_id:

                        usages.append(
                            {
                                "type": "song",
                                "song_id": song_id,
                                "channel_id": channel_id,
                                "program_id": program_id
                            }
                        )

        return usages

    def count_instruments(self):

        return len(
            self.get_instruments()
        )
