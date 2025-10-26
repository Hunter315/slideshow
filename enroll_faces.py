#!/usr/bin/env python3
"""
Batch Face Enrollment Script
Enrolls all photos with guest names into the face recognition system
"""

import sqlite3
import face_recognition
import pickle
from pathlib import Path
import sys

KNOWN_FACES_PATH = "known_faces.pkl"
DB_PATH = "photos.db"
UPLOADS_DIR = "uploads"

def load_known_faces():
    """Load existing known faces from disk"""
    if Path(KNOWN_FACES_PATH).exists():
        with open(KNOWN_FACES_PATH, 'rb') as f:
            data = pickle.load(f)
            return data['encodings'], data['names']
    return [], []

def save_known_faces(encodings, names):
    """Save known faces to disk"""
    data = {
        'encodings': encodings,
        'names': names
    }
    with open(KNOWN_FACES_PATH, 'wb') as f:
        pickle.dump(data, f)
    print(f"💾 Saved {len(names)} face encodings for {len(set(names))} people")

def enroll_from_database():
    """Enroll all photos with guest_name from the database"""

    # Load existing faces
    known_encodings, known_names = load_known_faces()
    initial_count = len(set(known_names))

    print(f"📚 Starting enrollment...")
    print(f"   Current database: {initial_count} people enrolled")

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all active photos with guest names
    cursor.execute("""
        SELECT filepath, guest_name
        FROM photos
        WHERE guest_name IS NOT NULL
        AND guest_name != ''
        AND status = 'active'
        ORDER BY uploaded_at ASC
    """)

    photos = cursor.fetchall()
    conn.close()

    if not photos:
        print("⚠️  No photos with guest names found in database")
        return

    print(f"📸 Found {len(photos)} photos with guest names")
    print()

    enrolled = 0
    skipped = 0
    failed = 0

    for filepath, guest_name in photos:
        image_path = Path(UPLOADS_DIR) / filepath

        if not image_path.exists():
            print(f"⚠️  File not found: {filepath}")
            failed += 1
            continue

        try:
            # Load image and detect faces
            image = face_recognition.load_image_file(str(image_path))
            encodings = face_recognition.face_encodings(image)

            if len(encodings) == 0:
                print(f"❌ {guest_name}: No face detected in {filepath}")
                skipped += 1
                continue

            # Use the first face found
            known_encodings.append(encodings[0])
            known_names.append(guest_name)
            print(f"✅ {guest_name}: Enrolled from {filepath}")
            enrolled += 1

        except Exception as e:
            print(f"❌ {guest_name}: Error processing {filepath}: {e}")
            failed += 1

    # Save updated faces
    if enrolled > 0:
        save_known_faces(known_encodings, known_names)
        final_count = len(set(known_names))
        new_people = final_count - initial_count

        print()
        print(f"🎉 Enrollment complete!")
        print(f"   • {enrolled} photos processed")
        print(f"   • {new_people} new people enrolled")
        print(f"   • {final_count} total people in database")
        if skipped > 0:
            print(f"   • {skipped} photos skipped (no face detected)")
        if failed > 0:
            print(f"   • {failed} photos failed")
        print()
        print("🔄 The face recognition camera will auto-reload within 1-2 seconds")
    else:
        print()
        print("⚠️  No new faces enrolled")

if __name__ == "__main__":
    try:
        enroll_from_database()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
