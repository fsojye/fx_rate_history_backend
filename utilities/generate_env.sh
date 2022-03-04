#!/bin/sh

BASEDIR=$(pwd)

printf "\e[33m%b\e[0m\n" "Generating .env file for $ENVIRONMENT"

# env_file="$BASEDIR/.env"
# env_temp="$BASEDIR/.env.secret"

# cp $env_temp $env_file

python -m pipenv run python utilities/_get_secret_params.py
