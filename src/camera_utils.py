# camera_utils.py
import cv2
import numpy as np
from gpio_config import Thresholds

def capture_frame():
    cap = cv2.VideoCapture(0)
    if not cap or not cap.isOpened():
        return None
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return None
    return frame

def is_healthy_by_color(frame):
    if frame is None:
        return None, 0.0
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_green = np.array(Thresholds.GREEN_LOWER, dtype=np.uint8)
    upper_green = np.array(Thresholds.GREEN_UPPER, dtype=np.uint8)
    mask = cv2.inRange(hsv, lower_green, upper_green)
    green_pixels = int(np.count_nonzero(mask))
    total_pixels = mask.size
    if total_pixels == 0:
        return None, 0.0
    green_percent = (green_pixels / total_pixels) * 100.0
    healthy = green_percent > Thresholds.GREEN_PERCENT_HEALTHY
    return healthy, green_percent
