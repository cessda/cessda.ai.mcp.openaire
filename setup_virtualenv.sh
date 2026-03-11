#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# Setup script for MCP OpenAIRE server with virtualenv

set -e

echo "=========================================="
echo "MCP OpenAIRE - Virtualenv Setup"
echo "=========================================="
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

echo "Detected Python version: $PYTHON_VERSION"

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo "Error: Python 3.10 or higher is required"
    exit 1
fi

echo "✓ Python version is compatible"
echo ""

# Create virtual environment
if [ -d "venv" ]; then
    echo "Virtual environment already exists."
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing virtual environment..."
        rm -rf venv
    else
        echo "Using existing virtual environment."
    fi
fi

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel -q
echo "✓ Package tools upgraded"
echo ""

# Install the package
echo "Installing mcp-openaire package..."
pip install -e . -q
echo "✓ Package installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.http.example .env
    echo "✓ .env file created"
    echo ""
    echo "Please edit .env file to configure your settings:"
    echo "  nano .env"
else
    echo ".env file already exists"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To activate the virtual environment:"
echo "  source venv/bin/activate"
echo ""
echo "To test the installation:"
echo "  python test_api.py"
echo ""
echo "To run the HTTP server:"
echo "  python -m mcp_openaire.server_http"
echo ""
echo "To deactivate the virtual environment:"
echo "  deactivate"
echo ""
echo "For server deployment, see DEPLOYMENT.md"
echo ""
