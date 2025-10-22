#!/bin/bash
# Quick Start Script for Luno AI
# This script sets up the environment and runs the application

echo "================================================"
echo "Luno AI - Quick Start"
echo "================================================"

# Check Python version
echo -e "\n1. Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "\n2. Creating virtual environment..."
    python3 -m venv venv
    echo "   ✅ Virtual environment created"
else
    echo -e "\n2. Virtual environment already exists"
fi

# Activate virtual environment
echo -e "\n3. Activating virtual environment..."
source venv/bin/activate
echo "   ✅ Virtual environment activated"

# Install dependencies
echo -e "\n4. Installing dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "   ✅ Dependencies installed"

# Check for .env file
echo -e "\n5. Checking configuration..."
if [ ! -f ".env" ]; then
    echo "   ⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "   ⚠️  Please edit .env and add your Google API key"
    echo "   Press Enter when ready to continue..."
    read
else
    echo "   ✅ .env file exists"
fi

# Run tests
echo -e "\n6. Running setup tests..."
python test_setup.py

# Check if tests passed
if [ $? -eq 0 ]; then
    echo -e "\n================================================"
    echo "Starting Streamlit application..."
    echo "================================================"
    echo ""
    streamlit run app.py
else
    echo -e "\n❌ Setup tests failed. Please fix the errors above."
    exit 1
fi
