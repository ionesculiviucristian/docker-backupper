#!/bin/bash
set -eu

source ./.venv/bin/activate

export PYTHONPATH=$(pwd)
exec python ./src/main.py "$@"

deactivate
