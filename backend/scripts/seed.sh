#!/bin/bash
set -e

echo "Starting database seeding..."
python manage.py seed
echo "Database seeding completed!"
