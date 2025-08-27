#!/bin/bash

set -x
set -e
set -o pipefail

SOURCE_DIR="${1:-./pykmmacro}"

test -d "$SOURCE_DIR" || exit 1
test -r "$SOURCE_DIR" || exit 1
test -x "$SOURCE_DIR" || exit 1

cat <<'EOF'
# type: ignore
EOF

ls "$SOURCE_DIR" |
grep -E '[.]py$' |
grep -v -E '^_' |
while read -r FILENAME; do
    TARGET="$SOURCE_DIR/$FILENAME"
    test -r "$TARGET"
    test -s "$TARGET"

    cat "$TARGET" |
    grep -E '^(def|class) ' |
    awk '{print $2}' |
    perl -pe 's/^([a-zA-Z0-9_]+).+$/$1/' |
    grep -v -E '^_' |
    sort |
    perl -e '@a=<>; s/\r?\n$// foreach @a; print join(", ", @a) . "\n"' |
    while read -r LINE; do
        MODULENAME="$(basename "$FILENAME" .py)"
        echo "from .$MODULENAME import $LINE"
    done
done
