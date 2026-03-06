from roboflow import Roboflow
from picamera2 import Picamera2
import cv2
import numpy as np
import time
from collections import Counter

# -----------------------------
# Initialize Roboflow
# -----------------------------
rf = Roboflow(api_key="0jEYnZ96qsMrtzFFmJr8")  # Replace with your Roboflow API key
project = rf.workspace("for-mosquito-datasets").project("mosquito-e70mr-rk7xq")
version = project.version(3)
model = version.model

# -----------------------------
# Initialize Picamera2
# -----------------------------
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration(main={"size": (1280, 720)})  # lower res for speed
picam2.configure(camera_config)
picam2.start()

# -----------------------------
# Variables for frame sending
# -----------------------------
last_sent_time = 0           # timestamp of last frame sent
send_interval = 5            # seconds between sending frames
last_predictions = []        # store last predictions to persist boxes

try:
    while True:
        # Capture frame
        frame = picam2.capture_array()
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        current_time = time.time()
        # Send to Roboflow only if interval passed
        if current_time - last_sent_time >= send_interval:
            last_sent_time = current_time
            predictions = model.predict(frame_bgr, confidence=40, overlap=30).json()
            last_predictions = predictions.get("predictions", [])

            # -----------------------------
            # Count mosquitoes
            # -----------------------------
            mosquito_boxes = []
            for pred in last_predictions:
                x, y = int(pred["x"]), int(pred["y"])
                w, h = int(pred["width"]), int(pred["height"])
                x1 = x - w // 2
                y1 = y - h // 2
                x2 = x + w // 2
                y2 = y + h // 2
                mosquito_boxes.append((x1, y1, x2, y2))

            mosquito_count = len(mosquito_boxes)
            print(f"Mosquitoes detected: {mosquito_count}")

        # Draw all last predictions on current frame
        for pred in last_predictions:
            x, y = int(pred["x"]), int(pred["y"])
            w, h = int(pred["width"]), int(pred["height"])
            x1 = x - w // 2
            y1 = y - h // 2
            x2 = x + w // 2
            y2 = y + h // 2
            cv2.rectangle(frame_bgr, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame_bgr, pred["class"], (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Display the frame
        cv2.imshow("Mosquito Detector", frame_bgr)

        # Small delay to reduce CPU usage
        time.sleep(0.05)

        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    picam2.stop()
    cv2.destroyAllWindows()