#!/usr/bin/env python3
"""
Real-time Face Recognition Service for Raspberry Pi 4
Detects and recognizes faces from camera feed
"""

import cv2
import face_recognition
import pickle
import time
import requests
import json
from pathlib import Path
import numpy as np

# Configuration
CAMERA_INDEX = 0  # Use video0 with V4L2 backend
KNOWN_FACES_PATH = "known_faces.pkl"
API_URL = "http://localhost:3000/api"
RECOGNITION_THRESHOLD = 0.6  # Lower = stricter matching
FRAME_SKIP = 2  # Process every Nth frame for better performance
SCALE_FACTOR = 0.5  # Downscale frames for faster processing

class FaceRecognitionService:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_known_faces()
        self.last_recognized = {}  # Track last recognition time per person
        self.last_reload_time = time.time()  # Track when we last reloaded faces

    def load_known_faces(self):
        """Load known faces from disk"""
        if Path(KNOWN_FACES_PATH).exists():
            with open(KNOWN_FACES_PATH, 'rb') as f:
                data = pickle.load(f)
                self.known_face_encodings = data['encodings']
                self.known_face_names = data['names']
                unique_names = list(set(self.known_face_names))
                print(f"📚 Loaded {len(self.known_face_names)} face samples for {len(unique_names)} people")
                if unique_names:
                    print(f"   People: {', '.join(sorted(unique_names))}")
        else:
            print("⚠️  No known faces found yet. Waiting for guests to upload photos...")

    def reload_faces_if_updated(self):
        """Check if known_faces.pkl has been updated and reload if needed"""
        if Path(KNOWN_FACES_PATH).exists():
            file_mtime = Path(KNOWN_FACES_PATH).stat().st_mtime
            if file_mtime > self.last_reload_time:
                print("\n🔄 New faces detected, reloading...")
                old_count = len(set(self.known_face_names))
                self.load_known_faces()
                new_count = len(set(self.known_face_names))
                if new_count > old_count:
                    print(f"✅ Learned {new_count - old_count} new person/people!")
                self.last_reload_time = time.time()

    def save_known_faces(self):
        """Save known faces to disk"""
        data = {
            'encodings': self.known_face_encodings,
            'names': self.known_face_names
        }
        with open(KNOWN_FACES_PATH, 'wb') as f:
            pickle.dump(data, f)
        print(f"Saved {len(self.known_face_names)} known faces")

    def enroll_face(self, image_path, person_name):
        """
        Enroll a new person by learning their face from an image

        Args:
            image_path: Path to image containing the person's face
            person_name: Name to associate with this face

        Returns:
            bool: True if enrollment succeeded, False otherwise
        """
        try:
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)

            if len(encodings) == 0:
                print(f"❌ No face found in {image_path}")
                return False

            # Use the first face found
            self.known_face_encodings.append(encodings[0])
            self.known_face_names.append(person_name)
            self.save_known_faces()
            print(f"✅ Enrolled {person_name} (total: {len(set(self.known_face_names))} people)")
            return True
        except Exception as e:
            print(f"❌ Error enrolling {person_name}: {e}")
            return False

    def recognize_faces(self, frame):
        """
        Detect and recognize faces in a frame

        Returns:
            List of tuples: [(name, location), ...]
        """
        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=SCALE_FACTOR, fy=SCALE_FACTOR)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Find faces
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        recognized = []

        for face_encoding, face_location in zip(face_encodings, face_locations):
            # Compare with known faces
            matches = face_recognition.compare_faces(
                self.known_face_encodings,
                face_encoding,
                tolerance=RECOGNITION_THRESHOLD
            )
            name = "Unknown"

            # Use the closest match
            face_distances = face_recognition.face_distance(
                self.known_face_encodings,
                face_encoding
            )

            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]

            # Scale back up face locations
            top, right, bottom, left = face_location
            top = int(top / SCALE_FACTOR)
            right = int(right / SCALE_FACTOR)
            bottom = int(bottom / SCALE_FACTOR)
            left = int(left / SCALE_FACTOR)

            recognized.append((name, (top, right, bottom, left)))

        return recognized

    def notify_recognition(self, person_name):
        """Notify the Node.js server that someone was recognized"""
        try:
            requests.post(
                f"{API_URL}/recognition",
                json={'name': person_name, 'timestamp': time.time()},
                timeout=1
            )
        except Exception as e:
            print(f"Failed to notify server: {e}")

    def run_camera(self):
        """Main loop: capture frames and recognize faces"""
        print("🎥 Starting camera...")
        # Use V4L2 backend explicitly (avoids GStreamer issues on Pi)
        video_capture = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_V4L2)

        # Check if camera opened successfully
        if not video_capture.isOpened():
            print("❌ ERROR: Could not open camera")
            print("   Make sure a camera is connected")
            print("   Camera index:", CAMERA_INDEX)
            print("   Try:")
            print("   - Plug in USB camera")
            print("   - Check camera permissions")
            print("   - Try different CAMERA_INDEX (0, 1, 2...)")
            return

        video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        video_capture.set(cv2.CAP_PROP_FPS, 30)

        print("✅ Camera opened successfully")

        frame_count = 0
        reload_check_interval = 30  # Check for new faces every 30 frames

        try:
            while True:
                ret, frame = video_capture.read()
                if not ret:
                    print("Failed to grab frame")
                    break

                frame_count += 1

                # Periodically check for new enrolled faces
                if frame_count % (FRAME_SKIP * reload_check_interval) == 0:
                    self.reload_faces_if_updated()

                # Skip frames for performance
                if frame_count % FRAME_SKIP != 0:
                    continue

                # Recognize faces
                recognized = self.recognize_faces(frame)

                # Draw boxes and names
                for name, (top, right, bottom, left) in recognized:
                    # Draw box
                    color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

                    # Draw name
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                    cv2.putText(
                        frame, name, (left + 6, bottom - 6),
                        cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1
                    )

                    # Notify server (throttle to once per 5 seconds per person)
                    if name != "Unknown":
                        current_time = time.time()
                        if (name not in self.last_recognized or
                            current_time - self.last_recognized[name] > 5):
                            self.last_recognized[name] = current_time
                            self.notify_recognition(name)
                            print(f"Recognized: {name}")

                # Display frame (comment out for headless operation)
                cv2.imshow('Face Recognition', frame)

                # Press 'q' to quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        finally:
            video_capture.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    service = FaceRecognitionService()

    # Example: Enroll faces from a directory
    # for image_path in Path("faces").glob("*.jpg"):
    #     name = image_path.stem  # Use filename as name
    #     service.enroll_face(str(image_path), name)

    # Start recognition
    service.run_camera()
