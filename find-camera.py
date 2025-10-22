#!/usr/bin/env python3
"""
Find working camera index
Scans all /dev/video* devices to find which one works
"""

import cv2
import os
import glob

def find_working_cameras():
    print("=" * 60)
    print("🔍 Scanning for working cameras...")
    print("=" * 60)

    # Get all video devices
    video_devices = glob.glob('/dev/video*')

    if not video_devices:
        print("❌ No /dev/video* devices found")
        print("   Is the camera plugged in?")
        return

    print(f"\nFound {len(video_devices)} video device(s):")
    for device in sorted(video_devices):
        print(f"  - {device}")

    print("\nTesting each device...\n")

    working_cameras = []

    for device in sorted(video_devices):
        # Extract index from /dev/videoX
        index = int(device.replace('/dev/video', ''))

        print(f"📹 Testing index {index} ({device})...", end=" ")

        try:
            cap = cv2.VideoCapture(index)

            if cap.isOpened():
                # Try to read a frame
                ret, frame = cap.read()

                if ret and frame is not None:
                    height, width = frame.shape[:2]
                    print(f"✅ WORKS! Resolution: {width}x{height}")
                    working_cameras.append({
                        'index': index,
                        'device': device,
                        'width': width,
                        'height': height
                    })
                else:
                    print("⚠️  Opens but can't read frames")

                cap.release()
            else:
                print("❌ Can't open")

        except Exception as e:
            print(f"❌ Error: {e}")

    print("\n" + "=" * 60)

    if working_cameras:
        print(f"✅ Found {len(working_cameras)} working camera(s):")
        print("=" * 60)
        for cam in working_cameras:
            print(f"\n  Index: {cam['index']}")
            print(f"  Device: {cam['device']}")
            print(f"  Resolution: {cam['width']}x{cam['height']}")

        print("\n" + "=" * 60)
        print("📝 To use in your scripts:")
        print("=" * 60)
        print(f"\nEdit these files and set:")
        print(f"  CAMERA_INDEX = {working_cameras[0]['index']}")
        print(f"\nFiles to update:")
        print(f"  - face_recognition_service.py")
        print(f"  - test-camera.py")

    else:
        print("❌ No working cameras found")
        print("=" * 60)
        print("\nTroubleshooting:")
        print("  1. Check camera is plugged in")
        print("  2. Check camera permissions: ls -l /dev/video*")
        print("  3. Add user to video group: sudo usermod -a -G video $USER")
        print("  4. Reboot and try again")

if __name__ == "__main__":
    find_working_cameras()
