import os
import sys
import django
from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from visualization.models import Parcel, SensorData
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

@sync_to_async
def get_system_status():
    parcels = Parcel.objects.filter(is_active=True)
    status_lines = ["🌿 *ATYS System Status* 🌿\n"]
    for p in parcels:
        last_data = SensorData.objects.filter(parcel=p).order_by('-timestamp').first()
        if last_data:
            line = f"📍 *{p.name}*\n" \
                   f"🌡 Temp: {last_data.temperature}°C | 💧 Moist: {last_data.soil_moisture}%\n" \
                   f"🔋 Battery: {p.battery_level}% | 📶 Signal: {p.rssi} dBm\n" \
                   f"⚙️ Irrigating: {'Yes 💦' if p.is_irrigating else 'No 🛑'}\n"
            status_lines.append(line)
        else:
            status_lines.append(f"📍 *{p.name}*: No data available.\n")
    return "\n".join(status_lines)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    status_text = await get_system_status()
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def send_alert(message: str):
    bot = Application.builder().token(TOKEN).build().bot
    if CHAT_ID:
        await bot.send_message(chat_id=CHAT_ID, text=f"🚨 *ATYS ALERT* 🚨\n{message}", parse_mode='Markdown')

def main() -> None:
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in environment.")
        return
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("status", status_command))
    print("Telegram Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
