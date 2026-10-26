#!/usr/bin/env python3
"""Rotate Random Wall cards for GitHub Pinned Gist card."""

import json
import os
import random
import sys
import urllib.request

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

GIST_ID = os.environ.get("RANDOM_WALL_GIST_ID")
GH_TOKEN = os.environ.get("GH_GIST_TOKEN")

# All cards must be exactly 5 lines high
CARDS = [
    # 1. Terminal About Me (Aligned)
    (
        "🔴 🟢 🟡       About_Me.exe          —  🗖  ✕\n"
        " • Did OpenSource\n"
        " • Likes DIY\n"
        " • My Secret: ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓\n"
        "⊞ ─────── Help Ever. Hurt Never. ────── 📶🔋"
    ),
    # 2. Devices I Own
    (
        "────────────── Devices I Own ───────────────\n"
        "1. Acer Swift 3 OLED\n"
        "2. OnePlus Nord 2\n"
        "3. OnePlus Pad 2\n"
        "4. HP Pavilion Gaming 16"
    ),
    # 3. Favourite Games
    (
        "───────────── Favourite Games ──────────────\n"
        "1. Clash of Clans\n"
        "2. Clash Royale\n"
        "3. Mobile Legends\n"
        "4. PUBG"
    ),
    # 4. Acer Specs
    (
        "──────────── Acer Swift 3 OLED ─────────────\n"
        "i5 12500H 2.50 GHz (12 Core)\n"
        "16 GB LPDDR5 Ram 4800 MT/s\n"
        "NVMe SSD 512 GB\n"
        "Intel Iris Xe Graphics"
    ),
    # 5. OnePlus Nord 2
    (
        "──────────── OnePlus Nord 2 5G ─────────────\n"
        "MediaTek Dimensity 1200-AI 3.0 GHz\n"
        "8 GB LPDDR4X RAM\n"
        "128 GB UFS 3.1 Storage\n"
        "ARM Mali-G77 MC9 GPU"
    ),
    # 6. OnePlus Pad 2
    (
        "────────────── OnePlus Pad 2 ───────────────\n"
        "Qualcomm Snapdragon 8 Gen 3 3.30 GHz\n"
        "12 GB LPDDR5X RAM\n"
        "UFS 3.1 Storage 256 GB\n"
        "Qualcomm Adreno 750 GPU"
    ),
    # 7. HP Pavilion Gaming 16
    (
        "────────── HP Pavilion Gaming 16 ───────────\n"
        "i7-10870H 2.20 GHz (8 Core)\n"
        "16 GB DDR4 RAM 2933 MT/s\n"
        "NVMe SSD 512 GB\n"
        "NVIDIA GeForce GTX 1650 Ti 4 GB GDDR6"
    ),
    # 8. IoT Hardware
    (
        "────────── Microcontrollers I Use ──────────\n"
        "ESP32-S3 — Dual-Core 240 MHz\n"
        "ESP8266 — Single-Core 160 MHz\n"
        "Arduino Mega 2560 — ATmega2560, 16 MHz\n"
        "Arduino Uno — ATmega328P, 16 MHz"
    )
]

def update_gist(gist_id, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "Random-Wall-Gist-Updater"
    }

    # Fetch current content to avoid picking the same card twice in a row
    get_req = urllib.request.Request(f"https://api.github.com/gists/{gist_id}", headers=headers)
    with urllib.request.urlopen(get_req) as resp:
        gist_data = json.loads(resp.read().decode("utf-8"))

    files = gist_data.get("files", {})
    filename = list(files.keys())[0] if files else "🎲 Random Wall"
    current_content = files.get(filename, {}).get("content", "").strip()

    # Pick a random card that is different from current
    available_cards = [c for c in CARDS if c.strip() != current_content]
    selected_card = random.choice(available_cards if available_cards else CARDS) + "\n"

    print(f"Selected card:\n{selected_card}")

    # Patch the gist
    patch_body = json.dumps({
        "description": "🎲 Random Wall (Auto-updated)",
        "files": {
            filename: {
                "content": selected_card
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
        print(f"Successfully updated Random Wall in '{filename}'")

def main():
    if not GIST_ID or not GH_TOKEN:
        print("RANDOM_WALL_GIST_ID or GH_GIST_TOKEN not set. Showing random card:")
        print(random.choice(CARDS))
        return

    update_gist(GIST_ID, GH_TOKEN)

if __name__ == "__main__":
    main()
