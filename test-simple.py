#!/usr/bin/env python3
"""
Simplest possible camera test with explicit format
"""

import cv2
import sys

print("1. Opening camera with V4L2...", flush=True)
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

if not cap.isOpened():
    print("FAILED to open camera")
    sys.exit(1)

print("2. Camera opened successfully", flush=True)

# Set format explicitly to MJPEG (usually faster and less likely to hang)
print("3. Setting format to MJPEG...", flush=True)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("4. Reading first frame...", flush=True)
ret, frame = cap.read()

if not ret:
    print("FAILED to read frame")
    cap.release()
    sys.exit(1)

print(f"5. SUCCESS! Frame captured: {frame.shape}", flush=True)

# Try a few more frames
for i in range(3):
    ret, frame = cap.read()
    if ret:
        print(f"   Frame {i+1}: OK ({frame.shape[1]}x{frame.shape[0]})", flush=True)
    else:
        print(f"   Frame {i+1}: FAILED", flush=True)

cap.release()
print("\n✅ Camera test PASSED!", flush=True)
