# Simple Setup Guide - Auto-Learning Face Recognition

## What This Does

1. **Guests upload selfies** with their names during the party
2. **System automatically learns** their faces from the photos
3. **Camera recognizes them** when they walk by later
4. **Everything is automatic** - no manual work during the party!

## One-Time Setup on Raspberry Pi

### 1. Install Everything

```bash
cd ~/slideshow
npm install
pip3 install -r requirements.txt
npm run build
```

### 2. Configure

```bash
nano .env
```

Add:
```
PORT=3000
ADMIN_API_KEY=your-secret-key
```

Save: `Ctrl+O`, `Enter`, `Ctrl+X`

### 3. Start Everything

```bash
chmod +x start-all.sh
./start-all.sh
```

## That's It!

Share this URL with guests:
```
http://<your-pi-ip>:3000
```

## How It Works

**Guest uploads selfie "Hi, I'm Sarah!"**
```
📸 Attempting to enroll: Sarah from photo123.jpg
   ✅ Newly enrolled: Sarah
```

**30 seconds later...**
```
🔄 New faces detected, reloading...
✅ Learned 1 new person/people!
```

**Sarah walks by the camera:**
```
Recognized: Sarah
[Green box with "Sarah" appears on screen]
```

## Files You Can Ignore

These are for the **old manual workflow** (where you pre-enroll faces):
- `enroll_faces.py` - Not needed for automatic mode
- `photo_processor.py` - Not needed for automatic mode
- `AUTO_FACE_RECOGNITION.md` - Old manual workflow docs
- `QUICK_START.md` - Old manual workflow docs

## Files You Need

- **`auto_enroll.py`** - Automatically learns from uploads
- **`face_recognition_service.py`** - Live camera recognition
- **`start-all.sh`** - Starts everything
- **`PARTY_WORKFLOW.md`** - Full documentation

## Troubleshooting

**Camera doesn't recognize guest:**
- Wait 30 seconds after upload for faces to reload
- Guest must enter their name when uploading
- Photo must have a clear face (selfie works best)

**Service won't start:**
```bash
# Check if already running
ps aux | grep "node\|python"

# Kill old processes
pkill -f "node\|python"

# Try again
./start-all.sh
```

**Need more help:**
See `PARTY_WORKFLOW.md` for complete guide.
