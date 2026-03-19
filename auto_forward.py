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

client = TelegramClient("new_session", api_id, api_hash)

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
client.start()
client.run_until_disconnected()
