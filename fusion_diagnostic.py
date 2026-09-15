def print_validation_errors(
    project,
    errors,
    title="Erreurs de validation"
):

    mix_errors = []
    program_errors = []
    song_errors = []
    other_errors = []
    structured_errors = []

    mix_ids = {
        mix_id
        for mix_id, _ in project.iter_mixes()
    }

    program_ids = {
        program_id
        for program_id, _ in project.iter_programs()
    }

    song_ids = {
        song_id
        for song_id, _ in project.iter_songs()
    }

    for error in errors:

        if not isinstance(
            error,
            str
        ):

            structured_errors.append(
                error
            )

            continue

        matched = False

        for song_id in song_ids:

            if error.startswith(
                f"{song_id} "
            ):

                song_errors.append(
                    error
                )

                matched = True
                break

        if matched:
            continue

        for program_id in program_ids:

            if error.startswith(
                f"{program_id} "
            ):

                program_errors.append(
                    error
                )

                matched = True
                break

        if matched:
            continue

        for mix_id in mix_ids:

            if error.startswith(
                f"{mix_id} "
            ):

                mix_errors.append(
                    error
                )

                matched = True
                break

        if not matched:

            other_errors.append(
                error
            )

    print()
    print("====================")
    print(title)
    print("====================")

    if mix_errors:

        print()
        print("MIX")
        print("---")

        for error in mix_errors:

            print(
                "-",
                error
            )

    if program_errors:

        print()
        print("PROGRAM")
        print("-------")

        for error in program_errors:

            print(
                "-",
                error
            )

    if song_errors:

        print()
        print("SONG")
        print("----")

        for error in song_errors:

            print(
                "-",
                error
            )

    if other_errors:

        print()
        print("AUTRES")
        print("------")

        for error in other_errors:

            print(
                "-",
                error
            )

    for error in structured_errors:

        print(
            "-",
            error.get(
                "message",
                error
            )
        )

def print_error_messages(
    errors
):

    for error in errors:

        if isinstance(
            error,
            str
        ):

            message = error

        else:

            message = error.get(
                "message",
                error
            )

        print(
            "-",
            message
        )
