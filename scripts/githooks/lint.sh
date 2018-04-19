#!/bin/sh

source "${FREE_RANGE_PYENV:?Must set to a python env path}/bin/activate"
# on macs you may need launchctl setenv FREE_RANGE_PYENV ~/envs/3.6.1

if ! python scripts/enforce_min_python_version.py; then
    echo "aborting commit"
    exit 1
fi

echo 'Running isort...'
git diff master --name-only | grep '\.py$' | xargs -L 1 isort "$@"

if [ $? -ne 0 ]; then
    echo '    isort failed.'
    exit 1
fi

echo 'Running autoflake...'
# Requires: pip install autoflake
git diff master --name-only | grep '\.py$' | xargs -L 1 autoflake --remove-all-unused-imports --remove-unused-variables -i "$@"

if [ $? -ne 0 ]; then
    echo '    autoflake failed.'
    exit 1
fi

# make sure everything is fixed
echo 'Running flake8...'
git diff master --name-only | grep '\.py$' | xargs flake8 "$@"

if [ $? -ne 0 ]; then
    echo '    flake8 failed.'
    exit 1
fi

echo 'Checking for todo items...'
git diff master --name-only | grep '\.py$' | xargs egrep --color '# *(question|fixme|todo).*$' "$@"

echo
echo 'Done.'
exit 0
