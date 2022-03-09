#!/bin/sh

printf "\e[33m%b\e[0m\n" "Generating swagger api documentation..."
python utilities/_generate_swagger.py swagger.json
