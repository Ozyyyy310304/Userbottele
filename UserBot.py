from telethon import TelegramClient, events
import os
import asyncio
from datetime import datetime
import json
import re

# API Configuration
api_id = '29798494'
api_hash = '53273c1de3e68a9ecdb90de2dcf46f6c'

client = TelegramClient('userbot', api_id, api_hash)
device_owner_id = None
afk_reason = None

# Directories
QR_CODE_DIR = "qr_codes"
os.makedirs(QR_CODE_DIR, exist_ok=True)

# Detected links storage
detected_links = set()

# Watermark
WATERMARK_TEXT = ""

def append_watermark_to_message(message):
    return f"{message}\n\n{WATERMARK_TEXT}"

# Blacklist Functions
def load_blacklist():
    try:
        with open('blacklist.json', 'r') as file:
            data = json.load(file)
        return data.get('blacklisted_groups', [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_blacklist(blacklisted_groups):
    data = {"blacklisted_groups": blacklisted_groups}
    with open('blacklist.json', 'w') as file:
        json.dump(data, file, indent=4)

# Device owner validation
def is_device_owner(sender_id):
    return sender_id == device_owner_id

# Detect Links
@client.on(events.NewMessage(incoming=True))
async def detect_links(event):
    if event.text:
        links = re.findall(r'(https?://t\.me/joinchat/\S+)', event.text)
        detected_links.update(links)

@client.on(events.NewMessage(pattern='.jgc', outgoing=True))
async def join_groups(event):
    sender = await event.get_sender()
    if not is_device_owner(sender.id):
        await event.respond(append_watermark_to_message("❌ You are not authorized to use this command."))
        await event.delete()
        return

    if not detected_links:
        await event.respond(append_watermark_to_message("❌ No group links detected."))
        await event.delete()
        return

    success_count = 0
    failed_count = 0

    for link in list(detected_links):
        try:
            await client(ImportChatInviteRequest(link.split('/')[-1]))
            success_count += 1
        except Exception as e:
            print(f"Failed to join group: {e}")
            failed_count += 1

    await event.respond(f"✅ Successfully joined {success_count} groups. ❌ Failed to join {failed_count} groups.")
    detected_links.clear()
    await event.delete()

# Global Broadcast
@client.on(events.NewMessage(pattern='.gcast', outgoing=True))
async def gcast(event):
    sender = await event.get_sender()
    if not is_device_owner(sender.id):
        await event.respond(append_watermark_to_message("❌ You are not authorized to use this command."))
        await event.delete()
        return

    reply_message = await event.get_reply_message()
    if not reply_message:
        await event.respond(append_watermark_to_message("❌ Please reply to a message to broadcast."))
        await event.delete()
        return

    sent_count = 0
    groups = [dialog for dialog in await client.get_dialogs() if dialog.is_group]
    for dialog in groups:
        if dialog.id in load_blacklist():
            continue
        try:
            if reply_message.media:
                media_path = await client.download_media(reply_message.media)
                await client.send_file(dialog.id, media_path, caption=append_watermark_to_message(reply_message.message))
            else:
                await client.send_message(dialog.id, append_watermark_to_message(reply_message.message))
            sent_count += 1
            await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Failed to send to {dialog.title}: {e}")

    await event.respond(append_watermark_to_message(f"⚡ Message Casted To: {sent_count} Groups"))
    await event.delete()

# Spam Command
@client.on(events.NewMessage(pattern=r'\.spam (\d+)', outgoing=True))
async def spam(event):
    sender = await event.get_sender()
    if not is_device_owner(sender.id):
        await event.respond(append_watermark_to_message("❌ You are not authorized to use this command."))
        await event.delete()
        return

    count = int(event.pattern_match.group(1))
    if count <= 0 or count > 100:
        await event.respond(append_watermark_to_message("❌ The spam count must be between 1 and 100."))
        await event.delete()
        return

    reply_message = await event.get_reply_message()
    if not reply_message:
        await event.respond(append_watermark_to_message("❌ Please reply to a message to spam."))
        await event.delete()
        return

    for _ in range(count):
        try:
            if reply_message.media:
                media_path = await client.download_media(reply_message.media)
                await client.send_file(event.chat_id, media_path, caption=append_watermark_to_message(reply_message.message))
            else:
                await client.send_message(event.chat_id, append_watermark_to_message(reply_message.message))
        except Exception as e:
            print(f"Error during spam: {e}")
            break
    await event.delete()

# QR Code Handling
@client.on(events.NewMessage(pattern='.addqr', outgoing=True))
async def add_qr(event):
    reply_message = await event.get_reply_message()
    if not reply_message or not reply_message.media:
        await event.respond(append_watermark_to_message("❌ Please reply to a QR code image to use this command."))
        await event.delete()
        return

    try:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_path = os.path.join(QR_CODE_DIR, f"qr_{timestamp}.jpg")
        await client.download_media(reply_message.media, file_path)
        await event.respond(append_watermark_to_message("✅ QR code added successfully!"))
    except Exception as e:
        await event.respond(append_watermark_to_message("❌ Failed to add QR code."))
        print(f"Error: {e}")
    await event.delete()

@client.on(events.NewMessage(pattern='.getqr', outgoing=True))
async def get_qr(event):
    qr_files = sorted(os.listdir(QR_CODE_DIR))
    if not qr_files:
        await event.respond(append_watermark_to_message("❌ No QR codes available."))
        await event.delete()
        return

    try:
        for qr_file in qr_files:
            file_path = os.path.join(QR_CODE_DIR, qr_file)
            await client.send_file(event.chat_id, file_path, caption=append_watermark_to_message(f"🖼 QR Code: {qr_file}"))
            await asyncio.sleep(1)
    except Exception as e:
        await event.respond(append_watermark_to_message("❌ Failed to send QR code."))
        print(f"Error sending QR code: {e}")
    await event.delete()

# Help Command
@client.on(events.NewMessage(pattern='.help', outgoing=True))
async def show_help(event):
    help_text = (
        "**Available Commands:**\n"
        "--------------------------\n"
        "**.gcast** - Broadcast a message to groups.\n"
        "**.jgc** - Join detected group links.\n"
        "**.spam <count>** - Spam a reply message.\n"
        "**.addqr** - Add a QR code (reply image).\n"
        "**.getqr** - Retrieve all saved QR codes.\n"
        "**.addbl** - Blacklist the current group.\n"
        "**.unbl** - Unblacklist the current group.\n"
        "**.showbl** - Show all blacklisted groups.\n"
        "--------------------------"
    )
    await event.respond(help_text)
    await event.delete()

async def main():
    await client.start()
    global device_owner_id
    device_owner = await client.get_me()
    device_owner_id = device_owner.id
    print(f"Bot is running as {device_owner.username}")

if __name__ == '__main__':
    client.loop.run_until_complete(main())
    client.run_until_disconnected()
