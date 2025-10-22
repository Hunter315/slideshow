#!/usr/bin/env python3
"""
Headless camera test - no display window required
Just prints results to terminal
"""

import cv2
import face_recognition
import pickle
from pathlib import Path
import time

CAMERA_INDEX = 0
KNOWN_FACES_PATH = "known_faces.pkl"

print("=" * 60)
print("🎥 Camera Test (Headless)")
print("=" * 60)

# Test 1: Can we open the camera?
print("\n1️⃣ Opening camera...")
video_capture = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_V4L2)

if not video_capture.isOpened():
    print("❌ FAILED: Cannot open camera")
    exit(1)

print("✅ Camera opened")

# Test 2: Can we read frames?
print("\n2️⃣ Reading frame...")
ret, frame = video_capture.read()

if not ret or frame is None:
    print("❌ FAILED: Cannot read frames")
    video_capture.release()
    exit(1)

print(f"✅ Frame captured: {frame.shape[1]}x{frame.shape[0]} pixels")

# Test 3: Load known faces
print("\n3️⃣ Loading known faces...")
if not Path(KNOWN_FACES_PATH).exists():
    print("❌ No known faces found")
    print("   Upload photos with names first!")
    video_capture.release()
    exit(1)

with open(KNOWN_FACES_PATH, 'rb') as f:
    data = pickle.load(f)
    known_encodings = data['encodings']
    known_names = data['names']

unique_names = list(set(known_names))
print(f"✅ Loaded {len(known_encodings)} face samples")
print(f"   People: {', '.join(unique_names)}")

# Test 4: Face detection test
print("\n4️⃣ Testing face detection (10 frames)...")
print("   Position yourself in front of camera...")
print("")

faces_detected = 0
faces_recognized = {}

for i in range(10):
    ret, frame = video_capture.read()
    if not ret:
        print(f"   Frame {i+1}: Failed to read")
        continue

    print(f"   Frame {i+1}: Processing...", end=" ")

    # Resize for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Find faces
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    if len(face_locations) > 0:
        faces_detected += 1
        print(f"Found {len(face_locations)} face(s)", end=" ")

        # Try to recognize
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(
                known_encodings,
                face_encoding,
                tolerance=0.6
            )

            if True in matches:
                face_distances = face_recognition.face_distance(
                    known_encodings,
                    face_encoding
                )
                best_match_index = face_distances.argmin()
                if matches[best_match_index]:
                    name = known_names[best_match_index]
                    faces_recognized[name] = faces_recognized.get(name, 0) + 1
                    print(f"→ ✅ {name}!", end="")
            else:
                print(f"→ ❓ Unknown", end="")
        print()
    else:
        print("No faces")

    time.sleep(0.5)

video_capture.release()

# Summary
print("\n" + "=" * 60)
print("📊 Test Results:")
print("=" * 60)
print(f"Frames with faces detected: {faces_detected}/10")

if faces_recognized:
    print(f"\n✅ SUCCESS! Recognized:")
    for name, count in faces_recognized.items():
        print(f"   - {name}: {count} time(s)")
    print("\n🎉 Camera recognition is WORKING!")
elif faces_detected > 0:
    print(f"\n⚠️  Detected faces but didn't recognize anyone")
    print("   Try:")
    print("   - Upload clearer photo")
    print("   - Better lighting")
    print("   - Face camera directly")
else:
    print(f"\n❌ No faces detected")
    print("   Try:")
    print("   - Move closer to camera")
    print("   - Better lighting")
    print("   - Check camera angle")

print("=" * 60)
