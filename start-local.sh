#!/bin/bash
# Startup script for LOCAL TESTING on Windows
# For Pi deployment, use start-all.sh

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "="
echo "="
echo "🎉 Party Slideshow with Face Recognition (LOCAL)"
echo "="
echo "="

# Start Node.js server in background
echo "📸 Starting photo upload server..."
node dist/server.js &
NODE_PID=$!
echo "   Server running (PID: $NODE_PID)"

echo ""
echo "="
echo "✅ Server running!"
echo "="
echo "📱 Guest upload: http://localhost:3000"
echo "🎬 Slideshow:    http://localhost:3000/slideshow"
echo "🔐 Admin panel:  http://localhost:3000/admin"
echo ""
echo "⚠️  Face recognition disabled on Windows"
echo "   (Python services only work on Raspberry Pi)"
echo "="
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Function to kill process on exit
cleanup() {
    echo ""
    echo "🛑 Stopping server..."
    kill $NODE_PID 2>/dev/null
    echo "✅ Server stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for process
wait
