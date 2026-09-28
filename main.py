import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from zoneinfo import ZoneInfo
from src.storage.database import init_db, alert_was_sent, mark_alert_as_sent
from src.telegram.bot import send_telegram_message
from src.alerts.formatter import format_upset_alert
from src.detectors.upset_detector import check_for_first_set_upset
from src.data_sources.flashscore_client import fetch_live_tennis_matches

print(">>> O FICHEIRO MAIN.PY FOI CARREGADO COM SUCESSO! <<<", flush=True)

# --- MINI SERVIDOR WEB (Para manter o Render ativo no plano gratuito) ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Tennis Alert Bot is alive and running!")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_web_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHandler)
    server.serve_forever()

# --- CICLO PRINCIPAL DO BOT ---
def run_bot_loop():
    print("=== TENNIS ALERT BOT A INICIAR ===", flush=True)
    init_db()
    
    check_interval = 480  # 8 minutos em segundos (480s)
    start_hour = 10       # Início às 10:00 (Hora de Portugal)
    end_hour = 23         # Fim às 23:00 (Hora de Portugal)
    
    try:
        while True:
            loop_start_time = time.time()
            
            # Valida a hora atual rigorosamente em Portugal (Lisboa)
            hora_atual = datetime.now(ZoneInfo("Europe/Lisbon")).hour
            
            # Valida se estamos dentro do horário ativo (10h às 23h)
            if not (start_hour <= hora_atual < end_hour):
                print(f"[{time.strftime('%H:%M:%S')}] Fora do horário ativo em PT ({start_hour}h às {end_hour}h). Em repouso...", flush=True)
                time.sleep(1800)  # Dorme 30 minutos antes de verificar novamente
                continue

            current_time = datetime.now(ZoneInfo("Europe/Lisbon")).strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n[BOT] [{current_time} PT] A iniciar ronda de verificação na Live Tennis API...", flush=True)
            
            # Proteção contra bloqueios na API
            try:
                matches = fetch_live_tennis_matches()
            except Exception as e:
                print(f"[ERRO] Falha ao comunicar com a Live Tennis API: {e}", flush=True)
                matches = None
            
            if not matches:
                print("Nenhum jogo ativo ou dados disponíveis neste ciclo.", flush=True)
            else:
                for match in matches:
                    match_id = match.get("match_id")
                    odds_data = match.get("odds", {})
                    
                    # Verificar Upset no 1.º Set (Única prioridade do bot)
                    upset_detected, winner, favorite = check_for_first_set_upset(match, odds_data)
                    if upset_detected:
                        alert_type = "UPSET_SET_1"
                        
                        ja_enviado = alert_was_sent(match_id, alert_type)
                        print(f"[DB CHECK] Match {match_id} | Alerta {alert_type} já foi enviado antes? {ja_enviado}", flush=True)
                        
                        if not ja_enviado:
                            print(f"[ALERTA] A preparar envio para o Telegram: {winner} venceu o 1.º set (Favorito: {favorite})", flush=True)
                            msg = format_upset_alert(
                                match, winner, favorite,
                                odds_data.get("odds_favorite", 1.3),
                                odds_data.get("odds_underdog", 3.5)
                            )
                            
                            sucesso_envio = send_telegram_message(msg)
                            print(f"[TELEGRAM CHECK] O envio da mensagem para o Telegram teve sucesso? {sucesso_envio}", flush=True)
                            
                            if sucesso_envio:
                                mark_alert_as_sent(match_id, alert_type, f"Upset set 1: {winner}")
                                print(f"[DB SUCCESS] Alerta marcado como enviado na base de dados para o jogo {match_id}", flush=True)
            
            # Cálculo preciso do tempo de espera para garantir exatamente 8 minutos entre inícios de ciclo
            elapsed_time = time.time() - loop_start_time
            sleep_time = max(0, check_interval - elapsed_time)
            
            print(f"Ciclo concluído em {int(elapsed_time)}s. A aguardar {int(sleep_time)}s para a próxima verificação...", flush=True)
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print("\n[BOT] Interrupção manual detetada (Ctrl+C). A encerrar o bot de forma segura.", flush=True)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_web_server, daemon=True)
    server_thread.start()
    run_bot_loop()