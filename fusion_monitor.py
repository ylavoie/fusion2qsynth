#!/usr/bin/env python3

import mido

from fusion_project import FusionProject

from fusion_lib import (
    find_fusion_input,
    build_channel_map,
    note_name,
    print_part
)


FILE = "fusion.json"

FUSION_IN = "CH345"


def main():

    project = FusionProject()

    data = project.data

    channel_map = build_channel_map(
        data
    )

    port_name = find_fusion_input()

    if not port_name:

        raise Exception(
            "Fusion MIDI introuvable"
        )

    print(
        "Monitoring :",
        port_name
    )

    with mido.open_input(port_name) as inp:

        try:
            for msg in inp:

                if msg.type not in (
                    "note_on",
                    "note_off"
                ):
                    continue

                ch = msg.channel + 1

                print()
                print(
                    msg.type.upper()
                )

                print(
                    " Canal :",
                    ch
                )

                print(
                    " Note :",
                    note_name(
                        msg.note
                    )
                )

                print(
                    " Velocity :",
                    msg.velocity
                )

                info = channel_map.get(
                    ch
                )

                if info:

                    part_id = info["part_id"]
                    part = info["part"]
                    print_part(part_id,part)

                else:

                    print(
                        " PART inconnue"
                    )

        except KeyboardInterrupt:
            print()
            print("Retour au menu")
            return

if __name__ == "__main__":

    main()
