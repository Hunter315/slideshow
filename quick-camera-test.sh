#!/bin/bash
# Quick camera test - tries common indices

echo "Quick Camera Test"
echo "================="
echo ""

for i in 0 2 4 6 8 10; do
    echo "Testing camera index $i..."
    timeout 2 python3 -c "
import cv2
cap = cv2.VideoCapture($i)
if cap.isOpened():
    ret, frame = cap.read()
    if ret:
        print('  ✅ Index $i WORKS!')
        exit(0)
cap.release()
print('  ❌ Index $i failed')
exit(1)
" && echo "*** USE INDEX $i ***" && exit 0
done

echo ""
echo "❌ No working camera found in common indices"
echo "Try manually with: v4l2-ctl --list-devices"
