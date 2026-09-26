import os
from dotenv import load_dotenv

# Carrega as variáveis do ficheiro .env
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL_SECONDS", "5"))
DB_PATH = os.path.join(os.path.dirname(__file__), "../../tennis_bot.db")