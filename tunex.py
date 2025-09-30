import telebot
from yt_dlp import YoutubeDL
import os
import time
from concurrent.futures import ThreadPoolExecutor
import tempfile

TOKEN = "8001415471:AAHuicYryT-O6g-Iitt275XFyEyZ5cGW_Bs"
bot = telebot.TeleBot(TOKEN)
FFMPEG_PATH = r"C:\FFmpeg\bin"

executor = ThreadPoolExecutor(max_workers=5)

ADMIN_ID = 8166301010

def download_mp3(query, chat_id):
    try:
        bot.send_message(chat_id, f"🔍 Ищу вашу песню: {query}...")
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{tmpdir}/%(title)s.%(ext)s',
                'noplaylist': True,
                'quiet': True,
                'ffmpeg_location': FFMPEG_PATH,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch1:{query}", download=True)
                filename = ydl.prepare_filename(info['entries'][0]).replace(".webm", ".mp3")
                
                time.sleep(1)
                
                bot.send_message(chat_id, f"✅ Песня готова: {info['entries'][0]['title']}")
                with open(filename, 'rb') as audio:
                    bot.send_audio(chat_id, audio)
                    
    except Exception as e:
        bot.send_message(chat_id, f"❌ Произошла ошибка: {e}")

# --- Команда /start ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🎵 Привет! Напиши название песни, и я пришлю mp3 прямо сюда 🎧\n\n"
    )

# --- Команда /about ---
@bot.message_handler(commands=['about'])
def about(message):
    bot.send_message(
        message.chat.id,
        "ℹ️ Этот бот создан для поиска и загрузки песен с YouTube в формате MP3.\n\n"
        "🎧 Просто напиши название песни — бот найдёт и отправит её тебе.\n\n"
        "👨‍💻 Разработчик: @coder_1771"
    )

# --- Функции обратной связи ---
def get_feedback(sms):
    if not sms.text:
        bot.send_message(sms.chat.id, "Пожалуйста, отправьте текст.")
        return

    user = sms.from_user
    username = user.username or 'Не указан'
    first_name = user.first_name or ''
    last_name = user.last_name or ''
    feedback = sms.text

    formatted_feedback = (
        f'🆕 Новый отзыв\n\n'
        f'🛂 Пользователь @{username}\n'
        f'📋 Имя: {first_name} {last_name}\n\n'
        f'✍️ Отзыв: {feedback}'
    )
    
    bot.send_message(chat_id=ADMIN_ID, text=formatted_feedback)
    bot.send_message(sms.chat.id, "✅ Спасибо за ваш отзыв!")

@bot.message_handler(commands=['feedback'])
def feedback_handler(sms):
    bot.send_message(
        sms.chat.id,
        "🗒 Отправьте ваш отзыв или предложение:",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(sms, get_feedback)

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    query = message.text
    bot.send_message(message.chat.id, f"🚀 Обрабатываю ваш запрос: {query}")
    executor.submit(download_mp3, query, message.chat.id)

bot.infinity_polling()