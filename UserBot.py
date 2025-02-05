from telethon import TelegramClient, events
from telethon.tl.functions.messages import ImportChatInviteRequest
import asyncio
from datetime import datetime
import json
import re
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import os


api_id = '29798494'
api_hash = '53273c1de3e68a9ecdb90de2dcf46f6c'
# Jika menggunakan file session langsung
client = TelegramClient('userbot.session', api_id, api_hash)
client = TelegramClient('userbot', api_id, api_hash)
device_owner_id = None
afk_reason = None

# Directory to store QR code images
QR_CODE_DIR = "qr_codes"

# Ensure the directory exists
os.makedirs(QR_CODE_DIR, exist_ok=True)

# Fungsi untuk memuat data blacklist dari file JSON
def load_blacklist():
    try:
        with open('blacklist.json', 'r') as file:
            data = json.load(file)
        return data['blacklisted_groups']
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Fungsi untuk menyimpan data blacklist ke dua file JSON
def save_blacklist(blacklisted_groups):
    data = {"blacklisted_groups": blacklisted_groups}
    
    # Simpan ke file blacklist.json
    with open('blacklist.json', 'w') as file:
        json.dump(data, file, indent=4)
    
    # Simpan ke file blacklist.json.save
    with open('blacklist.json.save', 'w') as file_save:
        json.dump(data, file_save, indent=4)

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

detected_links = set()  # Inisialisasi set untuk menyimpan link yang terdeteksi
detected_links = set()

def extract_links_from_message(message):
    # Pola regex untuk mendeteksi link grup Telegram
    pattern = r'https://t\.me/\+[\w-]+'
    return re.findall(pattern, message)

@client.on(events.NewMessage(incoming=True))
async def detect_links(event):
    if event.message.text:
        links = extract_links_from_message(event.message.text)
        for link in links:
            detected_links.add(link)

async def join_groups_in_batches(links, batch_size, delay_between_batches, delay_between_joins):
    """
    Gabung ke grup dalam batch untuk menghindari rate limit Telegram.

    Args:
        links (set): Kumpulan link grup.
        batch_size (int): Jumlah grup per batch.
        delay_between_batches (int): Jeda antar batch dalam detik.
        delay_between_joins (int): Jeda antar join dalam detik.
    """
    links = list(links)
    total_links = len(links)
    success_count = 0
    failed_count = 0

    for i in range(0, total_links, batch_size):
        batch = links[i:i + batch_size]
        print(f"🚀 Processing batch {i // batch_size + 1}: {batch}")

        for link in batch:
            try:
                invite_hash = link.split('+')[-1]  # Ambil hash undangan dari link
                await client(ImportChatInviteRequest(invite_hash))
                print(f"✅ Successfully joined: {link}")
                success_count += 1
                await asyncio.sleep(delay_between_joins)
            except Exception as e:
                print(f"❌ Failed to join {link}: {e}")
                if "A wait of" in str(e):
                    wait_time = int(re.search(r"(\d+)", str(e)).group(1))
                    print(f"⏳ Rate limited. Waiting for {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                failed_count += 1

        print(f"⏳ Batch {i // batch_size + 1} completed. Waiting {delay_between_batches} seconds...")
        await asyncio.sleep(delay_between_batches)

    return success_count, failed_count

@client.on(events.NewMessage(pattern='.jgc', outgoing=True))
async def join_groups(event):
    sender = await event.get_sender()
    if sender.id != device_owner_id:
        await event.respond("❌ You are not authorized to use this command.")
        await event.delete()
        return

    if not detected_links:
        await event.respond("❌ No group links detected.")
        await event.delete()
        return

    # Batasi ukuran batch dan delay
    batch_size = 10
    delay_between_batches = 600  # 10 menit
    delay_between_joins = 30     # 15 detik

    success_count, failed_count = await join_groups_in_batches(
        detected_links, batch_size, delay_between_batches, delay_between_joins
    )

    await event.respond(
        f"✅ Successfully joined {success_count} groups.\n❌ Failed to join {failed_count} groups."
    )
    detected_links.clear()
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
    # Notifikasi sedang mengirim
    SENDING_NOTIFICATION = "**🚨 Proses Global Casting**"
    status_message = await event.respond(append_watermark_to_message(SENDING_NOTIFICATION))
    
    groups = [dialog for dialog in await client.get_dialogs() if dialog.is_group]

    for dialog in groups:
        blacklisted_groups = load_blacklist()
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
    SENT_NOTIFICATION = f"⚡ Message Casted To: {sent_count} Groups"
    await status_message.edit(append_watermark_to_message(SENT_NOTIFICATION))
    
    # Delay 10 detik sebelum menghapus notifikasi
    await asyncio.sleep(10)
    await status_message.delete()
    await event.delete()  # Delete the original command message

@client.on(events.NewMessage(pattern='.addbl', outgoing=True))
async def blacklist_group(event):
    sender = await event.get_sender()
    if not is_device_owner(sender.id):
        await event.respond(append_watermark_to_message("❌ You are not authorized to use this command."))
        print("Unauthorized access attempt blocked.")
        await event.delete()  # Delete the command message
        return

    group_id = event.chat_id
    blacklisted_groups = load_blacklist()

    if group_id not in blacklisted_groups:
        blacklisted_groups.append(group_id)
        save_blacklist(blacklisted_groups)
        await event.respond(append_watermark_to_message("🚫 Group has been blacklisted successfully."))
    else:
        await event.respond(append_watermark_to_message("🚫 This group is already blacklisted."))
    await event.delete()  # Delete the command message after execution

@client.on(events.NewMessage(pattern='.unbl', outgoing=True))
async def unblacklist_group(event):
    sender = await event.get_sender()
    if not is_device_owner(sender.id):
        await event.respond(append_watermark_to_message("❌ You are not authorized to use this command."))
        print("Unauthorized access attempt blocked.")
        await event.delete()  # Delete the command message
        return

    group_id = event.chat_id
    blacklisted_groups = load_blacklist()

    if group_id in blacklisted_groups:
        blacklisted_groups.remove(group_id)
        save_blacklist(blacklisted_groups)
        await event.respond(append_watermark_to_message("✅ Group has been removed from the blacklist."))
    else:
        await event.respond(append_watermark_to_message("❌ This group is not in the blacklist."))
    
    await event.delete()  # Delete the command message after execution

@client.on(events.NewMessage(pattern='.showbl', outgoing=True))
async def show_blacklist(event):
    blacklisted_groups = load_blacklist()

    if not blacklisted_groups:
        await event.respond(append_watermark_to_message("❌ No groups in the blacklist."))
    else:
        groups_info = []
        for group_id in blacklisted_groups:
            try:
                group = await client.get_entity(group_id)  # Dapatkan info grup berdasarkan ID
                groups_info.append(f"{group.title} (ID: {group.id})")
            except Exception as e:
                groups_info.append(f"Error fetching group: {group_id}")
        
        groups_list = "\n".join(groups_info)
        await event.respond(append_watermark_to_message(f"🔴 Blacklisted Groups:\n{groups_list}"))
    
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
    
@client.on(events.NewMessage(pattern=r'\.spam (\d+)', outgoing=True))
async def spam(event):
    sender = await event.get_sender()
    if not is_device_owner(sender.id):
        await event.respond(append_watermark_to_message("❌ You are not authorized to use this command."))
        await event.delete()
        return

    # Parse jumlah spam dari argumen command
    args = event.pattern_match.group(1)
    if not args.isdigit():
        await event.respond(append_watermark_to_message("❌ Invalid format. Use `.spam <number>` and reply to a message."))
        await event.delete()
        return

    count = int(args)
    if count <= 0 or count > 100:  # Batasi jumlah spam untuk keamanan
        await event.respond(append_watermark_to_message("❌ The spam count must be between 1 and 100."))
        await event.delete()
        return

    reply_message = await event.get_reply_message()
    if not reply_message:
        await event.respond(append_watermark_to_message("❌ Please reply to a message to spam."))
        await event.delete()
        return

    # Mulai spam
    for i in range(count):
        try:
            if reply_message.media:
                media_path = await client.download_media(reply_message.media)
                await client.send_file(event.chat_id, media_path, caption=append_watermark_to_message(reply_message.message))
            else:
                await client.send_message(event.chat_id, append_watermark_to_message(reply_message.message))
        except Exception as e:
            print(f"Error during spam: {e}")
            break
            
    await event.delete()  # Hapus pesan command setelah selesai


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
        "**Available Commands:**\n"
        "--------------------------\n"
        "**.gcast** - Broadcast a message to groups.\n"
        "**.spam <count>** - Spamming The message you reply.\n"
        "**.jgc** - Joining all group on link\n"
        "**.addbl** - Blacklist the current group.\n"
        "**.unbl** - Unblacklist the current group.\n"
        "**.showbl** - Show all blacklisted groups.\n"
        "**.addqr** - Add a QR code (reply image).\n"
        "**.getqr** - Retrieve all saved QR codes.\n"
        "**.afk <reason>** - Set an AFK message.\n"
        "**.back** - Disable AFK mode.\n"
        "**.ping** - Check the bot's response time.\n"
        "--------------------------\n"
        "**and when you look at me,theres only memories is us kissin in the moonlight**"
        f"{WATERMARK_TEXT}"
    )
    await event.respond(help_text)
    await event.delete()  # Delete the command message after execution

@client.on(events.NewMessage(pattern='.ping', outgoing=True))
async def ping(event):
    start = datetime.now()
    await event.respond(append_watermark_to_message("🏓 Pong!"))
    end = datetime.now()
    latency = (end - start).total_seconds() * 1000
    await event.respond(f"📈Network Speed: {latency:.2f} ms")
    await event.delete()  # Delete the command message after execution

async def run_bot():
    await main()
    print("Bot is running...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(run_bot())
