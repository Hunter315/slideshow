#!/bin/bash
# Startup script for Party Slideshow + Face Recognition
# Runs both Node.js server and Python face recognition service

cd /home/pi/slideshow

echo "🎉 Starting Party Slideshow System..."

# Start Node.js server in background
echo "📸 Starting photo server..."
node dist/server.js &
NODE_PID=$!
echo "   Node.js server started (PID: $NODE_PID)"

# Wait for server to initialize
sleep 3

# Start face recognition
echo "🎯 Starting face recognition..."
python3 face_recognition_service.py &
PYTHON_PID=$!
echo "   Face recognition started (PID: $PYTHON_PID)"

echo ""
echo "✅ All services running!"
echo "📱 Share this URL with guests: http://$(hostname -I | awk '{print $1}'):3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to kill both processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $NODE_PID $PYTHON_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for both processes
wait
