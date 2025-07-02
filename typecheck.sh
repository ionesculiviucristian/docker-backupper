#!/bin/bash
set -eu

source ./.venv/bin/activate

mypy src/ --explicit-package-bases --package-root src

deactivate
