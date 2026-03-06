from roboflow import Roboflow
import cv2
import numpy as np
import time
import requests

# ==========================================================
# API KEYS
# ==========================================================
ROBOFLOW_API_KEY = "0jEYnZ96qsMrtzFFmJr8"
THINGSPEAK_API_KEY = "LS4JLCA9PRGX6APQ"
OWM_API_KEY = "a2017d3aedba1dfd94e5bfaa71345deb"
CITY = "Muntinlupa"

# ==========================================================
# WEATHER FUNCTION
# ==========================================================
def get_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={OWM_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    temperature = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    precipitation = data.get("rain", {}).get("1h", 0)

    return temperature, humidity, precipitation

# ==========================================================
# THINGSPEAK FUNCTION
# ==========================================================
def send_to_thingspeak(mosquito_count, temp, hum, rain):
    url = (
        f"https://api.thingspeak.com/update?api_key={THINGSPEAK_API_KEY}"
        f"&field1={temp}"
        f"&field2={hum}"
        f"&field3={rain}"
        f"&field4={mosquito_count}"
    )

    response = requests.get(url)
    print("ThingSpeak Response:", response.text)
    print("Data sent to ThingSpeak!\n")

# ==========================================================
# MOSQUITO DETECTION FUNCTION
# ==========================================================
def detect_mosquitoes():

    # Initialize Roboflow
    rf = Roboflow(api_key=ROBOFLOW_API_KEY)
    project = rf.workspace("for-mosquito-datasets").project("mosquito-e70mr-rk7xq")
    version = project.version(3)
    model = version.model

    # Initialize Webcam (default camera index 0)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    last_sent_time = 0
    send_interval = 20   # Send to ThingSpeak every 20 seconds
    last_predictions = []

    try:
        while True:
            ret, frame_bgr = cap.read()
            if not ret:
                print("Warning: Failed to read frame from webcam.")
                continue

            current_time = time.time()

            if current_time - last_sent_time >= send_interval:
                last_sent_time = current_time

                predictions = model.predict(frame_bgr, confidence=40, overlap=30).json()
                last_predictions = predictions.get("predictions", [])

                mosquito_count = len(last_predictions)
                print(f"Mosquitoes detected: {mosquito_count}")

                # Get weather
                temp, hum, rain = get_weather()

                print(f"Temp: {temp}°C | Humidity: {hum}% | Rain: {rain}mm")

                # Send to ThingSpeak
                send_to_thingspeak(mosquito_count, temp, hum, rain)

            # Draw bounding boxes (kept for potential future visualization use)
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

    finally:
        cap.release()

# ==========================================================
# MAIN
# ==========================================================
if __name__ == "__main__":
    detect_mosquitoes()