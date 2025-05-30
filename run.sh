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

# enable "dev mode" for Python interpreter
export PYTHONDEVMODE=1

# enable SIGSEGV handler for Python interpreter
export PYTHONFAULTHANDLER=1

# always use UTF-8 encoding for stdin/stdout/stderr even if they are redirected
export PYTHONIOENCODING='utf-8'

# disable buffering of stdout (same as `-u` command-line option)
export PYTHONUNBUFFERED=1

date -R
uname -a
which py
py -VV
py -m sysconfig
py -m pip freeze | grep -v -i ' @ file:///' | tee ./requirements.txt

exec py $*
