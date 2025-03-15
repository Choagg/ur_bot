import requests
from bs4 import BeautifulSoup
from telegram import Bot
import time
import os

# Lấy token và chat ID từ biến môi trường
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# URL danh sách căn hộ UR tại 和光市
UR_URL = "https://www.ur-net.go.jp/chintai/kanto/area/11_04_list.html"

def check_ur_wako():
    response = requests.get(UR_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    apartments = soup.find_all("div", class_="property-list")

    available_rooms = []
    for apt in apartments:
        name = apt.find("h3").text.strip()
        status = apt.find("span", class_="status").text.strip()
        if "募集中" in status:
            available_rooms.append(name)

    return available_rooms

def send_telegram_message(message):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

while True:
    available = check_ur_wako()
    if available:
        message = "🏠 *Có phòng trống tại UR 和光市!*\n\n" + "\n".join(available)
        send_telegram_message(message)
    time.sleep(600)  # Kiểm tra mỗi 10 phút