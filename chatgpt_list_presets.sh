for file in /usr/share/sounds/sf2/*.sf2; do
    echo
    echo "===== $(basename "$file") ====="

    tmp=$(mktemp)

    sf2dump "$file" 2>>sf2dump-errors.log |
    awk '
    /\(Preset:/ {
        line=$0

        name=line
        sub(/^[[:space:]]*/, "", name)
        sub(/[[:space:]]+\(Preset:.*/, "", name)

        preset=line
        sub(/.*Preset: /, "", preset)
        sub(/,.*/, "", preset)

        bank=line
        sub(/.*Bank: /, "", bank)
        sub(/,.*/, "", bank)

        printf "%d\t%d\t%s\n", bank, preset, name
    }' > "$tmp"

    echo "Nombre de presets : $(wc -l < "$tmp")"
    echo
    printf "%-5s %-7s %s\n" "BANK" "PRESET" "INSTRUMENT"

    sort -n -k1,1 -k2,2 "$tmp" |
    awk -F '\t' '
    {
        printf "%-5d %-7d %s\n", $1, $2, $3
    }'

    rm -f "$tmp"
done
