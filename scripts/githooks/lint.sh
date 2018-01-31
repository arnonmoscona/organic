#!/bin/sh

echo
echo 'Running isort...'
echo
git diff master --name-only | grep '\.py$' | xargs -L 1 -t isort "$@"

if [ $? -ne 0 ]; then
    echo '    isort failed.'
    exit 1
fi

echo
echo 'Running autoflake...'
echo
# Requires: pip install autoflake
git diff master --name-only | grep '\.py$' | xargs -L 1 -t autoflake --remove-all-unused-imports --remove-unused-variables -i "$@"

if [ $? -ne 0 ]; then
    echo '    autoflake failed.'
    exit 1
fi

# make sure everything is fixed
echo
echo 'Running flake8...'
echo
git diff master --name-only | grep '\.py$' | xargs -t flake8 "$@"

if [ $? -ne 0 ]; then
    echo '    flake8 failed.'
    exit 1
fi

echo
echo 'Checking for todo items...'
echo
git diff master --name-only | grep '\.py$' | xargs egrep --color '# *(question|fixme|todo)' "$@"

echo
echo 'Done.'
exit 0
