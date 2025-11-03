import os
import requests
import time
import math
import telegram

# Your location
LAT = 0.19626
LON = 35.07582
RADIUS_KM = 25  # Radius in km

# Secrets from Render environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = telegram.Bot(token=TELEGRAM_TOKEN)

def fetch_planes():
    url = "https://opensky-network.org/api/states/all"
    try:
        res = requests.get(url, timeout=10).json()
        states = res.get("states", [])
        planes = []

        for s in states:
            callsign = s[1]
            country  = s[2]
            lat      = s[6]
            lon      = s[5]

            if lat and lon:
                # Approximate km distance
                dist = math.dist([LAT, LON], [lat, lon]) * 111
                if dist <= RADIUS_KM:
                    planes.append({
                        "callsign": callsign.strip() if callsign else "Unknown",
                        "country": country,
                        "dist": round(dist, 1)
                    })
        return planes

    except Exception as e:
        print("Error:", e)
        return []

def notify(plane):
    msg = (
        f"✈️ Plane detected near your location!\n\n"
        f"Flight: {plane['callsign']}\n"
        f"Country: {plane['country']}\n"
        f"Distance: {plane['dist']} km"
    )
    bot.send_message(chat_id=CHAT_ID, text=msg)

def main():
    print("✅ SkySpotter AI (Free Version) is running...")
    sent = set()

    while True:
        planes = fetch_planes()
        for p in planes:
            key = f"{p['callsign']}|{p['country']}|{p['dist']}"
            if key not in sent:
                notify(p)
                sent.add(key)

        time.sleep(900)  # Check every 15 minutes

if __name__ == "__main__":
    main()
