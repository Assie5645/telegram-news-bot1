from telethon import TelegramClient, events
import json
import os
import re
import hashlib

# ==========================
# 🔑 API
# ==========================
api_id = 30133788
api_hash = "1f2d2d024eaafe22909fbb1131e1f084"

# ==========================
# 📡 CHANNELS
# ==========================
source_channels = [
    "@AAUMEREJA",
    "@AAU_GENERAL",
    "@PECCAAiT",
    "@AAUNews11"
]

destination_channel = "@AAUCentral"

from telethon.sessions import StringSession

SESSION = "1BJWap1sBu2mvJLznw4s0wFZVea5dgzdSejBlHKPx4Dc9eUCpCdB1ogOurd7LCjIGCILGYA79F6R1MQil1ATt2j5cEOKVKrpA7RT2zpZo5T8sRFkMz6IvRjVZQJZdW9byS3zJ17aR6jdwnoLH9qJoRC96WC5N_QN3m3yaSqFGBS8oE6_OsFro3m7AZQKHPuLxOnH179UcJbbaMOJwRU_S_vcrmdXiHS87_1jdfB8zQyFzskddCrV7Zuq6NXe87lznwc0gSKeEdfnq5L73zFuNV3_yNt6JpMxBGGVWHm8WrKJ02P4tIcg73hJqxXtKjsNruOEw8zwcqsYKIRADiwQLlpRXdzEBLUM="

client = TelegramClient(StringSession(SESSION), api_id, api_hash)

# ==========================
# 🧠 STORAGE
# ==========================
DATA_FILE = "processed.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        processed = json.load(f)
else:
    processed = {}

def save():
    with open(DATA_FILE, "w") as f:
        json.dump(processed, f)

# ==========================
# 🧹 CLEAN TEXT (REMOVE ADS)
# ==========================
def clean_text(text):
    if not text:
        return ""

    # remove links
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"@\w+", "", text)

    # remove common spam words
    spam_words = ["join", "subscribe", "follow", "t.me"]
    for word in spam_words:
        text = text.replace(word, "")

    return text.strip()

# ==========================
# 🧠 SMART DUPLICATE
# ==========================
def get_hash(text):
    text = clean_text(text.lower())
    return hashlib.md5(text.encode()).hexdigest()

print("🚀 PROFESSIONAL BOT RUNNING")

# ==========================
# 📸 HANDLE ALBUMS
# ==========================
@client.on(events.Album(chats=source_channels))
async def album_handler(event):

    album_id = str(event.grouped_id)
    text = event.messages[0].text or ""

    hash_key = get_hash(text)

    if hash_key in processed:
        print("⚠ Duplicate album skipped")
        return

    processed[hash_key] = True
    save()

    files = [msg.media for msg in event.messages]
    caption = clean_text(text)

    await client.send_file(
        destination_channel,
        files,
        caption=caption
    )

    print("📸 Full album forwarded")

# ==========================
# ✍ HANDLE NORMAL POSTS
# ==========================
@client.on(events.NewMessage(chats=source_channels))
async def message_handler(event):

    message = event.message

    if message.grouped_id:
        return

    text = message.text or ""
    hash_key = get_hash(text)

    if hash_key in processed:
        print("⚠ Duplicate skipped")
        return

    processed[hash_key] = True
    save()

    clean = clean_text(text)

    if message.media:
        await client.send_file(
            destination_channel,
            message.media,
            caption=clean
        )
    else:
        await client.send_message(
            destination_channel,
            clean
        )

    print("✅ Message forwarded clean")

# ==========================
# 🚀 RUN
# ==========================
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

async def main():
    print("🚀 BOT RUNNING ON RAILWAY")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
