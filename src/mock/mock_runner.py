import time

print(">>> O MOCK_RUNNER FOI INICIADO COM SUCESSO! <<<")

from src.telegram.bot import send_telegram_message
from src.alerts.formatter import format_mto_alert, format_upset_alert

def run_mock_test():
    print("=== A EXECUTAR MODO MOCK (TESTE DE ALERTAS) ===")
    
    mock_match = {
        "match_id": "CH_TEST_001",
        "tournament": "ATP Challenger Oeiras",
        "player1": "João Silva",
        "player2": "Carlos Santos",
        "current_set": 2,
        "score_summary": "6-4, 3-2"
    }
    
    print("\n1. A testar envio de alerta de Medical Timeout (MTO)...")
    mto_msg = format_mto_alert(mock_match, player_name="João Silva")
    send_telegram_message(mto_msg)
    
    time.sleep(2)
    
    print("\n2. A testar envio de alerta de Favorito que perdeu o 1.º set...")
    upset_msg = format_upset_alert(
        mock_match, "Carlos Santos", "João Silva", 1.25, 3.80
    )
    send_telegram_message(upset_msg)
    
    print("\n=== TESTE CONCLUÍDO. Verifica o teu Telegram! ===")

if __name__ == "__main__":
    run_mock_test()