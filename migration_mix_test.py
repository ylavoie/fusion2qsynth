python3 - <<'PY'
from fusion_project import FusionProject

project = FusionProject()

result = project.migrate_legacy_mixes()

print(result)

old = 0
new = 0

for mix_id, mix in project.get_mixes().items():

    if "channels" in mix:
        new += 1

    if "parts" in mix:
        old += 1

print("MIX nouveau format :", new)
print("MIX ancien format  :", old)

errors = project.validate()

print("Erreurs validation :", len(errors))

for error in errors:
    print("-", error)
PY
