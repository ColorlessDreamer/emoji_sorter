import requests
import time

# Replace with your actual URL that you want to keep alive.
URL = "https://b9494410-7e93-4d04-adbc-1d2eacbe593f-00-3kb1qptr1o1es.worf.replit.dev/sort?channel_id=1226724957795516434"

# Set the ping interval in seconds (e.g., 300 seconds = 5 minutes)
PING_INTERVAL = 300

while True:
    try:
        response = requests.get(URL)
        print(f"Pinged Site: {response.status_code}")
    except Exception as e:
        print(f"Error pinging {URL}: {e}")
    time.sleep(PING_INTERVAL)
