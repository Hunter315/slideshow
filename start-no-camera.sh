#!/bin/bash
# Startup script without camera - For testing uploads and auto-enrollment only
# Use this until you plug in a camera

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "="
echo "="
echo "🎉 Party Slideshow (No Camera Mode)"
echo "="
echo "="

# Start Node.js server in background
echo "📸 Starting photo upload server..."
node dist/server.js &
NODE_PID=$!
echo "   Server running (PID: $NODE_PID)"

# Wait for server to initialize
sleep 2

# Start auto-enrollment service (learns faces from uploaded photos)
echo "🎭 Starting auto-enrollment (learns from uploads)..."
python3 auto_enroll.py &
ENROLL_PID=$!
echo "   Auto-enrollment running (PID: $ENROLL_PID)"

echo ""
echo "="
echo "✅ Services running!"
echo "="

# Get IP address (works on both Linux and macOS)
if command -v hostname &> /dev/null && hostname -I &> /dev/null; then
    # Linux (Raspberry Pi)
    PI_IP=$(hostname -I | awk '{print $1}')
else
    # Fallback
    PI_IP="localhost"
fi

echo "📱 Guest upload: http://${PI_IP}:3000"
echo "🎬 Slideshow:    http://${PI_IP}:3000/slideshow"
echo "🔐 Admin panel:  http://${PI_IP}:3000/admin"
echo ""
echo "ℹ️  Camera recognition disabled"
echo "   Guests can upload photos and system will learn their faces"
echo "   Run start-all.sh after plugging in camera for full recognition"
echo "="
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Function to kill both processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $NODE_PID $ENROLL_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for all processes
wait
