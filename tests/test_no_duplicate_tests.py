#!/usr/bin/env python3

import ast
import copy

from collections import defaultdict
from pathlib import Path


def test_no_duplicate_tests():

    tests_dir = Path(__file__).resolve().parent

    signatures = defaultdict(list)
    duplicates = []
    total = 0

    for path in sorted(
        tests_dir.rglob("test_*.py")
    ):

        tree = ast.parse(
            path.read_text(encoding="utf-8"),
            filename=str(path)
        )

        names = defaultdict(list)

        def analyze(node, qualified_name):

            nonlocal total

            total += 1

            names[qualified_name].append(
                node.lineno
            )

            clone = copy.deepcopy(node)

            clone.name = "__test__"

            signature = ast.dump(
                clone,
                annotate_fields=True,
                include_attributes=False
            )

            signatures[signature].append(
                (
                    path,
                    qualified_name,
                    node.lineno
                )
            )

        for node in tree.body:

            if isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef
                )
            ):

                if node.name.startswith("test_"):

                    analyze(
                        node,
                        node.name
                    )

            elif isinstance(node, ast.ClassDef):

                for child in node.body:

                    if isinstance(
                        child,
                        (
                            ast.FunctionDef,
                            ast.AsyncFunctionDef
                        )
                    ):

                        if child.name.startswith("test_"):

                            analyze(
                                child,
                                f"{node.name}.{child.name}"
                            )

        for name, lines in names.items():

            if len(lines) > 1:

                duplicates.append(
                    f"{path}:{name} "
                    f"lignes {lines}"
                )

    structural_duplicates = []

    for locations in signatures.values():

        if len(locations) > 1:

            structural_duplicates.append(
                " | ".join(
                    f"{path}:{line} ({name})"
                    for path, name, line in locations
                )
            )

    errors = []

    if duplicates:

        errors.append(
            "Noms de tests dupliqués :\n"
            + "\n".join(duplicates)
        )

    if structural_duplicates:

        errors.append(
            "Copies structurelles :\n"
            + "\n".join(structural_duplicates)
        )

    assert not errors, (
        "\n\n".join(errors)
    )

    print(
        f"\nAudit des tests : "
        f"{total} définitions vérifiées, "
        "aucun duplicat."
    )
