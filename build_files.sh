#!/bin/bash

# Build script for Vercel deployment
echo "Starting build process..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Set Django settings module
export DJANGO_SETTINGS_MODULE=hootel.settings

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run database migrations (if needed)
echo "Running database migrations..."
python manage.py migrate --noinput

echo "Build process completed successfully!"