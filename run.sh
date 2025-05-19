#!/bin/bash

set -e

if [ "X$VIRTUAL_ENV" == "X" ]; then
    if [ -d ./Scripts ]; then
        source ./Scripts/activate
    elif [ -d ./bin ]; then
        source ./bin/activate
    else
        echo "ERROR: can not find venv directory" 1>&2
        exit 2
    fi
fi

set -x

date -R
uname -a
which python
python -VV
python -m sysconfig
python -m pip freeze | grep -v -i -E '^pydirectinput\s' | tee ./requirements.txt

exec python $*
