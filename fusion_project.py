#!/usr/bin/env python3

import os
import json
import shutil
import time
import copy

from fusion_lib import (
    note_name, note_range
)

# Fichiers
FUSION_FILE = "fusion.json"

# Sauvegarde
_BACKUP_COUNT = 3
_TMP_SUFFIX = ".tmp"

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

    def save_safe(self):

        errors = self.validate()

        if errors:

            print(
                "Sauvegarde refusée : erreurs de validation."
            )

            return False

        self._rotate_backups()

        if os.path.exists(self.filename):

            shutil.copy2(
                self.filename,
                self.filename + ".bak"
            )

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

        if errors:

            if old_name is None:

                mix.pop(
                    "name",
                    None
                )

            else:

                mix["name"] = old_name

            return (
                False,
                errors
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

        if errors:

            mixes.pop(
                new_mix_id,
                None
            )

            return (
                False,
                errors
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

        if errors:

            self.data = backup

            return (
                False,
                errors
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

        if errors:

            self.data = backup

            return (
                False,
                errors
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

        if not isinstance(mix, dict):

            errors.append(
                f"{mix_id} : définition invalide."
            )

            return errors

        if "parts" not in mix:

            errors.append(
                f"{mix_id} : aucune PART."
            )

            return errors

        for part_id, part in mix["parts"].items():

            errors.extend(
                self.validate_part_data(
                    mix_id,
                    part_id,
                    part
                )
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


        if "bank" not in part:

            errors.append(
                f"{prefix} : bank Fusion absente."
            )


        if "program" not in part:

            errors.append(
                f"{prefix} : program Fusion absent."
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

        part.update(
            updates
        )

        errors = self.validate()

        if errors:

            part.clear()

            part.update(
                old
            )

            return(
                False,
                errors
            )

        return (
            True,
            []
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

    #
    # Diagnostic
    #
    def get_diagnostic(self):

        results = []


        for mix_id, mix in self.iter_mixes():

            mix_result = {
                "mix": mix_id,
                "name": mix.get(
                    "name",
                    ""
                ),
                "parts": []
            }


            channels = []


            for part_id, part in mix.get(
                "parts",
                {}
            ).items():

                part_result = {
                    "part": part_id,
                    "fusion_valid": True,
                    "qsynth_configured": False,
                    "errors": []
                }


                #
                # Validation Fusion
                #

                if "midi_channel" not in part:

                    part_result["fusion_valid"] = False

                    part_result["errors"].append(
                        "Canal MIDI absent"
                    )

                else:

                    channels.append(
                        part["midi_channel"]
                    )


                #
                # Configuration QSynth
                #

                part_result["qsynth_configured"] = (
                    "sf2_bank" in part
                    and
                    "sf2_program" in part
                )


                mix_result["parts"].append(
                    part_result
                )


            #
            # Détection canaux partagés
            #

            duplicates = sorted({
                ch
                for ch in channels
                if channels.count(ch) > 1
            })


            if duplicates:

                mix_result["shared_channels"] = duplicates


            results.append(
                mix_result
            )


        return results

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

        print("=" * 40)

        print(
            mix.get(
                "name",
                mix_id
            )
        )

        print("=" * 40)

        for part_id, part in self.iter_parts(mix):

            self.print_part(
                part_id,
                part
            )

    def print_part(
        self,
        part_id,
        part
    ):

        print()

        print(
            "PART",
            part_id
        )

        print(
            "----------------"
        )


        instrument = self.resolve_part_instrument(
            part
        )


        if instrument:

            print(
                "Instrument :",
                instrument.get(
                    "name",
                    "?"
                )
            )

            print(
                "Bank       :",
                instrument.get(
                    "sf2_bank",
                    0
                )
            )

            print(
                "Program    :",
                instrument.get(
                    "sf2_program",
                    0
                )
            )

        else:

            print(
                "Instrument : Non configuré"
            )


        print(
            "Canal MIDI :",
            part.get(
                "midi_channel",
                "?"
            )
        )

        print(
            "Plage      :",
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
            "Velocity   :",
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

    def ensure_mix(
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

        return mixes[mix_id]

    def replace_mix_parts(
        self,
        mix_id,
        parts
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

        if errors:

            mix["parts"] = old_parts

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
