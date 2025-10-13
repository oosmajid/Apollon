#!/bin/bash

# Script to populate database with fake data
# Usage: ./populate_data.sh [--clear]

echo "Starting fake data population..."

# Change to backend directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
elif [ -d "../venv" ]; then
    echo "Activating virtual environment from parent directory..."
    source ../venv/bin/activate
fi

# Check if Django is available
if ! python3 -c "import django" 2>/dev/null; then
    echo "Error: Django is not installed or virtual environment is not activated."
    echo ""
    echo "Please do one of the following:"
    echo "1. Activate your virtual environment:"
    echo "   source venv/bin/activate"
    echo "2. Install requirements:"
    echo "   pip install -r requirements.txt"
    echo "3. Then run this script again"
    exit 1
fi

# Run Django management command
echo "Running Django management command..."
python3 manage.py populate_fake_data "$@"

echo "Fake data population completed!"
