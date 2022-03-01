#!/bin/sh

printf "\e[33m%b\e[0m\n" "Installing nodejs dependencies"
if [ -f yarn.lock ]; then
  yarn install --frozen-lockfile
else
  yarn install
fi

printf "\e[33m%b\e[0m\n" "Installing python dependencies"
python -m pip install --upgrade pip
python -m pip install pipenv
mkdir -p .venv
python -m pipenv install -d --ignore-pipfile
