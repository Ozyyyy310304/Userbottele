from telethon import TelegramClient, events
import os
import asyncio
from datetime import datetime

# API ID dan API Hash yang sama
api_id = '29798494'
api_hash = '53273c1de3e68a9ecdb90de2dcf46f6c'

# Session yang terpisah untuk dua akun
session_1 = 'userbot1_session'
session_2 = 'userbot2_session'

# Membuat client untuk kedua akun
client1 = TelegramClient(session_1, api_id, api_hash)
client2 = TelegramClient(session_2, api_id, api_hash)

# Variabel global
device_owner_id = None
afk_reason = None
QR_CODE_DIR = "qr_codes"
os.makedirs(QR_CODE_DIR, exist_ok=True)

blacklisted_groups = []
WATERMARK_TEXT = ""

# Fungsi untuk menambahkan watermark pada pesan
def append_watermark_to_message(message):
    return f"{message}\n\n{WATERMARK_TEXT}"

# Fungsi utama untuk memulai kedua client
async def main():
    await client1.start()
    await client2.start()
    print("Both clients started")

    # Auth untuk client pertama
    global device_owner_id
    if not await client1.is_user_authorized():
        phone_number = input("Please enter your phone number (with country code): ")
        try:
            await client1.send_code_request(phone_number)
            print("Code sent successfully!")
        except Exception as e:
            print(f"Error requesting code: {e}")
            return
        code = input("Please enter the code you received: ")
        try:
            await client1.sign_in(phone_number, code=code)
            print("Signed in successfully!")
        except Exception as e:
            print(f"Error during sign in: {e}")
            return

    device_owner = await client1.get_me()
    device_owner_id = device_owner.id
    print(f"Device owner ID: {device_owner_id}")

# Fungsi pengecekan apakah pengirim adalah pemilik perangkat
def is_device_owner(sender_id):
    return sender_id == device_owner_id

# Event dan Commands untuk client pertama
@client1.on(events.NewMessage(pattern='.gcast', outgoing=True))
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
    SENDING_NOTIFICATION = "**Global Casting on Proses**"
    status_message = await event.respond(append_watermark_to_message(SENDING_NOTIFICATION))

    groups = [dialog for dialog in await client1.get_dialogs() if dialog.is_group]
    for dialog in groups:
        if dialog.id in blacklisted_groups:
            continue
        try:
            if reply_message.media:
                media_path = await client1.download_media(reply_message.media)
                await client1.send_file(dialog.id, media_path, caption=append_watermark_to_message(reply_message.message))
            else:
                await client1.send_message(dialog.id, append_watermark_to_message(reply_message.message))
            sent_count += 1
            await asyncio.sleep(delay)
        except Exception as e:
            print(f"Failed to send to {dialog.title}: {e}")
    
    SENT_NOTIFICATION = f"**Message Casted To: {sent_count} Groups**"
    await status_message.edit(append_watermark_to_message(SENT_NOTIFICATION))
    await asyncio.sleep(10)
    await status_message.delete()
    await event.delete()

# Event dan Commands untuk client pertama
@client1.on(events.NewMessage(pattern='.blacklist', outgoing=True))
async def blacklist_group(event):
    sender = await event.get_sender()
    if not is_device_owner(sender.id):
        await event.respond(append_watermark_to_message("❌ You are not authorized to use this command."))
        print("Unauthorized access attempt blocked.")
        await event.delete()  
        return

    group_id = event.chat_id
    if group_id not in blacklisted_groups:
        blacklisted_groups.append(group_id)
        await event.respond(append_watermark_to_message("🚫 Group has been blacklisted successfully."))
    else:
        await event.respond(append_watermark_to_message("🚫 This group is already blacklisted."))
    await event.delete()  

# Event lainnya seperti .addqr, .getqr, .afk, dll tetap sama
# Misalnya: add_qr, get_qr, afk, back, help, ping dan lainnya

async def run_bots():
    await main()
    print("Both bots are running...")
    await asyncio.gather(
        client1.run_until_disconnected(),
        client2.run_until_disconnected()
    )

if __name__ == '__main__':
    asyncio.run(run_bots())
