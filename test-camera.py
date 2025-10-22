#!/usr/bin/env python3
"""
Quick camera test script
Tests if camera is working and can detect/recognize faces
"""

import cv2
import face_recognition
import pickle
from pathlib import Path

CAMERA_INDEX = 0  # Use video0 with V4L2 backend
KNOWN_FACES_PATH = "known_faces.pkl"

def test_camera():
    print("=" * 60)
    print("🎥 Camera Test")
    print("=" * 60)

    # Test 1: Can we open the camera?
    print("\n1️⃣ Testing camera connection...")
    # Use V4L2 backend explicitly (avoids GStreamer issues on Pi)
    video_capture = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_V4L2)

    if not video_capture.isOpened():
        print("❌ FAILED: Cannot open camera")
        print("   Try:")
        print("   - Check if camera is plugged in: ls /dev/video*")
        print("   - Try different index: CAMERA_INDEX=1 in script")
        return False

    print("✅ Camera opened successfully")

    # Test 2: Can we read frames?
    print("\n2️⃣ Testing frame capture...")
    ret, frame = video_capture.read()

    if not ret or frame is None:
        print("❌ FAILED: Cannot read frames from camera")
        video_capture.release()
        return False

    print(f"✅ Frame captured: {frame.shape[1]}x{frame.shape[0]} pixels")

    # Test 3: Load known faces
    print("\n3️⃣ Loading known faces...")
    if not Path(KNOWN_FACES_PATH).exists():
        print("❌ No known faces found (known_faces.pkl missing)")
        print("   Upload photos with names first!")
        video_capture.release()
        return False

    with open(KNOWN_FACES_PATH, 'rb') as f:
        data = pickle.load(f)
        known_encodings = data['encodings']
        known_names = data['names']

    unique_names = list(set(known_names))
    print(f"✅ Loaded {len(known_encodings)} face samples")
    print(f"   People: {', '.join(unique_names)}")

    # Test 4: Live face detection
    print("\n4️⃣ Starting live face detection...")
    print("   Position yourself in front of the camera")
    print("   Press 'q' to quit, 's' to save a test image")
    print("   Window should open showing camera feed")
    print("")

    frame_count = 0
    faces_detected = 0
    faces_recognized = 0

    try:
        while True:
            ret, frame = video_capture.read()
            if not ret:
                print("Failed to grab frame")
                break

            frame_count += 1

            # Process every 5th frame for speed
            if frame_count % 5 == 0:
                # Resize for faster processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
                rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

                # Find faces
                face_locations = face_recognition.face_locations(rgb_frame)
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

                if len(face_locations) > 0 and faces_detected == 0:
                    print(f"👤 Detected {len(face_locations)} face(s)!")
                    faces_detected = len(face_locations)

                # Recognize faces
                for face_encoding, face_location in zip(face_encodings, face_locations):
                    matches = face_recognition.compare_faces(
                        known_encodings,
                        face_encoding,
                        tolerance=0.6
                    )

                    name = "Unknown"
                    if True in matches:
                        face_distances = face_recognition.face_distance(
                            known_encodings,
                            face_encoding
                        )
                        best_match_index = face_distances.argmin()
                        if matches[best_match_index]:
                            name = known_names[best_match_index]
                            if faces_recognized == 0:
                                print(f"✅ RECOGNIZED: {name}")
                                faces_recognized += 1

                    # Scale back up
                    top, right, bottom, left = face_location
                    top *= 2
                    right *= 2
                    bottom *= 2
                    left *= 2

                    # Draw box
                    color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

                    # Draw name
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                    cv2.putText(
                        frame, name, (left + 6, bottom - 6),
                        cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1
                    )

            # Add status text
            cv2.putText(
                frame, f"Frames: {frame_count} | Detected: {faces_detected} | Recognized: {faces_recognized}",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
            )

            # Display
            cv2.imshow('Camera Test - Press Q to quit, S to save', frame)

            # Keyboard controls
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                filename = f"test_frame_{frame_count}.jpg"
                cv2.imwrite(filename, frame)
                print(f"💾 Saved: {filename}")

    except KeyboardInterrupt:
        print("\n\n⏹️  Stopped by user")

    finally:
        video_capture.release()
        cv2.destroyAllWindows()

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print("=" * 60)
    print(f"Total frames processed: {frame_count}")
    print(f"Faces detected: {faces_detected}")
    print(f"Faces recognized: {faces_recognized}")

    if faces_recognized > 0:
        print("\n✅ SUCCESS: Camera recognition is working!")
    elif faces_detected > 0:
        print("\n⚠️  PARTIAL: Camera detects faces but doesn't recognize them")
        print("   Try:")
        print("   - Upload a clearer photo")
        print("   - Ensure good lighting")
        print("   - Try different angles")
    else:
        print("\n❌ ISSUE: No faces detected")
        print("   Try:")
        print("   - Position yourself closer to camera")
        print("   - Ensure good lighting")
        print("   - Check camera angle")

    return True

if __name__ == "__main__":
    test_camera()
