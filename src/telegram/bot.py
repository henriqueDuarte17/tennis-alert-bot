import requests
from src.config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_telegram_message(message):
    """Envia uma mensagem de texto formatada para o chat do Telegram configurado."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[ERRO] Token ou Chat ID do Telegram não configurados no ficheiro .env")
        return False
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("[SUCESSO] Alerta enviado para o Telegram!")
            return True
        else:
            print(f"[ERRO] Falha ao enviar para o Telegram: {response.text}")
            return False
    except Exception as e:
        print(f"[EXCEÇÃO] Erro de rede ao comunicar com o Telegram: {e}")
        return False