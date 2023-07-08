#!/bin/bash


set -o errexit
# Update pip
pip install --upgrade pip setuptools wheel


# Install requirements
pip install -r requirements.txt
