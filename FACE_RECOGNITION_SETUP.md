# Face Recognition Setup for Raspberry Pi 4

This guide shows how to set up real-time face recognition that integrates with your slideshow app.

## Hardware Requirements

- Raspberry Pi 4 (4GB+ RAM recommended)
- Pi Camera Module v2/v3 OR USB webcam
- Optional: Google Coral USB Accelerator (for 10x faster performance)

## Software Installation on Pi 4

### 1. Install Python Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system packages for OpenCV
sudo apt install -y python3-pip python3-dev libatlas-base-dev libjasper-dev libqtgui4 libqt4-test libhdf5-dev

# Install cmake and dlib dependencies
sudo apt install -y cmake libopenblas-dev liblapack-dev libjpeg-dev

# Install Python packages (this may take 10-20 minutes on Pi 4)
pip3 install -r requirements.txt

# Enable camera (if using Pi Camera)
sudo raspi-config  # Interface Options → Camera → Enable
```

### 2. Enroll Known Faces

Create a directory with photos of people you want to recognize:

```bash
mkdir faces
# Add photos named as: john.jpg, sarah.jpg, etc.
```

Then enroll them:

```python
python3 face_recognition_service.py
```

Or enroll programmatically:

```python
from face_recognition_service import FaceRecognitionService

service = FaceRecognitionService()
service.enroll_face("faces/john.jpg", "John")
service.enroll_face("faces/sarah.jpg", "Sarah")
```

### 3. Run the Services

**Terminal 1 - Start Node.js server:**
```bash
cd ~/slideshow
node server-bundle.js  # Or ./slideshow-pi if using standalone
```

**Terminal 2 - Start face recognition:**
```bash
python3 face_recognition_service.py
```

## How It Works

1. **Camera captures video** at 30 FPS
2. **Python service processes every 2nd frame** (configurable)
3. **Detects faces** using HOG or CNN detector
4. **Recognizes faces** by comparing to enrolled encodings
5. **Sends notification** to Node.js server when someone is recognized
6. **Server can trigger** personalized slideshow or log attendance

## Configuration

Edit `face_recognition_service.py` to adjust:

```python
CAMERA_INDEX = 0              # USB camera index
RECOGNITION_THRESHOLD = 0.6   # Lower = stricter (0.4-0.7 recommended)
FRAME_SKIP = 2                # Process every Nth frame
SCALE_FACTOR = 0.5            # Resize for speed (0.25-1.0)
```

## Performance Optimization

### For Pi 4 (4GB):
- Default settings work well (~10-15 FPS)
- Use SCALE_FACTOR=0.5 for best balance

### For Pi 4 (8GB):
- Use SCALE_FACTOR=0.75 for better accuracy
- Set FRAME_SKIP=1 for real-time processing

### For faster performance:
- Add Google Coral USB Accelerator
- Use smaller image scale (SCALE_FACTOR=0.25)
- Process fewer frames (FRAME_SKIP=3 or 4)

## Troubleshooting

**Camera not detected:**
```bash
ls /dev/video*  # Check camera devices
v4l2-ctl --list-devices
```

**Low FPS:**
- Increase FRAME_SKIP
- Reduce SCALE_FACTOR
- Reduce camera resolution in code

**Poor recognition accuracy:**
- Ensure good lighting
- Enroll multiple photos per person
- Lower RECOGNITION_THRESHOLD
- Increase SCALE_FACTOR

**Out of memory:**
- Limit enrolled faces to <50 people
- Reduce camera resolution
- Close other applications

## Running on Boot

Create systemd service:

```bash
sudo nano /etc/systemd/system/face-recognition.service
```

Add:
```ini
[Unit]
Description=Face Recognition Service
After=network.target slideshow.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/slideshow
ExecStart=/usr/bin/python3 /home/pi/slideshow/face_recognition_service.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable face-recognition.service
sudo systemctl start face-recognition.service
```

## Next Steps

- Add database table for recognition events
- Create personalized slideshow based on recognized person
- Add web UI for enrolling faces via photo upload
- Implement WebSocket for real-time updates to slideshow
- Add statistics/attendance tracking
