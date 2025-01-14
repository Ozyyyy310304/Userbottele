from telethon import TelegramClient, events
import os
import asyncio
from datetime import datetime

api_id = '24318638'
api_hash = 'f0c6e208134ffee76c0d03bf72c6cdff'
client = TelegramClient('userbot', api_id, api_hash)

device_owner_id = None
afk_reason = None

# Directory to store QR code images
QR_CODE_DIR = "qr_codes"
os.makedirs(QR_CODE_DIR, exist_ok=True)

# Blacklisted group list
blacklisted_groups = []

# Watermark text
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

@client.on(events.NewMessage(pattern='.gcast', outgoing=True))
async def promote(event):
    await event.delete()
    sender = await event.get_sender()
    if not is_device_owner(sender.id):
        await event.respond(append_watermark_to_message("❌ You are not authorized to use this command."))
        return

    reply_message = await event.get_reply_message()
    if not reply_message:
        await event.respond(append_watermark_to_message("❌ Please reply to a message to promote."))
        return

    sent_count = 0
    delay = 0.1  # Set your desired delay time in seconds
    status_message = await event.respond(append_watermark_to_message("Starting promotion..."))
    groups = [dialog for dialog in await client.get_dialogs() if dialog.is_group]
    total_groups = len(groups)

    for dialog in groups:
        if dialog.id in blacklisted_groups:
            continue
        try:
            if reply_message.media:
                media_path = await client.download_media(reply_message.media)
                await client.send_file(dialog.id, media_path, caption=append_watermark_to_message(reply_message.message))
            else:
                message_with_watermark = append_watermark_to_message(reply_message.message)
                await client.send_message(dialog.id, message_with_watermark)
            sent_count += 1
            progress = (sent_count / total_groups) * 100
            await status_message.edit(append_watermark_to_message(f"Sending messages... {progress:.2f}%\nSent: {sent_count}"))
            await asyncio.sleep(delay)
        except Exception as e:
            print(f"Failed to send to {dialog.title}: {e}")

    await status_message.edit(append_watermark_to_message(f"✅ Finished sending messages!\nTotal groups sent: {sent_count}"))

@client.on(events.NewMessage(pattern='.blacklist', outgoing=True))
async def blacklist_group(event):
    await event.delete()
    sender = await event.get_sender()
    if not is_device_owner(sender.id):
        await event.respond(append_watermark_to_message("❌ You are not authorized to use this command."))
        return

    group_id = event.chat_id
    if group_id not in blacklisted_groups:
        blacklisted_groups.append(group_id)
        await event.respond(append_watermark_to_message("Group has been blacklisted successfully."))
    else:
        await event.respond(append_watermark_to_message("This group is already blacklisted."))

# Other command handlers remain similar...

async def run_bot():
    await main()
    print("Bot is running...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(run_bot())
