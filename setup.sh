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
pip install -r execution/requirements.txt
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
echo "1. Edit .env file and add your API keys:"
echo "   nano .env  # or use your preferred editor"
echo ""
echo "2. Test ScanSan API (requires SCANSAN_API_KEY):"
echo "   python execution/scansan_api.py SW1A E1"
echo ""
echo "3. Test explanation generator (requires ANTHROPIC_API_KEY):"
echo "   python execution/generate_explanation.py"
echo ""
echo "4. Read the documentation:"
echo "   - README.md: Project overview"
echo "   - directives/MASTER_ORCHESTRATION.md: AI orchestration guide"
echo "   - Agents.md: Architecture details"
echo ""
echo "🤖 Start using the AI orchestrator by asking:"
echo '   "I'\''m a student looking for housing in London..."'
echo ""
echo "========================================="
