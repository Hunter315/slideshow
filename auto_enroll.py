#!/usr/bin/env python3
"""
Automatic Face Enrollment Service
Watches uploaded photos and automatically enrolls faces using guest names
"""

import os
import time
import json
import sqlite3
import face_recognition
import pickle
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration
UPLOADS_DIR = "uploads"
DB_PATH = "photos.db"
KNOWN_FACES_PATH = "known_faces.pkl"
MIN_CONFIDENCE_FOR_ENROLLMENT = 0.8  # Only enroll clear, high-quality face photos

class FaceEnroller:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_known_faces()
        self.processed_photos = set()

    def load_known_faces(self):
        """Load existing known faces from disk"""
        if Path(KNOWN_FACES_PATH).exists():
            with open(KNOWN_FACES_PATH, 'rb') as f:
                data = pickle.load(f)
                self.known_face_encodings = data['encodings']
                self.known_face_names = data['names']
                print(f"✅ Loaded {len(self.known_face_names)} known faces")
                if len(self.known_face_names) > 0:
                    # Count unique names
                    unique_names = list(set(self.known_face_names))
                    print(f"   People: {', '.join(unique_names)}")
        else:
            print("📝 Starting with empty face database")

    def save_known_faces(self):
        """Save known faces to disk"""
        data = {
            'encodings': self.known_face_encodings,
            'names': self.known_face_names
        }
        with open(KNOWN_FACES_PATH, 'wb') as f:
            pickle.dump(data, f)

    def get_photo_info(self, photo_id):
        """Get guest name from database for a photo"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT guest_name FROM photos WHERE photo_id = ? AND guest_name IS NOT NULL",
                (photo_id,)
            )
            result = cursor.fetchone()
            conn.close()

            if result and result[0]:
                return result[0].strip()
            return None
        except Exception as e:
            print(f"   ⚠️  Database error: {e}")
            return None

    def enroll_from_photo(self, photo_path):
        """
        Enroll a face from an uploaded photo using the guest name from database

        Returns:
            (success, name) tuple
        """
        try:
            # Extract photo_id from filename
            filename = os.path.basename(photo_path)
            photo_id = Path(filename).stem

            # Skip if already processed
            if photo_id in self.processed_photos:
                return (False, None)

            # Get guest name from database
            guest_name = self.get_photo_info(photo_id)

            if not guest_name:
                # No guest name provided, skip enrollment
                self.processed_photos.add(photo_id)
                return (False, None)

            print(f"📸 Attempting to enroll: {guest_name} from {filename}")

            # Load and process image
            image = face_recognition.load_image_file(photo_path)
            face_encodings = face_recognition.face_encodings(image)

            if len(face_encodings) == 0:
                print(f"   ❌ No face detected - skipping enrollment")
                self.processed_photos.add(photo_id)
                return (False, guest_name)

            if len(face_encodings) > 1:
                print(f"   ⚠️  Multiple faces detected - using primary face")

            # Use the first/primary face
            new_encoding = face_encodings[0]

            # Check if this person already exists (compare with existing encodings)
            person_exists = False
            if len(self.known_face_encodings) > 0:
                matches = face_recognition.compare_faces(
                    self.known_face_encodings,
                    new_encoding,
                    tolerance=0.6
                )

                # Check if any matches are for the same person (name)
                for i, match in enumerate(matches):
                    if match and self.known_face_names[i].lower() == guest_name.lower():
                        person_exists = True
                        print(f"   ℹ️  {guest_name} already enrolled, adding additional sample")
                        break

            # Add the face encoding
            self.known_face_encodings.append(new_encoding)
            self.known_face_names.append(guest_name)
            self.save_known_faces()

            if person_exists:
                print(f"   ✅ Added additional face sample for: {guest_name}")
            else:
                print(f"   ✅ Newly enrolled: {guest_name}")

            self.processed_photos.add(photo_id)
            return (True, guest_name)

        except Exception as e:
            print(f"   ❌ Error enrolling face: {e}")
            self.processed_photos.add(photo_id)
            return (False, None)


class UploadHandler(FileSystemEventHandler):
    """Handles file system events in the uploads directory"""

    def __init__(self, enroller):
        self.enroller = enroller

    def on_created(self, event):
        """Called when a file is created in the uploads directory"""
        if event.is_directory:
            return

        # Only process image files
        if not event.src_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            return

        # Wait for file to be fully written and database to be updated
        time.sleep(1)

        # Try to enroll face from this photo
        self.enroller.enroll_from_photo(event.src_path)


def process_existing_photos(enroller):
    """Process any existing photos that haven't been enrolled yet"""
    uploads_path = Path(UPLOADS_DIR)

    if not uploads_path.exists():
        print(f"Creating {UPLOADS_DIR} directory...")
        uploads_path.mkdir(parents=True, exist_ok=True)
        return

    # Find all image files
    image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']:
        image_files.extend(uploads_path.glob(ext))
        image_files.extend(uploads_path.glob(ext.upper()))

    if len(image_files) > 0:
        print(f"\n📁 Checking {len(image_files)} existing photos for enrollment...")
        enrolled_count = 0
        for image_file in image_files:
            success, name = enroller.enroll_from_photo(str(image_file))
            if success:
                enrolled_count += 1

        if enrolled_count > 0:
            print(f"✅ Enrolled {enrolled_count} new face(s) from existing photos\n")
        else:
            print(f"ℹ️  No new faces to enroll from existing photos\n")


def main():
    print("=" * 60)
    print("🎭 Auto-Enrollment Service - Learning Faces from Uploads")
    print("=" * 60)
    print("\nHow it works:")
    print("1. Guests upload photos with their names")
    print("2. System automatically learns their faces")
    print("3. Camera can recognize them later in live video")
    print("=" * 60)

    # Initialize enroller
    enroller = FaceEnroller()

    # Process existing photos first
    process_existing_photos(enroller)

    # Set up file watcher for new uploads
    event_handler = UploadHandler(enroller)
    observer = Observer()
    observer.schedule(event_handler, UPLOADS_DIR, recursive=False)
    observer.start()

    print(f"👀 Watching {UPLOADS_DIR}/ for new photos to learn from...")
    print("   When guests upload photos with their names, I'll learn their faces!")
    print("   Press Ctrl+C to stop\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping auto-enrollment service...")
        observer.stop()

    observer.join()

    # Final summary
    unique_people = list(set(enroller.known_face_names))
    print(f"\n📊 Final Summary:")
    print(f"   Total face samples: {len(enroller.known_face_names)}")
    print(f"   Unique people learned: {len(unique_people)}")
    if unique_people:
        print(f"   People: {', '.join(sorted(unique_people))}")
    print("\n✅ Auto-enrollment service stopped")


if __name__ == "__main__":
    main()
