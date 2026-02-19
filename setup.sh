#!/bin/bash

# Setup script for Generador de Recursos Evangelísticos
# This script sets up both backend and frontend environments

set -e  # Exit on error

echo "=========================================="
echo "Generador de Recursos Evangelísticos"
echo "Setup Script"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Check Node version
echo "Checking Node.js version..."
node_version=$(node --version 2>&1)
echo "Found Node.js $node_version"

# Check LibreOffice
echo "Checking LibreOffice installation..."
if command -v libreoffice &> /dev/null; then
    echo "✓ LibreOffice is installed"
else
    echo "⚠ WARNING: LibreOffice not found. Please install it for PDF generation."
    echo "  Ubuntu/Debian: sudo apt-get install libreoffice"
    echo "  macOS: brew install --cask libreoffice"
fi

echo ""
echo "=========================================="
echo "Setting up Backend"
echo "=========================================="
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
else
    echo ".env file already exists"
fi

echo "✓ Backend setup complete"

cd ..

echo ""
echo "=========================================="
echo "Setting up Frontend"
echo "=========================================="
cd frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
else
    echo ".env file already exists"
fi

echo "✓ Frontend setup complete"

cd ..

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To start the application:"
echo ""
echo "1. Start the backend (in one terminal):"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "2. Start the frontend (in another terminal):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. Open your browser to: http://localhost:5173"
echo ""
