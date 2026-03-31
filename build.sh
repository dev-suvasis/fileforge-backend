#!/usr/bin/env bash
set -e

echo "==> Installing system dependencies..."
apt-get update -qq
apt-get install -y libreoffice poppler-utils --no-install-recommends -qq

echo "==> Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Running migrations..."
python manage.py migrate --noinput

echo "==> Build complete."
