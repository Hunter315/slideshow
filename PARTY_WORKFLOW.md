# Party Face Recognition Workflow

This is the **automatic** workflow where guests teach the system their faces during the party, and the camera can recognize them later!

## How It Works

```
┌──────────────────────────────────────────────────────────────┐
│                    DURING THE PARTY                          │
└──────────────────────────────────────────────────────────────┘

1. Guest arrives at party
   ↓
2. Scans QR code → uploads selfie with their name
   ↓
3. Auto-enrollment service LEARNS their face
   ↓
4. Camera service reloads faces (within ~30 seconds)
   ↓
5. Guest walks by camera → RECOGNIZED! 🎉
   ↓
6. Name appears on screen
   ↓
7. Server logs: "🎯 Face recognized: John at 8:45 PM"
```

## Setup (One Time, Before Party)

### 1. Install Dependencies

```bash
cd ~/slideshow
npm install
pip3 install -r requirements.txt
```

### 2. Build TypeScript

```bash
npm run build
```

### 3. Create .env File

```bash
nano .env
```

Add:
```
PORT=3000
ADMIN_API_KEY=your-secret-key-here
```

Save: `Ctrl+O`, `Enter`, `Ctrl+X`

### 4. Start Everything

```bash
chmod +x start-all.sh
./start-all.sh
```

You'll see:
```
🎉 Party Slideshow with Face Recognition
============================================================
📸 Starting photo upload server...
   Server running (PID: 1234)
🎭 Starting auto-enrollment (learns from uploads)...
   Auto-enrollment running (PID: 1235)
🎥 Starting live camera recognition...
   Camera recognition running (PID: 1236)

✅ All services running!
============================================================
📱 Guest upload: http://192.168.1.100:3000
🎬 Slideshow:    http://192.168.1.100:3000/slideshow
🔐 Admin panel:  http://192.168.1.100:3000/admin

How it works:
1. Guests upload photos with their names
2. System automatically learns their faces
3. Camera recognizes them when they walk by
============================================================
```

## During the Party

### For Guests

1. **Scan QR code** or visit `http://<pi-ip>:3000`
2. **Take/upload selfie**
3. **Enter their name** (important!)
4. **Upload**

That's it! The system now knows their face.

### What Happens Automatically

```
📸 Guest uploads photo with name "Sarah"
   ↓
🎭 Auto-enrollment service:
   "📸 Attempting to enroll: Sarah from abc123.jpg"
   "✅ Newly enrolled: Sarah"
   ↓
🎥 Camera service (within 30 seconds):
   "🔄 New faces detected, reloading..."
   "📚 Loaded 5 face samples for 3 people"
   "✅ Learned 1 new person/people!"
   ↓
👤 Sarah walks by camera:
   "Recognized: Sarah"
   [Display shows: Green box with "Sarah" label]
```

### What You See

**In the terminal where you ran `./start-all.sh`:**

```
📸 Attempting to enroll: John from photo1.jpg
   ✅ Newly enrolled: John

📸 Attempting to enroll: Sarah from photo2.jpg
   ✅ Newly enrolled: Sarah

🔄 New faces detected, reloading...
📚 Loaded 2 face samples for 2 people
   People: John, Sarah
✅ Learned 2 new person/people!

Recognized: John
Recognized: Sarah
Recognized: John
```

**On the camera display (if monitor connected):**

- Green boxes around recognized faces
- Names displayed below faces
- Red boxes for unknown people

## After the Party

### View Who Was Recognized

All recognition events are logged to the console with timestamps:

```bash
grep "Face recognized" /path/to/logs
```

Or check the Node.js server logs.

### Extract Face Data

The system stores:
- `known_faces.pkl` - All learned face encodings
- `photos.db` - Database with guest names and photo metadata

### Generate Reports (Future Feature)

You could build:
- "Who attended based on uploads"
- "Who was recognized by camera"
- "Photos featuring each person"

## Testing Before the Party

### 1. Upload Test Photo

Visit `http://<pi-ip>:3000` and upload a selfie with your name.

### 2. Watch Terminal

You should see:
```
📸 Attempting to enroll: YourName from xyz.jpg
   ✅ Newly enrolled: YourName
```

Then within 30 seconds:
```
🔄 New faces detected, reloading...
✅ Learned 1 new person/people!
```

### 3. Walk in Front of Camera

You should see:
```
Recognized: YourName
```

And on screen: Your name in a green box!

## Troubleshooting

### "No face detected - skipping enrollment"

**Cause:** Photo doesn't have a clear face

**Solution:**
- Guest should take a selfie (not group photo)
- Ensure good lighting
- Face should be front-facing
- Photo should be reasonably close-up

### Guest uploads but isn't learned

**Check:**
1. Did they enter their name in the form?
   ```bash
   # Check database
   sqlite3 photos.db "SELECT photo_id, guest_name FROM photos;"
   ```
2. Is auto-enrollment running?
   ```bash
   ps aux | grep auto_enroll
   ```
3. Check logs for errors

### Camera doesn't recognize after upload

**Wait:** Camera reloads faces every ~30 seconds (60 frames × frame_skip)

**Force reload:** Restart camera service
```bash
# Kill camera only
pkill -f face_recognition_service
# Restart just camera
python3 face_recognition_service.py &
```

### Multiple people upload, but only first is recognized

**Cause:** Camera hasn't reloaded yet

**Solution:** Wait 30 seconds between uploads for testing, or increase `reload_check_interval` in `face_recognition_service.py` to check more frequently

### Guest uploads photo without name

**Result:** Auto-enrollment skips it (no name = can't learn who they are)

**Prevention:** Make the name field required in the upload form (frontend change)

## Advanced Configuration

### Adjust Reload Frequency

Edit `face_recognition_service.py`:

```python
reload_check_interval = 30  # Check every 30 frames (default)
reload_check_interval = 10  # Check every 10 frames (more responsive)
```

Lower = more responsive but slightly more CPU usage

### Enrollment Confidence

Edit `auto_enroll.py`:

```python
MIN_CONFIDENCE_FOR_ENROLLMENT = 0.8  # Higher = stricter quality
```

Currently unused but available for future filtering

### Recognition Threshold

Edit `face_recognition_service.py`:

```python
RECOGNITION_THRESHOLD = 0.6  # Default
RECOGNITION_THRESHOLD = 0.5  # Stricter (fewer false positives)
RECOGNITION_THRESHOLD = 0.7  # Looser (more forgiving)
```

## File Structure

```
slideshow/
├── auto_enroll.py              # Watches uploads, learns faces
├── face_recognition_service.py # Camera recognition
├── start-all.sh                # Starts everything
├── uploads/                    # Guest photos (auto-created)
├── known_faces.pkl             # Learned faces (auto-created)
├── photos.db                   # Database (auto-created)
└── .env                        # Your config
```

## Performance

**Per Guest:**
- Upload photo: ~1 second
- Face enrollment: ~1-3 seconds
- Face reload: ~0.5 seconds
- Recognition in live video: ~real-time

**Scalability:**
- Raspberry Pi 4 (4GB): ~50 guests, smooth
- Raspberry Pi 4 (8GB): ~100+ guests, excellent
- Raspberry Pi Zero W: Not recommended (too slow for face recognition)

## Summary

**You need to do:**
1. Run `./start-all.sh` before party
2. Display QR code for guests
3. Let it run!

**System does automatically:**
1. Receives uploads from guests
2. Learns faces from photos with names
3. Reloads camera recognition with new faces
4. Recognizes people as they walk by
5. Logs all recognition events

**No manual intervention needed during the party!** 🎉
