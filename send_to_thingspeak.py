import requests
import time

THINGSPEAK_API_KEY = "LS4JLCA9PRGX6APQ"
OWM_API_KEY = "a2017d3aedba1dfd94e5bfaa71345deb"
CITY = "Muntinlupa"

def get_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={OWM_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    temperature = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    precipitation = data.get("rain", {}).get("1h", 0)

    return temperature, humidity, precipitation

def send_to_thingspeak(mosquito_count, temp, hum, rain):
    url = (
        f"https://api.thingspeak.com/update?api_key={THINGSPEAK_API_KEY}"
        f"&field1={temp}"
        f"&field2={hum}"
        f"&field3={rain}"
        f"&field4={mosquito_count}"
    )
    requests.get(url)

# Example mosquito count from your detection script
mosquito_count = 15  # replace with your real value

# Get weatherpython
temp, hum, rain = get_weather()

# Send everything
send_to_thingspeak(mosquito_count, temp, hum, rain)

print("Data sent!")