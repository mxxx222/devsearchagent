#!/bin/bash
# AI Search Dashboard - Project Restoration Script

echo "🚀 AI Search Dashboard - Project Restoration"
echo "=============================================="

# Check if backup exists
if [ ! -d "project_backup_20251023_082557" ]; then
    echo "❌ Backup directory not found!"
    echo "Please ensure project_backup_20251023_082557 exists"
    exit 1
fi

echo "📁 Found backup directory: project_backup_20251023_082557"

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r project_backup_20251023_082557/requirements.txt

# Copy configuration
echo "⚙️ Setting up configuration..."
cp project_backup_20251023_082557/config.env .

# Create database directory
echo "🗄️ Setting up database..."
mkdir -p data
cp project_backup_20251023_082557/trending_data.db . 2>/dev/null || echo "Database will be created on first run"

# Set up environment variables
echo "🔑 Loading environment variables..."
source config.env

# Test the application
echo "🧪 Testing application..."
python -c "
import sys
sys.path.insert(0, '.')
try:
    from app import app
    print('✅ Application imports successfully')
except Exception as e:
    print(f'❌ Import error: {e}')
"

echo ""
echo "🎉 Project restoration complete!"
echo ""
echo "To start the application:"
echo "1. source venv/bin/activate"
echo "2. source config.env"
echo "3. python app.py"
echo ""
echo "Access the dashboard at: http://localhost:8080"
echo ""
echo "For automation:"
echo "1. python topic_automation.py --once  # Test"
echo "2. python topic_automation.py         # Start automation"
echo ""
echo "📚 See PROJECT_SAVE_SUMMARY.md for complete documentation"
