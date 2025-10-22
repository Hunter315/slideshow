#!/usr/bin/env python3
"""
Test with grab() then retrieve() instead of read()
"""

import cv2
import time

print("Opening camera...", flush=True)
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

if not cap.isOpened():
    print("Failed to open")
    exit(1)

print("Camera opened", flush=True)

# Set low resolution and framerate
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
cap.set(cv2.CAP_PROP_FPS, 5)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)

print("Warming up camera (waiting 2 seconds)...", flush=True)
time.sleep(2)

print("Flushing buffer...", flush=True)
# Flush old frames
for i in range(5):
    cap.grab()

print("Trying grab() + retrieve() method...", flush=True)
for i in range(5):
    print(f"  Attempt {i+1}:", flush=True, end=" ")

    grabbed = cap.grab()
    print(f"grabbed={grabbed}", flush=True, end=" ")

    if grabbed:
        ret, frame = cap.retrieve()
        print(f"retrieved={ret}", flush=True, end=" ")
        if ret and frame is not None:
            print(f"✅ {frame.shape}", flush=True)
            cap.release()
            print("\n*** SUCCESS! Camera works! ***")
            exit(0)
        else:
            print("❌", flush=True)
    else:
        print("❌", flush=True)

    time.sleep(0.5)

cap.release()
print("\n❌ All attempts failed")
