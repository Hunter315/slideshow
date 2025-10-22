# Complete Setup Guide - Raspberry Pi 4 Only

This guide sets up everything on a single Raspberry Pi 4:
- Photo upload and slideshow server
- Real-time face recognition camera
- Auto-start on boot

## Hardware Needed

- Raspberry Pi 4 (4GB or 8GB RAM)
- MicroSD card (16GB+)
- Pi Camera Module v2/v3 OR USB webcam
- Power supply
- Optional: Monitor for slideshow display

## Step 1: Prepare Your Pi 4

### Initial Setup

1. **Install Raspberry Pi OS** (Lite or Desktop)
   - Use Raspberry Pi Imager
   - Enable SSH if needed
   - Set hostname to something memorable (e.g., "party-pi")

2. **Boot up and update:**
```bash
sudo apt update && sudo apt upgrade -y
```

3. **Get your Pi's IP address** (for guests to access from phones):
```bash
hostname -I
```
Write this down! Example: `192.168.1.100`

## Step 2: Install Node.js (for slideshow server)

```bash
# Install Node.js 18 (ARM64 compatible)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify
node --version
npm --version
```

## Step 3: Install Python Dependencies (for face recognition)

```bash
# Install system packages
sudo apt install -y python3-pip python3-dev libatlas-base-dev \
    cmake libopenblas-dev liblapack-dev libjpeg-dev \
    python3-opencv

# Install Python libraries (takes 10-15 minutes)
pip3 install face-recognition requests numpy

# Enable camera if using Pi Camera
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable
```

## Step 4: Transfer Your Application

### Option A: From USB Drive

On your Windows machine, copy these to USB:
- `dist/` folder (compiled TypeScript)
- `package.json`
- `face_recognition_service.py`
- `requirements.txt`
- `public/` folder (if you have HTML/CSS files)
- `deploy-pi.sh`

On Pi 4:
```bash
cd ~
mkdir slideshow
cp -r /media/pi/*/dist slideshow/
cp -r /media/pi/*/public slideshow/
cp /media/pi/*/package.json slideshow/
cp /media/pi/*/*.py slideshow/
cp /media/pi/*/*.txt slideshow/
```

### Option B: From GitHub (if you pushed changes)

```bash
cd ~
git clone https://github.com/Hunter315/slideshow.git
cd slideshow
git checkout no-node  # or main
npm install --production
```

## Step 5: Setup the Node.js Server

```bash
cd ~/slideshow

# Install production dependencies only
npm install --omit=dev

# Create necessary directories
mkdir -p uploads

# Create .env file
nano .env
```

Add to `.env`:
```
PORT=3000
ADMIN_API_KEY=your-secret-key-here
```

**Test the server:**
```bash
node dist/server.js
```

You should see:
```
🎉 Party Photo Server is running!
📸 Guest Upload:    http://192.168.1.100:3000
🔐 Admin Panel:     http://192.168.1.100:3000/admin
🖼️  Slideshow:       http://192.168.1.100:3000/slideshow
```

Visit that URL from your phone to test! Press `Ctrl+C` to stop.

## Step 6: Enroll Known Faces

Create a folder with photos of people:

```bash
cd ~/slideshow
mkdir faces
```

**Add photos via USB or take with camera:**
- Name files as: `john.jpg`, `sarah.jpg`, etc.
- One face per photo works best
- Good lighting, front-facing

**Enroll them:**
```python
python3 << EOF
from face_recognition_service import FaceRecognitionService
import os

service = FaceRecognitionService()

# Enroll all faces from the faces/ directory
for filename in os.listdir("faces"):
    if filename.endswith((".jpg", ".jpeg", ".png")):
        name = os.path.splitext(filename)[0]
        service.enroll_face(f"faces/{filename}", name)
        print(f"Enrolled: {name}")
EOF
```

## Step 7: Create Startup Script

Create a script to run both services:

```bash
nano ~/slideshow/start-all.sh
```

Add:
```bash
#!/bin/bash
cd /home/pi/slideshow

# Start Node.js server in background
node dist/server.js &
NODE_PID=$!
echo "Started Node.js server (PID: $NODE_PID)"

# Wait for server to start
sleep 3

# Start face recognition
python3 face_recognition_service.py &
PYTHON_PID=$!
echo "Started face recognition (PID: $PYTHON_PID)"

# Wait for both processes
wait
```

Make it executable:
```bash
chmod +x ~/slideshow/start-all.sh
```

**Test it:**
```bash
./start-all.sh
```

## Step 8: Auto-Start on Boot

Create systemd service:

```bash
sudo nano /etc/systemd/system/party-slideshow.service
```

Add:
```ini
[Unit]
Description=Party Slideshow with Face Recognition
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/slideshow
ExecStart=/home/pi/slideshow/start-all.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl enable party-slideshow.service
sudo systemctl start party-slideshow.service

# Check status
sudo systemctl status party-slideshow.service

# View logs
journalctl -u party-slideshow.service -f
```

## Step 9: Guest Access

Give your guests this URL (replace with your Pi's IP):
```
http://192.168.1.100:3000
```

They can:
- Upload photos from their phones
- Add their name and caption
- View the slideshow

## Step 10: Slideshow Display (Optional)

If you have a monitor connected to the Pi:

```bash
# Install a browser if using Pi OS Lite
sudo apt install -y chromium-browser

# Open slideshow in fullscreen kiosk mode
chromium-browser --kiosk --app=http://localhost:3000/slideshow
```

## Troubleshooting

### Server won't start
```bash
# Check if port 3000 is already in use
sudo lsof -i :3000

# Check logs
journalctl -u party-slideshow.service -n 50
```

### Camera not detected
```bash
# List video devices
ls /dev/video*

# Test camera
raspistill -o test.jpg  # For Pi Camera
```

### Face recognition is slow
Edit `face_recognition_service.py`:
- Increase `FRAME_SKIP` to 3 or 4
- Decrease `SCALE_FACTOR` to 0.25
- Reduce camera resolution

### Can't access from phone
```bash
# Check firewall
sudo ufw status

# Make sure Pi and phone are on same WiFi network
```

## Performance Tips

**Pi 4 4GB:**
- Can handle 10-20 simultaneous uploads
- ~10-15 FPS face recognition
- Works great for parties up to 100 people

**Pi 4 8GB:**
- Can handle 50+ simultaneous uploads
- ~15-20 FPS face recognition
- Smooth experience for larger events

## What Happens Now

1. **Guest arrives** → Pi camera recognizes them
2. **Console logs:** "🎯 Face recognized: John"
3. **Guest uploads photo** from their phone
4. **Photo appears** in slideshow automatically
5. **Future:** Show John's photos when he's recognized

## Next Steps

- Add WebSocket for real-time slideshow updates
- Create admin panel for managing enrolled faces
- Auto-tag uploaded photos with recognized faces
- Generate party attendance report
- Add photo filters/effects

Your Pi 4 is now a complete party photo and face recognition system!
