import os
import sqlite3
import uuid
import telebot

# =========================
# BOT TOKEN
# =========================

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN is not set")

bot = telebot.TeleBot(TOKEN)


# =========================
# DATABASE
# =========================

db = sqlite3.connect(
    "database.db",
    check_same_thread=False
)

cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_key TEXT UNIQUE,
    file_id TEXT,
    file_type TEXT,
    caption TEXT
)
""")

db.commit()


# =========================
# SAVE FILE
# =========================

def save_file(file_key, file_id, file_type, caption):

    cursor.execute("""
    INSERT INTO files
    (file_key, file_id, file_type, caption)
    VALUES (?, ?, ?, ?)
    """, (
        file_key,
        file_id,
        file_type,
        caption
    ))

    db.commit()


# =========================
# GET FILE
# =========================

def get_file(file_key):

    cursor.execute("""
    SELECT file_id, file_type, caption
    FROM files
    WHERE file_key = ?
    """, (file_key,))

    return cursor.fetchone()


# =========================
# RECEIVE FILE
# =========================

@bot.message_handler(
    content_types=[
        "document",
        "video",
        "audio",
        "photo"
    ]
)
def receive_file(message):

    file_id = None
    file_type = None

    if message.document:
        file_id = message.document.file_id
        file_type = "document"

    elif message.video:
        file_id = message.video.file_id
        file_type = "video"

    elif message.audio:
        file_id = message.audio.file_id
        file_type = "audio"

    elif message.photo:
        file_id = message.photo[-1].file_id
        file_type = "photo"

    caption = message.caption or ""

    file_key = uuid.uuid4().hex[:12]

    save_file(
        file_key,
        file_id,
        file_type,
        caption
    )

    username = bot.get_me().username

    link = f"https://t.me/{username}?start={file_key}"

    bot.reply_to(
        message,
        f"✅ FILE SAVED\n\n"
        f"🔗 SHARE LINK:\n{link}\n\n"
        f"🆔 ID: {file_key}"
    )


# =========================
# START COMMAND
# =========================

@bot.message_handler(commands=["start"])
def start(message):

    parts = message.text.split()

    if len(parts) == 1:

        bot.reply_to(
            message,
            "👋 Welcome!\n\n"
            "📁 Send me a file to create a share link."
        )

        return

    file_key = parts[1]

    data = get_file(file_key)

    if not data:

        bot.reply_to(
            message,
            "❌ File not found."
        )

        return

    file_id, file_type, caption = data

    chat_id = message.chat.id

    if file_type == "document":

        bot.send_document(
            chat_id,
            file_id,
            caption=caption
        )

    elif file_type == "video":

        bot.send_video(
            chat_id,
            file_id,
            caption=caption
        )

    elif file_type == "audio":

        bot.send_audio(
            chat_id,
            file_id,
            caption=caption
        )

    elif file_type == "photo":

        bot.send_photo(
            chat_id,
            file_id,
            caption=caption
        )


# =========================
# RUN BOT
# =========================

print("🤖 Bot Started...")

bot.infinity_polling()
