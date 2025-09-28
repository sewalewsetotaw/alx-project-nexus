#!/usr/bin/env bash
set -o errexit

# Install dependencies
pip install -r ecommerce_backend/requirements.txt

# Navigate into project folder for Django commands
cd ecommerce_backend

# Collect static files
python manage.py collectstatic --no-input

# Apply migrations
python manage.py migrate
