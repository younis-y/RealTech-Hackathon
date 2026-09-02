#!/bin/bash
# Veo Setup Script
# Initializes the 3-layer architecture environment

set -e  # Exit on error

echo "========================================="
echo "Veo 3-Layer Architecture Setup"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Found Python $PYTHON_VERSION"
echo ""

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.template .env
    echo "✅ .env file created"
    echo "⚠️  IMPORTANT: Edit .env and add your API keys before running scripts"
else
    echo "✅ .env file already exists"
fi
echo ""

# Ensure .tmp directory exists
if [ ! -d ".tmp" ]; then
    echo "Creating .tmp directory..."
    mkdir -p .tmp
    echo "✅ .tmp directory created"
else
    echo "✅ .tmp directory already exists"
fi
echo ""

# Verify directory structure
echo "Verifying directory structure..."
REQUIRED_DIRS=("directives" "execution" ".tmp")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✅ $dir/"
    else
        echo "  ❌ $dir/ missing"
        mkdir -p "$dir"
        echo "     Created $dir/"
    fi
done
echo ""

# Count files
DIRECTIVE_COUNT=$(ls -1 directives/*.md 2>/dev/null | wc -l)
SCRIPT_COUNT=$(ls -1 execution/*.py 2>/dev/null | wc -l)

echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "📁 Directory Structure:"
echo "   Directives: $DIRECTIVE_COUNT files"
echo "   Execution scripts: $SCRIPT_COUNT files"
echo "   Temp directory: .tmp/"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Optional: edit .env to add API keys. The ranking runs without any"
echo "   key; ANTHROPIC_API_KEY buys explanations, TFL_APP_KEY buys real"
echo "   commute times."
echo ""
echo "2. Run the pipeline:"
echo "   python demo_pipeline.py --persona student --budget 1200 --type rent \\"
echo "     --destination UCL --no-explanations"
echo ""
echo "3. Read the documentation:"
echo "   - README.md: what the project does and where each number comes from"
echo "   - directives/: the Markdown SOPs the orchestration layer reads"
echo ""
echo "========================================="
