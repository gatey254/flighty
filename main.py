import os
import requests
import time
import math
from datetime import datetime
from openai import OpenAI
import telegram

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

LAT = 0.19626
LON = 35.07582
RADIUS_KM = 25

bot = telegram.Bot(token=TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

def get_flights():
    url = f"https://opensky-network.org/api/states/all?lamin={LAT-0.3}&lomin={LON-0.3}&lamax={LAT+0.3}&lomax={LON+0.3}"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        if not data or not data.get("states"):
            return []
        flights = []
        for f in data["states"]:
            icao, callsign, country, lat, lon, baro_alt, *_ = f
            if lat and lon:
                dist = math.dist([LAT, LON], [lat, lon]) * 111
                if dist <= RADIUS_KM:
                    flights.append({
                        "icao": icao,
                        "callsign": callsign.strip() if callsign else "Unknown",
                        "country": country,
                        "distance": round(dist, 1)
                    })
        return flights
    except Exception as e:
        print("Error:", e)
        return []

def generate_trivia(flight):
    prompt = f"Give me one fun, tweet-length trivia fact about aircraft with callsign {flight['callsign']} (country: {flight['country']}). Be casual and engaging."
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=60,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return "Fun fact: this aircraft has quite a story!"

def notify(flight, trivia):
    msg = (
        f"✈️ Hey, look up!\n"
        f"That’s flight *{flight['callsign']}* from {flight['country']} about {flight['distance']} km away.\n\n"
        f"💡 {trivia}"
    )
    bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")

def main():
    print("SkySpotter AI is now live 🚀")
    seen = set()
    while True:
        flights = get_flights()
        for f in flights:
            if f["icao"] not in seen:
                trivia = generate_trivia(f)
                notify(f, trivia)
                seen.add(f["icao"])
        time.sleep(900)

if __name__ == "__main__":
    main()
