# Psychic Reading Feature Setup

## Overview

The psychic reading feature integrates with your facial recognition system to provide **completely touchless**, personalized, AI-generated psychic readings at your Halloween party. When guests approach the screen, spooky eyes appear and invite them to stare. After 4 seconds of continuous eye contact, the system automatically generates a mystical reading powered by Claude AI.

## Features

- **Fully Touchless**: No buttons, no mouse, no touching required - just stare into the eyes
- **Spooky Animated Eyes**: Hypnotic eyes that look around and blink, creating an immersive atmosphere
- **Auto-Trigger**: Automatically generates reading after 4 seconds of staring
- **Real-time Progress Bar**: Visual feedback showing how long they need to keep staring
- **Personalized Readings**: Claude AI generates unique readings using the guest's name
- **Unknown Guest Handling**: Shows mystical "cursed picture" message for unrecognized faces
- **Auto-Reset**: Interface resets after showing reading for 20 seconds

## Setup Instructions

### 1. Get an Anthropic API Key

1. Visit [console.anthropic.com](https://console.anthropic.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-ant-...`)

### 2. Configure Environment Variables

Edit your `.env` file and add your Anthropic API key:

```bash
PORT=3000
ADMIN_API_KEY=thisismysecretadminkey
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

**IMPORTANT**: Replace `sk-ant-your-actual-key-here` with your real API key from step 1.

### 3. Enroll Guest Faces

Before the party, ensure all guests' faces are enrolled in the system. You can do this by:

**Option A: Let guests upload photos themselves**
1. Direct guests to the photo upload page: `http://your-pi-ip:3000`
2. They upload a selfie with their name
3. The face recognition service will automatically learn their face

**Option B: Pre-enroll faces from a directory**
Uncomment and use the enrollment code in `face_recognition_service.py`:

```python
# Example: Enroll faces from a directory
for image_path in Path("faces").glob("*.jpg"):
    name = image_path.stem  # Use filename as name
    service.enroll_face(str(image_path), name)
```

### 4. Position the Camera

**CRITICAL**: The camera must be **hidden from view** but positioned to capture faces clearly.

- Mount camera near/above the screen
- Ensure it captures the area directly in front of the screen
- Test with `python3 face_recognition_service.py` to see the preview window
- Angle should capture faces at standing height

### 5. Start the Services

**Terminal 1 - Start the Node.js server:**
```bash
npm start
```

**Terminal 2 - Start the face recognition service:**
```bash
python3 face_recognition_service.py
```

### 6. Open the Psychic Reading Page

On the display screen, open a browser to: `http://localhost:3000/psychic`

**Recommended**: Use fullscreen mode (F11) for immersive experience.

## User Experience Flow

### For Recognized Guests:

1. **Idle State**: Screen shows "Awaiting a seeker of truth..." with mystical animations and stars
2. **Guest Approaches**: Hidden camera recognizes face (e.g., "Alice")
3. **Eyes Appear**: Spooky animated eyes appear with message: "Alice, Stare into my eyes to see your future"
4. **Progress Bar**: Bar fills as they continue staring, showing countdown (4s → 3s → 2s → 1s)
5. **Auto-Trigger**: At 4 seconds, automatically requests reading (no button click needed!)
6. **Loading**: "The spirits are consulting the cosmos..." with animated spinner
7. **Reading Display**: Personalized psychic reading appears in mystical text
   - Example: "Alice, the cosmic energies swirl around you tonight. A mysterious stranger will cross your path beneath the harvest moon, bringing unexpected laughter and mischief..."
8. **Auto-Reset**: After 20 seconds, returns to idle state for next guest

### For Unknown Guests:

1. **Idle State**: "Awaiting a seeker of truth..."
2. **Unknown Face Detected**: Camera sees someone not in the database
3. **Spooky Eyes + Warning**: Eyes appear with message:
   - "⚠️ The spirits do not know you ⚠️"
   - "You must first take a cursed picture to unlock the mystical realm"
   - Link to upload page: "Enter the Portal"
4. **Auto-Reset**: Returns to idle when they walk away

### If No One is Detected:

- Returns to idle state automatically
- Progress resets if person walks away mid-stare

## How It Works (Technical)

### Face Recognition Flow

1. **Python Service**: `face_recognition_service.py` continuously captures video
2. **Recognition Events**: Every ~2 seconds when same face detected, POSTs to `/api/recognition`
3. **Backend Tracking**: Server stores each event in `recognition_events` table
4. **Duration Calculation**: Server calculates continuous presence by looking at events in last 10 seconds

### Stare Duration Tracking

The `/api/recognition/current` endpoint returns:
```json
{
  "recognized": true,
  "personName": "Alice",
  "stareDuration": 3500,  // milliseconds of continuous presence
  "eventCount": 7         // number of recognition events in last 10 seconds
}
```

### Frontend Auto-Trigger Logic

- Frontend polls `/api/recognition/current` every 500ms (twice per second)
- Updates progress bar based on `stareDuration`
- When `stareDuration >= 4000ms`: automatically calls `/api/readings/request`
- Reading generated once per "session" (won't spam if they keep staring)

## API Endpoints

### GET /api/recognition/current
Returns the most recently recognized person with stare duration.

**Response (recognized, staring for 3.5s):**
```json
{
  "recognized": true,
  "personName": "Alice",
  "timestamp": 1729728708,
  "stareDuration": 3500,
  "eventCount": 7
}
```

**Response (no one detected):**
```json
{
  "recognized": false,
  "stareDuration": 0
}
```

### POST /api/readings/request
Generates a new psychic reading for a person.

**Request:**
```json
{
  "personName": "Alice"
}
```

**Response:**
```json
{
  "readingId": "uuid-here",
  "personName": "Alice",
  "readingText": "Alice, the cosmic energies swirl around you tonight...",
  "createdAt": 1729728708000
}
```

### GET /api/readings/:readingId
Retrieves a specific reading by ID.

**Response:**
```json
{
  "readingId": "uuid-here",
  "personName": "Alice",
  "readingType": "psychic",
  "readingText": "Alice, the cosmic energies swirl around you tonight...",
  "createdAt": 1729728708000
}
```

## Database Schema

### recognition_events Table
Stores every time a face is recognized (used to calculate stare duration).

| Column      | Type    | Description                          |
|-------------|---------|--------------------------------------|
| id          | INTEGER | Auto-incrementing primary key        |
| person_name | TEXT    | Name of recognized person            |
| timestamp   | INTEGER | Unix timestamp from Python service   |
| created_at  | INTEGER | When event was stored in database    |

### readings Table
Stores all generated psychic readings.

| Column       | Type    | Description                        |
|--------------|---------|-------------------------------------|
| id           | INTEGER | Auto-incrementing primary key      |
| reading_id   | TEXT    | UUID for the reading               |
| person_name  | TEXT    | Who the reading was for            |
| reading_type | TEXT    | Type of reading (default: psychic) |
| reading_text | TEXT    | The actual reading content         |
| created_at   | INTEGER | When reading was generated         |

## Customization

### Modify Stare Threshold

Change how long guests must stare (default 4 seconds):

**Backend** (`src/server.ts` line 244):
```typescript
const tenSecondsAgo = Date.now() - 10000; // Recognition event window (keep at 10s)
```

**Frontend** (`public/psychic.html` line 371):
```javascript
const STARE_THRESHOLD = 4000; // Change to desired milliseconds (e.g., 3000 for 3 seconds)
```

### Modify Reading Display Time

Change how long the reading is shown (default 20 seconds):

In `public/psychic.html` line 447:
```javascript
setTimeout(() => {
    showIdleState();
}, 20000); // Change to desired milliseconds
```

### Modify Polling Frequency

Change how often the frontend checks for face recognition (default 500ms):

In `public/psychic.html` line 493:
```javascript
pollInterval = setInterval(checkForRecognition, 500); // Change to desired milliseconds
```

**Note**: Faster polling = smoother progress bar, but more server requests.

### Modify Reading Prompt

Edit the Claude prompt in `src/server.ts` around line 292:

```typescript
content: `You are a mystical fortune teller at a Halloween party. Give ${personName} a creative, entertaining, and slightly spooky psychic reading. The reading should be personalized with their name, mysterious but fun, and appropriate for a party atmosphere. Keep it to 3-4 sentences. Make it feel authentic and engaging, with references to cosmic energies, fate, or mysterious forces. Do not use any formatting or special characters - just plain text.`
```

### Modify Theme Colors

Edit `public/psychic.html` CSS:

- **Background gradient**: Line 16 - `background: linear-gradient(...)`
- **Glow color**: Change `rgba(138, 43, 226, ...)` (purple) throughout
- **Eye pupil color**: Line 122 - `background: radial-gradient(...)`
- **Progress bar**: Line 175 - `background: linear-gradient(...)`

### Customize Eye Animations

- **Blink frequency**: Line 132-135 - `animation: blink 6s infinite` (change 6s)
- **Look around speed**: Line 113-117 - animation timing
- **Eye size**: Line 102-105 - `width` and `height` properties

## Troubleshooting

### "Failed to generate reading"
- Check that `ANTHROPIC_API_KEY` is set correctly in `.env`
- Verify your API key is valid and has credits
- Check server logs for authentication errors
- Ensure internet connection is working

### Progress bar fills but no reading appears
- Check browser console for errors (F12)
- Verify Claude API is responding (check server logs)
- Test manually: `curl -X POST http://localhost:3000/api/readings/request -H "Content-Type: application/json" -d '{"personName": "Test"}'`

### Faces not being recognized
- Ensure `face_recognition_service.py` is running
- Check that faces are enrolled (verify `known_faces.pkl` exists)
- Verify camera is working with the preview window
- Adjust `FRAME_SKIP` and `SCALE_FACTOR` in Python service for better performance

### Page shows "Awaiting a seeker..." forever
- Check face recognition service is sending events to `/api/recognition`
- Look at server logs for recognition events
- Test manually: `curl -X POST http://localhost:3000/api/recognition -H "Content-Type: application/json" -d '{"name": "Test", "timestamp": 1729728708}'`
- Then check: `curl http://localhost:3000/api/recognition/current`

### Progress bar resets before reaching 4 seconds
- Python service may not be sending events frequently enough
- Reduce `FRAME_SKIP` in `face_recognition_service.py` (default 2)
- Ensure camera has clear view of face
- Check that person is staying still and looking at screen

### Stare duration is inaccurate
- Backend only counts events from last 10 seconds
- If Python service throttles notifications (5s cooldown), disable for psychic reading
- Check `face_recognition_service.py` line 212-215 throttling logic

## Performance Tuning

### For Raspberry Pi Zero W
- Increase stare threshold to 5-6 seconds (gives more time for processing)
- Increase frontend poll interval to 1000ms
- In Python service: increase `FRAME_SKIP` to 3-4

### For Raspberry Pi 4
- Default settings work well
- Can decrease poll interval to 300ms for ultra-smooth progress bar
- Can reduce stare threshold to 3 seconds for faster experience

## Cost Considerations

Claude API charges per token. Approximate costs:

- **Per Reading**: ~$0.001-0.002 (depends on prompt + response length)
- **100 readings**: ~$0.10-0.20
- **Party with 50 guests (2 readings each)**: ~$0.10-0.20

The readings use `claude-3-5-sonnet-20241022` model with 500 max tokens.

## Security Notes

- **API Key**: Keep your `ANTHROPIC_API_KEY` secret. Never commit it to git.
- **Rate Limiting**: Consider adding rate limiting to prevent abuse
- **HTTPS**: Use HTTPS in production to protect API key in transit
- **Local Network**: Best used on a local network (not exposed to internet)
- **Camera Privacy**: Inform guests that a hidden camera is being used for face recognition

## Full System Startup Checklist

1. ✅ All guest faces enrolled in system
2. ✅ `.env` file has valid `ANTHROPIC_API_KEY`
3. ✅ Camera positioned to capture faces (hidden from view)
4. ✅ Node.js server running: `npm start`
5. ✅ Face recognition service running: `python3 face_recognition_service.py`
6. ✅ Browser open to `/psychic` page in fullscreen mode
7. ✅ Internet connection active (for Claude API calls)
8. ✅ Tested with a known face to verify auto-trigger works

## Tips for Best Experience

- **Lighting**: Ensure good lighting on guests' faces for reliable recognition
- **Camera Height**: Position at eye-level for best face detection
- **Screen Size**: Larger screen = more immersive (24" minimum recommended)
- **Audio**: Consider adding spooky background music or sounds
- **Ambiance**: Dim room lighting for more mystical atmosphere
- **Testing**: Test with multiple people before the party to tune stare threshold

Enjoy your mystical, touchless Halloween party experience! 🔮✨👁️
