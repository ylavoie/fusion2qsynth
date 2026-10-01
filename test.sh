#! /bin/bash -x

git diff --check
python3 -m py_compile *.py
python3 integration-globale.py

git status
git diff --stat
