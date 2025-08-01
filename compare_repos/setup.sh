#!/bin/bash

# JFrog Artifactory Repository Comparison Tool - Setup Script
# This script helps set up the Python environment and configuration

set -e

echo "🚀 Setting up JFrog Artifactory Repository Comparison Tool"
echo "========================================================="

# Check Python version
echo "📋 Checking Python version..."
python3 --version || {
    echo "❌ Python 3 is required but not found. Please install Python 3.7 or higher."
    exit 1
}

# Check if pip is available
echo "📦 Checking pip..."
python3 -m pip --version || {
    echo "❌ pip is required but not found. Please install pip."
    exit 1
}

# Install requirements
echo "📥 Installing Python dependencies..."
python3 -m pip install -r requirements.txt

# Create config from template if it doesn't exist
if [ ! -f "config.json" ]; then
    echo "⚙️  Creating configuration file from template..."
    cp config.template.json config.json
    echo "✅ Configuration template copied to config.json"
    echo "🔧 Please edit config.json with your Artifactory details before running the tool"
else
    echo "⚙️  Configuration file already exists: config.json"
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x compare_repos.py
chmod +x transfer_files.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Edit config.json with your Artifactory server details"
echo "   2. Set up authentication (tokens or environment variables)"
echo "   3. Run: python3 compare_repos.py --config config.json"
echo ""
echo "📚 For detailed usage instructions, see README.md"
echo ""
echo "🔍 Quick test of configuration:"
echo "   python3 compare_repos.py --help"
