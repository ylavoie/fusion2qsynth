#!/usr/bin/env python3

import os
import json
import shutil

import fusion_lib
from fusion_lib import print_mix as print_mix_lib
from fusion_constants import FUSION_FILE

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

        with open(
            self.filename,
            "r",
            encoding="utf-8"
        ) as f:

            self.data = json.load(f)

    def save(self):

        self.backup()

        with open(
            self.filename,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                self.data,
                f,
                indent=2,
                ensure_ascii=False
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

        if new_time != self.file_time:

            self.file_time = new_time

            self.load()

            return True

        return False

    def backup(self):

        if os.path.exists(
            self.filename
        ):

            shutil.copy2(
                self.filename,
                self.filename + ".bak"
            )

    #
    # Accès Mix
    #
    def get_mix(
        self,
        mix_id
    ):

        return self.data.get(
            mix_id
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

        for mix_id in fusion_lib.sort_mix_ids(
            self.data
        ):

            yield (
                mix_id,
                self.data[mix_id]
            )

    def count_mixes(self):

        return len(
            self.data
        )

    def summary(self):

        result = {}

        result["mixes"] = len(
            self.data
        )

        parts = 0
        configured = 0

        for mix in self.data.values():

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

    #
    # Validation
    #
    def validate(self):

        errors = []

        for mix_id, mix in self.data.items():

            errors.extend(
                self.validate_mix_data(
                    mix_id,
                    mix
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


        channels = []


        for part_id, part in mix["parts"].items():

            errors.extend(
                self.validate_part_data(
                    mix_id,
                    part_id,
                    part
                )
            )


            ch = part.get(
                "midi_channel"
            )

            if ch is not None:

                channels.append(ch)


        duplicates = sorted({
            ch
            for ch in channels
            if channels.count(ch) > 1
        })


        if duplicates:

            errors.append(
                f"{mix_id} : canaux MIDI partagés {duplicates}."
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

        return (
            "midi_channel" in part
            and
            "sf2_bank" in part
            and
            "sf2_program" in part
        )

    #
    # Diagnostic
    #
    def get_diagnostic(self):

        results = []


        for mix_id, mix in self.data.items():

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


        print_mix_lib(
            mix_id,
            mix
        )

    def mix_has_parts(
        self,
        mix_id
    ):

        mix = self.data.get(
            mix_id,
            {}
        )

        return bool(
            mix.get(
                "parts"
            )
        )

    def ensure_mix(
        self,
        mix_id
    ):

        if mix_id not in self.data:

            self.data[mix_id] = {

                "name":
                    f"Fusion Mix {mix_id}",

                "parts": {}

            }

        return self.data[mix_id]

    def prepare_capture(
        self,
        mix_id
    ):

        if mix_id not in self.data:

            self.data[mix_id] = {

                "name":
                    f"Fusion Mix {mix_id}",

                "parts": {}

            }

            return True

        if (
            "parts" in self.data[mix_id]
            and
            self.data[mix_id]["parts"]
        ):

            return False

        return True

    def get_mix_by_program(
        self,
        bank,
        program
    ):

        mix_id = f"{bank}:{program}"

        return self.get_mix(
            mix_id
        )

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

        for mix_id, mix in self.data.items():

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

                    "mix_id":
                        mix_id,

                    "part_id":
                        part_id,

                    "part":
                        part
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

        #
        # Nouveau format
        #

        if "instrument" in part:

            instrument = self.get_instrument(
                part["instrument"]
            )

            if instrument:

                return instrument


        #
        # Ancien format
        #

        if (
            "sf2_bank" in part
            and
            "sf2_program" in part
        ):

            return {

                "name":
                    part.get(
                        "name",
                        "Non configuré"
                    ),

                "sf2_bank":
                    part["sf2_bank"],

                "sf2_program":
                    part["sf2_program"]
            }


        return None
