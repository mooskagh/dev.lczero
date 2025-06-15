#!/bin/bash

set -e

cd lczero_dev_portal

echo "Running Django system checks..."
python manage.py check --verbosity=2

echo "Running isort..."
isort .

echo "Running black..."
black --preview --line-length=79 --enable-unstable-feature string_processing .

echo "Running flake8..."
flake8 .

echo "Running mypy..."
mypy .

echo "All checks passed!"