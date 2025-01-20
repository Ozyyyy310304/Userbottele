from telethon import TelegramClient, events
from telethon.tl.types import MessageEntityCustomEmoji
import os
import asyncio
from datetime import datetime

api_id = '29798494'
api_hash = '53273c1de3e68a9ecdb90de2dcf46f6c'

client = TelegramClient('userbot', api_id, api_hash)
device_owner_id = None
afk_reason = None

# Directory to store QR code images
QR_CODE_DIR = "qr_codes"
os.makedirs(QR_CODE_DIR, exist_ok=True)

blacklisted_groups = []
WATERMARK_TEXT = ""

# Function to append watermark to a message
def append_watermark_to_message(message):
    return f"{message}\n\n{WATERMARK_TEXT}"

async def main():
    await client.start()
    print("Client Created")

    global device_owner_id

    if not await client.is_user_authorized():
        phone_number = input("Please enter your phone number (with country code): ")
        try:
            await client.send_code_request(phone_number)
            print("Code sent successfully!")
        except Exception as e:
            print(f"Error requesting code: {e}")
            return
        
        code = input("Please enter the code you received: ")
        try:
            await client.sign_in(phone_number, code=code)
            print("Signed in successfully!")
        except Exception as e:
            print(f"Error during sign in: {e}")
            return

    print("Client Authenticated")
    device_owner = await client.get_me()
    device_owner_id = device_owner.id
    print(f"Device owner ID: {device_owner_id}")

def is_device_owner(sender_id):
    return sender_id == device_owner_id

@client.on(events.NewMessage(pattern='.ping', outgoing=True))
async def ping(event):
    start = datetime.now()

    # ID emoji premium
    custom_emoji_id = 5269563867305879894  # ID emoji premium

    # Kirim pesan dengan emoji premium
    await event.respond(
        "\ud83c\udfd3 Pong!",
        entities=[
            MessageEntityCustomEmoji(
                offset=0,  # Posisi karakter emoji
                length=1,  # Panjang karakter yang dirender sebagai emoji
                document_id=custom_emoji_id
            )
        ]
    )
    end = datetime.now()
    latency = (end - start).total_seconds() * 1000

    # Kirim latensi dengan tambahan emoji premium
    await event.respond(
        f"<emoji id={custom_emoji_id}>\ud83c\udfd3</emoji> Ping: {latency:.2f} ms",
        parse_mode="html"
    )
    await event.delete()

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
    delay = 0.1
    status_message = await event.respond("**\ud83d\udea8 Proses Global Casting...**")
    groups = [dialog for dialog in await client.get_dialogs() if dialog.is_group]

    for dialog in groups:
        if dialog.id in blacklisted_groups:
            continue
        try:
            if reply_message.media:
                media_path = await client.download_media(reply_message.media)
                await client.send_file(dialog.id, media_path, caption=append_watermark_to_message(reply_message.message))
            else:
                await client.send_message(dialog.id, append_watermark_to_message(reply_message.message))
            sent_count += 1
            await asyncio.sleep(delay)
        except Exception as e:
            print(f"Failed to send to {dialog.title}: {e}")

    await status_message.edit(f"⚡ **Message Casted To: {sent_count} Groups**")
    await asyncio.sleep(10)
    await status_message.delete()
    await event.delete()

async def run_bot():
    await main()
    print("Bot is running...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(run_bot())
