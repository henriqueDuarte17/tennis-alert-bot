import time
from src.telegram.bot import send_telegram_message
from src.alerts.formatter import format_mto_alert, format_upset_alert
from src.detectors.mto_detector import check_for_mto
from src.detectors.upset_detector import check_for_first_set_upset
from src.storage.database import init_db, alert_was_sent, mark_alert_as_sent

def run_mock_test():
    print("=== A EXECUTAR MODO MOCK COM BASE DE DADOS ===")
    
    # Inicializa a base de dados (cria o ficheiro .db se não existir)
    init_db()
    
    mock_match = {
        "match_id": "CH_TEST_001",
        "tournament": "ATP Challenger Oeiras",
        "player1": "João Silva",
        "player2": "Carlos Santos",
        "current_set": 2,
        "score_summary": "6-4, 3-2",
        "set1_finished": True,
        "set1_p1": 4,
        "set1_p2": 6
    }
    
    match_id = mock_match["match_id"]
    
    mock_incidents = [
        {"text": "Physio enters the court to treat the player João Silva for a right leg issue."}
    ]
    
    mock_odds = {
        "favorite": "João Silva",
        "underdog": "Carlos Santos",
        "odds_favorite": 1.25,
        "odds_underdog": 3.80
    }
    
    print("\n--- A testar Detetor MTO com Base de Dados ---")
    mto_detected, player_affected = check_for_mto(mock_incidents)
    if mto_detected:
        alert_type = "MTO"
        if alert_was_sent(match_id, alert_type):
            print(f"[INFO] O alerta '{alert_type}' para este jogo já tinha sido enviado anteriormente. Ignorado.")
        else:
            print(f"[ALERTA NOVO] MTO detetado para: {player_affected}")
            mto_msg = format_mto_alert(mock_match, player_name=player_affected)
            if send_telegram_message(mto_msg):
                mark_alert_as_sent(match_id, alert_type, f"MTO: {player_affected}")
    
    time.sleep(1)
    
    print("\n--- A testar Detetor Upset com Base de Dados ---")
    upset_detected, winner, favorite = check_for_first_set_upset(mock_match, mock_odds)
    if upset_detected:
        alert_type = "UPSET_SET_1"
        if alert_was_sent(match_id, alert_type):
            print(f"[INFO] O alerta '{alert_type}' para este jogo já tinha sido enviado anteriormente. Ignorado.")
        else:
            print(f"[ALERTA NOVO] Upset! {winner} venceu o 1.º set.")
            upset_msg = format_upset_alert(
                mock_match, winner, favorite, 
                mock_odds["odds_favorite"], mock_odds["odds_underdog"]
            )
            if send_telegram_message(upset_msg):
                mark_alert_as_sent(match_id, alert_type, f"Upset set 1: {winner}")
                
    print("\n=== TESTE CONCLUÍDO ===")

if __name__ == "__main__":
    run_mock_test()