#!/bin/bash


set -o errexit
# Update pip
pip install --upgrade pip


# Install requirements
pip install -r requirements.txt