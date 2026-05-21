#!/bin/sh
# Exit on error
set -e

# Run database migrations
echo "Applying database migrations via Alembic..."
alembic upgrade head

# Seed standard data
echo "Seeding default database records..."
python -m app.scripts.seed

# Execute the main container process
exec "$@"
