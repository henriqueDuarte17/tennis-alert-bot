from src.config.parsers.match_parser import load_match_fixture
from src.detectors.mto_detector import check_for_mto
from src.detectors.upset_detector import check_for_first_set_upset
from src.storage.database import init_db, alert_was_sent, mark_alert_as_sent
from src.telegram.bot import send_telegram_message
from src.alerts.formatter import format_mto_alert, format_upset_alert

def run_fixture_test():
    print("=== A TESTAR O BOT COM DADOS REAIS DO FIXTURE ===")
    
    init_db()
    
    # Carrega os dados reais do ficheiro JSON
    match_data = load_match_fixture("challenger_match.json")
    if not match_data:
        print("[ERRO] Fixture não encontrado.")
        return
        
    match_id = match_data.get("match_id", "CH_UNKNOWN")
    incidents = match_data.get("incidents", [])
    odds_data = match_data.get("odds", {})
    
    print(f"A analisar o jogo: {match_data.get('player1')} vs {match_data.get('player2')}")
    
    # 1. Testar MTO com dados do fixture
    mto_detected, player_affected = check_for_mto(incidents)
    if mto_detected:
        alert_type = "MTO_FIXTURE"
        if not alert_was_sent(match_id, alert_type):
            print(f"[ALERTA] MTO detetado no fixture para: {player_affected}")
            msg = format_mto_alert(match_data, player_affected)
            if send_telegram_message(msg):
                mark_alert_as_sent(match_id, alert_type, f"MTO: {player_affected}")
        else:
            print("[INFO] Alerta de MTO do fixture já tinha sido enviado anteriormente.")
            
    # 2. Testar Upset com dados do fixture
    upset_detected, winner, favorite = check_for_first_set_upset(match_data, odds_data)
    if upset_detected:
        alert_type = "UPSET_FIXTURE"
        if not alert_was_sent(match_id, alert_type):
            print(f"[ALERTA] Upset detetado no fixture! Vencedor do 1.º set: {winner}")
            msg = format_upset_alert(
                match_data, winner, favorite,
                odds_data.get("odds_favorite", 1.2),
                odds_data.get("odds_underdog", 3.5)
            )
            if send_telegram_message(msg):
                mark_alert_as_sent(match_id, alert_type, f"Upset: {winner}")
        else:
            print("[INFO] Alerta de Upset do fixture já tinha sido enviado anteriormente.")
            
    print("=== TESTE COM FIXTURE CONCLUÍDO ===")

if __name__ == "__main__":
    run_fixture_test()