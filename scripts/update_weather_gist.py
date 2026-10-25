#!/usr/bin/env python3
"""Update Local Time, Weather & Status Gist for GitHub Pinned Gist card."""

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

USERNAME = "Mayur-Pagote"
GIST_ID = os.environ.get("WEATHER_GIST_ID")
GH_TOKEN = os.environ.get("GH_GIST_TOKEN")
LOCAL_TZ = "Asia/Kolkata"

# Pune Coordinates
LATITUDE = 18.5204
LONGITUDE = 73.8567

def get_time_emoji(hour):
    if 6 <= hour < 12:
        return "🌅"  # Morning
    elif 12 <= hour < 17:
        return "🌞"  # Noon / Bright sunshine
    elif 17 <= hour < 20:
        return "🌇"  # Evening / Sunset
    else:
        return "🌙"  # Night

def fetch_weather():
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={LATITUDE}&longitude={LONGITUDE}&"
        f"current=temperature_2m,relative_humidity_2m,weather_code,is_day"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8")).get("current", {})

    temp = round(data.get("temperature_2m", 25))
    humidity = data.get("relative_humidity_2m", 60)
    code = data.get("weather_code", 0)
    is_day = bool(data.get("is_day", 1))

    # Temperature alert
    temp_alert = ""
    if temp >= 38:
        temp_alert = " 🥵"
    elif temp <= 10:
        temp_alert = " 🥶"

    # WMO Weather Codes to Emojis
    if code == 0:
        icon = "☀️" if is_day else "🌙"
        desc = "Clear Sky"
    elif code in (1, 2):
        icon = "🌤️" if is_day else "☁️"
        desc = "Mainly Clear" if code == 1 else "Partly Cloudy"
    elif code == 3:
        icon = "☁️"
        desc = "Overcast"
    elif code in (45, 48):
        icon = "🌫️"
        desc = "Foggy"
    elif code in (51, 53, 55, 61, 63, 65, 80, 81, 82):
        icon = "🌦️" if is_day else "🌧️"
        desc = "Rainy"
    elif code in (71, 73, 75, 77, 85, 86):
        icon = "❄️"
        desc = "Snowy"
    elif code in (95, 96, 99):
        icon = "⛈️"
        desc = "Thunderstorm"
    else:
        icon = "⛅"
        desc = "Clear"

    return f"{icon} {temp}°C, {desc} · Humidity {humidity}%{temp_alert}"

def get_status(now):
    # 1. Check if active on GitHub within last 90 minutes
    try:
        events_url = f"https://api.github.com/users/{USERNAME}/events/public?per_page=3"
        req = urllib.request.Request(events_url, headers={"User-Agent": "Mozilla/5.0"})
        if GH_TOKEN:
            req.add_header("Authorization", f"Bearer {GH_TOKEN}")
        with urllib.request.urlopen(req) as resp:
            events = json.loads(resp.read().decode("utf-8"))
            if events:
                last_event_time = events[0].get("created_at")
                if last_event_time:
                    dt = datetime.fromisoformat(last_event_time.replace("Z", "+00:00"))
                    diff_minutes = (datetime.now(timezone.utc) - dt).total_seconds() / 60
                    if diff_minutes <= 90:
                        return "💻 Coding / Active"
    except Exception:
        pass

    # 2. Time-of-day routine (IST)
    hr = now.hour
    minute = now.minute
    time_float = hr + minute / 60.0
    weekday = now.weekday()  # 5 = Sat, 6 = Sun

    if time_float >= 23.5 or time_float < 7.0:
        return "😴 Sleeping / Resting"
    elif 7.0 <= time_float < 9.5:
        return "☕ Morning Routine"
    elif 9.5 <= time_float < 18.5:
        return "🌴 Weekend Vibes" if weekday in (5, 6) else "💼 Working / Engineering"
    else:
        return "📚 Learning / Side Projects"

def generate_content():
    now = datetime.now(ZoneInfo(LOCAL_TZ))
    date_str = now.strftime("%d-%m-%Y & %A")
    t_icon = get_time_emoji(now.hour)
    time_str = now.strftime("%I:%M %p IST (UTC+5:30)")
    weather_str = fetch_weather()
    status_str = get_status(now)

    lines = [
        "Currently in Pune, India               Asia/Kolkata",
        f"🗓️ Date & Day   {date_str}",
        f"⏰ Time         {t_icon} {time_str}",
        f"☁️ Weather      {weather_str}",
        f"✅ Status       {status_str}",
    ]
    return "\n".join(lines) + "\n"

def update_gist(gist_id, token, content):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "Weather-Stats-Gist-Updater"
    }

    get_req = urllib.request.Request(f"https://api.github.com/gists/{gist_id}", headers=headers)
    with urllib.request.urlopen(get_req) as resp:
        gist_data = json.loads(resp.read().decode("utf-8"))

    files = gist_data.get("files", {})
    filename = list(files.keys())[0] if files else "📍 Pune, India"

    patch_body = json.dumps({
        "description": "📍 Pune, India — Live Time & Weather (Auto-updated)",
        "files": {
            filename: {
                "content": content
            }
        }
    }).encode("utf-8")

    patch_req = urllib.request.Request(
        f"https://api.github.com/gists/{gist_id}",
        data=patch_body,
        headers=headers,
        method="PATCH"
    )
    with urllib.request.urlopen(patch_req) as resp:
        print(f"Successfully updated weather gist '{filename}'")

def main():
    content = generate_content()
    print("Generated Weather Gist Content:")
    print(content)

    if not GIST_ID or not GH_TOKEN:
        print("WEATHER_GIST_ID or GH_GIST_TOKEN not set. Skipping update.")
        return

    update_gist(GIST_ID, GH_TOKEN, content)

if __name__ == "__main__":
    main()
