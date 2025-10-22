#!/bin/bash
# Startup script for Party Slideshow + Auto Face Learning + Live Recognition
# Runs Node.js server, auto-enrollment, and live camera recognition

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "="
echo "="
echo "🎉 Party Slideshow with Face Recognition"
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

sleep 1

# Start live camera face recognition
echo "🎥 Starting live camera recognition..."
python3 face_recognition_service.py &
CAMERA_PID=$!
echo "   Camera recognition running (PID: $CAMERA_PID)"

echo ""
echo "="
echo "✅ All services running!"
echo "="

# Get IP address (works on both Linux and macOS)
if command -v hostname &> /dev/null && hostname -I &> /dev/null; then
    # Linux (Raspberry Pi)
    PI_IP=$(hostname -I | awk '{print $1}')
elif command -v ipconfig &> /dev/null; then
    # Windows
    PI_IP="localhost"
else
    # Fallback
    PI_IP="localhost"
fi

echo "📱 Guest upload: http://${PI_IP}:3000"
echo "🎬 Slideshow:    http://${PI_IP}:3000/slideshow"
echo "🔐 Admin panel:  http://${PI_IP}:3000/admin"
echo ""
echo "How it works:"
echo "1. Guests upload photos with their names"
echo "2. System automatically learns their faces"
echo "3. Camera recognizes them when they walk by"
echo "="
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Function to kill all processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    kill $NODE_PID $ENROLL_PID $CAMERA_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for all processes
wait
