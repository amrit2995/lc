#!/bin/bash
set -eo pipefail
# Needed so the shell can find the poetry binary that is install
export PATH=$PATH:/home/carbon/.local/bin

# Installs poetry
pip install -U poetry
# Install all deps
poetry install