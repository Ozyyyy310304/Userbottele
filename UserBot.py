from telethon import TelegramClient, events
import os
import asyncio
from datetime import datetime
import json
from pytgcalls import PyTgCalls
from pytgcalls.types import InputAudioStream

api_id = '29798494'
api_hash = '53273c1de3e68a9ecdb90de2dcf46f6c'

client = TelegramClient('userbot', api_id, api_hash)
pytgcalls = PyTgCalls(client)

device_owner_id = None
afk_reason = None
QR_CODE_DIR = "qr_codes"
os.makedirs(QR_CODE_DIR, exist_ok=True)

# Load and save blacklist
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

WATERMARK_TEXT = ""

def append_watermark_to_message(message):
    return f"{message}\n\n{WATERMARK_TEXT}"

async def main():
    await client.start()
    print("Client Created")
    global device_owner_id

    if not await client.is_user_authorized():
        phone_number = input("Enter phone number: ")
        await client.sign_in(phone_number, input("Enter code: "))
    device_owner = await client.get_me()
    device_owner_id = device_owner.id

def is_device_owner(sender_id):
    return sender_id == device_owner_id

@client.on(events.NewMessage(pattern='.jvc', outgoing=True))
async def join_voice_chat(event):
    sender = await event.get_sender()
    if not is_device_owner(sender.id):
        await event.delete()
        return
    chat_id = event.chat_id
    try:
        await pytgcalls.join_group_call(chat_id, InputAudioStream('input.raw'))
        notif = await event.respond("✅ Joined Voice Chat.")
        await asyncio.sleep(5)
        await notif.delete()
    except Exception as e:
        await event.respond(f"❌ Failed to join: {e}")
    await event.delete()

@client.on(events.NewMessage(pattern='.lvc', outgoing=True))
async def leave_voice_chat(event):
    sender = await event.get_sender()
    if not is_device_owner(sender.id):
        await event.delete()
        return
    chat_id = event.chat_id
    try:
        await pytgcalls.leave_group_call(chat_id)
        notif = await event.respond("✅ Left Voice Chat.")
        await asyncio.sleep(5)
        await notif.delete()
    except Exception as e:
        await event.respond(f"❌ Failed to leave: {e}")
    await event.delete()

@client.on(events.NewMessage(pattern='.help', outgoing=True))
async def show_help(event):
    help_text = (
        "**Available Commands:**\n"
        "--------------------------\n"
        "**.gcast** - Broadcast a message to groups.\n"
        "**.spam <count>** - Spamming the message you reply to.\n"
        "**.addbl** - Blacklist the current group.\n"
        "**.unbl** - Unblacklist the current group.\n"
        "**.showbl** - Show all blacklisted groups.\n"
        "**.addqr** - Add a QR code (reply image).\n"
        "**.getqr** - Retrieve all saved QR codes.\n"
        "**.jvc** - Join the voice chat in the current group.\n"
        "**.lvc** - Leave the voice chat in the current group.\n"
        "**.afk <reason>** - Set an AFK message.\n"
        "**.back** - Disable AFK mode.\n"
        "**.ping** - Check the bot's response time.\n"
        "--------------------------\n"
        "**and when you look at me,theres only memories,that we kissin in the moonlight**"
        f"{WATERMARK_TEXT}"
    )
    await event.respond(help_text)
    await event.delete()

async def run_bot():
    await main()
    print("Bot is running...")
    await pytgcalls.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(run_bot())
