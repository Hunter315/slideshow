#!/bin/bash
# One-time setup script for Raspberry Pi
# Run this once to install everything

echo "🎉 Setting up Party Slideshow on Raspberry Pi"
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found"
    echo "   Run this script from the slideshow directory"
    exit 1
fi

echo ""
echo "📦 Installing Node.js dependencies..."
npm install

echo ""
echo "🐍 Installing Python dependencies..."
pip3 install -r requirements.txt

echo ""
echo "🔨 Building TypeScript..."
npm run build

echo ""
echo "📁 Creating directories..."
mkdir -p uploads

echo ""
echo "⚙️  Setting up environment..."
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
PORT=3000
ADMIN_API_KEY=change-me-to-something-secret
EOF
    echo "✅ Created .env file - REMEMBER TO CHANGE THE API KEY!"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🔧 Making scripts executable..."
chmod +x start-all.sh
chmod +x start-no-camera.sh

echo ""
echo "=============================================="
echo "✅ Setup complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. Edit .env and change ADMIN_API_KEY"
echo "   nano .env"
echo ""
echo "2. Test without camera:"
echo "   ./start-no-camera.sh"
echo ""
echo "3. Or with camera (after plugging it in):"
echo "   ./start-all.sh"
echo ""
echo "4. Visit: http://$(hostname -I | awk '{print $1}'):3000"
echo ""
