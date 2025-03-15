import requests
from bs4 import BeautifulSoup
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
import os
import time
import threading

# Lấy token từ biến môi trường
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# URL danh sách căn hộ UR tại 和光市
UR_URL = "https://www.ur-net.go.jp/chintai/kanto/area/11_04_list.html"

def check_ur_wako():
    """Kiểm tra danh sách căn hộ UR 和光市"""
    response = requests.get(UR_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    apartments = soup.find_all("div", class_="property-list")

    available_rooms = []
    for apt in apartments:
        name = apt.find("h3").text.strip()
        status = apt.find("span", class_="status").text.strip()
        if "募集中" in status:  # Chỉ lấy phòng đang mở đăng ký
            available_rooms.append(name)

    return available_rooms

def check_command(update: Update, context: CallbackContext):
    """Xử lý khi người dùng gửi lệnh /check"""
    available = check_ur_wako()
    if available:
        message = "🏠 *Danh sách phòng trống tại UR 和光市:*\n\n" + "\n".join(available)
    else:
        message = "🚫 Hiện tại không có phòng trống nào."
    
    update.message.reply_text(message, parse_mode="Markdown")

def send_telegram_message(message):
    """Gửi tin nhắn đến Telegram"""
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="Markdown")

def auto_check():
    """Tự động kiểm tra mỗi 10 phút và gửi tin nhắn nếu có phòng trống"""
    last_available = []
    while True:
        available = check_ur_wako()
        if available and available != last_available:
            message = "🏠 *Cập nhật mới! Có phòng trống tại UR 和光市:*\n\n" + "\n".join(available)
            send_telegram_message(message)
            last_available = available
        time.sleep(300)  # Chờ 10 phút

def main():
    """Chạy bot"""
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("check", check_command))

    # Chạy auto_check trong luồng riêng
    thread = threading.Thread(target=auto_check, daemon=True)
    thread.start()

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
