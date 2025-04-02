import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def get_walking_time(origin, destination):
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": origin,
        "destinations": destination,
        "mode": "walking",
        "key": API_KEY
    }
    response = requests.get(url, params=params).json()
    try:
        return response["rows"][0]["elements"][0]["duration"]["text"]
    except:
        return "Unavailable"
