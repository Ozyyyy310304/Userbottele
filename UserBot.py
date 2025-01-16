from telethon import TelegramClient, events
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

# Ensure the directory exists
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

from telethon import TelegramClient, events
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

# Ensure the directory exists
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

from telethon import TelegramClient, events
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

# Ensure the directory exists
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
    # Notifikasi sedang mengirim
    SENDING_NOTIFICATION = "**Global Casting on Proses**"
    status_message = await event.respond(append_watermark_to_message(SENDING_NOTIFICATION))
    
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
    
    # Notifikasi pesan terkirim
    SENT_NOTIFICATION = f"**Message Casted To: {sent_count} Groups**"
    await status_message.edit(append_watermark_to_message(SENT_NOTIFICATION))
    
    # Delay 10 detik sebelum menghapus notifikasi
    await asyncio.sleep(10)
    await status_message.delete()
    await event.delete()  # Delete the original command message

# The rest of your code remains unchanged...




@client.on(events.NewMessage(pattern='.blacklist', outgoing=True))
async def blacklist_group(event):
    sender = await event.get_sender()
    if not is_device_owner(sender.id):
        await event.respond(append_watermark_to_message("❌ You are not authorized to use this command."))
        print("Unauthorized access attempt blocked.")
        await event.delete()  # Delete the command message
        return

    group_id = event.chat_id
    if group_id not in blacklisted_groups:
        blacklisted_groups.append(group_id)
        await event.respond(append_watermark_to_message("🚫 Group has been blacklisted successfully."))
    else:
        await event.respond(append_watermark_to_message("🚫 This group is already blacklisted."))
    await event.delete()  # Delete the command message after execution

@client.on(events.NewMessage(pattern='.addqr', outgoing=True))
async def add_qr(event):
    sender = await event.get_sender()
    if not is_device_owner(sender.id):
        await event.respond(append_watermark_to_message("❌ You are not authorized to use this command."))
        print("Unauthorized access attempt blocked.")
        await event.delete()  # Delete the command message
        return

    reply_message = await event.get_reply_message()
    if not reply_message or not reply_message.media:
        await event.respond(append_watermark_to_message("❌ Please reply to a QR code image to use this command."))
        await event.delete()  # Delete the command message
        return

    try:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_path = os.path.join(QR_CODE_DIR, f"qr_{timestamp}.jpg")
        await client.download_media(reply_message.media, file_path)
        await event.respond(append_watermark_to_message("✅ QR code added successfully!"))
        print(f"QR code added with timestamp: {timestamp}")
    except Exception as e:
        await event.respond(append_watermark_to_message("❌ Failed to add QR code."))
        print(f"Error: {e}")
    await event.delete()  # Delete the command message after execution

@client.on(events.NewMessage(pattern='.getqr', outgoing=True))
async def get_qr(event):
    qr_files = sorted(os.listdir(QR_CODE_DIR))
    if not qr_files:
        await event.respond(append_watermark_to_message("❌ No QR codes available."))
        await event.delete()  # Delete the command message
        return

    try:
        for qr_file in qr_files:
            file_path = os.path.join(QR_CODE_DIR, qr_file)
            await client.send_file(event.chat_id, file_path, caption=append_watermark_to_message(f"🖼 QR Code: {qr_file}"))
            await asyncio.sleep(1)  # Optional delay to avoid spamming
    except Exception as e:
        await event.respond(append_watermark_to_message("❌ Failed to send QR code."))
        print(f"Error sending QR code: {e}")
    await event.delete()  # Delete the command message after execution

@client.on(events.NewMessage(pattern='.afk', outgoing=True))
async def afk(event):
    global afk_reason
    afk_reason = event.message.message[len('.afk '):].strip()
    if not afk_reason:
        afk_reason = "AFK"
    await event.respond(append_watermark_to_message(f"💤 AFK mode enabled with reason: {afk_reason}"))
    print(f"AFK mode enabled with reason: {afk_reason}")
    await event.delete()  # Delete the command message after execution

@client.on(events.NewMessage(incoming=True))
async def handle_incoming(event):
    global afk_reason
    if afk_reason and event.mentioned:
        await event.reply(append_watermark_to_message(f"🤖 I am currently AFK. Reason: {afk_reason}"))

@client.on(events.NewMessage(pattern='.back', outgoing=True))
async def back(event):
    global afk_reason
    afk_reason = None
    await event.respond(append_watermark_to_message("👋 I am back now."))
    print("AFK mode disabled.")
    await event.delete()  # Delete the command message after execution

@client.on(events.NewMessage(pattern='.help', outgoing=True))
async def show_help(event):
    help_text = (
        "🛠 **Available Commands:**\n"
        ".gcast - Broadcast a message to all groups.\n"
        ".blacklist - Blacklist the current group from receiving promotions.\n"
        ".addqr - Add a QR code (send image as a reply to this command).\n"
        ".getqr - Retrieve all saved QR codes.\n"
        ".afk <reason> - Set an AFK message with a reason.\n"
        ".back - Disable AFK mode.\n"
        ".ping - Check the bot's response time.\n"
        f"\n{WATERMARK_TEXT}"
    )
    await event.respond(help_text)
    await event.delete()  # Delete the command message after execution

@client.on(events.NewMessage(pattern='.ping', outgoing=True))
async def ping(event):
    start = datetime.now()
    # Ganti emoji di sini menggunakan emoji ID premium
    await event.respond(append_watermark_to_message("<emoji id=\"5927022501606460935\">🚫</emoji> Pong!"))
    end = datetime.now()
    latency = (end - start).total_seconds() * 1000
    await event.respond(append_watermark_to_message(f"📈 Ping: {latency:.2f} ms"))
    await event.delete()  # Delete the command message after execution


async def run_bot():
    await main()
    print("Bot is running...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(run_bot())
