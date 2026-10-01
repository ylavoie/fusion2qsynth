#! /bin/bash -x

git diff --check
python3 -m py_compile *.py
python3 integration-globale.py

python3 -m pytest

git status
git diff --stat
