#!/usr/bin/env python3
"""
Test different camera configurations to find one that works
"""

import cv2
import sys
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Timeout!")

# Set 3 second timeout for each test
signal.signal(signal.SIGALRM, timeout_handler)

configs = [
    ("Default", None, 640, 480),
    ("MJPG 320x240", cv2.VideoWriter_fourcc('M','J','P','G'), 320, 240),
    ("MJPG 640x480", cv2.VideoWriter_fourcc('M','J','P','G'), 640, 480),
    ("YUYV 320x240", cv2.VideoWriter_fourcc('Y','U','Y','V'), 320, 240),
    ("YUYV 640x480", cv2.VideoWriter_fourcc('Y','U','Y','V'), 640, 480),
]

for name, fourcc, width, height in configs:
    print(f"\nTesting: {name} ({width}x{height})...", flush=True)

    try:
        cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

        if not cap.isOpened():
            print("  ❌ Failed to open", flush=True)
            continue

        if fourcc:
            cap.set(cv2.CAP_PROP_FOURCC, fourcc)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimal buffer

        print("  Reading frame...", flush=True)

        # Set 3 second timeout
        signal.alarm(3)
        ret, frame = cap.read()
        signal.alarm(0)  # Cancel timeout

        if ret and frame is not None:
            print(f"  ✅ SUCCESS! {frame.shape}", flush=True)
            cap.release()
            print(f"\n*** USE THIS CONFIG: {name} ***")
            break
        else:
            print("  ❌ Read failed", flush=True)

        cap.release()

    except TimeoutError:
        print("  ⏱️  TIMEOUT (hung)", flush=True)
        try:
            cap.release()
        except:
            pass
    except Exception as e:
        print(f"  ❌ Error: {e}", flush=True)

print("\nDone")
