import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from zoneinfo import ZoneInfo
from src.storage.database import init_db, alert_was_sent, mark_alert_as_sent
from src.telegram.bot import send_telegram_message
from src.alerts.formatter import format_mto_alert, format_upset_alert
from src.detectors.mto_detector import check_for_mto
from src.detectors.upset_detector import check_for_first_set_upset
from src.data_sources.flashscore_client import fetch_live_tennis_matches

# --- MINI SERVIDOR WEB (Para manter o Render ativo no plano gratuito) ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Tennis Alert Bot is alive and running!")

def run_web_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHandler)
    server.serve_forever()

# --- CICLO PRINCIPAL DO BOT ---
def run_bot_loop():
    print("=== TENNIS ALERT BOT A INICIAR ===")
    init_db()
    
    check_interval = 480  # 8 minutos em segundos (480s)
    start_hour = 10       # Início às 10:00 (Hora de Portugal)
    end_hour = 23         # Fim às 23:00 (Hora de Portugal)
    
    try:
        while True:
            # Valida a hora atual rigorosamente em Portugal (Lisboa)
            hora_atual = datetime.now(ZoneInfo("Europe/Lisbon")).hour
            
            # Valida se estamos dentro do horário ativo (10h às 23h)
            if not (start_hour <= hora_atual < end_hour):
                print(f"[{time.strftime('%H:%M:%S')}] Fora do horário ativo em PT ({start_hour}h às {end_hour}h). Em repouso...")
                time.sleep(1800)  # Dorme 30 minutos antes de verificar novamente
                continue

            current_time = datetime.now(ZoneInfo("Europe/Lisbon")).strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n[{current_time} PT] A procurar jogos ao vivo...")
            
            # Vai buscar os jogos à fonte de dados
            matches = fetch_live_tennis_matches()
            
            if not matches:
                print("Nenhum jogo ativo ou dados disponíveis neste ciclo.")
            
            for match in matches:
                match_id = match.get("match_id")
                odds_data = match.get("odds", {})
                
                # 1. Verificar Medical Timeout (MTO)
                mto_detected, player_affected = check_for_mto(match)
                if mto_detected:
                    alert_type = "MTO"
                    if not alert_was_sent(match_id, alert_type):
                        print(f"[ALERTA] MTO detetado para {player_affected} (Jogo: {match_id})")
                        msg = format_mto_alert(match, player_affected)
                        if send_telegram_message(msg):
                            mark_alert_as_sent(match_id, alert_type, f"MTO: {player_affected}")
                
                # 2. Verificar Upset no 1.º Set
                upset_detected, winner, favorite = check_for_first_set_upset(match, odds_data)
                if upset_detected:
                    alert_type = "UPSET_SET_1"
                    if not alert_was_sent(match_id, alert_type):
                        print(f"[ALERTA] Upset detetado! {winner} venceu o 1.º set (Favorito era: {favorite})")
                        msg = format_upset_alert(
                            match, winner, favorite,
                            odds_data.get("odds_favorite", 1.3),
                            odds_data.get("odds_underdog", 3.5)
                        )
                        if send_telegram_message(msg):
                            mark_alert_as_sent(match_id, alert_type, f"Upset set 1: {winner}")
            
            print(f"Ciclo concluído. A aguardar 8 minutos para a próxima verificação...")
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        print("\n[BOT] Interrupção manual detetada (Ctrl+C). A encerrar o bot de forma segura.")

if __name__ == "__main__":
    # Inicia o mini-servidor web numa thread paralela para cumprir os requisitos do Render
    server_thread = threading.Thread(target=run_web_server, daemon=True)
    server_thread.start()
    
    # Arranca o loop principal do bot
    run_bot_loop()