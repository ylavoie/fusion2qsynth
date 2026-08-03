#!/usr/bin/env python3

import os
import json

import fusion_lib

class FusionProject:

    def __init__(
        self,
        filename="fusion.json"
    ):

        self.filename = filename
        self.data = {}

        self.load()

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

        fusion_lib.save_json(
            self.data
        )

    def get_mix(
        self,
        mix_id
    ):

        return self.data.get(
            mix_id
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

    def validate(self):

        return fusion_lib.validate_mix(
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

    def get_mix_or_none(self, mix_id):
        return self.data.get(mix_id)
